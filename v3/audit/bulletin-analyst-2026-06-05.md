# Audit Analyst — Bulletins live 2026-06-05

> Auditeur : @data-analyst (rigueur statistique / validité de la mesure)
> Bulletins couverts : bulletin-2026-06-04-18h (run 20h32) · bulletin-2026-06-05-05h (run 07h03) · bulletin-2026-06-05-08h (run 10h56)
> Ordre d'audit : chronologique (du plus ancien au plus récent)
> Mode shadow — N_eff insuffisant pour juger la performance. Cet audit juge la MÉTHODE et la fiabilité des chiffres.

---

## 1. Taille d'échantillon et warm-up

**N_eff global : ~0 cellule mesurable** pour les horizons 7j et 1m (pas encore de mesures conclues).
Pour le 24h, l'audit de la veille visible dans les bulletins donne un aperçu partiel :
- Argent 24h : 11 VRAI sur 11–13 prédictions → sur-représenté (Argent domine le décompte des mesures)
- CAC 40 24h : 0 VRAI sur 7 prédictions (FAUX en série — voir §5)
- Blé 24h : mix incohérent VRAI/FAUX avec flip de direction entre runs (voir §5)
- EUR/USD 24h : 3 FAUX consécutifs confirmés dans le bulletin 08h

**Conclusion warm-up** : on est en phase pré-statistique. Aucune affirmation de performance possible. Le billet de mesure le confirme implicitement (pas de Wilson/Brier disponibles dans les bulletins audités). Toute note de confiance affichée est une confiance de couverture des données, pas une confiance statistique.

---

## 2. Couverture pondérée par cellule

Synthèse des taux de couverture lus dans le decision-log (run 10h56) et les bulletins :

| Actif | Couverture | Statut |
|---|---|---|
| Argent | 75% | normale |
| Blé | 73.7% | normale |
| CAC 40 | 65% | normale (limite basse) |
| Cacao | ~50% | ⚠️ conf. faible — 2 critères forts manquants (météo p11, arrivées p9) |
| Café | ~60% | ⚠️ conf. faible — critères stocks ICE (p9), USD/BRL (p6), spread (p4) absents |
| Cuivre | ~48% | ⚠️ conf. faible — Caixin (p12) + inventaires LME/SHFE (p8) absents |
| EUR/USD | ~72% | normale — mais FedWatch (p6) et spread OAT-Bund EUR (p4) absents |
| Nasdaq | ~78% | normale — VXN régime (p7) et concentration top7 (p5) absents |
| Or | ~68% | normale — PBoC/CB (p9) absent |
| Pétrole | ~73% | normale — term structure (p5), Caixin (p4) absents |
| S&P 500 | ~82% | normale — AAII (p4) absent |
| VIX | ~72% | normale — put/call (p6) et gap RV-IV (p5) absents |

**Points critiques :**
- Cacao, Café, Cuivre sont en ⚠️ conf. faible sur les 3 runs → situation structurelle, pas un incident ponctuel
- Cuivre à 48% : la direction repose sur 3 critères seulement (mining strikes triplet p5 + DXY + ratio Cu/Or), dont 2 sont des proxies indirects. Le gate "conf. faible" est ACTIF et justifié.
- CAC 40 à 65% : V2X (p8) et Breadth CAC (p6) absents — 14 points de poids manquants sur ~40. La conclusion SHORT tient sur le spread OAT-Bund seul en 7j (mono-critère dominant confirmé dans le decision-log ligne 8).

---

## 3. Intégrité des normalisations [-1,1]

Valeurs saturées détectées (|norm| = 1.0) :

| Critère | Actif | Norm. | Observation |
|---|---|---|---|
| Ratio Gold/Silver | Argent | -1.000 | Gold/Silver = 61.5 avec centre=75, échelle=12 → (61.5-75)/12 = -1.125, plafonné à -1.0. Saturation attendue : le ratio est en dehors de la plage normale. Sain si la plage reflète l'historique réel — à vérifier lors de la calibration K. |
| Term structure VIX/VIX3M | VIX | -1.000 | VIX3M/VIX = 0.8223, centre=0.95, échelle=0.1 → (0.8223-0.95)/0.1 = -1.277, plafonné à -1.0. Saturation forte : le ratio est à 1.27 écarts-type en dehors de la plage. Indique un backwardation VIX inhabituel — plausible en régime de faible vol, mais l'échelle de 0.1 est très serrée. |
| CFTC COT Copper nets | Cuivre | +1.000 | 73313 nets → plafonné à +1.0. Indique que les positions commerciales Cu sont à un extrême historique. C'est une information réelle mais la saturation à +1.0 écrase la nuance. |
| Shiller CAPE | S&P 500 | +1.000 | CAPE = 42.7 → plafonné à +1.0. CAPE à 42.7 est effectivement dans le décile supérieur historique — saturation défendable. |
| RSI Nasdaq | Nasdaq | +0.948 (run 04/06) → +0.948 (stable) | Non saturé mais proche du plafond. |

**Conclusion normalisation** : 4 saturations détectées. Celles de Ratio Gold/Silver et Term structure VIX/VIX3M méritent une révision d'échelle (plage trop étroite → saturation fréquente → perte d'information). CAPE et COT Copper sont défendables. **Aucune anomalie bloquante mais calibration K recommandée** (déjà planifiée ~23/06).

---

## 4. Cohérence notes signées vs critères actifs (mono-critère)

Cellules à risque mono-critère identifiées dans le decision-log :

| Cellule | Critère dominant | Part du score |
|---|---|---|
| CAC 40 7j | Spread OAT-Bund (p10) | ~4x contrib des autres critères actifs — `mono_critere_dominant: true` confirmé decision-log |
| EUR/USD 7j | Différentiel taux 2Y US-DE (p12) | contrib -10.941 sur score total -11.35 → **96% du score sur 1 critère** |
| Or 7j | TIPS 10Y réels (p12) | contrib -8.61 sur score -3.83 (run 04/06) à -5.83 (run 05h) — dominant mais pas seul |
| Nasdaq 7j | TIPS 10Y réels (p11) | contrib -7.89 sur -8.94 → ~88% du score |

**Cas le plus critique : EUR/USD.** Le score 7j (-11.35) est porté à 96% par un seul critère (différentiel 2Y US-DE normalisé à +0.912). Le signal est fort et structurel — la direction SHORT est plausible — mais la robustesse est quasi-nulle : si le critère 2Y est mal normalisé ou sa z-score mal calculée, toute la cellule bascule. Le flag mono-critère n'est pas affiché dans le bulletin pour EUR/USD (alors qu'il l'est pour CAC 40 7j). **Incohérence à corriger** : si `mono_critere_dominant` n'est pas déclenché pour EUR/USD, le seuil de détection est insuffisant.

---

## 5. Biais directionnel sur les 3 runs

| Run | LONG | SHORT | Ratio SHORT |
|---|---|---|---|
| 04/06 18h (20h32) | 14 | 22 | 61% |
| 05/06 05h (07h03) | 11 | 25 | 69% |
| 05/06 08h (10h56) | 11 | 25 | 69% |

**Biais SHORT structurel confirmé** (69% des 36 cellules sur les 2 derniers runs). Les drivers identifiables :
- TIPS 10Y réels à 2.11 (norm +0.718) → SHORT sur Or, Argent, S&P, Nasdaq, simultanément
- DXY fort (118.9, norm -0.229) → SHORT sur Blé, Cuivre, EUR/USD, Or, Pétrole, S&P
- Différentiel 2Y US-DE élevé → SHORT EUR/USD dominant
- Term structure VIX saturée (-1.0) → SHORT VIX

**Symptôme structurel ou régime ?** Le biais SHORT est cohérent avec le régime macro actuel (taux réels élevés, dollar fort). Il n'est pas un artefact de codage. Cependant, 3 critères (TIPS, DXY, diff 2Y) apparaissent dans 7–8 actifs différents → **corrélation structurelle non décorrelée**. Les cellules ne sont pas indépendantes. L'hypothèse d'indépendance implicite dans le comptage LONG/SHORT est fausse.

---

## 6. Stabilité run-à-run (flips suspects)

Flips déclarés dans les bulletins :

| Cellule | Run 04/06 20h32 | Run 05/06 07h03 | Run 05/06 10h56 |
|---|---|---|---|
| Argent 1m | LONG (+1.86) | SHORT (-0.97) | SHORT (-0.70) |
| Blé 1m | SHORT (-0.09) ≈ | LONG (+0.39) | LONG (+0.39) |
| S&P 500 7j | LONG (+1.88) | SHORT (-2.41) | SHORT (-2.41) |
| VIX 24h | LONG (+2.35) | SHORT (-0.11) ≈ | SHORT (-0.11) ≈ |
| VIX 7j | LONG (+1.77) | SHORT (-0.13) ≈ | SHORT (-0.13) ≈ |
| Pétrole 7j | +3.05 LONG | +3.68 LONG | +12.85 LONG ← saut |

**Analyse des flips :**

1. **Argent 1m** : flip LONG → SHORT entre 20h32 et 07h03. Driver : TIPS 2.07 → 2.11 (+0.04%) et Mouvement or 5j varie (-0.01446 → -0.02169). Score passe de +1.86 à -0.97 : un écart de 2.83 pour 0.2 pts de TIPS → la cellule 1m est très sensible aux variations marginales. Le signe du Ratio Gold/Silver contribue +7.0 en 1m mais n'a pas changé (la direction du score flip est pilotée par la variation de la pertinence 1m, pas par un changement de données). Suspect : flip sur données quasi-stables.

2. **S&P 500 7j** : flip +1.88 → -2.41 entre les deux runs du 05/06. Le driver est la variation du taux 10Y delta 5j : -0.04 (run 20h32) → +0.01 (run 07h03). Une variation de +0.05% sur le taux 5j change le score de +1.403 à +0.366 sur ce critère (poids 9). Le reste du score ne change pas. Le flip est causé par **un seul critère très réactif à court terme** (taux 10Y delta intraday). La direction 7j flip sur une variation de 5bp. Instabilité notable.

3. **VIX 24h et 7j** : flip LONG (+2.35 et +1.77) → SHORT (-0.11) quasi-neutre. Le term structure VIX reste constant (0.8223, norm -1.000, saturé). La différence majeure est la **Tension géopolitique** (triplet) : elle était à +1 le 04/06 (contrib +2.88 et +2.40) et est à 0 le 05/06 (contrib 0). Ce flip de triplet est vraisemblablement causé par la fenêtre 48h qui a expiré ou par un changement de scoring DeepSeek entre les deux runs. VIX atterrit à ≈ (quasi-neutre, |score|<0.30) avec flag ≈ — le bulletin le signale correctement. Flip justifié mais frêle.

4. **Pétrole 7j** : saut +3.68 → +12.85 entre le run 07h03 et le run 10h56. Driver : triplet "OPEC+ politique production" passe de 0 (valeur absente/neutre) à +1 entre les deux runs. Ce seul critère (poids 6, pertinence 1.0 en 7j) génère +5.4 de contribution. C'est un saut de données réel dans la fenêtre 3h, non un bug — mais il illustre **la sensibilité extrême au triplet OPEC+ quand il bascule**. La note 7j passe de modérée (+3.68) à conviction forte (+12.85). Le Top 3 du bulletin du matin affichait EUR/USD, Nasdaq, S&P ; le bulletin 10h56 affiche Pétrole 7j en #1. Saut visible, cohérent avec les données, mais spectaculaire.

---

## 7. Verdict par axe

| Axe | Verdict |
|---|---|
| Taille d'échantillon / N_eff | À SURVEILLER — warm-up, 0 cellule mesurable en 7j/1m, Argent sur-représente les mesures 24h |
| Couverture pondérée | À SURVEILLER — 3 actifs structurellement en ⚠️ conf. faible (Cacao/Café/Cuivre), CAC à 65% mono-critère |
| Intégrité normalisations | À SURVEILLER — 4 saturations dont Ratio G/S et VIX term structure (échelles trop serrées) |
| Cohérence mono-critère | DÉFAUT — EUR/USD 96% sur 1 critère, flag mono_critere_dominant absent dans le bulletin |
| Biais directionnel | À SURVEILLER — SHORT 69% structurel (macro-cohérent) mais corrélation non décorrélée des critères macro |
| Stabilité run-à-run | À SURVEILLER — 2 flips suspects (Argent 1m sur données quasi-stables, S&P 7j sur 5bp taux court) + saut Pétrole sur triplet OPEC |

---

## TOP 3 des problèmes — classés par gravité

### P1 — DÉFAUT : mono-critère EUR/USD non signalé

EUR/USD 7j : 96% du score porté par le différentiel 2Y US-DE. Le flag `mono_critere_dominant` est absent du bulletin EUR/USD alors qu'il est présent pour CAC 40 7j. Si le seuil de détection est absolu (ex. ≥80% d'un critère), il doit se déclencher ici. Thomas peut interpréter la haute conviction EUR/USD comme un vrai signal robuste alors qu'il repose sur 1 seul paramètre. **Action : vérifier le seuil de `mono_critere_dominant` dans le code et l'appliquer à EUR/USD.**

### P2 — À SURVEILLER : instabilité S&P 500 7j sur variation marginale de taux

S&P 500 7j flip LONG → SHORT sur une variation de +0.05% du taux 10Y sur 5 jours (critère poids 9). Le critère "Taux 10Y delta 5j" est très sensible à l'intraday et son poids (9) lui donne un levier disproportionné sur un horizon 7j. La direction affichée peut changer à chaque run sans changement fondamental. **Action : envisager un lissage du delta (ex. moyenne 3 jours) ou réduire le poids relatif de ce critère en 7j.**

### P3 — À SURVEILLER : couverture structurellement basse sur Cacao/Café/Cuivre

Ces 3 actifs sont en ⚠️ conf. faible sur les 3 runs consécutifs. Cuivre à 48% : la direction repose sur un triplet binaire (mining strikes = 1) et deux proxies. Ce n'est pas une panne de flux mais un manque de données structurel (Caixin PMI mensuel, inventaires LME/SHFE non gratuits). Le gate ⚠️ est actif et fonctionne. Mais la direction LONG 24h et SHORT 7j/1m simultanées sur Cuivre avec des scores quasi-nuls (-0.22 en 7j) est un coin-flip non signalé. **Action : vérifier si `coin_flip:false` dans le decision-log pour Cuivre 7j — si la détection ne se déclenche pas pour un score à -0.22, le seuil de coin-flip est peut-être trop élevé.**

---

*Fichier produit : `v3/audit/bulletin-analyst-2026-06-05.md`*
*Verdict global : **AJUSTER** — méthode globalement saine, mais 1 défaut de signalement (P1) et 2 instabilités à corriger avant émission réelle.*
