# Audit Spec « 5 rapports + mesure ouverture→clôture » — Analyst (validité méthodologique)

> Date : 2026-06-08. Branche : `claude/elegant-ramanujan-OIKms`.
> Sources : `spec-refonte-5-rapports.md` + `spec-refonte-5-rapports-RESOLUTIONS.md` + `audit-journaliste-analyst-2026-06-08.md` + `project-context.md` + `founder-preferences.md`.
> Rôle : Analyst — rigueur statistique / décision data-driven.

---

## Verdict global

**7,5 / 10 — SOLIDE mais 3 défauts méthodologiques précis à corriger avant implémentation.**

Le cœur du modèle est sain : la logique ouverture→clôture corrige un biais réel, le passage à 1 décision/jour est la bonne réponse au gonflement ×3, et la contrainte WIN RATE ONLY est tenue. Les défauts identifiés ne cassent pas le système mais créent des zones grises exploitables ou des ambiguïtés d'implémentation qui produiront des bugs silencieux.

---

## 1. Le modèle ouverture→clôture pour le 24h tient-il ?

### 1.1 Principe : fondé et cohérent

Le changement est justifié. L'existant stampait le prix à 7h (marchés fermés ou pré-ouverture) puis comparait à J+1. Cela introduisait un biais systématique : le « delta » incluait la nuit, le pré-marché et la séance, alors que seule la séance est actionnable par Thomas.

Le nouveau modèle :
```
outcome_24h = signe(prix_clôture_J - prix_ouverture_J) vs call_7h
```
est exactement ce que Thomas peut opérer : il lit le bulletin à 7h, il entre à l'ouverture, il sort à la clôture. **La fenêtre de mesure = la fenêtre d'action réelle.** C'est rigoureux.

### 1.2 Cas tordus — analyse

| Cas | Spec | Jugement |
|---|---|---|
| Ouverture indisponible (Twelve KO) | ticker absent du JSON → `suivi-interrompu` | ✅ correct : zéro invention, pas de note |
| Gap d'ouverture brutal | Premier prix disponible après délai — traité sans traitement spécial | ✅ acceptable : le gap fait partie de la réalité. Un gap up → prix ouverture est déjà gappé, la mesure reste propre |
| Férié partiel (ex: 4 juillet US fermé, EU ouvert) | Garde globale KISS : skip si l'un est fermé | ⚠️ **défaut mineur** : voir §1.3 |
| Prix manquant clôture 22h | `clôture indisponible` → `suivi-interrompu` → retry 7h lendemain | ✅ correct |
| Double bulletin même créneau | Anti-doublon existant conservé | ✅ correct |
| VIX via VIXY (ETF NYSE) | Traité comme US : 15h30 Paris | ✅ correct |

### 1.3 Défaut sur les féries partiels (Q2 — résolution KISS)

La résolution Q2 retient la garde globale : skip si NYSE **ou** Euronext fermé. Conséquence : un 4 juillet (US fermé, EU ouvert), les actifs EU (CAC) et Continus (Or, EUR/USD) ne sont PAS stampés ni notés, alors que leurs marchés fonctionnent normalement.

**Problème statistique** : cela introduit un biais de sélection dans le win rate. Les jours où un seul marché est fermé peuvent avoir une dynamique différente (réduction de liquidité US → moins de bruit pour les actifs EU → biais positif potentiel sur les NC). En excluant ces jours, on exclut aussi des données potentiellement valides pour les actifs EU.

**Verdict** : le KISS est défendable en phase shadow (cas rares). Mais la spec doit **documenter explicitement ce biais** dans la section CA-MESURE et prévoir de compter ces jours dans un compteur `jours_exclus_garde_partielle` dans performance.md. Sans documentation, l'implémenteur peut l'oublier et Thomas ne verra pas combien de jours sont silencieusement sautés.

**Correction requise** : ajouter un critère d'acceptation `CA-M7 : un compteur jours_bourse_exclus (féries partiels) est visible dans performance.md`.

---

## 2. La note à 22h est-elle bien définie ?

### 2.1 Logique correcte

Le run R4 à 22h ferme et note les cellules 24h du bulletin 7h du même jour. La nuit = marchés fermés = le 24h est terminé. La formule `signe(close_J - open_J)` est propre. **Cette décision est la meilleure possible** : noter à J+1 matin reviendrait à inclure l'overnight (hors fenêtre d'action).

### 2.2 Problème de rétrocompat sur les bulletins 12h/18h existants

La résolution Q8 (Option B) stoppe la mesure des bulletins non-7h dès la mise en prod. Les anciens bulletins 12h/18h sont marqués `non-noté`. C'est propre.

**Risque non adressé** : les bulletins 12h/18h actuellement dans `measures-log.jsonl` avec des outcomes déjà écrits (VRAI/FAUSSE) pour les horizons 7j/1m ne sont pas mentionnés dans la spec. Si ces mesures restent dans `performance.md`, elles polluent les statistiques d'une façon difficile à distinguer des mesures propres (7h uniquement). La spec ne dit pas explicitement « exclure les mesures issues de bulletins non-7h du calcul des KPIs post-refonte ».

**Correction requise** : ajouter dans CA-M6 (ou nouveau CA-M6b) : « Les outcomes existants de bulletins 12h/18h sont préservés dans `measures-log.jsonl` mais EXCLUS du calcul des KPIs post-refonte (filtre sur `bulletin_id` : seuls les bulletins 7h sont comptés). »

---

## 3. Migration 7j/1m vers prix-ouverture — cohérence et biais

### 3.1 Résolution Q3 : migration vers prix-ouverture

La résolution retient la migration complète 7j/1m vers `prix_ouverture_J0`. Justification : « quasi gratuite, N≈0-1, rien à perdre ».

**Vérification de la cohérence** :

```
7j :  signe(prix_ouverture_J+7  - prix_ouverture_J0)  vs call_7h
1m :  signe(prix_ouverture_J+30 - prix_ouverture_J0)  vs call_7h
```

Comparaison entre horizons : les 3 horizons utilisent la même référence (ouverture J0) et le même point de mesure terminal (ouverture Jn). **Cohérence totale — c'est solide.**

### 3.2 Non-chevauchant — le passage à 1 décision/jour préserve-t-il la logique ?

Avant : 3 bulletins/jour → `select_non_overlapping` avec step_days = 7 (7j) ou 30 (1m) donnait N_eff déflaté ×21 ou ×90.

Après : 1 bulletin/jour → step_days = 7 pour le 7j → N_eff = N_brut / 7 (sur 7 jours ouvrés). Pour le 1m → N_eff = N_brut / 30 (~1 obs indépendante par mois). **La logique non-chevauchante est préservée et simplifiée.** Bon.

**Alerte sur N_eff 7j** : avec 1 bulletin/jour et step_days = 7, on accumule ~1 observation indépendante par semaine ouvrable. Pour atteindre N_eff = 15 (seuil warm-up), il faut **15 semaines = ~4 mois**. C'est un fait, pas un bug de spec — mais la spec ne le mentionne pas explicitement. Thomas doit savoir que le 7j sera en warm-up jusqu'en octobre 2026.

**Correction requise** : ajouter dans §6 Impact mesure une ligne sur le N_eff attendu par horizon post-refonte, avec dates estimées de sortie de warm-up (24h : ~J+25 ≈ mi-juillet ; 7j : ~15 semaines ≈ octobre 2026 ; 1m : hors portée horizon 6 mois).

---

## 4. Le passage à 1 décision/jour — correction du gonflement ×3

### 4.1 Le N_eff devient-il honnête ?

Oui. Avec 1 bulletin/jour (R1 7h uniquement), pour le 24h :
- N_brut = 1 par jour de bourse (plus de ×3).
- N_eff = N_brut (pour le 24h, step_days = 1 : toute mesure du lendemain est indépendante).
- N_eff = 15 → ~3 semaines ouvrées. **La formule « 15 = ~3 semaines » est exacte.** Bien.

**Ce que la spec ne dit pas** : après la refonte, les bulletins 12h/18h continuent d'exister comme rapports (R2/R3), mais ils ne génèrent plus de cellules LONG/SHORT. Il faut s'assurer que `run_suivi.py` (R2/R3) n'appelle JAMAIS `stamp_prix_emission` ni n'écrit dans `measures-log.jsonl`. Ce point est implicite dans la spec (CA-S6 : « le rapport suivi n'alimente PAS measures-log.jsonl ») mais une erreur d'implémentation est facile. Un test CI vérifiant que le count de lignes dans measures-log.jsonl n'augmente pas après un run 12h/18h manque.

**Correction requise** : ajouter CA-S6b : « Test CI post-run R2/R3 : `git diff v3/data/measures-log.jsonl` = vide (aucune ligne ajoutée). »

### 4.2 Transition des bulletins existants

La résolution Q8 (Option B) est correcte : marquer `non-noté` les anciens bulletins 12h/18h. La spec confirme (§6.3). Pas de défaut ici.

---

## 5. WIN RATE ONLY — respect dans toute la spec

### 5.1 Vérification systématique

| Section | Contenu | WIN RATE ONLY respecté ? |
|---|---|---|
| R1 Briefing 7h | LONG/SHORT + scores | ✅ |
| R2 Suivi 12h | Delta%, Statut, Suggestion Hold/Surveiller/Sortir | ✅ (aucun € ni montant) |
| R3 Suivi 18h | Identique R2 | ✅ |
| R4 Bilan 22h | Win rate du jour, outcomes VRAI/FAUSSE | ✅ |
| R5 Manager | Win rate hebdo, cellules/critères faibles | ✅ |
| CA-B5 | Test parsing : aucun `€`, `$`, `gain`, `rendement` | ✅ explicite |
| CA-W5 | Bilan semaine sans métrique monétaire | ✅ explicite |
| Manager §4.4 | « Il ne commente pas le P&L, les gains ou pertes monétaires » | ✅ explicite |

**WIN RATE ONLY est tenu dans l'ensemble de la spec.** C'est propre.

### 5.2 Zone grise : « Suggestion Sortir »

Le suivi R2/R3 contient une colonne `Suggestion` avec des valeurs `Hold / Surveiller / Sortir`. La valeur `Sortir` est une suggestion de sortie de position. La résolution Q4 la qualifie de « drapeau-suggestion seulement ».

**Risque de dérive** : `Sortir` n'est pas une métrique monétaire, mais si la suggestion est calculée sur la base d'un seuil d'amplitude (perte > seuil × 0.5), cela commence à ressembler à un signal de gestion de risque qui implique implicitement un montant. La spec est protégée par « JAMAIS un ordre — Thomas décide », mais l'implémenteur pourrait être tenté d'ajouter un raisonnement monétaire dans le calcul du seuil `Sortir`.

**Correction requise** : ajouter dans CA-S4 : « La valeur `Sortir` ne peut être générée que par comparaison de |Delta%| vs un seuil d'amplitude de l'actif (défini dans la fiche YAML en %, pas en €). Aucun calcul monétaire. »

---

## 6. Le Manager (dimanche 18h) — validité statistique de la détection

### 6.1 Les définitions de « cellule faible » sont-elles défendables ?

La spec définit 4 conditions pour qualifier une cellule de faible (§4.3) :

| # | Condition | N_eff requis | Jugement |
|---|---|---|---|
| 1 | Win rate < 50% sur N_eff ≥ 5 | **5** | ⚠️ trop bas |
| 2 | Dominée par un seul critère (◧) sur ≥ 50% des runs semaine | ~5 runs | ⚠️ structurel, pas statistique |
| 3 | Score quasi-neutre sur ≥ 3 runs consécutifs | 3 | ⚠️ trop bas |
| 4 | Critère de poids ≥ 8 absent sur ≥ 60% des runs | ~5 runs | ✅ détection opérationnelle |

**Problème statistique sur la condition 1** : déclarer une cellule « statistiquement défavorable » sur N_eff = 5 avec win rate < 50% n'est pas défendable. Sur 5 paris binaires, le p-value d'un test exact de Fisher pour H0 : p ≥ 0.50 avec k=0 succès est ~3.1% (unilatéral). C'est en limite de significativité, mais le seuil N_eff = 5 est celui d'une semaine et demie de shadow — trop peu pour conclure. Wilson_low sur N=5, k=2 (40%) est 0.093 — largement en dessous du seuil opérationnel de 50%.

La spec reconnaît l'ambiguïté : « statistiquement défavorable, même si non significatif ». C'est contradictoire : soit c'est significatif (seuil adapté), soit c'est une observation à garder en mémoire. Appeler ça « statistiquement défavorable » sur N=5 peut induire Thomas à invalider un critère sur du bruit.

**Correction requise** : remplacer dans §4.3, condition 1 : « Win rate < 50% sur N_eff ≥ 5 » par « Win rate < 50% sur N_eff ≥ 10 **ET** Wilson_low < 50% ». Pour N_eff entre 5 et 9, la condition passe en **observation sans proposition** (§4.6 : section « Observations sans proposition »). Cela évite la sur-réaction sur petit N.

### 6.2 Conditions 2 et 3 : détection opérationnelle, pas statistique

Les conditions 2 (mono-critère) et 3 (quasi-neutre persistant) sont des détections qualitatives, pas des tests statistiques. C'est acceptable — elles signalent un problème de structure du signal, pas un problème de performance. Mais elles peuvent déclencher une proposition sur une seule semaine (5 runs). Le risque est faible car ces conditions débouchent sur des **propositions que Thomas valide** — pas sur des modifications automatiques. La garde « Thomas valide » absorbe le risque de sur-réaction.

### 6.3 Les définitions de « critère faible » (§4.4) — même problème

La condition 2 : « contribution moyenne opposée à l'outcome final sur la semaine » — sur 5 runs, une contribution peut être opposée par hasard (régime contrariant, pas critère défaillant). Même recommandation : n'activer la proposition que si N_eff_semaine ≥ 10 ou si la condition est observée sur 2 semaines consécutives.

**Correction requise** : ajouter dans §4.4, condition 2 : « observé sur ≥ 2 semaines consécutives (ne pas proposer sur une seule semaine de données). »

### 6.4 Propositions « propose, Thomas valide » — garde correcte

Le principe cardinal « JAMAIS de modification silencieuse » est répété plusieurs fois (§4.1, §4.5, CA-W4). C'est le garde-fou principal contre la sur-réaction du Manager. La spec est rigoreuse sur ce point. ✅

---

## 7. Les 31 critères d'acceptation — testabilité binaire

### 7.1 Inventaire

| Bloc | Critères | Testables binaires ? | Problèmes |
|---|---|---|---|
| CA-MESURE (M1-M6) | 6 | 5/6 | CA-M5 : « référence décidée par Thomas » → résolu (Q3 = prix-ouverture), mais la formulation dans la spec est encore conditionnelle |
| CA-R2R3 (S1-S6) | 6 | 5/6 | CA-S4 : `Statut — neutre si |Delta%| < 0.1%` — le 0.1% est-il dans une constante configurable ou hardcodé ? Non précisé → risque de dérive |
| CA-R4 (B1-B5) | 5 | 4/5 | CA-B2 : « close 17h30 pour CAC » — dépend du comportement Twelve Data (Q5 non encore testée). Le CA ne peut être validé avant le test Q5. |
| CA-R5/Manager (W1-W5) | 5 | 4/5 | CA-W1 : « un run manuel hors dimanche avec `force=true` est ignoré » — contradictoire avec la table de vérité §5.3 qui montre que `force=true` bypass toujours. Ambiguïté |
| CA-INFRA (I1-I4) | 4 | 3/4 | CA-I3 : « validation `crontab -l` » n'est pas un test CI automatisable — c'est une vérification manuelle |

**Total testables automatiquement : ~21/31. Les 10 restants nécessitent validation manuelle ou dépendent de comportements externes (Twelve, VPS).**

### 7.2 Défauts précis

**CA-M5 toujours conditionnel** : la spec écrit « À implémenter selon réponse Q3 » alors que Q3 est résolu (prix-ouverture). La formulation doit être mise à jour pour être binaire.

**CA-W1 ambigu** : « Un run manuel hors dimanche avec `report_type=weekly_summary` est ignoré (sauf `force=true`) ». Mais la table de vérité §5.3 dit que `force=true` bypass le jour pour les bulletins — pas pour les weekly_summary. Est-ce que `force=true` permet de forcer un weekly_summary hors dimanche ? La spec ne le précise pas. Si oui, CA-W1 doit le documenter. Si non, la table de vérité doit avoir une ligne `dispatch (force=true) + weekly_summary → non, sauf dim`.

**CA-I3 non-automatisable** : la vérification du crontab VPS ne peut pas être faite en CI. Reformuler en « Test : `trigger-cycle.sh --check` affiche les créneaux 22h + 18h dim sur stdout → résultat parseable automatiquement. »

---

## 8. Points solides (ce qui ne nécessite pas de correction)

1. **Stamping idempotent** : entry-lock par actif/date — un re-run ne réécrase pas. ✅
2. **Séparation prix-émission / prix-ouverture** : deux fichiers distincts, sans confusion. ✅
3. **Fallback prix-émission si ouverture absente** (T1.3) : la rétrocompat est documentée. ✅
4. **OPEN_STAMP_DELAY_MIN = 5 min** : délai raisonnable pour éviter les prix d'ouverture instables. Non documenté si ce 5min est dans un fichier de config ou hardcodé — à préciser mais non bloquant.
5. **Anti-doublon ×3 conservé pour le créneau 22h** (CA-I4) : logique déjà éprouvée réutilisée. ✅
6. **Manager ne modifie aucun YAML** (CA-W4) : garde la plus importante, explicite. ✅
7. **WIN RATE ONLY tenu** : ni dans les rapports ni dans les critères d'acceptation une métrique monétaire ne s'est réintroduite. ✅
8. **Q9 — run_suivi léger (pas de scoring complet à 12h/18h)** : réduit les coûts API et élimine le risque de second bulletin complet concurrent. ✅

---

## 9. Tableau récapitulatif des défauts à corriger pour 10/10

| # | Défaut | Gravité | Section spec | Correction requise |
|---|---|---|---|---|
| D1 | Condition 1 Manager (win rate < 50% sur N=5) : sur-réaction sur petit N | **P0** | §4.3 | Relever à N_eff ≥ 10 + Wilson_low < 50% ; N=5-9 → observation uniquement |
| D2 | Rétrocompat mesures 12h/18h existantes : exclusion KPIs post-refonte non documentée | **P0** | §6.3 / CA-M6 | Ajouter CA-M6b : filtre bulletin_id 7h dans le calcul des KPIs post-refonte |
| D3 | CA-W1 ambigu : force=true + weekly_summary hors dimanche → comportement non spécifié | **P0** | §7 / Table §5.3 | Clarifier la table de vérité + CA-W1 pour le cas force=true weekly_summary |
| D4 | §6 n'indique pas les dates estimées de sortie de warm-up par horizon post-refonte | **P1** | §6.2 | Ajouter tableau N_eff attendu : 24h ~J+25, 7j ~15 semaines, 1m hors portée 6 mois |
| D5 | Féries partiels : biais de sélection non documenté, aucun compteur prévu | **P1** | §2.6 / CA-MESURE | Ajouter CA-M7 : compteur jours_bourse_exclus visible dans performance.md |
| D6 | CA-S4 : seuil 0.1% pour neutre non lié à une constante nommée | **P1** | §3.2 / CA-R2R3 | Nommer la constante `NEUTRAL_BAND_PCT = 0.001` dans les fiches ou config |
| D7 | CA-S6 sans test CI : R2/R3 pourraient écrire dans measures-log sans être détectés | **P1** | §7 CA-R2R3 | Ajouter CA-S6b : test CI git diff measures-log après run suivi = vide |
| D8 | CA-M5 encore conditionnel (Q3 résolu) | **P2** | §7 CA-MESURE | Mettre à jour CA-M5 pour refléter Q3 = prix-ouverture décidé |
| D9 | Condition 2 critère faible (§4.4) : observée sur 1 semaine = trop court | **P2** | §4.4 | Ajouter « observé sur ≥ 2 semaines consécutives avant proposition » |
| D10 | CA-I3 non-automatisable en CI | **P2** | §7 CA-INFRA | Reformuler comme check script parseable (trigger-cycle.sh --check) |

---

## 10. Note finale : 7,5 / 10

**Ce qui plafonne à 7,5 et non 9+** :
- D1 est un vrai risque méthodologique : un Manager qui déclenche des propositions sur N=5 peut conduire à des modifications de config non fondées. Thomas a insisté sur « mesurer avant d'agir » — la spec du Manager contredit ce principe sur la condition 1.
- D2 est un trou de spec potentiellement silencieux : des mesures 12h/18h existantes pourraient polluer les KPIs post-refonte sans être signalées.
- D3 est une ambiguïté qui produira un bug ou une décision arbitraire d'implémenteur.

**Ce qui amène de 7,5 à 10 après corrections** :
Corriger D1+D2+D3 (P0) → 8,5. Corriger D4+D5+D6+D7 (P1) → 9,5. Corriger D8+D9+D10 (P2) → 10.

---

*Produit par @data-analyst — TradingApp v3 — 2026-06-08*
