"""TradingApp v3 — Extractor DeepSeek (schéma directionnel v2.1).

Refonte chantier prompt v2 (cf. v3/ANALYSE-PROMPT-ia.md) + nettoyage v2.1
(cf. v3/ANALYSE-PROMPT-v2-ia.md) :
- Le LLM produit un signal DIRECTIONNEL (LONG/SHORT) par actif impacté.
  Impact neutre/incertain → NE PAS lister l'actif (impacts:[]). NEUTRAL retiré.
- `impacts[]` remplace `cours` mono-actif (un event peut toucher Brent + Or + VIX).
- `materiality` + `reliability` permettent de filtrer signal vs bruit.
- Taxonomie fusionnée : 1 `category` (~10 valeurs) + `subcat` libre.
- `confidence` par impact = bucket {high, medium, low} (fausse précision 0-100
  supprimée). Parsing défensif : entier reçu → mapping bucket.
- 3 few-shots ancrent le jugement (escalade géopol multi-actifs, news
  non-tradable, rumeur M&A).
- Parsing défensif : énums hors-bornes → normalisées ou rejetées.
- Champs morts retirés : `already_priced` (jamais consommé), `latence` (jamais
  consommée par la chaîne aval).

API DeepSeek = OpenAI-compatible. Modèle : deepseek-chat. temperature=0.

GARDES-FOUS COÛT (persistants dans v3/data/cost-ledger.json) :
- soft cap  ~0,50 $/jour : log WARN, on continue d'appeler le LLM
- hard cap  ~0,80 $/jour : bascule fallback (extracteur désactivé pour la journée
  -> news_collector écrit en mode brut)

Si DEEPSEEK_API_KEY est vide -> extracteur désactivé (mode passive).
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from config import COST_LEDGER_PATH

logger = logging.getLogger(__name__)

# ============================================================
# Caps coût (USD/jour)
# ============================================================
SOFT_CAP_USD_PER_DAY = float(os.environ.get("LLM_SOFT_CAP_USD", "0.50"))
HARD_CAP_USD_PER_DAY = float(os.environ.get("LLM_HARD_CAP_USD", "0.80"))


# ============================================================
# Énumérations fermées
# ============================================================

TRADABLE_ASSETS: Tuple[str, ...] = (
    "CAC40", "SP500", "NASDAQ", "EURUSD",
    "BRENT", "VIX", "GOLD", "SILVER", "COPPER",
    "COFFEE", "COCOA", "WHEAT",
)
_ASSETS_SET = set(TRADABLE_ASSETS)

DIRECTIONS: Tuple[str, ...] = ("LONG", "SHORT")
_DIR_SET = set(DIRECTIONS)

CONFIDENCE_BUCKETS: Tuple[str, ...] = ("high", "medium", "low")
_CONF_SET = set(CONFIDENCE_BUCKETS)

CATEGORIES: Tuple[str, ...] = (
    "geopolitical", "macro", "central_bank", "earnings", "commodity",
    "regulatory", "m_a", "weather", "supply_chain", "other",
)
_CAT_SET = set(CATEGORIES)

RELIABILITIES: Tuple[str, ...] = ("confirmed", "reported", "rumor")
_REL_SET = set(RELIABILITIES)

MATERIALITIES: Tuple[str, ...] = ("high", "medium", "low")
_MAT_SET = set(MATERIALITIES)

# Phase 2 — taxonomie persistance (axe News Trader, validé Thomas).
# - structurel : driver durable (OPEC, Ormuz, récolte, embargo) → porte la tendance
# - ponctuel   : choc court (frappe isolée, chiffre macro hebdo) → s'amortit
# - deja_cote  : compte-rendu de ce qui s'est passé (« S&P a monté 9 semaines »)
# - verbal     : déclaration, rumeur, « envisage », « pourrait »
NATURES: Tuple[str, ...] = ("structurel", "ponctuel", "deja_cote", "verbal")
_NAT_SET = set(NATURES)

# Version du prompt — bumper à chaque évolution sémantique du schéma.
# v2.2 (Phase 2 news) : ajout du champ `nature` au schéma DeepSeek.
# v2.3 (NT-1) : règle anti sur-structurel + few-shots single-name/deja_cote.
# v2.4 (audit 10/06) : DATE DU JOUR injectée dans le message variable (règle 10),
#   few-shot (c) M&A single-name → déclaration central_bank `verbal`, RÈGLES
#   renumérotées 1→10 (séquence stricte). Préfixe [system+few-shots] inchangé en
#   structure : un seul bump = une seule invalidation du cache DeepSeek.
PROMPT_VERSION = "v2.4"


# ============================================================
# Dataclass de sortie
# ============================================================

@dataclass
class Impact:
    asset: str                # ∈ TRADABLE_ASSETS
    direction: str            # ∈ DIRECTIONS = {LONG, SHORT}
    confidence: str = "low"   # ∈ CONFIDENCE_BUCKETS = {high, medium, low}

    def to_dict(self) -> Dict[str, Any]:
        return {"asset": self.asset, "direction": self.direction, "confidence": self.confidence}


@dataclass
class ExtractedEvent:
    # Schéma directionnel v2.1 (nettoyé)
    impacts: List[Impact] = field(default_factory=list)
    category: str = "other"
    subcat: str = ""
    trigger: str = ""
    news_zone: str = ""
    reliability: str = ""
    materiality: str = "low"
    # Phase 2 — persistance / amortissement (axe News Trader)
    nature: str = "ponctuel"  # fallback conservateur si absent / hors-énum
    # Méta
    error: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: int = 0


# ============================================================
# SYSTEM_PROMPT + few-shots
# ============================================================

SYSTEM_PROMPT = """Tu es un analyste senior d'un desk de news trading institutionnel.

Pour chaque news (titre + snippet), tu COMPRENDS l'événement, tu identifies quels
actifs parmi la liste FERMÉE sont impactés, et DANS QUEL SENS. Tu retournes
UNIQUEMENT un JSON strict.

ACTIFS TRADABLES (liste FERMÉE — n'utilise QUE ces ids, sinon n'inclus pas l'actif) :
CAC40, SP500, NASDAQ, EURUSD, BRENT, VIX, GOLD, SILVER, COPPER, COFFEE, COCOA, WHEAT

SCHEMA :
{
  "category": "<geopolitical | macro | central_bank | earnings | commodity | regulatory | m_a | weather | supply_chain | other>",
  "subcat": "<sous-thème précis, ex: 'Iran-Moyen-Orient', 'Fed-FOMC'. Vide si incertain.>",
  "trigger": "<fait déclencheur factuel, max 200 chars>",
  "news_zone": "<US | EU | EU-FR | BR | CN | RU | UA | AU | Moyen-Orient | Global>",
  "reliability": "<confirmed | reported | rumor>",
  "materiality": "<high | medium | low>",
  "nature": "<structurel | ponctuel | deja_cote | verbal>",
  "impacts": [
    { "asset": "<id de la liste fermée>",
      "direction": "<LONG | SHORT>",
      "confidence": "<high | medium | low>" }
  ]
}

RÈGLES :
1. AUCUNE INVENTION. Doute -> impacts:[], materiality:"low".
2. nature : axe PERSISTANCE de l'événement (sert à distinguer une news qui
   crée/confirme une tendance d'un compte-rendu déjà cuit) :
   - "structurel" : driver SYSTÉMIQUE et DURABLE qui impacte l'OFFRE ou la
     DEMANDE sur des MOIS (politique OPEC+ de production, blocus prolongé d'un
     détroit, destruction massive de récolte, embargo, sanctions étendues,
     accord commercial pluri-annuel). Mouvement qui TIENT à 1 mois.
   - "ponctuel" : fait DATÉ et CIRCONSCRIT (rapport programmé, audit/AGM/résultats
     d'une SEULE entreprise, frappe/grève à une date précise, statistique macro
     hebdo, incident industriel isolé). S'amortit en quelques jours.
     ⚠ ANTI-PIÈGE : un événement corporate single-name (« audit Cobre Panama
     vendredi », « décision FDA sur le médicament X », « grève Codelco lundi »)
     est PONCTUEL — pas structurel. Le ton « important » ne le rend pas systémique.
     RÈGLE : si le fait est ATTACHÉ À UNE DATE PRÉCISE et UNE SEULE ENTITÉ →
     `ponctuel`. Si le fait CHANGE LE RÉGIME d'offre/demande sur des MOIS pour
     TOUT un actif → `structurel`.
   - "deja_cote" : compte-rendu de ce qui s'est passé / récap performance
     (« S&P 500 a monté 9 semaines d'affilée », « pire mois depuis 2020 »,
     « récap hebdo des marchés »). L'info est DÉJÀ dans le prix → on l'écarte.
   - "verbal" : déclaration, rumeur, « envisage », « pourrait », « selon des sources »,
     officiel qui menace sans agir. Pas encore un fait → faible persistance.
3. impacts = SEULEMENT des actifs de la liste fermée réellement et directionnellement
   impactés. Un event peut en toucher plusieurs (ex: escalade géopol -> GOLD LONG,
   BRENT LONG, VIX LONG, SP500 SHORT). Aucun actif clair OU impact incertain/neutre
   sur un actif -> NE PAS lister l'actif (impacts peut être [] ou ne contenir que
   les actifs au sens clair).
4. direction = sens du PRIX de l'actif : hausse=LONG, baisse=SHORT.
   Pas de "neutre" : si tu ne sais pas trancher, n'inclus pas l'actif. Raisonne
   sur l'effet réel, ignore le ton du titre.
   CHAÎNES DE CAUSE MÉCANIQUES (applique-les, c'est de la logique, pas une opinion) :
   - Fed/banque centrale HAWKISH / hausse de taux / inflation persistante / ton
     restrictif → dollar FORT → EURUSD SHORT ; actions (SP500, NASDAQ, CAC40) SHORT ;
     GOLD SHORT (or non rémunéré pénalisé par les taux réels). DOVISH / baisse de
     taux → l'INVERSE (EURUSD LONG, actions LONG, GOLD LONG).
   - Risque/géopolitique qui MONTE (guerre, sanctions, escalade) → GOLD LONG,
     VIX LONG, actions SHORT ; pétrole/matières dont l'offre est menacée → LONG.
   - Choc d'OFFRE sur une matière (coupe OPEP, gel/sécheresse café-cacao-blé,
     rupture mine cuivre/argent) → la matière concernée LONG (moins d'offre = prix↑).
   - Cohérence : sur une même news, le dollar et les actions US réagissent en général
     dans le MÊME sens face à la politique monétaire (hawkish = USD↑ et actions↓ ;
     donc EURUSD SHORT VA AVEC SP500/NASDAQ SHORT). Ne tague pas EURUSD LONG en même
     temps que des actions US SHORT pour une cause monétaire.
5. confidence = "high" si la direction est très probable et bien étayée ;
   "medium" si plausible mais avec incertitude ; "low" si signal faible/contestable.
6. reliability : fait officiel="confirmed" ; presse/source citée="reported" ;
   "selon des sources"/spéculation="rumor".
7. materiality : "high" seulement si surprise/ampleur notable ; "medium" si signal
   crédible mais attendu ; "low" si bruit ou déjà connu.
8. News non-tradable (sport, lifestyle, opinion, people) -> category:"other",
   impacts:[], materiality:"low".
9. Titre EN ou FR : raisonne, réponds toujours dans ce schéma.
10. DATE DU JOUR : si le message fournit une ligne « DATE DU JOUR : YYYY-MM-DD »,
    utilise-la pour juger la fraîcheur SANS RIEN INVENTER. Un fait déjà survenu
    et daté de plusieurs jours est probablement « deja_cote » (l'info est dans le
    prix) ; un rapport/échéance programmé dont la date est passée est périmé
    (materiality plus basse). N'invente jamais une date absente : à défaut de date
    explicite dans la news, ne déduis rien de l'âge.

Réponds avec UNIQUEMENT le JSON."""


# Few-shots : 3 exemples calibrés pour ancrer le jugement.
FEW_SHOTS: List[Tuple[str, str]] = [
    # (a) Escalade géopol multi-actifs (haute matérialité, multi-impacts) — structurel
    (
        "TITRE : Iran retaliates with airstrikes on US bases, Brent jumps 5%",
        json.dumps({
            "category": "geopolitical",
            "subcat": "Iran-Moyen-Orient",
            "trigger": "Frappes iraniennes sur bases US, escalade militaire",
            "news_zone": "Moyen-Orient",
            "reliability": "confirmed",
            "materiality": "high",
            "nature": "structurel",
            "impacts": [
                {"asset": "BRENT",  "direction": "LONG",  "confidence": "high"},
                {"asset": "GOLD",   "direction": "LONG",  "confidence": "high"},
                {"asset": "VIX",    "direction": "LONG",  "confidence": "medium"},
                {"asset": "SP500",  "direction": "SHORT", "confidence": "medium"},
            ],
        }, ensure_ascii=False),
    ),
    # (b) News non-tradable -> impacts:[]
    (
        "TITRE : Royal wedding draws record TV audience in the UK",
        json.dumps({
            "category": "other",
            "subcat": "",
            "trigger": "Mariage royal britannique, audience TV record",
            "news_zone": "EU",
            "reliability": "confirmed",
            "materiality": "low",
            "nature": "ponctuel",
            "impacts": [],
        }, ensure_ascii=False),
    ),
    # (c) Déclaration conditionnelle d'un officiel → reliability:reported, nature=verbal.
    # Pas de single-name : une orientation de banque centrale touche l'indice large +
    # l'or sans passer par une seule entreprise (évite le piège single-name→indice).
    (
        "TITRE : Fed official says rate cuts could come sooner than expected if inflation cools",
        json.dumps({
            "category": "central_bank",
            "subcat": "Fed-FOMC",
            "trigger": "Un membre de la Fed évoque des baisses de taux plus tôt si l'inflation reflue",
            "news_zone": "US",
            "reliability": "reported",
            "materiality": "medium",
            "nature": "verbal",
            "impacts": [
                {"asset": "SP500",  "direction": "LONG", "confidence": "low"},
                {"asset": "NASDAQ", "direction": "LONG", "confidence": "low"},
                {"asset": "GOLD",   "direction": "LONG", "confidence": "low"},
            ],
        }, ensure_ascii=False),
    ),
    # (d-anti-piège NT-1) Fait daté single-name → ponctuel, PAS structurel
    # (audit / AGM / résultats d'UNE entreprise à UNE date → corporate ponctuel)
    (
        "TITRE : First Quantum to release Cobre Panama audit results on Friday",
        json.dumps({
            "category": "commodity",
            "subcat": "Single-name corporate audit",
            "trigger": "Publication audit Cobre Panama (First Quantum) vendredi",
            "news_zone": "Global",
            "reliability": "confirmed",
            "materiality": "medium",
            # Fait daté, single-name → ponctuel (PAS structurel)
            "nature": "ponctuel",
            "impacts": [
                {"asset": "COPPER", "direction": "LONG", "confidence": "low"},
            ],
        }, ensure_ascii=False),
    ),
    # (e) Compte-rendu de marché → deja_cote (info déjà dans le prix)
    (
        "TITRE : S&P 500 logs ninth weekly gain in a row, longest streak since 2004",
        json.dumps({
            "category": "macro",
            "subcat": "Equity recap",
            "trigger": "Le S&P 500 enchaîne 9 semaines de hausse consécutives",
            "news_zone": "US",
            "reliability": "confirmed",
            "materiality": "low",
            "nature": "deja_cote",
            "impacts": [],
        }, ensure_ascii=False),
    ),
]


# ============================================================
# Cost ledger
# ============================================================

def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_ledger() -> dict:
    try:
        if COST_LEDGER_PATH.exists():
            return json.loads(COST_LEDGER_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("cost-ledger lecture KO: %s", e)
    return {}


def _save_ledger(ledger: dict) -> None:
    try:
        COST_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        COST_LEDGER_PATH.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning("cost-ledger écriture KO: %s", e)


# ============================================================
# Parsing défensif
# ============================================================

def _norm_enum(value: Any, allowed: set, default: str = "") -> str:
    """Normalise une string contre une énumération. Retourne default si hors-énum."""
    if not isinstance(value, str):
        return default
    v = value.strip()
    if v in allowed:
        return v
    # Tente normalisation lowercase pour les énumérations lowercase
    vl = v.lower()
    if vl in allowed:
        return vl
    vu = v.upper()
    if vu in allowed:
        return vu
    return default


def _parse_confidence(value: Any) -> str:
    """Confidence en bucket {high, medium, low}.

    - String dans l'énum → renvoyée telle quelle (lowercase).
    - Entier ou float (compat ancien schéma 0-100) → mappé en bucket :
      >=66 → high, >=33 → medium, sinon → low.
    - String numérique → idem après cast.
    - Tout le reste → "low" (degradation gracieuse).
    """
    if isinstance(value, bool):  # bool est subclass de int → traité en premier
        return "low"
    if isinstance(value, str):
        s = value.strip().lower()
        if s in _CONF_SET:
            return s
        # Peut-être une string numérique
        try:
            num = float(s)
        except ValueError:
            return "low"
        return _bucket_from_number(num)
    if isinstance(value, (int, float)):
        return _bucket_from_number(float(value))
    return "low"


def _bucket_from_number(num: float) -> str:
    """Mapping numérique → bucket (compat ancien schéma 0-100)."""
    n = max(0.0, min(100.0, num))
    if n >= 66:
        return "high"
    if n >= 33:
        return "medium"
    return "low"


def _parse_impacts(raw: Any) -> List[Impact]:
    """Parse impacts[] avec validation stricte.

    - Asset hors-liste fermée → impact rejeté (zéro invention).
    - Direction NEUTRAL/inconnue → impact rejeté (le prompt v2.1 interdit NEUTRAL :
      un actif "neutre" ne doit simplement pas figurer dans impacts[]).
    - Tolérance rétro-compat sur 'bullish/bearish' (mappés LONG/SHORT) et entiers
      de confidence (mappés en bucket).
    """
    if not isinstance(raw, list):
        return []
    out: List[Impact] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        asset = _norm_enum(item.get("asset"), _ASSETS_SET, default="")
        if not asset:
            continue  # asset hors-liste -> on rejette l'impact (zéro invention)
        direction = _norm_enum(item.get("direction"), _DIR_SET, default="")
        if not direction:
            # Tolère "bullish/bearish" historique
            d_raw = (item.get("direction") or "")
            if isinstance(d_raw, str):
                dl = d_raw.strip().lower()
                if dl in ("bullish", "buy", "long"):
                    direction = "LONG"
                elif dl in ("bearish", "sell", "short"):
                    direction = "SHORT"
                # "neutral"/"flat"/"NEUTRAL" → rejet (impact non listé)
            if not direction:
                continue
        confidence = _parse_confidence(item.get("confidence"))
        out.append(Impact(asset=asset, direction=direction, confidence=confidence))
    return out


# ============================================================
# Extractor
# ============================================================

class Extractor:
    def __init__(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY non défini -> extracteur désactivé")
            self.client = None
            return

        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        except Exception as e:
            logger.error("Init client DeepSeek échouée (%s) -> extracteur désactivé (mode brut)", e)
            self.client = None
            return
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        self.total_calls = 0
        self.total_tokens_in = 0
        self.total_tokens_out = 0
        self.total_errors = 0
        self.hard_capped = False

        self.ledger = _load_ledger()
        self.day_key = _today_key()
        self.day_cost_usd = float(self.ledger.get(self.day_key, {}).get("cost_usd", 0.0))
        self._check_caps_initial()

        logger.info(
            "Extractor init: model=%s base_url=%s | cost_today=$%.4f (soft=$%.2f hard=$%.2f)",
            self.model, base_url, self.day_cost_usd, SOFT_CAP_USD_PER_DAY, HARD_CAP_USD_PER_DAY,
        )

    def _check_caps_initial(self):
        if self.day_cost_usd >= HARD_CAP_USD_PER_DAY:
            self.hard_capped = True
            logger.error(
                "HARD CAP atteint au boot : cost_today=$%.4f >= $%.2f -> fallback mode brut",
                self.day_cost_usd, HARD_CAP_USD_PER_DAY,
            )
        elif self.day_cost_usd >= SOFT_CAP_USD_PER_DAY:
            logger.warning(
                "SOFT CAP dépassé au boot : cost_today=$%.4f >= $%.2f (on continue)",
                self.day_cost_usd, SOFT_CAP_USD_PER_DAY,
            )

    def is_enabled(self) -> bool:
        return self.client is not None and not self.hard_capped

    def _update_cost(self, tokens_in: int, tokens_out: int):
        delta = (tokens_in * 0.14 + tokens_out * 0.28) / 1_000_000
        self.day_cost_usd += delta
        self.ledger[self.day_key] = {
            "cost_usd": round(self.day_cost_usd, 6),
            "calls": int(self.ledger.get(self.day_key, {}).get("calls", 0)) + 1,
            "tokens_in": int(self.ledger.get(self.day_key, {}).get("tokens_in", 0)) + tokens_in,
            "tokens_out": int(self.ledger.get(self.day_key, {}).get("tokens_out", 0)) + tokens_out,
        }
        _save_ledger(self.ledger)

        if self.day_cost_usd >= HARD_CAP_USD_PER_DAY and not self.hard_capped:
            self.hard_capped = True
            logger.error(
                "HARD CAP franchi : cost_today=$%.4f >= $%.2f -> bascule fallback brut",
                self.day_cost_usd, HARD_CAP_USD_PER_DAY,
            )
        elif self.day_cost_usd >= SOFT_CAP_USD_PER_DAY:
            logger.warning(
                "SOFT CAP dépassé : cost_today=$%.4f >= $%.2f",
                self.day_cost_usd, SOFT_CAP_USD_PER_DAY,
            )

    def _build_messages(self, title: str, snippet: str) -> List[Dict[str, str]]:
        """Construit le tableau messages.

        ORDRE CRITIQUE pour le prompt caching DeepSeek (cf. audit-ia §5) :
        le préfixe [system + few-shots] (~1k tokens) DOIT être STRICTEMENT stable
        d'un appel à l'autre. DeepSeek facture les cache hits ~10× moins cher
        sur l'input préfixe identique. Toute mutation (rotation few-shots, version
        de prompt embarquée dynamiquement, etc.) casserait le cache.
        Le seul contenu variable est le DERNIER message user (titre+snippet).
        """
        msgs: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Few-shots injectés en alternance user/assistant pour ancrer le jugement.
        # Préfixe stable → cache hit DeepSeek implicite.
        for user_msg, assistant_msg in FEW_SHOTS:
            msgs.append({"role": "user", "content": user_msg})
            msgs.append({"role": "assistant", "content": assistant_msg})
        # Vraie news : seul contenu variable (en queue, n'altère pas le cache préfixe).
        # DATE DU JOUR (Europe/Paris) préfixée UNIQUEMENT sur ce message variable :
        # la date change chaque jour → la mettre dans le system/few-shots casserait le
        # cache préfixe à chaque jour. Ici, en queue, c'est gratuit côté cache.
        today = datetime.now(ZoneInfo("Europe/Paris")).strftime("%Y-%m-%d")
        user_content = f"DATE DU JOUR : {today}\n\nTITRE : {title.strip()}"
        if snippet and snippet.strip():
            user_content += f"\n\nSNIPPET : {snippet.strip()[:1500]}"
        msgs.append({"role": "user", "content": user_content})
        return msgs

    def extract(self, title: str, snippet: str = "") -> ExtractedEvent:
        if not self.is_enabled():
            return ExtractedEvent(trigger=title[:200], error="extractor disabled or hard-capped")

        start = time.monotonic()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self._build_messages(title, snippet),
                temperature=0,
                response_format={"type": "json_object"},
                # max_tokens=800 : marge anti-troncature pour impacts[] riches
                # (cf. audit-ia §2). 500 tronquait des JSON multi-impacts → invalid
                # → event en mode brut. Sur tronquage : json.JSONDecodeError est
                # capté → ExtractedEvent.error → retry idempotent au prochain cycle
                # (cf. agent_news.run_one_cycle, pas de mark_title_seen sur erreur).
                max_tokens=800,
                timeout=20,
            )
            duration_ms = int((time.monotonic() - start) * 1000)
            data = json.loads(response.choices[0].message.content)
            if not isinstance(data, dict):
                raise ValueError("réponse JSON non-objet")

            tokens_in = response.usage.prompt_tokens if response.usage else 0
            tokens_out = response.usage.completion_tokens if response.usage else 0
            self.total_calls += 1
            self.total_tokens_in += tokens_in
            self.total_tokens_out += tokens_out
            self._update_cost(tokens_in, tokens_out)

            return ExtractedEvent(
                impacts=_parse_impacts(data.get("impacts")),
                category=_norm_enum(data.get("category"), _CAT_SET, default="other"),
                subcat=str(data.get("subcat") or "")[:80],
                trigger=str(data.get("trigger") or title)[:250],
                news_zone=str(data.get("news_zone") or "")[:30],
                reliability=_norm_enum(data.get("reliability"), _REL_SET, default=""),
                materiality=_norm_enum(data.get("materiality"), _MAT_SET, default="low"),
                # Phase 2 — nature : fallback "ponctuel" (conservateur : ne déclenche
                # ni l'amortissement deja_cote/verbal, ni le bonus structurel).
                nature=_norm_enum(data.get("nature"), _NAT_SET, default="ponctuel"),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                duration_ms=duration_ms,
            )
        except json.JSONDecodeError as e:
            self.total_errors += 1
            logger.warning("DeepSeek invalid JSON for '%s...': %s", title[:60], e)
            return ExtractedEvent(trigger=title[:200], error=f"invalid JSON: {e}"[:200])
        except Exception as e:
            self.total_errors += 1
            logger.warning("DeepSeek extract failed for '%s...': %s", title[:60], str(e)[:200])
            return ExtractedEvent(trigger=title[:200], error=str(e)[:200])

    def get_stats(self) -> dict:
        if self.client is None:
            return {"enabled": False, "reason": "no_api_key"}
        cost_in = self.total_tokens_in * 0.14 / 1_000_000
        cost_out = self.total_tokens_out * 0.28 / 1_000_000
        return {
            "enabled": not self.hard_capped,
            "hard_capped": self.hard_capped,
            "calls": self.total_calls,
            "errors": self.total_errors,
            "tokens_in": self.total_tokens_in,
            "tokens_out": self.total_tokens_out,
            "cycle_cost_usd": round(cost_in + cost_out, 4),
            "day_cost_usd": round(self.day_cost_usd, 4),
        }


# ============================================================
# Helpers d'encodage des impacts (utilisés par news_collector)
# ============================================================

def encode_impacts(impacts: List[Impact]) -> str:
    """Encodage compact : 'ASSET:DIR:BUCKET;ASSET:DIR:BUCKET'.

    Exemple : 'BRENT:LONG:high;GOLD:LONG:high;VIX:LONG:medium;SP500:SHORT:medium'
    Vide si impacts=[]. Direction NEUTRAL ou bucket invalide → impact ignoré.
    """
    if not impacts:
        return ""
    parts = []
    for imp in impacts:
        if not imp.asset or imp.asset not in _ASSETS_SET:
            continue
        if imp.direction not in _DIR_SET:
            continue
        bucket = imp.confidence if imp.confidence in _CONF_SET else "low"
        parts.append(f"{imp.asset}:{imp.direction}:{bucket}")
    return ";".join(parts)


def decode_impacts(encoded: str) -> List[Dict[str, Any]]:
    """Décodage tolérant. Retourne liste de dicts {asset, direction, confidence}.

    - confidence : bucket {high, medium, low}. Rétro-compat ancien schéma 0-100 :
      un entier est mappé en bucket (>=66 high, >=33 medium, sinon low).
    - Entrées invalides silencieusement ignorées.
    - NEUTRAL (ancien schéma) ignoré (l'IA n'émet plus NEUTRAL en v2.1).
    """
    if not encoded or not isinstance(encoded, str):
        return []
    out: List[Dict[str, Any]] = []
    for chunk in encoded.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        parts = chunk.split(":")
        if len(parts) < 2:
            continue
        asset = parts[0].strip().upper()
        direction = parts[1].strip().upper()
        if asset not in _ASSETS_SET or direction not in _DIR_SET:
            continue
        confidence = "low"
        if len(parts) >= 3 and parts[2].strip():
            raw_conf = parts[2].strip().lower()
            if raw_conf in _CONF_SET:
                confidence = raw_conf
            else:
                try:
                    confidence = _bucket_from_number(float(raw_conf))
                except ValueError:
                    confidence = "low"
        out.append({"asset": asset, "direction": direction, "confidence": confidence})
    return out


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ext = Extractor()
    if ext.client is None:
        print("Extractor disabled. Vérifie DEEPSEEK_API_KEY.")
        raise SystemExit(1)
    e = ext.extract(
        "Iran retaliates with airstrikes on US bases, Brent jumps 5%",
        "Tehran launched drone attacks; Brent crude surges past $110 in pre-market.",
    )
    print(e)
    print(ext.get_stats())
