# Audit visuel & design — Tous types de rapports
**TradingApp v3 · Round 1 · 2026-06-12**
Auditeur : @ux · Grille reproductible — chaque point perdu = citation + fix + localisation.

---

## 1. Tableau de notes

| Type de rapport | Hiérarchie /10 | Scannabilité /10 | Propreté /10 | Langage /10 | Charge /10 | **Moyenne** |
|---|---|---|---|---|---|---|
| Briefing 7h | 7 | 6 | 6 | 7 | 5 | **6,2** |
| Suivi 12h | 8 | 8 | 7 | 8 | 7 | **7,6** |
| Suivi 18h | 8 | 8 | 7 | 8 | 7 | **7,6** |
| Bilan du jour | 7 | 7 | 7 | 8 | 6 | **7,0** |
| Bilan semaine | — | — | — | — | — | **N/A (vide)** |
| Vue Résultats (performance.md) | 7 | 6 | 7 | 7 | 6 | **6,6** |
| Chrome page (build_html.py) | 7 | 6 | 7 | 6 | 5 | **6,2** |

**Note globale pondérée** (Briefing ×3, Bilan jour ×2, le reste ×1) :
`(6,2×3 + 7,6 + 7,6 + 7,0×2 + 6,6 + 6,2) / 10 = 6,54 / 10`

---

## 2. Constats par rapport

### 2.1 Briefing 7h (`bulletin-2026-06-12-07h.md`)

**Question clé du matin : « Je joue quoi aujourd'hui ? »**

#### Hiérarchie — 7/10 (−3)

**[H-B1]** La section `## 🎯 À jouer aujourd'hui (24h)` est bien en tête — PASS. Mais le tableau « Jouables » liste **11 lignes** sans hiérarchie visuelle entre les convictions fortes et les convictions fragiles. L'œil n'est pas guidé : Or SHORT -13.30 (forte) voisine Cacao SHORT -1.30 (forte avec 4 drapeaux) dans le même bloc sans séparation.
Fix : diviser « Jouables » en 2 sous-groupes — `Forte / sans drapeau` et `Forte / avec drapeau(s)`. Une ligne de séparation suffit.
Localisation : `scoring_analyste.py`, génération section `À jouer`.

**[H-B2]** Le bloc `## 🎯 Top convictions multi-horizons` arrive en 2e position — logique. Mais il présente 3 convictions **toutes SHORT** sans indiquer si elles sont indépendantes des 11 lignes du tableau principal. Le lien entre les deux sections n'est pas explicite.
Fix : ajouter une note d'intro : « _Ces 3 convictions sont les plus fortes tous horizons — elles peuvent recouper les lignes ci-dessus._ »
Localisation : `scoring_analyste.py`.

#### Scannabilité — 6/10 (−4)

**[S-B1]** En 10 secondes, Thomas ne peut pas répondre à « je joue quoi ? ». La `Sélection du jour` manque : le bloc `🎯 Sélection du jour — max 3` prévu dans le spec S7 (décision fondateur 12/06) **n'apparaît pas dans ce bulletin**. C'est le P0 de scannabilité.
Fix : vérifier que `scoring_analyste.py` génère le bloc Sélection en tête du bulletin (avant « À jouer »). Si la sélection est vide (`ne pas forcer`), le dire explicitement en 1 ligne.
Localisation : `scoring_analyste.py`, bloc Sélection du jour.

**[S-B2]** La légende des symboles est **en bas de la section Synthèse** (ligne 67-81 du bulletin), après deux gros tableaux. Un lecteur 5e-de-la-journée qui voit `⇄` ou `↯` dans le premier tableau n'a pas le réflexe de descendre chercher la légende.
Fix : réduire la légende inline dans le titre de section ou ajouter un tooltip dans le chrome HTML (légende permanente dans la subnav est déjà en place — voir chrome, mais elle est incomplète).
Localisation : `scoring_analyste.py` (markdown) + `build_html.py` (légende-bar).

**[S-B3]** Le tableau `Synthèse des décisions` (12 lignes × 4 colonnes) est redondant avec le tableau `À jouer`. Les mêmes actifs et directions apparaissent deux fois dans les 50 premières lignes du bulletin. À 7h du matin, Thomas a déjà lu l'info avant d'arriver à la Synthèse.
Fix (voir aussi Charge, C-B1) : replier la Synthèse dans un `<details>` par défaut sur la page HTML — elle devient du drill-down, pas de l'intro.
Localisation : `build_html.py`, transform post-markdown.

#### Propreté — 6/10 (−4)

**[P-B1]** Double notation du score dans le tableau `Synthèse des décisions` : certaines cellules affichent `SHORT -6.64 (brut SHORT -8.24)` avec le mot `SHORT` répété deux fois dans la même cellule. Exemple : `SHORT -6.64 (brut SHORT -8.24) ⚑ 📰 ⇄ ⌛`. C'est verbeux et difficile à parser visuellement.
Fix : `SHORT -6.64 (brut -8.24)` — supprimer la répétition du mot `SHORT` dans la parenthèse.
Localisation : `scoring_analyste.py`, rendu de la colonne notes.

**[P-B2]** Les colonnes `Effet 24h / Effet 7j / Effet 1m` dans le tableau `Détail par actif` affichent des valeurs comme `+0.000`, `-0.000`, `+0.000` pour les critères à direction news = 0. Ces zéros pollués encombrent le tableau et donnent une impression de bruit technique.
Fix : afficher `—` quand la valeur est exactement 0.000 (ou sous un seuil de 0.001).
Localisation : `scoring_analyste.py`, rendu du tableau détail.

**[P-B3]** Le titre `Drapeau : événement de marché majeur imminent` (ligne `Drapeau régime`) apparaît dans **chaque tableau actif** comme une ligne de critère à part entière. Il en résulte que le tableau Détail pour Or, Nasdaq, VIX, CAC, Cuivre, EUR/USD, etc., a toutes sa dernière ligne occupée par cette ligne identique — 10 occurrences du même libellé. C'est du bruit répété.
Fix : ne pas afficher la ligne `Drapeau régime ⚑` dans le tableau quand sa valeur = 0 (gate inactif). Quand le gate est actif (valeur = 1), la maintenir mais la repositionner en tête du tableau avec une mise en valeur visuelle (fond coloré, pas juste une ligne comme les autres).
Localisation : `scoring_analyste.py`, filtre lignes tableau détail.

**[P-B4]** La section `## Limites du jour` liste les n/a avec le format verbeux : `n/a : Météo Côte d'Ivoire + Ghana (pluies, 30 jours) (poids 11) — n/a (valeur absente)`. La parenthèse `(valeur absente)` est redondante avec le préfixe `n/a :`.
Fix : `n/a : Météo Côte d'Ivoire + Ghana (poids 11)` — supprimer la redondance finale.
Localisation : `scoring_analyste.py`, rendu section Limites.

#### Langage — 7/10 (−3)

**[L-B1]** Dans le tableau Synthèse, la colonne contient des libellés comme `LONG (+0.23) ⚑ ≈` sans aucune traduction du ≈. La légende en bas explique ≈ mais la Synthèse est lue avant la légende. Le lecteur matin voit ≈ sans comprendre.
Fix : déjà en partie couvert par le libellé `Conviction` dans le tableau `À jouer` (« molle (score faible) »). Mais dans la Synthèse pure, ajouter le libellé conviction entre parenthèses pour les cas ≈ et ◧ : `LONG (+0.23) ≈ molle`.
Localisation : `scoring_analyste.py`.

**[L-B2]** La phrase d'intro de la Sélection du jour utilise une formulation technique : _« conviction forte + couverture ≥0,70 + un pari par driver »_. Si Thomas lit cette ligne à 7h, le terme « couverture ≥0,70 » ne lui parle pas.
Fix : reformuler en trader : _« Signal fort, données suffisantes, et chaque type de marché représenté une seule fois. »_
Localisation : `scoring_analyste.py` ou template du bloc Sélection.

**[L-B3]** Le pied du bulletin indique `Analyste version : v3.0.0 · Fiches hash : f58368a91305`. C'est de la métadonnée technique sans valeur pour Thomas à 7h.
Fix : déjà partiellement géré via `<details class="debug-meta">` dans le chrome HTML. S'assurer que ce contenu est dans le bloc replié et pas en texte brut dans le markdown.
Localisation : `build_html.py`, transform metadata.

#### Charge — 5/10 (−5)

**[C-B1]** Le bulletin complet fait **plus de 400 lignes markdown**. Les sections principales pour la décision matin sont les 35 premières lignes (`À jouer` + `Top convictions`). Les 365 lignes restantes (Synthèse, Détail par actif 12×, Limites, Calls jugés) sont du drill-down. Un seul niveau de scroll suffit pour trouver l'info clé — mais sur mobile, c'est 4 pages de scroll avant d'atteindre le Détail.
Fix global : dans le rendu HTML, replier automatiquement (via `<details>`) les sections `Détail par actif` (chaque actif), `Limites du jour`, et `Flips vs veille`. La section `Synthèse des décisions` elle-même est borderline — voir fix S-B3.
Localisation : `build_html.py`, transforms post-markdown.

**[C-B2]** La section `## ⚠️ Cellules à surveiller` liste **16 lignes** — presque autant d'actifs que le bulletin entier. Un lecteur rationnel interprète « cellules à surveiller » comme une liste courte de cas critiques. Avec 16 entrées sur 36 cellules, c'est 44% du bulletin qui est en surveillance — la valeur signal est diluée.
Fix : pas de modification du critère de sélection (hors périmètre), mais réduire la visibilité : replier cette section dans un `<details>` par défaut (elle est déjà identifiée dans le code comme section à fold, vérifier que le fold est actif).
Localisation : `build_html.py`, déjà fold-section en principe — à vérifier si le fold est actif sur cette section.

**[C-B3]** La section `## 🔎 Calls 24h jugés` liste **31 entrées** avec la totalité des prédictions passées depuis le 2026-06-02. À 7h, Thomas cherche les résultats récents (J-1, J-2), pas l'intégralité de l'historique.
Fix : tronquer à 7 entrées max (≈ 1 semaine) dans le markdown affiché. L'historique complet est dans la vue Historique de la page.
Localisation : `scoring_analyste.py`, rendu section Calls jugés (paramètre `MAX_CALLS_DISPLAYED`).

**[C-B4]** Le bloc `⚭ Drivers macro partagés` indique : _« porte 2 cellule(s) SHORT sur 2 actif(s) (Nasdaq, Or) »_. La mention des actifs en prose est redondante avec le tableau `À jouer` qui affiche déjà l'icône ⚭ et le driver. Ce bloc double l'information sans l'enrichir.
Fix : reformuler en bullet unique et supprimer la reprise du tableau : _« ⚭ Taux réels US (TIPS) : Nasdaq et Or SHORT — un retournement les fausse ensemble. »_
Localisation : `scoring_analyste.py`, rendu bloc Drivers macro.

---

### 2.2 Suivi 12h (`2026-06-11-12h.md`)

**Question clé : « Je tiens ou je sors ? »**

#### Points forts
- Structure tableau unique, compacte : PASS.
- Note sur marchés US en haut (⚠️ pas encore ouvert) : PASS — empêche la confusion.
- `Tendance` colonne absente au 12h (remplacée par `—` partout) : UX correcte pour éviter un pseudo-signal sans baseline.
- Section Suggestions de sortie claire, 1 actif = 1 ligne.

#### Points perdus

**[H-S1]** — Hiérarchie 8/10. La colonne `Δ vs 7h` n'a que des `—` au 12h (normal — pas de snapshot précédent pour le 12h). Mais la colonne est présente et vide, ce qui crée du bruit visuel inutile.
Fix : au 12h, supprimer la colonne `Tendance` ET `Δ vs 7h` du tableau (elles sont vides). Remplacer par tableau à 7 colonnes : `Actif | Call 7h | Ouverture | Prix 12h | Delta% | Statut | Suggestion`.
Localisation : `run_suivi.py`, génération tableau 12h.

**[P-S1]** — Propreté 7/10. Incohérence entre les colonnes 12h et 18h : le 12h a `Δ vs 7h` (vide), le 18h a `Δ vs 12h` (rempli). Le libellé de colonne change entre les deux rapports. Un lecteur qui relit les deux rapports dans la même session voit des tableaux de structures différentes.
Fix : nommer uniformément `Δ précédent` ou introduire une colonne optionnelle rendue conditionnellement.
Localisation : `run_suivi.py`.

**[C-S1]** — Charge 7/10. La section `News à impact depuis 7h` reproduit mot pour mot les mêmes 3 news que le suivi 18h. Si Thomas lit les deux rapports, il lit deux fois la même info.
Note : ce comportement est probablement voulu (chaque rapport est autonome) mais il alourdit l'expérience de relecture.
Fix : pas de modification majeure, mais indiquer `(mêmes que ce matin)` si les news sont identiques entre 12h et 18h.
Localisation : `run_suivi.py`, logique news.

---

### 2.3 Suivi 18h (`2026-06-11-18h.md`)

**Question clé : « Je tiens ou je sors ? »**

#### Points forts
- Colonne `Tendance` remplie (↑ s'accélère / ↓ s'essouffle / ⇄ se retourne) : excellent signal visuel — PASS.
- Section Suggestions de sortie avec citation exacte du seuil : _« +1.02% contre le call (seuil 0.80%) »_ — très clair — PASS.
- Statuts ✅/⚠️ immédiats.

#### Points perdus

**[H-S2]** — Hiérarchie 8/10. Nasdaq, S&P 500 et VIX ont une ligne avec `—` partout sauf `Prix 18h`. L'œil accroche ces lignes incomplètes avant de comprendre qu'elles sont US. La note « pas encore ouvert » est au 12h, pas au 18h — au 18h, les marchés US sont ouverts depuis 15h30, donc les prix 18h sont disponibles mais le `Statut` est `—`. C'est confusant.
Fix : remplir le statut pour Nasdaq/S&P/VIX au 18h (ils sont ouverts) même si l'`Ouverture` est absente. Utiliser l'ouverture approchée (dernier prix connu) ou marquer explicitement `[réf approx]`. Si les données sont vraiment indisponibles, afficher `⏳ données manquantes` plutôt que `—`.
Localisation : `run_suivi.py`, logique statut actifs US au 18h.

**[P-S2]** — Propreté 7/10. La colonne `Δ vs 12h` affiche `+1.51pts` pour Cuivre. `pts` est ambigu : est-ce des points de pourcentage ? des points d'index ? Pour un actif côté à 6.2 USD, +1.51pts ne veut rien dire sans unité.
Fix : afficher `+1.51%pts` ou clarifier que `Δ vs 12h` est en points de pourcentage.
Localisation : `run_suivi.py`, formatage `Δ vs 12h`.

---

### 2.4 Bilan du jour (`2026-06-11.md`)

**Question clé du soir : « J'ai eu raison ? Pourquoi j'ai eu tort ? »**

#### Points forts
- Tableau résultats clair avec symboles ✅ ❌ ⚪ — PASS.
- Section `FAUX à forte amplitude` identifie les 6 erreurs avec ordre de magnitude — PASS.
- Section `News qui ont compté aujourd'hui` : explications causales en prose, excellentes — PASS.
- Catalyseurs J+1 avec dates et icônes d'impact — PASS.

#### Points perdus

**[H-BD1]** — Hiérarchie 7/10. Le titre `### Résultat des calls 7h` est suivi immédiatement d'un tableau à 7 colonnes. Thomas veut d'abord savoir : **1 contre 9** (score du jour) AVANT de voir le détail. Actuellement, le score `1/9 = 11%` est dans la section suivante (`Win rate du jour`), pas dans le titre de la section des résultats.
Fix : ajouter une ligne résumé EN TÊTE du tableau résultats : `**Résultat du 11/06 : 1 ✅ / 8 ❌ / 3 ⚪ — Win rate : 11%**`. Une ligne, avant le tableau.
Localisation : `bilan_jour.py`, rendu en-tête résultats.

**[H-BD2]** — Hiérarchie. La section `### Win rate du jour` présente 5 métriques :
- Paris conclusifs : 9 / 12
- Win rate du jour : 1/9 = 11%
- WR tradable du jour : 1/12 = 8%
- Win rate conviction forte (jour) : 11% (N=9)
- Win rate conviction faible (jour) : — (N=0)

Pour un soir de grosse défaite, Thomas a besoin de voir **le chiffre le plus important en premier** (1/9 = 11%), pas un entonnoir de 5 métriques. Les 3 dernières métriques sont du secondaire.
Fix : restructurer en 2 niveaux — primaire : `11% (1/9)` · secondaire replié : détail conviction forte/faible et WR tradable.
Localisation : `bilan_jour.py`.

**[P-BD1]** — Propreté 7/10. La ligne `FAUSSES aux retournements (shadow A5)` est précédée d'un bloc d'explication en italique sur 3 lignes : `_Cellules conclusives en situation de retournement (cap anti-inversion déclenché OU news opposées au quant hors-momentum). Métrique d'observabilité momentum v3 — DISTINCTE du win rate, sans impact décisionnel. WIN RATE ONLY._`. Cette explication est utile une fois — après, c'est du bruit.
Fix : réduire en 1 ligne : `_Métrique shadow momentum (ne change pas le WR) :_` et replier le reste dans un tooltip ou footnote.
Localisation : `bilan_jour.py`, rendu section FAUSSES retournements.

**[C-BD1]** — Charge 6/10. La section `### FAUX à forte amplitude` liste les 6 erreurs avec `→ À analyser dans le bilan semaine.` répété 6 fois. Ce bullet répété est du bruit — le lecteur a compris après la première occurrence.
Fix : ajouter le renvoi UNE SEULE FOIS, en bas de la liste : `_Ces erreurs seront analysées dans le bilan de semaine._`
Localisation : `bilan_jour.py`, rendu section FAUX amplitude.

**[C-BD2]** — Charge. Le bloc `### FAUSSES aux retournements (shadow A5)` présente une métrique dont l'utilité au lecteur soir est faible : c'est une métrique technique de calibration du moteur, pas un indicateur de trading. Dans un bilan de grosse défaite (11%), elle distrait de l'essentiel.
Fix (conservatoire) : replier cette section dans un `<details>` sur la page HTML, intitulé `Métriques techniques du moteur`.
Localisation : `build_html.py`, fold sur cette section.

---

### 2.5 Bilan semaine

Aucun fichier disponible (`v3/data/bilan-semaine/` ne contient que `.gitkeep`). Note : N/A — première semaine d'historique. L'audit reprendra dès qu'un fichier sera généré.

Cependant, d'après le code `run_weekly.py` documenté, des constats préventifs sont possibles :

**[P-BW1]** Le titre de la section sera généré automatiquement (`Semaine {YYYY}-S{XX}`). Le format ISO est correct techniquement mais peu lisible pour Thomas : `Semaine 2026-S24` vs `Semaine du 8 au 14 juin 2026`.
Fix : déjà prévu dans le chrome (`class="week-human-title"`) — vérifier que `build_html.py` le renseigne correctement avec les dates lundi-vendredi.
Localisation : `build_html.py`, fonction `week-human-title`.

---

### 2.6 Vue Résultats (`performance.md`)

**Question clé : « Est-ce que le système fonctionne ? »**

#### Points forts
- Tableau 24h / 7j / 1m bien séparé — PASS.
- Colonne `Statut` claire (⏳ / ✅ / ❌) — PASS.
- Explication en tête (WR / WR tradable / cible) — PASS.

#### Points perdus

**[H-R1]** — Hiérarchie 7/10. Le fichier commence par 9 lignes de métadonnées (`Généré :`, `Journaliste version :`, explication WR, WR tradable, cible, etc.) avant le premier tableau de données. Pour un lecteur qui consulte le win rate, ces 9 lignes sont du contexte, pas de l'info principale.
Fix : dans le rendu HTML (vue Résultats), afficher l'encart de contexte (`winrate-warmup`) en haut, puis le tableau directement. Les 9 lignes de métadonnées peuvent rester dans le markdown pour la pérennité mais leur présentation HTML doit les traiter comme du footer.
Localisation : `build_html.py`, rendu vue Résultats.

**[S-R1]** — Scannabilité 6/10. La ligne de synthèse `0 / 36 cellules fiables` est en **milieu** du fichier (après l'explication 9 lignes). C'est le chiffre le plus important — il devrait être en PREMIER.
Fix : remonter la ligne de synthèse en tête : `**Synthèse : 0 / 36 cellules fiables** (15 paris requis/cellule)`.
Localisation : `journaliste.py`, `render_performance`, ordre des sections.

**[P-R1]** — Propreté 7/10. Les colonnes `Win rate` et `WR tradable` affichent des valeurs `0.0%` pour 10 actifs sur 12 — le tableau est quasi entièrement des zéros. Un tableau de zéros à scannabilité nulle : le signal est noyé.
Fix : dans le rendu HTML, griser les lignes à N < 5 (trop peu pour être significatives) avec `.row-no-data`. Le code `build_html.py` a déjà la classe CSS `row-no-data` — vérifier qu'elle s'applique bien aux lignes N=1 de la vue win-rate.
Localisation : `build_html.py`, application `row-no-data` sur les tableaux markdown rendus.

**[P-R2]** — Propreté. La section `Flip vs continuation` en bas du fichier présente :
- `Win rate sur retournements : 33.3% (N=3)`
- `Win rate sur continuations : 0.0% (N=7)`
Sans contexte sur ce que ces chiffres signifient pour la décision de Thomas. À N=3/7, ces chiffres ne sont pas interprétables — l'afficher sans mise en garde crée une fausse impression.
Fix : ajouter `(N trop faible, non interprétable)` en italique. Ou replier dans `<details>` sur la page HTML.
Localisation : `journaliste.py`, `render_performance`, section Flip/continuation.

**[C-R1]** — Charge 6/10. Le fichier affiche 36 lignes de `— | — | 0 | 0 | ⏳ en attente` pour les horizons 7j et 1m. C'est 24 lignes de contenu vide qui dilue la vue.
Fix : dans le rendu HTML, masquer les lignes à `N=0` ET `Non notés=0` pour les horizons 7j et 1m. Un message unique : `_7j et 1m en attente de données (horizons longs — premiers résultats début juillet)_`.
Localisation : `build_html.py`, transform de la vue Résultats.

---

### 2.7 Chrome page (`build_html.py`)

**Bandeau, sidebar, subnav, folds, badges, grisage, styles tables, mobile.**

#### Points forts
- Dark mode automatique via `prefers-color-scheme` — PASS.
- Sidebar sticky avec vues nommées — PASS.
- Tables avec `overflow-x: auto` et classe `.dense-table` pour mobile — PASS.
- `.fold-section` et `.debug-meta` pour réduire la charge visuelle — PASS (mais partiellement utilisées, voir ci-dessous).
- Colorisation LONG/SHORT — PASS.
- Bandeau contexte permanent (`context-banner`) — PASS.

#### Points perdus

**[CH-1]** — Langage 6/10. La légende dans le header HTML (`<div class="legend">`) mentionne `⚠ divergence pm1/pondéré`. Le terme `pm1/pondéré` est du jargon système (A/B test interne). Thomas n'utilise pas ce vocabulaire.
Fix : remplacer par `⚠ divergence entre les deux méthodes de calcul` ou simplement `⚠ calcul contesté`.
Localisation : `build_html.py`, `<div class="legend">` (ligne ~847).

**[CH-2]** — Langage. Dans la légende-bar de la zone principale, l'item `|score| = force de conviction (≈ 50% + |score|/15, max à 7,5)` affiche une formule mathématique brute. À 7h du matin, Thomas ne lit pas de formules.
Fix : remplacer par : `plus la valeur est haute, plus la conviction est forte`.
Localisation : `build_html.py`, `<div class="legend-inner">` (ligne ~880).

**[CH-3]** — Scannabilité 6/10. La subnav propose des ancres (`Sauter à :`) mais leur liste est générée dynamiquement en JS. Sur le bulletin du 12/06, les ancres `Limites du jour`, `Calls 24h jugés`, `Détail par actif` sont présentes sans regroupement. Un utilisateur 5×/jour qui veut aller au Détail Argent doit cliquer `Détail par actif` puis scroller jusqu'à Argent — deux gestes.
Fix : les ancres par actif dans le Détail pourraient être sub-items ou le subnav pourrait inclure un lien direct `Détail : Or`, `Détail : Argent` etc. Complexité élevée — **quick win alternatif** : replier le bloc `Détail par actif` entier dans un `<details>` avec ancres internes uniquement quand ouvert. La subnav `Détail par actif` ouvre le fold et scrolle dedans.
Localisation : `build_html.py`, transform sections détail.

**[CH-4]** — Propreté 7/10. Le titre du navigateur est `TradingApp v3 — Bulletins`. Quand Thomas a l'onglet ouvert toute la journée, le titre ne lui dit pas quelle vue est active. Un onglet avec le titre du rapport actif (`Briefing 12/06 · 7h`) serait plus utile.
Fix : mettre à jour `document.title` en JS au changement de bulletin actif.
Localisation : `build_html.py`, JS `showBulletin()`.

**[CH-5]** — Charge 5/10. La `legend-bar` (sticky, au-dessus du contenu) occupe ~40px permanents. La `subnav` en occupe ~37px. Le header ~68px. Le context-banner ~50px. Total : **~195px** de chrome permanent en haut de page — soit ~20% d'un écran 1080p et ~35% d'un écran mobile 667px. Le contenu ne commence qu'après 195px de chrome.
Fix : fusionner `legend-bar` et `subnav` en une seule barre sticky (deux lignes au lieu de deux barres). La légende (très rarement consultée) passe en mode replié dans le `help-box` déjà présent. La `legend-bar` disparaît comme barre indépendante.
Localisation : `build_html.py`, CSS `.legend-bar` et `.subnav`.

**[CH-6]** — Mobile. Le masquage des colonnes 3 et 4 du tableau dense (`.dense-table td:nth-child(3)`, `:nth-child(4)`) supprime `Valeur actuelle` et `Penchant`. Il reste donc : `Critère | Comment c'est lu | Importance | Sens | Effet 24h | Effet 7j | Effet 1m`. Soit 7 colonnes sur mobile — toujours trop large pour scroller confortablement à 375px.
Fix : masquer aussi la colonne `Sens` sur mobile (elle est expliquée dans l'encart statique « Comment lire »). Réduire à 6 colonnes : `Critère | Comment c'est lu | Importance | Effet 24h | Effet 7j | Effet 1m`.
Localisation : `build_html.py`, CSS `.dense-table` mobile.

**[CH-7]** — Badges. Les badges `🔴` et `🟡` (dérivés des drapeaux existants) sont mentionnés dans l'historique des sessions comme implémentés, mais la légende HTML ne les documente pas. Ni le header, ni la légende-bar ne font référence à ces badges. Si Thomas les voit dans un tableau, il ne sait pas ce qu'ils signifient.
Fix : ajouter `🔴 alerte · 🟡 vigilance` dans la légende header ou la légende-bar.
Localisation : `build_html.py`, légende header.

---

## 3. Incohérences inter-rapports

| # | Problème | Rapport A | Rapport B | Fix |
|---|---|---|---|---|
| I-1 | Colonne `Δ` : `Δ vs 7h` (toujours vide) au 12h vs `Δ vs 12h` (rempli) au 18h | Suivi 12h | Suivi 18h | Uniformiser en `Δ précédent` (conditionnel) |
| I-2 | Libellé verdict : `VRAI` / `FAUSSE` dans le bilan vs `✅ VRAI` / `❌ FAUX` dans la vue Historique | Bilan jour | Vue Historique | Standardiser en `✅ VRAI` / `❌ FAUSSE` partout |
| I-3 | Format de la note : `SHORT (-8.12)` dans `À jouer` vs `SHORT (-8.12) ⚑ 📰 ⇄ ⌛` dans Synthèse vs `SHORT -6.64 (brut SHORT -8.24) ⚑ 📰 ⇄ ⌛` dans Synthèse quand pondéré. Trois formats différents pour le même actif. | Briefing (section À jouer) | Briefing (Synthèse) | Un format canonique : `SHORT −8.12 [flags]`, brut entre parenthèses uniquement si ≠ |
| I-4 | Statut Nasdaq/S&P/VIX : `🕐 pas encore ouvert` au 12h vs `—` au 18h (alors que les marchés sont ouverts depuis 15h30) | Suivi 12h | Suivi 18h | Au 18h, ces actifs doivent avoir un statut (⚠️ ou ✅ ou Hold) |
| I-5 | Symbole de séparation décimale : `0.20%` dans suivi 12h, `+0.44%` dans suivi 12h (cohérent), mais le tableau Détail du briefing utilise des virgules décimales dans certains libellés (`0,70` dans la légende) et des points ailleurs | Briefing (prose) | Briefing (tableaux) | Tout en point décimal dans les tableaux, virgule décimale en prose française — appliquer systématiquement |
| I-6 | Catalyseurs J+1 : présents dans le Bilan jour avec `~` et `🔴`/`🟡` ; absents des Suivis 12h/18h | Bilan jour | Suivi 18h | Ajouter les catalyseurs du lendemain en 1-2 lignes au suivi 18h (Thomas décide en fin de journée) |
| I-7 | Titre du rapport : le Suivi 12h commence par `## Suivi 12h — 2026-06-11 12h15` (niveau H2). Le Briefing commence par `# Bulletin Analyste — ...` (niveau H1). Le Bilan commence par `## Bilan du jour — ...` (niveau H2). Niveau de titre incohérent entre les rapports. | Briefing | Suivi / Bilan | Standardiser : tous les rapports commencent par H1 |

---

## 4. Le chemin vers 10/10

Liste ordonnée par impact décisionnel / facilité d'implémentation.

### Quick wins (< 1h de code chacun)

1. **[S-B1] Remonter / vérifier la Sélection du jour en tête du Briefing.** Si le bloc est absent du bulletin 7h du 12/06, c'est un bug de génération à corriger en priorité. C'est le P0 de scannabilité matin. → `scoring_analyste.py`

2. **[H-BD1] Ajouter une ligne résumé score AVANT le tableau résultats dans le Bilan du jour.** Une ligne : `**11/06 : 1 ✅ / 8 ❌ / 3 ⚪ — WR 11%**`. → `bilan_jour.py`

3. **[P-B1] Supprimer la répétition du mot SHORT/LONG dans la parenthèse `(brut SHORT -8.24)`** → `(brut -8.24)`. → `scoring_analyste.py`

4. **[P-B2] Zéros parasites dans le Détail : remplacer `+0.000` / `-0.000` par `—` quand la valeur est < 0.001.** → `scoring_analyste.py`

5. **[I-2] Standardiser VRAI/FAUSSE : `✅ VRAI` / `❌ FAUSSE` partout** (bilan jour + vue Historique). → `bilan_jour.py` + `build_html.py`

6. **[CH-4] Mettre à jour `document.title` au changement de bulletin actif** → `build_html.py`, JS `showBulletin()`.

7. **[S-R1] Remonter la ligne de synthèse `0/36 cellules fiables` en tête de `performance.md`** → `journaliste.py`, `render_performance`.

8. **[P-B4] Supprimer la redondance `— n/a (valeur absente)` dans la section Limites.** → `scoring_analyste.py`

9. **[C-BD1] Renvoi bilan semaine UNE seule fois au lieu de 6.** → `bilan_jour.py`

10. **[I-7] H1 pour tous les rapports** (Suivi et Bilan utilisent H2). → `run_suivi.py`, `bilan_jour.py`

### Chantiers (nécessitent test / plus de travail)

11. **[C-B1] Replier automatiquement `Détail par actif` (12 sous-sections) dans des `<details>` individuels.** C'est le fix de charge le plus impactant : réduit le bulletin visible de ~250 lignes. → `build_html.py`, transform post-markdown.

12. **[CH-5] Fusionner `legend-bar` et `subnav` en une seule barre sticky.** Récupère ~40px de chrome. → `build_html.py`, CSS + HTML.

13. **[C-B3] Tronquer `Calls 24h jugés` à 7 entrées max dans le bulletin markdown.** → `scoring_analyste.py`.

14. **[H-S2] Remplir le statut Nasdaq/S&P/VIX au suivi 18h** (marchés ouverts depuis 15h30). → `run_suivi.py`.

15. **[P-B3] Masquer les lignes `Drapeau régime` à valeur 0 dans le tableau Détail ; mettre en valeur quand valeur = 1.** → `scoring_analyste.py`.

16. **[C-R1] Masquer les lignes N=0 pour 7j et 1m dans la vue Résultats HTML.** → `build_html.py`.

17. **[I-6] Ajouter les catalyseurs J+1 au suivi 18h** (copie légère depuis le bilan). → `run_suivi.py`.

18. **[CH-2] Remplacer la formule `50% + |score|/15` par langage naturel dans la légende-bar.** → `build_html.py`.

19. **[L-B2] Reformuler la note d'intro Sélection du jour en langage trader.** → `scoring_analyste.py`.

20. **[C-B2] Vérifier et activer le fold sur `Cellules à surveiller`.** → `build_html.py`, vérification du transform fold.

---

## Tests UX — Grille de validation (reproductible round 2)

| Test | Critère | Vérifier au round 2 |
|---|---|---|
| Scannabilité matin | Sélection du jour visible en ≤ 3 secondes | Présent en 1er bloc du Briefing |
| Scannabilité soir | Score du jour visible sans scroll | Ligne résumé 1✅/8❌ en tête du Bilan |
| Charge Briefing | Longueur visible sans ouvrir les folds | < 80 lignes hors folds fermés |
| Cohérence inter-rapports | Même actif → même format de note | Vérifier Nasdaq : format identique dans À jouer et Synthèse |
| Statuts US au 18h | Aucun `—` pour Nasdaq/S&P/VIX après 15h30 | Statuts remplis ou motif explicite |
| Chrome mobile 375px | Tableau dense lisible sans scroll horizontal excessif | ≤ 5 colonnes visibles |
| Langage légende | Zéro formule mathématique exposée | `50% + |score|/15` absent |
| Doublons info | `SHORT` ne répété qu'une fois par cellule Synthèse | Grep `SHORT.*brut SHORT` = 0 résultats |

---

_Audit rédigé sur état du 2026-06-12 · Round 1 · Grille reproductible pour Round 2._
