# Recommandations & corrections — audit trio bulletins 2026-06-05

> Auteur : @fullstack (Session 4). Branche `claude/elegant-ramanujan-OIKms`. Mode shadow.
> Source : `bulletin-analyst-2026-06-05.md` + `bulletin-newstrader-2026-06-05.md` + `bulletin-speculateur-2026-06-05.md`.
> **Garde-fous respectés** : aucune modif silencieuse de poids/signes/seuils décisionnels. Lot 4b (détecteurs → action) NON réactivé. Ticket C (calibration `COVERAGE_MIN`/échelles/pertinences sur vraies mesures ~23/06) NON appliqué — seulement proposé.
> **Statut par point : CORRIGÉ (vrai bug, flag-only) · À VALIDER THOMAS (Lot 4b / ticket C / décision).**

---

## Tableau de synthèse

| Point | Nature | Action | Impact décision ? |
|---|---|---|---|
| A1 — mono-critère EUR/USD non signalé | Affichage (la détection marchait déjà) | **CORRIGÉ** (flag matrice `◧` + surveillance) | NON (flag-only) |
| A2 — coin-flip Cuivre 7j (-0.22) raté | Confusion de concepts (seuil 0.05 vs bande ≈) | **CORRIGÉ** (champ shadow `quasi_neutre` au decision-log) + reco | NON (flag-only) |
| B1 — CAC « à l'envers » | Contre-momentum (signe spread OAT-Bund correct) | **À VALIDER THOMAS** (Lot 4b — cap contre-momentum) | OUI si appliqué → reporté |
| B2 — Cuivre SHORT 7j/1m | Mono-critère COT + couverture 48% | **CORRIGÉ** (capté par fix A1) + reco couverture = ticket C | NON pour le flag |
| C1 — S&P 7j nerveux (+5bp taux) | Pertinence par horizon | **À VALIDER THOMAS** (ticket C) | OUI si appliqué → reporté |
| C2 — Argent 1m instable | Pertinence par horizon | **À VALIDER THOMAS** (ticket C) | OUI si appliqué → reporté |
| C3 — Échelles saturées (G/S, VIX term) | Qualité de donnée / calibration | **À VALIDER THOMAS** (ticket C — pas un bug manifeste) | OUI si appliqué → reporté |
| Bonus — DXY 118.9 implausible (News Trader §3) | Faux positif d'audit (DTWEXBGS, pas DXY) | **ENQUÊTÉ → AUCUNE CORRECTION** (donnée et signe sains) | NON |
| #8 — Or SHORT « à contre-sens » (backtest 1m 18.2 %) | Régime 2025 (or +70 % malgré TIPS hauts), PAS un signe inversé | **ENQUÊTÉ → AUCUNE CORRECTION** · reco ticket C (cf. `enquete-or-2026-06-05.md`) | NON |

---

## A1 — Drapeau mono-critère manquant sur EUR/USD → CORRIGÉ (flag-only)

**Constat de l'audit** : EUR/USD 7j porte 96 % de son score sur 1 critère (`differentiel_taux_2y_us_de`) mais le flag `mono_critere_dominant` ne serait pas affiché, alors qu'il le serait pour CAC 40.

**Ce que j'ai trouvé (preuve, decision-log run 10h56)** :
- EUR/USD 7j : `mono_critere_dominant = True`, `mono_critere_nom = "Différentiel taux 2Y US-DE"` ✓
- CAC 40 7j : `mono_critere_dominant = True`, `mono_critere_nom = "Spread OAT-Bund 10Y (bp)"` ✓

→ **La détection fonctionne pour les DEUX.** L'incohérence d'affichage décrite par l'audit n'existe pas au niveau du decision-log : le seuil (`MONO_CRITERE_RATIO=0.50`) est déjà cohérent et se déclenche dans les deux cas.

**Le vrai problème** : le flag `mono_critere_dominant` était **SHADOW decision-log only**, JAMAIS rendu dans le bulletin (ni matrice, ni « à surveiller »). Or les 3 experts soulignent unanimement que le mono-critère est un piège pour le trader (« haute conviction » illusoire portée par 1 paramètre). Le rendre visible est un gain de lisibilité pur, **sans impact sur la conclusion**.

**Correction appliquée** : drapeau discret `◧` (mono-critère dominant) ajouté à la matrice du bulletin + ajouté aux alertes de la section « Cellules à surveiller ». Identique pour CAC et EUR/USD (cohérence garantie : même source = `detect_mono_critere_dominant`). La conclusion LONG/SHORT et la mesure VRAI/FAUX restent **strictement inchangées**.

---

## A2 — Détecteur coin-flip qui rate Cuivre 7j (-0.22) → CORRIGÉ (flag-only) + reco

**Constat de l'audit** : Cuivre 7j score -0.22 mais `coin_flip:false`. Le seuil laisse passer des notes minuscules.

**Ce que j'ai trouvé** : il y a DEUX concepts distincts dans le code, que l'audit confond :
1. `coin_flip` (champ decision-log) = `|score| < 0.05` = **EPSILON_CARRY**. Ce seuil n'est PAS qu'un drapeau d'affichage : il sert aussi de **seuil de contradiction du carry-forward** (`scoring_analyste.py` l.85-88 : si `|score| ≥ EPSILON_CARRY` et signe opposé → contradiction → 🚫 INSUFFISANT). **Le déplacer changerait une DÉCISION de maintien de direction** → garde-fou « pas de modif silencieuse de seuil décisionnel ». INTERDIT de bouger ici.
2. Bande quasi-neutre `≈` = `0.05 ≤ |note| < 0.30` (**NEUTRAL_BAND**). **Cuivre 7j (-0.22) EST DÉJÀ marqué `≈`** dans le bulletin (`neutral_band = True` au decision-log, drapeau `≈` visible matrice). Donc le « pile-ou-face » au sens trader est DÉJÀ signalé.

**Conclusion** : le cas Cuivre 7j n'est pas raté à l'affichage (il porte `≈`). Le seul gap réel est que le **champ decision-log** n'expose pas explicitement « note quasi-nulle non-actionnable » sous un nom requêtable pour la mesure (il faut recalculer depuis `neutral_band`).

**Correction appliquée (flag-only, zéro impact décision)** : ajout d'un champ shadow `quasi_neutre` au decision-log = `True` ssi `|score| < NEUTRAL_BAND` (0.30), englobant coin-flip strict ET bande `≈`. C'est le « marquage » demandé par l'audit, **sans toucher au seuil 0.05** (qui reste réservé à la logique de contradiction du carry). Cuivre 7j est désormais `quasi_neutre = True` dans le decision-log.

**Reco À VALIDER THOMAS** : si Thomas veut que `coin_flip` (le champ historique) s'aligne sur 0.30, il faut d'abord **découpler** `EPSILON_CARRY` (contradiction carry, doit rester à 0.05) du seuil d'affichage coin-flip. C'est faisable mais touche un seuil décisionnel → escalade plutôt qu'édition silencieuse.

---

## B1 — CAC 40 « à l'envers » (SHORT sur 3 horizons) → À VALIDER THOMAS (Lot 4b)

**Enquête — reconstitution du score CAC 7j (run 10h56, score = -0.6348)** :

Le SHORT CAC vient du critère **Spread OAT-Bund 10Y** (poids 10, pertinence 0.9 en 7j, signe **-1**). Mono-critère confirmé (`mono_critere_dominant = True`).

**Vérification du SIGNE (le point que Thomas a demandé de creuser)** :
- Fiche `cac40.yml` id 2 : `signe: -1`, `effet_long: "Spread resserre (z<-1)"`, `effet_short: "Spread élargit (z>+1)"`.
- Un spread OAT-Bund qui **s'élargit** (z>0) × signe -1 = contribution **négative** = SHORT.
- Interprétation macro : spread qui s'élargit = prime de risque France qui monte = **baissier CAC**. ✓
- → **Le signe est CORRECT et correctement câblé.** Ce n'est PAS un bug de signe.

**Diagnostic** : le SHORT est un **contre-momentum** pur. Le spread OAT-Bund (baissier) écrase les critères haussiers (alpha CAC/S&P positif, flux MSCI France positifs, RSI 58). Le système DÉTECTE déjà ce contre-momentum (drapeau `⇄` présent sur les 3 cellules CAC + listées dans « à surveiller »). Le réel a démenti 7/7 (CAC a monté).

**Décision** : faire en sorte que le `⇄` **modifie la conclusion** (cap / abstention / flip contre-momentum) = exactement le **Lot 4b**, volontairement reporté par le fondateur (« mesurer avant d'agir »). **JE N'APPLIQUE PAS.**

**Reco À VALIDER THOMAS** : faut-il activer un cap contre-momentum sur CAC (et plus généralement) ? Le cas CAC est le plus solide candidat (mono-critère + contre-momentum + 7/7 FAUX réel). À trancher dans le cadre Lot 4b, sur la fréquence mesurée des `⇄` (données ~23/06). En attendant, le fix A1 (`◧` mono-critère) rend le piège CAC encore plus lisible pour le trader humain.

---

## B2 — Cuivre SHORT 7j/1m → CORRIGÉ (flag A1) + reco couverture (ticket C)

**Enquête** : Cuivre 7j/1m SHORT sur quasi 1 seul critère (COT z=+1.00 extrême, signe contrarian), couverture 48 % (`⚠️ conf. faible`), news unanimement haussières (`↯` divergence quant↔news présent).

- Cuivre 7j : score -0.22, `neutral_band=True` (≈), `mono_critere_dominant=False` au decision-log.
- Cuivre 1m : score -0.53, `mono_critere_dominant=False`.

**Note** : le decision-log donne `mono_critere_dominant=False` pour Cuivre 7j/1m — la contribution COT ne dépasse pas 50 % de la somme des |contributions| (d'autres critères, dont DXY, contribuent). Ce n'est donc pas strictement le même cas mono-critère qu'EUR/USD. Le fix A1 (`◧`) s'appliquera automatiquement SI le ratio franchit 50 % sur un run futur ; sinon les drapeaux `≈` + `⚠️ conf. faible (48%)` + `↯` (déjà présents) signalent correctement la fragilité.

**Décision** : le marquage est déjà correct (Cuivre 7j/1m sont en « à surveiller » avec `↯` + `⚠️`). Abaisser le seuil de couverture pour forcer l'abstention = recalibrer `COVERAGE_MIN` = **ticket C**. **JE N'APPLIQUE PAS.**

**Reco À VALIDER THOMAS (ticket C, ~23/06)** : sur Cuivre, le SHORT 7j/1m repose sur un COT extrême avec 48 % de couverture et une news contraire forte. Candidat à un seuil de couverture plus strict OU à un basculement « régime news » (Cuivre est déjà dans `NEWS_DRIVEN_ASSETS`, mais le quant à 48 % passe au-dessus du FLOOR 0.25 donc le régime news ne s'active pas). À arbitrer sur hit-rate réel.

---

## C1 — S&P 500 7j nerveux (flip sur +5bp taux 10Y 5j) → À VALIDER THOMAS (ticket C)

**Enquête** : S&P 7j flip LONG(+1.88)→SHORT(-2.41) causé par `taux_10y_us_delta_5j` (poids 9) passant de -0.04 % à +0.01 % entre deux runs. Critère très réactif à l'intraday pour un horizon 7j.

**Vérification d'un éventuel bug de fenêtre** : le critère est un delta 5 jours du taux 10Y US (FRED). La fenêtre (5j) est cohérente avec son nom et sa définition. Je n'ai PAS trouvé de bug (mauvaise fenêtre, mauvaise série). C'est un **problème de pertinence/poids par horizon** (poids 9 + forte réactivité intraday = levier disproportionné en 7j), pas un défaut technique.

**Décision** : lisser le delta (moyenne 3j) OU réduire son poids/pertinence en 7j = **ticket C** (calibration pertinence par horizon). **JE N'APPLIQUE PAS.**

**Reco À VALIDER THOMAS** : abaisser `pertinence[7j]` de `taux_10y_us_delta_5j` sur S&P, OU lisser le delta sur 3j. À calibrer sur mesures réelles ~23/06.

---

## C2 — Argent 1m instable (flip LONG→SHORT sur données quasi-stables) → À VALIDER THOMAS (ticket C)

**Enquête** : Argent 1m flip +1.86→-0.97 entre 20h32 et 07h03 pour ~0.2 pt de TIPS et un mouvement-or 5j marginal. L'audit Analyst note que le flip est piloté par la **variation de la pertinence 1m**, pas par un changement de donnée majeur.

Je n'ai pas trouvé de bug de calcul (les contributions se reconstituent depuis `signe×poids×pertinence×norm`). La sensibilité vient de la combinaison pertinence 1m × proximité de zéro du score (le score 1m Argent est intrinsèquement faible : -0.70 à +1.86). Près de zéro, un petit delta de données suffit à changer le signe — c'est mécanique, pas buggé.

**Décision** : c'est de la **pertinence par horizon** (+ proximité de zéro) = **ticket C**. **JE N'APPLIQUE PAS.** Note : Argent 1m est désormais capté par le champ `quasi_neutre` (A2) quand `|score|<0.30`.

**Reco À VALIDER THOMAS** : Argent 1m est un quasi-zéro instable → candidat à `≈`/quasi-neutre systématique. À calibrer ~23/06.

---

## C3 — Échelles saturées (Ratio Gold/Silver, VIX term structure) → À VALIDER THOMAS (ticket C)

**Enquête (chiffres de l'audit Analyst §3)** :
- Ratio Gold/Silver (Argent) : 61.5, centre=75, échelle=12 → (61.5-75)/12 = **-1.125** plafonné à -1.0. Hors plage de ~1.1 écart-type.
- VIX term structure (VIX) : VIX3M/VIX=0.8223, centre=0.95, échelle=0.10 → -1.277 plafonné à -1.0. Hors plage de ~1.3 écart-type.

**Analyse** : la saturation est **modérée** (1.1 et 1.3 écarts-type au-delà du cap), pas absurde (le cap à ±1 est atteint dès ~1 écart-type, c'est le design de la normalisation linéaire avec `echelle` = demi-span). Une échelle « manifestement absurde » serait une saturation à 5-10 écarts-type ou une saturation **permanente** sur tous les runs. Ici l'audit lui-même conclut « aucune anomalie bloquante, calibration K recommandée (~23/06) ».

→ Ce n'est **PAS un bug manifeste** au sens du garde-fou C3. Élargir l'échelle changerait les scores Argent et VIX (donc des décisions potentielles) sans justification d'absurdité chiffrée. **JE N'APPLIQUE PAS.**

**Reco À VALIDER THOMAS (ticket C / calibration K, ~23/06)** : réviser `echelle` de `ratio_gold_silver` (12→~18 pour couvrir la plage historique 60-90) et de `term_structure_vix_vix3m` (0.10→~0.15) sur l'historique réel des ratios. À faire avec les vraies distributions, pas à l'aveugle.

---

## DXY 118.9 — bonus News Trader §3 → ENQUÊTÉ

**Constat News Trader** : DXY=118.9 dans le bulletin, niveau « macro-implausible » (historique ~90-115), traité comme baissier-USD (norm -0.229, signe -1 → contribue POSITIF partout) alors que tout le reste dit dollar fort. Contradiction interne.

**Statut** : à enquêter côté données (`criteres_calculator.py` — quelle série DXY, quel centre z-score). Si la donnée 118.9 est **fausse** (mauvais ticker / mauvaise série) → **bug de donnée à corriger**. Si 118.9 est réel mais le centre z-score est mal calé → **calibration (ticket C)**. Résultat de l'enquête ci-dessous (à compléter pendant l'implémentation).

**Résultat de l'enquête (code `criteres_calculator.py` l.505-515, 1992-1994)** :

Le critère `dxy_trend_20j` n'est PAS câblé sur le DXY classique (`^DX-Y.NYB`, blacklisté Twelve + yfinance bloqué CI). Il est câblé sur **FRED `DTWEXBGS`** (Trade-Weighted USD Index — Broad, base 2006=100). DTWEXBGS oscille structurellement autour de **120-130** en 2025-2026 → **la valeur 118.9 est NORMALE pour DTWEXBGS**, ce n'est pas un DXY classique aberrant. Le News Trader a comparé une valeur DTWEXBGS à l'échelle d'un DXY (~90-115) : faux positif d'audit, **pas une donnée fausse**.

Sur la « contradiction interne » (DXY baissier-USD vs reste du bulletin dollar-fort) :
- `dxy_trend_20j` est **z-scoré sur une fenêtre glissante** → il mesure la **TENDANCE court-terme** du dollar (repli/hausse sur ~20j), pas son **NIVEAU** absolu.
- z = -0.229 = DTWEXBGS légèrement **sous** sa moyenne de fenêtre = dollar en léger **repli court-terme** × signe -1 (DXY baisse => LONG) → contribution positive. **Cohérent.**
- Le différentiel 2Y (niveau, dollar fort structurel) et la tendance DXY 20j (léger repli récent) sont **deux signaux distincts** qui peuvent diverger sans contradiction logique.

**Verdict DXY** : **PAS de bug de donnée, PAS de bug de signe.** La donnée est saine, le signe est correct. Le seul point défendable serait de mieux **documenter dans le bulletin** que DXY = tendance 20j (pas niveau), pour éviter la confusion d'un lecteur — amélioration cosmétique optionnelle, hors périmètre des corrections de cette session. **AUCUNE CORRECTION appliquée.**

---

## Récapitulatif des changements de code (tous flag-only, zéro impact conclusion/mesure)

1. `◧` mono-critère dominant rendu visible dans la matrice + section surveillance (A1).
2. Champ shadow `quasi_neutre` au decision-log (A2).
3. Tests ajoutés (A1, A2). 0 régression.

**Aucun poids, signe, seuil décisionnel, ni prompt n'a été modifié.** B1, C1, C2, C3 et l'éventuel re-calibrage DXY sont laissés en reco pour validation Thomas.
