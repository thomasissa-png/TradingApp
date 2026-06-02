# Performance du bulletin — Journaliste

- Généré : 2026-06-02T12:48:18.551815+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 2 | 50.0% | 2 | 50.0% | 0.095 | 0.2912 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.0146 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.2156 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 2 | 0.0% | 2 | 0.0% | 0.000 | 0.3128 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 2 | 50.0% | 2 | 50.0% | 0.095 | 0.1662 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 2 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 2 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.0000 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
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
| Argent | 24h | 1 | 100.0% | 1 | 0.0% |
| Blé | 24h | 1 | 100.0% | 1 | 100.0% |
| Cacao | 24h | 0 | — | 2 | 100.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 1 | 0.0% |
| Cuivre | 24h | 1 | 100.0% | 1 | 0.0% |
| Pétrole (Brent) | 24h | 0 | — | 1 | 100.0% |

- **Taux global flips** : 75.0% (N=4 mesures avec is_flip=True)
- **Taux global continuations** : 57.1% (N=7 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-01 | 2026-06-02 | Argent | 24h | LONG | 74.4657 | 76.3242 | +2.496% | 0.8% | VRAI | delta=+2.496% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | Blé | 24h | SHORT | 610.7924 | 603.2196 | -1.240% | 0.8% | VRAI | delta=-1.240% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | CAC 40 | 24h | LONG | 8183.3398 | 8205.7100 | +0.273% | 0.5% | non-conclusive | |delta|=0.273% ≤ seuil=0.5% |
| 2026-06-01 | 2026-06-02 | Cacao | 24h | LONG | 3924.6486 | 3970.6784 | +1.173% | 1.0% | VRAI | delta=+1.173% vs seuil=1.0% |
| 2026-06-01 | 2026-06-02 | Café (Arabica) | 24h | LONG | 265.5419 | 259.5682 | -2.250% | 1.0% | FAUSSE | delta=-2.250% vs seuil=1.0% |
| 2026-06-01 | 2026-06-02 | Cuivre | 24h | LONG | 6.3575 | 6.5880 | +3.626% | 0.8% | VRAI | delta=+3.626% vs seuil=0.8% |
| 2026-06-01 | 2026-06-02 | EUR/USD | 24h | SHORT | 1.1652 | 1.1644 | -0.071% | 0.25% | non-conclusive | |delta|=0.071% ≤ seuil=0.25% |
| 2026-06-01 | 2026-06-02 | Nasdaq | 24h | LONG | 738.2250 | 742.6900 | +0.605% | 0.7% | non-conclusive | |delta|=0.605% ≤ seuil=0.7% |
| 2026-06-01 | 2026-06-02 | Or | 24h | SHORT | 4521.6133 | 4531.4483 | +0.218% | 0.5% | non-conclusive | |delta|=0.218% ≤ seuil=0.5% |
| 2026-06-01 | 2026-06-02 | Pétrole (Brent) | 24h | LONG | 93.0815 | 93.8326 | +0.807% | 1.0% | non-conclusive | |delta|=0.807% ≤ seuil=1.0% |
| 2026-06-01 | 2026-06-02 | S&P 500 | 24h | LONG | 756.4000 | 758.4400 | +0.270% | 0.4% | non-conclusive | |delta|=0.270% ≤ seuil=0.4% |
| 2026-06-01 | 2026-06-02 | VIX | 24h | LONG | 23.2300 | 23.8650 | +2.734% | 3.0% | non-conclusive | |delta|=2.734% ≤ seuil=3.0% |
| 2026-05-31 | 2026-06-01 | Argent | 24h | SHORT | 75.3693 | 76.3242 | +1.267% | 0.8% | FAUSSE | delta=+1.267% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | Blé | 24h | SHORT | 610.7924 | 603.2196 | -1.240% | 0.8% | VRAI | delta=-1.240% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | CAC 40 | 24h | LONG | 8183.3398 | 8205.7100 | +0.273% | 0.5% | non-conclusive | |delta|=0.273% ≤ seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Cacao | 24h | LONG | 3924.6486 | 3970.6784 | +1.173% | 1.0% | VRAI | delta=+1.173% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Café (Arabica) | 24h | LONG | 265.5419 | 259.5682 | -2.250% | 1.0% | FAUSSE | delta=-2.250% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Cuivre | 24h | SHORT | 6.3621 | 6.5880 | +3.550% | 0.8% | FAUSSE | delta=+3.550% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | EUR/USD | 24h | SHORT | 1.1658 | 1.1644 | -0.120% | 0.25% | non-conclusive | |delta|=0.120% ≤ seuil=0.25% |
| 2026-05-31 | 2026-06-01 | Nasdaq | 24h | LONG | 738.2250 | 742.6900 | +0.605% | 0.7% | non-conclusive | |delta|=0.605% ≤ seuil=0.7% |
