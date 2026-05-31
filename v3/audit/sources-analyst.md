# Audit stratégique du sourcing — TradingApp v3
> Date : 2026-05-31 · Périmètre : 12 actifs × 3 horizons

---

## 1. Matrice de couverture par actif

Règle de lecture : **alimentable** = source câblée ou fonctionnelle (EIA, CFTC, Twelve Data, Open-Meteo/NOAA, Google News RSS, GNews/NewsAPI). **n/a** = source mentionnée dans la fiche mais non câblée, manquante ou bloquée (WGC, ICE, LME/SHFE, COMEX, USDA WASDE/NASS/FAS, GASC, Eurostat, Caixin, AAII, CME FedWatch, ports CI, CBOE, FRED).

| Actif | Critères scorables | Alimentables | n/a (source manquante) | Couverture |
|---|---|---|---|---|
| Pétrole (Brent) | 10 | 6 (EIA×2, CFTC, Twelve Data×3) | 4 (API Weekly, Caixin, Cushing indirect) | **FORTE** |
| Or | 8 | 4 (CFTC, Twelve Data×2, events-log) | 4 (FRED TIPS, WGC×2, flux ETF) | **MOYENNE** |
| Argent | 9 | 4 (CFTC, Twelve Data×3) | 5 (FRED TIPS, COMEX, flux ETF SLV, Caixin, rapports industrie) | **MOYENNE** |
| Cuivre | 8 | 4 (CFTC, Twelve Data×2, events-log) | 4 (Caixin, LME/SHFE, term struct, gnews RSS) | **MOYENNE** |
| Café (Arabica) | 8 | 4 (CFTC, Twelve Data×2, gnews RSS) | 4 (NOAA/météo Brésil, ICE stocks, CONAB calendrier, météo Vietnam) | **FAIBLE** |
| Cacao | 9 | 4 (CFTC, Twelve Data, events-log, gnews RSS) | 5 (NOAA météo CI+GH, ports Abidjan/San Pedro, ICE options, grindings ECA/NCA, EUDR) | **FAIBLE** |
| Blé | 9 | 4 (CFTC, Twelve Data, events-log, gnews RSS) | 5 (USDA WASDE/NASS/FAS, NOAA drought, BoM météo AU, GASC) | **FAIBLE** |
| S&P 500 | 9 | 6 (Twelve Data×4, CFTC, events-log) | 3 (FRED HY OAS, AAII, Shiller CAPE/fournisseur) | **FORTE** |
| Nasdaq | 9 | 7 (Twelve Data×5, CFTC, events-log) | 2 (FRED TIPS, flux ETF QQQ indirect) | **FORTE** |
| CAC 40 | 7 | 5 (Twelve Data×3, events-log, gnews RSS) | 2 (V2X disponible TD, flux ETF MSCI France) | **MOYENNE** |
| VIX | 8 | 5 (Twelve Data×2, CFTC, events-log) | 3 (CBOE P/C ratio, SKEW, VVIX — non câblés) | **MOYENNE** |
| EUR/USD | 8 | 6 (Twelve Data×4, CFTC, events-log) | 2 (FRED/Eurostat, CME FedWatch) | **FORTE** |

**Actifs structurellement sous-alimentés (FAIBLE)** : Café, Cacao, Blé. Leurs critères de poids les plus élevés (météo production, stocks exchange, arrivées port) sont précisément les non-câblés. Google News RSS compense en surface mais ne produit pas de valeur numérique normalisable — il alimente le `events-log`, pas les critères quantitatifs.

---

## 2. Équilibre du sourcing — déséquilibres identifiés

**Concentration Twelve Data** : présent dans 11 actifs sur 12 (tous sauf Café en primaire). Fournit DXY, TIPS via calcul, VIX, spreads, breadth, ratios. Si Twelve Data tombe → 40-60 % des critères scorables des actifs FORTE deviennent n/a en temps réel.

**Concentration macro US / indices US** : SP500, Nasdaq, VIX et EUR/USD captent ~80 % des impacts détectés dans le run de test (SP500 : 56, Nasdaq : 40, BRENT : 41, GOLD : 40 vs CAC : 3, COPPER : 3, WHEAT : 0, COFFEE : 0, COCOA : 0). Les feeds RSS (BBC, CNBC, Investing) sont calibrés US-macro par construction — les actifs agri et cuivre sont quasi invisibles.

**Agrégateurs dominants pour actifs sous-couverts** : Café, Cacao, Blé, Cuivre reposent sur Google News RSS (weight 0.8) et GNews/NewsAPI (weight 0.7) comme seules sources news dédiées. Ce sont des agrégateurs bruités, sans données de marché primaires.

**Redondance productive** : CFTC câblé sur 8 actifs — redondance utile (source primaire officielle, hebdo). EIA câblé sur pétrole uniquement — bien ciblé.

---

## 3. Fiabilité et dette technique

**Google News RSS** : robuste pour la livraison (HTTP 200 confirmé), mais : (1) résultats variables selon les termes de recherche, (2) aucune API officielle — Google peut modifier le format sans préavis, (3) pas de données numériques exploitables pour les critères de type zscore. Traiter ces flux comme `events-log` uniquement, jamais comme source de critère quantitatif.

**GNews/NewsAPI free tier** : plafond commun ~100 req/j. À 3 cycles/j × 11 requêtes STRUCTURED_QUERIES = 33 req/j théoriques. Marge confortable (~67 % headroom) — mais si les cycles passent à 6/j ou si les requêtes sont doublées, le plafond est atteint. Pas de risque immédiat, risque latent à monitorer.

**Sources primaires manquantes par famille critique** :
- Agri : USDA ERS/WASDE, NOAA Drought Monitor, ICE Futures — toutes bloquaient en 403/404 avec UA navigateur selon le commentaire du code. Voie alternative à creuser : USDA ERS propose des fichiers CSV/JSON téléchargeables sans auth pour WASDE.
- Métaux : LME et SHFE bloquent. Alternative : Quandl/Nasdaq Data Link (accès LME gratuit limité) ou Metals API (freemium).
- CBOE (VIX) : P/C ratio, SKEW, VVIX disponibles en CSV sur cboe.com/data — sans authentification, parsing HTML/CSV.
- FRED : API gratuite (clé simple), donne TIPS, HY OAS, fed funds futures — intégration directe simple, aucune raison de ne pas câbler.

---

## 4. Quotas et coût

| Source | Plafond free | Conso actuelle (~3 cycles/j) | Headroom | Risque |
|---|---|---|---|---|
| GNews | ~100 req/j | 33 req/j | 67 % | Faible, surveiller |
| NewsAPI | ~100 req/j | 33 req/j (partagés) | 67 % | Faible, surveiller |
| Google News RSS | Illimité (non officiel) | ~25 req/j | Confortable | Rupture silencieuse possible |
| Twelve Data (free) | 800 req/j ou 55/min | Estimé <200 req/cycle | OK | Dépendance critique sur pannes |
| FRED | Illimité (clé gratuite) | 0 (non câblé) | — | Opportunité manquée |
| EIA API | Illimité | Câblé pétrole | OK | — |
| CFTC | Illimité (CSV public) | Câblé 8 actifs | OK | — |

---

## 5. Stratégie de sourcing cible

**Mix cible par actif** : 2 sources primaires (API officielle + API marché) + 1 flux RSS spécialisé + GNews/NewsAPI pour event detection. Les actifs FORTE sont proches de cette cible. Les actifs FAIBLE n'ont que la moitié gauche (RSS/news) sans la moitié droite (APIs de données de marché).

**Nombre de sources minimal viable** : 3 sources câblées par actif dont au moins 1 source primaire numérique (pas RSS). En dessous, le critère le plus pondéré de la fiche reste à n/a en permanence et le score est structurellement incomplet.

---

## 5 priorités de sourcing

**P1 — Câbler FRED (API gratuite, clé simple)** : TIPS, HY OAS, fed funds probas. Débloque 2-3 critères sur Or, Argent, Nasdaq, S&P 500, EUR/USD. ROI maximal pour effort minimal.

**P2 — Câbler CBOE CSV (sans auth)** : P/C ratio, SKEW, VVIX en téléchargement direct. Débloque 3 critères VIX — actif aujourd'hui à MOYENNE par manque de ces seuls signaux.

**P3 — Câbler USDA ERS/PSD Open Data** : fichiers JSON publics (pas d'auth, pas de 403). Débloque WASDE stocks-to-use (Blé poids 11) et FAS imports (Blé poids 5). Remonte Blé de FAIBLE à MOYENNE.

**P4 — Ajouter Open-Meteo API pour agri (Brésil, Vietnam, CI, Ghana, Australie)** : API REST gratuite, sans auth, précipitations et température par coordonnées. Débloque Café météo Brésil (poids 11), Café météo Vietnam (poids 4), Cacao météo CI+Ghana (poids 11), Blé drought proxy (poids 9). Remonte potentiellement Café et Cacao de FAIBLE à MOYENNE/FORTE.

**P5 — Diversifier pour réduire la mono-dépendance Twelve Data** : ajouter Yahoo Finance API (non officielle mais stable) ou Alpha Vantage (500 req/j gratuit) comme fallback pour DXY, spreads, VIX. Si Twelve Data tombe, les actifs FORTE dégradent brutalement.

---

**Risque systémique n°1 : mono-dépendance Twelve Data**
Si Twelve Data est indisponible (panne, quota, changement de plan), 6 actifs sur 12 perdent simultanément 50-70 % de leurs critères scorables — dont tous les actifs cotés FORTE. Un fallback sur une seconde API marché (Alpha Vantage ou Yahoo Finance) est le garde-fou le plus urgent architecturalement.

- Open-Meteo est déjà dans la stack (câblé selon les sources vérifiées) : l'étendre aux coordonnées agri (Brésil, Vietnam, CI) est un delta mineur pour un impact majeur sur Café et Cacao.
- Les actifs agri (Café, Cacao, Blé) sont aujourd'hui dépendants de Google News RSS pour leurs critères de poids maximal — un agrégateur, pas une source primaire. C'est de la dette analytique, pas juste de la dette technique.
- FRED et CBOE sont des opportunités gratuites laissées sur la table : ils débloquent ~8 critères n/a sans aucun coût ni risque de quota.
