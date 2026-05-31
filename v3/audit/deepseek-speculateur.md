# Audit spéculateur — décisions directionnelles DeepSeek

Brief : 94 news à impact, auditées « est-ce que je mets du cash dessus ? ». Objectif système = suivre la VAGUE de tendance par actif (24h/7j/1m), sens LONG/SHORT.

Périmètre : 222 news, 94 à impact. Concentration : SP500 (56), BRENT (41), GOLD (40), NASDAQ (40), EURUSD (34), VIX (20). Deux gros thèmes portent 80% du signal : **Iran/Hormuz** (énergie+risk-off) et **inflation/Fed-hike** (actions short).

## 1. Tradeable vs bruit
Vrais catalyseurs de tendance (je regarde) : le **bloc inflation/hawkish-Fed** (#18, #20, #23, #24, #26, #28, #51, #202) — cohérent, répété, c'est une vraie vague macro SP500/NASDAQ SHORT. Le **bloc choc Hormuz physique** (#82, #83, #92, #172, #180, #181) où il y a une vraie disruption d'offre, pas un titre.
Bruit sur-coté par DeepSeek :
- **#5** Taiwan « negotiating chip » → SP500 SHORT + GOLD LONG : opinion de couloir, zéro flux. Bruit.
- **#6, #29, #30, #83, #169, #171, #177** : ce sont des **descriptions de ce qui vient de se passer** (« S&P 9e semaine de hausse », « Dow rises »), pas des catalyseurs. DeepSeek transforme un compte-rendu en signal directionnel.
- Toute la série **EIA structurelle** (#77, #78, #84, #86, #87, #90, #91) → BRENT SHORT sur des tendances d'offre à horizon 2027. Aucun edge intraday/hebdo, c'est du fond de rapport.
- **#43, #16, #103, #106** (nominations Warsh/Powell) → directions fortes sur de la politique de personne, pré-pricée des semaines à l'avance.
Verdict section : ~35 des 94 impacts sont du bruit tendanciel. DeepSeek sur-estime clairement l'impact directionnel de news mineures/descriptives.

## 2. Horizon (LE manque structurel)
DeepSeek ne donne AUCUN horizon. Pour un système 24h/7j/1m c'est un trou béant. Exemples justes à 24h, faux à 1m :
- **#61, #67, #175** (deal/ceasefire Iran) → BRENT SHORT, SP500 LONG : vrai le jour J, mais une rumeur de deal se dégonfle en 48h ; à 1m ça peut s'inverser (le deal capote → #27 « never bow »).
- **#13, #29** (consumer sentiment record low) : choc sentiment = 24h, sans suite de prix à 1m.
- À l'inverse, **#84, #86, #87** (capacités LNG/export) sont des thèses 1m+ nulles à 24h.
Sans champ horizon, le système mélange un scalp d'1h et une thèse trimestrielle dans le même bucket directionnel. À corriger en priorité.

## 3. Contrarian / déjà pricé
Le piège retail est massif ici. Les news « le marché a monté/baissé » génèrent un signal DANS le sens déjà consommé :
- **#6, #30, #171, #177** : LONG SP500 après que l'indice a déjà fait le move → on achète le haut.
- **#83, #180** : BRENT LONG après que le spot a déjà surgé → on entre en retard.
- **#18, #24** : SP500 SHORT « marché price un hike » — le hike EST déjà dans les futures ; edge nul, voire mean-reversion contrarian.
Estimation : **20-25 impacts** vont dans le sens d'une info déjà dans les cours. Edge nul à négatif.

## 4. Convictions (où JE prends, où je passe)
High conviction réelle (je prends) :
- **#82 / #92 / #172 / #181** — disruption physique Hormuz confirmée : BRENT LONG, GOLD LONG, c'est le seul cluster où je mets du size.
- **#23 / #26 / #28** — inflation chaude + Fed forcée hawkish : SP500/NASDAQ SHORT, trend macro propre.
- **#180** Japon -66% imports : signal d'offre concret, BRENT LONG.
DeepSeek met « high » et je PASSE :
- **#16, #103, #115** FOMC/Warsh → high : trop pré-pricé, je ne touche pas.
- **#39, #97, #99** (Piper Sandler / EIA « Hormuz fermé ») high : ce sont des **prévisions d'analystes/agences**, pas des faits — fiabilité « reported/confirmed » mais contenu spéculatif. High injustifié.

## 5. Risque de ruine
Le danger n°1 = **signaux contradictoires haute conviction sur le même actif à 2 jours d'écart**, suivis mécaniquement :
- BRENT : #3/#39/#82 disent LONG high, #66/#67/#175 disent SHORT high. Sans pondération temporelle ni netting, le système se fait essorer en allers-retours (whipsaw) — saignée garantie en range.
- **#61** (rumeur « rumor » + high impact) → SP500 LONG, BRENT SHORT sur une RUMEUR de deal. Suivre une rumor en high size = le scénario de perte sèche si démenti.
- **VIX LONG** émis 20 fois quasi systématiquement avec le risk-off : shorter implicitement la vol via un panier corrélé = perte non bornée si l'event ne vient pas (le carry du VIX long brûle).

---

## VERDICT : SOUS CONDITIONS

Le signal directionnel brut est exploitable pour du positionnement de tendance UNIQUEMENT si on ajoute 3 filtres. En l'état (suivi mécanique), NON — ça whipsaw et achète des moves déjà faits.

**Note : 5,5/10** (bonne lecture macro de fond inflation/énergie ; mais pas d'horizon, pas de gestion du déjà-pricé, signaux contradictoires non nettés).

- **PLUS GROS PIÈGE** : signaux haute conviction contradictoires sur BRENT/SP500 à quelques jours, sans netting ni horizon → whipsaw destructeur de capital en marché de range.
- Manque critique : champ **horizon (24h/7j/1m)** absent — indispensable pour ce système, à ajouter au JSON.
- ~20-25 impacts sont **déjà pricés** (news descriptives « le marché a monté ») : filtrer les titres-compte-rendu, ne garder que les catalyseurs.
- Garder le **cluster Hormuz physique** et le **bloc inflation hawkish** (vraies vagues) ; dégrader les rapports EIA structurels et nominations Fed (pré-pricés, pas tendanciels court/moyen).
