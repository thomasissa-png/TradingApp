# Schéma fiche actif (YAML) + spec de scoring — v3

> Source : `Bourse/Actifs/_README.md` + `Agents/Analyste.md` + fiche `Pétrole.md` (vault, lus 29/05).
> Les fiches markdown du vault sont converties en YAML machine-lisible ici (`v3/config/fiches/*.yml`).

## Formule de score (déterministe, zéro LLM)

```
contribution(critère, H) = valeur_normalisée × poids × pertinence[H] × signe
Score(H) = Σ contributions   pour H ∈ {24h, 7j, 1m}
Conclusion(H) = LONG si Score>0 · SHORT si Score<0 · tie-break si =0
```

**Tie-break (score = 0, Analyste §5.2, dans l'ordre) :**
1. Majorité des **3 critères les plus pesants** (|poids|) → 2/3 LONG ⇒ LONG, sinon SHORT.
2. Égalité 3-3 ⇒ reconduire la conclusion de la veille (même cellule).
3. Aucune veille ⇒ LONG par défaut.

## Types de normalisation (`valeur_normalisée` ∈ [−1, +1])

| type | calcul | exemple fiche |
|---|---|---|
| `zscore` | z = (val − moyenne_window) / écart-type ; puis `z / zscore_div` capé à ±`cap` | EIA surprise (window 52, div 2, cap 1) |
| `lineaire` | `(val − centre) / echelle` capé à ±`cap` | term structure (centré 0), spread Brent-WTI (centré 3 USD) |
| `triplet` | déterministe **+1 / 0 / −1** selon mots-clés/état (cf. `triggers-and-windows.yml`) | tension géopol, OPEC+ |
| `gate` | **TBD — sémantique non définie dans Analyste.md** (voir ⚠️ ci-dessous) | « événement extrême » Pétrole |

`signe` : `+1` normal, `−1` si le critère est inversé (ex : DXY monte ⇒ pétrole baisse → signe −1).
Valeur manquante / source DEAD ⇒ critère `n/a`, **poids 0 pour ce run** (red line zéro invention).

## ⚠️ Point à trancher par Thomas — sémantique du GATE

La fiche Pétrole a un critère `GATE — événement extrême` (poids = `gate`, pertinence 1/1/1) listant des conditions (OPEC meeting < 7j, frappes Iran < 48h, FOMC < 24h, EIA Crude < 4h). `Analyste.md` ne dit PAS ce que le gate FAIT au score. 3 interprétations possibles :
- (a) **multiplicateur de confiance** (booste l'amplitude du score sans changer le sens),
- (b) **drapeau d'alerte** (n'entre pas dans le score, signale juste « cellule sous événement » dans le bulletin),
- (c) **veto/forçage** (force une conclusion ou suspend la cellule).
→ Le moteur traitera le gate comme **(b) drapeau** par défaut (le plus sûr, n'altère pas le score) tant que Thomas n'a pas tranché.

## Schéma YAML d'une fiche

```yaml
actif: "<Nom>"
ticker_principal: "<ex BZ=F>"
famille: "<indices|volatilité|fx|énergie|métaux-précieux|métaux-industriels|agri>"
news_zone: "<US|EU|EU-FR|Global|...>"
version: <int>
seuils_reussite_pct:        # |delta| % dans le sens prédit pour compter VRAI
  24h: 1.0
  7j: 2.5
  1m: 6.0
criteres:
  - id: 1
    nom: "<libellé>"
    source: "<EIA API | Twelve Data | events-log | CFTC | ...>"
    cle_courante: "<clé dans criteres-courants.md>"
    normalisation: "<zscore|lineaire|triplet|gate>"
    # params selon type :
    zscore_window: 52        # zscore
    zscore_div: 2
    centre: 0                # lineaire
    echelle: 1
    cap: 1.0
    signe: 1                 # +1 ou -1
    poids: 10
    pertinence: { "24h": 1.0, "7j": 0.8, "1m": 0.3 }
    effet_long: "<condition qui pousse LONG>"
    effet_short: "<condition qui pousse SHORT>"
```

## Format `criteres-courants.md` (entrée du moteur, produit par l'ingestion)

YAML par actif → clé critère → valeur brute + timestamp. Le moteur lit la valeur brute, applique la normalisation de la fiche.
```yaml
last_update: 2026-05-29T06:45:00+02:00
petrole:
  eia_crude_surprise: { valeur: -1.8, ts: 2026-05-28T16:30:00+02:00 }   # σ vs consensus
  tension_geopol_moyen_orient: { valeur: +1, ts: ... }                   # triplet déjà résolu
  ...
```

## Sortie du moteur (`scoring_analyste.py`)

- MAJ section « Bulletin courant » de chaque fiche + `_bulletin-quotidien.md` (matrice 12×3, format Analyste §4).
- Chaque cellule : conclusion + score numérique. Flips vs veille tracés. Critères `n/a` listés en « Limites du jour ».
- Stamp `analyste_version` + hash des fiches.
