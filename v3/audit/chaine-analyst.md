# Audit delta ANALYST — run 18h00 (2026-06-01T18:20:26)
> 1er run CRON avec plan horizon actif. Auditeur : expert ANALYST (rigueur statistique/mesure).
> Ordre d'édition : criteres-courants → bulletin → decision-log → performance → performance-ab

---

## 1. Intégrité temporelle et déclenchement CRON

| Point | Statut | Détail |
|---|---|---|
| Timestamp génération | OK | 2026-06-01T18:20:26.471941+02:00 |
| Cohérence criteres-courants | OK | `last_update: 2026-06-01T16:20:26` (UTC = 18h20 CEST) — cohérent |
| Déclenchement CRON | CONFORME | Premier run schedule du jour avec plan horizon actif |
| Doublon anti-guard | N/A | Aucun run 18h antérieur détecté dans les logs |

---

## 2. Plan horizon — vérification actif par actif

### 2.1 Or — SHORT ×3 horizons

| Horizon | Score ±1 | Score pond | Conclusion | Ratio news | Cap appliqué |
|---|---|---|---|---|---|
| 24h | -1.544 | -2.544 | SHORT | 61,8 % | NON |
| 7j | -3.240 | -4.040 | SHORT | 38,2 % | NON |
| 1m | -2.293 | -2.893 | SHORT | 39,5 % | NON |

**Analyse :**
Le plan horizon a bien corrigé Or SHORT sur les 3 horizons. Le moteur numérique est le TIPS 10Y réels (z=2.06, contrib -2.99 à -5.97 selon horizon) — bear majeur pour l'or. La tension géopolitique (triplet=+1, medium/confirmed) contribue LONG à +1.5/+2.0/+2.5 mais est écrasée par TIPS.

Or 24h à ratio_news=61,8 % : le drapeau 📰 du bulletin est CORRECT (>50 %). Le cap anti-inversion news n'est PAS activé (`news_cap_applied: false`). Explication : le signe news (LONG via géopolitique) et le signe quant (SHORT via TIPS) sont OPPOSÉS — le cap ne joue que si la news inverserait la conclusion finale. Ici quant_total=-4.04 est déjà très SHORT ; la news ne peut pas inverser. Comportement CORRECT.

Cohérence mesure : Or SHORT mesuré VRAI sur le run du 31/05 (delta=-1.684% vs seuil=0.5%). Le plan horizon maintient SHORT — continuité logique valide.

### 2.2 VIX — SHORT ×3 horizons

| Horizon | Score ±1 | Score pond | Conclusion | Ratio news | Cap appliqué |
|---|---|---|---|---|---|
| 24h | -0.530 | -0.530 | SHORT | 0,0 % | NON |
| 7j | -0.627 | -0.627 | SHORT | 0,0 % | NON |
| 1m | -0.950 | -0.950 | SHORT | 0,0 % | NON |

**Analyse :**
Plan horizon appliqué : VIX SHORT sur les 3 horizons, sans news (ratio_news=0 partout — aucun triplet news activé pour VIX ce run). Pertinences recalibrées visibles : term_structure VIX/VIX3M pertinence 0.8/1.0/0.6 selon horizon — décroissance correcte à 1m. VIX absolu=14.95 (< 18 centre) pousse SHORT ; term_structure=0.822 (contango inverse fort) pousse SHORT. Cohérent.

Zéro drapeau 📰 sur VIX — CORRECT (ratio_news=0).

Avertissement marginal : scores faibles (-0.53 à -0.95). Un retour du VIX vers 20+ inverserait la conclusion. Sensibilité élevée à la normalisation linéaire (centre=20, échelle=10).

### 2.3 Nasdaq — SHORT ×3 horizons avec 📰

| Horizon | Score ±1 | Score pond | news_total | quant_total | ratio_news | Cap appliqué | Cap override |
|---|---|---|---|---|---|---|---|
| 24h | -0.00174 | -0.00174 | +4.0 | -0.00871 | **459 %** | **OUI** | NON |
| 7j | -0.428 | -0.428 | +4.5 | -2.141 | **210 %** | **OUI** | NON |
| 1m | -1.807 | -2.807 | +2.5 | -4.307 | 58 % | NON | NON |

**Analyse critique — Nasdaq 24h :**

Le score final -0.00174 est un quasi coin-flip absolu. Décomposition :
- TIPS 10Y (z=2.06) : contrib -2.738 (SHORT fort)
- SOX trend 5j (z=0.885) : contrib +5.574 (LONG fort — SOX à 571, très haussier)
- Sentiment IA méga-caps (triplet=+1, medium/confirmed) : contrib_pm1=+4.0, contrib_pond=+2.4
- Flux ETF QQQ : +0.614
- Spread Nasdaq-Russell : -1.859
- RSI 14j IXIC (78.1) : -1.6

Résultat quant seul : -0.009 — signal numérique presque nul. La news (ratio_news=459%) a été cappée via `news_cap_applied: true`. Sans le cap, le score serait LONG (news_total=+4.0 dominerait). Le cap a maintenu SHORT en retenant la composante news dominante haussière.

**Robustesse du SHORT Nasdaq 24h : FRAGILE.** Mathématiquement, le signal est à ±0.002 d'un coin-flip. Le moteur penche SHORT grâce au spread TIPS défavorable et au RSI suracheté, mais SOX et sentiment IA sont massivement LONG. Ce résultat n'est PAS une conviction directionnelle — c'est une quasi-neutralité que l'architecture traduit en SHORT par défaut (règle "jamais neutre"). Le drapeau 📰 est JUSTIFIÉ, mais un disclaimer opérationnel s'impose.

**Nasdaq 7j :** score -0.428 — plus robuste. quant_total=-2.141 (TIPS dominent clairement sur SOX à pertinence 1.0). Cap news appliqué (ratio_news=210%). Verdict: conviction SHORT modérée acceptable.

**Nasdaq 1m :** score -1.807 / pond -2.807. quant_total=-4.307 — TIPS+Spread-Russell très pesants. Ratio_news=58% d'où le drapeau 📰 CORRECT. Cap_applied=FALSE car la news tire LONG mais ne peut inverser un quant SHORT à -4.3. Cohérent avec le design.

**Verdict Nasdaq :** Le flip LONG→SHORT sur les 3 horizons entre midi et 18h est réel mais structurellement différent selon l'horizon. Le 24h est quasi-neutralité tranchée par défaut SHORT — signal non exploitable opérationnellement sans disclaimer fort.

---

## 3. Drapeaux 📰 — vérification exhaustive ratio_news

| Actif | Horizon | ratio_news (décision-log) | 📰 affiché bulletin | Correct ? |
|---|---|---|---|---|
| Blé | 24h | 57,2 % | OUI | CORRECT |
| Blé | 7j | **18,4 %** | OUI | **ANOMALIE** |
| Blé | 1m | **5,7 %** | OUI | **ANOMALIE** |
| Nasdaq | 24h | 459 % | OUI | CORRECT |
| Nasdaq | 7j | 210 % | OUI | CORRECT |
| Nasdaq | 1m | 58 % | OUI | CORRECT |
| Or | 24h | 61,8 % | OUI | CORRECT |
| Or | 7j | 38,2 % | NON | CORRECT (pas de drapeau) |
| Or | 1m | 39,5 % | NON | CORRECT (pas de drapeau) |
| Pétrole | 24h | 607 % | OUI | CORRECT |
| Pétrole | 7j | 363 % | OUI | CORRECT |
| Pétrole | 1m | 285 % | OUI | CORRECT |

**Anomalie Blé 7j et 1m :** Le bulletin affiche 📰 sur les 3 horizons du Blé. Mais le decision-log indique ratio_news=18.4% (7j) et 5.7% (1m) — largement sous le seuil 50%. Le drapeau 📰 est incorrect sur Blé 7j et 1m. Cause probable : le bulletin génère le drapeau à partir de `news_dominant: true` (présent pour les 3 horizons Blé dans le JSONL) plutôt que du ratio_news brut. Or `news_dominant` est vrai dès lors que |news_total| > |quant_total| — ce qui est une définition différente de "news > 50% du score total". **BUG à corriger : la logique drapeau 📰 doit utiliser `ratio_news > 0.5`, pas `news_dominant`.**

---

## 4. Analyse mesure — Brier et warm-up

### 4.1 État global

- Observations avec mesure terminée : 6 cellules avec N_eff ≥ 1 (sur 12), toutes en horizon 24h uniquement
- Toutes autres cellules (7j, 1m) : 0 mesure terminée (fenêtres non échues)
- Statut : warm-up, N_eff max = 1/15 requis pour déclarer éligibilité

### 4.2 Scores Brier (PROBA_SCALE=15)

| Actif | Conclusion | Outcome | Brier ±1 | Brier pond |
|---|---|---|---|---|
| Argent | SHORT | VRAI | 0.1464 | 0.1464 |
| Café | LONG | FAUSSE | 0.3729 | 0.3560 |
| Cuivre | SHORT | FAUSSE | 0.2663 | 0.2663 |
| EUR/USD | SHORT | VRAI | 0.2203 | 0.2203 |
| Or | SHORT | VRAI | **0.0435** | 0.0484 |
| Pétrole | LONG | VRAI | **0.0000** | 0.0364 |

**Lecture critique :**

Brier < 0.25 (cible KPI) : 4/6 cellules respectent la cible sur N=1. Aucune significativité statistique — valeurs indicatives de calibration de la proba émise uniquement.

Or : Brier=0.0435. Score=-1.544 → proba=0.5+min(1.544/15, 0.5)=0.603. Issue VRAI avec delta=-1.684% — calibration saine.

Pétrole : Brier=0.0000 (±1). Score=+6.989 → proba=1.0. Delta=+6.685% — la certitude était justifiée. Le pondéré donne 0.0364 (proba=0.806) — moins confiant mais toujours VRAI, cohérent avec l'atténuation par le cap.

Café (score +0.15 → proba=0.510) et Cuivre (score -0.28 → proba=0.519) : Brier élevés mais probabilités quasi-50%. Le système est honnête sur son incertitude — comportement correct pour des scores marginaux.

**PROBA_SCALE=15 sain à ce stade :** pas de saturation pathologique, pas de sur-confiance sur les signaux faibles.

### 4.3 Warm-up — projection

| Horizon | Mesures disponibles | Seuil N_eff | Estimation délai |
|---|---|---|---|
| 24h | 1/15 | 15 obs non-chevauchantes | ~15 jours shadow |
| 7j | 0/15 | 15 obs | ~15 semaines |
| 1m | 0/15 | 15 obs | ~15 mois |

8 cellules marquées "suivi-interrompu" (30/05 sans prix d'émission) correctement exclues du calcul.

---

## 5. Performance A/B

- N=6 cellules avec mesure pondérée (uniquement 24h du 31/05)
- Delta taux moyen pondéré − ±1 : **+0.00 pts** sur 6 cellules (stochastique à N=1)
- Brier pondéré légèrement dégradé sur Or (0.0484 vs 0.0435) et Pétrole (0.0364 vs 0.0000) : cohérent — le pondéré atténue les scores extrêmes et réduit la proba sur les issues certaines
- Café pondéré légèrement meilleur (0.3560 vs 0.3729) : le poids réduit sur Cycle Brésil (-0.42) atténue la confiance dans la mauvaise direction
- Conclusion A/B : trop tôt. Le pondéré est conçu pour performer sur du volume — 1 observation est du bruit pur.

---

## 6. Synthèse delta vs run midi

| Actif | Run 12h | Run 18h | Delta notable |
|---|---|---|---|
| Or | SHORT ×3 | SHORT ×3 | Stable, plan horizon confirmé |
| VIX | SHORT ×3 | SHORT ×3 | Stable |
| Nasdaq | LONG ≥1 horizon | SHORT ×3 | **Flip majeur — quasi coin-flip 24h** |
| Blé | SHORT ×3 | SHORT ×3 | Stable, mer Noire dominant |
| Pétrole | LONG ×3 | LONG ×3 | Stable, géopolitique dominant |
| Argent | SHORT | LONG ×3 | Flip via ratio Gold/Silver |
| Café | LONG ×3 | LONG 24h/7j, SHORT 1m | Divergence ±1 vs pond sur 1m |
| Cuivre | SHORT | LONG 24h, SHORT 7j/1m | Flip 24h via ratio Cuivre/Or |

---

## 7. Verdict GO/NO-GO mesure

**Intégrité pipeline : GO**
37 lignes JSONL, toutes cohérentes avec le bulletin (scores vérifiés sur Or, Nasdaq, VIX, Pétrole). Timestamps cohérents entre criteres-courants, decision-log et bulletin. CRON déclenché correctement.

**Plan horizon : GO avec réserve**
- Or SHORT : bien appliqué, confirmé par mesure VRAI antérieure. 
- VIX SHORT : bien appliqué, scores faibles mais cohérents.
- Nasdaq SHORT : appliqué mais 24h est un quasi coin-flip (-0.002) — signal non fiable opérationnellement sur cet horizon seul.

**Drapeaux 📰 : GO partiel**
- Nasdaq, Or 24h, Pétrole : corrects.
- Blé 7j et 1m : ANOMALIE — drapeau affiché à tort (ratio_news 18% et 6% < seuil 50%). Bug logique `news_dominant` vs `ratio_news > 0.5` à corriger.

**Mesure / Brier : GO (warm-up)**
- PROBA_SCALE=15 : calibration saine sur les 6 observations disponibles.
- 4/6 Brier < 0.25 au N=1 — pas de signal d'alarme.
- Warm-up confirmé, aucune décision KPI possible avant N_eff ≥ 15.

---

## Note globale : **7.5 / 10**

**Déductions :**
- -1.5 : Nasdaq 24h quasi coin-flip traduit en conviction SHORT sans disclaimer — signal non exploitable opérationnellement
- -0.5 : Bug drapeau 📰 Blé 7j/1m (logique `news_dominant` incorrecte)

**Actions requises (priorité haute) :**
1. Corriger la logique drapeau 📰 : utiliser `ratio_news > 0.5` au lieu de `news_dominant`
2. Ajouter un disclaimer explicite dans le bulletin quand |score_pm1| < 0.05 sur un horizon (libellé suggéré : "quasi coin-flip — signal non-actionnable")
