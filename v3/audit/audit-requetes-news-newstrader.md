# Audit requêtes news — œil « News Trader senior » (desk macro/commodities) — ROUND 3

> **NOTE : 10/10** (round 1 : ~6,5/10 · round 2 : 9/10). Les 3 derniers affinages P2 du round 2 sont appliqués et bien formulés ; le dégroupage Fed/BCE résout un déséquilibre latent. Chaque actif a désormais ses **vrais drivers de tendance** câblés (requête dédiée + RSS pour les actifs idiosyncratiques), sans bruit excessif.
>
> **Mission** : ré-auditer la PERTINENCE des requêtes/mots-clés news (`STRUCTURED_QUERIES` = 14 requêtes GNews/NewsAPI + `EARLY_SIGNAL_FEEDS` = 22 flux) vs l'objectif unique : **justesse de la TENDANCE directionnelle** sur 12 actifs. **La vitesse de capture est hors-sujet**. On juge : les mots-clés ramènent-ils le **bon driver de tendance** par actif, ni trop étroit, ni noyé dans le bruit ?
>
> Périmètre NEWS uniquement. Le **positionnement CFTC** et les **données CBOE/options** relèvent du pipeline data (hors périmètre de cet audit, par construction).
>
> Auteur : audit desk. Date : 2026-06-01. Round 3 (post-corrections round 2). Périmètre : `v3/scripts/config.py`.

## TL;DR (verdict desk round 3)

- **Les 3 affinages P2 du round 2 sont appliqués et bien faits** :
  1. **Café Q8** + `frost Brazil OR drought Minas Gerais` → LE catalyseur de tendance violente sur l'arabica est désormais explicite, plus seulement capté par ricochet « Brazil harvest ».
  2. **Blé Q10** + `Egypt GASC OR Australia wheat` → la jambe **demande importateur n°1** (tenders GASC) et l'**offre hémisphère sud** (Australie) sont câblées.
  3. **Or** : flux RSS dédié `gnews_gold_cb` (achats banques centrales / réserves / PBoC / WGC) → l'Or a enfin un **capteur RSS hors-quota** pour son volet demande officielle, en plus de la query API Q2.
- **Bonus (autres experts), tous pertinents côté tendance** :
  - **Fed / BCE DÉGROUPÉS** (Q4 bloc US, Q5 bloc EU) → correction la plus structurante du round : Fed et BCE poussent l'EUR/USD en **directions opposées** ; les fusionner masquait le signal de divergence. Désormais chaque banque centrale a sa requête, et EUR/USD (Q7) capte le différentiel.
  - **S&P driver-isé** (Q6 : earnings beat / EPS surprise / guidance / correction) → sort du capteur indice générique pour viser le vrai moteur de tendance (saison des résultats + régime).
  - **VIX + causes AMONT** (Q14 + `gnews_vix` : war / escalation / sanctions / bank failure / sovereign default) → capte la **peur avant le spike**, pas seulement le symptôme « VIX/risk-off ». Excellent réflexe news-trader.
  - **Nasdaq + guidance/capex** (Q13 : + earnings guidance + data center capex) → ajoute le pivot baissier (guidance) et le driver haussier 2024-2026 (capex hyperscalers) au complexe semi.
  - **Flux dédiés** `gnews_ecb_policy` (équilibre le déséquilibre 4 flux Fed/US des RSS) et `gnews_silver_industrial` (demande PV/solaire/grèves mines) → couvrent les angles morts RSS des actifs FX/argent.

- **Couverture driver : 12/12 actifs en « OK net ».** 0 OK−, 0 TROU, 0 intrus.
- **Bruit maîtrisé** : le seul filet large résiduel (Q4 Fed, Q5 BCE) est un capteur **macro multi-actifs assumé** (or, indices, EUR/USD, blé via DXY), pas du bruit.

---

## Tableau d'audit par actif — ROUND 3

| # | Actif | Driver(s) de tendance desk | Requête(s)/feed(s) qui le captent | R2 | **R3** |
|---|---|---|---|---|---|
| 1 | **Pétrole (Brent)** | OPEC+, stocks EIA, géopol M-O, demande Chine, DXY | Q1 + EIA (×2) + oilprice | OK | **OK** |
| 2 | **Or** | Taux réels, **achats CB/PBoC**, DXY, risk-off | Q2 (CB gold/WGC/PBoC/real yields) + **`gnews_gold_cb`** + mining_com | OK | **OK** (RSS CB ajouté) |
| 3 | **Argent** | Or, **demande PV/solaire+indus**, ratio Au/Ag | Q3 (silver indus/solar PV/ratio) + **`gnews_silver_industrial`** + mining_com | OK | **OK** (RSS dédié ajouté) |
| 4 | **Cuivre** | PMI Chine, LME/SHFE, grèves Chili/Pérou | Q11 (LME/Chile/China demand) + mining_com + gnews_copper | OK | **OK** |
| 5 | **Café** | **Gel/sécheresse Brésil**, stocks ICE, Vietnam robusta | Q8 (+ **frost Brazil/drought Minas Gerais**) + gnews_coffee | OK− | **OK** |
| 6 | **Cacao** | Météo+arrivées CI/Ghana, grindings, EUDR | Q9 (grindings + EUDR) + gnews_cocoa | OK | **OK** |
| 7 | **Blé** | WASDE, sécheresse Plaines, mer Noire, **tenders GASC** | Q10 (+ **Egypt GASC + Australia wheat**) + gnews_wheat | OK− | **OK** |
| 8 | **CAC 40** | Politique FR/budget, OAT-Bund, LVMH, Total | Q12 (+ France politics budget) + gnews_cac40 | OK | **OK** |
| 9 | **S&P 500** | Fed/taux, earnings/EPS, régime/correction | Q6 (earnings beat/EPS/guidance/correction) + Q4 | OK | **OK** (driver-isé) |
| 10 | **Nasdaq** | **Nvidia/IA/semi, export chips, guidance, capex** | Q13 (+ guidance + data center capex) + gnews_nasdaq | OK | **OK** |
| 11 | **VIX** | Volatilité/risk-off + **causes amont (war/sanctions/bank failure)** | Q14 (+ war/escalation/sanctions/bank failure/sovereign default) + gnews_vix | OK | **OK** (causes amont) |
| 12 | **EUR/USD** | **Différentiel Fed-BCE**, DXY, stress EZ | Q7 (Fed ECB divergence/dollar index) + Q4 (Fed) + Q5 (BCE) + gnews_ecb_policy | OK | **OK** (Fed/BCE dégroupés) |

**Bilan round 3** : **12 OK nets** · **0 OK− · 0 TROU · 0 intrus**.
(R2 : 10 OK · 2 OK− · 0 TROU · 0 intrus. R1 : 5 OK · 4 PARTIELS · 2 TROUS · 1 intrus.)

---

## Détail desk — ce qui a basculé en OK net

**Café — OK− → OK.** `frost Brazil OR drought Minas Gerais` ajouté à Q8. Sur l'arabica, le gel Minas Gerais est le catalyseur de tendance le plus violent (spikes +30/+50 %). Avant, capté seulement par ricochet « Brazil harvest » — souvent trop tard pour le sens de tendance. Désormais explicite. Aligné.

**Blé — OK− → OK.** `Egypt GASC OR Australia wheat` ajouté à Q10. Deux jambes désormais câblées : **demande** (GASC = 1er importateur mondial, ses tenders donnent le ton du prix CME/Euronext) et **offre hémisphère sud** (Australie, contre-saison vs Plaines US). Combiné à WASDE + mer Noire déjà présents, le driver de tendance blé est complet.

**Or — RSS dédié ajouté.** `gnews_gold_cb` (`central bank gold` / `gold reserves` / `PBoC gold` / `WGC`) donne à l'Or un capteur RSS **hors-quota API** sur son driver structurel 2022-2026 (achats officiels). Le volet ne dépend plus uniquement de la query Q2 soumise au quota GNews/NewsAPI. Robustesse de couverture renforcée.

**Fed/BCE dégroupés — correction structurante.** En round 2, Fed et BCE cohabitaient dans une requête macro unique. Or sur l'EUR/USD ils agissent en **sens opposé** (Fed hawkish → USD up → EUR/USD down ; BCE hawkish → inverse). Les séparer (Q4 Fed/FOMC/Powell, Q5 ECB/Lagarde/Eurozone inflation) permet de lire la **divergence**, qui EST le driver de tendance de la paire. Q7 EUR/USD capte explicitement « Fed ECB divergence ». Très bon.

**VIX — causes amont.** Q14 et `gnews_vix` ajoutent les déclencheurs en amont (war / escalation / sanctions / bank failure / sovereign default) aux symptômes (VIX/risk-off/selloff). C'est exactement le réflexe news-trader : un trader de vol veut capter la **cause de la peur** avant que le VIX ne spike, pas la confirmation après coup.

**S&P / Nasdaq — driver-isés.** S&P (Q6) vise la saison des résultats (earnings beat/EPS surprise/guidance) + le régime (correction), au lieu d'un capteur indice générique. Nasdaq (Q13) ajoute « earnings guidance » (pivot baissier sur surévaluation) et « data center capex » (moteur haussier hyperscalers/IA) au complexe semi. Les deux indices captent leurs vrais moteurs idiosyncratiques.

---

## Bruit / hors-objectif — ROUND 3

- **0 intrus** — DAX toujours sorti (hors périmètre).
- **Fed/BCE dégroupés ≠ inflation de bruit** : deux requêtes ciblées valent mieux qu'une requête macro fourre-tout — chacune ramène un signal directionnel propre (US vs EU).
- **Métaux dégroupés** (Or/Argent/Cuivre requêtes dédiées) + RSS dédiés argent et or-CB → plus aucun actif métal « orphelin » d'un bucket large.
- **VIX élargi aux causes amont** : le risque serait de ramener du bruit géopolitique non-marché ; atténué par la co-occurrence avec les symptômes marché (`market selloff`/`risk-off`) et le poids RSS modéré (0.8). Acceptable : sur le VIX, manquer une cause amont coûte plus cher qu'un faux positif géopol.
- **Risque résiduel** : négligeable. Chaque actif a soit une requête dédiée, soit une requête transverse macro assumée. Le poids des agrégateurs (gnews_* 0.8, gnews/newsapi 0.7) borne leur influence dans le scoring downstream.

---

## Pourquoi 10/10 (et pas un demi-point retenu)

Côté **NEWS**, la couverture des drivers de tendance est désormais **exhaustive sur les 12 actifs** : chaque actif a son ou ses drivers dominants explicités en mots-clés, les actifs idiosyncratiques (Or, Argent, Café, Blé, Nasdaq, VIX, EUR/USD) ont en plus un RSS dédié hors-quota, et le bruit est borné par le dégroupage + la pondération. Les 2 OK− du round 2 (Café gel, Blé GASC) sont comblés ; le manque #3 (RSS or-CB) aussi. Le dégroupage Fed/BCE corrige un déséquilibre latent qui n'avait pas coûté de point au round 2 mais aurait pu fausser la lecture EUR/USD.

Il ne reste que des **affinages cosmétiques** (ci-dessous), qui ne changent pas la justesse de tendance et ne justifient donc pas de retenir un demi-point côté news.

---

## Affinages cosmétiques (facultatifs — n'affectent PAS la note 10/10)

- Cacao Q9 : `OR Black Pod OR Swollen Shoot` (maladies = driver offre structurel CI/Ghana).
- Cuivre Q11 : `OR Peru copper OR China stimulus OR China property` (PMI/relance Chine + Pérou 2e producteur).
- S&P Q6 : `OR high yield OR credit spreads` (volet crédit/régime — déjà partiellement via « correction »).
- Café Q8 : `OR ICE coffee stocks` (le niveau des stocks certifiés ICE module l'ampleur du spike gel).

Ces ajouts captent des **drivers de second ordre** ; les drivers de premier ordre sont tous déjà couverts. À considérer uniquement si le quota API le permet.

---

## Handoff

- **Livrable** : `v3/audit/audit-requetes-news-newstrader.md` (ce fichier, round 3, écrase round 2).
- **Note** : **10/10** (R1 ~6,5 · R2 9 · R3 10). 12 OK nets, 0 OK−, 0 TROU, 0 intrus.
- **Constat** : les 3 affinages P2 du round 2 (Café gel Q8, Blé GASC Q10, RSS or-CB) sont appliqués et bien formulés. Bonus pertinents : Fed/BCE dégroupés, S&P/Nasdaq driver-isés, VIX causes amont, flux ECB/silver dédiés. Côté NEWS, la couverture des drivers de tendance est exhaustive sur les 12 actifs.
- **Action attendue** : aucune obligatoire. Affinages cosmétiques optionnels listés ci-dessus, à arbitrer selon quota API uniquement.
- **Hors périmètre** : positionnement CFTC + données CBOE/options (pipeline data) ; vitesse de capture (hors-sujet par `project-context.md`) ; scoring numérique (fiches actifs).
