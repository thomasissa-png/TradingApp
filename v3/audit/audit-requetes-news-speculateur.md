# Audit requêtes news — œil SPÉCULATEUR (trend-follower 24h/7j/1m) — ROUND 2

> Date : 2026-06-01 · Auditeur : expert Spéculateur (panel des 3 experts) · Cible : `v3/scripts/config.py` (STRUCTURED_QUERIES = 13 requêtes, EARLY_SIGNAL_FEEDS dont gnews_nasdaq/gnews_vix).
> Re-audit après application des corrections round 1. Question unique : **est-ce que ce que ramènent les requêtes m'aide à SUIVRE / RETOURNER une vraie vague de tendance, ou est-ce encore du bruit qui me fait flipper à tort ?**

## NOTE : 8/10

**+3 points vs round 1 (était ~5,5/10 implicite).** Mes deux cécités (Nasdaq tech/IA, VIX volatilité) sont **comblées en couverture** : le carburant arrive enfin aux critères `sentiment_ia_megacaps` et `tension_geopolitique_active`. Bon travail. Je ne mets pas 10/10 pour **3 raisons précises et corrigibles** (cf. §3) :

1. **VIX requêté à l'envers** — la requête VIX ramène les SYMPTÔMES (`VIX`, `volatility`, `selloff`, `flight to safety`) au lieu des CAUSES (`war`, `escalation`, `bank failure`, `default`, `sanctions`). Un trend-follower de la vague de peur arrive donc encore EN RETARD : il voit la volatilité quand elle a déjà doublé, pas le choc qui la déclenche. **C'est mon manque n°1 pour le 10/10.**
2. **Q5 indices encore 75 % rétroviseur** — `S&P 500 OR Wall Street OR US stocks OR earnings season` : 3 termes sur 4 sont des noms d'indices génériques qui ramènent « Wall Street closes higher / S&P ends mixed ». Seul `earnings season` est un driver. Q5 reste **génératrice nette de faux flips**.
3. **Nasdaq sans guidance/capex** — la requête Nvidia/semi/IA est bonne sur le choc d'offre (chips, export controls) mais rate le driver de RETOURNEMENT le plus violent : la **guidance** (`guidance cut`, `earnings miss`, `data center capex`). On capte la vague IA montante, on rate son pivot baissier.

**Pour 10/10 : 3 micro-corrections (§3), zéro nouvelle requête, zéro coût.**

---

## 1. Mes 2 cécités round 1 — sont-elles comblées ?

| Cécité round 1 | Statut round 2 | Détail |
|---|---|---|
| **Nasdaq — vague tech/IA non requêtée** | **🟢 COMBLÉE (couverture)** | Q12 `Nvidia OR semiconductor OR AI chips OR TSMC OR chip export controls OR Big Tech earnings` + `gnews_nasdaq`. Le critère `sentiment_ia_megacaps` (fiche nasdaq.yml, poids 5) reçoit enfin du carburant. ✅ |
| **VIX — vague volatilité/risk-off non requêtée** | **🟡 PARTIELLEMENT COMBLÉE** | Q13 `stock market volatility OR VIX OR risk-off OR market selloff OR flight to safety` + `gnews_vix`. Le critère `tension_geopolitique_active` reçoit du carburant MAIS via les symptômes, pas les causes (cf. §3.1). ⚠️ |

**Verdict cécités** : la cécité Nasdaq est levée nette. La cécité VIX est **déplacée, pas levée** — on est passé de « rien » à « du rétroviseur de volatilité ». Mieux que 0, mais ce n'est pas le carburant amont qu'un trend-follower de la peur exige.

---

## 2. Note par requête (les 13) — driver vs rétroviseur

Échelle : **A = catalyseur dur** (crée/retourne une vague) · **B = mixte** · **C = bruit rétroviseur** (faux flips).

| # | Requête (abrégée) | Note R2 | Évolution | Commentaire trend-follower |
|---|---|---|---|---|
| 1 | oil/brent/WTI/OPEC/crude inventories | **A** | = | Catalyseur dur OPEC+/stocks. Inchangé, solide. |
| 2 | gold/central bank gold buying/WGC/PBoC/real yields | **A** | ⬆ (B→A) | Enrichi achats BC + taux réels = vrais drivers de l'or. Excellent. |
| 3 | silver/industrial demand/solar PV/gold-silver ratio | **A-** | ⬆ (B→A-) | Demande indus./solaire = driver structurel argent. Très bon. |
| 4 | Fed/FOMC/ECB/inflation/CPI | **A** | = | Régime macro. Inchangé, solide. |
| 5 | **S&P 500 / Wall Street / US stocks / earnings season** | **C+** | ⬆ (C→C+) | DAX retiré (bien), `earnings season` ajouté (1 driver). Mais 3/4 termes = noms d'indices → **toujours « closes higher » dominant**. Reste du bruit. ⚠️ |
| 6 | EUR USD/ECB rate/Fed-ECB divergence/dollar index | **A-** | ⬆ (B/C→A-) | Resserré sur le différentiel Fed-BCE = LE driver d'EUR/USD. Gros progrès. |
| 7 | coffee/arabica/robusta/Brazil/Vietnam | **A** | = | Récolte/gel. Solide. |
| 8 | cocoa/Ivory Coast/Ghana/grindings/EUDR | **A** | ⬆ | + EUDR = driver réglementaire réel. Très bon. |
| 9 | wheat/Black Sea/Russia/US crop/WASDE | **A** | = | Géopol + WASDE. Solide. |
| 10 | copper/LME/Chile mine/China demand | **A** | = | Grève mine + Chine. Solide. |
| 11 | CAC 40/LVMH/Total/France budget | **B+** | = | Poids lourds + budget FR = drivers réels, mais « CAC 40 » ramène du compte-rendu. |
| 12 | **Nvidia/semi/AI chips/TSMC/chip export/Big Tech earnings** | **A-** | 🆕 | Choc d'offre chips = driver dur. Manque guidance/capex pour le pivot (cf. §3.3). |
| 13 | **volatility/VIX/risk-off/selloff/flight to safety** | **B-** | 🆕 | Carburant présent MAIS = symptômes (rétroviseur de vol), pas causes amont (cf. §3.1). ⚠️ |

**Bilan** : 8 requêtes en **A/A-** (vs 6 en round 1), 1 en B+, 1 en B-, 1 en C+. La dérive « rétroviseur » résiduelle se concentre sur **Q5 (indices) et Q13 (VIX)**.

---

## 3. Ce qu'il manque pour 10/10 — 3 corrections, 0 coût

### 3.1 — VIX : requêter les CAUSES, pas les symptômes (manque n°1)

**Problème** : `volatility OR VIX OR selloff OR flight to safety` décrit un marché qui A DÉJÀ paniqué. Pour un trend-follower, c'est le rétroviseur le plus cher : quand « market selloff » sort dans les titres, le VIX a déjà fait +50 %, la vague est à moitié jouée. Le critère fiche est `tension_geopolitique_active` (L1=Géopolitique) — il veut de la **géopol amont**, qui n'arrive PAS via ces mots.

**Correction** — remplacer Q13 par un mix cause+symptôme :
```
"war OR escalation OR military strike OR sanctions OR bank failure OR sovereign default OR market selloff OR risk-off OR VIX"
```
Garder `gnews_vix` mais réécrire sa query de la même façon (ajouter `war OR escalation OR sanctions OR %22bank+failure%22`). Effet : on capte le **choc systémique AVANT le spike VIX** → on entre/retourne la vague de peur au bon moment, pas après.

### 3.2 — Q5 indices : tuer le rétroviseur ou la dé-pondérer (manque n°2)

**Problème** : 3 termes sur 4 (`S&P 500`, `Wall Street`, `US stocks`) ramènent du compte-rendu de clôture = faux flips intraday sur un actif 7j/1m.

**Correction** — réécrire en drivers :
```
"stock market selloff OR market correction OR earnings season OR Fed rate stocks OR megacap tech OR market rally breadth"
```
**À défaut**, baisser le poids de la source qui porte Q5 (la requête structurée gnews/newsapi est déjà à 0,7 — acceptable, mais le flag `nature` DeepSeek devra impérativement filtrer `deja_cote` sur cette requête).

### 3.3 — Nasdaq : ajouter le driver de RETOURNEMENT (guidance/capex)

**Problème** : Q12 capte le choc d'offre (chips, export controls) mais pas le pivot baissier le plus brutal de la vague IA : une **guidance ratée** ou un **doute sur le capex data center**. C'est exactement ce qui retourne le Nasdaq en 7j.

**Correction** — étendre Q12 :
```
"Nvidia OR semiconductor OR AI chips OR TSMC OR chip export controls OR earnings guidance OR data center capex OR Big Tech earnings"
```
(ajout `earnings guidance OR data center capex`, qui peut remplacer la fin redondante si on veut rester court.)

> **Coût des 3 corrections** : ZÉRO requête ajoutée (on réécrit Q5, Q12, Q13 + 1 query RSS gnews_vix). Aucun impact moteur/budget/anti-timeout.

---

## 4. Pourquoi 8 et pas 9

Les 3 manques ci-dessus ne sont pas cosmétiques : **Q13 (VIX cause manquante)** laisse le trader systématiquement en retard sur la vague la plus rentable à retourner (la peur), et **Q5 (rétroviseur)** continue d'injecter des faux flips dans le scoring indices. Le flag `nature` DeepSeek en aval mitige le bruit Q5 mais **ne fabrique pas** le carburant géopol amont qui manque à Q13 — un filtre n'invente pas une donnée absente. Tant que Q13 reste en symptômes, le pivot VIX se prend en retard. C'est structurel, pas filtrable.

## 5. Verdict final

- **Commodités (1,2,3,7,8,9,10)** : 🟢 excellent. Drivers durs partout. Rien à toucher.
- **Macro/FX (4,6)** : 🟢 très bon. Q6 EUR/USD enfin sur le différentiel Fed-BCE.
- **Nasdaq (12)** : 🟢 cécité comblée. Manque guidance/capex pour le pivot (§3.3).
- **VIX (13)** : 🟡 carburant présent mais à l'envers (symptômes ≠ causes). **Manque n°1 du 10/10** (§3.1).
- **S&P (5)** : 🟡 amélioré (DAX retiré, earnings ajouté) mais reste 75 % rétroviseur (§3.2).
- **CAC (11)** : 🟢 OK (drivers FR présents).

**Chiffré** : sur 13 requêtes, **8 pleinement drivers (A/A-)**, 2 partielles (B+/B-), 1 résiduelle bruit (C+). Couverture utile passée de ~58 % (round 1) à **~85 %**. Les 3 micro-corrections §3 fermeraient les 15 % restants → **10/10 sans nouvelle requête ni surcoût.**

### Handoff
- **Action immédiate (3 edits)** : réécrire Q5 (drivers), Q12 (+ guidance/capex), Q13 (+ war/escalation/bank failure/default) + aligner la query RSS `gnews_vix`. Validation Thomas requise (modif requêtes = pas de modif silencieuse, garde-fous).
- **À mesurer en shadow** : sur Q13, le critère `tension_geopolitique_active` doit se déclencher sur un événement géopol AVANT le pic VIX (latence négative vs CBOE) — pas après.
- **Dépend de** : prompt DeepSeek classe L1=Géopolitique et L1=Tech-IA (déjà prévu) ; flag `nature` filtre `deja_cote` en aval (mitige Q5, ne corrige PAS Q13).
