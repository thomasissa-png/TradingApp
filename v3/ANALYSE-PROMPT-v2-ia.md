# Analyse — System prompt v2 DeepSeek (schéma directionnel)

> Audit `extractor.py` (SYSTEM_PROMPT + FEW_SHOTS + parsing) ET consommation aval
> (`triggers_classifier._resolve_triplet` / `_ia_direction_for`, `criteres_calculator`). 30/05/2026.

## Verdict
**GARDER le schéma directionnel, SIMPLIFIER les dimensions sur-spécifiées non consommées
ou non fiables.** Le cœur (`impacts[]` + `direction` + `materiality`) est bon et réellement
câblé. Parsing défensif solide, coût négligeable. Mais on extrait un signal plus riche que
ce que le downstream sait utiliser : tokens jetés.

## Ce qui est bon
- **`impacts[]` directionnel multi-actifs** : juste design (un event géopol touche GOLD/BRENT/VIX/SP500). Réellement consommé via `_ia_direction_for` + `IA_ASSET_TO_ACTIF` → triplet ±1. Amélioration clé vs `cours` mono-actif.
- **Parsing défensif** : `_parse_impacts` rejette l'asset hors-liste (zéro invention), tolère `bullish/bearish/buy/sell`, `_norm_enum` gère case/lower/upper, array non-liste → `[]`. Robuste au drift d'énums.
- **`materiality`** : EST consommée — départage LONG/SHORT conflictuels (`_MAT_WEIGHT`) et arme la GATE événement-extrême (`high` < 24h). Dimension qui paie.
- **Few-shots user/assistant** : bon ancrage, format API correct.

## Faiblesses (par impact)
**P1 — `confidence` 0-100 : signal extrait puis JETÉ.** `_ia_direction_for` n'utilise
`confidence` QUE pour départager 2 impacts du même actif dans un même event (rare). Le
triplet final reste **±1 fixe** (LONG→+1, SHORT→-1, NEUTRAL→0). La granularité 0-100
(fausse précision LLM) ne pondère JAMAIS le critère. Tokens out payés pour un nombre ignoré.

**P2 — `already_priced` : extrait, JAMAIS lu + non-fiable.** Parsé (`_parse_bool`), stocké,
mais aucun consommateur ne le lit. Et un LLM sans book/positionnement marché ne peut juger
« déjà pricé » de façon fiable. Dimension morte ET peu fiable → **retirer**.

**P3 — JSON imbriqué temp 0 : robuste, 1 angle mort.** `impacts:[]` array d'objets en
`json_object` temp 0 fiable en pratique ; parsing couvre asset/direction hors-liste, array
absent, confidence textuelle. Angle mort : `impacts:[]` (aucun actif jugé) indistinguable
de `impacts` absent (champ oublié) — ici sans conséquence (les deux = neutre). Risque
résiduel : `max_tokens=500` peut tronquer un `impacts[]` verbeux → JSON invalide → fallback brut.

**P4 — `NEUTRAL` : redondant avec `impacts:[]`, source de bruit.** `{direction:NEUTRAL}` vs
ne pas inclure l'actif = même résultat downstream (NEUTRAL traité comme 0). Pire : un event
100% NEUTRAL allume `ia_seen_any=True` et **bloque le fallback keyword** (l.652-653) — il peut
EFFACER un signal keyword qui aurait matché. Effet de bord indésirable. → retirer NEUTRAL de
l'énum ; actif à effet incertain = simplement non inclus (`impacts:[]`).

**P5 — Few-shots (3) : plancher correct, manquent 3 cas.** (a) multi-actifs CONFLICTUEL
(sens opposés, matérialités différentes) — exactement ce que `_MAT_WEIGHT` arbitre, non ancré ;
(b) `already_priced:true` jamais montré (si conservé) ; (c) NEUTRAL jamais illustré (si conservé).

**P6 — Coût & sur-dimensionnement.** Schéma + 3 shots ≈ ~900-1100 tok in, ~120-180 out ≈
**0,0002 $/news** (tarif 0,14/0,28 $/M codé l.367). Négligeable vs caps. Le vrai problème =
**dilution** : 8 dimensions LLM extraites, 4 consommées (`impacts, materiality, category, trigger`).
`news_zone` et `latence` ne sont lus nulle part non plus → mêmes candidats au retrait.

## Reco concrète : SIMPLIFIER (+ pondérer plus tard)
**Étape 1 — retirer le poids mort (gain immédiat, zéro risque downstream)** :
- Supprimer `already_priced`, `news_zone`, `latence` (non consommés).
- `confidence: 0-100` → `confidence: "high|medium|low"` (buckets plus fiables ; mapping inverse déjà présent l.264).
- Retirer `NEUTRAL` de l'énum (évite l'effacement de signal keyword, P4).
- Garder `materiality` (consommée). Bump `PROMPT_VERSION`.

**Étape 2 (optionnelle, vrai chantier) — rendre le signal riche utile** : pour ne pas jeter
`confidence`/`materiality`, pondérer : `triplet = sign(direction) × f(materiality, confidence) ∈ [-1,+1]`.
MAIS le contrat downstream est `valeur ∈ {-1,0,+1}` (calculator l.948 `int(triplets[cle])`) →
pondérer = passer le critère en type `lineaire` borné, impacte scoring_analyste. À planifier séparément.

**Décision** : Étape 1 maintenant (prompt léger, fiable). Ne pas multiplier les dimensions LLM
tant qu'elles ne sont pas câblées — « bad signal worse than no signal ».

### SCHEMA simplifié proposé
```json
{ "category":"<...>", "subcat":"<...>", "trigger":"<max 200c>",
  "reliability":"<confirmed|reported|rumor>", "materiality":"<high|medium|low>",
  "impacts":[ {"asset":"<liste fermée>","direction":"<LONG|SHORT>","confidence":"<high|medium|low>"} ] }
```
(`already_priced`, `news_zone`, `latence`, `NEUTRAL` retirés ; confidence en buckets.)
Ajouter 1 few-shot multi-actifs conflictuel pour ancrer l'arbitrage `materiality`.
