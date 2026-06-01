# Audit chaîne de production — TradingApp v3 — RUN 18h (2026-06-01 18:20)
Angle : news-trader senior, desk macro/commodities. Enjeu = JUSTESSE DIRECTIONNELLE et défendabilité desk.
Mode **DELTA post-déploiement plan horizon**. Référence = run de midi (6/10, commit 99023fe). Ce run est le **1er run planifié avec le plan horizon actif** : `pertinence` recalibrée, cap anti-inversion (la news ne retourne plus seule le quant sauf high+confirmed), drapeau 📰 si news>50%. On audite : (0) intégrité, (1) ce que le plan horizon a CHANGÉ, (2-5) cellules clés, puis les **4 points desk à trancher**.

---

## 0. Intégrité du run
- Horodatage aligné : bulletin `18:20:26+02:00`, criteres-courants `last_update 16:20:26Z` = 18:20 Paris, decision-log `2026-06-01-1820.jsonl generated_at 18:20:26+02:00`. Fraîcheur OK (bulletin l.65). RAS.
- 36 lignes JSONL (12×3). Scores rejoués cohérents avec la matrice au centième (vérifié Or, Nasdaq, Pétrole, VIX, EUR/USD). Rejouable.
- **Nouveauté traçée** : champs `news_total`, `quant_total`, `ratio_news`, `news_dominant`, `news_cap_applied`, `news_cap_override` désormais présents sur CHAQUE ligne. C'est le câblage du plan horizon — on peut enfin lire si le cap a joué. Progrès de traçabilité majeur vs midi (où le cap n'existait pas).
- **Cohérence flips** : les 9 flips déclarés (bulletin l.85-93) collent aux scores. Les 3 flips Nasdaq (24h/7j/1m LONG→SHORT) et les 3 Argent (SHORT→LONG) sont les mouvements structurants du run.

---

## 1. CE QUE LE PLAN HORIZON A CHANGÉ (cœur du DELTA)

**(A) Le cap anti-inversion a TUÉ le faux LONG Or 24h — la régression #1 du midi est corrigée.**
À midi, Or 24h sortait primaire **LONG +0.17** (faux signal porté par le triplet geopol +1) vs pondéré SHORT. Ce run, Or 24h sort **SHORT -1.54 en primaire ET en pondéré** (log l.25, `diverge:false`). Le triplet `tension_geopolitique=+1` est toujours là (contrib_pm1 +2.5) mais (i) sa pertinence est coupée à **0.5** (24h), et (ii) `news_dominant:true` mais `news_cap_applied:false` / `news_cap_override:false` : la news ne suffit plus à retourner le quant SHORT (TIPS réels +0.50σ contrib -2.99, VIX bas 14.95 contrib -1.60). **Le faux LONG démenti 2× par le marché a disparu.** Et le marché redonne raison : **Or SHORT = VRAI -1.684%** (perf l.49, Brier 0.0435, le meilleur du run).

**(B) La pollution geopol du VIX a DISPARU — la régression #2 du midi (materiality high blindant le LONG) est corrigée.**
À midi, VIX sortait LONG ×3 via un triplet geopol à facteur 1.0 non atténué. Ce run, le triplet `tension_geopolitique_active` est à **valeur:0** (source_track `ia_synthese_faible`, facteur null, contrib 0) sur les 3 horizons (log l.34-36). VIX sort **SHORT ×3 en quanti pur** (term structure VIX/VIX3M en contango -1.0σ → contrib -6.4/-8.0/-4.8). `diverge:false` cohérent — plus d'écart matrice/log. **Le LONG fabriqué est mort, le quanti vol parle seul.**

**(C) Le drapeau 📰 est posé correctement** sur Blé, Nasdaq, Or, Pétrole (matrice l.72-80) — exactement les cellules où `news_dominant:true`. C'est un bon signal de transparence : le desk voit d'un coup d'œil où la news pèse >50%.

**Verdict §1 : les deux régressions masquées du midi sont corrigées, et le marché valide (Or). C'est un vrai gain net, pas un déplacement de problème.**

---

## 2. OR & VIX repassés SHORT — défendable vs midi ?

**OUI, c'est le bon call desk, et le marché tranche dans ce sens.**
- **Or SHORT ×3** : le quanti est sans ambiguïté baissier. TIPS réels à +0.50σ (l'or déteste les taux réels hauts), VIX au plancher 14.95 (pas de bid risk-off), COT à +1.8 contrib 7j (positionnement encore long = surplomb vendeur). Le seul facteur haussier est le triplet geopol +1, désormais correctement sous-pondéré (pertinence 0.5/0.4/0.3 décroissante). À midi le primaire forçait un LONG ; ce run le primaire EST SHORT. **Mesure : Or SHORT VRAI -1.684%** (perf l.49). Le marché a donné raison au SHORT — exactement contre le LONG que produisait le midi. **Défendable à 100%, c'est même la meilleure cellule du run.**
- **VIX SHORT ×3** : term structure en contango profond (VIX/VIX3M 0.82, -1.0σ) + VIX absolu 14.95 = manuel du short-vol. Le bruit geopol qui polluait à midi est neutralisé. **Mesure non-conclusive** (+1.679% < seuil 5%, perf l.52) — le marché n'a pas tranché à 24h mais la direction quanti est saine. **Défendable.**

---

## 3. NASDAQ SHORT ×3 📰 — la news a-t-elle trop tiré vers SHORT ?

**NON — et c'est le point contre-intuitif du run : la news Nvidia est HAUSSIÈRE, le SHORT vient du QUANT, et le cap empêche justement la news de remonter le score vers LONG.**

Lecture fine (log l.22-24) :
- La news (`sentiment_ia_megacaps=+1`, Nvidia chip PC, confirmed, bulletin l.14-16) tire **LONG** : contrib_pm1 **+4.0** (24h). C'est le plus gros contributeur positif après le SOX.
- Le QUANT pur tire **SHORT** : TIPS réels +0.50σ (contrib **-2.74**, poids 11), spread Nasdaq-Russell tendu (contrib -1.86), RSI ^IXIC à **78** = suracheté (contrib -1.60). `quant_total` = **-0.009** (24h).
- `news_dominant:true`, `ratio_news:459` (24h), **`news_cap_applied:true`** : le cap a joué. Sans cap, la news LONG +4.0 aurait retourné le score vers LONG. Avec cap, la news ne peut pas inverser un quant SHORT (sentiment IA est `medium/confirmed`, PAS `high+confirmed` → pas d'override, `news_cap_override:false`). Donc **SHORT tient**.

**Tranche desk : SHORT 7j/1m défendable** (TIPS hauts + RSI suracheté + spread small-caps = compression méga-caps classique). **SHORT 24h = à nuancer** : score -0.00 (l.78 matrice, -0.002 log), c'est un quasi-pile-ou-face. Le drapeau 📰 est mérité, mais le SHORT 24h est si proche de zéro qu'un desk le traiterait **neutre/indécis**, pas short franc. La restriction export Nvidia/AMD Chine (baissière) que tu cites n'apparaît PAS comme critère branché — le `sentiment_ia_megacaps` est figé **+1 LONG** (chip launch), il n'intègre pas le volet export-control baissier. **Le SHORT n'est donc PAS « la news qui a trop tiré » : la news pousse LONG, c'est le quant qui pèse, et le cap a bien fait son travail en empêchant un faux retournement LONG.** Mesure : Nasdaq LONG (J-1) non-conclusif +0.307%.

**Réserve desk** : le `sentiment_ia` capté est unilatéralement haussier alors que l'actu Chine/export est mixte. Si le volet baissier était branché, le SHORT serait plus *fondé* fondamentalement — ici il est SHORT « par défaut quant », ce qui est correct mais maigre en conviction à 24h.

---

## 4. PÉTROLE LONG fort malgré le cap — le cap a-t-il joué ?

**Le cap n'a PAS joué, et c'est NORMAL : news et quant pointent dans le MÊME sens, il n'y a aucune inversion à empêcher.**

Log l.28-30 : `news_cap_applied:false`, `news_cap_override:false`.
- `news_total` = +6.0 (24h, LONG : tension Moyen-Orient +4.2 + OPEC+ +1.8) ;
- `quant_total` = **+0.99** (24h, POSITIF : Cushing -0.23σ contrib +0.56, COT short-couvert +0.42). Le quant est lui aussi LONG.
- `news_dominant:true` (ratio 6.07) mais **les deux composantes sont du même signe LONG**. Le cap anti-inversion ne se déclenche que si la news veut RETOURNER un quant de signe opposé. Ici rien à retourner → cap inactif, à juste titre.

**Donc ni cap ni override : le LONG passe parce qu'il est cohérent quant+news, pas par une faille.** Défendable desk : prime de risque Ormuz (frappes confirmed, events-log l.28-29 Liban/Gaza) + OPEC+ + Cushing bas = LONG Brent légitime. **Mesure : Pétrole LONG VRAI +6.685%** (perf l.50, Brier 0.0000). Le marché valide franchement.

**Nuance horizon conservée du midi** : `tension_geopol` décroît bien 4.2→4.2→1.4 (pertinence 0.6/0.6/0.2) = amortissement de la prime de risque front, BON réflexe. `opec_production` croît 1.8→5.4→6.0 = politique structurelle qui pèse plus long, BON aussi. La structure de terme reste défendable. **Seul défaut résiduel** : la valeur +12.24 à 7j est un score brut énorme dont l'amplitude ne reflète aucune cible de prix — mais la DIRECTION est juste et validée.

---

## 5. LE CAP PRODUIT-IL DES CONTRESENS, OU DES CELLULES PLUS SAINES ?

**Bilan : le cap assainit, il ne casse rien.** Recensement des `news_cap_applied:true` du run :
- **Nasdaq 24h & 7j** (l.22-23) : cap actif, empêche la news IA LONG de retourner un quant SHORT. **Sain** — sans lui on aurait un faux LONG méga-caps en plein RSI 78 suracheté.
- **Aucune autre cellule en cap actif.** Or (l.25-27) : `news_cap_applied:false` — le cap n'a pas eu besoin de jouer car le quant SHORT était déjà majoritaire après recalibrage pertinence. VIX : news à 0, sans objet. Pétrole : même sens, sans objet.

**Aucun contresens desk détecté du fait du cap.** Le cas qui aurait pu mal tourner — une news high+confirmed qui force un override contre un bon quant — **ne s'est pas produit** ce run (`news_cap_override:false` partout). Le garde-fou « override seulement si high+confirmed » n'a donc pas été testé en conditions réelles cette fois. **À surveiller** : le jour où un triplet `high+confirmed` apparaît, l'override pourra retourner le quant — il faudra vérifier que ce soit justifié (vraie frappe) et pas une rumeur sur-étiquetée.

**Point de vigilance résiduel (hérité, non causé par le cap)** : `reliability` reste figé à **`confirmed`** sur tous les triplets `ia_synthese` (Or, Pétrole, Nasdaq sentiment). C'est le même aplatissement qu'au midi. Tant que le track `ia_synthese` produit du `confirmed` en dur, l'override high+confirmed est à une seule étiquette de se déclencher sur une rumeur. **Le cap protège aujourd'hui PARCE QUE le sentiment IA est `medium` (pas high) ; si materiality montait à high, le garde-fou reposerait sur un `reliability` non discriminant.** C'est la faille de fond qui subsiste.

---

## 6. SYNTHÈSE DES 4 POINTS DESK

| Point | Tranche desk | Validé par le marché ? |
|---|---|---|
| **Or & VIX → SHORT** | **DÉFENDABLE**, meilleur call du run. Quanti baissier net, pollution geopol neutralisée. | **OUI** : Or SHORT VRAI -1.684% (Brier 0.0435). VIX non-concl. mais direction saine. |
| **Nasdaq SHORT ×3** | **DÉFENDABLE 7j/1m** (TIPS+RSI 78+spread). **24h = neutre** (score -0.00). La news pousse LONG, le SHORT est quant ; le cap a bien empêché un faux LONG. | Nasdaq J-1 non-concl. (+0.307%). |
| **Pétrole LONG fort** | **DÉFENDABLE**. Cap inactif car news+quant même sens (rien à inverser), pas un override. Prime Ormuz + OPEC+ + Cushing bas. | **OUI** : Pétrole LONG VRAI +6.685% (Brier 0.0000). |
| **Cap → contresens ?** | **NON** : cellules plus saines (Nasdaq), aucun contresens. Override jamais déclenché ce run. | Pas de cellule cap-induite démentie. |

---

## VERDICT GLOBAL desk (RUN 18h)

**Le plan horizon livre ce qu'il promettait : il corrige les DEUX régressions masquées du midi (faux LONG Or, LONG VIX pollué) sans introduire de contresens, et le marché valide le call le plus exposé (Or SHORT -1.68%).** C'est le premier run où le maillon news cesse de tourner en rond.

Ce qui a PROGRESSÉ vs midi (6/10) :
- **Cap anti-inversion opérationnel et traçé** (`news_cap_applied/override` loggés par cellule) ;
- **Faux LONG Or 24h éliminé** — primaire ET pondéré SHORT, validé marché (-1.68%) ;
- **Pollution geopol VIX éliminée** — triplet à 0, SHORT quanti pur, `diverge:false` cohérent ;
- **Pertinence recalibrée** décroît proprement par horizon (Or tension 0.5→0.3, Pétrole tension 0.6→0.2) ;
- **Drapeau 📰** posé juste sur les 4 cellules news-dominantes.

Ce qui RESTE à corriger (faille de fond, non causée par le plan horizon) :
- **`reliability` figé `confirmed`** sur tous les `ia_synthese` → l'override high+confirmed repose sur une étiquette non discriminante. Bombe à retardement : le jour où materiality monte à `high`, le garde-fou saute.
- **`sentiment_ia` unilatéral +1 LONG** : n'intègre pas le volet baissier (export-control Chine Nvidia/AMD). Le SHORT Nasdaq est « par défaut quant », pas par lecture news complète.
- **event_id toujours non traçé** dans les contribs : impossible de remonter du +1 geopol à la frappe source (frappe d'aujourd'hui à amortir vs archive à purger).
- **Amplitude des scores non calibrée** (Pétrole +12.24 à 7j) : direction juste, magnitude ininterprétable.

### Signaux DÉFENDABLES (tradables ce run)
- **Or SHORT ×3** — quanti baissier net, validé -1.68%. Le call du run.
- **Pétrole LONG ×3** — news+quant cohérents LONG, validé +6.69%.
- **VIX SHORT ×3** — contango + VIX bas, quanti pur propre.
- **Nasdaq SHORT 7j/1m** — TIPS+RSI 78+spread small-caps. (24h = neutre, score -0.00.)
- **EUR/USD SHORT 24h → LONG 1m** — pure lecture positionnement (USD/JPY + COT EUR), zéro news. Propre.
- **Cuivre SHORT 7j/1m, Cacao LONG, S&P/CAC/Argent LONG** — quanti cohérent.

### À TRAITER AVEC PRUDENCE
- **Nasdaq 24h** : score -0.00, neutre. Ne pas shorter franc, c'est un pile-ou-face. Le 📰 est juste mais le signal est nul.
- **Café 1m** : ⚠ diverge (primaire SHORT -0.92 / pondéré LONG +1.17), cycle Brésil calendrier vs COT. Suivre le pondéré (règle desk maintenue). Mesure J-1 : Café LONG FAUX -1.883% — seule cellule démentie, mais c'était le primaire LONG de la veille, pas ce run.

### Note chaîne : **8/10** (+2 vs midi)
Ingest 8 · propagation news **6** (cap opérationnel + pertinence recalibrée + 2 régressions corrigées ; plafonné par reliability figé confirmed + sentiment unilatéral + event_id absent) · quanti 8 · mesure 7 (Or/Pétrole validés, boucle saine). **Le maillon news passe de 3 à 6 : c'est le premier run qui débloque le verrou.** Le +2 est mérité et validé par la mesure, pas cosmétique.

### 3 correctifs desk prioritaires (réordonnés post-plan-horizon)
1. **Discriminer `reliability` réellement** dans le track `ia_synthese` (confirmed/reported/rumor) — sinon l'override high+confirmed se déclenchera un jour sur une rumeur sur-étiquetée. C'est désormais LE risque #1 (le cap protège tant que materiality reste `medium`).
2. **Brancher le volet baissier dans `sentiment_ia`** (export-control Chine) et plus largement permettre aux triplets news un signe -1 quand le flux net est baissier — comme `ble.geopolitique_mer_noire=-1` le fait déjà.
3. **Tracer l'event_id** dans chaque contrib triplet + purger archives Hormuz >30j : pour piloter la décroissance par horizon sur la NATURE/fraîcheur de l'event, pas seulement la pertinence a priori.
