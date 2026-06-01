# Performance du bulletin — Journaliste

- Généré : 2026-06-01T21:22:20.069575+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 1 | 0.0% | 1 | 0.0% | 0.000 | 0.3729 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 1 | 0.0% | 1 | 0.0% | 0.000 | 0.2663 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.0138 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.0435 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.0000 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.1282 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| VIX | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |

## Synthèse
- Cellules éligibles actif (Wilson low > 50%, taux_eff ≥ 70%) : **0** / 12
- Cellules shadow : 12 / 12

### Critère global (multiple testing — audit-data §2)

Avec 36 cellules testées, ~1-2 faux positifs attendus par hasard à α=0,05.
Critère d'éligibilité renforcé : Wilson low > 50 % (borne basse IC 95 % sur N_eff).

- Critère global : warm-up (aucune cellule avec N_eff ≥ 15)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-05-31 | 2026-06-01 | Argent | 24h | SHORT | 75.3693 | 75.0582 | -0.413% | 0.8% | non-conclusive | |delta|=0.413% ≤ seuil=0.8% |
| 2026-05-31 | 2026-06-01 | Blé | 24h | SHORT | 610.7924 | 608.6261 | -0.355% | 0.8% | non-conclusive | |delta|=0.355% ≤ seuil=0.8% |
| 2026-05-31 | 2026-06-01 | CAC 40 | 24h | LONG | 8183.3398 | 8146.5898 | -0.449% | 0.5% | non-conclusive | |delta|=0.449% ≤ seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Cacao | 24h | LONG | 3924.6486 | 3900.5820 | -0.613% | 1.5% | non-conclusive | |delta|=0.613% ≤ seuil=1.5% |
| 2026-05-31 | 2026-06-01 | Café (Arabica) | 24h | LONG | 265.5419 | 260.0702 | -2.061% | 1.0% | FAUSSE | delta=-2.061% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Cuivre | 24h | SHORT | 6.3621 | 6.5513 | +2.974% | 0.8% | FAUSSE | delta=+2.974% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | EUR/USD | 24h | SHORT | 1.1658 | 1.1633 | -0.215% | 0.25% | non-conclusive | |delta|=0.215% ≤ seuil=0.25% |
| 2026-05-31 | 2026-06-01 | Nasdaq | 24h | LONG | 738.2250 | 743.9750 | +0.779% | 0.7% | VRAI | delta=+0.779% vs seuil=0.7% |
| 2026-05-31 | 2026-06-01 | Or | 24h | SHORT | 4542.3575 | 4486.1155 | -1.238% | 0.5% | VRAI | delta=-1.238% vs seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Pétrole (Brent) | 24h | LONG | 91.0995 | 95.0187 | +4.302% | 1.0% | VRAI | delta=+4.302% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | S&P 500 | 24h | LONG | 756.4000 | 759.4900 | +0.409% | 0.4% | VRAI | delta=+0.409% vs seuil=0.4% |
| 2026-05-31 | 2026-06-01 | VIX | 24h | SHORT | 23.2300 | 23.6050 | +1.614% | 5.0% | non-conclusive | |delta|=1.614% ≤ seuil=5.0% |
| 2026-05-30 | 2026-05-31 | Argent | 24h | SHORT | — | 75.0582 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Blé | 24h | LONG | — | 608.6261 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | CAC 40 | 24h | LONG | — | 8146.5898 | — | 0.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cacao | 24h | LONG | — | 3900.5820 | — | 1.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Café (Arabica) | 24h | SHORT | — | 260.0702 | — | 1.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cuivre | 24h | SHORT | — | 6.5513 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | EUR/USD | 24h | SHORT | — | 1.1633 | — | 0.25% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Nasdaq | 24h | SHORT | — | 743.9750 | — | 0.7% | suivi-interrompu | prix d'émission indisponible |
