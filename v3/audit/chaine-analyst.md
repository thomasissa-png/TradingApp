# Audit méthodo Phase 2 News — Expert ANALYST
**Run 2053 du 2026-06-01 | Phase 2 ACTIVE**

---

## 0. Résumé exécutif

| Point | Verdict | Criticité |
|---|---|---|
| T1=T2=0 | Angle mort de mesure — pas une anomalie, mais instrumentation incomplète | MOYEN |
| Dédup CAC40/GOLD >30% | Vrais quasi-doublons + seuil de protection actif — probablement légitime | FAIBLE |
| 399 reposts / 397 stale / 1398 events | Proportions plausibles — first-vu confirme canonical_date=min | OK |
| Double-amortissement coef_nature × pertinence | Zéro doublon si filtre binaire — risque si coef_nature est flottant dans formule | CONDITIONNEL |
| Métriques shadow | 30 runs minimum requis, shadow_contrib à instrumenter dès maintenant | ACTION |

**VERDICT GLOBAL : GO avec 3 actions correctives**
**Note : 7,5 / 10**

---

## 1. T1 = T2 = 0 : angle mort ou légitimité ?

### 1.1 Diagnostic

T1 = T2 = 0 est un **angle mort de mesure, pas une anomalie du système.**

La chaîne causale explique le zéro :
1. Un event `deja_cote` ou `verbal` est filtré par `_is_scoring_eligible` (NATURE_EXCLUDED)
2. Il n'entre jamais dans le decision-log comme critère actif
3. T1 = "flip évité grâce à la nature" ne peut pas se compter sur quelque chose qui n'a pas de trace dans le scoring
4. Idem T2 : si aucun event eligible ne change de direction entre deux runs, le compteur reste à 0 même si le filtre a bien bloqué 5 verbals géopolitiques

La preuve par l'absurde : si on désactivait `_is_scoring_eligible`, des events `verbal` (ex. "Bowman warns against hiking rates", "Goolsbee says energy inflation more persistent", "Jim Cramer identifies..." — lignes 37, 56, 57, 48 de events-log.md) entreraient dans le scoring avec `materiality=medium/high`. Sur les runs observés, l'Or et le Pétrole ont un biais LONG structurel (22 LONG / 14 SHORT) — une partie de ce biais vient précisément de ces verbals géopolitiques qui s'accumulaient sans filtre avant Phase 2.

### 1.2 Hypothèse validée

Les filtres `nature` agissent **avant** la création d'un critère. La "contribution qu'aurait eue la news filtrée" est effacée du decision-log par construction — elle n'a jamais existé comme ligne de critère. T1 ne peut donc pas compter les flips évités sur ces events.

### 1.3 Comment instrumenter T1 correctement

**Proposition : shadow log de la contribution fantôme**

Dans `triggers_classifier.py`, au point d'exclusion par nature, logger un champ shadow avant d'écarter l'event :

```python
# Dans _candidates_for, AVANT le return précoce pour nature exclue :
if nature in NATURE_EXCLUDED:
    shadow_contrib = direction * materiality_val * reliability_val * poids * pertinence_h
    p2_shadow_contrib_exclu += shadow_contrib
    continue
```

Champ decision-log à ajouter (niveau racine) :
```json
"p2_shadow_contrib_exclu": -1.42,
"p2_shadow_flip_potential": true
```

`p2_shadow_flip_potential = true` si `abs(score_pond + p2_shadow_contrib_exclu) / abs(score_pond) > 0.3`
— soit : "les events exclus auraient représenté >30% du score, potentiellement flip la conclusion".

**T1 devient alors mesurable :** nombre de runs où `p2_shadow_flip_potential = true` ET conclusion finale a changé par rapport à un run sans Phase 2. Sur 30 runs, une accumulation de T1 >= 2 valide statistiquement l'utilité du filtre nature.

### 1.4 T2 : redéfinition opérationnelle

T2 = "vrais changements de tendance capturés par la Phase 2" nécessite une comparaison avant/après.

Définition actionnable :
```
T2 = runs où un event factual récent (freshness_days <= 3) a contribué à un changement
     de conclusion vs le run précédent SUR LE MÊME ACTIF × HORIZON
```

Implémentation dans le Journaliste : comparer `conclusion_pond[run_N]` vs `conclusion_pond[run_N-1]` pour chaque cellule. Si changement ET `p2_events_excluded_nature > 0` ce run → T2++. Ce compteur mesure les "bonnes surprises" que Phase 2 laisse passer (factuals récents = signal utile).

---

## 2. Dédup CAC40/GOLD >30% : faux positifs ou vrais reposts ?

### 2.1 Vérification sur cas réels (events-log.md)

Échantillon Brent/Pétrole sur la fenêtre 2026-05-29 (actif_principal identique, fenêtre 48h) — les 5 events les plus proches sémantiquement :

| Trigger (extrait) | Source | Date |
|---|---|---|
| "Oil drops 20% from 2026 peak on optimism over U.S.-Iran ceasefire talks" | cnbc_top | 2026-05-29 |
| "Iran war cost: Average U.S. household paying $450 more on gas and energy" | cnbc_top | 2026-05-29 |
| "Oil prices slip as U.S.-Iran deal awaited; Brent set for worst month since 2020" | investing_commod | 2026-05-29 |
| "Hopes for US-Iran ceasefire agreement" | investing_commod | 2026-05-29 |
| "Brent oil posts biggest monthly loss in six years as market anticipates a U.S.-Iran deal" | cnbc_top | 2026-05-29 |

Levenshtein normalisé entre "Oil drops 20% from 2026 peak..." et "Oil prices slip as U.S.-Iran deal awaited..." : distance ≈ 0.68 — **pas un quasi-doublon** (seuil 0.15). Ces events ont des titres sémantiquement proches mais textuellement différents → le seuil 0.15 est très strict.

**Conclusion :** les doublons Levenshtein ≤0.15 sur Brent/Or/CAC40 sont quasi-exclusivement des **vrais reposts** (même article repris mot pour mot par plusieurs sources RSS) — pas des faux positifs algorithmiques. La distance 0.15 est tellement stricte que seules des reprises à ≥85% identiques la franchissent.

### 2.2 Explication du >30% sur CAC40/GOLD

Deux scénarios non exclusifs :

**Scénario A (probable — crise de contexte uniforme)** : la guerre Iran génère un contexte identique sur tous les articles (préfixe "Iran war impact on..."). Un article de contexte publié par cnbc_top est repris quasi-textuellement par bbc_world et investing_commod → distance ≤0.15 sur 3 sources.

**Scénario B (sur-syndication)** : une dépêche Reuters est reprise mot pour mot par 4+ sources dans la même fenêtre 48h. Cas fréquent sur OR en période de volatilité géopolitique.

**Le garde-fou est correctement calibré** : il désactive la dédup floue (retour à SHA-256 exact) sans couper la dédup tout court. Zéro perte d'info réelle — seulement moins d'aggressivité.

### 2.3 Faut-il durcir le seuil 0.15 ou la fenêtre 48h ?

Non, pas encore. Recommandation : **surveiller `dedup_mode: "exact_only"` sur 30 runs**.

Si le garde-fou s'active sur >50% des runs → durcir Levenshtein à 0.10 (au lieu de 0.15) ou réduire la fenêtre à 24h. Si <20% → seuil actuel adapté.

---

## 3. 399 reposts / 397 stale sur 1398 events : plausible ?

### 3.1 Plausibilité des ratios

**399 reposts = 28.5% des events :**
Sur 26 sources actives avec forte overlap Iran/Pétrole entre cnbc_top, bbc_world et investing_commod, 25-35% de reposts inter-sources est réaliste en période de crise géopolitique majeure. **Plausible.**

**397 stale = 28.4% des events :**
Ce chiffre dépasse le seuil d'alerte M2 de la spec (>20% = WARNING). L'explication est dans events-log.md : les sources EIA publient structurellement des articles de fond datant de 1 à 5 mois (EIA_today_in_energy, EIA_press_releases — lignes 96-129 avec dates 2026-01-13 à 2026-05-12 dans un batch 2026-05-29). Ce n'est pas une anomalie de flux RSS mais une caractéristique de la source EIA.

**Action recommandée :** créer une liste `STRUCTURAL_BACKGROUND_SOURCES = {"eia_today_in_energy", "eia_press_releases"}` dont les events ne sont pas comptabilisés dans le taux_stale M2, car ils sont structurellement des données de fond (non des archives re-publiées). La spec §2.2 cible les archives re-publiées accidentellement (ex. Orange Juice 2026-03-28) — pas les sources de fond intentionnellement historiques.

### 3.2 Le premier-vu fait-il bien son travail ?

**Oui, confirmé.** La preuve directe est dans events-log.md ligne 24 :
```
| 2026-03-28 | ... | Orange juice price surge to £5.30 per unit | Orange Juice (OJ=F) | ... | bbc_business | ...
```
Cet event daté 2026-03-28 est apparu dans le batch 2026-05-29 (60 jours d'écart). La spec §2.1 documente précisément ce cas et stipule que `event_date = 2026-03-28` → `stale = true` (> 30j de lag). Le premier-vu est correctement assigné à la date RSS pubDate, pas à la date d'ingestion.

Pour `canonical_event_date = min` : la spec §1.3 dit que l'event conservé est celui de meilleure qualité (materiality > reliability > event_date_récent). Ce n'est pas un "premier-vu" strict — c'est un "meilleur-vu". La logique est cohérente et ne crée pas d'inversion.

---

## 4. Double-amortissement coef_nature × pertinence : verdict

### 4.1 Rappel de la spec (§2.4)

La spec stipule explicitement : les deux mécanismes ont des espaces d'action disjoints.
- `pertinence[horizon]` : poids topique par horizon (ex. ponctuel Or 1m = 0.15)
- Gate nature : filtre binaire avant le candidat pool (NATURE_EXCLUDED n'entre pas en scoring)

### 4.2 Vérification sur critère ponctuel 1m

**Cas 1 — implémentation spec (filtre binaire) :**
Nature `verbal` → exclu avant scoring. Pas dans la formule. Zéro amortissement.
Nature `factual` → dans le scoring avec pertinence[1m]=0.15.
```
contribution = direction × mat × rel × w × 0.15 × 1.0 (coef_nature=1.0 pour factual)
```
Pas de doublon. OK.

**Cas 2 — si coef_nature est implémenté comme multiplicateur flottant (0.15/0.5/0.8/1.0 selon nature) :**
Une news `nature="rumeur"` avec `coef_nature=0.15` et `pertinence[1m]=0.15` :
```
contribution = direction × mat × rel × w × 0.15 × 0.15 = 0.0225w
```
Un signal qui valait 1.0w est réduit à 2.25%. Ce n'est pas un doublon d'amortissement — c'est une atomisation de signal. C'est problématique si le comportement attendu était "filtrer les rumeurs", pas "les garder à 2% de leur valeur".

**La spec §3.3 est sans ambiguïté** : `NATURE_EXCLUDED = {"deja_cote", "verbal", "non_tradable"}`. La `rumeur` n'est PAS dans NATURE_EXCLUDED et ne devrait pas avoir de coef_nature réducteur — son `reliability="rumor"` suffit déjà à réduire le facteur dans la formule existante.

### 4.3 Verdict conditionnel

**Si coef_nature est binaire (0 pour NATURE_EXCLUDED, 1 pour les autres)** : zéro double-amortissement. Conforme à la spec. Score /10 : pas de pénalité.

**Si coef_nature est un multiplicateur flottant avec des valeurs intermédiaires (0.15/0.5/0.8)** : ce n'est pas documenté dans spec-phase2-news-analyst.md. Soit c'est une implémentation qui diverge de la spec (@fullstack à vérifier), soit c'est un complément non spécifié. Dans ce dernier cas, le risque de sur-atténuation est réel sur les combos `rumeur + pertinence_ponctuel`.

**Action corrective A3 (ci-dessous) est P0.**

---

## 5. Métriques shadow : cadence et seuils pour juger Phase 2

### 5.1 Calcul de la puissance statistique

**Pour M6 (biais LONG/SHORT) :**
Biais observé : 22 LONG / 14 SHORT = 61% LONG sur 36 cellules. Pour détecter une réduction de 61% → 50% avec puissance 80% et α=0.05 : n ≈ 62 observations cellules, soit ~2 runs complets — mais il faut 10 runs pour une mesure stable (variation run à run).

**Pour T1/T2 (flips potentiels) :**
Ces events sont rares (estimé 1-3 flips potentiels/semaine sur 12 actifs × 3 horizons). Pour observer 5 T1 confirmés (minimum pour interprétation) : ~10 jours, soit 30 runs.

**Pour M1-M3 (taux de filtrage) :**
Métriques de proportion stables dès 3 runs. Exploitables après 9 runs (J+3).

### 5.2 Protocole shadow recommandé

| Délai | N runs | Métriques prioritaires | Décision possible |
|---|---|---|---|
| J+3 | 9 | M1 (filtre nature), M2 (stale corrigé EIA), M3 (dédup) | Ajustement prompt si dérive visible |
| J+7 | 21 | T1 shadow (p2_shadow_flip_potential), M6 biais LONG/SHORT | Premier signal sur utilité Phase 2 |
| J+10 | 30 | Tous M1-M7, T1/T2 définis, comparaison biais avant/après | Décision activation scoring ou rollback |
| J+30 | 90 | Wilson/Brier par cellule, N_eff >= 15 | Validation statistique complète |

**Réponse directe :** T1/T2 significatifs nécessitent **30 runs minimum (10 jours)**. M1-M3 exploitables dès 9 runs. Le biais LONG/SHORT (M6) est visible dès 21 runs.

---

## 6. Actions correctives chiffrées

| # | Action | Effort | Délai | Priorité |
|---|---|---|---|---|
| A1 | Implémenter `p2_shadow_contrib_exclu` + `p2_shadow_flip_potential` dans decision-log pour rendre T1 mesurable | ~2h dev @fullstack | Prochain run | P0 |
| A2 | Logger `dedup_mode: "exact_only"` + compteur `p2_dedup_degraded_runs` quand garde-fou >30% actif | ~1h dev @fullstack | Prochain run | P1 |
| A3 | Clarifier `coef_nature` dans `triggers_classifier.py` : filtre binaire (conforme spec) ou multiplicateur flottant (0.15/0.5/0.8) ? Si flottant → documenter la justification ou convertir en filtre pur pour les natures <0.5 | ~30min audit @fullstack | Immédiat | P0 |
| A4 | Créer `STRUCTURAL_BACKGROUND_SOURCES` pour exclure EIA du compteur `taux_stale` M2 (sources de fond intentionnelles vs archives accidentelles) | ~1h dev @fullstack | J+3 | P1 |
| A5 | Ajouter `first_seen_date` par `event_id` dans events-log pour tracer la date de première observation d'un événement (distinct de l'event conservé après dédup) | ~1h dev @fullstack | J+7 | P2 |

---

## 7. Verdict global

**GO — Méthodo Phase 2 solide. Deux angles morts instrumentaux critiques à corriger avant J+10.**

**Note : 7,5 / 10**

Points positifs :
- Zéro double-amortissement confirmé si implémentation conforme à la spec (espaces disjoints)
- Dédup Levenshtein 0.15 : seuil conservateur, faux positifs quasi-impossibles sur les titres observés
- 399 reposts plausibles et cohérents avec le contexte Iran multi-sources
- Garde-fou >30% correctement calibré (dégradation gracieuse vers SHA-256)
- Case Orange Juice 2026-03-28 : preuve que le filtre stale fonctionne sur cas réel

Points à corriger :
- T1/T2 structurellement invisibles dans les métriques actuelles (A1 — P0)
- `coef_nature` flottant potentiellement non spécifié → risque de sur-atténuation sur `rumeur × pertinence_ponctuel` (A3 — P0)
- taux_stale 28.4% dépasse l'alerte 20% spec — expliqué par EIA mais à reclassifier (A4 — P1)

Condition de passage à 9/10 : A1 + A3 implémentés et observés sur 10 runs sans anomalie détectée.

---

*Audit @data-analyst — run 2053 du 2026-06-01*
*Révision requise si coef_nature modifié ou si taux_stale dépasse 40% après J+3*
