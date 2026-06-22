"""Couche d'ASSEMBLAGE du moteur « top 3 du jour » (selection_jour).

Transforme les données brutes du run (résultats de fond + events-log + prix) en
`AssetDay` exploitables par le moteur pur `selection_jour`. La partie PURE
(`assemble_assets`) reçoit ses prix via des callables injectés → testable sans
réseau. La partie LIVE (`compute_top3`) câble ces callables sur `market_data` et
reste BEST-EFFORT : toute panne dégrade proprement (jamais de crash du bulletin).

Découpage volontaire : aucune logique de SÉLECTION ici (elle est dans
`selection_jour`). Ici on ne fait que rassembler les faits.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import selection_jour as sj

logger = logging.getLogger(__name__)

# Mapping code-actif IA (events-log `impacts`) → libellé actif. Réutilise la table
# de référence de briefing (source unique), import paresseux/tolérant.
try:  # pragma: no cover - dépend de l'environnement d'exécution
    from briefing import _IA_ASSET_TO_LABEL as _CODE_TO_LABEL  # type: ignore
except Exception:  # noqa: BLE001
    _CODE_TO_LABEL = {}


def _favorable(raw_move: Optional[float], direction: str) -> Optional[float]:
    """Mouvement signé DANS LE SENS du pari (LONG→+, SHORT→inverse)."""
    if raw_move is None:
        return None
    return raw_move if direction == "LONG" else -raw_move


def assemble_assets(
    results: List[Any],
    events: List[Dict[str, Any]],
    now: datetime,
    *,
    fiche_meta: Dict[str, Dict[str, str]],
    get_closes: Callable[[str], List[float]],
    get_session_move: Callable[[str], Optional[float]],
    get_post_news_move: Callable[[str, datetime], Optional[float]],
) -> List[sj.AssetDay]:
    """Construit la liste des `AssetDay` (un par actif de `results`).

    - `fiche_meta` : {fiche_key: {"label", "ticker", "famille"}}.
    - `get_closes(fiche_key)` : clôtures journalières oldest→newest (porte momentum).
    - `get_session_move(fiche_key)` : mouvement overnight SIGNÉ (prix courant vs
      clôture veille). Pour les indices cash fermés à 7h, la couche LIVE lit ce
      mouvement sur le FUTURE qui cote la nuit (proxy) → garde-fous « contradiction »
      et « déjà coté » actifs même marché fermé. None si indisponible.
    - `get_post_news_move(fiche_key, dt)` : mouvement BRUT (non signé) entre `dt` et
      maintenant (proxy-aware côté LIVE). None → consommé non calculé (anti-faux-
      négatif : on ne déclare jamais « déjà coté » sans preuve de prix).
    Aucune exception ne remonte. NE SÉLECTIONNE RIEN.
    """
    # label → fiche_key (pour rattacher les impacts news à l'actif).
    label_to_key = {getattr(r, "nom", ""): getattr(r, "fiche_key", "") for r in results}

    # News par actif (clé = fiche_key).
    news_par_key: Dict[str, List[sj.NewsItem]] = {}
    for ev in events:
        ts = ev.get("ingest_ts")
        materiality_ev = (ev.get("materiality", "") or "")
        for imp in _impacts(ev):
            label = _CODE_TO_LABEL.get(imp.get("asset", ""))
            key = label_to_key.get(label or "", "")
            if not key:
                continue
            direction = imp.get("direction", "")
            if direction not in ("LONG", "SHORT"):
                continue
            # Force du signal SPÉCIFIQUE à CET actif (3ᵉ champ de l'impact, ex.
            # « EURUSD:SHORT:medium »). C'est le bon niveau : une news high globale
            # peut n'avoir qu'un impact « low » sur un actif donné (ex. EURUSD:LONG:low
            # → ne doit PAS déclencher). On retombe sur la matérialité de l'event si
            # le champ par-impact est absent/inconnu.
            imp_conf = (imp.get("conf", "") or "").lower()
            materiality = imp_conf if imp_conf in ("high", "medium", "low") else materiality_ev
            raw = get_post_news_move(key, ts) if isinstance(ts, datetime) else None
            news_par_key.setdefault(key, []).append(
                sj.NewsItem(
                    direction=direction,
                    materiality=materiality,
                    reliability=(ev.get("reliability", "") or ""),
                    nature=(ev.get("nature", "") or ""),
                    ingest_ts=ts if isinstance(ts, datetime) else None,
                    resume=_resume(ev),
                    post_news_move=_favorable(raw, direction),
                )
            )

    assets: List[sj.AssetDay] = []
    for r in results:
        key = getattr(r, "fiche_key", "")
        meta = fiche_meta.get(key, {})
        closes = list(get_closes(key) or [])
        session_move = get_session_move(key)
        fond_dir = ""
        conc = getattr(r, "conclusions", {}) or {}
        if conc.get("24h") in ("LONG", "SHORT"):
            fond_dir = conc["24h"]
        a = sj.AssetDay(
            actif=getattr(r, "nom", key),
            fiche_key=key,
            news=news_par_key.get(key, []),
            session_move=session_move,
            closes=closes,
            fond_dir=fond_dir,
        )
        a.groupe = meta.get("famille", "") or key
        assets.append(a)
    return assets


def _impacts(ev: Dict[str, Any]) -> List[Dict[str, str]]:
    """Liste d'impacts {asset, direction, conf} d'un event.

    Parse le format compact « ASSET:DIR:CONF;... » en CONSERVANT le 3ᵉ champ comme
    chaîne (high/medium/low) — contrairement à `briefing._parse_impacts_compact`
    qui le force en `int` et perd la matérialité par-impact (le cœur du bug de sens
    EUR/USD). Tolère une liste déjà décodée."""
    raw = ev.get("impacts")
    if isinstance(raw, list):
        return [
            {"asset": str(d.get("asset", "")).upper(),
             "direction": str(d.get("direction", "")).upper(),
             "conf": str(d.get("conf", d.get("confidence", "")) or "")}
            for d in raw if isinstance(d, dict)
        ]
    out: List[Dict[str, str]] = []
    for chunk in (raw or "").split(";"):
        parts = [p.strip() for p in chunk.split(":")]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            continue
        out.append({
            "asset": parts[0].upper(),
            "direction": parts[1].upper(),
            "conf": parts[2].lower() if len(parts) >= 3 else "",
        })
    return out


def _resume(ev: Dict[str, Any]) -> str:
    """Texte court d'une news (titre/trigger), tronqué pour l'affichage."""
    txt = (ev.get("trigger") or ev.get("l1") or ev.get("titre") or "").strip()
    return (txt[:68].rstrip() + "…") if len(txt) > 70 else txt


# ── Métadonnées des fiches (label / ticker / famille) ───────────────────────
def load_fiche_meta(fiches_dir: Path) -> Dict[str, Dict[str, str]]:
    """Lit les fiches YAML → {fiche_key: {label, ticker, famille}}. Best-effort."""
    out: Dict[str, Dict[str, str]] = {}
    if not fiches_dir.exists():
        return out
    try:
        import yaml  # type: ignore
    except Exception:  # noqa: BLE001
        return out
    for p in fiches_dir.glob("*.yml"):
        if p.stem.startswith("_"):
            continue
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:  # noqa: BLE001
            continue
        fm = data.get("frontmatter", data) if isinstance(data, dict) else {}
        out[p.stem] = {
            "label": str(fm.get("actif", fm.get("nom", p.stem))),
            "ticker": str(fm.get("ticker_principal", "")),
            "famille": str(fm.get("famille", "")),
        }
    return out


# AUDIT OVERNIGHT des 12 actifs (lecture du mouvement de nuit pour les garde-fous
# « contradiction de séance » et « déjà coté », à 7h Paris). RÉALITÉ DU STACK DE
# DONNÉES — MESURÉE SUR PIÈCES le 22/06 avec la clé Grow ACTIVE (workflow probe-data,
# run 27969365918), pas supposée :
#   - Journalier FRAIS (âge 0j) servi pour les 12 fiches ;
#   - Intraday 1h servi pour les 12 fiches, MAIS l'horizon diffère :
#       ✅ Or (GC=F), Argent (SI=F), Cuivre (HG=F), Pétrole (BZ=F), Café (KC=F),
#          Cacao (CC=F), Blé (ZW=F), EUR/USD (EUR=X) → barres 1h qui courent LA NUIT
#          (dernière barre 01:00–02:00 le lendemain) → garde-fous overnight ARMÉS.
#       ❌ S&P (^GSPC), Nasdaq (^IXIC), CAC (^FCHI), VIX (^VIX) → indices cash,
#          intraday s'arrête à la clôture (12:30 / 17:00) → PAS de prix de nuit à 7h.
#   - Aucune source overnight pour les indices, confirmée sur pièces : ES=F VIDE,
#     NQ=F VIDE, DX-Y.NYB VIDE (Twelve ne mappe aucun future CME ni le DXY → fallback
#     yfinance bloqué). SPY/QQQ frais mais s'arrêtent aussi à la clôture cash. Un proxy
#     « ES=F/NQ=F » serait INERTE (erreur déjà commise — corrigée). → PAS de proxy.
#
# Garde-fou prix indisponible la nuit (indices) : la news est quand même PRISE (anti-
# faux-négatif), seul « le prix contredit » manque jusqu'à l'ouverture du marché.
# Tous utilisent leur ticker propre ; aucun override n'est justifié (vérifié sur pièces).
PROXY_OVERNIGHT: Dict[str, str] = {}


# ── Câblage LIVE (réseau via market_data) — BEST-EFFORT, jamais de crash ─────
def compute_top3(
    results: List[Any],
    now: datetime,
    prix_reference: Dict[str, float],
    *,
    fiches_dir: Path,
    events_path: Path,
) -> List[sj.Pick]:
    """Assemble les données réelles (events-log + prix market_data) et renvoie le
    top 3 du jour. Tout échec (réseau, parsing) → [] (repli sur l'ancienne Sélection
    côté appelant). Prix mémoïsés par actif.

    Le momentum lit les clôtures du ticker CASH. Le mouvement OVERNIGHT (garde-fous
    contradiction / déjà-coté) lit le ticker PROXY (future) quand l'actif cash est
    fermé la nuit — sinon le ticker propre (actifs continus)."""
    try:
        import briefing as B  # noqa: PLC0415
        import criteres_calculator as cc  # noqa: PLC0415

        events = B.parse_events_with_ingest_ts(events_path)
        meta = load_fiche_meta(fiches_dir)
        daily_cash: Dict[str, List[float]] = {}
        hourly_ov: Dict[str, List] = {}
        prevclose_ov: Dict[str, Optional[float]] = {}

        def _overnight_ticker(key: str) -> str:
            return PROXY_OVERNIGHT.get(key) or meta.get(key, {}).get("ticker", "")

        def get_closes(key: str) -> List[float]:
            # Momentum : clôtures journalières du CASH (le cash a un historique propre).
            if key not in daily_cash:
                t = meta.get(key, {}).get("ticker", "")
                serie = cc.fetch_twelve_series(t, interval="1day", outputsize=15) if t else None
                daily_cash[key] = [c for _, c in (serie or [])]
            return daily_cash[key]

        def _hourly_ov(key: str) -> List:
            if key not in hourly_ov:
                t = _overnight_ticker(key)
                hourly_ov[key] = (cc.fetch_twelve_series(t, interval="1h", outputsize=48) or []) if t else []
            return hourly_ov[key]

        def _prevclose_ov(key: str) -> Optional[float]:
            if key not in prevclose_ov:
                t = _overnight_ticker(key)
                serie = cc.fetch_twelve_series(t, interval="1day", outputsize=5) if t else None
                vals = [c for _, c in (serie or [])]
                prevclose_ov[key] = vals[-1] if vals else None
            return prevclose_ov[key]

        def get_session_move(key: str) -> Optional[float]:
            bars = _hourly_ov(key)
            prev = _prevclose_ov(key)
            if not bars or not prev:
                return None
            current = bars[-1][1]
            return (current / prev - 1.0) if prev else None

        def get_post_news_move(key: str, dt: datetime) -> Optional[float]:
            bars = _hourly_ov(key)
            if not bars:
                return None
            prior = [c for (bdt, c) in bars if bdt <= dt]
            if not prior:
                return None
            return bars[-1][1] / prior[-1] - 1.0 if prior[-1] else None

        assets = assemble_assets(
            results, events, now, fiche_meta=meta,
            get_closes=get_closes, get_session_move=get_session_move,
            get_post_news_move=get_post_news_move,
        )
        # Diagnostic de couverture overnight (observable au lieu de supposé) : quels
        # actifs ont un prix de nuit (garde-fous armés) vs lesquels en sont privés.
        couverts = sorted(a.fiche_key for a in assets if a.session_move is not None)
        prives = sorted(a.fiche_key for a in assets if a.session_move is None)
        logger.info("top3 couverture overnight : armés=%s | sans prix de nuit=%s",
                    couverts or "—", prives or "—")
        ordre = [getattr(r, "fiche_key", "") for r in results]
        return sj.select_top3(assets, now, ordre)
    except Exception:  # noqa: BLE001 — best-effort : jamais bloquer le bulletin
        return []


# ── Rendu « décision d'abord » : le top 3 en tête du bulletin ────────────────
_PORTE_LABEL = {"news": "catalyseur news", "momentum": "momentum"}


def build_top3_block(
    picks: List[sj.Pick],
    prix_reference: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Bloc markdown « 🎯 Aujourd'hui » : les paris du jour, décision d'abord.
    Une ligne courte par pari (sens · prix · raison · porte). Vide assumé."""
    prix_reference = prix_reference or {}
    out: List[str] = ["## 🎯 Aujourd'hui", ""]
    if not picks:
        out.append("_Aucun pari qualifié aujourd'hui (ni catalyseur news, ni "
                   "momentum vivant) — on ne force pas._")
        out.append("")
        return out
    out.append("**Les paris du jour (max 3)** — visée +0,5 % en 24h")
    out.append("")
    for p in picks:
        px = prix_reference.get(p.fiche_key)
        px_str = f" @ {px:g}" if isinstance(px, (int, float)) else ""
        porte = _PORTE_LABEL.get(p.porte, p.porte)
        out.append(f"- **{p.actif}** {p.direction}{px_str} — {p.raison} · _{porte}_")
    out.append("")
    return out
