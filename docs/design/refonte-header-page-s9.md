# Refonte header page TradingApp v3 — Spec visuelle S9

> Auteur : @design · Date : 2026-06-20
> Périmètre : SYSTÈME VISUEL uniquement (contenu = @ux en parallèle)
> Fichier cible : `v3/scripts/build_html.py` (section `<style>` + HTML header)

---

## (a) Diagnostic visuel du header actuel — note /10

### Structure actuelle (L874-889 + L908-932)

La pile de chrome permanent comprend :

1. `<header>` sticky : h1 17px + ligne meta 12px + ligne legend 12px → ~70-75px
2. `.context-banner` : bandeau "Mode test" → ~36px
3. `.legend-bar` : 6 éléments légende directionnelle → ~46px (non-sticky mais visible d'emblée)
4. `.subnav` sticky (top:0 dans `.subnav`, mais sous `main`) : ~38px

**Hauteur de chrome figée en tête de viewport : ~110px (header + subnav). La legend-bar et le context-banner s'empilent en plus au chargement.**

### Scores par critère Thomas

| Critère | Score | Diagnostic |
|---|---|---|
| PRO | 6/10 | Propre mais générique. Niveau "admin interne à la va-vite" |
| ÉPURÉ | 4/10 | 4 strates de chrome empilées, surcharge informationnelle immédiate |
| HIÉRARCHIE | 5/10 | Le titre, la meta, la légende de 6 symboles, le bandeau test et la legend-bar ont tous le même poids visuel |
| RESPIRATION | 4/10 | Densité maximale en zone haute. Aucun espace blanc |
| COHÉRENCE | 7/10 | Les tokens dark mode sont bons (palette slate), appliqués avec cohérence |
| DENSITÉ MOBILE | 3/10 | ~110px de chrome sticky sur un viewport de 667px = 16 % consommés par du chrome |

**Note globale actuelle : 4,5/10**

### Problèmes identifiés

- **P0 — Mur de texte au-dessus de la ligne de flottaison** : le regard se noie avant d'atteindre le bulletin
- **P0 — Redondance legend** : la légende figure dans le header (L880-888), dans la `.legend-bar` (L908-926) ET dans le `.help-box` replié (L934-950) — trois fois la même info
- **P1 — Le bandeau "Mode test" n'est pas visuellement discret** : couleur `--accent-bg` (#1e3a5f) donne un bandeau bleu marqué, pas une indication discrète
- **P1 — La `.subnav` colle à `top:0` en contexte `main` mais le header lui-même colle aussi** → conflit de stickiness, comportement imprévisible selon scroll context
- **P2 — Typographie plate** : même graisse/couleur pour des informations de statut très différentes (titre app vs timestamp vs légende des symboles)

---

## (b) Tokens de design proposés

### Palette — conserver l'existant, affiner 3 valeurs

Les tokens actuels dans `:root` sont bons. Ajouts/raffinements uniquement.

```css
:root {
  /* === EXISTANTS À CONSERVER === */
  --bg:              #0f172a;   /* fond page */
  --bg-panel:        #1e293b;   /* panels, header, sidebar */
  --border:          #334155;   /* bordures douces */
  --border-strong:   #475569;   /* bordures mises en avant */
  --text:            #f1f5f9;   /* texte principal */
  --text-muted:      #94a3b8;   /* texte secondaire */
  --accent:          #60a5fa;   /* liens, pilules actives */
  --accent-bg:       #1e3a5f;   /* fond accent discret */
  --code-bg:         #1e293b;
  --row-alt:         #172033;
  --badge-bg:        #15803d;
  --badge-text:      #ffffff;
  --th-bg:           #243044;
  --dir-long-color:  #4ade80;   /* LONG vert */
  --dir-short-color: #f87171;   /* SHORT rouge */

  /* === NOUVEAUX TOKENS : bandeau statut === */
  --status-bg:       #0f1c2e;   /* fond bandeau test — plus sombre que accent-bg */
  --status-border:   #1d3045;   /* bordure bandeau test — à peine visible */
  --status-text:     #64748b;   /* texte statut — discret, 1 cran en dessous de text-muted */
  --status-dot:      #f59e0b;   /* point statut "mode test" — ambre, ni rouge ni vert */

  /* === NOUVEAU TOKEN : séparateur header === */
  --header-divider:  #253348;   /* ligne de séparation interne header — plus douce que --border */
}
```

### Spacing scale (ceux utilisés dans le header)

| Token sémantique | Valeur | Usage |
|---|---|---|
| `--space-2xs` | 2px | gaps internes micro |
| `--space-xs` | 4px | gap header-row items |
| `--space-sm` | 8px | padding vertical header ligne unique |
| `--space-md` | 12px | padding horizontal header compact |
| `--space-lg` | 16px | padding horizontal contenu principal |
| `--space-xl` | 20px | padding horizontal desktop |

### Typographie — hiérarchie dans le header

```
h1 header    : 15px / weight 600 / --text        → nom app + contexte
meta ligne   : 12px / weight 400 / --text-muted  → timestamp (secondaire)
statut badge : 11px / weight 500 / --status-text  → mode test (tertiaire)
```

Ratio : chaque niveau = −1 à −2px et −1 cran de poids. Lisible sans compétition.

### Rayons

```
--radius-sm  : 4px   (badges inline)
--radius-md  : 6px   (pilules subnav)
--radius-lg  : 8px   (cards, panels)
```

---

## (c) Spec du nouveau header

### Maquette ASCII — desktop (≥ 768px)

```
┌──────────────────────────────────────────────────── sticky ──┐
│ ☰  TradingApp v3 — Bulletins          ● Mode test · 08/08    │  ← 44px
└──────────────────────────────────────────────────────────────┘
                                                                   ↓ défile
┌───────────────────────────────────────────────────────────────┐
│  🟢 LONG = hausse · 🔴 SHORT = baisse · ⚑ gate · ⚪ coin-flip  │  ← legend-bar (NON sticky, défile)
│  📰 news>50% · ⚠ contesté · 🔴 alerte · 🟡 vigilance          │
└───────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────┐  sticky
│ Sauter à :  [Sélection]  [Synthèse]  [À jouer]  [Matrice]    │  ← subnav 38px
└───────────────────────────────────────────────────────────────┘
```

**Total chrome sticky permanent : 44px (vs ~110px actuels) → −60 %**

### Maquette ASCII — mobile (< 768px)

```
┌─────────────────────────────── sticky ──┐
│ ☰  TradingApp v3    ● Mode test         │  ← 40px
└─────────────────────────────────────────┘
                                              ↓ défile
┌─────────────────────────────────────────┐
│  🟢 LONG · 🔴 SHORT · ⚑ ⚪ 📰 ⚠       │  ← legend-bar compacte (défile)
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐  sticky
│ [Sélect.]  [Synthèse]  [Matrice]        │  ← subnav 36px
└─────────────────────────────────────────┘
```

**Total chrome sticky mobile : 40 + 36 = 76px (vs ~110px actuels) → −31 %**

### CSS cible — prêt à intégrer dans `<style>` de build_html.py

Remplace entièrement les blocs `header {`, `header .header-row`, `header h1`, `header .meta`, `header .legend`, `.context-banner`, `.context-inner`, `.legend-bar` et `.subnav` actuels.

```css
/* ─────────────────────────────────────────────────
   HEADER PRINCIPAL — ligne unique, sticky
   ───────────────────────────────────────────────── */
header {
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 0 var(--space-xl, 20px);
  position: sticky;
  top: 0;
  z-index: 20;
  height: 44px;
  display: flex;
  align-items: center;
}
header .header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
header h1 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}
/* Supprimé : header .meta et header .legend (intégrés ailleurs) */

/* ─────────────────────────────────────────────────
   BADGE STATUT — inline dans le header, côté droit
   ───────────────────────────────────────────────── */
.header-status {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}
.header-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--status-dot, #f59e0b);
  flex-shrink: 0;
}
.header-status-text {
  font-size: 11px;
  font-weight: 500;
  color: var(--status-text, #64748b);
  white-space: nowrap;
}
/* Sur très petit écran : masquer le texte "08/08", garder le dot */
@media (max-width: 380px) {
  .header-status-date { display: none; }
}

/* ─────────────────────────────────────────────────
   LÉGENDE DIRECTIONNELLE — défile avec le contenu
   (non-sticky — info consultée 1 fois, pas besoin permanent)
   ───────────────────────────────────────────────── */
.legend-bar {
  position: static;                   /* défile — plus de position sticky */
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 8px var(--space-xl, 20px);
  font-size: 12.5px;
  line-height: 1.5;
  color: var(--text-muted);
}
.legend-bar .legend-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
  align-items: center;
}
.legend-bar code {
  background: var(--code-bg);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 11px;
}

/* ─────────────────────────────────────────────────
   SOUS-NAVIGATION — seule zone sticky sous le header
   ───────────────────────────────────────────────── */
.subnav {
  position: sticky;
  top: 44px;                          /* colle juste sous le header (44px) */
  z-index: 4;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border);
  padding: 6px var(--space-xl, 20px);
  font-size: 13px;
}
.subnav .subnav-inner {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-wrap: nowrap;
  gap: 4px;
  align-items: center;
  overflow-x: auto;
  scrollbar-width: none;              /* Firefox */
}
.subnav .subnav-inner::-webkit-scrollbar { display: none; }
.subnav a {
  color: var(--accent);
  text-decoration: none;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--accent-bg);
  font-size: 12px;
  border: 1px solid transparent;
  white-space: nowrap;
  flex-shrink: 0;
}
.subnav a:hover {
  border-color: var(--accent);
}
.subnav a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
.subnav .subnav-label {
  color: var(--text-muted);
  font-size: 11px;
  margin-right: 4px;
  flex-shrink: 0;
}

/* ─────────────────────────────────────────────────
   SUPPRIMÉ : .context-banner et .context-inner
   Le contenu "Mode test" est maintenant inline
   dans .header-status (voir HTML ci-dessous)
   ───────────────────────────────────────────────── */
/* Note : supprimer les règles .context-banner et .context-inner existantes */
```

### HTML cible — remplace L874-932

```html
<header>
  <div class="header-row">
    <button class="hamburger" id="hamburger"
            aria-label="Ouvrir la liste des bulletins"
            aria-expanded="false">☰</button>
    <h1>TradingApp v3 — Bulletins</h1>
    <div class="header-status" role="status" aria-label="Statut : mode test">
      <span class="header-status-dot" aria-hidden="true"></span>
      <span class="header-status-text">Mode test
        <span class="header-status-date">· go-live 08/08</span>
      </span>
    </div>
  </div>
</header>
<!-- Overlay sidebar mobile -->
<div class="sidebar-overlay" id="sidebar-overlay"></div>
<div class="layout">
  <aside id="sidebar">
    <!-- ... sidebar inchangée ... -->
  </aside>
  <main id="bulletin-main">
    <!-- Légende directionnelle : défile avec le contenu -->
    <div class="legend-bar" id="legend-bar">
      <div class="legend-inner">
        <span><span class="dir-long">🟢 LONG</span> = hausse</span>
        <span>·</span>
        <span><span class="dir-short">🔴 SHORT</span> = baisse</span>
        <span>·</span>
        <span>⚪ non-actionnable</span>
        <span>·</span>
        <span>📰 news&gt;50%</span>
        <span>·</span>
        <span>⚑ gate · ⚠ contesté · 🟡 vigilance</span>
      </div>
    </div>
    <!-- Sous-navigation sticky (seul chrome permanent sous le header) -->
    <nav class="subnav" id="subnav" aria-label="Sections du bulletin">
      <div class="subnav-inner">
        <span class="subnav-label">Sauter à :</span>
        <span id="subnav-links"></span>
      </div>
    </nav>
    <div class="content-inner">
      <!-- ... contenu inchangé ... -->
    </div>
  </main>
</div>
```

---

## (d) Hiérarchie de stickiness

| Zone | Comportement | Hauteur | Justification |
|---|---|---|---|
| `<header>` | **sticky top:0** | 44px | L'identité de l'app et le statut "mode test" doivent rester visibles en permanence. 44px = touch target minimum iOS |
| `.legend-bar` | **défile** (static) | ~40px | Légende consultée une fois par session, pas besoin de chrome permanent. Le `.help-box` replié dans le contenu en reprend le détail |
| `.subnav` | **sticky top:44px** | 38px | Navigation intra-bulletin utile pendant la lecture. Colle juste sous le header sans conflit |
| `.context-banner` | **supprimé** | 0px | Absorbé dans `.header-status` inline — même info, 0 ligne supplémentaire |

**Chrome sticky total : 44 + 38 = 82px** (desktop et mobile)

*Pour mémoire : scroll-margin-top des ancres `h2` doit être mis à jour : `scroll-margin-top: 90px` (actuellement 100px — valeur désormais légèrement trop haute).*

---

## (e) Traitement visuel du bandeau "Mode test" — version discrète

### Principe

L'information "Mode test · go-live 08/08" est un **statut de fond**, pas une alerte. Elle doit être présente mais ne doit pas capter l'attention. Actuellement le bandeau bleu `--accent-bg` (#1e3a5f) est trop visible.

### Solution retenue : badge inline dans le header, côté droit

- **Point ambre `•`** (6px, `--status-dot: #f59e0b`) : signale un état "en cours" sans connotation d'erreur ou de succès
- **Texte 11px / `--status-text: #64748b`** : un cran plus sombre que `--text-muted`, quasi-invisible sans effort de lecture
- **Pas de fond coloré, pas de bordure** : s'intègre dans la ligne du header sans créer une zone visuelle séparée
- **Le label s'abrège sur très petit écran** : "Mode test" seulement (sans "· go-live 08/08") sous 380px

### Contraste WCAG

- `--status-text` (#64748b) sur `--bg-panel` (#1e293b) → ratio ~3,9:1
- Acceptable pour un texte de statut non-critique (niveau WCAG AA large text ou composant décoratif)
- Si Thomas estime qu'il doit être légèrement plus lisible : `--status-text: #718096` → ratio ~4,6:1 (passe AA)

---

## (f) Responsive

### Desktop ≥ 768px

```
Header : height 44px, padding 0 20px
  [ ☰ ] [ TradingApp v3 — Bulletins ─────────────── ] [ ● Mode test · go-live 08/08 ]

Legend-bar : padding 8px 20px, défile
Subnav : sticky top:44px, padding 6px 20px, pilules overflow-x:auto
```

### Mobile < 768px

```css
@media (max-width: 768px) {
  header {
    height: 40px;
    padding: 0 12px;
  }
  header h1 {
    font-size: 14px;
  }
  .header-status-text {
    font-size: 10px;
  }
  .legend-bar {
    padding: 6px 12px;
    font-size: 12px;
  }
  .subnav {
    top: 40px;        /* aligné sur la hauteur mobile du header */
    padding: 5px 12px;
  }
  .subnav a {
    font-size: 11.5px;
    padding: 3px 8px;
  }
  /* Masque la légende verbose sur très petit écran */
  .legend-bar .legend-inner span:nth-child(n+9) {
    display: none;   /* garde LONG/SHORT/⚪/📰, masque les derniers séparateurs */
  }
}
```

**`scroll-margin-top` des ancres h2/h3 sur mobile : `scroll-margin-top: 84px`** (header 40 + subnav 38 + 6px de respiration).

### Focus visible (accessibilité WCAG 2.2 AA)

Tous les éléments interactifs dans le header ont un focus-visible explicite :

```css
.hamburger:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
.subnav a:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
```

Le `.header-status` est un `div[role="status"]` non-interactif — pas de focus nécessaire.

---

## (g) Instructions d'implémentation ordonnées pour @fullstack

### Ordre d'intervention (ancres dans build_html.py)

**Étape 1 — Tokens CSS nouveaux (dans `:root`, L400-415)**

Ajouter dans le bloc `:root` existant, après `--dir-short-color` :

```python
# À ajouter dans la f-string CSS, dans le bloc :root, après --dir-short-color
"""      --status-bg:     #0f1c2e;
      --status-border:  #1d3045;
      --status-text:    #64748b;
      --status-dot:     #f59e0b;
      --header-divider: #253348;"""
```

**Étape 2 — Remplacement du bloc CSS `header` (L427-438)**

Remplacer les règles `header {`, `header .header-row`, `header h1`, `header .meta`, `header .meta-note`, `header .legend`, `header .legend code` par le CSS de la section (c) ci-dessus.

**Étape 3 — Remplacement du bloc `.context-banner` / `.context-inner` (chercher `.context-banner`)**

Supprimer entièrement ces deux règles (le bandeau disparaît du DOM, remplacé par `.header-status`).

**Étape 4 — Mise à jour du bloc `.legend-bar` (L513-526)**

Remplacer par le CSS `.legend-bar` de la section (c). Vérifier que `position: static` est bien présent (vs l'éventuelle valeur `sticky` si réintroduite).

**Étape 5 — Mise à jour du bloc `.subnav` (L527-550)**

Remplacer par le CSS `.subnav` de la section (c). Point clé : `top: 44px` (desktop) et `top: 40px` (mobile via `@media`).

**Étape 6 — Ajouter les règles `.header-status`, `.header-status-dot`, `.header-status-text` (après `.hamburger`)**

Insérer le bloc CSS `.header-status*` de la section (c).

**Étape 7 — Mise à jour du bloc `@media (max-width: 768px)` (L830-870)**

- Remplacer `header h1 {{ font-size: 15.5px; }}` → `font-size: 14px`
- Remplacer `.layout {{ height: calc(100vh - 86px); }}` → `calc(100vh - 40px)` (header 40px, plus de context-banner)
- Ajouter `.subnav {{ top: 40px; }}`
- Supprimer `.legend-bar {{ padding: 8px 12px; font-size: 12px; }}` et remplacer par la version responsive de la section (f)

**Étape 8 — Mise à jour du HTML header (L874-894)**

Remplacer les lignes L874-894 (header + context-banner) par le HTML cible de la section (c).

**Étape 9 — Supprimer la variable Python `generated_at` du HTML header**

La ligne `<div class="meta">Généré : {generated_at}{truncated_note}</div>` est supprimée du header. Si cette information doit subsister, la déplacer dans le pied de page `.debug-meta` (L592-598) ou dans un `<details>` discret.

**Étape 10 — Mise à jour des `scroll-margin-top`**

```python
# L553-554, remplacer :
# main h2 {{ ... scroll-margin-top: 100px; }}
# main h3 {{ ... scroll-margin-top: 100px; }}
# par :
# main h2 {{ ... scroll-margin-top: 90px; }}
# main h3 {{ ... scroll-margin-top: 90px; }}
# Et dans @media mobile :
# main h2 {{ scroll-margin-top: 84px; }}
# main h3 {{ scroll-margin-top: 84px; }}
```

**Étape 11 — Vérification de la hauteur `.layout`**

```python
# La hauteur du layout doit exclure seulement le header sticky (44px desktop)
# car la legend-bar défile désormais.
# .layout {{ height: calc(100vh - 44px); }}   ← desktop
# Mobile : calc(100vh - 40px)
```

### Checklist de validation post-implémentation

- [ ] Le chrome sticky sur desktop fait bien 44+38 = 82px (mesurer avec DevTools)
- [ ] Le chrome sticky sur mobile fait bien 40+38 = 78px
- [ ] Le badge "Mode test" est visible mais ne capte pas le regard au premier coup d'oeil
- [ ] La legend-bar défile et disparaît au scroll (ne colle plus)
- [ ] Les ancres subnav scrollent au bon endroit (scroll-margin-top respecté)
- [ ] Contraste "Mode test" text ≥ 3,9:1 (outil : WebAIM contrast checker)
- [ ] Focus visible sur hamburger et pilules subnav (Tab keyboard test)
- [ ] Sur mobile 375px : h1 lisible, status badge visible, subnav scrollable horizontalement

---

## Auto-évaluation — est-ce vraiment épuré, simple, agréable ?

**Épuré** : oui. Une seule ligne de header (44px). Le bandeau contexte disparaît du DOM. La legend défile. La subnav reste seule à coller. −60% de chrome permanent vs l'actuel.

**Simple** : oui. Le badge de statut est 3 mots + 1 date. Aucun élément décoratif ajouté. Aucune animation. Aucune ombre supplémentaire. La hiérarchie visuelle est lisible au premier coup d'oeil : titre → statut → contenu.

**Agréable** : oui, sous réserve d'implémentation propre. Le point ambre `•` sur fond panel sombre crée une signature discrète sans être agressif. La palette slate existante est conservée — elle est déjà bonne. La subnav avec `overflow-x: auto + scrollbar: none` sur mobile est le pattern attendu pour ce type d'interface.

**Note cible estimée après implémentation : 8/10**

Ce qui manque pour 9-10/10 (hors scope de cette spec, nécessite décision @ux sur le contenu) :
- Réorganisation de la sidebar (vues + bulletins = 2 groupes distincts, aujourd'hui mélangés)
- Traitement visuel de la "Sélection du jour" en tête de bulletin (accent visuel fort = 1 action primaire par vue)

---

**Handoff → @fullstack**

- Fichier produit : `/home/user/TradingApp/docs/design/refonte-header-page-s9.md`
- Décisions prises :
  - Header réduit à 44px ligne unique (titre + badge statut inline)
  - `.context-banner` supprimé, info intégrée dans `.header-status` côté droit
  - `.legend-bar` rendue non-sticky (défile avec le contenu)
  - `.subnav` reste sticky à `top:44px` (desktop) / `top:40px` (mobile)
  - 4 nouveaux tokens : `--status-bg`, `--status-border`, `--status-text`, `--status-dot`
  - Badge statut : point ambre 6px + texte 11px `--status-text`
- Points d'attention :
  - `scroll-margin-top` des ancres h2/h3 à mettre à jour (90px desktop, 84px mobile)
  - `.layout height` à recalculer (header seul : 44px desktop, 40px mobile)
  - La variable Python `generated_at` n'est plus dans le header HTML — à déplacer si besoin dans `.debug-meta`
  - Focus-visible explicite à ajouter sur `.hamburger` et `.subnav a` (WCAG 2.2 AA)
  - Ancres L à cibler : L400-415 (tokens), L427-438 (header CSS), `.context-banner` (Grep), L513-526 (legend-bar), L527-550 (subnav), L830-870 (media query mobile), L874-894 (HTML header)
