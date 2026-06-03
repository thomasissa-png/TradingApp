# Performance du bulletin — Journaliste

- Généré : 2026-06-03T07:05:43.296187+02:00
- Journaliste version : v3.1.0
- Fenêtre KPI : 30 dernières conclusions terminées par cellule
- PROBA_SCALE : 15.0 (proba = 0.5 + clip(|score|/SCALE, 0, 0.5))
- Cible éligibilité : 70% (Bourse.md)

## Matrice cellules (actif × horizon)

| Actif | Horizon | N_total | Taux_brut | N_eff | Taux_eff | Wilson_low | Brier | LONG/SHORT | Statut | Alertes |
|---|---|---|---|---|---|---|---|---|---|---|
| Argent | 24h | 4 | 100.0% | 2 | 100.0% | 0.342 | 0.1976 | 25/75% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 25.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Blé | 24h | 4 | 100.0% | 3 | 100.0% | 0.439 | 0.0911 | 0/100% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| CAC 40 | 24h | 4 | — | 0 | — | — | — | 50/50% | shadow | warm-up non-chevauchant : 0/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cacao | 24h | 3 | 100.0% | 2 | 100.0% | 0.342 | 0.2156 | 100/0% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Café (Arabica) | 24h | 3 | 0.0% | 2 | 0.0% | 0.000 | 0.3128 | 67/33% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Cuivre | 24h | 2 | 50.0% | 2 | 50.0% | 0.095 | 0.1662 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| EUR/USD | 24h | 2 | 100.0% | 1 | 100.0% | 0.206 | 0.2203 | 0/100% | shadow | warm-up non-chevauchant : 1/15 obs effectives; 2/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Nasdaq | 24h | 4 | 100.0% | 2 | 100.0% | 0.342 | 0.0324 | 50/50% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Or | 24h | 4 | 100.0% | 3 | 100.0% | 0.439 | 0.1123 | 0/100% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 0.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| Pétrole (Brent) | 24h | 3 | 100.0% | 3 | 100.0% | 0.439 | 0.0666 | 100/0% | shadow | warm-up non-chevauchant : 3/15 obs effectives; 3/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 100.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
| S&P 500 | 24h | 4 | 100.0% | 2 | 100.0% | 0.342 | 0.1650 | 75/25% | shadow | warm-up non-chevauchant : 2/15 obs effectives; 4/30 mesures terminées (fenêtre brute warm-up); biais distribution : LONG 75.0% (hors [30.0,70.0]%); 2 suivi(s) interrompu(s) sur la fenêtre observable |
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
| Argent | 24h | 1 | 100.0% | 1 | 100.0% |
| Blé | 24h | 1 | 100.0% | 2 | 100.0% |
| Cacao | 24h | 0 | — | 2 | 100.0% |
| Café (Arabica) | 24h | 1 | 0.0% | 1 | 0.0% |
| Cuivre | 24h | 1 | 100.0% | 1 | 0.0% |
| EUR/USD | 24h | 0 | — | 1 | 100.0% |
| Nasdaq | 24h | 1 | 100.0% | 1 | 100.0% |
| Or | 24h | 1 | 100.0% | 2 | 100.0% |
| Pétrole (Brent) | 24h | 0 | — | 3 | 100.0% |
| S&P 500 | 24h | 1 | 100.0% | 1 | 100.0% |

- **Taux global flips** : 85.7% (N=7 mesures avec is_flip=True)
- **Taux global continuations** : 86.7% (N=15 mesures avec is_flip=False)

## Dernières mesures (max 20)

| Émission | Échéance | Actif | Horizon | Concl. | Prix émis. | Prix actuel | Delta % | Seuil % | Outcome | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-06-02 | 2026-06-03 | Argent | 24h | SHORT | 76.4176 | 74.7049 | -2.241% | 0.8% | VRAI | delta=-2.241% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | Blé | 24h | SHORT | 605.6869 | 598.8305 | -1.132% | 0.8% | VRAI | delta=-1.132% vs seuil=0.8% |
| 2026-06-02 | 2026-06-03 | CAC 40 | 24h | SHORT | 8216.0098 | 8209.0898 | -0.084% | 0.5% | non-conclusive | |delta|=0.084% ≤ seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Nasdaq | 24h | SHORT | 742.6900 | 746.1400 | +0.465% | 0.7% | non-conclusive | |delta|=0.465% ≤ seuil=0.7% |
| 2026-06-02 | 2026-06-03 | Or | 24h | SHORT | 4526.7303 | 4470.2727 | -1.247% | 0.5% | VRAI | delta=-1.247% vs seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Pétrole (Brent) | 24h | LONG | 93.1302 | 97.0872 | +4.249% | 1.0% | VRAI | delta=+4.249% vs seuil=1.0% |
| 2026-06-02 | 2026-06-03 | S&P 500 | 24h | SHORT | 758.4400 | 759.4700 | +0.136% | 0.4% | non-conclusive | |delta|=0.136% ≤ seuil=0.4% |
| 2026-06-02 | 2026-06-03 | VIX | 24h | LONG | 23.8650 | 23.4600 | -1.697% | 3.0% | non-conclusive | |delta|=1.697% ≤ seuil=3.0% |
| 2026-06-02 | 2026-06-03 | Cacao | 24h | INSUFFISANT | 3894.4308 | 4109.7536 | — | 1.0% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Café (Arabica) | 24h | INSUFFISANT | 260.4126 | 259.1988 | — | 1.0% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Cuivre | 24h | INSUFFISANT | 6.6085 | 6.6240 | — | 0.8% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | EUR/USD | 24h | INSUFFISANT | 1.1643 | 1.1626 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Argent | 24h | SHORT | 75.1654 | 74.7049 | -0.613% | 0.8% | non-conclusive | |delta|=0.613% ≤ seuil=0.8% |
| 2026-06-02 | 2026-06-03 | Blé | 24h | SHORT | 602.4645 | 598.8305 | -0.603% | 0.8% | non-conclusive | |delta|=0.603% ≤ seuil=0.8% |
| 2026-06-02 | 2026-06-03 | CAC 40 | 24h | SHORT | 8209.0898 | 8209.0898 | +0.000% | 0.5% | non-conclusive | |delta|=0.000% ≤ seuil=0.5% |
| 2026-06-02 | 2026-06-03 | Cacao | 24h | LONG | 4075.9593 | 4109.7536 | +0.829% | 1.0% | non-conclusive | |delta|=0.829% ≤ seuil=1.0% |
| 2026-06-02 | 2026-06-03 | Café (Arabica) | 24h | SHORT | 259.2777 | 259.1988 | -0.030% | 1.0% | non-conclusive | |delta|=0.030% ≤ seuil=1.0% |
| 2026-06-02 | 2026-06-03 | EUR/USD | 24h | INSUFFISANT | 1.1632 | 1.1626 | — | 0.25% | non-notee | cellule INSUFFISANT — pas de prédiction (gate suffisance) |
| 2026-06-02 | 2026-06-03 | Nasdaq | 24h | SHORT | 746.2400 | 746.1400 | -0.013% | 0.7% | non-conclusive | |delta|=0.013% ≤ seuil=0.7% |
| 2026-06-02 | 2026-06-03 | Or | 24h | SHORT | 4487.9275 | 4470.2727 | -0.393% | 0.5% | non-conclusive | |delta|=0.393% ≤ seuil=0.5% |
