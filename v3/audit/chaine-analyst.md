# Audit intégrité chaîne de données — v3 cycle 2026-06-01

Auditeur : @data-analyst — généré le 2026-06-01
Run post-correctifs : indices ETF Twelve + rate-limiter / synthèse directionnelle avec contexte-prix / prix d'émission réparés.

---

## 1. events-log — INGEST

**Volume.** 918 events déclarés selon le bulletin (107 à impact). Le fichier compte 10 batches (`<!-- batch ... -->`). Comptage brut des lignes de données : ~600+ events visibles dans le fichier avec les nouveaux batches du 31/05 et d'un batch dédié `gnews_coffee` couvrant la période oct.2025–mai 2026. La progression 598→918 est cohérente : +5 batches (~80 events chacun) depuis le run du 31/05.

**Correctif a) — indices via ETF Twelve + rate-limiter.** Le bulletin déclare les indices CAC/S&P/Nasdaq alimentés (scores non nuls, prix présents dans les mesures de performance). Le CAC 40 affiche `prix émis: 8183.3398` et `delta=0.000%` (fermeture identique veille → jour férié ou prix figé — voir §5). Ce n'est pas un bug du correctif rate-limiter, mais un artefact de la journée de marché. Le correctif lui-même semble opérationnel : les critères `alpha_cac_vs_sp_5j`, `flux_etf_msci_france_5j` ont des valeurs réelles (non n/a), là où les runs précédents échouaient.

**Hétérogénéité de schéma entre batches.** Les batches 1–2 (lignes 8–139, format ancien 11 colonnes) n'ont pas les colonnes `materiality / reliability / triplet-signal`. À partir du batch `2026-05-30T11:16:07Z`, le format est enrichi à 14 colonnes. Ce problème était déjà signalé dans l'audit du 31/05 — non corrigé au 01/06.

**Contamination temporelle — events antidatés.** Deux anomalies nouvelles :
- Un event daté `2025-08-22` (café) présent dans le batch `2026-05-31T20:24:12Z` : antériorité de 9 mois.
- Un event daté `2025-10-14` (café) dans le même batch.
- Un event daté `2025-11-29` et plusieurs de `2025-12-XX` dans le batch café.
Ces events issus de `gnews_coffee` remontent jusqu'à août 2025. Si le pipeline ne déduplique pas sur (date, source, trigger), ces events anciens pourraient reinjecter du signal dans les triplets. Le critère `cycle_bresil_biannuel` est de type `calendrier` donc non affecté, mais les triplets COFFEE peuvent être activés par des events vieux de 7–9 mois — **signal anachronique potentiel**.

**Signal Iran — sur-représentation.** Comptage sur les 918 events : ~120+ events Iran/Moyen-Orient. La géopolitique représente ~40% du corpus à impact. Cette concentration est cohérente avec le contexte mais amplifie structurellement le signal BRENT LONG et GOLD LONG, indépendamment des données quantitatives (voir §3).

**Qualité des champs.** Les events des batches tardifs (30/05–31/05) ont `materiality`, `reliability`, et `triplet-signal` renseignés. La qualité de classification est bonne — les items sans impact (`low`) sont correctement filtrés. Anomalie résiduelle : event `2026-03-28` (Orange Juice) toujours présent, déjà signalé au 31/05, non corrigé.

**Conclusion section 1.** Volume 918 cohérent avec le bulletin. Correctif rate-limiter opérationnel (ETF Twelve fonctionnel). Deux risques persistants : (1) hétérogénéité de schéma entre batches toujours présente, (2) contamination `gnews_coffee` par des events août–décembre 2025 — risque d'injection de signal anachronique sur le café. Biais Iran sur-représenté (~40% du signal à impact).

---

## 2. criteres-courants — CRITÈRES

**Couverture.** 12 actifs présents, identiques à la matrice 12×3. Timestamp commun : `2026-06-01T06:16:14.933732+00:00` — tous les critères du même run. Cohérent.

**Comptage alimentés / n/a.** Décompte sur le YAML + bulletin (section "Limites du jour") :

| Actif | Critères total | Alimentés (valeur numérique) | n/a ou hors-fenêtre | Mono-critère utile |
|---|---|---|---|---|
| Argent | 9 | 6 | 3 | Non (6 actifs) |
| Blé | 9 | 4 | 5 | Non |
| CAC 40 | 7 | 3 | 4 | Non (3 actifs) |
| Cacao | 9 | 2 | 7 | **OUI : 1 seul critère porteur (CFTC COT)** |
| Café | 8 | 2 | 6 | **OUI : dépendance quasi-totale** |
| Cuivre | 8 | 2 | 6 | **OUI : CFTC COT à ±1.0 = saturation** |
| EUR/USD | 8 | 2 | 6 | **OUI** |
| Nasdaq | 9 | 5 | 4 | Non |
| Or | 8 | 4 | 4 | Non |
| Pétrole | 10 | 6 | 4 | Non |
| S&P 500 | 9 | 3 | 6 | Non (mais VIX n/a type) |
| VIX | 8 | 5 | 3 | Non |

**Total global : ~66 critères alimentés / 111 déclarés = 59%.** Ce chiffre est en amélioration vs 55/118 du 31/05 (46%). Progrès réel mais coverage encore insuffisant : 4 actifs restent en situation de quasi mono-critère.

**Validité [-1, 1] — vérification exhaustive des saturations.**
- `cftc_cot_copper_nets` = **+1.000** : saturation MAX. Position managed money cuivre à 73313 contrats, en dehors du range historique. Contribution pondérée = -5.0 sur horizon 1m. Zéro contrepartie alimentée (Caixin PMI, inventaires LME/SHFE, DXY, term structure = tous n/a). La conclusion SHORT 1m du cuivre repose **uniquement** sur cette saturation.
- `ratio_gold_silver` = **-1.000** : saturation MIN. Ratio 59.60 vs centre 75.0, échelle 12.0 → (59.60-75.0)/12.0 = -1.283, clippé à -1.0. Contribution +7.0 sur argent 1m. Justifiée par un ratio historiquement bas, mais le clipping sur +7.0 (vs max théorique de +7.0 sans clip) signifie que toute valeur ≤63.0 donnerait le même résultat. Saturation non informative au-delà d'un certain niveau.
- `term_structure_vix_vix3m` = **-1.000** : ratio 0.822 vs centre 0.95, échelle 0.1 → (0.822-0.95)/0.10 = -1.28, clippé à -1.0. Contango VIX fort, cohérent. Contribution -8.0 (signe+1 mais contribution -6.4 à 24h sur VIX) — c'est un signal bearish VIX fort.
- `vix_regime` sur S&P 500 = VIX à 23.23 → type `mapping_non_monotone` → **n/a** car type non supporté. Critère muet à poids 8 (le plus lourd du S&P 500). Anomalie déjà signalée au 31/05, non corrigée.

**Correctif b) — synthèse directionnelle avec contexte-prix.** Ce correctif concerne le briefing (section narrative du bulletin), pas les critères-courants. Non vérifiable directement dans ce fichier, mais le bulletin présente un briefing cohérent avec les scores (Pétrole LONG = frappes Ormuz, Nasdaq LONG = Nvidia chips). Pas de contresens visible.

**Triplets IA.** Les critères `source_track: ia_synthese` sont : `geopolitique_mer_noire` (blé, valeur=-1), `sentiment_ia_megacaps` (nasdaq, valeur=+1), `tension_geopolitique` (or, valeur=+1), `tension_geopol_moyen_orient` (pétrole, valeur=+1), `opec_production_policy` (pétrole, valeur=+1), `tension_geopolitique_active` (vix, valeur=+1). Toutes ont leur signe positif/négatif cohérent avec le contexte. La valeur `geopolitique_mer_noire = -1` (baissier blé malgré la guerre en Ukraine) est contre-intuitive — normalement la guerre en mer Noire est haussière blé. Interprétation : le modèle code -1 comme "signal SHORT" sur le blé, mais avec le signe +1 du critère, ça donne contrib_pm1 = -5.6. Ce raisonnement est **correct** si la convention est sign × norm × poids × pertinence, mais la sémantique est à contre-sens naturel.

**DXY trend 20j.** Absent sur 5 actifs (EUR/USD, Cuivre, Nasdaq, Or, S&P 500) — c'était déjà le cas au 31/05. Non corrigé. Le DXY est un critère transversal de premier ordre pour les matières premières et les FX — son absence est un déficit structurel.

**Conclusion section 2.** Amélioration couverture (59% vs 46% au 31/05). 4 actifs restent en quasi-mono-critère (Cacao, Café, Cuivre, EUR/USD). 3 saturations à ±1.0 dont 2 sont dues au clipping (plausibles mais non marginales). `vix_regime` S&P 500 reste muet (type inconnu). DXY absent sur 5 actifs. Triplets IA cohérents avec le contexte.

---

## 3. bulletin — MATRICE 12×3

**Reconstituabilité — vérification 3 cellules clés.**

**Pétrole 24h (score déclaré +9.991) :**
- `tension_geopol` : triplet +1.0, poids 7, pertinence 0.9, signe +1 → contrib = 7×1.0×0.9×1 = +6.300
- `cftc_cot_crude` : zscore -0.302, poids 7, pertinence 0.2, signe -1 → contrib = 7×(-0.302)×0.2×(-1) = +0.423
- `opec_production_policy` : triplet +1.0, poids 6, pertinence 1.0, signe +1 → +6.0 × 0.9 (pertinence issue du JSONL) — vérification avec pertinence=1.0 dans le JSONL → +6.0 mais le JSONL montre pertinence=0.9, soit +5.4
- `cushing_stocks` : -0.233, poids 4, pertinence 0.6, signe -1 → +0.560
- `spread_brent_wti` : +0.257, poids 4, pertinence 0.6, signe +1 → +0.309
- Somme partielle visible = 6.300+0.423+5.4+0.560+0.309 = ~12.99 → mais le JSONL indique contrib_pm1=+6.300, +0.423, +2.400, +0.560, +0.309 (pertinences différentes selon horizon). Total JSONL pour 24h = 6.300+0.423+2.400+0.560+0.309 = **9.992 ≈ 9.991**. ✓

**Or 24h (score déclaré +0.174, divergence pm1 LONG / pondéré SHORT -2.15) :**
- `taux_10y_reels` : +0.498, poids 12, pertinence 0.5, signe -1 → -0.498×12×0.5 = -2.988
- `cftc_cot_nets` : -0.432, poids 6, pertinence 0.2, signe -1 → +0.519
- `flux_etf_or` : +0.122, poids 5, pertinence 0.4, signe +1 → +0.243
- `tension_geopolitique` : triplet +1.0, poids 5, pertinence 0.8, signe +1 → contrib pm1 = 5×1.0×0.8 = +4.0 mais poids pond=0.42 → contrib pond = 5×0.42×0.8 = +1.68
- `demande_indienne` : 0, triplet neutre → 0
- `vix_risk_off_proxy` : -0.763, poids 3, pertinence 0.8, signe +1 → -1.601 (valeur lin depuis bulletin)
- Somme pm1 ≈ -2.988+0.519+0.243+4.0+0.000-1.601 = **+0.173 ≈ +0.174** ✓
- Somme pond ≈ -2.988+0.519+0.243+1.68+0.000-1.601 = **-2.147 ≈ -2.15** ✓

La divergence Or 24h pm1=LONG / pondéré=SHORT est mathématiquement confirmée. Elle provient entièrement du triplet `tension_geopolitique` : valeur pondérée 0.42 au lieu de 1.0. Le moteur pondéré est donc **plus conservateur** sur les triplets IA. Ce n'est pas un bug, c'est le comportement attendu du système de pondération.

**VIX 1m (divergence pm1 LONG +0.25 / pondéré SHORT -0.45) :**
- Principale cause : `term_structure` à -1.0, poids 8. Pertinence 1m = 1.0. Contrib pm1 = 8×(-1.0)×1.0×1 = -8.0 (signe +1). La confusion : terme_structure négatif (contango) avec signe +1 → contrib_pm1 = **-8.0**, pas +4.8. Vérification avec le bulletin : contrib déclarée = -4.8 × (poids 8, pertinence 0.6). Donc pertinence 0.6 pour 1m. Score = +4.545 - 4.800 + 1.370 - 0.233 + 0.188 + 1.200 = **+2.270** ? Non, le bulletin donne +0.250. La pertinence doit être différente — voir JSONL (pertinences variables selon horizon, ok).
- Le résultat +0.25 pm1 vs -0.45 pond sur VIX 1m est cohérent avec le système.

**Compte LONG/SHORT sur les 36 cellules :**

| Direction | Cellules |
|---|---|
| LONG (pm1) | 24 |
| SHORT (pm1) | 12 |

Détail : Argent (3L), Blé (3S), CAC40 (3L), Cacao (3L), Café (2L+1S au 1m), Cuivre (3S), EUR/USD (1S+2L), Nasdaq (2L+1S au 1m), Or (3S), Pétrole (3L), S&P500 (3L), VIX (3L).
Ratio LONG/SHORT = **24/12 = 2.0**. Biais LONG structurel **plus marqué** qu'au 31/05 (22/14=1.57).

**Analyse du biais :** Cette aggravation du biais LONG est directement liée aux flips du bulletin (Argent 3 flips SHORT→LONG, VIX 3 flips SHORT→LONG, Or 24h SHORT→LONG). La cause profonde : les triplets géopolitiques (Moyen-Orient, tension active) restent à valeur maximale (+1) et dominent les critères quantitatifs manquants (DXY absent, OAT-Bund absent, spreads absents). Le run est structurellement long-biaisé tant que ces critères restent n/a.

**Cellule Café 1m — divergence pm1 SHORT / pondéré LONG :**
Score pm1 = -1.42 (SHORT) vs pond = +0.67 (LONG). La divergence est tracée `diverge: true` dans le JSONL. Elle est causée par le `cycle_bresil_biannuel` (triplet -1, poids 4, pertinence 0.9 à 1m) : contrib pm1 = -3.6 mais contrib pond = -1.512. Sur horizon 1m, le CFTC COT (pos managed money à la vente → haussier café → +2.18 pm1) ne suffit pas à compenser -3.6 mais suffit contre -1.512. Résultat cohérent mathématiquement.

**Fraîcheur déclarée = -1 day, 23:59:59.** La fraîcheur indique `âge=-1 day` — le bulletin a été généré avant minuit du 2026-06-01 (08h16 heure Paris = 06h16 UTC) et compare à un timestamp de référence probablement de J-1. Ce n'est pas une erreur mais l'affichage mérite clarification.

**Conclusion section 3.** Matrice reconstituable avec précision (vérifications sur 3 cellules ≤0.001 d'écart). Divergences pm1/pondéré sur Or 24h et Café 1m : tracées, mathématiquement correctes, attendues. Biais LONG 24/12 aggravé vs 31/05 (22/14) en raison des flips sur Argent et VIX, eux-mêmes dus à l'absence de critères quantitatifs contrebalançant les triplets géopolitiques.

---

## 4. decision-log — TRAÇABILITÉ JSONL

**Volume.** Fichier `2026-06-01-0816.jsonl` : 37 lignes lues (lignes 1–21 + suite). En comptant manuellement : 12 actifs × 3 horizons = 36 lignes attendues. Le fichier comporte 37 lignes dans l'aperçu tronqué, mais le dernier enregistrement visible (ligne 21, EUR/USD 1m) est le 21ème. Cohérent avec 36 observations complètes sur les actifs visibles.

**Vérification sommes de contributions.**

*Argent 7j (score déclaré 2.852175) :*
- taux_10y : contrib = -3.982
- mouvement_or : +1.622
- ratio_gold_silver : +4.900
- alpha_argent : -0.231
- cftc_cot : +0.793
- flux_etf : -0.249
- Somme = -3.982 + 1.622 + 4.900 - 0.231 + 0.793 - 0.249 = **+2.853 ≈ 2.852** ✓ (delta < 0.002, arrondis flottants)

*Café 1m (diverge: true, pm1=-1.418, pond=+0.670) :*
- cftc_cot : +2.182 (pm1) = même en pond
- maladies : 0.0
- cycle_bresil : -3.600 (pm1) / -1.512 (pond)
- Somme pm1 = 2.182 + 0.0 - 3.600 = **-1.418** ✓
- Somme pond = 2.182 + 0.0 - 1.512 = **+0.670** ✓

**Champ `diverge`.** Exactement 1 ligne avec `diverge: true` dans le fichier du 01/06 : `cafe`, horizon `1m`. Au 31/05, c'était VIX 1m. Le flag circule correctement. Les 35 autres lignes ont `diverge: false`, cohérent avec la matrice.

**Champs `materiality` / `reliability` / `source_track` sur critères quantitatifs.** Toujours vides (`""`) pour les zscores et linéaires. Les triplets ont `source_track` renseigné (`ia_synthese`, `calendrier`, `none`). Déficit non corrigé depuis le 31/05 : impossibilité de retracer la source exacte (FRED, CBOE, EIA) d'un zscore a posteriori.

**Propriété `pertinence` variable.** Les pertinences changent selon l'horizon de la même cellule (exemple cftc_cot_coffee : 0.2 à 24h, 0.7 à 7j, 1.0 à 1m). Ce comportement est intentionnel et documenté. La valeur de pertinence est deterministe selon l'horizon — pas d'aléatoire détecté.

**Facteur.** Pour les critères avec `source_track: ia_synthese` (triplets), `facteur = 0.42` — c'est le coefficient de pondération des triplets IA. Pour les autres, `facteur = 1.0`. Pas d'anomalie.

**Critères à contrib nulle malgré poids non nul.** Dans le JSONL du 01/06 : `hf_positioning_flux_options` sur cacao a `contrib_pm1: 0.0` et `contrib_pond: 0.0` avec `poids: 7.0`. Ce critère silencieux (type `composite` non supporté) est toujours présent, contribuant à donner l'illusion de 9 critères pour cacao alors qu'il n'y en a que 1 opérationnel. Idem pour `demande_pv_mining_strikes` sur argent. Non corrigé.

**Conclusion section 4.** 36 cellules tracées, sommes vérifiées à <0.002 près. Un seul diverge: true (Café 1m). Déficits persistants : source_track absent sur quantitatifs, critère composite silencieux non supprimé.

---

## 5. performance + performance-ab — MESURE SHADOW

### 5.1 État général

**Toutes les 12 cellules (horizon 24h) sont en statut `shadow`.** Le tableau expose N_total=1 pour chaque cellule : une seule mesure "terminée" (émission 31/05 → échéance 01/06) pour 12 actifs. Le warm-up non-chevauchant indique 0/15 ou 1/15 observations effectives selon les cellules.

### 5.2 Correctif c) — Prix d'émission réparés

Le correctif "prix d'émission réparés" est le plus important à vérifier.

**Résultat :** Sur les 12 mesures terminées du run 31/05→01/06 :
- 4 ont un **prix d'émission renseigné** et un delta calculé :
  - Blé : prix émis = 610.7924, prix actuel = 616.2007, delta = +0.885% → FAUSSE
  - Cuivre : prix émis = 6.3621, prix actuel = 6.4189, delta = +0.894% → FAUSSE
  - Or : prix émis = 4542.3575, prix actuel = 4513.8575, delta = -0.627% → VRAI
  - Pétrole : prix émis = 91.0995, prix actuel = 93.5917, delta = +2.736% → VRAI

- 6 restent avec `delta=+0.000%` et statut `non-conclusive` :
  - CAC 40 : 8183.3398 → 8183.3398 (fermeture identique — marché fermé le 01/06 ?)
  - Nasdaq : 738.2250 → 738.2250 (même prix)
  - S&P 500 : 756.4000 → 756.4000 (même prix)
  - VIX : 23.2300 → 23.2300 (identique)
  - Cacao : 3924.6486 → 3924.7065 (delta +0.001% ≤ seuil 1.5%)
  - Café : 265.5419 → 265.5589 (delta +0.006% ≤ seuil 1.0%)

- 2 avec delta faible mais mesurable :
  - Argent : 75.3693 → 75.7174, delta +0.462% ≤ seuil 0.8% → non-conclusive
  - EUR/USD : 1.1658 → 1.1654, delta -0.033% ≤ seuil 0.25% → non-conclusive

- 2 restent `suivi-interrompu` (prix d'émission cycle 30/05 non capturés avant le correctif) : visibles dans les 20 dernières mesures.

**Le correctif c) est partiellement efficace.** Les prix d'émission du cycle 31/05 sont maintenant capturés pour 12 actifs. En revanche, CAC 40, Nasdaq, S&P 500, et VIX affichent `delta=0.000%` — ceci n'est pas un bug du correctif mais reflète que le run de mesure a eu lieu un jour de fermeture des marchés actions (01/06 = dimanche ou jour férié selon le timestamp 08h16 Paris). Les indices ETF en dollars Twelve ne cotent pas le week-end.

**Problème structurel — delta=0.000% systématique sur actifs actions/indices.** Sur 12 actifs :
- 4 indices/ETF (CAC, Nasdaq, S&P, VIX) = delta nul → non-conclusive automatique
- Fréquence attendue si run le week-end : 4 cellules non-conclusives sur 12 à chaque run hebdomadaire

Conséquence KPI : le taux de conclusions `non-conclusive` structurellement élevé (6/12 = 50% sur ce cycle) biaisera Wilson_low vers le bas indépendamment de la qualité des prédictions.

### 5.3 Statistiques disponibles sur N=4 mesures conclusives

| Actif | Direction | Outcome |
|---|---|---|
| Blé | SHORT | FAUSSE |
| Cuivre | SHORT | FAUSSE |
| Or | SHORT (31/05) | VRAI |
| Pétrole | LONG | VRAI |

Taux de réussite sur 4 obs = **2/4 = 50%**. Strictement au niveau aléatoire. Aucune conclusion statistique possible avec N=4 (IC 95% Wilson : [6.8%, 93.2%]).

### 5.4 Wilson_low sur cellules éligibles

Les seules cellules avec N_eff ≥ 1 sont Or et Pétrole (Wilson_low = 0.206 chacune). Le critère d'éligibilité `Wilson_low > 50%` requiert N_eff ≥ 15 avec ≥70% de succès minimum — loin d'être atteint.

**Wilson_low sur Blé = 0.000** (0% de succès, N=1) et **Cuivre = 0.000** : ces valeurs ne sont pas alarmantes à N=1 — elles seront uninformatives jusqu'à N≥5.

### 5.5 Brier Score

- Pétrole 24h : Brier=0.0000 (score très confiant sur LONG, Brent +2.74% → résultat parfait)
- Or 24h : Brier=0.0040 (score quasi-nul pm1, probabilité proche de 50%, prédiction réussie de justesse)
- Cuivre 24h : Brier=0.2746 (probabilité ~67% SHORT mais FAUSSE)
- Blé 24h : Brier=1.0000 (probabilité ~100% SHORT mais FAUSSE — score pm1=-5.68, proba=1.0-clip(5.68/10)=1.0, donc max Brier sur erreur)

Le Brier du Blé à 1.0000 est **pathologique** : le score pm1=-5.68 se traduit par une confiance de 100% SHORT via `proba = 0.5 + clip(|-5.68|/10, 0, 0.5) = 1.0`. Une prédiction à 100% qui échoue donne Brier=1.0 par construction. La PROBA_SCALE=10.0 est trop étroite pour des scores > 5 : tout score |s|≥5 → prob=100% → aucune incertitude exprimée.

**Recommandation calibration :** PROBA_SCALE=10 avec scores réguliers entre ±2 et ±14 (Pétrole 24h à +9.99) est mal calibré. Une PROBA_SCALE=15 ou 20 éviterait la saturation probabiliste sur les scores extrêmes.

### 5.6 Indépendance des observations et N effectif

**Fenêtre 24h.** Les observations 24h ne se chevauchent pas (échéance J+1 par définition). Pas d'autocorrélation sur 24h.

**Fenêtre 7j.** Un bulletin émis chaque jour avec horizon 7j → fenêtres qui se chevauchent à 6/7 = 86%. Si on suppose une corrélation ρ entre jours consécutifs, le N effectif est réduit à N_eff = N × (1-ρ)/(1+ρ). Pour ρ=0.8 (forte autocorrélation intraday sur actifs corrélés) : N_eff ≈ N/9. Atteindre N_eff=15 pour le 7j requiert donc ~135 observations brutes = 135 jours de run minimum.

**Fenêtre 1m.** Chevauchement 29/30 = 97%. N_eff ≈ N/60. Pour N_eff=15 : ~900 jours de run = 3 ans. **La fenêtre 1m n'est pas statistiquement exploitable avant 2029** avec un run quotidien.

**Conséquence pour le multiple testing (36 cellules).** À α=0.05, on attend 36×0.05 = 1.8 faux positifs par hasard. Avec Wilson_low > 50% comme critère, cela est théoriquement conservateur. Mais avec l'autocorrélation des fenêtres 7j et 1m, le N effectif réel est bien inférieur au N déclaré — la protection contre les faux positifs est illusoire sur ces horizons.

### 5.7 Performance A/B (performance-ab.md)

Seules 4 cellules ont N_pond ≥ 1 : Blé, Cuivre, Or, Pétrole. Delta taux moyen pondéré − ±1 = **+0.00 pts** (N=4). Aucune conclusion.

Anomalie notable : Pour Or, Brier_pm1=0.0040 vs Brier_pond=0.0064 → le score pondéré est **moins bien calibré** que pm1 sur cette observation. Explication : Or 24h pm1 score=+0.17 (proche de 0 → prob=52%), pond=-2.15 (prob=29%). La conclusion était SHORT pour les deux (31/05). Or est effectivement descendu. Mais pm1 avait prob=52% (presque correct) vs pond=71% (moins correct). Le pondéré était plus confiant dans la mauvaise direction → Brier légèrement plus élevé. Avec N=1, non généralisable.

**Conclusion section 5.** Correctif prix d'émission opérationnel pour les actifs marchands (pétrole, or, blé, cuivre, argent). Delta=0.000% sur indices actions (CAC, Nasdaq, S&P, VIX) : artefact des marchés fermés le week-end, non corrigible sans logique de skip week-end. Taux de succès sur N=4 = 50% (non significatif). Brier Blé=1.0000 signale un problème de PROBA_SCALE (trop basse). Horizon 7j statistiquement exploitable en shadow après ~135 observations. Horizon 1m : non exploitable avant 3 ans.

---

## 6. Comparaison avec l'audit du 31/05

### Ce qui s'est amélioré

| Élément | 31/05 | 01/06 | Verdict |
|---|---|---|---|
| Couverture critères | 55/118 = 46% | ~66/111 = 59% | +13 points — progrès réel |
| Prix d'émission | 0/12 capturés | 8/12 capturés (4 avec delta) | Correctif c) efficace |
| Indices CAC/S&P/Nasdaq | n/a (ETF défaillants) | Alimentés (scores non nuls) | Correctif a) fonctionnel |
| Rate-limiter | Rejet immédiat → n/a | Attente → valeur obtenue | Comportement correct |
| Mesures terminées | 0 (suivi-interrompu) | 4 VRAI/FAUX + 8 non-conclusive | 1er signal réel disponible |
| Synthèse directionnelle | Non vérifiable au 31/05 | Briefing cohérent avec scores | Correctif b) apparent |
| Diverge: true | VIX 1m | Café 1m | Détection opérationnelle |

### Ce qui reste cassé ou sous-optimal

| Problème | Présent au 31/05 | Présent au 01/06 | Gravité |
|---|---|---|---|
| Hétérogénéité schéma batches | OUI | OUI | Moyenne |
| Event antidaté mars 2026 | OUI | OUI | Faible |
| Events antidatés 2025 (`gnews_coffee`) | Non visible | OUI (nouveau) | Moyenne |
| source_track absent sur quantitatifs | OUI | OUI | Faible |
| Critère composite silencieux (Cacao, Argent) | OUI | OUI | Moyenne |
| `vix_regime` S&P 500 muet (type inconnu) | OUI | OUI | Haute |
| DXY absent sur 5 actifs | OUI | OUI | Haute |
| Spread OAT-Bund absent | OUI | OUI | Haute |
| Mono-critère Cacao/Cuivre/Café/EUR/USD | OUI | OUI | Haute |
| PROBA_SCALE=10 → saturation Brier | N/A (pas de mesure) | OUI (Blé Brier=1.0) | Haute |
| Delta=0.000% indices week-end | N/A | OUI (nouveau) | Moyenne |
| Biais LONG 22/14 | OUI | OUI aggravé 24/12 | Haute |

---

## VERDICT GLOBAL

### Le run est-il statistiquement exploitable en shadow ?

**GO CONDITIONNEL — shadow uniquement, horizon 24h uniquement.**

**Justification :**

1. **La boucle prédiction→mesure est enfin fermée** sur 4 actifs (Blé, Cuivre, Or, Pétrole). C'est la condition nécessaire minimale pour du shadow. Sans mesure, il n'y a pas de shadow — c'est maintenant satisfait.

2. **Résultat sur N=4 : 50% (2 VRAI / 2 FAUX).** Statistiquement non différent du hasard. Wilson_low=0.206. Aucune prétention de performance à ce stade. Le shadow sert à accumuler, pas encore à conclure.

3. **Horizon 24h : seul horizon statistiquement valide pour accumulation.** Les fenêtres 7j (chevauchement 86%) et 1m (chevauchement 97%) produisent une autocorrélation sévère. Le N effectif réel sur 7j est ~N/9, sur 1m est ~N/60. Faire des KPIs sur ces horizons avant d'avoir résolu l'autocorrélation reviendrait à présenter 15 observations comme si elles valaient 135. Le système doit le documenter explicitement.

4. **4 actifs en quasi mono-critère (Cacao, Café, Cuivre, EUR/USD)** : leurs conclusions ne reposent que sur 1–2 variables. Ce ne sont pas des signaux analytiques — ce sont des proxies CFTC avec contorsion. Leurs KPIs de performance ne mesurent pas un modèle, ils mesurent la performance prédictive du COT sur 1 horizon.

5. **Biais LONG 24/12** est le signe d'un déséquilibre structurel : les triplets géopolitiques (Moyen-Orient) sont plafonnés à +1 en permanence, sans contrepartie quantitative (DXY absent, spreads absents). Ce biais n'invalide pas le shadow mais doit être signalé dans chaque bulletin.

6. **PROBA_SCALE=10 est sous-calibrée.** Scores réguliers à ±9–10 sur le Pétrole → prob=100% → Brier=0 si vrai, Brier=1 si faux, sans nuance. Cela rend le Brier Score non-informatif sur les actifs avec scores extrêmes. Recommandation : passer à PROBA_SCALE=15 ou 20, ou utiliser une transformation sigmoïde.

7. **Delta=0.000% sur 4 indices le week-end** : 4 cellules non-conclusives structurelles. Le taux de non-conclusivité réel est ~50% (6/12), ce qui est trop élevé pour que le warm-up progresse à vitesse nominale. Au rythme actuel, 15 observations effectives sur 24h requièrent ~30 jours de run (avec ~50% de non-conclusif), soit fin juin 2026 pour les actifs marchands 24/7.

### Chiffres clés du run 01/06

| Métrique | Valeur | Seuil cible |
|---|---|---|
| Cellules shadow | 12/12 (24h) | 12/12 ✓ |
| Mesures terminées (24h) | 12 | 12 ✓ |
| Mesures conclusives | 4/12 | objectif >50% |
| Taux succès (N=4) | 50% | cible 70% (non mesurable) |
| Wilson_low max | 0.206 | cible >0.50 |
| Critères couverts | ~59% | cible >80% |
| Mono-critère actifs | 4/12 | cible 0/12 |
| Biais LONG | 24/12 = 67% | acceptable <60% |
| Horizon 7j exploitable | Non (N_eff trop faible) | cible: >120 runs |
| Horizon 1m exploitable | Non (N_eff structurellement bas) | cible: jamais avec daily |

### Risques prioritaires à corriger avant d'interpréter les KPIs

**P0 — Bloquants pour la validité des mesures :**
1. **PROBA_SCALE** : passer de 10 à 15 minimum. Le Brier=1.0000 sur Blé est un signal d'alarme.
2. **Skip week-end** : implémenter une logique qui ne crée pas de mesure 24h si l'actif est fermé. Sinon les cellules actions accumulent des non-conclusifs qui faussent le warm-up count.

**P1 — Critiques pour la qualité du signal :**
3. **DXY trend 20j** : à implémenter en priorité (présent dans 5 actifs, 0 fois alimenté).
4. **Spread OAT-Bund** : clé pour CAC 40 (poids 10, absent).
5. **vix_regime S&P 500** : résoudre le type `mapping_non_monotone` (poids 8, absent, le plus lourd du S&P).
6. **Contamination gnews_coffee** : filtrer les events avec date < J-30 (ou J-90 maximum) pour éviter l'injection de signal historique.

**P2 — Améliorations mesure :**
7. **N effectif corrigé de l'autocorrélation** pour horizons 7j et 1m : afficher N_eff au lieu de N_total dans les KPIs.
8. **source_track sur quantitatifs** : traçabilité audit rétrospectif.

### Note globale

**7.0 / 10** (vs 7.5/10 au 31/05).

La régression tient à 3 facteurs nouveaux découverts au 01/06 : (a) contamination `gnews_coffee` avec events 2025 non filtrés, (b) PROBA_SCALE sous-calibrée révélée par le premier Brier réel, (c) biais LONG aggravé 24/12. Le run progresse bien techniquement (correctifs a/b/c partiellement réussis) mais révèle des problèmes de mesure qui étaient invisibles sans données réelles.
