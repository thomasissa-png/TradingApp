# GATES — Audit SPÉCULATEUR (trend-follower)

> Concertation round 1. Angle : **éviter les mauvaises positions de tendance**.
> Question filtre pour CHAQUE gate : *est-ce que ça m'empêche de prendre une position à contre-tendance, ou de flipper sur du bruit ?*
> Format : `[Sx] Nom — ce qu'il attrape — EXISTE ✓ / MANQUE ✗ — P0/P1/P2`

Brutal. Un gate qui ne protège pas la **direction** ne mérite pas de tokens.

---

## S1 — Ingestion flux news

`[S1] Source-alive — détecte une source morte/figée (RSS qui ne bouge plus) qui me ferait croire à "pas de nouvelle = tendance intacte" alors que je suis aveugle — EXISTE ✓ (source_monitor) — P0`
`[S1] Couverture-actif minimale — au moins 1 flux vivant par actif suivi ; sinon je trend-suis un actif sur du quant seul SANS jamais voir le retournement narratif — MANQUE ✗ — P1`
`[S1] Timestamp-trust — la pubDate du flux n'est pas falsifiée/absente (sinon une vieille news passe pour fraîche et déclenche un faux retournement) — PARTIEL (fraîcheur en S3, mais validité du timestamp à l'ingestion non gardée) — P1`

> Trend-follower : S1 est l'angle mort le plus sournois. Une source figée = je crois la tendance confirmée par "silence", alors que le marché parle ailleurs. source_monitor couvre le cas dur (mort), pas le cas "vivante mais incomplète par actif".

## S2 — Extraction DeepSeek (triplets + nature + synthèse)

`[S2] Schéma-valide — triplet bien formé (actif connu / sens ∈ {long,short} / horizon ∈ {24h,7j,1m}) ; un triplet pourri = direction fantôme injectée dans le score — PARTIEL (parsing existe, mais gate de rejet dur à confirmer) — P1`
`[S2] Nature obligatoire — chaque triplet porte une `nature` ∈ {5 valeurs fermées} ; sans nature, je ne peux pas distinguer un signal structurel d'un coup de bruit ponctuel = cause racine du flip — EXISTE ✓ (spec Phase 2, en build) — P0`
`[S2] Anti-hallucination direction — DeepSeek ne doit pas inverser le sens du texte source (un titre baissier sorti "long") ; aucun garde-fou de cohérence texte→sens — MANQUE ✗ — P0`
`[S2] Confiance extraction — score de confiance DeepSeek seuillé ; une extraction "molle" ne doit pas peser comme une certitude dans la tendance — PARTIEL (reliability propagée, mais pas un gate de rejet) — P2`

> Trend-follower : le pire ici c'est l'**inversion de sens** par le LLM. Si DeepSeek lit un titre "OPEC maintient les quotas" (neutre/haussier pétrole) et sort SHORT, j'ouvre une position à contre-tendance sur une erreur de lecture pure. Personne ne re-vérifie texte→direction.

## S3 — Dédup / repost / nature / fraîcheur

`[S3] Anti-repost (T1) — un même event reposté 20× ne gonfle pas artificiellement un faux retournement par volume — EXISTE ✓ (T1, event_id SHA-256 + Levenshtein ≤15%) — P0`
`[S3] Fraîcheur / anti-stale (T2) — une news >30j (STALE) ou périmée ne déclenche pas un flip sur info morte — EXISTE ✓ (T2, STALE_THRESHOLD=30j, FRESHNESS_OVERRIDE_DAYS=3j) — P0`
`[S3] Exclusion deja_cote / non_tradable — une info déjà price-in ne re-pousse pas la position dans un sens déjà consommé par le marché — EXISTE ✓ (nature exclut deja_cote/verbal/non_tradable du scoring) — P0`
`[S3] Suffisance T1/T2 contre le flip réel ?? — T1/T2 attrapent volume+âge, MAIS PAS "1 seule news fraîche, unique, non-reposted, qui retourne une tendance de fond solide". C'est exactement le piège trend-follower n°1 et il passe les deux gates. — MANQUE ✗ — P0`
`[S3] Quorum de confirmation news — exiger ≥N sources INDÉPENDANTES (pas reposts) avant qu'une news puisse inverser une tendance établie — MANQUE ✗ — P0`

> Trend-follower BRUTAL : T1/T2 sont nécessaires mais **PAS suffisants**. Ils répondent "cette news est-elle gonflée/vieille ?" — ils ne répondent JAMAIS "cette news, même propre et fraîche, mérite-t-elle de casser une tendance de fond ?". Une dépêche unique, fraîche, bien formée = elle passe T1 (pas de repost), passe T2 (fraîche), et si elle est notée `nature=structurel high+confirmed` elle peut **override le cap α=0.8** et flipper la cellule. Or une news ponctuelle isolée n'est PAS une tendance. Il manque un **quorum** et un **test de force-de-tendance préexistante** (cf. S6/S7).

## S4 — Calcul critères quant (Twelve Data, COT, FRED)

`[S4] Prix non-périmé — le snapshot Twelve a < X h ; un prix figé/en retard fausse le z-score et donc le sens du momentum — PARTIEL (garde anti-doublon <2h sur snapshot cycle, mais pas un gate de staleness prix par symbole) — P0`
`[S4] Cohérence ETF-proxy ↔ sous-jacent — SPY/QQQ/FCHI/VIXY sont des proxys ; un décrochage proxy/indice (dividende, tracking error, gap) ne doit pas être lu comme un mouvement de tendance — MANQUE ✗ — P1`
`[S4] COT fraîcheur (publication hebdo + lag) — le COT a un lag structurel (T+3) ; le scorer ne doit pas traiter un COT vieux de 6j comme un signal de positionnement actuel — PARTIEL (FRED/CFTC ingéré, fraîcheur explicite non gardée) — P1`
`[S4] Outlier / spike garde — un tick aberrant (flash, mauvais print Twelve) ne crée pas un faux z-score extrême qui retourne la cellule — MANQUE ✗ — P1`
`[S4] Sens du z-score = sens du momentum — vérifier que le signe du critère quant correspond bien à la direction réelle du prix récent (anti-bug de signe) — MANQUE ✗ — P0`

> Trend-follower : un **bug de signe** ou un **prix périmé** sur le bloc quant est plus dangereux qu'une mauvaise news, parce que le quant est censé être le "cœur de la tendance". Si le z-score sort positif alors que le prix baisse depuis 5 séances, je trade le bruit contre la vague. Aucun gate ne confronte aujourd'hui *signe du critère* vs *direction prix observée*.

## S5 — Suffisance de données (NON TRAITÉ — déjà en build)

> Hors périmètre de cet audit (🔧 en build). Je note seulement, côté tendance : la suffisance ne doit pas se contenter de "assez de critères" mais "assez de critères **quant** porteurs de momentum" — une cellule décidée à 90% sur news et 10% quant n'est pas une décision de tendance, c'est un pari événementiel. À garder à l'esprit dans S5, traité en S6/S7 ci-dessous.

## S6 — Scoring / pondération

`[S6] Cap anti-inversion news α=0.8 — empêche la news de retourner seule une cellule sauf high+confirmed — EXISTE ✓ (plan horizon, override si high+confirmed) — P0`
`[S6] Drapeau ratio_news / 📰 — signale quand >50% du score vient de la news (décision fragile, pas une tendance) — EXISTE ✓ — P1`
`[S6] Divergence quant vs news ARBITRÉE — quand quant dit LONG et news dit SHORT (ou inverse), QUI gagne et POURQUOI doit être tranché par une règle explicite, pas par la somme aveugle des scores. Aujourd'hui c'est une addition : ±1 ou pondéré, le signe final sort du total sans détecter la contradiction. — MANQUE ✗ — P0`
`[S6] Score vs momentum prix récent — si le score final contredit la direction du prix sur la fenêtre de l'horizon (LONG mais prix en baisse nette 7j), lever un drapeau "contre-tendance" — MANQUE ✗ — P0`
`[S6] Garde macro / risk-off transverse — si un critère macro de régime est actif (VIX spike, risk-off), il doit pouvoir contraindre/pénaliser les cellules actions LONG, pas être noyé dans la moyenne — MANQUE ✗ — P1`
`[S6] Stabilité du score (anti-flip marginal) — un score qui passe de +0.05 à -0.05 d'un cycle à l'autre flippe la position sur du bruit ; exiger une marge minimale ou une hystérésis pour changer de sens vs cycle précédent — MANQUE ✗ — P0`

> Trend-follower BRUTAL : le système **additionne** quant et news. Une addition ne sait pas qu'elle vient d'arbitrer une contradiction. Quand le prix monte et la news dit SHORT, le total peut sortir SHORT à +51% news / -49% quant — et je shorte une vague haussière en croyant suivre un "score". Il faut un gate qui DÉTECTE la divergence et applique une règle trend-first (par défaut : la tendance prix gagne, la news doit être high+confirmed+quorum pour la renverser). Et le **flip marginal** (signe qui bascule sur 0.0X) est le bruit pur : sans hystérésis je change de camp chaque cycle.

## S7 — Conclusion LONG/SHORT (jamais-neutre, news_dominant, plan horizon)

`[S7] Jamais-neutre — force une décision (pas de zone grise paralysante) — EXISTE ✓ (LONG si score>0, SHORT sinon) — P0`
`[S7] Flag news_dominant — la conclusion expose quand elle est portée par la news — EXISTE ✓ (drapeau 📰) — P1`
`[S7] Cohérence inter-horizons — détecter LONG 24h / SHORT 7j / LONG 1m sur le même actif SANS justification (retournement attendu). Aujourd'hui les 3 horizons sont calculés via pertinence par critère, mais RIEN ne vérifie la plausibilité de la séquence. LONG 24h + SHORT 7j sans event daté entre les deux = incohérence muette. — MANQUE ✗ — P0`
`[S7] Cohérence inter-actifs corrélés — si je suis LONG S&P et LONG VIX en même temps (anti-corrélés structurels), un des deux est faux — aucun gate de cohérence de panier — MANQUE ✗ — P1`
`[S7] Respect d'un gate macro actif dans la conclusion — la conclusion ne doit pas rester LONG actions si un drapeau risk-off est actif au niveau régime (lien avec S6) — MANQUE ✗ — P1`
`[S7] Continuité vs conclusion précédente — la conclusion expose si elle FLIP par rapport au dernier cycle et exige une raison traçable (event_id ou franchissement de seuil quant), pas juste "le score a changé" — MANQUE ✗ — P0`

> Trend-follower : la conclusion est le dernier rempart avant que Thomas ouvre un turbo. **L'incohérence inter-horizons** est mortelle ici : un trader trend-follower lit "LONG 24h / SHORT 7j" et soit il ne comprend pas, soit il prend la mauvaise jambe. Une séquence d'horizons valide doit raconter UNE histoire (continuation, ou retournement daté). Et tout FLIP de conclusion doit pointer une CAUSE (event daté ou seuil quant franchi) — sinon c'est du bruit habillé en décision.

## S8 — Mesure VRAI/FAUX (Journaliste)

`[S8] Prix d'émission stampé — la mesure se fait contre le prix au moment de la conclusion (pas de look-ahead) — EXISTE ✓ — P0`
`[S8] Fenêtre de mesure = horizon — VRAI/FAUX évalué sur l'horizon annoncé (24h mesuré à 24h, pas à 1h ni 7j) — PARTIEL (à confirmer non-chevauchant) — P0`
`[S8] Non-chevauchement — éviter de compter 3× la même vague (24h quotidien / 7j hebdo / 1m mensuel) ce qui gonflerait la confiance dans un moteur de tendance faux — EXISTE ✓ (protocole défini, à durcir) — P0`
`[S8] Mesure séparée flip vs continuation — taux de réussite des conclusions QUI ONT FLIPPÉ vs celles qui CONTINUENT la tendance. Sans ça, je ne sais pas si mes retournements sont du skill ou du bruit. C'est LE chiffre qui valide/invalide un trend-follower. — MANQUE ✗ — P0`
`[S8] Attribution news-driven vs quant-driven — mesurer le taux de réussite des cellules news_dominant séparément ; si les flips news perdent, on durcit le cap α — PARTIEL (champs p2_* en shadow, attribution flip non isolée) — P1`

> Trend-follower : un moteur de tendance se juge sur **"mes retournements gagnent-ils plus souvent que mes continuations ?"**. Aujourd'hui la mesure agrège tout. Tant que flip et continuation ne sont pas mesurés séparément, je ne peux pas savoir si mon système retourne au bon moment ou s'il se fait fumer à chaque faux signal. C'est mesurable dès maintenant dans le decision-log.

## S9 — Publication (bulletin / HTML / biais)

`[S9] Drapeau biais directionnel global — signale si le bulletin est anormalement déséquilibré (ex. 61% LONG) = soit régime, soit bug systématique — PARTIEL (biais LONG suivi en audit, pas un gate de publication) — P1`
`[S9] Affichage explicite des conclusions à risque — toute cellule FLIP, news_dominant ou contre-momentum doit être visuellement signalée à Thomas AVANT exécution (📰 + un drapeau "retournement" / "contre-tendance") — PARTIEL (📰 existe, "contre-tendance" et "flip" non affichés) — P0`
`[S9] Cohérence bulletin ↔ decision-log — le HTML publié reflète exactement le score/sens loggé (pas de divergence d'arrondi/template qui inverserait un affichage) — MANQUE ✗ — P2`
`[S9] Gate shadow obligatoire — rien émis tant que KPI non atteints — EXISTE ✓ (mode shadow, KILL-CRITERION) — P0`

> Trend-follower : la publication est la dernière chance d'avertir l'humain. Si une cellule est en contre-momentum ou vient de flipper sans cause forte, Thomas doit le VOIR (drapeau visuel), pas le déduire. Un bulletin qui présente un SHORT contre-tendance avec la même typo qu'un LONG de continuation solide = il exécutera les deux pareil.

---

## TOP 5 — gates manquants les plus critiques pour la justesse de tendance

Classés par dégât direct sur la **direction de position**. Tous P0.

1. **[S6] Divergence quant vs news arbitrée** — le système ADDITIONNE au lieu d'ARBITRER. Quand le prix monte et la news dit SHORT, le total peut sortir SHORT sans que personne ne voie qu'on vient de trader contre la vague. Règle trend-first à câbler : la tendance prix gagne par défaut ; la news ne renverse que si high+confirmed+quorum. **C'est la première cause de position à contre-tendance.**

2. **[S3] Test de force-de-tendance avant flip news (le trou de T1/T2)** — T1/T2 attrapent le volume et l'âge, jamais "une news propre et fraîche suffit-elle à casser une tendance de fond solide ?". Une dépêche unique qui passe les deux gates peut override le cap α et flipper la cellule. Manque : **quorum de sources indépendantes + seuil de force-de-tendance préexistante** pour autoriser un retournement.

3. **[S7] Cohérence inter-horizons** — LONG 24h / SHORT 7j / LONG 1m sortent sans qu'aucun gate ne vérifie que la séquence raconte une histoire plausible (continuation ou retournement daté). Pour un trend-follower c'est une incohérence mortelle : on lit la mauvaise jambe. Gate : valider la plausibilité de la séquence d'horizons, exiger un event daté pour tout changement de sens entre horizons.

4. **[S6] Hystérésis anti-flip marginal** — un score qui bascule de +0.05 à -0.05 flippe la position sur du bruit pur, chaque cycle. Gate : marge minimale / hystérésis pour CHANGER de sens vs cycle précédent. Sans ça je me fais sortir et re-rentrer à contretemps sur le bruit, le pire ennemi du trend-follower.

5. **[S8] Mesure flip vs continuation séparée** — impossible aujourd'hui de savoir si mes retournements gagnent. C'est LE chiffre qui valide un moteur de tendance. Mesurable dès maintenant dans le decision-log (champ `is_flip` + taux de réussite ventilé). Sans lui, on durcit/relâche le cap α à l'aveugle.

> **Verdict trend-follower :** le pipeline est solide sur le bruit news (T1/T2/nature/cap α — bon travail). Il est AVEUGLE sur trois fronts qui produisent directement des positions à contre-tendance : (a) l'arbitrage quant-vs-news est une addition, pas une décision ; (b) rien ne confronte le sens final au momentum prix réel ; (c) le bruit marginal flippe les positions sans hystérésis. Tant que ces trois-là ne sont pas câblés, le système peut sortir un SHORT confiant en plein milieu d'une vague haussière — et personne dans la chaîne ne lèvera la main.

