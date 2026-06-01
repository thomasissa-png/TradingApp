# Audit données réelles + Scoping backtest quantitatif
> Angle : rigueur statistique / mesure / faisabilité. Date : 2026-06-01.
> Données sources : `performance.md`, `performance-ab.md`, 19 decision-logs (30/05→01/06), 4 fichiers prix-émission, `audit-data.md`.

---

## PARTIE 1 — Audit honnête des données réelles

### 1.1 Significativité statistique : que peut-on RÉELLEMENT affirmer ?

**Verdict brutal : rien de statistiquement affirmable à ce stade. Zéro.**

#### État des faits (01/06/2026)

- **N_eff = 0/12 cellules** pour la fenêtre non-chevauchante (seuil : 15 obs indépendantes).
- **4 cellules avec N_eff = 1** (Café, Cuivre, Or, Pétrole) — une seule observation chacune.
- **8 cellules avec N_eff = 0** (Argent, Blé, CAC, Cacao, EUR/USD, Nasdaq, S&P, VIX) — prix trop stables pour franchir le seuil.
- Horizon 7j et 1m : zéro mesure terminée (les premières échéances tombent fin mai–fin juin 2026).

#### Calcul de l'intervalle de confiance Wilson sur N=1

Pour N=1 et k succès, la formule Wilson 95% donne :

```
N=1, k=1 (VRAI) : IC Wilson = [0.206 ; 1.000] → borne basse 20.6%
N=1, k=0 (FAUSSE) : IC Wilson = [0.000 ; 0.794] → borne haute 79.4%
```

**Interprétation** : la borne basse 20.6% (meilleur cas, Or et Pétrole) est très en dessous du seuil opérationnel de 70%. Même les deux succès observés ne permettent pas d'affirmer quoi que ce soit. La borne basse doit dépasser 50% pour déclencher l'éligibilité — cela nécessite au minimum N≈10 avec 100% de réussite, ou N≈30 avec 77%+ (cf. table Wilson).

#### Puissance statistique : calcul

Pour détecter un taux réel de 70% contre l'hypothèse nulle H₀=50% (coin flip), avec α=0,05 unilatéral et puissance β=0,80 :

```
n_min = ((z_α × √(0.5×0.5) + z_β × √(0.7×0.3)) / (0.7 − 0.5))²
      = ((1.645 × 0.500 + 0.842 × 0.458) / 0.20)²
      ≈ ((0.823 + 0.386) / 0.20)²
      ≈ (6.04)²
      ≈ 37 observations indépendantes
```

**Avec 1 observation, la puissance est ~5% — équivalente à un pile ou face.** On ne peut pas distinguer un edge réel du bruit à N=1.

#### Table de référence : N_eff nécessaire pour dire quelque chose

| N_eff | k succès | Wilson_low | Conclusion possible |
|---|---|---|---|
| 1 | 1 | 0.206 | Rien — warm-up |
| 10 | 10 | 0.697 | Limite éligibilité si 100% |
| 15 | 12 | 0.551 | Éligible si ≥80% |
| 30 | 24 | 0.622 | Éligible si ≥80% |
| 30 | 21 | 0.519 | Éligible si ≥70% + Wilson_low>50% |
| **37** | **26** | **~0.536** | **Puissance 80% pour détecter edge** |

**Conclusion de la section** : le système a 3 jours de mesures effectives. C'est normal et prévu. Ce qui n'est pas acceptable, c'est de tirer des conclusions directionnelles de type "le système prédit bien" sur la base de 2 VRAI sur 4 mesurables. L'intervalle de confiance réel englobe trivialement le hasard.

---

### 1.2 Biais LONG (médiane 61%, pics 72%) : signal structurel ou bruit ?

#### Données brutes des decision-logs analysés (30/05→01/06, run 2133)

Sur l'ensemble des 19 runs disponibles, décompte des conclusions `conclusion_pm1` :

**Run 2133 (01/06, dernier run, 36 lignes actif×horizon) :**

```
LONG : Argent (3h), CAC (3h), Cacao (3h), Café (3h), Nasdaq (3h),
        Or (3h), S&P (3h) → 7 actifs × 3 horizons = 21 LONG
SHORT : Blé (3h), Cuivre (3h), EUR/USD (3h), Pétrole 7j/1m,
         VIX (3h) → 15 SHORT
Ratio LONG : 21/36 = 58%
```

**Run 30/05-1316 (premier run disponible) :**
```
Argent 24h : SHORT / 7j : LONG / 1m : LONG
Blé : LONG (3h)
→ Blé LONG au premier run, SHORT au dernier = flip sur news (Mer Noire)
```

#### Diagnostic du biais LONG

Le biais LONG observé (58-72%) a **deux origines distinctes** qu'il faut séparer :

**a) Biais structurel des critères quant** : la plupart des actifs ont des critères asymétriques. Par exemple, `ratio_gold_silver` avec `valeur_normalisee = -1.0` et `signe = -1` contribue LONG pour l'argent quel que soit le niveau des taux. Le `CFTC COT Cocoa` négatif pousse LONG systématiquement. Les pertinences sont plus élevées sur les horizons longs, or les critères de tendance (COT, ratios) ont souvent un signe LONG en régime bull de matières premières (2025-2026).

**b) Biais de régime de marché** : fin mai 2026, les indices US (SPY/QQQ simulés) sont en hausse, l'or en territoire record, le pétrole en reprise. Un système de trend-following va naturellement produire plus de LONG dans un régime haussier global — ce n'est pas un bug, c'est la définition du trend-following.

#### La distinction cruciale : biais vs bruit

Avec 3 jours de runs, on ne peut pas séparer ces deux causes avec un test statistique. **Le biais 61% est-il un signal ou du bruit ?** Voici le calcul :

```
H₀ : P(LONG) = 0.50 (pas de biais)
Observation : sur ~19 runs × 36 cellules = ~684 prédictions observées,
si 61% LONG → 417 LONG, 267 SHORT.
Test binomial : p-value ≈ < 0.001 (très significatif à N=684)
```

**Mais attention** : ces 684 prédictions ne sont PAS indépendantes. Les 36 cellules d'un même run partagent le même régime de marché. L'autocorrélation temporelle (3 runs/jour, données similaires) réduit l'indépendance effective à ~19 runs × facteur de décorrélation entre actifs ≈ peut-être 50-70 observations vraiment indépendantes.

À N≈60 observations indépendantes avec 61% LONG : p-value ≈ 0.04-0.08 → **borderline**. On ne peut pas affirmer que c'est un vrai biais structurel vs un régime de marché haussier passager.

#### Risque opérationnel du biais LONG

Le risque concret est le suivant : si le biais LONG est purement de régime (marché haussier), il disparaîtra à la première correction. Le système émettra alors un signal LONG massif précisément quand le marché retourne. Pour un trader de turbos, un biais LONG en tête de retournement est **catastrophique** (les turbos baissiers sont la couverture naturelle).

**Alerte maintenue** : le seuil 70% LONG doit rester actif. Si le biais persiste à >65% sur 30 runs consécutifs, auditer les critères quant un par un pour identifier lesquels ont un biais intrinsèque indépendant du régime.

---

### 1.3 Le problème "non-conclusive" dominant : seuils bien calibrés ?

#### Données observées (run 31/05→01/06, 12 cellules 24h)

| Actif | Delta observé | Seuil | Résultat |
|---|---|---|---|
| Argent | -0.488% | 0.8% | non-conclusive |
| Blé | -0.390% | 0.8% | non-conclusive |
| CAC 40 | -0.449% | 0.5% | non-conclusive |
| Cacao | -0.613% | 1.5% | non-conclusive |
| Café | -2.061% | 1.0% | FAUSSE |
| Cuivre | +2.946% | 0.8% | FAUSSE |
| EUR/USD | -0.213% | 0.25% | non-conclusive |
| Nasdaq | +0.685% | 0.7% | non-conclusive |
| Or | -1.287% | 0.5% | VRAI |
| Pétrole | +4.305% | 1.0% | VRAI |
| S&P 500 | +0.378% | 0.4% | non-conclusive |
| VIX | +1.980% | 5.0% | non-conclusive |

**Bilan** : 7/12 non-conclusives (58%), 2 VRAI (17%), 2 FAUSSE (17%), 1 seul run mesuré.

#### Analyse par catégorie de seuil

**Seuils trop larges (jettent trop de mesures) :**

- **Cacao 1.5%** : le marché du cacao est volatil (vol historique ~2-3%/jour), mais exiger 1.5% sur 24h élimine ~50% des sessions. Un seuil à 1.0% serait plus calibrant.
- **VIX 5.0%** : le VIX peut rester stable des semaines entières, puis exploser. Un seuil à 5% fait que presque toutes les mesures 24h seront non-conclusives hors choc. En pratique, mesurer le VIX sur 24h est peu pertinent — l'horizon 7j serait plus adapté avec un seuil à 10%.
- **Argent 0.8%** : l'argent a une volatilité journalière historique ~1-2%. Le seuil 0.8% est raisonnable mais génère beaucoup de non-conclusives en régime calme.

**Seuils correctement calibrés :**

- **Café 1.0%** : franchit régulièrement (delta observé -2.06%), mesure conclusive.
- **Or 0.5%** : franchit facilement (delta -1.29%), bon équilibre signal/bruit.
- **Pétrole 1.0%** : franchit souvent (delta +4.3%), cohérent avec la volatilité OPEC.
- **EUR/USD 0.25%** : le forex est peu volatile au jour le jour, seuil bas approprié.

**Seuils à la limite (risque de jeter trop de mesures en régime calme) :**

- **CAC 0.5%** : le CAC bouge en moyenne 0.5-0.8%/jour. Un seuil à 0.5% est juste, mais en régime latéral il produit beaucoup de non-conclusives. Envisager 0.4% ou une mesure sur le range H/L plutôt que close/close.
- **Nasdaq 0.7%** : cohérent avec la volatilité ETF QQQ, mais les semaines calmes génèrent des non-conclusives.
- **S&P 0.4%** : idem, semaines calmes = silences.

#### Recommandation sur les seuils

Trois ajustements prioritaires, ordonnés par impact sur le taux de mesures conclusives :

1. **VIX** : passer le seuil de 5% à 3% pour 24h, et ajouter une mesure 7j avec seuil 10%. Le VIX 24h à 5% est actuellement une cellule morte.
2. **Cacao** : baisser de 1.5% à 1.0%. La volatilité intra-journalière justifie cette baisse.
3. **Argent** : maintenir 0.8% mais signaler que les semaines à faible volatilité produiront un taux de non-conclusives élevé (>60%) — ne pas paniquer.

**Important** : tout ajustement de seuil doit être fait AVANT l'accumulation de mesures pour éviter un biais de sélection rétrospective (on ne recalibre pas les seuils pour améliorer un taux déjà calculé).

---

### 1.4 Phase 2 news — T1 monte (13 au dernier run) : quoi mesurer maintenant vs dans 30 runs ?

#### État au run 2133 (01/06)

- `p2_T1_faux_flips_evites` : visible sur Cacao (T1=1 sur 3 horizons) — gate cap anti-inversion actif.
- `p2_T2_vrais_flips_qualifies` : 0 partout — aucun flip qualifié validé.
- `p2_shadow_flip_potential = true` sur Cacao (shadow_contrib_exclu = -72.6), Café (134.8).
- `p2_M6_bias` : biais LONG dominant sur tous les actifs quant-only.

**Signification de T1=13 au dernier run** : ce chiffre est vraisemblablement agrégé sur l'ensemble des actifs×horizons d'un run (12 actifs × 3 horizons = 36 cellules × N runs). Sur Cacao seul, T1=1 par horizon. La montée de T1 indique que le gate `news_cap_applied=true` est déclenché de plus en plus souvent — le cap α=0.8 fonctionne.

#### Ce qu'on peut mesurer MAINTENANT (immédiat)

| Métrique | Données dispo | Interprétation possible |
|---|---|---|
| T1 par actif et par horizon | Oui (tous les runs depuis 01/06) | Quels actifs déclenchent le cap le plus souvent ? |
| Ratio news dominant (ratio_news > 50%) | Oui | Quels actifs sont news-driven vs quant-driven ? |
| p2_M2_stale_rate | Oui (0 actuellement) | Pas encore de news stale à >30j — normal après 3 jours |
| p2_shadow_flip_potential | Oui | Actifs où une news supprimée aurait retourné la conclusion |
| Divergence ±1 vs pondéré (diverge=true) | 0 actuellement | Aucune divergence observée — les deux scores coïncident |

#### Ce qu'il faudra attendre (30 runs ≈ J+10)

| Métrique | Pourquoi attendre | Horizon réaliste |
|---|---|---|
| T2 (vrais flips qualifiés) | Nécessite que nature="structurel" + high+confirmed → flip → outcome VRAI | J+10 minimum, J+30 pour N>5 |
| Taux stale (p2_M2) | Les news d'aujourd'hui deviendront stale dans ~30j | J+30 |
| Taux dédup (p2_M3) | Dépend du volume de news répétées sur un même event_id | J+7 à J+14 |
| Comparaison A vs B sur outcomes news-driven | Nécessite des outcomes conclusifs sur cellules news-dominantes (ratio_news>50%) | J+30 minimum |
| Significativité T1/T2 | Test binomial valide si N_T1 ≥ 20 | J+10 si cacao continue |

**Ce que T1=13 montre dès maintenant** : le gate fonctionne — il bloque des overrides. Mais on ne sait pas encore si ces overrides bloqués auraient été bons ou mauvais (c'est précisément ce que T2/outcomes mesurera). Ne pas confondre "le gate s'active" avec "le gate est correct".

---

## PARTIE 2 — Scoping du backtest quantitatif historique

### 2.1 Ce que le backtest peut prouver — et ce qu'il ne peut PAS

**Peut prouver :**
- L'edge directionnel du moteur **quant-only** (prix/z-scores/COT/RSI/ratios/spreads) sur données historiques
- La calibration des seuils d'amplitude par actif sur distributions historiques
- La robustesse du signal quant sur différents régimes de marché (bull 2023, correction 2022, choc 2024)
- La valeur des critères individuels via ablation (enlever COT → impact sur directional accuracy ?)

**Ne peut PAS prouver :**
- La valeur du composant **news/DeepSeek** (non reproductible — les news RSS du 15/03/2024 ne sont plus disponibles dans leur contexte d'époque)
- La performance du système **complet** (quant + news) — c'est l'objet du shadow forward
- La pertinence des **pertinences par horizon** (les valeurs 0.3/0.7/1.0 ont été fixées par jugement — le backtest peut les challenger mais pas les valider définitivement)
- Les coûts de transaction réels (spreads turbos, frais Bourse Direct) — ces coûts peuvent annuler un edge directionnel de 60-65%

---

### 2.2 Données historiques nécessaires

#### Sources et disponibilité

| Données | Source | Profondeur recommandée | Granularité | Coût |
|---|---|---|---|---|
| OHLCV actifs principaux (Or, Pétrole, Argent, Café, Blé, Cacao, Cuivre) | Twelve Data (API actuelle) | 5 ans (2021→2026) | Journalier | Inclus plan actuel |
| ETF indices (SPY, QQQ, FCHI proxy) | Twelve Data | 5 ans | Journalier | Inclus |
| CFTC COT (tous actifs avec contrats futures) | CFTC.gov (CSV hebdo gratuit) | 10 ans disponibles | Hebdomadaire | Gratuit |
| Taux FRED (TIPS 10Y, Fed Funds) | FRED API (gratuit) | 10 ans | Journalier/hebdo | Gratuit |
| VIX historique | CBOE (Yahoo Finance ou Twelve) | 5 ans | Journalier | Inclus ou gratuit |
| RSI (calculable) | Dérivé des OHLCV | idem | Calculé en Python | — |
| Z-scores (calculable) | Fenêtre glissante sur OHLCV | idem | Calculé | — |

#### Profondeur minimale vs recommandée

- **Minimum viable** : 2 ans (2024-2026) → ~500 jours de trading → ~500 prédictions 24h non-chevauchantes par actif.
- **Recommandé** : 4-5 ans (2021-2026) → inclut bull 2021, crash 2022, rebond 2023-2024, régime 2025. Diversité de régimes indispensable pour éviter un backtest optimisé sur un seul régime.
- **Maximum utile** : 8 ans (2018-2026) → données COT disponibles, mais les critères RSI/z-scores nécessitent ~100 jours de warmup, donc commencer les prédictions au J+100.

---

### 2.3 Protocole de backtesting non-chevauchant

#### Principe fondamental

La règle anti-chevauchement est la **contrainte architecturale centrale** du protocole. Sans elle, les résultats sont biaisés à la hausse par autocorrélation.

```
Horizon 24h  → échantillonnage quotidien → 0% chevauchement (prédictions indépendantes)
Horizon 7j   → échantillonnage hebdomadaire (lundi→lundi) → 0% chevauchement
Horizon 1m   → échantillonnage mensuel (1er→1er) → 0% chevauchement
```

**Conséquence sur N disponible (4 ans d'historique) :**

```
24h : ~1000 prédictions/actif × 12 actifs = ~12 000 prédictions totales
7j  : ~200 prédictions/actif × 12 actifs = ~2 400 prédictions totales
1m  : ~48 prédictions/actif × 12 actifs = ~576 prédictions totales
```

Pour l'horizon 1m, 48 obs/actif est insuffisant pour une validation statistique robuste — c'est à la limite (puissance ~60% à taux=70%). Privilégier l'horizon 24h pour les conclusions primaires du backtest.

#### Implémentation step-by-step

```python
# Pseudo-code du protocole backtest quant-only

for date in trading_dates_non_chevauchantes:
    # Reconstruire l'état du monde à cette date (UNIQUEMENT données disponibles avant date)
    donnees_quant = charger_donnees_avant(date, sources=[twelve_data, cftc, fred])

    # Calculer les critères quant (PAS les critères news — exclus du backtest)
    scores = calculer_scores_quant_only(donnees_quant, config_yaml)

    # Prédiction directionnelle
    prediction = "LONG" if score > 0 else "SHORT"

    # Mesurer l'outcome à date + horizon (24h/7j/1m)
    prix_entree = close[date]
    prix_sortie = close[date + horizon]
    delta_pct = (prix_sortie - prix_entree) / prix_entree

    # Classer outcome
    if abs(delta_pct) >= seuil_actif:
        outcome = "VRAI" if (prediction=="LONG" and delta_pct>0) or (prediction=="SHORT" and delta_pct<0) else "FAUSSE"
    else:
        outcome = "non-conclusive"  # exclure du calcul de taux
```

#### Walk-forward obligatoire

Un backtest in-sample seul est du data dredging. Le protocole DOIT inclure une validation walk-forward :

```
Données 2021-2024 (3 ans) → IS (in-sample) : calibrer les poids/pertinences
Données 2025-2026 (1 an) → OOS (out-of-sample) : mesurer la performance réelle
```

Si la performance OOS est significativement inférieure à IS (>10 points d'écart), c'est un signal de sur-ajustement. Répéter avec plusieurs splits temporels (k-fold temporel, k=3 minimum).

---

### 2.4 Critères GO/NO-GO du backtest

#### Seuils primaires (horizon 24h, N_eff ≥ 300 prédictions OOS par actif)

| Critère | Formule | Seuil GO | Seuil NO-GO | Priorité |
|---|---|---|---|---|
| Directional accuracy OOS | k_VRAI / (k_VRAI + k_FAUSSE) | ≥ 60% | < 55% | P0 |
| Wilson lower bound 95% (OOS) | IC bas du taux OOS | ≥ 55% | < 50% | P0 |
| Sharpe ratio directionnel | (mean(return_si_VRAI) − 0) / std(returns) annualisé | ≥ 0.5 | < 0.2 | P1 |
| p-value bootstrap (1000 permutations) | Probabilité d'obtenir ce taux par hasard | < 0.05 | > 0.10 | P0 |
| Taux de non-conclusives | % cellules < seuil amplitude | < 50% | > 70% | P1 |
| Écart IS vs OOS | |taux_IS − taux_OOS| | < 8 pts | > 15 pts | P1 |
| Stabilité cross-régime | Min taux sur 4 régimes distincts (bull/bear/vol/flat) | ≥ 55% | < 50% dans 2+ régimes | P0 |

#### Critères auxiliaires (horizon 7j et 1m — validation secondaire uniquement)

- Pour 7j : seuils réduits à directional accuracy OOS ≥ 58%, Wilson_low ≥ 50%.
- Pour 1m : seuils réduits à ≥ 55% vu N faible (N≈48 → IC large). Ne pas basculer en mode actif sur la base du 1m seul.

#### Test de permutation (bootstrap)

```python
# Procédure bootstrap (1000 itérations)
observed_accuracy = k_VRAI / (k_VRAI + k_FAUSSE)
null_distribution = []
for _ in range(1000):
    shuffled_predictions = np.random.permutation(predictions)  # casser le lien pred→outcome
    null_accuracy = compute_accuracy(shuffled_predictions, outcomes)
    null_distribution.append(null_accuracy)
p_value = np.mean(np.array(null_distribution) >= observed_accuracy)
# GO si p_value < 0.05
```

Ce test est plus robuste que le test binomial classique car il respecte la structure temporelle des données.

---

### 2.5 Effort et faisabilité

#### Estimation de l'effort

| Tâche | Complexité | Temps estimé | Dépendances |
|---|---|---|---|
| Script d'ingest historique (Twelve + CFTC + FRED) | Moyenne | 1-2 jours | API keys existantes |
| Reconstruction des critères quant sur historique | Haute | 2-3 jours | Refactoring des scripts existants pour mode "replay" |
| Moteur de backtest non-chevauchant | Moyenne | 1 jour | Script Python |
| Walk-forward + bootstrap | Moyenne | 1 jour | Librairies scipy/statsmodels |
| Dashboard résultats par actif/horizon/régime | Faible | 0.5 jour | Matplotlib ou Plotly |
| **Total** | | **5-7 jours de dev** | — |

#### Faisabilité technique

**Points favorables :**
- Le code de calcul des critères est déjà en production (`v3/scripts/`). Il faut l'extraire en mode "replay" sans dépendances GitHub Actions.
- Les données Twelve Data sont accessibles via l'API existante.
- CFTC COT est téléchargeable en CSV bulk — pas de rate-limiting.

**Points bloquants potentiels :**
- Certains critères utilisent des données en temps réel (NOAA weather, USDA WASDE delta) qui ne sont pas disponibles historiquement ou nécessitent une reconstruction manuelle. Ces critères devront être mis en `n/a` dans le backtest — c'est acceptable si leur poids est documenté (le backtest teste un sous-ensemble du quant).
- Les z-scores sont calculés sur fenêtre glissante (~252j) : les premières observations (J+0 à J+252) nécessitent un warmup — exclure les 252 premiers jours.
- Le ratio Gold/Silver utilise une normalisation linéaire avec des bornes fixes : vérifier que ces bornes sont cohérentes sur l'historique 2021 (le ratio était plus élevé).

#### Priorité recommandée

Le backtest quant historique est la prochaine étape de validation **la plus rentable** en termes d'information produite. Il peut être lancé en parallèle du shadow forward (les deux ne sont pas mutuellement exclusifs). Horizon de livraison : J+10 à J+14.

---

## Synthèse et recommandations actionnables

### Ce qu'on sait avec certitude (données réelles)

1. **Le pipeline fonctionne** : prix d'émission capturés, conclusions classées, decision-log complet. L'infrastructure de mesure est solide.
2. **Deux premières mesures conclusives** (Or SHORT VRAI, Pétrole LONG VRAI) sont encourageantes mais statistiquement non-significatives (IC Wilson borne basse = 20.6%).
3. **Deux premières erreurs** (Café LONG FAUSSE, Cuivre SHORT FAUSSE) sont également normales à N=1 et ne concluent rien.

### Ce qu'on ne sait pas encore

1. Si le moteur quant a un vrai edge directionnel — **le backtest historique est le seul juge fiable**.
2. Si le biais LONG 61% est structurel (problème) ou conjoncturel (régime haussier) — **attendre 30+ runs**.
3. Si les seuils d'amplitude sont bien calibrés — **recalibrer sur distribution historique des deltas par actif**.

### Actions prioritaires (par ordre d'impact)

| # | Action | Impact | Délai | Prérequis |
|---|---|---|---|---|
| A1 | Lancer le backtest quant-only sur 4 ans d'historique | Très élevé — seul vrai signal de valeur | J+14 | Dev 5-7j |
| A2 | Ajuster seuil VIX : 5% → 3% (24h) + ajouter 7j à 10% | Élevé — cellule morte actuellement | Immédiat | Config YAML |
| A3 | Ajuster seuil Cacao : 1.5% → 1.0% | Moyen — améliore N_eff | Immédiat | Config YAML |
| A4 | Ajouter alerte automatique si biais LONG > 65% sur 10 runs | Moyen — détection précoce | J+3 | Script Python |
| A5 | Recalibrer distribution z-scores sur historique 4 ans (bornes linéaires) | Moyen — cohérence des normes | J+7 | Backtest data |

### Calendrier de confiance

```
Aujourd'hui (J+3)     : N_eff = 0-4/cellule → aucune conclusion possible
J+15 (~15/06)         : N_eff ≈ 10-12/cellule 24h → premiers indicateurs directionnels
J+30 (~01/07)         : N_eff ≈ 15+ → éligibilité Wilson possible sur meilleures cellules
J+10 (backtest)       : premiers résultats backtest quant-only OOS disponibles
J+90 (~01/09)         : données 7j suffisantes (N≈80) pour validation robuste
```

**Verdict global** : le système est en mode de collecte normale. Aucune alarme justifiée, aucune validation justifiée. Le backtest historique est la seule action qui peut produire une information décisionnelle dans les 2 prochaines semaines.

---

*Produit par @data-analyst — TradingApp v3 — 2026-06-01*
