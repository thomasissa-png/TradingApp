# Audit UX — Page HTML TradingApp v3
## Date : 2026-06-10 · Auditrice : @ux

---

## 1. Verdict en tête

| Casquette | Note /10 | Verdict brutal |
|---|---|---|
| **Comprendre** | 5/10 | La page s'apprend, elle ne s'explique pas. Un trader qui arrive à froid comprend *qu'il y a des données* mais pas ce que fait le système, pourquoi shadow, ni ce qu'est vraiment une cellule. |
| **Décider** | 6/10 | Le Briefing 7h contient l'essentiel — mais la conviction est noyée dans le bruit des flags. Le scanner 3-min chrono accroche systématiquement sur la matrice 12×3 = 36 cellules avant d'avoir compris lesquelles regarder. |
| **Juger** | 5/10 | Le win rate est accessible mais illisible à froid : N trop petits, tout est « trop peu », le warm-up n'est pas contextualisé. La métrique A5 (FAUSSES aux retournements) est absente de la vue. |

---

## 2. Parcours commentés

### 2.1 Casquette COMPRENDRE — « qu'est-ce que ce système fait ? »

**Chemin réel :** Ouvrir `index.html` → header → légende → sidebar → premier bulletin.

**Étape 1 — Le header.**
Titre : `TradingApp v3 — Bulletins`. Sous-titre : `Généré : 2026-06-10 06:19 UTC`. Légende : `⚑ flip · 📰 news>50% · ⚪ coin-flip · ⚠ divergence pm1/pondéré`.

Premier problème : le titre dit « Bulletins », pas « système de positionnement directionnel ». Un trader qui n'a pas lu la doc ne sait pas s'il consulte des alertes, des analyses éditoriales ou des signaux automatiques. La légende dans le header (`⚑ flip`) ne correspond pas à la définition dans la légende du bulletin (`⚑ gate régime extrême actif`) — **discordance de vocabulaire entre header et contenu**.

**Étape 2 — La sidebar.**
Quatre vues : `📅 Aujourd'hui` / `📈 Résultats / Win rate` / `🗓️ Bilan semaine` / `📊 Historique / Performance`. Aucun libellé n'explique ce qu'est le système. Pas de page « À propos » ni d'encart contextuel. L'utilisateur à froid ne sait pas pourquoi il y a 4 vues ni dans quel ordre les lire.

**Étape 3 — L'encart `❓ Comment lire les scores`.**
Il existe, il est replié par défaut. Contenu correct techniquement. Mais il répond à « comment lire un score », pas à « qu'est-ce que ce système fait ». Un trader qui arrive à froid ne sait pas encore qu'il a besoin de lire les scores — il cherche d'abord à comprendre le principe.

**Étape 4 — Le bulletin lui-même.**
Titre : `Bulletin Analyste — 2026-06-10 · 07h19 (Paris)`. Le mot « Analyste » est un nom technique interne. Le sous-titre `Fiches hash : 54e58430ae1f` est du debug visible à l'utilisateur.

La section `🎯 Top 3 convictions du jour` est un bon point d'entrée — mais elle s'ouvre avec `EUR/USD 7j — SHORT (-20.36)` sans expliquer que `-20.36` est un score interne (non un %) ni ce que signifie `7j` comme horizon actionnable.

**Ce qui manque pour COMPRENDRE :**
- Un bandeau ou encart en tête de page (2-3 lignes) : « Ce système analyse 12 actifs × 3 horizons et tranche LONG ou SHORT. Seul le Briefing 7h est noté. Le reste suit. »
- La définition de « shadow » nulle part visible. Thomas sait ce que c'est ; un lecteur de passage (ou Thomas lui-même dans 6 mois) ne sait pas.
- Le symbole `⚑` est défini différemment en haut (« flip ») et dans la légende du bulletin (« gate régime extrême actif »). Incohérence de vocabulaire.

---

### 2.2 Casquette DÉCIDER — « le matin, 3 min chrono »

**Chemin réel :** Ouvrir la page → vue par défaut → `❓` replié → premier bulletin → synthèse des décisions → décision.

**La bonne nouvelle :** La section `🎯 Top 3 convictions du jour` est en tête, avant la matrice. C'est une excellente décision de hiérarchie. Elle donne les 3 meilleures cellules avec score et driver dominant. Sur le bulletin du 10/06 : `EUR/USD 7j — SHORT (-20.36)`, `S&P 500 1m — SHORT (-17.80)`, `Or 7j — SHORT (-16.13)`. Une ligne par conviction, lisible en 5 secondes.

**Problème 1 — La matrice Synthèse est une muraille.**
La table 12 × 3 = 36 cellules s'affiche immédiatement après. Sur le bulletin 10/06, voici la cellule CAC 40 24h :
```
CAC 40 | SHORT (-0.05) ⚑ ≈ ⇄ ⇆
```
Cinq symboles après la direction. Le trader doit mémoriser la légende pour chaque cellule. Sur 36 cellules, 23 portent au moins un drapeau. La densité de signes transforme la matrice en devinette.

**Problème 2 — Flags sans tri.**
Les cellules non-actionnables (`⚪`, `≈`, `⚠️ conf. faible`) ne sont pas visuellement séparées des cellules solides. Argent 24h `SHORT (-7.95)` et Cuivre 24h `SHORT (-0.14) ⚑ 📰 ≈ ⚠️` occupent le même espace visuel. Thomas doit mentalement filtrer avant d'agir.

**Problème 3 — Le score comme signal de conviction est opaque.**
La légende-bar dit : `|score| = force de conviction (≈ 50% + |score|/15, max à 7,5)`. C'est correct mais exige un calcul mental. Sur le bulletin 10/06, les scores vont de `-0.05` (CAC 24h) à `-20.36` (EUR/USD 7j). La plage est si large que la comparaison rapide entre actifs est difficile : `-7.95` pour Argent vs `-12.24` pour Argent 7j — lequel jouer ? La formule `50% + |score|/15` n'est pas instinctive.

**Problème 4 — Flips vs veille : section mal placée.**
La section `## Flips vs veille` (3 lignes, 10/06 : Blé, CAC) est reléguée APRÈS la légende et AVANT `## Détail par actif`. Elle devrait être visible avant la matrice complète — ce sont les cellules qui ont changé d'avis du jour au lendemain, donc les plus risquées à jouer immédiatement.

**Problème 5 — Le bloc ⚭ (drivers partagés) est absent de la vue HTML.**
Reco A flag-only validée Thomas (Session 6), mais au 10/06 ce bloc n'est pas dans le bulletin HTML. Les cellules partagent le même critère TIPS (Nasdaq/Or/Argent/S&P → tous SHORT) sans que ce soit signalé comme corrélation. Le risque de fausse conviction de consensus reste actif.

**Problème 6 — La légende-bar sticky `main h2 scroll-margin-top: 100px`.**
La barre de légende (score, LONG/SHORT, ⚪, 📰, ⚑, ⚠) est toujours visible. C'est utile. Mais elle double partiellement la légende du bulletin markdown (qui liste les mêmes symboles en texte courant). Double définition = confusion : la barre dit `⚑ gate`, le bullet dans le bulletin dit `⚑ gate régime extrême actif`. Pas le même niveau de précision.

---

### 2.3 Casquette JUGER — « le soir / week-end »

**Chemin réel :** Vue `📈 Résultats / Win rate` → vue `📅 Aujourd'hui` → Bilan du jour → vue `📊 Historique`.

**Vue « Résultats / Win rate » (performance.md).**
Bien structuré : tableau par horizon, trié par win rate décroissant, statuts clairs. Le header d'intro dit : « Le taux de bonnes directions par actif et par horizon. La vue de résultats la plus à jour. »

Friction principale : tout est `⏳ trop peu (X/15)`. Sur le bulletin 10/06 performance.md :
- Blé 24h : 100% sur 7 paris — lisible.
- CAC 40 24h : 0% sur 1 pari — le statut `⏳ trop peu (1/15)` signifie que c'est non-concluant, mais un N=1 à 0% peut inquiéter sans raison.

**Il manque un contexte de warm-up.** La phrase `0 / 36 cellules fiables` en tête est honnête mais décourageante à froid. Il n'y a pas d'indication de « dans combien de jours certaines cellules sortiront de warm-up (24h : ~J+25 dès le 11/06) ». Thomas sait, la page non.

**La métrique A5 « FAUSSES aux retournements » est absente de la vue HTML.**
A5 est implémentée dans le Bilan du jour (`run_bilan.py`), mais le Bilan semaine (absent au 10/06 — aucun fichier en `bilan-semaine/`) ne peut pas la reprendre. La vue Résultats ne l'affiche pas. C'est la métrique la plus critique pour juger si le système se trompe structurellement sur les retournements — elle est invisible.

**Vue « Aujourd'hui ».**
Le bilan 10/06 n'existe pas encore (22h15, heure de génération). Le suivi 18h est là. Le layout `details/summary` replié par jour est bien — chaque jour se déplie proprement. Mais sur le 10/06, l'utilisateur voit :
- `📅 Aujourd'hui` avec `2026-06-10` déplié → `Suivi 18h` + `Suivi 12h` repliés.
- Le Briefing 7h n'est PAS dans la vue « Aujourd'hui » — il est dans la liste de bulletins en sidebar, vue séparée.

Ce découpage crée un **parcours fragmenté** : pour juger une journée complète, Thomas doit naviguer sidebar (Briefing 7h) + vue Aujourd'hui (Suivi 12h/18h) + vue Aujourd'hui (Bilan 22h). Il n'existe pas d'écran « tout sur un seul jour » unifié.

**Vue Historique.**
Le win rate y est répété (bloc `history-winrate` réaffiche performance.md). Le tableau `Décision par décision` avec filtres actif/horizon/résultat est un bon outil de jugement post-hoc. Les filtres fonctionnent. La colonne `Réalisé %` permet de voir les amplitudes. Solide.

Manque : pas de colonne `Driver principal` ni `Flags actifs au moment du call`. Pour juger si une FAUSSE était évitable, Thomas ne peut pas recorréler avec les drapeaux du bulletin d'origine depuis l'historique.

**Vue Bilan semaine.**
Absente au 10/06 (aucun fichier `bilan-semaine/`). La section affiche `⏳ en attente`. Message correct, mais pas de date estimée de première apparition.

---

## 3. Constats priorisés

### P0 — Bloque la casquette

**P0-A — Incohérence de vocabulaire ⚑ (header vs bulletin)**
- **Problème** : Le header dit `⚑ flip`. La légende du bulletin dit `⚑ gate régime extrême actif`. Ce sont deux définitions incompatibles pour le même symbole.
- **Preuve** : Header HTML ligne `<code>⚑</code> flip ·` vs bulletin 10/06 `⚑ gate régime extrême actif`.
- **Fix** : Dans `render_html()`, remplacer `<code>⚑</code> flip` par `<code>⚑</code> gate régime`. Quick win — 1 ligne dans `build_html.py`.

**P0-B — Aucun contexte système visible à l'ouverture (casquette COMPRENDRE)**
- **Problème** : Le trader à froid ne sait pas ce que fait le système. « Bulletins » dans le titre ne dit rien du principe de fonctionnement. Le mot « shadow » est absent de toute vue.
- **Preuve** : Header `<title>TradingApp v3 — Bulletins</title>`, `<h1>TradingApp v3 — Bulletins</h1>`. Aucun encart d'introduction dans la page.
- **Fix** : Ajouter dans `render_html()` un bloc d'introduction statique (3 lignes, replié ou visible) avant l'encart `❓` : « Ce système analyse 12 actifs × 3 horizons et produit une direction LONG/SHORT. Seul le Briefing 7h est noté (mesure ouverture→clôture). Mode shadow : les décisions sont enregistrées mais pas exécutées. » Quick win — ajout HTML statique dans le template.

**P0-C — Le Bilan du jour est coupé du Briefing 7h (casquette JUGER)**
- **Problème** : Pour juger une journée, Thomas doit naviguer deux vues distinctes (sidebar Bulletins pour le 7h, vue Aujourd'hui pour 12h/18h/22h). Pas de vue « journée complète ».
- **Preuve** : Le Briefing 7h est dans `BULLETINS` (sidebar bulletins), les suivis/bilan dans `REPORTS` (vue Aujourd'hui). Le code `build_reports_payload` ne collecte pas les bulletins 7h.
- **Fix** : Dans la vue « Aujourd'hui », sous chaque groupe-jour (`today-day`), ajouter en premier item replié le Briefing 7h correspondant à cette date. Chantier — nécessite de fusionner `BULLETINS` et `REPORTS` par date dans le JS de la vue Aujourd'hui.

---

### P1 — Friction réelle

**P1-A — Aucune séparation visuelle entre cellules actionnables et cellules à ignorer**
- **Problème** : La matrice 36 cellules ne distingue pas les cellules solides (ex. Argent 24h SHORT -7.95) des quasi-neutres (ex. CAC 40 24h SHORT -0.05 ⚑ ≈). Thomas doit tout lire pour filtrer.
- **Preuve** : Bulletin 10/06, matrice Synthèse — CAC 40 24h et Argent 24h dans la même mise en forme.
- **Fix** : Mise en forme CSS : griser les lignes portant `≈` ou `⚪` (opacity 0.5). Quick win — règle CSS ciblée sur les td contenant ces symboles, appliquée via `colorizeDirections()`.

**P1-B — Les Flips vs veille ne sont pas mis en avant avant la matrice**
- **Problème** : Section `## Flips vs veille` après la légende = invisible au scan rapide. Ce sont les décisions qui ont retourné du jour au lendemain — les plus risquées.
- **Preuve** : Bulletin 10/06, ordre : Top 3 → Synthèse des décisions → Légende → Note → Cellules à surveiller (replié) → Briefing du jour → **Flips vs veille** → Détail par actif.
- **Fix** : Déplacer `## Flips vs veille` immédiatement après `## 🎯 Top 3 convictions du jour`, avant la matrice. Quick win — réordonner dans `scoring_analyste.py` ou `build_bulletin.py`.

**P1-C — Score brut illisible comme indicateur de conviction**
- **Problème** : Les scores vont de -0.05 à -20.36. Aucun repère visuel pour savoir si `-7.95` est « fort » ou « moyen ». La formule `50% + |score|/15` exige un calcul mental.
- **Preuve** : Légende-bar : `|score| = force de conviction (≈ 50% + |score|/15, max à 7,5)`. Score maximal vu au 10/06 : -20.36 (EUR/USD 7j), score minimal : +0.01 (Blé 24h).
- **Fix** : Afficher un badge textuel de conviction à côté de la note dans la matrice : `🔴 forte` (|score|>5), `🟡 modérée` (2-5), `⚪ faible` (<2). Quick win — ajout dans le rendu JS après `colorizeDirections`.

**P1-D — Métadonnées techniques visibles dans le bulletin (Fiches hash, version Analyste)**
- **Problème** : `Analyste version : v3.0.0` et `Fiches hash : 54e58430ae1f` sont affichés en tête du bulletin markdown. Thomas les voit. Ce sont des infos de debug/suivi interne.
- **Preuve** : Bulletin 10/06 lignes 3-5.
- **Fix** : Dans `scoring_analyste.py` (ou `build_bulletin.py`), replier ces métadonnées dans un `<details>` ou les supprimer de la vue principale. Quick win — wrapping ou exclusion du rendu.

**P1-E — La section « Limites du jour » est un bloc dense peu lisible**
- **Problème** : La section liste actif par actif les critères n/a et les gates actifs — 12 blocs, une trentaine de lignes. Utile pour le debug mais perturbant pour la décision.
- **Preuve** : Bulletin 10/06, section `## Limites du jour`, ~40 lignes listant `n/a : Activité industrielle Chine (PMI) (poids 12)` etc.
- **Fix** : Replier la section `## Limites du jour` en `<details>` (comme « Cellules à surveiller »). Quick win — même mécanisme `foldCellsToWatch`, ciblant `## Limites du jour`.

**P1-F — Le bloc ⚭ (drivers macro partagés) absent du bulletin HTML**
- **Problème** : La corrélation cachée (TIPS porte 4 actifs SHORT simultanément) est documentée mais non affichée. Reco A flag-only validée, non implémentée dans `scoring_analyste.py` au 10/06.
- **Preuve** : Bulletin 10/06 — aucune mention `⚭`. project-context.md S6 : « flag ⚭ drivers macro partagés au bulletin (Reco A flag-only) ».
- **Fix** : [Chantier — déjà en cours selon mémo S6] S'assurer que `scoring_analyste.py` génère bien le bloc ⚭ et vérifier au run du 11/06. Si absent → P0 pour S7.

**P1-G — La vue Bilan semaine affiche « en attente » sans date**
- **Problème** : `⏳ en attente` pour la vue Bilan semaine — aucune info sur quand ce sera disponible. Désorientant pour Thomas qui cherche à juger la semaine.
- **Preuve** : `<p id="week-empty" hidden>` rempli dynamiquement si `WEEKLY === null`.
- **Fix** : Afficher dans le message : « Premier bilan semaine généré le dimanche suivant (18h). » Quick win — modifier le texte statique dans `render_html`.

---

### P2 — Polish

**P2-A — `Généré : 2026-06-10T07:19:06.037270+02:00` en tête du bulletin : format ISO non-lisible**
- **Problème** : La date est au format ISO8601 complet avec microsecondes. Peu lisible en scan rapide.
- **Preuve** : Bulletin 10/06, ligne 2.
- **Fix** : Formater en `10 juin 2026 · 07h19 (Paris)` dans le script de génération. Quick win — strftime.

**P2-B — Titre de la page `TradingApp v3 — Bulletins` : fonctionnel mais neutre**
- **Problème** : Pas d'accroche. Ne reflète pas l'intent (positionnement directionnel, LONG/SHORT, trading de tendance).
- **Fix** : `TradingApp v3 — Signaux LONG/SHORT` ou rester sur le titre actuel mais ajouter un sous-titre dans le `<header>`. Cosmétique — faible priorité.

**P2-C — La subnav n'inclut pas les sections `## Flips vs veille` ni `## Audit de la veille`**
- **Problème** : La subnav génère des ancres pour les `h2` du bulletin. `## Flips vs veille` et `## Audit de la veille` sont des h2 mais n'apparaissent pas dans la subnav si le rendu marked ne leur attribue pas d'id. À vérifier.
- **Fix** : S'assurer que `buildSubnav` cible bien tous les h2 du rendu, y compris ceux à emoji.

**P2-D — `⚠️` et `⚠` : deux variantes du même symbole dans la légende**
- **Problème** : Le code `SYMBOL_TOOLTIPS` définit les deux variantes (`⚠️` et `⚠`) avec la même description. La légende du bulletin utilise `⚠️`. La légende header utilise `⚠`. Incohérence mineure.
- **Fix** : Harmoniser sur une seule variante partout. Quick win — 1 `replace_all` dans `build_html.py` et `scoring_analyste.py`.

---

## 4. Le test « plaisir »

**La page donne-t-elle envie d'y revenir 5×/jour ?**

**Points positifs :**
- Dark mode automatique — excellent choix, réduit la fatigue visuelle pour un trader matinal.
- La colorisation LONG (vert) / SHORT (rouge) dans les cellules de tableau est immédiate et lisible.
- La légende-bar sticky est une bonne décision : les définitions restent accessibles sans scroller.
- La subnav (`Sauter à :`) sur les bulletins denses évite de scroller 300 lignes pour trouver un actif.
- Le design est propre et sobre, sans surcharge graphique.

**Points négatifs pour le plaisir :**
- **Densité de symboles dans la matrice.** Sur le bulletin 10/06, la ligne `CAC 40 | SHORT (-0.05) ⚑ ≈ ⇄ ⇆` contient 4 drapeaux post-direction. Le cerveau en mode scan rapide trébuche sur cette densité.
- **Les 40 lignes de « Limites du jour ».** Section obligatoire pour l'intégrité mais qui s'affiche en plein avant d'être repliée. C'est un mur de texte technique au milieu d'un document de décision.
- **La section `## Audit de la veille`** au 10/06 liste 23 résultats avec des dates de prédiction dans le passé lointain (`prédit le 2026-06-02`). C'est de l'information de mesure, pas de décision. Elle mériterait d'être repliée ou transférée vers la vue Historique.
- **Le Briefing du jour** (`_1318 events analysés, 0 à impact (fenêtre 48h)_`) : lorsque la fenêtre est vide, cela génère une section avec une seule ligne `Aucun event marquant`. Acceptable mais décevant visuellement — un encart vide après un titre de section.
- **Mobile :** Le masquage des colonnes 3 et 4 (dense-table) sur mobile est bien pensé techniquement. En pratique, la table Synthèse (4 colonnes) reste lisible. La table Détail par actif (9 colonnes) devient lisible sur mobile grâce au masquage. Le scroll horizontal avec `overflow-x: auto` fonctionne. C'est correct, pas exceptionnel.

**Score plaisir estimé : 6/10.** La page est fonctionnelle et sobre. Elle n'est pas désagréable. Mais elle demande un effort cognitif à chaque consultation — elle ne guide pas, elle expose. Un utilisateur qui revient 5×/jour a besoin que la page lui dise en 3 secondes « regarde ça » — le Top 3 va dans ce sens, mais le reste de la structure dilue ce signal.

---

## 5. Top 5 recommandations par ordre d'impact

### Reco 1 — Replier « Limites du jour » et « Audit de la veille » (P1-E + cosmétique)
**Impact** : Réduit la longueur perçue du bulletin de ~40% sans rien supprimer. La décision se lit sur la première moitié de la page.
**Fix** : Étendre le mécanisme `foldCellsToWatch` pour cibler aussi `## Limites du jour` et `## Audit de la veille`. Quick win, 5 lignes dans `build_html.py`.
**Faisable sans toucher au scoring.** ✅

### Reco 2 — Corriger ⚑ dans le header + ajouter un bandeau contexte 3 lignes (P0-A + P0-B)
**Impact** : Résout la confusion du trader à froid et l'incohérence de vocabulaire en même temps.
**Fix** : (a) Remplacer `⚑ flip` → `⚑ gate régime` dans le header. (b) Ajouter entre le header et l'encart `❓` un bandeau statique : « 12 actifs × 3 horizons — direction LONG/SHORT — Briefing 7h seul noté (ouverture→clôture). Mode shadow. » Quick win, 2 changements dans `render_html`.
**Faisable sans toucher au scoring.** ✅

### Reco 3 — Griser les cellules non-actionnables dans la matrice Synthèse (P1-A)
**Impact** : Le scan de la matrice passe de 36 cellules à ~10-15 cellules visuellement actives. Réduction drastique du temps de décision.
**Fix** : Dans la fonction JS `colorizeDirections` (ou une nouvelle fonction `dimWeakCells`), ajouter après le rendu markdown : pour chaque `<td>` contenant `≈` ou `⚪`, appliquer `opacity: 0.4; color: var(--text-muted)` sur la ligne entière. Quick win, ~15 lignes JS dans `build_html.py`.
**Faisable sans toucher au scoring.** ✅

### Reco 4 — Unifier la vue journée (P0-C : Briefing 7h dans « Aujourd'hui »)
**Impact** : Thomas peut juger une journée sans changer de vue. Unifie le parcours DÉCIDER et JUGER.
**Fix** : Dans le JS de la vue Aujourd'hui (`renderToday`), pour chaque date présente dans `REPORTS`, chercher dans `BULLETINS` le bulletin de même date dont `slot === 'matin'` et l'insérer en premier item replié. Chantier moyen, ~30 lignes JS, aucune donnée à créer.
**Faisable sans toucher au scoring.** ✅

### Reco 5 — Ajouter un badge de conviction dans la matrice Synthèse (P1-C)
**Impact** : Rend la comparaison inter-actifs instinctive sans calcul. Thomas voit d'un coup d'œil les cellules `forte` vs `faible`.
**Fix** : Après `colorizeDirections`, injecter un badge textuel de conviction (ex. `🔴 forte` / `🟡 mod.` / `⚪ faible`) dans chaque `<td>` contenant un score signé. Seuils suggérés : |score| ≥ 5 = forte, 2-5 = modérée, < 2 = faible. Quick win, ~20 lignes JS dans `build_html.py`.
**Faisable sans toucher au scoring.** ✅

---

## Récapitulatif quick wins vs chantiers

| Catégorie | Items | Effort |
|---|---|---|
| **Quick wins (build_html.py / markdown)** | P0-A, P0-B, P1-B (réorder bulletin), P1-D, P1-E, P1-G, P2-A, P2-D, Reco 1, Reco 2, Reco 3, Reco 5 | 1-2h total |
| **Chantiers (nouvelles données / structure JS)** | P0-C (vue journée unifiée), P1-F (bloc ⚭ à vérifier au run 11/06) | 2-4h |

---

## Tests UX — synthèse rapide

| Test | Critère | Statut |
|---|---|---|
| Parcours COMPRENDRE : trader à froid comprend le système en 2 min | Aucun scroll requis pour voir le principe | ❌ — aucun texte d'intro accessible sans chercher |
| Décision 3 min : Top 3 visible immédiatement | Au-dessus de la ligne de flottaison | ✅ |
| Décision 3 min : matrice filtrée visuellement | Cellules faibles grisées | ❌ |
| Juger : win rate accessible en 1 clic | Vue Résultats en sidebar | ✅ |
| Juger : contexte de warm-up visible | Date de sortie warm-up affichée | ❌ |
| Cohérence symboles header/contenu | ⚑ défini pareil partout | ❌ |
| Mobile : tables denses lisibles | dense-table masque col 3+4 | ✅ |
| WCAG 2.2 contraste | dark mode + vert/rouge | ⚠️ vert #4ade80 sur #0f172a = à vérifier (ratio estimé OK) |

---

_Audit réalisé sur : bulletin 10/06 07h, suivi 18h, bilan-jour 09/06, performance.md, build_html.py (1589 lignes). Aucune modification de code — lecture seule._
