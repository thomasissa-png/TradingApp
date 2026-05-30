# Reco IA — TradingApp v3 (extraction news)

## TL;DR (verdict)

**GARDER l'extraction LLM, mais la SIMPLIFIER.** Modèle = **DeepSeek `deepseek-chat`** (déjà en place, imbattable sur ce ratio). Pas d'Anthropic/Gemini ici : 5-10x plus cher pour zéro gain mesurable sur cette tâche d'étiquetage court.
Coût actuel ~6 €/mois → **cible 2-3 €/mois** avec 3 optimisations triviales (prompt caching DeepSeek + pré-filtre durci + batching titres). Garde-fou coût dur à 15 €/mois (alerte) / 25 € (kill switch).

---

## 1. Garder, simplifier ou couper ?

### La vraie question : valeur du JSON structuré vs matching mots-clés ?

Le scoring Analyste lit `criteres-courants`, pas `events-log` directement. Le LLM remplit `events-log` pour :
- **L1/L2 + news_zone** → routage vers le bon critère/actif (ex : "Iran-Moyen-Orient" → critère "tensions géopolitiques Brent")
- **cours (ticker)** → désambiguïsation actif (un mot-clé "oil" ne dit pas Brent vs WTI vs majors)
- **confirmed_event + consequence chiffrée** → distinguer fait/rumeur (poids ≠ dans le scoring)
- **latence/durée** → fenêtre d'imputation horizon (24h vs 1m)

Un `triggers-and-windows.yml` mots-clés peut produire L1+zone mais **rate 100 % des points 2-4**. Sur 5000 events/mois, la qualité du `criteres-courants` quotidien dépend de cette désambiguïsation. **Couper = casser l'Analyste**, parce qu'on ne sait plus si "Brent" ou "Apple earnings" alimente la même cellule.

**Verdict : GARDER.** ROI = (~30 min/jour d'étiquetage manuel évité × 50 €/h) / 6 €/mois = **~125x**. Largement au-dessus du seuil 3.

### Ce qu'on simplifie

- **Supprimer du schéma** : `fin` (toujours vide en pratique, post-hoc), `duree` (recalculable depuis `latence` + L1), `consequence` (chiffrage rare dans titre+snippet — redondant avec Twelve Data). → schéma de 11 → **8 champs**. -25 % tokens output.
- **Supprimer `confirmed_event`** : règle déterministe possible (verbes "reports/jumps/cuts" vs "may/could/rumored") — fait côté Python, pas côté LLM.
- Schéma final : `L1, L2, trigger, cours, latence, news_zone, news_category` (7 champs).

---

## 2. Optimisations concrètes (chiffrées)

### A. Prompt caching DeepSeek (gratuit, gain immédiat)
DeepSeek facture les **cache hits à 0,014 $/M** input (vs 0,14 $ — **90 % off**). Le system prompt (~400 tokens, identique sur tous les appels) est éligible. Sur 5000 appels/mois × 400 tokens = 2M tokens input cachés → **0,28 $ → 0,028 $**. Économie : **~0,25 $/mois (~0,23 €)**. Activation : `cache_control` sur le system prompt (SDK OpenAI-compat le supporte côté DeepSeek via le header automatique — pas de code à changer, c'est implicite côté DeepSeek depuis 2024).

### B. Pré-filtre durci (gros gain)
Actuel : `is_finance_relevant` = OR sur ~120 regex → filtre ~70 %. Trop laxe : "stock" matche les stocks de marchandises ; "rate" matche tout. **Ajouter 2 couches** :
1. **Blacklist forte** (regex OR sur `\b(royal|celebrity|football|recipe|horoscope|fashion|kardashian|...)\b`) → kill avant whitelist.
2. **Source weighting** : Reddit/blogs → seuil de 2 keywords requis. Reuters/Bloomberg/FT → 1 keyword suffit.
Cible : **filtrer 85-90 %** (vs 70 %) → 5000 → **~3000 appels/mois**. Économie : -40 % du coût LLM = **~2,4 €/mois**.

### C. Batching titres (gain modéré, complexité +1)
Un appel = 1 titre actuellement. Batch de 5 titres dans un seul prompt → JSON array → divise par 5 le coût du system prompt (non caché en fallback) ET la latence d'overhead. Gain : ~30 % sur tokens input non cachés. **Mais** : si caching activé (A), gain ≈ 0. **Skip B + C, garder seulement A + B suffit.**

### D. Modèle : `deepseek-chat` vs `deepseek-reasoner`
- `deepseek-chat` (V3.1) : 0,14/0,28 $/M, latence ~1-2s, mode JSON natif. **Retenu.**
- `deepseek-reasoner` (R1) : 0,55/2,19 $/M, latence 5-15s (chain-of-thought). Surdimensionné pour de l'étiquetage de titre court. **Écarté.**

### E. Alternatives multi-provider (tranche)

| Modèle | Prix $/M (in/out) | Latence | Qualité tag fin (1-5) | Verdict |
|---|---|---|---|---|
| **DeepSeek chat** | 0,14 / 0,28 | ~1,5s | 4/5 | **Retenu — meilleur ratio, déjà en place** |
| Gemini 2.5 Flash-Lite | 0,10 / 0,40 | ~1s | 4/5 | Écarté — gain négligeable, migration coûte plus que l'économie |
| Claude Haiku 4.5 | 1,00 / 5,00 | ~1s | 5/5 | Écarté — 10x plus cher, qualité marginalement meilleure sur titre court |
| GPT-4o-mini | 0,15 / 0,60 | ~1s | 4/5 | Écarté — équivalent prix, qualité similaire |
| Llama 3.3 70B (auto-héb.) | ~0 + infra | ~3s | 3/5 | Écarté — pas de VPS en v3 |

**Pas de migration.** DeepSeek reste #1 sur ce use-case précis (étiquetage court, JSON strict, FR/EN mix).

---

## 3. Garde-fous coût (obligatoires)

- **Compteur quotidien** dans SQLite (`cost_today_usd`) — incrémenté à chaque appel.
- **Soft cap 0,50 $/jour** (~15 €/mois) → log WARN + email Thomas.
- **Hard cap 0,80 $/jour** (~25 €/mois) → kill switch, l'extracteur passe en mode `as_event_log_line_raw()` (colonnes vides) pour le reste de la journée.
- **Alerte taux d'erreur** : si `errors/calls > 5 %` sur 1h → log ERROR + ne pas retry.
- **Pas de retry agressif** : 1 seule tentative, fallback ligne raw si échec. Évite l'amplification de coût sur panne API.

---

## 4. Structured outputs + éval (livrables à ajouter en Phase 2.2)

- **Schéma Zod-équivalent** côté Python : `pydantic` `ExtractedEvent` avec validation stricte. Si parse échoue → 1 retry avec `"Ton JSON précédent était invalide, recommence."` puis fallback raw.
- **Eval set** : 30 titres-or (10 macro, 10 commodity, 10 corp/tech) avec ground truth L1/L2/cours/zone. À rejouer à chaque changement de prompt. Critères : exact match L1 ≥95 %, news_zone ≥90 %, cours ≥85 %.
- **Prompt versioning** : `PROMPT_VERSION = "v2.1"` en constante, loggé sur chaque event-log. Bump à chaque tweak.
- **Sample 5 % en prod** : Thomas vérifie 5 événements/jour à la main, score qualité dans un tableau hebdo.

---

## 5. Synthèse impact

| Action | Effort | Économie/mois | Risque |
|---|---|---|---|
| Schéma 11→7 champs | 30 min | -1,5 € (output) | 0 (champs morts) |
| Pré-filtre durci (B) | 1h | -2,4 € | Faux négatifs si trop strict — eval set à surveiller |
| Cache implicite DeepSeek | 0 | -0,25 € | 0 |
| Garde-fou coût | 1h | bornage | 0 |
| **Total** | **~2h30** | **6 € → 2-3 €/mois** | Faible |

**Budget projeté** : 2-3 €/mois nominal, hard cap 25 €/mois. Sous le seuil 30 € du briefing.

---

**Handoff → @orchestrator**
- Fichier produit : `vps-news-collector/reco/reco-ia.md`
- Décisions prises : garder DeepSeek `deepseek-chat`, schéma réduit 11→7, pré-filtre durci (blacklist + source-weighting), garde-fou 15 €/25 €. Pas de migration multi-provider.
- Points d'attention :
  - L'éval set 30 titres-or est à produire AVANT de toucher au prompt (sinon régression silencieuse).
  - Pré-filtre durci → risque de faux négatifs (events ratés). Mesurer sur 1 semaine shadow avant de lock.
  - Pas de batching tant que cache implicite suffit — ajouter complexité seulement si volume × 3.
  - Code à modifier reste dans `vps-news-collector/extractor.py` et `news_collector.py` — pas de nouveau module nécessaire.
