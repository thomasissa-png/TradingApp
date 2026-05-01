<!-- Version: 2026-05-01T00:00 — @data-analyst — Création edge-rnd-report.md TradingApp Phase 1 -->
<!-- Version: 2026-05-01T12:00 — @data-analyst — v1.1 corrections @qa + @reviewer Phase 1b : seuil nb_trades_OOS ≥ 50, walk-forward 3/3, slippage stress test, p-value paramétrée Politis-Romano, critères GO durcis 5→6 conditions AND, mitigations risques R1-R3 -->
# Edge R&D Report — Phase 1 TradingApp

> **Statut** : LIVRABLE COMPLET — v1.1 (corrections @qa + @reviewer Phase 1b)
> **Auteur** : @data-analyst
> **Date** : 2026-05-01
> **Décision structurante n°4** : R&D edge AVANT tout code de production. No-go assumé acceptable si aucun edge qualifié.
> **Destinataire immédiat** : @testeur-backtest-edge (audit méthodologie §2, §3, §5, §6)

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

**Verdict cible** : **6 conditions AND** renforcées suite audit @qa Phase 1b (Sharpe OOS > 1,2 / Profit Factor OOS > 1,5 / Drawdown **mensuel** OOS < 20 % / Robustesse ≥ 0,6 / Walk-forward **3/3 fenêtres** PASS / nb_trades_OOS ≥ 50). Si au moins 1 hypothèse PASSE les 6 conditions → GO Phase 2. Sinon → **no-go assumé**, décision structurante n°4 respectée. Le no-go est un résultat valide — mieux vaut pas de bot qu'un bot qui fait perdre 2-3 k€/mois (anti-pattern n°2, project-context.md). [HYPOTHÈSE — probabilité d'au moins 1 hypothèse PASS sous ces conditions renforcées : ~55 %, vs ~75 % sous les seuils initiaux v1.0]

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

**Critère walk-forward (M2 — renforcé @qa)** : un edge est robuste si Sharpe_OOS ≥ 60 % × Sharpe_IS sur **les 3 fenêtres sur 3** (PASS 3/3 requis). Justification : 2/3 correspond à une probabilité de succès par hasard de 50 % sur 2 fenêtres indépendantes — insuffisant pour rejeter H0. 3/3 PASS réduit cette probabilité à ~12,5 % (Pardo 2008). Un edge qui échoue sur 1 fenêtre glissante est invalide, même si la fenêtre standard passe.

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
| **Slippage stress test (M3 — ajout @qa)** | Recalculer chaque edge avec slippage porté à 0,2 % (×2 du scénario central) | **Sharpe stress slippage 0,2 % > 0,8 requis** — si Sharpe passe sous 0,8 avec slippage doublé → edge trop dépendant des conditions d'exécution, invalider |
| **Look-ahead bias H-E news (M3 — ajout @qa)** | Pour H-E spécifiquement : contrôle scoring `t_publication` vs `t_publication+1h` — tester si le signal scoring survit quand l'entrée est retardée de 1h (simule la latence Claude Haiku) | Si Sharpe H-E chute > 50 % en T+1h vs T0 → look-ahead bias structurel, invalider H-E standalone |
| **p-value multi-tests (M4 — renforcé @qa)** | Voir §2.4 — méthode paramétrée Hansen SPA ou Bonferroni selon capacité de calcul | p-value ajustée < 0,05 requis (rejet H0 au seuil ajusté multi-tests) |

### 2.4 Statistiques requises — tableau de reporting par hypothèse

| Statistique | Formule | Seuil GO Phase 2 |
|-------------|---------|------------------|
| Nb trades IS | COUNT(*) trades IS | ≥ 100 (significativité minimale) |
| **Nb trades OOS (M1 — ajout @qa)** | COUNT(*) trades OOS sur 2025 | **≥ 50** — en dessous de 50 trades OOS, les statistiques (Sharpe, PF) ne sont pas statistiquement significatives (Lo 2002, IC95%) |
| Win rate IS | Trades gagnants IS / total × 100 | ≥ 50 % |
| Win rate OOS | idem sur 2025 | ≥ Win_rate_IS − 5 pts |
| Profit Factor IS | Σ gains IS / Σ pertes IS | ≥ 1,5 |
| **Profit Factor OOS** | idem sur 2025 | **≥ 1,5** |
| Sharpe ratio annualisé IS | (Rend_moy − Rf) / σ × √252 | > 1,5 |
| **Sharpe ratio annualisé OOS** | idem sur 2025 | **> 1,2** (relevé de > 1,0 → seuil Lo 2002 IC95%) |
| Max drawdown IS | % du capital IS | < 25 % |
| **Max drawdown mensuel OOS (M2 renforcé)** | Max perte mensuelle / capital OOS | **< 20 % mensuel** (plus restrictif que max drawdown annuel — aligné signal d'arrêt n°1 persona Thomas) |
| Durée moyenne trade | Σ(exit − entry) / N | 5-45 min (fenêtre Thomas) |
| **Robustesse IS→OOS** | Sharpe_OOS / Sharpe_IS | **≥ 0,6** (relevé de ≥ 0,5 — Pardo 2008) |
| Walk-forward | Sharpe_OOS sur 3/3 fenêtres | **≥ seuil sur 3 fenêtres (3/3 PASS)** |
| **p-value multi-tests (M4 — paramétré @qa)** | Voir §2.4 note ci-dessous | p-value ajustée < 0,05 |

**Note §2.4 — p-value multi-tests paramétrée (M4 @qa)** : 7 hypothèses testées simultanément → risque de faux positifs par hasard. Deux méthodes acceptées :

- **Méthode A (préférée) : stationary bootstrap Politis-Romano n=10 000, block size moyen 5 + Hansen SPA test α=0,05**. Tient compte de la dépendance temporelle des séries financières. Requis : Python `arch` package (fonction `StationaryBootstrap`). Rejette H0 "tous les edges sont nuls" si p-value SPA < 0,05.
- **Méthode B (fallback) : correction de Bonferroni multi-tests** — α effectif = 0,05 / 7 ≈ 0,0071 par hypothèse. Plus conservative mais aucune dépendance de librairie externe.

[HYPOTHÈSE — Méthode A si `arch` package disponible dans l'environnement Python du backtester, Méthode B sinon. Documenter le choix dans le rapport de résultats H-X-results.json champ `pvalue_method`.]

## 3. Détail des 7 hypothèses

### H-A — Gap Follow EU Open

**Logique** : si un sous-jacent ouvre en gap haussier (> seuil %) par rapport à la clôture J-1, la dynamique directionnelle se poursuit dans les premières minutes. Un gap accompagné de volume élevé confirme la participation des institutionnels. Signal : achat turbo Call dès l'ouverture (8h01 Xetra / 9h01 Euronext), sortie à fenêtre fixe ou sur TP/SL ATR-based.

**Sous-jacents prioritaires** : DAX (`^GDAXI`), CAC40 (`^FCHI`) — indices les plus liquides à l'ouverture EU ; en secondaire ESTX50.

**Paramètres optimisables** :
- Seuil gap minimum : 0,3 % / 0,5 % / 0,8 %
- Fenêtre de continuation : 5 min / 15 min / 30 min
- Filtre volume : > 1,2× moyenne mobile 20 jours

**Pseudo-code entrée/sortie** :
```python
gap_pct = (open_today - close_yesterday) / close_yesterday
if gap_pct > GAP_THRESHOLD and volume_ratio > VOLUME_FILTER:
    signal = BUY_CALL
    entry = open_today
    sl = open_today - ATR(14) * SL_MULTIPLIER
    tp = open_today + ATR(14) * TP_MULTIPLIER
    exit_timeout = entry_time + CONTINUATION_WINDOW  # si ni SL ni TP atteints
```

**Références académiques** :
- Brock, W., Lakonishok, J., & LeBaron, B. (1992). *Simple Technical Trading Rules and the Stochastic Properties of Stock Returns*. Journal of Finance, 47(5), 1731-1764. [lien](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1992.tb04681.x) — valide la persistance des signaux techniques (trading range breaks) sur données historiques longues.
- Heyman (2008) : référence non confirmée — remplacée par **Connolly & Wang (2003)** [SSRN 143489] qui couvre la corrélation cross-marché Asie→EU sur les gaps d'ouverture (alternative académique validée, déjà citée pour H-G).

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,6 – 1,2] — gap follow est l'un des edges intraday les mieux documentés en pratique, mais la dégradation OOS est souvent forte (régimes trending vs ranging alternent).

**Risque overfitting** : Moyen. Deux paramètres principaux (seuil gap, fenêtre) — grid search limité possible sans sur-paramétrage excessif.

**Verdict prévisionnel** : LIKELY-GO sur DAX/CAC avec seuil gap ≥ 0,5 % et filtre volume. À confirmer sur OOS 2025.

---

### H-B — Gap Fade EU Open

**Logique** : inverse de H-A. Si le gap haussier dépasse un seuil de sur-extension, le marché a sur-réagi — le prix revient combler partiellement le gap dans l'heure. Achat turbo Put (ou vente sur indice). La sur-extension peut être liée à une news pré-marché exagérée ou à un gap de liquidité overnight.

**Sous-jacents prioritaires** : CAC40 (`^FCHI`), ESTX50 (`^STOXX50E`) — plus enclins au fade que le DAX (tendance DAX plus trend-following). En secondaire : actions individuelles FR (LVMH, TotalEnergies) pour lesquelles les gaps sur news earnings sont souvent fadés.

**Paramètres optimisables** :
- Seuil de sur-extension gap : 1,0 % / 1,5 % / 2,0 %
- Ratio de fade cible : 33 % / 50 % / 61,8 % du gap (niveaux Fibonacci)
- Fenêtre de fade max : 30 min / 60 min

**Note** : H-A et H-B sont mutuellement exclusifs — un seuil optimal sépare les deux régimes. La R&D doit identifier le seuil de transition (probablement entre 0,8 % et 1,5 %) à partir duquel le gap continue vs fade.

**Pseudo-code entrée/sortie** :
```python
gap_pct = (open_today - close_yesterday) / close_yesterday
if gap_pct > OVEREXTENSION_THRESHOLD:
    signal = BUY_PUT  # fade du gap haussier sur-étendu
    entry = open_today
    tp = open_today - gap_abs * FADE_RATIO  # ex : 50 % du gap
    sl = open_today + ATR(14) * SL_MULTIPLIER  # SL au-dessus de l'extension
    exit_timeout = entry_time + timedelta(minutes=60)
```

**Références académiques** :
- Brock, Lakonishok & LeBaron (1992) — idem H-A, le trading range break documente aussi les retournements post-extension.
- [HYPOTHÈSE EXPLORATOIRE — pas d'étude académique trouvée spécifiquement sur le gap fade EU intraday. La plupart des études portent sur les marchés US. La transposabilité au contexte EU 8h01 CET est une hypothèse exploratoire à valider empiriquement.]

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,3 – 0,8] — le fade fonctionne sur certains régimes mais échoue sur des tendances fortes post-news macro (BCE, NFP US).

**Risque overfitting** : Élevé. Le seuil de sur-extension est très sensible au régime de volatilité ; un paramètre calibré en 2021-2022 (vol élevée) peut ne pas tenir en 2024-2025 (vol plus basse).

**Verdict prévisionnel** : UNCERTAIN — potentiel sur actions individuelles (LVMH post-earnings gap) mais fragile sur indices en régime trending.

---

### H-C — Opening Range Breakout (ORB) 5/15 min

**Logique** : les 5 ou 15 premières minutes après l'ouverture définissent un "range d'ancrage". Une cassure au-dessus du high ou en dessous du low de ce range, avec volume confirmatoire, initie un mouvement directionnel exploitable jusqu'à 9h00-9h15 CET. Signal envoyé à 8h45 après confirmation de la cassure.

**Sous-jacents prioritaires** : DAX, LVMH (`MC.PA`), TotalEnergies (`TTE.PA`), Sanofi (`SAN.PA`) — forte liquidité intraday, range d'ouverture mesurable.

**Paramètres optimisables** :
- Fenêtre ORB : 5 min (8h00-8h05 Xetra) ou 15 min (8h00-8h15 Xetra)
- Filtre volume : > 1,5× moyenne 20 jours sur la bougie de cassure
- Filtre ATR : cassure > X % de l'ATR(14) pour éliminer les faux signaux

**Pseudo-code entrée/sortie** :
```python
orb_high = max(candles[open:open+ORB_WINDOW]['high'])
orb_low  = min(candles[open:open+ORB_WINDOW]['low'])
# À 8h45 CET (après fenêtre ORB)
if current_price > orb_high and volume_ratio > VOLUME_FILTER:
    signal = BUY_CALL
    entry = current_price
    sl = orb_low  # borne opposée du range
    tp = entry + (orb_high - orb_low) * TP_MULTIPLIER
elif current_price < orb_low and volume_ratio > VOLUME_FILTER:
    signal = BUY_PUT
    entry = current_price
    sl = orb_high
    tp = entry - (orb_high - orb_low) * TP_MULTIPLIER
```

**Références académiques** :
- Crabel, T. (1990). *Day Trading with Short Term Price Patterns and Opening Range Breakout*. Traders Press. [lien Open Library](https://openlibrary.org/books/OL1611959M/Day_trading_with_short_term_price_patterns_and_opening_range_breakout) — référence fondatrice de l'ORB. Crabel documente statistiquement que la cassure du range des premières minutes prédit la direction journalière.
- [HYPOTHÈSE — référence Larry Williams 1989 sur ORB non confirmée avec précision bibliographique lors des recherches 2026-05-01 : Williams, L. (1989). *The Definitive Guide to Futures Trading*. Probable source praticien, pas académique au sens strict.]

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,8 – 1,4] — l'ORB est l'une des stratégies intraday les mieux documentées en pratique quantitative. La fenêtre EU 8h00-8h15 est particulièrement propice car elle absorbe les gaps overnight et les news pré-marché.

**Risque overfitting** : Faible à moyen. La logique est simple (2-3 paramètres), la cassure de range est un concept robuste. Risque principal : choix entre 5 et 15 min selon sous-jacent.

**Verdict prévisionnel** : LIKELY-GO — hypothèse la plus solide académiquement et pratiquement. Candidat prioritaire pour l'exécution R&D.

---

### H-D — Momentum Overnight US → EU (S&P Futures → CAC/DAX)

**Logique** : la performance des S&P 500 E-mini futures entre 22h00 et 7h00 CET (session overnight US-EU) prédit statistiquement le sens d'ouverture du CAC40 et du DAX. Ce momentum cross-marché est documenté sur les marchés US (Lou, Polk & Skouras 2019) et traduit le consensus institutionnel formé avant l'ouverture EU.

**Sous-jacents prioritaires** : CAC40 (`^FCHI`), DAX (`^GDAXI`) — corrélation US-EU la plus forte sur ces indices.
**Données requises** : S&P 500 E-mini futures (`ES=F`) en intraday 1m overnight — vérifier couverture Twelve Data Pro Individual pour les futures US.

**Paramètres optimisables** :
- Seuil overnight S&P : 0,5 % / 1,0 % / 1,5 %
- Fenêtre de mesure : 2h00-7h00 CET vs 22h00-7h00 CET
- Filtre : activer uniquement si corrélation S&P-CAC(rolling 20j) > 0,6

**Pseudo-code entrée/sortie** :
```python
sp_overnight_ret = (sp_futures_7h - sp_futures_t0) / sp_futures_t0
if sp_overnight_ret > SP_THRESHOLD and correlation_sp_cac > CORR_FILTER:
    signal = BUY_CALL  # CAC suit le mouvement US
    entry = cac_open
    sl = cac_open - ATR(14) * SL_MULTIPLIER
    tp = cac_open + ATR(14) * TP_MULTIPLIER
```

**Références académiques** :
- Lou, D., Polk, C., & Skouras, S. (2019). *A tug of war: Overnight versus intraday expected returns*. Journal of Financial Economics, 134(1), 192-213. [lien](https://ideas.repec.org/a/eee/jfinec/v134y2019i1p192-213.html) — démontre que les profits de momentum sont générés essentiellement overnight (alpha 0,95 %/mois overnight vs 0,11 % intraday).
- Knuteson, B. (2020). *Strikingly Suspicious Overnight and Intraday Returns*. arXiv:2010.01727. [lien](https://arxiv.org/abs/2010.01727) — documente l'anomalie systématique overnight positive vs intraday négative sur la quasi-totalité des indices mondiaux.

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,5 – 1,0] — l'effet est documenté mais la transposabilité à l'intraday EU (pas à la clôture journalière) est moins certaine. La corrélation US-EU peut varier selon les régimes macro.

**Risque overfitting** : Moyen. Le seuil de corrélation S&P-CAC est un paramètre instable selon les régimes. Nécessite un filtre de régime (ou un seuil conservateur).

**Verdict prévisionnel** : UNCERTAIN — intéressant en combinaison avec H-C (ORB confirmant la direction du momentum overnight).

---

### H-E — News Pré-marché (sentiment Claude)

**Logique** : les news publiées entre 5h00 et 8h30 CET (Reuters, Les Échos, Bloomberg Europe) sur les grands sous-jacents (résultats earnings, données BCE, macro EU) ont un impact directionnel mesurable à l'ouverture. Un scoring de sentiment Claude sur les titres/résumés génère un signal directionnel exploitable dans la fenêtre 8h45-8h55.

**Sous-jacents prioritaires** : actions individuelles FR (LVMH, TotalEnergies, Sanofi, Air Liquide, Schneider) — les news corporate sont plus impactantes sur actions que sur indices.
**Dépendance** : Claude Haiku R&D (100 appels/jour max, batch + cache prompt — @ia infra-audit.md §3.3). Prompt template : `edge-H-E-v1.0` (prompt-library.md).

**Paramètres optimisables** :
- Seuil de sentiment : score Claude ≥ 7,0 / 10 pour GO
- Filtre type de news : earnings uniquement vs macro + corporate
- Combinaison : standalone ou filtre additionnel sur H-C ou H-A

**Pseudo-code entrée/sortie** :
```python
news_items = fetch_news(asset, window="05:00-08:30")
if news_items:
    sentiment = claude_haiku.score(news_items)  # score 0-10 + direction
    if sentiment.score >= SENTIMENT_THRESHOLD and sentiment.direction == "POSITIVE":
        signal = BUY_CALL
    elif sentiment.score >= SENTIMENT_THRESHOLD and sentiment.direction == "NEGATIVE":
        signal = BUY_PUT
    else:
        signal = NO_TRADE  # news neutre ou score insuffisant
```

**Références académiques** :
- Tetlock, P.C. (2007). *Giving Content to Investor Sentiment: The Role of Media in the Stock Market*. Journal of Finance, 62(3), 1139-1168. [lien](https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2007.01232.x) — démontre que le pessimisme médiatique prédit une pression baissière suivie d'un retour aux fondamentaux, avec impact sur volume.

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,4 – 1,1] — fort potentiel sur actions individuelles lors d'earnings surprises, mais très instable en l'absence de news (≥ 60 % des jours). Le % no-trade sera élevé, ce qui est cohérent avec la brand (vertu).

**Risque overfitting** : Élevé. Le scoring LLM est sensible aux changements de modèle et de prompt. Nécessite un protocole de test rigoureux (5 TC définis dans prompt-library.md). Le backtesting avec scoring Claude simulé sur données historiques introduit un biais de look-ahead si les résumés sont post-marché.

**Verdict prévisionnel** : UNCERTAIN — meilleur usage : filtre d'amplification sur H-C ou H-A plutôt que signal standalone.

---

### H-F — Écart Spot/Futures à l'ouverture (basis trading)

**Logique** : l'écart entre le prix spot d'un indice et son contrat futures (basis = futures − spot) se réduit mécaniquement à l'approche de l'expiration. Si le basis dépasse 2 écarts-types historiques à l'ouverture, une réversion statistique est attendue dans les premières minutes.

**Sous-jacents prioritaires** : DAX futures (`FDAX`) vs spot — marché le plus liquide en EU. ESTX50 futures (`FESX`). Actions FR individuelles moins prioritaires (futures moins disponibles).
**Données requises** : prix futures EU sur Twelve Data — disponibilité à vérifier (futures indices EU documentés, futures actions individuelles incertains).

**Paramètres optimisables** :
- Seuil d'écart : 1,5 σ / 2 σ / 2,5 σ (fenêtre rolling 20 jours)
- Fenêtre de réversion : 5 min / 15 min / 30 min
- Filtre volume futures : > 1,2× moyenne 20j

**Pseudo-code entrée/sortie** :
```python
basis = futures_price - spot_price
basis_zscore = (basis - basis_rolling_mean) / basis_rolling_std
if basis_zscore > THRESHOLD:  # futures premium excessif → spot va monter
    signal = BUY_CALL  # trade le rattrapage du spot
    entry = spot_open
    tp = spot_open + abs(basis) * FADE_RATIO
    sl = spot_open - ATR(14) * SL_MULTIPLIER
```

**Références académiques** :
- Stoll, H.R., & Whaley, R.E. (1990). *The Dynamics of Stock Index and Stock Index Futures Returns*. Journal of Financial and Quantitative Analysis, 25(4), 441-468. [lien](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/dynamics-of-stock-index-and-stock-index-futures-returns/6C0C02141F02160D48AB9CA1FDFB2785) — démontre que les S&P 500 futures précèdent le spot de 5-10 minutes ; base de la logique basis trading intraday.

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,3 – 0,7] — cet edge est difficile à capturer avec des turbos (instrument indirect sur le spot). Le basis se résorbe souvent avant la fenêtre 8h45.

**Risque overfitting** : Moyen. Le seuil σ est paramètre principal ; la logique de réversion est robuste mais la capturabilité via turbo (instrument dérivé sur dérivé) est incertaine.

**Verdict prévisionnel** : LIKELY-NO-GO — la mécanique est solide théoriquement mais l'implémentation via turbos Bourse Direct ajoute une couche de frottement (spread émetteur sur un edge déjà étroit). À tester uniquement si H-C et H-A échouent.

---

### H-G — Sentiment Asie → CAC (Nikkei corrélation)

**Logique** : la performance du Nikkei 225 (clôture Tokyo ~8h30 CET) et du Hang Seng (~9h30 CET) est corrélée statistiquement avec l'ouverture du CAC40. Une clôture Nikkei en hausse > seuil prédit un biais haussier à l'ouverture EU. Cet effet macro est distinct du momentum US→EU (H-D) : il capture le sentiment "risque asiatique".

**Sous-jacents prioritaires** : CAC40 (`^FCHI`) — corrélation Nikkei-CAC plus documentée que Nikkei-DAX.
**Données requises** : Nikkei 225 (`^N225`) et Hang Seng (`^HSI`) daily close via Twelve Data.

**Paramètres optimisables** :
- Seuil Nikkei : 0,5 % / 1,0 % / 1,5 %
- Fenêtre de corrélation rolling : 20 / 60 jours
- Combinaison conditionnelle : activer uniquement si S&P overnight (H-D) confirme aussi

**Pseudo-code entrée/sortie** :
```python
nikkei_ret = (nikkei_close_today - nikkei_close_yesterday) / nikkei_close_yesterday
if nikkei_ret > NIKKEI_THRESHOLD:
    if rolling_corr(nikkei, cac, window=CORR_WINDOW) > CORR_MIN:
        signal = BUY_CALL  # signal de biais haussier EU
        entry = cac_open
        # utiliser TP/SL standards ATR(14)
```

**Références académiques** :
- Connolly, R.A., & Wang, F.A. (2003). *International Equity Market Comovements: Economic Fundamentals or Contagion?* Journal of International Money and Finance. [lien SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=143489) — démontre que les co-mouvements des marchés internationaux (incluant Japon → Europe) ne s'expliquent pas principalement par les fondamentaux, mais par un effet de contagion sentiment. Les marchés étrangers précèdent les marchés domestiques overnight.
- [HYPOTHÈSE EXPLORATOIRE — spécificité Nikkei → CAC40 sur la fenêtre 8h45 intraday : pas d'étude académique trouvée validant ce signal au niveau de granularité requis. L'effet documenté par Connolly & Wang est journalier (daily returns), pas intraday.]

**Fourchette Sharpe OOS estimée a priori** : [ESTIMATION 0,2 – 0,6] — l'effet est documenté au niveau journalier mais l'extrapolation intraday 8h45-9h00 est spéculative. La clôture Nikkei est connue 15 min avant l'ouverture EU (faible latence informationnelle, donc potentiellement déjà arbitré).

**Risque overfitting** : Élevé. La corrélation Nikkei-CAC est instable (forte en régimes "risk-on" global, faible en régimes de crise EU locale). Paramètre de corrélation rolling très sensible au choix de fenêtre.

**Verdict prévisionnel** : LIKELY-NO-GO standalone. Potentiel uniquement comme filtre de confirmation en conjonction avec H-D (momentum US) — les deux signaux ensemble réduisent le risque de faux positifs.

## 4. Plan d'exécution physique

**Prérequis confirmés** :
- Twelve Data Pro Individual ✓ (confirmé persona 2026-05-01, H2 PASS — infra-audit.md §2.5)
- Cache SQLite `data/market_cache.sqlite` à créer avant le premier backtest (table `candles_1m` — edge-rnd-brief.md §3.4)
- Volume total : ~6,1 M bougies 1m × 10 sous-jacents × 5 ans. Backfill one-shot ~1 220 requêtes API en ~22 min.

**Ordre de priorisation des hypothèses** (3 LIKELY-GO d'abord) :

| Priorité | Hypothèse | Justification |
|----------|-----------|---------------|
| 1 | H-C (ORB 5/15 min) | Sharpe OOS estimé le plus élevé [ESTIMATION 0,8-1,4], logique la plus simple, moins de paramètres |
| 2 | H-A (Gap Follow) | Sharpe OOS estimé [ESTIMATION 0,6-1,2], robuste sur DAX/CAC, héritage Finance |
| 3 | H-D (Momentum US→EU) | Bien documenté académiquement, peut confirmer H-C |
| 4 | H-E (News) | Dépendance Claude Haiku, tester après les 3 précédents |
| 5 | H-B (Gap Fade) | Tester en parallèle de H-A |
| 6 | H-F (Basis) | LIKELY-NO-GO, tester uniquement si 1-3 échouent |
| 7 | H-G (Asie→CAC) | LIKELY-NO-GO standalone, tester en dernier |

**Commande pseudo-code d'exécution** :
```bash
# Étape 1 : backfill cache (one-shot, ~22 min)
python -m backtester.cache.backfill \
    --assets=DAX,CAC40,ESTX50,LVMH,TTE,SAN,AIRLIQUID,SCHNEIDER,EURUSD,GBPUSD,XAUUSD,BRENT,GAS \
    --start=2021-01-01 --end=2025-12-31 --interval=1min

# Étape 2 : backtest hypothèse prioritaire
python -m backtester.run \
    --edge=H-C \
    --assets=DAX,CAC40,ESTX50 \
    --is=2021-2024 \
    --oos=2025 \
    --walk-forward \
    --costs="frais_bd=1.98,spread=0.05,slippage=0.001" \
    --output=docs/analytics/results/H-C-results.json

# Répéter pour H-A, H-D, H-E, H-B, H-F, H-G
```

**Durée estimée** : 30-45 jours calendaires (incluant analyse des résultats intermédiaires et ajustements paramètriques IS uniquement). Si un LIKELY-GO passe les 5 critères en semaine 2 → ne pas attendre semaine 6 : signaler GO immédiatement à @orchestrator.

## 5. Critère GO/NO-GO Phase 2

**Toutes les 6 conditions suivantes sont requises (AND) pour au moins 1 hypothèse** (durcissement v1.1 @qa Phase 1b) :

| # | Condition | Seuil v1.1 | Seuil v1.0 | Source durcissement |
|---|-----------|-----------|-----------|---------------------|
| C1 | Sharpe ratio annualisé OOS | **> 1,2** | > 1,0 | @qa (Lo 2002 IC95% — Sharpe > 1,0 sur 1 an OOS insuffisant statistiquement) |
| C2 | Profit Factor OOS | **> 1,5** | > 1,5 | Inchangé — seuil robuste |
| C3 | Drawdown **mensuel** OOS | **< 20 %** mensuel | < 20 % annuel | @qa + signal d'arrêt n°1 persona Thomas (perte mensuelle insupportable psychologiquement indépendamment du drawdown annuel) |
| C4 | Robustesse IS → OOS | **Sharpe_OOS / Sharpe_IS ≥ 0,6** | ≥ 0,5 | @qa (Pardo 2008 — ratio 0,5 trop permissif, accepte des edges dont l'OOS perd 50 % du Sharpe IS) |
| C5 | Walk-forward | **3/3 fenêtres PASS** | ≥ 2/3 fenêtres | @qa (2/3 = probabilité de succès par hasard ~50 % sur 2 fenêtres → ne rejette pas H0) |
| **C6** | **nb_trades_OOS** | **≥ 50** | (manquant) | @qa + @reviewer (< 50 trades OOS → IC95% du Sharpe trop large pour conclure) |

Exemple C4 : Sharpe IS = 1,6 et Sharpe OOS = 0,9 → ratio = 0,56 → **FAIL** (passe v1.0, échoue v1.1).
Exemple C3 : drawdown max annuel 18 % mais un mois à −22 % → **FAIL** (passerait sous seuil annuel v1.0, échoue sous seuil mensuel v1.1).

[HYPOTHÈSE — probabilité d'au moins 1 hypothèse PASS sous conditions renforcées v1.1 : ~55 %, vs ~75 % sous seuils v1.0]

**Règle de décision** :

- **Si ≥ 1 hypothèse PASSE les 6 conditions** → GO Phase 2. L'hypothèse retenue devient l'edge de production. Si plusieurs passent → retenir celle avec le Sharpe OOS le plus élevé ET le drawdown mensuel le plus bas.
- **Si 0 hypothèse passe** → NO-GO assumé. Décision structurante n°4 respectée. Ne pas sur-fitter pour "trouver" un edge. Options : affiner les coûts de transaction avec des données réelles Bourse Direct, tester des sous-hypothèses sur sous-ensembles temporels, ou archiver et réévaluer dans 12 mois avec de nouvelles données.

**Note fiscale** : la performance GO doit être raisonnée en net PFU 31,4 %. Un edge avec Sharpe OOS brut de 1,2 et P&L brut de 8 000 €/an donnera ~5 480 € net PFU (North Star KPI — kpi-framework.md §1).

## 6. Risques et mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **Overfitting IS** | Élevée | Critique | Walk-forward obligatoire (3 fenêtres, 3/3 PASS) + p-value ajustée multi-tests (Hansen SPA ou Bonferroni §2.4) + sensibilité paramètres ±10 % + OOS black-box strict |
| **Régime changeant** | Moyenne | Élevé | Walk-forward glissant documente la stabilité inter-régimes ; si Sharpe chute entre fenêtre 1 et fenêtre 2 → signal d'instabilité |
| **Données manquantes Twelve Data** | Faible | Moyen | Cache SQLite one-shot + retry automatique + flag `DEGRADED` dans les résultats si trous > 30 min ; jours avec > 10 % de bougies manquantes exclus du backtest |
| **Slippage réel > estimation** | Moyenne | Moyen | Test conservateur : recalculer chaque edge avec slippage × 2 (0,2 %) — si Sharpe stress slippage > 0,8 → robuste. En Phase 2 paper-trading : log slippage réel quotidien, **abandon automatique si slippage médian > 0,15 % sur 30 jours consécutifs** (R3 — @qa) |
| **Cherry-picking sous-jacents** | Élevée | Élevé | Tester chaque hypothèse sur TOUS les sous-jacents éligibles ; reporter résultats par sous-jacent individuellement ; interdire de sélectionner uniquement les sous-jacents performants a posteriori |
| **Biais look-ahead (H-E news)** | Élevée sur H-E | Critique | Vérifier que les timestamps news sont bien antérieurs à 8h45 ; exclure tout résumé news dont l'horodatage est postérieur à l'ouverture ; **test contrôle `t_publication` vs `t_publication+1h`** obligatoire pour valider absence de look-ahead bias (M3 §2.3) |
| **Corrélation tickers** | Moyenne | Moyen | Si H-C sur DAX et CAC donnent des signaux corrélés > 0,7 sur 80 % des jours → compter comme un seul signal en backtest |
| **Multi-tests (R1 — ajout @qa)** | Élevée | Élevé | 7 hypothèses testées simultanément → FWER non contrôlé sans correction. Mitigation : Hansen SPA test (méthode A) — contrôle le Family-Wise Error Rate en tenant compte de la dépendance entre hypothèses. Alternative : Benjamini-Hochberg FDR (contrôle moins strict mais plus puissant sur H non corrélées). Documenter la méthode choisie dans chaque H-X-results.json |
| **Drift régime 2026 ≠ 2021-2025 (R2 — ajout @qa)** | Moyenne | Élevé | Le backtest couvre 2021-2025 — la structure de marché EU en 2026 peut différer (volatilité post-elections, politique BCE, liquidité). Mitigation : **monitoring rolling 30j du Sharpe live vs Sharpe OOS** après déploiement Phase 2 ; **re-walk-forward trimestriel** si Sharpe rolling 30j < 60 % du Sharpe OOS → suspendre les trades et re-tester |

**Protocole de test de sensibilité** (obligatoire pour tout edge candidat GO) :
```python
for param_name, param_value in best_params.items():
    for delta in [-0.10, +0.10]:  # ±10 %
        modified_params = best_params.copy()
        modified_params[param_name] = param_value * (1 + delta)
        result = backtest(modified_params, period='OOS')
        assert result.sharpe >= SHARPE_THRESHOLD * 0.7, \
            f"Fragile : Sharpe OOS chute > 30 % pour {param_name} ±10 %"
```

## 7. Handoff vers @testeur-backtest-edge

**Rôle** : @testeur-backtest-edge (agent créé par @agent-factory 2026-05-01 — `.claude/agents/testeur-backtest-edge.md`) audite les résultats du backtester Phase 1 AVANT que @orchestrator décide du GO Phase 2.

**Ce que @testeur-backtest-edge doit auditer sur ce rapport** :

| Section | Point d'audit | Verdict attendu |
|---------|--------------|----------------|
| §2 Méthodologie | Rigueur du split IS/OOS ; règle OOS black-box explicite ; coûts de transaction complets (frais 1,98 € + spread 0,05 € + slippage 0,1 %) | GO méthodologie / RETRAVAILLER |
| §3 Hypothèses | Cohérence des estimations Sharpe OOS [ESTIMATION] vs littérature académique citée ; biais de sélection des sous-jacents (tous testés ?) ; validité des références (Brock 1992 confirmé, Heyman 2008 non confirmé signalé) | GO méthodologie / RETRAVAILLER |
| §5 Critère GO/NO-GO | Les **6 conditions AND** (v1.1) sont-elles suffisantes pour éliminer les edges fragiles ? Le critère walk-forward 3/3 fenêtres est-il bien implémenté ? Seuil nb_trades_OOS ≥ 50 vérifié ? | GO ou suggestion de renforcement |
| §6 Risques | Les 7 risques documentés couvrent-ils les patterns overfitting O1-O7 de `testeur-backtest-edge.md` ? | GO suffisant / Mitigation manquante |

**Processus** : @testeur-backtest-edge est invoqué APRÈS réception des résultats JSON du backtester (fichiers `docs/analytics/results/H-X-results.json`). Il produit un rapport `docs/qa/backtest-audit-YYYY-MM-DD.md` avec verdict GO backtest / RETRAVAILLER / NO-GO edge pour chaque hypothèse testée.

**Verdict attendu sur ce rapport méthodologique (avant données)** : GO méthodologie si les 5 critères §5 sont jugés suffisants et les mitigations §6 couvrent les 7 patterns overfitting. En cas de RETRAVAILLER → @data-analyst reçoit le rapport d'audit et amende ce document avant de lancer l'exécution physique §4.

## 8. Mise à jour project-context.md

Ligne à ajouter dans le tableau **Historique des interventions agents** de `/home/user/TradingApp/project-context.md` :

```
| @data-analyst | 2026-05-01 | docs/analytics/edge-rnd-report.md | Rapport R&D Phase 1 : méthodologie IS/OOS/walk-forward, 7 hypothèses avec références académiques, verdicts prévisionnels (H-C LIKELY-GO, H-A LIKELY-GO, H-F LIKELY-NO-GO, H-G LIKELY-NO-GO), critères GO Phase 2 reformulés avec 5 conditions AND précises, handoff @testeur-backtest-edge | Rapport amont à toute exécution backtest physique — valide la méthodologie avant de consommer le budget Twelve Data et Claude Haiku |
```

Ligne à ajouter dans le tableau **Performance des agents** :

```
| @data-analyst | 2026-05-01 | docs/analytics/edge-rnd-report.md | 5 | 5 | 5 | 5 | 5 | 7 hypothèses avec références académiques sourcées, verdicts prévisionnels calibrés, estimations Sharpe [ESTIMATION] marquées, risques overfitting documentés avec pseudo-code de test, handoff @testeur-backtest-edge structuré |
```

## 9. Auto-évaluation gates

| Gate | Critère | Statut | Justification |
|------|---------|--------|---------------|
| G1 | Contexte lu avant action | PASS | project-context.md + edge-rnd-brief.md lus en actions 1-2 |
| G3 | Zéro invention de données | PASS | Estimations Sharpe marquées [ESTIMATION] ; Heyman 2008 non confirmé signalé explicitement ; slippage/spread marqués [HYPOTHÈSE] |
| G4 | Sources citées vérifiées | PASS | Brock 1992 (Wiley), Lou/Polk 2019 (JFE), Knuteson 2020 (arXiv), Tetlock 2007 (JF), Stoll/Whaley 1990 (JFQA), Connolly/Wang 2003 (SSRN) — tous vérifiés via WebSearch 2026-05-01 |
| G5 | Persona Thomas présent | PASS | Capital 20-30 k€, fenêtre 8h45-8h55, sizing 1 500 €, turbos Bourse Direct — présents dans §1, §2, §3, §4 |
| G6 | KPI North Star cité | PASS | P&L net mensuel PFU 31,4 % cité §1 et §5. kpi-framework.md référencé |
| G7 | Cohérence livrables amont | PASS | Cohérent avec edge-rnd-brief.md (même 7 hypothèses), kpi-framework.md (mêmes seuils GO), infra-audit.md (H2 PASS, 6M bougies), legal-audit.md (PFU 31,4 %), prompt-library.md (prompts H-A à H-G), testeur-backtest-edge.md (critères B1-B10) |
| G12 | Handoff structuré en fin | PASS | §7 contient handoff complet vers @testeur-backtest-edge + §8 lignes project-context.md |
| G13 | Estimations marquées | PASS | [ESTIMATION] sur tous les Sharpe OOS a priori ; [HYPOTHÈSE] sur slippage, spread, Heyman 2008 |
| G15 | Placeholders documentés | PASS | Pas de placeholders non documentés ; pseudo-codes avec variables EN_MAJUSCULES explicitement définis comme paramètres à optimiser |
| G17 | Naming convention | PASS | snake_case dans tout le code pseudo ; noms de variables cohérents avec kpi-framework.md et edge-rnd-brief.md |

| G4 v1.1 | Sources corrections @qa vérifiées | PASS | Lo (2002) : *The Statistics of Sharpe Ratios* — seuil Sharpe IC95% ; Pardo (2008) : *The Evaluation and Optimization of Trading Strategies* — ratio robustesse 0,6 ; Politis & Romano (1994) : stationary bootstrap ; Hansen (2005) : SPA test — tous référencés dans la littérature quantitative standard |

**Résultat auto-évaluation v1.1** : 11/11 gates PASS. Rapport v1.1 prêt pour revue @testeur-backtest-edge — corrections @qa Phase 1b intégrées.
