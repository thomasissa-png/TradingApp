"""Moteur de sélection du « top 3 du jour » (objectif : +0,5 % en < 24h).

Refonte de fond (juin 2026, validée 10/10 par les 3 experts Analyst / News Trader /
Spéculateur). Remplace l'ancienne logique de Sélection 24h, qui choisissait des
convictions de FOND (tendance 20j, macro lente) pour un objectif RAPIDE.

PRINCIPE — deux moteurs séparés :
  - CE module = SEUL sélecteur du top 3 « 24h » (événementiel + momentum).
  - Le moteur de fond (scoring_analyste) reste le garde-fou de direction ET le
    moteur EXCLUSIF des horizons 7j / 1m (inchangés).

LOGIQUE IMPLACABLE, DÉTERMINISTE, SANS « habitude »/volatilité passée. Le mouvement
attendu vient du CATALYSEUR (grosse news fraîche) ou du MOMENTUM EN COURS, jamais
des statistiques d'habitude de l'actif. Une grosse news casse l'habitude : si une
news est suffisamment importante, on prend le pari (on ne rate pas le mouvement).

Ce module est PUR : il ne fait aucun appel réseau. La couche d'intégration lui
fournit, par actif, les faits déjà calculés (news taguées + prix). Tout est
testable hors-ligne.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ── Seuils déterministes (valeurs de départ, calibrables sur les résultats) ──
OBJECTIF_MOVE: float = 0.005            # +0,5 % en 24h = la cible

# Fraîcheur d'une news (heures depuis l'ingestion), mesurée à l'instant de sélection.
FRESH_PLEIN_H: float = 2.0              # 0-2h : plein potentiel
FRESH_OK_H: float = 6.0                 # 2-6h : éligible
FRESH_MAX_H: float = 12.0               # 6-12h : éligible si move non consommé ; >12h mort

# « Déjà coté » : part du move (vers l'objectif) déjà parcourue depuis la news.
CONSOMME_DEJA_COTE: float = 0.70        # ≥ 70 % consommé ET n'avance plus → écarté

# Contradiction de séance (proportionnelle à la force de la news), mesurée APRÈS
# les premières minutes de bruit. Mouvement CONTRAIRE soutenu au-delà du seuil → veto.
CONTRA_P1: float = 0.004                # catalyseur majeur : 0,4 %
CONTRA_P2: float = 0.0015               # catalyseur modéré : 0,15 %

# Momentum (porte sans news) : sur séries de clôtures journalières.
ACCEL_CLOTURES: int = 3                 # 3 clôtures successives qui poussent même sens
CASSURE_SEANCES: int = 7                # nouvel extrême sur 7 séances

SELECTION_MAX: int = 3

# Paliers (plus petit = plus prioritaire).
PALIER_P1 = 1   # catalyseur MAJEUR frais aligné
PALIER_P2 = 2   # catalyseur modéré frais aligné, OU momentum vivant aligné
PALIER_P3 = 3   # momentum simple aligné + fond concordant


# ── Données d'entrée (fournies par l'intégration, déjà calculées) ───────────
@dataclass
class NewsItem:
    """Une news taguée touchant l'actif (champs issus de l'events-log)."""
    direction: str                      # "LONG" | "SHORT" (sens mécanique sur l'actif)
    materiality: str                    # "high" | "medium" | "low"
    reliability: str                    # "confirmed" | "reported" | "rumor"
    nature: str                         # "structurel" | "ponctuel" | "deja_cote" | "verbal"
    ingest_ts: Optional[datetime]       # horodatage d'ingestion (fraîcheur)
    resume: str = ""                    # texte court (affichage)
    # Mouvement déjà réalisé DANS LE SENS de la news depuis l'heure de la news,
    # en fraction (ex. 0.003 = +0,3 %). None si prix indisponible.
    post_news_move: Optional[float] = None


@dataclass
class AssetDay:
    """Faits du jour pour un actif (tout pré-calculé par l'intégration)."""
    actif: str
    fiche_key: str
    news: List[NewsItem] = field(default_factory=list)
    # Prix : mouvement de séance en cours (spot vs dernière clôture vue), signé.
    session_move: Optional[float] = None
    # Clôtures journalières oldest→newest (pour la porte momentum).
    closes: List[float] = field(default_factory=list)
    # Direction du fond 24h (garde-fou) : "LONG" | "SHORT" | "" (inconnu/neutre).
    fond_dir: str = ""


@dataclass
class Pick:
    """Un pari retenu pour le top 3."""
    actif: str
    fiche_key: str
    direction: str
    porte: str                          # "news" | "momentum"
    palier: int
    raison: str
    # Champs de départage (ordre total, exposés pour le decision-log/tests).
    mat_score: int = 0
    fresh_recency: float = 0.0          # plus grand = plus récent
    consomme: float = 1.0               # plus petit = plus de potentiel restant


# ── Briques déterministes ───────────────────────────────────────────────────
def _materiality_score(n: NewsItem) -> int:
    """Score ordinal indépendant du prix = base(matérialité) × facteur(source).
    0 = ne déclenche pas (low, rumeur, ou nature « déjà coté »)."""
    if (n.nature or "").lower() == "deja_cote":
        return 0
    base = {"high": 3, "medium": 2}.get((n.materiality or "").lower(), 0)
    rel = {"confirmed": 2, "reported": 1}.get((n.reliability or "").lower(), 0)
    return base * rel


def _palier_news(score: int) -> Optional[int]:
    """Palier d'un catalyseur selon son score de matérialité. None si non déclencheur."""
    if score >= 6:          # high × confirmed
        return PALIER_P1
    if score >= 3:          # high × reported (3) ou medium × confirmed (4)
        return PALIER_P2
    return None


def _fresh_hours(n: NewsItem, now: datetime) -> Optional[float]:
    """Âge de la news en heures (None si horodatage absent)."""
    if not isinstance(n.ingest_ts, datetime):
        return None
    ts = n.ingest_ts
    if ts.tzinfo and now.tzinfo:
        delta = now - ts
    else:
        delta = now.replace(tzinfo=None) - ts.replace(tzinfo=None)
    return delta.total_seconds() / 3600.0


def _consomme_ratio(n: NewsItem) -> float:
    """Part du move (vers l'objectif +0,5 %) déjà parcourue dans le sens de la news."""
    if n.post_news_move is None:
        return 0.0
    # Seul le mouvement DANS le sens de la news compte (un move contraire → 0 consommé).
    favorable = max(0.0, n.post_news_move)
    return favorable / OBJECTIF_MOVE


def _contradiction_active(asset: "AssetDay", direction: str, palier: int) -> bool:
    """True si le prix de séance contredit ACTIVEMENT le sens, au-delà du seuil
    proportionnel à la force de la news. Anti-faux-négatif : une simple hésitation
    ne suffit pas — il faut un mouvement contraire net."""
    if asset.session_move is None:
        return False
    seuil = CONTRA_P1 if palier == PALIER_P1 else CONTRA_P2
    if direction == "LONG":
        return asset.session_move <= -seuil
    if direction == "SHORT":
        return asset.session_move >= seuil
    return False


def _net_news_frais(asset: "AssetDay", now: datetime) -> float:
    """Net directionnel des news FRAÎCHES (age <= FRESH_MAX_H) de l'actif : somme
    des scores de matérialité SIGNÉS par direction (LONG = +, SHORT = −). Sert au
    garde-fou R3 (une news de sens minoritaire ne doit pas commander quand le net
    frais penche dans l'autre sens). Les news sans horodatage ou non déclencheuses
    (score 0) ne pèsent pas. 0.0 = vrai 50/50 → R3 ne bloque pas."""
    net = 0.0
    for n in asset.news:
        if n.direction not in ("LONG", "SHORT"):
            continue
        score = _materiality_score(n)
        if score <= 0:
            continue
        age = _fresh_hours(n, now)
        if age is None or age > FRESH_MAX_H:
            continue
        net += score if n.direction == "LONG" else -score
    return net


def _news_door(asset: "AssetDay", now: datetime) -> Optional[Pick]:
    """Porte CATALYSEUR : meilleure news déclencheuse, fraîche, non déjà cotée,
    non activement contredite. Retourne un Pick ou None.

    Garde-fous AJOUTÉS (juin 2026, sans rien retirer de l'anti-faux-négatif) :
      - R2 : si le fond contredit la news, le catalyseur ne prime QUE s'il est un
        vrai P1 frais (grosse news qui casse l'habitude). P2 ou P1 moins frais à
        contre-fond → rejeté (s'aligne sur le fond).
      - R3 : une news de sens MINORITAIRE est rejetée quand le net des news fraîches
        de l'actif penche dans l'autre sens (net != 0)."""
    net_frais = _net_news_frais(asset, now)
    best: Optional[Tuple[int, int, float, float, NewsItem]] = None
    for n in asset.news:
        if n.direction not in ("LONG", "SHORT"):
            continue
        score = _materiality_score(n)
        palier = _palier_news(score)
        if palier is None:
            continue
        age = _fresh_hours(n, now)
        if age is None or age > FRESH_MAX_H:
            continue
        # R2 — Garde-fou fond : si le fond va à l'inverse de la news, seul un vrai
        # catalyseur P1 ET frais (age <= FRESH_OK_H) peut casser l'habitude. Sinon
        # (P2, ou P1 moins frais), le catalyseur doit s'aligner sur le fond → rejet.
        if asset.fond_dir in ("LONG", "SHORT") and asset.fond_dir != n.direction:
            if not (palier == PALIER_P1 and age <= FRESH_OK_H):
                continue
        # R3 — Alignement sur le sens NET des news fraîches : on rejette une news
        # de sens minoritaire quand le net frais (non nul) penche à l'inverse.
        if net_frais > 0 and n.direction == "SHORT":
            continue
        if net_frais < 0 and n.direction == "LONG":
            continue
        consomme = _consomme_ratio(n)
        # 6-12h : éligible seulement si le move n'est pas déjà consommé.
        if age > FRESH_OK_H and consomme >= CONSOMME_DEJA_COTE:
            continue
        # « Déjà coté » : ≥70 % consommé ET n'avance plus (move de séance non favorable).
        if consomme >= CONSOMME_DEJA_COTE and not _move_prolonge(asset, n.direction):
            continue
        if _contradiction_active(asset, n.direction, palier):
            continue
        recency = max(0.0, FRESH_MAX_H - age)
        cand = (palier, score, recency, consomme, n)
        # On garde la news la plus forte (palier le plus prioritaire, puis score,
        # puis la plus fraîche, puis la moins consommée).
        if best is None or (palier, -score, -recency, consomme) < (
            best[0], -best[1], -best[2], best[3]
        ):
            best = cand
    if best is None:
        return None
    palier, score, recency, consomme, n = best
    return Pick(
        actif=asset.actif, fiche_key=asset.fiche_key, direction=n.direction,
        porte="news", palier=palier, raison=n.resume or "news high à contre-sens",
        mat_score=score, fresh_recency=recency, consomme=consomme,
    )


def _move_prolonge(asset: "AssetDay", direction: str) -> bool:
    """True si le mouvement de séance prolonge encore le sens (le move continue)."""
    if asset.session_move is None:
        return True  # pas d'info → on ne déclare pas « épuisé » (anti-faux-négatif)
    if direction == "LONG":
        return asset.session_move > 0
    return asset.session_move < 0


def _momentum_dir(closes: List[float]) -> Optional[str]:
    """Direction du momentum vivant : accélération sur N clôtures ET cassure de range.
    None si pas de momentum net."""
    if len(closes) < max(ACCEL_CLOTURES + 1, CASSURE_SEANCES + 1):
        return None
    # Accélération : ACCEL_CLOTURES dernières clôtures strictement monotones.
    recent = closes[-(ACCEL_CLOTURES + 1):]
    hausse = all(recent[i] < recent[i + 1] for i in range(len(recent) - 1))
    baisse = all(recent[i] > recent[i + 1] for i in range(len(recent) - 1))
    # Cassure : dernier close = nouvel extrême sur CASSURE_SEANCES séances.
    fenetre = closes[-(CASSURE_SEANCES + 1):]
    dernier = fenetre[-1]
    plus_haut = dernier >= max(fenetre[:-1])
    plus_bas = dernier <= min(fenetre[:-1])
    if hausse and plus_haut:
        return "LONG"
    if baisse and plus_bas:
        return "SHORT"
    return None


def _momentum_door(asset: "AssetDay") -> Optional[Pick]:
    """Porte MOMENTUM (sans news) : accélération + cassure, alignée séance, garde-fou
    fond non contredit. Retourne un Pick (palier P2) ou None."""
    direction = _momentum_dir(asset.closes)
    if direction is None:
        return None
    # Garde-fou : le fond ne doit pas contredire le sens du momentum.
    if asset.fond_dir in ("LONG", "SHORT") and asset.fond_dir != direction:
        return None
    # Alignement séance : jamais contre le prix du jour (anti-piège Café).
    if _contradiction_active(asset, direction, PALIER_P2):
        return None
    return Pick(
        actif=asset.actif, fiche_key=asset.fiche_key, direction=direction,
        porte="momentum", palier=PALIER_P2,
        raison=f"momentum {('haussier' if direction == 'LONG' else 'baissier')} "
               f"(accélération + cassure {CASSURE_SEANCES}j)",
        mat_score=0, fresh_recency=0.0, consomme=0.0,
    )


def _asset_pick(asset: "AssetDay", now: datetime) -> Optional[Pick]:
    """Le meilleur pari pour UN actif : le catalyseur prime sur le momentum ;
    s'ils s'opposent, le momentum est rejeté (la news commande). Fusion implicite :
    un seul Pick par actif."""
    news = _news_door(asset, now)
    mom = _momentum_door(asset)
    if news is not None:
        # Catalyseur vs momentum opposé sur le même actif → le catalyseur commande.
        return news
    return mom


def _sort_key(p: "Pick", ordre_index: Dict[str, int]) -> Tuple:
    """Ordre TOTAL strict (plus petit = plus prioritaire) :
    (a) palier P1>P2>P3 ; (b) catalyseur > momentum ; (c) score matérialité ;
    (d) fraîcheur (plus récent) ; (e) move le MOINS consommé ; (f) ordre fixe des actifs."""
    return (
        p.palier,
        0 if p.porte == "news" else 1,
        -p.mat_score,
        -p.fresh_recency,
        p.consomme,
        ordre_index.get(p.fiche_key, 10_000),
    )


def select_top3(
    assets: List["AssetDay"],
    now: datetime,
    ordre_actifs: Optional[List[str]] = None,
) -> List["Pick"]:
    """Sélectionne le top 3 du jour (objectif +0,5 %/24h), logique implacable.

    `ordre_actifs` = liste figée des fiche_key dans l'ordre canonique (départage
    ultime déterministe). PAS DE REMPLISSAGE : on retourne EXACTEMENT le nombre
    qualifié (0 à 3), jamais en abaissant un seuil. Dédup par type de marché
    (`groupe`) : un seul pari par moteur, on garde le mieux classé."""
    ordre_index = {k: i for i, k in enumerate(ordre_actifs or [])}
    picks: List[Pick] = []
    for a in assets:
        p = _asset_pick(a, now)
        if p is not None:
            picks.append(p)
    picks.sort(key=lambda p: _sort_key(p, ordre_index))

    # Dédup par type de marché (groupe) : on garde le premier (mieux classé).
    groupe_par_key = {a.fiche_key: getattr(a, "groupe", "") for a in assets}
    vus: set = set()
    retenus: List[Pick] = []
    for p in picks:
        g = groupe_par_key.get(p.fiche_key, "") or p.fiche_key  # pas de groupe → unique
        if g in vus:
            continue
        vus.add(g)
        retenus.append(p)
        if len(retenus) >= SELECTION_MAX:
            break
    return retenus
