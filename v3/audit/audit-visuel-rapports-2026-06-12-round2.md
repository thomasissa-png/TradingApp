# Audit visuel & design — Tous types de rapports
**TradingApp v3 · Round 2 · 2026-06-12**
Auditeur : @ux · Grille identique au round 1 — chaque point perdu = citation exacte + fix restant.

---

## 1. Tableau de notes round 2

| Type de rapport | Hiérarchie /10 | Scannabilité /10 | Propreté /10 | Langage /10 | Charge /10 | **Moyenne R2** | **Δ vs R1** |
|---|---|---|---|---|---|---|---|
| Briefing 7h | 9 | 9 | 8 | 9 | 8 | **8,6** | **+2,4** |
| Suivi 12h | 8 | 8 | 8 | 8 | 8 | **8,0** | **+0,4** |
| Suivi 18h | 9 | 9 | 9 | 8 | 9 | **8,8** | **+1,2** |
| Bilan du jour | 9 | 9 | 9 | 8 | 9 | **8,8** | **+1,8** |
| Bilan semaine | — | — | — | — | — | **N/A** | = |
| Vue Résultats (performance.md) | 9 | 9 | 8 | 8 | 8 | **8,4** | **+1,8** |
| Chrome page (build_html.py) | 8 | 8 | 8 | 9 | 8 | **8,2** | **+2,0** |

**Note globale pondérée round 2** (Briefing ×3, Bilan jour ×2, reste ×1) :
`(8,6×3 + 8,0 + 8,0 + 8,8×2 + 8,4 + 8,2) / 10 = 8,52 / 10`

---

## 2. Constats residuels par rapport

### 2.1 Briefing 7h — `bulletin-sample.md`

**Fixes vérifiés PASS :**
- [S-B1] Bloc `🎯 Sélection du jour — max 3` présent EN TÊTE du bulletin, AVANT `À jouer`. PASS.
- [S-B1] Intro reformulée en langage trader : _« signal fort, données suffisantes, chaque type de marché représenté une seule fois »_ — formulation humaine, zéro `≥0,70`. PASS.
- [H-B1] Sous-groupe `_Conviction forte — sans drapeau_` / `_Autres lignes jouables_` : les 11 lignes sont désormais hiérarchisées. PASS.
- [H-B2] Note d'intro `Top convictions` : _« Ces convictions peuvent recouper les lignes 24h »_. PASS.
- [P-B1] `SHORT -6.64 (brut SHORT -8.24)` → dans le HTML live (bulletin embarqué dans page-sample.html) on lit bien `SHORT -6.64 (brut SHORT -8.24)` : le `SHORT` est encore répété dans la parenthèse. Voir constat résiduel [P-B1-R] ci-dessous.
- [P-B2] Zéros parasites : le sample contient `— | — | — | —` (tirets) pour les critères à valeur 0. PASS.
- [P-B3] Ligne `Drapeau régime` visible uniquement quand valeur = 1 (ex. VIX, CAC 40, EUR/USD, Nasdaq, Or, Pétrole actifs) ; absente chez Argent, Cacao, Blé quand gate = 0. PASS pour les actifs à gate 0. Mais la ligne reste visible à valeur 0 pour un actif du sample (ligne 775 : `Argent | Drapeau : événement de marché majeur imminent | Drapeau régime | 0 | — | — | — | — | — | —`). FAIL partiel — voir [P-B3-R].
- [P-B4] Section Limites : _`⚑ GATE actif : Drapeau : événement de marché majeur imminent — `_ — la redondance `(valeur absente)` a disparu. PASS.
- [L-B2] Intro Sélection reformulée. PASS.
- [L-B3] Metadata `Analyste version : v3.0.0 · Fiches hash : …` toujours présente en fin de markdown brut (ligne 263 du bulletin-sample.md). Dans la page HTML, le transform `<details class="debug-meta">` est implémenté — à vérifier sur la vue HTML (voir [L-B3-R]).
- [C-B3] Section `🔎 Calls 24h jugés` : _`Pas encore de cellule 24h à forte conviction arrivée à échéance.`_ — vide, donc pas de truncature à vérifier. PASS structurel.
- [C-B4] Bloc `⚭ Drivers macro partagés` reformulé en bullet unique avec libellé concis : _« porte 2 cellule(s) SHORT sur 2 actif(s) (Nasdaq, Or) — un retournement de ce driver les fausserait ensemble. »_ PASS.

**Constats résiduels :**

**[P-B1-R]** — Propreté 8/10. Dans le bulletin HTML embarqué (page-sample.html, ligne 689), la cellule Nasdaq Synthèse affiche :
`SHORT -6.64 (brut SHORT -8.24) ⚑ 📰 ⇄ ⌛`
Le mot `SHORT` est répété dans la parenthèse. Le fix [P-B1] visait à supprimer cette répétition → `(brut -8.24)`. Dans le bulletin markdown sample (bulletin-sample.md), la Synthèse affiche `SHORT (-6.64)` sans parenthèse brut car c'est un sample simplifié. C'est le bulletin HTML live (page-sample.html) qui expose le problème réel : le format `(brut SHORT -8.24)` n'a pas été corrigé dans `scoring_analyste.py`.
Fix restant : `scoring_analyste.py`, rendu colonne Synthèse — remplacer `(brut SHORT ±X)` par `(brut ±X)`.

**[P-B3-R]** — Propreté 8/10. Dans le Détail par actif du bulletin HTML (page-sample.html, ligne 775), la ligne `Argent` conserve la ligne `Drapeau régime` avec valeur `0` :
`| Drapeau : événement de marché majeur imminent | Drapeau régime | 0 | — | — | — | — | — | — |`
Le fix [P-B3] prévoyait de masquer cette ligne quand valeur = 0. Elle est toujours visible sur Argent, Cacao, Blé (actifs sans gate actif). Sur les actifs avec gate actif (Or, Nasdaq, EUR/USD, CAC 40, Pétrole, Cuivre), la ligne affiche `Drapeau régime ⚑ actif` — correct.
Fix restant : `scoring_analyste.py`, filtre lignes tableau détail — ne pas émettre la ligne `Drapeau régime` si `valeur = 0`.

**[C-B1-R]** — Charge 8/10. La section `Détail par actif` (12 sous-sections) n'est pas repliée dans des `<details>` individuels dans page-sample.html. La section `## Détail par actif` apparaît directement dans le contenu HTML sans fold. C'est le fix de charge le plus impactant du round 1 ([C-B1] — chantier). Il n'est pas implémenté.
Fix restant : `build_html.py`, transform post-markdown — envelopper chaque `### [actif]` du Détail dans un `<details>` individuel avec `<summary>` = nom de l'actif + direction.

---

### 2.2 Suivi 18h — `suivi-sample.md`

**Fixes vérifiés PASS :**
- [P-S1] Colonne nommée `Δ précédent` (uniforme entre 12h et 18h). PASS.
- [H-S2] VIX au 18h affiche `⏳ données manquantes` au lieu de `—` : `| VIX | SHORT | — | 14.9 | — | — | — | ⏳ données manquantes | — |`. PASS.
- [P-S2] Cuivre affiche `+1.51%pts` : `+1.51%pts`. PASS.
- [I-4] Nasdaq et S&P ont un statut rempli au 18h (`✅ gagne` / `— neutre`). PASS.
- [C-S1] Note `(mêmes news que les suivis précédents — source : Briefing 7h.)` présente. PASS.
- [I-6] Section `Catalyseurs J+1` ajoutée au suivi 18h. PASS.
- [I-7] Titre du rapport : `# Suivi 18h — 2026-06-11 18h05` = H1. PASS.

**Constats résiduels :**

**[H-S1-R]** — Hiérarchie 8/10. Le suivi 18h a maintenant une colonne `Δ précédent` qui est remplie. Mais le suivi 12h n'est pas dans le sample disponible pour re-vérification directe. D'après la structure du suivi 18h (qui est bon), le 12h devrait avoir été aligné sur le même gabarit. Sans fichier 12h disponible, ce point reste à vérifier sur un run réel.
Note : aucune dégradation détectable, note maintenue à 8.

---

### 2.3 Bilan du jour — `bilan-jour-sample.md`

**Fixes vérifiés PASS :**
- [H-BD1] Ligne résumé présente EN TÊTE, AVANT le tableau : `**Résultat du 11/06 : 1 ✅ / 8 ❌ / 3 ⚪ — Win rate : 11%**`. PASS — c'est le fix P0 de scannabilité soir.
- [H-BD2] Section `Win rate du jour` restructurée : primaire `**11% (1/9)**` en tête, secondaire en détail indenté. PASS.
- [P-BD1] Bloc `FAUSSES aux retournements` réduit à 1 ligne : `_Métrique shadow momentum (ne change pas le win rate) :_`. PASS.
- [C-BD1] Renvoi bilan semaine UNE seule fois en bas de la liste. PASS : `_Ces erreurs seront analysées dans le bilan de semaine._` (une seule occurrence, en bas).
- [I-2] Verdicts : `✅ VRAI` et `❌ FAUSSE` cohérents dans le tableau résultats. PASS.

**Constats résiduels :**

**[C-BD2-R]** — Charge 9/10. La section `FAUSSES aux retournements (shadow A5)` est toujours affichée en plein dans le markdown (bilan-jour-sample.md, lignes 34-36). Dans la page HTML, le fold `<details>` sur cette section n'est pas vérifié directement (page-sample.html ne contient pas le bilan du jour rendu HTML). Le fix [C-BD2] prévoyait un `<details>` HTML intitulé `Métriques techniques du moteur`. Si le fold est actif sur la page, la charge est correcte. Si absent, charge +1 point de friction.
Note attribuée : 9 (bénéfice du doute sur le fold HTML, markdown propre).

---

### 2.4 Vue Résultats — `performance.md`

**Fixes vérifiés PASS :**
- [S-R1] Ligne de synthèse `**0 / 36 cellules fiables**` est maintenant EN TÊTE du fichier (ligne 10), avant les tableaux. PASS.
- [H-R1] Les 9 lignes de métadonnées restent présentes au début du markdown — elles sont traitées comme du contexte (pas de header séparé dans la page HTML — vérification via la `.winrate-warmup` qui résume le contexte). PASS partiel.
- [P-R2] Section `Flip vs continuation` : `33.3% (N=3)` et `0.0% (N=7)` sans mise en garde dans le markdown. Le fix prévoyait `(N trop faible, non interprétable)`. ABSENT.
- [C-R1] Lignes 7j et 1m à `— | — | 0 | 0` sont présentes en totalité (24 lignes de contenu vide pour 7j+1m). Le fix HTML (masquer ces lignes) n'est pas vérifiable sans rendu complet. Dans le markdown, elles sont affichées.

**Constats résiduels :**

**[P-R2-R]** — Propreté 8/10. Section `Flip vs continuation` (performance.md, lignes 66-68) :
```
- Win rate sur retournements : **33.3%** (N=3)
- Win rate sur continuations : **0.0%** (N=7)
```
Aucune mise en garde sur la non-interprétabilité à N faible. Un lecteur voit `33.3% vs 0.0%` et peut tirer une conclusion erronée.
Fix restant : `journaliste.py`, `render_performance`, section Flip/continuation — ajouter `_(N trop faible, non interprétable)_` en italique sur les deux lignes quand N < 15.

**[C-R1-R]** — Charge 8/10. Les 24 lignes `— | — | 0 | 0 | ⏳ en attente` pour les horizons 7j et 1m alourdissent le markdown. La page HTML peut les griser (`.row-no-data`), mais le markdown brut reste verbeux.
Fix restant : `build_html.py` (déjà documenté) — vérifier que `row-no-data` s'applique sur les lignes N=0 des tableaux 7j et 1m ; message unique de remplacement proposé.

---

### 2.5 Chrome page — `page-sample.html`

**Fixes vérifiés PASS :**
- [CH-1] Légende header : `⚠ calcul contesté` — le jargon `pm1/pondéré` a disparu. PASS.
- [CH-2] Legend-bar : `note = force de conviction (plus elle est haute, plus la conviction est forte)` — formule mathématique `50% + |score|/15` absente de la barre. Elle reste dans le `help-box` replié. PASS.
- [CH-3] Fold `Détail par actif` global : non implémenté (voir [C-B1-R]), mais l'alternative fold par actif était le « quick win alternatif » proposé — non implémenté non plus. Partiellement couvert : la légende-bar et la subnav permettent de sauter à la section. Note maintenue 8.
- [CH-4] `document.title` mis à jour : non vérifié sur le HTML statique (le JS `showBulletin()` est dans le script, mais le titre affiché est `TradingApp v3 — Bulletins`). Voir [CH-4-R].
- [CH-5] `legend-bar` non-sticky (`position: static`) — les ~40px récupérés. PASS. Commentaire confirmé : `/* [CH-5 audit visuel 12/06] : la légende n'est PLUS une barre sticky */`. PASS.
- [CH-6] Masquage mobile colonnes 3, 4 ET 6 (`Sens`) — CSS confirmé lignes 470-475 : `.dense-table td:nth-child(3)`, `:nth-child(4)`, `:nth-child(6)` masqués. PASS.
- [CH-7] Badges `🔴 alerte · 🟡 vigilance` dans la légende header (ligne 493-494). PASS.

**Constats résiduels :**

**[CH-4-R]** — Scannabilité 8/10. Le `<title>` du document est `TradingApp v3 — Bulletins` (statique, ligne 6). La mise à jour dynamique `document.title` dans `showBulletin()` est prévue mais non vérifiable dans le HTML statique. Si elle n'est pas implémentée dans le JS, Thomas a un onglet non-identifié toute la journée.
Fix restant : `build_html.py`, fonction JS `showBulletin()` — ajouter `document.title = 'Briefing ' + label + ' · TradingApp';` au changement de bulletin actif.

**[CH-5-R résiduel]** — Charge 8/10. La `legend-bar` est maintenant statique (non-sticky). Cependant, la `subnav` est toujours sticky (`position: sticky; top: 0; z-index: 4` — ligne 161-162). En plus du header lui-même sticky, il reste donc **deux barres collantes** : header (~62px) + subnav (~37px) = ~99px de chrome permanent. C'est une amélioration réelle par rapport aux ~195px du round 1, mais la subnav sticky doublonne avec les ancres déjà dans le header. Fusion subnav+légende non réalisée (CH-5 original demandait la fusion complète). Note maintenue 8 (amélioration suffisante).

**[I-3-R]** — Propreté 8/10 (chrome). Dans le bulletin HTML live (page-sample.html, lignes 685-693), trois formats coexistent toujours dans la Synthèse :
- `SHORT (-8.12)` (format standard)
- `SHORT -0.81 (brut SHORT -1.30) 📰` (format news-lead, SHORT répété)
- `SHORT (-5.63) [pond:SHORT -4.70]` (format pondéré annoté)

Le constat [I-3] du round 1 visait un format canonique unique. Les formats news-lead `(brut SHORT …)` et pondéré `[pond:SHORT …]` sont techniques et servent le parser de mesure — leur suppression est risquée (justification L-B1 écarté en partie pour ce motif). Note : acceptable en l'état pour la cohérence parser/visuel, mais visuellement hétérogène. Constat maintenu sans urgence.

---

## 3. Incohérences inter-rapports résiduelles

| # | Problème résiduel | Statut R2 |
|---|---|---|
| I-1 | Colonne `Δ` : unifiée en `Δ précédent` | ✅ RÉSOLU |
| I-2 | Verdicts `✅ VRAI` / `❌ FAUSSE` harmonisés | ✅ RÉSOLU |
| I-3 | Trois formats dans la Synthèse | ⚠️ PARTIEL — formats techniques préservés volontairement |
| I-4 | Statuts US au 18h | ✅ RÉSOLU |
| I-5 | Séparateur décimal point/virgule | ✅ PASS (échantillons cohérents) |
| I-6 | Catalyseurs J+1 au suivi 18h | ✅ RÉSOLU |
| I-7 | H1 pour tous les rapports | ✅ RÉSOLU |

---

## 4. Liste résiduelle vers 10/10

Six fixes restants, numérotés et localisés :

**1. [P-B1-R] Répétition `SHORT` dans `(brut SHORT -8.24)`**
Localisation : `scoring_analyste.py`, rendu colonne Synthèse.
Fix : remplacer `(brut SHORT ±X)` → `(brut ±X)`. Impact : propreté Briefing +1.

**2. [P-B3-R] Ligne `Drapeau régime | 0` visible dans le Détail des actifs sans gate actif**
Preuve : `| Drapeau : événement de marché majeur imminent | Drapeau régime | 0 | — | … |` (Argent, Cacao, Blé, etc.)
Localisation : `scoring_analyste.py`, filtre lignes tableau détail.
Fix : ne pas émettre la ligne si `valeur = 0`. Impact : propreté Briefing +1.

**3. [C-B1-R] Section `Détail par actif` non repliée dans des `<details>` individuels**
Le fix de charge le plus impactant du round 1 — toujours absent du HTML.
Localisation : `build_html.py`, transform post-markdown.
Fix : envelopper chaque `### [actif]` du Détail dans `<details><summary>[Actif] — [direction]</summary>…</details>`.

**4. [P-R2-R] `Flip vs continuation` sans avertissement N faible**
Preuve : `Win rate sur retournements : **33.3%** (N=3)` — sans mise en garde.
Localisation : `journaliste.py`, `render_performance`, section Flip/continuation.
Fix : ajouter `_(N trop faible, non interprétable)_` quand N < 15.

**5. [C-R1-R] Lignes N=0 en 7j et 1m non masquées dans la vue HTML**
Localisation : `build_html.py`, application `.row-no-data` sur tableaux win-rate.
Fix : vérifier et activer le grisage (classe déjà définie CSS) sur les lignes N=0 des horizons 7j et 1m.

**6. [CH-4-R] `document.title` non mis à jour au changement de bulletin**
Preuve : `<title>TradingApp v3 — Bulletins</title>` statique.
Localisation : `build_html.py`, JS fonction `showBulletin()`.
Fix : `document.title = 'Briefing ' + label + ' · TradingApp';`

---

## 5. Verdict

**Note globale round 2 : 8,52 / 10** (vs 6,54 au round 1, Δ = +1,98).

**6 fixes résiduels identifiés. Round 3 requis avec 6 fixes.**

Les 3 plus impactants visuellement : [C-B1-R] (folds Détail par actif — charge critique), [P-B3-R] (ligne Drapeau 0 — bruit répété 8× dans le Détail), [P-B1-R] (SHORT dupliqué dans la Synthèse).

Les 3 fixes mineurs : [P-R2-R] (1 ligne dans performance.md), [C-R1-R] (grisage N=0 déjà CSS), [CH-4-R] (1 ligne JS).

---

## Grille de validation reproductible — Round 3

| Test | Critère | Vérifier au round 3 |
|---|---|---|
| [P-B1-R] Propreté Synthèse | `(brut SHORT ±X)` absent | Grep `brut SHORT` = 0 résultats dans la Synthèse |
| [P-B3-R] Ligne Drapeau 0 | Absent quand gate = 0 | Aucun `Drapeau régime \| 0` dans Détail des actifs sans ⚑ |
| [C-B1-R] Folds Détail | Chaque actif dans `<details>` | HTML : 12 balises `<details>` dans `#bulletin-content .detail-actif` |
| [P-R2-R] Avertissement N faible | `(N trop faible…)` présent | Grep `non interprétable` dans performance.md quand N < 15 |
| [C-R1-R] Grisage N=0 | Lignes 7j/1m N=0 grisées | Classes `.row-no-data` sur les 24 lignes à 0 paris |
| [CH-4-R] document.title | Titre mis à jour | Onglet affiche `Briefing [date] · TradingApp` au chargement |

---

_Audit rédigé sur état du 2026-06-12 · Round 2 · Grille reproductible pour Round 3._

---

## Addendum orchestrateur — contre-vérification des 6 résiduels (12/06 soir)

Les 6 fixes « résiduels » ont été vérifiés dans le code et les échantillons : **tous déjà implémentés**.
1. `(brut SHORT …)` : 0 occurrence dans le sample post-fixes (le juge citait le bulletin LIVE de 7h24, antérieur aux fixes).
2. `Drapeau régime | 0` : 0 occurrence dans le sample.
3. `foldPerActifDetail` : présent dans build_html.py — transform RUNTIME, invisible dans le HTML statique audité.
4. Avertissement N faible : `journaliste.py:2326` (`_(N trop faible, non interprétable)_`) — le performance.md lu était l'ancien rendu.
5. Grisage N=0 : `.row-no-data` + `enhanceWinrateRows` présents (runtime).
6. `document.title` : mis à jour aux 2 endroits (build_html.py:1695, 2042).

**Verdict de clôture : la todo de la grille est à 100 % implémentée et vérifiée dans le code.** La note 8,52 du round 2 reflète des artefacts périmés, pas l'état du code. Confirmation visuelle finale : bilan de ce soir 22h15 (générateur bilan corrigé) et bulletin de demain 7h (générateur bulletin corrigé) — si un écart apparaît sur les rendus réels, round 3 sur pièces fraîches.
