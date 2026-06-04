# Performance du bulletin — Journaliste

- Généré : 2026-06-04T18:07:19.095411+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 9 | 66.7% | 4 | 75.0% | 0.301 | 0.2541 | 11/89% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 11.1% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 9 | 66.7% | 4 | 100.0% | 0.510 | 0.1993 | 33/67% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 9 | 33.3% | 3 | 66.7% | 0.208 | 0.3082 | 22/78% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 8 | 0.0% | 2 | 0.0% | 0.000 | 0.3644 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 7 | 71.4% | 4 | 50.0% | 0.150 | 0.2369 | 29/71% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 7/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 28.6% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 8 | 20.0% | 4 | 25.0% | 0.046 | 0.3974 | 88/12% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 8/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 87.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 5 | 50.0% | 2 | 50.0% | 0.095 | 0.5115 | 0/100% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 5/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 9 | 100.0% | 2 | 100.0% | 0.342 | 0.2217 | 22/78% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 22.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 9 | 42.9% | 4 | 75.0% | 0.301 | 0.2660 | 0/100% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 9 | 33.3% | 4 | 75.0% | 0.301 | 0.6460 | 100/0% | shadow | warm-up non-chevauchant : 4/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 9 | 0.0% | 2 | 0.0% | 0.000 | 0.3497 | 89/11% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 9/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 88.9% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
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
| Argent | 24h | 2 | 50.0% | 4 | 75.0% |
| Blé | 24h | 2 | 50.0% | 7 | 71.4% |
| CAC 40 | 24h | 0 | — | 6 | 33.3% |
| Cacao | 24h | 0 | — | 5 | 0.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 4 | 75.0% |
| Cuivre | 24h | 1 | 100.0% | 3 | 0.0% |
| EUR/USD | 24h | 0 | — | 2 | 50.0% |
| Nasdaq | 24h | 0 | — | 4 | 100.0% |
| Or | 24h | 1 | 100.0% | 6 | 33.3% |
| Pétrole (Brent) | 24h | 0 | — | 9 | 33.3% |
| S&P 500 | 24h | 1 | 0.0% | 2 | 0.0% |
| VIX | 24h | 0 | — | 1 | 0.0% |

- **Taux global flips** : 50.0% (N=8 mesures avec is_flip=True)
- **Taux global continuations** : 43.4% (N=53 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.6938 | 73.8552 | -1.123% | 0.8% | VRAI | delta=-1.123% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 598.8305 | 580.6944 | -3.029% | 0.8% | VRAI | delta=-3.029% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8209.0898 | 8244.2900 | +0.429% | 0.5% | non-conclusive | |delta|=0.429% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4109.7536 | 3958.0837 | -3.690% | 1.0% | FAUSSE | delta=-3.690% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 259.1988 | 248.0064 | -4.318% | 1.0% | VRAI | delta=-4.318% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.6240 | 6.5097 | -1.725% | 0.8% | FAUSSE | delta=-1.725% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1626 | 1.1628 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 739.4650 | -0.895% | 0.7% | VRAI | delta=-0.895% vs seuil=0.7% |
| 2026-06-03 | 2026-06-04 | Or | 24h | SHORT | 4470.2727 | 4476.4761 | +0.139% | 0.5% | non-conclusive | |delta|=0.139% ≤ seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Pétrole (Brent) | 24h | LONG | 97.0872 | 95.0901 | -2.057% | 1.0% | FAUSSE | delta=-2.057% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | S&P 500 | 24h | LONG | 759.4700 | 755.8600 | -0.475% | 0.4% | FAUSSE | delta=-0.475% vs seuil=0.4% |
| 2026-06-03 | 2026-06-04 | VIX | 24h | LONG | 23.4600 | 23.1100 | -1.492% | 3.0% | non-conclusive | |delta|=1.492% ≤ seuil=3.0% |
| 2026-06-03 | 2026-06-04 | Argent | 24h | SHORT | 74.1125 | 73.8552 | -0.347% | 0.8% | non-conclusive | |delta|=0.347% ≤ seuil=0.8% |
| 2026-06-03 | 2026-06-04 | Blé | 24h | SHORT | 602.7865 | 580.6944 | -3.665% | 0.8% | VRAI | delta=-3.665% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | CAC 40 | 24h | SHORT | 8184.6602 | 8244.2900 | +0.729% | 0.5% | FAUSSE | delta=+0.729% vs seuil=0.5% |
| 2026-06-03 | 2026-06-04 | Cacao | 24h | LONG | 4065.9017 | 3958.0837 | -2.652% | 1.0% | FAUSSE | delta=-2.652% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Café (Arabica) | 24h | SHORT | 258.8803 | 248.0064 | -4.200% | 1.0% | VRAI | delta=-4.200% vs seuil=1.0% |
| 2026-06-03 | 2026-06-04 | Cuivre | 24h | LONG | 6.5798 | 6.5097 | -1.066% | 0.8% | FAUSSE | delta=-1.066% vs seuil=0.8% |
| 2026-06-03 | 2026-06-04 | EUR/USD | 24h | INSUFFISANT | 1.1615 | 1.1628 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-03 | 2026-06-04 | Nasdaq | 24h | SHORT | 746.1400 | 739.4650 | -0.895% | 0.7% | VRAI | delta=-0.895% vs seuil=0.7% |
