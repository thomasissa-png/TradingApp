# Audit design — Page de lecture des bulletins

> Audit de forme uniquement (CSS + structure HTML + markdown rendu).
> Source auditée : `v3/scripts/build_html.py` (template complet) + `v3/data/bulletins/bulletin-2026-06-02.md` (bulletin 18h04).
> Aucune modification apportée au code.
> Date de l'audit : 2026-06-02.

---

## Note globale : **6,5 / 10**

| Dimension | Note | Commentaire court |
|---|---|---|
| Hiérarchie visuelle | 5/10 | L'essentiel (Synthèse) est noyé au milieu — 3 sections secondaires avant |
| Lisibilité des tableaux | 6/10 | Scroll horizontal fonctionnel, mais 10 colonnes + emojis = illisible sur mobile |
| Couleurs et sémantique | 6/10 | LONG/SHORT colorisés en vert/rouge dans les td — mais la Synthèse souffre du bug \b/emoji |
| Navigation | 8/10 | Sidebar + subnav sticky + hamburger mobile : point fort solide |
| Mobile | 5/10 | Layout globalement fonctionnel, mais tableaux à 10 colonnes et bug sticky th |
| Dark mode | 0/10 | Absent — critique pour le bulletin du soir (18h) |

---

## Ce qui est déjà bien (ne pas casser)

**La navigation est le point fort de la page.** La sidebar liste les bulletins avec date + créneau (matin/midi/soir), badge "dernier" vert pour le plus récent, état actif avec bordure accent bleue. La subnav sticky par section (Briefing / Matrice / Détail…) permet de sauter directement à n'importe quelle section. Thomas peut comparer deux bulletins en deux clics. C'est fonctionnel et bien pensé.

**La colorisation LONG/SHORT dans les tableaux** via `.dir-long` (vert #15803d) et `.dir-short` (rouge #b91c1c) est un vrai gain. La fonction `colorizeDirections()` applique aussi la couleur aux scores signés (+/-) dans les `<td>`. Le contraste est conforme : vert sur fond blanc = 5.1:1, rouge = 5.9:1 (WCAG AA validé).

**Le scroll horizontal des tableaux** via `.table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch }` est la bonne approche — évite l'écrasement et fonctionne sur iOS.

**L'encart "Comment lire les scores"** en `<details>` replié par défaut est une bonne décision : disponible mais non intrusif.

**Le fallback offline** (affichage brut markdown si `marked.js` ne charge pas) protège la lecture en `file://` hors réseau — utile et souvent oublié.

**La légende compacte dans la barre sticky** (LONG = hausse, SHORT = baisse, |score| = force) est un bon résumé permanent. La barre `legend-bar` + `subnav` occupent ~80px en haut de l'écran — acceptable.

---

## Top 8 points d'amélioration (priorisés impact / effort)

---

### 1. Pas de dark mode — critique pour le bulletin du soir (impact : FORT / effort : FAIBLE)

**Problème.** Le bulletin de 18h est lu en soirée sur fond blanc `#f8fafc`. Aucune variable dark n'est définie. Pour un trader qui consulte sur plusieurs écrans en fin de journée, un fond blanc dans un environnement sombre = fatigue oculaire = lecture moins attentive = risque de décision.

**Pourquoi c'est simple à corriger.** Le système de variables CSS (`--bg`, `--bg-panel`, `--text`, `--accent`, etc.) est déjà en place — c'est exactement le bon pattern. Il suffit d'ajouter un bloc `@media (prefers-color-scheme: dark)` dans le `<style>` du template Python.

**Piste concrète — valeurs à injecter dans `render_html()` :**

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a;
    --bg-panel: #1e293b;
    --border: #334155;
    --border-strong: #475569;
    --text: #f1f5f9;
    --text-muted: #94a3b8;
    --accent: #60a5fa;
    --accent-bg: #1e3a5f;
    --code-bg: #1e293b;
    --row-alt: #0f172a;
    --badge-bg: #15803d;
  }
}
```

Coût : ~15 lignes dans `build_html.py`, zéro changement de logique. Le dark mode se déclenche automatiquement selon le réglage système de Thomas.

---

### 2. La Synthèse arrive trop tard — l'essentiel est noyé sous 3 sections secondaires (impact : FORT / effort : FAIBLE)

**Problème.** Ordre actuel dans le bulletin 18h04 :
1. Briefing du jour (long — 30+ lignes de news par actif)
2. Bilan des news (secondaire)
3. Santé des sources (monitoring)
4. **Synthèse des décisions** ← la décision arrive en 4e position

Thomas doit scroller plusieurs écrans avant de voir "Or SHORT / Pétrole LONG / Nasdaq SHORT". Le matin à 7h, il veut cette information en 5 secondes.

**Ce qui est bien :** la subnav propose déjà un lien "Synthèse" — mais il est au milieu de la rangée de liens, pas mis en avant.

**Option A (pipeline, effort faible, impact fort)** : dans `run_bulletin.py`, émettre la section Synthèse en premier dans le markdown, avant le Briefing. Le Briefing est du contexte, la Synthèse est la décision. Rien dans la logique actuelle n'impose l'ordre actuel.

**Option B (CSS/JS, zéro pipeline)** : dans `selectBulletin()`, après le rendu marked, trouver le `<h2>` "Synthèse des décisions" et le `<table>` qui suit, et les déplacer DOM avant le premier `<h2>`. ~10 lignes JS. Plus fragile (dépend du texte exact du h2), mais zéro changement pipeline.

---

### 3. Bug probable de colorisation LONG/SHORT dans la table Synthèse (impact : FORT / effort : TRÈS FAIBLE)

**Problème.** La fonction `colorizeDirections()` utilise le regex `\bLONG\b` et `\bSHORT\b`. Dans la table Synthèse, les cellules contiennent du texte composite comme `SHORT ○ 📰` ou `LONG ●`. Les emojis ○ ● 📰 sont des caractères Unicode — en JavaScript, `\b` (word boundary) est défini pour `[a-zA-Z0-9_]` uniquement. Un emoji directement adjacent à "LONG" ou "SHORT" sans espace ne pose pas de problème car il y a un espace avant l'emoji. Mais la présence de `🚫` en début de cellule (pour les actifs insuffisants) casse potentiellement le parsing.

**À vérifier en pratique :** ouvrir `index.html` dans un navigateur, inspecter une cellule de la Synthèse contenant "SHORT ○" et vérifier si le texte "SHORT" est enveloppé dans un `<span class="dir-short">`.

**Fix probable (2 lignes JS)** : remplacer le regex `\bSHORT\b` par `(?<![a-zA-Z])SHORT(?![a-zA-Z])` pour une boundary plus robuste aux emojis et caractères spéciaux.

---

### 4. Bug CSS : `position: sticky` des `<th>` cassé dans un container `overflow-x: auto` (impact : MOYEN / effort : TRÈS FAIBLE)

**Problème.** Le CSS définit `main table th { position: sticky; top: 0; }` pour que les en-têtes des tableaux restent visibles au scroll vertical. Or les tableaux sont enveloppés dans `.table-wrap { overflow-x: auto }`. C'est un bug CSS documenté : `position: sticky` dans un container `overflow: auto` ne fonctionne pas — le sticky s'ancre au container, pas à la fenêtre. Les en-têtes ne sont donc pas vraiment stickies lors du scroll vertical.

**Conséquence visible.** Quand Thomas scrolle verticalement dans un long tableau Détail (12 actifs × 10 colonnes), les en-têtes de colonnes disparaissent. Il ne sait plus à quelle colonne correspond le chiffre qu'il lit.

**Fix.** Supprimer `position: sticky; top: 0;` des `th` (ça ne marche pas dans ce contexte de toute façon). Si on veut vraiment les sticky headers, il faut restructurer : mettre le scroll vertical sur un élément interne du `.table-wrap` et le scroll horizontal sur un conteneur externe — architecturalement plus complexe. Pour l'instant, supprimer la déclaration qui crée une fausse attente est le minimum.

---

### 5. Tableaux à 10 colonnes illisibles sur mobile — masquer la colonne Note (impact : MOYEN / effort : TRÈS FAIBLE)

**Problème.** Les tableaux "Détail par actif" ont 10 colonnes : Critère / Type / Valeur brute / Norm. / Poids / Signe / 24h / 7j / 1m / Note. Sur un écran 375px, le scroll horizontal couvre 3× la largeur d'écran. La colonne "Note" (10e colonne) affiche quasi-systématiquement `zscore (pré-calculé)` — c'est de l'information technique de débogage, pas de l'information décisionnelle.

**Fix — 3 lignes CSS dans le template :**

```css
@media (max-width: 768px) {
  /* Colonne Note (10e) — info technique, supprimée sur mobile */
  main table td:nth-child(10),
  main table th:nth-child(10) { display: none; }
  /* Colonne Valeur brute (3e) — 15 décimales inutiles sur mobile */
  main table td:nth-child(3),
  main table th:nth-child(3) { display: none; }
}
```

En masquant ces 2 colonnes, Thomas voit directement Critère / Type / Norm. / Poids / Signe / 24h / 7j / 1m en scrollant moins. Les colonnes décisionnelles (24h/7j/1m) passent dans le champ de vision.

---

### 6. "Cellules à surveiller" trop longue — 25 lignes de monitoring entre la Synthèse et les Flips (impact : MOYEN / effort : FAIBLE)

**Problème.** Dans le bulletin 18h04, la section "⚠️ Cellules à surveiller" liste 25 entrées avec leurs flags (`[🚫 ↯ ⌛]`). C'est du monitoring système, pas une décision. Elle sépare visuellement la Synthèse des Flips, qui sont pourtant les deux informations décisionnelles les plus importantes après la Synthèse.

**Piste concrète (JS, ~12 lignes).** Dans `selectBulletin()`, après le rendu marked, cibler le `<h2>` dont le texte contient "Cellules à surveiller", créer un `<details><summary>` autour du bloc qui suit, et le refermer par défaut. Le contenu reste accessible en un clic mais ne pollue pas la lecture rapide.

---

### 7. Soupe de symboles dans la Matrice — ajouter des tooltips natifs (impact : MOYEN / effort : FAIBLE)

**Problème.** Une cellule Matrice peut contenir `SHORT (-0.31) ⚑ 📰 ↯ ⇄` — 4 symboles collés. La légende est en bas du tableau (ou dans la barre sticky en haut — mais en version compacte). Au milieu de la lecture d'une cellule, l'utilisateur ne va pas scroller pour déchiffrer le 4e symbole.

**Piste concrète (JS, ~15 lignes).** Ajouter dans `colorizeDirections()` (ou une fonction séparée) un post-traitement qui enveloppe chaque symbole dans un `<span title="description">` :

```js
const SYMBOL_TOOLTIPS = {
  '↯': 'Divergence quant ↔ news (signes opposés)',
  '⇄': 'Contre-momentum (conclusion vs RSI opposés)',
  '⌛': 'Données périmées (stale)',
  '⊘': 'News démentie ou déjà cotée',
  '⚑': 'Gate régime extrême actif',
  '📰': 'News > 50% du score — pondéré en tête',
  '⚪': 'Quasi coin-flip (|score| < 0.05) — non-actionnable',
  '⚠️': 'Divergence primaire/pondéré ou confiance faible',
};
```

Tooltip natif au survol — zéro CSS supplémentaire, zéro espace visuel consommé. Sur mobile, le tap long affiche parfois le title selon le navigateur.

---

### 8. Section "Limites du jour" — redondante avec les tableaux Détail (impact : FAIBLE / effort : FAIBLE)

**Problème.** La section "Limites du jour" (en bas du bulletin, ~45 lignes) liste tous les critères `n/a` actif par actif. Ces informations sont déjà présentes dans les tableaux Détail, colonne "Note" = `n/a (valeur absente)`. La redondance allonge le bulletin sans ajouter de valeur.

**Piste concrète.** Dans le pipeline (`run_bulletin.py`), filtrer les Limites pour n'afficher que les critères avec un poids ≥ 8 (les vraiment importants qui manquent). Sur le bulletin 18h04, cela réduirait de ~45 à ~10 lignes les critères vraiment structurants (Caixin PMI poids 12, différentiel taux 2Y poids 12, DXY poids 8-9, etc.).

---

## Note sur le "Top 3 convictions"

La mission d'audit mentionne une section "🎯 Top 3 convictions" qui devrait apparaître en tête du bulletin. **Cette section est absente du bulletin 2026-06-02.** Le bulletin s'ouvre directement sur le Briefing. Si cette section est prévue dans le pipeline mais pas encore générée, c'est le changement structurel à fort impact le plus simple à implémenter : afficher les 3 actifs avec le |score| le plus élevé et une direction claire, en 3 lignes au-dessus de tout le reste. Pour Thomas, ce serait la réponse à "que faire ce matin ?" en moins de 3 secondes.

---

## Bilan visuel — ordre actuel vs ordre idéal

```
Ordre actuel (bulletin 18h04) :
  [header] Header sticky + légende symboles        OK
  [sticky] Barre LONG/SHORT + subnav               OK
  [replié] "Comment lire les scores"               OK
  [1] Briefing du jour (30+ lignes de news)        CONTEXTE — ne devrait pas être en 1er
  [2] Bilan des news (5 calls mesurés)             SECONDAIRE
  [3] Santé des sources (monitoring flux)          MONITORING
  [4] Synthèse des décisions ★                    DÉCISION — arrive trop tard
  [5] Cellules à surveiller (25 lignes de flags)   MONITORING DENSE
  [6] Flips vs veille                              UTILE
  [7] Matrice (tableau colorisé, 8 actifs)         UTILE
  [8] Détail par actif (10 col × 12 actifs)        RÉFÉRENCE
  [9] Limites du jour (~45 lignes de n/a)          REDONDANT

Ordre idéal pour un trader qui lit 3×/jour :
  [header] Header sticky + légende
  [sticky] Barre LONG/SHORT + subnav
  [0] 🎯 Top 3 convictions (si implémenté)
  [1] Synthèse des décisions (vue d'oiseau 12×3)
  [2] Flips vs veille (ce qui a changé)
  [3] Matrice (chiffres détaillés)
  [4] Briefing + Bilan news
  [5] Santé des sources
  [6] Détail par actif (tableaux)
  [7] Cellules à surveiller (replié)
  [8] Limites du jour filtrées (poids ≥ 8, replié)
```

---

## Résumé des actions, par ordre valeur / effort

| # | Action | Fichier à modifier | Effort | Impact |
|---|---|---|---|---|
| 1 | Dark mode (`@media prefers-color-scheme: dark`) | `build_html.py` — CSS | ~15 lignes | Fort |
| 2 | Remonter la Synthèse en premier dans le markdown | `run_bulletin.py` | Ordre sections | Fort |
| 3 | Vérifier/corriger regex colorisation dans Synthèse | `build_html.py` — JS | 2-3 lignes | Fort |
| 4 | Supprimer `position: sticky` sur `th` (bug CSS) | `build_html.py` — CSS | 2 lignes | Moyen |
| 5 | Masquer colonnes Note + Valeur brute sur mobile | `build_html.py` — CSS | 6 lignes | Moyen |
| 6 | Replier "Cellules à surveiller" en `<details>` | `build_html.py` — JS | ~12 lignes | Moyen |
| 7 | Tooltips sur les symboles (↯ ⇄ ⌛ ⊘ ⚑ 📰 ⚪ ⚠️) | `build_html.py` — JS | ~15 lignes | Moyen |
| 8 | Filtrer "Limites du jour" (poids ≥ 8 uniquement) | `run_bulletin.py` | Filtrage | Faible |
| 9 | Implémenter "🎯 Top 3 convictions" en tête | `run_bulletin.py` | Logique score | Fort (futur) |
