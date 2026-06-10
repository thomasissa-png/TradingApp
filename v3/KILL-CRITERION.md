# KILL-CRITERION — TradingApp v3 (shadow mode)

> **STATUT : VALIDÉ v1 (Thomas, 30/05/2026, sur recommandation).**
> Règle GRAVÉE : pas de relâchement post-hoc. Toute modif → `kill-criterion-v2` avec justification écrite.

## Pourquoi un kill criterion gravé

Sans seuil fixé à froid AVANT le début du shadow, le critère d'arrêt peut être
rétroactivement ajusté ("on n'est qu'à 53 %, encore 30 jours et ça remontera").
C'est la voie royale du biais de confirmation. La règle ci-dessous est versionnée
et signée pour empêcher cet ajustement post-hoc (cf. audit-data §6 "Kill criterion
formalisé").

## Règle proposée (à valider)

À **J+60 du shadow** (60 jours calendaires après activation, fuseau Europe/Paris),
**KILL ou PIVOT** si l'UNE des deux conditions ci-dessous est vraie :

1. **Taux de réussite directionnelle global < 55 %**
   - mesure : toutes cellules confondues
   - sur **observations NON-CHEVAUCHANTES** uniquement (cf. note autocorrélation)
   - exclusion des cellules avec `N < 5` observations non-chevauchantes (bruit trop fort)

   OU

2. **Aucune cellule individuelle ≥ 65 % sur N ≥ 15 observations non-chevauchantes**
   - "cellule" = combinaison (actif × horizon), soit 36 cellules (12 actifs × 3 horizons).
     Pas de `pattern_id` en v3 (notion legacy event-driven abandonnée).
   - 65 % est le seuil edge minimum revendiqué dans la thèse v3 ; en dessous, même
     la meilleure cellule ne fournit pas un signal exploitable
   - N ≥ 15 = puissance statistique minimale pour distinguer 65 % d'un coin flip à
     50 % (intervalle de confiance Wilson 95 % : [44 %, 81 %] — encore large mais
     suffisant comme garde-fou directionnel)

Si **les deux** conditions sont OK → CONTINUE shadow jusqu'à J+90 puis revue
complète (Brier score, calibration, stabilité semaine 1-4 vs 5-8, cf. audit-data §6).

## Note critique : observations NON-CHEVAUCHANTES

Les horizons 7 jours et 1 mois génèrent de l'autocorrélation forte si on compte
chaque jour comme une nouvelle observation. Une prédiction "Brent LONG à 7j"
émise lundi et une autre émise mardi mesurent quasi le même mouvement de marché
→ comptées comme 2 succès indépendants, on surestime massivement la précision.

**Règle de comptage non-chevauchante** :

- horizon **7 jours** : 1 observation par cellule par fenêtre de 7 jours (la 1ʳᵉ
  prédiction émise dans la fenêtre, les suivantes sont ignorées pour le scoring
  kill criterion)
- horizon **1 mois** (~30 jours) : 1 observation par cellule par fenêtre de 30
  jours
- horizon **1 jour** : pas de problème de chevauchement (1 obs/jour)

Cette règle s'applique UNIQUEMENT au calcul du kill criterion. Le scoring interne
peut continuer à compter toutes les observations pour le suivi opérationnel ; il
faut juste deux colonnes distinctes dans le dashboard : `n_total` et
`n_non_overlap`. Seul `n_non_overlap` entre dans la décision GO/KILL.

Source : audit-data §3 et §6 (autocorrélation des horizons multi-jours).

## Procédure d'évaluation à J+60

1. Snapshot figé : copier `v3/data/events-log.md` et la table de scoring à 00h00
   Europe/Paris le jour J+60.
2. Recompter les observations non-chevauchantes par cellule (script à écrire
   séparément, hors scope de ce fichier).
3. Calculer :
   - taux global = succès_non_overlap / total_non_overlap (cellules avec N ≥ 5)
   - top cellule = max(succès / N) parmi celles avec N ≥ 15
4. Appliquer la règle ci-dessus.
5. **Décision écrite, datée, signée Thomas** dans `v3/data/kill-decision-J60.md`.
   Pas de décision orale.

## Action requise AVANT J+1

- [x] Thomas valide les seuils (55 %, 65 %, N ≥ 15, J+60) — **validé v1 le 30/05/2026**
- [x] Définition de "cellule" : **actif × horizon** (36 cellules) — corrigé (plus de pattern_id)
- [x] Règle de comptage non-chevauchant — validée
- [ ] Poser le tag git `kill-criterion-v1` au lancement du shadow

Toute modification ultérieure de ce fichier doit créer une `kill-criterion-v2`
avec justification écrite ; jamais d'édition silencieuse.

## Pourquoi PAS de "encore 30 jours pour voir"

Le shadow doit avoir une fin. Si à J+60 les seuils ne sont pas atteints, deux
options :

- **KILL** : le système ne tient pas la promesse de tendance directionnelle. On
  arrête, on ne brûle pas plus de temps Thomas.
- **PIVOT** : on a appris quelque chose (ex: une cellule tire toute la perf, les
  autres saignent). On redéfinit le périmètre (ex: ne garder que cette cellule),
  on relance un NOUVEAU shadow de 60 jours avec un nouveau kill criterion gravé.

Pas de troisième voie "on attend encore". Cette discipline est la seule défense
contre l'illusion d'une remontée à venir.

---

## Addendum — Redémarrage v2 (2026-06-10)

> Append-only. **Ne modifie PAS les seuils gravés ci-dessus** (55 %, 65 %, N ≥ 15,
> J+60) : précise uniquement comment le cutover v2 réel du 10/06 affecte le
> comptage des observations par cellule.

**Portée du reset = 4 actifs seulement.** Les cellules de **cacao, pétrole,
nasdaq, argent** ont leur **référence de mesure changée** au 2026-06-10 (dédup des
fiches, audit Cowork 10/06 — Lot A : un critère redondant retiré sur chacune). Pour
ces 4 actifs, **les observations antérieures au 2026-06-10 ne comptent plus** dans
le calcul du kill criterion : N (chevauchant et non-chevauchant), le taux global et
le top-cellule ne sont calculés que sur les observations dont la date d'émission est
≥ `ref_changed`.

**Les 8 autres actifs gardent leur historique v1.** or, sp500, eurusd, cac40, café,
vix, blé, cuivre **ne sont PAS reset** : leur signal est inchangé, leur N continue
depuis l'origine.

**Pas de reset global.** `is_news_regime` / `ratio_news` décisionnel **non modifiés**
→ aucun delta de signal hors ces 4 actifs → pas de remise à zéro de l'ensemble.
Cutover **court** (lot unique daté du même jour).

**Registre source de vérité** : `v3/data/ref-changed.json`, **clé par
`ticker_principal`** (identifiant stable, robuste au renommage — cf. leçon L023).
Le Journaliste applique ce registre : aucune cellule des 4 actifs ne mélange une
observation pré-dédup (v1) et post-dédup (v2) dans un même compteur.

---

## Addendum — Correctif famille momentum-prix (2026-06-10)

> Append-only. **Ne modifie PAS les seuils gravés ni l'addendum « Redémarrage v2 »
> ci-dessus** : étend la portée du reset au correctif famille du 10/06 (lot postérieur
> au Lot A, même journée).

**Le reset s'étend à 4 actifs supplémentaires.** Un critère de tendance-prix
(`momentum_prix_20j_<actif>`, z-score des closes, signe +1) a été **ajouté** aux 7 fiches
commodities/métaux qui en étaient dépourvues (balayage `momentum-prix-sweep.md` :
8/12 fiches sans tendance-prix propre = incohérent avec la thèse trend-following).
Cet ajout change la référence de mesure → **café (`KC=F`), blé (`ZW=F`), cuivre
(`HG=F`), or (`GC=F`)** rejoignent le reset au 2026-06-10 : leurs observations
antérieures à cette date ne comptent plus dans le kill criterion. cacao (`CC=F`),
pétrole (`BZ=F`), argent (`SI=F`) étaient **déjà reset** au 2026-06-10 (Lot A) — leur
cutover du même jour couvre aussi l'ajout du momentum (pas de double entrée).

**Bilan : 8 actifs reset au 2026-06-10** (cacao, pétrole, nasdaq, argent, café, blé,
cuivre, or) ; **4 gardent l'historique v1** (sp500, eurusd, cac40, vix). Les seuils du
kill criterion (55 %, 65 %, N ≥ 15, J+60) et le mécanisme de scoring sont
**inchangés** (aucune nouvelle mécanique de calcul, `weighting.yml` non touché).

## Addendum — Cutover momentum v3 (2026-06-11)

> Append-only. **Ne modifie PAS les seuils gravés ni les addendums du 10/06.** Acte le
> cutover réel du momentum v3 corrigé (vague 1 + vague 2), effectif au bulletin 11/06 7h.

**Le momentum « déployé » le 10/06 était fonctionnellement identique à la v1** (z-score
du NIVEAU de close = laggard, constat bloquant A1). Les corrections atterrissent ce soir,
premier signal effectif au **bulletin 11/06 7h** : A1 (variation 20j + z-score de la
série de rendements), A2 (cap anti-inversion **aveugle au momentum**), A3 (poids momentum
**≤6 prove-first** : cacao 9→6, café/blé/cuivre 8→6, pétrole/or/argent 7→6), A6 (momentum
exclu de la couverture), A8 (famille complétée : EUR/USD poids 5, S&P 500/Nasdaq/CAC 40
poids 4, RSI indices poids 2 conservé), A9 (VIX exclu).

**Reset : 11 actifs au 2026-06-11.** Les 8 entrées existantes voient leur `ref_changed`
**avancé 2026-06-10 → 2026-06-11** (justif CHANGELOG.md, exigée par le `_doc` du registre)
— le momentum corrigé change leur référence de mesure. S'y ajoutent **EUR/USD (`EUR=X`),
S&P 500 (`^GSPC`), CAC 40 (`^FCHI`)**. **Seul `vix` (`^VIX`) garde son historique v1.**

**Conséquence sur N ≥ 15 à J+60 (= 2026-08-08).** Les observations antérieures au
2026-06-11 ne comptent plus pour les 11 actifs reset : fenêtre utile ~58 jours ouvrés,
N ≥ 15 peut ne pas être atteint à J+60 (le kill criterion ne s'applique qu'à N ≥ 15 — en
deçà, ni kill ni validation, on continue d'observer). Seul `vix` reste immédiatement
évaluable. **Les seuils (55 %, 65 %, N ≥ 15, J+60) et le mécanisme de scoring sont
inchangés.**

**Mesure (A5, shadow)** : métrique « FAUSSES aux retournements » ajoutée au Bilan du jour
(observabilité pure, DISTINCTE du WR) — **aucun impact sur ce kill criterion** : elle ne
peut ni déclencher ni empêcher un kill, elle sert uniquement à documenter l'effet du
momentum v3 aux points de retournement (forward-test J+60).
