# Spec technique — Phase 2 News : event_id, fraîcheur, nature, déduplication
**Analyst | 2026-06-01 | Périmètre : lot cœur**

---

## 0. Périmètre et hypothèses de départ

Ce document spécifie le **lot cœur** de la Phase 2 News. Il couvre :
- `event_id` : identifiant stable pour déduplication
- `event_date` : champ de fraîcheur de l'événement (distinct de la date d'ingestion)
- `nature` : classification sémantique par DeepSeek (champ nouveau)
- Gate de fraîcheur sur l'override du cap anti-inversion (high+confirmed)
- Reporting du signal « vs consensus »

**Ce que ce document ne change pas :**
- La formule de scoring pondéré (contribution = direction × materiality × reliability × poids × pertinence[h])
- Le cap anti-inversion α=0.8 et sa logique de déclenchement
- L'override high+confirmed existant (il est conservé, avec gate fraîcheur ajouté)
- Le cutoff lookback de `triggers_classifier.py` (lookback_days paramétrable, défaut 7j pour la synthèse, 14j max)
- Le decision-log en append-only JSONL
- Les niveaux de fiabilité RELIABILITIES = {confirmed, reported, rumor} et MATERIALITIES = {high, medium, low}

**Activation : shadow direct** (pas d'A/B). Les champs nouveaux sont loggués dès le premier run,
le gate fraîcheur s'active sur l'override uniquement — le scoring actuel est inchangé jusqu'à
validation explicite par Thomas.

**Maturité data projet : niveau 2** (events custom DeepSeek, decision-log structuré, pas encore
d'historique backtest suffisant pour tests statistiques → mesure qualitative par cohorte de runs).

## 1. event_id — identification stable et déduplication

### 1.1 Construction du hash

L'`event_id` est un **SHA-256 tronqué à 12 caractères** calculé sur une chaîne normalisée.

**Entrées du hash :**
```
normalized_title = normalise(trigger)  # voir règles ci-dessous
key_string = f"{normalized_title}|{actif_principal}"
event_id = sha256(key_string.encode("utf-8")).hexdigest()[:12]
```

**Règles de normalisation du titre (`normalise`) :**
1. Mise en minuscules (`casefold`)
2. Suppression des accents (NFD → ASCII, ex. "énergie" → "energie")
3. Suppression des ponctuations et caractères spéciaux sauf espaces (`re.sub(r"[^a-z0-9\s]", "", ...)`)
4. Collapse des espaces multiples (`re.sub(r"\s+", " ", ...).strip()`)
5. Suppression du préfixe de source éventuel (ex. `"reuters:"`, `"bbc:"`) si présent en tête
6. Troncature à **120 caractères** (évite les titres ultra-longs de diverger sur des suffixes non-sémantiques)

**Actif principal (`actif_principal`) :**
- Pour les events mono-actif : le ticker normalisé de la colonne `cours` (ex. `"BZ=F"`, `"CL=F"`, `"GC=F"`)
- Pour les events multi-actifs (plusieurs `impacts[]` DeepSeek) : l'actif de plus haute `confidence` (en cas d'égalité : ordre alphabétique TRADABLE_ASSETS pour déterminisme)
- Pour les events sans actif (`cours` vide, `impacts=[]`) : chaîne `"NONE"`

**Pourquoi ce choix plutôt que URL/GUID RSS :**
Les flux RSS de `bbc_world`, `cnbc_top`, `investing_news` ne garantissent pas de GUID stable.
Un même article peut être ingéré avec des GUIDs différents selon le fetch. Le titre normalisé + actif
est plus stable sur la durée. Limite connue : deux events sans rapport sur le même actif avec des
titres proches → §1.2.

### 1.2 Règle de quasi-doublons (titres proches)

**Définition du quasi-doublon :**
Deux events sont quasi-doublons si, après normalisation, leur **distance de Levenshtein normalisée** est ≤ 0.15 (soit ≤15 % de caractères différents) ET qu'ils partagent le même `actif_principal`.

**Fenêtre temporelle de comparaison :** 48 heures glissantes à partir de l'`event_date` du nouveau
event (pas de la date d'ingestion). Au-delà de 48h, un event similaire est considéré comme une
mise à jour ou une recurrence, pas un doublon.

**Implémentation pratique :**
La déduplication exacte (SHA-256) est sans coût. La déduplication floue (Levenshtein) est coûteuse
à pleine échelle. Règle de compromis : la déduplication floue s'applique uniquement sur le **sous-ensemble des events dont l'`actif_principal` est identique ET dont `event_date` est dans la fenêtre 48h**. En pratique, ce sous-ensemble est de 2 à 8 events par actif par fenêtre → coût négligeable.

**Bibliothèque recommandée :** `python-Levenshtein` (déjà dans l'écosystème PyPI standard) ou
`rapidfuzz.distance.Levenshtein.normalized_distance` (plus rapide). Si indisponible → fallback sur
la distance exacte uniquement (SHA-256 seul), à documenter dans le log.

### 1.3 Règle de conservation — lequel on garde

Lorsque deux events sont identifiés comme doublons (exact ou quasi) :

| Critère de tri | Priorité | Justification |
|---|---|---|
| `materiality` = "high" > "medium" > "low" | 1 (primaire) | Le plus matériel est le plus signal |
| `reliability` = "confirmed" > "reported" > "rumor" | 2 | La source la plus fiable prime |
| `event_date` le plus récent | 3 | En cas d'égalité de qualité, le plus frais |
| `source` classée (cnbc > bbc > investing) | 4 (tiebreak final) | Classement qualitatif des sources du pipeline |

**Règle opérationnelle :** l'event conservé est celui qui gagne sur le **premier critère discriminant**
dans l'ordre ci-dessus. L'event écarté est **loggué** dans le decision-log avec `dedup_status: "dropped"` et `dedup_kept_id: "<event_id_conservé>"` — il n'est jamais supprimé de l'events-log (append-only).

**Garde-fou dédup trop agressive :** si, sur une fenêtre de 24h, plus de 30 % des events d'un actif
sont marqués `dedup_status: "dropped"`, lever un warning dans les logs (`logger.warning`) et
**désactiver la dédup floue pour cet actif sur ce run** (conserver uniquement la dédup exacte SHA-256).
Ce seuil de 30 % signale une sur-collision — p.ex. une crise où tous les titres Pétrole commencent
par "Iran war" et sont faussement fusionnés.

### 1.4 Implémentation dans le pipeline

**Où :** dans `v3/scripts/agent_news.py`, lors de l'écriture dans `events-log.md`, avant l'append.

**Ordre des opérations :**
1. Calcul du `event_id` (SHA-256)
2. Lookup dans le cache en mémoire des events des 48h précédentes (chargé au démarrage depuis les N dernières lignes de `events-log.md`)
3. Si match exact : `dedup_status = "dropped"`, skip l'append, log
4. Si match flou (Levenshtein ≤ 0.15 sur même actif, fenêtre 48h) : appliquer la règle de conservation §1.3
5. Sinon : `dedup_status = "new"`, append normal

L'`event_id` est **calculé une seule fois** à l'ingestion et jamais recalculé (stable dans le temps).

## 2. Fraîcheur — event_date vs date d'ingestion

### 2.1 Le problème : archive re-publiée

Le pipeline ingère des flux RSS toutes les heures. Ces flux peuvent contenir des articles anciens
re-publiés (mise à jour éditoriale, syndication, SEO). Exemple observé dans events-log.md :
un event daté `2026-03-28` (Orange Juice) est apparu dans un batch du `2026-05-27`, soit **60 jours
après la date de l'événement**.

Si ce lag n'est pas détecté, l'event se retrouve dans la fenêtre `lookback_days` du classifieur
et injecte un signal basé sur une information vieille de 2 mois comme si elle était fraîche.
L'effet est particulièrement dangereux pour l'override high+confirmed (qui lève le cap α=0.8) :
une vieille news "high+confirmed" re-publiée aujourd'hui pourrait déclencher l'override.

**Distinction critique :**
- `ingestion_date` : date à laquelle le script a écrit la ligne dans events-log.md (= date du batch)
- `event_date` : date à laquelle l'événement s'est réellement produit (= date de la news originale)

Le `lookback_days` du classifieur (`cutoff = now - timedelta(days=lookback_days)`) doit porter
sur `event_date`, pas sur `ingestion_date`. C'est déjà partiellement le cas via la colonne `date`
de events-log.md — mais ce champ n'est pas toujours fiable (cf. §2.2).

### 2.2 Champ event_date : source et parsing défensif

**Source de l'`event_date` :** par ordre de priorité décroissante :

1. **Balise `<pubDate>` ou `<dc:date>` du flux RSS** (parsée par le collecteur lors du fetch). C'est
   la source la plus fiable — elle reflète la date de publication originale, pas de re-ingestion.
2. **Date extraite du titre ou du snippet** par DeepSeek (uniquement si la balise RSS est absente
   ou clairement incohérente — ex. date future ou antérieure à 2020).
3. **`ingestion_date` comme fallback de dernier recours** — marquée `event_date_source: "fallback_ingestion"`
   dans le log, ce qui déclenche un flag `event_date_uncertain: true`.

**Parsing défensif :**
```python
def parse_event_date(rss_pubdate: str | None, ingestion_date: datetime) -> tuple[datetime, str]:
    """
    Retourne (event_date, source) où source ∈ {"rss", "fallback_ingestion"}.
    Règles de rejet de la date RSS :
    - Date future (> now + 1h de tolérance timezone)
    - Date antérieure à 2020-01-01 (trop ancienne pour être une news tradable)
    - Parsing impossible (format inconnu)
    """
    if rss_pubdate:
        try:
            dt = parse_rss_date(rss_pubdate)  # à implémenter avec email.utils.parsedate_to_datetime
            if datetime(2020, 1, 1, tzinfo=timezone.utc) <= dt <= ingestion_date + timedelta(hours=1):
                return dt, "rss"
        except Exception:
            pass
    return ingestion_date, "fallback_ingestion"
```

**Cas d'une archive re-publiée :** si `event_date` < `ingestion_date` - 30 jours → l'event est
tagué `stale: true`. Un event `stale: true` est **exclu du cutoff de lookback** du classifieur
(il ne contribue jamais au score, même s'il est high+confirmed). Il reste dans events-log.md
pour l'historique mais est filtré à l'entrée de `_candidates_for`.

### 2.3 Cutoff de fraîcheur pour l'override high+confirmed

L'override actuel lève le cap α=0.8 quand un triplet est `materiality=high` ET `reliability=confirmed`.
La Phase 2 ajoute un **gate de fraîcheur** sur cet override :

**Règle exacte :**
```
L'override high+confirmed est autorisé SI ET SEULEMENT SI :
    event_date >= now - FRESHNESS_OVERRIDE_DAYS
    ET event_date_uncertain != true (i.e. date_source != "fallback_ingestion")
```

**Valeur `FRESHNESS_OVERRIDE_DAYS` = 3 jours.**

Justification : un événement géopolitique high+confirmed perd son caractère "surprise" après 3 jours
(le marché a absorbé l'information). Au-delà, le maintenir dans l'override revient à permettre une
archive de laisser passer le cap indéfiniment — exactement le bug décrit en §2.1.

Si le gate échoue (event trop vieux ou date incertaine) : l'event reste dans le scoring comme
événement normal (cap α=0.8 s'applique), il n'est pas exclu. Seul l'override est bloqué.

**Ce n'est PAS un decay continu.** C'est un cutoff binaire : avant 3j → override autorisé,
après 3j → cap normal. Pas de coefficient de décroissance, pas d'amortissement progressif.

### 2.4 Articulation avec la pertinence existante (zéro double-amortissement)

**Rappel de la mécanique actuelle (revue-plan-horizon-analyst.md §2) :**
```
contribution = direction × materiality × reliability × poids × pertinence[horizon]
```
La `pertinence[horizon]` est déjà un decay par horizon, calibré critère par critère dans les YAML.

**Ce que la Phase 2 N'AJOUTE PAS :**
- Aucun `decay_factor` global sur la famille news (rejeté dans la revue §3 pour double-amortissement)
- Aucun coefficient de décroissance sur `event_date` dans la contribution au score

**Ce que la Phase 2 ajoute sur la fraîcheur :**
- Un filtre binaire `stale: true` qui exclut les archives du candidat pool (filtre avant scoring)
- Un gate binaire sur l'override uniquement (pas sur le scoring normal)

**Pourquoi c'est sans doublon :**
- `pertinence[horizon]` agit sur TOUS les events dans la fenêtre lookback — c'est un poids de
  pertinence topique par horizon (ex. géopolitique Or à 24h = 0.5)
- Le gate fraîcheur agit uniquement sur la SÉLECTION des candidats (`stale`) et sur l'OVERRIDE.
  Il ne touche pas au calcul de contribution une fois l'event dans le pool.

Les deux mécanismes ont des espaces d'action disjoints. Pas de doublon.

## 3. Flag nature — classification DeepSeek

### 3.1 Champ `nature` : valeurs fermées

La `nature` est une dimension sémantique orthogonale à la `category` existante. Elle caractérise
le **type informationnel** de la news, pas son thème. Son rôle principal est de **filtrer les news
à faible signal tradable** (verbal, déjà_côté) avant qu'elles n'entrent dans le scoring.

**Valeurs fermées — NATURE_VALUES :**

| Valeur | Définition | Exemples |
|---|---|---|
| `"factual"` | Événement concret, mesurable, nouveau | Décision FOMC officielle, chiffre EIA publié, frappe militaire confirmée |
| `"verbal"` | Déclaration, interview, commentaire d'un responsable sans décision formelle | "Fed Governor Bowman warns...", "analyst says...", "Jim Cramer identifies..." |
| `"deja_cote"` | Information déjà connue du marché, re-publiée ou rappelée | Récapitulatif de semaine, "recall the Iran war impact...", article de contexte |
| `"rumeur"` | Information non confirmée, spéculative | "Sources say...", "reportedly considering..." — distinct de `reliability="rumor"` |
| `"non_tradable"` | Information sans impact financier direct | Lifestyle, sport, culture, opinion personnelle |

**Règle de mapping avec `category` et `reliability` existants :**
- `nature` est INDÉPENDANT de `category` (une news `geopolitical` peut être `"verbal"` si c'est
  une déclaration sans acte)
- `nature` est COMPLÉMENTAIRE à `reliability` : une news `reliability="confirmed"` peut être
  `nature="deja_cote"` (fait confirmé mais déjà absorbé). Ce cas est précisément celui qu'on veut
  détecter pour bloquer l'override.

### 3.2 Prompt DeepSeek — extension minimale

L'extracteur (`extractor.py`) produit déjà `category`, `subcat`, `trigger`, `reliability`,
`materiality`. La Phase 2 ajoute **un seul champ** dans le schéma : `nature`.

**Extension du SCHEMA dans SYSTEM_PROMPT :**
```json
{
  "category": "...",
  "subcat": "...",
  "trigger": "...",
  "news_zone": "...",
  "reliability": "...",
  "materiality": "...",
  "nature": "<factual | verbal | deja_cote | rumeur | non_tradable>",
  "impacts": [...]
}
```

**Extension des RÈGLES dans SYSTEM_PROMPT** (à ajouter après la règle 8 existante) :
```
9. nature :
   - "factual" : événement concret nouveau (décision officielle, chiffre publié, acte militaire)
   - "verbal" : déclaration, avertissement, interview sans décision formelle
   - "deja_cote" : information déjà connue, rappel d'un contexte existant, récapitulatif
   - "rumeur" : non confirmé, "selon des sources", spéculatif (peut coexister avec impacts définis)
   - "non_tradable" : aucun impact financier (sport, culture, opinion personnelle)
   Règle de priorité si doute : verbal > factual (préférer la prudence).
```

**Extension du few-shot (c) — rumeur M&A :** ajouter `"nature": "rumeur"` dans la réponse attendue.
Ajouter un **4e few-shot** dédié à `"deja_cote"` :
```
TITRE : Iran war cost: Average U.S. household paying $450 more on gas and energy
→ nature: "deja_cote"  (l'impact de la guerre Iran sur l'énergie est un contexte connu,
  pas une nouvelle information de prix)
```

**Impact sur les coûts DeepSeek :** l'ajout d'un champ JSON et d'une règle représente ~30 tokens
supplémentaires par requête (system prompt) + ~5 tokens par réponse. Sur 80 events/batch à 3 runs/jour
: ~21 000 tokens/jour supplémentaires. Au tarif deepseek-chat (~0,14 $/M tokens input), coût
additionnel ≈ **0,003 $/jour** — négligeable par rapport au soft cap de 0,50 $.

### 3.3 Règle d'utilisation dans la chaîne scoring

La `nature` n'entre **pas** dans la formule de contribution. Elle est un **filtre pré-scoring** :

**Règle exacte dans `triggers_classifier.py` (dans `_candidates_for` ou en amont) :**
```python
NATURE_EXCLUDED = {"deja_cote", "verbal", "non_tradable"}

def _is_scoring_eligible(ev: dict) -> bool:
    """Un event est éligible au scoring IA/keyword si sa nature n'est pas dans NATURE_EXCLUDED."""
    nature = (ev.get("nature") or "").strip().lower()
    if nature in NATURE_EXCLUDED:
        return False
    return True
```

**Ce filtre s'applique en entrée de `_candidates_for`** — avant toute logique IA/keyword.
Un event `verbal` ou `deja_cote` n'atteint jamais le scoring, même s'il est `high+confirmed`.

**Cas particulier `nature="rumeur"` :** les rumeurs NE sont PAS exclues automatiquement.
Elles entrent dans le scoring mais leur `reliability="rumor"` entraîne déjà un `facteur` réduit
dans le scoring pondéré. La nature `rumeur` est loggée pour l'audit shadow (§5) mais ne filtre pas.

**Gate fraîcheur + nature sur l'override :** la combinaison la plus dangereuse est
`materiality=high` + `reliability=confirmed` + `nature=deja_cote`. Le gate fraîcheur §2.3 couvre
déjà ce cas (event vieux → override bloqué). Pour les events récents `deja_cote` (re-publiés
dans les 3 derniers jours), le filtre `_is_scoring_eligible` les exclut — ils n'atteignent pas
l'override.

### 3.4 Fallback si nature absente ou ambiguë

**Nature absente** (DeepSeek ne retourne pas le champ, ou champ vide) :
- Fallback : `nature = "factual"` [HYPOTHÈSE conservatrice]
- Marquage : `nature_source = "fallback_default"` dans le decision-log
- Justification : un event sans classification de nature doit être traité comme potentiellement
  tradable. Ignorer un signal réel (faux négatif) est plus coûteux qu'inclure un bruit (faux positif
  atténué par `materiality` et `reliability`).

**Nature hors-bornes** (valeur non reconnue dans NATURE_VALUES) :
- Fallback identique : `nature = "factual"`, `nature_source = "fallback_invalid"`
- Logger en WARNING : `logger.warning("nature invalide reçue de DeepSeek : '%s'", raw_nature)`

**Nature ambiguë — DeepSeek retourne une valeur mais avec faible confiance** :
Le champ `nature` est un enum fermé — il n'y a pas de score de confiance attaché. Si la valeur est
dans NATURE_VALUES, elle est prise telle quelle. La "confiance" sur la nature dépend de la qualité
du prompt et des few-shots. Pas de mécanisme de confidence sur `nature` en Phase 2 (trop complexe,
coût LLM non justifié). Si on observe des taux de `verbal`/`deja_cote` anormalement hauts en shadow
(>60 % d'exclusions sur un actif), revoir le few-shot.

**Reporting du « vs consensus » :**
Le champ `nature` permet de taguer les events qui rapportent une surprise vs consensus :
`nature="factual"` + trigger contenant une divergence mesurée (ex. "Core PCE 3.3% vs 3.1% expected").
En Phase 2, ce reporting est purement qualitatif : le trigger est loggué dans le decision-log tel
quel. Une extraction structurée du delta consensus est hors périmètre lot cœur (nécessite un champ
supplémentaire et un few-shot dédié — Phase 3 potentielle).

## 4. Schéma de données

### 4.1 Colonnes ajoutées à events-log.md

**Schéma actuel (11 colonnes) :**
```
| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
```

**Schéma Phase 2 (16 colonnes — 5 ajouts) :**
```
| date | L1 | L2 | trigger | cours | latence | R | source | news_zone | category | pattern_id |
| event_id | event_date | nature | dedup_status | stale |
```

**Détail des 5 nouveaux champs :**

| Colonne | Type | Valeurs | Description |
|---|---|---|---|
| `event_id` | string(12) | hex SHA-256 | Identifiant stable normalisé titre+actif |
| `event_date` | ISO8601 date | `YYYY-MM-DD` ou `YYYY-MM-DDTHH:MM:SSZ` | Date réelle de l'événement (source RSS pubDate de préférence) |
| `nature` | enum | `factual\|verbal\|deja_cote\|rumeur\|non_tradable` | Classification DeepSeek ou fallback |
| `dedup_status` | enum | `new\|dropped` | `dropped` si dupliqué, `new` sinon |
| `stale` | boolean | `true\|false` | `true` si event_date < ingestion_date - 30j |

**Rétrocompatibilité :** les lignes existantes antérieures à la Phase 2 auront ces 5 colonnes vides.
Le parser doit traiter les valeurs vides comme `event_id=""`, `event_date=None`, `nature="factual"` (fallback),
`dedup_status="new"`, `stale=False`. Ce comportement doit être documenté dans le commentaire du parser.

**Lignes `dedup_status="dropped"` :** elles sont appendées dans events-log.md (append-only respecté)
mais **le parser les filtre en mémoire** avant de les passer à `_candidates_for`. Elles sont visibles
dans l'historique pour audit mais ne participent pas au scoring.

### 4.2 Champs ajoutés au decision-log (format JSONL)

**Champs actuels dans le decision-log** (lus dans `2026-06-01-1820.jsonl`) :
```json
{
  "bulletin_date", "generated_at", "fiche_key", "actif", "horizon",
  "score_pm1", "score_pond", "conclusion_pm1", "conclusion_pond", "diverge",
  "criteres": [{"cle", "nom", "type_norm", "valeur", "valeur_normalisee", "valeur_ponderee",
                "poids", "pertinence", "signe", "materiality", "reliability", "source_track",
                "facteur", "contrib_pm1", "contrib_pond"}],
  "news_total", "quant_total", "ratio_news", "news_dominant",
  "news_cap_applied", "news_cap_override"
}
```

**Champs Phase 2 ajoutés au niveau racine :**
```json
{
  "p2_events_considered": 12,
  "p2_events_excluded_stale": 1,
  "p2_events_excluded_nature": 3,
  "p2_events_excluded_dedup": 2,
  "p2_override_gate_blocked": false,
  "p2_override_gate_reason": null
}
```

**Champs Phase 2 ajoutés dans chaque élément `criteres[]` (pour les critères news) :**
```json
{
  "event_id": "a3f8bc2e1d90",
  "event_date": "2026-05-29T14:32:00Z",
  "nature": "factual",
  "event_date_source": "rss",
  "freshness_days": 3,
  "nature_source": "deepseek"
}
```

**Détail des champs racine :**

| Champ | Type | Description |
|---|---|---|
| `p2_events_considered` | int | Nombre d'events dans le pool avant filtres Phase 2 |
| `p2_events_excluded_stale` | int | Events exclus car `stale=true` |
| `p2_events_excluded_nature` | int | Events exclus car `nature ∈ NATURE_EXCLUDED` |
| `p2_events_excluded_dedup` | int | Events avec `dedup_status=dropped` (non recomptés) |
| `p2_override_gate_blocked` | bool | True si l'override high+confirmed a été bloqué par le gate fraîcheur |
| `p2_override_gate_reason` | string\|null | Raison du blocage : `"stale"`, `"date_uncertain"`, ou null |

### 4.3 Compatibilité append-only et parsing existant

**events-log.md :** fichier Markdown avec tableau pipe-delimited. L'ajout de colonnes est
rétrocompatible tant que le parser utilise les **noms de colonnes** (header) plutôt que les
**positions ordinales**. À vérifier dans `agent_news.py` — si le parser utilise `split("|")[4]`
au lieu de `row["event_id"]`, il faudra migrer vers un parsing par nom de colonne.

**decision-log JSONL :** format JSON, nouveaux champs ignorés par les lecteurs actuels
(JSON est extensible par nature). Les champs Phase 2 sont préfixés `p2_` pour éviter les
collisions avec de futurs champs sans préfixe. Les lecteurs qui ne connaissent pas `p2_*`
les ignorent silencieusement — aucune migration nécessaire.

**Invariant préservé :** append-only strict. Aucun edit de ligne existante. Aucune suppression.

## 5. Mesure en shadow — indicateurs d'audit sans A/B

Le trafic actuel du pipeline (3 runs/jour) ne permet pas de tests A/B statistiquement valides
(trop peu d'observations pour des intervalles de confiance exploitables sur un taux de réussite
binaire). La mesure se fait donc par **analyse de cohorte de runs** sur des indicateurs proxy
de qualité du signal.

### 5.1 Métriques à observer dans le decision-log

**Métriques Phase 2 à extraire par run ou par semaine :**

**M1 — Taux de filtrage par nature**
```
taux_filtre_nature[actif] = p2_events_excluded_nature / p2_events_considered
```
Valeur attendue : 20-40 % sur Pétrole et VIX (beaucoup de verbal géopolitique).
Si > 60 % → over-filtering, revoir le prompt nature.
Si < 10 % → under-filtering, revoir les few-shots.

**M2 — Taux de filtrage stale**
```
taux_stale = p2_events_excluded_stale / p2_events_considered (global)
```
Valeur attendue : 2-8 % (archives re-publiées sont rares mais existent).
Si > 20 % → anomalie dans le flux RSS (source en mode re-publication massive).

**M3 — Taux de déduplication**
```
taux_dedup[actif] = p2_events_excluded_dedup / (p2_events_considered + p2_events_excluded_dedup)
```
Valeur attendue : 5-15 % sur les actifs à forte couverture (Pétrole, Or).
Si > 30 % → seuil de sécurité déclenché (§1.3), revoir le threshold Levenshtein.

**M4 — Fréquence d'override gate bloqué**
```
taux_override_bloque = sum(p2_override_gate_blocked == true) / N_runs
```
Valeur attendue : 0-5 % (les vrais high+confirmed récents doivent passer).
Si > 20 % → le gate est trop restrictif (FRESHNESS_OVERRIDE_DAYS trop court).
Si 0 % sur >30 runs → normal si peu d'events high+confirmed, ou gate jamais déclenché (log à vérifier).

**M5 — Composition nature des events scoring-eligible par actif**
Distribution hebdomadaire : `{factual: X%, rumeur: Y%}` (verbal/deja_cote/non_tradable exclus).
Cible : factual > 50 % des events éligibles sur les actifs à news lourde (Pétrole, Or, VIX).

**M6 — Biais LONG/SHORT résiduel sur les actifs problématiques**
Comparer sur 30 runs :
- Avant Phase 2 : distribution conclusion_pond pour Pétrole, Or, VIX
- Après Phase 2 : même distribution
Si la Phase 2 réduit la dominance LONG sur Pétrole/Or → signal positif (le verbal géopolitique
LONG pro-guerre était sur-représenté).

**M7 — part news bornée [0,1] par actif après Phase 2** *(corrigé 10/06 — bornage)*
Définition (corrigée) : `M7 = |news_total| / (|news_total| + |quant_total| + ε)` = **part de la
magnitude directionnelle portée par les news**, bornée dans **[0,1]** (×100 = %, JAMAIS > 100%).
Doit baisser sur les actifs où les exclusions par nature sont élevées. C'est le meilleur proxy
d'amélioration disponible.
> **⚠️ Changement d'unité 10/06** : l'ancienne définition réutilisait le champ décisionnel
> `ratio_news = |news|/|quant|` (NON borné — observé jusqu'à 72.7 ≈ 7269% quand la couverture
> quant est faible, d'où les valeurs absurdes « 400-695% » signalées). La métrique d'OBSERVABILITÉ
> M7 est désormais une **part bornée** lisible en %. Le champ DÉCISIONNEL `ratio_news` (brut,
> comparé à `NEWS_DOMINANT_RATIO=0.5` par la gate régime news) est **inchangé** — aucun impact
> sur le scoring. Clé `p2_M7_ratio_news` conservée (continuité du decision-log), valeur bornée.
Objectif : `ratio_news < 0.5` sur >80 % des cellules (vs situation actuelle où Blé atteint 57).

### 5.2 Seuils d'alerte et interprétation

| Métrique | Seuil alerte | Action recommandée |
|---|---|---|
| `taux_filtre_nature > 60 %` sur un actif | WARNING log | Revoir few-shots, audit 20 events exclus manuellement |
| `taux_stale > 20 %` | WARNING log | Vérifier source RSS (bbc_business ?) — possible re-publication massive |
| `taux_dedup > 30 %` | WARNING log + désactiver dédup floue pour cet actif | Mode dégradé SHA-256 uniquement |
| `taux_override_bloque > 20 %` | INFO log | Augmenter FRESHNESS_OVERRIDE_DAYS à 5j et observer |
| `ratio_news > 2.0` après Phase 2 sur un actif | WARN | La Phase 2 n'a pas réduit la dominance — investiguer la nature des events restants |
| Zéro events éligibles sur un actif après filtres Phase 2 | WARNING | Pipeline en mode dégradé — `news_total = 0` par construction, signal quant seul |

### 5.3 Cadence de revue

- **J+3 après activation :** vérification manuelle des M1-M3 (taux de filtrage). Ajustement prompt si dérive.
- **J+10 (30 runs) :** revue M5, M6, M7. Décision de maintien, ajustement ou rollback du gate fraîcheur.
- **J+30 :** revue complète, décision d'activation des impacts scoring de la nature (Phase 3 éventuelle).

**Protocole de rollback :** si M7 (`ratio_news`) n'a pas bougé ou a augmenté après 30 runs,
le problème n'est pas la nature des news mais leur poids dans la fiche YAML (revoir §4 de
revue-plan-horizon-analyst.md). Dans ce cas : désactiver `_is_scoring_eligible` (revenir au
comportement actuel) sans impacter les champs de logging qui, eux, restent utiles.

## 6. Compat avec l'existant — checklist négative

Chaque point vérifie qu'une mécanique existante n'est pas cassée ou doublonnée.

| # | Mécanique existante | Impact Phase 2 | Verdict |
|---|---|---|---|
| C1 | `pertinence[horizon]` par critère YAML | Non touché. Le filtre nature agit en amont du candidat pool, pas sur le calcul de contribution. | OK — zéro doublon |
| C2 | Cap anti-inversion α=0.8 | Non touché. Le gate fraîcheur agit uniquement sur l'override, pas sur le cap lui-même. | OK |
| C3 | Override high+confirmed | Gate fraîcheur ajouté (FRESHNESS_OVERRIDE_DAYS=3j). L'override reste fonctionnel pour les events récents. | OK — extension conservative |
| C4 | Cutoff lookback (`cutoff = now - timedelta(days=lookback_days)`) | Non touché. Le filtre `stale` est appliqué AVANT l'entrée dans `_candidates_for`, donc avant le cutoff. Un event stale n'atteint pas le cutoff test. | OK |
| C5 | Synthèse directionnelle DeepSeek (`ia_synthese`) | Non touché. La synthèse porte sur les events après filtres Phase 2. Si tous les events d'un actif sont exclus par nature, la synthèse renvoie vide → le critère tombe à 0 par la logique existante (niveau 2 : prix tranchera). | OK |
| C6 | Conflit IA non tranché (`ia_conflict`) | Non touché. Le mécanisme de tranche par materiality_weight puis récence est inchangé. | OK |
| C7 | Fallback keyword | Non touché. Les events `verbal`/`deja_cote` exclus du scoring IA n'entrent pas non plus dans le fallback keyword (même filtre `_is_scoring_eligible` appliqué avant le branchement IA/keyword). | OK |
| C8 | Decision-log append-only JSONL | Nouveaux champs `p2_*` ajoutés. Format JSON extensible, aucun lecteur existant cassé. | OK |
| C9 | `ratio_news` dans le decision-log | Déjà présent et calculé. Inchangé. La Phase 2 ne modifie pas sa formule — mais en réduisant `news_total` via les filtres nature/stale, `ratio_news` baissera naturellement. C'est l'effet attendu. | OK |
| C10 | `source_track` sur les critères | Inchangé pour les flows existants (`ia_synthese`, `ia_synthese_faible`, `ia_conflict`, `keyword`, `calendrier`). Les events exclus par Phase 2 ne génèrent pas de `source_track` — ils ne sont pas dans le scoring. | OK |

## 7. Edge cases et garde-fous

**EC1 — News sans date fiable (event_date_source = "fallback_ingestion")**
- Le champ `event_date_uncertain = true` est loggué
- L'event est inclus dans le scoring (pour ne pas perdre de signal)
- L'override high+confirmed est **bloqué** (le gate fraîcheur exige date_source != fallback)
- Raison : une archive re-publiée dont on ne peut pas vérifier la date ne doit pas lever le cap
- Comptabilisé dans `p2_override_gate_reason: "date_uncertain"`

**EC2 — Nature absente de DeepSeek (champ manquant ou vide)**
- Fallback : `nature = "factual"`, `nature_source = "fallback_default"`
- L'event est inclus dans le scoring (comportement conservateur)
- Log WARNING pour suivi de fréquence : si > 10 % des events sans nature → bug prompt

**EC3 — Dédup trop agressive (faux positifs Levenshtein)**
Scénario : crise intense sur un actif où tous les titres commencent par le même contexte
(ex. "Iran war:" en préfixe, tous les titres Oil sont à distance ≤15 %)
- Garde-fou §1.3 : si taux_dedup > 30 % sur un actif en 24h → désactiver la dédup floue
  pour cet actif sur ce run (SHA-256 uniquement)
- En mode dégradé, un WARNING est loggué avec `dedup_mode: "exact_only"` dans le decision-log

**EC4 — Event high+confirmed récent mais de nature "deja_cote"**
Scénario : un recap officiel de la Fed (confirmed, high materiality) qui résume un meeting
déjà connu. C'est high+confirmed MAIS deja_cote.
- Le filtre `_is_scoring_eligible` exclut l'event du scoring (deja_cote ∈ NATURE_EXCLUDED)
- L'event n'atteint pas l'override
- C'est le comportement voulu : le marché a déjà pricé l'information

**EC5 — Zéro events éligibles après filtres Phase 2 sur un actif entier**
Scénario : tous les events d'un actif sur la fenêtre lookback sont verbal/deja_cote/stale.
- `p2_events_considered > 0`, `p2_events_excluded_nature + p2_events_excluded_stale = p2_events_considered`
- Comportement du critère news : renvoie 0 (pas de signal)
- `news_total = 0`, score quant tranche seul
- Ce comportement est correct et transparent — il sera visible via `ratio_news = 0`
- Un WARNING est loggué : `"Zéro events éligibles Phase 2 pour actif X — scoring news désactivé ce run"`

**EC6 — event_date dans le futur (ex. annonce pré-publiée avec date de conférence)**
- Si event_date > ingestion_date + 1h : rejeté par le parsing défensif §2.2
- Fallback sur ingestion_date, marqué `event_date_source: "fallback_ingestion"`
- Logique : une date future est soit une erreur, soit une annonce forward — dans les deux cas,
  la fraîcheur de l'information est indéterminée

**EC7 — Collision SHA-256 sur event_id tronqué à 12 caractères**
Probabilité de collision sur 12 hex = 1/16^12 ≈ 10^-14. Sur 10 000 events/mois, probabilité
de collision sur le mois ≈ 10^-6. Négligeable en pratique. Si collision détectée (deux events
différents avec même event_id et actif différent), les deux sont conservés (`dedup_status: "new"`
car actif_principal diffère). L'event_id est un identifiant de déduplication, pas un UUID global.

**EC8 — Ingestion sans API DeepSeek (mode passif)**
Le mode passif (`DEEPSEEK_API_KEY` vide) produit des events sans `nature` ni `event_date` structurés.
Dans ce mode, les filtres Phase 2 s'appliquent avec le fallback : `nature = "factual"` (aucun
event exclu par nature), `event_date` = `ingestion_date` (gate fraîcheur inactif — tous les events
récents passent). La Phase 2 est transparente en mode passif : elle n'exclut rien, elle log
uniquement les métriques M1-M4 à 0.

## 8. Résumé des règles exactes (référence implémentation)

### Constantes

```python
# event_id
EVENT_ID_LENGTH = 12                     # hex chars (SHA-256 tronqué)
EVENT_ID_TITLE_MAX_CHARS = 120           # normalisation titre
LEVENSHTEIN_THRESHOLD = 0.15             # distance normalisée max pour quasi-doublon
DEDUP_TIME_WINDOW_H = 48                 # fenêtre dédup floue en heures
DEDUP_MAX_RATIO = 0.30                   # seuil sécurité dédup agressive → mode exact-only

# Fraîcheur
STALE_THRESHOLD_DAYS = 30               # event_date < ingestion_date - 30j → stale
FRESHNESS_OVERRIDE_DAYS = 3             # gate override high+confirmed
EVENT_DATE_MIN = datetime(2020, 1, 1)   # date minimale acceptable pour RSS pubDate

# Nature
NATURE_VALUES = {"factual", "verbal", "deja_cote", "rumeur", "non_tradable"}
NATURE_EXCLUDED = {"deja_cote", "verbal", "non_tradable"}  # exclus du scoring
NATURE_FALLBACK = "factual"             # si absent/invalide
```

### Flux d'ingestion (agent_news.py)

```
Pour chaque event RSS :
  1. parse_event_date(rss_pubdate, ingestion_date) → (event_date, date_source)
  2. stale = (event_date < ingestion_date - 30j)
  3. event_id = sha256(normalise(trigger) + "|" + actif_principal)[:12]
  4. dedup_check(event_id, event_date) → dedup_status ∈ {"new", "dropped"}
  5. [DeepSeek si actif] → nature (avec fallback)
  6. append events-log.md (toujours, même si dropped ou stale)
```

### Flux scoring (triggers_classifier.py — _candidates_for)

```
Pour chaque event candidat :
  1. Si dedup_status == "dropped" → EXCLURE
  2. Si stale == true → EXCLURE (comptabiliser dans p2_events_excluded_stale)
  3. Si nature ∈ NATURE_EXCLUDED → EXCLURE (comptabiliser dans p2_events_excluded_nature)
  4. Appliquer cutoff lookback existant (event_date >= now - lookback_days)
  5. → event eligible pour scoring IA/keyword
```

### Gate override high+confirmed

```
Override autorisé SI :
  materiality == "high"
  ET reliability == "confirmed"
  ET event_date >= now - FRESHNESS_OVERRIDE_DAYS (3 jours)
  ET event_date_source != "fallback_ingestion"
Sinon : cap α=0.8 normal (pas d'override)
```

### Decision-log Phase 2 (champs racine supplémentaires)

```json
{
  "p2_events_considered": <int>,
  "p2_events_excluded_stale": <int>,
  "p2_events_excluded_nature": <int>,
  "p2_events_excluded_dedup": <int>,
  "p2_override_gate_blocked": <bool>,
  "p2_override_gate_reason": <"stale"|"date_uncertain"|null>
}
```

### PROMPT_VERSION à bumper

Bumper `PROMPT_VERSION` de `"v2.1"` à `"v2.2"` dans `extractor.py` lors de l'ajout du champ `nature`
au schéma. Ce bump permet de distinguer les events classifiés avec l'ancien schéma (sans nature)
des events classifiés avec le nouveau (avec nature) — utile pour l'audit shadow (les events
pré-Phase-2 sans nature reçoivent le fallback `"factual"` et ne sont pas exclus rétroactivement).

---

*Spec produite par @data-analyst — 2026-06-01. Implémenter via @fullstack après validation Thomas.*
*Révision requise si FRESHNESS_OVERRIDE_DAYS ou LEVENSHTEIN_THRESHOLD sont ajustés après 30 cycles shadow.*
