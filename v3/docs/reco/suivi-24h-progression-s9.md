# Suivi 24h — Tableau de progression « Sélection du jour » + reco Vendre / Pas vendre (S9)

Demande fondateur (Thomas, S9). WIN RATE ONLY : aucune valeur monétaire ; l'ampleur
en % du mouvement est OK (demandée). Branche `claude/elegant-tesla-tsz9ld`.

## 1. Tableau de progression « Sélection du jour » (vue rapide, en TÊTE)

Ajouté en tête de chaque suivi (12h et 18h), AVANT le suivi détaillé. Source : les
cellules `selection_du_jour: true` du decision-log 24h du jour (réutilise
`bilan_jour.load_selection_map`, mapping mesuré, zéro invention).

Colonnes : `Actif | Call 7h | % vs ouv. 12h | % vs ouv. 18h | Tendance | Vendre / Pas vendre`.

- Le `%` est le mouvement directionnel **signé FAVORABLE** vs l'ouverture
  (`fav = +delta si LONG, −delta si SHORT`) : `+` = va dans le sens du call (gagne),
  `-` = contre nous. But : voir la PROGRESSION 12h→18h d'un coup d'œil.
- Au **12h** : seule la colonne « 12h » est remplie (« 18h » = `—`, placeholder).
- Au **18h** : « 12h » = favorable du snapshot 12h, « 18h » = favorable courant.
- Aucune cellule sélectionnée ce jour-là → « Pas de sélection aujourd'hui. » (pas
  d'invention). Le suivi détaillé de TOUTES les positions 24h reste plus bas.

Implémentation : `run_suivi._render_selection_table` + champs `selection`, `vendre`,
`fav_now`, `fav_prec` sur `SuiviLigne`.

## 2. Reco binaire « Vendre / Pas vendre » — `compute_vendre` (fonction pure)

Remplace la colonne « Suggestion » (Hold / Surveiller / Sortie) dans le tableau
Sélection ET dans le suivi détaillé. Orientée MAXIMISATION DU GAIN depuis l'ouverture.
Le drapeau interne `suggestion` reste calculé (il alimente encore le bloc
« Suggestions de sortie »), mais n'est plus affiché en colonne.

`compute_vendre(delta_now, delta_prec, call, neutral_band_pct) -> "Vendre" | "Pas vendre"` :

- Soit `fav_now`, `fav_prec` les favorables signés (None au 12h, faute de précédent).
- `|delta_now|` sous la bande neutre → **Pas vendre** (rien à verrouiller).
- **Favorable** (`fav_now > 0`) :
  - 12h (fav_prec None) → **Pas vendre** (laisse courir, pic indétectable).
  - 18h : si `fav_now < fav_prec` (gain reflue = pic passé) OU signe inversé
    (était pour nous, maintenant contre) → **Vendre** ; sinon → **Pas vendre**.
- **Contre nous** (`fav_now < 0`) :
  - 12h → **Pas vendre** (laisse la journée).
  - 18h : si `fav_now < fav_prec` (ça empire) → **Vendre** ; si ça se redresse vers
    l'ouverture → **Pas vendre**.
- Données absentes (delta None, call non LONG/SHORT) → **Pas vendre** (défaut sûr).

Note rendue sous le tableau (1 ligne) : « Vendre = verrouiller un avantage qui reflue,
ou couper un pari qui empire ; sinon on garde. »

## 3. Rendu mobile

Le tableau Sélection (6 colonnes) est trop large pour 390px. Pas de masquage de la
reco : sur mobile (CSS `.selection-progression`, classe posée en JS par
`markSelectionTables` sur la signature d'en-tête « % vs ouv. 12h ») on resserre
police/padding ET on masque la colonne « Tendance » (5e) — la progression des deux
colonnes `%` porte déjà la dynamique, et la reco « Vendre / Pas vendre » reste
visible SANS scroll. Sur desktop, les 6 colonnes sont affichées.

## Garde-fous respectés

- WIN RATE ONLY (aucun €/$/gain/perte dans les chaînes affichées ; le mot « gain »
  est évité dans le rendu — token interdit par `test_aucune_mention_monetaire`).
- Zéro invention : données absentes → `—` / « Pas vendre » / « Pas de sélection ».
- Pas de tiret cadratin `—` dans une chaîne FR créée ; le `—` reste comme placeholder
  de cellule vide (autorisé).
- Le suivi n'écrit toujours pas dans measures-log / performance.
