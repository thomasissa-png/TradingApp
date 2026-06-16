# SELECTION-RULE — TradingApp v3 (shadow mode)

> **STATUT : VALIDÉ v1 (Thomas, 2026-06-10, sur recommandation).**
> Règle GRAVÉE : pas de relâchement post-hoc. Toute modif → `selection-rule-v2` avec justification écrite AVANT consultation des résultats.

---

## Pourquoi pré-enregistrer cette règle

Sans critère de sélection fixé à froid AVANT les premiers résultats, le seuil
d'entrée en trading réel peut être abaissé rétroactivement ("WR à 65 %, c'est déjà
bien, on peut commencer"). C'est exactement le biais de confirmation que `KILL-CRITERION.md`
vise à bloquer — la même discipline s'applique ici, côté sélection.

La règle ci-dessous est versionnée et datée pour empêcher tout ajustement
post-hoc. Elle est complémentaire au kill criterion : là où le kill criterion
décide si le système reste en vie, la règle de sélection décide quelles cellules
méritent d'être tradées.

---

## Objectif (rappel — ce que cette règle sert)

Le produit est le **trade directionnel sur 1 jour (horizon 24h), entrée et sortie
intraday**. Le J+60 ci-dessous n'est **PAS** une durée de détention ni un délai-but :
c'est uniquement le **point de contrôle** (la preuve statistique minimale) avant de
risquer du capital réel. Dès qu'une cellule 24h franchit le seuil au checkpoint,
elle se trade **chaque jour ouvré**. La règle est volontairement **24h-only** pour
coller à cet objectif. (Signé Thomas 2026-06-10 : « mon but, c'est trader sur 1 jour. »)

## Règle de sélection (formule GRAVÉE)

**Ancrage temporel gravé (anti-post-hoc)** : `J0 = 2026-06-09` (mise en service de
la mesure ouverture→clôture + 1 décision notée/jour — le WR tradable n'existe que
depuis cette refonte). Donc **J+60 = 2026-08-08** et **J+90 = 2026-09-07** (fuseau
Europe/Paris). Ces dates sont fixes : aucune renégociation du point de départ.

À **J+60 (2026-08-08)**, Thomas ne trade QUE les cellules 24h satisfaisant :

> **WR tradable ≥ 70 % sur N ≥ 15 paris non-chevauchants**
> (N compté depuis `ref_changed` pour les cellules requalifiées par changement de référence)

Si **aucune cellule** ne passe ce seuil à J+60 : **pas de trading, revue à J+90 (2026-09-07)**.
C'est une **issue valide et attendue** : ne rien trader à J+60 = la discipline qui
protège contre le trading prématuré sur du bruit, pas un échec.

---

## Définition : WR tradable (métrique de décision de trading)

**Formule :**

```
WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif)
```

Les conclusions `non-conclusif` (NC) sont comptées au dénominateur : elles
représentent un pari qui n'a pas pu être résolu, donc une journée de capital
immobilisé sans résultat net. Les inclure au dénominateur pénalise justement les
cellules qui génèrent beaucoup de NC.

### Pourquoi deux métriques distinctes

| Métrique | Formule | Rôle | Où utilisée |
|---|---|---|---|
| **WR conclusif** | VRAI / (VRAI + FAUSSE) | Mesure la justesse directionnelle du moteur sur les cas tranchés | Kill criterion — évalue si le moteur est vivant |
| **WR tradable** | VRAI / (VRAI + FAUSSE + NC) | Mesure la performance nette d'une cellule tradable, NC inclus | Sélection — décide si une cellule vaut la peine d'être tradée |

Le kill criterion s'intéresse à la question : "le moteur prédit-il juste quand il
peut conclure ?" Le WR conclusif répond à cela sans que les NC (souvent hors
contrôle du moteur) polluent le signal sur la justesse directionnelle.

La règle de sélection s'intéresse à une question différente : "si Thomas suit cette
cellule en trading réel, combien de fois sera-t-il gagnant sur l'ensemble des
journées engagées, NC compris ?" Le WR tradable répond à cela.

Ces deux métriques mesurent deux choses légitimement différentes et ne doivent
pas être confondues ni substituées l'une à l'autre. Décision Thomas validée le
2026-06-10 (Lot 2 du brief audit 10/06).

---

## Note critique : non-chevauchement des paris

La règle de sélection porte **exclusivement sur les cellules 24h** (horizon 1 jour).

L'horizon 24h est naturellement non-chevauchant : chaque prédiction émise un jour J
est mesurée à la clôture de J+1, une prédiction émise à J+1 est mesurée à la
clôture de J+2 — les fenêtres de mesure sont disjointes. Pas de correction de
comptage nécessaire sur cet horizon (contrairement aux horizons 7j et 1m qui
souffrent d'autocorrélation forte, voir `KILL-CRITERION.md` section "Note critique :
observations NON-CHEVAUCHANTES").

**Pourquoi limiter la sélection au 24h ?** Les horizons 7j et 1m présentent de
l'autocorrélation entre observations consécutives. Pour atteindre N ≥ 15
observations réellement indépendantes sur ces horizons, il faudrait 15 semaines
(7j) ou 15 mois (1m) de shadow — horizon incompatible avec la prise de décision à
J+60. Le 24h est le seul horizon qui accumule suffisamment d'observations
non-chevauchantes dans la fenêtre shadow.

N ≥ 15 sur l'horizon 24h = 15 jours de marché ouverts avec une conclusion nette
sur la cellule concernée. C'est le seuil minimal de puissance statistique pour
distinguer 70 % d'un coin flip à 50 % avec un intervalle de confiance Wilson 95 %
acceptable (aligné sur la logique de puissance du kill criterion).

---

## `ref_changed` : remise à zéro du compteur N

Pour les cellules dont la **référence de mesure a changé** (nouveau critère dominant,
recalibration de la pondération, changement de source de données — cf. Lot 1 du
brief audit 10/06), l'historique antérieur n'est plus comparable aux observations
récentes.

**Règle :** pour ces cellules, **N repart de zéro à la date `ref_changed`**. Seules
les observations postérieures à cette date entrent dans le calcul du WR tradable
et du compteur N pour la règle de sélection.

Conséquence opérationnelle : si une cellule passe en dessous de N ≥ 15 après
remise à zéro, elle n'est plus éligible à J+60, même si son WR tradable cumulé
depuis l'origine était ≥ 70 %. La discipline vaut dans les deux sens.

---

## Procédure d'application à J+60

1. Snapshot figé : copier `v3/data/events-log.md` et la table de scoring à 00h00
   Europe/Paris le jour J+60.
2. Pour chaque cellule 24h : calculer `WR tradable = VRAI / (VRAI + FAUSSE + NC)`
   en ne comptant que les observations postérieures à `ref_changed` si applicable.
3. Filtrer : garder uniquement les cellules avec **N ≥ 15** observations valides.
4. Appliquer le seuil : ne retenir pour trading que les cellules avec **WR tradable ≥ 70 %**.
5. **Décision écrite, datée, signée Thomas** dans `v3/data/selection-decision-J60.md`.
   Pas de décision orale.
6. Si aucune cellule ne passe : noter "pas de trading, revue à J+90" dans le même
   fichier et ne rien trader.

---

## Ce que cette règle n'est pas

- Elle ne remplace pas le kill criterion (les deux s'appliquent indépendamment).
- Elle ne garantit pas la performance future des cellules sélectionnées.
- Elle ne s'applique pas aux horizons 7j et 1m (non-chevauchement non garanti
  sur la fenêtre J+60).
- Elle ne peut pas être assouplie post-hoc. Si à J+60 le WR tradable d'une cellule
  est à 68 %, la cellule n'est pas sélectionnée. Pas de "c'est proche de 70 %".

---

## Toute modification ultérieure

Toute modification de cette règle doit :

1. Créer un fichier `v3/selection-rule-v2.md` (nouveau fichier, ne pas éditer
   celui-ci).
2. Inclure une **justification écrite** rédigée AVANT consultation des résultats
   du shadow.
3. Être datée et signée Thomas.

Jamais d'édition silencieuse de ce fichier.

---

## Addendum — Redémarrage v2 (2026-06-10)

> Append-only. **Ne modifie PAS le texte de la règle gravée ci-dessus** : précise
> uniquement la portée d'application de `ref_changed` au cutover v2 réel du 10/06.

**Portée du reset = 4 actifs seulement.** Les cellules de **cacao, pétrole,
nasdaq, argent** ont leur **référence de mesure changée** au 2026-06-10 (dédup des
fiches, audit Cowork 10/06 — Lot A) : un critère redondant a été retiré sur chacune,
donc leur signal n'est plus strictement comparable à l'historique antérieur. Pour
ces 4 actifs, **N et le WR tradable repartent de zéro au 2026-06-10** (au sens de la
section « `ref_changed` » ci-dessus).

**Les 8 autres actifs gardent leur historique v1.** or, sp500, eurusd, cac40, café,
vix, blé, cuivre **ne sont PAS reset** : aucune fusion de critère ne les a touchés,
leur signal est inchangé, leur compteur N continue depuis l'origine.

**Pas de reset global.** Le mécanisme décisionnel `is_news_regime` / `ratio_news`
**n'a pas été modifié** → aucun delta de signal hors ces 4 actifs → aucune raison de
remettre à zéro l'ensemble du shadow. Le cutover est **court** (lot unique daté du
même jour, pas un étalement progressif).

**Registre source de vérité** : la liste des cellules reset et leur date
`ref_changed` est tenue dans `v3/data/ref-changed.json`, **clée par
`ticker_principal`** (identifiant stable, robuste à un renommage de l'actif — cf.
leçon L023). C'est ce registre que le Journaliste applique pour l'enforcement
anti-mélange v1/v2 (aucune cellule des 4 actifs ne compte une mesure pré-dédup
avec une mesure post-dédup).

**Impact sur J+60 (2026-08-08, inchangé)** : pour les 4 actifs reset, N compte
depuis le 2026-06-10 ; ils peuvent ne pas atteindre N ≥ 15 à J+60 (issue valide).
Les 8 autres conservent leur N depuis l'origine. La règle de sélection elle-même
(WR tradable ≥ 70 % / N ≥ 15, 24h-only) est **inchangée**.

---

## Addendum — Correctif famille momentum-prix (2026-06-10)

> Append-only. **Ne modifie PAS le texte gravé ni l'addendum « Redémarrage v2 »
> ci-dessus** : étend uniquement la portée du `ref_changed` au correctif de famille
> du 10/06 (même journée, lot postérieur au Lot A).

**Le balayage `momentum-prix-sweep.md` (10/06) a établi que 8/12 fiches n'ont aucun
critère de tendance-prix propre** — incohérent avec la thèse trend-following. Décision
Thomas (phase de création) : ajouter un critère `momentum_prix_20j_<actif>` (z-score
des closes du sous-jacent, signe +1 = suit la tendance) aux **7 fiches commodities/métaux
absentes** : cacao, café, blé, cuivre, pétrole, or, argent. Le cacao réduit aussi
`hf_positioning_flux_options` de 7 → 5 (contrarian COT sur-pondéré, cacao-case-study §4).

**Le reset s'étend à 4 actifs supplémentaires.** café (`KC=F`), blé (`ZW=F`),
cuivre (`HG=F`), or (`GC=F`) voient leur **référence de mesure changée** au 2026-06-10
(nouveau critère dominant ajouté à la fiche) → **N et WR tradable repartent de zéro au
2026-06-10**. cacao (`CC=F`), pétrole (`BZ=F`), argent (`SI=F`) étaient **déjà reset** au
2026-06-10 par l'addendum Lot A ci-dessus : leur cutover du même jour couvre aussi
l'ajout du momentum (pas de double entrée dans `ref-changed.json`, append-only respecté).

**Bilan reset après ce correctif** : 8 actifs reset au 2026-06-10 (cacao, pétrole,
nasdaq, argent, café, blé, cuivre, or). 4 actifs gardent leur historique v1 (sp500,
eurusd, cac40, vix — non touchés par le correctif famille ; les indices et l'EUR/USD
sont **hors périmètre de ce tour**, traités plus tard / Ticket C).

**Mécanisme de scoring INCHANGÉ** : aucune nouvelle mécanique de calcul (le moteur
z-score déjà les closes d'un symbole, cf. `sox_trend_5j`), `weighting.yml` non touché,
formules de normalisation et `seuils_reussite_pct` inchangés. La règle de sélection
elle-même (WR tradable ≥ 70 % / N ≥ 15, 24h-only) reste **inchangée**.

## Addendum — Cutover momentum v3 (2026-06-11)

> Append-only. **Ne modifie PAS le texte gravé ni les addendums « Redémarrage v2 »
> et « Correctif famille momentum-prix » du 10/06.** Acte le cutover réel du momentum
> v3 corrigé (vague 1 + vague 2), qui atterrit au bulletin **11/06 7h**.

**Le momentum-prix v3 « déployé » le 10/06 était fonctionnellement identique à la v1**
(routé vers le z-score du NIVEAU de close, un laggard — constat bloquant A1 de la
concertation `momentum-family-verdict.md`). Les corrections moteur + fiches atterrissent
ce soir, premier signal effectif au **bulletin 11/06 7h** :
- **A1 (moteur)** : `momentum_prix_20j_*` routé vers la VRAIE variation 20j
  (`close[t]/close[t-20]-1`) puis z-score de la **série de rendements** (60j) — plus le
  niveau. Voir `_twelve_variation_zscore`.
- **A2 (moteur)** : cap anti-inversion **aveugle au momentum** (`cap = |quant − contrib_momentum|×0,8`) — le momentum décide la direction, jamais l'étouffement des news.
- **A3 (fiches)** : poids momentum ramenés à **≤6 (prove-first)** : cacao 9→6, café/blé/cuivre 8→6, pétrole/or/argent 7→6.
- **A6 (moteur)** : momentum exclu du calcul de couverture (préserve le filet news 📰).
- **A8 (fiches)** : fin de la famille — EUR/USD (`EUR=X`, poids 5), S&P 500 (proxy SPY, poids 4), Nasdaq (proxy QQQ, poids 4), CAC 40 (`^FCHI`, poids 4). RSI indices poids 2 **conservé**.
- **A9** : VIX **exclu** (mean-reverting) — seul actif sans reset.

**Reset : 11 actifs au 2026-06-11.** Les 8 entrées existantes de `ref-changed.json`
(cacao, pétrole, nasdaq, argent, café, blé, cuivre, or) voient leur `ref_changed`
**avancé de 2026-06-10 → 2026-06-11** (justification gravée dans CHANGELOG.md, comme
l'exige le `_doc` du registre) : le momentum corrigé change leur référence de mesure, les
cellules reset repartent à zéro quand il atterrit (mémo S5). S'y ajoutent **3 nouvelles
entrées** : EUR/USD (`EUR=X`), S&P 500 (`^GSPC`), CAC 40 (`^FCHI`). **Seul `vix`
(`^VIX`) garde son historique v1.**

**Conséquence sur N ≥ 15 à J+60 (= 2026-08-08).** Les 11 actifs reset comptabilisent
leurs observations à partir du 2026-06-11 seulement : la fenêtre utile est **~58 jours
ouvrés**, ils peuvent ne pas atteindre N ≥ 15 à J+60 (issue valide, pas un échec). Seul
`vix` conserve un N pré-11/06 immédiatement comparable. La règle de sélection (WR
tradable ≥ 70 % / N ≥ 15, 24h-only) reste **inchangée**.

**Mesure (A5, shadow)** : une métrique « FAUSSES aux retournements » (distincte du WR,
zéro impact décisionnel) est ajoutée au Bilan du jour pour comparer avant/après momentum
v3 le taux d'erreurs aux points de retournement. Elle n'altère NI le scoring, NI cette
règle, NI le kill-criterion.


---

## Addendum — 2026-06-10 (soir) : lot autopilote « sources & critères » (S6)

- **VIX rejoint le reset du 2026-06-11** (critère `gap_rv_iv` poids 5 ressuscité — calculable depuis SPY+CBOE déjà ingérés). **À compter du 11/06, les 12 actifs sont en ère v2** ; plus aucune cellule ne porte d'historique v1.
- Critères ressuscités le même jour : café `usd_brl` (poids 6, Twelve), EUR/USD `balance_commerciale_ez` (poids 3, Eurostat) — actifs déjà reset au 11/06, même ère.
- Conséquence N≥15 à J+60=2026-08-08 : inchangée (déjà documentée pour les 11 autres) — désormais valable pour les 12.


---

## Addendum — 2026-06-15 : critères des actifs continus sur le prix le plus frais (fin de l'angle mort overnight/week-end)

**Défaut démontré lundi 15/06.** Pour l'or (`GC=F`), le prix dont le système dispose à 7h le lundi = **exactement le close de vendredi** (capteur `shadow_gap_overnight ≈ 0`). Les critères de niveau/momentum/RSI s'appuient sur `close[-1]` (close J-1) → le système **ignorait tout mouvement overnight/week-end** sur les actifs cotés en **continu** (or, argent, pétrole, cuivre, cacao, café, blé, FX) et pouvait recommander un SHORT prioritaire contre un actif ayant déjà bougé de +2 %, invisible pour lui. Légitime pour S&P/Nasdaq/CAC (marché cash **fermé** à 7h → close J-1 = dernier prix réel), **faux** pour les continus.

**Correctif (VOLET A).** Pour les actifs du groupe **continu** uniquement (source : `mesure_ouverture.actif_group`), si un prix temps réel **plus frais** que `close[-1]` est disponible au run, il est **appendé** comme dernier point de la série de closes (ou remplace `close[-1]` si même jour). Point d'injection unique : `criteres_calculator.fetch_twelve_series` → tous les critères à série de closes (z-score niveau, variation 20j, RSI, perf 5j) en bénéficient. **Dégradation sûre** : prix frais absent OU non plus récent que `close[-1]` (cas Twelve gratuit le lundi 7h) → **série inchangée, comportement actuel exact** (zéro invention). Les non-continus (S&P/Nasdaq/CAC/VIX) ne sont **jamais** touchés.

**Visibilité (VOLET B).** Sous la « Sélection du jour », un drapeau ⚠️ signale un actif continu qui **bouge à contre-sens** de la conclusion depuis la dernière clôture vue (`shadow_gap_overnight` ≥ 0,8 % et de sens opposé). Anti-bruit : gap ≈ 0 ou aligné → rien.

**Reset : 8 actifs continus au 2026-06-15** (or `GC=F`, argent `SI=F`, pétrole `BZ=F`, cuivre `HG=F`, cacao `CC=F`, café `KC=F`, blé `ZW=F`, EUR/USD `EUR=X`). Leur `ref_changed` avance **2026-06-11 → 2026-06-15** (justification gravée dans CHANGELOG.md, comme l'exige le `_doc` du registre) : le signal change quand le prix frais est intégré. **3e reset des continus — coût assumé, vrai défaut corrigé.** Les non-continus (`^GSPC`, `^IXIC`, `^FCHI`, `^VIX`) gardent leur `ref_changed` 2026-06-11. La règle de sélection (WR tradable ≥ 70 % / N ≥ 15, 24h-only) reste **inchangée** ; les poids/seuils des fiches ne sont **pas** touchés. 

---

## Addendum — 2026-06-16 : or/argent/Brent servis par le symbole Twelve natif (fin du fallback yfinance caché)

**Constat (sondage live API Twelve, clé réelle).** Les futures Yahoo `GC=F`/`SI=F`/`BZ=F` renvoient **404** sur Twelve `/time_series`. Le système les obtenait jusqu'ici via un **fallback yfinance silencieux** — angle mort de provenance. Twelve sert ces actifs **uniquement sous leurs symboles spot natifs**, vérifiés au bon niveau : or `XAU/USD` (close 4326 ≈ niveau système ~4325), argent `XAG/USD` (~70), Brent `XBR/USD` (~83).

**Changement (présentation/source, pas de scoring).** La couche de traduction `market_data._TICKER_MAP` interroge désormais Twelve sous `XAU/USD`, `XAG/USD`, `XBR/USD` pour le **prix ET l'historique** → Twelve devient la **source unique** de ces 3 actifs (le fallback yfinance n'est plus déclenché puisque Twelve répond). Le **`ticker_principal` des fiches reste `GC=F`/`SI=F`/`BZ=F`** (identifiant interne stable, L023) — seul le symbole INTERROGÉ change.

**Reset.** Le niveau spot diffère légèrement du future → z-scores/momentum bougent → **le signal change**. `ref_changed` de `GC=F`, `SI=F`, `BZ=F` avance **2026-06-15 → 2026-06-16** (`ref-changed.json`, append-only). **Cuivre/cacao/café/blé : INCHANGÉS** — Twelve ne sert PAS ces futures au bon niveau (`XCU/USD`, `COCOA`, `COFFEE`, `WHEAT` = 404 ; ETF au mauvais niveau écartés, zéro invention) → ils gardent yfinance et leur `ref_changed` 2026-06-15. La règle de sélection (WR tradable ≥ 70 % / N ≥ 15, 24h-only) et **aucun poids ni seuil** ne sont touchés.

**Provenance.** Chaque cycle logge désormais la source réellement utilisée par symbole (`twelve_native` / `yfinance_fallback` / `stooq_fallback`) dans `criteres-health.md` (bloc « Provenance des prix ») — fin de l'angle mort.
