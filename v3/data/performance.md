# Performance du bulletin — Journaliste

- Généré : 2026-06-02T16:27:28.136614+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.2013 | 50/50% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.0146 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.2156 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 2 | 0.0% | 2 | 0.0% | 0.000 | 0.3128 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 2 | 50.0% | 2 | 50.0% | 0.095 | 0.1662 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 2 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.1031 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.0010 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 2 | — | 0 | — | — | — | 50/50% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |

## Synthèse
- Cellules éligibles actif (Wilson low > 50%, taux_eff ≥ 70%) : **0** / 12
- Cellules shadow : 12 / 12

### Critère global (multiple testing — audit-data §2)

Avec 36 cellules testées, ~1-2 faux positifs attendus par hasard à α=0,05.
Critère d'éligibilité renforcé : Wilson low > 50 % (borne basse IC 95 % sur N_eff).

- Critère global : warm-up (aucune cellule avec N_eff ≥ 15)

## Flip vs continuation (additif — taux global inchangé)

| Actif | Horizon | N_flip | Taux_flip | N_continuation | Taux_continuation |
|---|---|---|---|---|---|
| Argent | 24h | 1 | 100.0% | 0 | — |
| Blé | 24h | 1 | 100.0% | 1 | 100.0% |
| Cacao | 24h | 0 | — | 2 | 100.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 1 | 0.0% |
| Cuivre | 24h | 1 | 100.0% | 1 | 0.0% |
| Or | 24h | 1 | 100.0% | 1 | 100.0% |
| Pétrole (Brent) | 24h | 0 | — | 2 | 100.0% |

- **Taux global flips** : 80.0% (N=5 mesures avec is_flip=True)
- **Taux global continuations** : 75.0% (N=8 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-01 | 2026-06-02 | Argent | 24h | LONG | 74.4657 | 75.3693 | +1.213% | 0.8% | VRAI | delta=+1.213% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | Blé | 24h | SHORT | 610.7924 | 600.9939 | -1.604% | 0.8% | VRAI | delta=-1.604% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | CAC 40 | 24h | LONG | 8183.3398 | 8193.5596 | +0.125% | 0.5% | non-conclusive | |delta|=0.125% ≤ seuil=0.5% |
| 2026-06-01 | 2026-06-02 | Cacao | 24h | LONG | 3924.6486 | 4114.5675 | +4.839% | 1.0% | VRAI | delta=+4.839% vs seuil=1.0% |
| 2026-06-01 | 2026-06-02 | Café (Arabica) | 24h | LONG | 265.5419 | 260.7235 | -1.815% | 1.0% | FAUSSE | delta=-1.815% vs seuil=1.0% |
| 2026-06-01 | 2026-06-02 | Cuivre | 24h | LONG | 6.3575 | 6.6447 | +4.519% | 0.8% | VRAI | delta=+4.519% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | EUR/USD | 24h | SHORT | 1.1652 | 1.1639 | -0.112% | 0.25% | non-conclusive | |delta|=0.112% ≤ seuil=0.25% |
| 2026-06-01 | 2026-06-02 | Nasdaq | 24h | LONG | 738.2250 | 742.2100 | +0.540% | 0.7% | non-conclusive | |delta|=0.540% ≤ seuil=0.7% |
| 2026-06-01 | 2026-06-02 | Or | 24h | SHORT | 4521.6133 | 4495.1902 | -0.584% | 0.5% | VRAI | delta=-0.584% vs seuil=0.5% |
| 2026-06-01 | 2026-06-02 | Pétrole (Brent) | 24h | LONG | 93.0815 | 95.2794 | +2.361% | 1.0% | VRAI | delta=+2.361% vs seuil=1.0% |
| 2026-06-01 | 2026-06-02 | S&P 500 | 24h | LONG | 756.4000 | 757.6500 | +0.165% | 0.4% | non-conclusive | |delta|=0.165% ≤ seuil=0.4% |
| 2026-06-01 | 2026-06-02 | VIX | 24h | LONG | 23.2300 | 23.6000 | +1.593% | 3.0% | non-conclusive | |delta|=1.593% ≤ seuil=3.0% |
| 2026-05-31 | 2026-06-01 | Argent | 24h | SHORT | 75.3693 | 75.3693 | +0.000% | 0.8% | non-conclusive | |delta|=0.000% ≤ seuil=0.8% |
| 2026-05-31 | 2026-06-01 | Blé | 24h | SHORT | 610.7924 | 600.9939 | -1.604% | 0.8% | VRAI | delta=-1.604% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | CAC 40 | 24h | LONG | 8183.3398 | 8193.5596 | +0.125% | 0.5% | non-conclusive | |delta|=0.125% ≤ seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Cacao | 24h | LONG | 3924.6486 | 4114.5675 | +4.839% | 1.0% | VRAI | delta=+4.839% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Café (Arabica) | 24h | LONG | 265.5419 | 260.7235 | -1.815% | 1.0% | FAUSSE | delta=-1.815% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Cuivre | 24h | SHORT | 6.3621 | 6.6447 | +4.443% | 0.8% | FAUSSE | delta=+4.443% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | EUR/USD | 24h | SHORT | 1.1658 | 1.1639 | -0.160% | 0.25% | non-conclusive | |delta|=0.160% ≤ seuil=0.25% |
| 2026-05-31 | 2026-06-01 | Nasdaq | 24h | LONG | 738.2250 | 742.2100 | +0.540% | 0.7% | non-conclusive | |delta|=0.540% ≤ seuil=0.7% |
