<!-- Version: 2026-05-01T00:00 — @data-analyst — Création edge-rnd-report.md TradingApp Phase 1 -->
# Edge R&D Report — Phase 1 TradingApp

> **Statut** : SQUELETTE — sections en cours de remplissage
> **Auteur** : @data-analyst
> **Date** : 2026-05-01
> **Décision structurante n°4** : R&D edge AVANT tout code de production. No-go assumé acceptable si aucun edge qualifié.

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Méthodologie](#2-méthodologie)
3. [Détail des 7 hypothèses](#3-détail-des-7-hypothèses)
4. [Plan d'exécution physique](#4-plan-dexécution-physique)
5. [Critère GO/NO-GO Phase 2](#5-critère-gonogo-phase-2)
6. [Risques et mitigations](#6-risques-et-mitigations)
7. [Handoff vers @testeur-backtest-edge](#7-handoff-vers-testeur-backtest-edge)
8. [Mise à jour project-context.md](#8-mise-à-jour-project-contextmd)
9. [Auto-évaluation gates](#9-auto-évaluation-gates)

---

## 1. Vue d'ensemble

Ce rapport constitue la **décision structurante n°4** de TradingApp : R&D edge AVANT tout code de production. Il documente la méthodologie, les 7 hypothèses d'edge et les critères stricts qui déterminent si le projet avance vers la Phase 2 (Build) ou accepte le no-go.

**Contexte**. Thomas dispose d'un capital dédié de 20-30 k€ et trade des turbos Bourse Direct sur 13 sous-jacents EU dans la fenêtre 8h45-8h55 CET. La taille de position de référence est 1 500 € × levier × 10 = 15 000 € d'exposition notionnelle. Le problème n'est pas l'exécution — c'est l'absence d'un signal backtesté en qui avoir confiance pour engager ce capital avec levier. La Phase 1 R&D existe pour répondre à une seule question : y a-t-il un edge statistiquement robuste sur cette fenêtre ?

**7 hypothèses à tester** :

| ID | Nom | Famille |
|----|-----|---------|
| H-A | Gap Follow EU Open | Tendance gap |
| H-B | Gap Fade EU Open | Contre-tendance gap |
| H-C | Opening Range Breakout 5/15 min | Momentum intraday |
| H-D | Momentum Overnight US → EU (S&P Futures → CAC/DAX) | Momentum cross-marché |
| H-E | News Pré-marché (sentiment Claude) | Fondamental/alternatif |
| H-F | Écart Spot/Futures à l'ouverture | Arbitrage statistique |
| H-G | Sentiment Overnight Asie → CAC (Nikkei corrélation) | Macro cross-marché |

**Verdict cible** : 5 conditions AND (Sharpe OOS > 1,0 / Profit Factor OOS > 1,5 / Drawdown OOS < 20 % / Robustesse ≥ 50 % / Walk-forward ≥ 2/3 fenêtres > seuil). Si au moins 1 hypothèse PASSE les 5 conditions → GO Phase 2. Sinon → **no-go assumé**, décision structurante n°4 respectée. Le no-go est un résultat valide — mieux vaut pas de bot qu'un bot qui fait perdre 2-3 k€/mois (anti-pattern n°2, project-context.md).

**KPI North Star** : P&L net mensuel après frais Bourse Direct (1,98 € aller-retour) et fiscalité PFU **31,4 %** annuel (12,8 % IR + 18,6 % prélèvements sociaux, taux 2025 confirmé par @legal — legal-audit.md). La performance de la R&D est évaluée en net PFU, pas en brut.

**Périmètre** : ce document couvre exclusivement la Phase 1 R&D. Il ne contient aucune décision de code. L'implémentation est conditionnelle aux résultats de cette phase.

## 2. Méthodologie

### 2.1 Split temporel IS / OOS / Walk-forward

| Période | Rôle | Règle |
|---------|------|-------|
| **2021-2024 (4 ans)** | In-Sample (IS) — optimisation paramètres | Paramètres libres, grid search autorisé |
| **2025 (1 an)** | Out-of-Sample (OOS) — validation stricte | AUCUNE modification paramètre après IS. OOS = black box |
| **Walk-forward fenêtre 1** | IS 2021-2023 / OOS 2024 | Fenêtre glissante |
| **Walk-forward fenêtre 2** | IS 2022-2024 / OOS 2025 | Fenêtre glissante |
| **Walk-forward fenêtre standard** | IS 2021-2024 / OOS 2025 | Référence principale |

**Règle absolue** : regarder l'OOS avant d'avoir fixé les paramètres IS invalide immédiatement l'edge (data snooping bias). Les paramètres sont gelés dès la fin de l'optimisation IS.

**Critère walk-forward** : un edge est robuste si Sharpe_OOS ≥ 50 % × Sharpe_IS sur **au moins 2 fenêtres sur 3**. Un edge qui passe uniquement sur la fenêtre standard mais échoue sur les deux fenêtres glissantes est invalide.

### 2.2 Coûts de transaction intégrés dans chaque simulation

```python
frais_total_par_trade = (
    0.99 + 0.99      # frais Bourse Direct achat + vente = 1,98 €
    + 0.05           # spread émetteur [HYPOTHÈSE — estimation centrale, à mesurer en paper]
    + position * 0.001  # slippage 0,1 % du montant (1500 € × 0,001 = 1,50 €)
)
# Total par aller-retour sur position 1500 € : ~3,53 €
# Impact annualisé sur 252 trades (1/j) : ~890 €/an soit ~5,9 % du capital dédié 15 000 €
```

**Sizing de référence** : 1 500 € par trade × levier × 10 = 15 000 € exposition notionnelle. Taille midpoint de la fourchette persona (1 000-2 000 €).

### 2.3 Tests de robustesse anti-overfitting

| Test | Description | Seuil de rejet |
|------|-------------|----------------|
| **Cherry-picking** | Vérifier que les résultats ne dépendent pas de quelques trades exceptionnels | Retrait des 5 % trades extremes → PF doit rester ≥ 1,3 |
| **Corrélation tickers** | Si l'edge passe sur DAX et CAC simultanément, vérifier corrélation des signaux | Corrélation > 0,7 → compter comme un seul signal (risque doublement de position) |
| **Sensibilité paramètres ±10 %** | Variation de chaque paramètre optimisé de ±10 % → résultats doivent rester ≥ seuils | Si Sharpe chute > 30 % pour variation ±10 % → fragile, invalider |
| **p-value** | Test bootstrap sur la séquence des trades IS (H0 : résultats dus au hasard) | p-value < 0,05 requis (rejet H0 au seuil 5 %) |

### 2.4 Statistiques requises — tableau de reporting par hypothèse

| Statistique | Formule | Seuil GO Phase 2 |
|-------------|---------|------------------|
| Nb trades IS | COUNT(*) trades IS | ≥ 100 (significativité minimale) |
| Win rate IS | Trades gagnants IS / total × 100 | ≥ 50 % |
| Win rate OOS | idem sur 2025 | ≥ Win_rate_IS − 5 pts |
| Profit Factor IS | Σ gains IS / Σ pertes IS | ≥ 1,5 |
| **Profit Factor OOS** | idem sur 2025 | **≥ 1,5** |
| Sharpe ratio annualisé IS | (Rend_moy − Rf) / σ × √252 | > 1,5 |
| **Sharpe ratio annualisé OOS** | idem sur 2025 | **> 1,0** |
| Max drawdown IS | % du capital IS | < 25 % |
| **Max drawdown OOS** | % du capital OOS | **< 20 %** |
| Durée moyenne trade | Σ(exit − entry) / N | 5-45 min (fenêtre Thomas) |
| **Robustesse IS→OOS** | Sharpe_OOS / Sharpe_IS | **≥ 50 %** |
| Walk-forward | Sharpe_OOS sur 2/3 fenêtres | ≥ seuil sur 2 fenêtres min |
| p-value bootstrap | Test H0 : aléatoire | < 0,05 |

## 3. Détail des 7 hypothèses

### H-A Gap Follow EU Open
[STUB — à remplir : ~35 lignes]

### H-B Gap Fade EU Open
[STUB — à remplir : ~35 lignes]

### H-C Opening Range Breakout (ORB) 5/15 min
[STUB — à remplir : ~35 lignes]

### H-D Momentum Overnight US → EU
[STUB — à remplir : ~35 lignes]

### H-E News Pré-marché
[STUB — à remplir : ~35 lignes]

### H-F Écart Spot/Futures
[STUB — à remplir : ~35 lignes]

### H-G Sentiment Asie → CAC
[STUB — à remplir : ~35 lignes]

## 4. Plan d'exécution physique

[STUB — à remplir : ~30 lignes]

## 5. Critère GO/NO-GO Phase 2

[STUB — à remplir : ~15 lignes]

## 6. Risques et mitigations

[STUB — à remplir : ~30 lignes]

## 7. Handoff vers @testeur-backtest-edge

[STUB — à remplir : ~20 lignes]

## 8. Mise à jour project-context.md

[STUB — à remplir : ~5 lignes]

## 9. Auto-évaluation gates

[STUB — à remplir]
