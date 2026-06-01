# Revue de plan — Intensité news par horizon (avis news trader senior)

Brief : Thomas veut être SÛR des prévisions 24h/7j/1m. Plan proposé : (1) un `decay_factor`
global news {24h:1.0, 7j:0.7, 1m:0.3}, (2) interdire à la news d'inverser seule le quant.
Avis AVANT implémentation. Périmètre : revue de conception, pas audit de run.

> Convention : L = prix de l'actif monte, S = baisse. VIX L = vol monte (risk-off).

---

## TL;DR (verdict desk)

- **Réglage 1 (decay global) : NO-GO.** Doublon direct avec la `pertinence` par horizon
  déjà en place, et REGRESSION : il écrase la différenciation par critère qui est justement
  la bonne réponse desk. Garder la pertinence, la corriger là où elle ment.
- **Réglage 2 (news ne renverse jamais le quant) : NO-GO en l'état.** Trop brutal. Un vrai
  choc d'offre (Ormuz) DOIT pouvoir primer. Remplacer par une règle d'override conditionnel
  (fraîcheur + matérialité + type de news), pas une interdiction sèche.
- **Le vrai manque (structurel vs frais-déjà-price) : NON réglé par le plan.** C'est LE
  trou. Il faut un `event_id`/date tracée + un flag structurel/ponctuel. À ajouter.

---

## 1. Le decay global fait-il doublon avec la pertinence ?

OUI, doublon — et pire qu'un doublon : une régression.

Mécanique réelle (lue dans `scoring_analyste.py:352`) :

```
contribution(H) = valeur_norm × poids × pertinence[H] × signe
Score(H)        = Σ contributions(H)   sur tous les critères
```

La `pertinence[H]` PAR CRITÈRE décroît DÉJÀ l'intensité par horizon, et — point capital —
elle le fait **différemment selon la nature du driver**. Exemple `fiches/petrole.yml` :

| Critère pétrole              | 24h | 7j  | 1m  | Lecture desk |
|------------------------------|-----|-----|-----|--------------|
| Tension géopol Moyen-Orient  | 0.9 | 0.7 | 0.2 | choc ponctuel : fort à chaud, s'éteint à 1m |
| OPEC+ politique production   | 0.4 | 0.9 | 1.0 | structurel : monte en puissance, tient à 1m |
| CFTC COT nets                | 0.2 | 0.8 | 1.0 | positionnement : effet lent |

C'est EXACTEMENT la distinction « choc Ormuz ≠ politique OPEC+ structurelle » que tu cherches.
Le moteur la fait déjà. Un `decay_factor` global {24h:1.0, 7j:0.7, 1m:0.3} appliqué uniformément :

- **écrase** la courbe OPEC (qui doit MONTER vers 1m, pas tomber à 0.3) → on tuerait le signal
  structurel le plus utile à 1m. Contresens desk net.
- **multiplie deux décroissances** sur la géopol (0.2 × 0.3 = 0.06 à 1m) → sur-amortissement,
  la news devient invisible alors qu'on voulait juste la calmer.
- traite « tout pareil » alors que le problème est précisément l'hétérogénéité des news.

Verdict : la bonne approche desk = **régler la pertinence par critère**, pas ajouter un decay
uniforme. Si la géopol pétrole 0.9/0.7/**0.2** te semble encore trop forte à 7j, baisse le 7j
à 0.4-0.5 (cf. `geopol_iran` id varie déjà : 0.9/0.3/0.1 sur un autre critère pétrole). Le
levier existe, par critère, par actif. C'est plus de travail que de poser un chiffre global,
mais c'est la seule façon de ne pas casser les drivers structurels.

> Note importante : le decay est-il sur la NEWS ou sur le CRITÈRE ? La synthèse DeepSeek
> (`synthese_directionnelle.py`) sort UNE direction/conviction par actif, SANS notion d'horizon.
> Le seul endroit où l'horizon vit, c'est la `pertinence` du critère news dans la fiche. Donc
> un « decay_factor news » ne peut s'appliquer QUE là où la pertinence s'applique déjà →
> c'est littéralement le même multiplicateur. Doublon confirmé au niveau du code.

---

## 2. « La news ne peut plus inverser seule le quant » — sain pour un desk ?

NON en l'état — c'est jeter le bébé avec l'eau du bain. Mais l'intention est bonne.

D'abord, cadrons ce que « inverser seule » veut dire ici. La news n'est pas un override :
c'est UN critère pondéré (`poids × pertinence`) dans une somme. S'il « inverse » le score,
c'est qu'il pesait plus que la somme du reste — un choix de poids, pas une prise de contrôle.
Les cas Or-24h / VIX-1m que tu cites = la news a sur-pesé un quant qui avait raison. Le bon
correctif n'est pas « la news ne pèse plus jamais », c'est « la news ne pèse trop QUE quand
elle le mérite ».

Cas où la news DOIT primer (sinon le desk perd de l'argent) :
- **Choc d'offre dur et frais** : Ormuz fermé, frappe sur Natanz, blocus mer Noire. Le
  momentum prix d'avant est invalidé en quelques heures — le prix n'a pas encore pricé.
  Interdire l'inversion ici = rester short un marché qui gappe +8%.
- **Renversement de régime confirmé** : OPEC cut surprise vs consensus hike. Le quant
  (term structure, COT) est en retard d'un cycle.

Cas où la news NE doit PAS primer (ton vrai problème) :
- **News = momentum déjà coté** (#6 streak, records, inflows). Descriptif passé vendu comme
  forward. Le prix a déjà bougé → la news ne doit rien inverser.
- **Commentaire verbal** (Fed speakers #178/#204) : pas de contenu directionnel dur.
- **Panier risk-off plaqué** (#13/#29 demande faible → BRENT L à tort).

Reco desk — remplacer l'interdiction sèche par un **override conditionnel** (3 conditions
cumulatives pour que la news prime/inverse) :

1. **Fraîcheur** : event ≤ 48h (sinon le prix a déjà arbitré — c'est déjà la logique
   « LE PRIX NE MENT PAS » du SYSTEM_PROMPT, on la durcit).
2. **Matérialité haute + reliability confirmed/reported** (pas rumor, pas verbal).
3. **Type = choc structurel d'offre/régime** (pas momentum-déjà-coté, pas single-name).

Si les 3 ne sont pas réunies → la news est **plafonnée** (ne peut pas dépasser, disons, la
contribution nette du bloc quant) au lieu d'être interdite. C'est le `_has_contradictory_high_impacts`
qui existe déjà (cap conviction high→medium) généralisé en « cap vs prix ». Par défaut donc :
la news NE renverse PAS (ton intention est le défaut) ; elle renverse SEULEMENT sous les 3 gates.

---

## 3. Le vrai manque : structurel vs frais-déjà-price — le plan le règle-t-il ?

NON. Et c'est le seul changement qui attaque la cause racine. Les réglages 1 et 2 sont des
rustines sur le symptôme (intensité) ; le manque est informationnel.

Aujourd'hui la synthèse DeepSeek ne sait pas distinguer :
- une news **structurelle** (OPEC cut → effet qui dure des semaines, doit tenir à 1m),
- d'une news **fraîche mais déjà price** (#6 streak → effet nul forward),
- ni tracer un **event_id/date** stable pour dé-dupliquer une news re-publiée (le marché
  l'a déjà jouée hier, elle ressort aujourd'hui → on la re-compte à tort).

Ce qu'il faut AJOUTER (et qui manque vraiment) :

- **`event_id` + `event_date` tracés** par event dans l'events-log et propagés jusqu'à la
  synthèse. Permet : dé-duplication, calcul de fraîcheur réel (pas l'âge de la ligne de log),
  et l'override conditionnel du §2.
- **Flag `nature` ∈ {structurel, ponctuel/choc, momentum-déjà-coté, verbal}** posé par
  l'extracteur. C'est ce flag qui devrait piloter la courbe de pertinence par horizon (un choc
  ponctuel décroît vite, un structurel monte vers 1m) — exactement la logique déjà codée en
  dur dans les `pertinence` des fiches, mais qu'on rendrait DATA-DRIVEN par event au lieu de
  figée par critère.
- **Garde « vs consensus / déjà price »** : la synthèse réagit au NIVEAU, pas à l'écart aux
  attentes (angle mort #50 de l'audit DeepSeek). Une news conforme au consensus ou un mouvement
  déjà réalisé → contribution forward ~0. C'est ce qui aurait neutralisé Or-24h / VIX-1m
  proprement, sans casser Ormuz.

---

## Reco finale (ordre de priorité desk)

1. **NE PAS** ajouter le decay_factor global. Garder la pertinence par critère ; ajuster
   les courbes qui mentent (géopol pétrole trop forte à 7j → baisser ; OPEC OK, ne pas toucher).
2. **Remplacer** « news n'inverse jamais » par un override conditionnel à 3 gates
   (fraîcheur ≤48h + matérialité high/confirmed + type=choc structurel). Défaut = la news ne
   renverse pas ; elle renverse seulement sous gates. Réutiliser `_has_contradictory_high_impacts`.
3. **Ajouter** `event_id`/`event_date` + flag `nature` + garde « déjà price/vs consensus ».
   C'est la cause racine. Sans ça, on règle des chiffres à l'aveugle.

Net : le plan corrige le symptôme (intensité) avec un outil (decay global) qui casse la
distinction structurel/ponctuel déjà acquise. La valeur est dans la pertinence par critère
+ le tracking event_id/nature, pas dans un multiplicateur uniforme.

---

### Handoff

- **Fichiers concernés** : `v3/config/fiches/*.yml` (pertinence par critère), `v3/scripts/synthese_directionnelle.py` (override conditionnel, garde fraîcheur/vs-consensus), `v3/scripts/triggers_classifier.py` (propagation event_id/nature + cap vs prix), `v3/scripts/extractor.py` (flag nature, event_id/date).
- **À trancher avec Thomas** : valeur du cap d'override (news ≤ contribution nette quant ? ou facteur ×1.5 ?) et seuil de fraîcheur (48h proposé).
- **Décision** : NO-GO decay global, NO-GO interdiction sèche, GO override conditionnel + tracking event_id/nature.
- **Non couvert ici** : calibration chiffrée des nouvelles courbes de pertinence (à faire par actif, hors revue).
