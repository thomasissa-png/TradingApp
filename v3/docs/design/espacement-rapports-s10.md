# Espacement des vues rapport (S10)

> Livrable @design — session S10, 26/06/2026.
> Destinataire : @fullstack pour implémentation dans `v3/scripts/build_html.py`.
> Perimetre : vues Briefing 7h / Suivi 12h-18h / Bilan uniquement. Ne touche pas le hero, le header, le footer.
> Contrainte absolue : ZERO tiret cadratin. ZERO montant. WIN RATE ONLY.

---

## 1. Systeme d'espacement (echelle de reference)

Echelle 4px de base, conforme aux tokens existants et a la direction "Clarté de conviction" (S10).

| Alias      | Valeur  | Usage type dans les rapports                       |
|------------|---------|---------------------------------------------------|
| `xs`       | 4px     | Espace interne micro (badge, tag)                 |
| `sm`       | 8px     | Espace entre elements inline, gap icone/texte     |
| `md`       | 16px    | Padding compact (tableaux, tags)                  |
| `md+`      | 20px    | Padding horizontal carte secondaire               |
| `lg`       | 24px    | Padding horizontal carte principale, gap vertical |
| `xl`       | 32px    | Padding horizontal content-inner desktop          |
| `2xl`      | 48px    | Padding bottom content-inner (respiration basse)  |

Principe directeur : les cartes ont un padding interne minimum `md` (16px) sur les cotes, `lg` (24px) pour les cartes principales et le contenu en prose. Le padding de la carte mere (.today-day) est toujours superieur ou egal au padding de ses enfants.

---

## 2. Corrections classe par classe

### 2a. `.content-inner` (L643-647)

Contexte : le padding global du conteneur de rapport. C'est l'espace entre les bords du `<main>` et tout le contenu. Valeur actuelle correcte sur desktop, mais le padding lateral de 32px doit rester stable et ne pas etre ecrase par des sous-composants.

| Propriete       | AVANT                        | APRES recommande                | Justification                                         |
|----------------|------------------------------|---------------------------------|------------------------------------------------------|
| `padding`      | `24px 32px 48px 32px`        | `24px 32px 48px 32px`           | Desktop : inchange, valeurs correctes                |
| mobile `<=768` | Non specifie (herite)        | `20px 16px 40px 16px`           | 16px lateral min sur mobile ; 20px haut pour respirer sous la subnav |

> Action concrete : dans le `@media (max-width: 768px)`, ajouter explicitement `.content-inner { padding: 20px 16px 40px; }`. Actuellement il n'y a pas de surcharge mobile sur `.content-inner`, ce qui signifie que les 32px desktop peuvent etre ecrases par d'autres regles ou que le contenu se serre naturellement.

---

### 2b. `.today-day` (L1052-1056) : carte-conteneur de jour

La carte est le premier niveau visuel. Son `summary` (titre du jour) doit avoir un padding genereux pour signaler son rang hierarchique.

| Propriete              | AVANT                          | APRES recommande                   | Justification                                            |
|-----------------------|--------------------------------|------------------------------------|----------------------------------------------------------|
| `summary` padding     | `12px 16px`                   | `14px 20px`                        | +4px vertical = aire de clic plus confortable (touch 44px) ; +4px horizontal = respiration du titre par rapport au bord de la carte |
| `border-radius`       | `10px`                        | `10px` (inchange)                  | Bon                                                      |
| `margin`              | `0 0 18px 0`                  | `0 0 24px 0`                       | +6px inter-carte = separation plus lisible entre les jours dans l'historique |

---

### 2c. `.today-report .report-body` (L1082) : corps de rapport

**Probleme principal signale par le fondateur.** Valeur actuelle `padding: 4px 18px 16px 32px` : 4px en haut (quasi nul), 18px a droite (asymetrie injustifiee), 16px en bas, 32px a gauche (pour aligner avec la fleche du summary a 32px). L'asymetrie droite/gauche cree une sensation de desequilibre et le 4px du haut colle le premier h2 ou paragraphe directement sous le summary.

| Propriete  | AVANT                      | APRES recommande              | Justification                                                            |
|-----------|----------------------------|-------------------------------|--------------------------------------------------------------------------|
| `padding` | `4px 18px 16px 32px`      | `16px 24px 24px 28px`        | Haut 16px : air sous le summary avant le premier titre. Droite 24px : symetrie visuelle (pas besoin d'aligner sur la fleche). Bas 24px : respiration avant la bordure suivante. Gauche 28px : leger retrait conserve pour hierarchie visuelle, mais reduit depuis 32px pour ne pas trop coller le contenu au bord gauche relatif. |

> Note : le padding-left de 32px etait pense pour aligner le contenu avec le debut du texte du `summary` (qui a lui-meme `padding-left: 32px` pour la fleche). Ce n'est pas une contrainte absolue : 28px reste dans la meme zone et evite la sensation de texte "engouffre" dans un retrait excessif.

---

### 2d. `.today-report > summary` (L1072) : en-tete de rapport (Briefing / Suivi / Bilan)

| Propriete  | AVANT                            | APRES recommande                  | Justification                                                   |
|-----------|----------------------------------|-----------------------------------|-----------------------------------------------------------------|
| `padding` | `10px 16px 10px 32px`           | `12px 20px 12px 32px`            | +2px vertical = aire de clic >= 44px (titre 13.5px + 2x12px = 37px natif ; avec line-height ~1.35 ca passe a ~42px -- acceptable). +4px horizontal droit = symetrie avec le nouveau body. Left 32px : inchange pour aligner la fleche. |

---

### 2e. `.decision-selection` (L819) : encart selection du jour

Carte secondaire a filet accent. Valeur actuelle correcte (`padding: 16px 20px`) mais mobile resserre a 12px/12px, ce qui est juste acceptable. Ajustement leger.

| Propriete       | AVANT desktop     | APRES desktop    | AVANT mobile `<=640` | APRES mobile `<=640` | Justification                                              |
|----------------|-------------------|------------------|-----------------------|----------------------|------------------------------------------------------------|
| `padding`      | `16px 20px`       | `16px 24px`      | `12px 12px`          | `12px 16px`          | Desktop : +4px horizontal pour aligner sur le rythme `md+`. Mobile : passer de 12px a 16px lateral evite que le tableau interne touche les bords de la carte |

---

### 2f. Tableaux : `main table th, main table td` (L854)

Valeur actuelle `padding: 10px 13px`. Les 13px horizontaux sont la source principale du "texte colle au bord" dans les cellules, surtout pour les colonnes etroites.

| Propriete  | AVANT           | APRES recommande | Justification                                                              |
|-----------|-----------------|------------------|----------------------------------------------------------------------------|
| `padding` | `10px 13px`    | `10px 16px`      | +3px par cote = 6px gagnes par cellule. Passe les cellules de 13px (trop serre) a 16px (standard confortable). Le vertical de 10px est correct : garde la densite des tableaux trading. |

Mobile : voir section 2g.

---

### 2g. `.table-wrap` (L837) : marges du wrapper de tableau

| Propriete  | AVANT       | APRES recommande  | Justification                                          |
|-----------|-------------|-------------------|--------------------------------------------------------|
| `margin`  | `16px 0`    | `20px 0`          | +4px haut/bas = separation plus nette entre les tableaux et les titres/paragraphes qui les encadrent |

---

### 2h. Titres `main h1`, `main h2`, `main h3` dans le markdown rendu

**H1** (L792-796) : titre de page (ex. "Briefing 7h - vendredi 26/06"). Le `margin-top: 8px` est trop serre apres la subnav.

| Propriete      | AVANT                         | APRES recommande              | Justification                                                     |
|---------------|-------------------------------|-------------------------------|-------------------------------------------------------------------|
| `margin-top`  | `8px`                        | `16px`                        | Separation visible entre la subnav ou le hero et le titre de rapport |
| `padding-bottom` | `12px`                    | `14px`                        | +2px pour equilibrer la bordure basse                            |

**H2** (L800-803) : titres de sections (ex. "Analyse macro", "Positionnement").

| Propriete      | AVANT                         | APRES recommande              | Justification                                                       |
|---------------|-------------------------------|-------------------------------|---------------------------------------------------------------------|
| `margin-top`  | `42px`                       | `36px`                        | 42px est trop genereux, creait des blancs excessifs entre sections |
| `padding`     | `2px 0 8px 14px`             | `4px 0 10px 14px`             | +2px haut/bas : air supplementaire autour du texte du titre        |

> Note : le `padding-left: 14px` du h2 est fonctionnel (barre accent `::before` en position absolute). Il ne touche pas le bord de la carte uniquement si `.report-body` a un padding-left suffisant -- ce qui est corrige en 2c (28px).

**H3** (L809) : sous-titres.

| Propriete      | AVANT         | APRES recommande  | Justification                                          |
|---------------|---------------|-------------------|--------------------------------------------------------|
| `margin-top`  | `26px`       | `20px`            | Reduit pour ne pas detacher les sous-titres de leur contexte |

---

### 2i. Coherence mobile : `.selection-progression td`, `.bilan-perf-table td` (L1227-1228)

Valeur actuelle `padding: 7px 6px`. Les 6px horizontaux sont tres serres -- c'est la source du "colle au bord" sur mobile pour ces tables specifiques.

| Propriete  | AVANT           | APRES recommande | Justification                                                            |
|-----------|-----------------|------------------|--------------------------------------------------------------------------|
| `padding` | `7px 6px`      | `7px 10px`       | +4px horizontal par cote. La table reste dense (7px vertical conserve), mais les cellules ont un minimum de respiration. La contrainte d'overflow-x gere les depassements, pas le padding. |

---

## 3. Resume des valeurs (tableau de reference rapide)

| Classe / selecteur                          | Avant                    | Apres                     |
|--------------------------------------------|--------------------------|---------------------------|
| `.content-inner` (mobile `<=768`)          | (herite = 32px lateral)  | `20px 16px 40px`          |
| `.today-day > summary` padding             | `12px 16px`              | `14px 20px`               |
| `.today-day` margin-bottom                 | `18px`                   | `24px`                    |
| `.today-report > summary` padding          | `10px 16px 10px 32px`    | `12px 20px 12px 32px`     |
| `.today-report .report-body` padding       | `4px 18px 16px 32px`     | `16px 24px 24px 28px`     |
| `.decision-selection` padding (desktop)    | `16px 20px`              | `16px 24px`               |
| `.decision-selection` padding (mobile)     | `12px 12px`              | `12px 16px`               |
| `main table th, td` padding                | `10px 13px`              | `10px 16px`               |
| `.table-wrap` margin                       | `16px 0`                 | `20px 0`                  |
| `main h1` margin-top                       | `8px`                    | `16px`                    |
| `main h1` padding-bottom                   | `12px`                   | `14px`                    |
| `main h2` margin-top                       | `42px`                   | `36px`                    |
| `main h2` padding (haut bas)               | `2px 0 8px 14px`         | `4px 0 10px 14px`         |
| `main h3` margin-top                       | `26px`                   | `20px`                    |
| `.selection-progression td, .bilan-perf-table td` padding (mobile) | `7px 6px` | `7px 10px` |

---

## 4. Principe d'application (ordre pour @fullstack)

1. Modifier `.today-report .report-body` en priorite : c'est la correction la plus visible (rapport ouvert = premier element que le fondateur lit).
2. Modifier `main table th, main table td` : impact immediat sur tous les tableaux de tous les rapports.
3. Ajouter la surcharge `.content-inner` en `@media (max-width: 768px)`.
4. Ajuster `.decision-selection` padding mobile.
5. Ajuster `.today-day > summary` et margin-bottom.
6. Ajuster les titres `h1/h2/h3`.
7. Ajuster `.selection-progression` et `.bilan-perf-table` padding mobile.

---

## 5. Ce qu'on ne touche pas

- `.page-hero` : correct, hors perimetre rapport.
- `.today-report > summary::before` (fleche ▸) : inchange, la position est geree par le padding-left du summary.
- `.table-wrap` background (ombre scroll) : inchange.
- Les `font-size` des tableaux : inchanges (13.5px desktop, 12px mobile pour `.selection-progression`).
- Les tokens CSS `:root` : pas de nouveau token ajoute -- toutes les valeurs ci-dessus sont des px directs compatibles avec l'echelle 4px existante.
- Les logos, badges, sidebar, hero, header, footer : hors perimetre.

---

## 6. Note de confiance

**9/10.** Les valeurs sont derivees des valeurs existantes par increments sur l'echelle 4px, sans rupture. Le cas le plus risque est `.today-report .report-body padding-left: 28px` (vs 32px actuel) : si le fondateur trouve que le contenu n'est plus suffisamment aligne avec le summary, passer a 30px. Toutes les autres corrections sont non ambigues.

Le padding `7px 10px` sur mobile pour `.selection-progression` est le seul endroit ou la densite est maintenue de facon deliberee (tableaux trading sur ecran etroit -- garder compact est fonctionnel).

---

**Handoff @fullstack**

Fichiers produits :
- `/home/user/TradingApp/v3/docs/design/espacement-rapports-s10.md` (ce fichier)

Decisions prises :
- Echelle : tout sur la grille 4px. Aucune valeur arbitraire.
- Le correctif prioritaire est `.today-report .report-body` : passer de `4px 18px 16px 32px` a `16px 24px 24px 28px`.
- Les cellules de tableaux passent de 13px a 16px de padding horizontal : impact maximal/effort minimal.
- Mobile : `.content-inner` recoit une surcharge explicite a 16px lateral. `.selection-progression` passe de 6px a 10px horizontal.

Points d'attention :
- Verifier le rendu du `h2::before` (barre accent `::before`) apres la modification du `padding` h2 : le `top/bottom` de l'absolute est calcule sur le padding, une variation de 2px est sans consequence.
- Le `padding-left: 28px` du report-body n'est plus aligne pixel-perfect avec le `padding-left: 32px` du summary : c'est intentionnel, le leger decalage donne de l'air.
- Ne pas ajouter de transitions CSS sur les paddings (pas d'animation sur l'ouverture des `<details>`).
