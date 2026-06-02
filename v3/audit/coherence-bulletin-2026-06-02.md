# Cohérence trio d'experts — Bulletin 2026-06-02 (run 12h29)

> Synthèse des 3 audits : `bulletin-analyst.md`, `bulletin-newstrader.md`, `bulletin-speculateur.md`.
> Panel officiel (cf. `README.md`). Méthode : on retient en priorité ce qui converge (≥2 experts).

## Verdict consolidé : **AJUSTER — 6/10** (unanime)

| Expert | Note | Δ vs 31/05 |
|---|---|---|
| Analyst (rigueur stat) | 6.0/10 | — |
| News Trader (desk macro) | 6/10 | +0.5 |
| Spéculateur (conviction cash) | 6/10 | +1.5 |

**Progrès réel** confirmé par les 3 : plus aucune cellule portée à 100 % par un triplet keyword non confirmé (le « blé LONG aberrant » du 31/05 a disparu) ; drapeaux ↯/⇄/⚪ lisibles ; moteur arithmétique propre (Analyst : 3/3 reconstitutions ✓). Le système est devenu **honnête sur ses trous**.

## Le noyau sain (les 3 d'accord — cellules à conviction)

- **Or SHORT (24h/7j/1m)** — la plus propre : TIPS réel 2.07 (roi de l'or) + COT + VIX bas, géopol correctement neutralisée à 0 (déjà pricée). Monotone, zéro news-dépendance.
- **Pétrole LONG (7j/1m)** — ossature OPEC+ (driver lent voulu) + COT + Cushing ; tient sans la news Ormuz. Le `sign_conflict` EIA est cohérent avec le LONG (stocks bas → hausse).
- **Argent LONG (1m)** — ratio Gold/Silver extrême + COT.

→ 5 critères actifs chacun, scores amples. **Publiables.**

## Convergences critiques (≥2 experts) — à corriger

### 🔴 C1 — Coin-flips contre news fraîche (3 experts)
- **Nasdaq 24h SHORT** : score **-0.02** (⚪↯⇄ simultanés) tranché par la règle jamais-neutre, alors que le signal IA/Nvidia est **LONG fort** (chip Nvidia confirmé, SOX +0.89), écrasé par TIPS (poids 11). Edge inexistant. **Artefact identique au 31/05, non résolu.**
- **VIX 24h SHORT** (News Trader, P0) : triplet géopol `+1 confirmed` frais (frappes Ormuz/Ukraine le jour même) mais conclusion SHORT car term structure 0.82 écrase. Shorter la vol à contre-news fraîche sur 24h = non défendable ; ↯ levé mais conclusion non désarmée.

### 🔴 C2 — 42 % du bulletin en INSUFFISANT (3 experts) — **cause racine identifiée**
5 actifs hors production : S&P 500 (27 %), EUR/USD (18 %), Cuivre (35 %), Cacao (37 %), Café (29 %).
**Consensus des 3 sur la cause** : ce **n'est PAS le seuil du gate S5** (qui fonctionne comme conçu), mais des **critères quant lourds structurellement absents** — TIPS (partagé Nasdaq↔S&P), DXY, Caixin PMI, LME stocks, FedWatch — + **feeds muets** (mining_com 403, gnews/newsapi 429) qui privent les soft commodities de leurs triplets.
**Effet de bord grave** : le gate **masque** l'incohérence de régime Nasdaq/S&P du 31/05 au lieu de la résoudre (S&P muet car son TIPS est absent, alors que ce même TIPS porte ~90 % du SHORT Nasdaq). On perd aussi S&P 1m qui était la meilleure cellule la veille.

## Tension à arbitrer (désaccord)
- **Analyst** : baisser temporairement `COVERAGE_MIN` 0.40 → 0.30 pour réduire les INSUFFISANT.
- **Spéculateur** : au contraire, **ne pas publier** de direction sous 50 % de couverture.
→ **Arbitrage proposé** : ne PAS toucher le seuil (les 3 disent que la vraie cause = données absentes). Baisser le seuil = pansement qui re-publierait des cellules sous-couvertes. **Garder le seuil, combler les données** (C2). À trancher par Thomas.

## Solos à retenir (1 expert, mais P0)
- **Doublon Cacao** (Analyst, P0) : `hf_positioning_flux_options` = `cftc_cot_cocoa` (même brut -22 106 / normalisé -0.759). Impact nul ce cycle (composite inactif) mais **à corriger avant activation**.
- **Ambiguïté `valeur_ponderee` vs `valeur_normalisee`** (Analyst, P0) : la reconstitution arithmétique suggère que le moteur utilise `valeur_normalisee` pour les contributions → `valeur_ponderee` serait un champ non utilisé en scoring. Source de confusion pour les audits. À clarifier.
- **Pétrole 24h** (Spéculateur) : score brut +5.61 mais ~60 % porté par la news Ormuz (spike, pas vague) → afficher le **pondéré en primaire** sur les cellules 📰.

## Plan d'action consolidé

**P0 (avant tout)**
1. **Désarmer / abstenir les coin-flips contre news fraîche** : Nasdaq 24h + VIX 24h (|score|≈0 + flags + contre-news confirmée). Réconcilier visuellement les cellules ↯.
2. **Intégrité scoring** : corriger le doublon Cacao + clarifier `valeur_ponderee`/`valeur_normalisee` avant toute activation composite.

**P1 (le vrai levier)**
3. **Rebrancher les critères quant lourds absents** (TIPS partagé Nasdaq↔S&P, DXY, Caixin/LME, FedWatch) — **cause racine des 5 INSUFFISANT**. C'est le chantier #1.
4. **Réparer les feeds muets** (mining_com 403, gnews/newsapi 429) qui assèchent les soft commodities.
5. Afficher le **pondéré en primaire** sur les cellules 📰 (News Trader + Spéculateur).

**P2**
6. **Brier/Wilson par cellule** dès N suffisant, avant tout capital réel — valider que Or/Pétrole/Argent/Nasdaq-1m tiennent >70 % sur 30 conclusions.

## Lien avec la Priorité 1 du mémo de reprise
Le mémo demandait de « vérifier la calibration coverage sur le run frais ». **C'est fait, sur données fraîches (12h29)** : 42 % en INSUFFISANT, **et la cause est tranchée par le trio** → ce **n'est pas** un seuil mal calibré, c'est le **pipeline qui ne remplit pas assez de critères quant lourds**. La correction n'est donc pas `COVERAGE_MIN`, mais **rebrancher TIPS/DXY/Caixin/LME/FedWatch + réparer les feeds muets** (P1 ci-dessus).
