# Reco wording — Tableau « Détail par actif »

> Livrable @copywriter → @fullstack. Strings finales, prêtes à câbler.
> Aucun chiffre ni logique modifiés — uniquement les libellés.
> Branche : claude/elegant-ramanujan-OIKms

---

## 1. Nouveaux en-têtes de colonnes

[Framework : FAB — chaque colonne : ce qu'elle est → ce qu'elle dit → ce que Thomas en fait]

**Tableau actuel (10 colonnes) :**
```
| Critère | Type | Valeur brute | Norm. | Poids | Signe | 24h | 7j | 1m | Note |
```

**Tableau proposé (9 colonnes — colonne « Note » supprimée, voir §4) :**
```
| Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m |
```

**Justification colonne par colonne :**

| Ancienne | Nouvelle | Pourquoi |
|---|---|---|
| Critère | Critère | Inchangé — déjà clair |
| Type | Comment c'est lu | Traduit la méthode en question que Thomas se pose naturellement |
| Valeur brute | Valeur actuelle | « Brute » implique « pas fiable » — « actuelle » dit juste « c'est le chiffre en ce moment » |
| Norm. | Penchant | Court, trader, dit exactement ce que c'est : dans quel sens penche ce critère |
| Poids | Importance | Universel, sans jargon |
| Signe | Sens | Gardé — complété par §3 ci-dessous |
| 24h / 7j / 1m | Effet 24h / Effet 7j / Effet 1m | « Effet » + horizon = contribution lisible (pousse LONG ou SHORT sur ce délai) |
| Note | — | Supprimée (voir §4) |

---

## 2. Table de traduction des `type`

Règle : 2-4 mots max, compréhensible sans explication.

| Valeur code (`type`) | Libellé affiché dans le tableau |
|---|---|
| `zscore` | Écart à la normale |
| `lineaire` | Échelle graduée |
| `mapping_non_monotone` | Régime par seuils |
| `composite` | Signal combiné |
| `triplet` | Direction news |
| `gate` | Drapeau régime |

**Notes de traduction :**

- **Écart à la normale** : Thomas comprend instinctivement — « ce taux est 2× au-dessus de sa moyenne récente ». Évite « z-score » et « percentile ».
- **Échelle graduée** : dit qu'il y a une règle (neutre quelque part, extrêmes aux bouts). Si le contexte `centre=75 echelle=12` doit être visible → voir §5.
- **Régime par seuils** : le VIX à 18 vs 25 vs 40 = des régimes différents, pas une progression linéaire. « Seuils » dit ça.
- **Signal combiné** : plusieurs signaux sous-jacents fusionnés en un seul. Court, exact.
- **Direction news** : issu des news, donne une direction (pas un niveau). Différencie bien du quantitatif.
- **Drapeau régime** : hors score normal — c'est un signal d'alerte sur le régime de marché. « Drapeau » = attention, pas une mesure ordinaire.

---

## 3. Reformulation de la colonne « Sens »

**Problème actuel :** `+1` / `-1` — incompréhensible sans notice.

**Proposition — strings exactes à afficher dans la cellule :**

| Valeur code | Libellé affiché | Lecture en clair |
|---|---|---|
| `+1` | `normal` | Quand le critère monte → haussier pour l'actif |
| `-1` | `inversé` | Quand le critère monte → baissier pour l'actif (ex. taux réels hauts = mauvais pour l'or) |

**Exemple concret prêt à câbler (colonne Sens) :**
- Taux 10Y US réels (TIPS), signe = -1 → affiche : `inversé`
- RSI 14 jours, signe = +1 → affiche : `normal`

**Alternative avec icône si le template HTML le permet (optionnel, à valider avec @fullstack) :**
- `+1` → `↑ normal`
- `-1` → `↓ inversé`

Recommandation : commencer avec le texte seul (`normal` / `inversé`) — plus robuste sur mobile et email.

---

## 4. Reco sur la colonne « Note »

**Verdict : supprimer.**

Actuellement, « Note » répète le type (ex. `zscore (pré-calculé)`, `lineaire centre=75 echelle=12`). Une fois la colonne « Comment c'est lu » bien formulée (§2), la Note n'apporte rien de nouveau — elle surcharge le tableau sans décision supplémentaire pour Thomas.

Si le paramètre technique (`centre=75 echelle=12`) doit rester accessible → le déplacer en **infobulle** sur la cellule « Comment c'est lu » (hover sur desktop, tap sur mobile), pas dans le tableau principal. C'est un détail de calibration, pas une info de décision.

**Ce que @fullstack fait :**
1. Supprimer la colonne `Note` du template HTML du bulletin
2. Si souhaité : ajouter un attribut `title="centre=75, échelle=12"` sur les cellules `Échelle graduée` — Thomas peut accéder à la valeur technique sans qu'elle pollue la lecture normale

---

## 5. Encart « Comment lire ce tableau »

[Niveau de conscience : Problem-Aware — Thomas sait que le tableau est dur à lire, pas encore à l'aise avec la mécanique]

À placer **une seule fois**, au-dessus de la première section « Détail par actif » du bulletin. Pas répété par actif.

**String exacte à câbler (HTML ou Markdown selon le template) :**

---

**Comment lire ce tableau**

Chaque ligne est un critère qui influence la direction de l'actif.

- **Penchant** (de −1 à +1) : à quel point ce critère pousse dans un sens. −1 = fortement baissier, +1 = fortement haussier, 0 = neutre.
- **Importance** : le poids de ce critère dans la note finale. Un critère à 8 compte 4× plus qu'un critère à 2.
- **Sens** : `normal` = quand la valeur monte, c'est haussier. `inversé` = quand la valeur monte, c'est baissier (ex. des taux réels élevés pèsent sur l'or).
- **Effet 24h / 7j / 1m** : la contribution chiffrée de ce critère à chaque horizon. Positif = pousse LONG, négatif = pousse SHORT. La somme de tous les effets donne la note finale.

---

**Longueur :** 5 lignes de contenu (dans la limite des 4-6 demandées). Pas d'en-tête lourd — le titre « Comment lire ce tableau » suffit.

---

## 6. Traitement du paramètre `lineaire centre=X echelle=Y`

**Recommandation : retirer de la vue principale.**

Le paramètre `centre=75.0 echelle=12.0` est utile pour calibrer le modèle, pas pour décider LONG/SHORT. Thomas n'en a pas besoin pour lire le bulletin.

**Ce qui s'affiche dans le tableau :** `Échelle graduée` (colonne « Comment c'est lu »).

**Ce qui disparaît :** `lineaire centre=75.0 echelle=12.0` (retiré du rendu HTML).

**Si Thomas veut y accéder un jour :** le `decision-log` JSONL le contient déjà. Pas besoin de l'exposer dans la vue bulletin.

---

## Handoff → @fullstack

**Fichier produit :** `/home/user/TradingApp/v3/audit/reco-wording-detail-bulletin.md`

**Décisions prises (non négociables) :**
1. En-têtes finaux : `Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m`
2. Colonne `Note` : **supprimée**
3. Traductions `type` : voir §2 (strings exactes)
4. Colonne `Sens` : `normal` (pour +1) / `inversé` (pour -1) — texte seul, pas d'icône en V1
5. Encart « Comment lire ce tableau » : string exacte au §5, une seule occurrence par bulletin
6. Paramètre `lineaire centre=X echelle=Y` : **retiré de la vue**, présent uniquement dans le decision-log

**Points d'attention pour @fullstack :**
- Le fichier `scoring_analyste.py` l.1989 contient les en-têtes actuels — c'est là que la substitution se fait
- Vérifier que `build_html.py` masque bien les bonnes colonnes sur mobile après renommage (le masquage actuel cible probablement les colonnes par position ou par nom)
- L'encart « Comment lire ce tableau » est statique — une seule insertion dans le template HTML, pas générée ligne par ligne
- Zéro changement de valeur, score ou logique — uniquement les libellés

**Ne commit pas ce fichier** — l'orchestrateur regroupe les commits de la session.
