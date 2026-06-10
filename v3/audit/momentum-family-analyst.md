# Audit Quantitatif — Famille momentum-prix v2
**Auteur** : Analyst quantitatif (trio d'audit v3)
**Date** : 2026-06-10
**Statut** : Analyse pure — AUCUN code/YAML modifié
**Verdict global** : **6/10**

---

## 1. NIVEAU vs VARIATION — Verdict tranché

**La v2 (z-score de la VARIATION 20j) est le bon estimateur. La v1 (z-score du NIVEAU de close) doit être abandonnée.**

Argument statistique rigoureux : le z-score du NIVEAU mesure *où se situe le prix dans sa distribution historique de closes*, pas la direction de sa dérivée. En début de retournement baissier, le prix reste structurellement au-dessus de sa moyenne 60j pendant plusieurs semaines (mean-reversion lente des niveaux). Le z-score de niveau est un indicateur *laggard* : il confirme les tendances établies mais rate les retournements — exactement le bug cacao documenté.

Le z-score de la VARIATION 20j (rendement 20j glissant normalisé) est un estimateur de premier ordre de la dérivée du prix. Il passe négatif dès que le mouvement sur 4 semaines glissantes bascule — soit plusieurs semaines avant que le niveau franchisse sa moyenne 60j. Pour un call à horizon 24h/7j dans une thèse trend-following, **la dérivée prime le niveau**.

Nuance à noter : les deux estimateurs ne mesurent pas la même chose. Le z-score de niveau capte "le prix est-il structurellement haut ou bas dans son historique" (utile pour les signaux de valeur relative). Le z-score de variation capte "le mouvement récent est-il inhabituel". La thèse directionnel/trend-following appelle sans ambiguïté la variation — c'est la définition même du momentum.

**Recommandation tranchée : z-score de la VARIATION 20j, window de normalisation 60j.**

---

## 2. Fenêtre 20j — Pertinente, mais le calcul actuel est NIVEAU, pas VARIATION

**Point critique non résolu dans l'implémentation.**

La v2 théorique = z-score de la variation 20j. Mais `_twelve_zscore_from_symbol` calcule `zscore_from_series(closes[-60:])` — c'est un z-score du **niveau** de close (le dernier close normalisé dans la distribution des 60 closes). C'est exactement la v1 que le design v2 prétend remplacer.

Pour que `momentum_prix_20j_cacao` soit vraiment un z-score de variation 20j, il faudrait le router via la branche `mouvement_or_5j` avec une fenêtre de 20j au lieu de 5j :
```python
perfs = [closes[i] / closes[i - 20] - 1.0 for i in range(20, len(closes)) ...]
```
**Ce n'est pas ce que fait le code actuel.** Le cas par défaut du dispatcher (ligne 1778) appelle `_twelve_zscore_from_symbol` = z-score des niveaux de close. Le nommage `momentum_prix_20j_*` est trompeur : les fiches décrivent une variation 20j, le code calcule un niveau.

Conséquence : la v2 telle qu'implémentée est fonctionnellement identique à la v1 sur ce point central. L'argument "retard au retournement" que la v2 est censée corriger n'est pas corrigé.

**Fenêtre de normalisation 60j** : justifiée. Une distribution de 60 rendements 20j glissants (~3 ans) est suffisante pour calibrer le z-score sans surfit. En dessous de 40 périodes, la distribution est bruitée ; au-delà de 120, les régimes changent (le z-score compare la tendance actuelle à un passé trop lointain).

**Normalisation brute vs z-score** : le z-score est préférable au seuil brut. Un rendement de -5% sur 20j est très baissier pour l'or (vol 10% annualisée) mais peu significatif pour le cacao (vol 30%). La normalisation par la distribution propre de l'actif absorbe l'hétérogénéité des volatilités. Seuil brut = risque de sous-pondération sur actifs peu volatils et sur-pondération sur actifs très volatils.

---

## 3. Look-ahead / Causalité — Faible risque, mais un angle borgne

Le z-score de niveau sur closes quotidiennes est strictement causal (on utilise la série `closes[-window:]` qui se termine au dernier close disponible). Pas de look-ahead introduit par la mécanique de normalisation.

Risque résiduel identifié : si `fetch_twelve_series` renvoie des données incluant le close *intraday* du jour en cours (cours non définitif), le z-score de rendement 20j serait calculé sur une valeur partielle. Pour un call diffusé à 7h, le close J-1 doit être le dernier point utilisé. Le code (`outputsize=window+5`) ne garantit pas explicitement l'exclusion du close courant — à vérifier en production.

---

## 4. Circularité / Overfit — C'est le risque principal

**C'est la question la plus sérieuse, et la réponse est nuancée.**

"Le prix monte → prédire que le prix monte" est une tautologie *seulement si* on utilise la même fenêtre de calcul que l'horizon de prédiction. Un z-score de rendement 20j pour prédire les 24h suivantes n'est pas circulaire : on utilise un signal *passé* (rendement des 20 dernières sessions) pour prédire une session *future*. C'est le principe fondateur du momentum, validé empiriquement dans la littérature académique (Jegadeesh-Titman 1993, Carhart 1997, et répliqué sur commodities par Erb-Harvey 2006).

Mais le risque réel est différent : **le momentum sur fenêtre 20j est très fortement corrélé à d'autres critères déjà présents** (COT, flux ETF, news). Sur 11 fiches ajoutant simultanément un signal de momentum, le win-rate shadow *augmentera mécaniquement* non pas parce qu'on ajoute de l'information, mais parce qu'on ajoute un critère corrélé aux outcomes dans l'échantillon d'apprentissage.

Compte tenu du backtest OOS à **46%** : le signal quant pur est faible. Ajouter le momentum sur 11 fiches sur la même période d'observation crée un risque d'overfitting in-sample. Le vrai test est un OOS propre : si le win-rate shadow sur les 90 prochains jours (post-implémentation) ne monte pas au-delà de 52-55%, le signal est cosmétique.

**Garde-fou recommandé** : ne pas valider le design sur le backtest existant (il n'est pas indépendant — la période cacao fait partie du même échantillon). Figer l'implémentation à une date fixe et mesurer sur les 60 jours suivants en forward-test strict.

---

## 5. Poids — Cacao 9 est justifié, différenciation raisonnable

Cacao poids 9 : la fiche cacao a un poids total effectif de ~46 (hors gate). Un poids 9 représente ~20% du signal total — raisonnable pour un critère primaire de tendance sur un actif dont le case-study montre que l'absence de ce critère a produit 5 FAUSSES consécutives. Justifié.

Café/blé/cuivre à 7-8, pétrole/or/argent à 6-7 : la différenciation par volatilité intrinsèque est une bonne pratique (plus l'actif est volatil, plus la tendance de prix a de l'information marginale). Mais attention : sur les fiches avec poids total plus faible (blé : ~57, café : ~44), un poids 8 représente déjà 14-18%. L'impact relatif varie selon la fiche — une calibration par % du poids total serait plus rigoureuse qu'un poids nominal fixe.

EUR/USD poids ~6 : logique réduite. Les différentiels de taux (poids 12+9+6) capturent 60% du signal. Le momentum FX 20j a une valeur marginale plus faible que sur les commodities — le poids 6 est correct.

---

## 6. VIX exclusion — D'accord, pour les bonnes raisons

Le VIX est structurellement mean-reverting (OU-process) : sa "tendance directionnelle" est un retour à la moyenne, pas un momentum. Un z-score de variation 20j du VIX serait contra-intuitif (une hausse de 20j prédit un retournement baissier, pas une continuation). La fiche VIX est déjà bien couverte par `niveau_vix_absolu` (poids 10, signe -1 contrarian) et `term_structure_vix_vix3m` — ces deux critères capturent correctement la dynamique mean-reverting.

Ajouter un momentum-prix directionnel (+1) sur le VIX serait une erreur statistique : il inverserait la logique appropriée à cet actif.

---

## 5 Amendements concrets (priorité décroissante)

**A1 — CRITIQUE : corriger le calcul pour que la v2 soit vraiment une VARIATION 20j**
Le dispatcher actuel route `momentum_prix_20j_*` vers `_twelve_zscore_from_symbol` = z-score des niveaux de close. Il faut créer une branche dédiée `cle.startswith("momentum_prix_20j_")` calculant `closes[i] / closes[i-20] - 1.0` sur la fenêtre glissante, puis z-scorant la série de rendements. Sans cet amendement, la v2 = v1 fonctionnellement.

**A2 — IMPORTANT : ajouter un forward-test gate avant validation**
Le backtest OOS à 46% ne peut pas valider le momentum ajouté sur la même fenêtre d'observation. Fixer une date de cut (J0 = date d'implémentation) et n'évaluer le gain de win-rate qu'à J+60. Tout gain mesuré avant J+60 sur données historiques est suspect.

**A3 — IMPORTANT : vérifier le close as-of dans `fetch_twelve_series`**
S'assurer que pour un run 7h, le dernier point renvoyé est bien le close J-1 (définitif) et non un cours intraday J0. Sinon le z-score de variation 20j serait calculé sur une valeur partielle.

**A4 — RECOMMANDÉ : calibrer les poids en % du total de la fiche, pas en absolu**
Le poids 8 pour le blé (14% du total) et le poids 8 pour le café (18% du total) n'ont pas le même impact. Documenter la part cible (objectif : 15-20% du signal effectif disponible) et ajuster le poids nominal en conséquence fiche par fiche.

**A5 — RECOMMANDÉ : RSI indices — conserver, ne pas ajouter momentum directionnel**
Le RSI poids 2 sur S&P/Nasdaq/CAC est un signal contrarian (oversold = LONG), complémentaire d'un momentum directionnel. Si un momentum-prix 20j est ajouté sur les indices (P3 dans le sweep), utiliser un poids 4-5 max (les taux et spreads de crédit capturent déjà la majeure partie de la tendance équité). Ne pas monter à 7-8 comme sur les commodities.

---

## Synthèse verdict /10

| Axe | Note | Commentaire |
|---|---|---|
| Choix VARIATION vs NIVEAU | +3 | Correct en théorie — mais non implémenté |
| Cohérence avec thèse trend-following | +2 | Défaut systémique identifié et adressé |
| Risque circularité géré | +1 | Reconnu mais garde-fou absent |
| Implémentation technique | -2 | La v2 calcule encore du NIVEAU (bug A1) |
| Poids et calibration | 0 | Raisonnable mais approximatif |
| VIX exclusion | +2 | Bonne décision, bonne raison |

**Score : 6/10** — Le diagnostic est juste et la direction est bonne. Le design v2 est théoriquement supérieur à la v1. Mais l'amendement A1 est bloquant : sans correction du dispatcher, la v2 déployée sera fonctionnellement identique à la v1, et le bug cacao ne sera pas corrigé. Les poids et pertinences sont raisonnables sous réserve de calibration par % du total.

---

*Analyse pure — aucun code/YAML modifié. Trio audit v3 — analyst quantitatif. 2026-06-10*
