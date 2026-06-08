# Performance du bulletin — Journaliste

- Généré : 2026-06-08T07:05:58.329589+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 21 | 95.0% | 6 | 83.3% | 0.436 | 0.1277 | 5/95% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 4.8% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Argent | 7j | 2 | 50.0% | 1 | 100.0% | 0.206 | 0.2431 | 50/50% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 21 | 33.3% | 6 | 66.7% | 0.300 | 0.2341 | 71/29% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 71.4% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 7j | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.0286 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 21 | 42.9% | 3 | 33.3% | 0.061 | 0.2937 | 10/90% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 9.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 7j | 2 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 20 | 0.0% | 6 | 0.0% | 0.000 | 0.3717 | 100/0% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 20/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 7j | 2 | 0.0% | 1 | 0.0% | 0.000 | 0.4218 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 19 | 81.8% | 5 | 60.0% | 0.231 | 0.2257 | 10/90% | shadow | warm-up non-chevauchant : 5/15 obs effectives; 19/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 10.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 7j | 2 | 0.0% | 1 | 0.0% | 0.000 | 0.4410 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 20 | 5.6% | 6 | 16.7% | 0.030 | 0.5475 | 95/5% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 20/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 95.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 7j | 2 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 17 | 100.0% | 5 | 100.0% | 0.566 | 0.0360 | 0/100% | shadow | warm-up non-chevauchant : 5/15 obs effectives; 17/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 7j | 2 | 50.0% | 1 | 0.0% | 0.000 | 0.2559 | 50/50% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 21 | 90.0% | 6 | 66.7% | 0.300 | 0.1912 | 10/90% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 9.5% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 7j | 2 | 50.0% | 1 | 0.0% | 0.000 | 0.5025 | 50/50% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 21 | 100.0% | 6 | 100.0% | 0.610 | 0.1411 | 0/100% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 7j | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.0308 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 21 | 92.9% | 6 | 83.3% | 0.436 | 0.1271 | 95/5% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 95.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 7j | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.0005 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 21 | 5.0% | 6 | 16.7% | 0.030 | 0.4269 | 95/5% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 95.2% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 7j | 2 | 0.0% | 1 | 0.0% | 0.000 | 0.6115 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 21 | 64.7% | 6 | 66.7% | 0.300 | 0.1687 | 71/29% | shadow | warm-up non-chevauchant : 6/15 obs effectives; 21/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 71.4% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 7j | 2 | — | 0 | — | — | — | 50/50% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); N_eff déflaté par chevauchement (÷9 pour 7j) — KPI non significatif tant que N_eff < 15; 2 suivi(s) interrompu(s) sur la fenêtre observable |

## Synthèse
- Cellules éligibles actif (Wilson low > 50%, taux_eff ≥ 70%) : **0** / 24
- Cellules shadow : 24 / 24

### Critère global (multiple testing — audit-data §2)

Avec 36 cellules testées, ~1-2 faux positifs attendus par hasard à α=0,05.
Critère d'éligibilité renforcé : Wilson low > 50 % (borne basse IC 95 % sur N_eff).

- Critère global : warm-up (aucune cellule avec N_eff ≥ 15)

## Flip vs continuation (additif — taux global inchangé)

| Actif | Horizon | N_flip | Taux_flip | N_continuation | Taux_continuation |
|---|---|---|---|---|---|
| Argent | 24h | 2 | 50.0% | 18 | 100.0% |
| Argent | 7j | 2 | 50.0% | 0 | — |
| Blé | 24h | 2 | 50.0% | 16 | 31.2% |
| Blé | 7j | 1 | 100.0% | 1 | 100.0% |
| CAC 40 | 24h | 0 | — | 7 | 42.9% |
| Cacao | 24h | 0 | — | 16 | 0.0% |
| Cacao | 7j | 0 | — | 2 | 0.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 8 | 87.5% |
| Café (Arabica) | 7j | 1 | 0.0% | 1 | 0.0% |
| Cuivre | 24h | 1 | 0.0% | 16 | 6.2% |
| EUR/USD | 24h | 0 | — | 14 | 100.0% |
| EUR/USD | 7j | 1 | 100.0% | 1 | 0.0% |
| Nasdaq | 24h | 2 | 50.0% | 18 | 94.4% |
| Nasdaq | 7j | 2 | 50.0% | 0 | — |
| Or | 24h | 1 | 100.0% | 18 | 100.0% |
| Or | 7j | 1 | 100.0% | 1 | 100.0% |
| Pétrole (Brent) | 24h | 0 | — | 14 | 92.9% |
| Pétrole (Brent) | 7j | 0 | — | 2 | 100.0% |
| S&P 500 | 24h | 3 | 33.3% | 17 | 0.0% |
| S&P 500 | 7j | 1 | 0.0% | 1 | 0.0% |
| VIX | 24h | 7 | 42.9% | 10 | 80.0% |

- **Taux global flips** : 46.4% (N=28 mesures avec is_flip=True)
- **Taux global continuations** : 59.7% (N=181 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-01 | 2026-06-08 | Argent | 7j | LONG | 74.4657 | 67.8012 | -8.950% | 2.0% | FAUSSE | delta=-8.950% vs seuil=2.0% |
| 2026-06-01 | 2026-06-08 | Blé | 7j | SHORT | 610.7924 | 576.2411 | -5.657% | 2.5% | VRAI | delta=-5.657% vs seuil=2.5% |
| 2026-06-01 | 2026-06-08 | CAC 40 | 7j | LONG | 8183.3398 | 8218.2402 | +0.426% | 1.2% | non-conclusive | |delta|=0.426% ≤ seuil=1.2% |
| 2026-06-01 | 2026-06-08 | Cacao | 7j | LONG | 3924.6486 | 3761.4009 | -4.160% | 4.0% | FAUSSE | delta=-4.160% vs seuil=4.0% |
| 2026-06-01 | 2026-06-08 | Café (Arabica) | 7j | LONG | 265.5419 | 246.4862 | -7.176% | 3.0% | FAUSSE | delta=-7.176% vs seuil=3.0% |
| 2026-06-01 | 2026-06-08 | Cuivre | 7j | SHORT | 6.3575 | 6.2491 | -1.705% | 2.0% | non-conclusive | |delta|=1.705% ≤ seuil=2.0% |
| 2026-06-01 | 2026-06-08 | EUR/USD | 7j | SHORT | 1.1652 | 1.1535 | -1.006% | 0.7% | VRAI | delta=-1.006% vs seuil=0.7% |
| 2026-06-01 | 2026-06-08 | Nasdaq | 7j | SHORT | 738.2250 | 705.2100 | -4.472% | 1.5% | VRAI | delta=-4.472% vs seuil=1.5% |
| 2026-06-01 | 2026-06-08 | Or | 7j | SHORT | 4521.6133 | 4314.9946 | -4.570% | 1.3% | VRAI | delta=-4.570% vs seuil=1.3% |
| 2026-06-01 | 2026-06-08 | Pétrole (Brent) | 7j | LONG | 93.0815 | 97.0695 | +4.284% | 2.5% | VRAI | delta=+4.284% vs seuil=2.5% |
| 2026-06-01 | 2026-06-08 | S&P 500 | 7j | LONG | 756.4000 | 737.4000 | -2.512% | 1.0% | FAUSSE | delta=-2.512% vs seuil=1.0% |
| 2026-06-01 | 2026-06-08 | VIX | 7j | LONG | 23.2300 | 24.3200 | +4.692% | 10.0% | non-conclusive | |delta|=4.692% ≤ seuil=10.0% |
| 2026-06-05 | 2026-06-08 | Argent | 24h | SHORT | 72.7855 | 67.8012 | -6.848% | 0.8% | VRAI | delta=-6.848% vs seuil=0.8% |
| 2026-06-05 | 2026-06-08 | Blé | 24h | LONG | 580.9226 | 576.2411 | -0.806% | 0.8% | FAUSSE | delta=-0.806% vs seuil=0.8% |
| 2026-06-05 | 2026-06-08 | CAC 40 | 24h | SHORT | 8244.2900 | 8218.2402 | -0.316% | 0.5% | non-conclusive | |delta|=0.316% ≤ seuil=0.5% |
| 2026-06-05 | 2026-06-08 | Cacao | 24h | LONG | 3964.7694 | 3761.4009 | -5.129% | 1.0% | FAUSSE | delta=-5.129% vs seuil=1.0% |
| 2026-06-05 | 2026-06-08 | Café (Arabica) | 24h | SHORT | 247.2584 | 246.4862 | -0.312% | 1.0% | non-conclusive | |delta|=0.312% ≤ seuil=1.0% |
| 2026-06-05 | 2026-06-08 | Cuivre | 24h | LONG | 6.4164 | 6.2491 | -2.608% | 0.8% | FAUSSE | delta=-2.608% vs seuil=0.8% |
| 2026-06-05 | 2026-06-08 | EUR/USD | 24h | SHORT | 1.1615 | 1.1535 | -0.690% | 0.25% | VRAI | delta=-0.690% vs seuil=0.25% |
| 2026-06-05 | 2026-06-08 | Nasdaq | 24h | SHORT | 740.5000 | 705.2100 | -4.766% | 0.7% | VRAI | delta=-4.766% vs seuil=0.7% |
