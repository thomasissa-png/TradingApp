# Spec Phase 2 News — UNIFIÉE (synthèse des 2 experts)

> Fil rouge : **justesse de l'orientation de tendance ET des changements de tendance**.
> Périmètre validé Thomas : lot cœur · nature classée par DeepSeek · activation directe en shadow.
> Réconcilie `spec-phase2-news-newstrader.md` (desk) + `spec-phase2-news-analyst.md` (méthode).

## 0. Le but, en une phrase
Distinguer une **news fraîche + structurelle** (qui crée/confirme une tendance → on suit) d'une **news déjà-cotée / verbale / re-publiée** (bruit → on écarte) — pour **moins de faux changements de tendance** et **mieux capter les vrais**.

## 1. POINT À TRANCHER — la taxonomie `nature`
Les 2 experts proposent des axes différents :
- **News Trader** (axe *persistance*) : `structurel / ponctuel / deja_cote / verbal`
- **Analyst** (axe *fiabilité/tradabilité*) : `factual / verbal / deja_cote / rumeur / non_tradable`

**Ma recommandation (alignée sur le but tendance)** : adopter l'axe **persistance** du News Trader comme `nature`, car c'est lui qui dit si un mouvement va **TENIR** (structurel → suivre la tendance) ou **RETOMBER** (ponctuel → ne pas courir après). L'axe fiabilité de l'Analyst (`rumeur/factual`) est **déjà couvert** par le champ `reliability` existant (confirmed/reported/rumor) → ne pas le dupliquer. `non_tradable` ≈ `deja_cote/verbal`.

→ **`nature` ∈ {structurel, ponctuel, deja_cote, verbal}** + on garde `reliability` tel quel.

## 2. Impact de la nature (coef × pertinence, PAS de decay global)
Coefficient par horizon qui **module la `pertinence`** déjà en place (validé : pas de double-amortissement) :

| nature | 24h | 7j | 1m | Effet tendance |
|---|---|---|---|---|
| `structurel` | 0.8 | 1.0 | 1.0 | porte la tendance, tient à 1m |
| `ponctuel` | 1.0 | 0.5 | 0.15 | choc court, s'amortit |
| `deja_cote` | ~0 | ~0 | ~0 | compte-rendu → écarté du scoring |
| `verbal` | 0.3 | 0.2 | 0.1 | rumeur/déclaration → plafonné bas |

## 3. Fraîcheur (2 seuils binaires, aucun decay continu)
- `event_date` parsé depuis `pubDate` RSS ; fallback = date d'ingestion (marqué `event_date_source=fallback`).
- **🔑 PREMIER-VU FAIT FOI (anti-repost, règle Thomas)** : si un même `event_id` (match exact OU flou) a déjà été enregistré un jour précédent, la fraîcheur se calcule sur la **date la PLUS ANCIENNE jamais vue** (`canonical_event_date = MIN(event_date)` sur TOUT l'historique events-log, pas seulement la fenêtre 48h). Une news reçue en retard / re-publiée **ne peut PAS passer pour fraîche** ni déclencher un faux changement de tendance. C'est la priorité absolue : on se base toujours sur la première occurrence.
- **STALE = 30j** : `canonical_event_date` plus vieux → exclu du pool (l'archive 2025 re-publiée ne pollue pas).
- **Gate override = 72h** : la news ne peut **renverser** le quant (= déclencher un **changement de tendance**) que si : `canonical_event_date` ≤72h ET nature ∈ {structurel, ponctuel} ET materiality=high ET reliability≠rumor. Sinon, pas d'inversion. *(C'est LE point qui sert la détection de changement de tendance — et le « premier-vu » empêche un repost de le déclencher à tort.)*

## 4. event_id + déduplication
- `event_id` = SHA-256/12 de `normalise(trigger)+"|"+actif`.
- Dédup exacte (event_id) sur **tout l'historique** + dédup floue (Levenshtein normalisée ≤0.15) sur fenêtre 48h/actif.
- **Conservation de la LIGNE** : on garde la meilleure occurrence (materiality > reliability > source) MAIS on **stampe toujours `canonical_event_date` = la date la PLUS ANCIENNE** des occurrences (cf. §3 premier-vu fait foi). Ne JAMAIS prendre la date la plus récente pour la fraîcheur.
- Les reposts détectés → `dedup_status="repost"`, exclus du scoring courant (déjà comptés la 1re fois), mais appendés (traçabilité).
- Garde-fou anti-sur-dédup : si >30% droppés/actif/24h → mode dégradé (SHA exact seul).

## 5. Schéma (append-only, par nom de colonne)
- events-log : +`event_id`, `event_date`, `nature`, `dedup_status`, `stale` (les dropped/stale restent appendés, filtrés en mémoire).
- decision-log : +`event_id`, `event_date`, `nature`, `event_date_source`, `freshness_days` par critère news ; métriques `p2_*` au niveau racine.
- DeepSeek : +1 champ `nature` au prompt, PROMPT_VERSION v2.1→v2.2, fallback `ponctuel` si absent (conservateur).

## 6. Mesure en shadow (activation directe) — angle TENDANCE
7 métriques (M1 filtrage nature, M2 stale, M3 dédup, M4 gate bloqué, M5 composition nature, M6 biais LONG/SHORT, M7 ratio_news) + **2 métriques tendance ajoutées** :
- **T1 — faux flips évités** : nb de flips de cellule qui auraient eu lieu SANS Phase 2 mais sont écartés (portés par deja_cote/verbal).
- **T2 — vrais flips qualifiés** : nb de flips portés par structurel+frais+high (changements de tendance « propres »), à croiser avec la mesure VRAI/FAUX.
Cadence : J+3, J+10, J+30. Rollback si M7/biais ne bougent pas.

## 7. Zéro doublon avec l'existant (checklist)
pertinence · cap α=0.8 · override · cutoff lookback · synthèse IA · conflit IA · fallback keyword · decision-log append-only · ratio_news · source_track → **tous inchangés**, Phase 2 s'ajoute en amont (filtre nature/stale AVANT le cutoff) et raffine l'override.

## 8. Critère de validation (les 3 experts devront cocher)
**« Phase 2 réduit-elle les faux changements de tendance et améliore-t-elle les vrais ? »** — jugé sur T1/T2 + la section Flips (remontée en haut) croisée avec VRAI/FAUX.
