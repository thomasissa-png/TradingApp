# Gates méthodologiques — Pipeline TradingApp v3
**Analyst | 2026-06-02 | Concertation round 1**

> Grille exhaustive des points de contrôle par étape. Chaque gate est classé :
> - **EXISTE ✓** : implémenté dans le code (testé ou opérationnel)
> - **MANQUE ✗** : absent ou partiel — à instrumenter
> - **P0** : bloquant — erreur silencieuse possible, intégrité du signal compromise
> - **P1** : important — biais ou perte de données sans visibilité
> - **P2** : amélioration — robustesse et observabilité supplémentaires

---

## S1. Ingestion flux news

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S1-G1] Schema RSS/ATOM** | Article sans `title`, sans `link`, ou avec `published_at` None → injecté silencieusement dans le pipeline | MANQUE ✗ | P0 |
| **[S1-G2] Fraîcheur brute d'ingestion** | Article dont `published_at` > NOW + 10 min (horloge source dans le futur) ou < NOW - 30 j (article fantôme recyclé) → rejeté sans log | MANQUE ✗ | P1 |
| **[S1-G3] Disponibilité source** | Source silencieusement absente du fetch (HTTP 4xx/5xx non loggué, timeout silencieux) → trou de couverture non détecté | EXISTE ✓ (source_monitor) | — |
| **[S1-G4] Volume anormal par source** | Source qui émet 0 articles (panne) ou >200 articles/run (flood/spam) sur un run → ni alerte ni throttle | MANQUE ✗ | P1 |
| **[S1-G5] Encodage / caractères nuls** | Titre ou body contenant `\x00`, séquence UTF-8 invalide, ou entités HTML non décodées → provoque crash ou hash instable en S3 | MANQUE ✗ | P2 |

---

## S2. Extraction DeepSeek

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S2-G1] Schéma JSON de réponse** | Réponse DeepSeek sans clé `impacts`, ou `impacts` non-liste, ou item sans `asset`/`direction`/`materiality`/`reliability` → parsing défensif présent mais rejet silencieux non loggué | EXISTE ✓ (parsing défensif) / MANQUE ✗ (log structuré du rejet) | P0 |
| **[S2-G2] Enum `direction` hors-bornes** | Valeur `direction` ∉ {LONG, SHORT} (ex. "BULLISH", "NEUTRAL", entier) → normalisation ou rejet documenté ? | EXISTE ✓ (normalisé ou rejeté selon code) | — |
| **[S2-G3] Enum `horizon` hors-bornes** | Si `horizon` est renvoyé par le LLM (champ futur Phase 2) et vaut "2w" ou None → rejet sans crash | MANQUE ✗ | P1 |
| **[S2-G4] Enum `asset` hors `TRADABLE_ASSETS`** | Actif inconnu (ex. "TESLA", "BTC") → actuellement filtré, mais non compté → angle mort sur la qualité du prompt | EXISTE ✓ (filtré) / MANQUE ✗ (compteur d'actifs rejetés) | P1 |
| **[S2-G5] Enum `nature` fermée (Phase 2)** | Valeur `nature` ∉ {structurel, ponctuel, verbal, deja_cote, non_tradable} → rejet ou fallback silencieux ; les valeurs "verbal"/"deja_cote"/"non_tradable" doivent exclure l'event du scoring | MANQUE ✗ | P0 |
| **[S2-G6] Réponse vide / fallback LLM** | LLM retourne `impacts:[]` sur tous les articles d'un run → run continue sans news ; non distinguable d'un run sans news réelles | MANQUE ✗ (flag `llm_empty_run` absent) | P1 |
| **[S2-G7] Cohérence `materiality` × `reliability`** | `materiality=high` + `reliability=rumor` = signal à fort poids sur base fragile → aucun garde-fou combiné | MANQUE ✗ | P1 |
| **[S2-G8] Idempotence de l'extraction** | Même article soumis deux fois → produit-il exactement le même triplet ? (temperature=0 mais prompt peut dériver si contexte différent) | MANQUE ✗ (non testé en CI) | P2 |
| **[S2-G9] Garde-fou coût (hard cap)** | Dépassement `HARD_CAP_USD_PER_DAY` → bascule passive documentée, mais pas de test CI validant que le pipeline ne plante pas en mode fallback | EXISTE ✓ (logique présente) / MANQUE ✗ (test CI manquant) | P2 |

---

## S3. Dédup / repost / nature / fraîcheur

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S3-G1] Stabilité du hash `event_id`** | Variation mineure du titre (espace final, casse différente entre sources) génère un `event_id` différent → faux négatif de dédup | EXISTE ✓ (normalisation SHA-256/12 spécifiée) | — |
| **[S3-G2] Collision de hash** | Deux titres sémantiquement différents → même `event_id` sur 12 chars hex (probabilité ~1/16^12, négligeable mais non documentée) | MANQUE ✗ (aucun log de collision détecté) | P2 |
| **[S3-G3] Seuil dédup Levenshtein ≤15%** | Seuil trop bas → faux positifs (events distincts fusionnés) ; trop haut → doublons passent (CAC40/GOLD >30% = vrais doublons selon audit) — calibration non rejouée sur corpus récent | EXISTE ✓ (seuil spécifié) / MANQUE ✗ (validation sur corpus actif) | P1 |
| **[S3-G4] Gate fraîcheur T1 (event_date vs ingestion)** | `event_date` None ou antérieure à `NOW - STALE_THRESHOLD` (30j) → event stale injecté dans le scoring avec poids plein | EXISTE ✓ (STALE_THRESHOLD spécifié) / MANQUE ✗ (implémentation à confirmer) | P0 |
| **[S3-G5] Gate fraîcheur T2 sur override high+confirmed** | Override anti-inversion déclenché sur un event stale (>3j) → conclusion faussée sans drapeau | EXISTE ✓ (FRESHNESS_OVERRIDE_DAYS=3j spécifié) / MANQUE ✗ (implémenté ?) | P0 |
| **[S3-G6] Exclusion nature non-tradable du scoring** | `nature` ∈ {verbal, deja_cote, non_tradable} → event exclu du scoring mais compté dans les métriques M1-M7 (risque : T1 gonflé artificiellement) | MANQUE ✗ | P0 |
| **[S3-G7] Compteur taux_stale hors sources de fond** | EIA = source de fond à publication hebdomadaire ; inclure EIA dans le taux_stale gonfle artificiellement le taux sans signaler une anomalie | MANQUE ✗ (recommandé dans audit précédent A4-P1) | P1 |
| **[S3-G8] Idempotence du pipeline dédup** | Deux runs successifs sur le même corpus → résultat identique ? (hash + Levenshtein doivent être déterministes) | MANQUE ✗ (test CI manquant) | P2 |

---

## S4. Calcul critères quant (Twelve Data / COT / FRED)

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S4-G1] Prix > 0 (sanity de base)** | Twelve Data renvoie 0 ou négatif pour un prix d'actif (erreur API, unité mal parsée) → z-score infini ou division par zéro en aval | MANQUE ✗ | P0 |
| **[S4-G2] Prix None / NaN silencieux** | Valeur manquante propagée comme `None` ou `NaN` dans le calcul → critère noté n/a mais sans log → coverage surestimée | EXISTE ✓ (critère → n/a si valeur manquante) / MANQUE ✗ (NaN explicit check) | P0 |
| **[S4-G3] Variation aberrante (spike)** | Variation 1j > 20% sur indice ou > 50% sur commodity sans flag → données corrompues ou split non ajusté absorbés comme signal réel | MANQUE ✗ | P0 |
| **[S4-G4] Borne z-score** | z-score non borné (ex. z=15 sur série courte) → contribution au score disproportionnée, écrase les autres critères | MANQUE ✗ (borne clip(-3, 3) ou similaire absente ?) | P0 |
| **[S4-G5] Division par zéro sur écart-type nul** | Série de prix constante (API bloquée, prix figé) → écart-type = 0 → division par zéro dans le z-score | MANQUE ✗ | P0 |
| **[S4-G6] Cohérence temporelle des données COT** | COT CFTC publié le vendredi avec délai ~3j → utilisation d'une valeur COT d'une semaine datée comme "courante" sans vérification de l'âge réel | MANQUE ✗ (look-ahead risk si date COT non contrôlée) | P1 |
| **[S4-G7] Fraîcheur données FRED** | Taux FRED mis à jour mensuellement/trimestriellement → utilisation d'une valeur FRED de M-1 sans flag d'ancienneté | MANQUE ✗ | P1 |
| **[S4-G8] Cohérence unités** | Prix Twelve Data en USD vs COT en lots vs FRED en % → normalisation d'unités non contrôlée → critères de nature incompatible agrégés | MANQUE ✗ (dépend des fiches YAML) | P1 |
| **[S4-G9] Disponibilité Twelve Data (rate-limit)** | Rate-limiter attend (RPM=55 documenté) mais si l'attente dépasse le timeout du workflow GitHub → run partiel avec critères manquants non signalés | EXISTE ✓ (rate-limiter attend) / MANQUE ✗ (timeout global non gardé) | P1 |
| **[S4-G10] Idempotence des critères quant** | Deux runs sur la même fenêtre temporelle → critères identiques ? (si l'API renvoie des valeurs légèrement différentes selon l'heure d'appel, le score change) | MANQUE ✗ | P2 |

---

## S5. [EXCLUS — couverture pondérée traitée séparément]

*Hors périmètre de cet audit (en build — paliers COVERAGE_OK/MIN déjà spécifiés dans scoring_analyste.py).*

---

## S6. Scoring / pondération

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S6-G1] Réconciliation somme des contributions** | Σ contributions individuelles ≠ score final (bug de pondération, arrondi flottant) → score publié non reproductible depuis le decision-log | MANQUE ✗ | P0 |
| **[S6-G2] Score total NaN / Inf** | Critère avec z-score Inf ou poids None → score = NaN propagé silencieusement → conclusion basée sur None | MANQUE ✗ | P0 |
| **[S6-G3] Borne du score normalisé** | Score pondéré non borné → valeur hors plage attendue (ex. score=47 quand l'échelle est [-10, 10]) → PROBA_SCALE mal calibrée en S8 | MANQUE ✗ | P1 |
| **[S6-G4] Cohérence coef_nature** | `coef_nature` est-il strictement binaire {0, 1} (spec) ou flottant en implémentation ? Un flottant crée un double-amortissement avec `pertinence[h]` | MANQUE ✗ (à vérifier — signalé A3-P0 dans audit précédent) | P0 |
| **[S6-G5] Normalisation par horizon indépendante** | Score 24h calculé avec données 1m dans la fenêtre → look-ahead sur 24h | MANQUE ✗ | P1 |
| **[S6-G6] Poids nuls (tous critères n/a)** | Σ poids = 0 sur un actif × horizon → division par zéro dans la normalisation pondérée → déjà géré par S5 (INSUFFISANT) mais interaction non testée | EXISTE ✓ (COVERAGE_MIN) / MANQUE ✗ (test du cas limite poids=0 exact) | P1 |
| **[S6-G7] Détection de distribution dégénérée** | Distribution des scores sur 30 runs concentrée sur une valeur (ex. 90% des runs → score ∈ [0.0, 0.05]) → signal d'un critère dominant qui écrase tout | MANQUE ✗ (aucune alerte sur variance des scores) | P1 |
| **[S6-G8] Biais LONG/SHORT >70%** | Actuellement calculé dans journaliste.py mais pas en sortie du scoring → détection tardive (après publication) | EXISTE ✓ (journaliste) / MANQUE ✗ (drapeau en amont du scoring) | P1 |

---

## S7. Conclusion LONG/SHORT

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S7-G1] Conclusion jamais-neutre (règle absolue)** | Score exactement 0.0 (après arrondi flottant) → tie-break défini ? Aucun actif ne doit sortir "NEUTRE" | EXISTE ✓ (SEUIL_LONG=0.0, LONG si >0) / MANQUE ✗ (cas score==0.0 exact non documenté → SHORT par défaut ?) | P0 |
| **[S7-G2] Override news_dominant correct** | Drapeau 📰 émis si `ratio_news` > 50% → mais si score numérique est nul et news = seule source, la conclusion repose sur 0 dato quant → fausse confiance | MANQUE ✗ | P0 |
| **[S7-G3] Cohérence plan horizon (24h vs 7j vs 1m)** | Conclusion 24h=LONG + 7j=SHORT + 1m=LONG sans explication → incohérence temporelle légitime ou signe d'instabilité du scoring ? Aucun gate de cohérence inter-horizons | MANQUE ✗ | P1 |
| **[S7-G4] Cap anti-inversion α=0.8 (borne et effet réel)** | α=0.8 borne la contribution news pour ne pas inverser le signal quant — mais si score_quant est très proche de 0, même α=0.8 peut inverser → gate sur amplitude score_quant avant application du cap | MANQUE ✗ | P1 |
| **[S7-G5] Conclusion INSUFFISANT cohérente avec bulletin**| Actif en INSUFFISANT → bulletin l'affiche comme tel, mais la synthèse directionnelle et le HTML le traitent-ils comme "pas de signal" (non affiché) ou comme "INSUFFISANT" (affiché avec warning) ? | MANQUE ✗ (comportement pipeline aval non spécifié) | P1 |
| **[S7-G6] Reproductibilité de la conclusion** | Même `criteres-courants.md` → même conclusion à chaque re-run ? (test de reproductibilité déterministe) | MANQUE ✗ (non couvert en CI) | P2 |

---

## S8. Mesure VRAI/FAUX (Journaliste)

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S8-G1] Intégrité prix d'émission** | Prix d'émission écrit dans `prix-emission/YYYY-MM-DD.json` absent ou corrompu → mesure VRAI/FAUX impossible → `suivi-interrompu` silencieux sans alerte | EXISTE ✓ (idempotent : ancien préservé si fetch échoue) / MANQUE ✗ (alerte si TOUS les tickers d'un actif échouent) | P0 |
| **[S8-G2] Zéro look-ahead temporel** | Journaliste compare prix courant à prix d'émission → s'assurer que `prix_courant_date >= bulletin_date` (jamais prix antérieur à l'émission utilisé comme "courant") | MANQUE ✗ (contrôle explicite de l'ordre temporel absent) | P0 |
| **[S8-G3] Cohérence échéance ≥ date émission** | Pour horizon 24h : échéance = émission + 24h. Pour 7j : émission + 7j. Pour 1m : émission + 30j. Un bug de calcul de date pourrait mesurer avant l'échéance | MANQUE ✗ (vérification de l'ordre échéance > émission non explicite) | P0 |
| **[S8-G4] Seuils de réussite par actif (calibration)** | VIX seuil 5% → trop large (audit précédent : revoir à 3%). Cacao 1.5% → revoir à 1.0%. Seuils figés sans gate de recalibration périodique | EXISTE ✓ (seuils définis) / MANQUE ✗ (gate de révision des seuils ≥ tous les 30 runs) | P1 |
| **[S8-G5] Distribution LONG/SHORT mesurée ≥ 30 conclusions** | KPI Wilson/Brier calculés sur N<30 → intervalles de confiance non valides → affichage trompeur en warm-up (N_eff=0/12 actuellement) | EXISTE ✓ (statut shadow si <30) / MANQUE ✗ (suppression de l'affichage Wilson si N<30) | P1 |
| **[S8-G6] Brier score cohérent avec PROBA_SCALE** | PROBA_SCALE=15 → proba = 0.5 + clip(score/15, -0.5, 0.5). Si score > 7.5, proba = 1.0 → Brier pénalise extrêmement une mauvaise prédiction à forte confiance. Aucun gate sur la distribution des probas (doit-elle être uniforme ?) | MANQUE ✗ | P1 |
| **[S8-G7] Chevauchement inter-horizons** | Conclusion 7j émise le J, mesurée sur J+7. Conclusion 7j émise J+1 mesurée J+8 → chevauchement → non-indépendance des mesures → p-values invalides (non-chevauchant spécifié dans le protocole backtest mais pas dans le Journaliste live) | MANQUE ✗ | P1 |
| **[S8-G8] Multiple-testing (12 actifs × 3 horizons)** | 36 cellules testées simultanément → correction Bonferroni/BH requise pour les KPI statistiques. Actuellement aucun ajustement | MANQUE ✗ | P2 |
| **[S8-G9] Continuité du fichier `performance.md`** | Regénéré à chaque run → si le run échoue à mi-chemin, fichier tronqué ou vide → perte de l'historique affiché | MANQUE ✗ (écriture atomique ?) | P1 |

---

## S9. Publication (bulletin / HTML / biais)

| Gate | Ce qu'il attrape | Statut | Priorité |
|---|---|---|---|
| **[S9-G1] Détection de biais directionnel global** | Bulletin avec >70% LONG ou >70% SHORT sur les 12 actifs → actuellement détecté en journaliste mais pas bloqué à la publication | EXISTE ✓ (alerte journaliste) / MANQUE ✗ (drapeau dans le bulletin lui-même) | P1 |
| **[S9-G2] Complétude du bulletin (12 actifs × 3 horizons)** | Bulletin publié avec des cellules manquantes (actif absent → Thomas ne voit pas le vide) | MANQUE ✗ | P0 |
| **[S9-G3] Intégrité HTML (balises non fermées, injection)** | Template HTML avec variable None ou chaîne non échappée → rendu cassé ou injection XSS dans un contexte email | MANQUE ✗ | P2 |
| **[S9-G4] Commit atomique git** | Crash entre l'écriture du bulletin et le commit → bulletin local mais non commité → git-as-storage incohérent | MANQUE ✗ (vérifier que l'écriture + commit sont dans un bloc try/finally) | P1 |
| **[S9-G5] Timestamp de publication cohérent** | Bulletin daté avec timezone incorrecte (UTC vs CET) → Thomas lit "7h" mais le bulletin est de "5h UTC" → confusion sur la fraîcheur | MANQUE ✗ | P1 |
| **[S9-G6] Anti-doublon de publication** | Garde-fou anti-doublon (skip si snapshot <2h) → mais si deux runs s'exécutent exactement au même créneau (redondance ×3), le second publie un bulletin identique | EXISTE ✓ (garde-fou <2h documenté) | — |
| **[S9-G7] Drapeau 📰 dans le bulletin final** | Drapeau `news_dominant` calculé mais absent du rendu HTML → Thomas ne voit pas l'avertissement | MANQUE ✗ (à vérifier dans build_html.py) | P1 |

---

## Top 5 des gates manquants les plus critiques

Ces 5 gates représentent des **erreurs silencieuses à impact direct sur le signal** — elles ne plantent pas le pipeline mais corrompent la conclusion sans que Thomas ni le système ne le détectent.

### #1 — [S4-G4] Borne z-score (P0)
**Pourquoi c'est le plus critique.** Un z-score non borné est le vecteur le plus probable d'un score pathologique. Une série courte (ex. VIX sur 5 jours d'API lente) ou une valeur aberrante (spike Twelve Data) génère z=10, z=20, qui écrase tous les autres critères. Le système publie LONG ou SHORT avec une conviction artificielle de 100% sur un seul point de donnée corrompu. Correction : `clip(z, -3.0, 3.0)` + log si z > 2.5 avant clip.

### #2 — [S4-G5] Division par zéro sur écart-type nul (P0)
**Corollaire du #1 mais différent.** Si l'API renvoie le même prix plusieurs jours consécutifs (figé, panne non détectée), l'écart-type de la série = 0 → ZeroDivisionError ou NaN flottant selon l'implémentation Python. En Python, `float / 0.0` lève une exception → crash du run entier. `numpy` retourne `NaN`. Ni l'un ni l'autre n'est gardé. Correction : `if std == 0: critere n/a`.

### #3 — [S2-G5] Enum `nature` fermée — exclusion du scoring (P0)
**Gate Phase 2 le plus structurant.** Si `nature` ∈ {verbal, deja_cote, non_tradable} et que l'event n'est pas exclu du scoring, un discours de banquier central ou une rumeur déjà absorbée contribue au score comme un vrai signal fondamental. Ce gate est la raison d'être de la Phase 2 — sans lui, la classification `nature` est décorative.

### #4 — [S8-G2 + S8-G3] Zéro look-ahead Journaliste (P0)
**Intégrité de la mesure = intégrité de tout le KPI framework.** Si le Journaliste peut comparer un prix "courant" antérieur à l'émission (bug de date, timezone, DST), il marque VRAI une prédiction sur un prix qu'il "connaissait déjà". Le taux de réussite serait gonflé artificiellement. Thomas activerait l'émission sur la foi d'un KPI biaisé. C'est le scénario de perte financière directe.

### #5 — [S6-G1] Réconciliation somme des contributions (P0)
**Le decision-log devient inutile sans ce gate.** Si Σ contributions individuelles ≠ score final publié, le decision-log ne permet pas de rejouer ni d'expliquer une conclusion. Toute l'observabilité du système repose sur la traçabilité. Un bug d'arrondi flottant (ex. `sum()` vs accumulation en boucle avec `+=`) suffit à créer l'écart. Correction : assertion `abs(sum_contrib - score_final) < 1e-9` loggée à chaque run.

---

## Automatisables vs revue humaine

### Gates automatisables en CI (pytest / assert)

Ces gates sont **déterministes et sans jugement** — une assertion Python suffit. Ils doivent être dans la suite de tests existante (360 tests verts) avant tout passage en émission réelle.

| Gate | Type de test |
|---|---|
| S4-G4 Borne z-score | `assert abs(z) <= 3.0` dans `test_criteres.py` |
| S4-G5 Division par zéro écart-type | `pytest.raises` sur série constante |
| S4-G1 Prix > 0 | `assert prix > 0` dans `test_market_data.py` |
| S4-G2 NaN silencieux | `assert not math.isnan(valeur)` avant normalisation |
| S6-G1 Réconciliation score | `assert abs(sum_contrib - score_final) < 1e-9` |
| S6-G2 Score NaN/Inf | `assert math.isfinite(score)` |
| S7-G1 Jamais-neutre score==0 | Test avec fixture score=0.0 exact → vérifier SHORT |
| S8-G2 Zéro look-ahead | Test fixture : `prix_courant_date < bulletin_date` → lever ValueError |
| S8-G3 Cohérence échéance | Test paramétrisé sur les 3 horizons |
| S3-G8 Idempotence dédup | Deux appels successifs → résultat identique |
| S2-G8 Idempotence extraction | Même article × 2 → même triplet (temperature=0) |
| S9-G2 Complétude bulletin | `assert len(conclusions) == 12 * 3` |

### Gates de revue humaine (Thomas, revue périodique)

Ces gates impliquent un **jugement contextuel** non automatisable ou une **décision de recalibration** qui modifie les paramètres du système.

| Gate | Fréquence recommandée | Responsable |
|---|---|---|
| S3-G3 Calibration seuil Levenshtein | Tous les 30 runs (≈ J+10) | Thomas + data |
| S4-G6 Cohérence temporelle COT | Après chaque publication CFTC (vendredi) | Thomas |
| S4-G7 Fraîcheur FRED | Mensuelle (lors de la publication) | Thomas |
| S6-G7 Distribution dégénérée des scores | Hebdomadaire (lecture decision-log) | Thomas |
| S8-G4 Révision seuils réussite | Tous les 30 runs conclusifs | Thomas |
| S8-G5 Suppression Wilson si N<30 | À l'activation de l'émission | Thomas |
| S8-G7 Chevauchement inter-horizons | Avant activation A/B test pondéré | Thomas + data |
| S9-G1 Biais directionnel global | À chaque bulletin (lecture visuelle) | Thomas |
| Top5 #3 Enum nature + scoring | Premier run Phase 2 activé | Thomas + dev |

**Règle de priorisation** : les 12 gates automatisables CI doivent passer AVANT toute sortie du mode shadow. Les gates de revue humaine S8-G4, S8-G7 et Top5 #3 doivent être validés AVANT activation de l'émission réelle (post-shadow).
