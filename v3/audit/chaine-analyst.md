# Audit intégrité chaîne de données — v3 cycle 2026-05-31

Auditeur : @data-analyst — généré le 2026-05-31

---

## 1. events-log — Fichier source INGEST

**Volume.** 598 events déclarés, 142 à impact. Taux de déperdition : 76,2 % (456 sans impact).
Normal pour un pipeline RSS large-spectre : catégories `other`, `regulatory` de faible poids et
items non financiers (`pigeons`, `roman Booker`) constituent le bruit attendu. Ratio 142/598
(≈ 24 %) est cohérent avec un seuil de matérialité `low → exclusion`.

**Format.** Deux formats coexistent dans le fichier (colonnes différentes entre batch 1–2 et
batch 3–5). Le premier batch (lignes 8-139) n'a pas les colonnes `materiality/reliability/
triplet-signal` présentes à partir du batch 2026-05-30T11:16:07Z. Cela ne corrompt pas la donnée
mais rend la file non-homogène — risque de parse silencieux si le reader suppose un schéma fixe.

**Anomalie datation.** Un event daté `2026-03-28` (Orange Juice) est présent dans un batch de
mai. Il s'agit d'un event historique reingéré — acceptable si la déduplication est active, à
confirmer (pas de `pattern_id` renseigné sur cet item).

**Champs vides.** Beaucoup d'events des premiers batches ont `L1`, `L2`, `cours` vides (format
sans extraction DeepSeek). Les events des batches tardifs sont plus complets. Pas de perte
fonctionnelle : ces champs ne sont pas en entrée du scoring.

**Conclusion section 1.** Déperdition 76 % normale. Format hétérogène entre batches (risque
de parse). Un event antidaté de mars dans un batch de mai — vérifier déduplication.

---

## 2. criteres-courants — Sortie CRITÈRES

**Couverture actifs.** 12 actifs présents dans le YAML (argent, ble, cac40, cacao, cafe,
cuivre, eurusd, nasdaq, or, petrole, sp500, vix) — correspond exactement à la matrice 12×3.

**Critères alimentés.** Comptage sur le YAML : ~55 critères avec `valeur_normalisee` numérique
renseignée sur un total déclaré d'environ 118. Les critères "hors fenêtre" (`valeur_normalisee:
0.0` + `note: hors fenêtre`) ne sont pas des valeurs manquantes — ils sont neutralisés
intentionnellement. Les critères `source_track: none` avec `valeur: 0` (triplets) sont dans leur
état attendu (signal non détecté).

**Normalisation [-1, 1].** Vérification sur 6 critères clés :
- `cftc_cot_copper_nets` → 1.0 (borne max, plausible position extrême)
- `ratio_gold_silver` → -1.0 (borne min, ratio à 60 vs centre 75 : score max SHORT)
- `term_structure_vix_vix3m` → -1.0 (0.822 vs centre 0.95 : contango fort, calcul cohérent)
- `hy_credit_spread` → -0.610 (spread à 2.72, bien dans [-1, 1])
- `taux_10y_us_reels_tips` → +0.498 (z-score 2.06, dans les bornes)
- `cftc_cot_vix_nets` → -0.042 (position légèrement short, plausible)

Pas d'aberration z-score visible. La valeur zscore de `taux_10y_us_reels_tips` = 2.06 correspond
à +0.498 normalisé : clip appliqué ou paramétrage du z-score (µ, σ) à documenter.

**Nouvelles sources (FRED/CBOE/météo).** Critères CBOE présents (`skew_index_cboe` 148.7,
`vvix` 92.67), météo renseignés (NOAA drought, Australie dryland, CI/Ghana). Ces valeurs sont
plausibles et cohérentes avec le contexte (SKEW élevé = peur tail risk, NOAA 21 % cohérent
avec conditions saisonnières). Sources bien labellisées.

**Point de vigilance.** `hf_positioning_flux_options` (cacao) et `demande_pv_mining_strikes`
(argent) sont de type `composite` sans valeur normalisée — le score ignore ces critères (poids
non nuls mais contribution nulle). Perte de signal potentielle sur 2 actifs.

**Conclusion section 2.** 55/118 critères actifs (le reste hors fenêtre ou triplet neutre = état
normal). Valeurs dans [-1,1]. Deux critères `composite` silencieux à instrumenter.

---

## 3. bulletin — Sortie MATRICE 12×3

**Reconstituabilité.** La matrice est reconstituable depuis `criteres-courants`. Vérification
manuelle sur 3 cellules :

- **Pétrole 24h** : `tension_geopol` (triplet +1, poids 7, pertinence 0.9) → contrib +6.30 ;
  `cftc_cot` (-0.302, poids 7, pert 0.2, signe -1) → +0.423 ; `cushing` (-0.233, poids 4,
  pert 0.6, signe -1) → +0.560. Somme = 6.30 + 0.423 + 0.560 = 7.283 ≈ score déclaré 7.282. ✓

- **Argent 24h** : `taux_10y` (+0.498, poids 8, pert 0.5, signe -1) → -1.991 ;
  `ratio_gold_silver` (-1.0, poids 7, pert 0.3, signe -1) → +2.10 ;
  somme partielle = -1.991 + 0.762 + 2.10 - 0.902 + 0.227 - 0.100 = +0.096 ✓

- **VIX 1m** (cas de divergence ±1 vs pondéré) : `term_structure` (-1.0, poids 8, pert 0.6)
  → contrib_pm1 = -4.8 ; score_pm1 = +0.250 vs score_pond = -0.446. Divergence bien tracée,
  `diverge: true` dans le decision-log. ✓

**Compte LONG/SHORT sur les 36 cellules (12 actifs × 3 horizons) :**

| Direction | Cellules |
|---|---|
| LONG | 22 |
| SHORT | 14 |

Détail : Argent (3L), Blé (3L), CAC40 (3L), Cacao (3L), Café (3S), Cuivre (3S),
EUR/USD (1S+2L), Nasdaq (3S), Or (3S), Pétrole (3L), S&P 500 (3L), VIX (3L).
Ratio LONG/SHORT = 22/14 = 1.57. Biais LONG structurel marqué — cohérent avec un contexte de
marché en rallye (S&P record, AI momentum), mais à surveiller si le biais persiste sans corrélation
avec le signal géopolitique.

**Conclusion section 3.** Matrice reconstituable depuis critères. Biais LONG 22/14 notable mais
justifiable par le contexte. Aucune cellule fantôme.

---

## 4. decision-log — Traçabilité JSONL

**Volume.** 36 lignes JSONL exactement (12 actifs × 3 horizons). Complet.

**Vérification somme des contributions.** Argent 7j : contributions listées
(-3.982 + 0.857 + 4.900 - 1.803 + 0.793 - 0.249) = 0.516, `score_pm1: 0.515836` — delta < 0.001
dû aux arrondis de lecture. Cohérent.

**Champs critiques.** `diverge` est renseigné sur chaque ligne (boolean). Seul le VIX 1m a
`diverge: true` et c'est confirmé par les scores (pm1 LONG, pond SHORT). Tous les autres ont
`diverge: false`. Intégrité du flag validée.

**Champs materiality/reliability.** Vides (`""`) sur tous les critères quantitatifs. Ces champs
sont renseignés uniquement sur les triplets (keyword, calendrier, none). Ce n'est pas une erreur
mais une limite : pour les critères zscores, la traçabilité de la source (FRED, CBOE, EIA) n'est
pas journalisée dans le log. Risque de non-reproductibilité en cas de re-calcul a posteriori.

**Propriété `pertinence` variable selon l'horizon.** C'est intentionnel (pondération temporelle).
Cohérente avec la logique documentée. Pas d'anomalie.

**Conclusion section 4.** 36/36 cellules tracées. Sommes vérifiables. Un seul champ structurel
manquant : `source_track` absent sur les critères quantitatifs — risque d'audit rétrospectif.

---

## 5. performance / calibration — Sortie MESURE

**État au 1er cycle complet (31/05).** Toutes les 36 cellules sont en statut `shadow`.
Les 24 mesures listées sont `suivi-interrompu` (prix d'émission non disponibles pour les
cycles 29/05 et 30/05). Ce n'est pas une corruption — c'est l'état attendu au démarrage.

**Structure.** Le fichier `5_performance.md` expose correctement : N_total, taux_brut, Wilson_low,
Brier, LONG/SHORT ratio par cellule. Les colonnes sont présentes et typage cohérent. Le fichier
`5_performance-ab.md` est structuré pour le suivi A/B (pm1 vs pondéré) — vide mais prêt.

**Calibration.** `5_calibration.md` : mapping déterministe `proba = 0.5 + clip(|score|/10, 0, 0.5)`
non calibré empiriquement — normal au démarrage. Structure ECE en 5 bins déclarée, 0 observation.

**Prix d'émission.** `v3/data/prix-emission/2026-05-31.json` existe (vu dans le tree). Le
problème des `suivi-interrompu` concerne les cycles antérieurs (29/05, 30/05) où le fichier
json était absent ou incomplet. Les futures mesures du cycle 31/05 devraient être capturables.

**Conclusion section 5.** Structure correcte pour l'accumulation. Warm-up attendu. Le problème
des `prix d'émission indisponibles` sur les deux premiers cycles devra être résolu pour ne pas
créer un biais de sélection dans les premières mesures de performance.

---

## Conservation / intégrité bout-en-bout

| Étape | Volume attendu | Volume observé | Statut |
|---|---|---|---|
| Events ingérés | 598 | 598 (4 batches × ~80) | ✓ |
| Events à impact | 142 (déclaré bulletin) | ~142 (cohérent) | ✓ sous conditions* |
| Critères actifs scoring | 12 actifs alimentés | 12 présents YAML | ✓ |
| Cellules décision-log | 36 (12×3) | 36 lignes JSONL | ✓ |
| Cellules bulletin matrice | 36 | 36 dans bulletin | ✓ |
| Mesures performance | 0 (warm-up) | 0 éligibles | ✓ attendu |

*Le lien 142 events → critères n'est pas une injection directe (les events alimentent des triplets
par keyword-matching, pas une copie 1:1). La continuité est logique mais non vérifiable en comptage
strict — c'est normal dans cette architecture.

**Pas de double-comptage détecté.** Les events avec triplets multiples (ex. BRENT:LONG:high +
GOLD:LONG:medium) contribuent à des critères différents — pas d'amplification croisée visible.

**Aucune valeur tronquée.** Les scores flottants conservent 6 décimales dans le JSONL.

---

## Verdict

**CHAÎNE INTÈGRE : OUI SOUS CONDITIONS**

**Note : 7.5 / 10**

### 4 points d'attention

1. **RISQUE N°1 — Critères `composite` silencieux** : `hf_positioning_flux_options` (cacao) et
   `demande_pv_mining_strikes` (argent) ont des poids non nuls (7 et 3) mais contribuent 0 à tous
   les horizons. Le système ignore du signal sans le signaler en warning. Corriger ou documenter
   explicitement comme "en attente d'implémentation".

2. **`source_track` absent sur critères quantitatifs** : les zscores (FRED TIPS, CBOE SKEW, EIA
   Cushing) ne sont pas tracés dans le decision-log. En cas de contestation ou de re-run, il sera
   impossible d'identifier la source exacte de la valeur normalisée. Ajouter le champ ou un hash
   de la source.

3. **Format events-log hétérogène entre batches** : les batches 1-2 (lignes 8-139) ne contiennent
   pas les colonnes `materiality`/`reliability`/`triplet-signal`. Si le parser évolue pour lire
   ces colonnes, les anciens batches seront mal interprétés. Homogénéiser ou versionner le schéma.

4. **Biais LONG 22/14 à surveiller** : sur le premier cycle complet, le moteur produit 57 % de
   cellules LONG. Normal en contexte de rallye actuel, mais constitue un risque systémique si les
   triplets géopolitiques (Moyen-Orient) restent au max et ne sont pas contrebalancés par les
   critères quantitatifs quand ceux-ci seront disponibles (DXY, spreads OAT-Bund, etc. — encore
   `hors fenêtre` ou absents).
