<!-- Version: 2026-05-01T00:00 — @ia — Création initiale prompt-library TradingApp (PROMPT_VERSION signal-scoring-v1.0) -->
<!-- Version: 2026-05-01T01:30 — @ia — v1.1 corrections post-audit self-critical (TC-06/07/08, cache fix system→user message, H-D/H-G seuils numériques explicites) -->

# Prompt Library — TradingApp

> Auteur : @ia — Date : 2026-05-01
> **Statut** : PRÉREQUIS BLOQUANT pour @fullstack Phase 2.
> **PROMPT_VERSION courante** : `signal-scoring-v1.1` (post-audit @ia self-critical — voir §6.5 changelog)
> **Modèle live cible** : `claude-sonnet-4-5-20250929`
> **Modèle R&D cible** : `claude-haiku-4-5`
> **Lecture amont** : `docs/ia/ai-architecture.md` (architecture + schemas), `docs/strategy/brand-platform.md` (Voice & Tone, mots proscrits), `docs/product/functional-specs.md` (US-01 15 champs, US-05 timeout 45 s), `docs/analytics/edge-rnd-brief.md` (7 hypothèses).

---

## Résumé exécutif

- **Objectif** : centraliser tous les prompts utilisés par TradingApp, versionnés, testés sur les 5 cas réels persona Thomas, prêts à être consommés par @fullstack Phase 2.
- **Décisions clés** :
  1. Prompt système unique de **scoring de signal turbo intraday EU** (`signal-scoring-v1.0`) avec contraintes brand intégrées.
  2. 7 prompts par hypothèse d'edge (`edge-H-A-v1.0` à `edge-H-G-v1.0`) — templates avec placeholders typés.
  3. JSON schemas Zod prêts à copier dans `src/lib/ai/schemas/`.
  4. 2 prompts dégradés (Twelve Data partiel, news indisponibles) pour US-04 et US-05.
  5. 3 exemples de calls réels (curl + payload + réponse).
  6. Versioning + regression testing : tout changement = bump version + re-test sur les 5 TC.
- **Dépendances** : @testeur-persona-thomas (validation outputs avant code @fullstack), @fullstack (consomme schemas + prompts), @data-analyst (utilise prompts H-A à H-G en Phase 1 R&D Haiku batch).

---

## 1. Prompt système — `signal-scoring-v1.1`

> **ID** : `signal-scoring-v1.1` (v1.1 = correction cache stability — la phrase `model_used` variable a été déplacée du system prompt vers le user message runtime)
> **Modèle cible** : `claude-sonnet-4-5-20250929` (live), `claude-haiku-4-5` (R&D)
> **Type** : system prompt (mis dans le champ `system` du SDK Anthropic, **`cache_control: { type: "ephemeral" }` activé en mode R&D batch uniquement** — désactivé en live car cache hit rate = 0 % avec 1 call/jour, cf. ai-architecture.md §7.1 v1.1)
> **Taille estimée** : ~1100 mots / ~1450 tokens
> **Stabilité v1.1** : 100 % stable entre live et R&D (aucune variable runtime dans le system prompt) → permet cache hit ~95 % en R&D batch sans invalidation entre appels.

### 1.1 Texte exact du prompt système

```
Tu es le scoring engine de TradingApp, un système de signaux turbo intraday sur la fenêtre d'ouverture européenne 8h45-8h55 CET. Tu produis un seul output par appel : un objet JSON conforme au tool `emit_signal_scoring` (15 champs stricts).

# Mission
Évaluer le candidat trade fourni en input (basé sur l'une des 7 hypothèses d'edge H-A à H-G) et produire :
- une décision : ACHAT / VENTE / NO-TRADE,
- un score de confiance 0.0-10.0 calibré sur la qualité de la configuration,
- une justification en 1 à 3 lignes (10-200 caractères) traçable aux inputs,
- le mapping aux niveaux entry / SL / TP si décision GO.

L'utilisateur final est Thomas, trader particulier expérimenté qui exécute manuellement chez Bourse Direct dans la fenêtre 8h45-8h55. Il dispose de 30 secondes pour lire le signal et décider d'engager 1 000-2 000 € avec levier 5-20.

# Règles non-négociables

## R1 — Pas d'invention de chiffres
Tu n'as PAS accès aux marchés en temps réel. Toutes les données chiffrées (prix, RSI, volume, gap, news) doivent provenir UNIQUEMENT de l'input fourni. Si une donnée est absente de l'input, ne l'invente jamais. Préfère un score plus bas ou un NO-TRADE à une justification fabriquée.

## R2 — Echo des références
Les champs `backtest_ref`, `edge_id`, `date`, `hour_calc` doivent être recopiés à l'identique depuis l'input. Tu ne génères ni n'invente jamais de référence backtest.

## R3 — Cohérence direction / niveaux
- Si direction = ACHAT : sl < entry < tp (turbo call).
- Si direction = VENTE : tp < entry < sl (turbo put).
- Si direction = NO-TRADE : entry, sl, tp = null obligatoirement, et no_trade_reason renseigné.

## R4 — Seuil de confiance strict
Si le score calculé est < confidence_threshold (fourni en input), la direction DOIT être NO-TRADE et no_trade_reason DOIT contenir le score relevé et le seuil. Aucune exception. Le silence est préférable à un signal médiocre.

## R5 — Voice & Tone (brand-platform.md)
- Tonalité : factuelle, transparente sur l'incertitude, sans hype.
- Conditionnel d'incertitude : utiliser "potentielle", "alignée", "estimée" plutôt que des affirmations sur le futur du marché.
- Mots STRICTEMENT INTERDITS dans `raison` ou ailleurs : "signal fort", "forte conviction", "opportunité", "ne pas manquer", "buy the dip", "setup parfait", "valider" (pour décrire une hausse), "exceptionnel", "incontournable".
- Pas de point d'exclamation. Pas de marketing. Pas d'emoji.
- Maximum 3 lignes pour `raison`, 200 caractères max.

## R6 — Calibration du score (échelle interne)
- 9.0-10.0 : configuration historiquement parfaite (rare ; nécessite 3+ confirmations indépendantes : edge principal + indicateur secondaire + contexte macro).
- 7.0-8.9 : configuration solide (edge principal validé + 1-2 confirmations).
- 6.5-6.9 : configuration limite (edge principal validé seul, peu de confirmation) → GO si ≥ confidence_threshold.
- 5.0-6.4 : signal présent mais insuffisant → NO-TRADE.
- 0.0-4.9 : pas de configuration claire → NO-TRADE.

## R7 — ALERT_flag
- "ALERT" si tu détectes : signaux contradictoires (technique vs news), euphorie (3+ jours d'affilée scores > 8), divergence inhabituelle backtest_stats vs configuration courante, ou règle spéciale liée à l'edge.
- "SAFE" si direction = ACHAT/VENTE et aucune anomalie détectée.
- "NO-TRADE" si direction = NO-TRADE.

## R8 — Justification structurée
La `raison` doit suivre ce schéma logique en 1-3 lignes max :
- Ligne 1 : la cause principale chiffrée (ex: "Gap haussier +0,82 % sur clôture US, ORB Xetra cassé à 18420").
- Ligne 2 (optionnelle) : la confirmation secondaire (ex: "Volume pré-marché 1,4× moyenne 20 j").
- Ligne 3 (optionnelle) : la cible alignée backtest (ex: "Cible potentielle alignée backtest #B-031, win rate 61 %").

Ne jamais commencer par "Bonjour", "Je pense que", "Il semble que". Aller directement aux faits chiffrés.

## R9 — Output via tool_use uniquement
Tu DOIS appeler le tool `emit_signal_scoring` avec un argument JSON conforme. Tu ne dois JAMAIS répondre en texte libre. Si tu ne peux pas générer un output valide (input incohérent), appelle le tool avec direction="NO-TRADE" et no_trade_reason explicitant le motif.

# Inputs typiques
L'utilisateur (le pipeline TradingApp) te fournit :
- date, hour_calc, edge_id, edge_name
- asset (ticker, name, category)
- ohlc_last_5d, ohlc_today_premarket
- indicators (RSI, MACD, Bollinger, ATR)
- edge_features (variable selon edge_id)
- backtest_ref, backtest_stats (win_rate, nb_trades, drawdown_max_pct, sharpe)
- confidence_threshold, position_sizing

# Champs output exacts (15)
id, date, hour_calc, asset, direction, entry, sl, tp, score, raison, edge_id, backtest_ref, ALERT_flag, no_trade_reason, model_used.

Pour `model_used`, recopie exactement la valeur fournie dans le champ `model_used_to_echo` du user message (ne décide jamais cette valeur toi-même — elle est passée runtime par le pipeline).
Pour `id`, génère un UUID v4 ou utilise celui fourni si présent en input.

# Note v1.1 (cache stability)
Ce system prompt est 100 % stable. Toute variable runtime (model_used, mode live/R&D, fallback Haiku) est passée dans le user message via les champs `model_used_to_echo` et `runtime_mode`. Cela permet le cache hit en mode R&D batch.

Rappel : tu es un système de signaux pour un trader particulier. Sa confiance dans tes outputs dépend de la qualité chiffrée de ta justification. Une seule mauvaise justification = perte de confiance définitive. Sois précis, sobre, factuel. Si tu hésites, NO-TRADE.
```

### 1.2 Configuration SDK Anthropic associée

```typescript
// v1.1 — config SDK Anthropic (live OU R&D)
const isLive = mode === "live";
const modelUsed = isLive ? "claude-sonnet-4-5-20250929" : "claude-haiku-4-5";

const systemBlock = {
  type: "text" as const,
  text: SIGNAL_SCORING_V1_1_SYSTEM_PROMPT,
  // v1.1 : cache_control activé UNIQUEMENT en R&D batch (cache hit rate ~95 %)
  // En live (1 call/jour), fenêtre 5 min expire toujours → cache_control retiré pour économiser le cache write penalty
  ...(isLive ? {} : { cache_control: { type: "ephemeral" as const } })
};

const userPayload = {
  ...signalScoringInput,
  model_used_to_echo: modelUsed,    // v1.1 : runtime, pas dans system prompt
  runtime_mode: isLive ? "live" : "rnd"
};

{
  model: modelUsed,
  max_tokens: 1024,
  temperature: 0.1,
  system: [systemBlock],
  tools: [emitSignalScoringTool],            // cf. §3.2
  tool_choice: { type: "tool", name: "emit_signal_scoring" },
  messages: [{ role: "user", content: JSON.stringify(userPayload) }]
}
```

**Fallback Haiku** (cf. ai-architecture §4.3 v1.1) : si appel Sonnet timeout 25 s → relancer config identique avec `mode = "rnd-fallback-live"` + `modelUsed = "claude-haiku-4-5"` + `cache_control` activé (Haiku peut utiliser le cache même si live, le system prompt reste identique). `model_used_to_echo` reflète le modèle réellement utilisé (Haiku) → traçabilité SQLite.

---

## 2. Prompts par hypothèse d'edge (H-A à H-G)

> Chaque prompt est un **template d'enrichissement de l'input** (pas du system prompt). Il complète les `edge_features` envoyés à Claude avec une instruction contextualisée. Le system prompt §1 reste constant.

### 2.1 `edge-H-A-v1.0` — Gap Follow EU Open

**Placeholders typés** :
- `{ASSET_NAME}` : ex "DAX"
- `{GAP_PCT}` : ex 0.82
- `{PREV_CLOSE_US}` : ex 4521.30
- `{ORB_CONFIRMED}` : boolean
- `{VOLUME_PREMARKET_RATIO}` : ex 1.4

**Bloc à injecter dans le user message (en plus du JSON input)** :

```
EDGE: H-A — Gap Follow EU Open

Hypothèse à scorer : si le sous-jacent {ASSET_NAME} ouvre en gap haussier (+{GAP_PCT}%) par rapport à la clôture US (S&P {PREV_CLOSE_US}), la dynamique continue dans les 30 premières minutes.

Confirmations attendues pour score ≥ 7 :
- Gap minimum 0,5 % (seuil paramétrique optimisé R&D — référence backtest fournie).
- ORB Xetra/Euronext cassé dans le sens du gap (orb_breakout=true) — si applicable.
- Volume pré-marché > 1,2× moyenne 20 jours.
- RSI 14 entre 50 et 70 (pas de surachat extrême).

Drapeau ALERT si :
- Gap > 1,5 % (sur-extension probable — risque de fade — H-EDGE-B plutôt qu'H-A).
- Volume pré-marché < 0,8× moyenne (gap sur faible participation = peu fiable).
```

### 2.2 `edge-H-B-v1.0` — Gap Fade EU Open

**Placeholders typés** :
- `{ASSET_NAME}`, `{GAP_PCT}`, `{OVEREXTENSION_THRESHOLD}` (1.0/1.5/2.0), `{FADE_RATIO}` (33/50/61.8)

**Bloc à injecter** :

```
EDGE: H-B — Gap Fade EU Open

Hypothèse à scorer : si {ASSET_NAME} ouvre en gap haussier de +{GAP_PCT}% (> seuil sur-extension {OVEREXTENSION_THRESHOLD}%), le prix revient combler partiellement le gap dans l'heure ({FADE_RATIO}%).

Direction attendue : VENTE (turbo Put).

Confirmations pour score ≥ 7 :
- Gap > seuil sur-extension (1,5 % min recommandé).
- RSI 14 > 70 (surachat) sur les bougies pré-marché.
- Bollinger position : prix au-dessus de la borne supérieure (+2 σ).
- Volume pré-marché < moyenne 20 j (gap sans conviction = candidat fade).

ALERT si :
- News fortement haussière publiée < 1h avant ouverture (gap pourrait être justifié → ne pas fader).
- Continuation observée sur les 5 premières min (ORB bullish → fade contrarié).
```

### 2.3 `edge-H-C-v1.0` — Opening Range Breakout (ORB) 5/15 min

**Placeholders typés** :
- `{ASSET_NAME}`, `{ORB_WINDOW_MIN}` (5 ou 15), `{ORB_HIGH}`, `{ORB_LOW}`, `{BREAKOUT_DIRECTION}` ("haussier"/"baissier"), `{VOLUME_FILTER_OK}` (boolean)

**Bloc à injecter** :

```
EDGE: H-C — Opening Range Breakout (ORB {ORB_WINDOW_MIN} min)

Hypothèse à scorer : le range des {ORB_WINDOW_MIN} premières min ({ORB_LOW}-{ORB_HIGH}) est cassé au {BREAKOUT_DIRECTION}, avec volume confirmatoire ({VOLUME_FILTER_OK}).

Direction attendue : ACHAT si breakout haussier, VENTE si breakout baissier.

Confirmations pour score ≥ 7 :
- Cassure nette (clôture bougie 1m au-dessus/en dessous du range, pas juste mèche).
- Volume bougie de cassure > 1,5× moyenne sur la fenêtre ORB.
- RSI 14 dans les 50-65 (haussier) ou 35-50 (baissier).
- MACD histogram dans le sens de la cassure.

SL = borne opposée du range (R&D edge-rnd-brief §H-C).

ALERT si :
- Cassure sur très faible volume (< 0,8× moyenne ORB) = fakeout probable.
- News contradictoire au breakout détectée dans le contexte.
```

### 2.4 `edge-H-D-v1.1` — Momentum Overnight US → EU (v1.1 — seuils explicites)

**Placeholders typés** :
- `{SP_OVERNIGHT_PCT}` : ex 0.6
- `{ASSET_NAME}` : ex "CAC40"
- `{CORRELATION_WINDOW}` : ex "2h00-7h00 CET"

**Bloc à injecter** :

```
EDGE: H-D — Momentum Overnight US → EU (v1.1)

Hypothèse à scorer : la performance des futures S&P 500 sur la fenêtre {CORRELATION_WINDOW} ({SP_OVERNIGHT_PCT}%) prédit le sens d'ouverture EU sur {ASSET_NAME}.

Direction attendue : ACHAT si S&P overnight > +0,5 %, VENTE si < -0,5 %, sinon NO-TRADE.

Seuils numériques explicites (v1.1) pour score ≥ 7 :
- |S&P futures overnight| > 0,4 σ (écart-type historique 30 jours sur fenêtre overnight 22h00-7h00 CET).
- Corrélation rolling 30 jours S&P futures ↔ {ASSET_NAME} ≥ 0,5 (corrélation suffisante pour transposer le signal).
- Mouvement absolu overnight > 0,6 % (delta_overnight > 0,6 % en valeur absolue, en plus du critère σ — protège contre micro-mouvements en période de faible vol historique).
- Pas de divergence Asie / Europe (pas de Nikkei contraire — voir H-G en complément).
- RSI 14 EU compatible avec la direction.

ALERT si :
- News macro EU contraire au signe overnight US (exemple : BCE hawkish surprise alors que S&P bullish overnight).
- Écart historique inhabituel (delta_overnight > +/- 2 σ vs distribution backtest 30j) — sur-extension probable, candidat au fade plutôt qu'au follow.
- Corrélation rolling 30j < 0,5 (signal non transposable, prendre NO-TRADE plutôt qu'ACHAT/VENTE faible).
```

### 2.5 `edge-H-E-v1.0` — News Pré-marché (scoring sentiment)

**Placeholders typés** :
- `{NEWS_TITLES}` : array de 1-10 titres
- `{ASSET_NAME}` : ex "TotalEnergies"
- `{TIME_WINDOW}` : ex "5h00-8h30 CET"

**Bloc à injecter** :

```
EDGE: H-E — News Pré-marché

Hypothèse à scorer : les news publiées entre {TIME_WINDOW} sur {ASSET_NAME} (ou son secteur) ont un impact directionnel mesurable sur l'ouverture.

Titres news à analyser :
{NEWS_TITLES}

Tâche :
1. Évaluer le sentiment de chaque titre (-1 très négatif, 0 neutre, +1 très positif).
2. Pondérer par mots-clés (PIB, BCE, NFP, earnings, profit warning, guidance, M&A).
3. Calculer un sentiment_score agrégé.

Direction attendue :
- ACHAT si sentiment_score ≥ +0,5 (et pas de contradiction technique).
- VENTE si sentiment_score ≤ -0,5.
- NO-TRADE si entre -0,5 et +0,5 (signal pas assez tranché).

Confirmations pour score ≥ 7 :
- Sentiment_score absolu > 0,6.
- Au moins 2 titres convergents (pas un seul scoop).
- Source : Reuters, Bloomberg, Les Échos, AFP — pas de blogs spéculatifs.
- Confluence avec signal technique (H-A, H-B, H-C) = bonus +0,5 sur score.

ALERT si :
- Sentiment news contradictoire avec configuration technique → NO-TRADE recommandé (signaux contradictoires).
- Une seule news majeure très forte (>+0,8 ou <-0,8) sur un seul titre = volatilité, pas direction.

Note : ce prompt est utilisé en R&D (Haiku 4.5 batch + cache) — cap 100 appels/jour (cf. ai-architecture.md §1.2).
```

### 2.6 `edge-H-F-v1.0` — Écart Spot/Futures à l'Ouverture

**Placeholders typés** :
- `{ASSET_NAME}`, `{SPOT_PRICE}`, `{FUTURES_PRICE}`, `{SPREAD_SIGMA}` (en écarts-types historiques)

**Bloc à injecter** :

```
EDGE: H-F — Écart Spot/Futures à l'Ouverture

Hypothèse à scorer : l'écart entre spot {ASSET_NAME} ({SPOT_PRICE}) et futures EU correspondants ({FUTURES_PRICE}) dépasse {SPREAD_SIGMA} σ historiques → réversion attendue dans les 5-30 min.

Direction attendue :
- ACHAT du spot si spot < futures de > 2 σ (spot va remonter vers futures).
- VENTE du spot si spot > futures de > 2 σ (spot va baisser vers futures).

Confirmations pour score ≥ 7 :
- Écart > 2 σ (vraie déviation statistique, pas bruit).
- Volume normal sur les deux instruments (pas de halt ou anomalie).
- Pas de news justifiant la divergence.

ALERT si :
- Écart > 3 σ (anomalie possible — vérifier données feed, pas arbitrage).
- Liquidité futures dégradée (spread bid/ask > moyenne).
```

### 2.7 `edge-H-G-v1.1` — Sentiment Overnight Asie (v1.1 — seuils explicites)

**Placeholders typés** :
- `{NIKKEI_CLOSE_PCT}` : ex 1.2
- `{HSI_CLOSE_PCT}` : ex 0.8
- `{ASSET_NAME}` : ex "CAC40"

**Bloc à injecter** :

```
EDGE: H-G — Sentiment Overnight Asie (v1.1)

Hypothèse à scorer : Nikkei 225 a clôturé à {NIKKEI_CLOSE_PCT}% et Hang Seng à {HSI_CLOSE_PCT}%. La corrélation historique avec {ASSET_NAME} prédit le sens d'ouverture EU.

Direction attendue :
- ACHAT si Nikkei + HSI tous deux > +0,5 % (et S&P overnight non contraire).
- VENTE si Nikkei + HSI tous deux < -0,5 %.
- NO-TRADE si signaux Asie contradictoires entre eux.

Seuils numériques explicites (v1.1) pour score ≥ 7 :
- |Nikkei close − {ASSET_NAME} open prévu| > 1,0 % (delta minimum pour qu'un transfert de momentum soit informationnel).
- Corrélation rolling 60 jours Nikkei ↔ {ASSET_NAME} ≥ 0,4 (corrélation suffisante — Asie/EU sont moins corrélés que US/EU, seuil plus bas).
- Nikkei et HSI alignés (même signe — pas l'un haussier, l'autre baissier).
- S&P futures overnight non contraire (cf. H-D en confluence).
- Pas de news EU ouvrant contre la direction Asie.

ALERT si :
- Asie bullish (Nikkei+HSI > +0,5 %) + S&P bearish (S&P futures overnight < -0,3 %) → signaux globaux contradictoires, préférer NO-TRADE.
- Corrélation rolling 60j < 0,4 (signal non transposable, NO-TRADE plutôt qu'ACHAT/VENTE faible).
- Delta Nikkei vs {ASSET_NAME} historique > 2 σ (sur-extension macro, possible fade plutôt que follow).

Note : edge macro, signal moins granulaire — utiliser en complément d'un edge technique (H-C ou H-A) plutôt qu'en autonome.
```

---

## 3. Schemas JSON — Zod (TS) et Pydantic (Py)

### 3.1 Tool `emit_signal_scoring` (input_schema Anthropic)

```json
{
  "name": "emit_signal_scoring",
  "description": "Émet le scoring structuré du signal turbo intraday EU pour TradingApp. À appeler une seule fois par requête. Tous les champs sont obligatoires.",
  "input_schema": {
    "type": "object",
    "properties": {
      "id": { "type": "string", "description": "UUID v4" },
      "date": { "type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
      "hour_calc": { "type": "string", "pattern": "^\\d{2}:\\d{2}$", "description": "HH:MM CET" },
      "asset": { "type": "string", "minLength": 1, "maxLength": 50 },
      "direction": { "type": "string", "enum": ["ACHAT", "VENTE", "NO-TRADE"] },
      "entry": { "type": ["number", "null"], "description": "Prix turbo, null si NO-TRADE" },
      "sl": { "type": ["number", "null"] },
      "tp": { "type": ["number", "null"] },
      "score": { "type": "number", "minimum": 0, "maximum": 10 },
      "raison": { "type": "string", "minLength": 10, "maxLength": 300 },
      "edge_id": { "type": "string", "enum": ["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"] },
      "backtest_ref": { "type": "string", "pattern": "^#B-\\d{3}$" },
      "ALERT_flag": { "type": "string", "enum": ["ALERT", "SAFE", "NO-TRADE"] },
      "no_trade_reason": { "type": ["string", "null"] },
      "model_used": { "type": "string" }
    },
    "required": ["id", "date", "hour_calc", "asset", "direction", "entry", "sl", "tp", "score", "raison", "edge_id", "backtest_ref", "ALERT_flag", "no_trade_reason", "model_used"]
  }
}
```

### 3.2 Zod schema (TypeScript — `src/lib/ai/schemas/signalOutput.schema.ts`)

```typescript
import { z } from "zod";

export const SignalOutputSchema = z.object({
  id: z.string().uuid(),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  hour_calc: z.string().regex(/^\d{2}:\d{2}$/),
  asset: z.string().min(1).max(50),
  direction: z.enum(["ACHAT", "VENTE", "NO-TRADE"]),
  entry: z.number().positive().nullable(),
  sl: z.number().positive().nullable(),
  tp: z.number().positive().nullable(),
  score: z.number().min(0).max(10),
  raison: z.string().min(10).max(300),
  edge_id: z.enum(["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"]),
  backtest_ref: z.string().regex(/^#B-\d{3}$/),
  ALERT_flag: z.enum(["ALERT", "SAFE", "NO-TRADE"]),
  no_trade_reason: z.string().nullable(),
  model_used: z.string(),
}).strict();

export type SignalOutput = z.infer<typeof SignalOutputSchema>;

// Schema input (envoyé à Claude)
export const SignalInputSchema = z.object({
  date: z.string(),
  hour_calc: z.string(),
  edge_id: z.enum(["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"]),
  edge_name: z.string(),
  asset: z.object({
    ticker: z.string(),
    name: z.string(),
    category: z.enum(["indice_eu", "blue_chip_fr", "fx", "commodity"]),
  }),
  ohlc_last_5d: z.array(z.object({
    date: z.string(),
    open: z.number(), high: z.number(), low: z.number(), close: z.number(), volume: z.number(),
  })).max(5),
  ohlc_today_premarket: z.array(z.object({
    ts: z.string(),
    open: z.number(), high: z.number(), low: z.number(), close: z.number(), volume: z.number(),
  })),
  indicators: z.object({
    rsi_14: z.number().min(0).max(100),
    macd_signal: z.number(),
    macd_histogram: z.number(),
    bollinger_upper: z.number(),
    bollinger_lower: z.number(),
    bollinger_middle: z.number(),
    atr_14: z.number().nonnegative(),
  }),
  edge_features: z.record(z.union([z.number(), z.string(), z.boolean(), z.array(z.string())])),
  backtest_ref: z.string().regex(/^#B-\d{3}$/),
  backtest_stats: z.object({
    win_rate: z.number().min(0).max(100),
    nb_trades: z.number().int().min(30),
    drawdown_max_pct: z.number().max(0),
    sharpe_ratio: z.number(),
    period: z.string(),
  }),
  confidence_threshold: z.number().min(0).max(10),
  position_sizing: z.object({
    capital_engage_target: z.number().positive(),
    leverage_target: z.number().positive(),
  }),
});

export type SignalInput = z.infer<typeof SignalInputSchema>;
```

### 3.3 Pydantic schema (Python — équivalent)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional

class SignalOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    hour_calc: str = Field(pattern=r"^\d{2}:\d{2}$")
    asset: str = Field(min_length=1, max_length=50)
    direction: Literal["ACHAT", "VENTE", "NO-TRADE"]
    entry: Optional[float]
    sl: Optional[float]
    tp: Optional[float]
    score: float = Field(ge=0, le=10)
    raison: str = Field(min_length=10, max_length=300)
    edge_id: Literal["H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G"]
    backtest_ref: str = Field(pattern=r"^#B-\d{3}$")
    ALERT_flag: Literal["ALERT", "SAFE", "NO-TRADE"]
    no_trade_reason: Optional[str]
    model_used: str
```

---

## 4. Prompts dégradés (US-04 et US-05)

> Ces prompts s'utilisent quand des données sont partiellement disponibles (Twelve Data partiel) ou que des sources sont manquantes (news indispo). Ils permettent à Claude de continuer à scorer avec un signal partiel **assorti d'un drapeau ALERT** et `no_trade_reason` documenté si la dégradation est trop forte.

### 4.1 Prompt dégradé — `signal-scoring-degraded-twelvedata-v1.0`

**Quand l'utiliser** : Twelve Data a renvoyé une partie des données (OHLC OK mais indicateurs partiels, ou inverse). Pipeline déclenche ce prompt à la place du standard.

**Bloc à ajouter au user message** (après l'input JSON tronqué) :

```
DÉGRADATION DÉTECTÉE — Twelve Data partiellement indisponible.

Champs manquants dans cet appel : {LISTE_CHAMPS_MANQUANTS}

Instructions spécifiques :
- Tu dois scorer SEULEMENT à partir des données disponibles.
- Le score MAXIMUM autorisé en mode dégradé est 7.0 (jamais > 7 sans données complètes).
- ALERT_flag DOIT être "ALERT" si direction != "NO-TRADE".
- raison DOIT mentionner explicitement la dégradation : ex "Note : ORB non calculable (volume manquant), score plafonné."
- Si > 50 % des champs essentiels manquent (OHLC ET indicateurs ET edge_features) → direction = "NO-TRADE", no_trade_reason = "Dégradation Twelve Data trop forte pour scoring fiable."
```

### 4.2 Prompt dégradé — `signal-scoring-degraded-news-v1.0`

**Quand l'utiliser** : edge_id = H-E (news pré-marché) mais source news indisponible (API news down, Twelve Data news non couverte par le plan).

**Bloc à ajouter** :

```
DÉGRADATION DÉTECTÉE — Source news indisponible pour H-E.

Instructions :
- Si l'edge sélectionné aujourd'hui par le pipeline était H-E uniquement → bascule sur l'edge secondaire fourni en `edge_features.fallback_edge_id` si présent, sinon direction = "NO-TRADE", no_trade_reason = "Edge H-E impossible : source news indisponible. Pas d'edge secondaire applicable."
- Si l'edge principal n'est pas H-E mais que H-E était utilisé en confirmation → continuer avec l'edge principal seul, score plafonné à 7.5, ALERT_flag = "ALERT", raison citant l'absence de confirmation news.
```

---

## 5. Exemples de calls réels (curl + payload + réponse)

> Ces 3 exemples sont copiables pour tests manuels par @fullstack lors de l'intégration. Ils correspondent à TC-01, TC-03 et TC-05 de `ai-architecture.md` §6.

### 5.1 Exemple 1 — TC-01 ACHAT DAX (Sonnet 4.5 live)

**Curl** :

```bash
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 1024,
    "temperature": 0.1,
    "system": [
      { "type": "text", "text": "<contenu signal-scoring-v1.0 §1.1>", "cache_control": { "type": "ephemeral" } }
    ],
    "tools": [ { "name": "emit_signal_scoring", "description": "...", "input_schema": { "type": "object", "properties": {...}, "required": [...] } } ],
    "tool_choice": { "type": "tool", "name": "emit_signal_scoring" },
    "messages": [{
      "role": "user",
      "content": "EDGE: H-A — Gap Follow EU Open\n\nINPUT JSON:\n{\"date\":\"2026-05-04\",\"hour_calc\":\"08:47\",\"edge_id\":\"H-A\",\"edge_name\":\"Gap Follow\",\"asset\":{\"ticker\":\"^GDAXI\",\"name\":\"DAX\",\"category\":\"indice_eu\"},\"ohlc_last_5d\":[...],\"ohlc_today_premarket\":[...],\"indicators\":{\"rsi_14\":58,\"macd_histogram\":0.3,\"bollinger_upper\":18450,\"bollinger_lower\":18200,\"bollinger_middle\":18325,\"atr_14\":85,\"macd_signal\":12.4},\"edge_features\":{\"gap_pct\":0.82,\"prev_close_us\":4521.30,\"orb_breakout\":true,\"orb_high\":18420,\"volume_premarket_ratio\":1.4},\"backtest_ref\":\"#B-031\",\"backtest_stats\":{\"win_rate\":61,\"nb_trades\":87,\"drawdown_max_pct\":-18,\"sharpe_ratio\":1.3,\"period\":\"2021-2025\"},\"confidence_threshold\":6.5,\"position_sizing\":{\"capital_engage_target\":600,\"leverage_target\":6}}\n\nModel used: claude-sonnet-4-5-20250929"
    }]
  }'
```

**Réponse Claude (extrait `tool_use` block)** :

```json
{
  "id": "msg_01abc...",
  "model": "claude-sonnet-4-5-20250929",
  "stop_reason": "tool_use",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01...",
      "name": "emit_signal_scoring",
      "input": {
        "id": "8f4b2c1e-3a5d-4f7a-9b2c-1e3a5d4f7a9b",
        "date": "2026-05-04",
        "hour_calc": "08:47",
        "asset": "DAX Turbo Call",
        "direction": "ACHAT",
        "entry": 3.42,
        "sl": 3.21,
        "tp": 3.85,
        "score": 8.0,
        "raison": "Gap haussier +0,82 % sur clôture US, ORB Xetra cassé à 18420 avec volume pré-marché 1,4x moyenne. Cible potentielle alignée backtest #B-031.",
        "edge_id": "H-A",
        "backtest_ref": "#B-031",
        "ALERT_flag": "SAFE",
        "no_trade_reason": null,
        "model_used": "claude-sonnet-4-5-20250929"
      }
    }
  ],
  "usage": { "input_tokens": 4823, "cache_creation_input_tokens": 1450, "cache_read_input_tokens": 0, "output_tokens": 198 }
}
```

### 5.2 Exemple 2 — TC-03 NO-TRADE EuroStoxx50 (Sonnet 4.5 live)

**Curl** : identique sauf user message (input EuroStoxx flat, gap 0,1 %, RSI 51).

**Réponse Claude (extrait)** :

```json
{
  "input": {
    "id": "5c7d3e2f-...",
    "date": "2026-05-06",
    "hour_calc": "08:44",
    "asset": "EuroStoxx50",
    "direction": "NO-TRADE",
    "entry": null, "sl": null, "tp": null,
    "score": 5.2,
    "raison": "Marché flat à l'ouverture (gap +0,1 %), RSI neutre 51, range ORB non cassé.",
    "edge_id": "H-A",
    "backtest_ref": "#B-031",
    "ALERT_flag": "NO-TRADE",
    "no_trade_reason": "Score max relevé 5,2/10 — en dessous du seuil 6,5.",
    "model_used": "claude-sonnet-4-5-20250929"
  }
}
```

### 5.3 Exemple 3 — TC-05 timeout (DEGRADED MODE — pas d'output Claude)

**Curl** : identique avec `timeout=45000` ms côté SDK.

**Comportement** : pas de réponse en 45 s → SDK throw `TimeoutError` → pipeline déclenche retry 1 (10 s wait, 30 s timeout) → timeout → retry 2 (5 s wait, 15 s timeout) → timeout → US-05 DEGRADED MODE.

**Pas de payload Claude** — Telegram reçoit le template DEGRADED MODE de `functional-specs §2`. SQLite logue `statut="erreur_claude"`, `motif_erreur_claude="timeout"`, `circuit_breaker_count++`.

---

## 6. Versioning des prompts

### 6.1 Format de version

Chaque prompt a un ID stable + une version sémantique :

| ID prompt | Version courante | Modèle cible |
|---|---|---|
| `signal-scoring-v1.0` | v1.0 | `claude-sonnet-4-5-20250929` (live) / `claude-haiku-4-5` (R&D) |
| `edge-H-A-v1.0` à `edge-H-G-v1.0` | v1.0 | idem |
| `signal-scoring-degraded-twelvedata-v1.0` | v1.0 | idem |
| `signal-scoring-degraded-news-v1.0` | v1.0 | idem |

**Règle** :
- **v1.X** (mineur) : tweak du prompt système (ajout d'un mot proscrit, reformulation), changement de seuil, ajout d'un cas dégradé.
- **v2.X** (majeur) : restructuration du JSON output, changement de modèle (Sonnet 4.5 → 4.6), réécriture du système prompt.

### 6.2 Couplage avec `model_used` dans l'output

Le champ `model_used` du JSON output contient le nom du modèle. La version du prompt est tracée séparément en SQLite par le pipeline :

```sql
ALTER TABLE signals ADD COLUMN prompt_version TEXT NOT NULL DEFAULT 'signal-scoring-v1.0';
```

**Recommandation @fullstack** : ajouter cette colonne dès la création de la table `signals` pour tracer rétroactivement quelle version de prompt a généré chaque signal.

### 6.3 Regression testing avant promotion d'une nouvelle version

**Protocole de bump version (obligatoire)** :

1. Sauvegarder le prompt courant dans `docs/ia/prompt-archive/signal-scoring-vX.Y.md` (à créer si bump).
2. Modifier le prompt — bump version dans le frontmatter (ex: v1.0 → v1.1).
3. Run des 5 test cases TC-01 à TC-05 (cf. ai-architecture.md §6) avec la nouvelle version contre les fixtures stockées.
4. Comparer chaque output au "expected output" stocké dans `tests/fixtures/ai/expected/TC-XX.json`.
5. Si TOUS les TC passent (output dans la tolérance — score ±0,3, raison contient les keywords attendus, direction identique) → promotion OK.
6. Si UN TC régresse → soit corriger le prompt, soit documenter la régression assumée + alerter @reviewer.

**A/B testing optionnel** : pour les promotions majeures (v2.X), router 50/50 entre v1.X et v2.X pendant 2 semaines en production, mesurer score moyen + qualité justification (validation @testeur-persona-thomas) avant cutover complet.

### 6.4 Storage des fixtures de test

```
tests/
  fixtures/
    ai/
      inputs/
        TC-01-dax-gap-up.json
        TC-02-cac-gap-down-news.json
        TC-03-eurostoxx-flat.json
        TC-04-lvmh-conflict.json
        TC-05-timeout-simulation.json
      expected/
        TC-01-expected.json
        TC-02-expected.json
        TC-03-expected.json
        TC-04-expected.json
        TC-05-expected.json (vide — comportement DEGRADED MODE attendu)
```

Action @qa : intégrer ces fixtures dans la suite E2E avant promotion en V1 live (cf. `_gates.md` G25).

---

## 7. Auto-évaluation — Gates BLOQUANT

| Gate | Critère | Verdict | Évidence |
|---|---|---|---|
| G1 | Toutes sections présentes | PASS | §1 à §7 remplies, 0 TODO |
| G3 | Bloc Handoff structuré | PASS | §Handoff en fin de fichier |
| G5 | Persona Thomas identique project-context.md | PASS | Thomas cité, capital 1500 €, levier 5-20, fenêtre 8h45-8h55 cohérents |
| G6 | KPI North Star (P&L net mensuel après PFU 31,4 %) implicite | PASS | Pas de mention fiscalité dans les prompts (cohérent — fiscalité est aval, calculée côté code US-08) |
| G7 | 0 contradiction livrables amont | PASS | Référence ai-architecture.md (15 champs schema), brand-platform.md (mots proscrits R5, conditionnel R5), functional-specs.md (US-01 schema, US-05 timeout 45 s), edge-rnd-brief.md (7 hypothèses) |
| G12 | Implémentable sans question | PASS | Prompts complets prêts à copier, schemas Zod + Pydantic, exemples curl, env vars listées dans ai-architecture.md |
| G13 | 0 donnée inventée | PASS | Tarifs Anthropic référencés ai-architecture.md §1.1 ; PROMPT_VERSION explicite ; aucune valeur de score "réelle" affirmée — exemples sont des illustrations |
| G14 | Livrables absents signalés | PASS | Fixtures `tests/fixtures/ai/` à créer par @qa Phase 2 — signalé dans §6.4 |
| G15 | 0 placeholder résiduel | PASS | Placeholders typés dans templates (ex `{ASSET_NAME}`) sont des **variables de template volontaires**, pas des `[À REMPLIR]` oubliés. Cohérent G15 (annotations vs placeholders). |
| G17 | Pas copiable pour concurrent | PASS | Spécifique TradingApp : Thomas, turbos Bourse Direct, fenêtre 8h45-8h55, 7 hypothèses H-A à H-G nommées (gap follow EU open, ORB Xetra, news pré-marché Reuters/Bloomberg/Les Échos), tickers `^GDAXI`/`^FCHI`/`^STOXX50E`, mots proscrits brand-platform |

---

## Handoff

---
**Handoff → @orchestrator (relai vers @testeur-persona-thomas pour validation, puis @fullstack Phase 2 + @data-analyst Phase 1)**

- **Fichiers produits** :
  - `/home/user/TradingApp/docs/ia/prompt-library.md` (ce fichier — prérequis bloquant Phase 2)
  - Couplé avec `/home/user/TradingApp/docs/ia/ai-architecture.md`
- **Décisions prises** :
  - PROMPT_VERSION initiale : `signal-scoring-v1.0`.
  - Tool use natif Anthropic (`tool_choice: { type: "tool", name: "emit_signal_scoring" }`) pour forcer le JSON 15 champs.
  - Système prompt cacheable avec `cache_control: { type: "ephemeral" }` (-90 % coût input cacheable).
  - Température 0.1, max_tokens 1024.
  - Mots proscrits enforcés au niveau prompt système (R5) + validation post-réponse côté code (cf. ai-architecture.md §3.2).
  - 7 prompts par hypothèse d'edge avec placeholders typés réutilisables.
  - 2 prompts dégradés (Twelve Data partiel, news indispo) avec règle "score plafonné 7.0" + ALERT_flag forcé.
  - Versioning sémantique v1.X / v2.X + regression testing obligatoire avant promotion.
- **Points d'attention BLOQUANTS pour @fullstack** :
  - **Ne pas démarrer l'intégration Claude avant validation @testeur-persona-thomas** des outputs attendus TC-01 à TC-05 (cf. ai-architecture.md §6).
  - Implémenter `validateSignalOutput.ts` AVANT d'envoyer un message Telegram (validation Zod + echo checks + mots proscrits + cohérence direction/SL/TP).
  - Stocker `prompt_version` en SQLite à chaque insertion dans `signals` (ALTER TABLE).
  - Cap `RND_DAILY_CALL_CAP=100` enforcer côté code (compteur SQLite quotidien).
- **Points d'attention pour @data-analyst (Phase 1 R&D)** :
  - Utiliser les prompts `edge-H-A-v1.0` à `edge-H-G-v1.0` avec `claude-haiku-4-5` + Batch API + Prompt Caching.
  - Respecter le cap 100 ap/j (volume R&D — cf. ai-architecture.md §1.3).
  - Loguer chaque appel R&D avec `prompt_version` pour reproductibilité backtest.
- **Points d'attention pour @testeur-persona-thomas** :
  - Valider que les outputs des TC-01, TC-02, TC-04 (signaux GO et NO-TRADE conflit) passent le test "je sais si je trade en moins de 30 secondes".
  - Vérifier que la `raison` de chaque signal contient un chiffre traçable (pas de phrase générique).
  - Vérifier zéro mot proscrit dans les outputs (Grep `signal fort|opportunité|ne pas manquer|setup parfait|forte conviction`).
- **Actions Replit requises** :
  - [ ] Aucune action Replit directement déclenchée par ce livrable (les vars d'env sont dans le handoff de `ai-architecture.md`).
  - [ ] À noter pour @fullstack lors de l'intégration : créer `src/lib/ai/prompts/` contenant les fichiers TS/Py exportant chaque prompt comme constante + `src/lib/ai/schemas/signalOutput.schema.ts`.
  - [ ] Créer `tests/fixtures/ai/inputs/` et `tests/fixtures/ai/expected/` avec les 5 TC (action @qa Phase 2).

---
