# Gates pipeline — SYNTHÈSE DE CONCERTATION (round 1 consolidé)

> Fusion des 3 audits (News Trader / Analyst / Spéculateur) sur la grille 9 étapes.
> Total brut : ~134 gates listés → dédupliqués ici. **Consensus** = signalé par ≥2 experts (confiance max).
> Sources : `gates-newstrader.md`, `gates-analyst.md`, `gates-speculateur.md`.

## Ce qui EXISTE déjà (ne pas reconstruire)
- **S1** `source_monitor` (santé flux) ✓ · **S3** T1/T2 dédup + nature (exclut deja_cote/verbal) ✓ · **S5** suffisance données (🔧 en build) · **S6** cap news α=0.8 + drapeau 📰 ✓ · **S7** jamais-neutre ✓ · **S8** prix d'émission stampé + non-chevauchant ✓ · **S9** gate shadow (KILL-CRITERION) ✓

---

## GATES CONSENSUS (≥2 experts) — priorité absolue

| # | Gate | Étape | Experts | Pourquoi critique |
|---|---|---|---|---|
| **C1** | **Cohérence de signe DeepSeek** (news baissière classée LONG) + table signe macro (CPI/NFP/taux) | S2 | NT, Sp | L'erreur la plus chère : tout le pipeline part du mauvais côté. Aucun re-check texte→sens. |
| **C2** | **Intégrité quant** : borne z-score `clip(-3,3)`, std=0→n/a, prix>0, NaN/Inf check, anti-spike (var aberrante) | S4/S6 | An, NT, Sp | Un z-score non borné/NaN écrase tous les critères → conviction artificielle 100% sur donnée corrompue. |
| **C3** | **Arbitrage divergence quant↔news** (au lieu d'additionner) + détection conflit 50/50 | S6 | Sp, NT | Racine n°1 des positions à contre-tendance : SHORT 51% news/49% quant en pleine vague haussière, sans drapeau. |
| **C4** | **Anti-bascule mono-news + quorum** de sources indépendantes avant de retourner une tendance | S3/S6 | NT, Sp | Une seule dépêche fraîche peut flipper un actif (passe T1/T2). Manque plafond + quorum + force-tendance. |
| **C5** | **Intégrité mesure** : verrou prix d'émission + échéance figée + zéro look-ahead (échéance≥émission, prix_courant≥émission) | S8 | NT, An, Sp | Sans verrou, le taux de réussite est corruptible (moving goalposts) → KPI illusoire → décision faussée. |
| **C6** | **Cohérence inter-horizons** (LONG 24h / SHORT 7j sans cause datée = incohérence muette) | S7 | Sp, NT, An | Le lecteur prend la mauvaise jambe. La séquence d'horizons doit raconter une histoire (continuation/retournement daté). |
| **C7** | **Publication** : cohérence biais agrégé↔détail + affichage conviction/contre-tendance/flip | S9 | NT, Sp, An | Dernier rempart : Thomas doit VOIR un SHORT contre-tendance/flip, pas l'exécuter comme un LONG solide. |
| **C8** | **Détection « déjà cotée »** (already priced) + démenti/correction chaînés | S3 | NT, (Sp) | Entrer sur un move déjà fait → faux « VRAI » non exécutables. |
| **C9** | **Intégrité horodatage/TZ** à l'ingestion (timestamps mixtes UTC/local) | S1 | NT, An, Sp | Fausse la fraîcheur (S3) ET le prix d'émission (S8) en cascade. |

## GATES SOLO importants (1 expert, P0/P1)
- **[An] Réconciliation Σ contributions = score** (S6) — sans ça le decision-log est inrejouable. **P0.**
- **[Sp] Hystérésis anti-flip marginal** (S6) — score +0.05→-0.05 flippe sur du bruit chaque cycle. **P0 trend.**
- **[Sp] Mesure flip vs continuation séparée** (S8) — LE chiffre qui valide un moteur de tendance. **P0.**
- **[An] Enum nature → exclusion scoring effective** (S2/S3) — sinon la classification nature est décorative. **P0.**
- **[Sp] Score vs momentum prix récent** (S6) — drapeau si conclusion contredit le prix sur l'horizon. **P0.**
- **[An] Multiple-testing 36 cellules** (S8) — correction Bonferroni/BH pour les p-values KPI. **P2.**
- **[An] Distribution dégénérée des scores** (S6) + **idempotence bout-en-bout** (S2/S3/S7). **P1/P2.**
- **[NT] Garde macro/risk-off transverse** (S6) — un VIX spike doit contraindre les LONG actions. **P1.**

---

## ROADMAP DE BUILD proposée (par lots, ordre de valeur/risque)

**Lot A — Intégrité quant & calcul (P0, automatisable, faible risque)** ← commencer ici
C2 + réconciliation Σ : `clip(z,-3,3)`, std=0→n/a, prix>0, NaN/Inf, anti-spike, `assert |Σcontrib−score|<1e-9`. Pur déterministe, assertions pytest. **~½ j.**

**Lot B — Intégrité mesure (P0)**
C5 : verrou prix d'émission, échéance figée, assertions zéro look-ahead dans `journaliste.py`. Crédibilité du KPI. **~½ j.**

**Lot C — Jugement directionnel / trend-first (P0, cœur métier)**
C3 (arbitrage quant↔news, défaut tendance-prix gagne) + C4 (anti-bascule + quorum) + hystérésis + C6 (cohérence inter-horizons) + score-vs-momentum. **~1-2 j.**

**Lot D — Sanity DeepSeek (P0, sémantique)**
C1 (cohérence signe + table macro) + C8 (déjà-cotée/démenti). Partie rules-table + éventuel 2e check DeepSeek. **~1-2 j.**

**Lot E — Publication & observabilité (P1)**
C7 (biais↔détail, affichage conviction/contre-tendance/flip) + C9 (TZ) + flip/continuation mesuré + distribution dégénérée. **~1 j.**

**12 gates automatisables** (assertions pytest) doivent passer AVANT sortie du mode shadow. Les recalibrations (seuils, Levenshtein, multiple-testing) = revue humaine avant émission réelle.
