# Audit de fond du signal (quant + news) : le News Trader, 2026-07-01

> Panel d'audit trio (Analyst / News Trader / Spéculateur). Angle News Trader : la couche news sert-elle la tendance, comme le veut la doctrine (docs/founder-preferences.md), ou la renverse-t-elle ?
> Sources : `v3/data/measures-log.jsonl` (102 mesures, 23/06 au 30/06), `v3/data/decision-log/` (8 runs, 23/06 au 01/07, 315 cellules), `v3/data/source-health.md` et `v3/data/criteres-health.md` (cycle 01/07), `v3/audit/persistance-shadow-mesure.md` (18/06), `v3/audit/rumeur-structurel-shadow.md` (18/06), `CHANGELOG.md`.
> WIN RATE ONLY. Aucun chiffre inventé : chaque nombre est recompté sur fichier.

## NOTE GLOBALE : 6,5 / 10

Le signal global tient l'objectif fondateur sur la fenêtre mesurée : **win rate 43/60 = 72 %** (mesures conclusives VRAI+FAUSSE), au-dessus du seuil de 70 % visé au 08/08. Mais : (1) une poche de défaillance systématique news-driven (Nasdaq 0/6) viole frontalement la doctrine "les news servent la tendance, jamais ne la renversent", (2) 37 % des mesures sont non conclusives, ce qui fragilise la preuve pour le 08/08, (3) sur les 3 cutovers shadow, un seul est réellement tranchable aujourd'hui.

## Q1. Les 3 instruments shadow : assez de données pour trancher ?

Comptages réels sur les 8 decision-logs du 23/06 au 01/07 (315 cellules, 2562 critères loggés).

### (a) Persistance news (persist_shadow_*) : DONNÉES INSUFFISANTES, NO-GO maintenant

- Champs présents et vivants : 309 critères news porteurs de `persist_shadow_alive` / `persist_shadow_age_days` / `persist_shadow_blocks_flip` (33 par run du 23 au 26/06, 48 par run depuis le 29/06).
- `persist_shadow_alive` = True : **309/309**. `persist_shadow_blocks_flip` = True : **0/309**. L'événement discriminant (une news persistée qui bloquerait un flip) ne s'est JAMAIS produit sur la fenêtre.
- Âge max observé : **9,22 jours** (distribution 0 à 9,22 j). Le rapport du 18/06 exigeait des events dépassant 30 j pour comparer persistance et hard-drop 30 j : on en est très loin. Aucun critère n'est mort ni par âge ni par amortissement sur la fenêtre.
- Ce qui EST confirmé : `quant_disconfirms` = True sur **158/309 (51 %)** des critères persistés. Cela recoupe l'alerte du 18/06 (désaccord persistant structurel-long à 71 %, au-dessus des deux seuils 15 % / 30 %) : toute persistance devra être conditionnée au véto quant, jamais age-only.
- Verdict : **NO-GO cutover, données insuffisantes**. Zéro cas où le régime shadow aurait divergé du régime live. Continuer la mesure telle quelle, réévaluer quand au moins un `blocks_flip=True` ou un critère > 30 j apparaît.

### (b) Rumeur vers verbal (nature_shadow_downgrade) : NO-GO en l'état, mesure à compléter

- Déclenchements shadow : **138** sur 2562 critères loggés (5,4 %), en hausse (6 le 23/06, 27 le 01/07). Tous sur nature = structurel, ce qui est cohérent avec la cible (rapport 18/06 : 59,9 % des structurels, 1013/1690, seraient rétrogradés).
- Problème de fond, déjà visible le 18/06 et confirmé : le déclencheur est dégénéré. **993/1013 déclenchements = "reliability seule"** (reliability = reported), 17 reliability+keyword, 3 keyword seul. Ce n'est pas un détecteur de rumeur, c'est un reclassement de quasi TOUTES les news non confirmées. L'activer ferait passer le coef nature de 1,0 à 0,2 (7j) et 0,1 (1m) sur 60 % des structurels : amputation massive de la couche news sans preuve outcome.
- Ce qui manque pour trancher : le lien au win rate. Aucun champ ne persiste le score contrefactuel "si downgrade actif" ; impossible de compter les cellules dont la conclusion aurait changé, ni leur outcome. Indice favorable au downgrade tout de même : les 6 FAUSSE Nasdaq news-driven (voir Q2) auraient toutes vu leur poids news fortement réduit.
- Verdict : **NO-GO cutover en l'état, données insuffisantes sur l'axe qui compte** (outcome). Reco : ajouter au decision-log le score et la conclusion contrefactuels sous downgrade, puis replay sur 23/06 au 01/07 (faisable hors ligne, "mesurer avant d'agir").

### (c) Démenti textuel vs démenti déjà coté : TRANCHABLE, et c'est NO-GO définitif pour le textuel

- Détecteur de démenti textuel (DENIAL_KEYWORDS) : **0 déclenchement sur tout l'historique** (rapport 18/06, 2052 records sur 17 dates ; rien de neuf depuis dans les decision-logs). Données suffisantes pour conclure : le démenti textuel ne capte rien.
- Le canal quantitatif, lui, vit : `quant_disconfirms` = True 158 fois, `already_priced` = True sur **86 critères** (avec `already_priced_age_days` et `already_priced_horizon` persistés). Le vrai démenti est bien le quant qui se retourne, conformément à la doctrine "le quant reste patron".
- Verdict : **TRANCHÉ. NO-GO armement du détecteur textuel** (le garder en shadow coûte zéro, mais ne rien construire dessus). Le mécanisme déjà-coté quantitatif est le bon canal et fonctionne.

## Q2. La couche news aide-t-elle ou nuit-elle au win rate ?

Sur measures-log.jsonl (102 mesures, dont 60 conclusives VRAI/FAUSSE, 38 non-conclusive, 4 suivi-interrompu). N petit : aucun de ces écarts n'est statistiquement significatif, ce sont des tendances.

| Segment | WR conclusif |
|---|---|
| news_driven = True | 20/27 = **74 %** |
| news_driven = False (quant pur) | 23/33 = **70 %** |
| ratio_news = 0 | 16/24 = 67 % |
| ratio_news >= 0,5 | 6/8 = 75 % |
| 24h global | 32/47 = 68 % (news 16/23 = 70 %, quant 16/24 = 67 %) |
| 7j global | 11/13 = 85 % (news 4/4, quant 7/9) |

- En moyenne, la couche news N'EST PAS nuisible : les calls news-driven font légèrement mieux (74 % vs 70 %).
- MAIS la moyenne cache une défaillance concentrée : **Nasdaq 0/6 conclusif, dont 5 FAUSSE news-driven SHORT consécutives (24, 25, 26, 29, 30/06)** avec des ratio_news de 1,58 à **10,36** : la couche news pesait jusqu'à 10 fois le quant et a maintenu un SHORT contre la bande pendant une semaine. C'est exactement le scénario que la doctrine interdit (news qui renverse la tendance). Hors Nasdaq, les news-driven font 20/22 = 91 %.
- Symétriquement, les pires calls quant purs : EUR/USD 0/3 (SHORT scores -13,1 à -16,5, forte conviction, faux 3 jours), blé 1/3, CAC 0/1. Le quant a aussi ses poches (voir Q5).
- Honnêteté sur N : 27 et 33 mesures conclusives par bras, sur 6 jours de bulletins. Un écart 74/70 sur ces N ne prouve rien ; la seule conclusion robuste est la poche Nasdaq (6 échecs consécutifs du même mécanisme, même signe, même cause).

## Q3. Santé du signal quant (cycle du 01/07)

- **Sources news** (source-health.md) : 37 flux configurés, 37 appelés, **37 OK, 0 échec, 0 skip**, 3 muets (eia_press_releases 8/0, fed_monetary 15/0, investing_stocks 10/0, cause dédup+blacklist+filtre, pas une panne). 2058 items reçus, 884 gardés. État sain.
- **Critères** (criteres-health.md) : 42 motifs de skip, 75 occurrences. Les n/a structurels à fort poids potentiel : `put_call_ratio_cboe_5j` et `vix_risk_usdjpy` (CBOE non câblé), `fedwatch_proba`, `breadth_cac_ma50`, `aaii_bull_bear` et 13 z-scores "source non programmatique". Ce sont des trous connus de capteurs, pas des régressions.
- **Les 3 nouveaux actifs (cutover 26/06) sont vivants** : coverage 24h au 01/07 : coton 0,8378, sucre 1,0000, USD/JPY 0,8780 (decision-log 01/07). Flux dédiés actifs : gnews_cotton 100/43 gardés, gnews_sugar 100/47, gnews_usdjpy 100/92. Trous résiduels ciblés : `nass_crop_progress_cotton` (non programmatique), `meteo_inde_gujarat_coton` (reportée 1 j), `vix_risk_usdjpy` (CBOE). Aucun des trois n'a encore de mesure conclusive (coton 0 conclusif sur 2, sucre 2 non encore échues, usdjpy 2 en cours) : leur win rate est encore invérifiable.
- **Clé Twelve** : pas de fallback anormal. 29 symboles servis en twelve_native (dont CANE, COTN, USD/JPY). Traces résiduelles : 4 séries vides (USDGHS=X, USDXOF=X, ^STOXX50EVOL, ^VXN, symboles exotiques) et 3 valeurs reportées d'1 à 2 jours (caixin_pmi_manuf, 2 météo). Le point ouvert "clé Twelve à régénérer" (CHANGELOG, point (c) session du ~17/06) ne laisse pas de trace visible ce cycle ; le blocker est administratif, pas encore un trou de données.

## Q4. Cohérence par horizon : le 7j/1m recopie-t-il le 24h ?

Sur le decision-log du 01/07 (15 actifs, conclusion pondérée) :

- Divergence de DIRECTION vs 24h : **7j = 2/15** (cuivre 24h LONG vs 7j SHORT ; pétrole 24h LONG vs 7j SHORT), **1m = 4/15** (cuivre, Nasdaq, pétrole, S&P 500 s'inversent en 1m).
- Divergence de SCORE : **0 score strictement identique** entre horizons (15/15 actifs ont des scores 24h, 7j, 1m tous différents, souvent de plusieurs points, ex. cacao +1,87 / +7,63 / +18,87).
- Lecture : ce n'est PAS une recopie mécanique (les pondérations par horizon travaillent réellement), mais la direction 7j confirme le 24h dans 87 % des cas. C'est attendu quand la tendance domine ; le vrai test est le win rate 7j mesuré séparément (85 % sur 13 mesures, encourageant) et le 1m, qui n'a AUCUNE mesure conclusive à ce jour (0 ligne 1m dans measures-log). L'objectif fondateur porte sur 24h/7j/1m : le tiers 1m de l'objectif est aujourd'hui non mesuré.

## Q5. Les chantiers différés (ticket C, ~ session 4) pèsent-ils déjà sur les outcomes ?

Référence : CHANGELOG 2026-06-05 (Lot 4b contre-momentum et ticket C calibration, recos "À VALIDER THOMAS", non appliquées).

- **Frein contre-momentum CAC : OUI, ça pèse.** CAC 40 : 0/1 conclusif, 7/8 non-conclusive ; l'unique mesure conclusive est la FAUSSE du 24/06 (SHORT -1,38, quant pur), le cas exact flaggé B1 le 05/06. Le drapeau existe, le frein non.
- **Pertinence S&P 7j : un cas.** S&P 500 7j SHORT -10,91 FAUSSE le 24/06 (news_driven False). Une occurrence, non conclusif statistiquement, mais c'est le point C1 resté ouvert.
- **Quasi-neutres |score| < 0,30 : ne pèse pas encore.** 4 cellules mesurées seulement (3 VIX VRAI, 1 Nasdaq non-conclusive), 3/3 conclusives VRAI. Rien à corriger en urgence sur pièces.
- **Échelles : OUI, et c'est le point le plus grave.** Le ratio_news non borné (observé jusqu'à 10,36 sur Nasdaq) laisse la couche news écraser le quant, cause directe des 5 FAUSSE Nasdaq. `NEWS_DOMINANT_RATIO = 0,5` (scoring_analyste.py, ligne 169) est un seuil d'ÉTIQUETAGE (flag news_driven), pas un plafond de contribution : rien ne cape le poids news dans le score. Le chantier "échelles" différé a donc déjà un coût mesuré.

## Verdicts cutovers (synthèse)

| Cutover | Verdict | Chiffre clé |
|---|---|---|
| (a) Persistance news quant-vetoed | NO-GO, données insuffisantes | 0/309 blocks_flip, âge max 9,2 j < 30 j |
| (b) Rumeur vers verbal | NO-GO en l'état, mesure outcome manquante | 138 déclenchements mais 98 % = reliability:reported, 0 contrefactuel loggé |
| (c) Démenti textuel | TRANCHÉ : NO-GO définitif (le quant est le démenti) | 0 déclenchement textuel historique vs 158 quant_disconfirms |

## Top findings

### P0 : la couche news renverse la tendance sur Nasdaq et perd 6/6
Nasdaq 0/6 conclusif, 5 FAUSSE news-driven SHORT consécutives (24 au 30/06), ratio_news 1,58 à 10,36 : violation mesurée de la doctrine "les news servent la tendance, jamais ne la renversent". `NEWS_DOMINANT_RATIO` n'est qu'un flag, aucune borne de contribution n'existe.
**Reco (une seule)** : sans toucher au ratio tranché le 20/06, produire pour Thomas le replay contrefactuel Nasdaq 23/06 au 01/07 avec contribution news plafonnée à 1x le quant (et variante coef verbal), win rate avant/après, pour décision fondateur sur preuve.

### P1 : 37 % de mesures non conclusives, et le 1m n'est pas mesuré du tout
38/102 non-conclusive + 4 suivi-interrompu : à ce rythme, la preuve du 08/08 (WR >= 70 %) reposera sur un N conclusif trop faible, et l'horizon 1m (un tiers de l'objectif) a 0 mesure.
**Reco** : instrumenter la cause de chaque non-conclusive dans measures-log (seuil trop strict, donnée absente, week-end) et ouvrir la mesure 1m maintenant (les émissions du 23/06 échoient au 23/07 : c'est mécaniquement possible avant le 08/08).

### P2 : poches quant faibles connues et non freinées (EUR/USD, CAC, blé)
EUR/USD 0/3 avec convictions fortes (-13 à -16,5), CAC 0/1 sur le contre-momentum flaggé depuis le 05/06, blé 1/3 sur scores quasi neutres (-1,04 / -1,09). Le quant a ses propres angles morts, tous déjà identifiés dans le ticket C et Lot 4b différés.
**Reco** : présenter à Thomas le chiffrage ci-dessus pour arbitrer le Lot 4b (frein contre-momentum) en priorité, les deux autres restant en observation.

## Handoff

- Livrable : `v3/audit/audit-fond-newstrader-2026-07-01.md` (ce fichier). Aucun autre fichier modifié.
- Pour l'Analyst : la question des échelles (P0) est quant-compatible, le plafond proposé préserve le quant patron.
- Pour le Spéculateur : les 3 nouveaux actifs sont vivants côté critères mais sans aucun outcome conclusif ; ne pas les compter dans la preuve du 08/08 avant mi-juillet.
- Prochaine échéance de mesure : premier critère news franchissant 30 j attendu au plus tôt vers le 21/07 (âge max 9,2 j au 01/07) ; le cutover (a) ne pourra pas être retranché avant.
