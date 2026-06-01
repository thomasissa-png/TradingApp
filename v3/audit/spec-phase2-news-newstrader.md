# Spec desk — Phase 2 news (TradingApp v3)

Auteur : news trader senior (desk macro/commodities). Périmètre tranché par Thomas :
**lot cœur**, classification de nature par **DeepSeek**, activation **directe en shadow**.

Brief : donner à chaque news une **carte d'identité** pour distinguer une news *fraîche
structurelle* (doit peser) d'une *vieille déjà digérée / compte-rendu / archive re-publiée*
(ne doit plus peser). Aujourd'hui DeepSeek sort 1 direction/actif sans notion de nature ni de
fraîcheur ; `reliability` est figé à `confirmed` (override du cap, non discriminant) ; le cutoff
lookback existe (`triggers_classifier.py:743`) mais ne distingue pas la nature.

> Convention : L = actif monte, S = baisse. Sources des exemples : `v3/data/events-log.md`
> (triplets + colonnes materiality/reliability), `v3/audit/revue-plan-horizon-newstrader.md`,
> `v3/config/fiches/petrole.yml`.

---

## 0. TL;DR desk

- 4 classes de `nature` : `structurel` (driver de tendance), `ponctuel` (choc court),
  `deja_cote` (compte-rendu du passé), `verbal` (déclaration/rumeur).
- Chaque classe pilote un **coefficient d'impact par horizon** (24h/7j/1m) — c'est la nature,
  pas un decay global, qui module la courbe.
- **Gate de fraîcheur** : une news ne peut PRIMER (override du cap anti-inversion) que si
  `fraîcheur ≤ 48h` **ET** `nature ∈ {structurel, ponctuel}` **ET** `materiality = high`
  **ET** `reliability ∈ {confirmed, reported}`. Sinon : plafonnée, jamais d'inversion.
- DeepSeek doit produire 3 champs nouveaux : `nature`, `event_id`, `event_date`.
- Risque #1 réglé : `reliability` figé `confirmed` devient inoffensif car l'override ne dépend
  plus de lui seul mais du couple **nature × fraîcheur × materiality**.

---

## 1. Taxonomie `nature` (4 classes)

La `nature` répond à UNE question desk : *cette news crée-t-elle un flux directionnel
forward, et sur quelle durée ?* Elle ne dit PAS le sens (ça reste le triplet
`ACTIF:DIR:materiality`), elle dit le **type de catalyseur**. 4 classes, exclusives.

### 1.1 `structurel` — driver de tendance durable

Modifie le **régime offre/demande** ou un **équilibre de marché** sur des semaines/mois. Le prix
met du temps à l'intégrer entièrement → l'effet doit MONTER ou TENIR vers 1m (comme la courbe
OPEC+ de `petrole.yml` : pertinence 0.3 → 0.9 → 1.0).

Exemples réels (events-log) :
- **Fermeture du détroit d'Ormuz le 28 février** (L101, L111, L116) : « closure of Strait of
  Hormuz », ~20% de l'offre mondiale coupée. Choc d'offre dur ET persistant → structurel.
  Tient à 1m (le brut est resté à $94+ pendant des semaines, cf. L118).
- **Fracture OPEC+ / départ des Émirats** (L177) : `BRENT:SHORT:medium` — rupture de la
  discipline de quota = oversupply structurel. Effet qui se déploie sur le cycle, pas intraday.
- **Mauvaises récoltes café Brésil + Vietnam** (L22/L155) : `COFFEE:LONG:high` — déficit
  d'offre saisonnier durable. Structurel softs.

### 1.2 `ponctuel` — choc court, s'amortit vite

Événement isolé, daté, sans changement de régime. Fort à chaud (24h), décroît vers 1m (comme la
géopol Moyen-Orient de `petrole.yml` : 0.6 → 0.6 → 0.2). C'est un *spike*, pas une *tendance*.

Exemples réels :
- **Frappe sur Beyrouth / hôpitaux Gaza** (L28/L29) : `BRENT:LONG`, frappe isolée. Prime de
  risque qui retombe si pas d'escalade sur l'offre. Ponctuel.
- **Drones ukrainiens sur port/dépôt pétrolier russe** (L171) : `BRENT:LONG:medium` — outage
  localisé, réparable. Choc court.
- **Surprise hebdo EIA/API** (fiche `petrole.yml` crit. 1-2, pertinence 1.0 → 0.3 → 0.1) :
  chiffre de stocks > 2σ. Bouge le 24h, oublié à 1m. Ponctuel par construction.

### 1.3 `deja_cote` — compte-rendu du passé, PAS un catalyseur

Décrit un mouvement **déjà réalisé** ou un état **déjà connu du marché**. Contenu forward ≈ 0 :
le prix a déjà bougé, ou la news re-publie une info que le marché a digérée. Piège desk classique
(« le S&P a monté 9 semaines » vendu comme signal haussier alors que c'est de l'histoire).

Exemples réels :
- **« S&P500 record with 8/11 sectors down »** (L182) : compte-rendu de séance. Le record est
  *déjà coté*. `SP500:LONG:medium` ici est une erreur typique — descriptif passé, flux forward nul.
- **« Brent posts biggest monthly loss in six years »** (L69) / **« worst month since 2020 »**
  (L85) : bilan mensuel. Le mouvement est *fait*. Re-jouer ce S serait re-compter le passé.
- **« Oil drops 20% from 2026 peak »** (L39) : narration de baisse déjà survenue. Pas un
  catalyseur forward — au mieux une cause (deal Iran) déjà tracée ailleurs.
- **Record disconnect in volatility spread** (L166, `materiality low`) : état de marché
  descriptif, aucun flux directionnel. Déjà coté.

### 1.4 `verbal` — déclaration / rumeur / intention, flux nul

Mots, pas faits. « envisage de », « very close to », « mulls », commentaire de banquier central
sans décision. Pas de changement matériel d'offre/demande → contribution faible, jamais d'override.

Exemples réels :
- **« US VP Vance says US and Iran *very close* to deal but *not there yet* »** (L26) : intention,
  pas accord signé. Verbal.
- **« Trump *évalue* une proposition de cessez-le-feu »** / **« Trump *mulls* deal »** (L43/L181) :
  conditionnel, réversible. Verbal (le triplet `BRENT:SHORT:medium` doit être dégradé).
- **Fed Goolsbee / Bowman speakers** (L56, L31 du log brut) : commentaire de gouverneur, pas de
  décision FOMC. Verbal — flux directionnel dur nul.
- **Exxon executive *warns* prices could spike to $150-160** (L167) : prévision d'un dirigeant,
  pas un fait d'offre. Verbal/opinion, malgré `materiality high` annoncé → à dégrader.

> Frontière `ponctuel` vs `verbal` : un **fait daté** (frappe, outage, chiffre publié) = ponctuel.
> Une **parole/prévision** (warn, mull, say) = verbal, même si l'acteur est crédible.
> Frontière `structurel` vs `deja_cote` : OPEC+ qui *décide* un cut = structurel ; un article qui
> *raconte* que le prix a monté après un cut passé = deja_cote.

---

## 2. Règle desk d'impact par nature (coefficients par horizon)

Principe : la `nature` fournit un **multiplicateur d'impact news par horizon**, appliqué à la
contribution du critère news AVANT entrée dans la somme du score. Ce n'est PAS un decay global
uniforme (cf. revue : NO-GO, ça écrase la courbe OPEC qui doit monter à 1m). C'est un coefficient
*par classe* qui épouse la forme déjà codée dans les `pertinence` des fiches, mais rendue
data-driven par event au lieu de figée par critère.

Formule (extension de `scoring_analyste.py:352`) :

```
contribution(H) = valeur_norm × poids × pertinence[H] × coef_nature[H] × signe
```

### Coefficients indicatifs `coef_nature[H]`

| `nature`     | 24h  | 7j   | 1m   | Forme desk | Ancrage fiche |
|--------------|------|------|------|------------|---------------|
| `structurel` | 0.8  | 1.0  | 1.0  | monte puis tient — driver de tendance | OPEC+ 0.3/0.9/1.0 |
| `ponctuel`   | 1.0  | 0.5  | 0.15 | spike qui s'amortit vite | géopol 0.6/0.6/0.2, EIA 1.0/0.8/0.3 |
| `deja_cote`  | 0.1  | 0.05 | 0.0  | quasi-ignoré, flux forward nul | — (passé, pas un critère) |
| `verbal`     | 0.3  | 0.2  | 0.1  | faible partout, réversible | — (parole, pas un fait) |

Lectures desk :
- **`structurel`** sous-pondéré à 24h (0.8) : un changement de régime n'explose pas le prix le
  jour même, il se déploie. Plein effet à 7j/1m. Ex. fracture OPEC+ (L177) : peser plus à 1m
  qu'à 24h.
- **`ponctuel`** : plein effet à chaud (1.0 à 24h), divisé par ~7 à 1m (0.15). Ex. frappe Gaza
  (L28) : prime de risque qui retombe. Combiné à la `pertinence` géopol déjà décroissante, on
  obtient un amortissement net à 1m (0.15 × 0.2 = 0.03) — voulu, pas du sur-amortissement
  accidentel car c'est le SEUL multiplicateur ajouté (le decay global, lui, en empilait deux).
- **`deja_cote`** : ~0. Ex. « S&P 8/11 sectors down » (L182), « biggest monthly loss » (L69)
  ne doivent rien injecter forward. C'est ce qui neutralise les faux signaux Or-24h / VIX-1m
  sans casser Ormuz.
- **`verbal`** : plafond bas (0.3 max). Ex. Vance « very close » (L26), Trump « mulls » (L43) :
  un flux, oui, mais faible et révisable au prochain tweet.

> Note d'implémentation : `coef_nature` ne remplace PAS la `pertinence` par critère, il la
> **module**. Une news `verbal` sur le critère OPEC (pertinence 1.0 à 1m) reste plafonnée par son
> coef 0.1 → 0.1 net. Une news `structurel` sur le même critère garde 1.0. La nature corrige
> donc la pertinence *figée* du critère quand l'event réel ne correspond pas à la nature présumée
> du critère (ex. une ligne L2=OPEC qui est en fait un compte-rendu, pas une décision).

---

## 3. Gate de fraîcheur (override du cap anti-inversion)

Rappel du cap existant : `_has_contradictory_high_impacts` plafonne déjà la conviction
(high→medium) quand une news contredit le bloc quant. L'override = la permission, pour une news,
de **dépasser ce cap et inverser** le score. Aujourd'hui cet override s'appuie sur `reliability`
seul, figé `confirmed` → toujours ouvert (= jamais discriminant). On le remplace par un gate
multi-conditions.

### Règle d'override (4 conditions CUMULATIVES)

Une news ne PRIME (peut inverser/dépasser le cap quant) que si **les 4** sont vraies :

1. **Fraîcheur ≤ 48h** — `now − event_date ≤ 48h`. Au-delà, « LE PRIX NE MENT PAS » : le marché
   a déjà arbitré, la news ne peut plus surprendre. Seuil 48h = 2 séances pleines, assez pour
   couvrir un week-end news (frappe vendredi → ouverture lundi). On calcule sur `event_date`
   (date du fait), PAS sur l'âge de la ligne de log — une archive re-publiée garde sa vieille
   `event_date` et échoue donc le gate (cf. Ormuz « le 28 février » re-cité en avril, L101/L111).
2. **`nature ∈ {structurel, ponctuel}`** — un `deja_cote` ou un `verbal` ne prime JAMAIS, quelle
   que soit sa fraîcheur. Un compte-rendu frais reste un compte-rendu.
3. **`materiality = high`** — choc matériel sur l'offre/demande, pas un single-name ni un bruit.
4. **`reliability ∈ {confirmed, reported}`** — pas `rumor`. (Une fois `reliability` réellement
   produit par DeepSeek, cf. §5 — tant qu'il est figé `confirmed`, cette condition est neutre
   mais les 3 autres tiennent le gate.)

Si les 4 ne sont pas réunies → la news est **plafonnée** à la contribution nette du bloc quant
(ne peut pas la dépasser), **jamais interdite**. Défaut système = la news n'inverse pas ; elle
n'inverse que sous les 4 gates.

### Articulation fraîcheur × nature × matérialité (cas réels)

| News (events-log) | Fraîcheur | nature | materiality | Override ? |
|---|---|---|---|---|
| Ormuz fermé, frappe Natanz (frais) | ≤48h | structurel | high | **OUI** — doit primer, prix gappe |
| Fracture OPEC+ EAU (L177) | ≤48h | structurel | high* | **OUI** si matérialité confirmée |
| Frappe Gaza isolée (L28) | ≤48h | ponctuel | high | OUI court terme, mais coef_nature l'amortit à 1m |
| « S&P 8/11 sectors down » (L182) | ≤48h | deja_cote | medium | **NON** — nature exclut |
| Vance « very close to deal » (L26) | ≤48h | verbal | medium | **NON** — nature + materiality excluent |
| Ormuz « le 28 février » re-cité (L101) | >48h | structurel | high | **NON** — fraîcheur échoue (déjà digéré) |
| Exxon « warns $150-160 » (L167) | ≤48h | verbal | high→dégrader | **NON** — verbal exclut, malgré high annoncé |

*La fracture OPEC+ est `reported` materiality high dans le log : si confirmée, override légitime.

> Le gate règle les deux pièges symétriques : laisse passer le **choc d'offre frais**
> (Ormuz) que la revue veut absolument préserver, et bloque le **compte-rendu / la rumeur /
> l'archive** (S&P streak, Vance, Ormuz-re-publié) qui sur-pesaient à tort.

---

## 4. Ce que DeepSeek doit produire

### 4.1 Champs à ajouter à l'extraction

Schéma actuel = 7 champs + triplets `ACTIF:DIR:materiality` + `materiality` + `reliability`.
Phase 2 ajoute **3 champs** par event :

| Champ | Type | Valeurs | Rôle |
|---|---|---|---|
| `nature` | enum | `structurel` \| `ponctuel` \| `deja_cote` \| `verbal` | pilote `coef_nature[H]` (§2) + gate (§3) |
| `event_id` | string stable | hash du fait (acteur+action+date, pas du titre RSS) | dé-duplication : une news re-publiée = même `event_id` → comptée une fois |
| `event_date` | date ISO | date du **fait**, pas de la publication RSS | calcul de fraîcheur réel (§3 cond. 1) |

`event_id` doit être stable à la **reformulation** : « Strait of Hormuz closure Feb 28 » et
« closure of Strait of Hormuz » (L101 vs L111) = même `event_id`. Construire l'id sur
acteur + action + `event_date`, jamais sur le texte du titre.

### 4.2 Consignes de prompt DeepSeek (pièges desk)

À injecter dans le SYSTEM_PROMPT d'extraction :

1. **« Un compte-rendu n'est pas un catalyseur. »** Si la phrase DÉCRIT un mouvement déjà
   survenu (« a monté de X% », « biggest monthly loss », « record », « 8/11 sectors down »,
   « posts », « set for worst month ») → `nature = deja_cote`. Le passé ne prédit pas le forward.
2. **« Une rumeur ou une intention n'est pas un fait. »** Verbes au conditionnel ou de parole
   (« mulls », « envisage », « very close to », « warns », « says », « could », « considers »,
   « pending approval ») → `nature = verbal`, et `reliability ≤ reported` (jamais `confirmed`).
3. **« Un changement de régime durable ≠ un choc isolé. »** Décision d'offre/demande qui tient
   des semaines (quota OPEC+ décidé, fermeture de détroit, déficit de récolte, sanctions
   structurelles) → `structurel`. Événement daté sans changement de régime (frappe isolée,
   chiffre hebdo, outage réparable) → `ponctuel`.
4. **« Date le FAIT, pas l'article. »** `event_date` = quand le fait s'est produit (ex. « le 28
   février »), pas quand l'article paraît. Si l'article ré-évoque un fait ancien, garder la date
   ancienne → la news sera correctement jugée non-fraîche.
5. **« materiality = impact sur l'offre/demande, pas sur l'émotion du titre. »** Un dirigeant qui
   *prédit* $150 (L167) n'est pas `high` matériel : c'est une opinion → dégrader. `high` est
   réservé aux faits qui déplacent réellement l'équilibre (Ormuz, cut OPEC+, déficit dur).

---

## 5. Risque #1 : `reliability` figé `confirmed`

### Le problème

`reliability` est figé à `confirmed` pour TOUS les events (override du cap, non discriminant).
Conséquence : la seule condition qui ouvre l'override d'inversion est *toujours vraie*. Donc
n'importe quelle news — y compris un compte-rendu (« S&P 8/11 down ») ou une rumeur (« very
close to deal ») — peut, en théorie, dépasser le cap quant et inverser le score. C'est la cause
des sur-pondérations Or-24h / VIX-1m relevées dans la revue.

### Pourquoi nature + fraîcheur rend l'override fiable

On **retire à `reliability` son rôle de gardien unique**. L'override ne dépend plus d'un seul
champ corrompu, mais du **couple `nature × fraîcheur × materiality`** (§3), où :

- `nature` est **discriminante par construction** : `deja_cote` et `verbal` sont exclus du gate
  quoi qu'il arrive. Même si `reliability=confirmed` (figé), un compte-rendu ne prime jamais.
- `fraîcheur` est **calculée sur `event_date` réel** : une archive re-publiée échoue le gate
  même si elle est marquée `confirmed`.
- `materiality=high` filtre le bruit single-name.

Résultat : tant que DeepSeek ne produit pas un vrai `reliability`, le gate **tient quand même**
sur 3 conditions sur 4. Le champ figé devient **inoffensif** au lieu d'être un trou béant.

### Trajectoire de durcissement (2 temps)

1. **Phase 2 (maintenant)** : `nature` + `event_id`/`event_date` produits par DeepSeek. Gate à
   3 conditions effectives (`reliability` neutre). L'override redevient discriminant
   immédiatement, sans dépendre du fix `reliability`.
2. **Suite** : DeepSeek produit un `reliability` réel (consigne prompt #2 : `verbal` ⇒
   `reliability ≤ reported`). La 4ᵉ condition s'active, le gate passe à 4/4. Pas un prérequis
   Phase 2 — un renforcement.

> En clair : on ne *répare* pas `reliability` en Phase 2, on le **rend non-bloquant** en
> déplaçant la décision sur des signaux qu'on contrôle (nature, date du fait). Le champ figé
> ne peut plus ouvrir l'override tout seul.

---

## 6. Activation shadow & handoff

### Activation directe en shadow (décision Thomas)

`nature` + `coef_nature[H]` + gate de fraîcheur sont calculés et **loggués**, mais ne modifient
PAS le score servi en prod tant que le shadow tourne. On compare en parallèle :
- `score_prod` (logique actuelle, sans nature),
- `score_shadow` (avec `coef_nature` + gate override).

Critères de promotion shadow → prod (à valider sur run réel) :
- Les events `deja_cote`/`verbal` voient leur contribution forward tomber (~0) sans casser les
  conclusions VRAIES déjà bonnes.
- Les chocs `structurel` frais (type Ormuz) gardent / gagnent leur capacité à primer à 7j/1m.
- Pas de régression sur les triplets `confirmed high` légitimes (OPEC+ cut, déficit récolte).

### Champs à trancher avec Thomas

- **Seuil de fraîcheur** : 48h proposé (2 séances + week-end). Alternative discutable : 72h pour
  les softs/agri à diffusion plus lente. Défaut retenu : **48h**.
- **Valeur du plafond hors-override** : news ≤ contribution nette du bloc quant (proposé) vs
  facteur ×1.5. Défaut retenu : **≤ contribution nette quant**.
- **`coef_nature` `ponctuel` à 1m** : 0.15 proposé ; à calibrer si trop sévère sur les chocs
  géopol qui s'enkystent (escalade prolongée → re-classer en `structurel` plutôt que gonfler le coef).

### Handoff (fichiers concernés)

- `v3/scripts/extractor.py` — produire `nature`, `event_id`, `event_date` + consignes prompt §4.2.
- `v3/scripts/synthese_directionnelle.py` — propager `nature`/`event_date`, appliquer le gate §3.
- `v3/scripts/triggers_classifier.py` — `coef_nature[H]` dans la contribution (`:352` côté
  scoring), fraîcheur sur `event_date` réel (vs cutoff `:743`), dé-dup par `event_id`,
  généraliser `_has_contradictory_high_impacts` en cap vs prix.
- `v3/config/fiches/*.yml` — inchangées : la `pertinence` par critère reste la base, `coef_nature`
  la module (pas de doublon avec un decay global — cf. revue, NO-GO confirmé).
- `v3/data/events-log.md` — 3 colonnes ajoutées (`nature`, `event_id`, `event_date`).

### Décisions

- **GO** : taxonomie `nature` 4 classes, `coef_nature[H]`, gate override 4 conditions, 3 champs
  DeepSeek, activation shadow directe.
- **NO-GO** (rappel revue) : decay global uniforme, interdiction sèche d'inversion.
- **Non couvert ici** : calibration chiffrée finale des `coef_nature` par actif (à faire sur run
  shadow), production d'un `reliability` réel (renforcement post-Phase 2).
