# Mesure SHADOW — persistance « news vit tant que le quant ne la dément pas »

> Rapport NON commité. Pure lecture/agrégation de l'historique decision-log.
> ZÉRO changement de signal/score/conclusion. WIN-RATE hors périmètre (mesures structurelles).

- Généré : 2026-06-18T08:54:28
- Runs analysés : 57 fichiers JSONL | 2052 records (cellule×run)
- Fenêtre : 2026-05-30 → 2026-06-18 (17 bulletin_dates distincts)
- Seuils désaccord de référence : Analyst 15% / data-analyst 30%

Segmentation OBLIGATOIRE nature × horizon — les deux ne sont JAMAIS moyennés.

## ⭐ Synthèse pour décision

1. **Désaccord persistant — ALERTE.** Sur les news STRUCTURELLES aux horizons longs, le flag de divergence système (bruit déjà exclu) atteint **71%** (pire : 1m, 111/157 cellules) — **au-dessus des DEUX seuils** (15% Analyst / 30% data-analyst). Passer en persistance-until-quant-confirms SANS garde-fou figerait ces directions news alors que le quant les dément déjà majoritairement. → la persistance doit IMPÉRATIVEMENT être conditionnée à « quant ne dément pas ».
2. **Mort des critères — NON OBSERVABLE sur 17j.** Âge max = 28j < 30j, coef_nature min > 0. Ni le hard-drop 30j ni l'amortissement n'ont jamais tué un critère. La comparaison des deux régimes n'est PAS tranchable empiriquement aujourd'hui → raison d'être de l'instrumentation forward (Partie B).
3. **Promotion ponctuel→structurel : 0 candidat** (max récurrence ponctuel = 4 séances < seuil 5). Le risque « rater une tendance qui s'installe » ne s'est pas matérialisé sur la fenêtre, mais la fenêtre est courte.
4. **Détecteur de démenti textuel : 0 déclenchement** sur tout l'historique. Confirme le consensus des 3 experts : le démenti réel est QUANTITATIF, pas textuel. Garder DENIAL_KEYWORDS en shadow, ne pas l'armer.

> **Verdict seuils** : désaccord persistant structurel-long ≈ 69-71% ≫ 30% → la persistance « age-only » est DANGEREUSE pour les structurels. Le passage à « persist-until-quant-confirms » est cohérent SI ET SEULEMENT SI le quant garde le droit de véto (ce que mesure `persist_shadow_alive`/`quant_disconfirms`, Partie B).

## 1. Comment meurent les critères news aujourd'hui

Population de critères news par état (figée, état au moment du run — pas trajectoire). `amorti_avant_30j` = coef_nature tombé à 0 AVANT le filet d'âge. `hard_drop_30j` = âge ≥ 30j (le filet tranche). `vivant` = encore porté.

| nature | horizon | total | amorti<30j | hard-drop 30j | vivant | % amorti | % hard-drop |
|---|---|--:|--:|--:|--:|--:|--:|
| structurel | 24h | 342 | 0 | 0 | 342 | 0.0% | 0.0% |
| structurel | 7j | 342 | 0 | 0 | 342 | 0.0% | 0.0% |
| structurel | 1m | 342 | 0 | 0 | 342 | 0.0% | 0.0% |
| ponctuel | 24h | 101 | 0 | 0 | 101 | 0.0% | 0.0% |
| ponctuel | 7j | 101 | 0 | 0 | 101 | 0.0% | 0.0% |
| ponctuel | 1m | 101 | 0 | 0 | 101 | 0.0% | 0.0% |
| autre | 24h | 142 | 0 | 0 | 142 | 0.0% | 0.0% |
| autre | 7j | 142 | 0 | 0 | 142 | 0.0% | 0.0% |
| autre | 1m | 142 | 0 | 0 | 142 | 0.0% | 0.0% |


**⚠️ Fenêtre trop courte pour le hard-drop.** L'âge MAX observé sur tout l'historique est de **28.2 jours** (< 30). Le filet d'âge 30j n'a donc JAMAIS pu se déclencher. Tous les critères news sont encore « vivants » au sens âge. La mort, sur cette fenêtre, ne passe QUE par l'amortissement `coef_nature` (gradient ci-dessous), jamais par le hard-drop.

Gradient d'amortissement `coef_nature` observé (≠ kill brutal — modulation douce) :

| coef_nature | nb critères news |
|--:|--:|
| 0.10 | 8 |
| 0.15 | 101 |
| 0.20 | 8 |
| 0.30 | 8 |
| 0.50 | 101 |
| 0.80 | 342 |
| 1.00 | 785 |

> Lecture (intuition Newstrader, à confirmer sur fenêtre plus longue) : le `coef_nature` minimal observé est > 0 (jamais 0) → aucun critère n'est tué par amortissement sur cette fenêtre non plus. **Conclusion provisoire : sur 17 jours, AUCUN des deux mécanismes de mort n'a mordu.** La question « persistance vs hard-drop 30j » n'est donc PAS encore tranchable empiriquement — il faut accumuler des events qui dépassent 30j (instrumentation forward, Partie B).

## 2. Taux de désaccord persistant (proxy « retournement raté »)

### 2a. Vue DÉCISIONNELLE (niveau cellule) — proxy de référence

`flag_dis` = `divergence_quant_news=True` posé par le système (signes opposés ET les DEUX magnitudes > epsilon → exclut le bruit). C'EST le proxy le plus proche du « retournement raté ». `net_dis` = signe(news_total) net opposé au quant (plus large). Segmenté par nature DOMINANTE de la cellule × horizon.

| nature(dom) | horizon | cellules | flag divergence | % flag | vs 15% | vs 30% | net dis. | % net |
|---|---|--:|--:|--:|:--:|:--:|--:|--:|
| structurel | 24h | 157 | 76 | 48.4% | ⚠️ATT | ⚠️ATT | 77 | 49.0% |
| structurel | 7j | 157 | 108 | 68.8% | ⚠️ATT | ⚠️ATT | 111 | 70.7% |
| structurel | 1m | 157 | 111 | 70.7% | ⚠️ATT | ⚠️ATT | 114 | 72.6% |
| ponctuel | 24h | 67 | 26 | 38.8% | ⚠️ATT | ⚠️ATT | 33 | 49.3% |
| ponctuel | 7j | 67 | 23 | 34.3% | ⚠️ATT | ⚠️ATT | 33 | 49.3% |
| ponctuel | 1m | 67 | 24 | 35.8% | ⚠️ATT | ⚠️ATT | 34 | 50.7% |
| autre | 24h | 304 | 0 | 0.0% | ok | ok | 7 | 41.2% |
| autre | 7j | 304 | 1 | 0.3% | ok | ok | 9 | 52.9% |
| autre | 1m | 304 | 0 | 0.0% | ok | ok | 9 | 52.9% |

> Le `flag divergence` est le seuil que Thomas doit regarder : il EXCLUT déjà le bruit (petits désaccords négligeables). Si > 30% sur structurels longs → la persistance amplifierait un problème réel. Si < 15% → marge confortable.

### 2b. Vue STRICTE (par critère news individuel) — borne haute

Chaque voix news comptée séparément (une cellule à 3 news contre-quant = 3). SUR-estime le désaccord (ne déduplique pas les voix d'une même cellule). Borne haute.

| nature | horizon | voix éligibles | dément quant | confirme quant | % désaccord |
|---|---|--:|--:|--:|--:|
| structurel | 24h | 246 | 109 | 137 | 44.3% |
| structurel | 7j | 246 | 178 | 68 | 72.4% |
| structurel | 1m | 246 | 181 | 65 | 73.6% |
| ponctuel | 24h | 80 | 38 | 42 | 47.5% |
| ponctuel | 7j | 80 | 39 | 41 | 48.8% |
| ponctuel | 1m | 80 | 41 | 39 | 51.2% |
| autre | 24h | 22 | 8 | 14 | 36.4% |
| autre | 7j | 22 | 10 | 12 | 45.5% |
| autre | 1m | 22 | 10 | 12 | 45.5% |

## 3. TDL — Trend-Divergence Lag (runs entre bascule quant et flip conclusion)

Pour les events où le signe du quant a basculé : nb de runs jusqu'au flip de conclusion (ou fin d'event si pas de flip). Médiane par nature × horizon.

| nature | horizon | n events avec bascule | médiane lag (runs) | min | max |
|---|---|--:|--:|--:|--:|
| structurel | 24h | 2 | 0.0 | 0 | 0 |
| ponctuel | 24h | 3 | 1.0 | 0 | 1 |
| ponctuel | 7j | 4 | 0.5 | 0 | 7 |
| ponctuel | 1m | 5 | 1.0 | 0 | 7 |

> Lag élevé = la conclusion reste accrochée à la news longtemps après que le quant a tourné (retournement raté coûteux). Lag faible/0 = le système suit déjà le quant.

## 4. Candidats promotion ponctuel → structurel (> 5 séances)

Events classés `ponctuel` apparaissant sur > 5 bulletin_dates distincts (≈ séances) : la « nouvelle tendance qui s'installe » à ne pas rater.

- **Total candidats : 0**

_Aucun event ponctuel ne dépasse le seuil sur l'historique disponible (fenêtre 17j)._

Distribution de récurrence des events ponctuel (near-misses inclus, top 15) — permet de juger si le seuil de 5 séances est atteignable sur la fenêtre :

| event_id | actif | nb séances | première | dernière |
|---|---|--:|---|---|
| `4c495c7d569d` | nasdaq | 4 | 2026-06-05 | 2026-06-10 |
| `60b424d3caa9` | ble | 2 | 2026-06-01 | 2026-06-02 |
| `ac61cc5a9f44` | cacao | 2 | 2026-06-01 | 2026-06-02 |
| `d4c06b4ad629` | nasdaq | 2 | 2026-06-02 | 2026-06-03 |
| `dbf9364e740a` | or | 2 | 2026-06-08 | 2026-06-09 |
| `dbf9364e740a` | petrole | 2 | 2026-06-08 | 2026-06-09 |
| `dbf9364e740a` | vix | 2 | 2026-06-08 | 2026-06-09 |
| `af1792191952` | nasdaq | 2 | 2026-06-11 | 2026-06-12 |
| `f8ac42ecf6c4` | nasdaq | 2 | 2026-06-15 | 2026-06-16 |
| `3a1ea0ee1c97` | nasdaq | 1 | 2026-06-01 | 2026-06-01 |
| `15b7dff53af3` | or | 1 | 2026-06-01 | 2026-06-01 |
| `15b7dff53af3` | petrole | 1 | 2026-06-01 | 2026-06-01 |
| `15b7dff53af3` | vix | 1 | 2026-06-01 | 2026-06-01 |
| `2535780fbc6f` | nasdaq | 1 | 2026-06-03 | 2026-06-03 |
| `768c85013696` | nasdaq | 1 | 2026-06-04 | 2026-06-04 |

## 5. Détecteur de démenti (DENIAL_KEYWORDS) — SHADOW, non armé

- **Déclenchements `is_denial=True` sur l'historique : 0**

_Aucun déclenchement sur l'historique : le détecteur de mots-clés n'a JAMAIS matché. Confirme le consensus des 3 experts : le « démenti » réel n'est pas textuel mais quantitatif (le quant qui se retourne). À labelliser si des triggers apparaissent aux prochains runs réels._

---

### Notes méthodo (anti-invention)
- Mesure population (état figé par run), pas suivi continu d'un même critère, sauf TDL/4 qui reconstruisent une trajectoire via `event_id`.
- Records sans `quant_total` (versions anciennes du writer) exclus des mesures 2 et 3.
- `nature='verbal'`/absente repliée dans `autre` (jamais comptée comme structurel/ponctuel).
