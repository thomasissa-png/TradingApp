# Sourcing des capteurs pré-câblés sans donnée — investigation & recommandations

> Date : 2026-06-02 · Agent : @fullstack
> Contexte : 3 capteurs sont déclarés dans les fiches YAML mais tombent systématiquement
> en `n/a` faute de source alimentée. Investigation des sources GRATUITES & FIABLES,
> sous garde-fou **« zéro invention de données »** (CLAUDE.md commandement 2).
>
> **Décision transverse : AUCUN des 3 n'a de source gratuite *propre et nette*
> par API. Aucun n'a donc été câblé.** Chacun requiert un arbitrage de Thomas
> (accepter un proxy / payer une API / laisser n/a). Voir reco par capteur.

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

**→ DÉCISION REQUISE** : « Payer 25 $/mois l'API CME FedWatch (A), investiguer une source ZQ gratuite pour pyfedwatch (B), ou laisser n/a (C) ? »

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

**→ DÉCISION REQUISE** : « OK pour câbler le proxy **RSP/SPY** sur S&P (et un équivalent
QQQ-equal-weight type QQQE/SPY pour le Nasdaq) en remplacement du `% > MA50`, en
acceptant la sémantique proxy + recalibrage des seuils ? Ou laisser n/a ? »
*(Note : si OUI, le critère devra peut-être migrer de `lineaire` centre-50 vers `zscore`
du ratio, signe à recaler — la baisse du ratio = breadth qui se dégrade.)*

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

| Capteur | Source gratuite propre par API ? | Câblé ? | Décision requise |
|---|---|---|---|
| `fedwatch_proba` | Non (CME = 25 $/mois ; ZQ gratuit à sourcer pour pyfedwatch) | **Non** | A) payer CME · B) ZQ gratuit + pyfedwatch · C) n/a |
| `breadth_*_ma50` | Non (vrai breadth = web only ; calcul maison hors budget API) | **Non** | Proxy RSP/SPY (sémantique différente, recalibrage) OUI/NON ? |
| `caixin_pmi_manuf` | Non (S&P Global = communiqués ; pas d'API gratuite ; absent FRED) | **Non** | A) n/a + canal news · B) saisie manuelle mensuelle · C) API payante |

**Garde-fou respecté** : aucune valeur en dur, aucun proxy douteux câblé sans validation.
Mieux vaut 3 `n/a` honnêtes (absorbés par le gate de couverture S5) qu'une fausse donnée.
