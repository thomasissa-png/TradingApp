# Audit IA/LLM — Pipeline TradingApp v3 (bout-en-bout)

> Angle : robustesse prod, qualité extraction DeepSeek, pré-filtre/dédup, éval, coût, choix modèle.
> Périmètre : extractor.py (v2.1), news_collector.py, triggers_classifier.py, weighting.py. 30/05/2026.

## Verdict synthétique
Pipeline d'ingénierie SOLIDE (parsing défensif, caps coût, dégradation gracieuse) mais
AVEUGLE sur sa propre qualité : aucune boucle d'évaluation. On extrait des signaux de
trading sans jamais mesurer si l'extraction est juste. C'est le manque structurant.

## 1. Robustesse prod
- BON. temp=0 + `response_format=json_object` + `_norm_enum`/`_parse_impacts` = drift d'énums absorbé (asset hors-liste rejeté, bullish/bearish tolérés, confidence num→bucket).
- BON. Caps coût persistants (ledger JSON), hard-cap → fallback brut, clé absente → mode passif. Pas de crash possible.
- BON. Langue FR/EN gérée (prompt + classifier sans-accent). Dégradation gracieuse par feed.
- FAIBLE. **Idempotence non garantie sur erreur LLM** : un appel KO écrit une ligne brute (trigger seul, impacts vide). Au cycle suivant le même titre est dédupé (SQLite) → l'event n'est JAMAIS ré-extrait. Une erreur transitoire = event perdu définitivement. Pas de retry, pas de file "à ré-extraire".
- FAIBLE. **temp=0 ≠ déterminisme** côté DeepSeek (pas de seed, non garanti par l'API). Reproductibilité non testée.

## 2. Qualité d'extraction
- RISQUE STRUCTUREL. DeepSeek juge `direction` + `materiality` sur un TITRE court (snippet ≤1500c souvent absent en RSS). Inférer "Iran frappe → SP500 SHORT" est une chaîne causale spéculative, pas une lecture. Faux positifs probables sur titres ambigus/ironiques.
- RISQUE. Le prompt ordonne "AUCUNE INVENTION" mais demande simultanément d'inférer des impacts multi-actifs — injonction en tension. Sans book ni prix de marché, `materiality:high` est un jugement non-vérifiable.
- ANGLE MORT. Pas de garde-fou anti sur-extraction : rien ne plafonne le nombre d'impacts ni ne pénalise un actif "exotique" (COCOA SHORT sur une news macro US).
- `max_tokens=500` : un `impacts[]` riche + trigger peut tronquer → JSON invalide → event en mode brut (cf. point idempotence ci-dessus). Marge faible.

## 3. Pré-filtre + dédup
- BON. Blacklist-avant-whitelist = bonne intuition (vire sport/people avant test finance).
- FAIBLE. **Whitelist regex large** (`\bai\b`, `\bstrike\b`, `\bwar\b`, `\bchip\b`) → bruit qui consomme des appels LLM. `\bstrike\b` matche grève ET frappe ET strike d'option.
- FAIBLE. **Dédup Jaccard sur titre seul, seuil unique** : deux dépêches reformulées (<seuil) passent 2× → 2 appels LLM + double comptage downstream. Pas de dédup sémantique cross-langue (même event FR+EN = 2 events).
- RISQUE. Cache `DEDUP_CACHE_SIZE` borné en LIFO : un event qui ressort > N titres plus tard n'est plus reconnu comme doublon.

## 4. Boucle d'évaluation — MANQUE CRITIQUE
- ABSENT TOTAL. Aucun eval set de titres-or, aucune mesure de précision direction/matérialité, aucune détection de régression au bump `PROMPT_VERSION`. Le prompt est passé v2.0→v2.1 SANS test set de non-régression (cf. protocole migration de modèle).
- Conséquence : impossible de répondre "DeepSeek se trompe-t-il 5% ou 40% du temps ?". On trade sur un signal dont la qualité est inconnue et non monitorée.
- Reco : 30-50 titres-or annotés (direction+matérialité attendues par actif), run au moindre changement de prompt/modèle, LLM-as-judge (Claude) en arbitre. Sampling 2-5% en prod + scoring asynchrone.

## 5. Coût projeté
- Mesuré dans l'analyse v2 : ~0,0002 $/news (in 0,14$/M, out 0,28$/M). Avec ~26 sources × 3 cycles, après dédup+filtre l'ordre de grandeur réaliste est ~100-400 news LLM/jour → **~0,02-0,08 $/jour**. Soft-cap 0,50$ / hard-cap 0,80$ = marge ~10×. TIENT LARGEMENT.
- ATTENTION : tarif codé en dur (l.386). À re-vérifier (cache DeepSeek off-peak, hausse). Pas de prompt caching exploité alors que system+few-shots (~1k tok) sont identiques à chaque appel → caching réduirait l'input payé.

## 6. Choix DeepSeek
- DÉFENDABLE sur le coût pur. Mais sur CE use-case (jugement directionnel fin sur titre court, faible tolérance au faux positif), un modèle au raisonnement plus fort (Claude Haiku/Sonnet) réduirait les faux positifs — l'enjeu n'est pas le prix/token (négligeable ici) mais la QUALITÉ du signal de trading.
- Recommandation : ne PAS migrer à l'aveugle. D'abord construire l'eval set (§4), PUIS A/B DeepSeek vs Haiku/Sonnet sur les titres-or. La décision modèle doit être pilotée par la mesure, pas par le prix.

## Top 5 actions (priorité)
1. **[CRITIQUE] Eval set titres-or + non-régression de prompt** (§4) — sans ça, signal aveugle.
2. **[P1] File de ré-extraction sur erreur LLM** — sinon events perdus silencieusement (§1).
3. **[P1] Bornage impacts + garde-fou sur-extraction** + bump max_tokens à 800 (§2).
4. **[P2] Prompt caching DeepSeek** sur le préfixe system+few-shots (§5).
5. **[P2] A/B modèle piloté par l'eval set** avant toute migration (§6).
