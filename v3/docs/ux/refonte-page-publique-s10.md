# Refonte page publique — Spec UX S10

> Auteur : @ux · Date : 2026-06-25
> Cible : le primo-visiteur NON-TRADER (pas Thomas).
> Objectif : en 10 secondes, il comprend ce que c'est, pour qui, si ça marche.
> Contraintes non-négociables : WIN RATE ONLY (jamais €/P&L), statut "en validation" visible,
> zéro tiret cadratin, page épurée.

---

## 1. Parcours de lecture du primo-visiteur

### Principe directeur

Un primo-visiteur non-trader arrive sur la page sans contexte.
Sa question inconsciente suit une séquence invariable :

1. **C'est quoi ?** (3 secondes, zone above the fold)
2. **Pour qui / ça me concerne ?** (5-8 secondes, hero ou intro juste dessous)
3. **Est-ce que ça marche ?** (8-15 secondes, preuve immédiate)
4. **Comment ça fonctionne ?** (15-30 secondes, optionnel, pour les curieux)

La page actuelle commence directement à l'étape 4. Il n'y a pas de réponse aux étapes 1, 2, 3.

### Ordre de lecture cible (vertical, top-to-bottom)

```
ZONE A — Header repensé (always visible, sticky)
  Identité produit · Proposition de valeur courte · Statut "en validation"

ZONE B — Hero / intro d'accueil (above the fold, first screen)
  Ce que c'est · Pour qui · Ce qu'on ne fait PAS (clarté sur les limites)

ZONE C — Preuve : win rate (second screen, ou fin du hero sur mobile)
  La seule métrique qui compte · N actifs suivis · Statut chauffe honnête

ZONE D — Navigation principale (sidebar repensée)
  Libellés humains · Regroupement logique pour newcomer ET utilisateur régulier

ZONE E — Contenu existant (bulletins, performance, bilan, variations)
  INCHANGÉ structurellement · Accessible via nav

ZONE F — Footer
  Qui/quoi · Disclaimer · Statut mode test · Année
```

### Points de friction actuels sur le parcours primo-visiteur

- [FRICTION H2] : "TradingApp v3 · Bulletins" ne dit rien à quelqu'un qui ne connaît pas.
  Le mot "Bulletins" est du jargon interne. Solution : remplacer par une tagline.
- [FRICTION H8] : Le hero n'existe pas. Le contenu commence directement par le bulletin du jour.
  Un primo-visiteur ne sait pas ce qu'il regarde. Solution : ajouter une intro d'accueil.
- [FRICTION H2] : "Sauter à :" est du jargon de développeur. Solution : libellé humain ou supprimer.
- [FRICTION H1] : Pas de footer, pas d'ancrage de confiance en bas de page.
  Solution : footer minimal avec disclaimer.
- [FRICTION H6] : La sidebar liste des vues (Aujourd'hui / Bilan semaine / Performance / Variations 24h)
  sans aucune explication de ce que contient chaque vue pour un newcomer.

---

## 2. Spec du HERO / intro d'accueil

### Objectif du hero

Répondre aux questions 1 et 2 du primo-visiteur en moins de 8 secondes.
NE PAS rédiger le copy ici (mission @copywriter). Définir la structure et l'intention de chaque bloc.

### Structure du hero (5 blocs, dans l'ordre)

**Bloc H1 — Accroche principale (1 ligne, grande typographie)**
- Intention : dire CE QUE C'EST en une formule. Pas le nom du produit, la VALEUR.
- Contenu type attendu du copywriter : "Savoir dans quelle direction jouer chaque marché."
  (formule directionnelle, terrain commun trader et non-trader)
- Taille : titre H1, très visible, max 8-10 mots.
- Position : première chose lue après le header.

**Bloc H2 — Sous-titre explicatif (2 lignes max)**
- Intention : préciser le COMMENT sans jargon. 12 actifs, 3 horizons (24h/7j/1m), direction LONG ou SHORT.
  Le trader humain décide et exécute, le système analyse.
- Contenu type : "Chaque matin, un bulletin dit si l'or, le pétrole, le CAC40... sont haussiers ou baissiers.
  Sur 24 heures, 7 jours, ou 1 mois."
- Pas de chiffres techniques (pas de z-score, pas de score).

**Bloc H3 — Statut "en validation" (badge ou encart sobre)**
- Intention : être HONNETE sur le statut en cours. C'est un GARDE-FOU, pas une honte.
  Présenté comme signe de rigueur, pas comme avertissement négatif.
- Structure : badge sobre (1 ligne) + phrase de contexte (1-2 lignes max).
- Contenu type : "En validation · Go-live prévu le 08/08/2026.
  Le système tourne en conditions réelles depuis [date]. On mesure avant d'ouvrir."
- Style : sobre, pas d'alerte rouge. Couleur neutre ou ambre doux.
- Position : juste sous le sous-titre, ou en fin de hero.

**Bloc H4 — Ce qu'on ne fait PAS (2-3 lignes, petite typo)**
- Intention : couper les malentendus AVANT qu'ils arrivent. Un non-trader peut croire à un robot
  qui place des ordres, ou à des promesses de gains.
- Contenu type : "Le système ne place aucun ordre. Il ne promet aucun gain.
  Il donne une direction, pas un résultat."
- Style : discret, police réduite, pas de rouge alarmiste.

**Bloc H5 — Invitation à entrer (CTA implicite ou explicite)**
- Intention : inviter à voir la performance ou le bulletin du jour.
- Sur desktop : la sidebar est déjà visible, le CTA peut être textuel ("Voir les résultats").
- Sur mobile : bouton ou lien ancre vers la vue Performance.
- NE PAS mettre de CTA d'inscription (pas de compte utilisateur dans ce produit).

### Pattern de layout du hero

- **Pattern** : stack vertical centré, full-width, fond légèrement distinct du reste de la page
  (pas de section de couleur criarde, cohérence avec le dark mode existant).
- **Desktop** : largeur max ~700px centré dans la zone main (sidebar visible à gauche).
- **Mobile** : 100% width, padding horizontal 16px, blocs empilés dans l'ordre H1-H2-H3-H4-H5.
- **Responsive** : H3 (statut) reste visible sur mobile, ne pas masquer.

---

## 3. Refonte du MENU

### Problèmes du menu actuel

**Sidebar actuelle :**
```
📅 Aujourd'hui
🗓️ Bilan semaine
📊 Performance
📈 Variations 24h
--- Bulletins ---
[liste des bulletins]
```

**Subnav actuelle :**
```
Sauter à : [liens vers les sections du bulletin]
```

**Problèmes identifiés :**
1. "Variations 24h" : le newcomer ne sait pas ce que c'est (différent du "bilan semaine" comment ?).
2. "Sauter à :" : jargon technique. Devrait être invisible ou reformulé.
3. Les libellés avec emoji fonctionnent, mais l'ordre priorise le quotidien de Thomas,
   pas le parcours du primo-visiteur (qui voudrait voir la Performance en premier).
4. Aucune intro visible pour chaque vue depuis la sidebar.

### Proposition de restructuration de la sidebar

**Groupe 1 : "Résultats" (primo-visiteur : est-ce que ça marche ?)**
```
Résultats · Win rate     [vue Performance actuelle — L1121]
Historique complet       [sous-section de Performance, décision par décision]
```

**Groupe 2 : "Bulletins" (utilisateur régulier : que dit le système aujourd'hui ?)**
```
Bulletin du jour         [vue Aujourd'hui actuelle — L1109]
Bilan de la semaine      [vue Bilan semaine actuelle — L1115]
```

**Groupe 3 : "Marchés" (pour les curieux)**
```
Mouvements de marché     [vue Variations 24h actuelle — L1164]
```

**Section repliable :**
```
Archives (bulletins passés)  [liste des bulletins existante — L1072]
```

**Règle de libellé :**
- Libellés sans jargon, sans abréviation.
- "Performance" reste comme libellé secondaire (entre parenthèses ou sous-libellé) pour que Thomas
  retrouve ses repères.
- Emojis : conserver si déjà en place (cohérence), mais non obligatoires.

### Refonte de la subnav "Sauter à :"

**Option recommandée : supprimer le libellé "Sauter à :" et ne conserver que les liens**

Rationale : le libellé est du jargon de site web des années 2000. Les liens seuls suffisent.
La barre de navigation rapide reste utile pour naviguer dans un bulletin long, mais sans ce label.

**Structure cible :**
```html
<nav class="subnav" aria-label="Navigation dans le bulletin">
  <div class="subnav-inner">
    <!-- juste les liens, pas de label "Sauter à :" -->
    <span id="subnav-links"></span>
  </div>
</nav>
```

**Alternative si Thomas préfère garder un label :** "Dans ce bulletin :" (plus naturel).

### Libellés à garder compatibles avec les vues existantes

| ID HTML actuel | Libellé actuel sidebar | Libellé proposé | Vue ciblée |
|---|---|---|---|
| `#vue=performance` | 📊 Performance | Résultats · Win rate | `#history-view` (L1121) |
| `#vue=aujourdhui` | 📅 Aujourd'hui | Bulletin du jour | `#today-view` (L1109) |
| `#vue=semaine` | 🗓️ Bilan semaine | Bilan de la semaine | `#week-view` (L1115) |
| `#vue=variations` | 📈 Variations 24h | Mouvements de marché | `#variations-view` (L1164) |

Les ancres `#vue=...` NE DOIVENT PAS changer (routing JS interne, compatibilité bookmarks).
Seuls les libellés texte dans `<a>` changent.

---

## 4. Spec du FOOTER

### Rationale

Pas de footer = pas d'ancrage de confiance. Pour un primo-visiteur qui reçoit un lien partagé,
l'absence de footer renforce l'impression de "page technique inachevée".
Le footer remplit 3 fonctions : identité, disclaimer légal, honnêteté sur le statut.

### Structure du footer (3 colonnes desktop, stack mobile)

**Colonne 1 — Identité**
- Nom du système (TradingApp v3 ou le nom public si différent)
- Tagline courte (1 ligne, à définir par @copywriter)
- Exemple : "Analyse directionnelle sur 12 actifs · 3× par jour"

**Colonne 2 — Statut et contexte**
- "En validation depuis [mois/an] · Go-live cible 08/08/2026"
- "Le système ne place aucun ordre. L'exécution reste humaine."
- "Win rate = seule métrique suivie (taux de bonnes directions)."

**Colonne 3 — Disclaimer**
- "Cette page est à usage privé et informatif."
- "Les bulletins ne constituent pas un conseil en investissement."
- "Les performances passées ne préjugent pas des performances futures."
- Année de copyright (2026).

### Pattern de layout du footer

- **Pattern** : grille 3 colonnes sur desktop, stack vertical sur mobile (ordre : Identité → Statut → Disclaimer).
- **Responsive** : sur mobile (<768px), les 3 colonnes s'empilent. Identité en premier (ancrage visuel),
  Disclaimer en dernier.
- **Style** : fond légèrement plus sombre que le body (cohérence dark mode), police réduite (0.85rem),
  pas de couleur alarmiste sur le disclaimer.
- **Séparation** : ligne de bordure fine au-dessus du footer (border-top).
- **Position** : après le `</div class="layout">` (L1175 dans build_html.py), avant `</body>`.

### Ce que le footer NE doit PAS contenir

- Aucun montant, pourcentage de gain, P&L.
- Aucun lien vers des réseaux sociaux (pas de présence publique actuellement).
- Aucun formulaire de contact ou d'inscription (usage privé).

---

## 5. Instructions @fullstack — Liste P0/P1/P2

### Ce qui NE DOIT PAS bouger

- Les parsers markdown (rendering des bulletins, Bilan semaine, etc.)
- Les vues existantes et leur contenu : `#today-view` (L1109), `#week-view` (L1115),
  `#history-view` (L1121), `#variations-view` (L1164)
- Les fonctions JS : `colorizeDirections`, routing `#vue=...`, filtrages historique
- Les ancres `href="#vue=..."` dans la sidebar (bookmarks et routing JS)
- Les blocs de données JS : `BULLETINS`, `REPORTS`, `WEEKLY`, `WEEKLIES`, `MEASURES`, `PERF_AB`,
  `WINRATE_MD`, `VARIATIONS_MD` (L1177-1184)
- La `help-box` `<details>` (L1082) : conserver telle quelle, emplacement inchangé
- Les 1474+ tests existants : zéro régression attendue (les modifications sont HTML/CSS only)

---

### P0 — Modifications critiques (sans elles, la page reste incompréhensible)

**P0-1 : Ajouter le hero/intro dans `<div id="bulletin-content">` ou avant**

Actuellement : `<div id="bulletin-content"><p>Chargement...</p></div>` (L1106).
Le hero doit s'afficher AVANT le chargement du bulletin (pas dedans, pour ne pas être écrasé).

Insertion : après `</details>` (fermeture help-box, L1105), avant `<div id="bulletin-content">` (L1106).

```html
<!-- HERO — visible uniquement sur la vue d'accueil (aucune vue active) -->
<section id="hero-intro" class="hero-intro" aria-label="Présentation du système">
  <h1 class="hero-title"><!-- @copywriter : accroche principale --></h1>
  <p class="hero-subtitle"><!-- @copywriter : sous-titre explicatif --></p>
  <div class="hero-status">
    <span class="hero-status-badge">En validation</span>
    <!-- @copywriter : phrase de contexte -->
  </div>
  <p class="hero-disclaimer-inline"><!-- @copywriter : ce qu'on ne fait pas --></p>
</section>
```

Comportement JS : le hero se masque automatiquement dès qu'une vue est active
(`hidden` ajouté par le routeur quand `#vue=...` change).
Il est visible au chargement initial (pas de vue active) et quand l'utilisateur
revient à l'état sans vue sélectionnée.

**P0-2 : Remplacer le nom dans `<a class="brand">` (L1052-1055)**

Actuel :
```html
<span class="brand-name">TradingApp <span class="brand-v">v3</span>
  <span class="brand-sub">· Bulletins</span>
</span>
```

Modification : supprimer `<span class="brand-sub">· Bulletins</span>`.
Remplacer par la tagline (@copywriter la fournit), ou laisser juste le nom court.
L'espace libéré permet de respirer.

**P0-3 : Ajouter le footer après `</div>` de `.layout` (L1175)**

Insérer avant `<script>` :
```html
<footer class="site-footer" role="contentinfo">
  <div class="footer-inner">
    <div class="footer-col footer-col-identity">
      <!-- @copywriter : nom + tagline courte -->
    </div>
    <div class="footer-col footer-col-status">
      <p>En validation · Go-live cible 08/08/2026.</p>
      <p>Le système ne place aucun ordre. L'exécution reste humaine.</p>
    </div>
    <div class="footer-col footer-col-disclaimer">
      <p>Les bulletins ne constituent pas un conseil en investissement.</p>
      <p>Les performances passées ne préjugent pas des performances futures.</p>
      <p class="footer-year">© 2026</p>
    </div>
  </div>
</footer>
```

**P0-4 : Supprimer le libellé "Sauter à :" dans la subnav (L1077)**

Actuel : `<span class="subnav-label">Sauter à :</span>`

Remplacer par : `<span class="subnav-label" aria-hidden="true"></span>` (vide)
ou supprimer entièrement le `<span class="subnav-label">` en vérifiant qu'il n'est pas
référencé en JS. Alternative : remplacer le texte par "Dans ce bulletin :".

---

### P1 — Modifications importantes (améliorent significativement la lisibilité)

**P1-1 : Restructurer la sidebar avec les groupes de navigation**

Dans `<ul id="nav-views">` (L1065-1070), modifier les libellés et l'ordre :

```html
<ul id="nav-views">
  <!-- Groupe 1 : Résultats -->
  <li class="nav-group-label" aria-hidden="true">Résultats</li>
  <li><a href="#vue=performance" id="nav-history" class="nav-view-link">📊 Win rate</a></li>
  <!-- Groupe 2 : Bulletins -->
  <li class="nav-group-label" aria-hidden="true">Bulletins</li>
  <li><a href="#vue=aujourdhui" id="nav-today" class="nav-view-link">📅 Bulletin du jour</a></li>
  <li><a href="#vue=semaine" id="nav-week" class="nav-view-link">🗓️ Bilan de la semaine</a></li>
  <!-- Groupe 3 : Marchés -->
  <li class="nav-group-label" aria-hidden="true">Marchés</li>
  <li><a href="#vue=variations" id="nav-variations" class="nav-view-link">📈 Mouvements</a></li>
</ul>
```

CSS pour `.nav-group-label` : `font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em;
color: var(--text-muted); padding: 12px 16px 4px; pointer-events: none;`

**P1-2 : CSS du hero (à ajouter dans le `<style>` de build_html.py)**

```css
.hero-intro {
  padding: 32px 24px 24px;
  max-width: 680px;
  margin: 0 auto;
}
.hero-title {
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 12px;
}
.hero-subtitle {
  font-size: 1rem;
  color: var(--text-secondary, #aaa);
  line-height: 1.6;
  margin-bottom: 16px;
}
.hero-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.hero-status-badge {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.hero-disclaimer-inline {
  font-size: 0.8rem;
  color: var(--text-muted, #666);
  border-left: 2px solid var(--border, #333);
  padding-left: 10px;
  margin-top: 8px;
}

/* Footer */
.site-footer {
  border-top: 1px solid var(--border, #333);
  padding: 24px 24px 16px;
  margin-top: 32px;
}
.footer-inner {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
  max-width: 960px;
  margin: 0 auto;
}
.footer-col {
  font-size: 0.8rem;
  color: var(--text-muted, #888);
  line-height: 1.6;
}
.footer-col p { margin: 0 0 6px; }
.footer-year { margin-top: 8px; opacity: 0.6; }

@media (max-width: 767px) {
  .footer-inner {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .hero-title { font-size: 1.3rem; }
}

/* Labels de groupe dans la sidebar */
.nav-group-label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted, #666);
  padding: 12px 16px 4px;
  pointer-events: none;
  display: block;
}
```

**P1-3 : Masquage conditionnel du hero**

Dans le JS de routing existant (chercher la fonction qui gère `#vue=...`, probablement
autour de `window.addEventListener('hashchange', ...)` ou `handleHash()`),
ajouter :

```js
const heroEl = document.getElementById('hero-intro');
// Masquer le hero quand une vue est active, le montrer sinon
if (heroEl) {
  heroEl.hidden = !!currentVue;  // true = masqué si vue active
}
```

**P1-4 : Titre `<h1>` dans `#today-view` (L1110)**

Actuel : `<h1>📅 Aujourd'hui</h1>`
Proposé : `<h1>📅 Bulletin du jour</h1>`
(cohérence avec le libellé sidebar)

Idem pour les autres vues si les H1 internes sont ajustés. Non bloquant.

---

### P2 — Améliorations optionnelles (polish)

**P2-1 : Meta tags pour le partage (Open Graph)**

Ajouter dans `<head>` (pour que le lien partagé s'affiche bien sur WhatsApp/LinkedIn) :
```html
<meta property="og:title" content="[Tagline courte — @copywriter]" />
<meta property="og:description" content="Analyse directionnelle sur 12 actifs. En validation." />
<meta property="og:type" content="website" />
```

**P2-2 : `<title>` de la page**

Actuel : vraisemblablement "TradingApp v3" ou vide.
Proposé : "[Tagline courte] · issa-capital.com" (à définir avec @copywriter).

**P2-3 : Aria-label du brand (L1052)**

Actuel : `aria-label="TradingApp v3 — accueil"` (contient un tiret cadratin dans l'attribut).
Proposé : `aria-label="TradingApp v3, accueil"` (virgule, cohérent avec la préférence Thomas).

**P2-4 : Message vide dans `#today-view` quand aucun bulletin**

Actuel : `<p id="today-empty" hidden></p>` (L1113, vide).
Proposé : ajouter un texte dans cet élément : "Le bulletin du jour n'est pas encore disponible.
Il est publié à 7h, 12h et 18h (heure de Paris)." (visibilité contrôlée par JS existant).

---

## Tests UX — Parcours primo-visiteur

| Test | Critère de succès | Statut |
|---|---|---|
| Primo-visiteur comprend le sujet en 10 sec | Hero visible above the fold, accroche claire | A valider apres implem |
| Charge cognitive hero : max 3 blocs principaux | H1 + H2 + H3 (statut) = 3 blocs avant le fold | Spec OK |
| Statut "en validation" visible sans être alarmiste | Badge sobre ambre, pas de rouge | Spec OK |
| Aucun €/P&L dans hero et footer | WIN RATE ONLY respecté partout | Spec OK |
| Zéro tiret cadratin dans tout texte affiché | "Sauter à :" supprimé, aria-label corrigé | Spec OK |
| Nav accessible au clavier | IDs sidebar inchangés, focus order logique | A verifier apres implem |
| Footer visible sur mobile | grid → stack vertical documenté | Spec OK |
| Vues existantes non cassées | IDs HTML inchangés, ancres JS inchangées | Sous condition |

---

## Agents spécialisés recommandés

| Agent proposé | Type | Role | Justification | Priorite |
|---|---|---|---|---|
| @copywriter | Contenu | Rediger les textes du hero (H1/H2/H3/H4), tagline footer, title meta | La spec definit la STRUCTURE et l'INTENTION, pas les mots. Le copywriter doit ecrire les formules sans tiret cadratin, sans jargon, en connaissant les contraintes WIN RATE ONLY | Haute |
| @fullstack | Developpement | Implementer P0, P1, P2 dans build_html.py | Instructions detaillees ci-dessus avec references aux lignes exactes | Haute |

---

## Metriques HEART

| Dimension | Signal | Metrique cible | Methode |
|---|---|---|---|
| Task success | Le primo-visiteur identifie la valeur du produit | Comprension en < 10 sec (test utilisateur) | Test qualitatif 5 personnes non-traders |
| Adoption | Part des visiteurs qui scrollent vers Performance | % scroll depth > Performance | Event analytics (scroll depth) |
| Happiness | Thomas est fier de partager le lien | Retour subjectif Thomas apres partage | Feedback direct |
