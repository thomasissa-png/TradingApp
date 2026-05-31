# Audit desk — Justesse directionnelle DeepSeek (94 news à impact)

Auditeur : news trader senior. Source : `v3/data/test-extraction-report.md`. Méthode : table récap (directions L/S exactes des 94 décisions, lignes 23-244) + lecture du raisonnement JSON détaillé (News 1-6 intégrales + few-shots/règles). Convention : L = prix de l'actif monte, S = prix baisse. VIX L = vol monte (= risk-off).

## 1. Justesse directionnelle — cas les plus parlants

**CORRECTS (bon réflexe desk)**
- #3 / #39 / #82 / #92 / #97 / #99 / #172 / #181 Hormuz fermé / choc d'offre : BRENT L, GOLD L, VIX L, SP500 S. Panier géopol pétrole textbook. Colonne vertébrale saine.
- #61 / #67 / #175 désescalade Iran (ceasefire/deal) : BRENT S, GOLD S, VIX S, SP500 L. Le panier s'inverse proprement vs #3 — bon signe, pas un copier-coller aveugle.
- #23 / #24 / #26 / #51 inflation chaude / hausse Fed anticipée : SP500 S, NASDAQ S, EURUSD S, GOLD S. Cohérent : hot CPI → real yields up → or ET actions down, USD up → EURUSD down. EURUSD bien orienté.
- #30 NFP plus fort qu'attendu : SP500 L, NASDAQ L, EURUSD S. Dollar fort post-jobs bien lu (EURUSD S correct).
- #37 China industrial profits +24.7% : COPPER L. Lecture demande Chine → cuivre, propre.
- #180 imports brut Japon -66% : BRENT L (disruption offre/reroutage). Fin.
- #66 oil slips on deal awaited : BRENT S, isolé, pas de panier forcé. Mesuré.

**DOUTEUX / FAUX**
- #6 SP500 winning streak 9 semaines → SP500 L / NASDAQ L (high) / VIX S. C'est du MOMENTUM déjà réalisé vendu comme prédiction : la news EST le mouvement passé. Aucun edge forward, et confidence high injustifiée.
- #16 Warsh (faucon) prête serment → SP500 L, NASDAQ L. DOUTEUX : un chair hawkish est plutôt baissier actions. Le GOLD S et EURUSD S sont OK, mais le signe actions est contestable.
- #13 / #29 consumer sentiment record low → SP500 S mais BRENT L + GOLD L. FAUX partiel : un effondrement de confiance US est désinflationniste/demande faible → BRENT devrait être S, pas L. Le panier risk-off "or+pétrole montent" est plaqué mécaniquement (le pétrole n'est pas un refuge).
- #5 soutien Taïwan réaffirmé → SP500 S, GOLD L (low). Impact fantôme : non-événement diplomatique, ne devrait pas générer d'impact tradable.
- #52 Chine commande 200 Boeing → SP500 L. Single-name (Boeing) extrapolé à l'indice : surinterprétation.
- #109 fin d'une enforcement action Fed → SP500 L. Impact fantôme administratif.
- #169 falling crude → BRENT S, SP500 L, CAC40 L : OK sur Brent mais CAC40 L sur baisse pétrole = lien ténu (CAC ≠ panier énergie net).
- #178 / #204 Bowman "trop tôt pour juger" → mouvements actions + GOLD/VIX. Commentaire verbal sans contenu directionnel net → matérialité surévaluée.

## 2. Erreurs de raisonnement récurrentes

- **News = prix (momentum déjà joué)** : #6 (streak actions), records/inflows → traités comme signaux forward alors que c'est du descriptif passé. Erreur la plus fréquente côté actions/or.
- **Panier géopol plaqué** : BRENT L systématiquement collé à GOLD L / VIX L même quand la news est une demande faible (#13/#29) où le pétrole devrait baisser. Confusion "risk-off = tout-refuge monte".
- **Single-name → indice** : #52 Boeing, #5 Taïwan → impact indice sur événement non systémique.
- **Commentaire verbal traité comme donnée dure** : Fed speakers (#178, #204) génèrent des impacts multi-actifs sur du blabla.
- **PAS d'inversion de signe EURUSD** (contrairement à une crainte initiale) : sur macro US forte/hot, DeepSeek met bien EURUSD S (#23,#24,#26,#30,#51). Bon point — c'est l'un de ses réflexes les plus fiables.

## 3. Matérialité / fiabilité — calibration

- Globalement correcte. `reported` pour géopol/rumeur, `confirmed` pour data officielle, `rumor` pour opinion (#2). Bon tri.
- **Trop généreux en materiality** sur commentaires verbaux Fed (#178/#204 en medium/high) et non-événements (#5, #109).
- **Filtrage single-stock excellent** : Meta #1, Berkshire #4, Nio #32, SoFi #210 → impacts:[] à juste titre. ~128 news écartées, très peu de faux négatifs visibles. C'est la vraie force du système.
- Confidence peu discriminante (surtout medium) ; high parfois mal placé (#6 momentum).

## 4. Multi-actifs (paniers)

- Panier Hormuz/Iran : cohérent ET réversible (#3 vs #61) — preuve que ce n'est pas un copier-coller pur. Bon.
- MAIS le réflexe "GOLD L + BRENT L + VIX L" est appliqué à des news qui n'ont PAS de prime de risque offre (#13/#29 demande faible) → mécanique sur ces cas.
- Panier inflation/Fed (#23/#24/#26/#51) : SP500/NASDAQ/EURUSD/GOLD tous alignés et corrects, bonne maîtrise du bloc taux.
- Panier Chine (#37 copper) : juste mais sous-exploité (COPPER peu mobilisé, 3 occurrences seulement).

## 5. Angle mort desk

- **Price-in / surprise vs consensus** : DeepSeek réagit au NIVEAU, pas à l'écart aux attentes. Un FOMC/CPI conforme ne devrait pas bouger le marché ; lui génère quand même un panier.
- **Momentum déjà coté** : ne distingue pas une news prédictive d'un constat de prix passé (#6).
- **Pétrole ≠ refuge** : l'amalgame or/pétrole dans le panier risk-off est l'angle mort technique le plus net.
- **Régime de marché / second tour** : pas de "good-is-bad" ni d'effet demande sur les commodities.

---

## VERDICT

**Fiable pour décision directionnelle : SOUS CONDITIONS.** Note : **6/10.**

- Solide là où ça compte : chocs d'offre pétrole (panier Hormuz cohérent et réversible), bloc inflation/Fed avec EURUSD bien orienté, et un filtrage single-stock de très bonne qualité (128 écartées, peu de bruit).
- **ERREUR LA PLUS DANGEREUSE : le panier risk-off plaqué mécaniquement — "GOLD L + BRENT L + VIX L" — appliqué à des news de demande FAIBLE (#13/#29) où le Brent devrait baisser.** Signe pétrole inversé dans ces cas : perte directe sur le crude.
- Deuxième risque : confond momentum déjà coté (#6) et signal forward → faux edge sur actions/or, avec confidence high trompeuse.
- À utiliser tel quel sur géopol-pétrole et inflation/Fed ; à surveiller (override desk) sur les paniers commodities issus de news macro de demande et sur les commentaires verbaux de banquiers centraux. Ajouter une couche "vs consensus" comblerait l'angle mort principal.
