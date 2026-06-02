# Gates pipeline — LISTE FINALE CONVERGÉE (après concertation round 2)

> Synthèse des 3 experts (News Trader / Analyst / Spéculateur) après débat contradictoire.
> Sources : `gates-CONSOLIDE.md` + `gates-{expert}-r2.md`. S5 (suffisance données) = ✅ déjà livré.

## Frictions tranchées (les 3 désaccords du round 2)

**F1 — C3 « trend-first dur » (Spé) vs « news peut casser la tendance » (NT)** → **Compromis adopté** :
C3 ne désigne PAS un gagnant fixe. Il **détecte et drapeaute** la divergence quant↔news ; le **cap α=0.8** (déjà en place) arbitre l'amplitude de l'override news ; **C1** garantit que le signe est juste ; et le gate **score-vs-momentum** (résidu-détecteur) attrape toute conclusion finale à contre-tendance. Une vraie news fraîche peut donc casser une tendance (via cap α + high+confirmed), mais jamais en silence.

**F2 — C8 déjà-cotée : P0 (NT) vs P1 (Spé)** → **Scindé (Analyst)** :
- **C8a** détection « already priced » = **P0** (Lot 5, avec la sanity sémantique).
- **C8b** chaînage démenti/correction = **P1** (post-shadow).

**F3 — C4 quorum strict (Spé) vs anti-quorum (NT : un scoop n'a qu'une source)** → **Compromis** :
Pas de quorum bloquant. C4 = **plafond de contribution mono-news** + **seuil materiality×reliability** (gate réclamé par NT, P0) → un scoop high+confirmed passe, une rumeur isolée non.

## Démotions actées (consensus)
Latence d'ingestion → P2 (monitoring, non-CI) · anti-hallucination citation → P2 · cohérence inter-actifs corrélés → P2 · multiple-testing → P2 **mais trigger explicite : avant émission réelle** (correction Bonferroni obligatoire pour valider un KPI sur 36 cellules).

---

## ROADMAP FINALE (ordre de build convergé)

### Lot 1 — Fondation déterministe (P0, automatisable CI) ← démarrer ici
- **C2** intégrité quant : `clip(z,-3,3)`, std=0→n/a, prix>0, NaN/Inf, anti-spike (var aberrante)
- **Réconciliation Σ** : `assert |Σ contrib − score| < 1e-9` (observabilité, P0)
- **C9** normalisation UTC des timestamps à l'ingestion *(Analyst : dépendance — doit précéder C5, sinon on verrouille un prix sur une TZ fausse)*
> ½ j, pur déterministe, prérequis de tout. 

### Lot 2 — C1 : cohérence de signe DeepSeek (P0, gate n°1 unanime)
- Table de référence signe macro (CPI/NFP/taux) + sanity texte→sens (news baissière jamais classée LONG)
> Le gate le plus important des 3 experts : un signe inversé à la source contamine tout l'aval.

### Lot 3 — Intégrité mesure (P0)
- **C5** verrou prix d'émission + échéance figée + assertions zéro look-ahead *(sûr car timestamps UTC depuis Lot 1)*
> Crédibilise le KPI shadow MAINTENANT (on mesure pendant qu'on améliore).

### Lot 4 — Cœur directionnel / justesse de tendance (P0)
- **C3** détection + drapeau divergence quant↔news (cap α arbitre)
- **C4** plafond mono-news + seuil materiality×reliability
- **Hystérésis** anti-flip marginal (score +0.05→−0.05 ne flippe plus la position)
- **Score-vs-momentum** prix récent (résidu-détecteur de C3)
- **C6** cohérence inter-horizons (P1)

### Lot 5 — Sanity sémantique
- **C8a** détection déjà-cotée (P0) · **C8b** démenti/correction (P1, post-shadow)

### Lot 6 — Publication & observabilité (P1)
- **C7** affichage conviction/contre-tendance/flip + cohérence biais agrégé↔détail
- **Mesure flip vs continuation** séparée (le chiffre qui valide un moteur de tendance)
- Distribution dégénérée des scores · multiple-testing (trigger : avant émission)

---

## Synthèse en une ligne
Plomberie déterministe (Lot 1) → signe juste (Lot 2) → mesure incorruptible (Lot 3) → jugement de tendance arbitré, pas additionné (Lot 4) → sanity news (Lot 5) → transparence à la publication (Lot 6). Les gates automatisables doivent passer AVANT sortie du mode shadow ; les recalibrations (seuils, multiple-testing) AVANT émission réelle.
