# Performance du bulletin — Journaliste

- Généré : 2026-06-04T20:35:19.961135+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 80.0% | 3 | 100.0% | 0.439 | 0.2442 | 11/89% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 11.1% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 9 | 66.7% | 4 | 100.0% | 0.510 | 0.1993 | 33/67% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 9 | 33.3% | 3 | 66.7% | 0.208 | 0.3082 | 22/78% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 8 | 0.0% | 2 | 0.0% | 0.000 | 0.3644 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 7 | 71.4% | 4 | 50.0% | 0.150 | 0.2369 | 29/71% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 7/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 28.6% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 8 | 33.3% | 4 | 25.0% | 0.046 | 0.3407 | 88/12% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 87.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 5 | 100.0% | 2 | 100.0% | 0.342 | 0.2081 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 5/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 9 | — | 0 | — | — | — | 22/78% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 9 | 42.9% | 4 | 75.0% | 0.301 | 0.2660 | 0/100% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 9 | 33.3% | 4 | 75.0% | 0.301 | 0.6460 | 100/0% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 9 | 100.0% | 1 | 100.0% | 0.206 | 0.0356 | 89/11% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 88.9% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 9 | 0.0% | 1 | 0.0% | 0.000 | 0.4312 | 78/22% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 77.8% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |

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
| Argent | 24h | 1 | 100.0% | 4 | 75.0% |
| Blé | 24h | 2 | 50.0% | 7 | 71.4% |
| CAC 40 | 24h | 0 | — | 6 | 33.3% |
| Cacao | 24h | 0 | — | 5 | 0.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 4 | 75.0% |
| Cuivre | 24h | 1 | 100.0% | 4 | 25.0% |
| EUR/USD | 24h | 0 | — | 2 | 100.0% |
| Or | 24h | 1 | 100.0% | 6 | 33.3% |
| Pétrole (Brent) | 24h | 0 | — | 9 | 33.3% |
| S&P 500 | 24h | 0 | — | 1 | 100.0% |
| VIX | 24h | 0 | — | 1 | 0.0% |

- **Taux global flips** : 66.7% (N=6 mesures avec is_flip=True)
- **Taux global continuations** : 44.9% (N=49 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.6938 | 73.8771 | -1.093% | 0.8% | VRAI | delta=-1.093% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 598.8305 | 581.4389 | -2.904% | 0.8% | VRAI | delta=-2.904% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8209.0898 | 8244.2900 | +0.429% | 0.5% | non-conclusive | |delta|=0.429% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4109.7536 | 3927.6033 | -4.432% | 1.0% | FAUSSE | delta=-4.432% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 259.1988 | 247.2572 | -4.607% | 1.0% | VRAI | delta=-4.607% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.6240 | 6.5259 | -1.480% | 0.8% | FAUSSE | delta=-1.480% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1626 | 1.1616 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 742.8600 | -0.440% | 0.7% | non-conclusive | |delta|=0.440% ≤ seuil=0.7% |
| 2026-06-03 | 2026-06-04 | Or | 24h | SHORT | 4470.2727 | 4474.8736 | +0.103% | 0.5% | non-conclusive | |delta|=0.103% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Pétrole (Brent) | 24h | LONG | 97.0872 | 95.1296 | -2.016% | 1.0% | FAUSSE | delta=-2.016% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | S&P 500 | 24h | LONG | 759.4700 | 757.7800 | -0.223% | 0.4% | non-conclusive | |delta|=0.223% ≤ seuil=0.4% |
| 2026-06-03 | 2026-06-04 | VIX | 24h | LONG | 23.4600 | 22.9900 | -2.003% | 3.0% | non-conclusive | |delta|=2.003% ≤ seuil=3.0% |
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.1125 | 73.8771 | -0.318% | 0.8% | non-conclusive | |delta|=0.318% ≤ seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 602.7865 | 581.4389 | -3.541% | 0.8% | VRAI | delta=-3.541% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8184.6602 | 8244.2900 | +0.729% | 0.5% | FAUSSE | delta=+0.729% vs seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4065.9017 | 3927.6033 | -3.401% | 1.0% | FAUSSE | delta=-3.401% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 258.8803 | 247.2572 | -4.490% | 1.0% | VRAI | delta=-4.490% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.5798 | 6.5259 | -0.819% | 0.8% | FAUSSE | delta=-0.819% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1615 | 1.1616 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 742.8600 | -0.440% | 0.7% | non-conclusive | |delta|=0.440% ≤ seuil=0.7% |
