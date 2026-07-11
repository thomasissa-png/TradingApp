# CHANGELOG — TradingApp v3

> Historique des sessions de travail (le plus récent en haut). Détail technique : `git log` + `v3/audit/`.

## 2026-07-11 — S11 : autopsie de la semaine 06-10/07 + 3 sondes shadow « tendance mûre » (GO fondateur)

Audit intégral de la semaine (Top 3 : 3/12 en métrique turbo, direction 4/7 à l'échéance, 12 pertes évitées par les écartements ↯ en 3 jours) puis autopsie du sujet fondateur « plus c'est monté, plus ça corrige » : panel des 3 experts + données 23/06→10/07.

### Verdicts du panel (v3/audit : synthèse en chat, données decision-log × measures-log, N=56)
- L'intuition n'est PAS supportée en direction (pire segment = tendance moyenne, pas saturée ; échantillon saturé = un épisode café corrélé). Les vrais risques : **flips 1/6** (déclenchés PAR le mouvement extrême, donc à contretemps : café flip SHORT le 09/07 pile le +12,3 %, re-LONG le 10/07 pile le -2,9 %) et **asymétrie d'ampleur** (cacao 10/07 : conviction record +12.31, max favorable +0,01 %, max adverse **-9,28 %** : barrière de turbo = 100 % de la mise). Signal d'épuisement déjà en base (plus de news structurel fraîche, news auto-référentielles, ⌛, COT extrême). Angle mort structurel : le penchant 3j est plafonné à ±1, l'ampleur déjà parcourue est effacée.

### 3 sondes SHADOW livrées (observabilité pure, zéro changement de signal, verdicts à N≥15)
- **Confirmation post-flip** : `shadow_flip_j0` / `shadow_flip_conf` au decision-log (WR flips J0 vs confirmés).
- **Catalyseur épuisé** : `shadow_cat_epuise` / `shadow_sens_fond` (3j saturé seul contre news+7j+20j : qui avait raison ; cas fondateurs café 09/07 et cacao 10/07 rejoués en tests).
- **Taux de KO virtuel** : `ko_virtuel` / `pari_mur` au sortie-timing-log (-3 % touché avant +1 %, segmenté paris mûrs ⌛ vs frais, KO_VIRTUEL_PCT=3.0 à recalibrer sur preuve ; `pari_mur` = proxy deja_cote documenté). Ligne 🧨 au bilan du soir + 3 compteurs au bilan hebdo.
- Suite complète : **2055 verts / 34 skips / 0 rouge**, v3/data intact.

## 2026-07-03 — S11 (fin) : audit de pertinence du bulletin + positions ouvertes + capteurs réellement branchés

Audit de pertinence du bulletin 03/07 (jour du NFP) : « est-ce ce dont on a besoin ? ». 7 points validés fondateur, tous livrés, + les vraies causes racines des capteurs muets.

### Pertinence du bulletin (7 points)
- **Alerte catalyseur J0 sur les paris** (« 🔴 NFP à 14h30 : Argent traverse l'annonce », drapeau jamais un ordre) ; **news pré-publication marquées** (fin du « NFP décevant » affiché à 7h23 pour un chiffre de 14h30) ; **flips de bruit** étiquetés et relégués ; **phrase dollar dédiée USD/JPY** (résolution par actif dans la biblio, 2 phrases latentes signalées) ; **Santé des sources reléguée** après les sections de décision.
- **📌 Positions ouvertes (Swing 7j / 1m)** : état persisté au decision-log (record dédié), reconstruction depuis le 30/06 (8 positions dont EUR/USD 1m SHORT pris 30/06 à 1.13861), % courant vs la VRAIE entrée, clôture au retournement, fin des entrées réimprimées chaque matin. Refactor structurel en cours de route : le record d'état vit à la PERSISTANCE, `build_decision_log_records` garde son contrat cellules-only (20 KeyError attrapés par la suite complète, réparés d'un coup).
- Reste en décision fondateur : pari « fragile (1 seul critère) » inéligible à la Sélection (reco : oui).

### Capteurs (causes racines prouvées sur logs)
- **Stamp US** : aucun run ne tombait dans [15h40, 17h[ (VPS 15h15 trop tôt, ticks GitHub retardés ~2h routés suivi) → filet stamp avant le suivi 18h + fetch des indices via proxies SPY/QQQ/VIXY (les ^ sont yfinance-only, bloqué CI).
- **USDA** : la clé n'était consommée NULLE PART → handler NASS QuickStats implémenté (z-score stocks blé trimestriels, écart WASDE documenté) ; **hors-fenêtre = n/a propre** (le placeholder 0.0 pseudo-présent neutralisait le garde-fou capteurs éteints, cas Blé pari n°3 le 03/07) ; cutover Blé → 04/07.
- Gel Mouvements complété (le sortie-timing re-persisté au prix courant dérivait, priorité au realized daté) ; ⚠️ max suspect propagé jusqu'au « Gagné > 1 % » ; paris perdants sortis des « Occasions manquées ».
- Suite complète : **2024 verts / 34 skips / 0 rouge**, v3/data intact.

## 2026-07-02 — S11 (suite) : bilan hebdo + Mouvements de marché audités/corrigés, dette apurée à zéro (GO fondateur)

Poursuite des audits surface par surface (« même travail ») puis apurement TOTAL de la dette sur ordre fondateur (« ne laisse aucune dette »).

### Bilan hebdomadaire (8 corrections, audit S26)
- Colonne « Mouvement 24h réel » (realized/outcome du measures-log, fin de la perf de phase recopiée : le « Cacao +13,6 % » du S26 était la phase mar→ven affichée comme mouvement du jour) ; « Opportunités ratées » sur le jour d'émission (un pari Top 1 ne peut plus y figurer « non classé ») ; learnings recalculés et doctrine-aware ; « Win rate par conviction » compté depuis les picks persistés (le N=0/0 venait d'une classification sur mesure live) ; sous-section « Mesures shadow en cours (reco 28/06) » ; dédup ; wording ; zéro cadratin. Puis : dead code `_conviction_semaine` retiré, **cumul Top 1/Top 3 instrumenté** (`performance/weekly/selection-wr.jsonl`, idempotent).

### Page « Mouvements de marché » (7 corrections)
- **🐛 P0 : historique figé.** Le « % clôture » des jours passés était recalculé chaque matin au prix courant (café 29/06 : +8,52 % puis +13,42 % selon le jour de lecture ; lignes qui apparaissaient/disparaissaient rétroactivement via le filtre > 1 %). Désormais : realized favorable de la cellule 24h datée, figé, test anti-dérive à deux générations. Max du jour câblé, raison honnête dédupliquée, conviction libellé+note, colonne Résultat ✅/❌/⚪, zéro cadratin.

### Apurement de dette (registre vidé)
- **Suivi** : justification UNIQUE bulletin↔suivi (le bulletin persiste `selection_raison` au decision-log, le suivi l'affiche verbatim) ; **% Sélection vs prix d'émission 7h (L027)** avec snapshot base-entrée dédié, puis **base émission unifiée** jusqu'au bout (suivi-tracking marqué `base:"emission"`, bilan/hebdo refusent le mélange de bases, « — » sur snapshots antérieurs).
- **Tests** : les 3 rouges pré-existants élucidés (tous des évolutions documentées : flag stale v2.2, cutover 30/06, reweight horizons) ; 22 échecs environnementaux (pandas/holidays absents du conteneur) → skips ciblés motivés, couverture CI intacte (deps prouvées dans requirements + workflows) ; **fin de la pollution de `v3/data/` par les tests** (writers à chemin dynamique + fixture autouse + filet de session qui nomme le test fautif).
- **Mesure** : garde-fou `prix_suspect_stale` (close fournisseur strictement identique au jour précédent, cas coton 2.371 les 29-30/06) → ⚠️ affiché au bilan, outcome jamais modifié.
- Cutovers réalignés sur la réalité du déploiement : EUR=X et ZW=F avancés au 2026-07-03 (le merge est arrivé APRÈS l'émission 7h du 02/07, discipline anti-mélange) ; COTN/CANE restent au 02/07.

## 2026-07-01 (soir) — S11 : audit des suivis 12h/18h + clé USDA + ouverture US réparée (GO fondateur)

Audit fond+forme des rapports `suivi/2026-07-01-12h.md` et `-18h.md`, 11 améliorations validées fondateur, 9 livrées le soir même (2 reportées avec justification). Effectif au suivi du 02/07 12h.

### Capteurs et mesure
- **Clé `USDA_API_KEY` posée par le fondateur** (vérifiée valide sur l'API NASS) → le critère stocks blé (poids 11) ressuscite ⇒ **cutover Blé** (`ZW=F` → 2026-07-02, addendum SELECTION-RULE).
- **Ouverture US enfin captée** : cause racine prouvée (l'unique tick post-15h35 est souvent retardé de 1-3h par GitHub et tombait hors de toute fenêtre de routage → stamp US silencieusement raté les 30/06 ET 01/07). Fix : fenêtre de rattrapage ph==16 + nouvelle ligne cron `42 13-15 UTC` (été comme hiver, sans churner les crons existants). Idempotent, un 15h42 réussi garde priorité.
- **Coton/Sucre reclassés groupe horaire US** (ETF COTN/CANE cotés bourse US, étaient traités en continus : faux neutres à midi, suivi-interrompu en série) ⇒ cutover `COTN`/`CANE` → 2026-07-02 (impact quasi nul, warm-up N=0 depuis le 30/06).

### Bilan 22h15 (8 corrections, audit du bilan réel du 01/07)
- **🐛 P0 : « Max gain jour » unifié** : la section 1 (qui décide Gagné > 1 % et nourrit le Top 1/Top 3) consommait le high/low de bougie 1day (gonflé : Cacao +1.88 % vs +0.42 % réel), l'annexe l'excursion 1h fidèle aux suivis. Source unique = excursion favorable (garde-fou anti-tick hérité du suivi). ⚠️ Le WR Sélection cumulé d'avant le 02/07 (6-14 paris) contenait des max gonflés : **signalé, historique non réécrit**.
- **🐛 P0 : bloc « Sortie » adossé aux suivis réels** (il citait « le suivi disait Vendre » sur un pari où le 12h réel affichait « Laisse courir ») : l'action réellement affichée est reproduite depuis suivi-tracking, « non tracée » sinon.
- Learnings alignés doctrine (fin de « capter la news plus tôt », occasion manquée = règle exacte d'exclusion citée) ; nouvelle sous-section « Écartés qui ont évité un FAUX » (les garde-fous crédités : cas Nasdaq 01/07 écarté ↯, fini -1.40 %) ; « Ce qu'on doit améliorer » → « Occasions manquées (hors Sélection) » sans phrasé circulaire ; % favorable signé partout dans le narratif (légende Delta% brut explicite à l'annexe) ; « gagné au max intraday, refermé à X % » ; zéro cadratin.

### Suivis 12h/18h (7 corrections rendu/logique)
- **Δ précédent et Tendance ↑↓⇄ recalés sur le % favorable signé** (bug de signe : Argent affichait « +4.00 pts » quand la position perdait 4 points ; convention FIX 3 du 23/06 enfin appliquée partout).
- **Garde-fou max gain suspect** (plafond seuil_24h × 5 → « ⚠️ à vérifier ») : le « Blé +7.93 % » venait d'un tick aberrant (~633) avalé sans borne par le calcul d'excursion.
- **« 🕐 pas encore ouvert »** pour les ETF US non cotés (fin du faux « +0.00 % neutre » du Sucre à midi).
- **Panorama sans ordres** : colonne Action remplacée par « Call : ✅ intact / ✖ cassé » ; Coupe/Sécurise/Tiens réservés aux 3 paris détenus (décision fondateur 23/06 rétablie) + message de cohérence sous « Suggestions de sortie ».
- **News à contre-sens marquée** « (à contre-sens du pari) » + fallback vers les grosses actus quand la ligne pari est vide ; conviction = libellé + note « forte (+8.77) ».
- **Reportés (planifiés, risque de régression pipeline-wide)** : alignement textuel des justifications bulletin↔suivi ; % Sélection contre le prix d'émission 7h (aujourd'hui vs ouverture stampée, écart faible mais réel).

## 2026-07-01 — S11 : audit complet du bulletin + implémentation intégrale (GO fondateur)

Audit fond+forme du bulletin 2026-07-01-07h (trio + avis orchestrateur), 24 améliorations validées fondateur, toutes livrées le jour même. Effectif au bulletin du 02/07 7h.

### Règles de sélection (restrictives, zéro cutover)
- **Véto « news contre la tendance courte »** : un pari 24h dont le driver dominant est la news et dont la tendance 3j est à contre-sens est écarté de la Sélection (cas de référence : Cacao LONG du 01/07). Motif visible dans « Écartés ».
- **Plancher d'intensité** `SELECTION_INTENSITE_MIN = 0.30` (calibré sur la distribution réelle des decision-logs 23/06→01/07) : on ne force jamais un pari mou ; moins de 3 paris = normal.
- **Conviction plafonnée « fragile (capteurs éteints) »** : critère de poids max n/a OU ≥2 critères de poids ≥8 n/a → cellule inéligible à la Sélection (cas Blé, stocks USDA morts).

### Ticket C — frein des capteurs non-tendance sur le 24h (cutover EUR/USD seul)
- Le reweight du 30/06 avait déjà mis les structurels à pertinence 24h 0.1 ; seul retardataire : `usd_jpy_proxy_risk` (EUR/USD) 0.7→0.1. Effet 01/07 : EUR/USD 24h SHORT→LONG ⇒ signal change ⇒ `ref_changed` EUR=X au 2026-07-02. CAC 40 vérifié conforme (aucun changement). Addendums SELECTION-RULE + KILL-CRITERION.
- **Signe météo cacao** : symétrie validée S8 confirmée conforme au code ; mention « convention de signe à valider » retirée des raisons affichées.

### Capteurs
- 🐛 **PMI Caixin** : le placeholder hors-fenêtre émettait une valeur dégénérée (0.0 sans valeur brute) → « n/a (valeur non numérique) » au bulletin et pollution de criteres-last-good. Fix : handler dédié systématique, n/a propre. Aucun impact score. V2X/VXN/stocks/or-BC : sources absentes assumées (n/a propres), clé USDA = action fondateur.

### Rendu du bulletin (17 points, présentation pure)
- Raison d'un pari toujours adossée à un **titre de news réel** (fin du « pas de titre représentatif ») ou au premier driver concret ; « Porté par » jamais à contre-sens ; paradoxe net/top-titre expliqué en parenthèse.
- « Note » (chiffre) ≠ « Conviction » (libellé) ; « forte » exige |intensité| ≥ 0.30 sinon « modérée (signal peu net) » ; « (écarté des paris) » affiché sur les lignes concernées.
- « Cellules à surveiller » réduite à Sélection + flips ; **table Intensité supprimée** (sa valeur vit dans le libellé de conviction, la Synthèse reste la table centrale) ; légende complète (⚠️♻) + test anti-symbole-orphelin ; note ⌛ sous les paris ; colonne **Objectif** (seuil 24h signé) ; formes humaines (« valeur 2.15, la hausse pousse à la baisse ») ; noms de critères sans tiret cadratin ; « prix de référence approximatif ».

### Dette repérée
- Des tests écrivent dans les vrais chemins `v3/data/` quand la suite tourne (pollution nettoyée avant chaque commit) → à isoler (tmp_path) lors d'une prochaine session.
- Tests `test_twelve_native_remap` rendus robustes aux resets ultérieurs (cassés depuis le 30/06, pré-existant vérifié).

## 2026-06-23 — Futures US le matin (Phase 1) : fetch VPS + lecture suivi

Le matin, le cash US est fermé (ouvre 15h30) et Twelve Data ne sert AUCUN future
CME (ES=F/NQ=F vides), yfinance bloqué sur les runners GitHub. Solution : un fetch
des futures depuis une IP non bloquée (le VPS) qui écrit un fichier, lu par le
cycle (GitHub Actions). Phase 1 = CÔTÉ REPO uniquement. Aucune touche au scoring /
matrice / conclusions / sélection / bilan. WIN RATE ONLY.

### A — Nouveau script `v3/scripts/fetch_us_futures.py`
- Fetch yfinance de ES=F (S&P 500) et NQ=F (Nasdaq). VIX hors Phase 1.
- Append d'un snapshot horodaté dans `v3/data/futures-us/{YYYY-MM-DD}.json` :
  dernier prix par ticker (top niveau) + série `snapshots` (1er snapshot = réf).
- Best-effort TOTAL : yfinance KO/vide → n'écrit RIEN (zéro fichier vide, zéro
  invention), log + exit 0. Conçu pour tourner sur le VPS (cron). Le commit/push
  est délégué au wrapper VPS (câblage séparé).

### B — Intégration suivi (`run_suivi.py`)
- Quand le cash US est fermé (`us_pas_ouvert`) ET qu'un prix future FRAIS (ts ≤
  30 min) existe : statut « 🔵 via future ES=F/NQ=F » au lieu de « cash fermé ».
- % calculé FUTURE vs FUTURE (snapshot courant vs 1er snapshot du jour) → échelle
  cohérente, JAMAIS mélangé avec un proxy cash. Favorable signé par le call.
- Fichier absent/périmé → repli « 🕐 cash fermé (ouvre 15h30) » inchangé.
- VIX reste « cash fermé » (pas de future Phase 1).

### Tests
- `tests/test_fetch_us_futures.py` (NOUVEAU, 6 tests, fetcher injecté, zéro réseau).
- `tests/test_run_suivi.py` : +3 tests (via future frais / périmé / échelle), test
  « cash fermé » existant adapté (dir futures dédié vide) — reste vert.
- Résultat : `test_fetch_us_futures` + `test_run_suivi` + `test_build_html*` =
  98 passed (baseline : pandas/holidays absents de l'env, inchangé).

### Reste à câbler (Phase 1bis, VPS) — hors repo
- Wrapper cron VPS : `python v3/scripts/fetch_us_futures.py && git add
  v3/data/futures-us && git commit -m "data: futures US snapshot" && git push`.

## 2026-06-23 — Suivi 12h/18h : 4 fixes de rendu (cohérence sorties, news, signe, légende)

Audit du rendu du suivi (`run_suivi.py`) sur le rapport réel `2026-06-23-12h.md`,
4 corrections validées fondateur. Aucune touche au scoring / matrice / conclusions
/ `load_selection_map` : RENDU uniquement (+ 2 helpers purs). WIN RATE ONLY.

### FIX 1 — sorties cohérentes et limitées aux 3 paris
- Le bloc « Suggestions de sortie » ne porte QUE sur les paris du jour
  (`selection=True`) — plus aucune suggestion sur un actif non détenu (Blé/Pétrole
  ne sont plus listés). AVANT : suggestions sur tous les actifs 24h.
- Source de vérité UNIQUE des verdicts : `vendre_from_suggestion(suggestion)` →
  la colonne « Vendre ? » de la table Sélection == le bloc Suggestions (mêmes
  seuils 0.80/1.00, mêmes verdicts, jamais l'un « vendre » et l'autre « tenir »).
  AVANT : `compute_vendre` (heuristique reflux) divergeait du seuil.
- Le panorama « Positions du matin » perd sa colonne « Vendre / Pas vendre » (on
  ne détient pas ces 12 actifs — c'est un panorama de marché).

### FIX 2 — section news centrée paris + grosses actus conservées
- « News des paris du jour » : VRAI titre de la news dominante par pari
  (`news_reelle_paris`, source events-log, même que `news_majeures`), plus jamais
  « Synthèse news (net, IA) ». Pas de titre exploitable → « — » (zéro invention).
- « Grosses actualités depuis Xh » : GARDÉ — high matérialité depuis le créneau
  précédent, MÊME hors top 3 (ex. Pétrole/Ormuz, demande fondateur).
- SUPPRIMÉS du rendu : « Contexte news (Synthèse net IA) » (actifs non-paris) et
  « Actus du jour » (titres RSS bruts de faible matérialité). La récolte RSS reste
  active pour la dédup/snapshot mais n'est plus affichée.

### FIX 3 — convention de signe unique (% favorable signé par le call)
- Le panorama « Positions du matin » affiche désormais le `% favorable` signé par
  le call (`+`=gagne / `-`=perd), comme la table Sélection. AVANT : delta brut →
  signes opposés pour le même actif (EUR/USD +0,23 vs -0,23 ; Or -0,06 vs +0,06).

### FIX 4 — légende courte
- 1 phrase : « Vendre = sortir maintenant ; % favorable +=gagne/−=perd ;
  Meilleur/Pire = excursion max depuis l'ouverture. » AVANT : pavé 4 lignes.

### Portée + tests
- S'applique automatiquement au 12h ET au 18h (même `build_suivi`). Le 18h
  conserve la dynamique US (`Δ précédent`, tendance `↗/↘ US`, Catalyseurs J+1) :
  vérifié par rendu manuel + tests.
- `run_suivi.py` : +`vendre_from_suggestion`, +`news_reelle_paris`, +champ
  `SuiviRapport.news_paris`. Tests : 98 PASS (test_run_suivi, test_suivi_news_fraiches,
  test_build_html_reports, test_cycle_build_html_ordering, test_cacao_choc_offre_16_06,
  test_porte_par_news_reelle). Régressions baseline hors-périmètre : `pandas`/
  `holidays` absents du conteneur (test_backtest, etc.) — inchangées par ce lot.

## 2026-06-23 — UNE seule sélection du jour, partout (tête == decision-log == suivi)

Bug de cohérence majeur (fondateur) : le suivi 12h traquait des positions
DIFFÉRENTES des paris affichés dans la tête « 🎯 Aujourd'hui ». Cause racine :
DEUX fonctions de sélection coexistaient. La tête (`select_paris_du_jour`,
Option C : top 3 convictions 24h jouables, |note| desc, ↯ news-à-contre-sens
exclus) affichait une sélection ; mais le champ `selection_du_jour` du
decision-log était écrit par l'ANCIENNE `compute_selection_du_jour` (dédup
famille macro + veto « tape ») — donc run_suivi / bilan_jour / run_weekly
traquaient une AUTRE sélection. Divergence tête ↔ suivi.

### Correctif — point d'écriture unique dérivé de la tête (`scoring_analyste.py`)
- Nouveau `selection_du_jour_map(results, now)` : dérive `(selection_keys,
  motif_exclusion)` de `select_paris_du_jour` (la tête). Source de vérité UNIQUE.
- `select_paris_du_jour` : paramètre `hors_top` (liste remplie) qui trace le
  motif sur le MÊME classement que la tête : « écarté : news à contre-sens (↯) »
  ou « hors top 3 ».
- `build_decision_log_records` (point d'écriture `selection_du_jour`) : ne passe
  PLUS par `compute_selection_du_jour` → appelle `selection_du_jour_map`. Le
  champ est posé sur EXACTEMENT les cellules affichées. AVANT : dédup famille
  macro + veto « tape » (sélection différente). APRÈS : top 3 |note| hors ↯.
- `render_bulletin` : UNE SEULE tête. Suppression de la branche `else`
  (`build_decision_sheet` + `build_selection_du_jour_block`, basées sur
  `compute_selection_du_jour`) ; `build_paris_du_jour_block` est toujours rendu.
  Plus jamais deux blocs « 🎯 Aujourd'hui » contradictoires.
- `compute_selection_du_jour` / `build_decision_sheet` / `build_selection_du_jour_block`
  RETIRÉES de la chaîne decision-log ET de render_bulletin (conservées définies
  pour les tests legacy uniquement, ne pilotent plus rien). Veto « tape »
  (double-critère news+momentum) ABANDONNÉ (décision fondateur : une news fraîche
  à contre-sens exclut, point — déjà fait par l'exclusion ↯).
- `bilan_jour._raison_exclusion` : commentaire aligné sur la nouvelle source
  (lecture inchangée — `load_selection_map` non touchée).
- NON FAIT (volontaire) : aucune dédup famille macro ajoutée à
  `select_paris_du_jour` (préserve la tête approuvée par le fondateur ; question
  dédup gérée séparément). Zéro touche scoring / conclusions / matrice Synthèse.

Tests : `test_selection_du_jour.py` — 2 tests decision-log mis à jour vers le
nouveau contrat (Option C, plus de dédup), +2 tests d'identité (map == tête ;
profil 23/06 ↯ Or/EUR exclus → decision-log == tête == load_selection_map).
Suite ciblée : 336 passed, 4 failed (baseline `holidays`/`pandas` absents,
identiques sur HEAD non modifié — zéro régression introduite).

## 2026-06-23 — Un seul principe d'ordre « À jouer (24h) » + garde-fou ↯ paris (Option C)

Incohérence relevée par le fondateur (validée + 3 experts, Option C) : le tableau
« À jouer aujourd'hui (24h) » découpait les convictions FORTES en deux sous-groupes
(« sans drapeau » PUIS « avec drapeau(s) »), faisant remonter une note plus FAIBLE
mais propre (Argent SHORT -6,09) AU-DESSUS d'une note plus FORTE mais contestée
(Or SHORT -16,69 ↯). En parallèle, les paris du jour étaient choisis par |note|
brute → ils prenaient Or/EUR (↯) alors que le tableau affichait Argent/Pétrole en
tête. Deux ordres contradictoires. RENDU + SÉLECTION uniquement (zéro touche au
scoring, aux conclusions, à la matrice Synthèse).

### A — Tableau : tri par |note|, fin du découpage propre/contesté (`scoring_analyste.py`)
- `build_a_jouer_block` (l.2194) : suppression de `forte_clean`/`forte_flagged`.
  Les convictions fortes forment UN SEUL groupe « _Conviction forte_ » trié par
  |note| décroissante (`buf` déjà trié). Le drapeau ↯/◧/⇄… reste AFFICHÉ dans la
  colonne « Drapeaux » comme avertissement inline mais ne réordonne plus.
  - Avant : Argent (-6,09 propre) et Pétrole (-1,86 propre) AU-DESSUS de Or
    (-16,69 ↯) et EUR/USD (-15,97 ↯). Après : Or, EUR/USD (les plus fortes notes,
    ↯ affiché) puis Cacao, Argent… par |note|. Groupe « autres jouables » inchangé.
- Texte « Comment lire » (l.4223) : ajusté (tri par note, drapeaux = avertissements
  inline, plus de mention « sans drapeau / avec drapeau »).

### B — Paris du jour : exclusion des ↯ news à contre-sens (`scoring_analyste.py`)
- Nouveau `_cell_news_a_contresens` (l.2403) : source de vérité UNIQUE du ↯ réutilisée
  (`r.divergence_quant_news` OU `_feed_news_contredit_call`, même expression que
  `_compute_cell_risk_flags`/`_synthese_cell_risk_flags`). Aucune réinvention.
- `select_paris_du_jour` : garde le tri |note| desc et les exclusions existantes,
  AJOUTE l'exclusion des cellules ↯ (on saute, on prend la suivante non-↯). < 3
  éligibles → liste plus courte (s'abstenir est valide). Param `ecartes_contresens`
  (transparence) → liste des fortes top-note écartées pour ↯.
  - Avant : paris = Or (-16,69 ↯), EUR/USD (-15,97 ↯), Cacao. Après : Or/EUR exclus,
    paris = top non-↯ (Cacao, Argent, CAC 40) + mention « Or, EUR/USD écartés (↯) ».
- `build_paris_du_jour_block` : ligne de transparence sous les paris quand le cas
  se produit ; message « aucun pari » élargi (couverture, neutre OU news à contre-sens).

### Tests
- Nouveau `tests/test_a_jouer_ordre_et_paris_contresens.py` (7 tests) : ordre tableau
  forte ↯ > forte propre, exclusion ↯ des paris, < 3 non-↯, non-↯ retenue, repro 23/06.
- `test_audit_visuel_2026_06_12.py` : `test_hb1_jouables_scinde_forte_sans_drapeau`
  → `test_hb1_jouables_groupe_forte_unique` (un seul groupe, plus de découpage).
- `test_paris_du_jour_convictions.py` : assertion message « aucun pari » mise à jour.
- Suite ciblée : 235 passed. Suite complète : 1718 passed, 26 baseline (25 ModuleNotFound
  pandas/yfinance/holidays + 1 config news_cap divergente, tous pré-existants).

## 2026-06-23 — Rendu unifié du driver + news high fraîche qui domine le 24h

Incohérence relevée par le fondateur (Pétrole 24h) : « Porté par » citait
« Stocks Cushing → contribue +1.74 » (qui pousse à la HAUSSE) sur un SHORT,
tandis que la synthèse citait la tendance 20j (−1.63). Deux drivers différents,
l'un à CONTRE-SENS du call. Fond du problème : la grosse news fraîche pesait 0.

### Volet 1 — Rendu unifié (`v3/scripts/scoring_analyste.py`)
- `_top_driver` (l.1967, source UNIQUE de « Porté par », Sélection, ⚭, feuille de
  décision) route désormais vers `_driver_dominant_net` (driver dominant DANS LE
  SENS du call — même source que la synthèse) sur cellule directionnelle franche
  (LONG/SHORT, |note| ≥ NEUTRAL_BAND). Fallback |contribution| brute UNIQUEMENT
  hors direction franche (quasi-neutre/INSUFFISANT) → zéro régression. « Porté
  par » et synthèse convergent PAR CONSTRUCTION.
  - Avant Pétrole 24h SHORT : « Porté par » = Cushing +1.74 (contre-sens) ;
    synthèse = tendance 20j −1.63. Après : les deux citent le MÊME driver net
    SHORT (la tendance 20j résiduelle tant que la news ne domine pas — cf. V2).
- `_raison_parts` (l.3584) et `raison_cellule_phrase` (l.3700) appliquent
  `_enrich_net_news_label` quand le driver dominant EST le porteur net news →
  TITRE RÉEL de la news au lieu de la phrase biblio figée (cohérent avec « Porté
  par »). `now` threadé jusqu'à la cellule de Synthèse (l.4652). Cas du docstring
  `_raison_cellule` (quasi-neutre, INSUFFISANT, meteo_cacao douteux, gates exclus,
  chiffre pondéré 📰, co-driver news) PRÉSERVÉS.

### Volet 2 — Une news high fraîche pèse vraiment dans le 24h (`v3/scripts/triggers_classifier.py`)
- Diagnostic SUR PIÈCES (`data/decision-log/2026-06-23-0841.jsonl`, Pétrole 24h
  SHORT score −1.86) : le porteur net news `tension_geopol_moyen_orient`
  (poids 7, pertinence 24h boostée à 1.0) contribuait **0** car son
  `valeur_normalisee` = **0.0** — source_track `ia_synthese_faible`. Cause : la
  synthèse nette DeepSeek du corpus est ressortie « faible/neutral » (net dilué
  par d'anciennes news Brent LONG type Hormuz) → niveau-2 → `val=0`. Donc ni le
  cap ni le poids ni la pertinence n'étaient en cause (déjà au max) : le SIGNE
  net du carrier était nul. Le SHORT était porté par la seule tendance 20j
  résiduelle (−1.63). Le LLM (synthèse) étant probabiliste, on ne le touche PAS ;
  on agit sur le levier déterministe (le fallback niveau-2).
- FIX MINIMAL : avant d'abandonner à `val=0` au niveau-2 du carrier, filet
  « news IA `materiality=high` FRAÎCHE (≤ 72h, `is_fresh_for_override`) et
  UNIDIRECTIONNELLE (zéro high à contre-sens) » → matérialise le signe net (±1),
  source_track `ia_synthese_news_high`. CONSERVATEUR : conflit high ou rien de
  high frais → reste à 0 (zéro invention de direction). 7j/1m intacts (le filet
  ne touche que le signe ±1 du carrier, pas les pertinences par horizon).
  - Avant : news high fraîche SHORT BRENT → carrier 0 → news ne pèse pas dans le
    24h. Après : carrier −1 → ×poids 7 ×pertinence 24h 1.0 (magnitude 7.0) >
    tendance 20j résiduelle 24h (6×0.4×|−0.679| ≈ 1.63) → la news DOMINE le 24h.
- Nouveau track propagé à `SYNTHESE_NET_TRACKS` (scoring_analyste + run_suivi) →
  affiché comme porteur net news (libellé enrichi titre réel, cohérent V1).
- Test : `v3/tests/test_news_high_domine_24h.py` (5 cas : domination chiffrée,
  conflit→0, medium→0, ancien→0, non-régression synthèse high).

## 2026-06-23 — Transparence du porteur NET news : titre réel au lieu de « Synthèse news (net, IA) »

Problème fondateur : quand une ligne est portée par le NET news, le rendu
affichait le libellé OPAQUE « Synthèse news (net, IA) » — sans QUELLE news ni
POURQUOI (ce matin « Cacao LONG — Synthèse news (net, IA) » ; « ça veut dire
quoi ? aucun learning possible »). La vraie raison (corpus net haussier El Niño)
n'apparaissait nulle part.

### Enrichissement PUR RENDU (`v3/scripts/scoring_analyste.py`)
- NOUVEAU `_dominant_news_for_actif(now)` : carte {actif: (sens_net, titre_réel)}
  de la news DOMINANTE par actif. RÉUTILISE la source de vérité UNIQUE du feed
  « Top actualités à impact » (`briefing.filter_recent_impactful` +
  `_primary_actif_from_event` + `_sort_by_materiality_then_date` +
  `_direction_arrow_for`) — aucun parseur events-log dupliqué. Mémoïsé par
  mtime/taille/date (comme `_fresh_high_feed_dirs`). Titre = champ `trigger`,
  tronqué proprement ~70 car.
- NOUVEAU `_enrich_net_news_label(label, r, now)` : si `label` == le libellé
  opaque « Synthèse news (net, IA) » → remplacé par « news net {haussière|
  baissière} : {titre réel} ». Fallback sans titre exploitable → « news net
  haussière/baissière ». Sens indéterminé / news indispo → libellé d'origine
  (dégradation sûre, best-effort, jamais de crash).
- Branché sur les 2 points de rendu visés : `select_paris_du_jour` (raison des
  paris du jour) et `_driver_detail` (colonne « Porté par » de « À jouer
  aujourd'hui (24h) »), avec `now` threadé. Top swing utilise aussi `_driver_detail`.
- Avant : « Cacao LONG — Synthèse news (net, IA) ». Après : « Cacao LONG — news
  net haussière : El Niño menace les récoltes du cacao ».
- NON touché : scoring, conclusions, matrice « Synthèse des décisions »,
  `cle_courante`/signe/poids/`_nom_affiche` des AUTRES critères. Seul le porteur
  net news est enrichi ; tout critère quant garde son libellé legacy.
- Tests : `v3/tests/test_porte_par_news_reelle.py` (10 cas — net haussier avec
  titre, fallback sans titre, sens baissier, news neutre ignorée, critère
  quant inchangé, troncature, verrou pur-rendu). Suite ciblée verte.

## 2026-06-23 — Un seul cerveau : la tête « 🎯 Aujourd'hui » dérive des convictions 24h (fin du moteur séparé) + boost news 24h

Décision fondateur + 3 experts. CAUSE RACINE : deux moteurs parallèles. La tête
« 🎯 Aujourd'hui » venait de `selection_jour.compute_top3` (catalyseur news +
momentum), un classement SÉPARÉ qui pouvait CONTREDIRE le fond — ce matin
« Or LONG » en tête alors que la conviction 24h de fond était « Or SHORT -14,49
forte », et « Nasdaq SHORT » hors des plus fortes convictions.

### A. Tête dérivée des convictions 24h jouables (`v3/scripts/scoring_analyste.py`)
- NOUVEAU `select_paris_du_jour()` + `build_paris_du_jour_block()` : les 3 paris
  du jour = les 3 PLUS FORTES CONVICTIONS 24h JOUABLES. Source UNIQUE = les mêmes
  cellules que le bloc « À jouer aujourd'hui (24h) » (NON `_cell_a_eviter` :
  exclut 🚫 / ⚪ / ≈), AVEC exclusion supplémentaire des « fragile (couverture
  insuffisante) ». Tri par |note| décroissant, top 3. Sens du pari = sens de la
  conviction. Si < 3 jouables : moins de 3 (zéro invention, zéro remplissage).
- `render_bulletin` (tête) : `_sjd.build_top3_block(compute_top3(...))` REMPLACÉ
  par `build_paris_du_jour_block(results, ...)`. `compute_top3` DÉBRANCHÉ de la
  tête. Le module `selection_jour`/`selection_jour_data` reste en place (tests +
  decision-log) mais ne PILOTE plus la tête. Conséquence : le pari du jour ne
  peut JAMAIS contredire sa conviction (cohérence par construction).
- NON touché : matrice « Synthèse des décisions », blocs Swing 7j / Positions 1m,
  mesure (mesure_bilan), build_html, le 7j/1m.

### B. Boost traçable du poids du critère NEWS en 24h (10 fiches porteuses du net IA)
Pour qu'une grosse news fraîche remonte naturellement la conviction 24h (et entre
dans le top 3 PAR la conviction, jamais contre elle). Pertinence 24h du critère
porteur de la « Synthèse news (net, IA) » portée à 1.0 ; 7j/1m INCHANGÉS.
Règle fondateur « zéro modification silencieuse » → avant/après ci-dessous :

| Fiche | Critère porteur (cle_courante) | 24h avant | 24h après |
|---|---|---|---|
| or | tension_geopolitique | 0.5 | 1.0 |
| nasdaq | sentiment_ia_megacaps | 0.8 | 1.0 |
| cac40 | tension_politique_fr | 0.5 | 1.0 |
| vix | tension_geopolitique_active | 0.9 | 1.0 |
| petrole | tension_geopol_moyen_orient | 0.6 | 1.0 |
| cuivre | mining_strikes_chili_perou | 0.7 | 1.0 |
| argent | demande_pv_mining_strikes | 0.2 | 1.0 |
| cafe | maladies_cabosses_rouille | 0.3 | 1.0 |
| cacao | maladies_cabosses | 0.2 | 1.0 |
| ble | geopolitique_mer_noire | 0.7 | 1.0 |

Justification de la valeur 1.0 : c'est l'horizon où une news fraîche compte le
plus ; le COEF_NATURE amortit déjà ponctuel/verbal par horizon, et la tendance
(7j/1m) reste pleinement pertinente (inchangée). eurusd/sp500 n'ont pas de
porteur net IA (absents de CRITERION_SCOPE) → non modifiés.

### C. Vérification cas réel 23/06 (simulation `render_bulletin`)
Profil fond : Or SHORT -14,49 forte, EUR/USD SHORT -15,87 forte, CAC 40 SHORT,
Nasdaq +0,20 (quasi-neutre). Tête produite : EUR/USD SHORT, Or SHORT, CAC 40
SHORT. AUCUN « Or LONG », Nasdaq exclu (quasi-neutre), aucun pari ne contredit
sa conviction. Cuivre « couverture insuffisante » serait exclu même à |note| fort.

### Tests
NOUVEAU `v3/tests/test_paris_du_jour_convictions.py` (A : ordre + sens + exclusions
quasi-neutre/insuffisant/couverture insuffisante ; B : cas 23/06 sans Or LONG ;
C : sanity boost news 24h). 172 tests verts sur le périmètre scoring/sélection/
render/html. Baseline pré-existante inchangée (pandas/holidays absents → mêmes
~11 échecs ModuleNotFoundError sur test_criteres/test_bilan_jour_cam7_cab2).

## 2026-06-22 — Mesure partagée étendue aux Suivis 12h/18h + Bilan semaine R5 (cohérence par construction)

- **But** : faire hériter les autres rapports de la mesure du « Bilan du jour » (module `mesure_bilan`) au lieu de mesures divergentes — une seule source de vérité.
- **Suivis 12h/18h (`run_suivi.py`)** :
  - **Cours max intraday** : en plus du fav% ponctuel, capture l'excursion MAX favorable ET adverse depuis l'ouverture, en RÉUTILISANT `mesure_bilan._excursions_intraday` (+ `_bars_du_jour`) sur la série 1h (`fetch_twelve_series(ticker,"1h",24)`) — zéro duplication. Nouveaux champs `SuiviLigne.max_favorable_pct/max_adverse_pct`, affichés (« Meilleur point / Pire point ») et persistés dans suivi-tracking (clés ADDITIVES `max_fav_pct`/`max_adv_pct` ; `call`/`fav_pct`/`heure` inchangées).
  - **Robustesse prix** : relevé via cascade cohérente avec le bilan (dernière barre 1h → spot ; `prix_courant_cascade`). Source absente → `—`, jamais comblé.
  - **GARDE-FOU HONNÊTETÉ (cause du suivi 18h vide d'aujourd'hui)** : si le Briefing 7h du jour est INTROUVABLE (archivé en cours de journée), le rapport l'AFFICHE (« Briefing 7h du jour introuvable : suivi des positions impossible ») au lieu d'un tableau vide silencieux. Distinct de « briefing trouvé mais 0 position » (`briefing_7h_existe`, même détection que `mesure_bilan.load_cells_et_prix_7h`).
- **Bilan semaine R5 (`run_weekly.py`)** :
  - **GARDE-FOU HONNÊTETÉ** : une semaine sans aucune mesure affiche « Mesure indisponible cette semaine (donnée absente) : à ne pas lire comme RAS » dans les sections 3/4/5, jamais un « Rien à améliorer / RAS » trompeur (`_mesure_indisponible_semaine`, libellé aligné sur `bilan_jour._MSG_MESURE_INDISPO`).
  - **Agrégation** : vérifié de bout en bout que ce que `persist_mesures_jour` écrit dans le measures-log est bien lu par `selection_semaine` (round-trip testé) — format de clés cohérent, aucune incohérence à corriger.
- **Tests** : +9 suivi (excursions LONG/SHORT, cascade de prix 1h→spot→`—`, briefing introuvable vs 0 position, persistance tracking) + +5 weekly (mesure indispo helper + rendu + round-trip persist→agrégation). Fetchers injectés, zéro réseau. Suite : **1693 passed, 22 failed (baseline préexistante : 18 `pandas` manquant + 4 jours fériés `holidays`), 0 régression**.

## 2026-06-22 — Refonte mesure du « Bilan du jour » : fenêtre = jour de bourse MÊME (auto-suffisante)

- **Cause racine (vérifiée sur pièces, run 22h15)** : `build_bilan_jour` déléguait la notation à `journaliste.measure(today=compute_echeance(date_j,"24h"))`, soit le PROCHAIN jour ouvré. À 22h15 le soir J, la clôture de J+1 n'existe pas → les 12 calls 7h sortaient tous « non-notee » SANS le moindre fetch (défaut STRUCTUREL de conception, pas un fetch raté). measures-log vide → variations-24h vide → « à améliorer » vide.
- **Refonte** : nouveau module `scripts/mesure_bilan.py` — mesure AUTO-SUFFISANTE de la journée J (ouverture → clôture ~22h) pour chaque call 7h. Référence = ouverture du jour (réutilise `_resolve_prix_reference`), clôture via CASCADE (bougie 1day → dernière barre 1h → spot → fav% suivi reconstruit → sinon non-notee « donnée absente »). Verdict VRAI/FAUSSE/NC réutilise `measure_cell` (seuils inchangés). Capture le **cours MAX du jour** : excursion favorable/adverse max sur la série 1h intraday (extrema des close ; Twelve ne sert pas de high/low intra-barre).
- **`Measure` étendu (champs OPTIONNELS, non-breaking)** : `max_favorable_pct`, `max_adverse_pct`, `prix_cloture_source`, `prix_cloture_heure`. Consommateurs en aval (compute_perf_top3, gros_moves, win_rate_*, matrice synthèse) inchangés.
- **Affichage** : nouvelle colonne « Cours max jour » (table top 3) + colonnes « Max favorable / Max adverse » (table « Résultat des calls 7h »).
- **Persistance** : les mesures du jour alimentent le measures-log (merge non destructif, idempotent) puis régénèrent variations-24h.md → le gros move du jour (ex. cacao +8 %) y apparaît et devient le plus gros raté/opportunité.
- **Garde-fou d'honnêteté** : si 0/N cellules notées, le rapport affiche « Mesure indisponible aujourd'hui (donnée absente) : à ne pas lire comme RAS » au lieu de « Aucun pari raté » / « Rien de net » (qui se lisaient « journée parfaite »).
- **Fix indices (cohérence d'échelle)** : market_data mappe `^GSPC`→SPY (~750) et `^IXIC`→QQQ (~740). Plutôt que changer le mapping global (risque sur les ouvertures déjà stampées en proxy, non vérifiable en live ici), garde-fou de cohérence d'échelle dans `mesure_bilan` : si référence et clôture diffèrent d'un ordre de grandeur (ratio hors [1/3 ; 3]) → mesure REFUSÉE « échelle incohérente » plutôt qu'un delta absurde (ex. (5500−748)/748).
- **Tests** : `tests/test_mesure_bilan.py` (16 tests, fetchers injectés, zéro réseau) — excursions LONG/SHORT, cascade clôture complète, cohérence d'échelle, garde-fou honnêteté, variations-24h peuplé. 2 tests CA-B2 obsolètes (`close_approx`/EU 17h30) réécrits sur la nouvelle conception. Suite : **1679 passed, 22 failed (baseline préexistante : 18 `pandas` manquant + 4 jours fériés), 0 régression**.

## 2026-06-22 — Audit 1 mois (3 experts) : carry 1m 24h→96h + Positions 1 mois jouables + sonde data

- **Carry 1m 24h → 96h** (consensus 3 experts) : maintenir une conviction MENSUELLE seulement 24h sur trou de data était incohérent (le 7j tolérait 48h > 1m). Fenêtre désormais proportionnelle à l'horizon (1m=96h > 7j=48h). Tests carry_forward mis à jour.
- **Bloc « 🗓️ Positions 1 mois (max 3) » jouable** (Spéculateur) : le 1m était un panorama ; désormais sélection cadrée (objectif = seuil 1m de l'actif, entrée = prix réf, dédup par driver), miroir du Swing 7j. `build_swing_block` générique (7j + 1m).
- **Sonde data** (`probe_data_coverage.py` + workflow `probe-data`) : verify-first, la clé Twelve Grow étant active — mesure par actif la fraîcheur journalière, l'intraday 1h, et si futures/indices directs résolvent. À lancer à la main.
- À FAIRE (proposé, non expédié à l'aveugle) : mémoire structurelle news TTL (~30j 1m / ~10j 7j) — chaînon manquant relevé par le News Trader. Et fixes data #2 selon la sonde.

## 2026-06-22 — Recalibrage horizon↔fenêtre du 7j : tendance COURTE (7j) + 20j → 1 mois

- **Problème (Thomas, confirmé sur pièces)** : le score 7j s'appuyait sur une tendance-prix **20 jours** (pertinence 7j=1.0 partout) — retard ~10j incohérent avec un horizon 7j.
- **Correctif (11 fiches ; vix exclu)** : ajout `momentum_prix_7j_<actif>` (mêmes tickers, lag 7 lu dans le cle par le dispatcher générique). Pertinences : 7j neuf = {24h:0.3, 7j:1.0, 1m:0.2} (domine le 7j, retard ~2-3j) ; 20j démotée = {24h:0.4, 7j:0.3, 1m:1.0} (sert le 1 mois). Poids inchangés.
- **Robustesse** : lag 7 < lag 20 en besoin de données → si le 20j calcule, le 7j aussi. Vérifié : 11/11 actifs calculent (série synthétique), 20j non-régressé. Tests `test_momentum_7j.py`. Vérif finale = run CI 7h.

## 2026-06-18 — Refonte briefing 7h + raison par cellule (audit 3 experts 10/10) + instrumentation persistance (shadow)

**Session « briefing efficace + tendance valide tant que non démentie ». Tout mergé sur `main`, 1437 tests verts.**

- **Refonte briefing 7h (9 points, pur rendu, zéro impact signal)** — `b081492`. Décor du jour remonté en intro (catalyseur FOMC *annoncé*, jamais un résultat — honnêteté heure d'émission) ; fraîcheur masquée si OK ; méthodologie sortie des sections du jour vers une seule « ## Comment lire les scores » ; « Porté par » enrichi (nom complet + valeur + sens + contribution) ; suppression du double bloc news ; nouvelle section « ## News par actif » ; synthèse 24h/7j/1m dépliée par défaut (HTML) ; **fix prix de réf. vides** = bug d'affichage (backfill depuis le fetch live quand le stamp n'existe pas encore au rendu), PAS la clé Twelve (le stamp 2026-06-17 était bien rempli).
- **Raison principale par cellule (Synthèse 24h/7j/1m)** — `9351f93`+`cb007f3`+`b75e3fe`. Chaque cellule porte sa raison, calculée par le système depuis le **driver dominant DANS LE SENS de la conclusion nette** (jamais le plus fort |effet| à contre-sens), via bibliothèque experte éditable `v3/config/raisons-drivers.yml` (39 drivers). Recalculée à chaque run (« au fur et à mesure », persiste tant que le driver dominant ne change pas). Quasi-neutre dit, gate FOMC jamais cité, météo cacao en phrase neutre (signe à valider). **Amorcée par un audit marché des 3 experts**, puis **auditée et itérée jusqu'à 10/10** (3 rounds : 7→9→10 ; bloquants levés = drapeaux hérités exacts de la grille, chiffre pondéré quand 📰, co-driver news cité, actionnabilité par cellule). Pur rendu, zéro impact signal.
- **Persistance des tendances — instrumentation SHADOW + mesure** — `997512e`. Cadre la question fondateur « une tendance reste valide tant que non démentie ». **Avis des 3 experts + mesure convergent (L028)** : le vrai démenti = le QUANT qui se retourne (détecteur de mots-clés = 0 déclenchement historique) ; sur structurels 7j/1m le quant dément déjà ~71 % → persistance « age-only » dangereuse, le quant garde le véto. 4 champs `persist_shadow_*` additifs au decision-log (zéro impact signal) + rapport `v3/audit/persistance-shadow-mesure.md`. **Cutover NON fait** : attend l'accumulation forward (>30j) + GO Thomas sur les chiffres.
- **Points ouverts remontés** : (a) **convention de signe « météo cacao »** douteuse (pluie au-dessus normale traitée haussière) — à valider, rejoint le chantier cacao ; (b) regroupement N2 d'horizons à drapeaux divergents masque un flag de prudence d'un horizon (réserve audit non bloquante, réglage 1-ligne si voulu) ; (c) clé Twelve à régénérer (action Thomas).

## 2026-06-16 — FIX L027 (P0) : la mesure du WR des continus part de l'ÉMISSION 7h, plus de l'« ouverture » 8h (GO mesure Thomas)

**Défaut P0 corrigé, prouvé sur pièces.** La « référence d'ouverture » des actifs **continus** (cotés 24/7 : or, argent, pétrole, cuivre, cacao, café, blé, EUR/USD) était stampée à **heure fixe 8h Paris**. Ce point pouvait tomber **au milieu d'un mouvement déjà entamé depuis l'émission du bulletin de 7h** → le 24h n'était mesuré que sur la **fin tronquée** du mouvement, classant des calls **perdants** en « NC ». **Cas fondateur (15/06, or, XAU/USD natif)** : open de session ≈ 4215 → close ≈ 4309 (**+2,2 %**, plus haut +3,6 %), le **SHORT était PERDANT**, mais classé **« NC » (+0,18 %)** car la référence 8h (≈ 4308) tombait **après** le rallye. **Conséquence : le win rate des continus CACHAIT des pertes et était artificiellement flatté** — fondement de toute la mesure.

- **Fix (sémantique de mesure, scopé aux continus).** `journaliste._resolve_prix_reference` devient **group-aware** (via `mesure_ouverture.actif_group`, zéro liste en dur) : pour un **continu**, référence du 24h = **prix d'ÉMISSION 7h** (le moment où Thomas lit le bulletin et peut agir ; un continu cote en continu à 7h ⇒ prix live valide) ; alignement **leçon L021** (« mesurer depuis le point d'EXÉCUTION réel »). Fallback ouverture si émission absente (WARNING). Pour un **non-continu** (indices cash CAC 9h / S&P-Nasdaq 15h30, VIX — fermés à 7h) : **INCHANGÉ**, référence = ouverture de marché (un prix de 7h y serait un prix de nuit). Fallback émission si ouverture absente.
- **Choix vs bougie open→close (justifié sur pièces).** L'option « open→close de la bougie journalière Twelve » a été **écartée** : l'« open » d'une bougie `1day` XAU/USD suit une frontière de session arbitraire (rollover ~23h NY / 00h UTC), **pas 7h Paris quand Thomas agit** → elle recrée exactement la classe de bug L027 (référence non alignée sur l'action) + dépendance fetch supplémentaire. L'émission 7h EST le point d'exécution réel et est **déjà stampée** (`prix-emission/{bid}.json`) pour tous les bulletins. Le close-side reste le `prix_courant` mesuré à échéance.
- **Étiquette « référence dégradée » (présentation).** `scoring_analyste.build_audit_veille_24h` : la mention « mesure v1 / référence dégradée » est désormais **group-aware** (`_source_canonique_attendue`) — elle ne s'affiche QUE si la source réelle diffère de la source **canonique** du groupe (continu→émission, non-continu→ouverture). Un continu mesuré depuis l'émission n'est PLUS étiqueté à tort « v1 ».
- **Cutover (changement de SÉMANTIQUE du WR).** `ref-changed.json` append-only : les **8 continus** (`GC=F`, `SI=F`, `BZ=F`, `HG=F`, `CC=F`, `KC=F`, `ZW=F`, `EUR=X`) voient leur `ref_changed` avancé au **1er bulletin sous la nouvelle sémantique = 2026-06-17** (motif « fix L027, GO mesure Thomas »). Repartent **N=0 au 17/06**. **4e reset des continus — coût assumé, VRAI défaut corrigé (dit honnêtement).** Les 4 non-continus gardent `ref_changed` 2026-06-11. Addendums datés append-only dans `KILL-CRITERION.md` + `SELECTION-RULE.md` (texte des règles **inchangé** — seule la valeur mesurée du WR des continus devient honnête).
- **Test-verrou (critère d'acceptation n°1).** `tests/test_verrou_l027_mesure_continu.py` reproduit le cas or 15/06 (open 4215 → close 4309, SHORT) et prouve qu'il ressort désormais **FAUX** (et plus « NC »). Contre-épreuve incluse : avec l'ancienne référence 8h le même call serait NC (le bug matérialisé).
- **Garde-fous** : WIN RATE ONLY (amplitude % uniquement pour seuiller VRAI/FAUX/NC, zéro montant), zéro invention (source absente → suivi-interrompu), **aucun poids ni seuil ni prompt touché**, `v3/data/` non pollué (sauf `ref-changed.json` = livrable du cutover).
- Tests mis à jour pour la nouvelle sémantique (semantic change assumé, pas de casse silencieuse) : `test_mesure_ouverture.py` (continu→émission / non-continu→ouverture + fallbacks), `test_ref_changed_continu_15_06.py`, `test_cutover_v2.py`, `test_twelve_native_remap.py` (dates de cutover → 17/06, motif natif conservé), `test_scoring.py` (étiquette dégradée group-aware). Suite : **1323 passed** (hors env-only).

## 2026-06-16 — Or/argent/Brent : symbole Twelve natif (XAU/XAG/XBR/USD) + provenance loggée par symbole

**Constat (sondage live API Twelve, clé réelle).** Les futures Yahoo `GC=F`/`SI=F`/`BZ=F` renvoient **404** sur Twelve `/time_series` → le système les obtenait via un **fallback yfinance silencieux** (angle mort de provenance). Twelve sert ces matières premières **uniquement sous leurs symboles spot natifs**, vérifiés au bon niveau : or `XAU/USD` (close 4326 ≈ ~4325), argent `XAG/USD` (~70), Brent `XBR/USD` (~83).

- **Remap (présentation/source, pas de scoring).** `market_data._TICKER_MAP` : `GC=F → XAU/USD`, `SI=F → XAG/USD`, `BZ=F → XBR/USD` (l'ancien `BZ=F → CO1` type=commodities renvoyait 404). Le mapping s'applique au **prix (`fetch_price`) ET à l'historique (`fetch_history`)** → Twelve devient la **source unique** de ces 3 actifs (le fallback yfinance n'est plus déclenché). **`ticker_principal` des fiches INCHANGÉ** (`GC=F`/`SI=F`/`BZ=F` = identifiant interne stable, L023) — seul le symbole INTERROGÉ change, via la couche de traduction. Le dispatch des critères se fait par `cle in TWELVE_SYMBOLS` (clé `momentum_prix_20j_*`), indépendant du champ texte `source` → zéro effet du relibellé sur le calcul.
- **Provenance loggée (fin de l'angle mort).** Nouveau registre `market_data._provenance` (`record_provenance`/`get_provenance`/`clear_provenance`) : `fetch_history`/`fetch_price` enregistrent la source réellement utilisée (`twelve_native` / `yfinance_fallback`), Stooq idem (`stooq_fallback`) côté `criteres_calculator`. Exposé dans `criteres-health.md` (bloc « Provenance des prix » : N | source | symboles). On sait DÉSORMAIS toujours d'où vient chaque prix.
- **Libellés `source:` honnêtes (fiches).** or/argent/pétrole → `Twelve Data (XAU/USD)` / `(XAG/USD)` / `(XBR/USD)`. Cuivre/cacao/café/blé → `yfinance (Twelve ne sert pas ce future)` : **Twelve ne sert PAS ces futures au bon niveau** (`XCU/USD`, `COCOA`, `COFFEE`, `WHEAT` = 404 ; ETF au mauvais niveau écartés — **zéro invention**) → yfinance conservé. **Aucun poids ni seuil touché.**
- **Cutover (changement de SIGNAL).** Le niveau spot diffère légèrement du future → z-scores/momentum bougent. `ref-changed.json` append-only : `ref_changed` de `GC=F`, `SI=F`, `BZ=F` avancé **2026-06-15 → 2026-06-16** (motif « source = Twelve natif XAU/XAG/XBR, fin de la dépendance yfinance cachée »). Repartent **N=0 au 16/06**. **Cuivre/cacao/café/blé INCHANGÉS** (gardent `ref_changed` 2026-06-15). Addendums datés append-only dans `SELECTION-RULE.md` + `KILL-CRITERION.md` (texte des règles **inchangé**).
- **Garde-fous** : WIN RATE ONLY, zéro invention (pas d'ETF au mauvais niveau pour les 4 futures non servis), **aucun poids ni seuil de fiche touché**, `v3/data/` non pollué (sauf `ref-changed.json` = livrable).
- Tests : `tests/test_twelve_native_remap.py` (mapping price+history GC=F→XAU/USD, SI=F→XAG/USD, BZ=F→XBR/USD ; ticker_principal inchangé ; provenance twelve_native/yfinance_fallback/stooq_fallback ; cuivre/cacao/café/blé non remappés ; cutover ref-changed 16/06) — **ZÉRO réseau (mocks)**. L'effet live (Twelve natif renvoie bien la série) sera confirmé au prochain run avec clé.

## 2026-06-15 — Actifs continus : critères sur le prix le plus frais (fin de l'angle mort overnight/week-end)

**Défaut démontré lundi 15/06.** Pour l'or (`GC=F`), le prix dont le système dispose à 7h le lundi = **exactement le close de vendredi** (`shadow_gap_overnight ≈ 0`). Les critères de niveau/momentum/RSI s'appuient sur `close[-1]` (close J-1) → le système **ignorait tout mouvement overnight/week-end** sur les actifs cotés en **continu** (or, argent, pétrole, cuivre, cacao, café, blé, EUR/USD) et pouvait shorter en silence contre un actif déjà reparti de +2 %. Légitime pour S&P/Nasdaq/CAC (cash fermé à 7h), faux pour les continus.

- **VOLET A — prix le plus frais injecté (continus uniquement).** Nouveau point d'injection unique dans `criteres_calculator.fetch_twelve_series` : pour les tickers du groupe **continu** (source de vérité réutilisée : `mesure_ouverture.actif_group`, **zéro liste en dur**), si un prix temps réel **plus frais** que `close[-1]` est posé en override, il est **appendé** (date du tick > close J-1) ou **remplace** `close[-1]` (même jour). Source du prix : `fetch_twelve_price` (même appel que `stamp_prix_emission`), primé une fois par ticker au début de `run()` puis nettoyé (`finally`). Tous les critères à série de closes (z-score niveau, variation 20j/momentum, RSI, perf 5j) en bénéficient. **Dégradation sûre OBLIGATOIRE** : prix frais absent OU non plus récent que `close[-1]` (cas Twelve gratuit le lundi 7h) → **série inchangée, comportement actuel exact** (zéro invention). Non-continus (S&P/Nasdaq/CAC/VIX) **jamais** touchés. Effet réel non vérifiable dans le conteneur (pas de clé Twelve → fetch retourne le close de vendredi → no-op sûr observé) ; la **logique est testée par mocks**, l'effet live sera confirmé au prochain run avec clé.
- **VOLET B — visibilité.** Sous « Sélection du jour », drapeau ⚠️ « bouge à contre-sens depuis la dernière clôture vue (+X %) » pour un actif **continu** sélectionné dont `shadow_gap_overnight` ≥ **0,8 %** et de **sens opposé** à la conclusion (LONG alors que ça baisse, SHORT alors que ça monte). Anti-bruit : gap ≈ 0, aligné, ou non continu → rien.
- **VOLET C — cutover (changement de SIGNAL).** `ref-changed.json` append-only : `ref_changed` des **8 actifs continus** (`GC=F`, `SI=F`, `BZ=F`, `HG=F`, `CC=F`, `KC=F`, `ZW=F`, `EUR=X`) avancé **2026-06-11 → 2026-06-15** (motif « critères sur prix le plus frais — fin de l'angle mort overnight/week-end », justification gravée ici comme l'exige le `_doc`). Ils repartent **N=0 au 15/06** — **3e reset des continus, coût assumé, vrai défaut corrigé**. Non-continus (`^GSPC`, `^IXIC`, `^FCHI`, `^VIX`) **inchangés** (close J-1 reste leur dernier prix réel). Addendums datés append-only dans `SELECTION-RULE.md` + `KILL-CRITERION.md` (texte gravé des règles **inchangé**).
- **Garde-fous respectés** : WIN RATE ONLY, zéro invention, **aucun poids ni seuil de fiche touché**, `v3/data/` non pollué (sauf `ref-changed.json` = livrable).
- Tests : `tests/test_fresh_price_continu.py` (8, VOLET A : append/remplace/no-op périmé/no-op absent/non-continu/décalage momentum/réutilisation `actif_group`/rejet prix invalide) + `tests/test_gap_contresens_continu.py` (8, VOLET B : contre-sens hausse/baisse, aligné, sous-seuil, non-continu, None, absent, intégration bloc) — **ZÉRO réseau (mocks)**. Gate `python -m pytest v3/ -q` : pas de nouvelle régression (22 failed env-only pré-existants — `pandas`/`holidays` absents — inchangés).

## 2026-06-10 (soir) — Lot autopilote « sources & critères » (S6)

- **Santé des critères persistée** : `v3/data/criteres-health.md` à chaque run (motif + cause HTTP exacte par critère n/a) — fin de l'angle mort ; le run du 11/06 révélera la cause CI-only de `meteo_ci_ghana_precip_30j` (cacao, poids 11). Durcissement Open-Meteo (throttle + 1 retry différé).
- **Critères ressuscités** (cutover : motifs au `ref-changed.json`) : café `usd_brl` (6, Twelve), VIX `gap_rv_iv` (5, calculé SPY+CBOE), EUR/USD `balance_commerciale_ez` (3, Eurostat EA21 sans clé). **VIX rejoint le reset 11/06 → 12/12 actifs en ère v2.**
- **Calendrier éco statique** (`v3/config/calendrier-eco.yml` + `calendrier_eco.py`) : FOMC 2026 datés (officiel) + CPI/NFP/BCE/OPEC/WASDE/EIA/COT en règles « ~ » (zéro date inventée). Catalyseurs J+1 du Bilan alimentés ; **gate ⚑ raccordé en déterministe** (FOMC J-1/J0, flag hors score).
- **Fallback prix Stooq (dormant)** : séries de critères uniquement si Twelve échoue, symbole mappé, 1day — JAMAIS les stamps de mesure ; tout-Twelve OU tout-Stooq, tracé `twelve_fallback_stooq:*`. 404 depuis le conteneur (anti-bot) → à re-valider en CI.
- **Sources écartées (zéro invention)** : WASDE+Crop Progress (QuickStats 401 — secret `USDA_API_KEY` gratuit à créer, fort impact blé p.11+6), WGC or (pas de feed public), ICE arabica (PDF/JS), AAII (403 anti-bot) → option `v3/data/manual/` à trancher.
- Tests : 1153 passed (+59 sur le lot), 22 failed env-only conteneur.

## 2026-06-11 (Session 6) — MOMENTUM v3 vague 2 : poids ≤6 (A3) + famille complète (A8/A9) + mesure (A5) + cutover

> Suite de la vague 1 (moteur A1/A2/A6, déjà sur la branche). La concertation `v3/audit/momentum-family-verdict.md` (Analyst/News Trader/Spéculateur → GO-MODIFIÉ) avait établi que le momentum « déployé » le 10/06 était **fonctionnellement identique à la v1** (z-score du NIVEAU de close = laggard, bug cacao). Vague 1 a corrigé le moteur ; vague 2 finit fiches + mesure + cutover.

- **A3 — poids conservateurs ≤6 (prove-first)** sur les 7 fiches existantes : `momentum_prix_20j_*` ramené à **6** partout (cacao **9→6**, café/blé/cuivre **8→6**, pétrole/or/argent **7→6**). Commentaire daté à côté de chaque poids (« prove-first concertation 10/06, promotion 6→supérieur seulement sur preuve — métrique FAUSSES-aux-retournements »). Promotion au-delà de 6 = sur preuve shadow uniquement, jamais le plus gros poids d'une fiche tant que non prouvé.
- **A8/A9 — fin de la famille** : ajout `momentum_prix_20j_eurusd` (`eurusd.yml`, source Twelve `EUR=X` = ticker_principal, signe +1, **poids 5**, complémentaire de `dxy_trend_20j`) + `momentum_prix_20j_{sp500,nasdaq,cac40}` (proxys ETF **SPY/QQQ** + **^FCHI**, signe +1, **poids 4** = plafond indices A8, **RSI poids 2 CONSERVÉ**). **VIX NON touché** (A9 — mean-reverting, momentum exclu). **4 nouvelles entrées `TWELVE_SYMBOLS`** (mapping ONLY ; le dispatcher par préfixe `momentum_prix_20j_` → `_twelve_variation_zscore` fait le calcul variation 20j). Aucune autre mécanique, ALPHA/seuils/poids non-momentum **intacts**.
- **A5 — métrique « FAUSSES aux retournements » (shadow)** : `bilan_jour.py` += `is_reversal_context()` / `load_reversal_context_map()` / `fausses_aux_retournements()` + agrégat `FaussesAuxRetournements`. Une cellule est « en retournement » si (R1) le cap anti-inversion s'est déclenché (`news_cap_applied`) **OU** (R2) le signe des news est opposé au quant hors-momentum (`cap_quant_ex_momentum`). On compte les conclusions **FAUSSES** parmi les cellules conclusives en retournement, affiché dans le **Bilan du jour** (section dédiée). **DISTINCTE du win rate, observabilité PURE** : zéro impact scoring/conclusions/kill-criterion, WIN RATE ONLY (aucun PnL). Forward-test J+60 = **2026-08-08**.
- **Cutover (reset 11 actifs au 2026-06-11)** : `ref-changed.json` — `ref_changed` des **8 entrées existantes avancé 2026-06-10 → 2026-06-11** (la v3 corrigée — variation 20j + cap aveugle + poids 6 — atterrit ce soir, 1er bulletin avec le signal = 11/06 7h ; mémo S5 « les cellules reset repartiront à zéro quand le momentum corrigé atterrira »), motif complété sur chaque entrée. **3 nouvelles entrées** : `EUR=X`/`^GSPC`/`^FCHI` (motif « ajout momentum_prix_20j v3 (variation 20j) »). Résultat : **11 actifs reset au 11/06**, seul `vix` (`^VIX`) garde son historique v1. Addendums datés append-only dans `SELECTION-RULE.md` + `KILL-CRITERION.md` (« Cutover momentum v3 — 2026-06-11 ») : 11 actifs reset, conséquence N≥15 à J+60 documentée, texte gravé des règles **inchangé**.
- Tests : tests fiches (4 nouvelles clés dans `TWELVE_SYMBOLS` ∩ YAML, `momentum_prix_*` poids ≤6 partout, VIX sans momentum) + tests A5 synthétiques (retournement détecté/non, FAUSSE comptée/non). Gate `python -m pytest v3/ -q` : pas de nouvelle régression (22 failed env-only pré-existants — `pandas`/`holidays` absents du conteneur — inchangés).

## 2026-06-10 (Session 5) — Fiches v3 : critère tendance-prix (correctif famille trend-following)

**Défaut systémique corrigé.** Le balayage (`v3/audit/momentum-prix-sweep.md`) a montré que **8/12 fiches n'avaient AUCUN critère de tendance-prix propre** — incohérence avec la thèse trend-following (révélé par le cas cacao, Lot F). Décision Thomas : correctif de **famille** maintenant (phase de création), pas un patch cacao, avec `ref_changed` sur les actifs concernés.

- **7 fiches ABSENTES commodities/métaux** dotées d'un `momentum_prix_20j_<actif>` (`zscore`, `zscore_window:60` — cohérent `sox_trend`/`dxy_trend`, le « 20j » = horizon conceptuel ; **signe +1** = prix au-dessus de sa distribution récente → tendance haussière suivie → LONG) : **cacao(9)/café(8)/blé(8)/cuivre(8)/pétrole(7)/or(7)/argent(7)**. Cacao : `hf_positioning_flux_options` **7→5** (contrarian sur-pondéré, cacao-case-study §4).
- **Gel moteur respecté** : `criteres_calculator.py` n'a reçu que **7 entrées `TWELVE_SYMBOLS`** (mapping ticker → chemin z-score-closes existant `_twelve_zscore_from_symbol`). Aucune nouvelle mécanique, `weighting.yml`/`scoring_analyste.py`(logique)/normalisations/`seuils_reussite_pct` **intacts**. Dégradation propre en n/a si donnée absente.
- **Cutover étendu** : `ref-changed.json` += `KC=F`/`ZW=F`/`HG=F`/`GC=F` (CC=F/BZ=F/SI=F déjà au 10/06 via Lot A). **Bilan reset : 8 actifs** repartent N=0 au 10/06 (cacao, petrole, nasdaq, argent, café, blé, cuivre, or) ; **4 gardent v1** (sp500, eurusd, cac40, vix). Addendums datés `SELECTION-RULE.md` + `KILL-CRITERION.md` (texte gravé inchangé).
- Tests : **1043 passed** (le « 1 failed » = faux échec `test_aucune_ecriture_config`, git-status-dépendant, repasse vert après commit). 3 tests mis à jour (cutover 4→8 actifs attendu).
- ⚠️ **Décision de conception à revoir (flag Thomas)** : momentum = **z-score du NIVEAU de close** (cohérent avec les critères « trend » existants) vs **z-score de la VARIATION 20j** (vrai momentum de rendement, recommandé par le case-study) — ce dernier exigerait une extension moteur d'1 ligne (hors gel). Choix actuel = niveau, gel-safe et consistant. À trancher. **EUR/USD (ABSENT, FX) + indices FAIBLE : tour suivant.**

## 2026-06-10 (Session 5) — Lot E (news : famine FIFO réparée) + Lot F (cas cacao)

**Lot E — actifs « sourds » aux news : diagnostic-first.** Le « Argent 27 / S&P 31 / VIX 3 » du brief était un **artefact de comptage** (champ `cours` = 1er actif d'un multi-impact). Comptage réel via `impacts[]` : **S&P 659, VIX 304** (faux sourds, OK) ; seul **Argent 11 = vrai sourd**. **Cause racine** : `MAX_EXTRACTIONS_PER_CYCLE=80` tronquait la file en **FIFO** → les flux dédiés (`gnews_silver_industrial`/`gnews_vix`/`gnews_nasdaq`/`copper`/`cac40`/`wheat`/`ecb`/`gold`, positions 500-800) **n'atteignaient jamais le seuil** → **0 ligne** dans events-log malgré des flux sains (62-99 items/cycle, ✅ dans source-health). Café/Brent dominaient car accumulés avant saturation.
- **Fix** (`agent_news.py`, `news_collector.py`) : **round-robin par source** avant troncature (équité vs famine FIFO) + `MAX 80→240`/cycle (débit, **pas** le cap coût) + **filtre fraîcheur à l'ingestion** `INGEST_MAX_AGE_DAYS=30` (stoppe l'écriture des archives Google News pré-2026-04 qui gonflaient Café). **Aucun flux ajouté** (flux sains, prouvé). Cap coût DeepSeek **intact** (~$0.22/j estimé, soft cap $0.50). Gel scoring respecté. +7 tests. `v3/audit/news-coverage-diagnostic.md`.
- ⚠️ **À surveiller (effet sur le cutover)** : Lot E va faire écrire enfin les flux dédiés → les news critères de plusieurs actifs (argent surtout, marginalement vix/nasdaq/cuivre/cac40/blé/eurusd/or) seront plus complets en v2. Argent est déjà dans le reset. Pour les autres : changement **marginal** (couverture news générale déjà présente) → **pas de reset préventif** (mesurer avant d'agir) ; à ajouter à `ref-changed.json` seulement si une cellule change visiblement de conclusion.

**Lot F — cas d'école cacao (analyse, aucun code).** Verdict : **le dédup (Lot A) NE SUFFIT PAS**. Rejeu v2 : conclusion reste LONG 100% (score 24h +0.55 à +1.19). Problème de fond : (1) `hf_positioning_flux_options` = logique **contrarian** (fausse en marché baissier installé, pèse 26-100% car ~50% de la fiche n/a) ; (2) **aucun critère de tendance-prix** (momentum/RSI) → baisse réelle invisible, news SHORT (68-80% hit) bridées par cap anti-inversion α=0.8. **Reco fiche v3 (NON implémentée, à valider Thomas)** : ajouter `momentum_prix_20j_cacao` (~poids 9) + réduire `hf_positioning_flux_options` 7→5 (aurait donné ~-2.8 → SHORT). `v3/audit/cacao-case-study.md`.

## 2026-06-10 (Session 5) — Cutover v2 (reset PARTIEL 4 actifs) + propagation L023

**Redémarrage shadow v2 — portée PARTIELLE.** Suite aux 4 fusions (Lot A), seuls les **4 actifs dédupliqués** (cacao, petrole, nasdaq, argent) voient leur signal changer → reset de leur compteur N / win-rate. Les **8 autres gardent leur historique v1** (`is_news_regime` non modifié → aucun delta de signal hors dédup). Exigence Thomas respectée : **v1 et v2 jamais mélangés dans un même compteur**, aucune cellule à cheval.

- **`v3/scripts/system_version.py`** (créé) : `SYSTEM_VERSION="v2"` + `load_ref_changed()`/`ref_changed_for_ticker()`. **`v3/data/ref-changed.json`** (créé) : registre clé par **`ticker_principal`** (stable, L023), append-only, dégradation propre si absent (→ aucun reset).
- **`journaliste.py`** : champ `Measure.system_version` stampé par mesure (v1 si `bulletin_date < ref_changed`, v2 sinon) ; `_apply_ref_changed_cutover()` filtre les mesures pré-cutover des seules cellules au registre **avant `compute_kpi`** → N, WR conclusif, WR tradable, n_regimes, Wilson repartent de 0 au 2026-06-10 sur les 4 actifs uniquement. `scoring_analyste.py` : champ `system_version` ajouté au decision-log.
- **Addendums datés append-only** dans `SELECTION-RULE.md` + `KILL-CRITERION.md` (« Redémarrage v2 — 2026-06-10 ») : portée 4 actifs, motif, cutover court, **texte gravé des règles inchangé**. Les 4 actifs reset peuvent légitimement ne pas atteindre N≥15 à J+60 (08/08) — attendu.
- **Propagation L023** : agrégation par critère déjà sûre (`cle_courante` partout dans le decision-log) ; mapping fragile par nom d'actif (`render_weekly_winrate`) **durci** (clé stable `fiche_key`, suppression du `name_to_key`). L023 → **propagé**. +15 tests (`test_cutover_v2.py`). Suite : **1037 passed / 3 skipped / 0 failed**.
- *Note (signalée à Thomas)* : `measures-log.jsonl` est re-dérivé déterministe à chaque run depuis les bulletins (append-only, source de vérité) — pas une réécriture de données passées ; le `system_version` par ligne reflète le régime d'émission.

## 2026-06-10 (Session 5) — Dédup fiches v2 + compteur régimes + fix M7 (Lots A/C/D, audit Cowork 10/06)

> ⚠️ **Contre-audit** : l'audit Cowork annonçait 9 doublons ; vérif YAML → **8/9 inexistants** (critères renommés 7-8/06, pas des doublons). Voir `v3/audit/fiches-v2-dedup.md` + leçon L023. **4 fusions réelles** seulement. Cutover v2 = **reset `ref_changed` PARTIEL sur ces 4 actifs** (les 8 autres gardent leur historique v1) — `is_news_regime` n'a PAS été modifié donc aucun delta de signal hors dédup.

- **Lot A — dédup (4 fusions, poids gardé = MAX, jamais somme)** : `cacao.yml` retire `cftc_cot_cocoa` (déjà dans le composite ICE+CFTC) · `petrole.yml` retire `api_weekly_surprise` (= pré-indicateur mardi d'EIA, perte assumée du signal mardi soir) · `nasdaq.yml` retire `concentration_top7` (inverse de `breadth`) · `argent.yml` retire `alpha_argent_vs_or_5j` (≈ `ratio_gold_silver`). Chaque fusion commentée dans le YAML (critère absorbé, poids avant/après, donnée secondaire abandonnée — pas de fallback dans le schéma). `weighting.yml`, normalisations, `seuils_reussite_pct` **intacts**.
- **Lot D — 2 mécanismes** : (1) `is_news_regime` diagnostiqué = **pas mort, juste rare** (4 déclenchements/51 logs, tous Cuivre 02-03/06 ; le « 0% » Cowork vaut post-06/06) — **modifie bien le score** (remplace INSUFFISANT par LONG/SHORT mesuré) → **conservé tel quel** + test synthétique prouvant déclenchement+impact conclusion. (2) `p2_M7_ratio_news` affichait jusqu'à 7269 % (réutilisait le ratio décisionnel non borné) → **borné [0,1]** = `|news|/(|news|+|quant|+ε)`. Le champ **décisionnel `ratio_news` est inchangé** (zéro impact scoring). Doc M7 mise à jour.
- **Lot C — compteur régimes** : `count_regimes()` = 1 + nb changements de direction sur les paris notés non-chevauchants. Affiché `N (régimes=Y)` dans `performance.md` + bilan hebdo. **Indicateur, zéro changement aux règles** (SELECTION-RULE reste N≥15). NB : le brief annonçait `LLLLSSSL → 4` mais c'est **3 régimes** (2 changements) — code correct, test ajusté.
- Tests : **1021 passed / 3 skipped** (l'unique « failed » = faux positif `test_aucune_ecriture_config`, disparaît une fois les fiches commitées). Pollution `v3/data/` (tests build_html/source_monitor préexistants) révoquée avant commit.

## 2026-06-10 (Session 5) — Fix backtest cache (faux vert) + garde-fou (@fullstack)

**Diagnostic d'un run `backtest-v2-fred` « success » mais CREUX.** Le run #1 (2026-06-10) a fini vert mais avec **0 date testée sur toutes les cellules** et **aucun `fred__` généré** → `+FRED` non clos. **Cause racine** (`historical_data.py`) : le nom du fichier cache embarque `end = aujourd'hui+1`. Le cache committé finit à `2026-06-06` → tout run un autre jour cherche `…__{autre_date}.csv` inexistant → cache miss 100% → fallback yfinance → bloqué en CI → DataFrame vide → 0 date → FRED jamais appelé. Le workflow ne marchait que le jour de (re)commit du cache.

- **Fix (A) — cache tolérant à la date** (`historical_data.py`) : `_fetch_yfinance_full` suit (1) cache exact, (2) **cache-hit via glob** `{prefix}__*.csv` (réutilise le cache dont la plage couvre la fenêtre, slice sur `[start, end]`), (3) yfinance. L'import yfinance est déplacé APRÈS (2) → le chemin cache n'importe jamais yfinance. Zéro invention (on tronque, on ne fabrique pas). COT/FRED non concernés (cache sans date de fin variable).
- **Fix (B) — garde-fou « échec visible »** (`backtest_quant.py`) : `BacktestNoDataError` + champ `n_dates_tested` ; si total dates testées = 0 → `raise` → `sys.exit(1)`. Plus de faux vert.
- **Tests** : `test_backtest_cache_glob.py` (8 tests, exercés **sans yfinance** via fixture forçant l'ImportError). `pytest -k backtest` : **29 passed** (les tests historiques `test_backtest.py` passent désormais aussi via le cache-hit glob — bénéfice direct du fix A).
- **Bénéfice** : le workflow `backtest-v2-fred` peut désormais tourner n'importe quel jour → relancé pour clore réellement l'arm `+FRED`.

## 2026-06-10 (Session 5) — Sonde futures 8h, PROVE-FIRST (Lot 1 étape 1, @infrastructure)

**Audit mesure 10/06 — Lot 1, étape 1 SEULEMENT (prove-first).** Objectif : pouvoir noter S&P 500 / Nasdaq / VIX depuis une référence **8h Paris** (Thomas entre à 8h sur turbos répliquant les futures Globex), au lieu de l'ouverture cash US 15h30 actuelle. **AUCUNE fiche ni `suivi.yaml` touchée** — c'est une sonde de disponibilité, le mapping attend le verdict du run CI + validation Thomas. Gel scoring respecté. Branche `claude/tradingapp-s5-shadow-5rapports-lq5g9z`.

- **Constat code (prouvé sans réseau)** : `_TICKER_MAP` ne contient **aucun future indice/VIX** (que des commodities) ; `ES=F`/`NQ=F`/`VX=F` non mappés → `_map_ticker` renvoie `None` → **fallback yfinance** → **n/a sur GitHub Actions** (Yahoo bloque les IP datacenter). En l'état, ces 3 symboles sortent n/a en CI.
- **Sonde** (`validate_symbols.py`, CLI `--freshness-8h`) : teste des **variantes pures Twelve** (ES/ES1!/NQ/NQ1!/VX/VX1!) hors `_TICKER_MAP`, deux critères — (a) répond (close>0), (b) **frais à 8h** (timestamp daté du jour, pas un close veille). Output → `v3/audit/symbol-validation-8h-run.md` (séparé du verdict d'analyse).
- **Workflow CI** `.github/workflows/probe-futures-8h.yml` : `workflow_dispatch` only, `permissions: contents: read`, **aucun commit**, artifact + log. À lancer **entre 08h00 et 08h30 Paris**. Shadow préservé (zéro schedule).
- **Verdict** (`v3/audit/symbol-validation-8h.md`) : **non concluable sans run CI réel à 8h**. Hypothèse probable (à confirmer) : ES/NQ/VX absents de Twelve free/Grow → pas de réf 8h gratuite → S&P/Nasdaq/VIX **restent 15h30, shadow-only**.
- **2 tests `test_validate_symbols.py` en échec corrigés** : ce n'était pas un `KeyError` mais une `AssertionError` (mock sans clé API franchissant un garde-fou légitime de `criteres_calculator`). Fix = `setenv` dans les tests, **code prod intouché**. +8 tests de fraîcheur. `pytest v3/tests/test_validate_symbols.py` : **25 passed** (avant : 2 failed/15 passed).
- ⚠️ **Secret à confirmer** : le brief dit `TWELVE_API_KEY`, le code/workflows utilisent `TWELVE_DATA_API_KEY`. Vérifier le nom réel côté repo avant le run (sinon « SKIP »).

## 2026-06-10 (Session 5) — WR tradable (Lot 2, @fullstack)

**Audit mesure 10/06 — Lot 2.** Ajout d'une métrique **WR tradable** = `VRAI / (VRAI + FAUSSE + non-conclusif)` à côté du WR conclusif existant, dans le Journaliste et les bilans. Motif : ~43 % des paris résolus sont non-conclusifs et exclus du WR conclusif, alors qu'en réel Thomas serait quand même en position ces jours-là → le WR conclusif surestime le WR exécutable. Mode shadow, **WIN RATE ONLY** (aucun euro), **gel du scoring** (zéro modif `scoring_analyste.py`/`weighting.yml`/poids/seuils de fiche). Branche `claude/tradingapp-s5-shadow-5rapports-lq5g9z`.

- **`journaliste.py`** : `select_non_overlapping_tradable` (fenêtre non-chevauchante VRAI/FAUSSE/NC), `CellKPI.tradable_eff_pct` + `n_tradable`, colonne « WR tradable » dans `render_performance` et l'archive hebdo. Invariant garanti par construction : `tradable_eff_pct <= taux_eff_pct` (même numérateur, dénominateur élargi).
- **`bilan_jour.py`** : `wr_tradable_jour` dans le bilan du jour. **`run_weekly.py`** : WR tradable dans le bilan semaine / Manager (champs `wr_tradable`/`n_tradable`, colonne « Cellules porteuses »).
- **Coexistence** : aucune métrique retirée, WR conclusif conservé pour le kill criterion v1 (gravé). `non-notee` et `suivi-interrompu` exclus des deux dénominateurs (constantes existantes réutilisées).
- **Tests** : `test_wr_tradable.py` créé (12 tests : calcul jeu mixte, invariant `WR_tradable <= WR_conclusif` paramétré, exclusion non-notee/interrompu). En-têtes `test_journaliste_v2.py` / `test_winrate_view_weekly.py` recalés. Zone : **78 passed** (vérif directe). Suite complète : 988 passed / 3 skipped / 8 échecs **environnementaux hors périmètre** (6 × yfinance absent, 2 × `test_validate_symbols` mock — à traiter au Lot 1).

## 2026-06-10 (Session 5) — SELECTION-RULE pré-enregistrée (Lot 3, @data-analyst)

**Audit mesure 10/06 — Lot 3.** Création de `v3/SELECTION-RULE.md` : règle de sélection des cellules à trader, **pré-enregistrée et gravée** (modèle `KILL-CRITERION.md`, statut VALIDÉ daté/signé Thomas, anti-post-hoc). Mode shadow, **WIN RATE ONLY**, **gel du scoring** (aucun poids/critère/seuil touché). Branche `claude/tradingapp-s5-shadow-5rapports-lq5g9z`.

- **Règle gravée** : à J+60 du shadow, ne trader QUE les cellules **24h** avec **WR tradable ≥ 70 % sur N ≥ 15 paris non-chevauchants** (N compté depuis `ref_changed` pour les cellules requalifiées). Aucune cellule éligible → pas de trading, revue J+90.
- **Deux métriques distinguées** : WR conclusif `VRAI/(VRAI+FAUSSE)` (kill criterion, moteur vivant) vs **WR tradable** `VRAI/(VRAI+FAUSSE+NC)` (sélection, métrique de décision de trading — introduite par le Lot 2). Décision Thomas validée 2026-06-10.
- **Limité au 24h** (7j/1m : autocorrélation → 15 sem/15 mois pour N indépendant, hors fenêtre J+60). `ref_changed` remet N à zéro dans les deux sens. Procédure J+60 écrite/signée, garde-fou anti-modification silencieuse (toute modif → `selection-rule-v2.md`).

## 2026-06-09 (Session 7b) — Tableau win rate affiché sur la page (@fullstack)

**Manque corrigé** : notre tableau win-rate-only propre (`v3/data/performance.md`, win rate par actif × horizon) n'était référencé **nulle part** dans `build_html.py` — Thomas ne voyait pas « le tableau avec les résultats d'orientation des actifs ». L'onglet Performance n'affichait que l'ancien A/B Taux/Brier (périmé). Mode shadow, WIN RATE ONLY, zéro modification de la logique de mesure, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### `build_html.py` — collecte + vue win-rate
- **`load_performance_md`** (nouveau) : lit `v3/data/performance.md` en markdown brut, ou `None` si absent (dégradation propre). Zéro transformation — réutilise tel quel le markdown du journaliste.
- **Nouvelle vue sidebar « 📈 Résultats / Win rate »** : rend le tableau win-rate-only via le pipeline marked.js existant (colorisation, tooltips, tables). Routage hash `#vue=resultats`. Absent → message de dégradation propre.
- **Onglet Historique modernisé** : le tableau win rate passe **en tête** (`#history-winrate`, résultats principaux) ; l'ancien bloc A/B Taux/Brier est **rétrogradé** dans un `<details>` replié « Détail technique par cellule » (masqué si `PERF_AB` vide). Les vues « Aujourd'hui »/« Bilan semaine » de la passe 1 et l'affichage des bulletins sont intacts.

### Tests — `v3/tests/test_build_html_winrate.py` (8 tests, verts)
- `load_performance_md` lit le MD / absent → `None` ; `render_html` embarque le tableau (`const WINRATE_MD`, grep de l'en-tête `| Actif | Win rate | …`) ; nav + section dédiées ; win rate en tête de l'onglet Historique + A/B rétrogradé ; dégradation propre (`WINRATE_MD = null`, pas de placeholder) ; garde-fou win-rate-only (aucun terme argent injecté par le builder). Suite complète `pytest v3/` : **984 passed, 3 skipped**. `git checkout -- v3/data/` avant commit (pytest régénère l'index).

## 2026-06-09 (Session 7) — Page index.html : affichage des 5 rapports (@fullstack)

**Bug corrigé** : depuis la refonte « 5 rapports », `build_html.py` ne ramassait QUE les `bulletin-*.md` (briefing 7h). Les suivis 12h/18h, le bilan du jour 22h et le bilan de semaine étaient produits mais **invisibles** sur la page. Mode shadow, WIN RATE ONLY, zéro modification de poids/seuils/scoring, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### `build_html.py` — collecte + rendu des nouveaux rapports
- **`build_reports_payload`** (nouveau) : collecte `v3/data/suivi/*.md` (12h/18h) + `v3/data/bilan-jour/*.md` (22h), tri date+heure décroissants, limite aux 30 jours récents. Chaque entrée porte `kind` (suivi/bilan-jour), `date`, `slot`. Dossier absent/vide → liste vide (dégradation propre, zéro crash).
- **`build_weekly_payload`** (nouveau) : renvoie le bilan de semaine le plus récent (`win-rate-YYYY-S##.md`, tri ISO année+semaine), ou `None`.
- **Sérialisation JS** factorisée (`_entries_to_js`) ; `REPORTS` + `WEEKLY` embarqués comme `BULLETINS`.
- **2 nouvelles vues** dans la sidebar : « 📅 Aujourd'hui » (briefing 7h + suivis + bilan du jour **regroupés par jour**, jour le plus récent ouvert par défaut, rendu MD paresseux par rapport) et « 🗓️ Bilan semaine ». Réutilisent le pipeline MD existant (marked.js + colorisation LONG/SHORT + tooltips + tables). Refacto : `showHistory`/`hideHistory` → `showAuxView`/`hideAuxViews` mutualisés (today/week/history).
- Dégradation propre : pas de bulletin mais des suivis → ouvre « Aujourd'hui » ; `WEEKLY` absent → section vide ; routage hash `#vue=aujourdhui` / `#vue=semaine`.

### Tests — `v3/tests/test_build_html_reports.py` (9 tests, verts)
- Collecte suivis+bilan (tri bilan 22h avant suivis, slots 12h/18h/22h), tri multi-jours, dossiers absents, fichiers hors format ignorés ; weekly le plus récent / absent ; rendu HTML inclut les 3 types ; dégradation propre sans rapports (`const WEEKLY = null`) ; garde-fou win-rate-only sur fixtures. Suite complète `pytest v3/` : **977 passed, 3 skipped**. JS embarqué validé (parse Node OK).

## 2026-06-08 (Session 6) — Finalisation refonte 5 rapports : CA-M7 + CA-B2 (@fullstack)

**Les 2 restes de la refonte implémentés** (spec §7 CA-M7/CA-B2). Mode shadow, WIN RATE ONLY, zéro modification silencieuse de poids/seuils/scoring, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### CA-M7 — Compteur de jours de bourse exclus (férié partiel) — `journaliste.py`
- **`is_partial_holiday(d)`** (nouveau, pur) : True si `is_trading_day(d)` exclut le run (jour de semaine férié de marché) alors qu'AU MOINS UN marché (NYSE/XNYS OU Euronext/XECB) est ouvert. Distinction des deux calendriers via la lib `holidays` (vérifié : Memorial Day = NYSE fermé/Euronext ouvert ; 1er Mai = inverse ; Noël = les deux). Fallback sans lib → False (zéro invention : on ne prétend pas savoir qu'un marché était ouvert ; le compteur sous-estime plutôt que de sur-compter).
- **`compter_jours_bourse_exclus(date_debut, date_fin)`** (nouveau) : compte les jours partiels sur la fenêtre inclusive.
- **`render_performance`** : nouvelle ligne « Jours de bourse exclus (férié partiel, un marché ouvert) : **N** sur la fenêtre {min émission} → {aujourd'hui} ». Fenêtre = de la 1ère date d'émission mesurée à aujourd'hui ; rien d'affiché si aucune mesure (pas de fenêtre inventée).

### CA-B2 — Clôture CAC officielle 17h30 (fallback robuste Q5) — `bilan_jour.py`
- Pour les actifs **EU (CAC)**, la clôture de référence du 24h = **close officiel 17h30** (bougie `1day` du jour J via `fetch_twelve_series`), PAS le spot 22h. Groupe EU résolu par `mesure_ouverture.actif_group` (override « CAC 40 → eu », heures depuis suivi.yaml — **zéro heure codée en dur**).
- **Fallback robuste (Q5 non validé en shadow)** : si Twelve ne renvoie pas de bougie datée du jour J (close 17h30 pas encore publié le soir même pour FCHI/ETF), on retombe sur le **dernier prix disponible + marqueur `[close approx]`** dans le tableau + note « À valider en live (Q5) ». **Zéro invention** : aucun close fabriqué.
- `build_bilan_jour` : nouveau param `fetch_series` (injectable, Twelve Data par défaut) + champ `BilanJour.close_approx_tickers`. Enveloppe `fetch_price` ; tous les autres actifs (US/continus) inchangés (spot 22h).

### Tests — `v3/tests/test_bilan_jour_cam7_cab2.py` (11 tests, verts)
- CA-M7 : `is_partial_holiday` (Memorial Day, 1er Mai, Noël non partiel, week-end non partiel), `compter_jours_bourse_exclus` (2 partiels sur mai, fenêtre vide, bornes inversées), affichage dans performance.md.
- CA-B2 : close officiel 17h30 utilisé si dispo (spot 22h ignoré), fallback `[close approx]` + note Q5 sinon, aucune mention monétaire.
- Gate `python3 -m pytest v3/ -q` : **968 passed, 3 skipped** (pré-existants). `git checkout -- v3/data/` avant commit.

## 2026-06-08 (Session 5) — Câblage cron/workflows des 5 rapports + stamps d'ouverture (@infrastructure)

**Routage des créneaux → bons runners + stamps d'ouverture aux VRAIES ouvertures** (spec §5 + CA-I*). Aucun run déclenché, mode shadow préservé, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### Routage par heure de Paris (cycle.yml — un seul workflow, runner selon l'heure réelle, DST-safe)
- **Nouveau step `Route`** : après la garde, calcule l'heure de Paris réelle et choisit le runner (`slot`) : **07h→`run_bulletin.py`** (R1 complet, stampe déjà les continus) · **08h05/09h05/15h35→`run_stamp.py`** (stamps d'ouverture prix-only) · **12h→`run_suivi.py 12h`** (R2 léger, PAS le bulletin, Q9) · **18h→`run_suivi.py 18h`** (R3) · **22h15 Paris→`run_bilan.py`** (R4, note les 24h). Les plages horaires absorbent l'écart été/hiver ; **jamais d'offset UTC en dur** (22h15 Paris = 20h15 UTC été / 21h15 UTC hiver — un `20h UTC` fixe noterait avant la clôture NYSE 5 mois/an).
- **Cron étendu** : créneaux historiques 7h/12h/18h **inchangés** (UTC fixe `5,10,16`, ne pas churner). Nouveaux créneaux (stamps + bilan) = **cron horaire `12,27,42 6,7,8,13,14,20,21`** + garde heure-Paris dans le step Route. Anti-doublon ×3 étendu (grep stamp/suivi/bilan). Steps conditionnés au `slot` (bulletin = ingest→bulletin→mesure→html ; stamp/suivi12/suivi18/bilan = runner unique). Garde `is_trading_day` (jours de bourse + fériés) + `force` **inchangée** pour tous les créneaux cycle.yml.
- **`v3/scripts/run_stamp.py`** (nouveau) : runner léger prix-only qui appelle `mesure_ouverture.stamp_prix_ouverture(now=...)` — AUCUN scoring/DeepSeek, idempotent + entry-lock (re-déclencher est sans effet). `stamp_prix_ouverture` ne stampe que les marchés ouverts à `now` → à 08h05 EU/US skippés, à 15h35 continus/EU déjà verrouillés. Aucune liste d'actifs codée (filtre par groupe de marché).

### Bilan semaine dimanche (workflow SÉPARÉ — choix Q7)
- **`.github/workflows/weekly-summary.yml`** (nouveau) : `schedule "12,27,42 16 * * 0"` (dim 16h UTC = 18h Paris) + `workflow_dispatch`(input `force`) + push `v3/RUN-WEEKLY.txt`. **Garde INVERSÉE vs cycle.yml** : bypass `is_trading_day`, ne tourne QUE le dimanche (`weekday()==6`/`%u==7`), `force=true` bypass (CA-W1.c). Anti-doublon ×3. Step `run_weekly.py`. **Garde-fou CA-W4 au commit** : refuse si `git diff v3/config/` non vide (le Manager n'applique rien).

### VPS Anya (horloge — routage autoritaire côté workflow)
- **`trigger-cycle.sh`** : créneaux Paris étendus à `07/08/09/12/15/18/22` (jours ouvrés → cycle.yml) + **dimanche 18h → weekly-summary.yml** (workflow cible choisi dans le script). Samedi muet. Flag **`--check`** (sortie parseable des créneaux, CA-I3). **`crontab.tradingapp`** : minute `0`→**`15`** (`15 * * * *`) pour que le tir 22h tombe à 22h15 Paris (≥ garde routage) — jamais un UTC fixe.

### Table de vérité (`test-guard-logic.sh`) — tous verts
- Ajout `route_slot` (miroir du step Route) + `weekly_decision` (garde workflow dimanche). Nouveaux cas : 7 créneaux de routage (été+hiver), bilan 22h15 vs 22h00→none, 8 cas weekly (dimanche/lundi/samedi/force/push). **ALL PASS.**

### CA-I* couverts / restants
Couverts : **CA-I1** (22h → R4 seul, pas de re-scoring) · **CA-I2** (dimanche → R5 seul, bypass bourse, weekday()==6) · **CA-I3** (VPS `--check` parseable : `22h15-paris-jours-bourse` + `18h-dimanche`) · **CA-I4** (anti-doublon ×3 sur 22h). **Restants @fullstack** (logique de MESURE, hors périmètre infra — touchent `bilan_jour.py`/`journaliste.py`, et CA-B2 dépend de Q5 non validé en shadow) : **CA-M7** (compteur `jours_bourse_exclus` dans performance.md) · **CA-B2** (close CAC officiel 17h30 dans le bilan). **Gates** : `pytest v3/ -q` 957 verts · `test-guard-logic.sh` ALL PASS · cycle.yml + weekly-summary.yml YAML valides · trigger `bash -n` OK. **Aucun run déclenché.**

## 2026-06-08 (Session 5) — Phase 3 refonte 5 rapports : bilan de la semaine dimanche 18h + le Manager (@fullstack)

Implémentation de la **Phase 3** (dernière) de `v3/docs/reco/spec-refonte-5-rapports.md` (v2, §4 + CA-W*) : le **bilan de la semaine (R5)** produit dimanche 18h + **le Manager**, 4e agent historique du système (Veilleur / Analyste / Journaliste / **Manager**), enfin implémenté. Le Manager est la couche apprentissage/pilotage : il LIT les résultats de la semaine et **PROPOSE des ajustements de config — Thomas VALIDE à la main, jamais d'application silencieuse**. **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention.**

### Livrables (@fullstack)
- **`v3/scripts/run_weekly.py`** (nouveau, R5 + Manager) — `build_bilan_semaine(now=...)` produit `v3/data/bilan-semaine/{AAAA-Sxx}.md`. Sections : (1) **win rate de la semaine** (archive hebdo `win-rate-{ISO}.md` reprise **telle quelle**, CA-W2) ; (2) **win rate par conviction** forte/faible (§4.7/CA-W6 — réutilise `bilan_jour.win_rate_par_conviction` + `load_conviction_map`, zéro nouveau champ ; conviction lue au decision-log du jour de décision) ; (3) **cellules porteuses** = ce qui MARCHE (§4.6, win rate ≥ 65% sur N_eff ≥ 5) ; (4) cellules à surveiller ; (5) **propositions d'ajustement** (format strict §4.5) ; (6) observations sans proposition ; (7) **dates de sortie de warm-up** par horizon (24h ~juillet, 7j ~octobre, 1m hors portée). **Réutilise `journaliste.measure()`** pour les KPIs (zéro recalcul custom). `wilson_low` du KPI ∈ [0,1] → converti en %. Fuseaux `ZoneInfo`, jamais d'offset en dur. CLI `python3 run_weekly.py`.
- **Le Manager — détection (le P0 corrigé du trio)** : une cellule est **faible** (→ proposition) UNIQUEMENT si **N_eff ≥ 10 ET Wilson_low < 50% ET observé sur ≥ 2 semaines CONSÉCUTIVES**. Entre N_eff 5-9 → **observation, PAS de proposition** (« mesurer avant d'agir »). Persistance inter-semaines via snapshots `v3/data/bilan-semaine/.state/{ISO}.json` (candidates faibles de la semaine), relus pour confirmer la 2e semaine — **donnée de mesure, jamais de la config**. Chaque proposition est justifiée par les **chiffres réels du KPI** (win rate, N_eff, Wilson) — zéro invention. **Le Manager n'applique RIEN** (CA-W4 : `git diff v3/config/` vide après run, **testé**).
- **Tests** — `test_run_weekly.py` (14 cas dérivés des CA-W* : petit N → pas de proposition, 1ère semaine → observation, **2 semaines consécutives → proposition**, champs obligatoires CA-W3, **`git diff v3/config/` vide après run** CA-W4, cellules porteuses §4.6, win rate par conviction CA-W6 + N insuffisant, **zéro montant** WIN-RATE-ONLY, persistance inter-semaines roundtrip, archive hebdo reprise telle quelle CA-W2). **957 tests verts** (+14), `v3/data/` non pollué (`git checkout` + dossier `bilan-semaine/` + `.state/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-W* couverts / restants
Couverts : **CA-W1 (guard dimanche — logique build, le déclenchement infra restant), CA-W2, CA-W3, CA-W4, CA-W5, CA-W6**. Restants (dépendent de l'infra — @infrastructure) : **CA-I2** (schedule dimanche 16h UTC + bypass `is_trading_day` + guard `weekday()==6` dans `cycle.yml`), **CA-I3** (créneau dimanche VPS Anya). Le cron dimanche 18h = infra, séparé (pas de PR, pas de run déclenché).

## 2026-06-08 (Session 5) — Phase 2 refonte 5 rapports : suivis 12h/18h légers + runner bilan 22h (@fullstack)

Implémentation de la **Phase 2** de `v3/docs/reco/spec-refonte-5-rapports.md` (v2, §3.2/§3.3) : les rapports de **SUIVI 12h (R2) et 18h (R3)**, courts (Thomas lit en 2 min), + le **runner CLI du bilan 22h** (R4). **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention. Le suivi N'ÉCRIT PAS dans measures-log (pas de cellule mesurée, pas de re-scoring DeepSeek).** Phase 3 (Manager dimanche) NON faite.

### Livrables (@fullstack)
- **`v3/scripts/run_suivi.py`** (nouveau, R2/R3) — `build_suivi(report_type, now=...)` lit les positions 24h du **Briefing 7h du jour** (`load_briefing_cells`, exclut INSUFFISANT) et produit `v3/data/suivi/{date}-{12h|18h}.md`. Pour chaque actif : **statut vs SON ouverture** (`(prix − ouverture)/ouverture` % → ✅ gagne / ⚠️ perd / — neutre sous `neutral_band_pct`), **dynamique de tendance** (↑ s'accélère / ↓ s'essouffle / ⇄ se retourne vs le suivi précédent — snapshot 12h relu au 18h ; flags US ↗ confirmé / ↘ infirmé au 18h), **suggestion de sortie** (`Sortie à envisager` si `|Delta%| ≥ SEUIL_PCT_actif` CONTRE le call — **drapeau, jamais un ordre** ; sinon Hold/Surveiller), **news à impact** (court, best-effort depuis le decision-log 7h, zéro DeepSeek). **Marchés US à 12h** : affichés explicitement `🕐 pas encore ouvert` (ouverture 15h30) — pas de ligne trompeuse ; 1er statut US au 18h. Heures via `mesure_ouverture.actif_group`/`is_open_for_stamp` (ZoneInfo, **jamais d'offset en dur**). **Léger** : prix + news, PAS de matrice LONG/SHORT, PAS de scoring (Q9). CLI : `python3 run_suivi.py 12h|18h`.
- **`v3/scripts/run_bilan.py`** (nouveau, runner R4) — appelle `bilan_jour.build_bilan_jour(now=...)` (Phase 1) + `write_bilan_jour`. CLI `--date`. Le **déclenchement 22h15 Paris = infra (séparé)**.
- **Tests** — `test_run_suivi.py` (15 cas dérivés des CA-S* : briefing 24h actionnables, statut vs ouverture ✅/⚠️/neutre, dynamique ↑/↓/⇄ + Δ vs 12h au 18h, flag US confirmé/infirmé, drapeau sortie au seuil contre le call, US pas-ouvert à 12h (🕐) puis ouvert à 18h, **run_suivi n'écrit pas measures-log**, rapport court sans matrice, zéro mention monétaire, ouverture absente → —, runner bilan smoke). **943 tests verts** (+15), `v3/data/` non pollué (`git checkout` + dossier `suivi/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-S* couverts / restants
Couverts : **CA-S1, CA-S2, CA-S3, CA-S4, CA-S5, CA-S6, CA-S6b** + runner R4 (CA-B* déjà couverts en Phase 1). Restants (dépendent de l'infra — @infrastructure) : **CA-I1/I3/I4** (steps cycle 12h/18h/22h appellent run_suivi/run_bilan, anti-doublon, créneaux VPS), **Q9** (les créneaux 12h/18h lancent-ils encore run_bulletin complet ? — décision Thomas/infra).

## 2026-06-08 (Session 5) — Phase 1 refonte 5 rapports : mesure ouverture→clôture + bilan 22h (@fullstack)

Implémentation de la **Phase 1** de `v3/docs/reco/spec-refonte-5-rapports.md` (v2) : le prix de référence du 24h passe de « prix au run 7h » (souvent marché fermé / prix de nuit) à l'**ouverture propre de chaque marché → clôture, jugée à 22h le jour même**. Corrige l'artefact signalé par Thomas (call jugé FAUX à cause du prix de nuit). **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention.** Phases 2 (suivis 12h/18h) et 3 (Manager dimanche) NON faites.

### Avant / après (Or 24h, démontré)
Même mouvement réel, call LONG : **ancien** modèle réf=3500 (prix 7h nuit) → clôture 3420 = −2.3 % → **FAUSSE** (artefact). **Nouveau** modèle réf=3400 (ouverture propre 8h) → clôture 3420 = +0.59 % → **VRAI** (vraie tendance de session).

### Livrables (@fullstack)
- **`v3/scripts/mesure_ouverture.py`** (nouveau) — `stamp_prix_ouverture(date_j, now=...)` écrit `v3/data/prix-ouverture/{YYYY-MM-DD}.json` (1/jour, clé par date, distinct de prix-emission). Stampe chaque actif **après l'ouverture de son marché + délai 5 min** (continus 08h05, CAC 09h05, US 15h35 — heures Paris via `ZoneInfo`, **jamais d'offset codé en dur**). Idempotent + entry-lock (ré-écriture refusée). Twelve KO → ticker **absent** du JSON (zéro invention → suivi-interrompu). Mapping groupe EU/US/Continu par **famille de fiche** + override par nom (CAC=eu, S&P/Nasdaq/VIX=us, reste=continu). **Convention 08h des continus = référence conventionnelle assumée (Q10, décision Thomas), PAS close-to-close** — documentée. Config `v3/config/suivi.yaml` (`neutral_band_pct`, `open_stamp_delay_min`, heures, mapping).
- **`v3/scripts/journaliste.py`** — (1) **Référence 24h/7j/1m = prix d'ouverture** du jour de décision (`_resolve_prix_reference`), **fallback prix-emission + WARNING** si ouverture absente (Q3/CA-M5). Champ `prix_reference_source` (`ouverture`/`emission`) tracé dans `measures-log.jsonl`. (2) **Filtre 7h (CA-M6/M6b)** : `is_seven_am_bulletin` (reconnaît `07h` Paris, `05h` UTC historique, ancien nommage) + `measure(only_seven_am=True)` → seul le Briefing 7h est noté ; les suivis 12h/18h sont marqués `non-noté` (exclus des KPIs). **Fin du gonflement N_brut ×3.** (3) `run()` stampe l'ouverture (continus à 7h, EU/US complétés aux runs ultérieurs), param `prix_ouverture_dir` isolable.
- **`v3/scripts/bilan_jour.py`** (nouveau, R4) — `build_bilan_jour(now=...)` note les calls 24h du 7h (ouverture→clôture), produit le markdown R4 : résultat par actif, **win rate du jour**, **win rate par conviction** forte/faible (CA-W6, depuis decision-log : `score_pm1` + drapeaux `coin_flip`/`quasi_neutre`/`mono_critere_dominant`/`diverge`), **FAUX à gros mouvement** (flag `⚡` si |delta| ≥ 2×seuil, tri par **amplitude % — PAS d'argent**), news qui ont compté (Option C croisement, zéro DeepSeek), catalyseurs J+1 best-effort. **Le déclenchement 22h15 Paris = infra (à faire), la FONCTION est construite et paramétrable par `now`.** Config `v3/config/manager.yaml` (`score_fort_seuil`). **Aucune mention monétaire** (test garde-fou).
- **Tests** — `test_mesure_ouverture.py` (15 cas dérivés des CA-M*/CA-B*/CA-W6 : mapping groupe, délai+DST, stamp idempotent/entry-lock, Twelve KO absent, 24h=ouverture, fallback émission, filtre 7h reconnaissance + fin ×3, conviction forte/faible, bilan note 24h, zéro montant, flag gros move). `conftest.py` autouse anti-pollution prix-ouverture. 2 tests adaptés au nouveau modèle (multislot : 16h désormais `non-noté` ; audit veille : bulletin 7h). **928 tests verts** (+15), `v3/data/` non pollué (`git checkout` + dossiers `prix-ouverture/`+`bilan-jour/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-M* couverts / restants
Couverts : **CA-M1, CA-M2, CA-M3, CA-M4, CA-M5 (Q3), CA-M6, CA-M6b, CA-B1, CA-B3, CA-B4, CA-B5, CA-W6**. Restants (dépendent de l'infra — @infrastructure) : **CA-M7** (compteur `jours_bourse_exclus` dans performance.md), **CA-B2** (clôture CAC=17h30 — comportement Twelve à valider Q5), **CA-I1/I4** (cron 22h + anti-doublon), créneau VPS 22h15.

## 2026-06-08 (Session 4) — `performance.md` refondu en tableau WIN RATE propre + archive hebdo figée

Thomas trouvait `performance.md` illisible (colonne « Alertes » = pavé répété sur chaque ligne, Brier inutile, double colonne de taux, 1m absent). **Présentation + nouveau fichier hebdo uniquement — zéro changement de la logique de mesure** (entry-lock, look-ahead, N_eff, seuils VRAI/FAUX, decision-log inchangés).

### Correctif (@fullstack)
- **`v3/scripts/journaliste.py`** — `render_performance` réécrit en **tableau win-rate-only** : colonnes `Actif | Win rate | Paris (réels) | Non notés | Statut`, **groupé par horizon (24h → 7j → 1m), trié par win rate décroissant**, **36 cellules (12 actifs × 3 horizons) toujours visibles dont le 1m** (`⏳ en attente`). Win rate = `taux_eff` (N_eff indépendants, pas le N_brut gonflé ×3). Statuts win-rate-only sans aucune notion d'argent : `⏳ trop peu (N/15)` / `✅ objectif atteint` (N_eff ≥ 15 ET ≥ 70 % ET Wilson_low > 50 %) / `❌ sous l'objectif` / `⏳ en attente`. Ligne de synthèse en tête (`X / 36 cellules fiables`). **Retirés de l'affichage** : Brier, `Taux_brut`, colonne « Alertes » (pavé), `LONG/SHORT`, statut shadow répété, P&L (jamais présent) — **conservés dans `measures-log.jsonl`/decision-log pour le technique**. Section « Flip vs continuation » réduite à 2 lignes d'agrégats (omise si pas de données).
- **Archive hebdomadaire figée** — nouvelle `render_weekly_winrate` + `write_weekly_winrate` : à chaque run, écrit le même tableau (win rate **cumulé** + colonne **« Nouveaux paris (semaine) »**) dans `v3/data/performance/weekly/win-rate-{AAAA-Sxx}.md` (semaine ISO Europe/Paris). Réécrit pendant la semaine, **figé** dès qu'elle est passée (plus aucun run ne le touche) → historique semaine par semaine. Helpers `iso_week_label` / `iso_week_bounds`. Dossier `v3/data/performance/weekly/` créé (`.gitkeep`).
- **`build_html.py` inchangé** : la page ne rend PAS la matrice de `performance.md` (l'onglet Historique lit `measures-log.jsonl` + `performance-ab.md`, tous deux intacts) → aucune incohérence introduite.
- **Tests** : `test_winrate_view_weekly.py` neuf (18 cas : colonnes, tri décroissant, 36 lignes dont 1m, statuts, synthèse, semaine ISO, archive au bon chemin, colonne nouveaux paris, run bout-en-bout). Tests asservis à l'ancien format mis à jour (`test_journaliste_v2.py`, `test_lot6_publication_observabilite.py`, `test_journaliste.py`). **913 tests verts**, `v3/data/` non pollué (`git checkout` post-run, dossier `weekly/` préservé). Shadow préservé, aucun run déclenché.

## 2026-06-08 (Session 4) — Détail par actif : synthèse directionnelle 24h/7j/1m placée avant le tableau de chaque actif

Thomas voulait voir la **décision des 3 horizons d'abord**, puis le détail des critères qui la justifie. Avant : sous `### {nom}` on enchaînait directement le tableau, et la ligne « Scores » arrivait après. **Mise en page uniquement — zéro changement de chiffre, score, logique ou conclusion.**

### Correctif (@fullstack)
- **`v3/scripts/scoring_analyste.py`** — ligne de synthèse directionnelle insérée juste après `### {nom}` et **avant** le tableau de critères : `**24h : LONG (+20.00) · 7j : SHORT (−8.16) · 1m : SHORT (−3.90)**` (direction `r.conclusions[h]` + note signée `r.scores[h]` à 2 décimales, séparateurs `·` cohérents avec le bulletin). L'ancienne ligne `- Scores : 24h=… · 7j=… · 1m=…` placée **après** le tableau (désormais redondante) a été **retirée** (pas de doublon).
- **Tests** : `test_detail_synthese_avant_tableau` (neuf) vérifie l'ordre titre < synthèse < en-tête de tableau, les 3 horizons avec note signée 2 décimales, et l'absence de l'ancienne ligne « - Scores : ». **898 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Mesure VRAI/FAUX et decision-log identiques. Shadow préservé, aucun run déclenché.

## 2026-06-06 (Session 4) — Noms des 100 critères reformulés en langage trader

Thomas ne comprenait pas les noms de critères (« NOAA drought % Midwest+Plains D2+ », « USDA WASDE stocks-to-use mondial », « CFTC COT nets »…). Implémentation de la spec @copywriter `v3/audit/reco-wording-noms-criteres.md` — **champ `nom:` uniquement**, zéro modification de `cle_courante`, poids, signe, source, normalisation, seuils, logique, score ou conclusion.

### Correctif (@fullstack)
- **`v3/config/fiches/*.yml` (12 fiches)** — les **noms des 100 critères** (115 libellés `nom:` gates inclus) reformulés en langage trader : **acronymes de sources retirés** (NOAA, WASDE, COT/CFTC, COMEX, LME, SHFE, EIA, API, DXY, GATE, NASS, GASC, EUDR, FedWatch, Caixin…) → libellés clairs (ex. « NOAA drought % Midwest+Plains D2+ » → « Sécheresse dans les plaines céréalières US » ; « CFTC COT nets » → « Positionnement des gros spéculateurs (or) » ; « DXY trend 20j » → « Tendance du dollar (20 jours) »). **Acronymes porteurs d'info conservés** (PMI, RSI, VIX/VXN/V2X, SKEW/VVIX, ICE, CAPE) + **mini-glossaire** ajouté 1× en pied de la section « Détail par actif » (`v3/scripts/scoring_analyste.py`, `DETAIL_TABLE_GLOSSARY_LINES`).
- **Tests** : `v3/tests/test_fiches_wording.py` (neuf, 4 cas) — aucun acronyme de source dans les `nom:` des fiches réelles, blé sans « NOAA », COT or traduit, glossaire citant PMI/RSI/VIX/SKEW/VVIX. **897 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Shadow préservé, aucun run déclenché.

## 2026-06-06 (Session 4) — Tableau « Détail par actif » reformulé en langage trader

Thomas ne comprenait pas les lignes critères du tableau (`zscore`, `Norm.`, `Signe -1`, `lineaire centre=75 echelle=12`…). Implémentation de la spec @copywriter `v3/audit/reco-wording-detail-bulletin.md` — refonte des libellés/colonnes uniquement, **zéro changement de chiffre, score, logique ou conclusion**.

### Correctif (@fullstack)
- **`v3/scripts/scoring_analyste.py`** — en-têtes reformulés (9 colonnes, « Note » supprimée) : `Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m`. Types traduits via `TYPE_NORM_LABELS` (zscore→Écart à la normale, lineaire→Échelle graduée, mapping_non_monotone→Régime par seuils, composite→Signal combiné, triplet→Direction news, gate→Drapeau régime ; fallback sur le brut si type inconnu, pas de crash). Colonne **Sens** humaine : `normal` (signe +1) / `inversé` (signe -1), `—` pour les gates. **Gate actif préservé** : « Drapeau régime ⚑ actif » affiché dans « Comment c'est lu » (info de risque ex-portée par la colonne Note). Paramètres techniques `centre=X echelle=Y` retirés de la vue (restent au decision-log). Encart **« Comment lire ce tableau »** statique inséré 1× avant le 1er actif.
- **`v3/scripts/build_html.py`** — masquage mobile recalé sur le tableau 9 colonnes : 3e (« Valeur actuelle ») + 4e (« Penchant ») au lieu de l'ex-10e (« Note » disparue). Tableau lisible sur mobile (Critère + Sens + 3 colonnes Effet conservés).
- **Tests** : assertions des en-têtes / Note / masquage mobile mises à jour (`test_bulletin_top3_fusion.py`, `test_build_html_multislot.py`), + 2 tests neufs (`test_detail_table_wording_humain`, `test_detail_table_sens_inverse`) vérifiant nouveaux en-têtes, traduction de type, Sens normal/inversé et encart unique. **893 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Mesure VRAI/FAUX et decision-log identiques. Shadow préservé.

## 2026-06-06 (Session 4) — Fériés de marché AUTO via lib `holidays` (NYSE XNYS + Euronext XECB) — fin de la maintenance annuelle manuelle

**Demande fondateur** : que la mise à jour des jours fériés de marché soit **automatique chaque année, zéro maintenance manuelle**. Avant : `MARKET_HOLIDAYS` était une liste statique « à étendre chaque année » → dette de maintenance + risque d'oubli (un férié non recopié = run sur prix figés).

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** — `_is_market_holiday` refondu : **source PRIMAIRE = lib `holidays`**, calendrier **XNYS** (NYSE) **∪ XECB** (TARGET/ECB = exactement les fermetures Euronext : 1 Jan, Vendredi saint, Lundi de Pâques, 1 Mai, 25 Déc, 26 Déc), **calculé pour l'année de la date testée** → valable 2026/2027/2028… **automatiquement**, plus de liste à étendre. `_is_market_holiday(d) = d ∈ (XNYS(d.year) ∪ XECB(d.year)) ∪ MARKET_HOLIDAYS`.
- **`MARKET_HOLIDAYS` (statique)** → devient (1) **fallback déterministe** anti-crash si la lib est absente/échoue, (2) **filet d'override manuel** pour fermetures ad-hoc hors lib (deuil national, etc.). Commentaire « à étendre chaque année » remplacé par « la lib couvre l'auto ; ce set = overrides exceptionnels + fallback ». Couverture 2026 conservée pour le fallback.
- **ROBUSTESSE (garde-fou critique)** : tout échec (ImportError, code financier absent de la version, API différente) → `_is_market_holiday` retombe **proprement** sur le socle statique, **JAMAIS de crash** (un crash dans la garde = NO-OP permanent du pipeline). Pattern try/except import préservé et durci.
- **`.github/workflows/cycle.yml`** — étape Guard : `pip install -q holidays || echo …` ajouté **juste avant** l'appel `python3 -c is_trading_day` (la garde tourne AVANT le setup des deps). Si ce pip échoue (réseau), `|| true` n'interrompt rien → fallback statique. Table de vérité + commentaires mis à jour (source des fériés devient auto ; logique conceptuelle inchangée). YAML revalidé (`yaml.safe_load`).
- **`v3/requirements.txt`** : `holidays==0.98` ajouté (pure-python) pour le pipeline de mesure.
- **Tests `v3/tests/test_is_trading_day.py`** (7 → **12 cas verts**) : **PREUVE de l'automatisme** — fériés **2027** (Noël 24/12, Thanksgiving 25/11, Lundi de Pâques 29/03) et **2028** (Vendredi saint 14/04, Thanksgiving 23/11, 1 Mai) calculés par la lib, **absents du statique** → `is_trading_day=False` ; **cohérence croisée** lib (XNYS ∪ XECB) vs statique **2026** (identiques, zéro divergence) ; **fallback ImportError** via monkeypatch → pas de crash, jour ouvré non bloqué. Simulation du chemin CI exact (`python3 -c`) : Noël 2026/2027, Thanksgiving 2027, Vendredi saint 2028 → NO-OP ; mardis ordinaires 2026/2028 → run. **Aucune régression** (174 tests journaliste/mesure verts). `v3/data/` non pollué.
- **Garde-fous** : zéro invention, mode shadow, logique de compute non touchée (calendrier de garde uniquement), aucun jour ouvré normal bloqué, fallback anti-crash testé. **Aucun run déclenché.** `test_scoring.py` non touché (autre agent en parallèle).

## 2026-06-06 (Session 4) — Test audit-veille rendu déterministe (date figée jour ouvré) — fin du faux rouge week-end

**Bug du test (pas du code)** : `test_audit_veille_liste_conviction_normale_vrai` et `test_audit_veille_exclut_faible_carry_news` (`v3/tests/test_scoring.py`) ancraient `now = datetime.now()` puis `bdate = now - 1 jour`. Le **samedi**, `bdate` = vendredi et la logique d'échéance 24h jour-ouvré/fériés (ajoutée en S3) reporte au lundi → la cellule n'est « pas encore » mesurable → l'assertion `assert "Pas encore" not in txt` casse. Le test échouait donc **uniquement selon le jour réel d'exécution** (rouge le samedi 06/06, vert en semaine).

### Correctif (@fullstack)
- **`v3/tests/test_scoring.py`** : `now` figé sur **`datetime(2026, 6, 9, 12, 0)`** (mardi) → `bdate` = **lundi 2026-06-08** (jour ouvré, NI week-end NI férié de marché) → échéance 24h mûre quel que soit le jour réel. **2 tests corrigés**. Assertions métier intactes (✅, VRAI, +5.00%, exclusion faible/carry/news). `test_audit_veille_warmup_message` laissé tel quel (indépendant du jour : vérifie le message warm-up sans cellule à mesurer).
- **Gate** : `python3 -m pytest v3/tests/test_scoring.py -q` → **33 passed, 100% vert** (dont les 3 `test_audit_veille_*`). `v3/data/` non pollué (`git checkout` post-run).

## 2026-06-06 (Session 4) — Garde de run étendue aux jours fériés de marché (réutilise `MARKET_HOLIDAYS`)

**Demande fondateur (« point final »)** : des rapports **uniquement les jours où la bourse est OUVERTE**. Le week-end était déjà coupé ; il manquait les **jours fériés de marché** — un lundi férié (NYSE/Euronext fermés) produisait encore un bulletin sur **prix figés à la clôture précédente** + mesures 24h dégénérées (« +0.0% ») qui polluent le shadow.

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** : nouvelle fonction importable **`is_trading_day(d: date) -> bool`** = `jour ouvré (lun-ven) and not _is_market_holiday(d)`. **SOURCE DE VÉRITÉ UNIQUE** : réutilise EXACTEMENT le calendrier existant `_is_market_holiday` / `MARKET_HOLIDAYS` (NYSE ∪ Euronext) — **zéro liste de dates dupliquée**, une seule à maintenir. La fonction ne juge QUE le jour (le bypass `force` reste dans la garde YAML).
- **`.github/workflows/cycle.yml`** — étape Guard : le test week-end bash pur est remplacé par un appel **Python** à `is_trading_day(today Europe/Paris)` (stdlib + `MARKET_HOLIDAYS` statique, aucune dépendance réseau/pip — `python3` est dispo sur les runners avant le setup deps). Conservé : échappatoire `force`/`RUN-CYCLE.txt` (bypass tout), anti-doublon ×3 schedule-only. Si bourse fermée (week-end **OU** férié) et pas de force → `run=false` (NO-OP) avec log clair (« week-end » / « férié de marché AAAA-MM-JJ »). Table de vérité mise à jour (ligne « dispatch (VPS) / jour férié / false → NON ← FIX »).
- **VPS (`trigger-cycle.sh`)** : la garde week-end bash y reste (fast-path) ; les **fériés** sont gérés de façon **autoritaire au niveau du workflow** (le VPS n'a pas l'env Python du repo et NE recopie AUCUNE liste de fériés). Le VPS peut tirer un lundi férié → le workflow NO-OP. Documenté dans `v3/ops/vps-trigger/README.md`.
- **Tests** : `v3/tests/test_is_trading_day.py` (7 cas : mardi True, samedi/dimanche False, **férié réel de `MARKET_HOLIDAYS`** False, cohérence calendrier, signature `is_trading_day(d)` sans `force`). `test-guard-logic.sh` étendu (param `holiday`) → **13 cas verts** dont férié schedule/dispatch/force/push. `v3/data/` non pollué (vérifié).
- **Garde-fous** : zéro duplication du calendrier, zéro invention, mode shadow, aucun jour ouvré normal bloqué, logique de compute non touchée (garde de déclenchement uniquement). Aucun run déclenché.

## 2026-06-06 (Session 4) — Garde week-end étendue à `workflow_dispatch` (VPS) + input `force` + garde jour-ouvré VPS

**Bug** : un briefing a été produit **samedi 06/06 07h** alors que le week-end doit être coupé. **Cause racine** (diagnostiquée, non ré-enquêtée) : la garde week-end de `cycle.yml` ne s'appliquait qu'aux événements `schedule`. Or le **driver réel** est le **pinger VPS**, qui déclenche en **`workflow_dispatch`**. L'early-exit en tête de garde (`if event != schedule → run=true; exit`) traitait `workflow_dispatch` comme un forçage manuel → le NO-OP week-end (plus bas) n'était jamais atteint pour le VPS. Résultat : run samedi sur prix figés (clôture vendredi) → mesures 24h dégénérées polluant le shadow.

### Correctif (@infrastructure)
- **`.github/workflows/cycle.yml`** : input booléen **`force`** (défaut `false`) ajouté à `workflow_dispatch`. Garde **restructurée** (table de vérité en commentaire) : (1) **forçage explicite** = `inputs.force=='true'` **OU** push `RUN-CYCLE.txt` → `run=true`, bypass tout (week-end inclus) = échappatoire humaine ; (2) **sinon** (schedule OU dispatch-VPS sans force) → **garde week-end** (sam/dim Europe/Paris → `run=false`) ; (3) jour ouvré → **anti-doublon ×3 pour le schedule uniquement** (VPS = 1 tir/créneau, toujours passé, comportement préservé). **Aucun run de semaine affecté.**
- **`v3/ops/vps-trigger/trigger-cycle.sh`** : **garde jour-ouvré** ajoutée (`TZ=Europe/Paris date +%u ≥ 6 → exit 0`) → le pinger ne dispatche même pas le week-end (économise un no-op, cohérence). `TRADINGAPP_FORCE=1` bypass aussi. Garde week-end côté `cycle.yml` conservée en **défense en profondeur**.
- **`v3/ops/vps-trigger/test-guard-logic.sh`** : nouveau script de test (miroir exact de la décision YAML) — **10 cas verts** dont les 6 clés de la table de vérité. README VPS documenté.
- **Garde-fous respectés** : aucun run déclenché (logique seule), compute du pipeline non touché (garde de déclenchement uniquement), mode shadow préservé.

## 2026-06-06 (Session 4) — `mining_com` retiré (403 Cloudflare persistant CI, retry inefficace)

**Contexte** : le retry 403 borné posé le 05/06 (`RETRY_STATUS_WITH_403`, cf. Bug 2 plus bas) **n'a PAS résolu** le problème. Le run live frais du 06/06 07h montre `mining_com` **toujours ❌ HTTP 403**. **Diagnostic confirmé** (pas ré-enquêté) : blocage **Cloudflare PERSISTANT sur la plage d'IP des runners GitHub Actions** — le feed répond 200 ailleurs, jamais depuis CI. Le retry ne peut rien faire si TOUTE la plage d'IP est bloquée (≠ 403 intermittent par requête, hypothèse du 05/06 invalidée). **Décision (avec Thomas) : retirer la source** (poids faible ~1.1, redondante avec `investing_commodities`/`investing_metals` poids 0.9 + `oilprice`).

### Retrait (@fullstack)
- **`v3/scripts/config.py`** : ligne `("mining_com", …)` retirée de `EARLY_SIGNAL_FEEDS` + poids `"mining_com": 1.1` retiré de `SOURCE_WEIGHTS`. Commentaire de retrait documenté in-place (pourquoi). Le **total de flux n'est PAS figé** (`source_monitor.summary()` = `len(self.by_name)` dynamique) → il se décrémente seul, plus de faux « partiel ». Plus aucun appel `mining_com` → plus de ❌ 403 dans `source-health.md`.
- **Aucun critère cassé** : les news sont poolées + matchées par mots-clés. Les critères `mining_strikes_*`/`demande_pv_mining_strikes` (cuivre/argent) matchent sur le **pool global** de news, sans dépendance au flux `mining_com` (vérifié : zéro mapping nommé vers le flux). Le retrait enlève quelques items, ne touche ni scoring ni mesure.
- **Mécanisme retry 403 conservé** pour les autres RSS scrapables (`RETRY_STATUS_WITH_403` reste utile si un flux a un 403 *réellement* intermittent) — commentaires généralisés (plus de dépendance à mining.com comme exemple).
- **Pas de remplacement câblé** : aucun flux métaux/mining RSS gratuit n'a de certitude de marcher depuis les runners CI (c'est le piège exact qui a tué mining_com). Candidats à TESTER avant câblage : `kitco.com` RSS, `investing.com/rss/commodities_Industrial_Metals.rss`. Retrait net = objectif minimal atteint.
- **Tests** : références flux→config remplacées (`investing_metals` / nom générique) ; assertions `mining_com not in feeds/polled` ajoutées. Suites ingestion+http_retry+source_monitor **61 verts**. Suite `v3/` complète : **878 passed** (1 échec **pré-existant** `test_audit_veille_liste_conviction_normale_vrai`, date-dépendant samedi, sans lien). `v3/data/` restauré après pytest (pas de pollution des runs réels).

## 2026-06-05 (Session 4) — Corrections audit trio bulletins live (A1/A2 flag-only) + recos Lot 4b/ticket C

**Contexte** : audit trio des bulletins live 04-05/06 (Analyst/News Trader/Spéculateur). Verdict unanime **AJUSTER**. Corrections appliquées = **flag-only, zéro impact conclusion/mesure**. Tout ce qui touchait une DÉCISION (Lot 4b contre-momentum, ticket C calibration) → **reco À VALIDER THOMAS**, pas appliqué (garde-fous fondateur). 870 → 873 → **879 tests** (+6 : 2 micro-bugs run live 18h04, voir bas de section), 0 régression. Doc clé : `v3/audit/reco-corrections-2026-06-05.md`.

### Outil — relancer le backtest quant v2 AVEC FRED (@infrastructure)
- **Nouveau workflow `.github/workflows/backtest-v2.yml`** (job `backtest-v2-fred`, `workflow_dispatch` **MANUEL uniquement**, jamais de cron → ne concurrence pas `cycle-decision`, mode shadow préservé). Expose `FRED_API_KEY` (secret), lance `backtest_quant.py`, publie le log/REPORT en **artifact** (`upload-artifact`). But : clore le verdict sur l'arm d'ablation **`+FRED`** (le run de réf a tourné sans clé → `+FRED` == `price-only`).
- **Stratégie cache** : yfinance étant **bloqué sur les runners CI**, le **cache prix/COT** (`v3/backtest/.cache/*.csv`, 35 fichiers, 3,6 Mo, OHLCV/COT publics, **0 secret**) est **committé** (`git add -f`, dossier gitignored). Le CI lit ce cache (0 appel yfinance) + appelle **FRED réellement** (les `fred__*.csv` sont **volontairement NON committés**) + CFTC Socrata. Step sanity qui abort si cache absent. Fallback documenté : VPS Anya.
- **Garde-fous** : `permissions: contents: read`, **AUCUN commit auto** (l'exécution salit `v3/data/` via import `scripts/` → un commit écraserait les runs réels de `cycle-decision`). Doc « Comment relancer avec FRED » ajoutée à `v3/backtest/REPORT.md`. Tests `test_backtest.py` **21 verts**. **Non déclenché** (Thomas décide du lancement).

### Vrais bugs corrigés (affichage uniquement)
- **A1 — mono-critère rendu VISIBLE** (`◧`) : la détection `mono_critere_dominant` fonctionnait déjà (CAC 7j ET EUR/USD 7j = True au decision-log — l'« incohérence d'affichage » de l'audit n'existait pas), mais le flag était SHADOW decision-log only, jamais affiché. Les 3 experts jugent le mono-critère trop fragile pour rester invisible (EUR/USD 7j = 96% sur 1 critère). Ajouté : drapeau `◧` dans la matrice + section « Cellules à surveiller » + légende. **Conclusion/mesure inchangées.**
- **A2 — champ shadow `quasi_neutre`** au decision-log (`|score| < NEUTRAL_BAND=0.30`) : englobe coin-flip strict ET bande `≈`. Cuivre 7j (-0.22) était raté par `coin_flip` (seuil 0.05) → désormais `quasi_neutre=True`. **Le seuil `coin_flip`/`EPSILON_CARRY` (0.05) N'A PAS bougé** (il est couplé à la contradiction du carry-forward = seuil décisionnel, garde-fou).

### Enquêtes → reportées (pas de bug → reco)
- **B1 CAC « à l'envers »** : signe spread OAT-Bund **vérifié CORRECT** (élargissement → SHORT = risque France baissier, conforme). SHORT = contre-momentum pur (déjà flaggé `⇄`). Faire agir le `⇄` = **Lot 4b → reco À VALIDER THOMAS** (cap contre-momentum), non appliqué.
- **B2 Cuivre SHORT 7j/1m** : mono-critère COT + couverture 48%. Marquage déjà correct (`≈`+`⚠️`+`↯`). Abaisser couverture = **ticket C → reco**.
- **C1 S&P 7j / C2 Argent 1m / C3 échelles saturées** : pertinence par horizon + échelles. Aucun bug technique trouvé (fenêtres/séries correctes, saturation modérée ~1.1-1.3σ non absurde) → **ticket C → recos**, non appliqué.
- **DXY 118.9** (bonus News Trader) : **faux positif d'audit** — `dxy_trend_20j` câblé sur FRED DTWEXBGS (base 2006=100, ~120-130 normal), PAS le DXY classique. z-score = tendance 20j (pas niveau). Donnée + signe **sains** → aucune correction.
- **#8 Or SHORT « à contre-sens »** (backtest 1m 18.2 %) : enquête signe complète (`v3/audit/enquete-or-2026-06-05.md`). SHORT piloté à ~60 % par le critère **TIPS** (taux réels), signe `-1` **macro-canonique vérifié CORRECT** (taux réels hauts → coût d'opportunité or → baissier). **PAS un bug de signe.** Les 7 signes Or sont corrects. Le backtest « sent l'inversion » à tort : (a) il **ne teste pas le TIPS** (run sans `FRED_API_KEY` → poids 0, le 18 % = COT+price-only), (b) il est **news-blind** sur un or **+70 % en 2025 MALGRÉ des TIPS au plus haut** = **rupture de régime** (or-refuge/dédollarisation a découplé la relation or/taux-réels). Inverser le signe = overfit au régime 2025 (l'Or basculerait +12.6/+13.4 LONG). → **RÉGIME/CALIBRATION → reco À VALIDER THOMAS** (ticket C : rééquilibrer poids/pertinence TIPS vs géopol-refuge ; re-run backtest avec FRED). **Aucune correction de code.** Impact décision : NON (Or reste SHORT, `↯` signale déjà le piège).

### 2 micro-bugs du run live 18h04 (audit infra/affichage — zéro impact décision, mode shadow)
- **Bug 1 — nom de fichier du bulletin en UTC au lieu de Paris** (`scoring_analyste.py`). Le run 18h04 Paris produisait `bulletin-2026-06-05-16h.md` (heure UTC) alors que le **titre interne** (« 18h04 (Paris) ») et le **decision-log** (`...-1804.jsonl`) sont en heure Paris → fichier incohérent avec son contenu. **Cause racine** : `out_path` utilisait `now.astimezone(timezone.utc)` au lieu de `now` (Europe/Paris), la même source d'heure que le titre. **Fix** : construire le créneau du nom depuis `now` (Paris) → `bulletin-...-18h.md`. Le `bulletin_id` (stem) est une clé d'identité opaque (prix d'émission, tri, parsing) jamais réinterprétée comme une heure UTC → changement sûr. **Les bulletins déjà produits ne sont PAS renommés** (rétro-compat, historique préservé). +1 test (run 18h04 Paris → `-18h.md` + cohérence titre). Commit `e5f849b`.
- **Bug 2 — `mining_com` 403 revenu malgré l'UA Chrome**. **Diagnostic** : l'UA Chrome ÉTAIT bien propagé sur ce flux (`_fetch_rss` → `http_get_retry(headers=…)`), et `mining.com/feed/` répond **200** depuis cet environnement (les 3 jeux de headers testés passent). Le 403 n'est donc **PAS** « header non propagé » ni un **blocage durable** : c'est un **403 WAF (Cloudflare) intermittent** (challenge transitoire selon l'IP/géo des runners GitHub Actions). Le problème : le 403 était traité comme **non-retriable** → un 403 ponctuel devenait un échec définitif sur le cycle. **Fix mesuré, sans forçage** : (a) en-têtes navigateur enrichis sur les RSS (`config.BROWSER_HEADERS` = UA + `Accept` + `Accept-Language`, certains WAF inspectent `Accept*`) ; (b) nouveau paramètre `retry_status` sur `http_get_retry` + set `RETRY_STATUS_WITH_403` appliqué **au seul flux RSS** → un 403 transitoire est retenté (borné par `max_retries`), pas FRED/GNews/NewsAPI (défaut inchangé, zéro régression). Si le 403 **persiste** après retries → `source_monitor` signale le flux **muet** = dégradation propre déjà en place (zéro acharnement, zéro invention de news). +6 tests (3 http_retry, 2 ingestion RSS, +helpers). Commit séparé.

## 2026-06-03 (Session 3) — Audits trio, refonte page de rendu & comblement des données

**Contexte** : revue fondateur du bulletin frais + audits par le trio + le designer. Beaucoup de polissage, de fiabilisation et de **branchement de données** (le gros levier de qualité). 684 → **859 tests**, 0 régression.

### Bulletin — polissage post-audit trio (affichage/shadow, 0 impact conclusions)
- **Top 3 convictions = actifs distincts** ; **régime news** affiché sans contradiction de signe (`LONG [quant -0.08] 📰`) ; **bande quasi-neutre `≈`** (shadow, |note|<0.30) ; **mono-critère dominant** loggé (shadow). (`f19face`)
- **Fix mesure** : les cellules news (`📰 régime news` + `(brut LONG +X)`) n'étaient PAS mesurées → parsers corrigés. (`e2b3e18`)

### Page de rendu (`build_html`) — audit designer 6.5/10 → ~8.5
- **Favicon** (base64 — les entités HTML ne s'affichaient pas), **dark mode auto**, **onglet « 📊 Historique / Performance »** + persistance `measures-log.jsonl`, tooltips symboles, fusion en 1 table, ⚑ dégonflé. (`120df61`,`6c33b2f`,`9d8726b`,`1ec3158`)
- Bulletin : **décimales 4 sig figs**, section **« Audit de la veille 24h »** (réel %+VRAI/FAUX), **flux muets** reclassés (≠ pannes), ligne **Fraîcheur lisible**, légende d'échelle. (`0eb4bab`,`120df61`,`4f49f14`,`0c307b3`)

### Fiabilité mesure
- **Le système ne tourne plus le week-end** (garde jours-ouvrés cron) ; **échéance 24h sur jour ouvré** (vendredi→lundi) **+ jours fériés** NYSE/Euronext ; **verrou look-ahead C5 armé** (date du tick) ; **filet anti-mesure dégénérée** (prix figé = non-conclusive). (`875722c`,`f629fff`)
- **Dédup news inter-jours** verrouillée (event_id SHA-256 + event_date + Levenshtein 48h, rapidfuzz). (`e64a7b5`)

### Données comblées (gros gain de couverture)
- Récupérés via fix composite/mapping + source VIX unifiée : café météo (p11), VIX régime S&P (p8), HF cacao… (`7bbe128`)
- **Caixin PMI** via extraction news (`f0a9790`) ; **DXY**/**taux 10Y delta 5j**/**spread OAT-Bund** via FRED (`45dd253`) ; **Shiller CAPE** via scraper multpl défensif (`38fdded`) ; **différentiel taux 2Y US-DE** (EUR/USD, **poids 12**) via FRED+ECB Data Portal (`2197e1f`).
- ⚠️ Signe/échelle de ces nouveaux critères = **hypothèses à valider en shadow** (comme le proxy breadth).

## 2026-06-02 (Session 2) — Gate intelligent (anti-biais de survie) + audits reproductibles

**Contexte** : revue des 6 points fondateur + audits par le trio (Analyst/Spéculateur/NewsTrader). La P1 « calibration coverage » (12 actifs muets en INSUFFISANT) est attaquée non par un seuil arbitraire mais par un **gate à priorités**.

### Gate de suffisance — nouvelle logique à priorités (`scoring_analyste.py`)
- **Hystérésis de maintien** (carry-forward, horizon-aware) : `0.25 ≤ cov < 0.40` + dernière direction valide non contredite + non périmée → **⏸ maintenu** au lieu de 🚫 (`COVERAGE_FLOOR=0.25`, `CARRY_MAX_AGE_H={24h:24,7j:48,1m:24}`). Source = decision-log scanné. Smoke réel : **9 cellules récupérées**. (`b868b6d`)
- **Régime news-driven** (cuivre/cacao/café) : couverture quant insuffisante + biais news net (`ratio_news>0.5`) → **📰 direction news** au lieu de 🚫. Helper `compute_news_bias` factorisé. (`2b209d8`)
- Ordre final : quant ≥40% → ⏸ carry → 📰 news → 🚫. Cellules ⏸/📰 portent une vraie direction → **mesurées** (tags `is_carry`/`is_news_regime` pour audit hit-rate futur).

### Bulletins & monitoring
- **3 briefings/jour distincts** `bulletin-{date}-{HH}h.md` (fin du biais de survie : matin/midi/soir s'écrasaient) ; prix d'émission re-clés par créneau ; chacun mesuré. (`7df13ce`)
- **Monitoring sources 3 états** : OK / ⚠️ partiel (R/N) / ❌ — fin des faux ❌ GNews quand 13/14 requêtes passent. (`8b172c2`)
- Note + **confiance%** au lieu de force ●/○, + légende d'échelle. (`040f687`, `0c307b3`)

### Bug & audits
- **🐛 Bug VIX** : `vix_regime` renvoyait +1.0 (plateau 14-25) au lieu du triangle des fiches → faux signal **haussier** systémique sur S&P/Nasdaq/CAC dès que VIX∈[14,25]. Corrigé en triangle (VIX 23.9 : +1.0→-0.36). (`5719cde`)
- **Audit S&P reproductible** (`v3/audit/sp500-explication-reproductible.md`) : la formule `signe×poids×pertinence×norm` reconstitue les scores au centième. Drivers réels = taux réels TIPS + breadth (pas le VIX, absent du run). A corrigé une narration initiale erronée (crédit HY mal signé) ET un angle mort de l'audit lui-même.
- Vérifié : `compute_coverage` pondère déjà par poids (ticket E, rien à faire) ; horodatage = faux problème.
- **684 tests**, 0 régression (8 échecs pré-existants env-only).
- **Différé → C** : calibrer `COVERAGE_MIN` (0.40) sur hit-rate réel — rouvrir ~2026-06-23 quand les tags `is_carry`/`is_news_regime` auront accumulé assez de mesures.

### Polissage post-audit du bulletin (trio → consensus en 3 rounds)
Audit forme+fond du bulletin par le trio : Fond **6/10** (méthode 8, mais données qui la nourrissent 4), Forme **6/10** (transparence forte, mais dense/bruitée). Plan de 6 actions re-priorisé par « impact/effort », exécuté en autopilote :
- **🔴 #1 Bug normalisation** : `normalise()` jetait en silence les critères `composite`/`mapping_non_monotone` (« type inconnu ») → critères à fort poids récupérés : café météo (+11), S&P VIX régime (+8), CAC V2X (+8), Nasdaq VXN (+7), cacao HF (+7). Bug côté consommateur seul (émission déjà correcte). (`7bbe128`)
- **🔴 #2 Incohérence VIX** : `vix_regime` lisait 23.6 (Twelve) vs 14.95 (CBOE) pour le même VIX → unifié sur la source CBOE fraîche (14.95 → +0.975 régime sain). (`7bbe128`)
- **🟡 #6 News** : dédup des news identiques au sein d'un actif (doublon SoftBank CAC) + troncature propre sur frontière de phrase (140→240). (`4e737e0`)
- **🟢 #4/#5 Forme** : bloc **🎯 Top 3 convictions** en tête ; **fusion des 2 tables** de synthèse en une ; **⚑ régime extrême** annoncé 1× au lieu de 12× ; « à surveiller » resserrée (27→6-7 lignes, alertes directionnelles seules). (`1ec3158`)
- **⏸ Différé → #3** : combler les vraies données absentes (Caixin PMI cuivre p.12, diff. taux EUR/USD p.12, etc.) = chantier sources (nouvelles intégrations), non autopilotable.
- **716 tests** verts, 0 régression (8 échecs pré-existants env-only).

## 2026-06-01 (soir) — Observabilité news + optimisation requêtes (10/10)

- **Bilan des news** : bloc dans le bulletin marquant les calls portés par les news qui ont marché/raté (juger le jugement DeepSeek).
- **source_monitor** : santé des flux par cycle (appelé/OK/échec/muet + reçus vs gardés + raison) → `v3/data/source-health.md` + bloc « Santé des sources » dans le briefing + kit d'analyse. Fix 4 flux muets (gnews_cac40 FR, gnews_wheat query, investing_stocks doublon ; mining_com 403 visible).
- **Optimisation requêtes news (audit 3 experts, 3 rounds → 10/10 côté news)** : comble Nasdaq (Nvidia/IA/semi) + VIX (volatilité + causes amont war/escalation), retire DAX, supprime Q3 redondante, dégroupe Or/Argent/Cuivre, sépare Fed/BCE, S&P earnings-driver, enrichit CB-gold/solaire/EUDR/WASDE/café-gel/blé-GASC/CAC-SBF120. 14 requêtes, 22 flux. Plafond news 9,5-10 (reste = pipeline data : CFTC COT, ETF, CBOE, GASC).
- **Kit d'analyse du matin** : `python3 v3/scripts/analyse_complete.py` (matrice, bilan news, mesure, Phase 2 T1/T2, biais, flips, santé sources, backtest).
- **Backtest quant v1** : `v3/backtest/` — moteur historique no-look-ahead ; v1 (price-only, 4 actifs × 24h) = NO-GO (50.8% OOS, partiel). v2 (COT+FRED+horizons) = prochain chantier.

## 2026-06-01 — Fiabilisation run quotidien + plan horizon

**Contexte** : répétition des cycles quotidiens pour débusquer les défauts cachés, audit par les 3 experts, correction en autopilote.

### Correctifs pipeline
- **Routing IA-first réparé** : le parser ignorait les impacts DeepSeek → la synthèse directionnelle (LONG/SHORT par actif) pilote désormais les critères news.
- **Prix d'émission réparés** : la boucle prédiction→mesure (Journaliste) est fermée — conclusions VRAI/FAUX réelles.
- **Indices via ETF Twelve Data** : `^GSPC→SPY`, `^IXIC→QQQ`, `^FCHI→FCHI`, `^VIX→VIXY`, etc. (yfinance bloqué sur les runners GitHub). Débloque CAC/S&P/Nasdaq (0 tie-break).
- **Rate-limiter Twelve** : `_acquire_rate_limit` attend un slot au lieu de rejeter (→ fallback yfinance bloqué) ; `TWELVE_RPM=55` (plan Grow). Cause racine des indices n/a en CI.
- **PROBA_SCALE 10→15** (anti-saturation Brier), propagation `reliability`, garde chevauchement 7j/1m.

### Audits (3 experts : Analyst / News Trader / Spéculateur)
- Audit des runs dans l'ordre d'édition (`v3/audit/chaine-*.md`).
- **Audit de cohérence** (`coherence-3-experts.md`) : 2 faux positifs écartés sur preuve (signe géopol déjà câblé `ia_synthese` ; events 2025 filtrés par cutoff lookback).
- Trio formalisé comme panel d'audit officiel (`v3/audit/README.md`).

### Plan horizon (validé Thomas + 3 experts)
- **Constat** : DeepSeek produit 1 direction/actif **horizon-agnostique** ; sur cellules faibles/longues la news domine voire inverse le quant (Or 24h 43%, VIX 1m 480%).
- **Décision** : PAS de decay global (casserait l'OPEC). Recalibrage `pertinence` (or/petrole/vix) + cap anti-inversion α=0.8 (override si high+confirmed) + `ratio_news`/drapeau 📰.
- **Preuve** : Or 24h +0.17→−1.33 SHORT, VIX 1m +0.25→−0.55 SHORT, Pétrole/S&P inchangés. 360 tests.

### Infra
- `schedule` GitHub diagnostiqué **retardé de 1-3h** (6 runs prouvés les 30-31/05), pas une panne. Redondance cron ×3 (`:12/:27/:42`) + garde-fou anti-doublon. Permissions read/write activées.
- **À faire (Phase 2)** : tracer `event_id`/date + flag nature news (structurel/ponctuel/déjà-price) — cause racine du biais news.
