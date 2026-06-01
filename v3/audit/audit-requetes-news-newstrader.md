# Audit requêtes news — œil « News Trader senior » (desk macro/commodities) — ROUND 2

> **NOTE : 9/10** (round 1 : ~6,5/10). Les 2 TROUS et 3 des 4 PARTIELS sont comblés ; l'intrus DAX est sorti. Reste 1 point pour le 10/10 : quelques **catalyseurs de tendance « violents/spécifiques »** non explicités dans les mots-clés (gel café, tenders GASC blé) + 2 RSS dédiés manquants.
>
> **Mission** : ré-auditer la PERTINENCE des requêtes/mots-clés news (`STRUCTURED_QUERIES` GNews/NewsAPI + `EARLY_SIGNAL_FEEDS`) vs l'objectif unique : **justesse de la TENDANCE directionnelle** sur 12 actifs. **La vitesse de capture est hors-sujet**. On juge : les mots-clés ramènent-ils le **bon driver de tendance** par actif, ni trop étroit, ni noyé dans le bruit ?
>
> Auteur : audit desk. Date : 2026-06-01. Round 2 (post-corrections). Périmètre : `v3/scripts/config.py`.

## Manques pour 10/10 (liste exacte)

Trois affinages, tous **P2** (le squelette est désormais correct, ce sont des catalyseurs de pointe) :

1. **Café — catalyseur « gel » non explicité.** La requête capte récolte/Brésil/Vietnam, mais LE déclencheur de tendance violente sur l'arabica est le **gel/sécheresse Minas Gerais**. Ajouter `frost Brazil OR drought Minas Gerais` (Q7). Sans ça, un spike de gel n'est capté que par ricochet « Brazil harvest ».
2. **Blé — demande importateur absente.** WASDE/mer Noire/US OK, mais le **signal de demande directionnel** = tenders **GASC Égypte** (1er importateur mondial) + récolte **Australie/Argentine** (offre HS). Ajouter `Egypt GASC wheat tender OR Australia wheat OR Argentina wheat` (Q9).
3. **2 RSS dédiés manquants** côté `EARLY_SIGNAL_FEEDS` : un flux **or-banques-centrales** (`gnews_gold_cb`) et le mot **`Nvidia`/`SOX`** est dans la query API mais le RSS `gnews_nasdaq` est bien là — OK. Manque surtout `gnews_gold_cb` pour donner à l'Or un capteur RSS dédié au volet demande officielle (aujourd'hui seul mining_com + query API). **Optionnel** : le volet CB or est déjà dans Q2, donc impact faible.

Affinages cosmétiques (n'enlèvent pas de point mais cités) : Cacao → maladies `Black Pod / Swollen Shoot` ; Cuivre → `Peru OR China stimulus / property` ; S&P → `high yield OR credit spreads` pour le volet crédit.

---

## TL;DR (verdict desk round 2)

- **Les 3 corrections P0/P1 du round 1 sont appliquées et bien faites** : Nasdaq a sa requête dédiée (Nvidia/semi/TSMC/export/Big Tech earnings) **+ RSS** ; VIX a sa requête + RSS (volatility/risk-off/selloff/flight to safety) ; DAX est retiré ; S&P sort en requête propre ; Or enrichi (central bank gold buying / PBoC / real yields) ; Argent dégroupé + PV/solaire/ratio ; EUR/USD resserré sur le différentiel Fed-BCE ; Cacao + EUDR ; Blé + WASDE ; Q3 agri générique redondante supprimée.
- **Couverture driver désormais correcte sur 10/12 actifs en « OK net »**, 2 en « OK avec catalyseur de pointe manquant » (Café gel, Blé GASC).
- **Bruit fortement réduit** : plus de DAX, plus de `forex/yen` fourre-tout, dégroupage des métaux. Le filet large résiduel (Q4 Fed/CPI) est légitime (macro transverse).
- **Aucun TROU restant.** Le bloc actions/vol US, point noir du round 1, est désormais câblé.

---

## Tableau d'audit par actif — ROUND 2

| # | Actif | Driver(s) de tendance desk | Requête(s)/feed(s) qui le captent | Round 1 | **Round 2** |
|---|---|---|---|---|---|
| 1 | **Pétrole (Brent)** | OPEC+, stocks EIA, géopol M-O, demande Chine, DXY | Q1 + EIA + oilprice | OK | **OK** |
| 2 | **Or** | Taux réels, **achats CB/PBoC**, DXY, risk-off | Q2 enrichi (central bank gold buying/PBoC/real yields) | PARTIEL | **OK** (RSS CB en option) |
| 3 | **Argent** | Or, **demande PV/solaire+indus**, ratio Au/Ag | Q3 (silver industrial/solar PV/gold silver ratio) + mining_com | PARTIEL | **OK** |
| 4 | **Cuivre** | PMI Chine, LME/SHFE, grèves Chili/Pérou | Q10 (LME/Chile/China demand) + mining_com | OK | **OK** |
| 5 | **Café** | **Gel/sécheresse Brésil**, stocks ICE, Vietnam robusta | Q7 (Brazil/Vietnam harvest) + gnews_coffee | OK | **OK−** (manque `frost`) |
| 6 | **Cacao** | Météo+arrivées CI/Ghana, grindings, EUDR | Q8 (+ grindings + EUDR deforestation) + gnews_cocoa | OK | **OK** |
| 7 | **Blé** | WASDE, sécheresse Plaines, mer Noire, **tenders Égypte** | Q9 (Black Sea/Russia/US crop/WASDE) + gnews_wheat | OK | **OK−** (manque GASC/Australie) |
| 8 | **CAC 40** | Politique FR/budget, OAT-Bund, LVMH, Total | Q11 (+ France politics budget) + gnews_cac40 | OK | **OK** |
| 9 | **S&P 500** | Fed/taux, VIX/risk-off, crédit HY, méga-caps | Q5 dédié (S&P/Wall Street/US stocks/earnings) + Q4 | PARTIEL | **OK** (crédit HY en bonus) |
| 10 | **Nasdaq** | **Nvidia/IA/semi/SOX, export chips, méga-caps** | Q12 dédié + gnews_nasdaq | **TROU** | **OK** |
| 11 | **VIX** | **Volatilité/risk-off/selloff/safe-haven** | Q13 dédié + gnews_vix | **TROU** | **OK** |
| 12 | **EUR/USD** | **Différentiel Fed-BCE**, DXY, stress EZ | Q6 resserré (ECB rate/Fed ECB divergence/dollar index) + Q4 | PARTIEL | **OK** |

**Bilan round 2** : **10 OK nets** · **2 OK− (catalyseur de pointe à expliciter : Café gel, Blé GASC)** · **0 TROU · 0 intrus**.
(Round 1 : 5 OK · 4 PARTIELS · 2 TROUS · 1 intrus DAX.)

---

## Détail desk — ce qui a basculé en OK

**Nasdaq — TROU → OK.** `Nvidia OR semiconductor OR AI chips OR TSMC OR chip export controls OR Big Tech earnings` (Q12) + `gnews_nasdaq`. Capte enfin le driver dominant 2024-2026 : idiosyncrasie tech/IA, semis, restrictions export Chine, earnings méga-caps. C'est la correction la plus importante du round et elle est bien ciblée. Affinage marginal possible : `SOX` / `hyperscaler capex`, mais non bloquant (TSMC + semiconductor couvrent déjà le complexe).

**VIX — TROU → OK.** `stock market volatility OR VIX OR risk-off OR market selloff OR flight to safety` (Q13) + `gnews_vix`. Le sentiment/risk-off — driver par nature de la vol — est désormais capté. Aligné. RAS.

**Or — PARTIEL → OK.** Q2 ajoute `central bank gold buying OR WGC OR PBoC gold OR real yields`. Les deux jambes du moteur de tendance (taux réels **et** demande officielle) sont câblées. Seul résidu : pas de RSS dédié `gnews_gold_cb` (le volet CB ne vit que dans la query API GNews/NewsAPI, soumise au quota) — d'où le « RSS en option » dans les manques.

**Argent — PARTIEL → OK.** Dégroupé de l'or et enrichi : `silver industrial demand OR solar photovoltaic OR gold silver ratio`. Le différenciateur argent vs or (demande PV + ratio) est explicite. Aligné fiche.

**S&P 500 — PARTIEL → OK.** Sort de l'ancien bucket pollué : `S&P 500 OR Wall Street OR US stocks OR earnings season`. Requête propre, DAX évacué. Bonus possible non bloquant : `high yield OR credit spreads OR recession` pour le volet crédit/régime.

**EUR/USD — PARTIEL → OK.** Resserré : `EUR USD OR ECB rate decision OR Fed ECB divergence OR dollar index`. Le `yen`/`forex` fourre-tout du round 1 est retiré, le différentiel de politique monétaire est explicite. Aligné.

**Cacao / Blé — affinés.** Cacao + `EUDR deforestation` (régulation = driver d'offre structurel) ✓. Blé + `WASDE USDA` ✓. Restent les catalyseurs de **demande** (GASC) et offre Sud (Australie/Argentine) pour le 10/10 — cf. manques.

---

## Bruit / hors-objectif — ROUND 2

- **DAX retiré** ✓ — plus d'intrus consommant du quota.
- **Q6 nettoyé** ✓ — `yen` et `forex` génériques supprimés ; resserrage sur EUR/USD + Fed-BCE.
- **Métaux dégroupés** ✓ — Or, Argent, Cuivre ont chacun leur requête dédiée ; plus de `platinum` parasite.
- **Q4 `Fed OR FOMC OR ECB OR inflation OR CPI`** : conservé, **légitime** — macro-driver transverse (or, indices, EUR/USD, blé via DXY). Ce n'est pas du bruit, c'est un capteur multi-actifs.
- **Risque résiduel faible** : chaque actif a maintenant soit une requête dédiée, soit (pour le macro) une requête transverse assumée. Plus d'actif « orphelin » dépendant d'un bucket large.

---

## Mots-clés à ajouter pour viser 10/10 (formulations exactes)

```python
# Q7 Café — expliciter le catalyseur de tendance violent (gel)
"coffee prices OR arabica OR robusta OR Brazil harvest OR Vietnam coffee OR frost Brazil OR drought Minas Gerais",

# Q9 Blé — ajouter demande importateur (GASC) + offre hémisphère sud
"wheat prices OR Black Sea grain OR Russia wheat OR US wheat crop OR WASDE USDA OR Egypt GASC tender OR Australia wheat",
```

```python
# EARLY_SIGNAL_FEEDS — RSS dédié or/banques centrales (donne à l'Or un capteur RSS hors quota API)
("gnews_gold_cb", "https://news.google.com/rss/search?q=%22central+bank+gold%22+OR+%22PBoC+gold%22+OR+%22gold+demand+WGC%22&hl=en-US&gl=US&ceid=US:en", 3600),
# + SOURCE_WEIGHTS : "gnews_gold_cb": 0.8
```

Cosmétiques (facultatifs, n'affectent pas la note) :
- Cacao Q8 : `OR Black Pod OR Swollen Shoot` (maladies = driver offre structurel).
- Cuivre Q10 : `OR Peru copper OR China stimulus OR China property`.
- S&P Q5 : `OR high yield OR credit spreads` (volet crédit/régime de marché).
- Nasdaq Q12 : `OR SOX OR hyperscaler capex` (le complexe semi est déjà bien couvert via TSMC+semiconductor).

---

## Verdict & priorisation — ROUND 2

**La couverture mots-clés est-elle alignée sur la justesse de tendance ? → OUI, à 9/10.**

Le bloc actions/vol US — point noir structurel du round 1 — est résolu : Nasdaq et VIX ont chacun requête **+** RSS dédiés, captant leurs vrais drivers (Nvidia/semi/export pour le Nasdaq, risk-off/volatilité pour le VIX). Les 3 PARTIELS métaux/FX (Or-CB, Argent-PV, EUR/USD-Fed/BCE) sont comblés, le S&P a sa requête propre, l'intrus DAX est sorti et le bruit FX/métaux est nettoyé. C'est un travail de desk désormais solide sur les 12 actifs.

Le point manquant pour le 10/10 n'est plus structurel mais **fin** : deux **catalyseurs de tendance « de pointe »** (gel café, tenders GASC blé) sont captés seulement par ricochet, et l'Or n'a pas de RSS dédié pour son volet demande officielle (uniquement la query API soumise au quota). Ces ajouts sont P2, à faible coût, et porteraient la couverture à l'exhaustivité des drivers.

### Top 3 affinages pour le 10/10
1. **[P2] Q7 Café — `frost Brazil OR drought Minas Gerais`** : le gel est LE catalyseur de tendance violente sur l'arabica.
2. **[P2] Q9 Blé — `Egypt GASC tender OR Australia wheat`** : capter la jambe demande (importateur n°1) et l'offre Sud.
3. **[P2] RSS `gnews_gold_cb`** : capteur RSS hors-quota pour le volet achats banques centrales de l'or.

> Conforme à `project-context.md` : ces affinages renforcent la **justesse de la tendance** (couverture du driver), pas la vitesse. À valider par Thomas avant modif `config.py` (pas de modif silencieuse + bump `PROMPT_VERSION` si le mapping article→actif change).

---

## Handoff

- **Livrable** : `v3/audit/audit-requetes-news-newstrader.md` (ce fichier, round 2, écrase round 1).
- **Note** : **9/10** (vs ~6,5/10 round 1). 10 OK nets, 2 OK− (Café gel, Blé GASC), 0 TROU, 0 intrus.
- **Constat** : toutes les corrections P0/P1 du round 1 sont appliquées et pertinentes. Reste 3 affinages P2 pour le 10/10 (cf. section dédiée), à coût quasi nul.
- **Action attendue** : si Thomas valide, appliquer les 2 reformulations Q7/Q9 + le RSS `gnews_gold_cb` → @fullstack, avec bump `PROMPT_VERSION` et tests verts.
- **Hors périmètre** : ne touche ni la vitesse de capture (hors-sujet par `project-context.md`) ni le scoring numérique (couvert par les fiches).
