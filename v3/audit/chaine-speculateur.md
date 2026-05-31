# Audit chaîne de production v3 — angle TRADER SPÉCULATEUR (cycle 31/05/2026)

Question : un trend-follower (vagues 24h/7j/1m) a-t-il, en bout de chaîne, un signal EXPLOITABLE,
ou la conviction se dilue-t-elle de fichier en fichier ? Audit fichier par fichier, dans l'ordre d'édition.

---

## 1. `1_events-log.md` — la matière première (news)
598 events, 142 à impact. Les VRAIS drivers de tendance sont là, et ils sont riches :
- **Pétrole** : signal bidirectionnel net — Iran/Hormuz/Israël-Liban (haussier) VS « cessez-le-feu US-Iran », « Brent -20% du pic », « plus grosse perte mensuelle en 6 ans » (baissier). La VAGUE réelle de mai est BAISSIÈRE (détente).
- **Nasdaq** : tension claire — restrictions export Nvidia/AMD Chine (↓) vs Dell +757%/+32% (↑). Driver macro = Fed (Bowman/Goolsbee/Kashkari : inflation énergie persistante → taux hauts).
- **Café** : « mauvaises récoltes Brésil+Vietnam », prix £5 → driver HAUSSIER explicite.
Constat : à l'entrée, le signal directionnel est FORT et daté. Rien ne manque ici. C'est la meilleure étape de la chaîne.

## 2. `2_criteres-courants.md` — la traduction en chiffres (1re dilution)
Vraies données présentes (TIPS 2.06, HY 2.72, VIX 14.95, SKEW 148.7, VVIX 92.67, COT, flux ETF). MAIS :
- **Les news directionnelles deviennent un triplet booléen 0/1** puis pondéré ×0.42. Toute la nuance « détente pétrole » du fichier 1 est écrasée en `tension_geopol_moyen_orient: 1` (HAUSSIER), à CONTRE-SENS de la vague réelle baissière. Le signal s'inverse ici.
- **Café haussier (news récoltes) → 0** : `maladies_cabosses_rouille: 0`, `source_track: none`. Le driver n°1 du fichier 1 n'a aucun canal numérique → perdu.
- Drivers macro morts : WASDE, EIA, crop progress, sentiment IA, OPEC = `note: hors fenêtre`/`none` → contribuent 0 malgré des poids 8-11.
Dilution réelle : la news qualitative survit mal, seul le quanti (taux/COT/flux) passe proprement.

## 3. `3_bulletin.md` — briefing + matrice 12×3 (re-concentration partielle)
Le briefing réaffiche les bonnes news (Hormuz, Nvidia-Chine, SoftBank 75 Mds€ FR, récoltes café). Bon.
MAIS la matrice contredit parfois le briefing :
- **Pétrole = LONG +7.28/+7.52** alors que le briefing liste « Brent plus grosse perte en 6 ans » et « Arabie baisse les prix ». Le moteur est LONG sur un actif en vague baissière. NON exploitable / dangereux.
- **Café = SHORT** alors que la news dominante est une pénurie haussière → contre-sens.
- Cohérents avec la vraie vague : **Nasdaq SHORT** (taux réels + restrictions Nvidia), **S&P LONG** (HY serré 2.72), **Cuivre SHORT** (PMI Chine faible).
Amplitude : 24h tassée (Argent +0.10, CAC +0.11, Or -0.13 — le système « ne sait pas »), 7j/1m tranchée.

## 4. `4_decision-log.jsonl` — 36 cellules, l'anatomie du score
Le scoring est traçable et honnête (contrib par critère visible). Lecture spéculateur :
- **Conviction CROÎT avec l'horizon, mécaniquement** : Argent +0.10 (24h) → +3.29 (1m) ; Nasdaq -2.07 → -4.30. Cause = `pertinence` qui monte vers 1.0 à 1m, pas un signal de tendance plus fort. La conviction longue est un ARTEFACT de pondération, pas un read de momentum.
- **Un driver domine souvent tout** : Cuivre = COT seul (-5.0, les 2 autres critères à 0) ; Pétrole = géopol +6.3 sur 7.28. Score = quasi-mono-critère → fragile.
- **Taux réels = même valeur (+0.50, signe -1) recyclée** sur Or/Nasdaq/Argent : pousse Or SHORT et Argent LONG en même temps (cohérent), mais l'argent LONG tient sur `ratio_gold_silver` figé normalisé à -1.0 → contrib +7.0, pas un trend.
- **VIX 1m diverge** (pm1 LONG +0.25 / pond SHORT -0.45) → cellule à signal nul, non exploitable.
Beaucoup de critères à contrib 0.0 (null) avec poids 8-11 → dilution du signal utile dans des cases vides.

## 5. `5_performance*.md` + `5_calibration.md` — la mesure (1er cycle)
**VIDE, attendu** : 12/12 cellules en `shadow`, N_total=0, toutes mesures `suivi-interrompu / prix d'émission indisponible`.
Calibration : « pas assez d'observations (<10) ». Le mapping score→proba (0.5 + |score|/10) est **déterministe, NON calibré empiriquement**.
Conséquence spéculateur : aucune boucle de feedback ce cycle. On ne sait PAS si un score +7 vaut mieux qu'un +1. La conviction affichée n'est pas encore adossée à un hit-rate. Normal au cycle 1, mais à noter : tant que cette étape est vide, l'amplitude des scores est invérifiable.

---

## Le signal survit-il à la chaîne ?
- **Fichier 1 (news)** : signal directionnel FORT et exploitable. Pic de qualité.
- **Fichier 2 (critères)** : 1re grosse perte — news→triplet 0/1×0.42, drivers qualitatifs (café, détente pétrole) écrasés ou inversés.
- **Fichier 3-4 (bulletin/scores)** : re-concentration sur le quanti (taux/HY/flux → S&P, Nasdaq, Cuivre cohérents et tranchés), mais conviction longue artificielle (pertinence) et cellules mono-critère fragiles. 24h trop tassé pour trader.
- **Fichier 5 (mesure)** : absente → pas de validation de l'amplitude.

**VERDICT : DILUÉ (partiellement exploitable).** Le quanti macro survit (Nasdaq SHORT, S&P LONG, Cuivre SHORT = tradables). Le qualitatif géopol/softs se dégrade ou s'inverse (Pétrole LONG et Café SHORT à CONTRE-SENS de la vraie vague). Le 24h ne tranche pas ; le 1m tranche pour de mauvaises raisons (pondération, pas momentum).

**Note : 5/10** (matière première 9/10, transmission 4/10).

4 puces actionnables :
- **Stopper l'écrasement news→triplet×0.42** : le pétrole en détente est scoré LONG — cabler la DIRECTION de la news (baissier/haussier), pas juste « tension active ».
- **Cabler les drivers qualitatifs orphelins** (café récoltes, sentiment IA) : poids 5-11 qui contribuent 0 = signal jeté.
- **Découpler conviction et horizon** : que +3.29 à 1m vienne d'un momentum réel, pas d'une pertinence montante — sinon faux signal de force.
- **Flag mono-critère** : Cuivre -5.0 = COT seul, Pétrole = géopol seul → marquer « 1 driver » pour ne pas trader comme une conviction multi-confirmée.
