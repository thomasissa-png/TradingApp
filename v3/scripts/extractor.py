"""TradingApp v3 — Extractor DeepSeek (schéma directionnel v2).

Refonte chantier prompt v2 (cf. v3/ANALYSE-PROMPT-ia.md) :
- Le LLM produit un signal DIRECTIONNEL (LONG/SHORT/NEUTRAL) par actif impacté,
  pas juste une description.
- `impacts[]` remplace `cours` mono-actif (un event peut toucher Brent + Or + VIX).
- `materiality` + `reliability` permettent de filtrer signal vs bruit.
- Taxonomie fusionnée : 1 `category` (~10 valeurs) + `subcat` libre.
- 3 few-shots ancrent le jugement (escalade géopol multi-actifs, news
  non-tradable, rumeur M&A).
- Parsing défensif : énums hors-bornes → normalisées ou rejetées.

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

DIRECTIONS: Tuple[str, ...] = ("LONG", "SHORT", "NEUTRAL")
_DIR_SET = set(DIRECTIONS)

CATEGORIES: Tuple[str, ...] = (
    "geopolitical", "macro", "central_bank", "earnings", "commodity",
    "regulatory", "m_a", "weather", "supply_chain", "other",
)
_CAT_SET = set(CATEGORIES)

RELIABILITIES: Tuple[str, ...] = ("confirmed", "reported", "rumor")
_REL_SET = set(RELIABILITIES)

MATERIALITIES: Tuple[str, ...] = ("high", "medium", "low")
_MAT_SET = set(MATERIALITIES)

LATENCES: Tuple[str, ...] = ("intraday", "overnight", "weekend", "jours")
_LAT_SET = set(LATENCES)


# ============================================================
# Dataclass de sortie
# ============================================================

@dataclass
class Impact:
    asset: str                # ∈ TRADABLE_ASSETS
    direction: str            # ∈ DIRECTIONS
    confidence: int = 0       # 0-100

    def to_dict(self) -> Dict[str, Any]:
        return {"asset": self.asset, "direction": self.direction, "confidence": self.confidence}


@dataclass
class ExtractedEvent:
    # Nouveau schéma directionnel
    impacts: List[Impact] = field(default_factory=list)
    category: str = "other"
    subcat: str = ""
    trigger: str = ""
    news_zone: str = ""
    latence: str = ""
    reliability: str = ""
    materiality: str = "low"
    already_priced: bool = False
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
  "latence": "<intraday | overnight | weekend | jours>",
  "reliability": "<confirmed | reported | rumor>",
  "materiality": "<high | medium | low>",
  "already_priced": <true | false>,
  "impacts": [
    { "asset": "<id de la liste fermée>",
      "direction": "<LONG | SHORT | NEUTRAL>",
      "confidence": <entier 0-100> }
  ]
}

RÈGLES :
1. AUCUNE INVENTION. Doute -> impacts:[], materiality:"low".
2. impacts = SEULEMENT des actifs de la liste fermée réellement et directionnellement
   impactés. Un event peut en toucher plusieurs (ex: escalade géopol -> GOLD LONG,
   BRENT LONG, VIX LONG, SP500 SHORT). Aucun actif clair -> impacts:[].
3. direction = sens du PRIX de l'actif (hausse=LONG, baisse=SHORT, neutre=NEUTRAL).
   Raisonne sur l'effet réel, ignore le ton du titre.
4. reliability : fait officiel="confirmed" ; presse/source citée="reported" ;
   "selon des sources"/spéculation="rumor".
5. materiality : "high" seulement si surprise/ampleur notable ; "medium" si signal
   crédible mais attendu ; "low" si bruit ou déjà connu.
6. already_priced=true si la news est une confirmation d'attendu déjà connu du marché.
7. News non-tradable (sport, lifestyle, opinion, people) -> category:"other",
   impacts:[], materiality:"low".
8. Titre EN ou FR : raisonne, réponds toujours dans ce schéma.

Réponds avec UNIQUEMENT le JSON."""


# Few-shots : 3 exemples calibrés pour ancrer le jugement.
FEW_SHOTS: List[Tuple[str, str]] = [
    # (a) Escalade géopol multi-actifs (haute matérialité, multi-impacts)
    (
        "TITRE : Iran retaliates with airstrikes on US bases, Brent jumps 5%",
        json.dumps({
            "category": "geopolitical",
            "subcat": "Iran-Moyen-Orient",
            "trigger": "Frappes iraniennes sur bases US, escalade militaire",
            "news_zone": "Moyen-Orient",
            "latence": "intraday",
            "reliability": "confirmed",
            "materiality": "high",
            "already_priced": False,
            "impacts": [
                {"asset": "BRENT",  "direction": "LONG",  "confidence": 85},
                {"asset": "GOLD",   "direction": "LONG",  "confidence": 75},
                {"asset": "VIX",    "direction": "LONG",  "confidence": 70},
                {"asset": "SP500",  "direction": "SHORT", "confidence": 60},
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
            "latence": "jours",
            "reliability": "confirmed",
            "materiality": "low",
            "already_priced": False,
            "impacts": [],
        }, ensure_ascii=False),
    ),
    # (c) Rumeur M&A -> reliability:rumor, materiality:medium
    (
        "TITRE : Sources say Microsoft in early talks to acquire AI startup Anthropic",
        json.dumps({
            "category": "m_a",
            "subcat": "Big Tech M&A",
            "trigger": "Rumeur d'acquisition d'Anthropic par Microsoft (early talks)",
            "news_zone": "US",
            "latence": "jours",
            "reliability": "rumor",
            "materiality": "medium",
            "already_priced": False,
            "impacts": [
                {"asset": "NASDAQ", "direction": "LONG", "confidence": 40},
            ],
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


def _parse_confidence(value: Any) -> int:
    """Confidence numérique 0-100. Accepte aussi 'high/medium/low' en fallback."""
    if isinstance(value, (int, float)):
        return max(0, min(100, int(value)))
    if isinstance(value, str):
        s = value.strip().lower()
        # Si DeepSeek glisse vers l'énumération textuelle malgré la consigne
        mapping = {"high": 80, "medium": 50, "low": 25}
        if s in mapping:
            return mapping[s]
        try:
            return max(0, min(100, int(float(s))))
        except ValueError:
            return 0
    return 0


def _parse_impacts(raw: Any) -> List[Impact]:
    """Parse impacts[] avec validation stricte : asset hors-liste => rejet de l'entrée."""
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
                elif dl in ("neutral", "flat"):
                    direction = "NEUTRAL"
            if not direction:
                continue
        confidence = _parse_confidence(item.get("confidence"))
        out.append(Impact(asset=asset, direction=direction, confidence=confidence))
    return out


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "oui")
    return False


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
        msgs: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        # Few-shots injectés en alternance user/assistant pour ancrer le jugement.
        for user_msg, assistant_msg in FEW_SHOTS:
            msgs.append({"role": "user", "content": user_msg})
            msgs.append({"role": "assistant", "content": assistant_msg})
        # Vraie news
        user_content = f"TITRE : {title.strip()}"
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
                max_tokens=500,
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
                latence=_norm_enum(data.get("latence"), _LAT_SET, default=""),
                reliability=_norm_enum(data.get("reliability"), _REL_SET, default=""),
                materiality=_norm_enum(data.get("materiality"), _MAT_SET, default="low"),
                already_priced=_parse_bool(data.get("already_priced")),
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
    """Encodage compact : 'ASSET:DIR:CONF;ASSET:DIR:CONF'.

    Exemple : 'BRENT:LONG:85;GOLD:LONG:75;VIX:LONG:70;SP500:SHORT:60'
    Vide si impacts=[].
    """
    if not impacts:
        return ""
    parts = []
    for imp in impacts:
        if not imp.asset or imp.asset not in _ASSETS_SET:
            continue
        if imp.direction not in _DIR_SET:
            continue
        parts.append(f"{imp.asset}:{imp.direction}:{int(imp.confidence)}")
    return ";".join(parts)


def decode_impacts(encoded: str) -> List[Dict[str, Any]]:
    """Décodage tolérant. Retourne liste de dicts {asset, direction, confidence}.
    Entrées invalides silencieusement ignorées (rétro-compat avec lignes vides)."""
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
        try:
            confidence = int(parts[2].strip()) if len(parts) >= 3 and parts[2].strip() else 0
        except ValueError:
            confidence = 0
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
