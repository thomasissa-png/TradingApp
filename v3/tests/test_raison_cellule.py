"""Tests ciblés — « raison principale » par cellule (Synthèse des décisions).

Couvre les garanties de l'audit `/tmp/audit-marche-raisons.md` :
  (a) la raison va TOUJOURS dans le sens de la conclusion (jamais à contre-sens,
      cas S&P 7j net-carrier) ;
  (b) quasi-neutre (|note| < NEUTRAL_BAND) → libellé neutre, pas de direction ;
  (c) gate (⚑ FOMC) jamais cité ;
  (d) fallback nom canonique si driver hors config ;
  (e) meteo_cacao → phrase neutre (signe douteux) ;
  (f) verrou PUR RENDU : aucune mutation de conclusion/score.

PUR RENDU : zéro LLM, zéro réseau.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import scoring_analyste as sa  # noqa: E402


def _crit(
    nom: str,
    cle: str,
    contribs: Dict[str, float],
    *,
    signe: int = 1,
    is_gate: bool = False,
    is_na: bool = False,
) -> sa.CritereResult:
    return sa.CritereResult(
        id=cle,
        nom=nom,
        type_norm="lineaire",
        valeur_brute=1.0,
        valeur_norm=1.0,
        poids=5.0,
        signe=signe,
        pertinence={h: 1.0 for h in sa.HORIZONS},
        note="",
        contributions=dict(contribs),
        cle_courante=cle,
        is_gate=is_gate,
        gate_active=is_gate,
        is_na=is_na,
    )


def _actif(
    nom: str,
    criteres: List[sa.CritereResult],
    scores: Dict[str, float],
    conclusions: Dict[str, str],
) -> sa.ActifResult:
    return sa.ActifResult(
        nom=nom,
        fiche_key=nom.lower(),
        criteres=criteres,
        scores=dict(scores),
        conclusions=dict(conclusions),
        tie_break_notes={},
        scores_pond={h: 0.0 for h in sa.HORIZONS},
        conclusions_pond={h: "" for h in sa.HORIZONS},
        tie_break_notes_pond={},
        diverge={h: False for h in sa.HORIZONS},
        coverage=1.0,
        confidence={h: "normale" for h in sa.HORIZONS},
    )


# ---------------------------------------------------------------------------
# (a) net-carrier : jamais à contre-sens (cas S&P 7j)
# ---------------------------------------------------------------------------

def test_sp500_7j_net_carrier_jamais_contre_sens():
    """S&P 7j LONG (+5.52) alors que le plus fort |effet| est `taux_10y_us_reels_tips`
    (−6.51, pousse SHORT). La raison DOIT venir d'un porteur LONG (taux 10a / crédit),
    JAMAIS du driver baissier dominant en |effet|."""
    h = "7j"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.51}),
        _crit("Variation taux 10a", "variation_taux_10y_5j", {h: +5.07}),
        _crit("Spread crédit HY", "credit_spread_hy_us", {h: +4.18}),
        _crit("Régime VIX", "vix_regime_seuils", {h: +4.68}),
    ]
    r = _actif("S&P 500", crit, {h: +5.52}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    # Le porteur NET dominant côté LONG est variation_taux_10y_5j (+5.07).
    assert "taux longs US qui refluent" in raison
    assert "(+5.1)" in raison
    # Garantie dure : aucune phrase baissière de taux réels (driver à contre-sens).
    assert "coûtent à porter" not in raison
    assert "taux réels US élevés" not in raison


def test_or_24h_short_driver_taux_reels():
    """Or 24h SHORT (−7.82) : driver porteur SHORT = taux réels élevés."""
    h = "24h"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91}),
        _crit("Géopolitique", "tension_geopolitique", {h: -1.20}),
    ]
    r = _actif("Or", crit, {h: -7.82}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "taux réels US élevés" in raison
    assert "(-3.9)" in raison


# ---------------------------------------------------------------------------
# (b) quasi-neutre → libellé neutre, pas de direction
# ---------------------------------------------------------------------------

def test_vix_7j_quasi_neutre_pas_de_direction():
    """VIX 7j LONG (+0.07) mais |note| < NEUTRAL_BAND → quasi-neutre.
    Driver dominant en |effet| est baissier (term structure −8.00) : on ne doit
    NI raconter une direction LONG, NI citer le driver baissier."""
    h = "7j"
    crit = [
        _crit("Structure de vol", "vix_term_structure", {h: -8.00}),
        _crit("Niveau VIX", "vix_niveau_absolu", {h: +4.04}),
    ]
    r = _actif("VIX", crit, {h: +0.07}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert raison == sa._RAISON_QUASI_NEUTRE
    assert "(" not in raison  # aucune contribution chiffrée


def test_cac_1m_quasi_neutre():
    h = "1m"
    crit = [_crit("Spread OAT-Bund", "ecart_taux_fr_de_10a", {h: -3.40})]
    r = _actif("CAC 40", crit, {h: -0.10}, {h: "SHORT"})
    assert sa._raison_cellule(r, h) == sa._RAISON_QUASI_NEUTRE


# ---------------------------------------------------------------------------
# (c) gate FOMC jamais cité
# ---------------------------------------------------------------------------

def test_gate_fomc_jamais_cite():
    """Un gate ⚑ actif (même avec un gros effet apparent) n'est JAMAIS le driver
    de la raison — il est exclu par `is_gate`."""
    h = "24h"
    crit = [
        _crit("Drapeau régime FOMC", "gate_fomc", {h: -99.0}, is_gate=True),
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91}),
    ]
    r = _actif("Or", crit, {h: -7.82}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "FOMC" not in raison
    assert "régime" not in raison.lower()
    assert "taux réels US élevés" in raison


# ---------------------------------------------------------------------------
# (d) fallback nom canonique si driver hors config
# ---------------------------------------------------------------------------

def test_fallback_nom_canonique_hors_config():
    h = "24h"
    crit = [_crit("Critère exotique XYZ", "driver_inconnu_hors_biblio", {h: +2.50})]
    r = _actif("Actif X", crit, {h: +2.50}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    # Le corps + chiffre restent le fallback nom canonique ; N1 (force) + B2 (◧
    # mono-critère, seul critère porteur) s'ajoutent désormais (enrichissement 10/10).
    assert raison.startswith("Critère exotique XYZ (+2.5)")
    assert "◧" in raison  # mono-critère hérité de la cellule
    assert "[conviction" in raison  # repère d'actionnabilité N1


def test_donnee_absente_tiret():
    """Aucun contributeur dans le sens de la conclusion → « — » (jamais de crash)."""
    h = "24h"
    # Conclusion LONG mais le seul critère pousse SHORT → aucun porteur LONG.
    crit = [_crit("Critère contraire", "driver_inconnu_hors_biblio", {h: -2.50})]
    r = _actif("Actif Y", crit, {h: +0.50}, {h: "LONG"})
    assert sa._raison_cellule(r, h) == "—"


# ---------------------------------------------------------------------------
# (e) meteo_cacao → phrase neutre (signe douteux)
# ---------------------------------------------------------------------------

def test_meteo_cacao_phrase_neutre():
    h = "24h"
    crit = [_crit("Météo cacao", "meteo_cacao_cote_ivoire_ghana", {h: +1.37})]
    r = _actif("Cacao", crit, {h: +1.75}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert "convention de signe à valider" in raison
    # Pas d'assertion directionnelle bullish/bearish assénée.
    assert "bonne récolte" not in raison


# ---------------------------------------------------------------------------
# matching par préfixe (familles à suffixe d'actif)
# ---------------------------------------------------------------------------

def test_prefixe_momentum_prix():
    h = "24h"
    crit = [_crit("Tendance Brent 20j", "momentum_prix_20j_petrole", {h: -3.38})]
    r = _actif("Pétrole (Brent)", crit, {h: -3.30}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "tendance 20 jours baissière" in raison
    assert "(-3.4)" in raison


# ---------------------------------------------------------------------------
# (f) verrou PUR RENDU : aucune mutation de conclusion/score
# ---------------------------------------------------------------------------

def test_pur_rendu_aucune_mutation():
    h = "7j"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -6.51}),
        _crit("Régime VIX", "vix_regime_seuils", {h: +4.68}),
    ]
    r = _actif("S&P 500", crit, {h: +5.52}, {h: "LONG"})
    score_avant = dict(r.scores)
    conc_avant = dict(r.conclusions)
    contribs_avant = [dict(c.contributions) for c in r.criteres]
    _ = sa._raison_cellule(r, h)
    _ = sa.build_raisons_block([r])
    assert r.scores == score_avant
    assert r.conclusions == conc_avant
    assert [dict(c.contributions) for c in r.criteres] == contribs_avant


def test_build_block_structure():
    """Le bloc compact contient une ligne par actif, format scannable."""
    h = "24h"
    crit = [_crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91})]
    scores = {hz: (-7.82 if hz == "24h" else 0.0) for hz in sa.HORIZONS}
    conc = {hz: ("SHORT" if hz == "24h" else sa.CONCLUSION_INSUFFISANT) for hz in sa.HORIZONS}
    r = _actif("Or", crit, scores, conc)
    lines = sa.build_raisons_block([r])
    joined = "\n".join(lines)
    assert "**Or**" in joined
    assert "24h :" in joined and "7j :" in joined and "1m :" in joined
    assert "_(SHORT)_" in joined  # direction rappelée sur la cellule franche


# ===========================================================================
# Helpers enrichis (drapeaux, news-pondération, source_track) pour B1/B2/B3.
# ===========================================================================

def _crit_full(
    nom: str,
    cle: str,
    contribs: Dict[str, float],
    *,
    signe: int = 1,
    source_track: str = "",
    is_denial: bool = False,
    event_date: str = "",
) -> sa.CritereResult:
    c = _crit(nom, cle, contribs, signe=signe)
    c.source_track = source_track
    c.is_denial = is_denial
    c.event_date = event_date
    return c


def _actif_full(
    nom: str,
    criteres: List[sa.CritereResult],
    scores: Dict[str, float],
    conclusions: Dict[str, str],
    *,
    scores_pond: Optional[Dict[str, float]] = None,
    conclusions_pond: Optional[Dict[str, str]] = None,
    news_cap_info: Optional[Dict[str, Dict[str, float]]] = None,
    divergence_quant_news: Optional[Dict[str, bool]] = None,
    confidence: Optional[Dict[str, str]] = None,
) -> sa.ActifResult:
    r = _actif(nom, criteres, scores, conclusions)
    if scores_pond is not None:
        r.scores_pond = dict(scores_pond)
    if conclusions_pond is not None:
        r.conclusions_pond = dict(conclusions_pond)
    if news_cap_info is not None:
        r.news_cap_info = {h: dict(v) for h, v in news_cap_info.items()}
    if divergence_quant_news is not None:
        r.divergence_quant_news = dict(divergence_quant_news)
    if confidence is not None:
        r.confidence = dict(confidence)
    return r


# ---------------------------------------------------------------------------
# B2 — héritage des drapeaux de prudence (la raison ne dit pas plus que le système)
# ---------------------------------------------------------------------------

def test_b2_nasdaq_24h_herite_divergence_et_deja_cote():
    """Nasdaq 24h LONG news-pondéré : la raison hérite ↯ (divergence) ET ⌛
    (déjà coté, event news du 16/06 vu en 24h) ET 📰 (news-pondéré)."""
    h = "24h"
    now = datetime(2026, 6, 17, 7, 23, tzinfo=timezone.utc)
    crit = [
        _crit_full("Tendance semi-conducteurs", "sox_trend_5j", {h: +4.20}),
        _crit_full(
            "Sentiment IA/méga-caps", "sentiment_ia_megacaps", {h: +1.34},
            source_track="ia_synthese", event_date="2026-06-16T00:00:00+00:00",
        ),
    ]
    r = _actif_full(
        "Nasdaq", crit, {h: +2.86}, {h: "LONG"},
        scores_pond={h: +1.01}, conclusions_pond={h: "LONG"},
        news_cap_info={h: {"news_total_pm1": 3.2, "quant_total_pm1": -0.34}},
        divergence_quant_news={h: True},
    )
    raison = sa._raison_cellule(r, h, now)
    assert "↯" in raison        # divergence héritée
    assert "⌛" in raison        # déjà coté hérité
    assert "📰" in raison        # news-pondéré hérité (B3)


# ---------------------------------------------------------------------------
# B3 — chiffre pondéré (pas brut) quand 📰 : jamais de contradiction avec la note
# ---------------------------------------------------------------------------

def test_b3_nasdaq_24h_chiffre_pondere_pas_brut():
    """La raison ne doit PAS afficher « +4.2 » seul (contradiction avec la note
    pondérée +1.01 de la colonne) : elle cite la note pondérée (brut→pondéré)."""
    h = "24h"
    now = datetime(2026, 6, 17, 7, 23, tzinfo=timezone.utc)
    crit = [
        _crit_full("Tendance semi-conducteurs", "sox_trend_5j", {h: +4.20}),
        _crit_full(
            "Sentiment IA/méga-caps", "sentiment_ia_megacaps", {h: +1.34},
            source_track="ia_synthese",
        ),
    ]
    r = _actif_full(
        "Nasdaq", crit, {h: +2.86}, {h: "LONG"},
        scores_pond={h: +1.01}, conclusions_pond={h: "LONG"},
        news_cap_info={h: {"news_total_pm1": 3.2, "quant_total_pm1": -0.34}},
    )
    raison = sa._raison_cellule(r, h, now)
    assert "+1.0 pondéré" in raison       # note pondérée de la colonne
    assert "brut +2.9" in raison          # brut montré comme la colonne
    assert "(+4.2)" not in raison         # JAMAIS le brut du driver seul


# ---------------------------------------------------------------------------
# B1 — co-driver news co-dominant mentionné (Pétrole 7j)
# ---------------------------------------------------------------------------

def test_b1_petrole_7j_codriver_opec_news():
    """Pétrole 7j SHORT : momentum −5.6 (principal) vs OPEC+ −5.4 (news, quasi-
    égal) → la raison DOIT mentionner OPEC+ (news), pas masquer ce co-driver."""
    h = "7j"
    now = datetime(2026, 6, 17, 7, 23, tzinfo=timezone.utc)
    crit = [
        _crit_full("Tendance Brent 20j", "momentum_prix_20j_petrole", {h: -5.63}),
        _crit_full(
            "Politique OPEC+", "opec_production_policy", {h: -5.40},
            source_track="ia_synthese",
        ),
        _crit_full(
            "Tension Moyen-Orient", "tension_geopol_moyen_orient", {h: -4.20},
            source_track="ia_synthese",
        ),
    ]
    r = _actif_full(
        "Pétrole (Brent)", crit, {h: -15.88}, {h: "SHORT"},
        scores_pond={h: -10.31}, conclusions_pond={h: "SHORT"},
        news_cap_info={h: {"news_total_pm1": -9.6, "quant_total_pm1": -6.28}},
    )
    raison = sa._raison_cellule(r, h, now)
    assert "tendance 20 jours baissière" in raison      # driver principal (momentum)
    assert "OPEC+" in raison                            # co-driver news B1
    assert "(news)" in raison                           # étiqueté news
    assert "📰" in raison                                # news-pondéré hérité


# ---------------------------------------------------------------------------
# N1 — repère d'actionnabilité (force) sur cellule franche
# ---------------------------------------------------------------------------

def test_n1_force_presente_sur_cellule_franche():
    """Cellule franche (|note| ≥ seuil) sans drapeau → conviction « forte »
    présente dans la raison (lentille Spéculateur)."""
    h = "24h"
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips", {h: -3.91}),
        _crit("Géopolitique", "tension_geopolitique", {h: -3.50}),
        _crit("Variation taux 10a", "variation_taux_10y_5j", {h: -3.00}),
    ]
    r = _actif("Or", crit, {h: -7.82}, {h: "SHORT"})
    raison = sa._raison_cellule(r, h)
    assert "[conviction forte]" in raison


def test_n1_pas_de_force_sur_quasi_neutre():
    """Quasi-neutre → pas de force assénée (reste « pas de driver franc »)."""
    h = "7j"
    crit = [_crit("Structure de vol", "vix_term_structure", {h: -8.00})]
    r = _actif("VIX", crit, {h: +0.07}, {h: "LONG"})
    raison = sa._raison_cellule(r, h)
    assert raison == sa._RAISON_QUASI_NEUTRE
    assert "conviction" not in raison


# ---------------------------------------------------------------------------
# N2 — regroupement des horizons au MÊME driver
# ---------------------------------------------------------------------------

def test_n2_regroupe_horizons_meme_driver():
    """Or : 24h/7j/1m portés par le MÊME driver (taux réels) → 1 puce regroupée
    « même driver — … (−3.9 / −7.8 / −7.8) » au lieu de 3 répétitions."""
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips",
              {"24h": -3.91, "7j": -7.80, "1m": -7.80}),
    ]
    r = _actif(
        "Or", crit,
        {"24h": -7.82, "7j": -10.07, "1m": -8.59},
        {"24h": "SHORT", "7j": "SHORT", "1m": "SHORT"},
    )
    lines = sa.build_raisons_block([r])
    joined = "\n".join(lines)
    assert "24h/7j/1m : même driver" in joined
    assert "(-3.9 / -7.8 / -7.8)" in joined
    # Une SEULE occurrence de la phrase (pas 3 répétitions).
    assert joined.count("l'or/les sans-rendement coûtent à porter") == 1


def test_n2_garde_detail_quand_drivers_differents():
    """Nasdaq : drivers DIFFÉRENTS par horizon (semi-conducteurs en 24h, taux
    réels en 7j/1m) → on NE regroupe PAS le 24h ; 7j/1m (même driver) regroupés."""
    crit = [
        _crit("Tendance semi-conducteurs", "sox_trend_5j",
              {"24h": +4.20, "7j": 0.0, "1m": 0.0}),
        _crit("Taux réels US", "taux_10y_us_reels_tips",
              {"24h": -2.0, "7j": -7.20, "1m": -7.20}),
    ]
    r = _actif(
        "Nasdaq", crit,
        {"24h": +2.86, "7j": -1.50, "1m": -3.42},
        {"24h": "LONG", "7j": "SHORT", "1m": "SHORT"},
    )
    lines = sa.build_raisons_block([r])
    joined = "\n".join(lines)
    assert "24h : semi-conducteurs" in joined        # 24h détaillé (driver distinct)
    assert "7j/1m : même driver" in joined           # 7j/1m regroupés (taux réels)


# ===========================================================================
# B2-EXACT — VERROU ANTI-DIVERGENCE : drapeaux(raison) == drapeaux(grille Synthèse)
# ===========================================================================
# Audit round 2 (9/10) : la raison passait par `_compute_cell_risk_flags` (jeu de
# prédicats parallèle) avec un `now` distinct de la grille → VIX 24h portait ⌛ en
# trop, Pétrole 24h un ⌛ faux. Désormais la raison ET la grille tirent leurs
# drapeaux de prudence de l'UNIQUE `_synthese_cell_risk_flags` au MÊME `now`.
# Ce verrou re-rend un VRAI bulletin (render_bulletin), parse la grille de Synthèse
# ET le bloc « Raison principale », et exige l'égalité cellule par cellule.

import re as _re

# Symboles STRUCTURELS de la grille jamais portés par la raison (hors périmètre
# « prudence ») : à retirer de la cellule de grille avant comparaison.
_FLAGS_STRUCTURELS = {"⚑", "≈", "⚪", "🚫"}
# Tous les symboles de prudence possibles (ordre indifférent pour l'extraction).
_FLAGS_PRUDENCE = ["📰", "⏸", "⚠️", "◧", "↯", "⇄", "⇆", "⌛", "⊘"]


def _prudence_from_grid_cell(cell: str) -> List[str]:
    """Extrait, DANS L'ORDRE, les symboles de prudence rendus dans une cellule de
    la grille de Synthèse (en ignorant le texte « régime news (54%) », « maintenu »,
    les chiffres et les symboles structurels ⚑/≈/⚪)."""
    out: List[str] = []
    for ch in cell:
        if ch in _FLAGS_STRUCTURELS:
            continue
        if ch in _FLAGS_PRUDENCE and (not out or out[-1] != ch):
            out.append(ch)
    return out


def _prudence_from_raison_segment(seg: str) -> List[str]:
    """Extrait, dans l'ordre, les symboles de prudence d'un segment de raison
    (« 24h : … 📰 ↯ _(SHORT)_ »)."""
    out: List[str] = []
    for ch in seg:
        if ch in _FLAGS_PRUDENCE and (not out or out[-1] != ch):
            out.append(ch)
    return out


def _parse_bulletin_flags(md: str, results=None):
    """Retourne deux dicts {(actif, horizon): [symboles]} de drapeaux de prudence.

    - `grid` : lus depuis la grille « ## Synthèse des décisions » du bulletin
      rendu (chaque cellule porte désormais AUSSI sa raison « <br>· driver »,
      point #3 — on n'extrait ici que les drapeaux de prudence du cœur de cellule).
    - `raison` : lus depuis `build_raisons_block(results)`, le chemin de code
      INDÉPENDANT (`_raison_flags_suffix`) qui doit rester aligné sur la grille
      (verrou anti-divergence B2-exact). On le calcule directement plutôt que de
      parser un bloc « Raison principale » désormais retiré du bulletin (point #3 :
      la raison vit dans la cellule, le bloc-liste redondant a été supprimé).
    """
    lines = md.splitlines()
    grid: Dict[tuple, List[str]] = {}
    raison: Dict[tuple, List[str]] = {}
    in_synth = False
    for ln in lines:
        if ln.startswith("## Synthèse des décisions"):
            in_synth = True
            continue
        if in_synth and ln.startswith("## "):
            in_synth = False
        # Lignes de grille : « | Actif | c24 | c7j | c1m | »
        if in_synth and ln.startswith("| ") and " | " in ln and not ln.startswith("| Actif"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) == 4 and cells[0] not in ("", "---"):
                actif = cells[0]
                for h, cell in zip(sa.HORIZONS, cells[1:]):
                    grid[(actif, h)] = _prudence_from_grid_cell(cell)
        # Bloc raison (chemin indépendant) : « - **Actif** : 24h : … · 7j : … »
        m = _re.match(r"- \*\*(.+?)\*\* : (.+)$", ln)
        if m:
            actif = m.group(1)
            body = m.group(2)
            for seg in body.split(" · "):
                hm = _re.match(r"\s*(24h|7j|1m)(?:/(?:24h|7j|1m))* : (.+)$", seg)
                if not hm:
                    continue
                # Cas regroupé « 7j/1m : … » → applique aux deux horizons du groupe.
                hzs = _re.findall(r"(24h|7j|1m)", seg.split(" : ", 1)[0])
                syms = _prudence_from_raison_segment(seg)
                for h in hzs:
                    raison[(actif, h)] = syms
    # [Point #3] Le bloc « Raison principale » n'est plus dans le bulletin : on
    # rejoue `build_raisons_block` (chemin de code indépendant de la grille) pour
    # conserver le verrou anti-divergence raison ↔ grille sur ses propres lignes.
    if results is not None:
        raison_md = "\n".join(sa.build_raisons_block(results, _NOW_BULLETIN))
        for ln in raison_md.splitlines():
            m = _re.match(r"- \*\*(.+?)\*\* : (.+)$", ln)
            if not m:
                continue
            actif = m.group(1)
            body = m.group(2)
            for seg in body.split(" · "):
                hm = _re.match(r"\s*(24h|7j|1m)(?:/(?:24h|7j|1m))* : (.+)$", seg)
                if not hm:
                    continue
                hzs = _re.findall(r"(24h|7j|1m)", seg.split(" : ", 1)[0])
                syms = _prudence_from_raison_segment(seg)
                for h in hzs:
                    raison[(actif, h)] = syms
    return grid, raison


def _make_news_weighted_short(nom: str, h: str, *, event_date: str = "",
                              divergence: bool = False) -> sa.ActifResult:
    """Cellule SHORT news-pondérée (📰) — reproduit VIX/Pétrole 24h de la grille."""
    crit = [
        _crit_full("Tendance 20j", f"momentum_prix_20j_{nom.lower()}", {h: -3.30},
                   event_date=event_date),
        _crit_full("Driver news", f"news_{nom.lower()}", {h: -2.50},
                   source_track="ia_synthese", event_date=event_date),
    ]
    scores = {hz: (-3.30 if hz == h else 0.0) for hz in sa.HORIZONS}
    conc = {hz: ("SHORT" if hz == h else sa.CONCLUSION_INSUFFISANT) for hz in sa.HORIZONS}
    return _actif_full(
        nom, crit, scores, conc,
        scores_pond={hz: (-1.63 if hz == h else 0.0) for hz in sa.HORIZONS},
        conclusions_pond={hz: ("SHORT" if hz == h else "") for hz in sa.HORIZONS},
        news_cap_info={h: {"news_total_pm1": -5.0, "quant_total_pm1": -3.3}},
        divergence_quant_news={hz: (divergence and hz == h) for hz in sa.HORIZONS},
    )


# `now` = bulletin (2026-06-17 07h). Un event du 17/06 n'est PAS encore already-priced
# en 24h à cette date → AUCUN ⌛ (c'était le bug : à J+1 il le devenait).
_NOW_BULLETIN = datetime(2026, 6, 17, 7, 0, tzinfo=timezone.utc)


def test_b2_exact_vix_24h_pas_de_deja_cote():
    """VIX 24h (event du 17/06, pas encore already-priced en 24h au 17/06) :
    PAS de ⌛ — ni dans la grille, ni dans la raison ; et grille == raison."""
    r = _make_news_weighted_short("VIX", "24h", event_date="2026-06-17T00:00:00+00:00")
    md = sa.render_bulletin([r], {}, _NOW_BULLETIN, "h", "ok")
    grid, raison = _parse_bulletin_flags(md, [r])
    assert "⌛" not in grid[("VIX", "24h")], grid[("VIX", "24h")]
    assert "⌛" not in raison[("VIX", "24h")], raison[("VIX", "24h")]
    assert "📰" in raison[("VIX", "24h")]
    # Égalité stricte grille ↔ raison (le verrou anti-divergence).
    assert raison[("VIX", "24h")] == grid[("VIX", "24h")]


def test_b2_exact_petrole_24h_pas_de_deja_cote():
    """Pétrole 24h (event du 17/06) : PAS de ⌛, 📰 présent, grille == raison."""
    r = _make_news_weighted_short("Pétrole (Brent)", "24h",
                                  event_date="2026-06-17T00:00:00+00:00")
    md = sa.render_bulletin([r], {}, _NOW_BULLETIN, "h", "ok")
    grid, raison = _parse_bulletin_flags(md, [r])
    assert "⌛" not in grid[("Pétrole (Brent)", "24h")]
    assert "⌛" not in raison[("Pétrole (Brent)", "24h")]
    assert "📰" in raison[("Pétrole (Brent)", "24h")]
    assert raison[("Pétrole (Brent)", "24h")] == grid[("Pétrole (Brent)", "24h")]


def test_b2_exact_event_anterieur_garde_le_deja_cote():
    """Non-régression : un event du 16/06 EST already-priced en 24h au 17/06 →
    ⌛ présent dans la grille ET dans la raison (le verrou ne sur-corrige pas)."""
    r = _make_news_weighted_short("Café (Arabica)", "24h",
                                  event_date="2026-06-16T00:00:00+00:00")
    md = sa.render_bulletin([r], {}, _NOW_BULLETIN, "h", "ok")
    grid, raison = _parse_bulletin_flags(md, [r])
    assert "⌛" in grid[("Café (Arabica)", "24h")]
    assert "⌛" in raison[("Café (Arabica)", "24h")]


def test_b2_exact_balayage_grille_egale_raison():
    """VERROU GÉNÉRAL : sur un bulletin multi-actifs/horizons, pour CHAQUE cellule
    directionnelle, les drapeaux de prudence de la raison == ceux de la grille."""
    actifs = [
        _make_news_weighted_short("VIX", "24h", event_date="2026-06-17T00:00:00+00:00"),
        _make_news_weighted_short("Pétrole (Brent)", "24h",
                                  event_date="2026-06-17T00:00:00+00:00", divergence=True),
        _make_news_weighted_short("Café (Arabica)", "24h",
                                  event_date="2026-06-16T00:00:00+00:00"),
    ]
    # Un actif quant pur multi-horizons (mono-critère → ◧) pour couvrir ◧.
    crit = [_crit("Taux 2 ans", "spread_taux_2y_us_de",
                  {"24h": -8.0, "7j": -14.0, "1m": -14.0})]
    eurusd = _actif("EUR/USD", crit,
                    {"24h": -8.18, "7j": -14.17, "1m": -13.85},
                    {"24h": "SHORT", "7j": "SHORT", "1m": "SHORT"})
    actifs.append(eurusd)

    md = sa.render_bulletin(actifs, {}, _NOW_BULLETIN, "h", "ok")
    grid, raison = _parse_bulletin_flags(md, actifs)
    # Chaque cellule directionnelle présente dans la raison doit matcher la grille.
    checked = 0
    for key, raison_syms in raison.items():
        assert key in grid, f"cellule {key} absente de la grille"
        assert raison_syms == grid[key], (
            f"DIVERGENCE {key} : raison={raison_syms} != grille={grid[key]}"
        )
        checked += 1
    assert checked >= 6  # au moins 6 cellules directionnelles balayées


# ===========================================================================
# N3 — chiffres HOMOGÈNES dans un groupe (jamais note pondérée + effet brut mêlés)
# ===========================================================================

def test_n3_groupe_chiffres_homogenes_nasdaq():
    """Nasdaq 7j (news-pondéré : « −2.1 pondéré, brut −1.5 ») et 1m (effet brut
    « −7.2 ») ont une sémantique de chiffre DIFFÉRENTE → on NE les regroupe PAS
    (sinon « −2.1 pondéré, brut −1.5 / −7.2 » mêlerait note pondérée et effet)."""
    crit = [
        _crit_full("Taux réels US", "taux_10y_us_reels_tips",
                   {"7j": -1.50, "1m": -7.20}),
    ]
    r = _actif_full(
        "Nasdaq", crit,
        {"24h": 0.0, "7j": -1.50, "1m": -7.20},
        {"24h": sa.CONCLUSION_INSUFFISANT, "7j": "SHORT", "1m": "SHORT"},
        # 7j news-pondéré (📰), 1m non → sémantique de chiffre différente.
        scores_pond={"7j": -2.10, "1m": -7.20},
        conclusions_pond={"7j": "SHORT", "1m": ""},
        news_cap_info={"7j": {"news_total_pm1": -3.0, "quant_total_pm1": -1.5}},
    )
    joined = "\n".join(sa.build_raisons_block([r], _NOW_BULLETIN))
    # JAMAIS la parenthèse hétérogène mêlant pondéré et effet brut.
    assert "-2.1 pondéré, brut -1.5 / -7.2" not in joined
    # 7j garde sa sémantique pondérée homogène, 1m sa sémantique d'effet, séparés.
    assert "-2.1 pondéré, brut -1.5" in joined
    assert "(-7.2)" in joined


def test_n3_groupe_homogene_reste_groupe():
    """Non-régression N2 : deux horizons de MÊME sémantique (effet brut tous deux)
    et même driver RESTENT regroupés (le verrou N3 ne casse pas les groupes sains)."""
    crit = [
        _crit("Taux réels US", "taux_10y_us_reels_tips",
              {"24h": -3.91, "7j": -7.80, "1m": -7.80}),
    ]
    r = _actif(
        "Or", crit,
        {"24h": -7.82, "7j": -10.07, "1m": -8.59},
        {"24h": "SHORT", "7j": "SHORT", "1m": "SHORT"},
    )
    joined = "\n".join(sa.build_raisons_block([r], _NOW_BULLETIN))
    assert "24h/7j/1m : même driver" in joined
    assert "(-3.9 / -7.8 / -7.8)" in joined
