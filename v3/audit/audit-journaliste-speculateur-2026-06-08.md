# Audit du JOURNALISTE — angle Spéculateur trend-follower

> « Est-ce que ce score me convaincrait de mettre du cash en réel ? »
> Auditeur : Spéculateur (trio officiel). Date : 2026-06-08. Branche : `claude/elegant-ramanujan-OIKms`.
> Sources auditées : `v3/scripts/journaliste.py`, `run_journaliste.py`, `v3/data/performance.md`, `performance-ab.md`, `measures-log.jsonl` (324 records).

## VERDICT : LÉGER (mesure honnête sur la méthode, creuse sur la preuve)

La mesure est **techniquement propre** (zéro look-ahead, entry-lock, échéances figées, non-chevauchant, Wilson) mais elle ne **prouve rien d'exploitable** aujourd'hui : aucune cellule éligible, échantillon minuscule, et surtout elle ne dit **jamais si je gagne de l'argent**.

---

## Ce que je vois quand je regarde le score (chiffres réels du run 2026-06-08)

### 1. Le « 100 % » n'est pas un score de confiance, c'est un mirage de petit N
Plusieurs cellules affichent fièrement **100 %** (Or 24h, EUR/USD 24h, Pétrole 7j…). Mais derrière :
- **Or 7j = 100 %** repose sur **1 seule** observation effective (N_eff=1). Pile ou face gagné une fois.
- **EUR/USD 24h = 100 %** sur N_eff=5, Wilson_low **0.566**. C'est la SEULE cellule où la borne basse dépasse 50 %. Toutes les autres « 100 % » ont une borne basse ≤ 0.61 et restent **shadow**.
- Le rapport est honnête sur ce point (il colle « warm-up », « N_eff déflaté », Wilson partout) — mais quelqu'un qui lit juste la colonne `Taux_brut` voit « 95 %, 100 %, 92 % » et croit que ça marche. **Le chiffre vendeur (taux_brut) est en colonne 4 ; le chiffre honnête (Wilson_low sur N_eff) est en colonne 7.** Hiérarchie visuelle à l'envers pour un décideur pressé.

### 2. Verdict officiel du système lui-même : 0 sur 24
- **Cellules éligibles (Wilson low > 50 % ET taux_eff ≥ 70 %) : 0 / 24.** Critère global : « warm-up, aucune cellule avec N_eff ≥ 15 ». **Le système dit lui-même qu'il ne sait encore rien prouver.** Bon réflexe — mais ça veut dire que TOUT le reste est décoratif tant qu'on n'a pas accumulé.

### 3. La moitié des décisions ne sont jamais jugées
Sur les 324 records du `measures-log.jsonl` :
- VRAI 124 · FAUSSE 90 · **non-conclusive 54** · **suivi-interrompu 48** · non-notee 8.
- Le dénominateur du taux = VRAI+FAUSSE = **214**. Donc **110 décisions sur 324 (34 %) ne produisent AUCUNE leçon** (mouvement trop petit, ou prix manquant). Sur certaines cellules c'est pire : tous les runs récents portent « 2 suivi(s) interrompu(s) sur la fenêtre ». Une mesure qui s'évapore un tiers du temps me convainc à 66 %, pas à 100 %.

### 4. Le 7j est embryonnaire, le 1m n'existe pas
- Horizons mesurés : **24h = 276 records, 7j = 48, 1m = 0**. Le `measures-log` ne contient **aucune** mesure 1m.
- Toutes les cellules 7j sont à N_eff = 0 ou 1 (« 2/30 mesures terminées »). **On ne mesure réellement QUE le 24h.** Or le produit vend 3 horizons (24h/7j/1m) et moi, trend-follower, je joue surtout 7j/1m. **Les deux horizons qui m'intéressent ne sont pas mesurés.**

### 5. « VRAI » ≠ « j'aurais gagné de l'argent »
C'est le cœur du problème. `measure_cell` fait : `delta_pct = (courant - emission)/emission`, puis VRAI si `|delta| > seuil` dans le bon sens. Donc :
- **VRAI = le prix a bougé d'un cheveu au-dessus du seuil dans le bon sens.** Seuil EUR/USD 24h = **0.25 %**. Un VRAI peut valoir +0.26 %.
- **Aucune notion d'amplitude du gain.** Un VRAI à +0.3 % et un VRAI à +8 % comptent **pareil** (1 point). Un FAUSSE à -0.3 % et un FAUSSE à -9 % comptent pareil (0 point).
- **Exemple réel dans le log** : Argent 7j LONG, delta **-8.95 %** → 1 seule FAUSSE. Une perte massive pèse autant qu'un petit raté. En turbo (effet de levier), -8.95 % avec levier = compte liquidé — la mesure ne le voit pas.
- **`grep` exhaustif confirme : ZÉRO trace de `pnl`, `rendement`, `cumul`, `equity`, `payoff`, `mise` dans tout `journaliste.py`.** Le système ne mesure **jamais** d'argent.

### 6. On ne mesure JAMAIS le cumul / la performance d'un portefeuille
Il n'existe **aucun** « si tu avais suivi tous les calls, tu serais à +X % / -Y % ». La mesure est une **collection de % de bonnes directions hors-sol, cellule par cellule**, jamais agrégée en courbe d'equity. Donc impossible de répondre à MA question de base : **« est-ce que ce système, joué en vrai, gagne de l'argent ? »** Le « taux global flips 46.4 % / continuations 59.7 % » est intéressant méthodo mais ne se convertit en aucun €.

## Les 3 manques les plus graves

1. **AUCUNE mesure d'argent / de P&L cumulé.** « VRAI » = direction juste d'un cheveu, pas « j'ai gagné ». Un VRAI à +0.3 % et un FAUSSE à -9 % se neutralisent dans le taux alors qu'en turbo l'un fait peanuts et l'autre liquide le compte. **Sans P&L pondéré par l'amplitude (et une courbe d'equity « si je suivais tous les calls »), ce score ne me dit pas si je gagne de l'argent.** C'est rédhibitoire pour passer en réel.

2. **Le 7j est embryonnaire (N_eff 0-1) et le 1m n'est PAS mesuré du tout (0 record).** On valide statistiquement un seul horizon (24h) alors que le trend-following se joue sur 7j/1m. **On émettrait en réel sur des horizons jamais mesurés.**

3. **34 % des décisions ne sont jamais jugées (110/324 non-conclusives + interrompues) et 0/24 cellules sont éligibles.** Le seuil de non-conclusive avale beaucoup de cas, les `suivi-interrompu` reviennent à chaque run (data manquante), et au final le système avoue lui-même « warm-up partout ». **Tant que ça, la mesure est creuse — pas fausse, mais vide de preuve.**

## Ce qui manque pour que je passe en réel — checklist

- [ ] **P&L réaliste** : mesurer le rendement signé réel par call (delta % effectif, pas binaire), pondéré par l'amplitude. Un gros raté doit peser plus qu'un petit.
- [ ] **Courbe d'equity cumulée** : « si tu avais joué tous les calls (ou les calls à conviction X), tu serais à +/- Y % » — avec et sans coûts (spread turbo, frais Bourse Direct). C'est LE chiffre qui me convainc.
- [ ] **Sharpe / hit-ratio pondéré gain-moyen vs perte-moyenne** (payoff ratio) : 60 % de bonnes directions avec gains < pertes = je perds quand même.
- [ ] **Mesure réelle du 7j et du 1m** (le 1m est à zéro) avant toute émission sur ces horizons.
- [ ] **N_eff ≥ 15 par cellule** (le système l'exige déjà — il faut juste accumuler ; ~plusieurs semaines).
- [ ] **Réduire le taux de non-conclusive/interrompu** ou au moins le **publier en tête** (combien de calls « comptés pour du beurre » ce mois-ci ?), sinon le taux affiché survend.
- [ ] **Hiérarchie d'affichage honnête** : mettre Wilson_low / taux_eff (sur N_eff) AVANT le taux_brut, pour qu'un « 100 % (N=1) » ne saute pas aux yeux comme une réussite.
- [ ] **Drawdown max** sur la période simulée (un trend-follower vit ou meurt sur le drawdown).

## Ce qui est déjà solide (à ne pas casser)

- **Intégrité anti-triche** : entry-lock du prix d'émission (immuable), échéance figée déterministe, refus look-ahead, refus mesure prématurée, jamais d'invention de prix (suivi-interrompu + retry). Du sérieux.
- **Rigueur stat de la borne** : non-chevauchant (`select_non_overlapping`), Wilson_low comme critère d'éligibilité, N_eff_min=15, multiple-testing. La méthode est saine.
- **Honnêteté du warm-up** : le système refuse de se déclarer éligible (0/24) et colle les alertes partout. Il ne ment pas — il est juste encore vide.
- **A/B ±1 vs pondéré** mesuré en parallèle (delta -0.71 pt : le pondéré n'apporte rien pour l'instant, donc rester sur ±1 — bonne discipline « activer sur preuve »).

## Conclusion Spéculateur
La plomberie de mesure est propre et honnête, mais elle répond à « la direction était-elle juste ? » et **jamais à « est-ce que j'aurais gagné de l'argent ? »**. Pour un trend-follower qui met du cash, c'est la mauvaise question. **LÉGER** : il manque le P&L cumulé pondéré par l'amplitude, le drawdown, et la mesure réelle du 7j/1m. Avec ça (et N_eff qui monte), le score deviendrait crédible. En l'état : **je ne mets pas un euro en réel sur ce score.**
