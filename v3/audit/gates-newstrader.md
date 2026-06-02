# Gates pipeline — angle NEWS TRADER senior (concertation round 1)

> Objectif : un point de contrôle (gate) à chaque endroit où un trader de desk se ferait piéger.
> Format : `[Sx] Nom — ce qu'il attrape (erreur de jugement évitée) — EXISTE ✓ / MANQUE ✗ — P0/P1/P2`
> Note desk : S5 (suffisance de données) volontairement non traité (déjà en build).

---

## S1. Ingestion des flux news

Sur un desk, tout commence par : "est-ce que je vois bien tout le marché, et est-ce que ce que je vois est récent ?" Un flux mort ou en retard = on trade aveugle.

- `[S1] Santé des flux par cycle — un flux tombé (0 item) traité comme "marché calme" alors qu'on est juste sourd — EXISTE ✓ (source_monitor) — P0`
- `[S1] Latence d'ingestion (lag horodatage source → ingestion) — news vieilles de 40 min ingérées comme fraîches, on entre après que le marché a déjà bougé — MANQUE ✗ — P0`
- `[S1] Couverture par classe d'actif — tous les flux FX morts mais on conclut quand même sur EURUSD parce qu'un flux equities tourne — MANQUE ✗ — P1`
- `[S1] Détection volume anormal (spike/famine) — 5x le volume normal = événement majeur OU flux qui boucle/duplique ; famine = panne silencieuse — MANQUE ✗ — P1`
- `[S1] Intégrité horodatage / fuseau — timestamps en TZ mixtes (UTC vs local) → fraîcheur (S3) et prix d'émission (S8) faussés — MANQUE ✗ — P0`
- `[S1] Garde black-out / halte marché — news ingérées hors séance ou pendant halte, à traiter différemment (gap d'ouverture, pas exécutable) — MANQUE ✗ — P2`

## S2. Extraction DeepSeek (triplets actif/sens/horizon + nature + synthèse)

C'est LE point le plus dangereux du pipeline. Le LLM peut inverser un sens, halluciner un actif, ou se tromper de signe macro. Un trader ne fait jamais confiance à une lecture de sens non challengée.

- `[S2] Cohérence de signe (sanity du sens) — DeepSeek classe LONG une news intrinsèquement baissière (ex. "OPEC augmente la production" → SHORT pétrole, pas LONG ; "Fed hawkish surprise" → SHORT actions). C'est l'erreur n°1 du desk — MANQUE ✗ — P0`
- `[S2] Validation de l'actif extrait (ticker existe & tradable) — DeepSeek invente/mappe un actif non couvert ou ambigu ("Tesla" → TSLA equity vs exposition auto) — MANQUE ✗ — P0`
- `[S2] Anti-hallucination de citation — synthèse directionnelle qui affirme un chiffre/fait absent du texte source (CPI "à 3,1%" jamais écrit dans la news) — MANQUE ✗ — P0`
- `[S2] Garde-fou signe macro (CPI/NFP/taux) — table de référence figée : CPI > attendu = baissier actions / haussier USD ; chômage > attendu = baissier USD ; etc. L'IA se trompe régulièrement de signe sur le contre-intuitif — MANQUE ✗ — P0`
- `[S2] Confiance / abstention d'extraction — triplet produit avec faible confiance traité comme certain ; il faut un seuil sous lequel on s'abstient plutôt que d'inventer un sens — MANQUE ✗ — P1`
- `[S2] Cohérence horizon vs nature — news structurelle (réglementation) classée horizon intraday, ou flash earnings classé horizon "long terme" — incohérence nature↔horizon — MANQUE ✗ — P1`
- `[S2] Détection conditionnel / futur / rumeur — "la Fed POURRAIT baisser", "selon des sources" traité comme fait acté → sens directionnel surévalué — MANQUE ✗ — P1`
- `[S2] Schéma de sortie strict (validation JSON triplets) — triplet mal formé / champ manquant qui casse silencieusement le scoring en aval — EXISTE ✓ (à confirmer) — P2`

## S3. Dédup / repost / nature / fraîcheur

Le piège classique du desk : trader une news comme si elle était neuve alors qu'elle est déjà cotée. "Buy the rumor, sell the news" — quand ça sort partout, c'est souvent déjà dans le prix.

- `[S3] Dédup texte / quasi-dup — la même dépêche reprise par 5 sources compte comme 5 signaux et fait basculer un actif (faux consensus) — EXISTE ✓ (T1/T2, dédup) — P0`
- `[S3] Détection "déjà cotée" (news stale / already priced) — événement annoncé hier, repris aujourd'hui en angle nouveau ; on entre sur un move déjà fait. Aucun garde ne vérifie si le prix a DÉJÀ réagi — MANQUE ✗ — P0`
- `[S3] Repost / recyclage éditorial — article "rewrite" d'un fait ancien (anniversaire, rétrospective) classé comme nouvelle — EXISTE ✓ (nature) — partiel — P1`
- `[S3] Fenêtre de fraîcheur calibrée par horizon — une news de 3h est morte pour l'intraday mais valide pour le swing ; un seuil unique de fraîcheur sur-filtre ou sous-filtre — MANQUE ✗ — P1`
- `[S3] Anti-cluster mono-source — 4 items "indépendants" qui viennent tous du même wire (Reuters relayé) → pondération à diviser, pas à additionner — MANQUE ✗ — P1`
- `[S3] Détection démenti / correction / mise à jour — une news suivie d'un démenti 20 min après ; sans chaînage, on garde le signal initial faux — MANQUE ✗ — P0`

## S4. Calcul critères quant (prix Twelve Data, COT, FRED)

Le quant confirme ou contredit la news. Le piège : des données stale, un mauvais symbole, ou un COT/FRED périmé qu'on lit comme frais. Un prix faux contamine tout l'aval (scoring ET mesure VRAI/FAUX).

- `[S4] Fraîcheur du prix (Twelve Data) — dernier prix daté de la veille / week-end traité comme live ; biais d'entrée et S8 faussés — MANQUE ✗ — P0`
- `[S4] Mapping symbole news ↔ symbole data — l'actif extrait en S2 ne pointe pas le bon ticker Twelve Data (CL vs WTI vs USOIL) → on score le mauvais marché — MANQUE ✗ — P0`
- `[S4] Plausibilité du prix (anti-outlier/spike erroné) — tick aberrant de l'API (prix x10, 0, négatif) pris pour un vrai move — MANQUE ✗ — P0`
- `[S4] Péremption COT — COT publié hebdo (vendredi, données de mardi) : déjà 3-6 jours de retard ; le lire comme positionnement "actuel" est une erreur — MANQUE ✗ — P1`
- `[S4] Péremption / révision FRED — séries macro révisées rétroactivement ; vintage non figé → backtest et conclusion changent sous nos pieds — MANQUE ✗ — P1`
- `[S4] Cohérence devise / unité — prix en USD vs devise locale, % vs points de base, mélange d'unités dans les seuils — MANQUE ✗ — P2`
- `[S4] Gestion trou de données (API timeout/quota) — un critère quant absent silencieusement traité comme neutre au lieu de réduire la confiance — MANQUE ✗ (recouvre S5) — P1`

## S6. Scoring / pondération

Là où une seule news mal pondérée fait basculer un actif entier. Le desk se méfie du "single-point of failure" : un signal dominant non vérifié qui écrase tout le reste.

- `[S6] Anti-bascule mono-news (concentration) — un actif passe LONG→SHORT à cause d'UN item ; il faut un plafond de contribution par news unique et un quorum minimal — MANQUE ✗ — P0`
- `[S6] Bornage de la normalisation — un score normalisé qui sature (tout à +1) parce que l'échelle n'est pas robuste aux extrêmes → perte de granularité — MANQUE ✗ — P1`
- `[S6] Audit du coef_nature — un coefficient de nature (rumeur vs officiel) mal appliqué qui sur-pondère une rumeur au niveau d'un communiqué officiel — MANQUE ✗ — P1`
- `[S6] Pertinence par horizon (cohérence pondération↔horizon) — news intraday pondérée dans la conclusion swing et inversement (fuite de signal entre horizons) — MANQUE ✗ — P1`
- `[S6] Détection signaux contradictoires non résolus — moitié des news LONG, moitié SHORT, score net ≈ 0 masqué en "léger LONG" : il faut signaler le CONFLIT, pas moyenner aveuglément — MANQUE ✗ — P0`
- `[S6] Garde anti double-comptage — le même fait pondéré via news ET via critère quant (ex. la news EST le chiffre macro déjà dans FRED) → signal compté deux fois — MANQUE ✗ — P2`

## S7. Conclusion LONG/SHORT

La règle "jamais-neutre" est un risque assumé : elle force une direction même quand le marché ne donne rien. Le desk veut un garde-fou pour ne pas forcer un trade sur du bruit.

- `[S7] Plancher de conviction (abstention même en jamais-neutre) — forcer LONG/SHORT sur un score quasi nul = trader le bruit ; il faut un drapeau "faible conviction" même si on doit afficher un sens — MANQUE ✗ — P0`
- `[S7] Cohérence news_dominant ↔ direction finale — la news dominante est SHORT mais la conclusion sort LONG (le quant a renversé sans justification tracée) → incohérence à bloquer ou expliquer — MANQUE ✗ — P0`
- `[S7] Cohérence inter-horizons — LONG intraday + SHORT swing sur le même actif sans note de transition : acceptable mais doit être EXPLICITE, pas un bug silencieux — MANQUE ✗ — P1`
- `[S7] Garde direction vs quant (news contre tendance) — conclusion LONG alors que le prix/COT/macro pointent SHORT : le contrarian est permis mais doit être justifié, pas subi — MANQUE ✗ — P1`
- `[S7] Plan d'horizon exécutable — conclusion sans niveau/échéance cohérents avec l'horizon (plan "intraday" avec échéance à 2 semaines) — MANQUE ✗ — P1`
- `[S7] Traçabilité du verdict (audit trail) — impossible de reconstruire POURQUOI LONG (quelles news, quels poids) → pas d'apprentissage post-mortem — MANQUE ✗ — P2`

## S8. Mesure VRAI/FAUX (Journaliste)

Le scoring du desk : la mesure VRAI/FAUX doit être incontestable. Le piège : un prix d'émission mal capté ou une échéance flottante qui transforme un faux en "vrai" a posteriori (data snooping involontaire).

- `[S8] Verrouillage du prix d'émission (entry lock) — prix d'entrée recalculé après coup avec un tick plus favorable → biais qui gonfle artificiellement le taux de réussite — MANQUE ✗ — P0`
- `[S8] Échéance figée à l'émission — échéance ajustée a posteriori pour tomber sur un moment favorable (moving goalposts) — MANQUE ✗ — P0`
- `[S8] Cohérence du prix de mesure (même source/symbole qu'à l'entrée) — entrée mesurée sur Twelve Data, sortie sur une autre source/symbole → écart structurel pris pour un move — MANQUE ✗ — P0`
- `[S8] Seuils VRAI/FAUX définis AVANT échéance — seuil de validation décidé après avoir vu le résultat — MANQUE ✗ — P1`
- `[S8] Gestion gap / illiquidité à l'échéance — échéance tombe sur un week-end/halte : prix de référence = dernier tick vs ouverture suivante (peut inverser le verdict) — MANQUE ✗ — P1`
- `[S8] Traitement des trades "neutres forcés" — un trade à conviction quasi nulle (cf. S7) compté plein pot dans le scoring fausse le taux de réussite global — MANQUE ✗ — P1`

## S9. Publication (bulletin / HTML / biais LONG-SHORT)

Dernière barrière avant que le lecteur agisse. Le piège : un bulletin qui affiche une conviction que l'analyse n'a pas, ou un biais LONG-SHORT incohérent avec le détail par actif.

- `[S9] Cohérence biais agrégé ↔ détail par actif — le bandeau "biais LONG" alors que la majorité des actifs sont SHORT (erreur d'agrégation visible par le lecteur) — MANQUE ✗ — P0`
- `[S9] Affichage du niveau de conviction / abstention — un "faible conviction" (S7) doit être visible dans le bulletin, pas masqué en directionnel net qui pousse à surtrader — MANQUE ✗ — P0`
- `[S9] Garde-fou de complétude (no silent drop) — un actif disparaît du bulletin suite à une erreur en amont sans mention → le lecteur croit "pas de signal" — MANQUE ✗ — P1`
- `[S9] Horodatage & péremption du bulletin — bulletin publié avec timestamp ambigu / sans heure de validité → lu trop tard, signaux intraday morts — MANQUE ✗ — P1`
- `[S9] Cohérence HTML ↔ données source — divergence entre le rendu HTML et les données calculées (arrondi, troncature, mauvais champ affiché) — MANQUE ✗ — P2`
- `[S9] Disclaimer / non-advice — bulletin client-facing sans cadre (conformité, "pas un conseil") — MANQUE ✗ — P2`

---

## TOP 5 des gates manquants les plus critiques (angle desk)

Classés par "combien d'argent ça fait perdre quand ça casse", priorité au plus traître (silencieux + fréquent).

1. **[S2] Cohérence de signe (sanity du sens)** — P0. L'erreur la plus chère et la plus fréquente : DeepSeek inverse le sens d'une news contre-intuitive ("OPEC augmente la prod" classé haussier pétrole, "Fed hawkish" classé haussier actions). Tout le pipeline aval est correct mais part du mauvais côté. Sans garde-fou de signe (table de référence + double-check), on trade systématiquement à l'envers sur le contre-intuitif.

2. **[S3] Détection "déjà cotée" (already priced)** — P0. Le piège n°1 du news trading : entrer sur un move déjà fait. Rien dans le pipeline ne vérifie si le prix a DÉJÀ réagi à la news. Sans ça, on génère des signaux "VRAIS" en backtest qui sont en réalité non exécutables (on serait entré après le saut).

3. **[S6] Anti-bascule mono-news (concentration)** — P0. Une seule news non vérifiée qui retourne un actif entier = single point of failure. Plafond de contribution par news + quorum minimal. Couplé à la détection de signaux contradictoires (ne pas moyenner un 50/50 en "léger LONG").

4. **[S8] Verrouillage prix d'émission + échéance figée** — P0. Sans entry lock et échéance gelée à l'émission, le scoring VRAI/FAUX est corruptible (moving goalposts) : le taux de réussite affiché devient une illusion, et toute décision basée dessus est faussée. C'est la crédibilité de tout le système.

5. **[S2] Garde-fou signe macro (CPI/NFP/taux)** — P0. Cas particulier critique de la sanity de signe, mais assez systémique pour mériter sa propre table figée : CPI haut = baissier actions / haussier USD, chômage haut = baissier USD, etc. L'IA se trompe de signe précisément sur les chiffres macro où l'enjeu est le plus gros (jours de publication = plus gros volumes).

**Mention desk** : ces 5 sont tous P0 et tous MANQUANTS. Les 4 premiers couvrent les 4 façons distinctes de perdre de l'argent (mauvais côté / trop tard / sur-concentration / mesure corrompue). Le 5e est le sous-cas le plus rentable à blinder en premier car concentré sur les jours macro.

