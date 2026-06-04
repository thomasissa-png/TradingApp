# Performance du bulletin — Journaliste

- Généré : 2026-06-04T07:07:54.683799+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 80.0% | 4 | 75.0% | 0.301 | 0.2101 | 11/89% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 11.1% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 9 | 85.7% | 4 | 100.0% | 0.510 | 0.1812 | 33/67% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 9 | 100.0% | 2 | 100.0% | 0.342 | 0.2403 | 22/78% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 8 | 100.0% | 2 | 100.0% | 0.342 | 0.2156 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 7 | 60.0% | 4 | 50.0% | 0.150 | 0.2493 | 29/71% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 7/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 28.6% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 8 | 16.7% | 4 | 25.0% | 0.046 | 0.4286 | 88/12% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 87.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 5 | 100.0% | 2 | 100.0% | 0.342 | 0.2081 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 5/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 9 | 100.0% | 2 | 100.0% | 0.342 | 0.0324 | 22/78% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 9 | 42.9% | 4 | 75.0% | 0.301 | 0.2660 | 0/100% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 9 | 60.0% | 4 | 75.0% | 0.301 | 0.4142 | 100/0% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 9 | 25.0% | 2 | 50.0% | 0.095 | 0.2652 | 89/11% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 88.9% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 9 | — | 0 | — | — | — | 78/22% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 77.8% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |

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
| Argent | 24h | 2 | 50.0% | 3 | 100.0% |
| Blé | 24h | 2 | 50.0% | 5 | 100.0% |
| CAC 40 | 24h | 1 | 100.0% | 2 | 100.0% |
| Cacao | 24h | 0 | — | 2 | 100.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 3 | 66.7% |
| Cuivre | 24h | 1 | 100.0% | 4 | 0.0% |
| EUR/USD | 24h | 0 | — | 2 | 100.0% |
| Nasdaq | 24h | 1 | 100.0% | 1 | 100.0% |
| Or | 24h | 1 | 100.0% | 6 | 33.3% |
| Pétrole (Brent) | 24h | 0 | — | 5 | 60.0% |
| S&P 500 | 24h | 2 | 50.0% | 2 | 0.0% |

- **Taux global flips** : 63.6% (N=11 mesures avec is_flip=True)
- **Taux global continuations** : 62.9% (N=35 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.6938 | 73.6431 | -1.407% | 0.8% | VRAI | delta=-1.407% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 598.8305 | 583.2138 | -2.608% | 0.8% | VRAI | delta=-2.608% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8209.0898 | 8150.4199 | -0.715% | 0.5% | VRAI | delta=-0.715% vs seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4109.7536 | 4073.7314 | -0.877% | 1.0% | non-conclusive | |delta|=0.877% ≤ seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 259.1988 | 253.0483 | -2.373% | 1.0% | VRAI | delta=-2.373% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.6240 | 6.4376 | -2.814% | 0.8% | FAUSSE | delta=-2.814% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1626 | 1.1610 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 744.2300 | -0.256% | 0.7% | non-conclusive | |delta|=0.256% ≤ seuil=0.7% |
| 2026-06-03 | 2026-06-04 | Or | 24h | SHORT | 4470.2727 | 4478.0798 | +0.175% | 0.5% | non-conclusive | |delta|=0.175% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Pétrole (Brent) | 24h | LONG | 97.0872 | 96.9079 | -0.185% | 1.0% | non-conclusive | |delta|=0.185% ≤ seuil=1.0% |
| 2026-06-03 | 2026-06-04 | S&P 500 | 24h | LONG | 759.4700 | 754.1900 | -0.695% | 0.4% | FAUSSE | delta=-0.695% vs seuil=0.4% |
| 2026-06-03 | 2026-06-04 | VIX | 24h | LONG | 23.4600 | 23.4600 | +0.000% | 3.0% | non-conclusive | prix courant == prix d'émission (mouvement nul — marché probablement fermé) |
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.1125 | 73.6431 | -0.633% | 0.8% | non-conclusive | |delta|=0.633% ≤ seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 602.7865 | 583.2138 | -3.247% | 0.8% | VRAI | delta=-3.247% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8184.6602 | 8150.4199 | -0.418% | 0.5% | non-conclusive | |delta|=0.418% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4065.9017 | 4073.7314 | +0.193% | 1.0% | non-conclusive | |delta|=0.193% ≤ seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 258.8803 | 253.0483 | -2.253% | 1.0% | VRAI | delta=-2.253% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.5798 | 6.4376 | -2.161% | 0.8% | FAUSSE | delta=-2.161% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1615 | 1.1610 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 744.2300 | -0.256% | 0.7% | non-conclusive | |delta|=0.256% ≤ seuil=0.7% |
