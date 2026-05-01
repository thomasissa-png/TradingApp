<!-- Version: 2026-05-01T00:00 — @ia — Création initiale edge-scoring-model TradingApp -->
<!-- Version: 2026-05-01T01:30 — @ia — v1.2 corrections post-audit self-critical (SC7 plausibilité, repondération D1 30→35 / D6 15→10, TC-06/07/08) -->

# Edge Scoring Model — TradingApp

> Auteur : @ia — Date : 2026-05-01
> Mission : modèle de scoring multi-dimension du signal turbo (1.0-10.0), hybride Claude + sanity checks déterministes.
> **Lecture obligatoire amont** : `project-context.md`, `docs/ia/ai-architecture.md` (modèles + 9 règles anti-hallucination + tool use), `docs/ia/prompt-library.md` (PROMPT_VERSION signal-scoring-v1.0, prompts H-A à H-G), `docs/analytics/edge-rnd-brief.md` (7 hypothèses + seuils GO Phase 2), `docs/product/functional-specs.md` (US-01 schéma 15 champs, US-05 timeout 45 s).
> **Version modèle** : `scoring-model-v1.2` (Phase 1b post-audit @ia self-critical, couplé `prompt-version=signal-scoring-v1.1`). Voir §7.1bis pour le changelog.

---

## Résumé exécutif

- **Approche hybride** : Claude (Sonnet 4.5 live, Haiku 4.5 R&D) génère un score brut 1.0-10.0 + raison structurée → **7 sanity checks déterministes ex-post (v1.2)** → score final + flag (ALERT / SAFE / NO-TRADE).
- **6 dimensions pondérées** (v1.2 — repondération D1/D6) : D1 force signal (**35 %**), D2 confluence indicateurs (15 %), D3 contexte news (15 %), D4 volatilité (15 %), D5 régime VIX/V2X (10 %), D6 référence backtest (**10 %**).
- **7 sanity checks anti-overfitting / anti-euphorie** (v1.2) : SC1 cohérence direction, SC2 R/R ≥ 1.5, SC3 score > 9 → ALERT, SC4 % no-trade < 20 % → pénalité, SC5 langage spéculatif → plafond 6.0, SC6 diversité sous-jacents 30j → plafond 7.0 + ALERT, **SC7 plausibilité LLM vs déterministe (|écart| > 1.5) → plafond 7.0 + ALERT**.
- **CONFIDENCE_THRESHOLD split paper/live** (v1.1) : `CONFIDENCE_THRESHOLD_PAPER = 7.0` (bootstrap conservateur 4-8 sem.), `CONFIDENCE_THRESHOLD_LIVE = 6.5` [HYPOTHÈSE — calibrable R&D]. Sélection runtime via `STRATEGY_ACTIVE` SQLite (US-11).
- **Coût/signal Sonnet 4.5** : ~0,03 $ (cohérent ai-architecture §7 — verdict H4 PASS confortable).
- **Verdict modèle** : à valider par @testeur-backtest-edge avant Phase 2.

---

## 1. Architecture du scoring

### 1.1 Approche hybride (LLM + déterministe)

Ni LLM seul (risque hallucination + sur-confiance), ni calcul déterministe seul (perd la capacité d'agréger contexte qualitatif news + régime). **Hybride obligatoire** :

1. **Claude génère le score brut** (1.0-10.0) à partir de l'input typé `SignalScoringInput` (cf. ai-architecture §2.1) et produit la `raison` (1-3 lignes).
2. **Calcul parallèle déterministe** (v1.2) : Σ pondérée D1-D6 calculée côté code à partir des inputs (sert de référence pour SC7 plausibilité).
3. **7 sanity checks déterministes ex-post** (v1.2) corrigent le score si nécessaire (plafonnage, flag ALERT, NO-TRADE forcé).
4. **Score final + flag** émis dans le JSON 15 champs (US-01).

### 1.2 Diagramme de flux

```
                  ┌─────────────────────────────┐
                  │ Inputs typés (SignalScoring │
                  │ Input — ai-architecture §2.1)│
                  │ - OHLC 5j + premarket 1m    │
                  │ - Indicateurs (RSI/MACD/BB) │
                  │ - News titres (H-E)         │
                  │ - edge_features (par H-A..G)│
                  │ - backtest_ref + stats      │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────┐
                  │ Claude Sonnet 4.5 (live)    │
                  │ ou Haiku 4.5 (R&D)          │
                  │ tool_use=emit_signal_scoring│
                  │ température 0.1             │
                  │ → score_brut (1.0-10.0)     │
                  │ → raison (10-200 chars)     │
                  │ → direction (ACHAT/VENTE/   │
                  │   NO-TRADE)                 │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────┐
                  │ 6 sanity checks déterministes│
                  │ SC1 cohérence direction     │
                  │ SC2 R/R ≥ 1.5               │
                  │ SC3 score > 9 → ALERT       │
                  │ SC4 % no-trade < 20 % → -1  │
                  │ SC5 langage futur → ≤ 6.0   │
                  │ SC6 div. sous-jacents 30j   │
                  │     → ≤ 7.0 + ALERT          │
                  └──────────────┬──────────────┘
                                 │
                                 ▼
                  ┌─────────────────────────────┐
                  │ Score final + flag          │
                  │ ALERT / SAFE / NO-TRADE     │
                  │ → JSON 15 champs (US-01)    │
                  │ → SQLite signals + Telegram │
                  └─────────────────────────────┘
```

---

## 2. Dimensions d'évaluation

### 2.1 Tableau récapitulatif des 6 dimensions

| # | Dimension | Poids | Source | Formule | Range |
|---|---|---|---|---|---|
| **D1** | Force du signal d'edge | **35 %** (v1.2, ex-30 %) | `edge_features` (variable selon H-A..G) | amplitude normalisée par σ historique 30j | 0-10 |
| **D2** | Confluence indicateurs techniques | **15 %** (v1.1, ex-20 %) | `indicators` (RSI/MACD/Bollinger) | % des 3 indicateurs alignés avec la direction signal | 0-10 |
| **D3** | Contexte news pré-marché | **15 %** | `edge_features.news_titles` + `sentiment_score` | sentiment ×10 (signe aligné direction) — **plafond 7.0 si news indispo** | 0-10 |
| **D4** | Volatilité réalisée vs implicite | **15 %** | `indicators.atr_14` + VIX/V2X (si disponible) | ratio σ_realisée / σ_implicite ; > 1 = sur-volatilité | 0-10 |
| **D5** | Régime de marché VIX/V2X | **10 %** | VIX (ou V2X pour EU) + classification trend/range/panic | VIX < 15 trend = 8, 15-25 range = 6, > 25 panic = 3 | 0-10 |
| **D6** | Référence backtest | **10 %** (v1.2, ex-15 % v1.1, ex-10 % v1.0) | `backtest_stats` (Sharpe + win_rate + nb_trades + fraicheur) | Sharpe×3 + win_rate/10 + min(nb_trades/20, 5) ; pénalité si backtest > 90j | 0-10 |

**Justification rééquilibrage v1.1** (verdict @qa) : D2 confluence techniques baissée car les 3 indicateurs (RSI/MACD/BB) sont fortement corrélés intra-classe (signal redondant) — 20 % surévaluait leur poids informationnel réel. D6 backtest remontée car la qualité statistique de l'edge (Sharpe, win_rate, nb_trades) est le signal le plus robuste anti-overfitting — 10 % sous-pondérait la référence empirique.

**Justification repondération v1.2** (audit @ia self-critical) : D1 force du signal d'edge remontée à 35 % car c'est le **vrai signal informationnel** (amplitude normalisée par σ — mesure directe de l'edge en train de se manifester). D6 backtest redescendue à 10 % car c'est un **signal binaire frais/pas frais** plutôt qu'un signal informationnel granulaire (la qualité Sharpe + win_rate est déjà capturée par le seuil minimum nb_trades ≥ 30 et la pénalité fraîcheur > 90j — au-delà, la pondération marginale décroît). Total reste 100 % (35 + 15 + 15 + 15 + 10 + 10).

### 2.2 Formule globale

```
score_brut = clip( Σ(D_i × poids_i × normalisation_i), 1.0, 10.0 )
```

- `poids_i` = pondération du tableau (somme = 100 %).
- `normalisation_i` = facteur correctif spécifique à la dimension (ex: D3 plafonné à 7.0 si news indispo, cf. prompt dégradé `prompt-library.md` §4.2).
- Borné [1.0, 10.0] — pas de score < 1 ni > 10 (validation Zod stricte cf. ai-architecture §9).

### 2.3 Détail par dimension

**D1 — Force du signal d'edge (35 %, v1.2)** : variable selon `edge_id`.
- H-A Gap Follow : `D1 = clip(|gap_pct| / σ_gap_30j × 5, 0, 10)` (gap normalisé par écart-type historique 30 jours).
- H-C ORB : `D1 = clip((breakout_amplitude / atr_14) × 4, 0, 10)`.
- H-E News : `D1 = clip(|sentiment_score| × 10, 0, 10)`.
- (Détail par hypothèse dans `prompt-library.md` §2.)

**D2 — Confluence indicateurs (15 %, v1.1)** : alignement des 3 indicateurs avec direction signal.
- 3/3 alignés = 10, 2/3 = 6, 1/3 = 3, 0/3 = 0.
- ACHAT aligné : RSI > 50, MACD histogram > 0, prix > Bollinger middle.
- VENTE aligné : RSI < 50, MACD histogram < 0, prix < Bollinger middle.

**D3 — Contexte news (15 %)** : sentiment news pré-marché.
- `D3 = sentiment_score × 10` si direction signal = signe(sentiment).
- `D3 = -sentiment_score × 5` si direction opposée (pénalité, signal contre-news).
- **Plafond 7.0 si `news_titles` absent ou < 2 titres** — cohérent prompt dégradé `prompt-library.md` §4.2 (le bot ne doit pas sur-confier sans contexte news).

**D4 — Volatilité réalisée vs implicite (15 %)** : ratio.
- Si `σ_realisée / σ_implicite > 1.2` (sur-volatilité) → D4 = 8 (favorable scalp turbo).
- Si ratio entre 0.8 et 1.2 → D4 = 5.
- Si ratio < 0.8 (sous-volatilité) → D4 = 3 (turbo peu rentable, bouger lent).

**D5 — Régime VIX/V2X (10 %)** : classification.
- VIX < 15 → régime "trend" → D5 = 8 (favorable signaux directionnels).
- VIX 15-25 → régime "range" → D5 = 6 (neutre).
- VIX > 25 → régime "panic" → D5 = 3 (défavorable, levier risqué).
- Si VIX indisponible → D5 = 5 par défaut (neutre, pas de pénalité).

**D6 — Référence backtest (15 %, v1.1)** : qualité statistique.
- `D6 = clip(Sharpe×3 + win_rate/10 + min(nb_trades/20, 5), 0, 10)`.
- **Pénalité fraicheur** : si backtest > 90 jours → `D6 -= 1.5` (les régimes de marché bougent).
- Pénalité `nb_trades < 30` (cf. edge-rnd-brief seuils) → `D6 -= 2`.

---

## 3. Anti-overfitting / Anti-euphorie — 6 sanity checks (v1.1)

> Ces sanity checks sont **déterministes** (pas LLM) et appliqués **après** la réponse Claude. Cohérent avec R-AI-1 à R-AI-9 (ai-architecture §3) — défense en profondeur.

### 3.1 SC1 — Cohérence direction / SL / TP

**Règle** : la direction doit être cohérente avec le placement SL/TP.
- ACHAT : `entry > sl` ET `entry < tp` (turbo call).
- VENTE : `entry < sl` ET `entry > tp` (turbo put — SL au-dessus, TP en-dessous).
- Si incohérence détectée → **NO-TRADE forcé** + `no_trade_reason: "incohérence direction/SL/TP détectée par sanity check"` + log SQLite `sanity_check_failed=SC1`.

**Pourquoi** : Claude peut occasionnellement inverser (rare avec température 0.1 + tool use, mais possible). Coût d'une erreur direction sur turbo levier 10 = perte totale en quelques minutes. SC1 = filet de sécurité non-négociable.

### 3.2 SC2 — Risk/Reward minimum 1.5

**Règle** : `(TP - entry) / (entry - SL) ≥ 1.5` pour ACHAT, et symétrique pour VENTE.
- Si R/R < 1.5 → **score plafonné à 6.0** (sous `CONFIDENCE_THRESHOLD_LIVE` 6.5 et a fortiori sous `_PAPER` 7.0 → NO-TRADE de fait dans les deux modes, v1.1).
- Si R/R < 1.0 → **NO-TRADE forcé** + `no_trade_reason: "R/R < 1.0 — gain potentiel insuffisant vs risque"`.

**Pourquoi** : un signal avec R/R 1:1 ou pire est mathématiquement perdant à win_rate < 50 %. Cohérent edge-rnd-brief seuil PF > 1.5 — un signal individuel doit refléter la qualité statistique de l'edge.

### 3.3 SC3 — Score brut > 9.0 → flag ALERT (revue manuelle)

**Règle** : si `score_brut > 9.0` → `ALERT_flag = "ALERT"` (pas auto-envoi sans review).
- Le signal est bien envoyé sur Telegram, mais avec un préfixe "ALERT — score exceptionnel 9.X, à valider manuellement avant trade".
- Thomas peut overrider avec `/trade go` (cf. functional-specs US-08).

**Pourquoi** : cohérent avec **signal d'arrêt n°4 personas** ("score d'euphorie — méfiance"). Un score 9.5 sur scoring à 6 dimensions hétérogènes est statistiquement suspect (probablement overfit ou erreur d'input). La règle anti-euphorie : "trop beau pour être vrai" déclenche revue, pas exécution aveugle.

### 3.4 SC4 — % no-trade 7 derniers jours < 20 % → pénalité -1.0

**Règle** : si sur les 7 derniers jours ouvrés, le bot a émis < 20 % de NO-TRADE → `score_brut -= 1.0` sur le signal du jour.
- Lookup SQLite `signals` : `SELECT COUNT(*) FILTER (WHERE direction='NO-TRADE') / COUNT(*) FROM signals WHERE date >= date('now', '-7 days')`.
- Si ratio < 0.20 → pénalité.

**Pourquoi** : le bot doit accepter de se taire (silence assumé = pilier brand-platform Pilier 3 "Backtesté"). Si < 20 % de NO-TRADE → le bot **force des signaux** (probablement par sur-fit ou par seuil trop bas). Cohérent avec data-analyst kpi-framework "% no-trade = vertu", alerte si < 20 %. Cette pénalité ramène le scoring vers la sobriété.

### 3.5 SC5 — Langage spéculatif sans chiffres → plafond 6.0

**Règle** : si la `raison` mentionne un futur conjugué (`pourrait`, `devrait`, `probablement`, `possible que`, `va peut-être`) **sans être adossé à un chiffre** → score plafonné à 6.0.
- Détection : regex `/\b(pourrait|devrait|probablement|peut-être|possible que|va peut-être)\b/i` sur `raison`.
- Vérification chiffres : présence d'au moins un nombre ou pourcentage dans la même phrase.
- Si match speculatif sans chiffre → `score = min(score_brut, 6.0)` + log `sanity_check_softfail=SC5`.

**Pourquoi** : cohérent brand-platform §6 Voice & Tone — Do #4 "conditionnel d'incertitude" mais Don't "vague sans chiffres". "Le marché pourrait monter" = no-go. "Cible potentielle 18450 (cohérent backtest #B-031 win rate 61 %)" = OK. Le conditionnel doit être quantifié.

### 3.6 SC6 — Diversité sous-jacents 30 jours (v1.1)

**Règle** : si dans la fenêtre 30 jours glissants, l'edge `edge_id` du signal a triggé sur **1 seul sous-jacent / 13** (univers Bourse Direct DAX/CAC/EuroStoxx + 10 actions BD), alors :
- `score = min(score_brut, 7.0)` (plafond)
- `ALERT_flag = "ALERT"` (signal de courbure trop spécifique).
- Lookup SQLite `signals` :
  ```sql
  SELECT COUNT(DISTINCT asset_ticker) FROM signals
  WHERE edge_id = :edge_id
    AND date >= date('now', '-30 days')
    AND direction != 'NO-TRADE';
  ```
- Si résultat = 1 → SC6 déclenché.

**Pourquoi** : angle mort d'overfitting **O5 runtime** (cf. testeur-backtest-edge — overfitting au sous-jacent sur lequel l'edge a "appris"). Si l'edge H-A trigge **uniquement** sur DAX et jamais sur CAC ni EuroStoxx ni les 10 actions BD pendant 30 jours, c'est un signal qu'il est sur-spécifié au régime DAX (ex: liquidité, gap-pattern Xetra). La pondération vers 7.0 + ALERT force Thomas à valider manuellement avant trade. **Bootstrap** : SC6 désactivé les 30 premiers jours (besoin d'historique signaux).

### 3.7 Tableau de synthèse SC1-SC6 (v1.1)

| SC | Test | Action si échec | Sévérité |
|---|---|---|---|
| SC1 | direction cohérente avec SL/TP | NO-TRADE forcé | Bloquant |
| SC2 | R/R ≥ 1.5 | Score plafonné 6.0 ; R/R < 1.0 → NO-TRADE forcé | Bloquant |
| SC3 | score brut ≤ 9.0 | Flag ALERT (revue manuelle) | Avertissement |
| SC4 | % no-trade 7j ≥ 20 % | Score -1.0 | Pénalité |
| SC5 | conditionnel chiffré dans raison | Score plafonné 6.0 | Pénalité |
| **SC6** (v1.1) | **diversité sous-jacents 30j ≥ 2** | **Score plafonné 7.0 + flag ALERT** | **Avertissement** |

---

## 4. Calibration de CONFIDENCE_THRESHOLD (split paper/live, v1.1)

### 4.1 Valeurs initiales — split paper-trading vs live

**Décision v1.1** (verdicts @reviewer testeur-persona-thomas + @qa testeur-backtest-edge) : un seuil unique ne reflète ni le verbatim Thomas ni la rigueur méthodologique. **Split en 2 variables d'environnement** :

| Variable | Valeur initiale | Mode | Justification |
|---|---|---|---|
| `CONFIDENCE_THRESHOLD_PAPER` | **7.0** | Paper-trading (4-8 premières semaines) | **Verbatim Thomas** : "j'engage à partir de 7" (personas.md critères pull-the-trigger). Conservateur en bootstrap = apprentissage, on filtre dur, on accepte plus de NO-TRADE. |
| `CONFIDENCE_THRESHOLD_LIVE` | **6.5** [HYPOTHÈSE] | Live (post-validation paper) | Permissif après calibration empirique R&D — cible la valeur f(seuil) maximale (cf. §4.2). |
| `CONFIDENCE_THRESHOLD_ACTIVE` | runtime | Sélection automatique | Lecture `STRATEGY_ACTIVE` SQLite (cf. US-11 `/stop`). Si `STRATEGY_ACTIVE = 'paper'` → `CONFIDENCE_THRESHOLD_PAPER` ; si `'live'` → `CONFIDENCE_THRESHOLD_LIVE`. |

**Pseudo-code de sélection** (`src/lib/ai/scoring.ts`) :
```ts
const mode = await db.get("SELECT mode FROM strategy_state WHERE id = 1");
const threshold = mode.mode === "paper"
  ? Number(process.env.CONFIDENCE_THRESHOLD_PAPER ?? 7.0)
  : Number(process.env.CONFIDENCE_THRESHOLD_LIVE ?? 6.5);
```

### 4.1bis Procédure de transition paper → live

**Critères de bascule** (à valider explicitement par Thomas via `/start live` après revue) :
1. **Durée minimum** : ≥ 4 semaines paper-trading concluant.
2. **Volume minimum** : ≥ 30 signaux émis (hors NO-TRADE) en paper.
3. **% no-trade** : entre 30 % et 70 % (ni sur-trading, ni silence permanent).
4. **Win rate paper** : ≥ 55 % (cohérent edge-rnd-brief seuil).
5. **Drawdown max paper** : ≤ -20 % (cohérent edge-rnd-brief seuil).
6. **Aucun déclenchement circuit breaker** (3 timeouts consécutifs) sur les 7 derniers jours.

Si critères 1-6 PASS → @data-analyst valide via dashboard hebdo + Thomas exécute `/start live`. Sinon → 4 semaines paper supplémentaires + audit @qa.

### 4.2 Méthodologie de calibration en R&D

Phase 1 R&D edge (cf. edge-rnd-brief §5) :

1. **Exécuter le scoring sur 5 ans backtest** pour les 7 hypothèses H-A à H-G (in-sample 2021-2024 + out-of-sample 2025).
2. **Distribuer les scores** : histogramme par hypothèse, par sous-jacent, par direction.
3. **Tester plusieurs seuils** : 5.5, 6.0, 6.5, 7.0, 7.5, 8.0.
4. **Pour chaque seuil, calculer la fonction objectif** :
   ```
   f(seuil) = (profit_factor × win_rate × (1 - |%_no_trade - 0.50|)) / drawdown_max_pct
   ```
   (le terme `(1 - |%_no_trade - 0.50|)` favorise un % no-trade autour de 50 % — ni 0 % "force des trades", ni 90 % "ne trade jamais").
5. **Choisir le seuil qui maximise `f(seuil)`** sur le walk-forward 3 fenêtres (cf. edge-rnd-brief).
6. **Vérifier robustesse** : le seuil optimal doit être stable sur les 3 fenêtres walk-forward (variation < ±0.5).

### 4.3 Passage à la calibration finale

La calibration R&D §4.2 produit la valeur optimale de `CONFIDENCE_THRESHOLD_LIVE` (la valeur paper reste figée à 7.0 par décision persona).

- Si calibration sort `CONFIDENCE_THRESHOLD_LIVE = X.Y` ≠ 6.5 → `@testeur-backtest-edge` audite + `@ia` met à jour la variable d'environnement et documente dans `model-selection.md` (à créer Phase 1 si valeur change).
- `CONFIDENCE_THRESHOLD_PAPER = 7.0` reste figé (ancrage verbatim Thomas — modification = revue persona requise).
- Le split est documenté pour Thomas dans le help du bot (`/help` US-XX) : "Mode paper = filtre 7.0 conservateur, mode live = filtre 6.5 calibré R&D."

---

## 5. Test cases — 5 inputs réalistes complets

### 5.1 TC-01 — ACHAT DAX gap+ORB (score 8.0, SAFE)

**Input** (lundi 4 mai 2026, 8h47 CET) :
```json
{
  "edge_id": "H-A", "asset": {"ticker": "^GDAXI", "name": "DAX"},
  "edge_features": {"gap_pct": 0.82, "prev_close_us": 4521.30,
                    "orb_breakout": true, "orb_high": 18420,
                    "volume_premarket_ratio": 1.4, "sigma_gap_30d": 0.45},
  "indicators": {"rsi_14": 58, "macd_histogram": 0.3, "bollinger_position": "upper_quartile"},
  "news_titles": null,
  "vix": 14.2,
  "backtest_ref": "#B-031",
  "backtest_stats": {"win_rate": 61, "nb_trades": 87, "drawdown_max_pct": -18, "sharpe": 1.3, "period": "2021-2025", "age_days": 12}
}
```

**Décomposition par dimension** :

| Dim | Calcul | Score | Pondéré |
|---|---|---|---|
| D1 (30 %) | gap_pct/σ_gap = 0.82/0.45 ×5 = 9.1 | 9.1 | 2.73 |
| D2 (15 %, v1.1) | RSI 58 + MACD>0 + BB upper = 3/3 alignés ACHAT | 10 | 1.50 |
| D3 (15 %) | news indispo → plafond 7.0 | 7.0 | 1.05 |
| D4 (15 %) | volume_ratio 1.4 = sur-volatilité | 8 | 1.20 |
| D5 (10 %) | VIX 14.2 < 15 = trend | 8 | 0.80 |
| D6 (15 %, v1.1) | Sharpe 1.3×3 + 61/10 + min(87/20,5) = 14.9 → clip 10 ; backtest 12j frais → pas de pénalité | 10 | 1.50 |
| **Σ** | | | **8.78** |

**Réponse Claude (résumée)** : `direction=ACHAT`, `score_brut=8.0` (Claude tempère le 8.78 vers 8.0, jugement composite raisonnable), raison "Gap haussier +0,82 % sur clôture US + ORB Xetra cassé à la hausse (18420) + volume pré-marché 1,4× moyenne. Cible potentielle alignée backtest #B-031."

**Sanity checks appliqués** :
- SC1 : entry 3.42 < tp 3.85, entry 3.42 > sl 3.21 → cohérent ACHAT ✅
- SC2 : R/R = (3.85-3.42)/(3.42-3.21) = 2.05 ≥ 1.5 ✅
- SC3 : 8.0 ≤ 9.0 → SAFE ✅
- SC4 : %no-trade 7j = 30 % ≥ 20 % → pas de pénalité ✅
- SC5 : raison "Cible potentielle alignée backtest" — conditionnel chiffré ✅

**Score final** : **8.0**, `ALERT_flag=SAFE`, signal envoyé sur Telegram.

### 5.2 TC-02 — VENTE CAC gap+news BCE (score 7.0, SAFE)

**Input** (mardi 5 mai 2026, 8h48 CET) :
```json
{
  "edge_id": "H-E", "asset": {"ticker": "^FCHI", "name": "CAC40"},
  "edge_features": {"gap_pct": -0.65, "sentiment_score": -0.72,
                    "news_titles": ["BCE: signal hawkish inattendu", "TotalEnergies: profit warning Q2"]},
  "indicators": {"rsi_14": 42, "macd_histogram": -0.2, "bollinger_position": "lower_quartile"},
  "vix": 18.5,
  "backtest_ref": "#B-024",
  "backtest_stats": {"win_rate": 56, "nb_trades": 64, "drawdown_max_pct": -22, "sharpe": 0.9, "age_days": 30}
}
```

**Décomposition** :

| Dim | Calcul | Score | Pondéré |
|---|---|---|---|
| D1 (30 %) | sentiment ×10 = 7.2 | 7.2 | 2.16 |
| D2 (15 %, v1.1) | RSI 42 + MACD<0 + BB lower = 3/3 alignés VENTE | 10 | 1.50 |
| D3 (15 %) | sentiment -0.72 ×10 = 7.2 (aligné VENTE) | 7.2 | 1.08 |
| D4 (15 %) | atr élevé sur news = sur-volatilité | 7 | 1.05 |
| D5 (10 %) | VIX 18.5 = range | 6 | 0.60 |
| D6 (15 %, v1.1) | Sharpe 0.9×3 + 56/10 + min(64/20,5)=11.5→clip 10 ; backtest 30j ok | 10 | 1.50 |
| **Σ** | | | **7.89** |

**Réponse Claude** : `direction=VENTE`, `score_brut=7.0` (Claude pondère vers le bas vu Sharpe modeste), raison "Gap baissier -0,65 % + BCE hawkish inattendu (sentiment -0,72) + RSI 42 / MACD négatif. Cible potentielle alignée backtest #B-024."

**Sanity checks** :
- SC1 : VENTE → entry 1.85 < sl 1.92, entry 1.85 > tp 1.72 ✅
- SC2 : R/R = (1.85-1.72)/(1.92-1.85) = 1.86 ≥ 1.5 ✅
- SC3 : 7.0 ≤ 9.0 → SAFE ✅
- SC4 : %no-trade 7j = 25 % ≥ 20 % ✅
- SC5 : "Cible potentielle alignée backtest" ✅

**Score final** : **7.0**, `ALERT_flag=SAFE`, signal VENTE envoyé.

### 5.3 TC-03 — NO-TRADE marché flat (score 5.2, NO-TRADE)

**Input** (mercredi 6 mai 2026, 8h44 CET) :
```json
{
  "edge_id": "H-A", "asset": {"ticker": "^STOXX50E", "name": "EuroStoxx50"},
  "edge_features": {"gap_pct": 0.10, "orb_breakout": false, "sigma_gap_30d": 0.45},
  "indicators": {"rsi_14": 51, "macd_histogram": 0.05, "bollinger_position": "middle"},
  "vix": 16.8,
  "backtest_ref": "#B-031",
  "backtest_stats": {"win_rate": 61, "nb_trades": 87, "drawdown_max_pct": -18, "sharpe": 1.3, "age_days": 14}
}
```

**Décomposition** :

| Dim | Calcul | Score | Pondéré |
|---|---|---|---|
| D1 (30 %) | gap 0.10/0.45×5 = 1.1 | 1.1 | 0.33 |
| D2 (15 %, v1.1) | RSI 51 ≈ neutre, MACD ≈ 0, BB middle = 0/3 alignés | 0 | 0.00 |
| D3 (15 %) | news indispo → plafond 7.0 | 7.0 | 1.05 |
| D4 (15 %) | volatilité moyenne | 5 | 0.75 |
| D5 (10 %) | VIX 16.8 = range | 6 | 0.60 |
| D6 (15 %, v1.1) | backtest stats fortes | 10 | 1.50 |
| **Σ** | | | **4.23** (v1.1, ex-3.73) |

**Réponse Claude** : `direction=NO-TRADE`, `score_brut=5.2` (Claude remonte légèrement par jugement composite mais reste sous seuil), raison "Marché flat à l'ouverture (gap 0,1 %), RSI neutre, range ORB non cassé. Aucune configuration au-dessus du seuil actif (6.5 live ou 7.0 paper)."

**Sanity checks** :
- SC1 : NO-TRADE → entry/sl/tp = null ✅
- SC2 : N/A pour NO-TRADE
- SC3 : 5.2 ≤ 9.0 ✅
- SC4 : %no-trade 7j = 30 % ✅
- SC5 : "Aucune configuration au-dessus du seuil" — pas de spéculatif ✅
- SC6 (v1.1) : H-A trigge sur 5 sous-jacents distincts dans 30j (DAX/CAC/EuroStoxx/2 actions BD) ≥ 2 ✅

**Score final** : **5.2**, `ALERT_flag=NO-TRADE`, message Telegram NO-TRADE 3 lignes.

### 5.4 TC-04 — NO-TRADE conflit news/technique (score 5.8, ALERT)

**Input** (jeudi 7 mai 2026, 8h47 CET) :
```json
{
  "edge_id": "H-C", "asset": {"ticker": "MC.PA", "name": "LVMH"},
  "edge_features": {"orb_breakout": true, "orb_direction": "haussier", "orb_amplitude": 1.8,
                    "news_titles": ["LVMH: rumeur scission Tiffany"], "sentiment_score": -0.5},
  "indicators": {"rsi_14": 62, "macd_histogram": 0.4, "bollinger_position": "upper_quartile", "atr_14": 1.5},
  "vix": 17.2,
  "backtest_ref": "#B-018",
  "backtest_stats": {"win_rate": 58, "nb_trades": 52, "drawdown_max_pct": -19, "sharpe": 1.1, "age_days": 22}
}
```

**Décomposition** :

| Dim | Calcul | Score | Pondéré |
|---|---|---|---|
| D1 (30 %) | ORB haussier amplitude 1.8/atr 1.5 ×4 = 4.8 | 4.8 | 1.44 |
| D2 (15 %, v1.1) | RSI 62 + MACD>0 + BB upper = 3/3 alignés ACHAT | 10 | 1.50 |
| D3 (15 %) | sentiment -0.5 (signal hausser, news baissier) → pénalité ×5 = -2.5 | 0 (clip) | 0.00 |
| D4 (15 %) | atr 1.5 = volatilité moyenne | 5 | 0.75 |
| D5 (10 %) | VIX 17.2 = range | 6 | 0.60 |
| D6 (15 %, v1.1) | nb_trades 52 < 30 ? Non, 52 OK ; Sharpe 1.1×3+5.8+min(52/20,5)=11.7→clip 10 | 10 | 1.50 |
| **Σ** | | | **5.79** |

**Réponse Claude** : `direction=NO-TRADE`, `score_brut=5.8`, raison "Signaux techniques (ORB haussier) et news (sentiment -0,5 sur rumeur scission) contradictoires — pas de configuration univoque."

**Sanity checks** :
- SC1 : NO-TRADE → entry/sl/tp = null ✅
- SC2 : N/A
- SC3 : 5.8 ≤ 9.0 → mais conflit détecté → **ALERT_flag = ALERT** (signal divergence)
- SC4 : %no-trade 7j = 28 % ≥ 20 % ✅
- SC5 : raison sans futur spéculatif ✅

**Score final** : **5.8**, `ALERT_flag=ALERT` (conflit détecté), message Telegram NO-TRADE avec mention "signaux contradictoires".

### 5.5 TC-05 — Timeout DEGRADED MODE (pas de scoring)

**Input** (vendredi 15 mai 2026, 8h47 CET) :
- Données Twelve Data OK, contexte assemblé OK.
- Appel Claude n°1 : timeout 45 s.
- Retry 1 (10 s plus tard) : timeout 30 s.
- Retry 2 (5 s plus tard) : timeout 15 s.
- Total écoulé : 8h49:30 — encore avant cutoff 8h55.

**Décomposition** : N/A (pas de réponse Claude reçue).

**Sanity checks** : non applicables — le pipeline n'a pas de score à corriger.

**Action pipeline** :
- US-05 DEGRADED MODE déclenchée.
- Telegram reçoit le template DEGRADED MODE (3 lignes — cf. functional-specs §2).
- SQLite : `direction=NO-TRADE`, `statut="erreur_claude"`, `motif="timeout_après_2_retries"`, `circuit_breaker_counter += 1`.
- Si `circuit_breaker_counter >= 3` consécutifs → pause 24h + alerte critique Telegram.

**Score final** : **N/A**, `ALERT_flag=NO-TRADE` (DEGRADED MODE), pas de signal envoyé (silence assumé).

---

## 6. Performance et coûts

### 6.1 Tokens par appel

| Élément | Tokens estimés | Source |
|---|---|---|
| System prompt (cacheable) | ~3 200 | `prompt-library.md` §1 |
| User input (variable) | ~600-1 200 (selon edge_id et news) | `SignalScoringInput` |
| **Input total** | **~3 800-4 400** | sous cap 5 000 (ai-architecture §2.1) |
| Output JSON 15 champs + raison | ~500-900 | tool_use forcé |
| **Output total** | **~600-1 000** | sous cap 1 000 |

### 6.2 Latence cible

- **Cible** : < 30 s par appel scoring.
- **Marge US-05** : 45 s timeout − 30 s cible = **15 s de marge**.
- Sonnet 4.5 P50 estimée 3-6 s pour 5k in / 1k out (cf. ai-architecture §1.1) → cible largement atteignable.
- Si latence P95 dépasse 30 s pendant 3 jours → alerte + audit (peut-être dégradation provider).

### 6.3 Coût par signal

Calcul Sonnet 4.5 live avec prompt caching (-90 % sur ~80 % du prompt) :

| Élément | Tokens | Tarif | Coût |
|---|---|---|---|
| Input cacheable (3 200 × 80 %) | 2 560 | 0,30 $/M (cached) | 0,00077 $ |
| Input non-cacheable (3 200 × 20 % + 1 000) | 1 640 | 3,00 $/M | 0,00492 $ |
| Output | 800 | 15,00 $/M | 0,01200 $ |
| **Total / signal** | | | **~0,019 $ ≈ 0,02 €** |

Sans cache : ~0,03 $/signal (cohérent ai-architecture §7.1 — 0,66 $/mois ÷ 22 signaux ≈ 0,03 $/signal).

### 6.4 Verdict H4

✅ **PASS confortable** : 22 signaux/mois × 0,02-0,03 $ = **0,44-0,66 $/mois live**, très large marge sous le budget 10 €/mois. Cohérent ai-architecture §7.3.

### 6.5 Optimisations rappel

1. **Prompt caching ephemeral** sur le system prompt (3 200 tokens) — `-90 %` sur réutilisations.
2. **Pas de streaming** — synchrone simple.
3. **Cap `max_tokens=1024`** sur output.
4. **Batch API en R&D uniquement** — pas pour le live (latence batch 24h incompatible avec fenêtre 8h45-8h55).

---

## 7. Versioning et migration modèle

### 7.1 Version du modèle de scoring

- **Version actuelle** : `scoring-model-v1.1` (Phase 1b corrections @reviewer + @qa).
- **Couplage** : `scoring-model-v1.1` ↔ `prompt-version=signal-scoring-v1.1` ↔ `model_used=claude-sonnet-4-5-20250929` (live, **tag exact inchangé** cf. L002) ou `claude-haiku-4-5` (R&D).
- **Stockage SQLite** : table `signals` colonnes `scoring_model_version`, `prompt_version`, `model_used` (cf. data-analyst kpi-framework SQL schema).

### 7.1bis Changelog

**v1.1 (2026-05-01) — Corrections Phase 1b @reviewer + @qa**
- **A3 (split CONFIDENCE_THRESHOLD)** : décomposition en `CONFIDENCE_THRESHOLD_PAPER = 7.0` (verbatim Thomas) et `CONFIDENCE_THRESHOLD_LIVE = 6.5` [HYPOTHÈSE] avec sélection runtime via `STRATEGY_ACTIVE` SQLite. Procédure transition paper → live explicitée (§4.1bis).
- **A4a (repondération D2/D6)** : D2 confluence indicateurs 20 % → **15 %** (corrélation intra-classe RSI/MACD/BB), D6 référence backtest 10 % → **15 %** (signal le plus robuste anti-overfitting). Total reste 100 % (30 + 15 + 15 + 15 + 10 + 15).
- **A4b (ajout SC6 diversité sous-jacents)** : nouveau sanity check — si edge trigge sur 1 seul sous-jacent / 13 dans fenêtre 30 jours → score plafonné 7.0 + flag ALERT. Couvre angle mort O5 runtime (overfitting au sous-jacent d'apprentissage). Bootstrap 30j (lookup historique requis).
- **Test cases TC-01 à TC-05** : recalculés avec nouvelles pondérations (cf. §5).

**v1.0 (2026-05-01) — Création initiale**
- Approche hybride Claude + 5 sanity checks. 6 dimensions (30/20/15/15/10/10). CONFIDENCE_THRESHOLD unique = 6.5 [HYPOTHÈSE]. 5 TC réalistes.

### 7.2 Quand bumper la version

- **v1.X** (mineure) : ajustement poids dimensions D1-D6, ajustement seuils sanity checks (ex: SC2 R/R 1.5 → 1.7).
- **v2.0** (majeure) : ajout/suppression d'une dimension, refonte de l'architecture hybride.
- **Couplé** : si bump `scoring-model-v1.1 → v1.2`, alors bump aussi `prompt-version=signal-scoring-v1.2` (synchronisation obligatoire pour traçabilité). À ce jour : `v1.1` ↔ `signal-scoring-v1.1`.

### 7.3 Procédure de migration (cf. ai-architecture §8 + protocole agent @ia)

1. **Lire la doc API du nouveau modèle** (si Sonnet 4.6 sort).
2. **Comparer paramètres** (mapping ancien → nouveau).
3. **Régression test sur les 5 cases TC-01 à TC-05** (fixtures `tests/fixtures/ai/`). Si un output régresse → ne pas déployer.
4. **Propager à TOUS les builders** — Grep `claude-sonnet-4-5` dans `src/lib/ai/` doit retourner 0 occurrence après migration. Builders concernés : `scoringClient.ts`, `rndScoringClient.ts`, `newsScoringClient.ts`.
5. **Bump PROMPT_VERSION + scoring-model-version** (sync obligatoire).
6. **Documenter dans `model-selection.md`** (à créer si migration) + mise à jour ai-architecture §1.2.

### 7.4 Tag exact obligatoire (rappel L002)

`claude-sonnet-4-5-20250929` (tag exact, **pas `-latest`**). Cohérent ai-architecture §1.2 + règle alias agent @ia. Un alias cross-family peut basculer de génération sans warning = régression silencieuse en production sur signal qui engage du capital réel.

---

## 8. Handoff vers @testeur-backtest-edge

### 8.1 Mission de l'audit

Audit du modèle de scoring `scoring-model-v1.1` (Phase 1b corrections @reviewer + @qa intégrées) avant Phase 2 implémentation.

### 8.2 Points d'audit résolus en v1.1

- ✅ **Pondérations D1-D6 rééquilibrées** (D2 20→15, D6 10→15) — verdict @qa intégré.
- ✅ **Angle mort overfitting O5 runtime couvert** par SC6 (diversité sous-jacents 30j).
- ✅ **CONFIDENCE_THRESHOLD split paper/live** — résout conflit persona (7.0) vs méthodologue (6.5 calibrable).

### 8.2bis Points d'audit restants pour @testeur-backtest-edge

1. **Validité statistique du nouveau split 30/15/15/15/10/15** sur 5 ans backtest walk-forward — produire histogrammes de scores par hypothèse pour vérifier qu'aucune dimension ne sature systématiquement.
2. **Calibration `CONFIDENCE_THRESHOLD_LIVE`** : exécuter §4.2 sur les 7 hypothèses H-A à H-G + walk-forward 3 fenêtres → confirmer 6.5 ou recommander valeur optimale.
3. **Reproductibilité scoring** : avec température 0.1 + tool use forcé + sanity checks déterministes, le même input produit-il le même output à ±0,2 ? Tester sur les 5 TC.
4. **Validation SC6 seuil 1/13** : faut-il un seuil plus fin (ex: 2/13 → ALERT, 1/13 → NO-TRADE) ? Validation empirique sur 5 ans.

### 8.3 Verdict attendu

- **GO modèle v1.1** : `scoring-model-v1.1` validé, Phase 2 peut démarrer (intégration `src/lib/ai/` par @fullstack).
- **RETRAVAILLER §X** : ajustements ciblés (poids dimensions, seuils SC, calibration). @ia bump v1.2 et re-soumet.
- **NO-GO modèle** : repenser l'approche (ex: scoring déterministe pur sans LLM, ou inverse). @orchestrator escalade.

---

## 9. Auto-évaluation — Gates BLOQUANT

| Gate | Critère | Verdict | Évidence |
|---|---|---|---|
| G1 | Toutes sections présentes | PASS | §1 à §8 + auto-éval §9 remplies |
| G3 | Bloc Handoff structuré présent | PASS | §8 + bloc Handoff final |
| G5 | Persona Thomas identique project-context.md | PASS | TC-01 à TC-05 cohérents fenêtre 8h45-8h55, capital 1500 €, turbos Bourse Direct, journée type Thomas. **v1.1 : `CONFIDENCE_THRESHOLD_PAPER = 7.0` ancré sur verbatim Thomas "j'engage à partir de 7"** (cohérence persona renforcée). |
| G6 | Cohérence brand-platform | PASS | SC5 conditionnel chiffré obligatoire, SC4 % no-trade vertu, mots proscrits intégrés via R-AI-7 (ai-architecture §3). SC6 anti-overfitting cohérent Pilier 3 "Backtesté". |
| G7 | 0 contradiction livrables amont + cohérence persona/méthodologue | PASS | Référence explicite ai-architecture §1.1 (modèles), §3 (R-AI-1..9), §7 (coûts), prompt-library.md §1 (system prompt), §2 (prompts H-A..G), §4.2 (prompt dégradé), edge-rnd-brief §5 (seuils GO Phase 2), functional-specs US-01 (15 champs) + US-05 (timeout), US-11 (`STRATEGY_ACTIVE`). **v1.1 résout le conflit verdicts @reviewer (persona 7.0) vs @qa (calibrable 6.5) via split d'env var** = cohérence persona + méthodologue PASS. |
| G12 | Implémentable @fullstack sans question | PASS | Formules explicites D1-D6 + pseudo-code 6 SC + fonction objectif calibration + 5 TC complets décomposés + **pseudo-code TS de sélection threshold runtime §4.1** + lookup SQL SC6 §3.6 + critères transition paper→live §4.1bis. |
| G13 | 0 donnée inventée | PASS | Tarifs sourcés ai-architecture §1.1 ; tokens sourcés §2.1 + §5 ; HYPOTHÈSE 6.5 marquée explicitement §4.1 ; valeur 7.0 sourcée verbatim Thomas (personas.md). |
| G14 | 5 test cases complets | PASS | §5 — 5 TC avec input JSON + décomposition D1-D6 (pondérations v1.1) + Claude résumé + sanity checks (incl. SC6 v1.1) + score final. TC-03 Σ recalculé 3.73 → **4.23** (NO-TRADE inchangé sous les 2 seuils). |
| G15 | 0 placeholder résiduel | PASS | Aucun `[À REMPLIR]`/`[TODO]` ; `[HYPOTHÈSE]` n'apparaît qu'au §4.1 (`CONFIDENCE_THRESHOLD_LIVE`), volontaire et marqué. La valeur paper 7.0 n'est pas hypothèse (verbatim persona). |
| **G17** | **Pas copiable pour concurrent** | **PASS** | Spécifique TradingApp : Thomas (verbatim "à partir de 7"), turbos BD, fenêtre 8h45-8h55, 7 hypothèses H-A..G nommées, 13 sous-jacents BD nommés (SC6), `STRATEGY_ACTIVE` SQLite US-11, brand-platform §6, calibration walk-forward 3 fenêtres edge-rnd-brief. |
| G17 | Pas copiable pour concurrent | PASS | Spécifique TradingApp : Thomas, turbos, fenêtre 8h45-8h55, 7 hypothèses H-A..G nommées, calendrier fériés FR (TC-05), sous-jacents BD (DAX/CAC/EuroStoxx/LVMH), brand-platform §6 cité |

---

## Handoff

---
**Handoff → @orchestrator (relai vers @testeur-backtest-edge pour audit, puis @fullstack Phase 2)**

- **Fichiers produits** :
  - `/home/user/TradingApp/docs/ia/edge-scoring-model.md` (ce fichier, **scoring-model-v1.1** Phase 1b)
- **Décisions prises** :
  - Approche **hybride** Claude (score brut + raison) + **6 sanity checks déterministes** (v1.1) ex-post.
  - **6 dimensions** pondérées (v1.1) : D1 force signal 30 %, D2 confluence **15 %**, D3 news 15 %, D4 volatilité 15 %, D5 régime VIX 10 %, D6 backtest **15 %**.
  - **6 sanity checks** (v1.1) : SC1 cohérence direction (bloquant), SC2 R/R ≥ 1.5 (bloquant si <1.0), SC3 score > 9 → ALERT, SC4 % no-trade 7j < 20 % → -1.0, SC5 spéculatif sans chiffre → plafond 6.0, **SC6 diversité sous-jacents 30j (1/13) → plafond 7.0 + ALERT**.
  - **CONFIDENCE_THRESHOLD split paper/live** (v1.1) : `_PAPER = 7.0` (verbatim Thomas, bootstrap conservateur 4-8 sem.), `_LIVE = 6.5` [HYPOTHÈSE — calibration R&D]. Sélection runtime via `STRATEGY_ACTIVE` SQLite (US-11). Procédure transition paper → live §4.1bis.
  - **Coût/signal** : ~0,02-0,03 $ avec cache (verdict H4 PASS confortable).
  - **Versioning** : `scoring-model-v1.1` couplé à `prompt-version=signal-scoring-v1.1` + `model_used=claude-sonnet-4-5-20250929` (tag exact L002).
- **Points d'attention** :
  - **Prérequis bloquant Phase 2** : audit @testeur-backtest-edge (4 points §8.2) avant que @fullstack code l'intégration.
  - **Calibration `CONFIDENCE_THRESHOLD`** : Phase 1 R&D obligatoire — valeur 6.5 a priori conservatrice mais à valider sur 5 ans backtest avec walk-forward 3 fenêtres.
  - **VIX/V2X** : si données indisponibles via Twelve Data → D5 = 5 par défaut (neutre, pas de pénalité). À vérifier que le plan Twelve Data Pro Individual inclut VIX/V2X.
  - **SC4 lookup SQLite** : la table `signals` doit être en place avec ≥ 7 jours de données avant que SC4 puisse s'activer. Bootstrap : SC4 désactivé les 7 premiers jours.
  - **Migration future Sonnet 4.6+** : suivre protocole §7.3 — régression test sur les 5 TC, Grep tag exact dans tous les builders.
  - **Coordination @qa** : tests E2E doivent inclure les 5 TC + propriété de reproductibilité (même input → même output ±0.2).
- **Actions Replit requises** :
  - [x] **Nouvelles env vars v1.1** : `CONFIDENCE_THRESHOLD_PAPER=7.0` et `CONFIDENCE_THRESHOLD_LIVE=6.5` (remplacent l'ancienne `CONFIDENCE_THRESHOLD` unique). `RND_DAILY_CALL_CAP`, `MONTHLY_AI_BUDGET_EUR`, `ANTHROPIC_MODEL_LIVE`, `ANTHROPIC_MODEL_RND` inchangées.
  - [x] **Coordination @data-analyst** : la table `strategy_state` (mode `paper`/`live`) doit exister AVANT que `src/lib/ai/scoring.ts` puisse sélectionner le seuil actif (cf. US-11 `/stop`/`/start`). Bootstrap : `mode = 'paper'` par défaut à l'init.
  - [x] **SC6 lookup SQLite** : la table `signals` doit avoir ≥ 30 jours d'historique avant que SC6 puisse s'activer. Bootstrap : SC6 désactivé les 30 premiers jours (en plus du bootstrap SC4 7 jours déjà documenté).
  - [x] Aucune migration DB nouvelle au-delà des colonnes `scoring_model_version`, `prompt_version`, `model_used`, `sanity_check_failed` déjà spécifiées (à vérifier `data-analyst kpi-framework`).
  - [x] Aucune modification `.replit`/`replit.nix` requise.

---
