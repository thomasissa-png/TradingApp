# Bilan du soir 24h — refonte 3 blocs (S9)

> Demande fondateur Thomas, design validé. Branche `claude/elegant-tesla-tsz9ld`
> (suite de la Vague A « suivi 24h » : tableau Sélection + décision « Vendre à
> 12h/18h » datée, `compute_vendre`, % favorable signé — déjà mergé).
>
> **WIN RATE ONLY** : aucune valeur monétaire. L'ampleur en % est OK (Thomas l'a
> demandée). **Zéro invention** : un point de relevé absent → « — » + trou signalé.

## Intention

Le BILAN DU SOIR (22h15) groupe désormais **3 blocs en tête**, avant la mesure
détaillée existante (qui est conservée intacte — win rate du jour, par
conviction, FAUX à forte amplitude, news, catalyseurs).

### Bloc 1 — Performance 24h du Top 3 (la Sélection du jour)

Pour chaque cellule `selection_du_jour: true` (horizon 24h) :
- **% favorable signé vs ouverture à 12h / 18h / clôture** (`+` = va dans le sens
  du call). Source : `run_suivi.fav_delta` (fonction de vérité unique, réutilisée).
- **PIC** = meilleur % favorable atteint parmi {12h, 18h, clôture} + **à quelle
  heure**.
- **Verdict de sortie optimale relié aux heures** (`_verdict_sortie`) :
  * pic à la clôture → « monté jusqu'au bout, tenir était le bon choix » ;
  * pic avant la clôture + clôture plus basse → « sortir à {heure} aurait été
    mieux » (avec les deux valeurs) ;
  * jamais favorable → « rien à verrouiller ».
- **Confrontation à la reco réelle du suivi** (`compute_vendre` recalculé sur les
  relevés 12h→18h) : capté / sorti trop tôt / raté.

### Bloc 2 — Gros mouvements hors Top 3 + pourquoi pas joués

Cellules 24h **non sélectionnées** dont `|mouvement vs ouverture| ≥ 2 × seuil_actif`
(réutilise `GROS_MOVE_FACTOR`), **triées du plus gros au plus petit** (le plus gros
= le plus intéressant à jouer). Pour chacune :
- **mouvement %** signé ;
- **bonne direction ou ratée** (call 24h vs sens réel via `fav_delta`) ;
- **pourquoi pas sélectionné** (`reason_non_selection`, déduit du decision-log) ;
- **1 ligne d'apprentissage**.

### Bloc 3 — Apprentissage du jour

Synthèse déterministe sur les blocs 1-2 (`compute_apprentissage_jour`) : sorties
optimales ratées, sélection trop prudente (bonne direction non jouée), mauvaise
direction sur un gros move, trous de données intraday signalés.

## D'où viennent les % de pic 12h / 18h (persistance ajoutée)

Les snapshots `v3/data/suivi/{date}-12h.json` existants ne stockent que des deltas
bruts par actif (pas de call, pas de fav%, pas de 18h, nom d'actif divergent). Ils
sont **insuffisants** pour reconstruire le pic.

→ **Persistance dédiée ajoutée** dans `run_suivi.py` :
`v3/data/suivi-tracking/{date}.json`, écrit **aux deux créneaux 12h ET 18h** par
`save_suivi_tracking`. Forme :

```json
{
  "12h": {"S&P 500": {"call": "LONG", "fav_pct": 1.0, "heure": "12h05"}},
  "18h": {"S&P 500": {"call": "LONG", "fav_pct": 0.8, "heure": "18h05"}}
}
```

- **Idempotente** : un même créneau remplace son propre bloc sans toucher l'autre
  (rejouer le 12h ne perd pas le 18h).
- N'écrit **que** les cellules `selection=True` avec un `fav_now` calculable
  (zéro invention : un actif sans relevé exploitable est absent → trou explicite).
- **Cache de présentation** (CA-S6) : n'alimente NI `measures-log` NI
  `performance.md`. `v3/data/` jamais commité par l'agent.

Le Bilan lit ce json (`load_suivi_tracking`) + l'ouverture (`prix-ouverture/{date}`)
+ la clôture (mesure existante, NON réécrite). **Si une heure manque** (pas de
relevé, ou snapshot vide `{}` comme le 19/06) → affichée « — », pic calculé sur les
points disponibles, trou signalé au Bloc 3.

## Logique « pourquoi pas sélectionné » + honnêteté zéro-invention

`reason_non_selection`, par priorité :
1. **`selection_motif_exclusion`** présent dans le decision-log → raison EXACTE
   tracée par le sélecteur (`"hors top 3"`, `"même pari (taux/dollar) que EUR/USD"`).
2. Sinon, **déduite des étapes 1-2 de `compute_selection_du_jour`** (source unique,
   pas une invention) : conviction non « forte » (drapeau actif ou |score| sous le
   seuil) → critère conviction nommé ; couverture < `SELECTION_COVERAGE_MIN` (0,70)
   → critère couverture chiffré.
3. **Indéterminable** (record absent, ou conviction forte + couverture OK sans
   motif tracé) → **« raison non tracée »** (jamais d'invention).

## Tests

`v3/tests/test_bilan_soir_24h.py` (27 tests, tous verts) :
- Bloc 1 : pic à 12h (sortir plus tôt), pic à la clôture (tenir), point manquant
  (pic sur dispo + trou signalé), jamais favorable, call discordant ignoré,
  non-sélectionnés exclus.
- Bloc 2 : bonne direction / mauvaise direction, sous-seuil exclu, tri du plus
  gros, top3 exclu ; `reason_non_selection` (motif exact, conviction, couverture,
  drapeau, non tracée).
- Bloc 3 : sortie ratée + prudence, mauvaise direction, trou de données, rien de
  notable.
- Persistance : save/load 12h+18h, idempotence (ne touche pas l'autre créneau),
  n'écrit que la Sélection avec fav, « rien à écrire » n'efface pas, absent → {}.
- Reco « Vendre à 18h » recalculée (verrouille gain qui reflue / laisse courir).

Suite complète : **22 failed (env-only pré-existants : `holidays`/`pandas`/
`yfinance` absents — test_backtest\*, test_criteres, test_bilan_jour_cam7_cab2),
1521 passed, 12 skipped**. Zéro régression introduite (les 22 env-only files
contiennent exactement 22 échecs ; tous les autres fichiers passent).

## Garde-fous respectés

- WIN RATE ONLY (% jamais €). Agrégation par cellule (L023, via `selection_map`).
- **Zéro tiret cadratin `—` dans une chaîne affichée créée** : `—` n'apparaît que
  comme placeholder de cellule vide (ponctuation FR ailleurs).
- La mesure existante (ouverture/clôture, win rate, conviction) n'est PAS modifiée
  — les 3 blocs sont ajoutés EN TÊTE, le reste est conservé.
- `build_html.py` réussit (bilan rendu en markdown via marked + CSS de la page).
- Vérif visuelle desktop 1280 + mobile 390 : tableau lisible (en-têtes complets
  desktop / courts mobile via `.c-full`/`.c-short`), 3 blocs clairs, aucun mot
  coupé.
