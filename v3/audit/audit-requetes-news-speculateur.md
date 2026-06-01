# Audit requêtes news — œil SPÉCULATEUR (trend-follower 24h/7j/1m)

> Date : 2026-06-01 · Auditeur : expert Spéculateur (panel des 3 experts) · Cible : `v3/scripts/config.py` (STRUCTURED_QUERIES, EARLY_SIGNAL_FEEDS, RSS_FEEDS) + 12 fiches `v3/config/fiches/`.
> Question unique : **est-ce que ce que ramènent les requêtes m'aide à SUIVRE / RETOURNER une vraie vague de tendance, ou est-ce du bruit qui me fait flipper à tort ?**

## TL;DR (brutal)

- **Set actuel = MOITIÉ utile pour un trend-follower.** Bon sur les commodités (catalyseurs durs : OPEC, récolte, mine). Aveugle sur les 2 vagues les plus rentables à suivre en 2025-2026 : **la vague tech/IA (Nasdaq) et la vague de volatilité/risk-off (VIX)**.
- **Faille structurelle** : 2 fiches déclarent un critère news (`sentiment_ia_megacaps` Nasdaq, `tension_geopolitique_active` VIX) **mais AUCUNE requête ne ramène le sujet**. Le critère existe, le carburant n'arrive jamais → critère muet → poids gaspillé.
- **3 ajouts changeraient tout** (cf. §4) : (A) requête Tech-IA/Nvidia/chips, (B) requête volatilité/risk-off/war, (C) requête earnings méga-caps.

---

## 1. Catalyseurs de vague vs bruit — verdict par requête

Échelle de notation (point de vue « ça m'aide à rester du bon côté de la vague ? ») :
**A = catalyseur dur** (provoque/confirme une vague, mots-clés à effet directionnel) ·
**B = mixte** (un peu de driver, beaucoup de compte-rendu) ·
**C = bruit** (surtout opinion/compte-rendu, génère de faux flips).

| # | Requête | Note | Catalyseurs durs qu'elle ramène | Bruit qu'elle ramène |
|---|---|---|---|---|
| 1 | oil OR brent OR WTI OR **OPEC** | **A** | décisions OPEC+ (quotas), sanctions, stocks EIA, Détroit d'Ormuz | « oil edges higher », notes de courtiers |
| 2 | gold OR silver OR copper OR platinum | **B** | achats banques centrales (or), grève mine (cuivre/platine) | « gold rises on safe-haven », commentaires |
| 3 | wheat OR corn OR coffee OR cocoa OR sugar | **B** | sécheresse, USDA WASDE, embargo | round-up matières premières génériques |
| 4 | Fed OR FOMC OR **ECB** OR inflation OR **CPI** | **A** | décision de taux, surprise CPI, ton hawkish/dovish, minutes | « investors await the Fed », prévisions d'analystes |
| 5 | Nasdaq OR S&P 500 OR CAC 40 OR DAX | **C** | quasi rien de causal | **100 % de « index closes higher/lower », « Wall St mixed »** = pur compte-rendu rétroviseur |
| 6 | EUR USD OR yen OR dollar index OR forex | **B/C** | intervention BoJ, écart de taux | « euro slips vs dollar », analyse technique de blog |
| 7 | coffee/arabica/robusta/**Brazil/Vietnam harvest** | **A** | gel/sécheresse Brésil, récolte Vietnam, ICE stocks | |
| 8 | cocoa/**Ivory Coast/Ghana**/grindings | **A** | maladie cabosses, météo Afrique de l'Ouest, grindings | |
| 9 | wheat/**Black Sea/Russia**/US crop | **A** | corridor grain, frappes ports, conditions de culture | |
| 10 | copper/LME/**Chile mine**/China demand | **A** | grève mine Chili, stimulus/demande Chine, stocks LME | |
| 11 | CAC 40/**LVMH/Total/France budget** | **B** | résultats poids lourds, risque budgétaire/politique FR | « le CAC termine en hausse » |

**Lecture trend-follower** : les requêtes commodités (1,2,3,7-11) et macro (4) ramènent du **driver de vague** — exactement ce qui CRÉE une tendance OPEC/récolte/taux durable. La requête **5 (indices) est du bruit pur en l'état** : « S&P closes higher » ne dit rien sur la prochaine vague, c'est le rétroviseur. La requête **6 (FX) est faible** : du compte-rendu, peu de drivers.

---

## 2. Actifs aveugles à leur vague

Pour chaque actif : la **vague que doit suivre le trader**, et si une requête la ramène vraiment.

| Actif | Vague réelle à suivre | Requête qui l'alimente | Couverture | Critère news de la fiche | Carburant arrive ? |
|---|---|---|---|---|---|
| Brent | choc offre OPEC+ / sanctions / Ormuz | #1 + EIA RSS + oilprice | ✅ forte | triplet géopol/offre | OUI |
| Or | risk-off + achats BC + taux réels | #2 + macro #4 | 🟡 moyenne | — surtout numérique | partiel |
| Argent | suit l'or + demande indus. | #2 + investing_metals | 🟡 moyenne | — | partiel |
| Cuivre | grève mine + demande Chine | #10 dédiée + mining_com | ✅ forte | demande Chine | OUI |
| Café | gel/sécheresse Brésil | #7 dédiée + gnews_coffee | ✅ forte | météo/récolte | OUI |
| Cacao | maladie + météo Afrique Ouest | #8 dédiée + gnews_cocoa | ✅ forte | offre Afrique | OUI |
| Blé | guerre/corridor Black Sea + USDA | #9 dédiée + gnews_wheat | ✅ forte | géopol/récolte | OUI |
| CAC 40 | poids lourds + budget/politique FR | #11 dédiée + gnews_cac40 | 🟡 moyenne | résultats/politique FR | partiel |
| S&P 500 | régime macro + earnings larges | #5 (bruit) + macro #4 | 🔴 faible | — | NON utile |
| **Nasdaq** | **vague tech/IA — Nvidia, chips, capex IA, guidance méga-caps** | **AUCUNE** (#5 = bruit) | **🔴 NULLE** | **`sentiment_ia_megacaps` (L1=Tech-IA)** | **NON — critère muet** |
| **VIX** | **vague de volatilité / risk-off — guerre, krach, choc systémique** | **AUCUNE** (rien sur war/risk-off/vol) | **🔴 NULLE** | **`tension_geopolitique_active` (L1=Géopolitique)** | **NON — critère muet** |
| EUR/USD | divergence Fed/BCE + intervention BoJ | #4 + #6 (faible) | 🟡 moyenne | — | partiel |

### Les 2 cécités graves (confirmées dans les fiches)

**Nasdaq — la vague tech/IA n'est PAS requêtée.** La fiche `nasdaq.yml` a un critère `id:6 sentiment_ia_megacaps` (source `events-log L1=Tech-IA`, poids 5, pertinence 24h=0.8 / 7j=0.9). Or **aucune requête GNews/NewsAPI ni RSS ne contient `Nvidia`, `AI`, `chip`, `semiconductor`, `earnings`, `Microsoft`, `guidance`**. La requête #5 ne ramène que « Nasdaq closes higher ». Conséquence trend-follower : **la plus grosse vague directionnelle de 2023-2026 (rallye IA) ne déclenche jamais le critère news.** On suit la vague tech avec UNIQUEMENT du numérique (SOX, breadth, TIPS) — donc on rate les **retournements amorcés par une news** (mauvaise guidance Nvidia, restriction export chips) tant que le prix n'a pas déjà tourné. Pour un trend-follower, **rater le pivot = se retrouver à contre-sens sur 7j-1m.**

**VIX — la vague de volatilité / risk-off n'est PAS requêtée.** La fiche `vix.yml` a un critère `id:8 tension_geopolitique_active` (source `events-log L1=Géopolitique`, poids 4, pertinence 24h=0.9) ET un GATE `id:9` (FOMC/CPI/ECB imminent). Mais **aucune requête ne ramène `war`, `conflict`, `sanctions`, `risk-off`, `selloff`, `volatility`, `crash`, `escalation`**. Le seul carburant indirect = la géopol qui transpire de #1 (pétrole) et #9 (blé). Conséquence : **le système ne voit la montée de volatilité que par les chiffres CBOE (term structure, put/call) — qui montent APRÈS le choc.** Un trend-follower de la vague de peur a besoin du **catalyseur (escalade, choc systémique) AVANT que le VIX n'ait déjà doublé.** Là, il arrive en retard sur chaque spike.

---

## 3. Mots-clés bruit (faux flips) vs drivers durs

| À BANNIR / dé-pondérer (font de faux flips) | Pourquoi c'est du poison trend-follower |
|---|---|
| `closes higher/lower`, `edges up`, `ends mixed`, `Wall St rises` | **Rétroviseur pur** : décrit la bougie passée, déclenche un flip qui suit le bruit intraday |
| `forecast`, `analysts expect`, `price target`, `outlook` | **Opinion** : avis de courtier ≠ catalyseur, crée des signaux sans événement réel |
| `could`, `may`, `fears`, `concerns` (titres sans fait) | conditionnel/sentiment → faux positifs L1 |
| `rallies on optimism`, `slips on caution` | habillage narratif d'un mouvement déjà coté (déjà-price) |

| DRIVERS DURS à privilégier (créent/retournent une vague) | Effet directionnel |
|---|---|
| `OPEC+ cuts/raises quotas`, `sanctions`, `embargo`, `strike`, `mine halt` | choc d'offre → vague durable |
| `drought`, `frost`, `harvest`, `disease`, `crop damage`, `USDA WASDE` | choc agri → vague saisonnière |
| `rate decision`, `hike/cut`, `hawkish/dovish`, `CPI surprise` | régime macro → vague taux/FX/indices |
| `guidance cut/raised`, `earnings beat/miss`, `export ban (chips)`, `capex` | choc méga-cap → vague tech |
| `war`, `escalation`, `attack`, `default`, `bank failure` | choc systémique → vague risk-off / VIX |

**Garde-fou déjà en place (bon point)** : la fiche Phase 2 prévoit le flag `nature` DeepSeek excluant `verbal / deja_cote / non_tradable` du scoring — c'est exactement le filtre anti-bruit qu'il faut. **Mais il filtre en aval ; il ne crée pas le carburant manquant en amont.** Ajouter les bonnes requêtes reste indispensable.

---

## 4. Priorité — 3 ajouts qui changent le plus la justesse de tendance

Classés par impact sur le nombre de cellules dont la vague devient suivable.

**P1 — Requête Tech-IA (débloque Nasdaq + une partie de S&P).**
`Nvidia OR semiconductor OR AI chips OR Microsoft OR Apple OR earnings guidance OR data center capex`
+ RSS Google News dédié `gnews_tech_ai`. **Alimente enfin `sentiment_ia_megacaps`.** Impact : la plus grosse vague directionnelle du marché devient pilotable côté news → meilleurs pivots 7j/1m sur Nasdaq.

**P2 — Requête Volatilité / Risk-off (débloque VIX + protège tous les indices).**
`war OR escalation OR sanctions OR selloff OR risk-off OR market crash OR financial crisis OR geopolitical`
+ RSS `gnews_riskoff`. **Alimente `tension_geopolitique_active` (VIX) et le GATE régime extrême (Nasdaq/S&P).** Impact : on capte la vague de peur AVANT le doublement du VIX, et on coupe/retourne les indices au bon moment.

**P3 — Durcir la requête #5 indices (transformer du bruit en driver).**
Remplacer `Nasdaq OR S&P 500 OR CAC 40 OR DAX` (compte-rendu) par des drivers :
`stock market selloff OR Fed rate stocks OR earnings season OR tech megacap OR market correction OR rally`
Impact : moins de faux flips « closes higher », plus de catalyseurs d'indices. À défaut, **baisser le poids/fiabilité de #5** pour qu'elle ne génère plus de signaux directionnels.

> Note coût : ces 3 ajouts = +2 requêtes structurées et +2 RSS Google News (même mécanique éprouvée que `gnews_copper`/`gnews_coffee`, ~100 items/requête). Marginal sur le budget GNews. **Anti-timeout du système non concerné** (ingest est borné).

---

## 5. Verdict final

**Le set actuel sert un trend-follower de commodités — PAS un trend-follower d'indices/volatilité.**

- **OUI** sur 7 actifs (Brent, Cuivre, Café, Cacao, Blé + partiellement Or/Argent) : requêtes pleines de **catalyseurs durs** qui créent de vraies vagues. C'est du bon travail (les requêtes dédiées #7-11 de l'audit 30/05 ont corrigé les commodités).
- **NON** sur **Nasdaq et VIX** : deux fiches déclarent un critère news, **aucune requête ne l'alimente** → critère muet, vague non suivie, **retournements ratés**. C'est la cécité la plus chère pour un spéculateur 7j/1m.
- **FAIBLE** sur **S&P 500 et EUR/USD** : couverts par du compte-rendu (#5) et de la macro indirecte, peu de drivers propres.

**Chiffré** : sur 12 actifs, **~5 pleinement servis, 4 partiels, 3 mal/non servis (Nasdaq, VIX, S&P)**. La requête #5 (indices) est aujourd'hui **génératrice nette de bruit**. **Les 3 ajouts P1-P3 feraient passer la couverture utile de ~58 % à ~92 %** sans toucher au moteur ni au budget.

### Handoff

- **Action immédiate** : ajouter P1 + P2 dans `STRUCTURED_QUERIES` + 2 RSS dans `EARLY_SIGNAL_FEEDS` ; arbitrer P3 (réécrire ou dé-pondérer #5). Validation Thomas requise (modif requêtes = pas de modif silencieuse, cf. garde-fous).
- **À mesurer en shadow** : taux de déclenchement de `sentiment_ia_megacaps` (Nasdaq) et `tension_geopolitique_active` (VIX) avant/après — doivent passer de ~0 à non-nul.
- **Dépend de** : prompt DeepSeek doit savoir classer L1=Tech-IA et L1=Géopolitique (déjà prévu dans les fiches) ; flag `nature` Phase 2 fera le tri anti-bruit en aval.
