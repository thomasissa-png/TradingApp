# Spec analytique · Post-mortem hebdo (sections 3, 4, 5 et propositions)

> Document de référence pour l'implémentation des fonctions `_points_forts`, `_points_faibles`,
> `_learnings_semaine` et `build_propositions` dans `run_weekly.py`.
>
> Auteur : @data-analyst · Version cible : bilan dimanche 18h (R5)
> Contraintes absolues rappelées : WIN RATE ONLY (0 euro/dollar), zéro invention, français UTF-8,
> pas de tiret cadratin, déterministe (chaque phrase = règle chiffrée ou donnée réelle).

---

## Sommaire

- [1. Diagnostic de la version actuelle](#1-diagnostic-de-la-version-actuelle)
- [2. Architecture du post-mortem](#2-architecture-du-post-mortem)
- [3. Section 3 — Ce qu'on a bien fait (POURQUOI ça a marché)](#3-section-3--ce-quon-a-bien-fait-pourquoi-ca-a-marche)
- [4. Section 4 — Ce qu'on doit améliorer (POURQUOI ça a raté)](#4-section-4--ce-quon-doit-ameliorer-pourquoi-ca-a-rate)
- [5. Section 5 — Learnings actionnables](#5-section-5--learnings-actionnables)
- [6. Propositions d'ajustement](#6-propositions-dajustement)
- [7. Cas de dégradation (données absentes)](#7-cas-de-degradation-donnees-absentes)
- [8. Gabarits S25 (semaine 2026-06-16 au 2026-06-20)](#8-gabarits-s25-semaine-2026-06-16-au-2026-06-20)

---

## 1. Diagnostic de la version actuelle

### Ce qui ne va pas

Les fonctions `_points_forts`, `_points_faibles` et `_learnings_semaine` produisent des phrases
purement DESCRIPTIVES :

- "Cellules porteuses (>= 65%) : Bitcoin 24h (71,4%)." -> constate, n'explique pas POURQUOI.
- "Tendances 7j à contre-sens : Cacao SHORT (lun->mer) -2,1%." -> constate, n'explique pas ce
  qu'on n'a pas vu.
- "Pertes plus amples que les gains sur la sélection" -> observation comptable, pas un learning.

Thomas veut un vrai post-mortem de trading. La question n'est pas "qu'est-ce qui s'est passé ?"
mais "POURQUOI ça s'est passé et qu'est-ce qu'on change ?".

### Ce que les données permettent réellement

Les champs disponibles permettent de répondre à 3 questions causales distinctes :

| Question | Source | Champ clé |
|---|---|---|
| Call news-driven ou quant-pur ? | decision-log | `ratio_news` (0-1, proportion news) |
| Quelle news a fait bouger l'actif ? | events-log via `cause_news_high_apres()` | `materiality == "high"` |
| Signal mono-critère ou coin-flip suivi à tort ? | decision-log | `mono_critere_dominant`, `coin_flip`, `quasi_neutre` |
| Bascule captée ou subie ? | segments de tendance | structure multi-segments de `tendances_par_actif()` |
| Sortie tardive ? | bilan jour (données 12h/18h) | `perf_top3` non disponible en hebdo |

Ce qui manque et ne peut PAS être inventé : les relevés intraday 12h/18h ne sont PAS agrégés
dans `BilanSemaine`. Pour les sorties tardives, se limiter à l'asymétrie ampleur gagnantes/perdantes
depuis `SelectionSemaine`.

---

## 2. Architecture du post-mortem

### Principe : pick par pick, pas vue globale

Pour chaque pick de la Sélection du jour jugé cette semaine (n <= 5, horizon 24h, outcome VRAI ou
FAUSSE), le post-mortem doit répondre à UNE question causale tracée :

```
VRAI  + ratio_news > 50% -> "bon flair news : [résumé news via cause_news_high_apres]"
VRAI  + ratio_news <= 50% -> "call quant-pur confirme la tendance [direction]"
VRAI  + mono_critere_dominant ou coin_flip -> PARADOXE : succès sur signal faible, à signaler
FAUSSE + ratio_news > 50% -> "news raté : on était [LONG/SHORT] mais [résumé news opposée]"
FAUSSE + ratio_news <= 50% + mono_critere/coin_flip -> "signal faible suivi à tort (mono-critere ou coin-flip)"
FAUSSE + ratio_news <= 50% + signal fort -> "call quant raté, cause non identifiée"
```

Ce mapping est la colonne vertébrale de toute la refonte. Chaque section 3/4/5 en est dérivée.

### Sources de données, par type de phrase

| Type de phrase | Source primaire | Source secondaire |
|---|---|---|
| Win rate sélection | `bilan.selection.win_rate` | `bilan.selection.n_select` |
| Cause news (VRAI ou FAUSSE) | `cause_news_high_apres(actif, date_j, None)` depuis measures-log | events-log (materiality high) |
| Ratio news/quant à l'émission | measures-log champ `ratio_news` (persisté) | decision-log `p2_M7_ratio_news` (fallback) |
| Drapeaux signal faible | decision-log : `mono_critere_dominant`, `coin_flip`, `quasi_neutre` | `selection_motif_exclusion` |
| Type de mouvement tendance 7j | `bilan.tendances` -> structure de segments | `perf_pct` du segment |
| Cellule faible/porteuse | `bilan.cellules` -> `CelluleObs.faible_confirmee`, `.porteuse` | `wilson_low`, `n_eff` |

---

## 3. Section 3 — Ce qu'on a bien fait (POURQUOI ca a marche)

### Objectif

Thomas comprend POURQUOI ses picks gagnants ont fonctionné : est-ce que le système a capté une news
que le marché n'avait pas encore intégré ? Est-ce une continuation de tendance solide ? Est-ce une
bascule bien timée ? La réponse doit être tracée sur des chiffres, pas sur de l'intuition.

### Règles de dérivation déterministes

#### Règle 3.1 - Picks gagnants avec cause causale news

DÉCLENCHEUR : au moins 1 pick de la Sélection du jour, horizon 24h, outcome VRAI, ratio_news > 50%
(champ persisté dans measures-log ou lu via decision-log bulletin_date).

LOGIQUE :
1. Pour chaque pick VRAI de la semaine (issues de `selection_semaine()`), lire `ratio_news` dans
   measures-log (champ direct si présent, sinon jointure decision-log via `bulletin_date`).
2. Si ratio_news > 0.50 (= 50%), le call était dominé par la composante news.
3. Appeler `cause_news_high_apres(actif, echeance - 1j, None)` pour obtenir le résumé de la news
   high de ce jour. Si résumé présent : phrase causale. Si absent : "cause non identifiée".

SEUIL : ratio_news > 0.50 pour qualifier "news-driven". En dessous : "quant-pur".

GABARIT phrase :
> "[Actif] LONG/SHORT : call news-driven juste (ratio news [X]%). [Résumé news] a poussé dans
> notre sens."

> "[Actif] LONG/SHORT : call quant-pur confirmé. Aucune news high tracée, le mouvement directionnel
> a suivi les critères quantitatifs."

CAS PARADOXAL (signal faible + VRAI) :
Si outcome VRAI ET (mono_critere_dominant OR coin_flip OR quasi_neutre) : signaler le paradoxe
sans sur-interpréter.

GABARIT paradoxe :
> "[Actif] : succès sur signal classé faible (drapeau [mono-critere/coin-flip/quasi-neutre]). Pas
> de conclusion : conserver le garde-fou pour les prochaines semaines."

#### Règle 3.2 - Tendances 7j gagnantes : type de mouvement

DÉCLENCHEUR : au moins 1 segment de `bilan.tendances` avec `perf_pct >= _PERF_MATERIELLE_PCT`
(seuil actuel 0.5%).

LOGIQUE (déjà partiellement implémentée dans `_cause_segment`, à enrichir) :
- Segment unique sur toute la semaine (n_seg == 1) ET perf positive : continuation stable. L'actif
  a tenu sa direction sans retournement. Signal : le système n'a pas flipé inutilement.
- Segment issu d'une bascule (idx > 0) ET perf positive : le retournement a été capté à temps.
  C'est le cas le plus fort à valoriser.
- Plusieurs segments, le dernier gagnant : la fin de semaine a rattrapé un début difficile.

GABARIT continuation :
> "[Actif] LONG/SHORT toute la semaine ([perf]%) : tendance tenue sans bascule inutile. Le
> système a bien résisté au bruit."

GABARIT bascule bien captée :
> "[Actif] : bascule [LONG->SHORT / SHORT->LONG] captée [jour]. Le retournement a payé ([perf]%
> sur [jours] jours)."

#### Règle 3.3 - Conviction forte qui paie

DÉCLENCHEUR : `bilan.n_forte >= 3` ET `bilan.taux_forte >= 70.0%`.

Ajouter la comparaison avec conviction faible si les deux N >= 3 :

GABARIT :
> "Le tri par conviction fonctionne cette semaine : [taux_forte]% sur [n_forte] paris à conviction
> forte, contre [taux_faible]% sur [n_faible] paris faibles. Les filtres anti-coin-flip et
> anti-mono-critère ont bien discriminé."

#### Règle 3.4 - Sélection au-dessus de 60% (porte d'entrée minimale)

DÉCLENCHEUR : `bilan.selection.n_select >= 3` ET `bilan.selection.win_rate >= 60.0`.

GABARIT :
> "La Sélection 24h : [win_rate]% sur [n_select] picks jugés cette semaine ([n_vrai] gagnants).
> Ampleur moyenne des gagnants : [ampleur_moy_gagnantes]%."

NOTE : ne PAS répéter cette phrase si les règles 3.1/3.2 ont déjà cité les mêmes actifs avec
leur cause. La cause prime sur le comptage.

### Ordre de priorité des points

1. Picks gagnants avec cause tracée (Règle 3.1) - le plus instructif
2. Bascules bien captées (Règle 3.2, sous-cas bascule)
3. Continuations stables (Règle 3.2, sous-cas continuation)
4. Conviction forte qui paie (Règle 3.3)
5. Sélection au-dessus de 60% sans détail par pick (Règle 3.4) - seulement si 1-4 sont vides

Limiter à 4 points maximum. Au-delà : garder les plus informatifs (cause > statistique).

---

## 4. Section 4 — Ce qu'on doit améliorer (POURQUOI ca a rate)

### Objectif

Thomas comprend précisément CE QU'ON A RATÉ : quelle news allait contre notre call ? Quel signal
faible a été suivi alors qu'il aurait dû être filtré ? Une bascule trop tardive ? Une direction
qui tenait depuis trop longtemps malgré des signes de retournement ?

C'est la section la plus importante pour progresser. Chaque point doit permettre une décision
concrète.

### Règles de dérivation déterministes

#### Règle 4.1 - Picks perdants : news ratée ou signal faible suivi

DÉCLENCHEUR : au moins 1 pick de la Sélection du jour, horizon 24h, outcome FAUSSE.

LOGIQUE pick par pick :

CAS A : FAUSSE + ratio_news > 50%
-> Le call était dominé par les news. Le marché a réagi à une news que notre synthèse n'a pas
   vue ou a mal interprétée.
-> Appeler `cause_news_high_apres(actif, echeance - 1j, None)` : si une news high tracée va dans
   le sens OPPOSÉ au call -> c'est la news ratée. Si aucune news high tracée : "pas de catalyseur
   tracé, mouvement inexpliqué."

GABARIT news ratée :
> "[Actif] [LONG/SHORT] raté : call news-driven (ratio [X]%). [Résumé news adverse] a dominé le
> marché à contre-sens de notre position. Ce catalyseur n'était pas dans notre synthèse."

GABARIT news introuvable :
> "[Actif] [LONG/SHORT] raté : call news-driven (ratio [X]%) mais aucun catalyseur high tracé.
> Mouvement de marché non expliqué par l'events-log."

CAS B : FAUSSE + ratio_news <= 50% + (mono_critere_dominant OR coin_flip OR quasi_neutre)
-> Le call était faible dès l'émission ET il a raté. C'est un signal qu'on n'aurait pas dû
   sélectionner.
-> Identifier le drapeau dominant (priorité : coin_flip > mono_critere > quasi_neutre).
-> Si mono_critere_dominant : lire `mono_critere_nom` dans le decision-log.

GABARIT signal faible suivi à tort :
> "[Actif] : pari raté sur un signal classé faible (drapeau [coin-flip / mono-critere :
> [nom_critere] / quasi-neutre]). Ce type de signal devrait rester hors Sélection."

CAS C : FAUSSE + ratio_news <= 50% + signal fort (aucun drapeau, conviction forte)
-> Le call quant était solide mais le marché a fait autrement. Chercher si une news high est
   tracée quand même (peut-être sous-pondérée au scoring).

GABARIT call quant raté :
> "[Actif] : call quant raté sans drapeau de faiblesse (conviction forte). [Si news tracée :
> '[résumé news] a contre-pied le signal quant.' Sinon : 'cause non identifiée.']"

#### Règle 4.2 - Tendances 7j perdantes : retournement subi ou bascule tardive

DÉCLENCHEUR : au moins 1 segment de `bilan.tendances` avec `perf_pct < -_PERF_MATERIELLE_PCT`.

LOGIQUE :
- Segment avec bascule qui SUIT (suivi_dun_flip == True) : le système tenait une direction qui
  s'est retournée. La bascule a eu lieu APRÈS la perte. Question : y avait-il un signe dans
  les news avant ?
- Segment issu d'une bascule (issu_dun_flip == True) ET perf négative : le retournement n'a pas
  payé (faux flip). La direction précédente était probablement la bonne.

GABARIT retournement subi :
> "[Actif] tenait [LONG/SHORT] [jours] mais la direction s'est retournée ([perf]%). Bascule
> captée [jour de la bascule], après la perte. A vérifier : y avait-il un signal dans les news
> avant le retournement ?"

GABARIT faux flip :
> "[Actif] : bascule [LONG->SHORT / SHORT->LONG] qui n'a pas payé ([perf]% à contre-sens).
> L'ancienne direction tenait probablement encore."

#### Règle 4.3 - Sélection en dessous de 50% (signal d'alarme global)

DÉCLENCHEUR : `bilan.selection.n_select >= 3` ET `bilan.selection.win_rate < 50.0`.

GABARIT :
> "La Sélection 24h sous 50% cette semaine ([win_rate]% sur [n_select] picks). Vérifier si les
> picks perdants étaient dominés par des signaux faibles (drapeaux coin-flip / mono-critere) ou
> si les news ont systématiquement contre-piedé les calls."

NOTE : cette phrase est GÉNÉRALE. Elle est complétée par Règle 4.1 (détail pick par pick).
Ne pas dupliquer les noms d'actifs déjà cités en 4.1.

#### Règle 4.4 - Ampleur asymétrique (pertes > gains)

DÉCLENCHEUR : `ampleur_moy_perdantes` (valeur absolue) > `ampleur_moy_gagnantes`, les deux non None,
`selection.n_select >= 3`.

GABARIT :
> "Sorties : les mouvements adverses ([ampleur_perdantes]%) ont été plus amples que les gains
> ([ampleur_gagnantes]%). Cela suggère des positions tenues trop longtemps dans le mauvais sens,
> ou une asymétrie dans la structure de marché cette semaine."

NOTE sur la causalité : cette asymétrie peut aussi signifier que les BONS picks ont été pris sur
des mouvements limités, et les mauvais sur des mouvements brutaux (news). Le rédacteur ne tranche
pas entre ces hypothèses : il les cite toutes deux et laisse Thomas décider.

#### Règle 4.5 - Cellules faibles confirmées (signal structurel)

DÉCLENCHEUR : `any(c.faible_confirmee for c in bilan.cellules)`.

GABARIT (reformulé pour Thomas, sans jargon Wilson) :
> "[Actif] [horizon] : win rate [X]% sur [n_eff] paris mesurés. Sur les 2 dernières semaines,
> cette cellule n'a pas atteint 50% de réussite dans l'intervalle de confiance bas. Une proposition
> d'ajustement est disponible ci-dessous."

NOTE : éviter "Wilson_low < 50% ET N_eff >= 10 ET >= 2 semaines consécutives" dans le texte Thomas.
Traduire par la phrase ci-dessus. Les chiffres bruts restent dans la proposition formelle.

### Ordre de priorité des points

1. Picks perdants avec cause tracée (Règle 4.1) - le plus actionnable
2. Retournements subis ou faux flips (Règle 4.2)
3. Alarme globale sélection (Règle 4.3) - seulement si win_rate < 50%
4. Asymétrie ampleur (Règle 4.4)
5. Cellules faibles structurelles (Règle 4.5)

Limiter à 4 points. Prioriser les causes tracées sur les observations statistiques.

---

## 5. Section 5 — Learnings actionnables

### Objectif

Chaque learning = une décision concrète que Thomas peut prendre ou surveiller la semaine suivante.
Format : [observation chiffrée] + [action ou surveillance à J+7].

Pas de learning sans base chiffrée. Pas de redite des sections 3/4 (synthèse, pas répétition).

### Règles de dérivation déterministes

#### Règle 5.1 - Learning sur les drapeaux signal faible (si picks FAUSSE avec drapeau)

DÉCLENCHEUR : au moins 1 pick FAUSSE avec drapeau `coin_flip` OU `mono_critere_dominant` OU
`quasi_neutre` dans la semaine (identifié en Règle 4.1 CAS B).

GABARIT :
> "Les picks avec drapeau [coin-flip / mono-critere / quasi-neutre] ont raté cette semaine
> ([N] sur [Total] concernés). A surveiller : si ce pattern se confirme la semaine prochaine,
> envisager de durcir le filtre de sélection pour ces drapeaux."

#### Règle 5.2 - Learning sur le type de call (news vs quant)

DÉCLENCHEUR : au moins 2 picks jugés cette semaine (VRAI ou FAUSSE) avec `ratio_news` disponible,
et résultat différencié news vs quant.

CALCULER :
- win_rate_news = VRAI_news / (VRAI_news + FAUSSE_news) pour les picks de la semaine avec ratio_news > 50%
- win_rate_quant = VRAI_quant / (VRAI_quant + FAUSSE_quant) pour les picks avec ratio_news <= 50%
(N peut être très faible : signaler si N < 3)

GABARIT (si N >= 2 de chaque) :
> "Cette semaine, les calls news-driven : [win_rate_news]% ([N] picks). Les calls quant-purs :
> [win_rate_quant]% ([N] picks). [Si news > quant : 'Le flair news a payé davantage que le quant
> pur cette semaine.'] [Si quant > news : 'Le quant a mieux performé que les appels news-driven.']
> [Si N insuffisant : 'Trop peu de picks pour conclure (N < 3 dans un segment).']"

#### Règle 5.3 - Learning sur le timing des bascules 7j

DÉCLENCHEUR : au moins 1 bascule dans `bilan.tendances` (idx > 0 dans les segments), résultat
mixte (une bascule gagnante ET une perdante dans la semaine).

GABARIT :
> "Les bascules 7j cette semaine : [N] captées avec profit ([actifs gagnants]), [N] prises à
> contre-sens ([actifs perdants]). Le timing des retournements reste à calibrer : surveiller les
> news d'opposition avant toute bascule."

#### Règle 5.4 - Learning sur la conviction (si écart forte vs faible)

DÉCLENCHEUR : `bilan.n_forte >= 3` ET `bilan.n_faible_conv >= 3` ET écart > 10 points entre
`taux_forte` et `taux_faible_conv`.

GABARIT (conviction forte > faible) :
> "La conviction forte a discriminé ([taux_forte]% vs [taux_faible_conv]% en conviction faible).
> Le garde-fou fonctionne : ne pas assouplir le filtre."

GABARIT (conviction faible > forte, anomalie) :
> "Anomalie cette semaine : la conviction faible ([taux_faible_conv]%) dépasse la forte
> ([taux_forte]%). N encore modeste ([n_forte] + [n_faible_conv] paris). A surveiller mais
> pas de conclusion à tirer avant N >= 10 dans chaque catégorie."

#### Règle 5.5 - Learning sur la sélection trop prudente

DÉCLENCHEUR : `bilan.selection.n_select <= 2` ET `bilan.selection.win_rate >= 60.0`
(peu de picks mais bon taux).

GABARIT :
> "Seulement [n_select] pick(s) jugé(s) cette semaine pour un win rate de [win_rate]%.
> La sélection a peut-être été trop prudente. A surveiller : si le win rate tient au-dessus de
> 60% sur N >= 5, envisager d'élargir légèrement les critères de top 3."

#### Règle 5.6 - Learning par défaut (warm-up, N insuffisant)

DÉCLENCHEUR : aucune des règles 5.1-5.5 ne s'est déclenchée.

GABARIT :
> "Pas de learning net cette semaine : les N par catégorie restent trop faibles (warm-up) pour
> tirer une conclusion statistiquement fiable. On continue de mesurer."

### Nombre de learnings

Maximum 3 learnings par semaine. Prioriser : 5.1 (signal faible) > 5.2 (news vs quant) > 5.3
(timing bascules) > 5.4 (conviction) > 5.5 (prudence). Le 5.6 est le fallback unique.

---

## 6. Propositions d'ajustement

### Objectif

Thomas reçoit une proposition ACTIONNÉE (Thomas OUI/NON/reporter), formulée en français simple,
avec les chiffres qui la justifient et le risque d'erreur.

### Problème de la version actuelle

La phrase "aucune cellule faible confirmée sur >= 2 semaines consécutives (N_eff >= 10 ET
Wilson_low < 50%)" est incompréhensible pour Thomas.

### Règles de reformulation

#### Pour le CONSTAT (champ `constat` dans `build_propositions`)

VERSION ACTUELLE (à remplacer) :
> "Win rate X% sur N paris indépendants, Wilson_low Y% < 50%, observé sur >= 2 semaines
> consécutives."

VERSION CIBLE :
> "[Actif] [horizon] : [X]% de réussite sur [N] paris mesurés. Sur les deux dernières semaines,
> la borne basse de l'intervalle de confiance reste sous 50% : ce n'est pas un coup de malchance
> passager, c'est un signal de faiblesse structurelle."

#### Pour la PROPOSITION (champ `proposition`)

VERSION ACTUELLE (trop vague) :
> "Revoir la pondération des critères de [Actif] [horizon] (réduire le poids du critère qui
> tire dans le mauvais sens, identifié au decision-log)."

VERSION CIBLE (avec critère nommé si disponible) :

LOGIQUE : lire `mono_critere_nom` dans le decision-log de la semaine pour cette cellule. Si
présent, nommer le critère dominant.

GABARIT avec critère identifié :
> "Réduire le poids de '[nom_critere]' dans [Actif] [horizon] : ce critère domine les signaux
> mais le résultat sur 2 semaines est négatif. Action concrète : modifier le champ `poids` dans
> la config YAML de l'actif. Thomas doit valider avant toute modification."

GABARIT sans critère identifiable :
> "Revoir les critères de [Actif] [horizon] : le système n'a pas correctement discriminé sur
> 2 semaines. Analyser le decision-log pour identifier le critère dominant. Thomas tranche sur
> le levier à ajuster."

#### Pour la PHRASE "Aucune proposition" (quand tout va bien)

VERSION ACTUELLE (à supprimer) :
> "Aucune cellule faible confirmée sur >= 2 semaines consécutives (N_eff >= 10 ET Wilson_low
> < 50%). Le Manager n'invente pas d'ajustement sur petit N (mesurer avant d'agir)."

VERSION CIBLE :
> "Aucun ajustement proposé cette semaine : toutes les cellules avec suffisamment de paris
> mesurés restent au-dessus du seuil de confiance. On continue de mesurer."

#### Pour les OBSERVATIONS "cellule candidate" (1ère semaine, pas encore confirmée)

VERSION ACTUELLE :
> "[Actif] [horizon] : candidate faible cette semaine (win rate X%, N_eff Y, Wilson_low Z%)
> · 1ère semaine, PAS de proposition (attendre confirmation S+1)."

VERSION CIBLE :
> "[Actif] [horizon] : en observation cette semaine ([X]% de réussite sur [N] paris). Si la
> tendance se confirme la semaine prochaine, une proposition d'ajustement sera préparée."

#### Pour les OBSERVATIONS "cellule en zone N_eff 5-9" (trop peu de paris)

VERSION ACTUELLE :
> "[Actif] [horizon] : sous surveillance (N_eff Y entre 5-9) · observation, PAS de proposition
> (mesurer avant d'agir)."

VERSION CIBLE :
> "[Actif] [horizon] : seulement [N] paris mesurés, pas assez pour conclure. On attend [N_cible]
> paris avant d'agir."

N_cible = 10 (seuil N_EFF_PROPOSE défini dans le code).

---

## 7. Cas de dégradation (données absentes)

### Hiérarchie de dégradation propre (jamais d'invention)

| Donnée manquante | Comportement attendu | Phrase à produire |
|---|---|---|
| `ratio_news` absent dans measures-log et decision-log | Pas de classification news/quant | "[Actif] : ratio news non disponible pour ce pick (instrumentation manquante sur ce bulletin)." |
| `cause_news_high_apres()` retourne None | Pas de news high tracée | "cause non identifiée (pas de catalyseur tracé dans l'events-log)" |
| `mono_critere_nom` absent alors que `mono_critere_dominant` True | Drapeau signalé sans nom | "signal mono-critère (critère non nommé dans ce log)" |
| Segments de tendance vides (`bilan.tendances` vide) | Pas d'analyse 7j | Omettre les règles 3.2 et 4.2 entièrement |
| `bilan.selection.n_select == 0` | Pas de pick jugé | "Aucun pick de la Sélection 24h conclusif cette semaine (tous non-conclusifs ou semaine sans top 3)." |
| `n_forte < 3` ET `n_faible_conv < 3` | N conviction trop faible | Omettre Règle 3.3 et 5.4 entièrement |
| `realized_pct` absent dans measures-log | Pas d'ampleur | Omettre l'ampleur du pick concerné, compter quand même le win rate via `outcome` |

### Règle de robustesse globale

Si TOUTES les règles de la section 3 retournent liste vide (aucun déclencheur activé) :
> "Pas d'analyse disponible cette semaine : N trop faible sur tous les horizons (warm-up en cours).
> Les premiers learnings significatifs sont attendus autour de [WARMUP_DATES['24h']]."

---

## 8. Gabarits S25 (semaine 2026-06-16 au 2026-06-20)

### Contexte réel observé dans les données S25

Les decision-logs de S25 (2026-06-16 à 2026-06-19, derniers disponibles) montrent :

**Caractéristiques observées :**
- `ratio_news` = 0.0 sur l'ensemble des cellules lues (Argent 24h/7j/1m, Blé 24h/7j). Les calls
  sont 100% quant-purs cette semaine pour ces actifs : `news_total = 0`, `quant_total > 0`.
- Blé 24h/7j : `mono_critere_dominant: true`, `mono_critere_nom: "Tendance du blé (20 jours)"`,
  `confidence: "faible"`. Ce drapeau est tracé proprement.
- Argent : aucun drapeau actif, signal fort (coverage > 70%, aucun coin_flip/quasi_neutre).

**Implication pour les gabarits S25 :**

Si des picks FAUSSE existent sur Blé cette semaine (à vérifier dans measures-log après le run
dimanche), la Section 4 produira :

> "Blé SHORT 24h raté : call quant-pur sur signal faible (drapeau mono-critère : 'Tendance du
> blé (20 jours)' domine). Ce type de signal devrait rester hors Sélection."

Si des picks VRAI existent sur Argent (ratio_news = 0, signal fort) :

> "Argent LONG : call quant-pur confirmé. Aucune news high tracée, le mouvement directionnel a
> suivi les critères quantitatifs (ratio news 0%)."

**Pour la phrase "Aucune proposition" si aucune cellule faible confirmée :**

> "Aucun ajustement proposé cette semaine : toutes les cellules avec suffisamment de paris
> mesurés restent au-dessus du seuil de confiance. On continue de mesurer."

### Gabarit complet d'une section 3 riche (exemple fictif valide selon les règles)

```
## 3. Ce qu'on a bien fait cette semaine

- Or LONG : call quant-pur confirmé. Ratio news 0%, signal fort (aucun drapeau). Le mouvement
  dans notre sens a suivi les critères de tendance 20j et de flux ETF. Continuation stable sur
  les 3 jours.

- Cacao : bascule SHORT captée mercredi (+1,8% dans le bon sens sur 2 jours). Le retournement
  SHORT a été pris à temps, après une phase LONG peu convaincante en début de semaine.

- Le tri par conviction a payé : 75% de réussite sur 4 paris à conviction forte, contre 45%
  sur 2 paris à conviction faible. Les filtres anti-coin-flip ont bien discriminé.
```

### Gabarit complet d'une section 4 riche (exemple fictif valide selon les règles)

```
## 4. Ce qu'on doit améliorer

- Blé SHORT raté : call quant-pur sur signal faible (drapeau mono-critère : 'Tendance du blé
  (20 jours)' dominant, confidence faible). Ce signal n'aurait pas dû passer le filtre de
  sélection.

- Cuivre LONG : le marché a retourné à contre-sens (-1,2%) après 3 jours de tendance haussière.
  Aucune news high tracée avant la bascule. A vérifier en retrospective : y avait-il un signal
  macro (dollar, inventaires) avant le retournement ?

- La Sélection 24h cette semaine : 40% sur 5 picks. Les 3 picks perdants avaient tous un
  drapeau de faiblesse (2 mono-critère, 1 coin-flip). Le filtre de sélection mérite d'être
  durci sur les drapeaux.
```

### Gabarit complet d'une section 5 (exemple fictif valide selon les règles)

```
## 5. Les learnings de la semaine

- Les picks avec drapeau mono-critère ont raté 2 fois sur 2 cette semaine. Si ce pattern se
  confirme la semaine prochaine, durcir le filtre : un pick mono-critère ne passe pas dans
  le top 3.

- Cette semaine, calls quant-purs : 60% (3 picks). Calls news-driven : 0% (1 pick, trop peu
  pour conclure). Le quant a mieux performé mais N insuffisant côté news pour généraliser.

- Les bascules 7j : 1 captée avec profit (Cacao), 1 prise à contre-sens (Cuivre). Timing
  mitigé : surveiller les news macro avant les prochaines bascules SHORT sur matières premières.
```

---

## Annexe technique : champs nécessaires par règle

| Règle | Champs measures-log | Champs decision-log | Fonctions |
|---|---|---|---|
| 3.1 (news-driven VRAI) | `outcome`, `ratio_news`, `realized_pct`, `bulletin_date`, `actif` | `p2_M7_ratio_news` (fallback) | `cause_news_high_apres()` |
| 3.2 (tendances 7j) | - | `conclusion_pm1`, `horizon` | `tendances_par_actif()`, `_cause_segment()` |
| 3.3 (conviction) | `outcome` | `score_pm1`, drapeaux | `win_rate_par_conviction()` |
| 4.1 (FAUSSE + news) | `outcome`, `ratio_news`, `bulletin_date`, `actif` | `p2_M7_ratio_news`, `mono_critere_dominant`, `mono_critere_nom`, `coin_flip`, `quasi_neutre` | `cause_news_high_apres()`, `load_conviction_records()` |
| 4.2 (tendances perdantes) | - | `conclusion_pm1` | `tendances_par_actif()`, `_cause_segment()` |
| 5.1 (learning drapeaux) | `outcome` | `mono_critere_dominant`, `coin_flip`, `quasi_neutre` | `load_conviction_records()` |
| 5.2 (learning news vs quant) | `outcome`, `ratio_news` | `p2_M7_ratio_news` | `_news_vs_quant_winrate()` (réutilisable) |
| 6 (propositions) | - | `mono_critere_nom` (critère dominant) | `build_propositions()` (à modifier) |

### Nouvelle donnée requise pour les sections 3/4 : la jointure pick -> decision-log

Pour chaque pick de la `SelectionSemaine`, les champs `ratio_news`, `mono_critere_dominant`,
`coin_flip`, `quasi_neutre`, `mono_critere_nom` doivent être lus depuis le decision-log du jour de
décision (`bulletin_date`). La fonction `load_conviction_records(bulletin_date, decision_log_dir)`
existe déjà (retourne le record complet). Il faut l'appeler pick par pick.

Workflow d'enrichissement pick :
```
Pour chaque record r dans measures-log (horizon 24h, semaine ISO, outcome VRAI/FAUSSE) :
    decision_day = date.fromisoformat(r["bulletin_date"])
    records = load_conviction_records(decision_day, decision_log_dir)
    rec = records.get((r["actif"], "24h"))  # record complet
    ratio_news = r.get("ratio_news") or (rec.get("p2_M7_ratio_news", 0) if rec else None)
    drapeaux = {
        "mono_critere": rec.get("mono_critere_dominant", False) if rec else None,
        "mono_critere_nom": rec.get("mono_critere_nom") if rec else None,
        "coin_flip": rec.get("coin_flip", False) if rec else None,
        "quasi_neutre": rec.get("quasi_neutre", False) if rec else None,
    }
    # -> enrichir le pick avec ratio_news + drapeaux avant d'appliquer les règles
```

Ce workflow est à implémenter dans une nouvelle fonction helper
`_enrich_picks_semaine(records_semaine, decision_log_dir)` appelée depuis `build_bilan_semaine`.
