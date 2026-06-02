# Audit Analyst — Bulletin 2026-06-02 · 12h29

Auditeur : @data-analyst | Run : 2026-06-02T12:29:23 CET | Bulletin v3.0.0
Précédent audit : bulletin-analyst.md (run 2026-05-31 — référence)

---

## VERDICT GLOBAL

**AJUSTER — Note : 6.0/10**

Le moteur arithmétique reste sain (normalisations dans [-1,1], pas de division par zéro détectée). Mais ce bulletin présente trois problèmes structurels sérieux qui dégradent son utilisabilité par rapport au run du 31/05 :

1. **Gate S5 massif : 15 cellules sur 36 en INSUFFISANT** — soit 42% du bulletin hors production. La couverture réelle des actifs concernés (18%–37%) signale soit un pipeline de données partiellement muet, soit un seuil COVERAGE_MIN trop agressif. Ce point était marqué `⚠️ À VÉRIFIER (priorité 1)` dans project-context.md depuis le run sandbox — il se confirme sur données fraîches.
2. **Cacao : anomalie critique d'identité de normalisation** — `hf_positioning_flux_options` et `cftc_cot_cocoa` partagent la même valeur brute (-22 106) et la même normalisée (-0.759). C'est un doublon manifeste ou une erreur de câblage.
3. **Nasdaq × tous horizons : trio de flags ↯⇄ sur un score 24h quasi coin-flip (-0.02)** — la cellule est classée SHORT par la règle jamais-neutre mais le signal est statistiquement inexploitable.

---

## 1. Intégrité des normalisations [-1, 1]

**Violations détectées : 0**

Toutes les valeurs normalisées observées restent dans l'intervalle attendu. Saturations légitimes :
- CFTC COT Copper nets : +1.000 (z-score au plafond, déjà signalé run 31/05, comportement attendu)
- Term structure VIX/VIX3M : -1.000 (valeur linéaire hors de la plage centre±échelle = 0.95±0.1 ; le ratio observé à 0.822 donne (0.822-0.95)/0.1 = -1.28 → clampé à -1.000 conforme)
- RSI 14j Nasdaq : +1.000 (RSI=78.67, (78.67-50)/25 = +1.147 → clampé à +1.000 conforme)
- RSI 14j S&P 500 : +1.000 (RSI=75.90, (75.90-50)/25 = +1.036 → clampé à +1.000 conforme)
- SKEW CBOE : +0.913 — valeur 148.7, (148.7-135)/15 = +0.913, pas de saturation, dans la plage.

**Signaux d'alerte sur les valeurs brutes :**
- USDA WASDE (Blé) : `valeur_normalisee: 0.0` avec note `hors fenêtre` — le critère le plus lourd du Blé (poids 11) est neutralisé. Score Blé 24h = -0.086 : borderline, sensible à ce critère absent.
- Grindings Q (Cacao) : identique, `valeur_normalisee: 0.0` + note `hors fenêtre` (poids 5).

---

## 2. Anomalie critique — Cacao : doublon de valeur brute

**Cellule concernée : Cacao (tous horizons)**

Dans `criteres-courants.md`, les deux critères suivants ont des valeurs identiques :

| Critère | Valeur brute | Normalisée | Poids |
|---|---|---|---|
| `hf_positioning_flux_options` (composite) | -22 106.0 | -0.759 | 7 |
| `cftc_cot_cocoa` (zscore) | -22 106.0 | -0.759 | 6 |

Il est statistiquement impossible que le positionnement HF/options (composite) et le COT CFTC (nets, en lots) partagent la même valeur brute à l'unité près. Hypothèses :
- **H1 (probable) :** le pipeline a câblé la même source (CFTC COT nets) dans deux critères distincts. Le critère `hf_positioning_flux_options` est un doublage involontaire.
- **H2 :** le critère composite n'est pas encore implémenté et hérite par défaut de la valeur COT.

Dans le bulletin, `hf_positioning_flux_options` est affiché comme `n/a (type de normalisation inconnu : 'composite')` → il ne contribue PAS au score. L'impact sur le score final est donc nul ce cycle. Mais la donnée brute visible dans `criteres-courants.md` est trompeuse et doit être corrigée.

**P0 : vérifier l'implémentation du critère composite Cacao dans le pipeline.**

---

## 3. Gate S5 — Analyse de la couverture par actif

**Rappel seuils : ≥65% = normale · 40-65% = ⚠️ conf. faible · <40% = 🚫 insuffisant**

| Actif | Coverage | Gate S5 | Critères manquants déterminants |
|---|---|---|---|
| Cacao | 37% | 🚫 INSUFFISANT | Météo CI+Ghana (p.11), Arrivées port (p.9), Spread NY-London (p.4), FX CFA/Cedi (p.3) |
| Café (Arabica) | 29% | 🚫 INSUFFISANT | Météo Brésil (p.11 — CRITIQUE), Stocks ICE (p.9), USD/BRL (p.6), Spread Arabica-Robusta (p.4) |
| Cuivre | 35% | 🚫 INSUFFISANT | Caixin PMI (p.12 — CRITIQUE), LME+SHFE stocks (p.8), DXY (p.6), Term structure (p.5) |
| EUR/USD | 18% | 🚫 INSUFFISANT | Diff. taux 2Y US-DE (p.12 — CRITIQUE), DXY (p.9), FedWatch (p.6), Spread OAT-Bund (p.4) |
| S&P 500 | 27% | 🚫 INSUFFISANT | VIX régime (p.8 — mapping_non_monotone), Taux 10Y delta 5j (p.9), Breadth (p.7), DXY (p.5), AAII (p.4), CAPE (p.4) |
| CAC 40 | 40% | ⚠️ conf. faible | V2X (p.8), Spread OAT-Bund (p.10 — CRITIQUE), Breadth (p.6) |

**Observation transversale : DXY absent sur 7 actifs simultanément** (Blé, CAC, Cuivre, EUR/USD, Or, Pétrole, S&P 500). C'est le même critère transversal non câblé qu'au run 31/05. Il n'a pas été corrigé entre les deux runs — priorité P1 maintenue.

**Actifs avec score valide mais coverage basse :**
- CAC 40 (40%) : conclut SHORT 24h (-0.10) et LONG 7j/1m. Score marginal sur une base de 3 critères actifs sur 8. La divergence intra-horizons (SHORT 24h / LONG 7j-1m) sur des scores si faibles est préoccupante — signal plus proche du bruit que d'une tendance.

**Point positif :** le gate S5 fonctionne exactement comme conçu — les 5 actifs sous 40% sont correctement éliminés de la mesure VRAI/FAUX. Le système ne produit pas de conclusion fausse sur des données insuffisantes.

---

## 4. Validité statistique — Taille d'échantillon et mesure

**N effectif à ce stade :** 2 cellules mesurées (Blé 24h SHORT VRAI, Cuivre 24h LONG VRAI). N_eff = 2.

Aucune affirmation statistique n'est possible. Wilson N=2 :
- Borne basse 95% avec 2/2 succès : ~34% (loi Wilson exacte)
- À titre de comparaison, un tirage pile-ou-face donnerait 2/2 avec probabilité 25%

**Interprétation :** le bilan 2 VRAI / 0 FAUX est encourageant mais statistiquement non-informant. Il faut N≥30 pour que Wilson_low dépasse le seuil opérationnel de 50%.

**Chevauchement des fenêtres 7j ↔ 1m :**
Ce risque structurel identifié dans l'audit précédent reste actif. Les critères utilisés pour 7j et 1m partagent les mêmes valeurs (même timestamp `2026-06-02T10:29:23`), différenciées uniquement par le facteur de pertinence. Les scores 7j et 1m sont donc corrélés positivement par construction. L'indépendance des observations entre ces deux horizons est partielle, ce qui gonfle artificiellement le N apparent si on les compte séparément.

**Multiple testing :** non applicable à N=2, mais à surveiller dès N>10 (36 cellules × 3 horizons = 108 tests potentiels sans correction).

---

## 4b. Observation Nasdaq — divergence news vs quant confirmée dans les critères

Dans `criteres-courants.md`, le triplet `sentiment_ia_megacaps` (Nasdaq) est :
- **valeur : +1 (LONG), materiality: medium, reliability: confirmed**, freshness: 0.44 jour (news du jour même)
- `valeur_normalisee: 1.0` mais `valeur_ponderee: 0.6` → facteur effectif = 0.6 (et non 0.42 attendu pour un triplet standard)

Le triplet IA/Nvidia est donc **clairement LONG et frais**, avec une fiabilité élevée. Pourtant le score Nasdaq 24h = -0.02 (SHORT par jamais-neutre). Le moteur TIPS (-2.94) + spread Nasdaq-Russell (-1.88) + RSI surbuyé (-1.60) écrase le signal news LONG (+4.00 de contribution brute 24h dans le bulletin, mais pondéré à +0.6×poids×pertinence dans les critères).

**Vérification de la pondération du triplet :**
- Si `valeur_ponderee = 0.6` alors contribution = 0.6 × poids(5) × pertinence_24h = 0.6 × 5 × p
- Le bulletin indique +4.000 pour le triplet 24h → cela implique pertinence_24h = 4.0/(0.6×5) = 1.33 — valeur > 1.0, impossible si pertinence ∈ [0,1]
- Alternative : le bulletin utilise `valeur_normalisee × poids × pertinence` (pas `valeur_ponderee`), soit 1.0 × 5 × p = 4.0 → pertinence_24h = 0.8. Plausible.

**Incohérence potentielle P0 :** si le moteur de scoring utilise `valeur_normalisee` pour les triplets (et non `valeur_ponderee`), alors le champ `valeur_ponderee` dans `criteres-courants.md` est un artefact non utilisé ou documenté pour un autre usage. À clarifier dans la spec du pipeline — la définition de `valeur_ponderee` pour les triplets est ambiguë.

---

## 5. Analyse des scores marginaux et coin-flips

**Cellules quasi coin-flip (|score| < 0.10) :**

| Cellule | Score ±1 | Score pondéré | Flags | Risque |
|---|---|---|---|---|
| Nasdaq 24h | -0.02 ⚪ | -0.02 | ↯ ⇄ | CRITIQUE — voir §6 |
| VIX 24h | -0.11 | -0.11 | ↯ | Marginal |
| VIX 7j | -0.13 | -0.13 | ↯ | Marginal |
| Blé 24h | -0.09 | -0.09 | — | Marginal |
| CAC 40 24h | -0.10 | -0.10 | ⇄ | Marginal + ⚠️ conf. faible |

**Le Nasdaq 24h est le cas le plus problématique.** Score = -0.02, soit pratiquement zéro. La règle jamais-neutre tranche SHORT, mais le signal est:
- Dominé par deux critères opposés de très grande amplitude : TIPS (-2.94) vs SOX trend (+5.59)
- Enrichi par le triplet IA/Nvidia (+4.00 × pertinence)
- Affaibli par le spread Nasdaq-Russell (-1.88) et le RSI en surbuyé (-1.60)

La conclusion SHORT 24h sur le Nasdaq est arithmétiquement correcte mais économiquement fragile : si le SOX trend continue sa poussée à +0.888 de z-score, un seul critère renverse le signal. Le flag ⚪ dans le bulletin est approprié mais ne suffit pas — un utilisateur humain qui lit SHORT Nasdaq 24h sans lire la légende est induit en erreur.

---

## 6. Cohérence directionnelle inter-horizons

**Flips signalés : 19 sur 36 cellules** (53% du bulletin) — taux de flip très élevé versus le run précédent.

**Analyse des flips vers INSUFFISANT :** 14 des 19 flips sont des LONG/SHORT → INSUFFISANT, causés par l'activation du gate S5 sur ce run. Ces flips ne traduisent pas un changement de tendance mais un problème d'alimentation du pipeline.

**Flips directionnels réels (signal qui change de sens) :**
| Cellule | Avant | Après | Score avant | Score après | Interprétation |
|---|---|---|---|---|---|
| CAC 40 24h | LONG | SHORT | — | -0.10 | Score marginal — bruit probable |
| Nasdaq 24h | LONG | SHORT | — | -0.02 | Score quasi-nul — rule jamais-neutre uniquement |
| VIX 24h | LONG | SHORT | — | -0.11 | Marginal mais économiquement plausible (VIX à 14.95 = calme) |
| VIX 7j | LONG | SHORT | — | -0.13 | Idem |

**Incohérence CAC 40 :** SHORT 24h mais LONG 7j et LONG 1m. Sur une coverage de 40% et des scores de -0.10/+0.82/+0.60, cette structure en zig-zag 24h vs moyen terme est plus vraisemblablement un artefact du faible nombre de critères actifs qu'un vrai signal de retournement tactique. Le flag ⇄ (contre-momentum) sur 24h est justifié.

---

## 7. Biais directionnel agrégé

| Direction | Cellules | % |
|---|---|---|
| LONG | 8 | 22% |
| SHORT | 13 | 36% |
| INSUFFISANT | 15 | 42% |

Sur les 21 cellules actives (hors INSUFFISANT), le ratio SHORT/LONG est 13/8 = 62% SHORT. C'est cohérent avec un environnement de marché où les taux réels élevés (TIPS 2.07%) pèsent sur l'or et les actifs growth, et où la géopolitique Moyen-Orient est active.

**Actifs entièrement SHORT :** Or (3×3 fort, scores -4.19/-5.50/-4.11), Blé (3×3 faible), VIX (3×3 faible), Nasdaq (3×3 dont un coin-flip).

**Actifs entièrement LONG :** Argent (3×3 modéré), Pétrole (3×3 fort, scores +5.61/+11.77/+9.59).

**Tension logique notable :** Or SHORT × Pétrole LONG × VIX SHORT simultanément, dans un contexte de tensions Iran actives. La logique risk-off (Or↑, VIX↑) est absente. Le TIPS élevé comprime l'or malgré la géopolitique — tension réelle de marché, documentée dans le bulletin précédent, qui persiste.

---

## 8. Vérification arithmétique (reconstitution manuelle)

**Cellules spot-checkées :**

| Cellule | Reconstitution | Score log | Écart |
|---|---|---|---|
| Or 24h | TIPS: -3.209 + CFTC: +0.519 + ETF flux: +0.097 + Tension géopol: 0.000 + Demande ind: 0.000 + VIX proxy: -1.601 = **-4.194** | -4.194 | < 0.001 ✓ |
| Pétrole 24h | EIA: 0.000 + API: 0.000 + Géopol: +3.360 + CFTC: +0.423 + OPEC: +1.440 + Cushing: +0.560 + Spread: -0.169 = **+5.614** | +5.614 | < 0.001 ✓ |
| VIX 1m | Niveau: +2.525 + Term struct: -4.800 + SKEW: +1.370 + VVIX: -0.233 + CFTC: +0.188 + Géopol: +0.400 = **-0.550** | -0.550 | < 0.001 ✓ |

La formule `score = Σ(norm × signe × poids × pertinence)` est rigoureusement respectée sur les 3 cellules vérifiées. Le moteur arithmétique est sain.

**Note sur la pertinence :** les pertinences utilisées ne sont pas visibles dans le bulletin — seuls les scores finals sont exposés. Pour Or 24h, la contribution TIPS devrait être 2.07*poids×pertinence_24h = 0.535×12×0.50 = 3.209. La pertinence 24h de TIPS est donc 0.50 (implicite). Ce point ne constitue pas une anomalie mais un angle mort d'auditabilité : les pertinences par horizon devraient être loguées dans le decision-log pour reconstitution complète.

---

## 9. Santé des sources — impact sur la couverture

**Flux en échec ce cycle :**
- `gnews` (HTTP 429) : source généraliste, impact diffus sur plusieurs actifs
- `mining_com` (HTTP 403) : source spécialisée métaux — impact direct sur Cuivre, Cacao, Café, Or
- `newsapi` (HTTP 429) : source généraliste secondaire

**Flux muets (0 gardé) :**
- `cnbc_economy`, `eia_press_releases`, `eia_today_in_energy`, `investing_stocks`, `oilprice` : 67 items reçus, 0 gardés (dédup + blacklist + filtre finance)

**Lien coverage ↔ flux muets :** la disparition de `mining_com` (403) explique en partie la couverture basse de Cuivre (35%), Cacao (37%), Café (29%). Sur l'horizon quant, les critères manquants (Caixin PMI, LME stocks) sont des sources structurellement absentes depuis le run 31/05 — le flux news n'explique pas tout.

**Le gate S5 a donc deux causes distinctes** à traiter séparément :
- **Cause A (news) :** `mining_com` 403 prive les soft commodities d'une source de triplets → réparation pipeline P1
- **Cause B (quant) :** Caixin PMI, LME stocks, FedWatch, DXY ne sont toujours pas câblés → P0 structurel depuis run 31/05

---

## Points forts du bulletin

1. **Gate S5 fonctionne comme conçu** — 5 actifs éliminés de la mesure VRAI/FAUX sur couverture insuffisante. Aucune conclusion fausse-confiante générée. C'est la principale amélioration vs le run 31/05.
2. **Moteur arithmétique rigoureux** — 3/3 reconstitutions manuelles sans écart. Pas de régression depuis le run précédent.
3. **Flags visuels actifs et corrects** — ⚪ sur Nasdaq 24h (coin-flip), ↯ sur VIX (divergence quant/news), ⇄ sur CAC 40 (contre-momentum). La communication du doute au lecteur est présente.
4. **Pétrole et Or : signaux forts et redondants** — Pétrole LONG (5 critères actifs sur 10, score +5.61/+11.77) et Or SHORT (5 critères actifs sur 8, score -4.19/-5.50) sont les deux cellules les plus robustes du bulletin. Edge directionnel clair.
5. **Bilan news : 2/2 VRAI** — petit N mais encourageant. Le jugement DeepSeek sur Blé SHORT et Cuivre LONG s'est avéré correct.

---

## Recommandations

### P0 — Critiques (avant utilisation en production)

**P0-A — Doublon Cacao `hf_positioning_flux_options` / `cftc_cot_cocoa`**
Les deux critères partagent la même valeur brute (-22 106) et la même normalisée (-0.759) dans `criteres-courants.md`. Vérifier dans le pipeline si `hf_positioning_flux_options` est réellement câblé sur une source distincte ou s'il hérite par défaut de la valeur COT. Impact sur score Cacao : nul ce cycle (type `composite` → n/a), mais le champ brut est trompeur pour les audits. Corriger avant que le composite soit activé.

**P0-B — DXY trend 20j absent sur 7 actifs**
Ce critère transversal est manquant depuis au moins le run 31/05. Les actifs les plus impactés : EUR/USD (DXY poids 9, 2e critère de la fiche), Or (poids 8), S&P 500 (poids 5), Blé (poids 4), Pétrole (poids 5), CAC (n/a mais en liste), Cuivre (poids 6). Câbler une source fiable pour DXY (FRED, Twelve Data) avant émission réelle.

**P0-C — Ambiguïté `valeur_ponderee` vs `valeur_normalisee` pour les triplets**
Pour le triplet `sentiment_ia_megacaps` du Nasdaq : `valeur_normalisee=1.0` mais `valeur_ponderee=0.6`. La reconstitution arithmétique de la contribution +4.000 (24h) dans le bulletin est cohérente avec `valeur_normalisee × poids × pertinence` (1.0 × 5 × 0.8 = 4.0), PAS avec `valeur_ponderee × poids × pertinence`. Cela suggère que le moteur de scoring utilise `valeur_normalisee` pour les triplets (pas `valeur_ponderee`). Si c'est le cas, `valeur_ponderee` dans `criteres-courants.md` n'est pas la valeur utilisée en scoring — ambiguïté à documenter ou corriger dans le pipeline pour éviter des audits erronés.

**P0-D — Pertinences par horizon non loguées dans decision-log**
La reconstitution arithmétique des scores est possible depuis le bulletin mais nécessite de déduire les pertinences. Le decision-log devrait exposer `pertinence_24h`, `pertinence_7j`, `pertinence_1m` par critère pour auditabilité complète. Critique avant Phase 2 news (où les pertinences sont dynamiques).

### P1 — Haute priorité (avant fin shadow)

**P1-A — Recalibrer COVERAGE_MIN ou câbler les critères manquants structurels**
5 actifs en INSUFFISANT (42% du bulletin) signale un problème systémique. Deux options :
- Option 1 (court terme) : baisser `COVERAGE_MIN` de 0.40 à 0.30 temporairement si les critères quant absents (Caixin, LME, DXY, FedWatch) ne peuvent être câblés rapidement. Permet au moins d'avoir un signal dégradé plutôt que l'abstention totale.
- Option 2 (fond) : câbler Caixin PMI (Cuivre, S&P, Argent, Pétrole), LME+SHFE stocks (Cuivre), FedWatch (EUR/USD), DXY — ces 4 sources récupèrent 20-30 points de coverage sur les actifs concernés.
- Les deux options sont compatibles : baisser le seuil temporairement + câbler les sources en parallèle.

**P1-B — Réparer `mining_com` (HTTP 403)**
Ce flux alimente les triplets news pour Cuivre, Cacao, Café. Son échec contribue à la couverture basse des soft commodities. Vérifier si le 403 est un blocage IP (GitHub Actions) ou une authentification expirée.

**P1-C — Nasdaq 24h : score quasi-nul et flags multiples**
Score -0.02 avec flags ⚪↯⇄ simultanés. La règle jamais-neutre tranche SHORT mais l'edge est inexistant. Envisager un seuil d'abstention optionnel pour les cellules avec |score| < 0.05 ET ≥2 flags détecteurs — ou à minima documenter ce cas dans le briefing comme « signal non-actionnable ».

### P2 — Moyen terme (avant émission réelle)

**P2-A — Correction multiple-testing**
À N>10 cellules mesurées, appliquer une correction Bonferroni ou Benjamini-Hochberg sur les KPIs Wilson/Brier. 36 cellules × 3 horizons = 108 tests potentiels. Sans correction, le taux de faux positifs est élevé même à une performance réelle de 55%.

**P2-B — Indépendance 7j ↔ 1m**
Les scores 7j et 1m partagent les mêmes valeurs de critères (même timestamp). La corrélation inter-horizons est structurelle. Envisager une fenêtre de données différenciée par horizon (par exemple, prix J-7 pour le score 7j, prix J-30 pour le score 1m) pour réduire la dépendance.

**P2-C — Cohérence VIX SHORT × Pétrole LONG × Or SHORT**
Cette configuration simultanée en contexte de tensions Moyen-Orient actives mérite une gate de cohérence macro. Si VIX SHORT (calme de marché attendu) ET géopolitique OPEC active → signaler l'incohérence à l'utilisateur. Implémentar comme flag-only en shadow d'abord.

---

## Tableau de synthèse par actif

| Actif | Couverture | Score 24h | Fiabilité | Problème principal |
|---|---|---|---|---|
| Or | ~63% | -4.19 | HAUTE | Aucun |
| Pétrole | ~55% | +5.61 | HAUTE | DXY absent |
| Argent | ~67% | +0.74 | MOYENNE | 3 critères absents |
| VIX | ~75% | -0.11 | MOYENNE | Score marginal |
| Blé | ~44% | -0.09 | FAIBLE | Score marginal, USDA hors fenêtre |
| CAC 40 | 40% | -0.10 | FAIBLE | ⚠️ conf. faible, OAT-Bund absent |
| Nasdaq | ~56% | -0.02 | FAIBLE | Coin-flip, flags multiples |
| S&P 500 | 27% | — | 🚫 | INSUFFISANT |
| Cuivre | 35% | — | 🚫 | INSUFFISANT, doublon COT |
| EUR/USD | 18% | — | 🚫 | INSUFFISANT, taux 2Y absent |
| Cacao | 37% | — | 🚫 | INSUFFISANT, doublon composite |
| Café | 29% | — | 🚫 | INSUFFISANT, météo Brésil absente |

---

*Handoff → @orchestrator*
*Fichiers produits : `/home/user/TradingApp/v3/audit/bulletin-analyst.md`*
*Points d'attention critiques : doublon Cacao (P0-A), DXY absent 7 actifs (P0-B), 42% du bulletin en INSUFFISANT (P1-A), Nasdaq 24h coin-flip avec flags multiples (P1-C)*
