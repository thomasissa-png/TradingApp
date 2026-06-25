# Audit — Fallback « dernière valeur valide » (incident cacao 25/06)

> Panel des 3 experts (Analyst · News Trader · Spéculateur) — concertation contradictoire puis verdict commun.
> Pièces : `v3/data/criteres-health.md` (cycle 05:23 UTC), `v3/config/fiches/cacao.yml`, `v3/scripts/criteres_calculator.py` (`fetch_open_meteo_anomaly` L1534 / `_handle_meteo` L2733), `v3/scripts/scoring_analyste.py` (`COVERAGE_MIN=0.40` L71, `SELECTION_COVERAGE_MIN=0.70` L2629, `derniere_direction_valide` L835).
> Garde-fous fondateur : zéro invention · échec visible · mesurer avant d'agir sur le SIGNAL · WIN RATE ONLY.

## 0. Faits établis sur pièces (non contestés)

- Incident confirmé dans `criteres-health.md` (25/06, 05:23 UTC) :
  - `Open-Meteo injoignable (récents)` → `6.8,-5.3:net_error` (2 occ.) = la météo CI+Ghana (clé `meteo_ci_ghana_precip_30j`, **poids 11**, le plus lourd de la fiche) tombe n/a sur **panne réseau**, pas sur une vraie absence de donnée.
  - `Source z-score non programmatique` → `arrivees_port_abidjan_sanpedro_20j` (**poids 9**) = **aucune source automatisée** (trou structurel, pas une panne).
- Poids n/a cumulé = **20** sur une fiche dont le total tourne ~55-60 → couverture cacao **41 %**, sous `SELECTION_COVERAGE_MIN=0.70` → écarté du Top 3 (« fragile, couverture insuffisante »).
- Tous les autres signaux pointaient LONG et étaient justes : momentum 20j +1,78 / 7j +1,19, positionnement +1,26, news El Niño +3,20, news cartel CI+Ghana en séance. Le cacao a fait **+7,13 %** (meilleur move du jour).
- Précédent code décisif : `derniere_direction_valide` (L835) persiste déjà la **direction de sortie** d'une cellule, mais **PAS la valeur d'entrée d'un critère** → elle ne restaure donc PAS la couverture. C'est exactement le trou que la reco vise.

Le diagnostic « direction du système juste, filtre de couverture aveuglé par une source en panne sans fallback » **tient sur pièces**. Désaccord du panel : non pas sur le diagnostic, mais sur la **réponse**.

---

## 1. Analyst — le diagnostic est-il quantitativement sain ?

**Le diagnostic tient.** Réutiliser une valeur reportée est statistiquement sain **uniquement pour des critères dont la demi-vie >> l'âge de la valeur reportée**. Critère de décision : la valeur reportée est acceptable tant que l'erreur qu'elle introduit (variation possible sur l'âge) reste petite devant le bruit du critère (`zscore_div`).

Classement des critères cacao par vitesse de variation :

| Critère | Clé | Poids | Demi-vie | Fallback OK ? | Plafond d'âge proposé |
|---|---|---:|---|---|---|
| Météo CI+Ghana 30j | `meteo_ci_ghana_precip_30j` | 11 | très lente (anomalie sur 30j vs climato 5 ans) | **OUI** | **5 j ouvrés** |
| Arrivées ports 20j | `arrivees_port_abidjan_sanpedro_20j` | 9 | lente (cumul 20j) | OUI *si source existait* | 5 j ouvrés |
| Positionnement COT/options | `hf_positioning_flux_options` | 5 | hebdo (COT = 1 pub/sem) | OUI | **8 j** (1 cycle COT) |
| Taux de change CFA/cédi | `usd_cfa_usd_cedi` | 3 | moyenne | OUI | 3 j ouvrés |
| Momentum 20j / 7j | `momentum_prix_20j/7j_cacao` | 6 / 6 | **rapide (prix)** | **NON** | exclus |
| Spread NY-Londres | `spread_ny_london` | 4 | rapide (prix) | **NON** | exclus |

**Plafonds par TYPE** (pas un plafond unique) :
- Météo / structurel offre (30j) : **5 j ouvrés** — une anomalie de précipitations sur 30j ne bouge quasi pas en 5j ; l'erreur introduite est < bruit `zscore_div=2`.
- Taux / COT : **8 j** (couvre 1 publication COT hebdo + jours fériés).
- Prix / momentum / vol intraday : **0 (exclus)** — une valeur de prix périmée est *trompeuse*, pas conservatrice (cf. le bug de mesure or 8h, déjà documenté : une réf prix périmée a caché des pertes).

**Risque de fausser la couverture/score** : OUI si on compte la valeur reportée à **plein poids** sans la dégrader. Recommandation Analyst : la valeur reportée **compte dans la couverture** (sinon le fallback ne sert à rien) mais doit être **marquée `⚠️ reportée`** ET, idéalement, **comptée au poids plein dans la couverture mais pas dans la conviction** au-delà d'un certain âge. Sinon on recrée le risque inverse du « confiant mais aveugle » : confiant sur du vieux.

---

## 2. News Trader — les news auraient-elles dû sauver le pari ?

**La couche news a parfaitement fait son travail.** El Niño (+3,20) et cartel CI+Ghana (en séance) étaient des catalyseurs d'OFFRE forts, confirmés, dans le bon sens (haussier). **Mais elles n'ont PAS pu sauver le pari** parce que la sélection se fait sur la **couverture QUANT**, et la couche news n'entre pas dans ce calcul de couverture.

Point dur : **non, un signal news ne DOIT PAS, à lui seul, faire passer un pari en surclassant la couverture quant faible.** C'est la ligne fondateur tranchée 20/06 (S9) : le **quant reste dominant**, `NEWS_DOMINANT_RATIO` inchangé, les news sont du **contexte**, pas le moteur. Faire entrer un « override news » dans la sélection violerait frontalement cette décision et le mindset « la news ne renverse jamais la tendance ».

**Nuance que je défends quand même** : ici les news ne *renversaient* rien — elles **CONFIRMAIENT** un quant déjà LONG sur tous ses signaux vivants (momentum, positionnement). Le cas « quant unanime LONG + news fortes confirmées dans le même sens, écarté pour cause de SOURCE en panne » n'est pas le cas « news contre quant ». Donc : la news ne doit pas *sauver* le pari, mais elle peut servir de **signal de confirmation à mesurer** (shadow) dans une future règle de sélection, sans jamais devenir un override de signal.

---

## 3. Spéculateur — combien coûte de rater ça, et quelle réponse d'abord ?

**Le coût est réel et asymétrique.** +7,13 %, meilleur move du jour, raté à cause d'un `net_error` Open-Meteo, alors que TOUS les signaux décisionnels (hors les 2 sources mortes) disaient LONG. En turbo, c'est un gagnant franc laissé sur la table. Sur 30 jours de shadow forward (jalon 08/08), si une panne réseau benche ne serait-ce qu'un gagnant/semaine, on dégrade le N et on fausse à la baisse le win-rate de la Sélection — qui est *elle-même en procès*.

**Le fallback est-il LA bonne réponse ? Oui, mais ce n'est pas la SEULE.** Il y a deux maladies distinctes ici :
1. **Une panne** (météo `net_error`) → le fallback la soigne directement et proprement.
2. **Un trou structurel** (arrivées ports : aucune source) → le fallback n'a **rien à reporter** (jamais de valeur valide à persister) → ce critère reste n/a même avec fallback. Il faut **réparer/remplacer la source** OU **retirer/repondérer le critère** s'il reste durablement mort (sinon poids 9 mort en permanence = couverture cacao plafonnée).

**Ordre que je défends (et qui m'oppose à l'Analyst, voir §4)** :
- **D'ABORD le fallback** (rapide, sûr, soigne la panne, zéro impact signal direct sur les critères lents).
- **ENSUITE, en shadow uniquement**, instrumenter une **règle de sélection « haute-conviction »** : quand quant unanime + couverture franche *sur les critères VIVANTS* (≥ X poids vivant) + news confirmées, autoriser la sélection même si la couverture *totale* est plombée par des sources mortes. À **mesurer avant d'activer** (mindset fondateur). Le fallback seul ne couvre pas le cas où la source reste morte plusieurs jours (au-delà du plafond d'âge).

---

## 4. Concertation contradictoire (désaccords + résolution)

**Désaccord n°1 — La valeur reportée doit-elle compter à PLEIN poids dans la couverture ?**
- *Spéculateur* : OUI plein poids, sinon le fallback ne débloque pas la sélection (le but est de repasser >0,70).
- *Analyst* : DANGER — une météo reportée à J+5 à plein poids peut maintenir une conviction sur du périmé, c'est le « confiant mais aveugle » que Thomas déteste (15/06). Il faut au moins la marquer et la dégrader en conviction.
- **Résolution** : la valeur reportée **compte à plein poids dans la COUVERTURE** (objectif : ne plus bencher un gagnant pour une panne) MAIS est **marquée `⚠️ reportée` + âge affiché** (échec visible, garde-fou fondateur), et **le drapeau force le libellé de conviction à au mieux « contestée »** tant qu'un critère reporté est dans le top driver. On débloque la sélection sans prétendre à une conviction franche sur du vieux.

**Désaccord n°2 — Fallback d'abord, ou règle de sélection haute-conviction d'abord ?**
- *Spéculateur* : la règle de sélection est ce qui aurait *réellement* sauvé le cacao (couverture vivante franche), le fallback ne couvre pas les sources durablement mortes (arrivées ports).
- *News Trader* : toute règle qui surclasse la couverture quant frôle l'override de signal → terrain miné (décision 20/06), à ne PAS précipiter.
- *Analyst* : le fallback est un correctif d'**intégrité de donnée** (réparer une panne ≈ bug d'affichage/justesse → corriger tout de suite, 18/06), pas un changement de SIGNAL → il peut partir maintenant. La règle de sélection EST un changement de SIGNAL → shadow obligatoire.
- **Résolution** : **fallback d'abord** (correctif data, zéro impact signal sur les critères lents, déployable). La **règle haute-conviction part en SHADOW en parallèle** (poids 0, mesurée, jamais active sans preuve) — elle traite le cas résiduel des sources mortes que le fallback ne peut pas reporter.

**Désaccord n°3 (mineur) — quel plafond d'âge unique ?**
- *Spéculateur* : un plafond simple ~5 j ouvrés pour tout (lisible).
- *Analyst* : non, plafond **par type** (météo 5j ≠ COT 8j ≠ FX 3j) car les demi-vies diffèrent d'un ordre de grandeur.
- **Résolution** : plafond **par type** (Analyst a raison sur le fond), valeur par défaut conservatrice 5 j ouvrés si type non spécifié.

---

## 5. VERDICT COMMUN

**La reco fallback « dernière valeur valide » est VALIDÉE, affinée comme suit :**

**Périmètre (INCLUS)** — critères lents/structurels uniquement :
- Météo (toutes fiches météo `zscore`/`zscore_abs`), taux/rendements, COT/positionnement, change FX structurel, spreads structurels lents.
- Mécanisme : persister la dernière valeur valide par clé de critère ; en cas d'échec **réseau/source** (`net_error`, 429, série vide), réutiliser si **fraîche** ; marquer **`⚠️ reportée` + âge** (échec VISIBLE) ; **jamais d'invention** (si aucune valeur persistée n'existe → reste n/a).

**Périmètre (EXCLUS)** — une valeur périmée y serait trompeuse :
- Prix, momentum 20j/7j, vol intraday, spreads de prix, tout critère intraday. (Cf. bug de mesure or 8h : une réf prix périmée cache des pertes.)

**Plafonds d'âge par TYPE** (jours ouvrés) :
- Météo / structurel offre 30j : **5 j**
- COT / positionnement : **8 j** (1 cycle COT hebdo + fériés)
- Taux / rendements : **3 j**
- Change FX : **3 j**
- Au-delà du plafond → la valeur reportée **expire** → critère redevient n/a (pas de zombie).

**Garde-fous sur la couverture/conviction** (résolution désaccord n°1) :
- Valeur reportée = **plein poids dans la couverture** (débloque la sélection).
- Drapeau `⚠️ reportée` **affiché** ; tant qu'un critère reporté est driver du top, **conviction plafonnée à « contestée »** (pas « forte »).

**Recos complémentaires :**
1. **Réparer la source « arrivées ports ivoiriens » (poids 9)** : le fallback ne peut RIEN reporter (jamais de valeur valide) → poids 9 mort en permanence sur le cacao. Chantier data séparé (cf. ticket #3 « critères absents à fort poids »). Si non réparable à court terme : repondérer/retirer plutôt que laisser un poids 9 zombie qui plafonne structurellement la couverture cacao. **À trancher par Thomas** (pas inventer une source).
2. **Règle de sélection « haute-conviction » → SHADOW à mesurer** (poids 0, jamais active sans preuve) : sélection autorisée si quant unanime + couverture **des critères VIVANTS** franche + news confirmées dans le même sens, même si la couverture *totale* est plombée par des sources mortes. C'est le seul mécanisme qui aurait *réellement* sauvé le cacao au-delà du plafond d'âge. Mesurer le delta win-rate Sélection avant toute activation (mindset 20/06 + 12/06).
3. **Ordre d'exécution** : (a) fallback maintenant (correctif data) ; (b) règle haute-conviction en shadow en parallèle ; (c) réparation source arrivées ports (chantier data).

**Ce qu'on NE fait PAS** : aucun override news dans la sélection (quant dominant, décision 20/06) ; aucune invention de valeur ; aucune valeur prix reportée ; aucun changement de SIGNAL sans shadow.

**Note de confiance : 9,3 / 10.**
Le fallback est sain, ciblé, à garde-fous visibles, zéro invention, et traite la cause racine prouvée (panne réseau). Le -0,7 : le cas le plus coûteux (source durablement morte = arrivées ports) n'est PAS résolu par le fallback seul → la vraie complétude passe par la règle haute-conviction (à mesurer) + réparation source. Tant que ces deux-là ne sont pas tranchés/mesurés, le risque « un gagnant benché par un trou structurel » subsiste partiellement.

---

### Handoff

- **@fullstack** : implémenter la persistance « dernière valeur valide » par clé de critère (périmètre INCLUS ci-dessus), plafonds d'âge par type, drapeau `⚠️ reportée` + âge propagé au rendu (page + bulletin), expiration au-delà du plafond → n/a. Réutiliser le pattern de `derniere_direction_valide` (L835) mais au niveau VALEUR de critère, pas direction. Tests : panne météo simulée → valeur reportée comptée, drapeau visible, conviction plafonnée ; valeur > plafond → n/a. **Mode shadow d'abord** sur l'effet couverture/sélection avant cutover.
- **@data-analyst** : spécifier l'instrumentation SHADOW de la règle « haute-conviction » (définition « couverture des critères vivants », seuil X, métrique = delta win-rate Sélection). Poids 0, jamais active.
- **Thomas** : trancher le sort du critère « arrivées ports » (réparer source / repondérer / retirer) — zéro invention, décision fondateur requise.
