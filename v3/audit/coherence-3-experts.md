# Audit de cohérence des 3 experts — run 9e2ccc0 (2026-06-01)

> Vérification croisée des 3 rapports (`chaine-analyst/newstrader/speculateur.md`) contre le code
> et les données réelles. Objectif : ne corriger que des bugs PROUVÉS (gate G_PROOF, zéro invention).

## Verdict par claim

| Claim | Source | Verdict | Preuve |
|---|---|---|---|
| Inversion géopol : `tension_geopol = +1 LONG` figé par mots-clés, non câblé au scoring | Spéculateur (+ Analyst pour le biais) | ❌ **OBSOLÈTE** (corrigé le 31/05) | `criteres-courants` : `source_track: ia_synthese` ; `triggers_classifier.py:719` `val_signed = 1 if direction=="LONG" else -1`. Le `keyword` (l.844-850) n'est qu'un fallback sans synthèse. Pétrole LONG = **jugement DeepSeek**, pas un +1 figé. |
| Contamination events 2025 → look-ahead bias sur le Café | Analyst | ❌ **FAUSSE ALERTE** | `triggers_classifier.py:743` `cutoff = now - timedelta(days=lookback_days)` ; lookback max 60j (`triggers-and-windows.yml:319`). Les 45 events 2025 (>150j) sont **exclus** du scoring. Clutter d'archive, pas un biais. |
| PROBA_SCALE=10 → Brier pathologiques (saturation dès \|score\|>5) | Analyst | ✅ **VALIDE** | `journaliste.py:64` `PROBA_SCALE=10.0`, commenté « mapping non calibré empiriquement ». Scores réguliers ±5 à ±14 → saturation moitié des actifs. → **15**. |
| `reliability` vidée dans la chaîne (confirmed/reported/rumor perdu) | News Trader | ✅ **VALIDE** | 14× `reliability: ''` dans `criteres-courants` alors que le triplet du fichier 1 la porte. Propagation à réparer. |
| Autocorrélation 7j (~86%) / 1m (~97%) → N effectif illusoire | Analyst | ✅ **VALIDE** (déjà partiellement géré) | `performance.md` affiche déjà des warnings warm-up + Wilson sur N_eff. Renforcer : ne pas présenter de KPI 1m avant N_eff suffisant. |
| Pétrole LONG +10 = contre-sens à fuir | Spéculateur | ⚖️ **NUANCE** | News Trader a vérifié le log : flux frais `confirmed:high` d'escalade, mesuré **VRAI +2,74%** à 24h. Jugement synthèse défendable ce jour. Contexte-prix a déjà abaissé conviction (0.42). Pas un bug → **monitoré par le shadow**. |
| Mono-critère (Cacao/Café/Cuivre/EUR-USD ≈ COT seul) | Spécu + Analyst | ⚠️ **Pas un bug** | Manque de sources câblées (FRED, LME, Caixin…). Chantier sourcing séparé. |
| Conviction croît avec l'horizon | Spéculateur | 🔍 **À surveiller** | Possible artefact de pondération OU effet lookback (plus d'events sur 30j). Non tranché — pas corrigé sans preuve. |

## Périmètre de correction autopilote (items PROUVÉS uniquement)
1. **PROBA_SCALE 10 → 15** (`journaliste.py`)
2. **Propagation `reliability`** triplet → critère (`triggers_classifier.py`)
3. **Garde éligibilité mesure** : ne pas présenter de KPI tant que N_eff insuffisant (renfort `journaliste.py`)

## NE PAS toucher (faux positifs prouvés)
- Câblage du signe géopol (déjà `ia_synthese`).
- Purge « contamination 2025 » (le cutoff lookback l'exclut déjà).
