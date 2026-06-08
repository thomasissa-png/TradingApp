# Audit Journaliste — Angle Analyst (rigueur statistique)
> Date : 2026-06-08. Branche : claude/elegant-ramanujan-OIKms.
> Sources analysées : `journaliste.py` (v3.1.0), `performance.md`, `performance-ab.md`, `measures-log.jsonl` (extraits), `decision-log/2026-06-08-0704.jsonl`, `audit-reel-et-backtest-scope.md`, `KILL-CRITERION.md`.

---

## Verdict global

**LÉGER — la critique de Thomas est fondée.**

Le Journaliste a une infrastructure solide (entry-lock, look-ahead armé, non-chevauchant, Wilson, Brier), mais deux défauts structurels le rendent trop léger pour être décisionnel aujourd'hui : (1) les horizons 7j et 1m ne sont quasi jamais conclusifs, ce qui concentre de facto toute la mesure sur le 24h ; (2) le N_eff réel est trop faible (max 6/15 pour le 24h, 0-1/15 pour le 7j) et aucun critère global (multiple-testing) n'est encore activable.

---

## Partie 1 — Comment VRAI/FAUX est décidé : le seuil d'amplitude

### 1.1 Mécanique (code)

La règle est : `|delta_pct| > seuil → VRAI si dans le sens, FAUSSE sinon ; sinon non-conclusive`.

- Le seuil est lu dans `fiche.seuils_reussite_pct[horizon]` (YAML par actif).
- **Un mouvement minuscule peut-il donner VRAI trop facilement ?** Partiellement oui. EUR/USD a un seuil à 0.25 % — tout mouvement de 0.26 % compte comme VRAI. C'est un seuil calibré pour le forex, mais très bas : en régime directionnel continu (comme en mai–juin 2026), EUR/USD SHORT devient mécaniquement VRAI dès qu'il bouge un peu. Le taux de 100 % sur EUR/USD 24h (N=17) reflète autant le seuil bas que le signal réel.
- Le garde-fou anti-dégénéré (prix courant == prix émission → non-conclusive) est correct et implémenté.
- **Le « non-conclusive » est-il bien géré ?** Oui dans le code : exclu du dénominateur taux ET de Brier. Mais son volume est élevé et non signalé globalement. Voir section 3.

---

## Partie 2 — Les 3 horizons : mesurent-ils vraiment 24h / 7j / 1m ?

### 2.1 État des faits (performance.md, 2026-06-08)

| Horizon | Cellules avec N_eff > 0 | N_eff max observé | Conclusions 7j/1m terminées |
|---|---|---|---|
| 24h | 12/12 | 6 | 21 mesures / actif (brut chevauchant) |
| 7j | 9/12 | 1 | 2 mesures / actif (brut) |
| 1m | 0/12 | 0 | 0 mesures / actif |

**Constat brutal :**

- **L'horizon 1m n'existe pas encore.** Zéro mesure terminée. Aucune cellule 1m n'apparaît dans `performance.md`. Le système déclare 3 horizons, il en mesure 1 (et demi).
- **Le 7j est anecdotique.** N_brut = 2 par actif (premiers bulletins du 01/06 arrivés à échéance le 08/06). N_eff = 1 (non-chevauchant) — soit 1 seule observation indépendante. Wilson_low sur N=1, k=1 : 0.206. Wilson_low sur N=1, k=0 : 0.000. Ces KPIs ne signifient rien.
- **Le 24h concentre tout.** C'est l'unique horizon avec un N utilisable (6 obs non-chevauchantes). Mais N_eff = 6 < 15 (seuil warm-up), donc même le 24h est en warm-up.

### 2.2 Pourquoi les 7j/1m ne sont-ils pas plus avancés ?

Les premiers bulletins avec prix d'émission datent du ~29/05. Les échéances 7j tombent le 05/06 au plus tôt, les 1m tombent le ~28/06. Le système est en production depuis ~10 jours : c'est un simple problème de temps, pas un bug. **Mais Thomas demande si la mesure est "légère" et la réponse est oui : par construction, 10 jours de shadow = 0 mesure 1m et ~2 mesures 7j. Le Journaliste est structurellement limité à court terme.**

### 2.3 Déflation par chevauchement pour le 7j

Le code signale correctement : `N_eff déflaté par chevauchement (÷9 pour 7j)`. Avec 3 bulletins/jour et un horizon 7 jours, on a chevauchement ~86 % : sur 2 mesures brutes 7j, N_eff = 1 seulement. C'est correct dans le code, mais aggrave le problème de N.

**Pour le 1m (÷60) : le premier N_eff = 1 ne sera atteint qu'après 30 jours de shadow + 30 jours de délai = J+60 au plus tôt.** Le 1m est structurellement non mesurable dans les 60 premiers jours.

---

## Partie 3 — Volume de non-conclusives : le silence de la mesure

### 3.1 Décompte (performance.md)

Sur les cellules 24h (les seules avec data) :

| Actif | N_brut (terminées) | N_vrai + N_fausse | N_nc (estimé) | Ratio nc |
|---|---|---|---|---|
| Argent 24h | 21 | 20 (95%+5%) | 1 | ~5% |
| Blé 24h | 21 | 18 (33%+67%) | 3 | ~14% |
| CAC 40 24h | 21 | 14 (43%+57%) | 7 | ~33% |
| Cacao 24h | 20 | 17 (0%+100%) | 3 | ~15% |
| Café 24h | 19 | 11 (82%+18%) | 8 | ~42% |
| Cuivre 24h | 20 | 18 (6%+94%) | 2 | ~10% |
| EUR/USD 24h | 17 | 15 (100%+0%) | 2 | ~12% |
| Nasdaq 24h | 21 | 20 (90%+10%) | 1 | ~5% |
| Or 24h | 21 | 19 (100%+0%) | 2 | ~10% |
| Pétrole 24h | 21 | 14 (93%+7%) | 7 | ~33% |
| S&P 500 24h | 21 | 20 (5%+95%) | 1 | ~5% |
| VIX 24h | 21 | 17 (65%+35%) | 4 | ~19% |

*Note : N_nc = N_brut − (N_vrai + N_fausse). Les ratios sont estimés à partir des taux bruts.*

- Les nc varient de 5 % (Argent, Nasdaq, S&P) à 42 % (Café) — pas uniformes.
- Café 24h a 8/19 non-conclusives (42 %) malgré un seuil à 1.0 % : le café peut être volatil puis stable. Ce taux élevé est normal mais **n'est nulle part signalé globalement**.
- **Trou de reporting** : il n'existe pas de métrique `ratio_nc_global` dans `performance.md`. Thomas ne voit pas facilement combien de "silences" il y a dans la mesure. Un score de 100 % sur 15 mesures conclusives masque 10 non-conclusives qui pourraient indiquer un biais de sélection (le système ne se mesure que quand ça bouge fort dans le bon sens).

---

## Partie 4 — Indépendance et N_eff réel : le problème central

### 4.1 N_eff constaté

Les 12 cellules 24h ont toutes N_eff entre 3 et 6, contre un seuil warm-up de 15. Le tableau suivant résume :

| N_eff actuel | Cellules | Statut |
|---|---|---|
| 6 | Argent, Blé, Cacao, Café, Cuivre, Nasdaq, Or, Pétrole, VIX, EUR/USD | warm-up |
| 3 | CAC 40 | warm-up |
| 0-1 | Tout le 7j | non significatif |
| 0 | Tout le 1m | pas de données |

**N_eff = 6 maximum en 24h** (après ~10 jours de shadow). Pour atteindre N_eff = 15, il faut ~25 jours ouvrés supplémentaires soit environ J+35 depuis le lancement.

### 4.2 Le N_eff est-il bien calculé ?

La fonction `select_non_overlapping` implémente un algorithme correct : tri par échéance, sélection de la première mesure puis saut d'au moins `step_days` (= 1j pour 24h). Pour le 24h, `step_days = 1` : toute mesure du lendemain est éligible. C'est correct et non-biaisé.

Pour le 7j, `step_days = 7` : sur 2 mesures brutes distantes de 7 jours (01/06 et 08/06), N_eff = 1 (une seule observation, l'autre est dans la fenêtre d'exclusion). C'est correct.

**Pas de gonflement artificiel détecté dans la logique de sélection.** Le problème n'est pas un bug de calcul mais un manque de données brutes.

### 4.3 Problème latent : les 3 bulletins/jour partagent le même prix d'émission

Au decision-log 2026-06-08-0704.jsonl, les critères de l'Argent à 7h04 utilisent les mêmes valeurs de critères (`taux_10y_us_reels_tips = 2.11`, `ratio_gold_silver = 63.63`) pour les 3 horizons 24h/7j/1m. **Les 3 bulletins du même jour produiront quasi-systématiquement la même conclusion** (seules les `pertinence` varient par horizon, pas les valeurs des critères). Or, ces 3 bulletins comptent comme 3 lignes dans `measures-log.jsonl`.

Concrètement : dans `select_non_overlapping`, les bulletins du matin/midi/soir d'un même jour ont des `echeance` identiques pour le 24h (même jour ouvré suivant). La fonction garde la première et rejette les deux autres — **le code est donc correct**, mais si l'implémentation ne les déduplique pas parfaitement (échéances distinctes selon l'heure exacte), une inflation est possible. Ce point mérite une vérification rapide.

**Vérification dans le code** : `compute_echeance` calcule l'échéance à partir de `bulletin_date` (jour seul, pas l'heure). Trois bulletins du même jour donnent la même `echeance` pour 24h. `select_non_overlapping` trie par échéance et prend la première : les 2 autres sont rejetées. **Le code est correct sur ce point.** Mais les 3 bulletins produisent néanmoins 3 lignes dans `measures-log.jsonl` avec les mêmes scores et la même conclusion : le `N_brut` est triplé artificiellement pour chaque jour à 3 bulletins. `N_brut` affiché dans `performance.md` compte les mesures chevauchantes — il est donc gonflé ×3 par les créneaux intrajournaliers. Ce n'est pas grave car `N_eff` (décisionnel) les déduplique correctement, mais Thomas peut être induit en erreur par le `N_brut = 21` qui semble impressionnant.

---

## Partie 5 — Robustesse : look-ahead, mesure dégénérée, suivi-interrompu

### 5.1 Look-ahead : armé mais partiellement opaque

Le verrou C5 est implémenté et correct :
- `entry_lock` sur le prix d'émission : immuable une fois stampé.
- Vérification `prix_courant_date < bulletin_date` → INTERROMPU.
- Vérification `today < echeance` → INTERROMPU.

**Limite** : `prix_courant_date = None` si Twelve Data ne renvoie pas d'horodatage (retour scalaire). Dans ce cas, le verrou look-ahead reste "latent" — il ne détecte pas un éventuel prix périmé. Dans le code, `fetch_twelve_price` retourne probablement un float scalaire dans la plupart des cas (voir l'usage de `_extract_price_dated`). **Si Twelve Data renvoie un prix de la veille sans horodatage, le look-ahead ne le détecte pas.** Ce cas existe : Twelve API peut renvoyer le dernier prix disponible, qui en cas d'interruption peut être le close de la veille.

### 5.2 Mesure dégénérée (prix figé)

Le garde-fou `prix_courant == prix_emission → non-conclusive` est correct. Mais il ne détecte pas un prix quasi-figé (ex : +0.01 % sur marché fermé avec un tick parasite). Ce n'est pas critique, mais à noter.

### 5.3 Suivi-interrompu : volume et causes

Dans `performance.md`, toutes les cellules 24h affichent `2 suivi(s) interrompu(s) sur la fenêtre observable`. Ces 2 interrompus correspondent aux premiers bulletins (29/05) pour lesquels le prix d'émission ou le prix courant manquait (système pas encore opérationnel). C'est normal et non pathologique. Mais **aucune distinction n'est faite entre les causes d'interruption** : prix d'émission absent, Twelve indisponible, seuil manquant dans la fiche, ou refus look-ahead. Pour un audit opérationnel, distinguer ces causes serait utile.

---

## Partie 6 — KPIs : Wilson, Brier, multiple-testing

### 6.1 Wilson : calcul correct, mais critère d'éligibilité partiel

La formule `wilson_ci` est correcte (formule Wilson standard à z=1.96). Le seuil d'éligibilité `wilson_low > 0.50` (50 %) est conservateur et approprié.

**Problème** : l'éligibilité n'est déclenchée que si `taux_eff_pct >= 70 % ET wilson_low > 50 %`. La cellule EUR/USD 24h a `N_eff = 5, taux_eff = 100 %, wilson_low = 0.566` — elle devrait être éligible selon les règles, mais elle est en `shadow` à cause du warm-up (`N_eff < 15`). **Ce comportement est correct** : N_eff = 5 est trop petit pour conclure.

Ce qui manque : une ligne dans le tableau de synthèse montrant combien de cellules *seraient* éligibles si on retirait la contrainte warm-up. Cela permettrait à Thomas de savoir si la tendance est positive.

### 6.2 Brier : correct mais peu informatif à N petit

Le calcul `(proba - outcome)²` avec `proba = 0.5 + clip(|score|/PROBA_SCALE, 0, 0.5)` est correct. Le mapping score→proba est documenté comme non-calibré empiriquement (calibration.md le signale).

**Problème** : avec N=6 observations conclusives (non-chevauchantes), un Brier de 0.14 (Or 24h) vs 0.55 (Cuivre 24h) n'est pas interprétable statistiquement. L'incertitude sur le Brier à N=6 est énorme — aucun intervalle de confiance n'est fourni. Le Brier est affiché mais **son IC n'est nulle part calculé** : on ne sait pas si la différence Brier(Or)=0.14 vs Brier(Cuivre)=0.55 est significative ou du bruit.

### 6.3 Multiple-testing : signalé mais non activable

Le code affiche correctement `Avec 36 cellules testées, ~1-2 faux positifs attendus par hasard à α=0,05`. La correction est implémentée via Wilson_low > 50 % (seuil conservateur). **C'est correct.**

Mais la section `Critère global` dans `performance.md` affiche `warm-up (aucune cellule avec N_eff ≥ 15)` pour toutes les cellules — ce qui est honnête. **Aucune cellule n'est déclarée éligible, donc le risque de faux positif multiple-testing est nul aujourd'hui.** Le problème surviendra quand les N_eff monteront : avec 36 cellules simultanément évaluées, le seuil Wilson_low > 50 % peut encore produire des faux positifs (probabilité Bonferroni : ~1-2 cellules faussement éligibles sur 36 à α global = 5 %). Une correction Bonferroni formelle ou un seuil d'éligibilité relevé à Wilson_low > 55 % serait plus rigoureux.

### 6.4 Le « 100 % sur 8 » est-il signalé comme non significatif ?

Oui, explicitement. EUR/USD 24h (100 %, N_eff=5), Or 24h (100 %, N_eff=6) sont tous deux en `shadow` avec l'alerte `warm-up : 5/15 obs`. **Ce point est géré correctement.** Wilson_low EUR/USD = 0.566 : significatif à N_eff=5 avec 100 %, mais le warm-up N_eff<15 bloque l'éligibilité.

---

## Partie 7 — Ce qui manque pour une mesure sérieuse

### TOP 5 des manques, classés par gravité

---

**Manque #1 (CRITIQUE) — Horizon 1m structurellement absent de la mesure**

- **Constat** : 0 mesure 1m terminée. Zéro. Le système prétend mesurer 3 horizons, il n'en mesure qu'un (24h) et un demi (7j avec N=1). Un verdict sur la qualité du système à horizon 1m est impossible avant J+90 au minimum.
- **Impact** : 12 des 36 cellules (33 %) sont invisibles. Si les 24h sont bons par hasard de régime mais que le 1m est catastrophique, on ne le verra pas avant 3 mois.
- **Ce qu'il faut ajouter** :
  - Un compteur visible `jours_avant_premier_1m` dans `performance.md` (ex : "Premier 1m attendu le 2026-06-28").
  - Une alerte explicite en synthèse : "⚠️ Horizon 1m : 0/12 cellules mesurables — décision d'émission impossible sur cet horizon avant J+60".
  - À terme : le backtest quant v2 (COT+FRED+7j/1m) est le seul moyen d'avoir des données 1m rapidement.

---

**Manque #2 (CRITIQUE) — N_eff trop faible pour le kill criterion et pour toute affirmation**

- **Constat** : N_eff max = 6/15 pour le 24h, le seuil kill criterion (N≥15) n'est pas encore atteint sur une seule cellule. On est à J+10 de shadow.
- **Impact** : Thomas ne peut aujourd'hui pas savoir si les taux de 95-100 % (Argent, Or, EUR/USD, Pétrole) sont de l'edge ou du bruit de régime haussier. Wilson_low sur N=6 est au mieux 0.61 (Or 100 %), ce qui est prometteur mais non conclusif.
- **Ce qu'il faut ajouter** :
  - Un tableau `jours_avant_N15` par cellule dans `performance.md` : "Argent 24h : ~9 jours ouvrés supplémentaires pour N_eff=15".
  - Une date estimée de première évaluation significative (automatique à partir du rythme actuel d'accumulation).

---

**Manque #3 (IMPORTANT) — N_brut gonflé ×3 par les créneaux intrajournaliers : illusion de données**

- **Constat** : performance.md affiche N_brut=21 pour la plupart des actifs 24h, ce qui donne une impression trompeuse de maturité. En réalité, N_eff=6 (les 3 bulletins/jour d'un même jour partagent la même échéance 24h et sont dédupliqués dans N_eff mais pas dans N_brut).
- **Impact** : Thomas (ou un auditeur) peut penser que 21 observations sont disponibles pour juger le signal. Ce n'est pas le cas — il n'y a que 6 observations indépendantes.
- **Ce qu'il faut ajouter** :
  - Retirer N_brut de l'affichage principal, ou le renommer `N_brut (chevauchant, non-décisionnel)` avec une note explicite.
  - Mettre N_eff en colonne principale avec une note : "seul N_eff est décisionnel".

---

**Manque #4 (IMPORTANT) — Ratio non-conclusives global non affiché**

- **Constat** : le taux de non-conclusives n'est visible que cellule par cellule (en recalculant manuellement N_nc = N_brut - N_vrai - N_fausse). Il n'y a pas de métrique globale `ratio_nc` dans la synthèse.
- **Impact** : un ratio nc élevé (>40 %, cas du Café) peut masquer un biais de sélection : le système "se mesure" surtout quand les marchés bougent beaucoup. Si ces fortes journées sont corrélées au signal (ex : news = grosse volatilité = VRAI plus facile), le taux de réussite est surestimé.
- **Ce qu'il faut ajouter** :
  - Colonne `N_nc` et `%_nc` dans la matrice principale de `performance.md`.
  - Alerte si `%_nc > 50 %` sur une cellule (le signal ne se déclenche que dans la moitié des cas — utile de le signaler).
  - Note méthodologique : les nc ne sont pas "mauvais" mais leur volume doit être visible.

---

**Manque #5 (MODÉRÉ) — Absence d'IC sur le Brier + calibration empirique absente**

- **Constat** : le Brier est calculé mais sans intervalle de confiance. À N=6, un Brier de 0.13 vs 0.55 n'est pas statistiquement distinguable. De plus, le mapping `proba = 0.5 + clip(score/15, 0, 0.5)` est purement heuristique — non calibré sur les données réelles.
- **Impact** : le Brier est affiché comme KPI de référence, mais il ne permet pas de discriminer les cellules à N petit. Il risque de créer une fausse confiance (Pétrole Brier=0.0005 sur N=2 est absurde).
- **Ce qu'il faut ajouter** :
  - Bootstrap IC sur le Brier (100 permutations → borne [2.5%, 97.5%]) quand N_eff ≥ 10.
  - Note "non-interprétable à N<10" dans le tableau pour les cellules concernées.
  - À J+30 : calibration Platt scaling sur les données accumulées (la structure `compute_calibration` est déjà dans le code, mais elle ne s'active qu'à N_conclusif ≥ 10 — ce seuil est approprié).

---

## Partie 8 — Points positifs (ce qui est solide)

Pour être équitable, ces éléments sont correctement implémentés :

1. **Entry-lock prix d'émission** (C5 invariant #1) : immuable, idempotent, loggé. Solide.
2. **Non-chevauchant implémenté** (`select_non_overlapping`) : logique correcte, N_eff bien calculé, alertes explicites.
3. **Wilson IC** : formule correcte, seuil conservateur (>50 %), double contrainte warm-up (N_eff<15) ET Wilson pour l'éligibilité.
4. **Mesure dégénérée** (prix figé) : détecté → non-conclusive au lieu de VRAI/FAUSSE bidon.
5. **Exclusion INSUFFISANT** : cellules sans couverture suffisante exclues du taux et de Brier. Correct.
6. **Multiple-testing signalé** : le commentaire "36 cellules → 1-2 faux positifs" est visible dans performance.md. Honnête.
7. **Transparence warm-up** : toutes les cellules affichent clairement leur statut warm-up. Thomas sait qu'il est en phase de collecte.

---

## Synthèse : 5 actions prioritaires

| Priorité | Manque | Action | Effort |
|---|---|---|---|
| P0 | Horizon 1m structurellement absent | Afficher `jours_avant_premier_1m` + alerte "décision impossible horizon 1m" | 30 min code |
| P0 | N_brut trompeur | Renommer N_brut → "N_chevauchant (non-décisionnel)" + mettre N_eff en avant | 20 min code |
| P1 | N_eff trop faible sans date estimée | Ajouter `jours_estimés_avant_N15` par cellule dans synthèse | 1h code |
| P1 | Ratio nc global invisible | Ajouter colonnes N_nc + %_nc dans matrice performance.md | 30 min code |
| P2 | Brier non interprétable à N<10 | Note "non-interprétable" + IC bootstrap à N≥10 | 2h code |

---

*Produit par @data-analyst — TradingApp v3 — 2026-06-08*
