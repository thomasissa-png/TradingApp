# Logo mark Today Trade (S10)

> Livrable @design, 26/06/2026.
> Destinataire : @fullstack -- remplacer `.brand-mark` header, `.fb-mark` footer, et favicon SVG.

---

## 1. Concept retenu : "Ligne de conviction"

**Piste** : courbe de tendance ascendante en deux segments brisés, terminée par un point de conviction.

**Rationale** : trois points reliés par deux traits forment une ligne cassée qui monte -- c'est le geste graphique universel du "marché en tendance haussière", sans la lourdeur d'une flèche ni le cliché du chandelier japonais. Le point terminal (cercle plein) dit "voici le sens actuel" : c'est la "lecture" du marché, pas juste sa direction. A 28px comme à 16px, la forme reste lue en un geste. Sobre, technique, mémorisable.

Le segment bas-gauche est posé sur un axe horizontal implicite (fond du viewBox) : on lit inconsciemment un graphe de cours. Le segment terminal monte à ~40 deg, conveying momentum sans agressivité.

---

## 2. SVG inline -- mark monochrome (currentColor)

Coller tel quel dans le HTML. `currentColor` hérite de la couleur du parent (bleu #2563eb en header clair, #60a5fa en dark mode). Pas de couleur codée en dur.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" fill="none" aria-hidden="true">
  <!-- Axe de sol : trait bas suggerant un repere graphique -->
  <line x1="4" y1="26" x2="28" y2="26"
        stroke="currentColor" stroke-width="1.5"
        stroke-linecap="round" opacity="0.28"/>
  <!-- Ligne de tendance : 3 points, 2 segments ascendants -->
  <polyline points="5,24 13,17 21,11"
            stroke="currentColor" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"
            fill="none"/>
  <!-- Segment terminal : dernier elan, angle plus marque -->
  <line x1="21" y1="11" x2="27" y2="7"
        stroke="currentColor" stroke-width="2.4"
        stroke-linecap="round"/>
  <!-- Point de conviction : cap de la tendance -->
  <circle cx="27" cy="7" r="2.8"
          fill="currentColor"/>
</svg>
```

**Usage header** : remplacer le contenu de `.brand-mark` par ce SVG. Conserver le `border-radius: 8px` et `border: 1.5px solid var(--brand-gold)` autour du conteneur si vous souhaitez garder le cadre (voir section 4).

---

## 3. Variante favicon (fond bleu + mark blanc)

Fond carré arrondi bleu #2563eb, mark en blanc opaque. Copiable comme `favicon.svg` dans `public/`.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <!-- Fond bleu arrondi -->
  <rect width="32" height="32" rx="7" fill="#2563eb"/>
  <!-- Axe de sol blanc tenu -->
  <line x1="4" y1="26" x2="28" y2="26"
        stroke="white" stroke-width="1.4"
        stroke-linecap="round" opacity="0.35"/>
  <!-- Ligne de tendance blanche -->
  <polyline points="5,24 13,17 21,11"
            stroke="white" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"
            fill="none"/>
  <!-- Segment terminal -->
  <line x1="21" y1="11" x2="27" y2="7"
        stroke="white" stroke-width="2.4"
        stroke-linecap="round"/>
  <!-- Point de conviction -->
  <circle cx="27" cy="7" r="2.8"
          fill="white"/>
</svg>
```

Pour `favicon.ico` et les PNG derivés (16x16, 32x32, 180x180 apple-touch) : générer depuis ce SVG via un outil comme `sharp` ou `realfavicongenerator.net`. La forme reste nette à 16x16 car elle n'a que 3 points et 2 traits.

**`<meta name="theme-color" content="#2563eb">`** -- à conserver dans `<head>`.

---

## 4. Reco : garder ou retirer le cadre arrondi

**Retirer le cadre** (`border: 1.5px solid var(--brand-gold)` + `background: transparent`).

Pourquoi : le nouveau mark se suffit à lui-même -- la ligne de tendance a déjà une base (l'axe de sol) qui lui donne son assise visuelle. Le carré bordé doré était une béquille pour le glyphe `▲` qui n'avait pas de structure propre. Sans cadre, le mark respire mieux sur le fond `--brand-primary` (#1a2e4a), et le groupe `brand-mark + ISSA CAPITAL` est plus aéré.

**Taille de trait recommandée** : `stroke-width: 2.4` dans le SVG pour le rendu à 32px. Si le conteneur `.brand-mark` est réduit à 28px (mobile), le SVG scale bien -- pas de retouche nécessaire. En dessous de 24px, monter à `stroke-width: 2.6` ou utiliser la variante favicon (fond plein, moins de détail).

CSS à modifier dans `.brand-mark` :

```css
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px;
  /* Retirer : border, background, border-radius, font-size, font-weight, line-height */
  color: var(--brand-gold); /* ou var(--brand-accent) selon le choix de couleur du mark */
}
```

Si Thomas préfère garder le cadre pour la reconnaissance de "boite", conserver le `border-radius: 8px` et `border: 1.5px solid rgba(255,255,255,0.2)` (plus subtil que le doré) -- le mark blanc sur fond transparent fonctionne aussi bien.

---

## 5. Alternatives en reserve

### Alternative A : "Chevron double" -- direction sans ambiguité

Deux chevrons imbriqués, ouverts vers la droite et vers le haut. Plus iconique, moins "graphe financier", davantage "cap/direction".

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" fill="none" aria-hidden="true">
  <!-- Chevron exterieur -->
  <polyline points="8,24 16,16 8,8"
            stroke="currentColor" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"/>
  <!-- Chevron interieur, decale -->
  <polyline points="16,24 24,16 16,8"
            stroke="currentColor" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

Usage : si le concept "sens/direction" prime sur "marché/graphe". Risque : ressemble a un "suivant" de lecteur media.

### Alternative B : "T-tendance" -- initiale integree

La lettre T stylisee dont la jambe verticale est remplacee par une ligne ascendante. Relie le nom Today Trade au concept marché.

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32" fill="none" aria-hidden="true">
  <!-- Barre horizontale du T -->
  <line x1="6" y1="10" x2="26" y2="10"
        stroke="currentColor" stroke-width="2.4"
        stroke-linecap="round"/>
  <!-- Jambe ascendante : part du centre-bas et monte vers le point terminal -->
  <line x1="16" y1="10" x2="16" y2="23"
        stroke="currentColor" stroke-width="2.4"
        stroke-linecap="round" opacity="0.3"/>
  <!-- Ligne de tendance depuis la base de la jambe -->
  <polyline points="10,23 16,17 22,13 27,9"
            stroke="currentColor" stroke-width="2.4"
            stroke-linecap="round" stroke-linejoin="round"
            fill="none"/>
  <circle cx="27" cy="9" r="2.6" fill="currentColor"/>
</svg>
```

Usage : si l'ancrage au nom "Today Trade" est strategique (branding plus literal). Plus complexe a lire a 16px.

---

**Handoff -> @fullstack**

Fichiers produits :
- `/home/user/TradingApp/v3/docs/design/logo-today-trade-s10.md`

Actions a implementer dans `v3/scripts/build_html.py` :
1. Remplacer le contenu `▲` de `.brand-mark` par le SVG de la section 2.
2. Faire de meme pour `.fb-mark` dans le footer.
3. Remplacer le favicon SVG existant par la variante section 3.
4. Retirer `border: 1.5px solid var(--brand-gold)` et `font-size`/`font-weight`/`line-height` du CSS `.brand-mark` (la forme SVG se suffit).
5. Conserver `color: var(--brand-gold)` sur `.brand-mark` pour que `currentColor` herite la teinte dorée.

Points d'attention :
- Le SVG utilise `aria-hidden="true"` -- le nom de marque textuel `ISSA CAPITAL` adjacant porte l'accessibilité.
- Le favicon variante (section 3) : generer les PNG derives (16/32/180/192/512px) depuis le SVG avant deploy.
- Tester le rendu a 28px (mobile header) : la forme reste lisible sans retouche.
