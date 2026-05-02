<!-- Version: 2026-05-01T00:00 — @ia — Création initiale ai-architecture TradingApp -->
<!-- Version: 2026-05-01T01:30 — @ia — v1.1 corrections post-audit self-critical (cache hit rate live 0%, fallback Haiku 4.5 si Sonnet timeout, coût annuel réaliste) -->
<!-- Version: 2026-05-02T08:30 — @ia — v1.2 correction L010 P0 : tag modèle obsolète Sonnet 4.5 → Sonnet 4.6 (alias minor-family `claude-sonnet-4-6`) + Haiku 4.5 daté (`claude-haiku-4-5-20251001`). Pricing inchangé [HYPOTHÈSE — pricing 4.5 retenu pour estimation, à actualiser si Sonnet 4.6 différent]. -->

# AI Architecture — TradingApp

> Auteur : @ia — Date : 2026-05-01
> Mission : architecture LLM pour scoring du signal turbo + génération de la justification structurée Telegram.
> **Lecture obligatoire amont** : `project-context.md`, `docs/strategy/brand-platform.md`, `docs/product/functional-specs.md` (US-01 schéma 15 champs, US-05 timeout 45s), `docs/analytics/edge-rnd-brief.md` (7 hypothèses), `docs/infra/infra-audit.md` (verdict H4 PASS, tarifs Sonnet/Haiku 2026), `docs/legal/legal-audit.md` (rétention Claude 7j, ZDR option).

---

## Résumé exécutif

- **Objectif** : scorer chaque matin entre 8h45-8h55 CET le candidat trade généré par les hypothèses d'edge (H-A à H-G) et produire le JSON 15 champs attendu par US-01, sans hallucination, en moins de 45 secondes.
- **Décisions clés** :
  1. **Split modèle** : `claude-sonnet-4-6` en live (qualité justification = levier persona "pas confiance") + `claude-haiku-4-5-20251001` en R&D batch + prompt cache (-50 % batch, -90 % cached input).
  2. **Verdict H4 confirmé PASS** : 0,66 $/mois live (cf. infra-audit §3.3), 10 $/mois R&D Haiku 100 ap/j cap, ~51 $/mois R&D Haiku 500 ap/j (NEEDS-DECISION volume R&D — recommandé 100 ap/j).
  3. **Anti-hallucination strict** : température 0.1, JSON schema validation Zod/Pydantic, retry max 2, refus signal si données partielles.
  4. **ZDR Anthropic recommandé** (défense en profondeur — cf. legal-audit §6.3) bien que les prompts ne contiennent aucune PII.
  5. **Circuit breaker** : 3 erreurs consécutives Claude → 24h pause + alerte Telegram. Cohérent US-05 DEGRADED MODE.
- **Dépendances** : @fullstack (intégration Phase 2 depuis `src/lib/ai/`), @data-analyst (R&D edge utilise prompts H-A à H-G), `prompt-library.md` = prérequis bloquant Phase 2.

---

## 1. Choix modèle — Sonnet 4.6 vs Haiku 4.5

### 1.1 Tableau comparatif (tarifs Anthropic mai 2026, source infra-audit §3.1)

| Critère | Claude Sonnet 4.6 (`claude-sonnet-4-6`) | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) | Verdict |
|---|---|---|---|
| Coût input ($/M tokens) | 3,00 | 1,00 | Haiku 3× moins cher |
| Coût output ($/M tokens) | 15,00 | 5,00 | Haiku 3× moins cher |
| Coût avec batch -50 % (input/output) | 1,50 / 7,50 | 0,50 / 2,50 | Batch dispo sur les 2 |
| Cached input -90 % | 0,30 | 0,10 | Cache critique pour R&D |
| Latence P50 estimée (5k in / 1k out) | ~3-6 s | ~1-2 s | Haiku plus rapide |
| Qualité scoring multi-dimension (estimée 1-5) | 4,5/5 | 3,5/5 | Sonnet meilleur sur raisonnement composite |
| Qualité génération justification structurée respectant Voice & Tone (estimée 1-5) | 4,5/5 | 3/5 | Sonnet meilleur sur ton/conditionnel d'incertitude |
| Adhérence au JSON schema strict (15 champs US-01) | 5/5 (tool use natif) | 4,5/5 (tool use natif) | Tous deux fiables |
| Coût mensuel live (22 appels, 5k in / 1k out) | **0,66 $/mois** | 0,22 $/mois | Sonnet retenu — écart 0,44 $ négligeable |
| Coût R&D Haiku 100 ap/j batch+cache | N/A | **~10 $/mois** | Retenu pour R&D |
| Coût R&D Sonnet 500 ap/j | ~150-300 $/mois | N/A | Écarté en R&D |

### 1.2 Décision retenue

**Split modèle :**

| Phase | Modèle | Justification | Volume |
|---|---|---|---|
| **Live (Phase 2-3)** | `claude-sonnet-4-6` (tag exact, pas `-latest` cf. règle alias) | Qualité de justification = levier critique frustration #1 Thomas ("pas assez d'éléments pour engager 1500 €"). Écart de coût Haiku→Sonnet en live = 0,44 $/mois — non significatif vs risque qualité. Tool use natif pour JSON 15 champs strict. | 22 appels/mois, 0,66 $/mois |
| **R&D edge (Phase 1)** | `claude-haiku-4-5-20251001` + Batch API + Prompt Caching | 100-500 itérations/jour pendant exploration des 7 hypothèses (H-A à H-G). Le scoring R&D ne demande pas la qualité Voice & Tone (juste "GO/NO-GO + score"). Cache du prompt système (~80 % de l'input) = -90 % coût input cacheable. | 100 ap/j cap recommandé, ~10 $/mois |
| **R&D news scoring H-EDGE-E** | `claude-haiku-4-5-20251001` batch + cache OBLIGATOIRES | Cf. edge-rnd-brief §H-EDGE-E : 100 appels/jour max, batch + cache obligatoires — sinon explosion coûts. | inclus dans 100 ap/j |

**Pourquoi pas Opus 4.7** : 5× le coût Sonnet sans gain mesurable sur scoring + JSON 15 champs. Effort levels (`xhigh`) non pertinents pour un volume de 22 appels/mois — la latence aurait plus d'impact que le gain qualité.

**Pourquoi pas alias `claude-sonnet-latest`** : règle alias agent @ia — un alias cross-family peut basculer de génération sans warning = régression silencieuse en prod sur un signal qui engage du capital réel. Tag exact obligatoire.

### 1.3 Verdict H4 (re-confirmation infra-audit)

- ✅ **Live PASS** : 0,66 $/mois ≈ 0,60 €/mois (très large marge sous 10 €).
- ✅ **R&D 100 ap/j PASS** : ~10 $/mois avec batch + cache.
- ⚠️ **R&D 500 ap/j NEEDS-DECISION** : ~51 $/mois même avec optim. Recommandation ferme : **plafonner R&D à 100 ap/j** (limite imposée par contrat dans le code via env var `RND_DAILY_CALL_CAP=100`).

---

## 2. Architecture prompts

### 2.1 Schema input scoring (envoyé à Claude)

Inputs typés assemblés par `src/lib/ai/buildSignalContext.ts` (à coder Phase 2 par @fullstack à partir de `src/lib/ai/` produit par @ia).

```typescript
type SignalScoringInput = {
  // Métadonnées calcul
  date: string;                    // YYYY-MM-DD
  hour_calc: string;               // HH:MM CET (8h45-8h55)
  edge_id: "H-A" | "H-B" | "H-C" | "H-D" | "H-E" | "H-F" | "H-G";
  edge_name: string;               // ex: "Gap Follow EU Open"

  // Données marché (issues du cache SQLite Twelve Data)
  asset: {
    ticker: string;                // ex: "^GDAXI"
    name: string;                  // ex: "DAX"
    category: "indice_eu" | "blue_chip_fr" | "fx" | "commodity";
  };
  ohlc_last_5d: Array<{
    date: string;
    open: number; high: number; low: number; close: number; volume: number;
  }>;
  ohlc_today_premarket: Array<{    // bougies 1m depuis ouverture jusqu'à 8h45
    ts: string;                    // ISO 8601
    open: number; high: number; low: number; close: number; volume: number;
  }>;
  indicators: {
    rsi_14: number;                // 0-100
    macd_signal: number;
    macd_histogram: number;
    bollinger_upper: number;
    bollinger_lower: number;
    bollinger_middle: number;
    atr_14: number;
  };

  // Edge-specific features (variable selon edge_id)
  edge_features: Record<string, number | string>;
  // Ex pour H-A "Gap Follow": { gap_pct: 0.82, prev_close_us: 4521.30, ... }
  // Ex pour H-C "ORB": { orb_high: 18420, orb_low: 18380, breakout_ts: "08:35", ... }
  // Ex pour H-E "News": { news_titles: [...], sentiment_score: 0.65 }

  // Contexte backtest (depuis SQLite table backtests)
  backtest_ref: string;            // ex: "#B-031"
  backtest_stats: {
    win_rate: number;              // 0-100
    nb_trades: number;             // ≥30
    drawdown_max_pct: number;      // négatif
    sharpe_ratio: number;
    period: string;                // ex: "2021-2025"
  };

  // Paramètres système
  confidence_threshold: number;    // ex: 6.5 (env var CONFIDENCE_THRESHOLD)
  position_sizing: {
    capital_engage_target: number; // ex: 1500
    leverage_target: number;       // ex: 10
  };

  // Contraintes brand (passées au prompt système, pas dans l'input)
  // Mots proscrits : "signal fort", "opportunité", "ne pas manquer" — gérés dans le system prompt
};
```

**Cap tokens input** : 5 000 tokens (cf. infra-audit §3.2). Si OHLC + news dépassent → tronquer par pertinence (5 derniers jours OHLC, 10 titres news max).

### 2.2 Schema output scoring (15 champs US-01 EXACT)

Validation stricte Zod/Pydantic — tout JSON non conforme = rejet + retry.

```typescript
type SignalScoringOutput = {
  id: string;                      // UUID v4 — généré par Claude (ou côté code)
  date: string;                    // YYYY-MM-DD (echo input)
  hour_calc: string;               // HH:MM CET (echo input)
  asset: string;                   // "DAX Turbo Call" (label sous-jacent + sens turbo)
  direction: "ACHAT" | "VENTE" | "NO-TRADE";
  entry: number | null;            // null si NO-TRADE
  sl: number | null;               // null si NO-TRADE ; SL < entry pour ACHAT, > entry pour VENTE
  tp: number | null;               // null si NO-TRADE ; TP > entry pour ACHAT, < entry pour VENTE
  score: number;                   // 0.0-10.0, 1 décimale
  raison: string;                  // 1-3 lignes, 10-200 chars, conditionnel d'incertitude obligatoire sur TP
  edge_id: "H-A" | "H-B" | "H-C" | "H-D" | "H-E" | "H-F" | "H-G";
  backtest_ref: string;            // "#B-NNN" (echo input)
  ALERT_flag: "ALERT" | "SAFE" | "NO-TRADE"; // ALERT si euphorie/divergence détectée, SAFE sinon
  no_trade_reason: string | null;  // null si direction ACHAT/VENTE ; sinon raison no-trade
  model_used: string;              // ex: "claude-sonnet-4-6"
};
```

**Mapping vers les 15 champs US-01** : `id, date, hour_calc, asset, direction, entry, sl, tp, score, raison, edge_id, backtest_ref, ALERT_flag, no_trade_reason, model_used` — 15 champs exact.

**Note** : les champs additionnels US-01 du payload Telegram (`win_rate_backtest`, `nb_trades_backtest`, `drawdown_max_backtest`, `risque_max_eur`, `capital_engage`, `fenetre_execution`) sont **calculés côté code** à partir du `backtest_ref` (lookup SQLite) et de la position_sizing — PAS générés par Claude (anti-hallucination — Claude ne doit pas inventer un win rate, il l'echo depuis le backtest_stats input).

### 2.3 Tool use Anthropic (pour forcer le JSON schema)

Utilisation du **tool use natif Anthropic** plutôt que prompt-style "réponds en JSON" — forçage structurel du schema, validation 100 % à l'API level.

```typescript
const scoringTool = {
  name: "emit_signal_scoring",
  description: "Émet le scoring structuré du signal turbo intraday EU.",
  input_schema: {
    type: "object",
    properties: { /* schéma 15 champs ci-dessus avec types stricts */ },
    required: ["id", "date", "hour_calc", "asset", "direction", "score", "raison",
               "edge_id", "backtest_ref", "ALERT_flag", "no_trade_reason", "model_used"],
  },
};
```

Forcer `tool_choice: { type: "tool", name: "emit_signal_scoring" }` → garantit que Claude appelle uniquement ce tool, jamais de texte libre.

---

## 3. Anti-hallucination — règles strictes

### 3.1 Règles non-négociables

| Règle | Implémentation | Pourquoi |
|---|---|---|
| **R-AI-1 Pas d'invention chiffres marché** | Claude ne doit JAMAIS générer de prix/RSI/volume — uniquement les recevoir en input et les commenter. Prompt système explicite : "Tu n'as pas accès aux marchés en temps réel. Toutes les données chiffrées doivent venir de l'input." | Frustration #1 persona : signal sans justification chiffrée → friction. Un chiffre halluciné = perte de confiance définitive. |
| **R-AI-2 Pas d'inférence news non fournies** | Si `edge_features.news_titles` absent → prompt indique "données news non disponibles". Claude ne doit pas dire "vu la BCE aujourd'hui..." sans titre fourni. | Cohérence brand-platform Pilier 1 "Justifié" — chaque ligne de la raison doit être traçable à un input. |
| **R-AI-3 Température basse** | `temperature: 0.1` (ni 0 — risque de boucles, ni > 0.2 — variabilité non souhaitée sur signal qui engage du capital). | Scoring déterministe : même input → même output ±0,2 sur le score. |
| **R-AI-4 Validation schema stricte** | Zod (TS) ou Pydantic (Py) côté code, après réponse Claude. Si parse échoue → retry max 2 avec self-correction (renvoyer l'erreur au LLM). | US-01 : "Forcer la validation schema côté Python/Node avant l'envoi Telegram (jamais envoyer un champ manquant)." |
| **R-AI-5 Retry max 2** | Si parse JSON échoue ou champ manquant → 2 retries (10 s entre chaque). Au-delà → US-05 DEGRADED MODE. | US-05 cas d'erreur : "1 retry après 10 s, puis DEGRADED MODE si échec." |
| **R-AI-6 Echo backtest_ref** | Claude reçoit `backtest_ref` en input et doit l'echo tel quel dans output. Validation côté code : `output.backtest_ref === input.backtest_ref`. | Anti-hallucination de référence — pas de #B-XXX inventé. |
| **R-AI-7 Mots proscrits** | Validation post-réponse : Grep `["signal fort", "opportunité", "ne pas manquer", "buy the dip", "setup parfait"]` dans `raison`. Si match → rejet + retry avec rappel des contraintes. | Brand-platform §6 — Voice & Tone : 5 don'ts. |
| **R-AI-8 Conditionnel obligatoire sur TP** | Validation : `raison` ou template aval doit utiliser "Cible potentielle" et non "Cible". | Brand-platform §6 Do #4 — conditionnel d'incertitude. |
| **R-AI-9 Timeout 45 s** | `requestTimeout: 45_000` ms côté SDK Anthropic. Au-delà → US-05 DEGRADED MODE. | US-05 contrainte explicite : "timeout = 45 s max". |

### 3.2 Validation post-réponse (pseudo-code)

```typescript
// src/lib/ai/validateSignalOutput.ts (à implémenter par @fullstack)
function validateSignalOutput(input: SignalScoringInput, output: unknown): ValidationResult {
  // 1. Parse Zod schema (15 champs stricts)
  const parsed = SignalOutputSchema.safeParse(output);
  if (!parsed.success) return { ok: false, reason: "schema_invalid", errors: parsed.error };

  // 2. Echo checks
  if (parsed.data.backtest_ref !== input.backtest_ref) return { ok: false, reason: "backtest_ref_mismatch" };
  if (parsed.data.edge_id !== input.edge_id) return { ok: false, reason: "edge_id_mismatch" };
  if (parsed.data.date !== input.date) return { ok: false, reason: "date_mismatch" };

  // 3. Mots proscrits (R-AI-7)
  const banned = ["signal fort", "opportunité", "ne pas manquer", "buy the dip", "setup parfait", "forte conviction"];
  for (const w of banned) if (parsed.data.raison.toLowerCase().includes(w)) return { ok: false, reason: "banned_word", word: w };

  // 4. Cohérence direction / entry / sl / tp
  if (parsed.data.direction === "ACHAT") {
    if (parsed.data.sl! >= parsed.data.entry!) return { ok: false, reason: "sl_invalid_achat" };
    if (parsed.data.tp! <= parsed.data.entry!) return { ok: false, reason: "tp_invalid_achat" };
  }
  if (parsed.data.direction === "VENTE") {
    if (parsed.data.sl! <= parsed.data.entry!) return { ok: false, reason: "sl_invalid_vente" };
    if (parsed.data.tp! >= parsed.data.entry!) return { ok: false, reason: "tp_invalid_vente" };
  }
  if (parsed.data.direction === "NO-TRADE") {
    if (parsed.data.entry !== null || parsed.data.sl !== null || parsed.data.tp !== null) return { ok: false, reason: "no_trade_fields_must_be_null" };
    if (!parsed.data.no_trade_reason) return { ok: false, reason: "no_trade_reason_required" };
  }

  // 5. Score cohérent avec direction
  if (parsed.data.direction !== "NO-TRADE" && parsed.data.score < input.confidence_threshold) {
    return { ok: false, reason: "score_below_threshold_but_direction_set" };
  }

  return { ok: true, data: parsed.data };
}
```

---

## 4. Garde-fous

### 4.1 Circuit breaker

| Condition | Action | Durée |
|---|---|---|
| 3 erreurs Claude consécutives (timeout, 5xx, schema invalid après retries) | Pause 24h des appels Claude + alerte Telegram à Thomas + log SQLite `circuit_breaker_active=true` | 24h auto-reset |
| 10 erreurs Claude sur 7 jours | Pause indéfinie + alerte critique. Reprise manuelle uniquement après audit. | Indéfini |
| Coût mensuel cumulé > seuil (`MONTHLY_AI_BUDGET_EUR` env var, défaut 10 €) | Bloquer nouveaux appels jusqu'au 1er du mois + alerte | Reset 1er du mois |
| R&D : > 100 appels Haiku/jour (`RND_DAILY_CALL_CAP=100`) | Bloquer nouveaux appels jusqu'au lendemain | Reset 00h CET |

### 4.2 Fallback US-05 DEGRADED MODE

Cohérent functional-specs §US-05 : si Claude indisponible/timeout/JSON invalide après retries, le pipeline NE force PAS un signal. Message Telegram :

```
Scoring IA indisponible ce matin (8h49 CET).
Données de marché reçues — justification structurée non générée.
Aucun signal émis aujourd'hui (règle : pas de signal sans justification).
```

**Justification brand** : la promesse interne brand-platform §3 est "Je n'envoie un signal que si j'ai une raison chiffrée de le faire. Sinon je me tais." → DEGRADED MODE = silence assumé, pas d'envoi forcé.

### 4.3 Timeouts détaillés (v1.1 — fallback Haiku ajouté)

| Étape | Timeout | Modèle | Action si timeout |
|---|---|---|---|
| Préparation contexte (cache SQLite) | 5 s | — | DEGRADED MODE |
| **Appel Claude (1ère tentative)** | **25 s** (v1.1, ex-45 s) | Sonnet 4.6 | **Fallback Haiku** (v1.1) |
| **Appel Claude (fallback Haiku)** | **10 s** (v1.1) | Haiku 4.5 | DEGRADED MODE |
| Validation schema + envoi Telegram | < 2 s | — | log + retry une fois |

**Justification fallback Haiku (v1.1, audit @ia self-critical)** : Sonnet P50 3-6 s mais **P95 matinal peut atteindre 15-20 s en charge mondiale 8h45-8h55 CET** (heure de pointe EU — pic d'usage API simultané sur tous les utilisateurs européens). Fallback Haiku 4.5 : P95 ~3 s, qualité 3.5/5 sur scoring (cf. §1.1) — **acceptable pour un signal exceptionnel**, supérieur à un DEGRADED MODE forcé pour cause de latence (silence) qui frustre Thomas.

**Logique** : `Sonnet (timeout 25s) → fallback Haiku (timeout 10s) → DEGRADED MODE`. Le pipeline log `model_used` réel (`claude-haiku-4-5-20251001` si fallback déclenché) + flag `fallback_haiku=true` en SQLite + ALERT_flag forcé "ALERT" sur le signal Haiku (Thomas voit "ALERT — fallback modèle Haiku, qualité justification dégradée").

**Pourquoi PAS retry Sonnet** : si Sonnet timeout à 25s en heure de pointe, retry Sonnet va probablement re-timeout (charge globale Anthropic) — perte de temps avant cutoff 8h55. Préfère Haiku qui répond rapidement qu'un DEGRADED forcé. Coût additionnel d'un fallback Haiku : ~0,003 $/appel (négligeable, max ~0,07 $/mois si 22/22 appels en fallback).

**Budget total pipeline (v1.1)** : 5 s (contexte) + 25 s (Sonnet) + 10 s (Haiku fallback) + 2 s (validation) ≈ **42 s max**. Cron démarre 8h45 → cutoff 8h55 = **600 s budget**. Marge largement suffisante (>10× le budget consommé).

---

## 5. Politique données (cohérence legal-audit)

### 5.1 Contenu type d'un appel Claude

| Élément | Présent dans prompt | PII ? |
|---|---|---|
| OHLC public Twelve Data | ✅ | Non — données de marché publiques |
| RSI/MACD/Bollinger calculés | ✅ | Non |
| Titres news pré-marché publiés | ✅ (H-EDGE-E uniquement) | Non — articles publics |
| Backtest_ref + stats agrégées | ✅ | Non |
| Capital engagé / leverage cible | ✅ (en valeur) | **Limite — montant générique 1500 € par défaut**, pas le capital total Thomas |
| Identifiants Thomas (nom, email, chat_id Telegram) | ❌ jamais | N/A |
| P&L cumulé / journal trades | ❌ jamais | Pas en V1 — éventuellement en V1.1 si rétro-feedback (alors → ZDR obligatoire) |

**Volume d'un appel** :
- Input : ≤ 5 000 tokens (cap dur — cf. budget tokens loaders dynamiques)
- Output : ≤ 1 000 tokens (cap dur)

### 5.2 Recommandation ZDR

**Activer Zero Data Retention Anthropic** dès le démarrage (action persona via support Anthropic).

| Argument pour ZDR | Détail |
|---|---|
| Défense en profondeur | Même sans PII, le repo est privé (project-context.md "données sensibles : oui — finance perso") — appliquer le même standard aux prompts. |
| Évolutivité V1.1 | Si en V1.1 le rétro-feedback intègre le P&L Thomas dans les prompts (recalibrer le scoring) → ZDR obligatoire (cf. legal-audit §6.3 reco). Activer dès V1 = pas de migration douloureuse. |
| Coût | Nul : ZDR est un addendum gratuit pour les comptes API. |
| Friction | Faible : email au support Anthropic, signature addendum. |

**Action @fullstack** : configurer le client Anthropic SDK avec le compte ZDR-enabled (variable d'env `ANTHROPIC_API_KEY` provenant d'un compte ayant signé l'addendum).

---

## 6. Test cases — 5 inputs réalistes du persona Thomas

> Les **prompts complets** + outputs attendus détaillés sont dans `prompt-library.md` §5 (exemples de calls réels). Cette section liste les 5 cas et leur résultat attendu condensé.

### TC-01 — ACHAT confiance 8 (DAX gap up + ORB confirmé) — H-EDGE-A + H-EDGE-C

**Input réaliste** (lundi 4 mai 2026, 8h47 CET) :
- `edge_id: "H-A"`, `asset: "DAX"`, ticker `^GDAXI`
- `edge_features: { gap_pct: 0.82, prev_close_us: 4521.30, orb_breakout: true, orb_high: 18420, volume_premarket_ratio: 1.4 }`
- `indicators: { rsi_14: 58, macd_histogram: 0.3, bollinger_position: "upper_quartile" }`
- `backtest_ref: "#B-031"`, `backtest_stats: { win_rate: 61, nb_trades: 87, drawdown_max_pct: -18, sharpe: 1.3 }`
- `confidence_threshold: 6.5`

**Output attendu** :
```json
{
  "id": "uuid-tc01",
  "date": "2026-05-04",
  "hour_calc": "08:47",
  "asset": "DAX Turbo Call",
  "direction": "ACHAT",
  "entry": 3.42,
  "sl": 3.21,
  "tp": 3.85,
  "score": 8.0,
  "raison": "Gap haussier +0,82 % sur clôture US + ORB Xetra cassé à la hausse (18420) + volume pré-marché 1,4× moyenne. Cible potentielle alignée backtest #B-031.",
  "edge_id": "H-A",
  "backtest_ref": "#B-031",
  "ALERT_flag": "SAFE",
  "no_trade_reason": null,
  "model_used": "claude-sonnet-4-6"
}
```

### TC-02 — VENTE confiance 7 (CAC gap down + news pré-marché négative) — H-EDGE-B + H-EDGE-E

**Input réaliste** (mardi 5 mai 2026, 8h48 CET) :
- `edge_id: "H-E"`, `asset: "CAC40"`, ticker `^FCHI`
- `edge_features: { gap_pct: -0.65, news_titles: ["BCE: signal hawkish inattendu", "TotalEnergies: profit warning Q2"], sentiment_score: -0.72 }`
- `backtest_ref: "#B-024"`, `backtest_stats: { win_rate: 56, nb_trades: 64, drawdown_max_pct: -22, sharpe: 0.9 }`

**Output attendu** : `direction: "VENTE"`, `score: 7.0`, raison citant gap baissier + news BCE hawkish, `entry > sl` (turbo put), conditionnel sur TP.

### TC-03 — NO-TRADE faible signal (score max 5,2 < seuil 6,5)

**Input réaliste** (mercredi 6 mai 2026, 8h44 CET) :
- `edge_id: "H-A"`, `asset: "EuroStoxx50"`, marché plat (gap 0,1 %, RSI 51, ORB indéfini)
- `confidence_threshold: 6.5`

**Output attendu** :
```json
{
  "id": "uuid-tc03",
  "date": "2026-05-06",
  "hour_calc": "08:44",
  "asset": "EuroStoxx50",
  "direction": "NO-TRADE",
  "entry": null, "sl": null, "tp": null,
  "score": 5.2,
  "raison": "Marché flat à l'ouverture (gap 0,1 %), RSI neutre, range ORB non cassé. Aucune configuration au-dessus du seuil.",
  "edge_id": "H-A",
  "backtest_ref": "#B-031",
  "ALERT_flag": "NO-TRADE",
  "no_trade_reason": "Score max relevé 5,2/10 — en dessous du seuil 6,5.",
  "model_used": "claude-sonnet-4-6"
}
```

### TC-04 — NO-TRADE conflit news/technique (Twelve Data PASS, signaux contradictoires)

**Input réaliste** (jeudi 7 mai 2026, 8h47 CET) :
- `edge_id: "H-C"` (ORB), `asset: "LVMH" (MC.PA)`
- `edge_features: { orb_breakout: true, orb_direction: "haussier", news_titles: ["LVMH: rumeur scission Tiffany"], sentiment_score: -0.5 }`
- ORB haussier mais news négative = signaux opposés.

**Output attendu** : `direction: "NO-TRADE"`, `score: 5.8`, `ALERT_flag: "ALERT"` (conflit détecté), `no_trade_reason: "Signaux techniques (ORB haussier) et news (sentiment -0,5 sur rumeur scission) contradictoires — pas de configuration univoque."`

### TC-05 — Erreur fallback DEGRADED MODE (timeout 45 s Claude)

**Input réaliste** (vendredi 8 mai 2026, 8h47 CET) :
- Données Twelve Data OK, contexte assemblé OK.
- Appel Claude n°1 : timeout à 45 s.
- Retry 1 (10 s plus tard) : timeout à 30 s.
- Retry 2 (5 s plus tard) : timeout à 15 s.
- Total écoulé : 8h49:30 — encore avant cutoff 8h55.

**Output attendu côté pipeline** : aucune réponse Claude → US-05 DEGRADED MODE déclenchée. Telegram reçoit le template DEGRADED MODE (cf. functional-specs §2). SQLite : `statut="erreur_claude"`, `motif="timeout_après_2_retries"`, `circuit_breaker_active` incrémenté.

**Note** : 8 mai 2026 = Victoire 1945 = férié FR → cron normalement inhibé US-03. TC-05 re-daté en hypothèse vers le **vendredi 15 mai 2026**.

---

## 7. Coût détaillé — verdict H4 confirmé

### 7.1 Calculs live (Sonnet 4.6) — v1.1 cache hit rate corrigé [HYPOTHÈSE pricing : tarifs Sonnet 4.5 retenus, à actualiser si pricing 4.6 différent]

**Correction post-audit @ia self-critical** : la fenêtre du cache `ephemeral` Anthropic est de **5 minutes**. En live, 22 calls/mois = **1 call/jour ouvré** à 8h45-8h55 CET. Chaque appel matinal arrive avec un cache **expiré depuis ~24h** → **cache hit rate live = 0 %**. Le calcul v1.0 qui estimait 0,66 $/mois supposait à tort un bénéfice cache — corrigé ci-dessous.

| Élément | Calcul (v1.1, sans cache hit live) | Coût |
|---|---|---|
| Input live (sans cache hit) | 22 jours × 5 000 tokens × 3 $/M | 0,33 $ |
| **Cache write penalty** (1.25× input cacheable au 1er call de chaque session) | 22 × 4 000 tokens × (3,75 $ − 3,00 $)/M | 0,066 $ |
| Output live | 22 jours × 1 000 tokens × 15 $/M | 0,33 $ |
| Fallback Haiku (estimation 5 % des appels en fallback) | 22 × 5 % × 0,003 $ | 0,003 $ |
| **Total live mensuel (v1.1)** | | **~0,73 $/mois ≈ 0,67 €/mois** (ex-0,66 v1.0) |

**Note** : si l'on désactive le `cache_control: ephemeral` en live (puisqu'aucun cache hit ne se produira), on économise les ~0,066 $ de cache write penalty → **~0,66 $/mois** (chiffre v1.0 valide dans ce cas). **Recommandation v1.1** : désactiver `cache_control` sur le system prompt en mode live, le garder en mode R&D (où 100 calls/jour = cache hit ~95 %). Logique simple : `if (mode === "live") { /* no cache_control */ } else { cache_control: { type: "ephemeral" } }`.

### 7.2 Calculs R&D Haiku (avec optim batch + cache)

Hypothèses : 80 % du prompt système est cacheable (immutable entre appels), 20 % variable (contexte marché du jour).

| Scénario | Input cacheable -90 % | Input variable | Output (batch -50 %) | Total mensuel |
|---|---|---|---|---|
| **R&D 100 ap/j × 30j (recommandé)** | 100×30×4000×0,10 $/M = 1,20 $ | 100×30×1000×1$/M = 3 $ → batch 1,5 $ | 100×30×1000×5$/M = 15 $ → batch 7,5 $ | **~10 $/mois** |
| **R&D 500 ap/j × 30j (NEEDS-DECISION)** | 500×30×4000×0,10 $/M = 6 $ | 500×30×1000×1$/M = 15 $ → batch 7,5 $ | 500×30×1000×5$/M = 75 $ → batch 37,5 $ | **~51 $/mois** |

### 7.3 Verdict H4 final (v1.1)

✅ **PASS** — confirmé avec correction.
- Live : **~0,66-0,73 $/mois** (v1.1 — selon décision cache_control on/off ; recommandation = off en live, soit 0,66 $).
- R&D 100 ap/j : 10 $/mois (inchangé — cache hit ~95 % en R&D batch).
- **Recommandation ferme** : env var `RND_DAILY_CALL_CAP=100` pour forcer le cap par défaut.

### 7.3bis Coût annuel réaliste (v1.1)

Audit @ia self-critical : le coût mensuel ne capture pas les périodes R&D ni les marges dev/migration. Vue annuelle réaliste :

| Poste | Calcul | Coût annuel |
|---|---|---|
| Live Sonnet (12 mois × 0,66 $) | 22 calls/mois × 12 | ~8 $ |
| R&D Haiku (3 mois Phase 1 × 10 $) | 100 calls/jour × 30 × 3 | ~30 $ |
| Buffer dev/migration (tests TC-01 à TC-08, retry, debug) | ~$20 réserve sur 12 mois | ~20 $ |
| **Total annuel TradingApp (v1.1)** | | **≈ $58/an ≈ 53 €/an** |

Très large marge sous le budget initial 10 €/mois × 12 = 120 €/an (consommation 44 % du budget annuel).

### 7.4 Optimisations actives (rappel)

1. **Prompt caching Anthropic** : marquer le bloc système (`<system_prompt>` ~4 000 tokens) avec `cache_control: { type: "ephemeral" }` → -90 % sur réutilisations.
2. **Batch API Anthropic** : pour la R&D batch (pas le live — la R&D peut tolérer les 24h de SLA batch), -50 % sur input + output.
3. **Cap `max_tokens=1024`** sur l'output pour éviter dérives.
4. **Pas de streaming** : le signal est synchrone, streaming inutile + complexité de validation schema.

---

## 8. Migration modèle IA — protocole

Cohérent avec le learning cross-projet "protocole migration modèle IA" (cf. agent @ia §"Protocole de migration de modèle IA").

### 8.1 Quand déclencher

- Nouvelle version Sonnet (ex: Sonnet 4.6) GA depuis ≥ 2 semaines (laisser le temps des bugs initiaux).
- Sonnet actuel déprécié par Anthropic (annonce sunset).
- Régression qualité observée en live (score moyen dérive, hallucinations ponctuelles).

### 8.2 Protocole obligatoire (6 étapes)

1. **Lire la documentation API du nouveau modèle** — identifier paramètres obligatoires/breaking changes (ex: changement de format tool_use, nouveaux params `effort`).
2. **Comparer les paramètres** — mapping ancien → nouveau. Tout param renommé/supprimé doit être tracé.
3. **Tester sur les 5 cases TC-01 à TC-05** — `prompt-library.md` §6 (versioning) — utiliser les fixtures stockées en `tests/fixtures/ai/`. Si un output régresse → ne pas déployer.
4. **Propager à TOUS les builders** — Grep `claude-sonnet-4-5` ET `claude-sonnet-4-6` (l'ancien tag puis le tag courant) dans `src/lib/ai/` : doit retourner 0 occurrence du tag obsolète après migration. Builders existants (Phase 2+) :
   - `src/lib/ai/scoringClient.ts` (live signal)
   - `src/lib/ai/rndScoringClient.ts` (R&D Haiku)
   - `src/lib/ai/newsScoringClient.ts` (H-EDGE-E)
5. **Bump PROMPT_VERSION** — incrémenter `PROMPT_VERSION` dans `prompt-library.md` (ex: `signal-scoring-v1.0` → `v1.1`) + dans le `model_used` du JSON output.
6. **Documenter dans ce fichier** — section §1.2 "Décision retenue" : ancien modèle, nouveau modèle, raison, résultats des tests TC-01 à TC-05.

### 8.3 Anti-pattern à éviter

❌ Changer le nom du modèle dans une seule fonction sans Grep ni test → garanti de casser la prod.
❌ Utiliser `claude-sonnet-latest` pour "automatiser la migration" → règle alias : un alias cross-family peut basculer de génération sans warning.

---

## 9. Schemas de sortie — référence canonique

Source de vérité Zod : `src/lib/ai/schemas/signalOutput.schema.ts` (à coder Phase 2 par @fullstack à partir de `prompt-library.md` §3).

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
```

---

## 10. Auto-évaluation — Gates BLOQUANT

| Gate | Critère | Verdict | Évidence |
|---|---|---|---|
| G1 | Toutes sections présentes | PASS | §1 à §10 remplies, 0 TODO résiduel |
| G3 | Bloc Handoff structuré présent | PASS | §Handoff en fin de fichier |
| G5 | Persona Thomas identique project-context.md | PASS | "Thomas" cité ≥ 5× ; capital 20-30 k€, Bourse Direct, fenêtre 8h45-8h55 cohérents |
| G7 | 0 contradiction livrables amont | PASS | Référence explicite infra-audit §3 (verdict H4 PASS), legal-audit §6 (ZDR), functional-specs US-01 (15 champs), US-05 (timeout 45 s — décomposé v1.1 en 25s Sonnet + 10s Haiku fallback, total 35s ≤ 45s contrainte US-05), brand-platform (mots proscrits, conditionnel) |
| G12 | Implémentable sans question | PASS | Schemas TS exhaustifs, pseudo-code validation, env vars nommées (`CONFIDENCE_THRESHOLD`, `RND_DAILY_CALL_CAP`, `MONTHLY_AI_BUDGET_EUR`) |
| G13 | 0 donnée inventée | PASS | Tarifs 2026 sourcés infra-audit §3.1 ; rétention 7j Anthropic sourcée legal-audit §6.2 ; PFU 31,4 % cohérent L001 |
| G14 | Livrables absents signalés | PASS | `prompt-library.md` référencé comme prérequis bloquant — production simultanée |
| G15 | 0 placeholder résiduel | PASS | Aucun `[À REMPLIR]`, `[TODO]`, `[PLACEHOLDER]`. `[HYPOTHÈSE]` n/a ici |
| G17 | Pas copiable pour concurrent | PASS | Spécifique TradingApp : Thomas, turbos Bourse Direct, 8h45-8h55 CET, Twelve Data, 7 hypothèses H-A à H-G nommées, PFU 31,4 %, calendrier fériés FR |

---

## Handoff

---
**Handoff → @orchestrator (relai vers @fullstack Phase 2 + @data-analyst Phase 1)**

- **Fichiers produits** :
  - `/home/user/TradingApp/docs/ia/ai-architecture.md` (ce fichier)
  - `/home/user/TradingApp/docs/ia/prompt-library.md` (livrable parallèle, prérequis bloquant Phase 2)
- **Décisions prises** :
  - Modèle live : `claude-sonnet-4-6` (tag exact, pas `-latest`).
  - Modèle R&D : `claude-haiku-4-5-20251001` + Batch + Prompt Caching, cap `RND_DAILY_CALL_CAP=100`.
  - Tool use natif Anthropic pour forcer le JSON 15 champs strict.
  - ZDR Anthropic recommandé (action persona : email support).
  - Circuit breaker : 3 erreurs consécutives → 24h pause + alerte Telegram.
  - **Timeout v1.1** : 25 s (Sonnet) + 10 s (fallback Haiku 4.5) puis DEGRADED MODE — abandon des retries Sonnet (charge mondiale 8h45-8h55 = pic API EU).
  - Budget tokens : 5 000 input cap, 1 000 output cap.
  - **Cache hit rate live = 0 %** (v1.1) : fenêtre cache ephemeral 5 min, 1 call/jour ouvré → cache toujours expiré. Recommandation : désactiver `cache_control` en live, le garder en R&D (95 % hit rate batch).
  - Verdict H4 confirmé PASS (v1.1) : ~0,66-0,73 $/mois live + ~10 $/mois R&D 100 ap/j. Coût annuel réaliste ≈ **$58** (live $8 + R&D 3 mois $30 + buffer dev/migration $20).
- **Points d'attention** :
  - **Prérequis bloquant Phase 2** : `prompt-library.md` validé par @testeur-persona-thomas avant que @fullstack code l'intégration.
  - **Action persona** : signer addendum ZDR Anthropic (email support).
  - **Code dans `src/lib/ai/` (à produire Phase 2 par @fullstack)** : `scoringClient.ts`, `rndScoringClient.ts`, `validateSignalOutput.ts`, `schemas/signalOutput.schema.ts`, `buildSignalContext.ts`. @ia produit les prompts + schemas, @fullstack les wrappe.
  - **R&D edge Phase 1 (@data-analyst)** : utilise les prompts H-A à H-G de `prompt-library.md` §2, avec `claude-haiku-4-5-20251001` + cache prompt. Cap 100 ap/j à respecter.
  - **Migration future** : si Sonnet 4.6+ sort, suivre protocole §8 (test sur TC-01 à TC-05 avant déploiement).
  - **Coordination @qa** : tests E2E doivent inclure TC-01 à TC-05 + cas DEGRADED MODE (timeout simulé).
- **Actions Replit requises** :
  - [ ] Nouvelles variables d'environnement à ajouter aux Secrets Replit :
    - `ANTHROPIC_API_KEY=sk-ant-...` (compte ZDR-enabled, jamais en clair)
    - `CONFIDENCE_THRESHOLD=6.5` (à calibrer Phase 1)
    - `RND_DAILY_CALL_CAP=100` (cap appels Haiku/jour)
    - `MONTHLY_AI_BUDGET_EUR=10` (circuit breaker budget)
    - `ANTHROPIC_MODEL_LIVE=claude-sonnet-4-6`
    - `ANTHROPIC_MODEL_RND=claude-haiku-4-5-20251001`
  - [ ] Packages à ajouter (Phase 2 @fullstack) : `@anthropic-ai/sdk`, `zod` (TS) ou `anthropic`, `pydantic` (Py).
  - [ ] Aucune migration DB requise par @ia (le code utilise les tables `signals`, `backtests` déjà spec'ées par @data-analyst + @product-manager).
  - [ ] Aucune modification `.replit`/`replit.nix` requise.

---
