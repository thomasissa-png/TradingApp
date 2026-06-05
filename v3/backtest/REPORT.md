# Backtest QUANT historique — Rapport v2 (2026-06-05)

> Backtest du moteur **quant-only** (features price-derived + macro FRED/COT) sur
> historique réel. But : prouver/réfuter l'edge directionnel du moteur SANS la
> partie news (irreproductible).
> Méthode : no-look-ahead strict, échantillonnage non-chevauchant par horizon,
> walk-forward IS 2021-2024 / OOS 2025-01 → présent.

## Ce que v2 ajoute par rapport à v1

1. **FRED historique as-of** (`fred_series_asof` / `fred_spread_asof` LOCF /
   `fred_delta_asof`) : `DFII10` (taux réels TIPS — **corrige le bug v1** du proxy
   ETF `TIP` inversé), `BAMLH0A0HYM2` (HY spread), `DTWEXBGS` (DXY broad),
   `DGS10` delta 5j, spreads `DGS10−Bund` et `OAT−Bund`. Filtrage strict `< as_of`.
2. **CFTC COT historique as-of** (`cot_nets_asof`) : nets non-commerciaux
   (long−short) via Socrata `jun7-fc8e`, **même définition que le live**, z-score
   identique. Lag de publication T+3 appliqué (no-look-ahead).
3. **Horizons 7j + 1m** (mapping jours = `journaliste.HORIZON_DAYS` : 24h=1, 7j=7,
   1m=30 jours calendaires — aligné sur la mesure live).
4. **12 actifs** (vs 4 en v1) + **étude d'ablation** par groupe de critères.

Toutes les formules de normalisation/scoring sont **réutilisées du live** (zéro
réimplémentation divergente).

---

## ⚠️ Limite majeure du run présenté ici : FRED n/a (clé absente)

Le run ci-dessous a été exécuté dans un environnement **sans `FRED_API_KEY`**.
Conséquences :
- Les critères FRED (`DFII10`, `BAMLH0A0HYM2`, `DTWEXBGS`, `DGS10` delta/spreads)
  sont tombés en **n/a (poids 0)** → le scénario d'ablation **`+FRED` est IDENTIQUE
  à `price-only`** (la branche FRED n'est PAS réellement testée ici).
- **CFTC COT EST actif** (réseau Socrata OK) et **yfinance EST actif** (prix réels).

→ **Le code FRED est validé** (tests no-look-ahead verts, chemin exécuté), mais le
**verdict définitif sur la contribution FRED nécessite un re-run avec la clé**
(CI live l'a : `FRED_API_KEY` en secret GitHub). Voir « Reproductibilité ».

---

## Résultats OOS — pooled (12 actifs)

| Horizon | N concl. | Accuracy | Wilson_low |
|---|---|---|---|
| 24h | 2614 | 48.2% | 46.3% |
| 7j  | 486  | 44.4% | 40.1% |
| 1m  | 96   | 41.7% | 32.3% |
| **POOLED GLOBAL** | **3196** | **47.4%** | **45.7%** |

**Observation clé** : l'accuracy **décroît** avec l'horizon (48.2% → 44.4% →
41.7%). C'est l'**inverse** de la thèse trend-following (qui prédirait un edge
*croissant* à 7j/1m). Sur cet échantillon (COT actif, FRED absent), le moteur est
sous le pile-ou-face à tous les horizons.

## Résultats OOS — par cellule (sélection)

| Cellule | N | acc | WL | p-val | Verdict |
|---|---|---|---|---|---|
| ^GSPC 24h | 214 | 54.2% | 47.5% | 0.421 | NO-GO |
| ^FCHI 24h | 188 | 54.3% | 47.1% | 0.083 | NO-GO |
| **^VIX 7j** | 32 | **59.4%** | 42.3% | **0.049** | NO-GO (WL<55%) |
| **^VIX 1m** | 8 | **75.0%** | 40.9% | **0.039** | NO-GO (N=8) |
| GC=F 24h | 236 | 42.8% | 36.6% | 0.991 | NO-GO |
| GC=F 1m | 11 | 18.2% | 5.1% | 0.998 | NO-GO |
| HG=F 7j | 43 | 32.6% | 20.5% | 0.789 | NO-GO |

(Tableau complet 36 cellules dans le log de run.)

Le seul signal notable est **^VIX** (7j p=0.049, 1m p=0.039) mais avec accuracy
sous 60% / Wilson_low très loin de 55% et un N minuscule (8-32) → **ne remplit
AUCUN critère GO**. À surveiller, pas à conclure.

## Étude d'ablation — pooled OOS par groupe de critères

| Scénario | N concl. | Accuracy | Wilson_low | p-val |
|---|---|---|---|---|
| price-only | 3196 | 48.4% | 46.6% | 0.390 |
| +FRED | 3196 | 48.4% | 46.6% | 0.390 |
| +COT | 3196 | 47.4% | 45.7% | 0.418 |
| tous | 3196 | 47.4% | 45.7% | 0.418 |

Lecture (avec la réserve « FRED n/a » ci-dessus) :
- **+FRED == price-only** : artefact d'environnement (clé FRED absente) — **non
  concluant sur FRED**, à refaire avec la clé.
- **+COT DÉGRADE légèrement** l'accuracy (48.4% → 47.4%). Sur cet échantillon, le
  positionnement COT noncomm n'apporte pas d'edge directionnel — il en retire un
  peu (cohérent avec le COT noncomm souvent contrarian/bruité en directionnel CT).
- Aucun groupe ne fait passer le pooled au-dessus de 50%.

## Verdict v2 : **NO-GO** (périmètre testé : price + COT ; FRED en attente de clé)

Critères GO (accuracy OOS ≥60% ET Wilson_low ≥55% ET p-bootstrap <0.05) :
**aucune cellule, aucun horizon, aucun pooled** ne les remplit. Pooled global
**47.4%** (sous le hasard), edge **décroissant** avec l'horizon — contraire à la
thèse trend-following. Cohérent avec v1 (price-only 24h ≈ 50.8%).

## Valeurs aberrantes / points d'attention repérés

1. **Biais LONG massif en OOS** : `long%` OOS atteint **82-91%** sur plusieurs
   cellules (KC=F 82%, CC=F 91%). Effet régime 2025 haussier en partie, mais
   asymétrie qui suggère que le tie-break / signe des critères pousse
   structurellement LONG (cohérent avec le « biais LONG 61% borderline » noté par
   @data-analyst sur données réelles). À investiguer.
2. **GC=F (or) franchement à contresens** (24h 42.8%, 1m 18.2%) même avec le COT
   or actif → signe/échelle à revoir.
3. **N très faible en 1m** (3 à 14 conclusions/cellule) : walk-forward mensuel non-
   chevauchant sur ~17 mois OOS → toute accuracy 1m par cellule est statistiquement
   vide (NO-GO « N faible »).

## Limites résiduelles

1. **FRED non testé dans ce run** (clé absente) — re-run avec `FRED_API_KEY`
   requis pour conclure sur la branche FRED. Code prêt et testé.
2. **`differentiel_taux_2y_us_de`** n/a : côté DE = ECB Data Portal (pas FRED) côté
   live → câbler l'ECB historique = réimplémentation divergente, écartée. Poids 0.
3. **`shiller_cape_fwd_pe`** n/a : source live = scraper multpl (CAPE courant,
   non historisable). Pas de série FRED fiable équivalente. Poids 0.
4. **EIA / météo / news / triplets** restent n/a (non reproductibles), comme v1.
5. **CL=F (WTI) proxy pétrole** (vs BZ=F live) : historique yfinance plus propre ;
   BZ=F écarté pour ne pas double-compter la fiche petrole.

## Reproductibilité

```bash
export FRED_API_KEY=...        # secret GitHub côté CI (sinon FRED en n/a)
python3 v3/backtest/backtest_quant.py     # ~3-6 min (12 actifs × 3 horizons + ablation)
```
Réseau requis : yfinance (prix), Socrata CFTC (COT), FRED (macro). Cache disque
`v3/backtest/.cache/`. Tests : `pytest v3/tests/test_backtest.py` (21, dont 6
no-look-ahead : 2 prix + 4 FRED/COT).

---

## Annexe — verdict v1 (2026-06-01, conservé)

4 actifs × 24h, **price-only**. POOLED OOS **50.8%** (840 concl.) = pile ou face.
CL=F borderline (57.6%, p=0.019, <60%). Bug identifié : proxy ETF `TIP` inversé →
**corrigé en v2** (FRED `DFII10`).
