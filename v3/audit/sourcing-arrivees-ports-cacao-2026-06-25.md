# Audit — Sourcing du critère « Arrivées de cacao aux ports ivoiriens (20 j) »

> Suite directe de `v3/audit/fallback-source-cacao-2026-06-25.md` (reco complémentaire n°1 laissée ouverte : « réparer la source arrivées ports, ou repondérer/retirer — à trancher par Thomas, sans inventer »).
> Critère : `arrivees_port_abidjan_sanpedro_20j`, **poids 9** (2ᵉ plus lourd du cacao après la météo, poids 11), `signe -1` (arrivées baissent → LONG), `v3/config/fiches/cacao.yml` id=2.
> Statut actuel : **toujours n/a** — `criteres-health.md` (cycle 25/06 05:23 UTC) : « Source z-score non programmatique » = AUCUNE source automatisée. Le fallback « dernière valeur valide » ne peut RIEN reporter (jamais aucune valeur observée).
> Garde-fous fondateur : **zéro invention** (source absente → n/a, poids 0) · **zéro modif silencieuse des poids** · un changement de SIGNAL se mesure en **shadow** avant cutover. Ce document = RECO + plan. **Ne modifie NI fiche NI code NI poids.**

---

## 0. Pourquoi ça compte (rappel chiffré, sur pièces)

- Incident 25/06 : cacao **+7,13 %** (meilleur move du jour), **raté**. Cause = couverture cacao **41 %** (< `SELECTION_COVERAGE_MIN=0.70`) → écarté du Top 3. Le poids n/a cumulé était 20 : météo (11, panne réseau Open-Meteo) **+ arrivées ports (9, trou structurel)**.
- Le fallback (livré 25/06) soigne la **panne météo** mais **pas** les arrivées ports : aucune valeur n'a jamais été observée pour cette clé → rien à reporter. Tant que la source reste morte, **poids 9 zombie en permanence** → couverture cacao plafonnée structurellement, cacao durablement difficile à sélectionner.
- Donc : soit on **source** ce critère, soit on **repondère** (changement de SIGNAL → shadow + Thomas, hors de ce livrable). Ce document tranche le volet sourcing.

---

## 1. Recherche de sources (WebSearch, 25/06) — état réel, honnête

La donnée **existe** et est **suivie publiquement chaque semaine** (chiffres GEPEX, repris par Reuters le lundi : cumul saison depuis le 1ᵉʳ octobre + ventilation hebdo Abidjan/San-Pédro). Exemples vérifiés : semaine 15-21 déc ≈ 84 000 t (40 000 Abidjan / 34 000 San-Pédro) ; au 21 juin 2026, cumul **1,883 Mt (+18 % a/a)**, hebdo ≈ 29 000 t (9 000 Abidjan / 20 000 San-Pédro).

Le problème n'est donc PAS « la donnée n'existe pas » mais « par quel canal **accessible et idéalement programmatique** ».

| Source | Accès | Programmatique ? | Coût / licence | Fréquence | Latence | Fiabilité |
|---|---|---|---|---|---|---|
| **GEPEX** (exportateurs : Barry Callebaut, Olam, Cargill) | email/asso `info@gepexci.com`, pas de portail | **Non** (aucune API ni open data) | privé (réservé membres) | hebdo | — | très haute (source primaire) |
| **Reuters** (reprend GEPEX le lundi) | terminal Eikon/Refinitiv + articles web (souvent paywall) | API payante (terminal) ; pas de feed gratuit stable | élevé (licence terminal) | hebdo (lundi) | ~0-2 j | très haute |
| **cocoaintel.com** — page « Ivory Coast Cocoa Arrivals » | **page web publique**, datée, MAJ ~hebdo (ex. URL `…ivory-coast-cocoa-arrivals-3-may-2026`) ; section « Market Data » | **Semi** : scrapable (HTML), **pas d'API gratuite documentée** confirmée | gratuit en lecture web ; API/feed = devis (non public) | hebdo | ~1-3 j | bonne (agrégateur spécialisé, reprend GEPEX) |
| **ICCO** | bulletins trimestriels PDF (payants pour le détail) | Non | abonnement | trimestriel | élevée | haute mais **trop lente** (≠ glissant 20 j) |
| **Conseil Café-Cacao** (régulateur CI) | site institutionnel, communiqués | **Non** (pas d'open data des arrivées) | — | irrégulier | variable | haute mais non structuré |
| **Presse spécialisée FR** (Agence Ecofin, Sikafinance, Commodafrica) | articles web gratuits reprenant GEPEX | Non (prose, pas de flux) | gratuit | hebdo/ad hoc | ~1-3 j | bonne |

**Verdict sourcing, sans enrobage :**
- **Aucune source GRATUITE ET PROGRAMMATIQUE (API/CSV stable)** n'existe pour ce critère. GEPEX ne publie pas ; Reuters est payant/terminal ; le Conseil Café-Cacao et l'ICCO ne fournissent pas un flux glissant 20 j exploitable.
- La seule piste « semi-programmatique » est un **scrape de page** (cocoaintel.com), fragile par nature (page qui change, agrégateur tiers, pas de SLA, risque licence/robots), exactement le profil qu'on a déjà jugé fragile ailleurs (multpl CAPE = scraper défensif + override manuel en filet).
- En revanche, la donnée est **publiée en clair, hebdomadairement, avec un chiffre simple** (cumul saison + hebdo Abidjan/San-Pédro). C'est **lisible en 30 secondes** une fois par semaine.

---

## 2. Options (pour / contre / compatibilité « zéro invention »)

### (a) Intégrer un flux programmatique (scrape cocoaintel ou parse presse)
- **Pour** : automatisé, pas de geste humain.
- **Contre** : **aucune source gratuite fiable et stable**. Le scrape d'un agrégateur tiers est fragile (page change → critère retombe n/a, on n'a rien gagné), pose une **question de licence/robots** (revente de données GEPEX), et reste **hebdo** (pas un vrai flux temps réel). Risque élevé de « faux vert » (parse qui ramène un mauvais nombre = **invention déguisée**). Coût d'un vrai feed (Reuters/cocoaintel API) = non justifié pour 1 critère sur 1 actif.
- **Zéro invention** : tenable seulement avec garde-fous lourds (plage de plausibilité, rejet si parse ambigu) — beaucoup de code fragile pour un signal hebdo.

### (b) Saisie MANUELLE via `v3/data/manual/` (pattern déjà en place)
- **Pour** : le pattern **existe déjà et est éprouvé** (`v3/data/manual/shiller_cape.json` + `_read_manual_shiller_cape`, lecteur best-effort avec garde de plage, priorité sur scraper, n/a propre si absent/invalide). La donnée arrivées est **publiée 1×/sem, chiffre simple** → coût humain ≈ 1 min/semaine. **Zéro invention** native : on ne saisit QUE le chiffre publié (source citée), jamais une estimation. **Honnête et visible**.
- **Contre** : geste humain récurrent (dette opérationnelle) ; risque de **péremption** si Thomas oublie une semaine → il faut une **garde anti-péremption** (au-delà de N jours sans MAJ → la valeur expire → critère redevient n/a, jamais un chiffre zombie). C'est précisément le garde-fou « échec visible » du fondateur.
- **Compatibilité fallback** : parfaite — une fois une 1ʳᵉ valeur saisie, le fallback « dernière valeur valide » prend le relais sur une panne ponctuelle (plafond d'âge « structurel offre » = 5 j ouvrés déjà spécifié dans l'audit fallback).

### (c) Repondérer / retirer le poids 9 (si insourçable)
- **Pour** : supprime le plafond structurel de couverture ; honnête si la donnée était réellement inaccessible.
- **Contre** : c'est un **changement de SIGNAL** sur le 2ᵉ critère le plus lourd du cacao → **interdit ici** (shadow + validation Thomas obligatoires). Et ce serait **dommage** : la donnée existe, est de **haute qualité** et **fondamentale** pour le cacao (les arrivées ports = LE proxy d'offre court terme). La retirer reviendrait à s'amputer d'un signal réel par confort technique. **Non retenu** tant que (b) n'a pas été essayé.

---

## 3. RECO UNIQUE

### → Option (b) : saisie MANUELLE hebdomadaire via `v3/data/manual/arrivees_ports_ci.json`, avec garde anti-péremption.

**Pourquoi cette option et pas une autre :**
1. **La donnée existe, est publique, hebdo et simple** — la rater par confort technique serait absurde sur un poids 9 fondamental. La repondération (c) est prématurée et interdite ici (changement de signal).
2. **Aucune source gratuite/programmatique fiable n'existe** (verdict §1) → (a) = code fragile + risque licence + risque de faux vert (≈ invention) pour un signal qui ne bouge qu'une fois par semaine. Mauvais rapport robustesse/effort.
3. Le **pattern manuel est déjà en production** (Shiller CAPE), éprouvé, avec garde de plage et dégradation propre. Coût marginal ≈ **1 min/semaine** pour Thomas, contre un signal de **poids 9** récupéré. Rapport effort/valeur excellent.
4. **Zéro invention garantie** : on ne saisit QUE le chiffre publié (GEPEX via Reuters/cocoaintel/presse), source datée. Pas de valeur = n/a, comme aujourd'hui. On ne **dégrade rien**, on ne fait qu'**ouvrir la possibilité** de combler.

**Esquisse technique (à implémenter par @fullstack — PAS fait ici) :**
- Fichier : `v3/data/manual/arrivees_ports_ci.json`, schéma :
  ```json
  {"date_maj": "2026-06-22", "cumul_saison_kt": 1883, "hebdo_kt": 29,
   "abidjan_kt": 9, "sanpedro_kt": 20, "source": "GEPEX via Reuters 22/06"}
  ```
- **Normalisation z-score 60 j (inchangée par rapport à la fiche)** : la fiche demande un z-score `window=60`, `div=2`, `signe -1`. Le critère mesure une **variation d'arrivées** (« arrivées baissent → LONG »). Construire la **série historique** des arrivées hebdo (ou du cumul → différence hebdo) au fil des saisies : chaque MAJ append `{date, hebdo_kt}` dans un historique `v3/data/manual/arrivees_ports_ci_history.jsonl`. Le z-score se calcule sur la **série des arrivées hebdo** (déviation de l'arrivée de la semaine vs sa distribution 60 derniers points), strictement comme les autres critères z-score. **Tant que < ~8-10 points d'historique → critère n/a** (pas de z-score sur 1 point = anti-invention ; warm-up honnête, comme les KPI Wilson en chauffe).
- Lecteur `_read_manual_arrivees_ports()` calqué sur `_read_manual_shiller_cape` : best-effort, garde de **plage de plausibilité** (ex. hebdo ∈ [0, 200] kt — au-delà = parse/saisie suspecte → ignoré), n/a propre si fichier absent/invalide.
- **Garde anti-péremption (garde-fou clé)** : si `today - date_maj > 10 jours` (≈ 1,5 cycle hebdo + marge week-end/férié) → la valeur **expire** → critère redevient **n/a VISIBLE** (jamais un chiffre figé qui dériverait silencieusement). Cohérent avec le plafond « structurel offre » de l'audit fallback (5 j ouvrés pour le report sur panne ; ici 10 j calendaires car la donnée elle-même est hebdo). Drapeau `⚠️ saisie périmée` au rendu si on approche du seuil.
- **Aucun cutover de signal** : ajouter une source à un critère aujourd'hui n/a n'inverse aucune direction existante (il était à poids 0 effectif). Le critère **passe de n/a à actif** dès la 1ʳᵉ fenêtre d'historique suffisante. Comme c'est un critère qui **entre dans le score**, surveiller en **shadow** l'effet sur la direction cacao au premier run où il devient vivant (vérifier qu'il ne crée pas une bascule absurde) avant de considérer l'affaire close — mais ce n'est pas un changement de poids/seuil, juste le comblement d'un trou de données prévu par la fiche.

**Procédure opérationnelle (à documenter pour Thomas) :**
- Chaque **lundi** (ou au prochain run après publication GEPEX), relever le chiffre hebdo Abidjan + San-Pédro (cumul + hebdo) depuis une source publique (Reuters / cocoaintel / Agence Ecofin / Sikafinance) et mettre à jour le JSON. 1 min.
- Si oubli > 10 j → le système le signale tout seul (n/a visible), pas de dérive silencieuse.

**Ce qu'on NE fait PAS :** aucun scrape fragile imposé (option a écartée) ; aucune repondération du poids 9 (option c = signal, interdite ici) ; aucune valeur inventée/estimée ; le critère reste n/a tant que l'historique est insuffisant.

**Note de confiance : 8,5 / 10.**
La donnée est réelle, publique, de haute qualité et fondamentale ; le pattern manuel est éprouvé et zéro-invention ; le coût humain est dérisoire (1 min/sem) face à un poids 9 récupéré. Le -1,5 : (1) la saisie manuelle est une **dette opérationnelle** (dépend de la discipline hebdo de Thomas — atténué par la garde anti-péremption qui rend l'oubli visible, pas dangereux) ; (2) la **série z-score doit se construire dans le temps** (warm-up de quelques semaines avant que le critère soit vivant), donc l'incident-type ne sera couvert qu'**après** accumulation d'historique — ce n'est pas un fix instantané. Pour accélérer le warm-up, @fullstack peut **amorcer l'historique** avec quelques points hebdo déjà publiés et **datés/sourcés** (zéro invention : ce sont des chiffres réels publics), si Thomas valide cette amorce.

---

## Handoff → @fullstack

- **Fichiers produits** : `v3/audit/sourcing-arrivees-ports-cacao-2026-06-25.md` (ce document). **Aucune** modif de fiche/code/poids.
- **Décision** : combler `arrivees_port_abidjan_sanpedro_20j` (poids 9) par **saisie manuelle** `v3/data/manual/arrivees_ports_ci.json` + historique `…_history.jsonl`, pattern calqué sur Shiller CAPE, **garde anti-péremption 10 j** (expiration → n/a visible). Z-score 60 j inchangé (fiche), calculé sur la série des arrivées hebdo. Warm-up honnête : n/a tant que < ~8-10 points.
- **À implémenter (hors de ce livrable)** : lecteur `_read_manual_arrivees_ports`, branchement dans le dispatcher du critère, append historique, drapeau `⚠️ saisie périmée`, plage de plausibilité [0,200] kt, tests (saisie valide → critère vivant ; absente/périmée/hors-plage → n/a). **Mode shadow** au premier run vivant (vérifier la direction, pas de bascule absurde).
- **Points d'attention** : aucune source gratuite/programmatique fiable → la **saisie manuelle est la seule voie zéro-invention robuste** ; ne PAS imposer un scrape fragile (faux-vert = invention). Repondération du poids 9 = **changement de SIGNAL → shadow + Thomas**, à n'envisager QUE si Thomas refuse la saisie manuelle.
- **Décision Thomas requise** : (1) valider le principe de saisie manuelle hebdo (1 min/sem) ; (2) autoriser ou non l'**amorce d'historique** avec des points hebdo passés déjà publiés (datés/sourcés, zéro invention) pour raccourcir le warm-up.

### Sources (URLs)

- cocoaintel.com — Ivory Coast Cocoa Arrivals : https://www.cocoaintel.com/ivory-coast-cocoa-arrivals-3-may-2026/ · https://www.cocoaintel.com/cocoa-market-balances-strong-ivory-coast-arrivals-against-rising-weather-risks-22-june-2026/ · Market Data : https://www.cocoaintel.com/data/
- GEPEX (FCC member page) : https://www.cocoafederation.com/the-fcc/fcc-members/gepex-groupement-professionnel-des-exportateurs-de-cafe-et-de-cacao-de-cote-divoire
- Reprises presse hebdo GEPEX : https://invezz.com/news/2025/12/07/whats-driving-the-sudden-cocoa-pile-up-at-ivory-coasts-busiest-ports/ · https://www.sikafinance.com/marches/cote-divoire-forte-baisse-des-livraisons-de-cacao-aux-ports-dabidjan-et-san-pedro_24983 · https://www.agenceecofin.com/actualites/1512-134321-baisse-des-prix-du-cacao-la-filiere-ivoirienne-sous-tension-exportateurs-en-difficulte
- Conseil Café-Cacao (régulateur, pas d'open data arrivées) : http://www.cacao.gouv.ci/index.php?rubrique=1.3.2&langue=fr
