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


---

## Addendum — 2026-06-10 (soir) : lot autopilote « sources & critères » (S6)

- **VIX rejoint le reset du 2026-06-11** (critère `gap_rv_iv` poids 5 ressuscité — calculable depuis SPY+CBOE déjà ingérés). **À compter du 11/06, les 12 actifs sont en ère v2** ; plus aucune cellule ne porte d'historique v1.
- Critères ressuscités le même jour : café `usd_brl` (poids 6, Twelve), EUR/USD `balance_commerciale_ez` (poids 3, Eurostat) — actifs déjà reset au 11/06, même ère.
- Conséquence N≥15 à J+60=2026-08-08 : inchangée (déjà documentée pour les 11 autres) — désormais valable pour les 12.

---

## Addendum — 2026-06-15 : critères des actifs continus sur le prix le plus frais

**Changement de signal (VOLET A).** Pour les actifs **continus** (or, argent, pétrole, cuivre, cacao, café, blé, EUR/USD ; source `mesure_ouverture.actif_group`), les critères de niveau/momentum/RSI intègrent désormais le **prix temps réel plus frais que `close[-1]`** quand il est disponible (fin de l'angle mort overnight/week-end démontré le 15/06 sur l'or). Dégradation sûre : prix frais absent/périmé → comportement actuel exact (zéro invention).

**Impact kill-criterion.** Le kill-criterion (WR tradable < seuil sur N suffisant, 24h-only) **reste inchangé dans sa formule**. Seule la **référence de mesure** des 8 cellules continues change → leur `ref_changed` avance à **2026-06-15** (`ref-changed.json`, append-only, justifié CHANGELOG). Ces cellules repartent **N=0 au 15/06** (3e reset des continus — coût assumé). Conséquence sur N≥15 à J+60 (= 2026-08-14) : fenêtre utile raccourcie pour ces 8 actifs — issue valide, pas un échec. Les non-continus (`^GSPC`, `^IXIC`, `^FCHI`, `^VIX`) conservent leur historique depuis le 11/06. **Aucun poids ni seuil de fiche n'est touché.**


---

## Addendum — 2026-06-16 : or/argent/Brent servis par le symbole Twelve natif

**Changement de source.** Or/argent/Brent sont désormais interrogés chez Twelve sous leurs symboles spot natifs `XAU/USD`/`XAG/USD`/`XBR/USD` (les futures Yahoo `GC=F`/`SI=F`/`BZ=F` renvoient 404 sur Twelve → un fallback yfinance caché servait la donnée jusqu'ici). Twelve devient la source unique de ces 3 actifs.

**Impact kill-criterion.** La **formule** du kill-criterion (WR tradable < seuil sur N suffisant, 24h-only) reste **inchangée**. Seule la **référence de mesure** des 3 cellules (or, argent, Brent) change — le niveau spot diffère légèrement du future → leur `ref_changed` avance à **2026-06-16** (`ref-changed.json`, append-only, justifié CHANGELOG). Ces cellules repartent **N=0 au 16/06**. Conséquence sur N≥15 à J+60 (= 2026-08-15) : fenêtre utile raccourcie pour ces 3 actifs — issue valide, pas un échec. **Cuivre/cacao/café/blé inchangés** (Twelve ne sert pas ces futures au bon niveau → yfinance conservé, `ref_changed` 2026-06-15). Les non-continus et tous les autres actifs conservent leur historique. **Aucun poids ni seuil de fiche n'est touché.**


---

## Addendum — 2026-06-16 : fix L027 — la mesure du WR des continus part de l'ÉMISSION 7h (et non de l'« ouverture » 8h)

**Défaut corrigé (P0, prouvé sur pièces — GO mesure Thomas).** Pour les actifs **continus** (cotés 24/7), la « référence d'ouverture » était stampée à **heure fixe 8h Paris**. Ce point pouvait tomber **au milieu d'un mouvement déjà entamé** depuis l'émission du bulletin de 7h → le 24h n'était mesuré que sur la **fin tronquée** du mouvement. **Cas fondateur (15/06, or, XAU/USD natif)** : open de session ≈ 4215 → close ≈ 4309 (**+2,2 %**, plus haut +3,6 %). Le call **SHORT était PERDANT**, mais le système l'a classé **« NC » (+0,18 %)** car sa référence 8h (≈ 4308) était **APRÈS** le rallye. **Conséquence : le win rate des continus CACHAIT des pertes et était artificiellement flatté.**

**Correctif (sémantique de mesure).** Pour les continus uniquement (source : `mesure_ouverture.actif_group`), la **référence du 24h passe de l'OUVERTURE 8h au PRIX D'ÉMISSION 7h** — le moment où Thomas lit le bulletin et peut agir (un continu cote en continu à 7h ⇒ prix live valide). C'est l'alignement de la **leçon L021** (« mesurer depuis le point d'EXÉCUTION réel »). Les **non-continus** (indices cash CAC/S&P/Nasdaq 9h/15h30, VIX — fermés à 7h) sont **inchangés** : leur référence reste l'ouverture de marché (un prix de 7h y serait un prix de nuit). Le fix est **scopé aux continus**.

**Impact kill-criterion.** La **formule** (WR tradable < seuil sur N suffisant, 24h-only) reste **inchangée**. C'est la **valeur** du WR des continus qui devient honnête (les pertes masquées en « NC » ressortent désormais en FAUSSE). Les **8 continus** (`GC=F`, `SI=F`, `BZ=F`, `HG=F`, `CC=F`, `KC=F`, `ZW=F`, `EUR=X`) sont **reset N=0 au 2026-06-17** (1er bulletin sous la nouvelle sémantique ; `ref-changed.json`, append-only, justifié CHANGELOG). **4e reset des continus — coût assumé, VRAI défaut corrigé (dit honnêtement).** Conséquence sur N≥15 à J+60 : fenêtre utile raccourcie pour ces 8 actifs — issue valide, pas un échec. Les non-continus (`^GSPC`, `^IXIC`, `^FCHI`, `^VIX`) conservent leur historique depuis le 11/06. **Aucun poids ni seuil de fiche n'est touché.** Test-verrou : `tests/test_verrou_l027_mesure_continu.py` (le SHORT or du 15/06 ressort **FAUX**, plus jamais « NC »).


---

## Addendum — 2026-06-26 : 3 nouveaux actifs (USD/JPY, Coton, Sucre) — l'univers passe de 12 à 15 cellules

**Ajout (pas de changement de signal sur l'existant).** Trois nouveaux actifs entrent en mode shadow : **USD/JPY** (`USD/JPY`, famille fx), **Coton** (`COTN`, agri-softs), **Sucre** (`CANE`, agri-softs). Fiches `config/fiches/{usdjpy,coton,sucre}.yml` (8 critères + gate chacune), sources câblées dans `criteres_calculator.py` (CFTC noms exacts vérifiés Socrata, FRED spreads JP, Open-Meteo Texas/Gujarat/Ribeirão Preto, Twelve momentum + proxy Brent/USD-BRL/VIX). Critères sans source publique gratuite (taux BoJ daily, ESALQ éthanol, USDA CropProgress coton sans `USDA_API_KEY`) = n/a propre ou triplet news, **jamais inventés**.

**Impact kill-criterion.** La **formule** (WR tradable < seuil sur N suffisant, 24h-only) reste **inchangée**, et **aucune des 12 cellules existantes n'est touchée** (zéro reset des actifs en place — leur `ref_changed` et leur historique sont préservés). Les 3 nouvelles cellules (`USD/JPY`, `COTN`, `CANE`) entrent au registre `ref-changed.json` avec `ref_changed = 2026-06-26` : warm-up à zéro, seules les observations datées >= 26/06 comptent (il n'existe aucun historique antérieur). N≥15 / WR≥70 % à J+60 s'évalue donc pour elles à partir du 26/06. **Aucun poids ni seuil de fiche n'est touché.** Test-verrou : `tests/test_nouveaux_actifs_2026_06_26.py` (15 actifs enregistrés, conclusion LONG/SHORT cohérente avec le signe, n/a propre sans donnée).
