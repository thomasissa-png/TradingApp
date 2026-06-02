"""Tests gate C1 — cohérence de signe DeepSeek (v3/audit/gates-FINAL.md).

Couvre :
- Table de règles macro NON AMBIGUËS : détection sujet + surprise + conflit
- Cas réels : OPEP+production / CPI hot / Fed dovish / EIA stocks
- Cohérent (pas de conflit) → impact INTACT
- News sans pattern macro clair → ZÉRO faux positif
- Impact neutralisé → ne contribue pas au score
- Trace dans le decision-log (raw + CritereResult)
- Idempotence rejeu (resets entre runs)
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sign_consistency as sc  # noqa: E402
import triggers_classifier as tc  # noqa: E402
from sign_consistency import (  # noqa: E402
    MACRO_SIGN_RULES,
    ConflictHit,
    detect_sign_conflict,
)


# =============================================================================
# Helpers
# =============================================================================

def _mk_event(
    *,
    trigger: str,
    asset: str,
    direction: str,
    cours: str = "",
    category: str = "geopolitical",
    materiality: str = "high",
    reliability: str = "confirmed",
    nature: str = "structurel",
    confidence: str = "high",
    dt: datetime = None,
    l2: str = "",
) -> dict:
    """Construit un event au format attendu par triggers_classifier (post-parse)."""
    if dt is None:
        dt = datetime.now(timezone.utc) - timedelta(hours=2)
    return {
        "date": dt.isoformat(),
        "l1": "macro",
        "l2": l2,
        "trigger": trigger,
        "cours": cours,
        "latence": "T+0",
        "r": "5",
        "source": "test",
        "news_zone": "world",
        "category": category,
        "pattern_id": "",
        "impacts": f"{asset}:{direction}:{confidence}",
        "materiality": materiality,
        "reliability": reliability,
        "event_id": f"ev_{abs(hash(trigger))%10**8}",
        "event_date": dt.isoformat(),
        "nature": nature,
        "dedup_status": "kept",
        "stale": False,
        # champs internes pré-calculés
        "_dt": dt,
        "_event_dt": dt,
        "_canonical_dt": dt,
        "event_date_source": "rss",
        "_impacts": [
            {"asset": asset, "direction": direction, "confidence": confidence}
        ],
    }


# =============================================================================
# Module sign_consistency : détection pure
# =============================================================================

class TestDetectSignConflict:
    """Tests unitaires de la fonction de détection (pas de plumbing)."""

    def test_opep_augmente_production_long_brent_conflict(self):
        """OPEP augmente la production → BAISSIER pétrole. DeepSeek LONG → conflit."""
        hit = detect_sign_conflict(
            "OPEC raises production by 500kbd in surprise move",
            "BRENT", "LONG",
        )
        assert hit is not None
        assert hit.rule_name == "opec_production"
        assert hit.expected_direction == "SHORT"
        assert hit.ia_direction == "LONG"
        assert hit.surprise_polarity == "up"

    def test_opep_augmente_production_short_brent_coherent(self):
        """OPEP augmente → baissier. DeepSeek SHORT = COHÉRENT → pas de conflit."""
        hit = detect_sign_conflict(
            "OPEC raises production by 500kbd",
            "BRENT", "SHORT",
        )
        assert hit is None

    def test_opep_fr_augmente_production_long_brent_conflict(self):
        """Variante FR : 'OPEP augmente la production' + LONG → conflit."""
        hit = detect_sign_conflict(
            "L'OPEP augmente la production de 500kbd",
            "BRENT", "LONG",
        )
        assert hit is not None
        assert hit.rule_name == "opec_production"
        assert hit.expected_direction == "SHORT"

    def test_opep_cut_short_brent_conflict(self):
        """OPEP cut production → HAUSSIER pétrole. DeepSeek SHORT → conflit."""
        hit = detect_sign_conflict(
            "OPEC announces production cut of 1mbd",
            "BRENT", "SHORT",
        )
        assert hit is not None
        assert hit.expected_direction == "LONG"
        assert hit.surprise_polarity == "down"

    def test_cpi_hot_long_sp500_conflict(self):
        """CPI hot → baissier actions. DeepSeek LONG S&P → conflit."""
        hit = detect_sign_conflict(
            "US CPI surges above expectations, hotter than forecast",
            "SP500", "LONG",
        )
        assert hit is not None
        assert hit.rule_name == "cpi_actions"
        assert hit.expected_direction == "SHORT"

    def test_cpi_cooler_long_sp500_coherent(self):
        """CPI cooler → haussier actions. DeepSeek LONG = COHÉRENT."""
        hit = detect_sign_conflict(
            "US CPI cools, lower than expectations",
            "SP500", "LONG",
        )
        assert hit is None

    def test_fed_dovish_long_sp500_coherent(self):
        """Fed dovish → haussier actions. DeepSeek LONG = COHÉRENT."""
        hit = detect_sign_conflict(
            "Fed turns dovish, signals rate cut",
            "SP500", "LONG",
        )
        assert hit is None

    def test_fed_hawkish_long_sp500_conflict(self):
        """Fed hawkish → baissier actions. DeepSeek LONG → conflit."""
        hit = detect_sign_conflict(
            "Fed signals hawkish stance, rate hike imminent",
            "SP500", "LONG",
        )
        assert hit is not None
        assert hit.expected_direction == "SHORT"

    def test_eia_build_long_brent_conflict(self):
        """Stocks EIA build → baissier pétrole. DeepSeek LONG → conflit."""
        hit = detect_sign_conflict(
            "EIA crude oil inventories build by 5M barrels",
            "BRENT", "LONG",
        )
        assert hit is not None
        assert hit.rule_name == "eia_stocks"
        assert hit.expected_direction == "SHORT"

    def test_eia_draw_long_brent_coherent(self):
        """Stocks EIA draw → haussier pétrole. DeepSeek LONG = cohérent."""
        hit = detect_sign_conflict(
            "EIA crude oil inventories draw by 3M barrels",
            "BRENT", "LONG",
        )
        assert hit is None

    def test_nfp_strong_short_eurusd_coherent(self):
        """NFP stronger → USD up → EUR/USD down. DeepSeek SHORT = cohérent."""
        hit = detect_sign_conflict(
            "US Non-farm payrolls stronger than expected, beats forecast",
            "EURUSD", "SHORT",
        )
        assert hit is None

    def test_nfp_strong_long_eurusd_conflict(self):
        """NFP stronger → USD up → EUR/USD SHORT attendu. DeepSeek LONG → conflit."""
        hit = detect_sign_conflict(
            "US Non-farm payrolls stronger than expected, beats forecast",
            "EURUSD", "LONG",
        )
        assert hit is not None
        assert hit.expected_direction == "SHORT"


class TestNoFalsePositives:
    """Anti-faux-positif : pas de match → pas d'action."""

    def test_no_subject_no_conflict(self):
        """News sans sujet macro reconnu → None (zéro action)."""
        hit = detect_sign_conflict(
            "Apple announces new iPhone with breakthrough chip",
            "NASDAQ", "LONG",
        )
        assert hit is None

    def test_subject_without_surprise_no_conflict(self):
        """Sujet matché mais pas de cue de surprise → None."""
        hit = detect_sign_conflict(
            "OPEC meeting scheduled for next week",
            "BRENT", "LONG",
        )
        assert hit is None

    def test_subject_with_both_up_and_down_no_conflict(self):
        """Surprise ambiguë (up ET down) → None (anti-faux-positif)."""
        # « augmente » + « baisse » dans la même phrase OPEP
        hit = detect_sign_conflict(
            "OPEC could either raise production or cut production next month",
            "BRENT", "LONG",
        )
        assert hit is None

    def test_neutral_direction_no_conflict(self):
        """DeepSeek NEUTRAL → None (la fonction ne traite que LONG/SHORT)."""
        hit = detect_sign_conflict(
            "OPEC raises production",
            "BRENT", "NEUTRAL",
        )
        assert hit is None

    def test_asset_not_in_rule_no_conflict(self):
        """Asset hors scope d'une règle → None."""
        # CPI rule ciblée actions/EURUSD, pas BRENT
        hit = detect_sign_conflict(
            "US CPI hotter than expected",
            "BRENT", "LONG",
        )
        assert hit is None

    def test_word_boundary_war_vs_warm(self):
        """word-boundary : « warm » ne matche pas « war »."""
        # On vérifie que le matcher word-bounded ne fait pas n'importe quoi.
        # Pas de règle « war » dans MACRO_SIGN_RULES → assertion plus fine :
        # le helper _phrase_in lui-même est testé via cpi non matché par « cpis »
        text_norm = sc._norm("the cpis indicator showed nothing")
        # « cpi » est un sujet ; « cpis » ne doit PAS matcher (word boundary).
        assert not sc._phrase_in(text_norm, "cpi")

    def test_or_on_cpi_ambiguous_not_a_rule(self):
        """L'or sur CPI est volontairement EXCLU (ambigu) → pas de règle.

        Garde-fou : on vérifie qu'aucune règle MACRO_SIGN_RULES ne cible GOLD
        avec subject CPI, même indirectement.
        """
        for rule in MACRO_SIGN_RULES:
            if "GOLD" in rule.assets:
                for subj in rule.subject_phrases:
                    assert "cpi" not in subj.lower(), (
                        f"Règle ambiguë détectée : {rule.name} cible GOLD sur CPI"
                    )

    def test_empty_inputs_no_conflict(self):
        assert detect_sign_conflict("", "BRENT", "LONG") is None
        assert detect_sign_conflict("OPEC raises production", "", "LONG") is None
        assert detect_sign_conflict("OPEC raises production", "BRENT", "") is None


# =============================================================================
# Intégration triggers_classifier : neutralisation + trace
# =============================================================================

class TestIntegrationNeutralization:
    """Tests de bout en bout : conflit → impact neutralisé dans le pipeline."""

    def _mk_triggers_cfg(self):
        """Config minimale pour les critères pétrole / S&P / CAC."""
        return {
            "petrole": {
                "opec_politique": {
                    "type": "triplet",
                    "horizon_lookback_jours": 7,
                    "long_keywords": [],
                    "short_keywords": [],
                },
            },
            "sp500": {
                "sentiment_marche_actions": {
                    "type": "triplet",
                    "horizon_lookback_jours": 7,
                    "long_keywords": [],
                    "short_keywords": [],
                },
            },
        }

    def test_opep_augmente_long_brent_neutralise(self):
        """Cas réel : 'OPEP augmente production' + DeepSeek LONG BRENT →
        sign_conflict + neutralisé (valeur=0, source_track != ia)."""
        tc._reset_sign_conflicts()
        ev = _mk_event(
            trigger="OPEC raises production by 500kbd",
            asset="BRENT",
            direction="LONG",
            cours="(BZ=F)",
            category="commodity",
            l2="OPEC raises production",
        )
        triggers_cfg = self._mk_triggers_cfg()
        now = datetime.now(timezone.utc)
        res = tc.classify_all_with_meta(
            events=[ev], today=now, triggers_cfg=triggers_cfg, extractor=None,
        )
        # La cle YAML 'opec_politique' est remappée vers 'opec_production_policy'
        # par YML_KEY_TO_CLE_COURANTE.
        cell = res.get("petrole", {}).get("opec_production_policy", {})
        # Le triplet doit être 0 (neutralisé) — pas LONG (1) ni SHORT (-1).
        assert cell.get("valeur", 0) == 0, (
            f"Attendu neutralisé (0), obtenu {cell.get('valeur')}: {cell}"
        )
        # source_track ne doit PAS commencer par 'ia' (sinon le scoring le compte
        # comme news → on n'a pas neutralisé).
        assert not cell.get("source_track", "").startswith("ia"), (
            f"source_track devrait être hors 'ia*', got {cell.get('source_track')}"
        )
        # Trace présente
        assert cell.get("sign_conflict") is True
        details = cell.get("sign_conflict_details", [])
        assert len(details) >= 1
        d = details[0]
        assert d["asset"] == "BRENT"
        assert d["rule_name"] == "opec_production"
        assert d["ia_direction"] == "LONG"
        assert d["expected_direction"] == "SHORT"

    def test_cpi_hot_long_sp500_neutralise(self):
        """Cas réel : 'CPI hot' + DeepSeek LONG S&P → conflit + neutralisé."""
        tc._reset_sign_conflicts()
        ev = _mk_event(
            trigger="US CPI hotter than expected, surges above forecast",
            asset="SP500",
            direction="LONG",
            cours="(^GSPC)",
            category="macro",
            l2="US CPI surprise hot",
        )
        triggers_cfg = {
            "sp500": {
                "ia_signal_macro": {
                    "type": "triplet",
                    "horizon_lookback_jours": 7,
                    "long_keywords": [],
                    "short_keywords": [],
                },
            }
        }
        # Ajout d'un scope pour que l'event soit candidat sur S&P (route IA)
        prev_scope = dict(tc.CRITERION_SCOPE)
        try:
            tc.CRITERION_SCOPE[("sp500", "ia_signal_macro")] = {
                "categories": {"macro"},
                "domain_hints": set(),
                "strict_actif": False,
            }
            now = datetime.now(timezone.utc)
            res = tc.classify_all_with_meta(
                events=[ev], today=now, triggers_cfg=triggers_cfg, extractor=None,
            )
        finally:
            tc.CRITERION_SCOPE.clear()
            tc.CRITERION_SCOPE.update(prev_scope)
        cell = res.get("sp500", {}).get("ia_signal_macro", {})
        assert cell.get("valeur", 0) == 0, f"Attendu 0, got {cell}"
        assert cell.get("sign_conflict") is True
        det = cell.get("sign_conflict_details", [])
        assert det and det[0]["rule_name"] == "cpi_actions"
        assert det[0]["ia_direction"] == "LONG"
        assert det[0]["expected_direction"] == "SHORT"

    def test_fed_dovish_long_actions_no_conflict_intact(self):
        """Cas cohérent : 'Fed dovish' + DeepSeek LONG actions = PAS de
        conflit. L'impact reste INTACT (valeur = 1 LONG, source_track='ia').
        """
        tc._reset_sign_conflicts()
        ev = _mk_event(
            trigger="Fed turns dovish, signals rate cut",
            asset="SP500",
            direction="LONG",
            cours="(^GSPC)",
            category="central_bank_subtle",
            l2="Fed dovish",
        )
        prev_scope = dict(tc.CRITERION_SCOPE)
        try:
            tc.CRITERION_SCOPE[("sp500", "ia_signal_macro")] = {
                "categories": {"central_bank_subtle", "macro"},
                "domain_hints": set(),
                "strict_actif": False,
            }
            triggers_cfg = {
                "sp500": {
                    "ia_signal_macro": {
                        "type": "triplet",
                        "horizon_lookback_jours": 7,
                        "long_keywords": [],
                        "short_keywords": [],
                    }
                }
            }
            now = datetime.now(timezone.utc)
            res = tc.classify_all_with_meta(
                events=[ev], today=now, triggers_cfg=triggers_cfg, extractor=None,
            )
        finally:
            tc.CRITERION_SCOPE.clear()
            tc.CRITERION_SCOPE.update(prev_scope)
        cell = res.get("sp500", {}).get("ia_signal_macro", {})
        assert cell.get("valeur") == 1, f"Attendu LONG (1) intact, got {cell}"
        assert cell.get("source_track", "").startswith("ia"), (
            f"source_track devrait être 'ia*' (cohérent), got {cell.get('source_track')}"
        )
        assert not cell.get("sign_conflict"), (
            f"Pas de conflit attendu, got sign_conflict={cell.get('sign_conflict')}"
        )

    def test_no_pattern_no_action_zero_faux_positif(self):
        """News sans pattern macro → impact INTACT (zéro faux positif)."""
        tc._reset_sign_conflicts()
        ev = _mk_event(
            trigger="Random earnings beat from random small cap",
            asset="SP500",
            direction="LONG",
            cours="(^GSPC)",
            category="earnings",
            l2="random earnings",
        )
        prev_scope = dict(tc.CRITERION_SCOPE)
        try:
            tc.CRITERION_SCOPE[("sp500", "ia_signal_earn")] = {
                "categories": {"earnings"},
                "domain_hints": set(),
                "strict_actif": False,
            }
            triggers_cfg = {
                "sp500": {
                    "ia_signal_earn": {
                        "type": "triplet",
                        "horizon_lookback_jours": 7,
                        "long_keywords": [],
                        "short_keywords": [],
                    }
                }
            }
            now = datetime.now(timezone.utc)
            res = tc.classify_all_with_meta(
                events=[ev], today=now, triggers_cfg=triggers_cfg, extractor=None,
            )
        finally:
            tc.CRITERION_SCOPE.clear()
            tc.CRITERION_SCOPE.update(prev_scope)
        cell = res.get("sp500", {}).get("ia_signal_earn", {})
        # Aucun conflit → IA reste LONG
        assert cell.get("valeur") == 1, f"Attendu 1 (intact), got {cell}"
        assert not cell.get("sign_conflict")


class TestScoringNoContribOnConflict:
    """L'impact neutralisé NE doit PAS contribuer au score (= équivalent n/a)."""

    def test_neutralized_critere_zero_contribution_in_score(self):
        """Un critère news avec sign_conflict → valeur=0 → contributions=0.

        On reconstruit un raw type « triplet news » avec sign_conflict=True,
        valeur=0, et on vérifie qu'il ne pèse pas dans le score (via le
        scoring_analyste).
        """
        # On utilise ici directement le scoring_analyste sur une fiche
        # minimale construite à la main.
        import scoring_analyste as sa

        # Mock minimal d'une fiche : 1 critère news (triplet) + 1 critère
        # numérique stable pour avoir un baseline.
        fiche = {
            "actif": "test",
            "criteres": [
                {
                    "id": 1,
                    "nom": "news_signal_neutralise",
                    "cle_courante": "news_signal_neutralise",
                    "normalisation": "triplet",
                    "source": "ia",
                    "poids": 5,
                    "signe": 1,
                    "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
                },
            ],
        }
        # raw triplet neutralisé (valeur=0, sign_conflict=True)
        raw_data = {
            "news_signal_neutralise": {
                "valeur": 0,
                "valeur_normalisee": 0.0,
                "valeur_ponderee": 0.0,
                "materiality": "",
                "reliability": "",
                "source_track": "none",  # neutralisé → pas 'ia*'
                "ts": "2026-06-01T12:00:00+00:00",
                "sign_conflict": True,
                "sign_conflict_details": [{
                    "rule_name": "opec_production",
                    "asset": "BRENT",
                    "expected_direction": "SHORT",
                    "ia_direction": "LONG",
                    "event_id": "ev_x",
                    "title": "OPEC raises production",
                    "matched_subject": "opec",
                    "matched_surprise": "raise production",
                    "surprise_polarity": "up",
                }],
            }
        }
        res = sa.score_actif("test", fiche, raw_data)
        # Score doit être 0 (le seul critère a contribution 0)
        for h in ("24h", "7j", "1m"):
            assert abs(res.scores.get(h, 0.0)) < 1e-9, (
                f"Score {h} devrait être 0 (critère neutralisé), got {res.scores}"
            )
        # Et le CritereResult expose bien sign_conflict
        c = res.criteres[0]
        assert c.sign_conflict is True
        assert len(c.sign_conflict_details) == 1
        assert c.sign_conflict_details[0]["rule_name"] == "opec_production"


class TestDecisionLogTrace:
    """Le tracé du conflit doit apparaître dans le record decision-log."""

    def test_sign_conflict_present_in_decision_log_record(self):
        """build_decision_log_records émet bien `sign_conflict` + détails."""
        import scoring_analyste as sa

        fiche = {
            "actif": "test_actif",
            "criteres": [
                {
                    "id": 42,
                    "nom": "news_neutralised",
                    "cle_courante": "news_neutralised",
                    "normalisation": "triplet",
                    "source": "ia",
                    "poids": 5,
                    "signe": 1,
                    "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
                },
            ],
        }
        raw_data = {
            "news_neutralised": {
                "valeur": 0,
                "valeur_normalisee": 0.0,
                "valeur_ponderee": 0.0,
                "materiality": "",
                "reliability": "",
                "source_track": "none",
                "ts": "2026-06-01T12:00:00+00:00",
                "sign_conflict": True,
                "sign_conflict_details": [{
                    "rule_name": "cpi_actions",
                    "asset": "SP500",
                    "expected_direction": "SHORT",
                    "ia_direction": "LONG",
                    "event_id": "ev_42",
                    "title": "US CPI hotter than expected",
                    "matched_subject": "cpi",
                    "matched_surprise": "hotter",
                    "surprise_polarity": "up",
                }],
            }
        }
        res = sa.score_actif("test_actif", fiche, raw_data)
        now = datetime(2026, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        records = sa.build_decision_log_records([res], now)
        assert records, "Aucun record decision-log produit"
        # Chercher dans les contribs du premier record
        rec = records[0]
        crit_entries = rec.get("criteres", [])
        sc_entries = [c for c in crit_entries if c.get("sign_conflict")]
        assert sc_entries, (
            f"Aucun critère avec sign_conflict dans le decision-log "
            f"(criteres trouvés : {[c.get('nom') for c in crit_entries]})"
        )
        e = sc_entries[0]
        assert e["sign_conflict"] is True
        assert isinstance(e["sign_conflict_details"], list)
        assert e["sign_conflict_details"][0]["rule_name"] == "cpi_actions"


class TestIdempotence:
    """Resets entre runs : le stash ne fuit pas."""

    def test_reset_clears_stash(self):
        tc._reset_sign_conflicts()
        # Simule un enregistrement (via détection + récord direct)
        ev = _mk_event(
            trigger="OPEC raises production",
            asset="BRENT", direction="LONG",
            cours="(BZ=F)", category="commodity",
        )
        hit = sc.detect_sign_conflict("OPEC raises production", "BRENT", "LONG")
        assert hit is not None
        tc._record_sign_conflict(ev, "petrole", "opec_politique", "BRENT", hit)
        assert tc.get_sign_conflicts("petrole", "opec_politique"), "Stash devrait contenir 1 entry"
        # Reset
        tc._reset_sign_conflicts()
        assert tc.get_sign_conflicts("petrole", "opec_politique") == []

    def test_dedup_intra_cellule_par_event_id_asset(self):
        """Un même (event_id, asset) n'est inscrit qu'une fois par cellule."""
        tc._reset_sign_conflicts()
        ev = _mk_event(
            trigger="OPEC raises production", asset="BRENT", direction="LONG",
            cours="(BZ=F)", category="commodity",
        )
        hit = sc.detect_sign_conflict("OPEC raises production", "BRENT", "LONG")
        assert hit is not None
        tc._record_sign_conflict(ev, "petrole", "opec_politique", "BRENT", hit)
        tc._record_sign_conflict(ev, "petrole", "opec_politique", "BRENT", hit)
        tc._record_sign_conflict(ev, "petrole", "opec_politique", "BRENT", hit)
        assert len(tc.get_sign_conflicts("petrole", "opec_politique")) == 1
