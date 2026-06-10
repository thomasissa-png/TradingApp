# Diagnostic — couverture news « actifs sourds » (Argent / S&P / VIX)

> Lot E de l'audit Cowork 10/06. **Diagnostic d'abord**, fix ciblé ensuite.
> Méthode : comptages réels sur `v3/data/events-log.md` (4198 lignes data) +
> `v3/data/source-health.md` (cycle 2026-06-10 05:16 UTC) + lecture du code.
> Gel scoring respecté (aucun poids/seuil/normalisation/`weighting.yml` touché).

## TL;DR — la cause racine est UNE seule, et elle est structurelle

**`MAX_EXTRACTIONS_PER_CYCLE = 80` (`agent_news.py:50`) tronque la file `filtered`
en FIFO (`filtered[:80]`, ligne 104), AVANT que les flux dédiés des actifs sourds
ne soient atteints.** L'ordre de collecte place ces flux loin derrière la limite :
le 80e item tombe dans `oilprice` (10e source), alors que `gnews_silver_industrial`,
`gnews_vix`, `gnews_nasdaq` sont aux **positions 819, 624, 529** de la file.
Résultat : ils sont collectés, passent les filtres (santé ✅), mais **ne sont jamais
extraits ni écrits** dans events-log. Ce n'est ni un flux manquant, ni un flux
défaillant, ni un filtre trop strict, ni la dédup : c'est un **plafond de débit mal
réparti**.

## Preuves chiffrées

### 1. Les flux dédiés sont SAINS mais ABSENTS des écritures

`source-health.md` (dernier cycle, 2026-06-10) — les flux « sourds » fonctionnent :

| Flux | HTTP | Reçus | Gardés (post-filtre) |
|---|---|---:|---:|
| gnews_silver_industrial | 200 | 100 | **99** |
| gnews_vix | 200 | 100 | **97** |
| gnews_nasdaq | 200 | 100 | **95** |
| gnews_gold_cb | 200 | 100 | 97 |
| gnews_ecb_policy | 200 | 100 | 98 |
| gnews_copper | 200 | 71 | 71 |
| gnews_cac40 | 200 | 72 | 72 |
| gnews_wheat | 200 | 65 | 62 |

Pourtant, comptage des LIGNES réellement écrites dans events-log par source :

| Flux gnews_* déclaré | Lignes dans events-log |
|---|---:|
| gnews_coffee | 792 |
| gnews_cocoa | 195 |
| gnews_wheat | **0** |
| gnews_copper | **0** (`first=None`) |
| gnews_cac40 | **0** |
| gnews_nasdaq | **0** |
| gnews_vix | **0** |
| gnews_ecb_policy | **0** |
| gnews_silver_industrial | **0** |
| gnews_gold_cb | **0** |

→ **8 flux dédiés sur 10 n'ont JAMAIS écrit une ligne.** Le `Gardés` non-nul prouve
qu'ils passent dédup + blacklist + whitelist finance. Le delta entre « gardés » et
« écrits » = le plafond d'extraction.

### 2. Le 80e item tombe avant les flux gnews (simulation sur les `Gardés` du cycle)

Ordre de collecte = `RSS_FEEDS` → `EARLY_SIGNAL_FEEDS` (où vivent les gnews dédiés,
en QUEUE) → structured (gnews/newsapi). `collect_all` préserve l'ordre de `raw`
dans `filtered` (list-comp sur `deduped`, ligne 760), puis `agent_news` fait
`filtered[:80]`. Positions cumulées (1212 gardés/cycle) :

```
   1-71   bbc/cnbc/investing/eia ...
  72-83   oilprice            <-- MAX 80 tombe ICI (10e source)
 ...
 529-623  gnews_nasdaq        ← jamais atteint
 624-720  gnews_vix           ← jamais atteint
 819-917  gnews_silver_industrial ← jamais atteint
```

**Tout ce qui est ≥ position 81 est jeté à chaque cycle** (« le reste reviendra au
prochain cron », `agent_news.py:102`) — mais au cron suivant le même flot arrive,
est dédupliqué/re-tronqué à l'identique : les flux de queue ne remontent jamais.

### 3. Pourquoi Café/Brent dominent (784/773) et pas les autres

- **Café** : 792 lignes, dont **1016 lignes events-log sont pré-2026-04** (≈ ces
  archives viennent quasi toutes de `gnews_coffee`). Google News RSS sur la query
  café renvoie beaucoup d'articles à `pubDate` ancien → volume historique gonflé,
  accumulé AVANT que le volume total ne sature MAX=80. Café/cacao ont « pris leur
  place » dans la file quand elle était moins chargée.
- **Brent / Or / S&P (via impacts)** : ces actifs sont mentionnés par les sources
  de TÊTE de file (cnbc, bbc, eia, oilprice, fed) qui passent SOUS le seuil de 80 →
  ils captent des impacts. C'est pourquoi, via `impacts[]`, **SP500=659 et VIX=304**
  (head-of-feed), mais via le champ `cours` (1er actif) **SP500=328, VIX=3** — l'écart
  S&P 31 / VIX 3 du brief = comptage sur `cours`, biaisé par le multi-impact.

| Actif | Mentions via `impacts[]` | Mentions via `cours` (1er actif) |
|---|---:|---:|
| BRENT | 758 | 654 |
| COFFEE | 677 | 667 |
| SP500 | 659 | 328 |
| GOLD | 636 | 152 |
| NASDAQ | 482 | 194 |
| VIX | 304 | 3 |
| SILVER | **11** | **9** |
| WHEAT | 14 | 10 |
| COCOA | 229 | 204 |

→ **Argent (SILVER) est le seul vraiment sourd dans les DEUX comptages** (11/9) :
il n'a quasi aucune source de tête qui en parle (les desks macro ne titrent pas
sur l'argent), ET son flux dédié `gnews_silver_industrial` (99 gardés/cycle) est
intégralement jeté par MAX=80. VIX et S&P sont « faux sourds » : 304 et 659 via
impacts — le brief les a comptés sur `cours`.

## Causes racines par actif

| Actif | Cause racine | Preuve |
|---|---|---|
| **Argent** | (1) Aucune source de tête ne titre l'argent + (2) son flux dédié `gnews_silver_industrial` (99 gardés/cycle) est jeté à 100% par MAX=80 (position 819 ≫ 80). | impacts=11, cours=9 ; flux ✅ 99 gardés, 0 ligne écrite. |
| **VIX** | « Faux sourd » au comptage `cours` (3). Réellement 304 mentions via `impacts[]` (capté par les sources de tête : géopol/macro). Son flux dédié `gnews_vix` (97 gardés) est néanmoins jeté par MAX=80 → potentiel inexploité. | impacts=304 vs cours=3 ; gnews_vix ✅ 97 gardés, 0 ligne. |
| **S&P** | « Faux sourd » : 659 via `impacts[]`, 328 via `cours`. Le 31 du brief = comptage `cours` sur un actif souvent en impact secondaire (multi-impact géopol/macro). Pas un trou. | impacts=659, cours=328. |

**Verdict** : 1 cause racine commune et dominante = **plafond d'extraction FIFO
mal réparti (MAX=80)**. Aucune query trop étroite (les flux reçoivent 65-100 items),
aucun filtre whitelist/blacklist trop strict (gardés ≈ reçus), aucune sur-dédup
(pas de garde-fou `>30%` déclenché), aucun flux non câblé (tous appelés, ✅ au
monitor). Le filtre de fraîcheur (STALE_DAYS=30) joue son rôle côté scoring mais
n'explique pas les écritures manquantes.

## Sous-constat — trou de fraîcheur (réel, mais SECONDAIRE)

1016 lignes events-log sont **pré-2026-04** (jusqu'à 2022), quasi toutes
`gnews_coffee`. Google News RSS renvoie des articles à `pubDate` ancien sur les
queries larges. Ces lignes sont **déjà écartées du SCORING** par `STALE_DAYS=30`
(canonical_event_date > 30j → `stale=True` → exclu dans `_candidates_for`,
`triggers_classifier.py:1149`). Mais elles **polluent events-log** (4198 lignes
dont 24% de bruit historique) et gonflent le compteur Café. Ce n'est pas la cause
de la surdité Argent/VIX/S&P. **Recommandation** : filtrer la fraîcheur à
l'INGESTION (ne pas écrire les articles dont `published` > N jours), pour ne pas
accumuler d'archive. Ce filtre est VOULU côté scoring (STALE_DAYS=30) ; on le
RENFORCE à l'écriture pour ne plus polluer le log.

## Contrainte coût (NE PAS monter le cap)

- Coût mesuré : **~$0.0003 / extraction** (constant sur le ledger : 0.297-0.299 $/1000).
- Extraire TOUT (1228 gardés × 3 cycles = 3684 calls/j) ≈ **$1.10/j → dépasse le HARD
  CAP $0.80**. Donc on NE peut PAS tout extraire, et on NE monte PAS le cap.
- Aujourd'hui : ~92 calls/j (1 cycle productif à 80). Énorme marge sous le soft cap
  ($0.50) AVANT le plafond.

## Fix retenu (cf. §ÉTAPE 2 du handoff)

1. **Round-robin équitable** des flux dans `filtered` AVANT troncature : au lieu du
   FIFO (qui sert les 10 premières sources et affame les 23 autres), on prend en
   quote-part par source → chaque flux dédié obtient sa part du budget MAX.
2. **Relever MAX modérément** (80 → 240/cycle), dimensionné pour rester SOUS le soft
   cap : 240 × 3 cycles = 720 calls/j × $0.0003 ≈ **$0.22/j** (< soft cap $0.50, ≪
   hard cap $0.80). Le cap coût n'est PAS touché — c'est le débit qui est reréparti.
3. **Filtre de fraîcheur à l'ingestion** : ne pas écrire les articles `published`
   au-delà de `INGEST_MAX_AGE_DAYS` (défaut 30, aligné sur STALE_DAYS) → fin de la
   pollution archive Café. Documenté, désactivable par env.

Aucun nouveau flux ajouté : le diagnostic prouve que les flux EXISTENT et SONT SAINS.
Ajouter un flux n'aurait rien changé (il aurait fini en queue, jeté par MAX=80).
