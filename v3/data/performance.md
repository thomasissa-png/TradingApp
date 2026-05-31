# Performance du bulletin — Journaliste

- Généré : 2026-05-31T10:12:36.007561+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 10.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Blé | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| CAC 40 | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Cacao | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Café (Arabica) | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Cuivre | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| EUR/USD | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Nasdaq | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Or | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| Pétrole (Brent) | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| S&P 500 | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |
| VIX | 24h | 0 | — | 0 | — | — | — | — | shadow | aucune mesure terminée dans la fenêtre |

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
| 2026-05-30 | 2026-05-31 | Argent | 24h | SHORT | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Blé | 24h | LONG | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | CAC 40 | 24h | LONG | — | — | — | 0.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cacao | 24h | LONG | — | — | — | 1.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Café (Arabica) | 24h | SHORT | — | — | — | 1.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Cuivre | 24h | SHORT | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | EUR/USD | 24h | SHORT | — | — | — | 0.25% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Nasdaq | 24h | SHORT | — | — | — | 0.7% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Or | 24h | LONG | — | — | — | 0.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | Pétrole (Brent) | 24h | LONG | — | — | — | 1.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | S&P 500 | 24h | SHORT | — | — | — | 0.4% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-30 | 2026-05-31 | VIX | 24h | LONG | — | — | — | 5.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Argent | 24h | LONG | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Blé | 24h | SHORT | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | CAC 40 | 24h | LONG | — | — | — | 0.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Cacao | 24h | LONG | — | — | — | 1.5% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Café (Arabica) | 24h | SHORT | — | — | — | 1.0% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Cuivre | 24h | SHORT | — | — | — | 0.8% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | EUR/USD | 24h | SHORT | — | — | — | 0.25% | suivi-interrompu | prix d'émission indisponible |
| 2026-05-29 | 2026-05-30 | Nasdaq | 24h | SHORT | — | — | — | 0.7% | suivi-interrompu | prix d'émission indisponible |
