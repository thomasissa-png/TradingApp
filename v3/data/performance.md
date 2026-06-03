# Performance du bulletin — Journaliste

- Généré : 2026-06-03T17:08:25.465476+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 4 | 75.0% | 3 | 66.7% | 0.208 | 0.2277 | 25/75% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 25.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 4 | 100.0% | 3 | 100.0% | 0.439 | 0.1293 | 0/100% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 4 | 100.0% | 1 | 100.0% | 0.206 | 0.2408 | 50/50% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 3 | 100.0% | 2 | 100.0% | 0.342 | 0.2156 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 3 | 33.3% | 3 | 33.3% | 0.061 | 0.2780 | 67/33% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 3 | 33.3% | 3 | 33.3% | 0.061 | 0.2947 | 67/33% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 2 | 100.0% | 2 | 100.0% | 0.342 | 0.2081 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 4 | 100.0% | 2 | 100.0% | 0.342 | 0.0324 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 4 | 100.0% | 3 | 100.0% | 0.439 | 0.1160 | 0/100% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 4 | 100.0% | 3 | 100.0% | 0.439 | 0.0547 | 100/0% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 4 | 0.0% | 1 | 0.0% | 0.000 | 0.3450 | 75/25% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 75.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 4 | — | 0 | — | — | — | 75/25% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 75.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |

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
| Argent | 24h | 2 | 50.0% | 2 | 100.0% |
| Blé | 24h | 1 | 100.0% | 3 | 100.0% |
| CAC 40 | 24h | 1 | 100.0% | 0 | — |
| Cacao | 24h | 0 | — | 2 | 100.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 1 | 0.0% |
| Cuivre | 24h | 1 | 100.0% | 1 | 0.0% |
| EUR/USD | 24h | 0 | — | 2 | 100.0% |
| Nasdaq | 24h | 1 | 100.0% | 1 | 100.0% |
| Or | 24h | 1 | 100.0% | 3 | 100.0% |
| Pétrole (Brent) | 24h | 0 | — | 4 | 100.0% |
| S&P 500 | 24h | 1 | 0.0% | 0 | — |

- **Taux global flips** : 66.7% (N=9 mesures avec is_flip=True)
- **Taux global continuations** : 89.5% (N=19 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-02 | 2026-06-03 | Argent | 24h | SHORT | 76.4176 | 73.7572 | -3.481% | 0.8% | VRAI | delta=-3.481% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | Blé | 24h | SHORT | 605.6869 | 591.4433 | -2.352% | 0.8% | VRAI | delta=-2.352% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | CAC 40 | 24h | SHORT | 8216.0098 | 8170.7700 | -0.551% | 0.5% | VRAI | delta=-0.551% vs seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Nasdaq | 24h | SHORT | 742.6900 | 745.5800 | +0.389% | 0.7% | non-conclusive | |delta|=0.389% ≤ seuil=0.7% |
| 2026-06-02 | 2026-06-03 | Or | 24h | SHORT | 4526.7303 | 4449.7842 | -1.700% | 0.5% | VRAI | delta=-1.700% vs seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Pétrole (Brent) | 24h | LONG | 93.1302 | 97.7280 | +4.937% | 1.0% | VRAI | delta=+4.937% vs seuil=1.0% |
| 2026-06-02 | 2026-06-03 | S&P 500 | 24h | SHORT | 758.4400 | 756.0700 | -0.312% | 0.4% | non-conclusive | |delta|=0.312% ≤ seuil=0.4% |
| 2026-06-02 | 2026-06-03 | VIX | 24h | LONG | 23.8650 | 23.5800 | -1.194% | 3.0% | non-conclusive | |delta|=1.194% ≤ seuil=3.0% |
| 2026-06-02 | 2026-06-03 | Cacao | 24h | INSUFFISANT | 3894.4308 | 4035.6585 | — | 1.0% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Café (Arabica) | 24h | INSUFFISANT | 260.4126 | 255.2765 | — | 1.0% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Cuivre | 24h | INSUFFISANT | 6.6085 | 6.5075 | — | 0.8% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | EUR/USD | 24h | INSUFFISANT | 1.1643 | 1.1604 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Argent | 24h | SHORT | 75.1654 | 73.7572 | -1.873% | 0.8% | VRAI | delta=-1.873% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | Blé | 24h | SHORT | 602.4645 | 591.4433 | -1.829% | 0.8% | VRAI | delta=-1.829% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | CAC 40 | 24h | SHORT | 8209.0898 | 8170.7700 | -0.467% | 0.5% | non-conclusive | |delta|=0.467% ≤ seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Cacao | 24h | LONG | 4075.9593 | 4035.6585 | -0.989% | 1.0% | non-conclusive | |delta|=0.989% ≤ seuil=1.0% |
| 2026-06-02 | 2026-06-03 | Café (Arabica) | 24h | SHORT | 259.2777 | 255.2765 | -1.543% | 1.0% | VRAI | delta=-1.543% vs seuil=1.0% |
| 2026-06-02 | 2026-06-03 | Cuivre | 24h | LONG | 6.6466 | 6.5075 | -2.093% | 0.8% | FAUSSE | delta=-2.093% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | EUR/USD | 24h | INSUFFISANT | 1.1632 | 1.1604 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Nasdaq | 24h | SHORT | 746.2400 | 745.5800 | -0.088% | 0.7% | non-conclusive | |delta|=0.088% ≤ seuil=0.7% |
