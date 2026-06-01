# Audit chaîne de production — TradingApp v3 — RUN MIDI (2026-06-01 13:37, commit 99023fe)
Angle : news-trader senior, desk macro/commodities. Enjeu = JUSTESSE DIRECTIONNELLE et défendabilité desk.
Mode **DELTA** : ce run de midi est très proche du run de 9h51 (commit 9e2ccc0). On audite dans l'ordre d'édition : (0) intégrité, (1-5) ce qui a bougé cellule par cellule, puis le **point desk à trancher** (même direction news sur 24h/7j/1m). Le diagnostic structurel de fond (fuite jointure 1→2) est inchangé sauf mention explicite.

---

## 0. Intégrité du run (DELTA)
- Cohérence horodatage : bulletin, criteres-courants (`last_update 11:37:57Z` = 13:37 Paris) et decision-log (`generated_at 13:37:57+02:00`) **alignés sur le même run**. Fraîcheur OK (l.63 bulletin). RAS.
- 36 lignes JSONL (12 actifs × 3 horizons), scores recalculés cohérents avec la matrice du bulletin (vérifié Pétrole, Or, Nasdaq, VIX, Café, Cuivre, EUR/USD au centième). Rejouable. RAS.
- **Flips déclarés (l.82-92)** cohérents avec les scores. Aucune incohérence matrice/log/flips détectée.
- 2 divergences `diverge:true` dans le log : **Or 24h** (l.25) et **Café 1m** (l.15). Le bulletin en signale 3 avec ⚠ (Or 24h, VIX 1m, Café 1m). **Écart à noter** : VIX 1m est marqué ⚠ dans la matrice (l.77 implicite via annotation) mais le log VIX 1m sort `diverge:false` (primaire LONG +0.25 = pondéré +0.25, facteur 1.0). Voir §3.

---

## 1. INGEST — inchangé (toujours le maillon fiable)
Le run de midi partage le même events-log que le matin (même fenêtre 48h, mêmes confirmed:high LONG sur Ormuz/Liban). Diagnostic du matin maintenu : **le flux frais net penche LONG pétrole** (escalade actée), les SHORT sont des `reported` (rumeurs d'accord). Défauts persistants (archives Hormuz fév-avr non purgées, pas de pondération récence) **inchangés**. Pas de re-litige ici.

## 2. CRITÈRES / PROPAGATION NEWS — **un vrai progrès DELTA + une régression masquée**

**Ce qui a CHANGÉ depuis 9h51 (et c'est bien) :**
- **`reliability` est enfin propagé.** Au matin il arrivait vide (`reliability:""`) partout : la distinction confirmed/reported était jetée. À midi, **tous** les triplets news portent `reliability:"confirmed"` : Pétrole (log l.28-30), Or (l.25-27), VIX (l.34-36), Nasdaq sentiment_IA (l.22-24), Blé geopol mer Noire. **Le correctif #3 du matin a partiellement pris : reliability survit maintenant jusqu'au calcul.**

**MAIS la régression masquée :**
- `reliability` arrive **figé à `confirmed` sur 100 % des triplets**. Aucun `reported` ni `rumor` nulle part, alors que l'ingest, lui, distingue bien (frappes confirmed vs Trump/Goldman reported). **La granularité est de nouveau aplatie** — sauf que cette fois vers le HAUT (tout confirmed) au lieu de vers le vide. Effet net pire pour le desk : un tweet de négociation est désormais étiqueté « confirmed » au même titre qu'une frappe. Le champ existe mais ne discrimine rien.
- Le **signe** des triplets Moyen-Orient/Or/VIX reste **figé à +1 LONG** (`tension_geopol_moyen_orient: valeur:1`, criteres l.283-290). La fuite de fond « tension = +1 LONG en dur, jamais branché sur le SENS du log » est **toujours là**. Preuve que le branchement est possible : `ble.geopolitique_mer_noire: valeur:-1` (criteres l.49, log l.4 `contrib_pm1:-5.6`) SHORT correctement branché ET `reliability:confirmed`. Le moteur SAIT le faire sur le Blé, pas sur le pétrole.

**Materiality module bien le facteur (confirmé) :** Pétrole/Or `materiality:medium → facteur:0.6` ; VIX `materiality:high → facteur:1.0` (log l.34). Donc le facteur n'est PAS constant à 0.42 ce run (c'était le cas matin) — il varie 0.6/1.0 selon materiality. Léger raffinement vs matin.

## 3. BULLETIN — cellules qui ont BOUGÉ (cœur du DELTA)

Je ne re-juge que les cellules signalées comme modifiées vs matin.

**Cuivre — 24h FLIP SHORT→LONG (+0.13), 7j/1m restent SHORT (-1.53/-3.31).**
Le flip 24h est **mécaniquement fragile, pas une thèse desk** : il vient uniquement du ratio Cuivre/Or à +0.94σ (contrib +1.13, log l.16) qui dépasse de justesse le COT Copper à +1σ (contrib -1.00). +0.13 = bruit d'arrondi entre deux critères quasi opposés. Le 7j/1m SHORT (COT extrême + PMI Chine mou, l.45 « China factory activity stalls ») reste le vrai signal. **Desk : ignorer le LONG 24h (+0.13), tenir le SHORT structurel.** À noter : la mesure de la veille a donné **Cuivre SHORT FAUX (+2.80%, l.46 perf)** — le marché a violemment contredit le short cuivre sur 24h. Donc le flip LONG 24h va « dans le sens » du marché récent, par accident quanti, pas par lecture news.

**Café — 1m FLIP LONG→SHORT (-1.42), pondéré LONG +0.67 ⚠ (diverge:true, log l.15).**
Primaire SHORT porté par le **cycle Brésil bi-annuel = -1** (contrib_pm1 -3.6) contre COT Coffee +2.18. Le cycle Brésil est un signal `source_track:calendrier` à `facteur:0.42` → une fois pondéré, son poids fond et le COT reprend le dessus (pondéré LONG +0.67). **Desk : divergence calendrier-vs-positionnement, marginale.** La mesure 24h donne Café LONG VRAI (+1.26%, l.45) — cohérent avec le pondéré, pas le primaire. Règle desk maintenue : sur ⚠, suivre le pondéré.

**Or — 24h FLIP SHORT→LONG (+0.17), pondéré SHORT -1.43 ⚠ (diverge:true, log l.25).**
**Cellule la plus dangereuse du run, identique au défaut du matin.** Le primaire LONG existe UNIQUEMENT grâce au triplet `tension_geopolitique=+1` (contrib_pm1 +4.0, log l.25). Tout le quanti tire SHORT : TIPS réels +0.50σ (contrib -2.99), VIX 14.95 bas (-1.60). Dès qu'on pondère (facteur 0.6 sur le triplet), ça repasse SHORT -1.43. **La mesure tranche encore : Or SHORT = VRAI -0.771% (l.49 perf, Brier 0.0435).** Le primaire LONG forcé par le flag geopol est un **faux signal démenti par le marché, pour la 2e mesure consécutive.** Ne pas trader le primaire Or 24h.

**EUR/USD — SHORT 24h (-0.62) → LONG 7j/1m (+0.13/+1.27).**
Structure de terme défendable et propre : 24h porté par USD/JPY fort (proxy USD haussier, contrib -1.08) ; le flip LONG 7j/1m vient du COT EUR à -0.45σ (positionnement short extrême → potentiel de rebond, contrib +1.36/+2.04 croissant avec la pertinence). **C'est de la lecture de positionnement classique : USD fort à très court terme, mean-reversion EUR à horizon plus long.** Aucun triplet news ne pollue cette cellule (que du quanti). **Défendable.**

**Pétrole — LONG/LONG/LONG (+9.84/+13.34/+10.35).** Voir §6 (point desk) : c'est le cas d'école de la question des horizons.

**Nasdaq — LONG/LONG/SHORT (+4.25/+2.72/-1.57).** Inchangé vs matin, toujours la cellule la plus fine : momentum IA + SOX court terme, TIPS réels hauts + RSI 76 qui font basculer SHORT à 1m. Structure de terme cohérente. **Défendable.** Note : sentiment_IA porte `reliability:confirmed` (Nvidia chip, confirmed:high réel) — ici l'étiquette confirmed est JUSTE.

**VIX — LONG/LONG/LONG, mais ⚠ matrice vs diverge:false log (incohérence à signaler).**
Le bulletin annote VIX avec ⚠ mais le log sort `diverge:false` sur les 3 horizons (primaire = pondéré). Cause : `materiality:high → facteur:1.0` (log l.34-36), donc le triplet geopol +1 (contrib 3.6/2.4/1.2) n'est PAS atténué par la pondération — primaire et pondéré coïncident. **Conséquence desk grave** : sur VIX, le flag geopol passe à plein dans le pondéré aussi. Le quanti VIX dit pourtant clairement SHORT vol (term structure VIX/VIX3M en contango -1.0σ → contrib -6.4/-8.0/-4.8 ; VIX absolu 14.95 bas). Le LONG VIX ne tient QUE par le triplet geopol non corrigé + SKEW. **Le passage materiality high a ici un effet pervers : il blinde la pollution news au lieu de l'atténuer.** Le ⚠ du bulletin est le bon réflexe ; le `diverge:false` du log est trompeur.

## 4. TRAÇABILITÉ (decision-log) — DELTA
- **Progrès** : `reliability:confirmed` désormais tracé dans chaque contrib triplet (était `""`). On peut au moins lire l'étiquette.
- **Trous inchangés** : (a) `reliability` figé à confirmed = non discriminant (cf §2) ; (b) **aucun event_id / source_event / titre** dans les contribs (0 occurrence) — impossible de remonter du `contrib 6.3` au `BRENT:LONG:high` source. Le fil vers l'event reste rompu ; (c) le **primaire ±1 toujours non modulé** par materiality/facteur : Pétrole 24h `contrib_pm1:6.3` (log l.28) identique au matin et identique à la veille. Le facteur 0.6 ne touche que `contrib_pond:3.78`.
- Distribution facteur du run : triplets news à **0.6 (medium) ou 1.0 (high)** selon materiality — plus de 0.42 uniforme. Micro-progrès de granularité, mais toujours pas event-par-event.

## 5. MESURE (performance.md) — DELTA
Boucle d'apprentissage **toujours rebranchée** (prix d'émission captés, l.41-52). 7 outcomes conclusifs cette fenêtre :
- **Pétrole LONG = VRAI +2.827%** (l.50, Brier 0.0000). Le système a raison sur 24h.
- **Or SHORT = VRAI -0.771%** (l.49) — confirme que le **pondéré** (SHORT) avait raison contre le primaire (LONG +0.17). 2e démenti consécutif du flag geopol sur le primaire Or.
- **Cuivre SHORT = FAUX +2.804%** (l.46) — short quanti pris à revers, voir flip 24h §3.
- **Cacao LONG = VRAI +3.377%**, **Café LONG = VRAI +1.264%** (l.44-45) — cohérents avec les pondérés.
- 5 cellules non-conclusives (sous seuil), 0 éligible, 12/12 shadow, N_eff=0. **Aucune conclusion stat** — warm-up attendu.
**Verdict mesure :** confirme à nouveau (1) Pétrole LONG bon sens cette fenêtre, (2) le primaire Or LONG forcé par le triplet est un faux signal. La mesure valide la règle « sur ⚠, suivre le pondéré ».

---

## 6. POINT DESK À TRANCHER — même direction news sur 24h / 7j / 1m

**Question :** la synthèse applique le MÊME signe news (+1) sur les 3 horizons (Pétrole `tension_geopol=+1` identique 24h/7j/1m). Un desk traite-t-il une news géopol pareil à 24h et à 1 mois ?

**Tranche desk : NON, et c'est défendable seulement par accident sur le pétrole — le mécanisme est faux.**

Ce que fait le système (verbatim, Pétrole, log l.28-30) :
```
tension_geopol_moyen_orient: valeur:1 (signe identique 3 horizons)
contrib_pm1 : 6.3 (24h) / 4.9 (7j) / 1.4 (1m)   ← via pertinence 0.9 / 0.7 / 0.2
opec_production_policy:      valeur:1
contrib_pm1 : 2.4 (24h) / 5.4 (7j) / 6.0 (1m)   ← via pertinence 0.4 / 0.9 / 1.0
```

**Le système N'applique PAS aveuglément la même intensité.** Le SIGNE est identique (+1 LONG partout), mais la `pertinence` module l'amplitude par horizon. Et là il y a deux cas radicalement opposés :

**(A) DÉFENDABLE — tension géopol Ormuz décroissante avec l'horizon (pertinence 0.9→0.2).**
Pour le pétrole, `tension_geopol` pèse 6.3 à 24h mais s'effondre à 1.4 à 1m. **C'est exactement le bon réflexe desk** : une frappe sur Ormuz, c'est une prime de risque sur le contrat front, qui se dissipe à mesure que l'horizon s'allonge (le marché price une résolution moyenne). Un desk surpondère la news géopol fraîche sur le spot/front et la sous-pondère à 1 mois. **Ici le modèle imite correctement la décroissance de la prime de risque.** Le signe +1 reste légitime sur les 3 horizons SI la tension est structurelle (Ormuz, choke-point), mais l'intensité qui décroît est la bonne nuance.

**(B) CONTRESENS — quand une news fraîche garde la même intensité ou CROÎT à 1m.**
Le vrai problème n'est pas `tension_geopol`, c'est **OPEC+** : `opec_production_policy=+1` CROÎT de 2.4 (24h) à 6.0 (1m). Pour une décision OPEC+ ponctuelle, c'est défendable (une politique de production est structurelle, elle pèse plus à 1 mois qu'à 24h). MAIS le système ne fait AUCUNE différence de NATURE entre :
- une news **structurelle** (OPEC+ quotas, choke-point Ormuz permanent) → légitimement portée sur 7j/1m ;
- une news **événementielle fraîche** (une frappe ponctuelle, un tweet) → déjà price à 1m, devrait DÉCROÎTRE vers zéro.

Le seul outil de décroissance est la `pertinence` (réglée par actif/critère a priori), **pas une fonction de la fraîcheur ou de la nature de l'event.** Résultat : sur le pétrole la pertinence décroissante de `tension_geopol` rattrape par chance le bon comportement, mais **rien ne garantit que la news qui a déclenché le +1 soit encore tradable à 1m.** Et comme reliability est figé à `confirmed` et que l'event_id n'est pas tracé, **le système ne PEUT PAS savoir si le +1 vient d'une frappe d'aujourd'hui (à amortir) ou d'une archive de février (déjà price)** — il propage le même +1 à 1m dans les deux cas.

**Cas VIX — le contresens nu :** `tension_geopolitique_active=+1` contrib 3.6/2.4/1.2. À 1m, une « tension active » à +1.2 sur le VIX est un **contresens** : à un mois, un VIX à 14.95 en contango profond (term structure -1.0σ) dit que le marché a DÉJÀ digéré la tension. La news géopol fraîche n'a aucune raison de tenir le VIX haut à 1 mois. Le primaire LONG VIX 1m (+0.25) tient à 5 contre 4 sur ce seul triplet. **Là le « même signe à 1m » est clairement faux pour un desk vol.**

### Synthèse du point desk
| Cellule | Signe identique 3 horizons | Défendable ? | Pourquoi |
|---|---|---|---|
| Pétrole `tension_geopol` | +1, intensité 6.3→1.4 (décroît) | **OUI** (par chance) | décroissance pertinence ≈ amortissement prime de risque front |
| Pétrole `opec_production` | +1, intensité 2.4→6.0 (croît) | **OUI** | politique de production = structurelle, pèse plus à long terme |
| Or `tension_geopol` | +1, 4.0→1.5 (décroît) | **NON sur primaire** | démenti par marché 2× (Or SHORT VRAI) ; le quanti SHORT doit gagner |
| VIX `tension_active` | +1, 3.6→1.2 | **NON à 1m** | tension fraîche déjà price ; VIX bas + contango disent SHORT vol |

**Verdict du point :** le système a **un demi-bon réflexe** — il décroît l'intensité géopol avec l'horizon via la pertinence, ce qui imite l'amortissement de la prime de risque (défendable sur Ormuz structurel). Mais il lui manque **la distinction nature event** (structurel vs fraîche-déjà-price) et **le branchement du signe sur le sens réel du flux**. Sur le pétrole le hasard fait bien les choses ce run ; sur Or/VIX le « même +1 à 1m » fabrique des LONG que le marché dément.

---

## VERDICT GLOBAL desk (DELTA midi)

**Le run de midi améliore la TRAÇABILITÉ de la conviction (reliability + materiality désormais propagés) mais introduit une régression masquée (reliability figé à `confirmed`) et laisse la fuite de fond — signe news non branché — intacte.**

Ce qui a PROGRESSÉ vs 9h51 :
- `reliability` survit jusqu'au log (était vide) ;
- `materiality` module le facteur de façon non uniforme (0.6 medium / 1.0 high) — fini le 0.42 constant.

Ce qui a RÉGRESSÉ ou n'a pas pris :
- `reliability` **figé à confirmed partout** → non discriminant, et pire qu'un champ vide car il affirme à tort que des rumeurs sont confirmées ;
- **VIX materiality:high → facteur:1.0** blinde la pollution geopol dans le pondéré aussi (le ⚠ matrice ne se retrouve plus dans `diverge` du log) ;
- signe news figé +1, primaire ±1 non modulé, event_id non tracé — **inchangé**.

### Signaux DÉFENDABLES (tradables ce run)
- **Pétrole LONG** (24h surtout) — prime de risque géopol légitime, flux confirmed:high LONG, **validé mesure +2.83%**. Bon sens, mauvais mécanisme (cf §6).
- **Nasdaq LONG→LONG→SHORT** — structure de terme cohérente, sentiment_IA correctement étiqueté confirmed.
- **EUR/USD SHORT 24h→LONG 7j/1m** — pure lecture de positionnement (USD/JPY + COT EUR), zéro pollution news. Propre.
- **Cuivre SHORT 7j/1m** — COT extrême + PMI Chine mou (ignorer le flip LONG 24h à +0.13, bruit).
- **S&P LONG, CAC LONG, Argent LONG** — quanti cohérent, convictions faibles.

### À NE PAS TRADER (primaire pollué par le triplet geopol figé)
- **Or 24h** : primaire LONG +0.17 / pondéré SHORT -1.43. Marché a tranché SHORT (VRAI -0.77%), **2e fois**. Suivre le pondéré.
- **VIX (3 horizons, 1m surtout)** : LONG fabriqué par le triplet geopol à facteur 1.0 contre un quanti vol clairement SHORT. Le ⚠ matrice est juste, le `diverge:false` du log est trompeur.
- **Café 1m** : divergence calendrier/positionnement, marginale.
Règle desk maintenue : **sur toute cellule ⚠, suivre le pondéré.** Exception VIX : ici le pondéré EST pollué (facteur 1.0) — se rabattre sur le quanti pur (term structure → SHORT vol).

### Note chaîne : 6/10 (stable vs 9h51)
Ingest 8 · propagation news 3 (reliability propagé mais figé confirmed = +0/-0 net) · quanti 8 · mesure 6. Pas de mouvement net : le gain reliability est annulé par son aplatissement à confirmed, et la fuite de signe reste. La chaîne tourne en rond sur le maillon news.

### 3 correctifs desk prioritaires (inchangés, réordonnés par impact mesuré)
1. **Brancher le signe du triplet sur le primaire ±1** pour Moyen-Orient/Or/VIX, comme c'est déjà fait pour `ble.geopolitique_mer_noire=-1`. Sans ça, Or 24h continuera de sortir un LONG démenti (2 mesures sur 2).
2. **Discriminer reliability réellement** (confirmed > reported > rumor doit moduler le facteur) au lieu de figer `confirmed`, ET **distinguer la nature de l'event** (structurel vs fraîche-déjà-price) pour piloter la décroissance par horizon — pas seulement la `pertinence` a priori. C'est la réponse de fond au point desk §6.
3. **Tracer l'event_id source** dans chaque contrib triplet + **purger les archives Hormuz > 30j** du comptage : sans event_id, impossible de savoir si un +1 à 1m vient d'une frappe d'aujourd'hui (à amortir) ou de février (déjà price).
