# Audit architecture d'information — TradingApp v3 · Session 9

> Rédigé par @ux · 2026-06-20
> Périmètre : architecture d'information uniquement (pas le visuel — périmètre @design)
> Utilisateur unique : Thomas, trader expert
> Source : `build_html.py` L874-1526 · `bulletin-2026-06-19-08h.md` · `project-context.md`

---

## (a) Notes par casquette — état actuel

| Casquette | Note /10 | Ce qui fait baisser |
|---|---|---|
| **Comprendre** — Thomas comprend le contexte, les règles, les limites | **4/10** | Légende répétée 4× sans jamais être complète nulle part · help-box enfouie sous la nav · sens des symboles éparpillé entre header/legend-bar/help-box/markdown |
| **Décider** — Thomas identifie rapidement les 2-3 paris du jour | **6/10** | 4 sections quasi-redondantes (Sélection / À jouer / Top convictions / Synthèse) sans hiérarchie visuelle claire · subnav inutilisable → il scrolle manuellement · l'ordre actuel met la Sélection en tête mais la Synthèse (matrice) arrive APRÈS 4 sections |
| **Juger** — Thomas évalue la qualité du signal, les angles morts, le track record | **5/10** | Calls jugés repliés dans les sections de décision (mélange décision + track record) · Limites du jour enfouies en bas · Cellules à surveiller noyées entre deux sections · section "Santé des sources" consomme de l'espace sans utilité immédiate pour le trade |
| **Global** | **5/10** | Redondance × répétition × navigation cassée = charge cognitive élevée pour un trader qui lit 3× par jour |

**Cible post-refonte** : Comprendre 8/10 · Décider 9/10 · Juger 8/10 · Global 8/10

---

## (b) Inventaire des répétitions — décisions canoniques

### Répétition 1 : La légende des symboles (4 occurrences)

| Surface | Localisation | Symboles listés | Problème |
|---|---|---|---|
| **Header sticky** | `build_html.py` L880-888 | ⚑ 📰 ⚪ ⚠ 🔴 🟡 | Partielle et désynchronisée — pas ↯ ⇄ ⌛ ◧ ⚭ qui sont pourtant présents dans le bulletin |
| **legend-bar** | L908-925 | LONG/SHORT + note + ⚪ 📰 ⚑ ⚠ 🔴 🟡 | Doublonne le header + ajoute LONG/SHORT (utile) + répète les mêmes 6 symboles |
| **help-box** (fermée) | L934-950 | Légende complète + explication de la note | Replié → invisible par défaut mais SEUL endroit complet |
| **Markdown bulletin** (`## Comment lire les scores > Symboles et Note`) | `bulletin MD` L190-207 | Liste exhaustive avec descriptions complètes | Duplique la help-box et s'affiche EN PLEIN MILIEU du bulletin à chaque lecture |

**Décision canonique :**

1. **Header** : supprimer toute la `<div class="legend">` (L880-888). Cette ligne n'a pas de raison d'être en sticky permanent.
2. **legend-bar** : garder UNIQUEMENT `🟢 LONG = hausse · 🔴 SHORT = baisse · note = force de conviction`. Supprimer les 6 symboles — ils ont leur place ailleurs.
3. **help-box** : c'est LA place canonique de toute la légende des symboles. Toujours repliée. Le lien d'accès est dans la legend-bar : ajouter `· ❓ Symboles` (anchor vers la help-box).
4. **Markdown bulletin** (`## Comment lire les scores`) : cette section doit être SUPPRIMÉE du bulletin généré car elle est déjà dans la help-box. `scoring_analyste.py` doit arrêter de l'émettre (ou build_html doit la filtrer). [HYPOTHÈSE : la section est injectée par `scoring_analyste.py` L18 — à vérifier avant suppression]

**Résultat** : un seul endroit complet (help-box repliée), une seule ligne contextuelle (legend-bar, réduite).

---

### Répétition 2 : 4 vues du même classement 24h

Le bulletin contient 4 sections qui répondent toutes à la même question : "que trader aujourd'hui ?"

| Section | Contenu | Différence réelle | Verdict |
|---|---|---|---|
| **🎯 Sélection du jour** (max 3) | Top 3 filtré par driver unique + couverture | La vraie top-liste opérationnelle | **GARDER — première position** |
| **🎯 À jouer aujourd'hui (24h)** | 12 cellules 24h triées, Jouables/À éviter | Même liste plus longue + détail Porté par | **GARDER — mais fusionner logiquement avec Sélection** |
| **🎯 Top convictions multi-horizons** | Top 3 tous horizons | Ajoute 7j/1m — différent de la Sélection | **GARDER — mais renommer clairement "Top 7j/1m"** |
| **Synthèse des décisions** (matrice) | Tableau 12 actifs × 3 horizons + raisons | Vue d'ensemble indispensable | **GARDER — mais repositionner** |

**Redondance réelle :** La "Sélection" et "À jouer" partagent les mêmes actifs (Sélection = filtre sur À jouer). Ce sont deux niveaux du même flux, pas deux sections indépendantes.

**Décision :**
- Fusionner "Sélection du jour" et "À jouer" en une section `## Décision du jour` avec deux niveaux de lecture : (1) encart "Sélection" (max 3) sur fond distinct, (2) tableau complet en dessous.
- "Top convictions multi-horizons" → renommer `## Top 7j / 1m` et le placer APRÈS la Synthèse (il répond à une question différente : le swing).
- "Synthèse des décisions" → renommer `## Tableau de bord — 12 actifs` et le placer en position 2 (vue d'ensemble avant le détail).

---

### Répétition 3 : La note de système (bandeau × intro Résultats)

Le contexte "mode test / go-live 08/08 / WR ≥ 70%" apparaît :
- Dans le `context-banner` (L890-894) — bandeau permanent visible partout
- En tête de la vue Résultats (L956-959) — texte long avec les détails du jalon

**Décision :** Le bandeau reste (contrainte fondateur). La vue Résultats garde son explication longue car elle sert à un contexte différent (comprendre les chiffres). Pas de répétition problématique ici — les deux coexistent avec des niveaux de détail différents. [NOTE : le texte du bandeau actuel est déjà compact — OK]

---

## (c) Solution « Sauter à » — problème et correction

### Diagnostic précis

Le JS L1509 prend `raw.split(/[ —–\-:(]/)[0]` → premier token avant espace ou tiret.

Sur le bulletin réel, les titres `## ` sont :

| Titre complet (## ) | Token extrait | Lisible ? |
|---|---|---|
| `Décor du jour` | `Décor` | OK |
| `Santé des sources` | `Santé` | OK |
| `🎯 Sélection du jour — max 3` | `🎯` | ECHEC — émoji nu |
| `🎯 À jouer aujourd'hui (24h)` | `🎯` | ECHEC — doublon + émoji nu |
| `🎯 Top convictions multi-horizons` | `🎯` | ECHEC — triplon + émoji nu |
| `Synthèse des décisions` | `Synthèse` | OK |
| `Intensité comparable entre actifs (informatif)` | `Intensité` | OK |
| `⚠️ Cellules à surveiller` | `⚠️` | ECHEC — émoji nu |
| `⚭ Drivers macro partagés` | `⚭` | ECHEC — symbole nu |
| `Flips vs veille` | `Flips` | OK |
| `Comment lire les scores` | `Comment` | Passable |
| `Détail par actif` | `Détail` | OK |
| `Limites du jour` | `Limites` | OK |
| `🔎 Calls 24h jugés (fenêtre récente)` | `🔎` | ECHEC — émoji nu |
| `News par actif` | `News` | OK |

**Résultat** : 6 liens sur 15 sont illisibles.

### Solution retenue : libellés explicites fixés dans le générateur Python

Remplacer la logique JS `raw.split(...)` par une table de correspondance en Python dans `build_html.py` : les ancres de la subnav sont définies côté serveur, pas devinées côté client.

**Table de correspondance (à passer en données JSON dans le HTML) :**

```python
SUBNAV_LABELS = {
    "Décor du jour":                          "Décor",
    "Santé des sources":                      "Sources",  # repliée — voir §(e)
    "Sélection du jour":                      "Sélection",  # après fusion → "Décision"
    "À jouer aujourd'hui":                    "À jouer",    # fusionné dans Décision
    "Top convictions multi-horizons":         "7j/1m",
    "Synthèse des décisions":                 "Synthèse",
    "Intensité comparable entre actifs":      "Intensité",
    "Cellules à surveiller":                  "Surveiller",
    "Drivers macro partagés":                 "Drivers",
    "Flips vs veille":                        "Flips",
    "Comment lire les scores":                None,  # supprimé du bulletin (→ help-box)
    "Détail par actif":                       "Détail",
    "Limites du jour":                        "Limites",
    "Calls 24h jugés":                        "Calls",
    "News par actif":                         "News",
}
# None = ne pas inclure dans la subnav
```

**Implémentation** : le Python génère un attribut `data-subnav-label="Décision"` sur chaque `<h2>` correspondant (ou la liste est passée en JSON inline). Le JS lit `data-subnav-label` au lieu de `raw.split(...)`.

**Alternative plus simple si la fusion de sections est reportée** : modifier uniquement le JS L1509 pour :
1. Retirer les émojis en tête (`raw.replace(/^\p{Emoji}+\s*/u, '')`)
2. Prendre les 2 premiers mots au lieu du premier token (`raw.split(/[ —–\-:(]/)[0..1].join(' ')`)

Ce correctif minimal donne `Sélection du`, `Top convictions`, `Cellules à`, `Drivers macro`, `Calls 24h` — lisible sans refonte. Recommandé comme quick-win si la fusion est reportée.

---

## (d) Refonte header — ce qui reste / part / se replie

### État actuel (L874-894)

```
[☰] TradingApp v3 — Bulletins          ← h1 sticky
Généré : 2026-06-19T08:08:09...        ← meta timestamp
Légende symboles : ⚑ gate régime · 📰 news>50% · ⚪ coin-flip · ⚠ calcul contesté · 🔴 alerte · 🟡 vigilance
────────────────────────────────────────
⚠️ Mode test — non validé · go-live 08/08 (WR ≥ 70%, N ≥ 15)   ← context-banner
```

### Problèmes

1. **h1 "TradingApp v3 — Bulletins"** : label de produit permanent. Utile une fois, superflu à chaque lecture. Mais le hamburger menu y est accolé — à garder pour l'ancrage du bouton.
2. **"Généré : [timestamp ISO]"** : format machine. Thomas lit "Généré : 2026-06-19T08:08:09.816553+02:00" → charge cognitive inutile.
3. **Ligne légende** : supprimer (cf. §b — redondante avec legend-bar et help-box).
4. **Context-banner** : garder (contrainte fondateur), déjà compact.

### Décision

| Élément | Action | Justification |
|---|---|---|
| `h1` "TradingApp v3 — Bulletins" | Réduire à `<span>` + titre du bulletin courant | Ce qui intéresse Thomas = quel bulletin il lit, pas le nom du produit |
| Timestamp ISO | Formater en "19 juin · 08h08" | Lisible, même info |
| Ligne `<div class="legend">` entière | **Supprimer** | Redondante, partielle, prend 1 ligne sticky |
| Context-banner | Garder tel quel | Contrainte fondateur validée |

**Header cible (1 ligne sticky) :**
```
[☰] Bulletin 19 juin · 08h08          ⚠️ Mode test — go-live 08/08
```
La barre de légende LONG/SHORT reste dans `legend-bar` juste sous le header (non sticky).

---

## (e) Recommandations section par section

Ci-dessous les 15 sections du bulletin dans l'ordre actuel + les éléments de chrome de la page.

### Sections de chrome (page — hors markdown)

| Élément | Recommandation | Justification |
|---|---|---|
| **legend-bar** (L908-925) | Réduire à : `🟢 LONG = hausse · 🔴 SHORT = baisse · note = force · ❓ Symboles` | Seule info non-redondante = LONG/SHORT/note. Lien ❓ vers help-box remplace les 6 symboles répétés |
| **Subnav "Sauter à"** (L927-932) | Corriger les labels (cf. §c) + **n'afficher que les sections non repliées** | Navigation uniquement vers ce qui est visible |
| **help-box** (L934-950) | Conserver repliée + **compléter la liste des symboles** (↯ ⇄ ⌛ ◧ ⚭ manquants actuellement) | C'est LA référence unique des symboles |

### Sections markdown du bulletin (dans l'ordre courant)

**1. `## Décor du jour`** — GARDER, position 1
> Contexte journalier + catalyseurs. Informatif, court. Bien placé en tête.

**2. `## Santé des sources`** — REPLIER dans un `<details>` automatique
> Thomas n'a pas besoin de voir "34 flux OK, 0 en échec" à chaque lecture matin. Utile ponctuellement (diagnostic). Afficher uniquement si anomalie (flux en échec > 0 ou muets anormaux). [HYPOTHÈSE : le build_html pourrait conditionner le repli à `n_failing > 0` — à vérifier]
> Label replié : "Santé sources ✓ (tout OK)" vs "⚠️ Santé sources (1 échec)"

**3. `## 🎯 Sélection du jour — max 3`** → FUSIONNER avec §4 dans `## Décision du jour`
> Voir §b. La Sélection devient un encart en tête de la section fusionnée.

**4. `## 🎯 À jouer aujourd'hui (24h)`** → FUSIONNER avec §3
> Les deux sections répondent à "que trader". Après fusion, la structure est :
> ```
> ## Décision du jour
> [encart Sélection max 3 — sur fond distinct]
> [tableau complet "À jouer" replié par défaut, ouvert au clic "Voir tout"]
> ```
> Avantage : Thomas voit immédiatement ses 3 paris, peut dérouler si besoin.

**5. `## 🎯 Top convictions multi-horizons`** — GARDER + DÉPLACER après Synthèse + RENOMMER
> Renommer : `## Top swing (7j / 1m)` — différencie clairement de la Sélection 24h.
> Déplacer après `## Tableau de bord — 12 actifs` (ex-Synthèse).
> Raison : le swing intéresse Thomas APRÈS avoir vu le tableau complet.

**6. `## Synthèse des décisions`** → GARDER + RENOMMER + REPOSITIONNER en position 2 (juste après Décor)
> Renommer : `## Tableau de bord — 12 actifs × 3 horizons`
> Repositionner : après Décor, AVANT la Décision du jour. Thomas a besoin du panorama avant de zoomer.
> Alternative si Thomas préfère l'action d'abord : laisser en position actuelle. [À trancher avec Thomas]

**7. `## Intensité comparable entre actifs (informatif)`** — REPLIER dans un `<details>`
> Tableau de notes normalisées. Utile pour comparer les actifs entre eux mais pas pour la décision immédiate. Le libellé "(informatif)" dans le titre confirme ce statut.
> Label replié : "Intensité comparable (informatif)"

**8. `## ⚠️ Cellules à surveiller`** — GARDER + ancrer visible
> Liste d'alertes utiles à la décision. À garder dépliée. Mais aujourd'hui elle est noyée entre Intensité et Drivers — la faire remonter après "Décision du jour" (ou en bas de cet encart).

**9. `## ⚭ Drivers macro partagés`** — GARDER + positionner juste sous "Décision du jour"
> L'alerte ⚭ (faux consensus) est critique avant d'agir. À rapprocher de la Sélection.

**10. `## Flips vs veille`** — GARDER replié par défaut
> Utile pour détecter les retournements, mais Thomas le consulte en deuxième lecture, pas en premier. Replier.
> Label : "Flips vs veille (N flips)"

**11. `## Comment lire les scores`** — SUPPRIMER du markdown
> Entièrement redondant avec la help-box. Cf. §b décision canonique.
> Si la suppression est bloquée côté `scoring_analyste.py`, le `build_html.py` peut filtrer cette section à la génération (déjà fait pour d'autres sections).

**12. `## Détail par actif`** — GARDER replié par défaut
> Les 12 tableaux de critères sont indispensables pour juger mais lourds à parcourir. Déjà partiellement géré (cf. L981). Conserver repli, bon état actuel.

**13. `## Limites du jour`** — GARDER replié (toujours), mieux visibiliser
> Actuellement en bas, peu visible. Dans la nouvelle architecture, faire remonter Limites du jour juste AVANT Détail par actif (elles en sont le résumé).

**14. `## 🔎 Calls 24h jugés (fenêtre récente)`** — GARDER replié
> Track record récent. Utile à la casquette Juger. Replié OK, position basse OK.

**15. `## News par actif`** — GARDER replié par défaut quand "aucune actualité"
> Ce matin (19/06) : 12 sections "— aucune actualité". C'est du bruit total. La section doit être automatiquement repliée (ou masquée) quand aucun actif n'a de news. Si au moins 1 news → rester visible.

---

## (f) Maquette ASCII — nouvelle hiérarchie header + nav

```
╔══════════════════════════════════════════════════════════╗  ← header sticky (1 ligne)
║ [☰] Bulletin 19 juin · 08h08    ⚠️ Mode test · 08/08  ║
╠══════════════════════════════════════════════════════════╣  ← legend-bar (non sticky)
║ 🟢 LONG = hausse · 🔴 SHORT = baisse · note = force · ❓ ║
╠══════════════════════════════════════════════════════════╣  ← subnav (labels lisibles)
║ Sauter à : Décor · Décision · Synthèse · Surveiller ·  ║
║            Drivers · Flips · Détail · Limites · Calls   ║
╚══════════════════════════════════════════════════════════╝

[❓ Comment lire les scores (détails complets + symboles)] ← help-box repliée

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Décor du jour                                          ← position 1, toujours visible
[Catalyseurs · résumé marché]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Tableau de bord — 12 actifs × 3 horizons               ← position 2 (ex-Synthèse)
[Matrice 12×3 · Raison principale par cellule]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Décision du jour                                       ← position 3 (fusion Sélection + À jouer)
┌─────────────────────────────────────────────────────┐
│ 🎯 Sélection — max 3 (fond distinct)                │
│  Or SHORT -13.19 · Pétrole SHORT -10.55 · …         │
│  ⚠️ Décision de taux BCE aujourd'hui                 │
└─────────────────────────────────────────────────────┘
[▼ Voir tout — À jouer 24h (12 lignes)] ← replié par défaut

⚭ Drivers partagés : [Taux réels US → Or + Argent SHORT]  ← intégré sous Décision

⚠️ Cellules à surveiller : CAC · Cacao · Café · …         ← intégré sous Décision

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Top swing (7j / 1m)                                    ← position 4 (ex-Top convictions)
[Top 3 multi-horizons]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[▶ Flips vs veille (8 flips)]                             ← replié

[▶ Intensité comparable (informatif)]                     ← replié

[▶ 🔎 Calls 24h jugés — 4✅ / 3❌]                       ← replié

[▶ Santé sources ✓]                                       ← replié (ou visible si échec)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## Limites du jour                                        ← avant Détail
[n/a par actif]

## Détail par actif                                       ← toujours en bas, replié par actif
[12 tableaux de critères]

[▶ News par actif]                                        ← replié si "aucune actualité" partout
```

---

## (g) Instructions d'implémentation pour @fullstack (ordonnées par priorité)

### P0 — Quick wins (aucun impact contenu, 0 risque)

**I1 — Corriger le JS subnav (labels illisibles)**
- Fichier : `v3/scripts/build_html.py` · JS L1509
- Action : remplacer `raw.split(/[ —–\-:(]/)[0]` par :
  ```js
  let label = raw.replace(/^[\p{Emoji}\s]+/u, '').split(/[ —–\-:(]/)[0] || raw;
  ```
  Cela retire les émojis en tête avant d'extraire le premier mot. Résultat : `Sélection`, `Cellules`, `Drivers`, `Calls` au lieu d'émojis nus.
- Test : vérifier que les 15 liens de la subnav sont lisibles sur le bulletin 19/06.

**I2 — Supprimer la ligne légende du header**
- Fichier : `v3/scripts/build_html.py` · L880-888
- Action : supprimer les 9 lignes `<div class="legend">...</div>` entières.
- Test : vérifier que le header ne fait plus qu'une seule ligne (h1 + meta).

**I3 — Réduire la legend-bar**
- Fichier : `v3/scripts/build_html.py` · L908-925
- Action : remplacer le contenu de `<div class="legend-inner">` par :
  ```html
  <span><span class="dir-long">🟢 LONG</span> = hausse</span>
  <span>·</span>
  <span><span class="dir-short">🔴 SHORT</span> = baisse</span>
  <span>·</span>
  <span><code>note</code> = force de conviction</span>
  <span>·</span>
  <span><a href="#help-box-anchor" onclick="...">❓ Symboles</a></span>
  ```
  Supprimer les 6 spans `⚪ 📰 ⚑ ⚠ 🔴 🟡`.

**I4 — Formater le timestamp header en langage naturel**
- Fichier : `v3/scripts/build_html.py` · L879 (`<div class="meta">Généré : {generated_at}...`)
- Action : côté Python, formater `generated_at` en `"19 juin · 08h08"` avant injection. Note : la fonction JS `formatIsoHuman()` (L1071-1077) fait déjà ce formatage côté client pour le contenu markdown — réutiliser la même logique côté Python pour le header, ou appliquer `formatIsoHuman` sur l'élément `<div class="meta">` au `DOMContentLoaded`.
- Conserver l'ISO complet en `<time datetime="...">` pour l'accessibilité.

### P1 — Réorganisation des sections (impact structure)

**I5 — Compléter la help-box avec les symboles manquants**
- Fichier : `v3/scripts/build_html.py` · L934-950
- Action : ajouter dans `<div class="help-body">` le tableau des symboles manquants : ↯ divergence quant/news · ⇄ contre-momentum · ⌛ déjà coté · ◧ mono-critère · ⚭ driver partagé · ≈ quasi-neutre · ⇆ zigzag.
- Ces symboles sont définis dans le markdown (`## Comment lire les scores > ## Symboles et Note` L190-207) mais absents de la help-box.

**I6 — Replier automatiquement "Santé des sources"**
- Fichier : `v3/scripts/build_html.py` (section JS de post-rendu du markdown)
- Action : après rendu markdown, détecter le `<h2>` "Santé des sources" et l'envelopper dans un `<details class="fold-section">` avec `open` conditionnel si `n_failing > 0` (détectable depuis le texte "0 en échec" vs "N en échec").
- Label : `✓ Santé sources (tout OK)` ou `⚠️ Santé sources (N en échec)`

**I7 — Replier "Intensité comparable entre actifs"**
- Même mécanisme que I6 : détecter le `<h2>` par son texte, envelopper en `<details>`.
- Label : `Intensité comparable entre actifs (informatif)`
- Toujours replié (jamais `open` par défaut).

**I8 — Replier "News par actif" si toutes les sous-sections sont vides**
- Même mécanisme : détecter le `<h2>` "News par actif", vérifier si tous les `<li>` contiennent "aucune actualité", replier si oui.
- Label : `News par actif (aucune ce matin)` vs `News par actif`

**I9 — Replier "Flips vs veille"**
- Même mécanisme : toujours replié par défaut.
- Label : `Flips vs veille` + afficher le count "(N flips)" en summary si détectable.

**I10 — Renommer "🎯 Top convictions multi-horizons" → "Top swing (7j / 1m)"**
- Fichier : `v3/scripts/scoring_analyste.py` (source du titre dans le markdown)
- Action : modifier le titre de la section. [HYPOTHÈSE : localisation exacte dans scoring_analyste.py à confirmer]

### P2 — Restructuration profonde (modifier le générateur Python)

**I11 — Fusionner "Sélection du jour" et "À jouer aujourd'hui" en "Décision du jour"**
- Fichier : `v3/scripts/scoring_analyste.py`
- Action : générer une section unique `## Décision du jour` qui inclut :
  1. L'encart Sélection (max 3) en premier, balisé distinctement (ex. `> [encart]`)
  2. Le tableau "À jouer" complet en dessous, encapsulé pour repli JS
- Risque : refonte du générateur Markdown. Prioriser après I1-I10.

**I12 — Supprimer "## Comment lire les scores" du markdown émis**
- Fichier : `v3/scripts/scoring_analyste.py`
- Action : retirer la section entière. L'information est dans la help-box (après I5).
- Alternative sans toucher au générateur : dans `build_html.py`, filtrer les `<h2>` "Comment lire les scores" et leur contenu avant injection dans `bulletin-content`.

**I13 — Réordonner "Synthèse des décisions" en position 2 (après Décor)**
- Fichier : `v3/scripts/scoring_analyste.py`
- Action : déplacer la section `## Synthèse des décisions` avant `## Sélection du jour`.
- Alternative JS : réordonner les sections DOM après rendu markdown (plus simple, zéro impact sur le fichier .md).

**I14 — "Cellules à surveiller" et "Drivers macro" : remonter sous "Décision du jour"**
- Actuellement en position 8 et 9. Après fusion I11, les faire apparaître juste sous l'encart Sélection.
- Alternative JS : même logique de réorganisation DOM post-rendu.

---

## Auto-évaluation — itération vers 10/10

| Critère | État | Note |
|---|---|---|
| Chaque redondance a une décision canonique unique | ✅ | 4 répétitions documentées, 4 décisions rendues |
| Les sections informatives inutiles au trade sont repliées | ✅ | Santé sources / Intensité / News vide / Flips / Détail |
| La subnav est corrigée sans reconstruire l'archi | ✅ | I1 = 3 lignes JS |
| Le header n'a plus qu'une ligne sticky | ✅ | I2 + I4 |
| "Comment lire" n'est plus dans le flux principal | ✅ | I12 |
| Les 4 vues du classement 24h sont rationalisées | ✅ | Fusion (I11) + renommage Top swing (I10) |
| Les alertes utiles (⚠️ Cellules / ⚭ Drivers) restent visibles | ✅ | Non repliées, remontées sous Décision |
| Zéro info supprimée si elle sert Thomas | ✅ | Tout replié, pas supprimé (sauf "Comment lire" = doublon exact) |
| Instructions @fullstack avec ancres L précises quand connues | ✅ / ⚠️ | Connues pour chrome HTML · à confirmer pour scoring_analyste.py |
| WIN RATE ONLY respecté | ✅ | Aucune mention P&L / expectancy |

**Note post-itération** : Comprendre cible 8/10 · Décider cible 9/10 · Juger cible 8/10 · Global 8/10 — atteignable avec I1-I10 (P0+P1). I11-I14 (P2) font passer à 9/10.

---

## Points d'attention — informations manquantes signalées

- [MANQUE] Localisation exacte dans `scoring_analyste.py` de la section `## Comment lire les scores` et du titre `## 🎯 Top convictions multi-horizons` — à lire avant I10/I12.
- [MANQUE] Confirmation que la section "Santé des sources" expose bien le count `n_failing` dans le texte HTML (pour conditionner le repli en I6).
- [HYPOTHÈSE] La section `## Comment lire les scores` est injectée par `scoring_analyste.py` L18 (mentionné dans le brief) — à confirmer avant suppression.
- [DÉCISION THOMAS REQUISE] Ordre Synthèse vs Décision : Thomas préfère-t-il voir le panorama 12 actifs AVANT ou APRÈS la Sélection du jour ? (I13 dépend de cette réponse)

---

## Handoff structuré

---
**Handoff → @fullstack**

Fichiers produits :
- `/home/user/TradingApp/docs/ux/audit-page-s9.md` (ce fichier)

Fichiers à modifier (par @fullstack) :
- `v3/scripts/build_html.py` : I1 (L1509 JS), I2 (L880-888), I3 (L908-925), I4 (L879), I5 (L934-950), I6/I7/I8/I9 (JS post-rendu), I12 (filtre section optionnel)
- `v3/scripts/scoring_analyste.py` : I10 (renommage titre), I11 (fusion sections), I12 (suppression section), I13 (réordonnancement), I14 (déplacement sections)

Décisions prises :
- Place canonique unique de la légende = help-box (repliée)
- Header réduit à 1 ligne : titre bulletin + bandeau mode test
- legend-bar = LONG/SHORT/note + lien ❓ uniquement
- Subnav : correctif JS minimal (I1) = quick-win immédiat
- 4 vues 24h → 1 section fusionnée "Décision du jour" (P2)
- "Comment lire les scores" supprimé du markdown (doublon exact de help-box)
- 5 sections repliées : Santé sources / Intensité / News (si vide) / Flips / Détail

Points d'attention pour @fullstack :
- I1 est le quick-win le plus impactant (3 lignes JS, zéro risque)
- I11/I13/I14 (P2) modifient `scoring_analyste.py` — lire ce fichier avant d'agir
- La subnav ne doit afficher que les sections visibles (non repliées) après I6-I9
- [DÉCISION THOMAS REQUISE] avant I13 : ordre Synthèse vs Décision du jour
---
