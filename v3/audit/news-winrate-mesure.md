# Mesure de justesse des news — news-driven vs quant-pures, par horizon

_Généré le 2026-06-18 19:05 par `/tmp/backfill_news_winrate.py` (backfill measures-log × decision-log d'émission). Mesure-only, zéro impact signal._

**Méthode.** Chaque prédiction jugée (VRAI/FAUX, NC exclus) est rattachée à son entrée du decision-log d'émission via (date d'émission, actif, horizon). Une cellule est **news-driven** si `ratio_news` (|news|/|quant|, en %) > 50 % à l'émission ; sinon **quant-pure**. Win-rate = VRAI / (VRAI+FAUX).

**Garde-fou honnêteté.** Tout groupe avec **N < 15** paris jugés est marqué « en chauffe — non concluant ». Le système est en phase de chauffe : aucun win-rate sous ce seuil n'est présenté comme significatif.

**Couverture jointure.** 83/89 prédictions jugées rattachées à un `ratio_news` d'émission (93 %). Les non-rattachées (decision-log d'émission antérieur à l'instrumentation `ratio_news`) sont classées « inconnu » et exclues de la comparaison news/quant. Total lignes measures-log : 768.

## 1. Win-rate par horizon — news-driven vs quant-pures

| Horizon | News-driven (win-rate [N]) | Quant-pures (win-rate [N]) | Inconnu (N) |
|---|---|---|---|
| 24h | 0% [N=1 — en chauffe, non concluant] | 45% [N=51] | 3 |
| 7j | — (0 jugé) | 77% [N=31] | 3 |
| 1m | — (0 jugé) | — (0 jugé) | 0 |

> **Pourquoi N news-driven est-il si bas ?** Ce n'est pas un bug de jointure : très peu de cellules sont *dominées par les news* à l'émission. Cellules news-driven émises (decision-log, tous runs) : 24h=11, 7j=1, 1m=0. La plupart ne sont pas encore arrivées à échéance / jugées. **Conclusion structurelle : il est aujourd'hui impossible de juger la justesse des news — le système n'a quasi pas encore produit de call news-driven mûri.** La tuyauterie de mesure est désormais en place pour les capter dès qu'ils arriveront.

## 2. Progression dans le temps (semaine par semaine)

Win-rate news-driven puis quant-pures, par semaine ISO. Une tendance n'est lisible que si plusieurs semaines dépassent N≥15 — sinon « en chauffe ».

### Horizon 24h

| Semaine | News-driven | Quant-pures |
|---|---|---|
| 2026-W23 | — (0 jugé) | 59% [N=22] |
| 2026-W24 | 0% [N=1 — en chauffe, non concluant] | 42% [N=19] |
| 2026-W25 | — (0 jugé) | 20% [N=10 — en chauffe, non concluant] |

### Horizon 7j

| Semaine | News-driven | Quant-pures |
|---|---|---|
| 2026-W23 | — (0 jugé) | 76% [N=17] |
| 2026-W24 | — (0 jugé) | 79% [N=14 — en chauffe, non concluant] |

## 3. Verdict — réponses noir sur blanc

**(a) Les news tapent-elles mieux ou moins bien que le quant ?**

- **24h** : trop tôt pour conclure — news N=1, quant N=51 (seuil 15). En chauffe.
- **7j** : trop tôt pour conclure — news N=0, quant N=31 (seuil 15). En chauffe.
- **1m** : trop tôt pour conclure — news N=0, quant N=0 (seuil 15). En chauffe.

**(b) Où est-ce meilleur / pire selon l'horizon ?**

- Aucun horizon n'atteint encore le seuil de fiabilité des **deux** groupes (N≥15). Impossible de désigner un horizon gagnant/perdant sans mentir sur la robustesse. À revisiter quand le volume aura mûri.

**(c) Y a-t-il une tendance d'amélioration dans le temps ?**

- **Trop tôt pour dire.** Aucun horizon n'a ≥2 semaines avec N≥15 paris news-driven jugés. La progression hebdomadaire n'est pas mesurable de façon honnête tant que le volume reste en chauffe. C'est cohérent avec le constat Analyst (0/36 cellules fiables) : le système chauffe encore.

---

_Ce rapport est régénérable à tout moment (`python /tmp/backfill_news_winrate.py`). Au fil des runs journaliste, le forward persiste `news_driven`/`ratio_news` directement dans measures-log : la jointure backfill deviendra superflue et la couverture montera vers 100 %._
