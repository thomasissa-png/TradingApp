"""Fixtures partagées des tests v3.

Garde-fou anti-pollution : `run()`/`stamp_prix_ouverture()` écrivent par défaut
dans le VRAI dossier `v3/data/prix-ouverture/`. Les tests qui appellent
`journaliste.run(stamp_today=True)` sans isoler explicitement ce dossier
polluaient `v3/data/` (fichiers `{date}.json` parasites). Cette fixture autouse
redirige le défaut du module vers un tmp par test → zéro pollution, sans devoir
modifier chaque test individuellement.

Les tests qui passent explicitement `prix_ouverture_dir=...` ne sont pas affectés
(ils gardent leur isolation propre).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Constantes de chemin qui sont des DÉFAUTS D'ÉCRITURE dans les scripts. Sans
# redirection, un test qui appelle une fonction sans passer de chemin explicite
# écrit dans le VRAI `v3/data/` (pollution : suivi-tracking, measures-log,
# performance-ab, variations-24h, criteres-*). Chaque writer concerné résout
# désormais son chemin dynamiquement (path=None → constante module), donc ce
# monkeypatch du défaut est EFFECTIF. `is_dir` → on crée un dossier, sinon un
# fichier tmp. (module, attribut, is_dir)
_REDIRECT_WRITE_DEFAULTS = (
    ("run_suivi", "SUIVI_TRACKING_DIR", True),
    ("bilan_jour", "MEASURES_LOG_FILE", False),
    ("bilan_jour", "VARIATIONS_24H_FILE", False),
    ("journaliste", "PERFORMANCE_AB_FILE", False),
    ("journaliste", "MEASURES_LOG_FILE", False),
    ("criteres_calculator", "CRITERES_OUT", False),
    ("criteres_calculator", "CRITERES_HEALTH_OUT", False),
    ("last_good_cache", "LAST_GOOD_PATH", False),
    ("run_weekly", "SELECTION_WR_JSONL", False),
    # Fuites résiduelles attrapées par le filet au run du 02/07 :
    ("build_html", "OUT_PATH", False),
    ("agent_news", "SOURCE_HEALTH_FILE", False),
)


@pytest.fixture(autouse=True)
def _isole_prix_ouverture(tmp_path, monkeypatch):
    """Redirige le dossier prix-ouverture par défaut vers un tmp par test."""
    try:
        import mesure_ouverture as mo  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — module absent dans certains contextes
        return
    tmp_ouv = tmp_path / "_isolated_prix_ouverture"
    tmp_ouv.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(mo, "PRIX_OUVERTURE_DIR", tmp_ouv, raising=False)


@pytest.fixture(autouse=True)
def _isole_news_flux(monkeypatch):
    """Isole les tests de l'events-log LIVE pour le veto news↯ et le drapeau ↯.

    `_fresh_high_feed_dirs` (scoring_analyste) lit la VRAIE events-log pour savoir
    quelles news high fraîches contredisent un call. Sans isolation, le rendu et
    la Sélection dépendraient des news du jour (tests non déterministes). Défaut :
    AUCUNE news de flux. Les tests qui exercent la fonctionnalité re-monkeypatchent
    `_fresh_high_feed_dirs` APRÈS ce fixture (l'override prime)."""
    try:
        import scoring_analyste as _sa  # noqa: PLC0415
    except Exception:  # noqa: BLE001 — module absent dans certains contextes
        return
    monkeypatch.setattr(_sa, "_fresh_high_feed_dirs", lambda now: {}, raising=False)


@pytest.fixture(autouse=True)
def _isole_ecritures_data(tmp_path, monkeypatch):
    """Redirige TOUS les défauts d'écriture vers un tmp par test → zéro pollution de
    `v3/data/`. Les tests qui passent un chemin explicite ne sont pas affectés (ils
    gardent leur isolation propre) ; seul le DÉFAUT est dévié."""
    root = tmp_path / "_isolated_data"
    for i, (mod_name, attr, is_dir) in enumerate(_REDIRECT_WRITE_DEFAULTS):
        try:
            mod = __import__(mod_name)
        except Exception:  # noqa: BLE001 — module absent dans certains contextes
            continue
        target = root / f"{mod_name}_{attr}_{i}"
        if is_dir:
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(mod, attr, target, raising=False)


def _fingerprint_data() -> dict:
    """Empreinte (taille + sha1) de chaque fichier sous v3/data, hors caches Python."""
    fp: dict = {}
    if not _DATA_DIR.exists():
        return fp
    for p in _DATA_DIR.rglob("*"):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        try:
            data = p.read_bytes()
        except OSError:
            continue
        fp[str(p.relative_to(_DATA_DIR))] = (len(data), hashlib.sha1(data).hexdigest())
    return fp


@pytest.fixture(scope="session", autouse=True)
def _filet_anti_pollution_data():
    """DERNIER FILET : snapshot de v3/data avant la session, vérification à la fin.
    Si un test a modifié/créé/supprimé un fichier réel de v3/data → échec EXPLICITE
    listant les chemins pollués (les redirections ci-dessus doivent tout prévenir ;
    ce filet DÉTECTE toute fuite résiduelle)."""
    before = _fingerprint_data()
    yield
    after = _fingerprint_data()
    modifies = sorted(k for k in before if k in after and before[k] != after[k])
    supprimes = sorted(k for k in before if k not in after)
    crees = sorted(k for k in after if k not in before)
    if modifies or supprimes or crees:
        parts = []
        if modifies:
            parts.append("MODIFIÉS: " + ", ".join(modifies))
        if supprimes:
            parts.append("SUPPRIMÉS: " + ", ".join(supprimes))
        if crees:
            parts.append("CRÉÉS: " + ", ".join(crees))
        raise AssertionError(
            "Pollution de v3/data détectée par un test (isolation manquante) — "
            + " | ".join(parts)
        )
