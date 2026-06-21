"""Tests des correctifs issus de l'audit run 18h (2026-06-01).

Fix A : drapeau matrice 📰 = abs(news)/abs(quant) > 0.5 (cohérent avec decision-log)
        - cas signé/non-signé : signes opposés ne doivent PAS faire passer le ratio < 0
        - Blé 7j (news=+1.8, quant=+10) → ratio=0.18, PAS de 📰
        - Or 24h (news=-6.2, quant=+10) → ratio=0.62, 📰 présent

Fix B : marqueur ⚪ coin-flip dans la cellule de matrice si |score_pm1|<0.05
        + booléen coin_flip dans le decision-log

Fix C : build_html.py génère un index.html non vide contenant le dernier bulletin
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scoring_analyste as sa  # noqa: E402


def _detail_matrix_line(bulletin: str, actif_prefix: str = "| TestActif") -> str:
    """Retourne la ligne de l'actif dans la table de synthèse fusionnée
    ('## Synthèse des décisions' — format riche : direction + note + flags +
    conf%, anciennement '## Matrice'). #4.2 : les deux tables ont fusionné."""
    matrix_section = bulletin.split("## Synthèse des décisions")[1].split("## Détail")[0]
    return next(l for l in matrix_section.splitlines() if l.startswith(actif_prefix))


# Helpers (alignés sur test_news_cap.py)
def _fiche(quant_signe: int = 1, news_signe: int = 1, quant_poids: int = 10, news_poids: int = 10) -> dict:
    return {
        "actif": "TestActif",
        "criteres": [
            {
                "id": 1, "nom": "Quant",
                "cle_courante": "quant", "normalisation": "lineaire",
                "centre": 0.0, "echelle": 1.0, "cap": 1.0,
                "signe": quant_signe, "poids": quant_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
            {
                "id": 2, "nom": "News",
                "cle_courante": "news", "normalisation": "triplet",
                "cap": 1.0, "signe": news_signe, "poids": news_poids,
                "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
            },
        ],
    }


def _vals(quant_val: float, news_val: float, mat: str = "medium", rel: str = "confirmed") -> dict:
    return {
        "quant": {"valeur": quant_val, "source_track": "twelvedata"},
        "news": {"valeur": news_val, "source_track": "ia_synthese",
                 "materiality": mat, "reliability": rel},
    }


# ---------------------------------------------------------------------------
# Fix A — drapeau matrice 📰 utilise ratio abs/abs (pas signé)
# ---------------------------------------------------------------------------

def test_matrice_news_flag_uses_abs_ratio_ble_7j_pattern():
    """Reproduction Blé 7j : ratio réel 18% → AUCUN drapeau 📰.

    On force quant=+10 (forte conviction quant) et news=+1.8 (news mineure
    cohérente). L'ancienne logique signée donnait ratio = 1.8 / 10 = 0.18
    → ok par chance mais le bug d'origine est qu'avec un signe opposé
    (quant=+10, news=-1.8) la version signée donne -0.18 < 0.5 aussi.
    Le vrai cas Blé 7j : news=+1.8, quant=+10 → 0.18 < 0.5 → pas de 📰.
    """
    fiche = _fiche(quant_poids=10, news_poids=2)  # news ~ 18% du quant
    vals = _vals(quant_val=1.0, news_val=0.9)  # quant=+10, news=+1.8 (poids 2)
    res = sa.score_actif("ble", fiche, vals)
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    # Trouver la ligne de matrice du test
    matrice_line = next(l for l in bulletin.splitlines() if l.startswith("| TestActif"))
    assert "📰" not in matrice_line, (
        f"Ratio news/quant = ~0.18, ne doit PAS être floqué 📰. Ligne : {matrice_line!r}"
    )


def test_matrice_news_flag_present_when_ratio_above_50pct():
    """Or 24h pattern : ratio 62% → 📰 présent (régression du fix)."""
    fiche = _fiche(quant_poids=10, news_poids=10)
    vals = _vals(quant_val=0.5, news_val=-1.0)  # quant=+5, news=-10 → ratio=2.0
    res = sa.score_actif("or", fiche, vals)
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    # Cible la table de Synthèse (le nouveau « À jouer » a aussi des lignes
    # « | TestActif » mais ne porte pas le 📰 du ratio quant/news).
    matrice_line = _detail_matrix_line(bulletin)
    assert "📰" in matrice_line, (
        f"Ratio abs/abs = 2.0 > 0.5 doit faire apparaître 📰. Ligne : {matrice_line!r}"
    )


def test_matrice_news_flag_opposite_signs_uses_abs():
    """Bug d'origine : avec ratio signé, news=-1.0 face à quant=+0.6 donne
    -10/6 = -1.66 < 0.5 → drapeau MASQUÉ à tort. Avec abs/abs : 10/6=1.66 → 📰.
    """
    fiche = _fiche(quant_poids=6, news_poids=10)
    vals = _vals(quant_val=1.0, news_val=-1.0, mat="high", rel="confirmed")  # override → pas de cap
    res = sa.score_actif("test", fiche, vals)
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    matrice_line = _detail_matrix_line(bulletin)
    assert "📰" in matrice_line, (
        f"abs(-10)/abs(+6)=1.66>0.5 → 📰 attendu. Ligne : {matrice_line!r}"
    )


def test_matrice_legend_present():
    # Légende COMPACTE : ne liste QUE les symboles présents. On vérifie l'entête
    # de légende, puis qu'un ⚪ présent dans une cellule est bien documenté.
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    assert "**Légende**" in bulletin
    res2 = sa.score_actif("nasdaq", _fiche_tiny(), {"quant": {"valeur": 0.1, "source_track": "twelvedata"}})
    bulletin2 = sa.render_bulletin([res2], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    assert "⚪" in bulletin2 and "coin-flip" in bulletin2


# ---------------------------------------------------------------------------
# Fix B — marqueur ⚪ coin-flip (|score_pm1|<0.05)
# ---------------------------------------------------------------------------

def _fiche_tiny() -> dict:
    """Fiche minimale produisant un score quasi nul (pattern Nasdaq 24h −0.0017)."""
    return {
        "actif": "TestActif",
        "criteres": [{
            "id": 1, "nom": "Q",
            "cle_courante": "quant", "normalisation": "lineaire",
            "centre": 0.0, "echelle": 100.0, "cap": 1.0,
            "signe": 1, "poids": 1,
            "pertinence": {"24h": 0.1, "7j": 0.1, "1m": 0.1},
        }],
    }


def test_coin_flip_marker_in_matrix_when_score_below_threshold():
    """Score ≈ 0 → ⚪ doit apparaître dans la cellule (pattern Nasdaq 24h −0.0017)."""
    fiche = _fiche_tiny()
    vals = {"quant": {"valeur": 0.1, "source_track": "twelvedata"}}
    res = sa.score_actif("nasdaq", fiche, vals)
    # |score| doit être <0.05
    assert abs(res.scores["24h"]) < 0.05
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    matrice_line = _detail_matrix_line(bulletin)
    assert "⚪" in matrice_line, f"Score quasi nul → ⚪ attendu. Ligne : {matrice_line!r}"


def test_coin_flip_marker_absent_when_score_above_threshold():
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))  # score = 20
    bulletin = sa.render_bulletin([res], {}, datetime(2026, 6, 1, tzinfo=timezone.utc), "h", "ok")
    matrice_line = _detail_matrix_line(bulletin)
    assert "⚪" not in matrice_line, f"Score=20 → pas de ⚪. Ligne : {matrice_line!r}"


def test_coin_flip_field_in_decision_log():
    fiche = _fiche_tiny()
    vals = {"quant": {"valeur": 0.1, "source_track": "twelvedata"}}
    res = sa.score_actif("test", fiche, vals)
    records = sa.build_decision_log_records([res], datetime(2026, 6, 1, tzinfo=timezone.utc))
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert "coin_flip" in rec_24h
    assert rec_24h["coin_flip"] is True


def test_coin_flip_field_false_when_score_strong():
    fiche = _fiche()
    res = sa.score_actif("test", fiche, _vals(1.0, 1.0))
    records = sa.build_decision_log_records([res], datetime(2026, 6, 1, tzinfo=timezone.utc))
    rec_24h = next(r for r in records if r["horizon"] == "24h")
    assert rec_24h["coin_flip"] is False


# ---------------------------------------------------------------------------
# Fix C — build_html.py
# ---------------------------------------------------------------------------

def test_build_html_generates_non_empty_index(tmp_path, monkeypatch):
    """Le script build_html génère un index.html non vide contenant les bulletins."""
    # Exécute le script en sous-process (les chemins sont absolus dans le script).
    script = ROOT / "scripts" / "build_html.py"
    assert script.exists()
    res = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    assert res.returncode == 0, f"build_html.py a échoué : {res.stderr}"
    out = ROOT / "data" / "index.html"
    assert out.exists(), "index.html non créé"
    content = out.read_text(encoding="utf-8")
    assert len(content) > 500, "index.html trop court"
    assert "TradingApp v3" in content
    assert "marked.min.js" in content  # marked.js inclus
    assert "BULLETINS = [" in content  # données embarquées
    # Légende
    assert "coin-flip" in content
    assert "news&gt;50%" in content or "news>50%" in content
    # Contient au moins un bulletin (s'il en existe sur disque)
    bulletins_dir = ROOT / "data" / "bulletins"
    if bulletins_dir.exists() and any(bulletins_dir.glob("bulletin-*.md")):
        # Le dernier bulletin doit apparaître dans le JS embarqué
        latest = sorted(bulletins_dir.glob("bulletin-*.md"))[-1]
        # Au moins le filename doit apparaître
        assert latest.name in content, f"Bulletin {latest.name} non embarqué dans index.html"


def test_build_html_contains_color_classes_and_help_box():
    """Vérifie que l'index.html généré contient les classes de colorisation
    .dir-long / .dir-short et l'encart repliable 'Comment lire les scores'."""
    script = ROOT / "scripts" / "build_html.py"
    res = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    assert res.returncode == 0, f"build_html.py a échoué : {res.stderr}"
    out = ROOT / "data" / "index.html"
    content = out.read_text(encoding="utf-8")
    # Classes CSS de colorisation
    assert ".dir-long" in content, "Classe CSS .dir-long absente"
    assert ".dir-short" in content, "Classe CSS .dir-short absente"
    # Fonction JS de colorisation et son appel
    assert "colorizeDirections" in content, "Fonction colorizeDirections absente"
    # Encart d'aide repliable
    assert "Comment lire les scores" in content, "Encart d'aide absent"
    assert "help-box" in content, "Classe help-box absente"
    assert "<details" in content, "Balise <details> de l'encart absente"


def test_build_html_contains_sticky_legend_and_subnav():
    """Vérifie que la légende des scores vit dans le help-box « Comment lire »
    (la legend-bar redondante a été RETIRÉE — point #6 refonte) et que la
    sous-navigation d'ancres intra-bulletin est présente."""
    script = ROOT / "scripts" / "build_html.py"
    res = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    assert res.returncode == 0, f"build_html.py a échoué : {res.stderr}"
    out = ROOT / "data" / "index.html"
    content = out.read_text(encoding="utf-8")
    # [Point #6] La legend-bar redondante a été supprimée : la légende des scores
    # vit désormais UNIQUEMENT dans le help-box « Comment lire les scores ».
    assert "legend-bar" not in content, "legend-bar aurait dû être supprimée (point #6)"
    assert "help-box" in content, "Encart help-box (légende canonique) absent"
    assert "force de conviction" in content, "Texte de légende des scores absent"
    assert "non-actionnable" in content, "Mention non-actionnable absente"
    # Sous-navigation d'ancres intra-bulletin
    assert 'id="subnav"' in content, "Élément subnav absent"
    assert "buildSubnav" in content, "Fonction buildSubnav absente"
    assert "Sauter à" in content, "Label de sous-nav absent"
    # Hamburger mobile + sidebar toggle
    assert 'id="hamburger"' in content, "Bouton hamburger absent"
    assert "openSidebarMobile" in content, "Fonction openSidebarMobile absente"
    # Wrapping tables (scroll horizontal mobile)
    assert "wrapTables" in content, "Fonction wrapTables absente"
    assert "table-wrap" in content, "Classe CSS table-wrap absente"
    # Sidebar : repère DOUX (léger gras) sur le jour le plus récent. La pastille
    # verte « DERNIER » a été retirée (refonte S9, redondante) → on vérifie le
    # repère .latest qui la remplace.
    assert "aside a.latest" in content, "Repère .latest (jour récent) absent"
    # Position sticky toujours utilisée par le header (la subnav, elle, défile
    # avec le contenu depuis qu'elle a été dé-stickée — chrome permanent réduit).
    assert "position: sticky" in content or "position:sticky" in content


def test_build_html_escapes_backticks_and_dollar_brace():
    """Vérifie que l'échappement gère les caractères dangereux."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_html as bh
    s = "test `backtick` ${interp} \\ </script>"
    escaped = bh.escape_for_js_template_literal(s)
    assert "\\`" in escaped
    assert "\\${" in escaped
    assert "<\\/script>" in escaped
    # antislash doublé
    assert "\\\\" in escaped
