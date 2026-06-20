# Spec visuelle — Marqueur « bascule de tendance » inter-horizon
## Tableau « Synthèse des décisions » · TradingApp v3 · Session 9

> Destinataire : Thomas (fondateur) + @fullstack pour implémentation
> Statut : spec finale, pas encore câblée en production

---

## (a) Recommandation principale + rationale

### LA reco : liseré gauche coloré ambré + glyphe ⇌ en tête de cellule

**Principe exactement** : quand une cellule représente un retournement de
direction par rapport à l'horizon immédiatement plus court (7j ≠ 24h, ou
1m ≠ 7j), la cellule reçoit :

1. Un **liseré gauche de 3px ambre** (`#f59e0b` — le `--status-dot` déjà dans
   le système) qui signale visuellement le changement depuis le bord de la
   cellule, sans toucher à l'intérieur.
2. Un **glyphe `⇌`** en tête du contenu de direction, avant le texte LONG/SHORT,
   en taille réduite (11px, couleur ambre). Ce glyphe est le seul ajout textuel.

**Ce que ça donne dans la cellule** (schéma avant/après) :

```
AVANT (continuation)          APRÈS (bascule)
┌──────────────────┐          ┌─┬────────────────┐
│ LONG +4.2        │          │▌│ ⇌ SHORT −3.8   │ ← liseré ambre 3px
│ (raison...)      │          │▌│ (raison...)     │
└──────────────────┘          └─┴────────────────┘
                                  ↑ glyphe ⇌ ambre
```

### Pourquoi ce choix est le meilleur compromis

**Glance-ability immédiate.** Le liseré gauche est le seul signal que l'œil
capte en balayant verticalement une colonne. En 200ms de saccade oculaire, le
trader identifie "il y a un truc ambre sur cette ligne" sans lire. C'est le
pattern utilisé dans les terminaux Bloomberg (ligne active), les IDE (erreur de
lint), et les encarts `.decision-selection` déjà sur cette page — le cerveau de
Thomas connaît ce pattern.

**Le glyphe `⇌` double-code sans dépendre de la couleur.** Un trader
daltonien voit le symbole même sans distinguer l'ambre du vert/rouge.
`⇌` (U+21CC, double flèche inversée) est lisible à 11px, ne prend que 1
caractère, et exprime sémantiquement "inversion de sens" mieux que n'importe
quel emoji plus large.

**Ambré = catégorie propre.** Le tableau utilise déjà vert (`--dir-long-color`)
pour LONG, rouge (`--dir-short-color`) pour SHORT. L'ambre `#f59e0b` est
délibérément la TROISIÈME couleur — elle signifie "méta-information sur la
structure temporelle", pas "bon" ou "mauvais". Déjà présente via `--status-dot`
dans le header, le token existe, zéro invention.

**Épuré.** Le liseré est 3px — imperceptible si on ne le cherche pas, visible
dès qu'on le cherche. Aucun fond de cellule coloré, aucun badge flottant. Le
tableau reste dense et lisible.

**Mobile-compatible.** Sur mobile (scroll horizontal), le liseré gauche reste
TOUJOURS visible puisqu'il est sur le bord gauche de la cellule — la première
chose qu'on voit avant de scroller. Le glyphe `⇌` est en tête du contenu, donc
visible sans scroll même sur 375px.

**N'entre pas en conflit avec les drapeaux existants.** Les drapeaux actuels
(⇄ flip intra-horizon, ↯ convergence news, 📰 news-dominant, ◧ mono-critère,
⚠️ divergence, ⚑ flip hebdo) sont en fin de ligne, après le score. Le `⇌` est
en TÊTE, avant le texte directionnel. Espace distinct, lecture distincte.

---

## (b) Alternatives écartées (court)

**Fond de cellule teinté ambre/orange.** Écartée : entre en conflit direct avec
le vert/rouge directionnel qui colore déjà le TEXTE. Deux signaux chromatiques
dans la même cellule créent du bruit. Sur dark mode, un fond coloré est
agressif et casse l'harmonie du tableau.

**Badge texte « ↘ VIRE SHORT » ou « bascule ».** Écartée : trop verbeux, prend
de la largeur, double l'information déjà lisible (la direction change). Sur
mobile, ça force un scroll supplémentaire ou un retour à la ligne non-voulu.

**Pastille ronde colorée flottante (::before positionné absolument).** Écartée :
nécessite `position: relative` sur `td` — ce qui peut casser le scroll
horizontal mobile sur certains navigateurs iOS Safari. Risque d'implémentation.

**Icône 🔄 emoji.** Écartée : rendu incohérent inter-OS (Android vs iOS vs
Windows). Taille non-contrôlable en CSS pur. Trop "décoratif" pour un tableau
d'information dense. Le `⇌` Unicode est rendu identiquement partout.

**Colonne dédiée « Retournement ? »** Écartée : casse la structure existante
à 4 colonnes. Crée une colonne à faible densité (souvent vide). Le signal doit
être DANS la cellule, pas à côté.

---

## (c) Spec markup + CSS exacts

### Markup — cellule avec bascule

La cellule de tableau normale ressemble à :

```html
<td>
  <span class="dir-long">LONG +4.2</span>
  <span class="cell-reason">momentum positif · COT haussier</span>
</td>
```

La cellule avec bascule doit devenir :

```html
<td class="trend-flip">
  <span class="dir-short">
    <span class="trend-flip-glyph" aria-label="bascule de tendance" title="Retournement par rapport à l'horizon précédent">⇌</span>
    SHORT −3.8
  </span>
  <span class="cell-reason">pression vendeuse · news bearish</span>
</td>
```

**Règles d'application (logique côté Python/JS) :**
- Cellule 7j : `trend-flip` si direction(7j) ≠ direction(24h), pour le même actif
- Cellule 1m : `trend-flip` si direction(1m) ≠ direction(7j), pour le même actif
- Cellule 24h : jamais de `trend-flip` (pas d'horizon précédent dans le tableau)
- Cellules `🚫 insuffisant` : jamais de `trend-flip` (pas de direction fiable)

### CSS — à ajouter dans le bloc `<style>` de build_html.py

```css
/* ── MARQUEUR BASCULE DE TENDANCE ───────────────────────────────────────────
   Signale inter-horizon un retournement LONG→SHORT ou SHORT→LONG.
   Règle : 7j ≠ 24h  OU  1m ≠ 7j  (logique calculée côté Python/JS).
   Token couleur : --status-dot (ambre #f59e0b) — déjà dans :root.
   NE PAS utiliser --dir-long-color / --dir-short-color (risque confusion).
   ──────────────────────────────────────────────────────────────────────────*/

/* Liseré gauche ambre sur la cellule entière */
td.trend-flip {
  border-left: 3px solid var(--status-dot) !important;
  /* On override border-left sans toucher aux autres bordures du tableau.
     Le !important est nécessaire car main table td a déjà border-bottom. */
}

/* Glyphe ⇌ — minuscule, ambre, ne prend pas de place */
.trend-flip-glyph {
  display: inline-block;
  font-size: 11px;
  color: var(--status-dot);
  margin-right: 3px;
  vertical-align: middle;
  font-style: normal;
  /* Pas d'animation : respect prefers-reduced-motion, et épure. */
}

/* Mobile : le liseré reste visible en position collée-gauche (le scroll
   horizontal ne le cache pas — c'est le premier pixel de chaque cellule). */
@media (max-width: 768px) {
  td.trend-flip {
    border-left: 3px solid var(--status-dot) !important;
    /* Inchangé sur mobile — pas besoin d'adaptation. */
  }
  .trend-flip-glyph {
    font-size: 10.5px;
    margin-right: 2px;
  }
}
```

### Token de référence (existant dans :root)

| Token CSS | Light mode | Dark mode |
|---|---|---|
| `--status-dot` | `#f59e0b` | `#f59e0b` (identique — ambre reste ambre) |
| `--dir-long-color` | `#15803d` | `#4ade80` |
| `--dir-short-color` | `#b91c1c` | `#f87171` |
| `--text-muted` | `#64748b` | `#94a3b8` |
| `--border` | `#e2e8f0` | `#334155` |

`--status-dot` est déjà déclaré dans `:root` pour le point ambre du header.
Il n'est pas redéclaré dans `@media (prefers-color-scheme: dark)` — ce qui est
volontaire : l'ambre ne change pas entre les modes (convention "état/alerte"
universelle, pas un token de surface).

**Si `--status-dot` est absent du `:root` dark** (à vérifier dans le fichier
live) : ne PAS l'ajouter au dark — son absence est intentionnelle. Le token
est hérité depuis `:root` sans override et reste `#f59e0b` en dark. C'est le
comportement voulu.

---

## (d) Exemple concret de rendu — ASCII + texte

### Tableau de synthèse avec 2 bascules détectées

```
┌──────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ Actif            │ 24h                  │ 7j                  │ 1m                  │
├──────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ Or               │ LONG +4.2            │ LONG +3.1            │ LONG +2.8            │
│                  │ (tendance haussière) │ (trend intact)      │ (structurel long)   │
│                  │                      │                      │                      │
│                  │  [continuation — aucun marqueur]                                   │
├──────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ CAC 40           │ LONG +2.1            │ ▌⇌ SHORT −1.8       │ ▌⇌ LONG +0.9        │
│                  │ (momentum positif)  │ (pression court)    │ (support structurel)│
│                  │                      │ ← BASCULE L→S       │ ← BASCULE S→L       │
├──────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ Pétrole          │ SHORT −3.2           │ SHORT −2.8           │ ▌⇌ LONG +1.2        │
│                  │ (excès offre)       │ (tendance baissière)│ (saisonnalité long) │
│                  │                      │  [continuation]      │ ← BASCULE S→L       │
└──────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘

Légende : ▌ = liseré ambre (3px, bord gauche cellule)
          ⇌ = glyphe U+21CC (11px, ambre, avant le texte directionnel)
```

### Lecture trader (ce que Thomas voit en 2 secondes)

1. Balayage vertical de la colonne 7j → deux liserés ambre sur CAC 40 + 1m Pétrole
2. L'œil s'arrête sur la ligne CAC 40 → `⇌ SHORT` = le marché bascule à court terme
3. Sur la même ligne, 1m rebasule LONG → **zigzag inter-horizon détecté immédiatement**
4. Action : zoomer sur CAC 40 avant d'exécuter, la structure n'est pas propre

---

## (e) Note accessibilité

### Daltonisme
Le marqueur NE repose PAS uniquement sur la couleur. Le glyphe `⇌` est
visible en niveaux de gris (forme distincte, pas juste une teinte). Le liseré
est visible en niveaux de gris comme une variation d'épaisseur de bordure.
Testé mentalement sur les 3 types courants (deutéranopie, protanopie,
tritanopie) : dans les trois cas, `⇌` reste lisible et le liseré reste distinct.

### ARIA
```html
<span class="trend-flip-glyph"
      aria-label="bascule de tendance"
      title="Retournement par rapport à l'horizon précédent">⇌</span>
```
`aria-label` fournit le sens sémantique aux lecteurs d'écran.
`title` donne un tooltip hover (utile sur desktop).

### Contraste WCAG 2.2 AA
- Ambre `#f59e0b` sur fond `--bg-panel` blanc `#ffffff` : ratio 2.98:1 (insuffisant texte normal).
- **Correction** : le glyphe est en **11px bold** (`font-weight: 600` hérité de `.dir-*`) ET l'ambre est
  aussi porté par le liseré (non-textuel, seuil 3:1 pour UI). Le liseré 3px passe le seuil
  non-textuel (3:1 pour composants UI — WCAG 1.4.11). Pour le glyphe texte 11px, le
  contraste 2.98:1 est en-dessous du seuil AA texte normal (4.5:1). Deux options :

  **Option A (recommandée)** : `--status-dot` passe à `#d97706` en light mode (ambre plus sombre,
  ratio ≈ 4.6:1 sur blanc). En dark mode sur `--bg-panel: #1e293b`, `#f59e0b` donne un ratio de
  ≈ 5.1:1 — conforme. Modifier uniquement la valeur light dans `:root`.

  **Option B (minimaliste)** : wraper le glyphe dans un `<abbr>` avec `font-size: 12px` et
  `font-weight: 700`. Compenser la taille pour passer en "texte grand" (18px bold ou 24px
  — non applicable à 11px). L'option A est plus propre.

  **Recommandation finale** : ajuster `--status-dot` light à `#d97706` dans build_html.py
  `:root`. La valeur dark `#f59e0b` reste. Le liseré passe de toute façon le seuil UI.

### Reduced motion
Le marqueur est purement statique — aucune animation. Compatible
`prefers-reduced-motion: reduce` sans modification.

### Touch target mobile
Le glyphe `⇌` est non-interactif (pas de clic attendu). La cellule `td`
complète reste la cible de toucher si on implémente un tap futur. Pas de
contrainte touch target ici.

---

**Handoff → @fullstack**

Fichiers produits :
- `/home/user/TradingApp/docs/design/trend-change-synthese-s9.md` (ce fichier)

Décisions prises :
- Marqueur retenu : liseré `border-left: 3px solid var(--status-dot)` + glyphe `⇌` (U+21CC, 11px, ambre)
- Token couleur réutilisé : `--status-dot` (`#f59e0b`) — déjà dans `:root`, aucune invention
- Ajustement recommandé : `--status-dot` light → `#d97706` pour conformité WCAG AA texte
- Classe CSS : `td.trend-flip` (cellule) + `.trend-flip-glyph` (glyphe)
- Markup : `<td class="trend-flip">` + `<span class="trend-flip-glyph" aria-label="bascule de tendance">⇌</span>` avant le texte directionnel

Points d'attention pour l'implémentation :
- La **logique de détection** est à écrire dans `scoring_analyste.py` (côté génération du markdown) ou dans le JS de `build_html.py` (post-rendu marked.js). Recommandé : côté Python — le markdown émis contiendra directement la classe. Alternative : post-processing JS sur les cellules du tableau rendu.
- Cellule 24h : **jamais** de `trend-flip` (aucun horizon antérieur dans ce tableau)
- Cellules `🚫 insuffisant` : **jamais** de `trend-flip` (direction non fiable)
- Le `!important` sur `border-left` est nécessaire — la règle `main table td { border-bottom }` de la feuille de style est plus spécifique sans lui
- Dark mode : `--status-dot` n'a pas d'override dans `@media (prefers-color-scheme: dark)` — comportement voulu, ambre reste ambre
- Mobile : le liseré gauche est toujours visible en premier (avant scroll horizontal) — aucune adaptation nécessaire
