# Sourcing des capteurs pré-câblés sans donnée — investigation & recommandations

> Date : 2026-06-02 · Agent : @fullstack
> Contexte : 3 capteurs sont déclarés dans les fiches YAML mais tombent systématiquement
> en `n/a` faute de source alimentée. Investigation des sources GRATUITES & FIABLES,
> sous garde-fou **« zéro invention de données »** (CLAUDE.md commandement 2).
>
> **MAJ 2026-06-02 (décisions Thomas appliquées)** :
> - **Breadth** → CÂBLÉ via proxy participation **RSP/SPY** (S&P) et **QQQE/QQQ**
>   (Nasdaq). **CAC reste n/a** (pas d'ETF equal-weight gratuit évident).
> - **FedWatch** → reste **n/a** : investigation ZQ gratuit refaite, **aucune source
>   gratuite propre et fiable en production** (cf. §1 mis à jour). Pas de câblage.
> - Caixin PMI → inchangé (statu quo, hors périmètre de cette session).
>
> Contexte d'origine (2026-06-02, avant décisions) : les 3 capteurs étaient en
> `n/a` faute de source gratuite *propre et nette* par API.

---

## 1. FedWatch — `fedwatch_proba` (EUR/USD, poids 6)

**Besoin** : probabilité implicite d'un mouvement de taux Fed (cut/hike) au prochain FOMC,
dérivée des **30-Day Fed Funds futures (ZQ)**. Normalisation `lineaire`, centre 0,5.
Symptôme actuel : `SKIP_COUNTER["lineaire_unmapped:fedwatch_proba"]` (non mappé).

| Source | Coût | Fiabilité | Faisabilité |
|---|---|---|---|
| **CME FedWatch API officielle** | **25 $/mois** (payant) | Très haute (source de référence du marché, EOD + intraday, historique depuis 2015) | REST + OAuth2 — facile à câbler mais **payant** |
| Tool web CME (gratuit) | 0 € | Haute | **Pas d'API** : page HTML/JS dynamique → scraping fragile, anti-bot probable → non fiable |
| Lib `pyfedwatch` (GitHub, ARahimiQuant) | 0 € (code) | Méthodo correcte (réimplémente le calcul CME depuis les prix ZQ) | **Nécessite les prix ZQ** (Fed Funds futures par échéance) — **pas disponibles** dans l'infra Twelve actuelle (plan Grow, futures ZQ non listés) ; logique de calcul à valider/tester |

**Reco** : pas de source gratuite *propre* par API. Deux voies, à trancher par Thomas :
- **(A)** Souscrire l'API CME FedWatch (25 $/mois) → câblage trivial, donnée de référence. *Coût récurrent à valider — le projet est à coût infra 0 € aujourd'hui.*
- **(B)** Recalculer via `pyfedwatch` SI on obtient les prix ZQ gratuits (à sourcer : ZQ disponible sur certains feeds gratuits ?). Effort non trivial + validation méthodo.
- **(C)** Laisser `n/a` (statu quo) — le capteur ne pèse que 6 sur EUR/USD ; le gate de couverture S5 absorbe son absence.

**→ DÉCISION (2026-06-02) : option (B) investiguée, ÉCHEC → reste n/a (C).**

Investigation ZQ gratuit refaite (WebSearch + revue de l'infra) :

| Piste ZQ gratuit | Verdict |
|---|---|
| **Twelve Data** (infra actuelle) | Pas de futures ZQ sur le plan Grow (déjà constaté ; futures non listés) |
| **NY Fed Markets API** (markets.newyorkfed.org) | Expose EFFR / repo / SOMA — **pas les prix futures ZQ** (taux réalisés, pas l'implicite forward) |
| **FRED** | Aucune série ZQ ni « Fed funds futures implied rate » — seulement FEDFUNDS/EFFR réalisés (inutiles pour la proba forward) |
| **Databento** (ZQ dispo) | 125 $ de crédits offerts puis **payant** — pas une source gratuite stable |
| **FirstRate Data** | « 1 mois de mises à jour gratuites » puis payant — pas une API |
| **Yahoo `ZQ=F`** (via yfinance) | Existe, **mais yfinance est bloqué sur les runners CI** (IP datacenter, constat projet récurrent) → **non fiable en production** |
| **CME FedWatch API** | Référence du marché mais **25 $/mois (payant)** |

**Constat** : aucune source ZQ **gratuite, propre et fiable en environnement de
production** (CI GitHub Actions). La seule techniquement « gratuite » (Yahoo
`ZQ=F`) tombe sous le blocage yfinance des runners → ne pas s'y reposer. Conforme
au garde-fou « zéro invention » : **`fedwatch_proba` laissé n/a, non câblé.**

**→ RESTE À TRANCHER PAR THOMAS** : (A) payer l'API CME FedWatch 25 $/mois (câblage
trivial, donnée de référence) ; ou (C) statu quo n/a (poids 6 sur EUR/USD,
absorbé par le gate de couverture S5 ; le canal news capte les décisions Fed).
*Recommandation : (C) tant que le projet reste à coût infra 0 € ; basculer en (A)
si FedWatch devient un critère bloquant pour la qualité directionnelle EUR/USD.*

---

## 2. Breadth `% constituants > MA50` — `breadth_sp_ma50`, `breadth_nasdaq100_ma50`, `breadth_cac_ma50`

**Besoin** : pourcentage de composants de l'indice au-dessus de leur MA50. Normalisation
`lineaire`, centre 50. Symptôme actuel : `SKIP_COUNTER["no_breadth_data:breadth_*"]`
(handler renvoie `n/a` explicite — aucun vrai breadth).

| Source | Coût | Fiabilité | Faisabilité |
|---|---|---|---|
| **Vrai breadth (S5FI / $SPXA50R)** sur StockCharts / Barchart / TradingView / MacroMicro | 0 € en consultation web | Haute (indices officiels) | **Pas d'API libre** : web/charts, pas de feed JSON gratuit stable → scraping fragile |
| **Calcul propre maison** (fetch des ~500 constituants S&P + MA50 chacun) | 0 € en théorie | Haute | **Non faisable** sous le rate-limit Twelve (plan Grow ~55 RPM) : 500 séries/run × 3 indices = explosion du budget API ; CAC 40 jouable (40 titres) mais S&P/Nasdaq non |
| **Proxy RSP/SPY** (ratio equal-weight ÷ cap-weight) | 0 € | Moyenne — **proxy**, pas la vraie métrique : ratio en baisse = breadth qui se dégrade (rallye porté par les méga-caps) | **Facile** : RSP et SPY déjà fetchables via `fetch_twelve_series` ; z-score du ratio. Mais **change la sémantique** (ratio momentum ≠ % > MA50) → recalibrer centre/échelle/signe |

**Reco** : pas de vraie source gratuite par API ; le seul chemin gratuit *propre* est le
**proxy RSP/SPY**, qui est un **proxy à valider** (sémantique différente du `% > MA50`).
Conforme au brief, **non câblé** (le brief exige une décision Thomas avant tout proxy).
- Pour le **CAC 40** uniquement, un vrai breadth maison est techniquement envisageable
  (40 titres, budget API tenable) — mais asymétrique avec S&P/Nasdaq qui resteraient en proxy.

**→ DÉCISION (2026-06-02) : OUI au proxy → CÂBLÉ pour S&P et Nasdaq ; CAC reste n/a.**

Implémentation :
- `breadth_sp_ma50` → ratio **RSP/SPY** (equal-weight / cap-weight S&P 500).
- `breadth_nasdaq100_ma50` → ratio **QQQE/QQQ** (equal-weight / cap-weight Nasdaq-100).
- Fiches migrées de `lineaire` centre-50 vers **`zscore`** (le ratio ~0.x rend le
  centre-50 caduc), `zscore_window: 60`, `zscore_div: 2`, **`signe: +1`** : ratio
  EW/CW en hausse = participation large (rallye sain) = haussier pour l'indice ;
  en baisse = rallye porté par les méga-caps (breadth qui se dégrade) = baissier.
- `source` mise à jour (« proxy RSP/SPY » / « proxy QQQE/QQQ ») + commentaire fiche
  rappelant que **ce n'est pas le vrai % >MA50**.
- Câblage : `TWELVE_SYMBOLS` mappe les 2 clés vers des tuples `(EW, CW)` ; le
  dispatch zscore route `breadth_*` vers `_twelve_ratio_zscore` (réutilise le
  helper ratio existant, retry/cache/rate-limit hérités). Si une patte du ratio
  manque → `None` (n/a propre, absorbé par le gate S5). Tests : S&P (z>0 quand RSP
  surperforme), Nasdaq (z<0 quand QQQ surperforme), patte manquante → n/a, CAC n/a.

- **CAC 40** : **reste n/a**. Pas d'ETF CAC equal-weight gratuit évident pour un
  proxy ratio symétrique ; calcul maison (40 titres × MA50) jouable côté budget API
  mais asymétrique avec S&P/Nasdaq en proxy → non câblé (handler `no_breadth_data`).

---

## 3. Caixin PMI Chine — `caixin_pmi_manuf` (cuivre, pétrole, argent ; poids 12 sur cuivre)

**Besoin** : indice PMI manufacturier Caixin/S&P Global, mensuel (1er jour ouvré du mois).
Fenêtre d'activation déjà câblée (`is_in_activation_window` : jours 1-9 du mois).
Normalisation `lineaire`, centre 50. Symptôme actuel : valeur absente (pas de fetcher).

| Source | Coût | Fiabilité | Faisabilité |
|---|---|---|---|
| **S&P Global PMI** (press releases officiels) | 0 € en lecture | Haute (source officielle) | **Pas d'API gratuite** : communiqués HTML mensuels → scraping fragile, structure non garantie |
| Trading Economics / Investing.com / MQL5 / MacroMicro | freemium | Haute | API **payante** (Trading Economics : plan commercial) ; web sinon |
| Cbonds (index 29795) | payant (add-in Excel) | Haute | Pas d'API gratuite programmatique |
| FRED | — | — | **Caixin PMI absent de FRED** (FRED expose des PMI US/ISM, pas le Caixin Chine) |

**Reco** : **aucune API gratuite officielle**. La donnée est mensuelle (12 points/an) et
très médiatisée → une **alternative honnête, déjà dans l'architecture, existe** : le
capteur est **partiellement couvert par les news** (le GATE cuivre contient déjà les
mots-clés `caixin`/`pmi`/`chine` dans `_GATE_KEYWORDS["cuivre"]`, et la publication PMI
est captée par DeepSeek comme event directionnel). Le critère numérique `caixin_pmi_manuf`
reste donc `n/a`, mais le **signal n'est pas totalement perdu** (canal news).
- Option propre la moins coûteuse : **saisie manuelle mensuelle** d'1 valeur (1×/mois)
  dans un petit fichier de config versionné (12 valeurs/an) — *mais c'est une donnée
  saisie à la main, hors périmètre « source automatique fiable », à valider par Thomas*.

**→ DÉCISION REQUISE** : « Pour le Caixin PMI : (A) laisser n/a et s'appuyer sur le canal
news DeepSeek (statu quo), (B) saisie manuelle mensuelle versionnée (12 valeurs/an), ou
(C) souscrire une API payante (Trading Economics) ? »

---

## Synthèse décisionnelle

| Capteur | Source gratuite propre par API ? | Câblé ? (MAJ 2026-06-02) | Statut |
|---|---|---|---|
| `fedwatch_proba` | Non (ZQ gratuit investigué : Twelve/NYFed/FRED/Databento/Yahoo→tous KO en prod ; CME = 25 $/mois) | **Non** | Reste n/a — décision Thomas : payer CME (A) ou n/a (C) |
| `breadth_sp_ma50` | Proxy **RSP/SPY** (participation EW/CW) | **OUI** (zscore, signe +1) | Câblé + testé |
| `breadth_nasdaq100_ma50` | Proxy **QQQE/QQQ** (participation EW/CW) | **OUI** (zscore, signe +1) | Câblé + testé |
| `breadth_cac_ma50` | Non (pas d'ETF CAC equal-weight gratuit évident) | **Non** | Reste n/a (documenté) |
| `caixin_pmi_manuf` | Non (S&P Global = communiqués ; pas d'API gratuite ; absent FRED) | **Non** | Hors périmètre session — statu quo n/a + canal news |

**Garde-fou respecté** : breadth câblé **uniquement** via proxy validé par Thomas
(sémantique explicitement documentée « pas le vrai % >MA50 »). FedWatch + CAC + Caixin
laissés `n/a` honnêtes (absorbés par le gate de couverture S5) plutôt qu'une fausse
donnée. Aucune valeur en dur, aucune source douteuse forcée.
