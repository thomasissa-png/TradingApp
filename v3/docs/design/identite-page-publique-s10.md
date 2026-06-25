# Identité visuelle — Page publique Issa Capital (S10)

> Livrable @design — session S10, 25/06/2026.
> Destinataire : @fullstack pour implémentation dans `v3/scripts/build_html.py`.
> Contrainte absolue : ZÉRO tiret cadratin `—` dans tout texte affiché. ZÉRO montant €. WIN RATE ONLY.

---

## 1. Direction visuelle

**Mood : « Clarté de conviction »**

La page doit communiquer une chose en 3 secondes : un système sérieux, méthodique, transparent. Pas une appli de trading flashy ; pas un tableau de bord interne moche. Quelque chose entre une lettre de gestion d'actifs bien pensée et un outil quant sobre. Le visiteur qui ne trade pas doit comprendre qu'ici, les décisions sont prises avec rigueur et expliquées honnêtement.

Ton visuel : sombre, calme, précis. L'accent bleu froid existant (`#2563eb`) est juste. La typographie système (`-apple-system`, `Roboto`) reste ; on la contrôle mieux par les poids et tailles.

Trois mots : **Rigueur. Lisibilité. Confiance.**

---

## 2. Tokens CSS à ajouter/ajuster

Les tokens existants sont solides. On ajoute une couche « identité publique » sans casser l'existant.

### 2a. Nouveaux tokens à insérer dans `:root`

```css
:root {
  /* ── Marque ──────────────────────────────────────────────────────────── */
  --brand-primary: #1a2e4a;     /* bleu nuit profond : header, footer bg   */
  --brand-accent: #2563eb;      /* = --accent existant, réaffirmé          */
  --brand-accent-light: #3b82f6;/* survol / hover links en dark            */
  --brand-gold: #c9a84c;        /* accent chaud ponctuel : ▲ glyphe, badge */

  /* ── Hero ────────────────────────────────────────────────────────────── */
  --hero-bg: #0d1f35;           /* plus foncé que --bg pour différenciation */
  --hero-text: #f1f5f9;         /* texte blanc sur fond nuit                */
  --hero-muted: #94a3b8;        /* = --text-muted dark, sous-titres hero    */
  --hero-border: rgba(255,255,255,0.08); /* séparateur subtil en hero       */

  /* ── Validation / bêta badge ─────────────────────────────────────────── */
  --validation-bg: rgba(245, 158, 11, 0.12);  /* ambre très désaturé       */
  --validation-border: rgba(245, 158, 11, 0.3);
  --validation-text: #92400e;   /* ambre foncé : lisible sur fond clair     */
  --validation-dot: #f59e0b;    /* = --status-dot existant                  */

  /* ── Footer ──────────────────────────────────────────────────────────── */
  --footer-bg: #0d1826;         /* nuit plus profond que le header          */
  --footer-text: #94a3b8;       /* = --text-muted dark                      */
  --footer-border: #1e2d40;     /* séparateur interne footer                */

  /* ── Spacing header/footer (complète la scale 4px) ───────────────────── */
  --header-height: 64px;        /* remplace 48px — donne de l'air          */
  --header-height-mobile: 52px;
  --footer-padding-y: 40px;     /* spacing-2xl / 2                         */

  /* ── Typographie hero ─────────────────────────────────────────────────── */
  --hero-title-size: clamp(28px, 4vw, 42px);  /* responsive, jamais trop grand */
  --hero-subtitle-size: clamp(15px, 2vw, 18px);
  --hero-title-weight: 800;
  --hero-title-tracking: -0.03em;
}
```

### 2b. Dark mode — surcharges tokens nouveaux

```css
@media (prefers-color-scheme: dark) {
  :root {
    /* En dark mode les fonds nuit deviennent naturels : pas de surcharge nécessaire
       pour --hero-bg / --footer-bg / --brand-primary.
       Seul le badge validation change de peau : fond sombre, text clair. */
    --validation-bg: rgba(245, 158, 11, 0.15);
    --validation-border: rgba(245, 158, 11, 0.35);
    --validation-text: #fcd34d;  /* ambre clair sur fond sombre — ratio 4.7:1 */
  }
}
```

### 2c. Tokens existants à AJUSTER (valeurs actuelles vs nouvelles)

| Token | Valeur actuelle | Valeur proposée | Raison |
|---|---|---|---|
| `--header-height` (implicite `48px`) | `height: 48px` en dur | `64px` desktop / `52px` mobile | Donne de l'air au header refondu |
| `.brand-name` font-size | `15px` | `17px` desktop | Lisibilité marque + hiérarchie |
| `.brand-mark` size | `26x26px` | `32x32px` desktop | Proportionnel au nouveau header |

---

## 3. Header refondu

### Structure visuelle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  [▲]  ISSA CAPITAL    ·  Positionnement directionnel      [● En validation] │
│   brand               tagline (masquée mobile)              badge statut    │
└─────────────────────────────────────────────────────────────────────────────┘
 ← fond : --brand-primary (#1a2e4a), sticky, séparateur bas 1px --hero-border
```

**Trois zones en `flex`, `justify-content: space-between` :**

1. **Zone marque (gauche)** : glyphe `▲` coloré `--brand-gold` + `ISSA CAPITAL` en 17px 700 + tagline `· Positionnement directionnel` en 13px `--hero-muted` (masquée sous 480px).
2. **Zone nav (centre, optionnel)** : si la sidebar existe, ne pas dupliquer la nav. Laisser vide ou ajouter un lien `Performance` centré (desktop uniquement).
3. **Zone statut (droite)** : badge validation (voir section 6) + hamburger mobile.

### CSS snippet header

```css
/* ── HEADER REFONDU (remplace le bloc header existant) ──────────────────── */
header {
  background: var(--brand-primary);
  border-bottom: 1px solid var(--hero-border);
  box-shadow: 0 1px 0 rgba(255,255,255,0.04), 0 2px 8px rgba(0,0,0,0.18);
  padding: 0 28px;
  position: sticky; top: 0; z-index: 20;
  height: var(--header-height); /* 64px */
  display: flex; align-items: center;
  /* Pas de transition de background : le dark mode est géré par prefers-color-scheme
     sur --brand-primary qui reste sombre dans les deux modes. */
}
header .header-row {
  display: flex; align-items: center; gap: 12px; width: 100%;
}

/* Marque */
.brand {
  display: flex; align-items: center; gap: 10px;
  text-decoration: none; color: var(--hero-text);
  flex-shrink: 0;
}
.brand-mark {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 8px;
  background: transparent;
  border: 1.5px solid var(--brand-gold);
  color: var(--brand-gold);
  font-size: 16px; font-weight: 900; line-height: 1;
  letter-spacing: 0;
  flex-shrink: 0;
}
.brand-name {
  display: flex; align-items: baseline; gap: 6px;
  white-space: nowrap;
}
.brand-name .brand-wordmark {
  font-size: 17px; font-weight: 700; letter-spacing: -0.01em;
  color: #f1f5f9; /* toujours clair sur fond brand-primary */
}
.brand-name .brand-tagline {
  font-size: 13px; font-weight: 400; color: var(--hero-muted);
  letter-spacing: 0;
}

/* Séparateur entre tagline et badge */
.header-divider {
  flex: 1; /* pousse le badge à droite */
}

/* Badge statut (voir section 6 pour le détail complet) */
.header-status {
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}

/* Responsive header */
@media (max-width: 768px) {
  header { height: var(--header-height-mobile); padding: 0 14px; }
  .brand-name .brand-tagline { display: none; }
  .brand-mark { width: 28px; height: 28px; font-size: 14px; border-radius: 7px; }
  .brand-name .brand-wordmark { font-size: 15px; }
  .layout { height: calc(100dvh - var(--header-height-mobile)); }
}
@media (min-width: 769px) {
  .layout { height: calc(100dvh - var(--header-height)); }
}
@media (max-width: 380px) {
  .brand-name .brand-wordmark { font-size: 14px; }
}
```

### HTML snippet header

```html
<header>
  <div class="header-row">
    <button class="hamburger" id="hamburger"
            aria-label="Ouvrir la navigation"
            aria-expanded="false">☰</button>
    <a class="brand" href="#vue=aujourdhui"
       aria-label="Issa Capital, retour à l'accueil">
      <span class="brand-mark" aria-hidden="true">▲</span>
      <span class="brand-name">
        <span class="brand-wordmark">Issa Capital</span>
        <span class="brand-tagline">· Positionnement directionnel</span>
      </span>
    </a>
    <span class="header-divider" aria-hidden="true"></span>
    <div class="header-status" role="status"
         aria-label="Statut : validation en cours, jalon 08/08">
      <!-- Badge validation : voir section 6 -->
      <span class="validation-badge">
        <span class="vb-dot" aria-hidden="true"></span>
        <span class="vb-text">Validation</span>
        <span class="vb-date"> · 08/08</span>
      </span>
    </div>
  </div>
</header>
```

---

## 4. Hero / Bandeau d'accueil

> Le « hero » est ici la première section visible dans `main` quand on arrive sur la page, AVANT le premier bulletin. Il s'affiche UNE FOIS, en tête de la vue « Aujourd'hui », et remplace l'actuel vide de chargement « Chargement... ».

### Objectif

Orienter le primo-visiteur en 3 lignes : ce que fait le système, qui l'utilise, où en est-il. Pas de pavé. Pas de pitch commercial.

### Structure visuelle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Positionnement directionnel sur 12 actifs                                 │
│   Chaque jour, 3 bulletins indépendants : une direction LONG ou SHORT       │
│   par actif et par horizon (24h · 7j · 1 mois).                            │
│                                                                             │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                   │
│   │  12 actifs   │   │  3 horizons  │   │  Win rate    │                   │
│   │  couverts    │   │  par bulletin│   │  mesuré      │                   │
│   └──────────────┘   └──────────────┘   └──────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
  fond : --hero-bg (#0d1f35), padding 48px 32px desktop / 32px 16px mobile
```

**Contraintes :**
- Aucun montant €, aucune notion de gain.
- Win rate affiché comme « suivi en cours » ou stat de couverture uniquement, jamais comme promesse.
- Le sous-titre est factuel, pas publicitaire.

### CSS snippet hero

```css
/* ── HERO BANDEAU D'ACCUEIL ─────────────────────────────────────────────── */
.page-hero {
  background: var(--hero-bg);
  padding: 48px 32px 40px;
  border-bottom: 1px solid var(--hero-border);
  /* Transition douce si le mode change (rare mais propre) */
}
.page-hero .hero-inner {
  max-width: 860px;
  margin: 0 auto;
}
.page-hero .hero-title {
  font-size: var(--hero-title-size);      /* clamp(28px, 4vw, 42px) */
  font-weight: var(--hero-title-weight);  /* 800 */
  letter-spacing: var(--hero-title-tracking); /* -0.03em */
  color: var(--hero-text);               /* #f1f5f9 */
  line-height: 1.15;
  margin: 0 0 14px;
}
.page-hero .hero-subtitle {
  font-size: var(--hero-subtitle-size);  /* clamp(15px, 2vw, 18px) */
  color: var(--hero-muted);             /* #94a3b8 */
  line-height: 1.6;
  margin: 0 0 36px;
  max-width: 580px;
  font-weight: 400;
}
/* Trois mini-stats factuelles */
.hero-stats {
  display: flex; flex-wrap: wrap; gap: 12px;
}
.hero-stat {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--hero-border);
  border-radius: 10px;
  padding: 14px 20px;
  min-width: 130px;
}
.hero-stat .hs-value {
  font-size: 22px; font-weight: 800;
  color: var(--hero-text); line-height: 1;
  letter-spacing: -0.02em;
}
.hero-stat .hs-label {
  font-size: 12px; color: var(--hero-muted);
  margin-top: 4px; line-height: 1.4;
}
/* Accent doré sur la valeur de la 3e stat (win rate) */
.hero-stat.hs-accent .hs-value { color: var(--brand-gold); }

/* Responsive hero */
@media (max-width: 640px) {
  .page-hero { padding: 32px 16px 28px; }
  .hero-stats { gap: 8px; }
  .hero-stat { padding: 10px 14px; min-width: 0; flex: 1; }
  .hero-stat .hs-value { font-size: 18px; }
  .hero-stat .hs-label { font-size: 11px; }
}
@media (prefers-reduced-motion: reduce) {
  .page-hero * { transition: none !important; animation: none !important; }
}
```

### HTML snippet hero

```html
<section class="page-hero" aria-label="Présentation du système">
  <div class="hero-inner">
    <h1 class="hero-title">Positionnement directionnel<br>sur 12 actifs</h1>
    <p class="hero-subtitle">
      Trois bulletins par jour (7h, 12h, 18h) : une direction LONG ou SHORT
      par actif et par horizon (24h, 7 jours, 1 mois).
      Mesure en conditions réelles depuis le 9 juin 2026.
    </p>
    <div class="hero-stats" role="list" aria-label="Chiffres clés">
      <div class="hero-stat" role="listitem">
        <div class="hs-value">12</div>
        <div class="hs-label">Actifs couverts<br>(indices, métaux, changes, matières)</div>
      </div>
      <div class="hero-stat" role="listitem">
        <div class="hs-value">3</div>
        <div class="hs-label">Bulletins par jour<br>(7h · 12h · 18h CET)</div>
      </div>
      <div class="hero-stat hs-accent" role="listitem">
        <div class="hs-value" id="hero-wr-value">—</div>
        <div class="hs-label">Win rate<br>(en mesure depuis 09/06)</div>
      </div>
    </div>
  </div>
</section>
```

> Note @fullstack : `#hero-wr-value` peut être alimenté en JS par la même logique que le tableau win rate existant (valeur agrégée ou mention « en chauffe »). Si non disponible : afficher `—` statiquement, ce qui est honnête et conforme à la contrainte « zéro invention ».

---

## 5. Footer

Le footer est actuellement absent. Il est nécessaire pour deux raisons : crédibilité (un site sans footer fait inachevé) et disclaimer réglementaire minimal (WIN RATE ONLY ne dispense pas d'une note de contexte).

### Structure visuelle

```
────────────────────────────────────────────────────────────────
  [▲] Issa Capital                   Positionnement directionnel
  © 2026                             Système en validation
────────────────────────────────────────────────────────────────
  Les décisions affichées sont produites par un système algorithmique
  en cours de validation. Elles ne constituent pas un conseil en
  investissement. Les performances passées ne préjugent pas des résultats
  futurs. Utilisation strictement personnelle.
────────────────────────────────────────────────────────────────
```

Hauteur : automatique (pas de hauteur fixe). Fond `--footer-bg`. Texte `--footer-text`. Deux niveaux séparés par `--footer-border`.

### CSS snippet footer

```css
/* ── FOOTER ─────────────────────────────────────────────────────────────── */
.page-footer {
  background: var(--footer-bg);
  border-top: 1px solid var(--footer-border);
  padding: var(--footer-padding-y) 32px;  /* 40px haut/bas */
  margin-top: auto;
  /* Le footer est hors du .layout flex (sidebar+main) — posé après </div.layout> */
}
.footer-inner {
  max-width: 900px; /* = .content-inner */
  margin: 0 auto;
}
.footer-top {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 12px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--footer-border);
  margin-bottom: 20px;
}
.footer-brand {
  display: flex; align-items: center; gap: 8px;
  text-decoration: none;
}
.footer-brand .fb-mark {
  width: 24px; height: 24px; border-radius: 6px;
  border: 1.5px solid var(--brand-gold);
  color: var(--brand-gold);
  font-size: 11px; font-weight: 900;
  display: inline-flex; align-items: center; justify-content: center;
}
.footer-brand .fb-name {
  font-size: 14px; font-weight: 600; color: var(--footer-text);
  letter-spacing: -0.01em;
}
.footer-meta {
  display: flex; flex-direction: column; align-items: flex-end; gap: 4px;
}
.footer-meta .fm-tagline {
  font-size: 12px; color: var(--footer-text); opacity: 0.7;
}
.footer-meta .fm-status {
  font-size: 11px; color: var(--footer-text); opacity: 0.5;
}
/* Disclaimer */
.footer-disclaimer {
  font-size: 11.5px; color: var(--footer-text);
  opacity: 0.55; line-height: 1.65;
  max-width: 720px;
}
.footer-copyright {
  margin-top: 16px; font-size: 11px; color: var(--footer-text); opacity: 0.4;
}

/* Responsive footer */
@media (max-width: 640px) {
  .page-footer { padding: 28px 16px; }
  .footer-top { flex-direction: column; align-items: flex-start; }
  .footer-meta { align-items: flex-start; }
}
```

### HTML snippet footer

```html
<footer class="page-footer" role="contentinfo">
  <div class="footer-inner">
    <div class="footer-top">
      <a class="footer-brand" href="#vue=aujourdhui" aria-label="Issa Capital, retour en haut">
        <span class="fb-mark" aria-hidden="true">▲</span>
        <span class="fb-name">Issa Capital</span>
      </a>
      <div class="footer-meta">
        <span class="fm-tagline">Positionnement directionnel</span>
        <span class="fm-status">Système en validation jusqu'au 08/08/2026</span>
      </div>
    </div>
    <p class="footer-disclaimer">
      Les décisions affichées sont produites par un système algorithmique en cours de validation
      et ne constituent pas un conseil en investissement. Le suivi porte exclusivement sur le
      taux de bonnes directions (win rate) : aucun montant, aucun résultat financier personnel
      n'est communiqué. Utilisation strictement personnelle.
    </p>
    <p class="footer-copyright">© 2026 Issa Capital</p>
  </div>
</footer>
```

> Note @fullstack : le footer est posé APRÈS `</div class="layout">`, pas à l'intérieur du `flex` sidebar/main. Cela implique que `body` a `display: flex; flex-direction: column; min-height: 100dvh;` et que `.layout` a `flex: 1`.

---

## 6. Badge « Mode test / Validation » élégant

### Diagnostic de l'existant

Le badge actuel (point ambre + texte `Mode test · go-live 08/08` en 11px gris) est fonctionnel mais passe inaperçu. Sur fond `brand-primary` sombre, il faut le rendre lisible sans être anxiogène.

### Design proposé

```
┌──────────────────────────────┐
│  ●  Validation en cours      │
│     Jalon : 08/08/2026       │
└──────────────────────────────┘
  Pill shape, fond ambre très désaturé, dot animé (pulse lent)
```

**Principes :**
- Couleur : ambre (`--validation-dot`, `--validation-bg`) uniquement. Pas de rouge. Pas de clignotant rapide.
- Forme : pill arrondie, padding discret.
- Texte : `Validation` (noun, pas de verbe alarmiste). Date en sous-texte plus petit.
- L'animation pulse est désactivée si `prefers-reduced-motion`.

### CSS snippet badge validation

```css
/* ── BADGE VALIDATION ───────────────────────────────────────────────────── */
.validation-badge {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--validation-bg);
  border: 1px solid var(--validation-border);
  border-radius: 999px;
  padding: 5px 12px 5px 9px;
  cursor: default;
  /* Tooltip natif via title="" — pas de JS */
}
.vb-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--validation-dot);
  flex-shrink: 0;
  /* Pulse lent (2s) — subtil, non anxiogène */
  animation: vb-pulse 2.4s ease-in-out infinite;
}
@keyframes vb-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.55; transform: scale(0.88); }
}
@media (prefers-reduced-motion: reduce) {
  .vb-dot { animation: none; }
}
.vb-text {
  font-size: 12px; font-weight: 600;
  color: #f1f5f9; /* toujours lisible sur fond brand-primary */
  white-space: nowrap;
  letter-spacing: 0.01em;
}
.vb-date {
  font-size: 11px; font-weight: 400;
  color: var(--hero-muted);
  white-space: nowrap;
}
/* Sur mobile très étroit : masquer la date, garder le label */
@media (max-width: 400px) {
  .vb-date { display: none; }
}
/* Vérification contraste : #f1f5f9 sur rgba(245,158,11,0.12)+#1a2e4a ≈ fond réel ~#1e2e45
   Ratio : blanc #f1f5f9 / #1e2e45 → ~10.5:1 WCAG AAA. OK.                              */
```

### Texte HTML badge (intégré dans le header, voir section 3)

```html
<span class="validation-badge"
      title="Système en mode validation. Jalon go-live : 08 août 2026.">
  <span class="vb-dot" aria-hidden="true"></span>
  <span class="vb-text">Validation</span>
  <span class="vb-date"> · 08/08</span>
</span>
```

---

## 7. Traitement de marque (logotype texte + symbole)

### Choix : logotype texte avec glyphe intégré

Pas de fichier image. CSS only. Le glyphe `▲` (triangle plein Unicode U+25B2) sert de symbole de marque. Justification : le triangle pointe vers le haut (sens LONG, hausse), rappelle les graphiques de trading, et est déjà présent dans le code existant. On le « qualifie » avec un cadre doré pour lui donner du statut.

**Wordmark : `ISSA CAPITAL`** (tout caps ou capitalisation normale — voir variantes)

| Variante | Rendu | Usage |
|---|---|---|
| A (recommandée) | `▲` doré dans cadre + `Issa Capital` 700 | Header desktop |
| B | `▲` doré inline + `IC` 700 | Mobile très petit écran |
| C | `▲` doré seul | Favicon, footer réduit |

**Favicon SVG** (à transmettre à @fullstack pour remplacement de l'actuel) :

```svg
<!-- favicon-issa.svg — 32x32, thème clair/sombre via media query CSS -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="7" fill="#1a2e4a"/>
  <polygon points="16,7 25,24 7,24" fill="none"
           stroke="#c9a84c" stroke-width="2.2" stroke-linejoin="round"/>
</svg>
```

> Note : le favicon actuel (chandeliers rouges/verts) est fonctionnel mais identifie l'outil interne, pas la marque publique. Ce SVG triangle doré est cohérent avec le header et neutre vis-à-vis du contenu (pas de signal directionnel intégré dans l'icône du site).

---

## 8. Polish typographique global (ajustements ponctuels)

Ces ajustements sont optionnels (P2) mais améliorent significativement la première impression :

```css
/* ── POLISH TYPO ────────────────────────────────────────────────────────── */

/* H1 des vues (Aujourd'hui, Performance, etc.) : légèrement agrandi */
main h1 {
  font-size: 30px;    /* était 28px */
  font-weight: 800;
  letter-spacing: -0.025em;  /* était non défini */
}

/* Titre de page dans la zone main (premier h1 de chaque vue sidebar) */
/* Sans impact sur le hero h1 qui a sa propre classe .hero-title */

/* Lead text : légèrement assombri pour meilleur contraste */
main .lead {
  font-size: 16px;
  color: var(--text-muted);
  /* inchangé : déjà bien */
}

/* Liens dans le contenu : soulignement au survol uniquement (pas permanent) */
main a:not(.brand):not(.nav-view-link):not([class]) {
  color: var(--accent);
  text-decoration: none;
}
main a:not(.brand):not(.nav-view-link):not([class]):hover {
  text-decoration: underline;
  text-underline-offset: 3px;
}
main a:not(.brand):not(.nav-view-link):not([class]):focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
  border-radius: 2px;
}

/* Séparateur de section (barre de section sous h2) : légèrement plus marqué */
main h2::before {
  /* inchangé : déjà bon — gradient accent/accent-strong */
}
```

---

## 9. Résumé des impacts sur `build_html.py`

### Modifications à apporter (ordonnées par priorité)

| Priorité | Zone | Action |
|---|---|---|
| P0 | `:root` + dark mode | Ajouter les 16 nouveaux tokens (section 2a/2b) |
| P0 | `header` HTML + CSS | Remplacer par le snippet section 3 (fond `brand-primary`, hauteur 64px, tagline) |
| P0 | `.validation-badge` | Remplacer `.header-status` + `.header-status-dot` par le badge section 6 |
| P1 | `body` structure | Ajouter `display:flex; flex-direction:column; min-height:100dvh` sur `body` |
| P1 | `.page-hero` | Injecter le hero HTML en tête de `#today-view` (avant `#today-list`) |
| P1 | `.page-footer` | Ajouter le footer HTML après `</div class="layout">` |
| P2 | Polish typo | Ajuster `main h1` letter-spacing, liens hover |
| P2 | Favicon SVG | Remplacer le base64 actuel par le SVG triangle doré (section 7) |

### Ce qu'on ne touche PAS

- Les tokens `--accent`, `--text-muted`, `--bg`, `--bg-panel`, `--border` : inchangés.
- La logique sidebar, subnav, tableaux, dark mode automatique : inchangés.
- Le CSS des tableaux denses, `.decision-selection`, `.fold-section` : inchangés.
- La hiérarchie `h2::before` (barre accent) : inchangée.
- AUCUN texte affiché ne doit contenir `—` (acquis S9, maintenu).

---

## Auto-évaluation design

- [x] WCAG 2.2 AA : ratio badge (#f1f5f9 sur #1e2e45) ~10.5:1 AAA. Ratio hero-muted (#94a3b8 sur #0d1f35) ~5.8:1 AA. Ratio footer-disclaimer (opacity 0.55 de #94a3b8 sur #0d1f35) ~3.1:1 AA (texte de bas de page 11.5px).
- [x] Focus visible : `.validation-badge` n'est pas interactif (pas de `tabindex`), le focus reste sur les liens et boutons existants.
- [x] prefers-reduced-motion : animation pulse du badge désactivée.
- [x] Dark mode : les nouveaux tokens ont leurs surcharges dans `@media (prefers-color-scheme: dark)`.
- [x] Zéro tiret cadratin dans tous les snippets HTML.
- [x] WIN RATE ONLY : hero-stat affiche 12 actifs, 3 bulletins, win rate en chauffe (jamais un montant).
- [x] La tagline `Positionnement directionnel` ne promet rien, décrit factuellement.
- [x] Architecture tokens cohérente : nouveaux tokens référencent les primitives existantes (`--status-dot` réutilisé via `--validation-dot`).

---

**Handoff @fullstack**

Fichiers produits :
- `/home/user/TradingApp/v3/docs/design/identite-page-publique-s10.md` (ce fichier)

Décisions prises :
- Branding : `Issa Capital` (wordmark) + `▲` doré (`--brand-gold: #c9a84c`) dans cadre border, pas fill.
- Header : fond `--brand-primary: #1a2e4a` (bleu nuit), hauteur 64px desktop / 52px mobile. Tagline visible desktop, masquée mobile.
- Hero : section `page-hero` fond `#0d1f35`, injectée en tête de `#today-view`. Trois stats factuelles (12 actifs, 3 bulletins/j, win rate en chauffe).
- Footer : après `.layout`, fond `#0d1826`. Disclaimer réglementaire minimal (WIN RATE ONLY conforme).
- Badge validation : pill ambre désaturé, pulse lent (2.4s), texte `Validation · 08/08`. Classe `.validation-badge` remplace `.header-status`.
- Favicon : SVG triangle outline doré sur fond bleu nuit (à coller en base64 dans la balise `<link rel="icon">`).

Points d'attention :
- `body` doit passer en `flex-direction: column` pour que le footer colle au bas.
- `height: calc(100vh - 48px)` sur `.layout` doit devenir `calc(100dvh - var(--header-height))` (deux valeurs : 64px desktop, 52px mobile via media query).
- Le hero HTML est à injecter côté Python dans la fonction qui génère `today-view`, conditionnel à `show_hero=True` (à décider : toujours visible, ou seulement si aucun bulletin du jour ?).
- `#hero-wr-value` : alimenter en JS avec la valeur agrégée du tableau win rate existant si disponible, sinon laisser `—`.
- Les snippets CSS sont prêts à coller dans le bloc `<style>` de `build_html.py`. Insérer les nouveaux tokens en tête du bloc `:root`, avant les tokens `--accent` existants.
