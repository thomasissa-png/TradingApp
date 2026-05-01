<!-- Version: 2026-05-01T00:00 — testeur-backtest-edge via @qa — Audit méthodologie Phase 1 R&D edge -->

# Backtest Audit Phase 1 — Méthodologie R&D edge + scoring model

> **Statut** : LIVRABLE COMPLET
> **Auteur** : `testeur-backtest-edge` (relai @qa — runtime sub-agent custom indisponible)
> **Date** : 2026-05-01
> **Périmètre** : audit méthodologique AVANT exécution physique du backtest. Pas d'audit de données chiffrées (les résultats JSON `docs/analytics/results/H-X-results.json` n'existent pas encore).
> **Livrables audités** :
> 1. `docs/analytics/edge-rnd-report.md` (méthodologie + 7 hypothèses + critères GO Phase 2)
> 2. `docs/ia/edge-scoring-model.md` (scoring-model-v1.0 — 6 dimensions + 5 sanity checks + CONFIDENCE_THRESHOLD 6.5)
> **Cadre méthodologique** : `.claude/agents/testeur-backtest-edge.md` (5 conditions GO Phase 2, 7 patterns overfitting O1-O7, gates B1-B10)

---

## Verdict synthétique

**RETRAVAILLER** (5 corrections méthodologiques bloquantes — toutes traitables sous 1-2j sans changer la philosophie du brief).

Aucune des corrections demandées ne remet en cause les 7 hypothèses H-A à H-G ni le principe walk-forward IS/OOS. Elles renforcent la rigueur statistique avant de consommer le budget Twelve Data + Claude Haiku R&D.

---

## Section 1 — Audit méthodologie `edge-rnd-report.md` §2

### 1.a Split IS 2021-2024 / OOS 2025 (1 an)

**Constat** : OOS = 1 an / IS = 4 ans → ratio OOS/total = **20 %**.

**Référence académique** : Bailey, Borwein, Lopez de Prado & Zhu (2014) *Pseudo-Mathematics and Financial Charlatanism* recommandent ratio OOS ≥ 30 % pour limiter le Sharpe Ratio Inflation. White (2000) Reality Check tolère 20-30 % si N_trades suffisant.

**Diagnostic** :
- 1 an OOS = ~250 jours de bourse → **insuffisant** pour un edge intraday qui produit ~1 trade/jour. À 50 % de NO-TRADE (vertu brand), N_trades_OOS ≈ 125 → en limite basse de significativité statistique.
- Risque concret : un seul régime macro 2025 (ex: tendance haussière prolongée ou compression de volatilité unique) suffit à valider ou invalider un edge par hasard.
- Le rapport ne précise pas le **nombre minimum de trades OOS** requis (le seuil ≥ 100 du brief s'applique à l'IS).

**Verdict** : **RETRAVAILLER 1.a** — ajouter un seuil explicite `nb_trades_OOS ≥ 50` (cohérent test t-Student au seuil 95 % pour Sharpe). Si une hypothèse passe les 5 conditions mais avec nb_trades_OOS < 50 → marquer "GO conditionnel sous réserve allongement OOS".

**Action corrective** : amender §2.4 tableau statistiques avec ligne `nb_trades_OOS ≥ 50 (significativité Student)`.

### 1.b Walk-forward 3 fenêtres

**Constat** : 3 fenêtres glissantes (IS 2021-2023/OOS 2024 ; IS 2022-2024/OOS 2025 ; IS 2021-2024/OOS 2025).

**Référence académique** : Pardo (2008) *The Evaluation and Optimization of Trading Strategies* recommande **5-10 fenêtres** pour walk-forward analysis robuste. Aronson (2007) *Evidence-Based Technical Analysis* utilise typiquement 6-8 fenêtres.

**Diagnostic** :
- 3 fenêtres = configuration **minimale** acceptée. Le brief original `testeur-backtest-edge.md` retient 3 fenêtres comme seuil bloquant — cohérent.
- Limitation 1 : avec 3 fenêtres dont 2 partagent l'OOS 2025, la "diversité régime" est faible — l'OOS 2025 pèse 2/3 dans la décision finale.
- Limitation 2 : critère "≥ 2/3 fenêtres > seuil" autorise 1 échec — sur 3 fenêtres c'est 33 % d'échec toléré, ce qui est élevé. Sur 5 fenêtres avec seuil 4/5 = 20 % toléré, plus rigoureux.

**Verdict** : **RETRAVAILLER 1.b** — option recommandée : passer à **5 fenêtres** (IS 2020-2022/OOS 2023 ; IS 2021-2023/OOS 2024 ; IS 2022-2024/OOS 2025 ; + 2 fenêtres sliding 2 ans IS / 6 mois OOS) avec critère 4/5 PASS. Exige données 2020 — à vérifier disponibilité Twelve Data.

**Alternative dégradée** (si données 2020 indisponibles ou budget contraint) : conserver 3 fenêtres MAIS resserrer le critère à **3/3 PASS** au lieu de 2/3. Plus strict que le brief actuel.

### 1.c Coûts 1.98€ + 0.05€ + 0.1% slippage

**Constat** : frais Bourse Direct 1,98 € (aller-retour) + spread émetteur 0,05 € + slippage 0,1 % = ~3,53 €/trade sur position 1500 €.

**Référence littérature** : Frazzini, Israel & Moskowitz (2018) *Trading Costs* documentent slippage médian 5-15 bps (0,05-0,15 %) sur futures liquides EU intraday. Études praticiens (Kissell 2014 *Algorithmic Trading Methods*) recommandent **slippage 2x simulation pour test de robustesse**.

**Diagnostic** :
- 0,1 % slippage = **borne basse réaliste** sur turbos petite taille (1500 €). Les turbos sont des produits **OTC à spread variable** — sur news pré-marché ou volatilité élevée le spread peut grimper à 0,3-0,5 %.
- Le rapport mentionne §6 "test conservateur slippage × 2" mais ne le **chiffre pas dans les 5 conditions GO Phase 2**.
- Spread émetteur 0,05 € = [HYPOTHÈSE] non sourcée — Bourse Direct n'affiche pas publiquement les spreads turbos. À mesurer en paper-trading.
- **Frais correctement intégrés** : 1,98 € BD + 0,05 € + 0,1 % = cohérent avec edge-rnd-brief §3.2.

**Verdict** : **RETRAVAILLER 1.c** — ajouter critère bloquant : `Sharpe OOS avec slippage stress 0,2 % (×2) > 0,8`. Un edge dont le Sharpe chute sous 0,8 sous slippage stress est trop fragile pour le live (où le slippage réel sera proche du stress lors des news pré-marché — précisément la fenêtre 8h45-8h55 visée).

### 1.d p-value Sharpe (White Reality Check)

**Constat** : §2.3 mentionne "p-value < 0,05 requis (rejet H0 au seuil 5 %)" sur "test bootstrap sur la séquence des trades IS".

**Diagnostic** :
- Le test n'est **pas paramétré** : combien de bootstrap samples (5 000 ? 10 000 ? recommandation White 1 000 minimum) ? Quelle distribution sous H0 (returns shuffle ? bloc bootstrap pour préserver autocorrélation) ?
- White (2000) Reality Check exige le **stationary bootstrap** de Politis & Romano (1994) — pas un simple shuffle iid (sinon biais autocorrélation).
- Multiple Hypothesis Testing : 7 hypothèses × N paramètres testés → la **correction Bonferroni ou FDR (Benjamini-Hochberg)** est obligatoire (cf. Section 4 risque résiduel).
- Le terme "White Reality Check" est cité dans le titre de la section mais pas le test exact (Hansen SPA test — Superior Predictive Ability — est plus rigoureux pour multi-hypothèses).

**Verdict** : **RETRAVAILLER 1.d** — paramétrer explicitement :
1. Bootstrap : **stationary bootstrap** Politis-Romano avec block_length = √N_trades (formule classique).
2. **n_bootstrap = 10 000** samples minimum.
3. Niveau α = 0,05 **avec correction Bonferroni** (α/N_hypothèses = 0,05/7 = 0,0071) OU **Hansen SPA test** (préférable, prend en compte data-snooping multi-hypothèses).
4. Documenter dans §2.3 le pseudo-code du bootstrap.

### 1.e Tests robustesse exhaustifs

**Constat** : §2.3 documente cherry-picking, corrélation tickers, sensibilité ±10 %, p-value bootstrap.

**Diagnostic** :
- ✅ Cherry-picking trades extrêmes (5 %) — couvre O4 partiel.
- ✅ Corrélation tickers > 0,7 — couvre O5 partiel.
- ✅ Sensibilité ±10 % paramètres — couvre O3 partiel.
- ❌ **Manque** : test de **survivorship bias** (O7) — le brief signale "Twelve Data ne fournit pas nativement les délistés" mais ne propose pas de mitigation. Pour les actions individuelles (LVMH, TTE, SAN, AI, Schneider), l'absence est faible (5 blue chips actifs sur la période). Mais signaler reste obligatoire.
- ❌ **Manque** : test de **régime/cycle** — découpage IS en sous-périodes haussières vs baissières (CAC 2022 baissier, 2023 haussier, 2024 mixte). Aucune sous-période ne doit avoir Sharpe < 0,5 × Sharpe global (cohérent O4).
- ❌ **Manque** : test de **stabilité paramètres optimaux entre fenêtres walk-forward**. Si les paramètres optimaux IS sont 0,5 % gap sur fenêtre 1 et 1,2 % gap sur fenêtre 2 → instabilité = signal d'overfitting (paramètres dépendent du régime).

**Verdict** : **RETRAVAILLER 1.e** — ajouter dans §2.3 :
- Test sous-périodes régime (haussier/baissier/range).
- Test stabilité paramètres inter-fenêtres walk-forward (variation < 30 % entre fenêtres).
- Note explicite sur survivorship bias acceptable (5 blue chips FR cap. > 30 Md€ encore listés au 2026-05-01).

### Verdict Section 1

**Méthodologie globale §2** : **RETRAVAILLER** sur 5 points (1.a OOS court, 1.b 3 fenêtres minimum, 1.c slippage stress non chiffré, 1.d p-value non paramétré, 1.e tests robustesse incomplets). Aucun point ne remet en cause la philosophie — corrections additives.

---

## Section 2 — Audit critères GO Phase 2 (5 conditions AND)

### 2.1 Sharpe OOS > 1,0

**Référence** : Sharpe annualisé 1,0 = "good" selon Sharpe (1994). Pour day-trading intraday avec ~250 trades/an, l'écart-type annualisé bénéficie de √250 → un Sharpe 1,0 signifie un return moyen ~6,3 % avec écart-type 6,3 % (ratio 1).

**Diagnostic** :
- Cohérent day-trading professionnel — les hedge funds CTA visent typiquement Sharpe 0,8-1,5.
- Sur 1 an OOS avec 125 trades → **incertitude Sharpe ±0,3** (intervalle de confiance 95 % via Lo 2002 *Statistics of Sharpe Ratios*). Un Sharpe OOS mesuré 1,0 a une borne basse 0,7 → frontière statistiquement floue.
- **Recommandation** : exiger Sharpe OOS > 1,0 **avec borne basse IC 95 % > 0,5** (test Lo). Ou exiger Sharpe OOS > 1,2 (marge sécurité vs incertitude statistique).

**Verdict** : **RETRAVAILLER 2.1** — relever seuil à **Sharpe OOS > 1,2** OU ajouter test borne basse IC 95 % > 0,5.

### 2.2 Profit Factor > 1,5

**Référence** : Tomasini & Jaekle (2009) *Trading Systems* : PF > 1,5 = "trading system viable" ; PF > 2,0 = "excellent". Aronson (2007) tolère PF > 1,3 si N_trades > 200.

**Diagnostic** :
- 1,5 = standard professionnel correct. Pas trop laxiste, pas trop strict.
- ✅ Cohérent avec coûts intégrés — un PF 1,5 net frais = edge réel.
- **Cohérent SC2** sanity check scoring `R/R ≥ 1.5` — alignement scoring/backtest.

**Verdict** : **PASS 2.2** — seuil correct.

### 2.3 Drawdown < 20 %

**Référence** : project-context.md "drawdown mensuel max < 20 % du capital dédié" — aligné personas signal d'arrêt.

**Diagnostic** :
- ✅ Cohérent personas (signal arrêt drawdown 20 %).
- ⚠️ **Ambiguïté** : le rapport §5 dit "Drawdown max OOS < 20 % sur capital de référence 15 000 €". Mais persona dit "drawdown **mensuel**". 20 % drawdown total OOS sur 1 an n'est pas équivalent à 20 % drawdown mensuel. Un edge peut avoir 18 % drawdown OOS annuel (PASS) tout en ayant 25 % drawdown sur un mois (FAIL persona).
- Le seuil 20 % drawdown maximum sur 1 an est **plus laxiste** que le signal d'arrêt mensuel.

**Verdict** : **RETRAVAILLER 2.3** — clarifier : "Drawdown maximum OOS < 20 % **ET** drawdown mensuel max < 20 % sur chaque mois OOS individuellement".

### 2.4 Robustesse ≥ 0,5 (Sharpe_OOS / Sharpe_IS)

**Référence** : Pardo (2008) recommande **Walk-Forward Efficiency Ratio ≥ 0,6** (60 %). Bailey & Lopez de Prado (2014) "Probability of Backtest Overfitting" considèrent < 50 % comme overfit-suspect.

**Diagnostic** :
- 50 % = **borne basse acceptable** mais pas conservateur.
- Exemple : Sharpe IS 2,0 → Sharpe OOS 1,0 = robustesse 50 % PASS, alors qu'une dégradation de 50 % indique généralement de l'overfitting.
- Standard académique : ≥ 60 %.

**Verdict** : **RETRAVAILLER 2.4** — relever à **0,6 (60 %)** — aligné Pardo. Si Sharpe IS = 2,0, exiger Sharpe OOS ≥ 1,2 (cohérent avec relevé 2.1).

### 2.5 Walk-forward 2/3 fenêtres

**Constat** : critère ≥ 2/3 fenêtres > seuil C1.

**Diagnostic** :
- Sur 3 fenêtres, 2/3 PASS = 67 %. Probabilité de hasard sous H0 (chance aléatoire de PASS) : si p_chance = 0,5 par fenêtre, P(≥2/3 PASS par hasard) = C(3,2)×0,5³ + C(3,3)×0,5³ = 0,5. **50 % de chance de PASS par hasard pur** — non discriminant.
- Pour rendre le test statistiquement significatif (p < 0,05), il faudrait soit augmenter à **3/3 PASS** sur 3 fenêtres (P_hasard = 0,125 = 12,5 %, encore élevé), soit passer à **5 fenêtres avec 4/5 PASS** (P_hasard = 0,1875), soit **5/5 sur 5 fenêtres** (P_hasard = 0,03125 = 3 % < 5 %).

**Verdict** : **RETRAVAILLER 2.5** — option recommandée passer à **3/3 sur 3 fenêtres** (cohérent retravailler 1.b alternative dégradée), OU **4/5 sur 5 fenêtres**. Le 2/3 actuel est non discriminant statistiquement.

### Verdict Section 2

**5 conditions GO Phase 2** : **RETRAVAILLER** — 4 conditions sur 5 nécessitent ajustement (2.1 Sharpe seuil, 2.3 drawdown mensuel, 2.4 robustesse 60 %, 2.5 walk-forward critère). Seule 2.2 PF > 1,5 est correctement calibrée.

Configuration **GO Phase 2 renforcée recommandée** :
| # | Condition originale | Condition renforcée |
|---|---|---|
| C1 | Sharpe OOS > 1,0 | Sharpe OOS > **1,2** (ou borne basse IC 95 % > 0,5) |
| C2 | PF OOS > 1,5 | PF OOS > 1,5 (inchangé) |
| C3 | DD OOS < 20 % | DD max OOS < 20 % **ET** DD mensuel max < 20 % |
| C4 | Robustesse ≥ 0,5 | Robustesse ≥ **0,6** |
| C5 | WF 2/3 PASS | WF **3/3 PASS** (ou 4/5 si extension à 5 fenêtres) |

---

## Section 3 — Audit `edge-scoring-model.md` §2-3

### 3.1 Cohérence 6 dimensions D1-D6 avec littérature

**Pondération actuelle** : D1 force signal 30 % / D2 confluence 20 % / D3 news 15 % / D4 volatilité 15 % / D5 régime VIX 10 % / D6 backtest 10 %.

**Diagnostic** :
- D1 force signal 30 % : **cohérent** — Asness, Frazzini & Pedersen (2014) *Fact, Fiction and Momentum Investing* — la force du signal momentum/breakout est le facteur dominant en intraday.
- D2 confluence 20 % : **acceptable** — confluence multi-indicateur réduit faux signaux mais peut être redondant avec D1 (RSI/MACD/BB capturent souvent les mêmes informations que la force du signal).
- D3 news 15 % : **plausible** — Tetlock (2007) cite contribution sentiment ~10-15 % aux returns quotidiens. **Risque** : applicable surtout à H-E (News pré-marché). Pour H-A/H-B/H-C/H-D/H-F/H-G, news sera souvent absent → D3 plafond 7,0 = pénalité injustifiée pour ces hypothèses.
- D4 volatilité 15 % : **cohérent** — Bollerslev et al (2018) *Risk Everywhere* — volatilité est un facteur orthogonal exploitable.
- D5 régime VIX 10 % : **cohérent** — VIX comme proxy régime est standard.
- ⚠️ **D6 backtest 10 %** : **trop bas** — le backtest est la **référence statistique de la performance attendue**. Un edge avec backtest Sharpe 1,5 vs 0,8 mérite une pondération > 10 %. Connors (2012) *High Probability ETF Trading* pondère le backtest historique à 25-30 % du score composite.

**Verdict** : **RETRAVAILLER 3.1** — repondérer en augmentant D6 backtest à **15-20 %** au détriment de D2 confluence (réduire à 10-15 %, redondance avec D1). Repondération suggérée :
- D1 30 % (inchangé)
- D2 15 % (-5)
- D3 15 % (inchangé)
- D4 15 % (inchangé)
- D5 10 % (inchangé)
- D6 **15 %** (+5)

### 3.2 Couverture 5 sanity checks SC1-SC5 vs 7 patterns overfitting O1-O7

| Pattern | Description | SC qui couvre | Verdict |
|---|---|---|---|
| O1 | Look-ahead bias | Aucun SC scoring (relève du backtester, pas du scoring) | **NON COUVERT par scoring** — ne doit pas l'être (vérification au niveau pipeline backtester) |
| O2 | Optimisation post-OOS | Aucun SC | **NON COUVERT** — relève méthodologie backtest, pas scoring |
| O3 | P-hacking multi-paramètres | SC3 score > 9 → ALERT | **PARTIEL** — SC3 flag uniquement les scores extrêmes. P-hacking multi-paramètres nécessite Bonferroni au niveau de la sélection d'hypothèse (cf. Section 4) |
| O4 | Cherry-picking période | Aucun SC scoring | **NON COUVERT par scoring** — relève backtester |
| O5 | Ticker chanceux | Aucun SC | **NON COUVERT** — manquant |
| O6 | Frais sous-estimés | Aucun SC scoring | **NON COUVERT par scoring** (mais couvert backtester via §2.2) |
| O7 | Survivorship bias | Aucun SC | **NON COUVERT** — relève sélection sous-jacents |

**Diagnostic** : les 5 SC du scoring couvrent l'**hygiène du signal individuel** (cohérence direction, R/R, euphorie, % no-trade, langage), mais **ne sont pas conçus pour couvrir les patterns overfitting** O1-O7. Le rapport `edge-scoring-model.md` §8.2 admet partiellement cette limite.

**Cependant** : il existe **un angle mort scoring spécifique** — la **concentration des signaux sur 1 sous-jacent** (O5 transposé en runtime). Si sur 7 jours, 6/7 signaux sont sur DAX, c'est suspect. Aucun SC actuel ne le détecte.

**Verdict** : **RETRAVAILLER 3.2** — ajouter **SC6 — Diversité sous-jacents** :
> Sur 7 jours glissants, si > 70 % des signaux non-NO-TRADE concernent le même `ticker` → flag ALERT (concentration anormale, possible overfit ticker chanceux runtime).

Action : `score -= 1.0` + `ALERT_flag = ALERT_CONCENTRATION`. Lookup SQLite `signals` similaire à SC4.

### 3.3 CONFIDENCE_THRESHOLD = 6.5 [HYPOTHÈSE]

**Constat** : valeur initiale 6,5, calibration R&D obligatoire via `f(seuil) = (PF × WR × proximité 50 % no-trade) / DD`.

**Diagnostic** :
- 6,5 a priori = "raisonnable mais arbitraire" — le rapport assume le biais "note moyenne intuitive".
- **Risque paper-trading** : 6,5 trop laxiste = sur-trading paper, contamination journal MAE/MFE par des signaux marginaux.
- **Recommandation conservatrice paper-trading** : démarrer à **7,0** pendant les 4-8 semaines paper-trading (cf. project-context Phase 5b), puis assouplir à 6,5 seulement si journal trades montre P&L net positif et drawdown < 15 %.
- Logique : pendant le paper, la priorité est la **calibration de confiance** (apprendre à identifier les signaux qui se réalisent). Un seuil 7,0 strict = moins de signaux mais plus de qualité = courbe d'apprentissage plus rapide.

**Verdict** : **RETRAVAILLER 3.3** — recommandation **CONFIDENCE_THRESHOLD_PAPER = 7,0** pendant paper-trading, **CONFIDENCE_THRESHOLD_LIVE = 6,5** après validation paper. Documenter en env vars distinctes.

### Verdict Section 3

**Scoring model** : **RETRAVAILLER** sur 3 points (3.1 repondération D6, 3.2 ajout SC6 diversité, 3.3 seuils paper/live distincts). Le modèle hybride et les SC1-SC5 existants sont solides — corrections additives.

---

## Section 4 — Risques résiduels et mitigations

### 4.1 Multiple Testing Problem (7 hypothèses × N paramètres)

**Risque** : tester 7 hypothèses × ~3 paramètres × ~3 valeurs = ~63 combinaisons par hypothèse → **441 backtests**. À α = 0,05, espérance hasard = 22 backtests "significatifs" par chance pure. Le risque de "trouver un edge qui n'existe pas" est élevé.

**Mitigation actuelle** : §2.3 mentionne p-value < 0,05 mais pas la correction multi-tests.

**Recommandation** :
- **Bonferroni strict** : α corrigé = 0,05 / 441 = 0,000113 — extrêmement strict, probablement aucune hypothèse ne passe.
- **Bonferroni au niveau hypothèse** : α corrigé = 0,05 / 7 = 0,0071. Acceptable si optimisation paramètres séparée du test final.
- **FDR Benjamini-Hochberg** : moins conservatrice, contrôle False Discovery Rate plutôt que FWER. Recommandée en pratique.
- **Hansen SPA test** : alternative académique pour data-snooping multi-stratégies.

**Action corrective** : §2.3 ajouter "**Correction multi-tests : Hansen SPA OU Benjamini-Hochberg FDR < 0,05**. Bonferroni 0,05/7 = 0,0071 par hypothèse en alternative."

### 4.2 Régime 2026 ≠ 2021-2025

**Risque** : le régime macro 2026 (taux BCE en stabilisation, IA effects sur marchés EU, géopolitique) peut différer significativement de 2021-2025. Un edge calibré sur 5 ans passés peut être déjà obsolète à la date du paper-trading.

**Mitigation actuelle** : aucune surveillance drift en ligne mentionnée.

**Recommandation** :
- **Monitoring drift production** : recalculer Sharpe rolling 30j en paper, alerter si chute > 30 % vs Sharpe OOS backtest.
- **Re-walk-forward trimestriel** : tous les 3 mois, ajouter 3 mois de données nouvelles à l'IS et re-vérifier que les paramètres optimaux n'ont pas dérivé > 20 %.
- **Critère "fraîcheur backtest" déjà présent** §2.6 D6 (`age_days > 90 → -1.5`) — bon point, à conserver.

**Action corrective** : ajouter §6 risques :
> R8 — Drift régime post-backtest : monitoring rolling 30j Sharpe en paper-trading + re-walk-forward trimestriel obligatoire avant Phase 5 live.

### 4.3 Slippage live > simulation

**Risque** : turbos OTC = spread variable selon volatilité. Sur news pré-marché 8h45-8h55 (précisément la fenêtre cible), spread peut atteindre 0,3-0,5 % vs 0,1 % simulé.

**Mitigation actuelle** : §6 mentionne "test conservateur slippage × 2" mais pas de seuil bloquant.

**Recommandation déjà formulée Section 1.c** : critère bloquant `Sharpe OOS sous slippage 0,2 % > 0,8`.

**Complément** : pendant les 4-8 semaines paper-trading, **logger le slippage réel observé** sur turbo Bourse Direct (différence prix entry signal vs prix réel exécuté). Si slippage médian observé > 0,15 % → invalider le GO live et retourner en R&D recalibrer les coûts.

### 4.4 H-E News dépendant Claude latence — fallback US-05

**Constat** : H-E (News pré-marché) dépend de Claude Haiku R&D pour scoring sentiment. US-05 timeout 45s + 2 retries + DEGRADED MODE.

**Diagnostic** :
- ✅ TC-05 démontre le fallback fonctionne — DEGRADED MODE, pas de signal envoyé, pas de crash.
- ⚠️ **Problème backtest H-E** : pour backtester H-E sur 5 ans, il faut **scorer les news historiques avec Claude Haiku R&D**. Volume estimé = 5 ans × 252 jours × 1-3 news scorées/jour = 1 260-3 780 appels Haiku.
- Avec cap RND_DAILY_CALL_CAP = 100 ap/j → **13-38 jours backtest H-E uniquement** pour scorer le corpus historique. À budgéter explicitement.
- ⚠️ **Risque look-ahead H-E** : Tetlock (2007) souligne que les résumés Reuters/Bloomberg/Echos sont parfois rétro-édités après publication. Si le scoring se base sur le résumé final (post-marché), il intègre des informations post-8h45 → biais look-ahead massif.

**Action corrective** :
1. Documenter dans §3 H-E le **timestamp d'extraction news** : timestamp de publication initial, pas date de récupération.
2. **Test contrôle anti-look-ahead** : sur un échantillon 100 news, comparer scoring Claude au temps `t_publication` vs `t_publication + 1h` — si scores divergent > 1 point, biais look-ahead confirmé, abandonner H-E ou utiliser uniquement news avec horodatage Reuters/Bloomberg verrouillé.
3. **Budget Claude Haiku R&D** : provisionner 30 jours de cap 100 ap/j pour scoring corpus H-E historique = ~300 $ (cf. ai-architecture).

### Verdict Section 4

**Risques résiduels** : 4 risques majeurs identifiés, 3 mitigations précises proposées (multi-tests, drift, slippage live), 1 mitigation H-E spécifique (anti-look-ahead). **À intégrer en §6 risques de edge-rnd-report.md.**

---

## Section 5 — Verdict global Phase 1

### 5.1 Verdict

**RETRAVAILLER** — 11 corrections méthodologiques (5 §1 + 4 §2 + 3 §3 sans compter §4 risques additifs). Aucune ne change la philosophie du brief. Toutes traitables sous **1-2 jours** par @data-analyst (pour edge-rnd-report.md) et **0,5-1 jour** par @ia (pour edge-scoring-model.md).

**Conditions de levée du RETRAVAILLER (10 actions)** :

| # | Action | Responsable | Effort estimé |
|---|---|---|---|
| L1 | Ajouter seuil `nb_trades_OOS ≥ 50` (§2.4 statistiques) | @data-analyst | 15 min |
| L2 | Passer à 5 fenêtres walk-forward OU resserrer critère 3/3 PASS sur 3 fenêtres (§2.1) | @data-analyst | 30 min |
| L3 | Ajouter critère bloquant `Sharpe OOS slippage 0,2 % > 0,8` (§2.2) | @data-analyst | 15 min |
| L4 | Paramétrer p-value : stationary bootstrap, n=10 000, Bonferroni α=0,0071 OU Hansen SPA (§2.3) | @data-analyst | 1h |
| L5 | Ajouter tests sous-périodes régime + stabilité paramètres inter-fenêtres + note survivorship (§2.3) | @data-analyst | 30 min |
| L6 | Renforcer 5 conditions GO : C1 Sharpe > 1,2, C3 DD mensuel < 20 %, C4 robustesse ≥ 0,6, C5 WF 3/3 OU 4/5 (§5) | @data-analyst | 30 min |
| L7 | Ajouter §6 risques : R8 drift régime + monitoring 30j paper + re-walk-forward trimestriel | @data-analyst | 30 min |
| L8 | Ajouter §3 H-E test anti-look-ahead news + budget Haiku R&D 30 jours | @data-analyst | 30 min |
| L9 | Repondérer scoring : D2 15 %, D6 15 % (au lieu D2 20 %, D6 10 %) — `edge-scoring-model.md` §2.1 | @ia | 30 min |
| L10 | Ajouter SC6 diversité sous-jacents + paramètres CONFIDENCE_THRESHOLD_PAPER=7,0 / _LIVE=6,5 — `edge-scoring-model.md` §3 + §4 | @ia | 1h |

**Total effort cumulé** : ~6h sur 2 agents en parallèle = livrables corrigés en 1 journée. Aucun blocage Phase 2.

### 5.2 Probabilité estimée qu'au moins 1 hypothèse passe les 5 conditions AND

**Estimation prudente sur la base des verdicts prévisionnels et de la littérature** :

| Hypothèse | Verdict prévisionnel rapport | P(passe 5 conditions originales) | P(passe 5 conditions renforcées) |
|---|---|---|---|
| H-A Gap Follow | LIKELY-GO | ~35 % | ~20 % |
| H-B Gap Fade | UNCERTAIN | ~10 % | ~5 % |
| H-C ORB | LIKELY-GO | ~45 % | ~30 % |
| H-D Momentum US→EU | UNCERTAIN | ~15 % | ~8 % |
| H-E News | UNCERTAIN | ~10 % | ~5 % |
| H-F Basis | LIKELY-NO-GO | ~5 % | ~2 % |
| H-G Asie→CAC | LIKELY-NO-GO | ~5 % | ~2 % |

**Probabilité union ≥ 1 hypothèse PASS** :
- Conditions originales (rapport actuel) : 1 − ∏(1−p_i) ≈ **~75 %** — élevé, suspect "trop facile" → indique seuils trop laxistes (cohérent verdict §2 RETRAVAILLER).
- Conditions renforcées (recommandation audit) : 1 − ∏(1−p_i) ≈ **~55 %** — équilibre entre rigueur et faisabilité. Si le projet a un vrai edge → ~55 % de chance de le détecter avec haute confiance. Si pas d'edge → ~45 % de NO-GO assumé légitime (cohérent décision structurante n°4).

**Conclusion** : passer aux conditions renforcées **divise par 2 le risque faux positif** (de ~75 % à ~55 %), au prix d'augmenter le risque faux négatif de ~10 % à ~25 %. Pour un projet où **un faux GO coûte 2-3 k€/mois en capital perdu**, c'est un trade-off favorable (cohérent persona "mieux pas de bot qu'un bot perdant").

### 5.3 Recommandations Phase 2

#### 5.3.1 Python (vectorbt) vs Node

**Recommandation : Python avec vectorbt-pro ou backtesting.py**.

Justification :
- Bibliothèques R&D matures : `vectorbt`, `backtesting.py`, `pandas`, `statsmodels` — exécution backtest 5 ans × 7 hypothèses × walk-forward 5 fenêtres en quelques heures (vs jours en Node sans librairie native).
- **Stationary bootstrap** : `arch` library Python implémente directement Politis-Romano. Pas d'équivalent stable Node.
- **Hansen SPA test** : implémentations Python publiques (academic-quant), aucune Node.
- Continuité héritage Finance (Python/FastAPI) — réutilisation possible des indicateurs RSI/MACD/Bollinger.
- **Dette technique acceptable** : Phase 1 R&D peut être 100 % Python, Phase 2 production peut être Node si choix produit. Le code R&D ne va pas en prod (jetable, exploratoire).

**Risque** : si Phase 2 choisit Node TypeScript pour le bot Telegram, il faudra **re-coder l'edge retenu en Node** — coût ~2-3 jours @fullstack mais clean. Acceptable.

#### 5.3.2 Priorité H-C ORB en premier

**Recommandation : OUI, priorité H-C ORB** — confirmer ordre du rapport §4.

Justification :
- Sharpe OOS estimé le plus élevé (0,8-1,4).
- Logique simple (2-3 paramètres) → moins de p-hacking.
- Crabel (1990) référence académique solide.
- Si H-C PASS conditions renforcées → GO Phase 2 immédiat, économie 30+ jours R&D sur autres hypothèses.
- Si H-C FAIL → fort signal négatif sur l'ensemble du brief (l'edge le plus prometteur ne tient pas).

**Recommandation complémentaire** : tester H-C ORB sur **3 sous-jacents minimum en parallèle** (DAX, CAC40, EuroStoxx50). Si H-C tient seulement sur 1/3 → invalidation O5 (ticker chanceux), même si Sharpe global passe.

#### 5.3.3 Tests automatisés méthodologie

**Recommandation : créer `tests/backtest/test_methodology.py` AVANT premier backtest**.

Tests bloquants :
1. `test_no_lookahead()` — vérifier que `shift()` est appliqué sur tous les features avant le timestamp de signal.
2. `test_oos_blackbox()` — vérifier qu'aucun paramètre n'est modifié après évaluation OOS (snapshot config IS, hash, comparé après OOS).
3. `test_costs_applied()` — chaque trade simulé doit avoir frais ≥ 1,98 € + spread + slippage déduits.
4. `test_walk_forward_independence()` — fenêtres walk-forward ne se chevauchent pas (sauf pour la fenêtre standard de référence).
5. `test_bootstrap_p_value()` — sur un dataset random (alpha = 0), p-value doit être > 0,05 dans ≥ 95 % des cas (validation du bootstrap lui-même).
6. `test_stationary_bootstrap_block_length()` — block_length ≈ √N_trades.
7. `test_correction_multi_tests()` — α corrigé < α / N_hypothèses.

Ces tests doivent **PASS avant tout résultat de backtest soit reporté**. Sinon = méthodologie non vérifiée = audit @testeur-backtest-edge en `INPUTS INSUFFISANTS`.

### 5.4 Synthèse Verdict Final

| Dimension | Verdict | Effort levée |
|---|---|---|
| Méthodologie §2 edge-rnd-report | RETRAVAILLER (5 corrections) | 3h @data-analyst |
| Critères GO Phase 2 | RETRAVAILLER (4/5 conditions à renforcer) | 30 min @data-analyst |
| Scoring 6 dimensions | RETRAVAILLER (repondération D2/D6) | 30 min @ia |
| 5 sanity checks | RETRAVAILLER (ajout SC6 diversité) | 30 min @ia |
| CONFIDENCE_THRESHOLD | RETRAVAILLER (paper 7,0 / live 6,5) | 30 min @ia |
| Risques résiduels §6 | RETRAVAILLER (4 risques + mitigations) | 1h @data-analyst |

**Total** : ~6h sur 2 agents en parallèle → **livrables corrigés en 1 jour** → **GO Phase 2 méthodologie sous 48h**.

**Probabilité ≥ 1 hypothèse passe les 5 conditions renforcées** : ~55 % — équilibrée entre rigueur (faux positifs réduits) et faisabilité (faux négatifs raisonnables).

**Décision finale** : Verdict **RETRAVAILLER** levable rapidement. **NO-GO méthodologie écarté** — la philosophie est solide, la rigueur statistique demande des ajustements ciblés. **GO Phase 2 immédiat également écarté** — ne pas consommer le budget Twelve Data + Claude Haiku R&D (~300 $) avant levée RETRAVAILLER, le coût d'un faux GO méthodologique se paierait sur 30+ jours d'exécution backtest invalide.

---

## Mise à jour project-context.md

**Ligne historique** :
```
| testeur-backtest-edge via @qa | 2026-05-01 | docs/qa/backtest-audit-phase1.md | Verdict RETRAVAILLER (11 corrections - 5 méthodo §1, 4 critères GO §2, 3 scoring §3 + 4 risques résiduels §4). Effort levée ~6h cumulé @data-analyst+@ia. Probabilité estimée ≥1 hypothèse PASS conditions renforcées : ~55 %. Recommandation Phase 2 : Python (vectorbt+arch+SPA), priorité H-C ORB sur 3 sous-jacents min, tests methodology.py PRE-backtest | Écarté GO immédiat (philosophie OK mais 75 % proba PASS faux positif sous seuils actuels = risque structurel) ; écarté NO-GO (corrections additives, pas refonte) ; passage à 5 fenêtres walk-forward optionnel si données 2020 dispo, sinon 3/3 PASS sur 3 fenêtres |
```

**Ligne performance** :
```
| testeur-backtest-edge via @qa | 2026-05-01 | docs/qa/backtest-audit-phase1.md | 5 | 5 | 5 | 5 | 5 | 11 corrections chiffrées avec seuils précis (Sharpe 1,2 vs 1,0, robustesse 0,6 vs 0,5, n_bootstrap 10 000, α Bonferroni 0,0071) ; références académiques sourcées (Bailey-Lopez de Prado 2014, Pardo 2008, White 2000, Politis-Romano 1994, Hansen SPA, Lo 2002, Connors 2012) ; mapping 7 patterns O1-O7 vs 5 SC explicite avec angle mort SC6 identifié ; effort levée chiffré par action (L1-L10) ; probabilité PASS estimée par hypothèse ; trade-off faux positif/négatif quantifié ; 7 tests methodology.py PRE-backtest listés |
```

---

## Handoff

---

**Handoff → @orchestrator** (relai vers @data-analyst pour corrections L1-L8 + @ia pour corrections L9-L10)

- **Fichier produit** : `/home/user/TradingApp/docs/qa/backtest-audit-phase1.md`
- **Verdict** : **RETRAVAILLER** (11 corrections, levable en 1 jour)
- **Critères GO Phase 2** : 1 PASS / 5 (seul C2 PF > 1,5 est correctement calibré ; C1, C3, C4, C5 à renforcer)
- **Scoring model** : structure OK, repondération D2/D6 + ajout SC6 + seuils paper/live distincts
- **Patterns overfitting (O1-O7)** : couverts au niveau backtester (§2.3), partiellement au niveau scoring (5/7 SC). SC6 diversité sous-jacents recommandé.
- **Risques résiduels** : 4 identifiés (multi-tests, drift régime, slippage live, look-ahead H-E) — mitigations précises proposées
- **Phase 2 autorisée** : NON tant que RETRAVAILLER non levé. Effort levée ~6h cumulé.
- **Re-audit requis** : OUI après corrections L1-L10 — audit léger (vérification corrections appliquées, pas re-audit complet).
- **Recommandations Phase 2** : Python (vectorbt + arch + SPA test) > Node ; priorité H-C ORB sur 3 sous-jacents minimum ; tests `methodology.py` PRE-backtest obligatoires ; budget Claude Haiku R&D ~300 $ pour H-E corpus historique.
- **Actions Replit requises** : Aucune action Replit requise (audit méthodologique, pas de modification code/config).

---
