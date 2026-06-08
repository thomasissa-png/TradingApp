# Résolutions des 9 questions ouvertes — refonte 5 rapports

> Tranché par l'orchestrateur selon les préférences fondateur (`docs/founder-preferences.md`) + le design validé Thomas. À pressuriser par le trio. Thomas peut overrider n'importe quelle décision.

| Q | Sujet | Décision retenue | Raison |
|---|---|---|---|
| **Q1** | Timing du stamp d'ouverture | **Stamper à la VRAIE ouverture** de chaque marché (fetch prix-only léger : ~8h05 continus, ~9h05 EU, ~15h35 US — sans scoring/DeepSeek). | Thomas a demandé explicitement « ouverture **propre** de chaque marché ». Stamper 3h plus tard trahit la demande. Coût = simples fetch prix (pas de scoring). ⚠️ ajoute des moments de stamp côté VPS. |
| **Q2** | Jour semi-férié (1 marché fermé) | **KISS : garde globale actuelle** (skip si NYSE **ou** Euronext fermé). Raffinement « run partiel » noté pour plus tard. | Cas rare ; éviter la complexité maintenant. |
| **Q3** | Référence 7j/1m | **Migrer 7j/1m vers prix-ouverture** (cohérence totale avec le 24h). | Migration quasi gratuite : 7j/1m sont en warm-up (N≈0-1), rien à perdre. Fallback prix-emission si ouverture absente. |
| **Q4** | Suggestion « Sortir » (12h/18h) | **Drapeau-suggestion seulement** : `à surveiller` / `sortie à envisager` quand la position est contre nous au-delà du seuil d'amplitude de l'actif. JAMAIS un ordre — Thomas décide. | Cohérent « le système ne place jamais d'ordre » + Thomas voulait des « sorties possibles ». |
| **Q5** | Close EU via Twelve à 18h | **@fullstack teste** `fetch_twelve_price("FCHI")` après 17h30 ; si pas de close officiel → dernier prix dispo + note. | Inconnue technique, pas une décision Thomas. Détail d'implémentation. |
| **Q6** | News « qui ont compté » (bilan 22h) | **Option C : croiser** les news ingérées du jour avec les actifs VRAI/FAUSSE du bilan (afficher les news du créneau de l'actif). **Zéro appel DeepSeek en plus.** | Gratuit, zéro invention, suffisant. |
| **Q7** | Job dimanche | **Workflow séparé `weekly-summary.yml`** (propre, pas de confusion avec les runs quotidiens). | Plus net, garde `weekday()==6`. |
| **Q8** | Rétrocompat bulletins 12h/18h existants | **Option B : stopper la mesure des bulletins non-7h** dès la mise en prod (anciens marqués `non-noté`). | Corrige le gonflement ×3 immédiatement. Peu de données perdues (warm-up). |
| **Q9** | Scoring complet 3×/jour ? | **Option A : 12h/18h = `run_suivi` léger** (prix + impact news, PAS de scoring complet). Scoring complet uniquement à 7h. | Exécute la décision Thomas (12h/18h = suivis courts) ET réduit les coûts API. |

## Les 3 calls que Thomas doit connaître (peut overrider)
1. **Q9 — un seul bulletin complet/jour (7h).** À partir de là, 12h/18h ne sont plus des bulletins complets, juste des suivis courts. C'est exactement ta demande, mais à acter : tu perds les ré-analyses complètes de 12h/18h.
2. **Q1 — stamp à la vraie ouverture** = quelques moments de fetch en plus (8h/9h/15h35). Petit ajout d'infra, mais c'est le prix de « référence = vraie ouverture ».
3. **Q4 — le système suggère une sortie (drapeau), ne l'ordonne jamais.** Tu gardes la main.
