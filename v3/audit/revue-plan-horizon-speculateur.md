# Revue de plan — Horizon news vs momentum (œil SPÉCULATEUR trend-follower)

Brief : Thomas veut être SÛR de la tendance par horizon (24h / 7j / 1m). Le plan propose 2 réglages news. Je dis lequel je garde, lequel je jette, et la config qui maximise la JUSTESSE de tendance. Pas un audit de run — une revue AVANT code.

Statut : REVUE DE PLAN. Brutal, chiffré.

---

## TL;DR (verdict en 4 lignes)

- Réglage 1 (decay_factor GLOBAL) : **JETÉ**. Doublon avec `pertinence`, double-decay à 1m, casse les critères slow par actif.
- Réglage 2 (news ne flip plus seule le signe du quant) : **GARDÉ et renforcé**. C'est LE réglage trend-follower.
- Le vrai problème n'est pas « news trop forte à 1m », c'est « news ADDITIVE qui vote LONG/SHORT au lieu de FILTRER le momentum ».
- Config retenue : news en FILTRE (gate de conviction), pas en terme additif inversant.

---

## 1. Ce que fait le moteur AUJOURD'HUI (constaté dans le code)

Source : `scoring_analyste.py:352` et `:406-409`.

```
contribution[h] = valeur_norm × poids × pertinence[h] × signe
score[h]        = Σ contributions[h]   (somme de TOUS les critères)
conclusion[h]   = LONG si score[h] > 0 sinon SHORT   (SEUIL_LONG = 0.0)
```

Trois faits qui changent tout pour la revue :

1. **La news est un critère ADDITIF comme un autre.** Le critère news (synthèse DeepSeek → `tension_geopol_*`) entre dans la MÊME somme que momentum, RSI, prix. Il ne filtre rien : il VOTE. S'il pèse plus que la somme des quants, il flippe le signe. C'est exactement le scénario Pétrole +9.84 → +13.34 : news plate qui pousse dans le même sens, le score franchit 0 et « accélère » sans pente prix.

2. **`pertinence` est DÉJÀ un vecteur de décroissance par horizon, PAR CRITÈRE.** Ex. `petrole.yml:51` géopol = `{24h:0.9, 7j:0.7, 1m:0.2}`. La news géopol est donc déjà divisée par 4.5 entre 24h et 1m. Le decay existe. Il est juste local et calibré par critère.

3. **La direction news est CONSTANTE sur les 3 horizons** (DeepSeek rend un seul `direction/conviction` par actif, `synthese_directionnelle.py:11`). C'est ça l'anomalie que Thomas voit : même flèche à 24h/7j/1m. Mais le moteur la pondère DÉJÀ différemment via `pertinence[h]`. Le problème n'est donc pas « la news ne décroît pas », c'est « une news plate à conviction medium suffit à VOTER le signe ».

## 2. Réglage 1 — decay_factor global {24h:1.0, 7j:0.7, 1m:0.3} : pourquoi je le JETTE

**C'est un DOUBLON pur de `pertinence`, et il fait pire.**

Effet réel sur le critère géopol pétrole (`pertinence` actuelle 0.9/0.7/0.2) si on multiplie par le decay global :

| Horizon | pertinence actuelle | × decay global | poids news EFFECTIF | facteur d'écrasement |
|---|---|---|---|---|
| 24h | 0.90 | ×1.0 | **0.90** | inchangé |
| 7j  | 0.70 | ×0.7 | **0.49** | −30% |
| 1m  | 0.20 | ×0.3 | **0.06** | −70% → news quasi nulle |

À 1m on tue le signal DEUX fois : 0.20 (déjà calibré) × 0.30 = **0.06**. La news géopol pétrole à 1 mois ne pèse plus rien — alors qu'un blocus d'Ormuz est PRÉCISÉMENT un driver 1 mois. Réponse directe à la Q2 : **oui, doublon, et oui, on tue deux fois le signal à 1m. Trop.**

Pire encore — le decay GLOBAL est aveugle au sens de la pente par critère. Regarde les `pertinence` réelles dans `petrole.yml` :
- géopol Ormuz : `0.9 / 0.7 / 0.2` → décroît (driver court).
- EUDR / inventaires structurels (`:65` `0.2 / 0.8 / 1.0`) → **CROÎT** avec l'horizon (driver long).

Un decay global {1.0, 0.7, 0.3} appliquerait −70% à 1m sur un critère qui DOIT culminer à 1m. Il inverse la logique de calibration métier. Un trend-follower 1 mois a justement besoin que les drivers structurels montent en horizon, pas qu'on les rabote uniformément.

**Verdict R1 : JETÉ.** Si une `pertinence` est mal calibrée (trop forte à 1m sur tel actif), on corrige la LIGNE de la fiche concernée — pas avec un multiplicateur global qui casse les autres.

## 3. Réglage 2 — la news ne peut plus inverser seule le signe du quant : pourquoi je le GARDE

C'est LE bon réglage. Un trend-follower vit ou meurt sur UNE chose : **ne pas être sorti d'une tendance prix valide par du bruit narratif.** Le scénario Pétrole +9.84→+13.34 (news plate qui « accélère » et franchit 0) est exactement une inversion de signe pilotée par la news additive. R2 l'interdit.

Mécaniquement, dans le code actuel, le signe est franchi quand :
```
|contribution_news[h]| > |Σ contributions_quant[h]|   ET signe opposé
```
R2 = on bloque ce franchissement. Concrètement : si le bloc quant (momentum/RSI/prix) vote LONG, la news ne peut PAS rendre le score < 0 à elle seule. Elle peut au mieux ramener le score vers 0 (réduire la conviction), pas le retourner.

C'est aligné avec le commentaire déjà présent dans le code : *« Le prix ne ment pas »* (`synthese_directionnelle.py:19, :105`). DeepSeek a déjà l'instruction d'abaisser sa conviction si la news contredit le prix. R2 rend cette intention DURE au niveau du score au lieu de la laisser au bon vouloir du LLM (qui, lui, peut halluciner une conviction high sur news plate).

**Verdict R2 : GARDÉ.** C'est le seul des deux réglages qui sert directement la justesse de tendance.

Mais R2 tel quel est INCOMPLET : « ne pas inverser » n'est qu'une moitié. Si la news pousse DANS le sens du quant mais sur du vide (news plate, conviction low), elle gonfle quand même le score et fait « accélérer » un faux trend. Il faut la version filtre (§5).

## 4. Réponses directes aux 3 questions

**Q1 — Décroître la news (R1) ou empêcher la news de contrer le momentum (R2) ? Lequel prioritaire ?**
R2, sans hésiter. Pour suivre une vague, l'ennemi n°1 du trend-follower est le **whipsaw** : sortir/inverser une position sur tendance prix encore valide à cause d'une news. R1 ne touche QUE l'amplitude (et mal) ; R2 protège le SIGNE, qui est tout ce qui compte pour la direction de tendance. Décroître la news ne sert à rien si elle peut encore retourner le signe à 24h. **Priorité absolue : R2.**

**Q2 — Le decay global fait-il doublon avec `pertinence` (risque de tuer 2× le signal à 1m) ?**
Oui, doublon total. Démontré §2 : géopol pétrole à 1m = 0.20 × 0.30 = **0.06**, signal news quasi anéanti sur un horizon où certains drivers (Ormuz, OPEC) sont au contraire pertinents. Et le global ignore les critères dont la `pertinence` CROÎT avec l'horizon (EUDR 0.2/0.8/1.0). C'est la raison principale du rejet de R1.

**Q3 — La news devrait-elle être un FILTRE (confirme/infirme le momentum) plutôt qu'un ingrédient additif ? Le plan va-t-il dans ce sens ?**
Oui, FILTRE. Pour un trend-follower la hiérarchie est : **le prix décide la direction, la news module la CONVICTION.** Le plan va dans ce sens à MOITIÉ : R2 empêche l'inversion (bon début de logique filtre), mais le moteur garde la news en terme additif qui peut encore gonfler un faux trend dans le sens du quant. **Il faut aller au bout : news = gate de conviction, pas terme de score.** Voir §5.

## 5. Config retenue (maximise la justesse de tendance)

**Principe : le prix vote la direction, la news filtre la conviction. La news ne crée jamais une tendance, elle confirme ou la met en doute.**

### A. GARDER R2, en version « filtre bidirectionnel » (le cœur)

Au lieu de juste « news n'inverse pas », appliquer cette règle dans le calcul de `score[h]` :

```
quant[h]  = Σ contributions des critères NON-news (momentum, RSI, prix...)
news[h]   = contribution du critère news (DeepSeek)

direction[h] = signe(quant[h])         # le prix décide, TOUJOURS

# la news ne fait que moduler l'amplitude, jamais le signe :
si signe(news[h]) == signe(quant[h]) :   score[h] = quant[h] + news[h]   # confirme → renforce
sinon                                :   score[h] = quant[h] × (1 − k·|news[h]|_norm)  # infirme → réduit conviction, sans flip
```
- Confirme le momentum → on autorise l'add (la vague est validée des deux côtés).
- Infirme le momentum → on N'inverse PAS, on réduit l'amplitude (= baisse de conviction). `k` ∈ [0.3 ; 0.6] borné pour que `score` ne change jamais de signe.
- Si `quant[h] = 0` (pas de momentum) → la news NE crée pas de direction : `score[h] = 0` (NEUTRAL). C'est ce qui aurait tué le faux trend Pétrole.

### B. Anti « news plate » : gate de conviction DeepSeek (résout le vrai bug)

La cause-racine du Pétrole n'est pas l'horizon, c'est une news SANS PENTE qui pèse quand même. Filtre dur en amont, dans `triggers_classifier` :

```
si conviction_deepseek == "low"  → contribution_news = 0   (déjà partiellement fait, niveau 2 fallback prix)
si conviction == "medium"        → contribution_news ×= 0.5
si conviction == "high"          → contribution_news ×= 1.0
```
News plate = DeepSeek doit rendre `low/NEUTRAL` (le system prompt l'exige déjà, `:96-98`). Si DeepSeek triche en mettant medium sur du plat, le ×0.5 + la règle A bornent les dégâts. **Pas de pente = pas de vote.** C'est ta phrase, codée.

### C. JETER R1. Garder `pertinence` par critère comme SEUL mécanisme d'horizon.

`pertinence` est le bon outil : per-critère, per-horizon, calibré métier. Si un critère news est jugé trop fort à 1m, on édite SA ligne dans la fiche. Exemple ciblé si Thomas veut amortir la news géopol courte sur le long :
```
# petrole.yml géopol — déjà 0.9/0.7/0.2, c'est correct. Ne pas y toucher avec un global.
```
Aucun multiplicateur global. Zéro double-decay.

### Tableau récap décision

| Élément | Décision | Raison 1 ligne |
|---|---|---|
| R1 decay_factor global | **JETÉ** | doublon `pertinence` + double-decay 1m + casse drivers structurels |
| R2 news n'inverse pas le signe | **GARDÉ** | protège le signe = protège la tendance (anti-whipsaw) |
| News additive pure | **REMPLACÉ** | passe en filtre de conviction (A) |
| Gate conviction DeepSeek | **AJOUTÉ** | tue la news plate à la source (le vrai bug Pétrole) |
| `pertinence` par critère | **CONSERVÉ** | seul mécanisme d'horizon, calibré métier |

## 6. Ce que je surveille après implémentation

1. **Taux d'inversion news-only** : compter les cycles où `signe(score) ≠ signe(quant)`. Cible après R2-filtre : **0%**. Si > 0, la borne `k` est trop lâche.
2. **Faux trends plats** : rejouer le run Pétrole +9.84→+13.34 sur la nouvelle logique. Attendu : score ne franchit pas 0 sans pente prix → reste NEUTRAL ou conviction basse. C'est le test d'acceptation n°1.
3. **Drivers 1m structurels** : vérifier que EUDR cacao / OPEC pétrole (pertinence montante à 1m) gardent leur poids — preuve qu'on n'a PAS étouffé le 1 mois (ce que R1 aurait fait).
4. **Cohérence des 3 horizons** : la direction peut LÉGITIMEMENT différer entre 24h et 1m (momentum court vs structurel). Ne pas « corriger » cette divergence — c'est le signal, pas le bruit. Ce qu'on supprime, c'est la news qui IMPOSE la même flèche partout, pas la divergence prix.

---

### Une phrase pour Thomas
Tu n'as pas un problème d'horizon, tu as un problème de **rôle de la news** : elle vote alors qu'elle devrait filtrer. Jette le decay global (il tue ton 1 mois deux fois), garde le « pas d'inversion » et pousse-le jusqu'au filtre de conviction. Le prix mène la danse, la news dit juste si elle y croit.
