# Audit chaîne de production — TradingApp v3 (cycle 31/05/2026)
Angle : news-trader senior. Enjeu = justesse directionnelle de tendance. On suit la propagation d'un signal de bout en bout.

## 1_events-log.md — INGEST
Qualité : **bonne**, c'est le maillon le plus riche. Les batches récents (≥30/05, schéma 12 champs) portent des triplets directionnels exploitables : `BRENT:SHORT:high`, `GOLD:LONG:high`, + materiality + reliability (confirmed/reported/rumor). DeepSeek lit correctement la nuance : ligne 312 « Trump réunion décision finale, Brent chute » → `BRENT:SHORT:high` ; ligne 223 « Blocus Ormuz » → `BRENT:LONG:high`. Le desk verrait juste.
Défauts : (a) deux schémas cohabitent — les vieux batches (l.9-140) n'ont NI triplet NI materiality/reliability, signal perdu d'office ; (b) des archives Hormuz fév-avr (l.111,326,336,341,343) restent `BRENT:LONG:high` et polluent le comptage : 62 BRENT:LONG vs 42 BRENT:SHORT alors que le **flux frais 29-31/05 est massivement de-escalation/SHORT**. Aucune pondération par récence.
Ce qui se perd ensuite : les triplets, la materiality et la reliability — la vraie valeur ajoutée — ne survivent pas à l'étape 2.

## 2_criteres-courants.md — CRITÈRES
Qualité : **correcte sur le quanti, cassée sur le news**. Les critères marché (CFTC, flux ETF, TIPS, ratios) sont normalisés proprement. Mais tout le signal news est écrasé en un flag binaire.
Fuite majeure : `petrole.tension_geopol_moyen_orient = {valeur:1, source_track:keyword, materiality:'', reliability:''}` (l.294-301). Le triplet `BRENT:SHORT:high` dominant devient un **+1 LONG** par simple présence de mots-clés « Iran/Ormuz ». Idem `or.tension_geopolitique=1` (l.263), `vix.tension_geopolitique_active=1` (l.367), `ble.geopolitique_mer_noire=1` (l.58). Tous LONG, tous `valeur_ponderee:0.42` en dur. Materiality/reliability arrivent **vides** : la distinction confirmed vs rumor de l'étape 1 est jetée.
Conséquence desk : un marché qui price une détente (Brent -20% sur le mois, cf. l.39/193) est lu « tension = haussier pétrole ». Contresens directionnel.

## 3_bulletin.md — BULLETIN
Qualité : **matrice lisible mais Briefing/score désaccordés**. La matrice 12×3 est défendable là où le quanti domine (Cuivre SHORT via COT à +1σ ; S&P LONG via spreads HY serrés). Le Briefing affiche pourtant des news contradictoires non arbitrées : Pétrole (l.27-30) juxtapose « blocus Ormuz ↑ » et « Arabie baisse les prix ↓ » sans trancher, puis le score sort **LONG +7.28 24h** porté à 86 % par le seul triplet geopol (+6.3). Le desk, lui, est short Brent ce jour-là.
Incohérences : (a) le Briefing cite des titres (« Israel seizes castle », « Chicago PMI ») quasi absents du log audité — désynchro source/affichage ; (b) en-tête « 598 events / 142 impact » alors que le fichier log en contient ~410 : le bulletin tape dans un corpus plus large que celui fourni. Or 24h SHORT mais triplet tension `+4.0` LONG : le quanti sauve la conclusion, pas le news.

## 4_decision-log.jsonl — TRAÇABILITÉ
Qualité : **excellente mécaniquement, vide sémantiquement côté news**. 36 cellules, chaque contrib chiffrée et rejouable (Argent 24h : TIPS -1.99, ratio G/S +2.10 → +0.096 LONG). On peut auditer le calcul.
Mais sur CHAQUE critère triplet : `materiality:"", reliability:"", facteur:0.42` figé. Pétrole 24h : `tension_geopol_moyen_orient valeur:1 → contrib_pm1:6.3` (50 % du score). Le log trace QUE le keyword a matché, pas QUELLE news ni QUEL sens — impossible de remonter au `BRENT:SHORT:high` d'origine. Le `facteur 0.42` est constant partout (Blé, Café, Or, Pétrole), preuve qu'aucune materiality réelle ne le module. La traçabilité s'arrête au flag, le fil vers l'event source est coupé.

## 5_performance / ab / calibration — MESURE
1er cycle, attendu quasi vide. Toutes cellules `shadow`, N=0. **À signaler quand même** : les mesures 30→31/05 sont toutes `suivi-interrompu / prix d'émission indisponible` (perf l.41-61). Les prix d'émission ne sont jamais capturés → même avec du volume, l'outcome restera non mesurable. La boucle d'apprentissage est cassée en amont, pas juste en warm-up. Calibration : mapping score→proba déterministe non calibré empiriquement (calib l.5) — proba affichée non garantie.

## Propagation d'un signal de bout en bout — l'Iran/Ormuz
Étape 1 (solide) : 29-31/05 le log capte la détente — l.193 `BRENT:SHORT:high`, l.312 `BRENT:SHORT:high`, l.307 `BRENT:SHORT:medium`. Direction baissière, reliability tracée.
Étape 2 (FUITE) : tout cela se condense en `petrole.tension_geopol_moyen_orient = 1` = LONG, keyword, materiality vide. Le sens s'inverse, la reliability disparaît.
Étape 3 : le bulletin sort Pétrole **LONG +7.28** dont +6.3 vient du flag inversé. Le Briefing montre les news contradictoires mais ne les arbitre pas.
Étape 4 : le decision-log grave `contrib 6.3` sans pointer l'event, fil source rompu.
Étape 5 : aucune mesure ne pourra dire que c'était faux (prix manquants).
Le signal entre juste et ressort à l'envers, amplifié, non mesurable.

## VERDICT
**La chaîne fuit à la jointure 1→2.** L'ingest (DeepSeek) est de qualité desk ; tout le reste hérite d'un signal news mutilé. Le quanti (COT, flux, taux) traverse intact et sauve souvent la conclusion ; le news est systématiquement transformé en biais LONG géopolitique, à contre-tendance les jours de détente. Mesure inopérante (prix non captés).

**Note chaîne : 4/10** (ingest 8, propagation news 2, quanti 7, mesure 1).

- Brancher les triplets directionnels (BRENT:SHORT:high) sur le critère au lieu d'un flag présence/absence keyword → corrige l'inversion de sens.
- Propager materiality + reliability jusqu'au decision-log et moduler `facteur` (aujourd'hui 0.42 figé) ; pondérer par récence pour ne pas laisser les archives Hormuz fév-avr dominer.
- Tracer l'event-id source dans chaque contrib triplet du decision-log (fil rompu actuellement).
- Réparer la capture du prix d'émission AVANT d'attendre le warm-up : sans elle l'étape 5 ne mesurera jamais rien.
