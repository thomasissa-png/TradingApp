# Performance du bulletin — Journaliste

- Généré : 2026-06-01T08:17:49.964712+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 10.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 1 | 0.0% | 1 | 0.0% | 0.000 | 1.0000 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 1 | 0.0% | 1 | 0.0% | 0.000 | 0.2746 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 1 | — | 0 | — | — | — | 0/100% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.0040 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 1 | 100.0% | 1 | 100.0% | 0.206 | 0.0000 | 100/0% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 1 | — | 0 | — | — | — | 100/0% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 1/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
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
| 2026-05-31 | 2026-06-01 | Argent | 24h | SHORT | 75.3693 | 75.7174 | +0.462% | 0.8% | non-conclusive | |delta|=0.462% ≤ seuil=0.8% |
| 2026-05-31 | 2026-06-01 | Blé | 24h | SHORT | 610.7924 | 616.2007 | +0.885% | 0.8% | FAUSSE | delta=+0.885% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | CAC 40 | 24h | LONG | 8183.3398 | 8183.3398 | +0.000% | 0.5% | non-conclusive | |delta|=0.000% ≤ seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Cacao | 24h | LONG | 3924.6486 | 3924.7065 | +0.001% | 1.5% | non-conclusive | |delta|=0.001% ≤ seuil=1.5% |
| 2026-05-31 | 2026-06-01 | Café (Arabica) | 24h | LONG | 265.5419 | 265.5589 | +0.006% | 1.0% | non-conclusive | |delta|=0.006% ≤ seuil=1.0% |
| 2026-05-31 | 2026-06-01 | Cuivre | 24h | SHORT | 6.3621 | 6.4189 | +0.894% | 0.8% | FAUSSE | delta=+0.894% vs seuil=0.8% |
| 2026-05-31 | 2026-06-01 | EUR/USD | 24h | SHORT | 1.1658 | 1.1654 | -0.033% | 0.25% | non-conclusive | |delta|=0.033% ≤ seuil=0.25% |
| 2026-05-31 | 2026-06-01 | Nasdaq | 24h | LONG | 738.2250 | 738.2250 | +0.000% | 0.7% | non-conclusive | |delta|=0.000% ≤ seuil=0.7% |
| 2026-05-31 | 2026-06-01 | Or | 24h | SHORT | 4542.3575 | 4513.8575 | -0.627% | 0.5% | VRAI | delta=-0.627% vs seuil=0.5% |
| 2026-05-31 | 2026-06-01 | Pétrole (Brent) | 24h | LONG | 91.0995 | 93.5917 | +2.736% | 1.0% | VRAI | delta=+2.736% vs seuil=1.0% |
| 2026-05-31 | 2026-06-01 | S&P 500 | 24h | LONG | 756.4000 | 756.4000 | +0.000% | 0.4% | non-conclusive | |delta|=0.000% ≤ seuil=0.4% |
| 2026-05-31 | 2026-06-01 | VIX | 24h | SHORT | 23.2300 | 23.2300 | +0.000% | 5.0% | non-conclusive | |delta|=0.000% ≤ seuil=5.0% |
| 2026-05-30 | 2026-05-31 | Argent | 24h | SHORT | — | 75.7174 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Blé | 24h | LONG | — | 616.2007 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | CAC 40 | 24h | LONG | — | 8183.3398 | — | 0.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cacao | 24h | LONG | — | 3924.7065 | — | 1.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Café (Arabica) | 24h | SHORT | — | 265.5589 | — | 1.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cuivre | 24h | SHORT | — | 6.4189 | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | EUR/USD | 24h | SHORT | — | 1.1654 | — | 0.25% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Nasdaq | 24h | SHORT | — | 738.2250 | — | 0.7% | suivi-interrompu | prix d'émission indisponible |
