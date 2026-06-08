# Audit du JOURNALISTE (agent de mesure) — regard News Trader senior

> Auteur : News Trader senior (15 ans desk macro/commodities). Date : 2026-06-08.
> Périmètre : `v3/scripts/journaliste.py` (+ `run_journaliste.py`), sorties
> `v3/data/performance.md`, `v3/data/measures-log.jsonl`, decision-log
> `v3/data/decision-log/2026-06-08-0704.jsonl`, fiches `seuils_reussite_pct`.
> Question posée par Thomas : « la mesure est très légère — mesure-t-elle VRAIMENT
> si le call directionnel était bon, au sens d'un desk ? »

## VERDICT : À RENFORCER

La plomberie est honnête (entry-lock, échéance figée, zéro look-ahead, zéro
invention, non-chevauchant + Wilson). Mais **ce que la mesure mesure** ne
correspond pas encore à « j'étais dans le bon sens d'une vague exploitable sur
turbo ». Trois trous structurels font qu'un score à 95 % peut cohabiter avec un
call qu'un desk jugerait médiocre. Détail ci-dessous.

---

## 1. Ce que fait la mesure (rappel factuel)

- Compare **prix d'émission** (stampé au run via `fetch_twelve_price`) au **prix
  courant** à l'échéance. `delta_pct = (courant - émission)/émission`.
- VRAI si `|delta| > seuil[horizon]` ET dans le sens prédit ; FAUSSE si au-delà
  du seuil dans le sens opposé ; non-conclusive si `|delta| ≤ seuil` ;
  suivi-interrompu si un prix manque.
- Seuils `seuils_reussite_pct` par actif/horizon (ex. Or 24h=0,5 % / 7j=1,3 % /
  1m=3,0 % ; VIX 24h=3 % ; Pétrole 24h=1,0 %).
- KPI = taux brut (chevauchant, indicatif) + **taux_eff non-chevauchant** +
  Wilson low + Brier. Éligible si N_eff≥15, taux_eff≥70 %, Wilson_low>50 %.

C'est propre côté intégrité. Le problème est la **définition du « bon call »**.

---

## 2. Les 3 trous qui me gênent le plus (desk)

### TROU #1 — Mesure binaire SANS MAGNITUDE : le sens compte, l'amplitude est jetée

La mesure est un **bit** (VRAI/FAUSSE) dès qu'on franchit le seuil. Une fois
au-delà du seuil, **+0,51 % et +9 % comptent pareil** (Or 24h). Un desk ne
raisonne jamais comme ça : un call directionnel « bon » qui rapporte 9 % et un
call « bon » qui frémit à 0,51 % au-dessus du seuil n'ont pas la même valeur, et
surtout l'asymétrie gain/perte n'est jamais mesurée.

Conséquence visible dans `performance.md` :
- **Or 24h = 100 %**, **EUR/USD 24h = 100 %**, **Pétrole 24h = 92,9 %** : ces
  taux disent « bon sens souvent » mais **ne disent rien sur combien**. On ne
  sait pas si la tendance suivie était large (exploitable sur turbo) ou un
  filet d'eau juste au-dessus du seuil.
- Inversement **Cuivre 24h = 5,6 %**, **Cacao 24h = 0 %**, **S&P 24h = 5 %** :
  on ne sait pas si les « FAUSSE » sont de gros contre-sens (cher sur turbo à
  levier) ou des micro-faux à 0,9 % (négligeables). Pour un trader, la
  différence est **toute la gestion du risque**.

Ce qui manque : une **amplitude réalisée moyenne du bon sens** (gain moyen quand
VRAI) ET une **amplitude moyenne du contre-sens** (perte moyenne quand FAUSSE),
voire un proxy d'**expectancy** (espérance) = `P(VRAI)·gain_moyen −
P(FAUSSE)·perte_moyenne`. Sans ça, le taux de réussite est un **hit-rate aveugle
au P&L** : on peut avoir 70 % de bons sens et perdre de l'argent (les 30 %
faux = gros contre-mouvements, les 70 % vrais = frémissements). Le champ
`realized_pct` EXISTE dans `measures-log.jsonl` mais **n'est agrégé nulle part**
dans les KPI — la donnée est là, elle n'est pas exploitée.

### TROU #2 — Le prix d'émission n'est PAS un prix d'entrée tradable ; le seuil VRAI couvre à peine un frémissement, pas un mouvement net de frais+spread+levier

Trois sous-problèmes qui font qu'un VRAI à la mesure ≠ un trade gagnant au desk :

**(a) Prix d'émission = dernier tick au moment du run, pas un close officiel.**
`stamp_prix_emission` appelle `fetch_twelve_price(ticker)` qui renvoie un simple
`float` « dernier prix » (vérifié dans `criteres_calculator.py`). Le bulletin de
7h CET stampe un prix **pré-ouverture US / mi-séance Asie selon l'actif** ; celui
de 18h un prix **post-clôture Europe**. La mesure compare donc deux **snapshots
intraday hétérogènes** pris à des heures différentes du cycle de marché — pas
deux clôtures comparables. Le Mémo de reprise note d'ailleurs « ancrage clôture
EXACT » comme raffinement NON FAIT.

**(b) Gap d'ouverture mal géré.** Pour les actions/indices (S&P, Nasdaq, CAC), le
turbo réel est entré à l'**ouverture** du lendemain, pas au dernier tick de la
veille. Si le sous-jacent gappe à l'ouverture, le delta mesuré
(courant−émission) inclut un gap **sur lequel le trader n'a jamais pu entrer au
prix d'émission**. La mesure peut donc créditer (ou débiter) un mouvement
non-capturable. Ce n'est pas neutralisé.

**(c) Le seuil VRAI est un seuil de "mouvement détectable", pas de "mouvement
exploitable sur turbo".** Or 24h = **0,5 %**, CAC 24h = 0,5 %, EUR/USD 24h = 0,4 %.
Sur un **turbo à levier** (le produit réel de Thomas chez Bourse Direct), il faut
soustraire **spread d'entrée/sortie + écart de financement + la barre de
knock-out**. Un mouvement de 0,5 % du sous-jacent, amplifié par le levier, est
**à peine au-dessus du bruit** une fois les frais payés. Donc **un VRAI au seuil
actuel n'est pas garanti d'être un trade vert**. Le seuil mesure « le marché
a-t-il un peu bougé dans mon sens », pas « le mouvement était-il assez net pour
gagner net de frais sur turbo ». Le seuil devrait être **calé sur le coût rond
de transaction du turbo**, pas sur la volatilité minimale détectable.

**Filet anti-mesure dégénérée présent mais partiel** : `prix_courant ==
prix_emission` → non-conclusive (bien). Mais l'égalité EXACTE est rare ; un
prix figé qui bouge d'un tick d'arrondi passe à travers. Et la date du tick
n'étant jamais renvoyée par `fetch_twelve_price`, le **verrou look-ahead est
latent (inactif en prod)** — le code le dit lui-même (« verrou latent mais
sûr »). Donc en cas de cache périmé / week-end mal géré côté fournisseur, rien
ne refuse réellement la mesure côté date.

### TROU #3 — Le call 7j et 1m n'est quasiment jamais jugé de façon significative : ils sont structurellement non-mesurés

L'objectif NON NÉGOCIABLE du projet est la **tendance** (7j/1m, c'est le cœur du
trend-following). Or c'est précisément là que la mesure est la plus faible :

- **Échéance calendaire brute** pour 7j et 1m (`bulletin_date + 7` / `+ 30`),
  sans report jour-ouvré (seul 24h est reporté). Un call 7j émis un mercredi
  échoit le mercredi suivant ; un call 1m peut échoir un week-end/férié →
  comparé à une clôture figée. Le code l'assume (« bruit week-end négligeable »)
  mais sur 1m une échéance qui tombe sur un lundi férié US mesure un prix mort.
- **Chevauchement massif** : 3 bulletins/jour × call 7j → le non-chevauchant
  déflate N_eff de **÷9 (7j)** et **÷60 (1m)** (constaté par l'Analyst, écrit
  dans le code). Résultat dans `performance.md` : **toutes les lignes 7j sont à
  N_eff = 0 ou 1**, Wilson_low ~0,2, alertes « KPI non significatif tant que
  N_eff < 15 ». **Aucune cellule 7j n'est mesurable**, et 1m n'apparaît même pas
  encore (warm-up). Le seul horizon réellement scoré est **24h** — soit
  l'horizon le MOINS pertinent pour du trend-following.

Autrement dit : **on mesure bien l'horizon qui compte le moins (24h) et pas du
tout les horizons qui sont la raison d'être du système (7j/1m)**. Un desk ne
ferait pas confiance à un score de tendance qui ne sait noter que le lendemain.

---

## 3. Autres faiblesses (réelles mais secondaires)

- **Biais distributionnel ignoré comme signal de perf.** Quasiment toutes les
  cellules sont à 90-100 % LONG ou SHORT (Or 0/100, Pétrole 95/5, Cacao 100/0,
  S&P 95/5). Le système alerte « biais distribution » mais ne le **pénalise
  pas** dans le score. Un call qui est SHORT 95 % du temps et a raison parce que
  le marché baissait n'est pas un bon « call directionnel » — c'est un **pari de
  régime**. Sur turbo, c'est crucial : si la cellule ne flip jamais, elle ne
  mesure pas une compétence directionnelle, juste un alignement avec une longue
  vague. La ventilation **flip vs continuation** existe (bien !) et montre déjà
  l'info (Café flip 0 % vs continuation 87,5 % = le système gagne en suivant,
  perd aux retournements) — mais elle reste **descriptive**, pas intégrée au
  verdict d'éligibilité.
- **Pas de prix « best/worst » sur la fenêtre (pas de MFE/MAE).** Sur turbo, ce
  qui tue, c'est le **knock-out touché en cours de route** même si le prix
  revient bon à l'échéance. La mesure ne regarde QUE le prix à l'échéance, pas le
  **chemin** (max favorable / max adverse). Un call « VRAI à l'échéance » a pu
  faire sauter la barrière à J+0,5. La mesure dit VRAI ; le trader est knock-out.
- **Tous les actifs traités au même horodatage de mesure** alors que NYSE,
  Euronext, FX et commodities n'ont pas les mêmes heures de clôture. Un run 18h
  CET mesure le S&P en pleine séance US et le CAC après clôture — incohérent
  pour comparer « le call du jour ».
- **PROBA_SCALE=15 non calibré empiriquement** (le code le dit). Le Brier est
  donc indicatif. Pas bloquant tant que c'est shadow, mais à ne pas vendre comme
  une vraie probabilité.

## 4. Ce qui est SOLIDE (à conserver tel quel)

- **Intégrité anti-triche exemplaire** : entry-lock prix d'émission immuable,
  échéance figée déterministe (`compute_echeance`), refus de look-ahead et de
  mesure prématurée → `suivi-interrompu` plutôt qu'un outcome inventé. **Zéro
  invention de prix/outcome** : red lines respectées. C'est la base saine.
- **non-conclusive bien séparée** de FAUSSE (un frémissement sous seuil n'est pas
  un mauvais call) et **exclue du dénominateur** — méthodologiquement correct.
- **Statut éligibilité honnête** : non-chevauchant + Wilson_low + N_eff≥15 →
  refuse de déclarer une cellule bonne sur 2 points. Aucune cellule n'est
  faussement promue (0/24 éligibles, c'est la vérité du warm-up).
- **INSUFFISANT exclu** de la mesure (gate suffisance) : on ne note pas un call
  qu'on n'a pas vraiment émis.
- **24h reporté au prochain jour ouvré + fériés** : la cause n°1 de mesure
  dégénérée (vendredi→samedi = même close) est traitée pour 24h.

## 5. Ce qu'il manque pour qu'un desk fasse confiance au score

Par priorité (un desk valide un score s'il reflète un P&L, pas un comptage) :

1. **Magnitude / expectancy** : agréger `realized_pct` (déjà loggé !) en
   gain_moyen(VRAI), perte_moyenne(FAUSSE), et une espérance par cellule. Sans
   ça le hit-rate ne dit rien sur l'argent.
2. **Seuil VRAI calé sur le coût rond du turbo** (spread + frais + financement),
   pas sur la vol minimale détectable. Définir un « mouvement exploitable »
   plutôt qu'un « mouvement détectable ». Sinon un VRAI ≠ trade vert.
3. **Rendre 7j/1m réellement mesurables** : ce sont les horizons de la tendance
   = la raison d'être. Pistes : n'échantillonner qu'1 bulletin/jour pour le
   non-chevauchant 7j/1m, échéance reportée jour-ouvré aussi sur 7j/1m, et
   accepter que le verdict de tendance se construise sur des semaines.
4. **Prix d'émission = close officiel / prix d'ouverture tradable** (gérer le gap
   d'ouverture pour actions/indices) — comparer du comparable.
5. **MFE/MAE (chemin)** : flaguer les cellules dont le max adverse aurait
   knock-out un turbo avant l'échéance, même si VRAI à l'arrivée.
6. **Pénaliser/qualifier le biais de régime** : un call qui ne flip jamais doit
   être lu comme « suivi de vague », pas « compétence directionnelle ».

Aucune de ces 6 n'exige d'inventer une donnée : `realized_pct` est déjà là, les
coûts turbo sont connus, les séries OHLC permettent le chemin et les closes.

## 6. Réponse en 10 lignes (mots simples)

1. La mesure est **honnête mais légère** : elle compte juste si le sens était bon, oui ou non.
2. Elle compare un prix au départ et un prix à l'arrivée. C'est correct sur le principe.
3. Mais elle ne regarde **que le sens, jamais combien ça a bougé**. +0,5 % et +9 % = pareil.
4. Du coup un taux de 100 % ne dit pas si on aurait **gagné de l'argent** sur turbo.
5. Le seuil pour dire « VRAI » est petit (0,5 %) : un **frémissement** suffit, même si frais + levier le mangent.
6. Le prix de départ est le dernier prix au moment du run, **pas un vrai prix d'entrée** (gap d'ouverture non géré).
7. Les horizons **7j et 1m** — le cœur de la tendance — ne sont **presque jamais mesurés** (trop peu de points indépendants).
8. On mesure donc surtout le **24h**, l'horizon le moins important pour suivre une vague.
9. Le système gagne quand il **suit une longue vague** et perd aux **retournements** — mais ce n'est pas noté dans le score.
10. La plomberie anti-triche (prix figé, pas d'invention, pas de look-ahead) est **excellente** — c'est le « quoi mesurer » qu'il faut muscler.

**VERDICT : À RENFORCER.** Les 3 trous prioritaires : (#1) **pas de magnitude/
P&L** — un score sourd à l'argent ; (#2) **seuil + prix d'émission non
tradables** — un VRAI n'est pas un trade vert ; (#3) **7j/1m non mesurables** —
on ne note pas l'horizon qui justifie le système.
