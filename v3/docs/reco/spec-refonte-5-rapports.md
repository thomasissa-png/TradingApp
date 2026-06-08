# Spec — Refonte 5 rapports/jour + mesure ouverture→clôture

> **Source de vérité unique** pour @fullstack et @infrastructure.
> Statut : VALIDÉ Thomas (design validé en amont — la spec traduit fidèlement sans réinventer).
> Date : 2026-06-08. Branche : `claude/elegant-ramanujan-OIKms`.

---

## Sommaire

1. [Vue d'ensemble — schéma des 5 rapports](#1-vue-densemble--schéma-des-5-rapports)
2. [Modèle de mesure détaillé — ouverture→clôture](#2-modèle-de-mesure-détaillé--ouverturerarr-clôture)
3. [Contenu exact de chaque rapport (12h / 18h / 22h / dimanche)](#3-contenu-exact-de-chaque-rapport)
4. [Le Manager — bilan semaine dimanche 18h](#4-le-manager--bilan-semaine-dimanche-18h)
5. [Infra / cron — créneaux, exception dimanche, table de vérité garde](#5-infra--cron)
6. [Impact mesure — passage à 1 décision/jour](#6-impact-mesure)
7. [Critères d'acceptation par bloc](#7-critères-dacceptation-par-bloc)
8. [Ordre de construction — dépendances](#8-ordre-de-construction--dépendances)
9. [Risques et questions ouvertes](#9-risques-et-questions-ouvertes)

---

## 1. Vue d'ensemble — schéma des 5 rapports

### Rôle de chaque rapport

| # | Rapport | Heure (Paris) | Jours | Noté win rate ? | Rôle principal |
|---|---|---|---|---|---|
| R1 | **Briefing 7h** | 07h00 | Jours de bourse | **OUI — seul noté** | Décision du jour : LONG/SHORT 12 actifs × 3 horizons. Bulletin complet actuel. |
| R2 | **Suivi 12h** | 12h00 | Jours de bourse | Non | Statut des positions du matin vs ouverture marché. News à impact depuis 7h. Suggestions de sortie. |
| R3 | **Suivi 18h** | 18h00 | Jours de bourse | Non | Idem R2, avec prix de mi-séance US et clôture EU. |
| R4 | **Bilan du jour 22h** | 22h00 | Jours de bourse | Note les calls J | Bilan VRAI/FAUX des calls du matin (sens clôture−ouverture vs call), win rate du jour, news déterminantes. |
| R5 | **Bilan semaine** | 18h00 | Dimanche seulement | Récapitule la semaine | Win rate hebdo, cellules/critères faibles, propositions d'ajustement (Manager). Thomas valide. |

### Invariants transversaux

- **Un seul bulletin de décision par jour** : le Briefing 7h (R1). C'est lui qui alimente le Journaliste pour le win rate. Les suivis (R2/R3) et bilans (R4/R5) ne génèrent PAS de nouvelles cellules LONG/SHORT mesurables.
- **WIN RATE ONLY** partout. Aucune métrique monétaire (P&L, amplitude, gain), aucun montant, aucun ratio de rendement. Jamais.
- **Zéro modification silencieuse** de poids/seuils/scoring. Le Manager PROPOSE, Thomas VALIDE, avant toute application.
- **Mode shadow** : tout reste en shadow (rien émis publiquement) jusqu'à validation Thomas post-30 jours réels.

---

## 2. Modèle de mesure détaillé — ouverture→clôture

### 2.1 Principe fondateur (le vrai changement vs l'existant)

**Aujourd'hui (existant)** : le prix d'émission est stampé au moment du run (7h/12h/18h, marchés souvent encore fermés ou en pré-ouverture). Le Journaliste compare « prix au moment du bulletin » → « prix N jours plus tard ». Problème signalé par Thomas : le prix à 7h n'est PAS l'ouverture réelle de marché — il est souvent celui de la nuit (marchés fermés) ou de la pré-ouverture, ce qui fausse le calcul gain/perte.

**Après refonte** : le **prix de référence = l'ouverture propre de chaque marché**, stampée à l'heure d'ouverture réelle (voir table §2.2). Chaque actif a une fenêtre d'ouverture définie. Le Journaliste attend que chaque marché soit ouvert avant de stamper son prix de référence du jour.

### 2.2 Table des heures d'ouverture et clôture par actif (heure Paris / CEST été)

| Groupe | Actifs couverts | Ouverture Paris | Clôture Paris | Référence J | Clôture J |
|---|---|---|---|---|---|
| **EU Actions** | CAC 40 (Euronext, proxy FCHI/ETF) | **09h00** | **17h30** | Prix à 09h00 (ouverture Euronext) | Prix à 17h30 |
| **US Actions** | S&P 500, Nasdaq, VIX (proxy SPY/QQQ/VIXY) | **15h30** | **22h00** | Prix à 15h30 (ouverture NYSE/Nasdaq) | Prix à 22h00 |
| **Continus** | EUR/USD, Or, Argent, Cuivre, Pétrole/Brent, Blé, Cacao, Café | **08h00** | **22h00** | Prix à 08h00 (référence conventionnelle, pas d'ouverture nette) | Prix à 22h00 |

> **Note heure d'hiver (CET)** : les crons UTC restent fixes. En heure d'hiver (CET = UTC+1), l'ouverture Euronext est à 09h00 CET = 08h00 UTC, NYSE à 15h30 CET = 14h30 UTC, etc. Le stamping doit utiliser l'heure réelle Paris (TZ Europe/Paris), pas l'heure UTC fixe du cron.

### 2.3 Définitions précises

**Ouverture (prix de référence J)** : prix récupéré via Twelve Data le jour J, pour chaque actif, à l'heure d'ouverture de son marché (voir table §2.2). Ce prix est stampé une fois par jour de bourse (idempotent). Stocké dans un nouveau fichier `v3/data/prix-ouverture/{YYYY-MM-DD}.json` distinct des prix d'émission bulletin.

**Clôture (prix de fin de journée)** : prix récupéré à 22h00 Paris, après fermeture des marchés US. Pour le CAC 40, la clôture propre est à 17h30 (avant 22h — on utilise le close officiel 17h30).

**Distinction prix d'émission bulletin vs prix d'ouverture** :
- `prix-emission/{bulletin_id}.json` : inchangé, stamp au moment du run bulletin (existant, conservé pour les horizons 7j/1m).
- `prix-ouverture/{YYYY-MM-DD}.json` : NOUVEAU, stamp à l'ouverture de chaque marché (1 par jour de bourse). C'est la référence du modèle de mesure 24h.

### 2.4 Règles de mesure par horizon

#### Horizon 24h (le vrai changement)

```
outcome_24h = signe(prix_clôture_J - prix_ouverture_J) vs call_7h
```

- **prix_ouverture_J** : lu depuis `prix-ouverture/{YYYY-MM-DD}.json` (stampé à l'ouverture du marché)
- **prix_clôture_J** : récupéré à 22h, run R4 (Bilan du jour)
- **Note au run 22h** : c'est le run R4 (Bilan du jour) qui ferme et note les cellules 24h. La journée boursière EST le 24h (la nuit, marchés fermés → inutile d'attendre le lendemain).
- Seuil de réussite : inchangé (SEUIL_PCT par actif dans les fiches, voir §2.6)

#### Horizon 7 jours

```
référence = prix_ouverture du jour de décision (J0)
mesure    = prix_ouverture J+7 (prochain jour de bourse ≥ J0+7)
outcome   = signe(prix_ouverture_J7 - prix_ouverture_J0) vs call_7h
```

- Stockage : `prix-ouverture/{YYYY-MM-DD}.json` pour les deux extrêmes
- Noté au run Journaliste normal (7h ou 12h), quand l'échéance est atteinte

#### Horizon 1 mois

```
référence = prix_ouverture J0
mesure    = prix_ouverture J+30 (prochain jour de bourse ≥ J0+30)
outcome   = signe(prix_ouverture_J30 - prix_ouverture_J0) vs call_7h
```

### 2.5 Stamping du prix d'ouverture — logique exacte

**Nouveau module (ou extension de journaliste.py)** : `stamp_prix_ouverture(date_j)`.

Comportement :
1. Pour chaque actif (fiche YAML), identifier le groupe (EU/US/Continu) → heure d'ouverture.
2. Vérifier que l'heure courante Paris ≥ heure d'ouverture du groupe + OPEN_STAMP_DELAY_MIN (défaut : 5 min — laisser le marché s'équilibrer).
3. Appeler `fetch_twelve_price(ticker)` → prix spot.
4. Écrire dans `v3/data/prix-ouverture/{YYYY-MM-DD}.json` (clé par date — 1 fichier/jour).
5. Idempotent par actif : un actif déjà stampé pour ce jour n'est pas refetché (entry-lock, même logique que prix d'émission).
6. Si Twelve Data indisponible → log WARNING + ticker absent du JSON → Journaliste marquera `suivi-interrompu` (zéro invention).

**Qui l'appelle ?**
- Le run R2 (12h) stampe les actifs EU dont l'ouverture est à 09h → déjà ouverts depuis 3h.
- Le run R2 (12h) stampe aussi les actifs Continus (ouverts depuis 08h).
- Le run R3 (18h) stampe les actifs US (ouverts depuis 15h30) ET complète les tickers manquants des groupes précédents.
- Idempotence garantit qu'un re-run ne réécrase pas.

> **[QUESTION OUVERTE Q1]** : faut-il un créneau dédié 09h05 pour stamper l'ouverture EU immédiatement (avant le suivi 12h), ou le stamping dans le run 12h suffit-il ? Décision Thomas requise avant implémentation. Hypothèse courante : stamping dans le run 12h suffit (3h après ouverture EU, prix stable).

### 2.6 Gestion des cas tordus

| Cas | Comportement attendu |
|---|---|
| Ouverture indisponible (Twelve KO) | ticker absent du JSON ouverture → Journaliste : `suivi-interrompu`. Retry au prochain run. Zéro invention. |
| Gap d'ouverture (gap up/down brutal) | Aucun traitement spécial. On stampe le premier prix disponible après l'heure d'ouverture + délai. Le gap fait partie de la réalité du marché. |
| Férié partiel d'un seul marché (ex: 4 juillet : US fermé, EU ouvert) | Le groupe US n'est pas stampé ce jour. Les actifs US ont `suivi-interrompu` pour le jour férié. Le groupe EU est stampé normalement. La garde `is_trading_day` s'applique globalement → si l'un des deux est fermé, le run normal a quand même lieu (la garde teste la bourse au sens large). [QUESTION OUVERTE Q2 — voir §9] |
| Prix manquant au run 22h (Twelve KO en clôture) | Le Bilan du jour signale `clôture indisponible` pour les actifs concernés. Les cellules 24h de ces actifs restent `suivi-interrompu`. Retry au prochain run 7h. |
| Double bulletin dans le même créneau (anti-doublon) | Garde existante conservée (anti-doublon ×3 schedule). Le prix d'ouverture ne dépend pas du nombre de bulletins. |
| Actif avec ouverture décalée (VIX via VIXY — ETF suit NYSE) | Traité comme US : ouverture 15h30 Paris. |

### 2.7 Ce qui RESTE inchangé vs ce qui CHANGE

| Élément | Statut | Note |
|---|---|---|
| `stamp_prix_emission(bulletin_id)` | **Conservé** | Toujours appelé au run bulletin (7h). Sert aux horizons 7j/1m comme RÉFÉRENCE (comportement inchangé pour ces horizons jusqu'à décision contraire). |
| `compute_echeance(bulletin_date, horizon)` | **Conservé** | Aucun changement. |
| `select_non_overlapping(measures, horizon)` | **Conservé** | Aucun changement. |
| `compute_kpi(measures)` | **Conservé** | Aucun changement de formule. |
| `is_trading_day(d)` | **Conservé** | Source de vérité calendaire unique. |
| Prix de référence 24h | **CHANGE** | Était prix d'émission bulletin → devient prix d'ouverture du marché. |
| Fichier de stockage | **CHANGE** | Nouveau `prix-ouverture/{YYYY-MM-DD}.json` pour la référence 24h. |
| Qui note les 24h | **CHANGE** | Était le run Journaliste J+1 matin → devient le run R4 (Bilan 22h) le jour même. |
| Horizons 7j/1m | **À décider** | Peuvent rester sur `prix-emission` (référence actuelle) ou migrer vers `prix-ouverture`. Design validé Thomas mentionne `prix_ouverture_J0` pour 7j/1m → la spec suit cette intention. [Voir Q3 §9] |

---

## 3. Contenu exact de chaque rapport

### 3.1 R1 — Briefing 7h (inchangé dans sa structure)

**Ce rapport est le bulletin complet actuel.** La refonte ne modifie PAS le Briefing 7h. Il reste :
- Matrice 12 actifs × 3 horizons (LONG/SHORT + scores)
- Synthèse directionnelle top 3
- Bloc news (drapeaux, régimes)
- Bloc suffisance et gates
- Bloc source_monitor

**Seul changement lié à la refonte** : le stamp du `prix-ouverture` du jour est déclenché par ce run pour les actifs Continus (ouverts à 08h). Cela s'ajoute au stamp `prix-emission` existant. Aucun changement de format du bulletin.

**Ce qui est noté pour le win rate** : seul R1 alimente les cellules LONG/SHORT mesurées par le Journaliste. R2/R3/R4/R5 ne génèrent PAS de nouvelles cellules.

### 3.2 R2 — Suivi 12h (NOUVEAU)

**Objectif** : rapport COURT. Thomas lit en 2 minutes, pas en 10.

**Format imposé** :

```
## Suivi 12h — {date} {heure}

### Positions du matin vs ouverture

| Actif | Call 7h | Ouverture | Prix 12h | Delta% | Statut | Suggestion |
|---|---|---|---|---|---|---|
| Or      | LONG    | 3 420.0   | 3 435.2  | +0.44% | ✅ gagne | Hold |
| CAC 40  | SHORT   | 8 120.0   | 8 134.5  | +0.18% | ⚠️ perd  | Surveiller |
| ...     | ...     | ...       | ...      | ...    | ...     | ...        |

### News à impact depuis 7h (si applicable)
[2-3 news max ayant réellement bougé un actif. Si aucune news significative : « Pas de news impactante depuis 7h. »]

- **{Actif}** : {événement court} → {conséquence directionnelle en 1 ligne}

### Suggestions de sortie
[Uniquement les actifs en statut ⚠️ perd avec une suggestion motivée. Si tout va dans le sens du call : « Aucune alerte. »]
```

**Règles strictes pour R2** :
- Le tableau ne contient que les actifs dont le call 7h est actionnable (exclus : INSUFFISANT, non-noté).
- `Ouverture` = prix depuis `prix-ouverture/{date}.json` (stampé avant ou pendant ce run).
- `Prix 12h` = prix spot Twelve Data au moment du run 12h (NON stampé en tant que prix d'émission).
- `Delta%` = `(Prix 12h − Ouverture) / Ouverture × 100`. Signe du delta vs sens du call → Statut.
- **Statut** : `✅ gagne` si signe(delta) == sens(call), `⚠️ perd` sinon, `— neutre` si |delta| < 0.1%.
- **Suggestion** : valeurs fermées : `Hold` / `Surveiller` / `Sortir` (sortie suggérée si perte > seuil actif × 0.5 — [voir Q4 §9]).
- Pas de score pondéré, pas de critères détaillés. Ce n'est PAS un nouveau bulletin.
- Pas de note win rate. Ce rapport n'alimente PAS le Journaliste.

### 3.3 R3 — Suivi 18h (NOUVEAU)

**Identique à R2 dans sa structure.** Différences :
- Heure = 18h (marchés EU fermés, US en cours depuis 15h30).
- `Prix 18h` = prix spot au run 18h.
- `Delta%` toujours vs l'ouverture (même référence — pas vs le prix de 12h).
- Les actifs EU ont leur clôture officielle (17h30) → `Prix 18h` = close EU (17h30) pour les actifs EU.
- Les actifs US sont encore ouverts → `Prix 18h` = prix mid-séance US.
- Format identique, contenu mis à jour.

> **[QUESTION OUVERTE Q5]** : pour les actifs EU (clôture 17h30), utiliser le close officiel 17h30 ou le dernier prix disponible au run 18h (≈ 17h55 UTC, soit 17h55 Paris — marché déjà fermé) ? Les deux options donnent le même résultat si Twelve Data retourne le close. À valider comportement Twelve Data pour FCHI/ETF après 17h30.

### 3.4 R4 — Bilan du jour 22h (NOUVEAU)

**Objectif** : noter les calls du jour et produire le win rate quotidien.

**Format imposé** :

```
## Bilan du jour — {date}

### Résultat des calls 7h

| Actif | Call 7h | Ouverture | Clôture (22h) | Delta% | Résultat |
|---|---|---|---|---|---|
| Or      | LONG    | 3 420.0  | 3 451.3       | +0.92% | ✅ VRAI   |
| CAC 40  | SHORT   | 8 120.0  | 8 089.5       | −0.37% | ✅ VRAI   |
| Nasdaq  | LONG    | 19 500.0 | 19 483.0      | −0.09% | ⚪ NC      |
| ...     | ...     | ...      | ...           | ...    | ...       |

### Win rate du jour
- Paris conclusifs : X / Y (Z non-conclusifs sous seuil)
- Win rate du jour : **X/X = N%**
- Win rate cumulé : voir performance.md

### News qui ont compté aujourd'hui
[3-5 news ayant eu un impact réel sur les prix. Uniquement si identifiables.]

- **{Actif}** : {news} → {impact constaté}
```

**Règles strictes pour R4** :
- `Clôture (22h)` = prix spot Twelve Data au run 22h, pour chaque actif.
- Pour le CAC 40 : clôture = close officiel Euronext 17h30 (pas le prix à 22h, marché fermé).
- `Résultat` : calculé par le Journaliste avec `prix_ouverture` comme référence (pas `prix_emission`). Seuil par actif (fiches).
- **Cellules non-conclusives (NC)** : delta < seuil → ⚪. Non comptées dans le win rate du jour.
- Win rate du jour = VRAI / (VRAI + FAUSSE) — non-conclusives exclues. Même règle que la mesure globale.
- Ce rapport écrit les outcomes dans `measures-log.jsonl` (run Journaliste appelé dans le step 22h). Les outcomes sont définitifs pour l'horizon 24h.
- **Pas de re-notation le lendemain** pour les cellules 24h notées à 22h (déjà définitives).
- Les news « qui ont compté » : sélection éditoriale du Journaliste/DeepSeek (non automatisée — [voir Q6 §9]).

### 3.5 R5 — Bilan semaine dimanche 18h (NOUVEAU)

Détaillé en section 4 (Le Manager).

---

## 4. Le Manager — bilan semaine dimanche 18h

### 4.1 Rôle

Le Manager est la partie **apprentissage/pilotage** du système. Il n'émet pas de décision de trading. Il lit les résultats de la semaine et propose des ajustements de configuration que Thomas doit valider avant toute application.

**Principe cardinal** : le Manager PROPOSE. Thomas valide. JAMAIS de modification silencieuse.

### 4.2 Métriques lues par le Manager

| Métrique | Source | Description |
|---|---|---|
| Win rate par cellule (actif × horizon) | `performance.md` | Taux VRAI/(VRAI+FAUSSE) non-chevauchant, fenêtre 30 |
| Win rate hebdo | `win-rate-{AAAA-Sxx}.md` (archive) | Nouveaux paris de la semaine + cumul |
| N_eff par cellule | `performance.md` | Nombre de paris indépendants (warm-up si < 15) |
| Critères n/a fréquents | `decision-log/*.jsonl` | Critères souvent absents (source morte ou faible coverage) |
| Contributions par critère | `decision-log/*.jsonl` | Part de |contribution| par critère sur la semaine |
| Cellules quasi-neutres (≈) | `decision-log/*.jsonl` | Cellules avec |score| < NEUTRAL_BAND — faible conviction |
| Cellules is_carry | `decision-log/*.jsonl` | Cellules maintenues par hystérèse (source partiellement morte) |
| Détecteurs actifs (◧/⇆/↯) | `decision-log/*.jsonl` | Drapeaux mono-critère, contradiction, coin-flip |

### 4.3 Définition d'une « cellule faible »

Une cellule (actif × horizon) est faible si l'une des conditions suivantes est vraie :

1. **Win rate < 50%** sur N_eff ≥ 5 paris (statistiquement défavorable, même si non significatif)
2. **Dominée par un seul critère** (◧ drapeau mono-critère actif sur ≥ 50% des runs de la semaine)
3. **Score quasi-neutre persistant** (|score| < NEUTRAL_BAND sur ≥ 3 runs consécutifs)
4. **Critère principal souvent n/a** (critère de poids ≥ 8 absent sur ≥ 60% des runs de la semaine)

### 4.4 Définition d'un « critère faible »

Un critère est faible si :
1. **Souvent n/a** : absent sur ≥ 40% des runs sur 2 semaines (problème de source ou de couverture)
2. **Contribution inverse** : sa contribution moyenne est opposée à l'outcome final de la cellule sur la semaine (critère qui tire dans le mauvais sens)
3. **Variance excessive** : critère qui flippe de signe entre deux runs consécutifs sans event significatif (instabilité de source)

### 4.5 Format des propositions d'ajustement

Chaque proposition suit ce format strict dans le bilan dimanche :

```
### Proposition P{N} — {titre court}

**Type** : Ajustement de poids / Désactivation critère / Changement de seuil / Note d'observation
**Actif(s) concerné(s)** : {liste}
**Critère(s) concerné(s)** : {nom exact dans la fiche YAML}
**Constat** : {fait observé — chiffré si possible, ex. "win rate 33% sur 3 paris, critère TIPS absent 4/5 runs"}
**Proposition** : {modification précise, ex. "Réduire poids `taux_reel_us` de 12 à 8 pour Or 7j"}
**Risque** : {ce qui peut mal tourner si on applique}
**Validation requise** : Thomas OUI/NON avant toute modification de config YAML

[ ] Thomas valide — appliquer au prochain run
[ ] Thomas refuse — garder en observation
[ ] Thomas demande plus de données — reporter à S+{N}
```

**Ce que le Manager ne fait PAS** :
- Il n'applique jamais une modification lui-même.
- Il ne propose pas de retirer une source de données (c'est un chantier données, pas un ajustement de poids).
- Il ne propose pas de changement de logique de scoring (c'est un chantier dev, pas un ajustement de config).
- Il ne commente pas le P&L, les gains ou pertes monétaires.

### 4.6 Format complet du bilan dimanche 18h

```
## Bilan semaine — {AAAA-Sxx} ({lundi} → {vendredi})

### Win rate de la semaine
[Tableau issu de win-rate-{AAAA-Sxx}.md — pris tel quel, sans retraitement]

### Cellules à surveiller
| Actif | Horizon | Raison | Win rate | N_eff |
|---|---|---|---|---|
| {actif} | {H} | {raison courte} | {taux%} | {N} |

### Critères sous-performants
| Critère | Actif(s) | Problème observé | Fréquence |
|---|---|---|---|
| {critère} | {actifs} | {ex: souvent n/a} | {X/5 runs} |

### Propositions d'ajustement (à valider Thomas)
{0 à N propositions, format §4.5}

### Observations sans proposition
{Faits observés qui ne justifient pas encore une proposition (warm-up, N_eff trop faible). Garder en mémoire pour S+1.}
```

---

## 5. Infra / cron

### 5.1 Créneaux actuels et nouveaux

| Créneau | Heure Paris | Jours | Statut | Rapport produit |
|---|---|---|---|---|
| `5h` UTC (05:12/27/42) | 07h00 CEST | Jours de bourse | **Existant** | R1 Briefing 7h |
| `10h` UTC (10:12/27/42) | 12h00 CEST | Jours de bourse | **Existant → R2** | R2 Suivi 12h |
| `16h` UTC (16:12/27/42) | 18h00 CEST | Jours de bourse | **Existant → R3** | R3 Suivi 18h |
| `20h` UTC (20:12/27/42) | 22h00 CEST | Jours de bourse | **NOUVEAU** | R4 Bilan du jour |
| Dimanche `16h` UTC | 18h00 CEST | **Dimanche** seulement | **NOUVEAU** | R5 Bilan semaine |

> Heure d'hiver (CET = UTC+1) : 5h UTC = 6h CET, 10h UTC = 11h CET, 16h UTC = 17h CET, 20h UTC = 21h CET. À documenter dans le cron YAML.

### 5.2 Exception dimanche — bilan semaine

Le bilan dimanche est une **exception délibérée à la garde jours-de-bourse**. Les marchés sont fermés le dimanche mais ce rapport est un bilan de performance, pas un bulletin sur prix live.

**Règle** : le créneau dimanche 18h (`16h UTC dimanche`) BYPASS la garde `is_trading_day` et s'exécute UNIQUEMENT si `datetime.weekday() == 6` (dimanche). Il ne produit PAS de bulletin de décision, ne stamp pas de prix d'émission, ne génère pas de cellules LONG/SHORT.

**Mise en oeuvre dans cycle.yml** : ajouter un `schedule` séparé `"0 16 * * 0"` (dimanche 16h UTC) avec un paramètre d'identification `report_type: weekly_summary`, et un step dédié qui bypass la garde `is_trading_day` spécifiquement pour ce créneau.

**Alternative** : job séparé `weekly-summary` dans le même workflow. [Voir Q7 §9]

### 5.3 Table de vérité de la garde — mise à jour complète

| Déclencheur | Jour | Force | Report type | → Run ? | Raison |
|---|---|---|---|---|---|
| schedule (7/12/18h) | Lun-Ven ouvré | — | bulletin | OUI* | Jour de bourse (*anti-doublon ×3) |
| schedule (7/12/18h) | Sam/Dim | — | bulletin | NON | Week-end |
| schedule (7/12/18h) | Jour férié | — | bulletin | NON | Marché fermé |
| dispatch VPS | Lun-Ven ouvré | false | bulletin | OUI | Driver réel |
| dispatch VPS | Sam/Dim | false | bulletin | NON | Week-end |
| dispatch VPS | Jour férié | false | bulletin | NON | Marché fermé |
| dispatch (force=true) | N'importe | true | bulletin | OUI | Bypass humain |
| push RUN-CYCLE.txt | N'importe | — | bulletin | OUI | Bypass humain |
| schedule dim 16h UTC | **Dimanche** | — | **weekly_summary** | **OUI** | Exception bilan — pas de prix live |
| schedule dim 16h UTC | Lun-Sam | — | weekly_summary | NON | Sécurité : ne s'exécute que le dimanche |
| dispatch (force 22h) | Jour férié | true | bilan_jour | OUI | Bypass humain |

### 5.4 VPS Anya — mise à jour du trigger

Le fichier `v3/ops/vps-trigger/trigger-cycle.sh` doit être mis à jour pour ajouter :
- Le créneau **22h Paris** (jours de bourse) : cron `0 20 * * 1-5` (UTC) avec garde `is_trading_day` côté VPS.
- Le créneau **dimanche 18h** : cron `0 16 * * 0` (UTC) — pas de garde is_trading_day (le dimanche est intentionnel).

**Redondance** : le créneau 22h suit la même logique ×3 schedule côté GitHub Actions. Le VPS envoie 1 tir/créneau (workflow_dispatch). Anti-doublon conservé.

### 5.5 Nouveaux scripts nécessaires

| Script | Description | Appelé par |
|---|---|---|
| `run_suivi.py` | Produit R2/R3 (suivi intra-journée). Lit `prix-ouverture`, fetch prix courant, génère le rapport markdown court. | Step cycle 12h et 18h |
| `run_bilan_jour.py` | Produit R4 (bilan 22h). Fetch clôture, appelle Journaliste pour noter les 24h, génère le rapport. | Step cycle 22h |
| `run_bilan_semaine.py` | Produit R5 (bilan dimanche). Lit performance.md + decision-log + archive hebdo. Génère le rapport Manager. | Step cycle dimanche 18h |
| Extension `journaliste.py` | Nouvelle fonction `stamp_prix_ouverture(date_j)` + logique de mesure 24h sur prix-ouverture. | Appelé par run_suivi.py et run_bilan_jour.py |

---

## 6. Impact mesure — passage à 1 décision/jour

### 6.1 Problème actuel

Avec 3 runs/jour (7h/12h/18h), **3 bulletins** sont générés, chacun avec ses propres cellules LONG/SHORT. Le Journaliste mesure les 3. Résultat : **1 jour de bourse = 3 mesures potentielles par cellule**. Sur une fenêtre de 30 conclusions, cela représente ~10 jours réels seulement, pas 30. Audit Journaliste 08/06 : N_brut trompeur ×3 vs N_eff = 6 indépendants.

### 6.2 Solution : 1 décision/jour = le Briefing 7h

**Après refonte** :
- **Seul R1 (Briefing 7h) génère des cellules mesurées** pour le win rate.
- R2/R3 ne créent pas de nouvelles cellules. Ils lisent les cellules de R1 et rapportent leur évolution intra-journée.
- R4 (Bilan 22h) **note** les cellules de R1 du jour (en tant que Journaliste, pour l'horizon 24h).
- R5 consolide les notes de la semaine.

**Conséquence directe** :
- N_eff par cellule 24h : 1 par jour de bourse (≈ 5/semaine). Pour atteindre 15 paris : 3 semaines. Identique à l'actuel N_eff (qui était déjà non-chevauchant).
- **N_brut ne gonfle plus ×3** : N_brut 24h ≈ N_eff (1 bulletin/jour).
- Cohérence : la métrique « Paris (réels) » dans performance.md correspond à de vrais jours de trading distincts.

### 6.3 Compatibilité backward

Les bulletins 12h et 18h existants (déjà dans `v3/data/bulletins/`) ont des cellules stampées. Deux options :
- **Option A** : continuer à les mesurer via l'ancien Journaliste jusqu'à ce qu'ils expirent naturellement (horizon 7j/1m). Propre mais complexe à gérer.
- **Option B** : ne mesurer que les bulletins de la série 7h à compter de la mise en prod. Les anciens bulletins 12h/18h sont mesurés comme avant jusqu'à expiration.

[QUESTION OUVERTE Q8 — voir §9] Décision Thomas requise.

### 6.4 Référence ouverture vs émission pour 7j/1m

Avec `prix-ouverture` disponible, les horizons 7j/1m peuvent aussi migrer vers la référence ouverture plutôt que le prix d'émission bulletin (potentiellement à 7h, marché fermé). Cela rendrait la comparaison cohérente (ouverture J0 → ouverture J+7 ou J+30).

[QUESTION OUVERTE Q3 — voir §9] Décision Thomas requise.

---

## 7. Critères d'acceptation par bloc

### CA-MESURE (Bloc 2 — modèle de mesure)

- [ ] **CA-M1** : `stamp_prix_ouverture(date_j)` crée `v3/data/prix-ouverture/{YYYY-MM-DD}.json`. Contenu : dict `{ticker: float}`. Idempotent : re-run ne réécrase pas un ticker déjà présent.
- [ ] **CA-M2** : Pour chaque actif, le prix d'ouverture est récupéré après l'heure d'ouverture du groupe (EU : 09h05 Paris minimum, US : 15h35, Continu : 08h05). Un prix récupéré avant ce délai lève une exception et est rejeté.
- [ ] **CA-M3** : Si Twelve Data indisponible pour un ticker, le ticker est ABSENT du JSON (pas de valeur null, pas de valeur inventée). Le Journaliste doit traiter l'absence comme `suivi-interrompu`.
- [ ] **CA-M4** : Le calcul 24h utilise `prix-ouverture/{date_bulletin}.json` comme référence (pas `prix-emission`). Vérifiable en inspectant `measures-log.jsonl` : champ `prix_emission` contient la valeur d'ouverture, pas le prix à 7h.
- [ ] **CA-M5** : Les horizons 7j/1m utilisent la référence décidée par Thomas (prix-ouverture ou prix-emission) — à implémenter selon réponse Q3.
- [ ] **CA-M6** : `N_brut` dans performance.md correspond à 1 par jour de bourse (pas 3). Test : générer 3 bulletins le même jour → N_brut = 1 (seul R1 mesuré).

### CA-R2R3 (Bloc 3 — Suivis 12h/18h)

- [ ] **CA-S1** : Le rapport suivi contient exactement le tableau des actifs actionnables (exclusion INSUFFISANT/non-noté). Le tableau comporte les colonnes : `Actif | Call 7h | Ouverture | Prix {H}h | Delta% | Statut | Suggestion`.
- [ ] **CA-S2** : `Ouverture` = valeur de `prix-ouverture/{date}.json`. Si le JSON est absent ou le ticker manquant, la colonne affiche `—` (pas de valeur inventée).
- [ ] **CA-S3** : `Delta%` = `(Prix_courant - Ouverture) / Ouverture × 100`. Calculé avec 2 décimales.
- [ ] **CA-S4** : `Statut` : `✅ gagne` si `signe(Delta%) == sens(Call)`, `⚠️ perd` sinon, `— neutre` si `|Delta%| < 0.1%`.
- [ ] **CA-S5** : Le rapport suivi ne contient PAS de matrice LONG/SHORT (pas de nouvelles décisions). Longueur maximale : 50 lignes markdown.
- [ ] **CA-S6** : Le rapport suivi n'alimente PAS `measures-log.jsonl` ni `performance.md`.

### CA-R4 (Bloc 3 — Bilan 22h)

- [ ] **CA-B1** : Le Bilan 22h appelle le Journaliste avec `prix-ouverture/{date}.json` comme référence. Les outcomes 24h écrits dans `measures-log.jsonl` ont `prix_emission` = valeur d'ouverture réelle.
- [ ] **CA-B2** : Pour le CAC 40, la clôture utilisée est le close officiel 17h30 (pas le prix à 22h UTC). Test : le delta CAC dans le rapport = `(close_17h30 - ouverture_09h00) / ouverture_09h00 × 100`.
- [ ] **CA-B3** : Les cellules 24h notées à 22h ont `outcome` définitif (`VRAI` / `FAUSSE` / `non-conclusive`). Elles ne sont PAS re-notées au run 7h du lendemain.
- [ ] **CA-B4** : Le win rate du jour dans le rapport = `N_VRAI / (N_VRAI + N_FAUSSE)`, non-conclusives exclues. Formule identique à la formule globale.
- [ ] **CA-B5** : Le rapport bilan ne contient PAS de mention monétaire (gain en €, multiplicateur, P&L). Test de parsing : aucun symbole `€`, `$`, `gain`, `perte`, `rendement`.

### CA-R5 / Manager (Bloc 4 — Bilan semaine)

- [ ] **CA-W1** : Le bilan dimanche est produit uniquement le dimanche (guard `weekday() == 6`). Un run manuel hors dimanche avec `report_type=weekly_summary` est ignoré (sauf `force=true`).
- [ ] **CA-W2** : Le tableau win-rate hebdo du bilan provient directement de `win-rate-{AAAA-Sxx}.md` (archive existante). Aucun recalcul custom.
- [ ] **CA-W3** : Les propositions d'ajustement (P{N}) ont toutes les champs obligatoires : Type, Actif(s), Critère(s), Constat, Proposition, Risque, Validation requise. Un champ vide = proposition rejetée par le système (validation CI).
- [ ] **CA-W4** : Le bilan ne modifie AUCUN fichier de configuration YAML. Vérification post-run : `git diff v3/config/` = vide.
- [ ] **CA-W5** : Le bilan ne contient PAS de métrique monétaire.

### CA-INFRA (Bloc 5 — cron)

- [ ] **CA-I1** : Le créneau 22h (jours de bourse) déclenche R4 et UNIQUEMENT R4. Il ne re-lance pas le bulletin 7h ni le scoring complet.
- [ ] **CA-I2** : Le créneau dimanche 18h déclenche R5 et UNIQUEMENT R5. La garde `is_trading_day` est bypassée (dimanche est intentionnel). Le créneau dimanche NE s'exécute PAS les lundis-samedis.
- [ ] **CA-I3** : La mise à jour du VPS Anya inclut les 2 nouveaux créneaux dans `/etc/cron.d/tradingapp`. Validation : `crontab -l` affiche les entrées 22h jours bourse + 18h dimanche.
- [ ] **CA-I4** : L'anti-doublon ×3 schedule s'applique au créneau 22h (même logique que 7h/12h/18h). Test : 3 triggers schedule dans la même heure → 1 seul run réel.

---

## 8. Ordre de construction — dépendances

### Phase 1 — Mesure ouverture→clôture + Bilan 22h (R4)

**Prérequis** : aucun autre rapport ne peut être finalisé sans le prix d'ouverture comme référence.

Tâches (en dépendance stricte) :

```
T1.1 — Extension journaliste.py :
       - Fonction stamp_prix_ouverture(date_j, fiches, fetch_price, base_dir)
       - Constante OPEN_STAMP_DELAY_MIN = 5 (délai post-ouverture)
       - Table MARKET_OPEN_HOURS par groupe d'actifs
       - Logique d'appel depuis stamp_prix_ouverture : vérif heure Paris ≥ heure_ouverture + délai
       Tests : CA-M1, CA-M2, CA-M3

T1.2 — Modification run_bulletin.py (7h) :
       - Appel stamp_prix_ouverture pour actifs Continus (ouverts à 08h → déjà disponibles à 07h05)
       - [NOTE : actifs EU/US pas encore ouverts à 7h → non stampés ici]
       Tests : idempotence, pas de régression sur les tests existants

T1.3 — Modification mesure 24h dans journaliste.py :
       - measure_cell : pour horizon 24h, lire prix_ouverture au lieu de prix_emission
       - Rétrocompat : si prix-ouverture absent → fallback prix-emission avec WARNING (transition)
       Tests : CA-M4, CA-M6, CA-B3

T1.4 — Nouveau script run_bilan_jour.py :
       - Fetch clôture pour tous les actifs (Twelve Data)
       - Appel stamp_prix_ouverture pour actifs US (pas encore stampés à 12h/18h si run 22h premier)
       - Appel Journaliste pour noter les cellules 24h du bulletin 7h
       - Génération rapport R4 markdown
       - Écriture dans v3/data/bilans-jour/{date}.md
       Tests : CA-B1, CA-B2, CA-B4, CA-B5

T1.5 — Mise à jour cycle.yml :
       - Nouveau schedule 22h (jours de bourse)
       - Step run_bilan_jour.py
       - Anti-doublon ×3
       - Mise à jour VPS trigger
       Tests : CA-I1, CA-I4
```

**Critère de sortie Phase 1** : les cellules 24h dans `measures-log.jsonl` ont `prix_emission` = prix d'ouverture réel, et sont notées VRAI/FAUSSE/NC le soir même (22h).

### Phase 2 — Suivis intra-journée (R2/R3)

**Prérequis** : Phase 1 terminée (stamp_prix_ouverture fonctionnel).

```
T2.1 — Nouveau script run_suivi.py :
       - Paramètre report_type: "12h" | "18h"
       - Lecture prix-ouverture + fetch prix courant
       - Génération tableau markdown (CA-S1 à CA-S5)
       - Écriture dans v3/data/suivis/{date}-{heure}.md
       Tests : CA-S1 à CA-S6

T2.2 — Modification cycle.yml :
       - Steps 12h et 18h appellent run_suivi.py à la place de (ou en plus de) run_bulletin.py
       [QUESTION OUVERTE Q9 — voir §9 : les steps 12h/18h doivent-ils encore lancer run_bulletin.py complet ou uniquement run_suivi.py ?]
       Tests : CA-I3 (mis à jour)
```

**Critère de sortie Phase 2** : les rapports suivis sont produits et committés. Ils ne génèrent pas de cellules dans measures-log.

### Phase 3 — Bilan semaine + Manager (R5)

**Prérequis** : Phase 1 terminée (win-rate archive hebdo fonctionnelle — déjà fait S24). Phase 2 optionnelle pour cette phase.

```
T3.1 — Nouveau script run_bilan_semaine.py :
       - Lecture performance.md, win-rate-{AAAA-Sxx}.md, decision-log (semaine)
       - Calcul métriques Manager (cellules faibles, critères faibles)
       - Génération rapport R5 avec propositions (format §4.5)
       - Écriture dans v3/data/bilans-semaine/{AAAA-Sxx}.md
       Tests : CA-W1 à CA-W5

T3.2 — Mise à jour cycle.yml :
       - Nouveau schedule dimanche 16h UTC
       - Guard weekday()==6 et bypass is_trading_day
       - Step run_bilan_semaine.py
       Tests : CA-I2

T3.3 — Mise à jour VPS Anya :
       - Créneau dimanche 18h dans /etc/cron.d/tradingapp
       Tests : CA-I3 (mis à jour)
```

**Critère de sortie Phase 3** : le bilan dimanche est produit et committé. Aucune modification YAML (CA-W4).

---

## 9. Risques et questions ouvertes

> Principe : zéro invention. Tout point non tranché est signalé ici. @fullstack ne doit PAS inventer une réponse. Thomas décide.

### Questions ouvertes (décision Thomas requise avant implémentation du bloc concerné)

**Q1 — Créneau dédié 09h05 pour stamp ouverture EU**
- Contexte : le run 12h stampe l'ouverture EU 3h après l'ouverture réelle. Le prix est stable mais pas celui de l'ouverture exacte.
- Option A : Ajouter un créneau 09h05 Paris (dédié stamp-only, pas de bulletin). Plus précis. +1 créneau VPS.
- Option B : Stamper dans le run 12h (3h après ouverture). Plus simple. Légère imprécision sur le prix exact de l'open.
- Bloque : T1.2 de Phase 1.

**Q2 — Jour semi-férié (un marché fermé, l'autre ouvert)**
- Contexte : le 4 juillet NYSE est fermé mais Euronext est ouvert. `is_trading_day` actuel teste NYSE ∪ Euronext → si l'un est fermé, la garde retourne False et stoppe tous les runs.
- Problème : on rate un jour Euronext actif.
- Option A : Garder la garde globale actuelle (plus simple, moins de cas tordus).
- Option B : Run partiel (stamp + bulletin uniquement pour les marchés ouverts ce jour-là).
- Bloque : T1.5, mais pas critique Phase 1 (rares).

**Q3 — Référence 7j/1m : prix-ouverture ou prix-emission ?**
- Contexte : le design validé mentionne `prix_ouverture_J0` pour 7j/1m. La spec suit.
- Impact : migration des cellules existantes si on change la référence en cours de route. Rétrocompat nécessaire.
- Option A : Migrer 7j/1m vers prix-ouverture (cohérence totale).
- Option B : Garder prix-emission pour 7j/1m, uniquement 24h migre vers prix-ouverture.
- Bloque : T1.3.

**Q4 — Seuil de suggestion « Sortir » dans R2/R3**
- Contexte : la suggestion `Sortir` dans le tableau suivi nécessite un seuil (ex. perte > seuil_actif × 0.5).
- Si pas de seuil défini → suggestion = `Hold` ou `Surveiller` seulement (pas de `Sortir` automatique).
- Option A : Seuil automatique (actif × facteur). Risque : suggestion mécanique sans jugement.
- Option B : Pas de suggestion `Sortir` automatique — seulement `Hold` / `Surveiller`. Thomas décide.
- Bloque : CA-S4 (choix de la valeur fermée `Suggestion`).

**Q5 — Close EU dans R3 (suivi 18h)**
- Contexte : le run 18h est après la clôture EU (17h30). Twelve Data retourne-t-il le close officiel pour FCHI/ETF après 17h30 ?
- Si oui : utiliser le close. Si non : utiliser le dernier prix disponible.
- Test requis : appeler `fetch_twelve_price("FCHI")` à 18h et vérifier la valeur retournée.
- Bloque : T2.1.

**Q6 — Sélection des news « qui ont compté » dans R4**
- Contexte : le bilan 22h mentionne les news qui ont réellement impacté les prix. Comment les identifier automatiquement ?
- Option A : Déléguer à DeepSeek (prompt : « parmi les news du jour, lesquelles ont causé un mouvement > seuil sur ces actifs ? »). +1 appel DeepSeek/jour.
- Option B : Sélection manuelle par Thomas (pas d'automatisation).
- Option C : Croiser news ingestées du jour avec actifs VRAI/FAUSSE du bilan → afficher les news du créneau de l'actif.
- Bloque : T1.4 (niveau de détail du rapport R4).

**Q7 — Job séparé vs schedule dans même workflow pour dimanche**
- Contexte : le bilan dimanche pourrait être un job séparé (`weekly-summary`) ou un schedule additionnel dans `cycle-decision`.
- Job séparé : plus propre, pas de risque de confusion avec les runs quotidiens.
- Schedule additionnel : plus simple, moins de fichiers YML.
- Bloque : T3.2.

**Q8 — Rétrocompat des bulletins 12h/18h existants**
- Contexte : il existe déjà des bulletins stampés 12h et 18h dans `v3/data/bulletins/`. Doit-on les mesurer jusqu'à expiration ou les ignorer ?
- Option A : Mesurer jusqu'à expiration (propre, rien perdu, mais N_brut gonfle encore 2-3 semaines).
- Option B : Stopper la mesure des bulletins non-7h à compter de la mise en prod. Les anciens sont marqués `non-note` rétroactivement.
- Bloque : T1.3 (logique de filtrage des bulletins à mesurer).

**Q9 — run_bulletin.py aux créneaux 12h/18h après refonte**
- Contexte : actuellement les runs 12h/18h produisent un bulletin complet (scoring + briefing). Après refonte, ces créneaux produisent R2/R3 (suivis courts).
- Option A : Remplacer run_bulletin.py par run_suivi.py aux créneaux 12h/18h. Le scoring complet n'est fait qu'à 7h.
- Option B : Conserver run_bulletin.py aux 3 créneaux (scoring complet) MAIS ne mesurer que le bulletin 7h. Les bulletins 12h/18h restent produits mais non-mesurés.
- Impact : Option B conserve le scoring complet 3×/jour (3 snapshots pour Thomas si utile). Option A réduit les coûts API (Twelve/DeepSeek).
- Bloque : T2.2.

### Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Twelve Data indisponible à l'heure d'ouverture | Moyen | Mesure 24h impossible ce jour | suivi-interrompu + retry au run suivant (zéro invention) |
| Décalage timestamp Twelve ≠ heure d'ouverture réelle | Faible | Légère imprécision du prix de référence | OPEN_STAMP_DELAY_MIN = 5 min (marché stabilisé) |
| VPS Anya absent au créneau 22h | Faible | Schedule GitHub seul (retard 1-3h possible) | Redondance ×3 schedule comme les autres créneaux |
| Bilan dimanche déclenché par erreur un lundi | Très faible | Run inutile, pas de dommage (pas de mesure) | Guard `weekday() == 6` stricte |
| Manager propose ajustement appliqué sans validation Thomas | Critique | Modification silencieuse de poids | CA-W4 : vérification git diff v3/config/ = vide après run R5 |
| Migration 24h vers prix-ouverture casse les tests existants | Moyen | Régression test suite | Rétrocompat : si prix-ouverture absent → fallback prix-emission + WARNING |

---

*Spec rédigée par @product-manager le 2026-06-08. Validé design : Thomas. Pour implémentation : @fullstack (@infrastructure pour cycle.yml + VPS). Source de vérité — ne pas modifier sans passer par @product-manager.*
