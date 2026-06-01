# Audit chaîne de production — TradingApp v3 (run 2026-06-01, commit 9e2ccc0)
Angle : news-trader senior, desk macro/commodities. Enjeu = JUSTESSE DIRECTIONNELLE de tendance et défendabilité desk. Pas la perf, pas la stat.
1er run post-correctifs (indices ETF débloqués, synthèse DeepSeek avec contexte-prix, prix d'émission réparés). Question : la chaîne news→critère→score est-elle juste côté desk ?

## 1. events-log.md — INGEST
Qualité : **bonne, c'est toujours le maillon le plus fiable côté desk.** DeepSeek lit bien la nuance directionnelle ET la reliability. Exemples du flux frais du jour :
- l.862 « Trump demande des modifications à l'accord US-Iran » → `BRENT:SHORT:medium`, reliability **reported** (rumeur de négo, pas un fait). Juste.
- l.881 « Trump déclare que l'Iran veut vraiment un accord » → `BRENT:SHORT:medium;GOLD:SHORT:low`, reported. Juste, c'est de la détente verbale non confirmée.
- l.861/890/895 frappes US-Iran + Israël-Liban → `BRENT:LONG:high`, **confirmed**. Juste, c'est de l'escalade actée.
- l.894 Goldman « demand destruction may offset supply risks » → `BRENT:SHORT:medium` reported. Nuance desk correcte.

**Le sens net du flux FRAIS (31/05–01/06) est bien LONG, pas SHORT** : 17 LONG (dont 8 confirmed:high) vs 10 SHORT (1 seul SHORT:high, le reste reported:medium/low). Les confirmed:high sont TOUS LONG (frappes, offensive Liban). **Important pour le brief** : le narratif « Brent -20%, plus grosse perte mensuelle en 6 ans, détente massive » N'EXISTE PAS dans ce log. Ce qui s'en rapproche = des `reported` SHORT:medium (Trump/accord, Goldman) noyés sous des `confirmed` LONG:high. Sur les données fournies à la machine, l'ingest a raison de pencher LONG.

Défauts persistants (non corrigés vs run 31/05) :
- (a) **Archives Hormuz fév-avr toujours présentes** : 21 lignes `BRENT:LONG:high` datées 2026-02/03/04 (l.326/336/341/343/796/806/811/813), dont la « fermeture du détroit le 28 février » ressortie en avril. Comptage brut tous horizons : **96 BRENT:LONG vs 60 BRENT:SHORT**. Aucune pondération par récence : un blocus de février gonfle encore le compteur LONG d'aujourd'hui. Pour un desk, un évènement de fév sur Ormuz n'est plus tradable, il est déjà dans le prix.
- (b) Reliability confirmed/reported est bien dans le log mais — spoiler étape 2 — ne survit pas.

## 2. criteres-courants.md — CRITÈRES
Quanti : **propre** (CFTC, flux ETF maintenant alimentés — flux_etf_qqq, msci_france, spy_ivv non nuls : le déblocage Twelve a bien pris). Côté news, **la fuite du 31/05 n'est PAS corrigée sur le sens.**

Le triplet directionnel `BRENT:SHORT:high` du log ne se branche TOUJOURS PAS sur le critère. Ce qu'on lit (l.283-290) :
```
petrole.tension_geopol_moyen_orient: {valeur:1, valeur_normalisee:1.0, materiality:medium, reliability:'', source_track:ia_synthese}
```
`valeur:1` = **+1 LONG en dur**, comme la veille. Le critère encode « il y a de la tension Moyen-Orient » = haussier pétrole, sans jamais consommer le SENS porté par les triplets `:SHORT:`. C'est exactement la fuite « tension_geopol = +1 LONG » signalée au run 31/05 — **toujours là**.

Ce qui A bougé (les correctifs visibles) :
- `source_track` est passé de `keyword` à `ia_synthese` : on est passé d'un match de mots-clés brut à une synthèse DeepSeek avec contexte-prix. Progrès de méthode.
- `materiality` est passée de `high` à `medium` (idem `or.tension_geopolitique`, `vix.tension_geopolitique_active`, `petrole.opec_production_policy`, `ble.geopolitique_mer_noire`). Le contexte-prix injecté a donc **abaissé la conviction** — c'est l'effet recherché.

Ce qui N'A PAS bougé et fait mal :
- **`reliability` arrive toujours vide** (`''`). La distinction confirmed (frappes actées) vs reported (rumeur d'accord) de l'étape 1 est **jetée**. Un desk ne traite pas une frappe confirmée comme un tweet de négociation.
- `materiality:medium` ne change que le score **pondéré** (via `facteur`), pas le score **primaire ±1** affiché en gros dans la matrice. Cf. §4 : le contexte-prix n'a pas touché la direction primaire.
- `ble.geopolitique_mer_noire: valeur:-1` (l.49) est bien SHORT — donc le moteur SAIT lire un -1 quand il vient de la synthèse. Preuve que techniquement le branchement directionnel est possible : il n'est juste pas appliqué au Moyen-Orient/Or/VIX, restés à +1 figé.

## 3. bulletin-2026-06-01.md — BULLETIN (36 cellules)
Matrice lisible, le primaire ±1 et le pondéré sont maintenant affichés côte à côte (`⚠` quand ils divergent) — bon réflexe de transparence. Jugement cellule par cellule :

**Défendables (quanti domine, news cohérent) :**
- **Cuivre SHORT** (-0.09/-1.91/-3.63) : porté par COT Copper à +1σ (positionnement long extrême = risque de débouclage) + PMI Chine qui cale (l.40 « China factory activity stalls »). Desk d'accord, short cuivre sur demande chinoise molle est un classique. Le ratio cuivre/or positif tempère à juste titre le 24h. **OK.**
- **S&P LONG** (+1.16/+4.88/+4.42) : HY credit spread serré (2.72, -0.61σ) = pas de stress crédit, flux SPY positifs. Défendable.
- **Argent LONG** (+1.56/+2.85/+5.06) : ratio Gold/Silver à 59.6 (bas → argent cher relativement... le critère le lit haussier via centre=75). Mou comme thèse mais le COT et le mouvement or 5j confirment. Acceptable, pas une conviction desk.
- **CAC LONG** (+0.27/+1.42/+1.04) : alpha vs S&P + flux MSCI France maintenant alimentés (déblocage Twelve OK) + SoftBank 75 Md€ data centers IA (l.20). Faible mais cohérent. **Le déblocage indices a bien restauré ces cellules** (CAC/Nasdaq/S&P n'étaient plus alimentés avant).

**Nasdaq LONG→LONG→SHORT** (+4.25/+2.72/-1.57) : la structure de terme est **défendable et même fine**. 24h porté par SOX +0.91σ et le sentiment IA (Nvidia nouveau chip PC, l.14-16, confirmed:high). Le flip 1m SHORT vient des TIPS réels à 2.06 (taux réels hauts pèsent sur les méga-caps à duration longue) + RSI 76 (suracheté). Un desk tient exactement ce discours : long le momentum IA court terme, prudent sur la valo à 1 mois taux réels hauts. **Cellule la plus intelligente du run.**

**Cellules sous warning ⚠ (primaire vs pondéré divergent) — à NE PAS trader :**
- **Or 24h LONG +0.17 mais pondéré SHORT -2.15** : le primaire est LONG uniquement grâce au triplet geopol +4.0 ; tout le quanti (TIPS réels +0.52, COT, VIX bas) tire SHORT. Dès qu'on pondère, ça repasse SHORT. **Signal instable, ne pas trader le 24h.** Note desk : la mesure d'hier a donné Or SHORT = VRAI (-0.627%), donc le pondéré avait raison contre le primaire. C'est le triplet geopol qui pollue le primaire.
- **VIX 1m LONG +0.25 mais pondéré SHORT -0.45** : idem, le +1.2 du triplet geopol fait basculer artificiellement en LONG un signal que le quanti (VIX 14.95 bas, term structure en contango) voit SHORT. Ne pas trader.
- **Café 1m SHORT mais pondéré LONG +0.67** : divergence cycle Brésil vs COT. Marginal.

**Conclusion bulletin :** là où le quanti est alimenté, la matrice est défendable. Les 3 cellules ⚠ sont exactement celles où le triplet geopol +1 LONG figé fait basculer le primaire à contre-quanti. Le warning ⚠ est un bon garde-fou : il pointe précisément les cellules polluées par la fuite §2.

## 4. decision-log/2026-06-01-0816.jsonl — TRAÇABILITÉ
Mécaniquement excellent et rejouable. Chaque contrib chiffrée. Mais côté news, **deux progrès partiels et deux trous béants.**

Pétrole 24h, triplet geopol (verbatim) :
```
{"cle":"tension_geopol_moyen_orient", "valeur":1, "materiality":"medium",
 "reliability":"", "source_track":"ia_synthese", "facteur":0.42, "contrib_pm1":6.3}
```

Progrès vs 31/05 :
- `source_track:ia_synthese` (était `keyword`) — on sait que c'est passé par la synthèse contexte-prix.
- `facteur:0.42` (était `0.7` la veille avec materiality high) — le contexte-prix a fait baisser le facteur pondéré.

Trous (inchangés) :
- **`contrib_pm1:6.3` est STRICTEMENT IDENTIQUE au run 31/05.** Le facteur 0.42 module `contrib_pond` (4.41) mais **PAS le primaire ±1**. Or c'est le primaire qui sort « Pétrole LONG +9.99 » en tête de matrice. **Le contexte-prix a baissé la conviction pondérée mais n'a pas bougé d'un iota la direction ni l'amplitude primaire.** Sur le score affiché, le correctif est cosmétique : 6.3 sur 9.99 = **63 % du primaire vient toujours du flag geopol +1 LONG.** Ajoute OPEC+ (`opec_production_policy:1`, contrib 2.4/5.4/6.0) et c'est ~90 % du score pétrole qui vient de 2 triplets news figés à +1, jamais branchés sur le sens du log.
- **`reliability:""` toujours vide** dans le log. confirmed vs reported perdu.
- **Aucun event_id / source_event / titre** tracé dans les contribs (grep : 0 occurrence). Impossible de remonter du `contrib 6.3` au `BRENT:LONG:high` (ou `:SHORT:`) d'origine. **Le fil vers l'event source reste rompu.** On trace QUE le keyword/synthèse a matché +1, pas QUELLE news ni quel sens initial.

Distribution `facteur` du run : 21× `0.42` (les triplets news, tous au même facteur figé), 114× `1.0`, 36× `null`. **Le 0.42 est de nouveau constant** sur tous les triplets — materiality:medium uniforme, donc aucune modulation fine event par event. La granularité reliability n'existe pas dans le calcul.

## 5. performance.md — MESURE
**Progrès majeur : les prix d'émission sont enfin capturés.** Au run 31/05 toutes les mesures étaient `suivi-interrompu / prix d'émission indisponible`. Le 01/06, la fenêtre 31/05→01/06 a des prix d'émission ET actuels réels (l.41-52). La boucle d'apprentissage **est rebranchée** — c'était le correctif le plus important et il a pris. Les `suivi-interrompu` restants (l.53+) sont l'ancienne fenêtre 30→31/05, normal.

Ce que la mesure dit sur les jugements desk ci-dessus (12 outcomes 24h mesurés) :
- **Pétrole LONG = VRAI (+2.736%, seuil 1.0%).** Le système a eu RAISON sur 24h. Brier 0.0000. → cf. cas Pétrole ci-dessous : sur cette fenêtre, pencher LONG était le bon call, même si la chaîne y arrive pour une mauvaise raison (flag figé, pas branchement du sens).
- **Or SHORT = VRAI (-0.627%).** Confirme mon jugement §3 : sur l'Or, c'est le **pondéré** (SHORT) qui avait raison, pas le primaire (LONG +0.17). Le triplet geopol +4.0 qui force le primaire en LONG était un contresens ; la pondération l'a sauvé. **Point dur : si on tradait le primaire affiché, on aurait été faux sur l'Or.**
- **Cuivre SHORT = FAUSSE (+0.894%)** et **Blé SHORT = FAUSSE (+0.885%).** Deux shorts quanti pris à revers sur 24h — bruit à seuil (0.8%), pas un défaut de chaîne news.
- 7 cellules `non-conclusive` (delta sous seuil) — normal en warm-up.

Statut global : 12/12 cellules `shadow`, N_eff=0, warm-up non-chevauchant. **Aucune éligibilité, aucune conclusion stat possible** — attendu au 1er run mesuré. Calibration score→proba toujours déterministe non calibrée empiriquement.

**Verdict mesure :** elle CONFIRME deux de mes jugements desk — (1) Pétrole LONG était le bon sens cette fenêtre, (2) sur l'Or le primaire LONG forcé par le triplet était un faux signal que seul le pondéré a rattrapé. La mesure valide donc l'idée que **le triplet geopol +1 LONG figé est dangereux sur le primaire** : il a sorti un Or LONG démenti par le marché.

## Le cas Pétrole — contresens ou prime de risque ?
**Tranche desk : ce run, Pétrole LONG est DÉFENDABLE — mais pour une raison que le brief décrit mal, et par un mécanisme qui reste cassé.**

Le brief oppose « flux frais massivement détente US-Iran (Brent -20% du pic, plus grosse perte mensuelle en 6 ans) » à « escalade Israël-Liban », et suggère que LONG serait un contresens. **Sur les données réellement dans le log, ce n'est pas le cas :**
- Le narratif « -20% / perte mensuelle » **n'est pas dans events-log** (grep négatif). Ce que le log contient comme baissier = des `reported` (Trump veut un accord, Goldman demand-destruction) — des rumeurs de négociation, pas des faits.
- Ce que le log contient comme haussier = des `confirmed:high` : frappes US-Iran autour d'Ormuz (l.861), Israël franchit le Litani au Liban (l.895), UE gèle le price cap russe (l.893). De l'escalade actée, ce jour-là.
- Net flux frais : **17 LONG (8 confirmed:high) vs 10 SHORT (1 SHORT:high, reste reported).** Un desk macro, devant CE tape, est **long la prime de risque géopol** : on n'est pas short Brent le jour où Israël traverse le Litani et où US-Iran échangent des frappes sur Ormuz, même si une rumeur d'accord traîne.
- **La mesure tranche : Pétrole LONG = VRAI +2.74% sur 24h.** Le desk et la machine sont du même côté, et le marché leur a donné raison.

**Donc : prime de risque légitime, PAS contresens — ce run.** C'est l'inverse du diagnostic du 31/05, où le flux frais était réellement de-escalation/SHORT et où le LONG figé était un vrai contresens.

**MAIS le mécanisme reste faux et ça finira par coûter :**
- Le LONG ne vient PAS d'un branchement du sens des triplets. Il vient du flag `tension_geopol_moyen_orient=1` figé à +1, qui sortirait LONG **quelle que soit** la direction du flux (le run 31/05 le prouve : flux SHORT, sortie LONG). Aujourd'hui le flag a raison par coïncidence : le flux frais EST LONG. Le jour où la détente sera réelle et confirmée, le flag sortira encore LONG et là ce sera le contresens du 31/05 qui revient.
- Les **archives Hormuz fév-avr** (21 lignes LONG:high) gonflent le compteur dans le bon sens aujourd'hui, mais ce sont des évènements déjà dans le prix depuis 4 mois — un desk ne les traderait pas. Elles ajoutent un biais LONG structurel qui maquillera le prochain retournement baissier.

**Le contexte-prix injecté a-t-il aidé ?** Partiellement et insuffisamment. Il a fait passer `materiality high→medium` et `facteur 0.7→0.42`, ce qui **abaisse la conviction pondérée**. Mais : (1) il n'a pas touché le **signe** (toujours +1 LONG), (2) il n'a pas touché le **primaire ±1** (contrib 6.3 inchangée) qui est le chiffre affiché en tête de matrice. Donc oui la conviction a baissé, non ce n'est pas assez : le primaire « LONG +9.99 » est identique à ce qu'il aurait été sans correctif.

## VERDICT GLOBAL desk

**La chaîne s'est améliorée à ses deux extrémités, mais la jointure 1→2 fuit toujours sur le sens.**
Correctifs qui ont pris : indices ETF alimentés (CAC/S&P/Nasdaq de nouveau crédibles), prix d'émission capturés (boucle de mesure rebranchée), synthèse `ia_synthese` avec contexte-prix qui abaisse la conviction (materiality medium, facteur 0.42). Réels progrès.
Correctif qui n'a PAS pris : le triplet directionnel (`BRENT:SHORT:high` / `:LONG:high`) **ne se branche toujours pas sur le signe du critère.** `tension_geopol=+1 LONG` reste figé, reliability jetée, event_id non tracé, primaire ±1 non modulé par le contexte-prix. La fuite « keyword → +1 LONG » du 31/05 est **atténuée en conviction, pas corrigée en direction.**

### Signaux DÉFENDABLES (tradables ce run)
- **Pétrole LONG** (24h surtout) — prime de risque géopol légitime, flux frais confirmed:high LONG, validé par la mesure (+2.74%). Bon sens, mauvais mécanisme.
- **Nasdaq LONG→LONG→SHORT** — meilleure cellule du run, structure de terme cohérente (momentum IA court / taux réels hauts long terme).
- **Cuivre SHORT** — COT extrême + PMI Chine mou. Classique desk.
- **S&P LONG, CAC LONG, Argent LONG** — quanti alimenté cohérent, convictions faibles mais pas absurdes.

### CONTRESENS POTENTIELS (justes par coïncidence, fragiles)
- **Pétrole LONG via le flag** : a raison aujourd'hui parce que le flux est LONG, mais sortirait LONG même en pleine détente (cf. 31/05). Bombe à retardement au prochain retournement baissier. Les archives Hormuz fév-avr aggravent le biais.

### À NE PAS TRADER (primaire pollué par le triplet geopol figé)
- **Or 24h** : primaire LONG +0.17 / pondéré SHORT -2.15. Le marché a tranché SHORT (mesure VRAI -0.63%). Le triplet geopol +4.0 a fabriqué un faux LONG.
- **VIX 1m** : primaire LONG / pondéré SHORT, même cause.
- **Café 1m** : divergence primaire/pondéré marginale.
Règle desk : **sur toute cellule ⚠ (primaire ≠ pondéré), suivre le pondéré, jamais le primaire** — c'est le primaire qui porte le flag geopol non corrigé.

### Note chaîne : 6/10 (était 4/10 au 31/05)
Ingest 8 · propagation news 3 (sens toujours pas branché, mais conviction enfin modulée) · quanti 8 (indices débloqués) · mesure 6 (prix captés, warm-up). +2 points : c'est la mesure et les indices qui montent, pas le news.

### 3 correctifs desk prioritaires (ordre)
1. **Brancher le signe du triplet sur le primaire ±1**, pas seulement le facteur pondéré. Le moteur SAIT le faire : `ble.geopolitique_mer_noire=-1` le prouve. Faire de même pour Moyen-Orient/Or/VIX → un flux net SHORT doit sortir un critère SHORT, primaire compris.
2. **Pondérer par récence et purger les archives > ~30j** (Hormuz fév-avr) du comptage directionnel — un évènement de février est dans le prix, pas un signal.
3. **Propager reliability jusqu'au calcul** (confirmed > reported > rumor module le facteur) et **tracer l'event_id source** dans chaque contrib triplet du decision-log — sans ça, impossible d'auditer pourquoi une cellule est LONG.
