# Audit de fiabilité — Bulletin réel v3.0.0 — 2026-05-31

Auditeur : @data-analyst | Cycle : premier bulletin réel, 36 cellules (12 actifs × 3 horizons)

---

## 1. Intégrité des valeurs

**Normalisations dans [-1, 1] :** aucune violation. Toutes les valeurs normalisées observées sont dans la plage attendue. Le seul cas limite est CFTC COT Copper nets = +1.000 (z-score saturé en borne haute) et Term structure VIX/VIX3M = -1.000 (valeur linéaire saturée) : les deux sont cohérents avec les formules déclarées dans les notes de calcul, pas aberrants.

**Nouvelles sources câblées ce cycle :**
- TIPS (taux 10Y réels) : valeur 2.06%, normalisée +0.498 — plausible (taux réels élevés en 2026, z-score < 1, aucune anomalie).
- HY credit spread (ICE BofA) : valeur 2.72%, normalisée -0.610 — serré par rapport aux historiques récents, signe négatif cohérent (spread bas = favorable actions). Plausible.
- SKEW CBOE : valeur 148.7, normalisée +0.913 (centre=135, échelle=15) — SKEW à 148.7 est effectivement élevé (queue gauche coûteuse), signe LONG VIX cohérent avec le contexte.
- VVIX : valeur 92.67, normalisée -0.155 (centre=95, échelle=15) — légèrement sous la moyenne, signe négatif (faible vol-de-vol = calme). Plausible.
- Météo agri (NOAA drought, météo Australie) : z-scores faibles (+0.105, -0.043) — aucune anomalie.

**Valeurs suspectes / signaux d'alerte :**
- Caixin PMI (Argent, Cuivre, Pétrole) : valeur brute = 0.0 avec note "hors fenêtre". Le score 0.0 est neutralisé mais la valeur brute nulle est trompeuse — ce n'est pas un PMI de 0 mais une donnée absente traitée en zéro. Risque de mauvaise interprétation dans les logs sans la note.
- CFTC COT Copper nets à 73 313 nets longs saturé à +1.000 : ce plafonnement est intentionnel mais masque l'amplitude réelle du positionnement.

**Anomalie de signe à investiguer — Or :**
TIPS 10Y réels à 2.06% donne une contrib négative (-2.99 à 24h) → pousse le score Or vers SHORT. Or un TIPS élevé supprime bien le prix de l'or (coût d'opportunité). Le signe -1 est économiquement correct. Mais la tension géopolitique (triplet +1, poids 5) pousse +4.0 en ±1. Le résultat net 24h = -0.126 (SHORT de justesse) reflète un moteur réellement tiraillé — ce n'est pas un bug, c'est une vraie tension de marché.

---

## 2. Traçabilité decision-log

**Cellules vérifiées à la main (reconstitution des scores) :**

| Cellule | Score reconstitué | Score log | Écart |
|---|---|---|---|
| Argent 24h | -1.9912 +0.7622 +2.1000 -0.9017 +0.2266 -0.0996 = **+0.0963** | 0.096311 | < 0.0001 ✓ |
| S&P 500 24h | +1.0825 +2.1345 +0.5498 +0.0087 = **+3.7755** | 3.775435 | < 0.0001 ✓ |
| VIX 1m (diverge) | pm1 = +2.525 -4.8 +1.370 -0.233 +0.188 +1.200 = **+0.250** / pond = idem sauf tension +0.504 → **-0.446** | 0.249546 / -0.446454 | < 0.0001 ✓ |

La formule `score = Σ(norm × signe × poids × pertinence)` est rigoureusement respectée sur les trois cellules testées. La diverge=true sur VIX 1m est arithmétiquement correcte. Le log est complet : 36 entrées pour 12 actifs × 3 horizons, toutes timestampées, toutes avec les champs critères détaillés.

---

## 3. ±1 vs pondéré — divergences

**Nombre de cellules divergentes : 1 sur 36** (VIX 1m uniquement).

Distribution des écarts pm1 vs pond :
- 25 cellules : score_pm1 = score_pond (actifs sans pondération triplet active)
- 10 cellules : écart matériel (actifs avec triplets géopolitiques ou cicle saisonnier actifs)
- 1 cellule seule bascule de direction : VIX 1m (pm1 LONG +0.25, pond SHORT -0.45)

Le pondéré est systématiquement plus conservateur que le ±1 sur les actifs géopolitico-dependants (Blé, Pétrole, Or, VIX) : les triplets pondérés à facteur 0.42 atténuent l'impact des news. C'est le comportement attendu. Aucune inflation pathologique détectée.

---

## 4. Biais directionnel — compte LONG/SHORT

| Direction | Cellules | % |
|---|---|---|
| **LONG** | **23** | 63.9% |
| **SHORT** | **13** | 36.1% |

Détail SHORT : Café 3×, Cuivre 3×, Nasdaq 3×, Or 3×, EUR/USD 24h (1×). Détail LONG : Argent 3×, Blé 3×, CAC 3×, Cacao 3×, EUR/USD 7j+1m, Pétrole 3×, S&P 500 3×, VIX 3× (dont 1 seul en pm1).

**Verdict biais :** le ratio 23/13 n'est pas pathologique pour un environnement de marché avec géopolitique active (Moyen-Orient, mer Noire), ralentissement chinois et taux élevés. Il n'y a pas de biais structurel de calibration (pas de 30/6 ou inversement). L'actif VIX à LONG alors que S&P est LONG est la seule tension logique notable — elle est réelle (SKEW élevé + géopolitique) et documente une couverture latente.

---

## 5. Couverture réelle — critères effectivement alimentés par actif

| Actif | Critères total | Alimentés | Taux | Critique manquant |
|---|---|---|---|---|
| Argent | 9 | 6 | 67% | Inventaires COMEX, demande PV |
| Blé | 9 | 4 | 44% | USDA WASDE, NASS crop, Égypte GASC, DXY |
| CAC 40 | 7 | 3 | 43% | V2X, OAT-Bund, breadth |
| Cacao | 8 | 4 | 50% | Arrivées port, spread NY-London |
| Café | 8 | 3 | 38% | Météo Brésil (poids 11!), stocks ICE, spread |
| Cuivre | 8 | 2 | 25% | Caixin PMI, LME+SHFE stocks, DXY, term structure, Cu/Or |
| EUR/USD | 8 | 2 | 25% | Différentiel taux 2Y (poids 12!), DXY, FedWatch, OAT-Bund |
| Nasdaq | 9 | 3 | 33% | VXN, SOX, breadth, concentration top 7, spread Russell |
| Or | 8 | 5 | 63% | PBoC achats, DXY |
| Pétrole | 10 | 5 | 50% | Term structure, DXY, spread Brent-WTI, EIA/API hors fenêtre |
| S&P 500 | 8 | 4 | 50% | VIX régime, breadth, DXY, AAII, CAPE |
| VIX | 8 | 6 | 75% | Put/Call ratio, Gap RV-IV |

**Actifs fragiles (≤ 2 critères actifs) :**
- **EUR/USD** : 2 critères actifs seulement. Le critère manquant le plus lourd est le différentiel taux 2Y US-DE (poids 12, le plus élevé de la fiche) — absent. La conclusion repose sur USD/JPY et CFTC COT uniquement. Haute fragilité structurelle.
- **Cuivre** : 2 critères actifs. Le Caixin PMI est traité "hors fenêtre" (neutre), réduisant la couverture à CFTC COT seul pour les conclusions SHORT. Le verdict -1.0 / -3.5 / -5.0 repose sur un seul critère quantitatif réel.

**Actif mono-critique :** Cuivre — les 3 scores SHORT sont intégralement déterminés par CFTC COT Copper nets (+1.000 saturé). Si cette valeur est erronée, les 3 cellules basculent.

---

## Risques systémiques identifiés

1. **DXY absent sur 6 actifs simultanément** (Blé, CAC, Cuivre, EUR/USD, Or, Pétrole, S&P 500) — critère transversal non câblé. Impact immédiat si le dollar bouge violemment.
2. **Cuivre mono-critique** : les 3 cellules SHORT (-1 / -3.5 / -5) reposent sur un seul z-score COT saturé. Zéro redondance.
3. **EUR/USD sous-alimenté** : le critère poids 12 (différentiel 2Y) est absent. Le signal de cette paire est structurellement peu fiable ce cycle.
4. **Triplets géopolitiques à facteur 0.42 sur 5 actifs simultanément** (Blé, Or, Pétrole, VIX, Café) : un seul fournisseur de signal de crise. Si la détection keyword rate un événement ou en double-compte un, 5 actifs sont affectés corrélativement.

---

## VERDICT

**Pipeline sain : SOUS CONDITIONS**

**Note : 6.5/10**

- Le moteur arithmétique est fiable : 3/3 cellules vérifiées à la main, zéro erreur de calcul, log complet et traçable.
- Les nouvelles sources (TIPS, HY, SKEW, VVIX, météo) produisent des valeurs plausibles et bien signées.
- Le ratio LONG/SHORT (23/13) est économiquement justifiable, pas symptomatique d'un biais de calibration.
- **Condition 1 (bloquante) :** câbler DXY trend 20j — absent sur 6 actifs, c'est le risque systémique n°1 de ce cycle.
- **Condition 2 (haute priorité) :** Cuivre et EUR/USD sont structurellement fragiles (≤ 2 critères actifs). Les conclusions sur ces actifs doivent être accompagnées d'un avertissement de confiance faible dans le bulletin.
- **Condition 3 :** traiter "Caixin PMI = 0.0 hors fenêtre" comme `null` dans les logs, pas comme valeur numérique 0 — risque de confusion dans les audits futurs.
- **Condition 4 (moyen terme) :** l'alignement triplets géopolitiques sur 5 actifs via keyword-detection crée une corrélation artificielle lors des chocs. Envisager une pondération différenciée par actif ou une gate de corrélation max.
