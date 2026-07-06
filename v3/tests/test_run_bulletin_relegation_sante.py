"""[Relégation Santé des sources — 03/07] La section « Santé des sources »
DESCEND après les sections de décision : juste avant « ## Comment lire les
scores » (donc après « Flips vs veille »).

Tests du splice run_bulletin.relocate_source_health_before_pedagogie :
- déplacement effectif (Flips < Santé < Comment lire) ;
- idempotence (re-run → une seule section, ordre conservé) ;
- fallback : ancre « Comment lire » absente → section laissée en place ;
- intégration sur un bulletin réel (render_bulletin) : ancres réelles présentes.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_bulletin as rb  # noqa: E402
import scoring_analyste as sa  # noqa: E402

NOW = datetime(2026, 7, 3, 7, 0, tzinfo=timezone.utc)

# Bulletin mimant l'état APRÈS prepend (Santé accolée au Décor, en tête).
_BULLETIN_HEAD_SANTE = (
    "# Bulletin Analyste — 2026-07-03\n\n"
    "## Décor du jour\n\n_Décor factuel._\n\n"
    "## Santé des sources\n\n_OK : 12 flux verts._\n\n"
    "## 🎯 Aujourd'hui\n\n_paris du jour._\n\n"
    "## Flips vs veille\n\n_Aucun changement de position vs veille._\n\n"
    "## Comment lire les scores\n\n_pédagogie._\n\n"
    "## Détail par actif\n\n_détail._\n"
)


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "bulletin-2026-07-03-07h.md"
    p.write_text(content, encoding="utf-8")
    return p


def test_sante_descend_apres_flips_avant_pedagogie(tmp_path: Path):
    p = _write(tmp_path, _BULLETIN_HEAD_SANTE)
    assert rb.relocate_source_health_before_pedagogie(p) is True
    b = p.read_text(encoding="utf-8")
    assert b.count("## Santé des sources") == 1
    assert b.index("## Flips vs veille") < b.index("## Santé des sources")
    assert b.index("## Santé des sources") < b.index("## Comment lire les scores")
    # Le Décor reste en tête ; la santé n'est plus accolée au Décor.
    assert b.index("## Décor du jour") < b.index("## Flips vs veille")
    assert "_OK : 12 flux verts._" in b  # contenu de la section inchangé


def test_relocation_idempotente(tmp_path: Path):
    p = _write(tmp_path, _BULLETIN_HEAD_SANTE)
    rb.relocate_source_health_before_pedagogie(p)
    rb.relocate_source_health_before_pedagogie(p)
    b = p.read_text(encoding="utf-8")
    assert b.count("## Santé des sources") == 1
    assert b.index("## Santé des sources") < b.index("## Comment lire les scores")


def test_fallback_sans_ancre_pedagogie(tmp_path: Path):
    """Ancre « Comment lire » absente → aucune relocation, section conservée."""
    content = (
        "# Bulletin\n\n## Décor du jour\n\n_x_\n\n"
        "## Santé des sources\n\n_OK._\n\n## Flips vs veille\n\n_rien._\n"
    )
    p = _write(tmp_path, content)
    assert rb.relocate_source_health_before_pedagogie(p) is False
    assert "## Santé des sources" in p.read_text(encoding="utf-8")


def test_sans_section_sante(tmp_path: Path):
    """Pas de « Santé des sources » du tout → no-op (False), bulletin intact."""
    content = "# Bulletin\n\n## Comment lire les scores\n\n_x_\n"
    p = _write(tmp_path, content)
    assert rb.relocate_source_health_before_pedagogie(p) is False
    assert p.read_text(encoding="utf-8") == content


def test_integration_bulletin_reel(tmp_path: Path):
    """Bulletin réel (render_bulletin) : les ancres « Flips » et « Comment lire »
    existent → la Santé (préfixée) se relègue correctement entre les deux."""
    fiche = {
        "actif": "TestActif",
        "criteres": [{
            "id": 1, "nom": "Quant", "cle_courante": "quant",
            "normalisation": "lineaire", "centre": 0.0, "echelle": 1.0,
            "cap": 5.0, "signe": 1, "poids": 10,
            "pertinence": {"24h": 1.0, "7j": 1.0, "1m": 1.0},
        }],
    }
    res = sa.score_actif(
        "test", fiche, {"quant": {"valeur": 1.0, "source_track": "twelvedata"}}
    )
    md = sa.render_bulletin([res], {}, NOW, "h", "ok")
    assert "## Flips vs veille" in md and "## Comment lire les scores" in md
    # On préfixe une Santé « en tête » (comme prepend_to_bulletin le ferait).
    md = "## Santé des sources\n\n_OK réel._\n\n" + md
    p = _write(tmp_path, md)
    assert rb.relocate_source_health_before_pedagogie(p) is True
    b = p.read_text(encoding="utf-8")
    assert b.count("## Santé des sources") == 1
    assert b.index("## Flips vs veille") < b.index("## Santé des sources")
    assert b.index("## Santé des sources") < b.index("## Comment lire les scores")
