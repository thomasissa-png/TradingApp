# #8 Or — enquête signe (bug ou régime ?)

> Auteur : @fullstack (Session 4). Branche `claude/elegant-ramanujan-OIKms`. Mode shadow.
> Mission : trancher si le SHORT Or est un **signe inversé** (vrai bug) ou le bon signe cassé par le **régime 2025** (calibration).
> Garde-fous : pas de modif silencieuse de signe/poids/seuil/prompt. Bug de signe → corrige. Calibration/régime → reco « À VALIDER THOMAS ».
> Sources : `v3/data/criteres-courants.md` (bloc `or:`) + `v3/data/decision-log/2026-06-05-1056.jsonl` + `v3/config/fiches/or.yml` + `v3/backtest/REPORT.md` + `backtest_quant.py`.

---

## TL;DR (verdict en 1 phrase)

**RÉGIME / CALIBRATION → À VALIDER THOMAS.** Le SHORT Or est piloté à ~60 % par le critère **taux réels TIPS**, dont le signe (`-1` : TIPS hauts → or baissier) est **macro-canonique et correctement câblé** ; ce n'est **PAS un bug de signe**. Le backtest qui « sent l'inversion » (1m 18.2 %) (a) **ne teste même pas TIPS** dans le run publié (FRED absent → poids 0), et (b) punit la relation canonique parce que **l'or a fait +70 % en 2025 MALGRÉ des taux réels au plus haut** — une rupture de régime, pas une erreur de code. Inverser le signe TIPS pour « matcher » le backtest serait un **overfit au régime 2025**.

---

## 1. Reconstitution du score Or (run 1056, decision-log)

Score pondéré reconstitué critère par critère = `signe × norm × poids × pertinence` (vérifié contre `contrib_pond`).

### Horizon 7j (score pondéré = **-4.63 → SHORT**)

| Critère | valeur | norm | signe | poids | pert. | contrib | sens |
|---|---|---|---|---|---|---|---|
| **Taux 10Y US réels (TIPS)** | 2.11 | +0.718 | **-1** | 12 | 1.0 | **-8.61** | SHORT |
| DXY trend 20j | 118.88 | -0.229 | -1 | 8 | 0.9 | +1.65 | LONG |
| CFTC COT nets | 149 660 | -0.432 | -1 | 6 | 0.7 | +1.82 | LONG |
| Flux ETF or 5j | ~0 | +0.092 | +1 | 5 | 1.0 | +0.46 | LONG |
| Tension géopolitique (news) | +1 | 1.0 | +1 | 5 | 0.4 | +1.20 | LONG |
| VIX risk-off | 14.95 | -0.763 | +1 | 3 | 0.5 | -1.14 | SHORT |
| Demande indienne | 0 | 0 | +1 | 3 | 0.3 | 0 | — |

**Part du TIPS dans la somme des |contributions| = 57.9 %.** Tous les autres critères « significatifs » poussent **LONG** (DXY, COT, flux, géopol) ; seul le TIPS (et un petit VIX bas) tire SHORT — mais le TIPS, à lui seul, écrase l'ensemble.

### Horizon 1m (score pondéré = **-3.79 → SHORT**)

Même structure : TIPS -8.61 (60 % du poids), DXY +1.47, COT +2.59, flux +0.32, géopol +0.90, VIX -0.46.

### Horizon 24h (score pondéré ≈ **-2.0 → SHORT**)

TIPS -4.31 (pertinence 0.5) + VIX -1.60 dominent ; même driver.

→ **Driver unique du SHORT sur les 3 horizons : le critère TIPS.** Sans lui, l'Or serait LONG net (cf. §4). Tout le reste de l'enquête se résume donc à : **le signe du TIPS est-il bon ?**

---

## 2. Vérification du SIGNE de chaque critère Or (comme OAT-Bund sur le CAC)

| Critère | signe fiche | logique macro canonique | verdict signe |
|---|---|---|---|
| **Taux réels TIPS** | **-1** | Taux réels hauts = coût d'opportunité élevé de détenir l'or (actif non rémunéré) = **baissier or**. C'est LA relation de manuel (Gibson's paradox / or vs real yields). | ✅ **CORRECT** |
| DXY trend 20j | -1 | Dollar fort = or (coté USD) plus cher pour le reste du monde = baissier or. Or norm<0 (DXY en repli 20j) × -1 = LONG. | ✅ CORRECT |
| CFTC COT nets | -1 | Signe **contrarian** assumé (fiche : « nets SHORT extrême → LONG squeeze »). Ici nets norm -0.43 (positionnement légèrement sous moyenne) × -1 = léger LONG. | ✅ CORRECT (contrarian voulu) |
| Flux ETF or 5j | +1 | Entrées ETF = demande = haussier or. | ✅ CORRECT |
| Tension géopolitique | +1 | Escalade = ruée vers le refuge = haussier or. | ✅ CORRECT |
| VIX risk-off | +1 | VIX haut = stress = haussier or refuge. Ici VIX 14.95 (bas) × +1 = SHORT (marché calme). | ✅ CORRECT |
| Demande indienne | +1 | Saison mariages/Diwali = haussier. | ✅ CORRECT |

**Aucun signe inversé.** Contrairement au cas que je cherchais (un OAT-Bund mal câblé aurait été un bug net), **tous les signes Or sont macro-corrects**. Le signe TIPS = -1 est le signe de manuel, identique à ce qu'un desk macro câblerait.

---

## 3. Pourquoi le backtest « sent » l'inversion (1m 18.2 %) — et pourquoi c'est trompeur

Deux faits techniques tuent l'hypothèse « bug de signe » :

### 3.a — Le backtest publié NE TESTE PAS le TIPS

`v3/backtest/REPORT.md` (« Limite majeure », l.27-38) : le run a tourné **sans `FRED_API_KEY`**. Conséquence directe : `taux_10y_us_reels_tips` (= `DFII10`), `dxy_trend_20j` (= `DTWEXBGS`) et les spreads FRED sont tombés en **n/a (poids 0)**. Le scénario d'ablation `+FRED == price-only` le prouve.

→ Le **18.2 % de GC=F 1m vient de COT + price-only**, PAS du critère TIPS. **On ne peut littéralement pas accuser le signe TIPS sur la foi de ce backtest** : le critère était débranché. Le REPORT note lui-même que +COT **dégrade** l'accuracy (48.4→47.4 %), cohérent avec un COT noncomm contrarian bruité en directionnel court — c'est ça que punit l'or backtest, pas le TIPS.

### 3.b — Le backtest est news-blind et le régime 2025 a cassé la relation or/taux réels

`backtest_quant.py` (l.226, 367-369) : **GATE toujours False, triplets toujours None** → géopolitique, refuge, achats banques centrales = **invisibles** au backtest. Or c'est exactement ce qui a porté l'or en 2025.

Donnée mesurée (yfinance GC=F) :
- **Or fin 2024 → juin 2026 : +69.9 %** ; **+62.7 % sur l'année 2025 seule.**
- Pendant ce temps, **taux réels TIPS au plus haut (z = +2.11)**.

C'est une **rupture de régime documentée** : en 2025 l'or a violemment monté *malgré* des taux réels élevés (moteurs : dédollarisation, achats massifs banques centrales/PBoC, prime géopolitique, refuge). La corrélation historiquement négative or/taux-réels s'est **découplée**. Un backtest **price-only / news-blind** qui ne voit que « TIPS hauts » (s'il était branché) ou que « le prix monte » price donc un signe canonique correct comme « faux » — c'est l'artefact classique d'un edge évalué dans le mauvais régime.

### 3.c — Le test décisif : qu'arriverait-il si on « corrigeait » le signe TIPS ?

Si on inversait `signe: -1 → +1` sur le TIPS (le « fix » que suggère naïvement le backtest) :

| Horizon | score actuel | score si signe TIPS inversé |
|---|---|---|
| 7j | -4.63 (SHORT) | **+12.59 (LONG fort)** |
| 1m | -3.79 (SHORT) | **+13.44 (LONG fort)** |

Cela aurait matché le réel 2025 haussier… mais en **inversant la macro de manuel** et en **overfittant un seul régime exceptionnel**. Le jour où les taux réels redeviennent le moteur dominant de l'or (régime normal), ce signe inversé serait catastrophiquement faux. **C'est précisément le piège que le garde-fou « ne touche pas si c'est le régime » protège.**

---

## 4. Réconciliation des deux indices contradictoires

| Indice | Lecture naïve | Lecture après enquête |
|---|---|---|
| **Backtest** : Or 1m 18.2 %, 24h 42.8 % | « signe inversé » | (a) TIPS débranché dans ce run (FRED n/a) → le 18 % ne juge PAS le TIPS ; (b) news-blind sur or 2025 +70 % → **punit un signe correct via rupture de régime**. |
| **News Trader live** : Or SHORT « **discutable** » (pas « à l'envers ») | arbitrage inconfortable | **Exactement juste.** Le desk valide la macro taux-réels (signe correct) mais signale que la géopol-refuge peut décorréler l'or. C'est de la **pondération régime**, pas un bug. |

Les deux indices **convergent** une fois décodés : il n'y a **pas** de signe inversé. Il y a un **critère TIPS au signe correct mais surdimensionné dans un régime (2025) où la relation or/taux-réels est cassée**, et une **prime géopolitique-refuge sous-pondérée**. C'est l'hypothèse (b) + (c) du brief, pas (a).

---

## 5. Verdict

### 🟢 PAS DE BUG DE SIGNE — RÉGIME / CALIBRATION → À VALIDER THOMAS

- Le signe TIPS (`-1`) est **macro-canonique et correctement câblé**. Tous les autres signes Or sont corrects. **Aucune correction de code appliquée** (garde-fou respecté : pas de modif silencieuse de signe).
- Le SHORT Or est **macro-défendable** (taux réels au plus haut) mais **fragile** parce qu'il repose à ~60 % sur un seul critère dont la relation directionnelle s'est **découplée en 2025** (or +70 % malgré TIPS hauts), et parce que la **prime géopolitique-refuge** (poids 5, pertinence 0.3-0.5) est trop faible pour contrebalancer.
- Le backtest 18.2 % **ne prouve PAS l'inversion** : il teste un or price-only/news-blind sans TIPS branché, dans un régime haussier exceptionnel.

### Recos À VALIDER THOMAS (ticket C / calibration — PAS appliquées)

1. **[Calibration régime, ticket C]** Le poids 12 + pertinence 1.0 du TIPS en font le maître absolu de l'Or sur 7j/1m. Dans un régime or-refuge/dédollarisation, c'est trop. Pistes (à trancher sur mesures réelles, pas à l'aveugle) : (a) abaisser `pertinence[7j/1m]` du TIPS sur l'or, OU (b) relever le poids/pertinence de `tension_geopolitique` (refuge) et `achats_pboc_cb_emergentes` (actuellement n/a — source WGC à câbler). Ne PAS toucher le **signe**.
2. **[Re-run backtest avec `FRED_API_KEY`]** Obligatoire avant toute conclusion sur le TIPS : le run publié ne teste pas FRED. Tant que ce re-run n'a pas tourné, **aucune affirmation sur la qualité directionnelle du signe TIPS n'est statistiquement fondée**.
3. **[Détecteur divergence quant↔news `↯`]** L'Or porte déjà `↯` (taux-réels SHORT vs géopol LONG) sur les 3 horizons : le piège est **déjà signalé** au trader humain. Le faire **modifier la conclusion** (cap/abstention quand `↯` + mono-driver) relève du **Lot 4b** (reporté par le fondateur). Même décision que B1/CAC : ne PAS réactiver.

### Impact décision : **NON.**

Rien n'est modifié dans le scoring, les signes, les poids ou les seuils. Le bulletin Or reste **SHORT** (inchangé). Le `↯` et le drapeau 📰 signalent déjà la fragilité. Tout est en reco pour arbitrage Thomas (ticket C, ~23/06, sur vraies mesures + re-run FRED).
