# Refonte du Bilan hebdomadaire — 5 sections (S9)

> Demande fondateur Thomas. Restructure le « Bilan de la semaine » (R5 / le Manager,
> dimanche 18h Paris) produit par `v3/scripts/run_weekly.py` (`build_bilan_semaine`)
> et rendu sur la page via `build_html.py`.
>
> RÈGLES ABSOLUES (héritées de la mission et de CLAUDE.md) :
> - **WIN RATE ONLY** — aucune valeur monétaire (€/$/PnL/gain/rendement). Toute
>   performance est un **% de mouvement directionnel**, jamais un montant.
> - **ZÉRO INVENTION** — une donnée manquante (prix de référence absent, etc.) est
>   affichée « — » / « non disponible », jamais fabriquée (commandement 2).
> - **Le Manager PROPOSE, n'applique RIEN** (CA-W4) — `git diff v3/config/` vide
>   après tout run. Préservé tel quel.
> - Aucune chaîne affichée créée par ce module ne contient de tiret cadratin `—`
>   (ponctuation FR — cf. S9 vague 2). Le `—` n'est utilisé que comme **placeholder
>   de valeur vide** (cellule sans donnée).

## Les 5 sections (ordre imposé)

### 1. Performance des 24h sélectionnés (la semaine)

**But** : agrégat hebdomadaire de nos « top du jour » (cellules `selection_du_jour: true`,
horizon 24h) sur les jours de la semaine ISO courante.

**Contenu** :
- **Win rate de la sélection** sur la semaine = VRAI / (VRAI + FAUSSE) des cellules
  sélectionnées, agrégé sur tous les jours de bourse de la semaine. Réutilise
  `bilan_jour.win_rate_selection` + `load_selection_map` (cumulé sur la semaine).
- **Ampleur moyenne en %** des sélections, séparée gagnantes / perdantes : moyenne
  du `|mouvement directionnel %|` des cellules sélectionnées conclusives. Le mouvement
  directionnel d'une cellule = `signe(LONG=+1, SHORT=-1) × (prix_echeance − prix_ref) / prix_ref × 100`,
  avec `prix_ref` = prix d'émission/ouverture du jour de décision (mêmes prix que la
  mesure, `_resolve_prix_reference`), `prix_echeance` = prix à l'échéance (J+1).

**Source de données** : measures-log (mesures jugées de la semaine) + decision-log du
jour (champ `selection_du_jour`). Un prix manquant → cellule exclue de l'ampleur (zéro
invention). N < 1 → « — (aucune sélection jugée cette semaine) ».

### 2. Performance par TENDANCE 7j, par actif (cœur de la demande)

**But** : pour CHAQUE actif, segmenter la semaine en **phases de direction 7j
CONSTANTE** et donner la **performance directionnelle** de chaque phase.

**Segmentation** (détail algorithmique) :
1. On parcourt les jours de bourse de la semaine ISO (lundi → dimanche), dans l'ordre.
2. Pour chaque jour, on lit le **dernier record** du decision-log de ce jour pour la
   cellule (actif, horizon `7j`) → sa direction (`conclusion_pm1` ∈ {LONG, SHORT}).
   On agrège par `cle_courante` = **`ticker_principal`** de la fiche (L023), robuste au
   renommage du nom d'affichage. Un jour sans decision-log lisible pour l'actif est
   **sauté** (pas de direction inventée).
3. Des jours **consécutifs de même direction** forment un **segment**. À chaque
   changement de direction (LONG→SHORT ou SHORT→LONG) = **bascule** = nouveau segment.
4. Le **prix de début de segment** = prix d'émission du **premier jour du segment**
   (le jour où cette direction a été prise ou a basculé — « les bons prix », L027) :
   `prix-emission/{date}-*.json` en priorité (point d'exécution réel 7h), fallback
   `prix-ouverture/{date}.json`. Résolu via le `ticker_principal` de la fiche.
5. Le **prix de fin de segment** :
   - segment **clos** (suivi d'une bascule) → prix d'émission du **dernier jour du
     segment** (la veille de la bascule) ;
   - segment **en cours** (dernier de la semaine) → **dernier prix disponible** =
     prix d'émission du dernier jour observé du segment (« maintenant » au sens des
     données présentes ; aucun fetch live en conteneur, zéro invention).
6. **Performance du segment** = `signe(LONG=+1, SHORT=−1) × (prix_fin − prix_debut) / prix_debut × 100`,
   soit le **% de mouvement DANS LE SENS de la tendance**. Un segment d'un seul jour
   (début == fin) a une perf de 0,0 % (pas encore de mouvement mesurable) — affiché tel
   quel, pas inventé.
7. **Cas prix manquant** : si le prix de début OU de fin du segment est introuvable
   (ticker absent des fichiers de prix), le segment est affiché avec sa direction et ses
   dates mais sa **perf = « — »** (zéro invention, aucun % fabriqué).

**Rendu attendu** (exemple) :
> **Or** : LONG (lun→mer) +1,5 % · SHORT (jeu→ven) +0,8 %

**Source** : decision-log par jour (direction 7j) ; `prix-emission/` + `prix-ouverture/` ;
fiches (`ticker_principal`). Agrégation par `cle_courante` (L023).

### 3. Ce qu'on a bien fait cette semaine

Synthèse courte et factuelle, **réutilise les « cellules porteuses »** déjà calculées par
le Manager (win rate ≥ 65 % sur N_eff ≥ 5) + le win rate par conviction forte s'il est
fiable + les segments de tendance gagnants de la section 2. Aucune donnée inventée :
chaque point cite un chiffre réel. Si rien de notable → message honnête « rien de
significatif cette semaine (warm-up) ».

### 4. Ce qu'on doit améliorer

Réutilise les **« cellules à surveiller »** (candidates faibles + faibles confirmées) et
les **propositions d'ajustement** du Manager (CA-W4 : il PROPOSE, n'applique RIEN). +
segments de tendance perdants de la section 2. Garde-fou conservé : pas de proposition
sur petit N (mesurer avant d'agir).

### 5. Les learnings de la semaine

Synthèse **actionnable et déterministe**, dérivée des sections 1-4 (pas de LLM, pas de
blabla) : sélection trop prudente / trop large, tendances 7j gagnantes vs perdantes par
actif, écart conviction forte vs faible, cellules persistantes sous l'objectif. Chaque
learning est gated par un seuil chiffré ; si aucun seuil franchi → « pas de learning
net cette semaine (échantillon insuffisant) ».

## Réutilisation (zéro recalcul custom)

- Win rate hebdo / par conviction / cellules porteuses / cellules à surveiller /
  propositions : **inchangés**, réutilisés tels quels.
- `bilan_jour.win_rate_selection` + `load_selection_map` : agrégés sur la semaine.
- `journaliste.measure` / `_resolve_prix_reference` / `iso_week_bounds` / `load_fiches`.
- `briefing.strip_monetaire` : appliqué si jamais on cite une news (filet WIN RATE ONLY).

## Persistance

L'état hebdo du Manager (`v3/data/bilan-semaine/.state/{ISO}.json`, candidates faibles)
est **conservé tel quel**. La segmentation par tendance est **recalculée à chaque run**
(lecture seule du decision-log + prix), sans nouvel état persisté.

## Limites honnêtes

- En conteneur, **aucun prix live** (clé Twelve absente) : la perf des segments en cours
  s'arrête au dernier prix d'émission présent dans `v3/data/`, pas au prix temps réel.
- Les données passées en conteneur (decision-log + prix archivés) permettent de **valider
  l'algorithme** mais le rendu live réel n'apparaîtra que sur un run live (lundi 23/06).
- 7j en warm-up jusqu'en octobre 2026 : la section 2 décrit le **mouvement de marché**
  par phase (observabilité), pas un win rate statistiquement significatif.
