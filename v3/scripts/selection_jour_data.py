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

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import selection_jour as sj

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
    prix_reference: Dict[str, float],
    fiche_meta: Dict[str, Dict[str, str]],
    get_closes: Callable[[str], List[float]],
    get_price_at: Callable[[str, datetime], Optional[float]],
) -> List[sj.AssetDay]:
    """Construit la liste des `AssetDay` (un par actif de `results`).

    - `fiche_meta` : {fiche_key: {"label", "ticker", "famille"}}.
    - `get_closes(fiche_key)` : clôtures journalières oldest→newest (porte momentum).
    - `get_price_at(fiche_key, dt)` : prix au timestamp `dt` (pour le move post-news).
      Retourne None si indisponible → consommé non calculé (anti-faux-négatif : on
      ne déclare jamais « déjà coté » sans preuve de prix).
    Aucune exception ne remonte : un actif sans données reste présent (sans news/
    momentum). NE SÉLECTIONNE RIEN.
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
            spot = prix_reference.get(key)
            p_news = get_price_at(key, ts) if isinstance(ts, datetime) else None
            raw = (spot / p_news - 1.0) if (spot and p_news) else None
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
        prev_close = closes[-1] if closes else None
        spot = prix_reference.get(key)
        session_move = (spot / prev_close - 1.0) if (spot and prev_close) else None
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
    top 3 du jour. Tout échec (réseau, parsing) → [] (le bulletin garde sa
    Sélection de repli côté appelant). Les prix sont mémoïsés par actif (1 fetch
    journalier + 1 horaire max par actif)."""
    try:
        import briefing as B  # noqa: PLC0415
        import criteres_calculator as cc  # noqa: PLC0415

        events = B.parse_events_with_ingest_ts(events_path)
        meta = load_fiche_meta(fiches_dir)
        daily: Dict[str, List[float]] = {}
        hourly: Dict[str, List] = {}

        def get_closes(key: str) -> List[float]:
            if key in daily:
                return daily[key]
            t = meta.get(key, {}).get("ticker", "")
            serie = cc.fetch_twelve_series(t, interval="1day", outputsize=15) if t else None
            daily[key] = [c for _, c in (serie or [])]
            return daily[key]

        def get_price_at(key: str, dt: datetime) -> Optional[float]:
            t = meta.get(key, {}).get("ticker", "")
            if not t:
                return None
            if key not in hourly:
                hourly[key] = cc.fetch_twelve_series(t, interval="1h", outputsize=48) or []
            prior = [c for (bdt, c) in hourly[key] if bdt <= dt]
            return prior[-1] if prior else None

        assets = assemble_assets(
            results, events, now,
            prix_reference=prix_reference or {}, fiche_meta=meta,
            get_closes=get_closes, get_price_at=get_price_at,
        )
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
