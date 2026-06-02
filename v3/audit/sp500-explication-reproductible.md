# S&P 500 — Pourquoi SHORT le 2026-06-02 (explication reproductible)

> **Objectif** : reconstituer chiffre-pour-chiffre les scores SHORT affichés du S&P 500
> (24h = **-5.94** · 7j = **-4.82** · 1m = **-3.82**, coverage **51 %**), à partir des
> données réellement utilisées et de la vraie formule du moteur. Pas de narration : tout
> se recalcule.

## 0. Source de vérité utilisée

Les scores affichés dans le tableau du bulletin (`v3/data/bulletins/bulletin-2026-06-02.md`,
ligne `| S&P 500 | SHORT ● | SHORT ● | SHORT ● |`) correspondent **exactement** au run
**`v3/data/decision-log/2026-06-02-1415.jsonl`** (`generated_at: 2026-06-02T14:15:08+02:00`).

Vérification : seul ce run produit `sp500 24h=-5.939769 / 7j=-4.820566 / 1m=-3.822578`
et `coverage=0.5082`. (Les runs plus tardifs 16h25 et 18h04 donnent des scores voisins mais
différents — le tableau publié fige les chiffres du run 14h15.) Toutes les valeurs ci-dessous
sont **lues** dans ce fichier, aucune n'est inventée.

## 1. La formule réelle d'agrégation

Source : `v3/scripts/scoring_analyste.py`, fonction `score_actif`, lignes **677-680** :

```python
pert_eff = pertinence[h] * coef_nature_h[h]          # L677
contributions[h]      = valeur_norm * poids * pert_eff * signe   # L678
contributions_pond[h] = vp         * poids * pert_eff * signe    # L680
```

Puis le score d'un horizon = **somme brute des contributions** (boucle L786+, `quant_total = sum(quant_contribs)` ;
le S&P n'a aucun critère news ce run, donc `score = Σ contributions`).

Points clés, **vérifiés dans le code, pas devinés** :
- **Pas** de division par `Σ poids` : le score n'est pas une moyenne pondérée, c'est une **somme**. Le coverage est calculé séparément (`compute_coverage`, L515-518) et sert au gating de confiance, **pas** à normaliser le score.
- **Pas** de scaling ×10 ni autre : les poids de fiche (2 à 10) sont déjà l'échelle.
- `coef_nature = 1.0` pour tous les critères quant (non-news) du S&P → `pert_eff = pertinence[h]`.
- `facteur = 1.0` partout ici (aucun cap news/quant déclenché : `news_total = 0`).
- Garde-fou `reconcile_score` (L191-217) garantit `Σ contributions = score` à 1e-9 près.

Donc, par critère et par horizon : **contribution = valeur_normalisee × poids × pertinence[h] × signe**.

## 2. Tableau par critère présent (valeurs du run 14h15)

5 critères présents (sur 10 de la fiche). `valeur_normalisee` et `signe` identiques aux 3 horizons ;
seule la `pertinence[h]` change.

| Critère | valeur_norm | signe | poids | pert 24h | pert 7j | pert 1m |
|---|---:|---:|---:|---:|---:|---:|
| hy_credit_spread | -0.5224 | -1 | 7 | 0.5 | 1.0 | 0.9 |
| breadth_sp_ma50 (proxy RSP/SPY) | -0.6311 | +1 | 7 | 0.9 | 0.8 | 0.5 |
| flux_etf_spy_ivv_5j | +0.2411 | +1 | 5 | 0.4 | 1.0 | 0.7 |
| rsi_14j_gspc | +1.0000 | -1 | 2 | 0.8 | 0.4 | 0.2 |
| taux_10y_us_reels_tips | +0.5349 | -1 | 10 | 0.5 | 1.0 | 1.0 |

### Contributions signées par horizon (= valeur_norm × poids × pertinence × signe)

| Critère | contrib 24h | contrib 7j | contrib 1m |
|---|---:|---:|---:|
| hy_credit_spread | **+1.828** | **+3.657** | **+3.291** |
| breadth_sp_ma50 | **-3.976** | **-3.534** | **-2.209** |
| flux_etf_spy_ivv_5j | +0.482 | +1.206 | +0.844 |
| rsi_14j_gspc | -1.600 | -0.800 | -0.400 |
| taux_10y_us_reels_tips | **-2.674** | **-5.349** | **-5.349** |
| **SOMME (score reconstitué)** | **-5.940** | **-4.821** | **-3.823** |

## 3. Reconstitution vs score affiché

| Horizon | Score reconstitué | Score affiché | Écart |
|---|---:|---:|---:|
| 24h | -5.940 | -5.94 | +0.0002 |
| 7j | -4.821 | -4.82 | -0.0009 |
| 1m | -3.823 | -3.82 | -0.0029 |

**OUI, la formule reconstitue les scores.** Les écarts (< 0.003) viennent uniquement de
l'arrondi des `valeur_normalisee` recopiées à 4 décimales ; avec les valeurs pleine précision
du décision-log, l'égalité est exacte (le garde-fou `reconcile_score` l'impose à 1e-9).
**Aucun terme manquant, aucun scaling caché, aucune intervention du gate.**

Script de vérification (sans réseau, valeurs en dur lues dans le décision-log) : voir bloc en annexe.

## 4. Critères ABSENTS — l'origine du coverage 51 %

Coverage = Σ poids présents / Σ poids fiche (non-gate) = **31 / 61 = 50.8 % ≈ 51 %**
(`compute_coverage`, L515-518 ; valeur stockée `coverage=0.5082`).

5 critères de la fiche `sp500.yml` sont **absents** du run (49 % du poids manquant) :

| Critère absent | poids | rôle attendu |
|---|---:|---|
| **vix_regime** | 8 | régime de volatilité |
| **taux_10y_us_delta_5j** | 9 | momentum taux nominaux |
| **dxy_trend_20j** | 5 | tendance dollar |
| **aaii_bull_bear** | 4 | sentiment contrarian |
| **shiller_cape_fwd_pe** | 4 | valorisation |

Le S&P est donc jugé sur **la moitié de son tableau de bord** seulement (motif des
drapeaux `[⚠️ ⇄]` du bulletin : couverture faible + flip).

## 5. La vraie raison du SHORT (basée sur les contributions dominantes réelles)

Le SHORT n'est **pas** « le marché a peur ». Il vient de **deux contributions négatives
qui écrasent tout** :

1. **Taux réels 10Y (TIPS) élevés** — `valeur_norm = +0.535` (z-score positif → taux réels
   au-dessus de leur moyenne 60j), `signe = -1`, `poids = 10`. C'est le critère le plus lourd
   de la fiche. Contribution : **-2.67 (24h)**, **-5.35 (7j et 1m)**. À 7j/1m c'est à lui seul
   plus que le score final.
2. **Breadth interne dégradée** (proxy RSP/SPY) — `valeur_norm = -0.631` (equal-weight
   sous-performe cap-weight → rallye porté par les méga-caps, participation étroite),
   `signe = +1`. Contribution : **-3.98 (24h)**, -3.53 (7j), -2.21 (1m). Critère dominant à 24h.

Ces deux postes (taux réels chers + breadth étroite) sont **partiellement compensés** par
deux signaux positifs : le **HY credit spread resserré** (`valeur_norm = -0.522`, signe -1 →
contrib **positive** +1.8 à +3.7, crédit calme = soutien) et des **flux ETF légèrement
entrants** (+0.5 à +1.2). Le RSI neutre-haut (=1.0 cappé, signe -1) ajoute un petit SHORT.

**Bilan** : le négatif (taux réels + breadth) l'emporte nettement → SHORT sur les 3 horizons.
À 7j/1m, c'est surtout les **taux réels** ; à 24h, c'est surtout la **breadth**.

## 6. Drapeau honnête — l'anomalie vix_regime

La mission signale un `vix_regime = +1.0` à VIX 23.9 jugé incohérent avec la fiche
(`mapping_non_monotone` : +1 au centre ~15, -1 aux extrêmes ; à VIX 23.9 on attendrait du
négatif). **Dans le run reconstitué ici, `vix_regime est tout simplement ABSENT`** du bloc
sp500 du décision-log : il n'a pas été calculé, il fait partie des 49 % de coverage manquant
(et le bloc `vix:` de `criteres-courants.md` porte un `niveau_vix_absolu = 14.95`, pas 23.9).

**Conséquence sur la conclusion** : **AUCUNE.** Comme vix_regime n'entre pas dans la somme,
il ne pèse pas un gramme sur les -5.94 / -4.82 / -3.82. Le SHORT tient **uniquement** sur les
taux réels et la breadth. L'anomalie +1.0 @ 23.9 (si elle apparaît dans un autre run, ex.
16h25/18h04) est à investiguer séparément, mais elle **ne change pas** le bulletin publié
(run 14h15) — qui est reconstitué TEL QUEL ci-dessus.

> Note : si vix_regime avait été présent et coté correctement négatif à VIX élevé (signe +1
> de la fiche × valeur_norm négative = contribution **négative**), il aurait **renforcé** le
> SHORT, pas l'inversé. Le sens de la conclusion est donc robuste à cette anomalie.

---

## Annexe — script de reconstitution (offline, valeurs lues dans le décision-log)

```python
# Formule scoring_analyste.py L678 : contrib = valeur_norm * poids * pertinence[h] * signe
# (coef_nature=1.0 pour les critères quant du S&P → pert_eff = pertinence)
criteres = {
  "hy_credit_spread":       dict(vn=-0.5224, signe=-1, poids=7,  pert={"24h":0.5,"7j":1.0,"1m":0.9}),
  "breadth_sp_ma50":        dict(vn=-0.6311, signe=1,  poids=7,  pert={"24h":0.9,"7j":0.8,"1m":0.5}),
  "flux_etf_spy_ivv_5j":    dict(vn=0.2411,  signe=1,  poids=5,  pert={"24h":0.4,"7j":1.0,"1m":0.7}),
  "rsi_14j_gspc":           dict(vn=1.0,     signe=-1, poids=2,  pert={"24h":0.8,"7j":0.4,"1m":0.2}),
  "taux_10y_us_reels_tips": dict(vn=0.5349,  signe=-1, poids=10, pert={"24h":0.5,"7j":1.0,"1m":1.0}),
}
cibles = {"24h":-5.94, "7j":-4.82, "1m":-3.82}
for h in ["24h","7j","1m"]:
    s = sum(c["vn"]*c["poids"]*c["pert"][h]*c["signe"] for c in criteres.values())
    print(h, "reconstitue=%.4f  cible=%.2f  ecart=%+.4f" % (s, cibles[h], s-cibles[h]))
# 24h reconstitue=-5.9398  cible=-5.94  ecart=+0.0002
# 7j  reconstitue=-4.8209  cible=-4.82  ecart=-0.0009
# 1m  reconstitue=-3.8229  cible=-3.82  ecart=-0.0029
```

**Conclusion** : formule reproduit les scores (écart < 0.003, dû à l'arrondi). SHORT confirmé,
porté par **taux réels TIPS** (7j/1m) et **breadth interne étroite** (24h).
