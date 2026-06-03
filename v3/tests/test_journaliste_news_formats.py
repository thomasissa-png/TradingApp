"""Non-régression : le Journaliste doit MESURER toutes les cellules actionnées,
y compris les formats news.

Régressions corrigées (audit 03/06) :
  - "(brut LONG +7.98)" (la direction dans la parenthèse cassait CELL_NEWS_LEAD_RE).
  - "LONG [quant -0.08] 📰 régime news (19%)" (format Q2 : aucun parser ne matchait
    → cellules en régime news non mesurées).
Sans ces parsers, ces cellules étaient silencieusement EXCLUES de la mesure
VRAI/FAUX — exactement les cellules news que le fondateur veut suivre.
"""
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from journaliste import parse_bulletin  # noqa: E402

BULLETIN = """# Bulletin Analyste — 2026-06-03 · 07h03 (Paris)

## Synthèse des décisions

| Actif | 24h | 7j | 1m |
|---|---|---|---|
| Argent | SHORT (-1.89) | SHORT (-1.06) | LONG (+1.99) |
| Cuivre | LONG [quant -0.08] 📰 régime news (19%) | SHORT [quant -0.28] 📰 régime news (35%) | LONG [quant -0.64] 📰 régime news (35%) |
| Pétrole (Brent) | LONG +6.06 (brut LONG +7.98) ⚑ 📰 | LONG +8.03 (brut LONG +11.87) ⚑ 📰 | LONG +6.23 (brut LONG +9.19) ⚑ 📰 |
"""


def _cells(tmp_path: Path):
    p = tmp_path / "bulletin-2026-06-03-05h.md"
    p.write_text(BULLETIN, encoding="utf-8")
    cells = parse_bulletin(p)
    return {(c.actif_name, c.horizon): c for c in cells}


def test_news_regime_cells_are_measured(tmp_path):
    """Régime news : direction = biais news, cellule bien présente et mesurée."""
    c = _cells(tmp_path)
    for h in ("24h", "7j", "1m"):
        assert ("Cuivre", h) in c, f"Cuivre {h} non mesuré (régime news perdu)"
    assert c[("Cuivre", "24h")].conclusion == "LONG"
    assert c[("Cuivre", "7j")].conclusion == "SHORT"
    assert c[("Cuivre", "1m")].conclusion == "LONG"
    # Le score quant affiché est conservé (mesure du score, direction = conclusion).
    assert c[("Cuivre", "24h")].score == -0.08
    assert c[("Cuivre", "1m")].score == -0.64


def test_news_lead_brut_with_direction_word_is_measured(tmp_path):
    """'(brut LONG +7.98)' : le brut reste le score primaire mesuré."""
    c = _cells(tmp_path)
    for h in ("24h", "7j", "1m"):
        assert ("Pétrole (Brent)", h) in c, f"Pétrole {h} non mesuré"
    pet = c[("Pétrole (Brent)", "24h")]
    assert pet.conclusion == "LONG"
    assert pet.score == 7.98          # brut = primaire
    assert pet.score_pond == 6.06     # pondéré = lead


def test_standard_cells_unchanged(tmp_path):
    """Format standard inchangé."""
    c = _cells(tmp_path)
    assert c[("Argent", "24h")].conclusion == "SHORT"
    assert c[("Argent", "24h")].score == -1.89
    assert c[("Argent", "1m")].conclusion == "LONG"
    assert c[("Argent", "1m")].score == 1.99


def test_all_actionable_cells_measured(tmp_path):
    """9 cellules actionnées (3 actifs × 3 horizons) → 9 mesurées, zéro perdue."""
    c = _cells(tmp_path)
    assert len(c) == 9
