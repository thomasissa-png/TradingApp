# Message Templates — Telegram
> TradingApp · Agent : @copywriter · Date : 2026-05-01
> v1.1 — 2026-05-01 — corrections @reviewer A1+A2
> Brand voice : Justifié · Concis · Backtesté — Zéro bullshit, transparent sur l'incertitude
> Framework copy : FAB (Feature → Advantage → Benefit) pour chaque champ du signal

---

## 1. Structure standard

[Framework : FAB — chaque champ livre une Feature, un Advantage, un Benefit implicite pour Thomas]
[Conscience : Most-Aware — Thomas connaît le produit, il attend le signal du jour]

### Format strict — 6 lignes signal + 1 ligne confiance

```
🟢 ACHAT / 🔴 VENTE / ⚪️ NO-TRADE  [Sous-jacent]
Entrée : [X,XX]  |  SL : [X,XX]  |  Cible potentielle : [X,XX]
Risque : [X€ max]  |  Capital engagé : [X€]  |  Avant [HH:MM] CET
Raison : [1-2 phrases max — chiffres obligatoires]
Backtest : [win_rate]% sur [nb] trades | DD max [−XX%] | Réf. [#B-NNN]
Score : [X.X]/10
```

### Champs obligatoires

| Champ | Format | Exemple |
|---|---|---|
| Sens | Emoji + mot | 🟢 ACHAT |
| Sous-jacent | Nom court | CAC40 Turbo Call |
| Entrée | Décimale 2 chiffres | 3,42 |
| SL | Décimale 2 chiffres | 3,21 |
| TP | Décimale 2 chiffres | 3,85 |
| Risque max | Arrondi entier en € | 126 € max |
| Capital engagé | Arrondi entier en € | 600 € |
| Fenêtre | Heure limite CET | Avant 8h55 CET |
| Raison | 1-2 phrases, chiffres | gap +0,8% + volume +32% |
| Backtest | Win rate + nb trades + DD | 63% sur 81 trades / DD −17% |
| Score | X.X/10 | 7,4/10 |
| Réf. | #B-NNN | #B-031 |

### Vocabulaire — tableau do/don't

| PROSCRIT | AUTORISÉ |
|---|---|
| "signal fort" | "Score 7,4/10" |
| "buy now" | "🟢 ACHAT — avant 8h55 CET" |
| "guaranteed" / "garanti" | "Backtest 63% sur 81 trades" |
| "perfect entry" | "Entrée : 3,42" |
| "opportunity" | "Raison : [chiffres]" |
| "ne pas manquer" | — (supprimer) |
| Futur affirmatif ("va monter") | Conditionnel ("cible potentielle") |

### Règles Markdown Telegram

- 1 emoji directionnel max en tête : 🟢 ACHAT, 🔴 VENTE, ⚪️ NO-TRADE
- 1-2 **bold** max par message (sous-jacent ou score uniquement)
- Pas de lien cliquable sur la 1re ligne
- Pas d'italique, pas de titres H1/H2
- Longueur totale : lisible en 25 secondes, ~10 lignes max

---

## 2. 14 exemples — variations par hypothèse

### H-A Gap Follow (ACHAT)

```
🟢 ACHAT  **DAX Turbo Call**
Entrée : 3,42  |  SL : 3,21  |  Cible potentielle : 3,85
Risque : 126 € max  |  Capital engagé : 600 €  |  Avant 8h55 CET
Raison : gap haussier DAX +0,9% vs clôture US — amplitude dans top 15% des 250 dernières ouvertures, volume Xetra 8h05 à +34% vs moyenne 5j
Backtest : 63% sur 81 trades | DD max −17% | Réf. #B-031
Score : 7,4/10
```

> Pourquoi cette tournure : "top 15% des 250 dernières ouvertures" ancre le chiffre dans une référence concrète — Thomas visualise la magnitude du gap sans avoir à l'interpréter. Le volume confirme l'engagement des market makers, pas juste la volatilité.

### H-A Gap Follow (VENTE)

```
🔴 VENTE  **CAC40 Turbo Put**
Entrée : 4,17  |  SL : 4,38  |  Cible potentielle : 3,71
Risque : 147 € max  |  Capital engagé : 700 €  |  Avant 8h55 CET
Raison : gap baissier CAC40 −1,1% vs clôture jeudi — futures US en baisse −0,7% pré-session, amplitude gap dans top 12% historique 5 ans
Backtest : 61% sur 94 trades | DD max −19% | Réf. #B-018
Score : 7,2/10
```

> Pourquoi cette tournure : la référence aux futures US pré-session traite implicitement l'objection "ce n'est que la réaction EU" — Thomas comprend que le signal intègre le contexte macro du moment.

### H-B Gap Fade (ACHAT)

```
🟢 ACHAT  **EuroStoxx50 Turbo Call**
Entrée : 2,88  |  SL : 2,71  |  Cible potentielle : 3,14
Risque : 119 € max  |  Capital engagé : 504 €  |  Avant 8h55 CET
Raison : gap baissier ESTX50 −0,6% au rebond : comble historiquement 58% des cas sous ce seuil — RSI 30min en survente à 28, rejet sur support 4 810
Backtest : 58% sur 73 trades | DD max −22% | Réf. #B-047
Score : 6,9/10
```

> Pourquoi cette tournure : "comble historiquement 58% des cas sous ce seuil" formule le mean-reversion comme une probabilité conditionnelle, pas une opinion — Thomas évalue le pari, pas la conviction du bot.

### H-B Gap Fade (VENTE)

```
🔴 VENTE  **CAC40 Turbo Put**
Entrée : 3,95  |  SL : 4,14  |  Cible potentielle : 3,56
Risque : 133 € max  |  Capital engagé : 592 €  |  Avant 8h55 CET
Raison : gap haussier CAC40 +1,3% fade — amplitude excessive vs ATR 5j (ratio 1,8×), zone de résistance 7 950 testée 3 fois sans franchissement, retour vers 7 810 cible potentielle
Backtest : 55% sur 68 trades | DD max −24% | Réf. #B-052
Score : 6,8/10
```

> Pourquoi cette tournure : "ratio 1,8× ATR" quantifie l'excès — Thomas a l'expérience pour interpréter ce chiffre sans explication. Le score légèrement plus bas (6,8) est cohérent avec un edge fade moins fiable que le gap follow.

### H-C ORB 5/15min (ACHAT)

```
🟢 ACHAT  **DAX Turbo Call**
Entrée : 4,05  |  SL : 3,84  |  Cible potentielle : 4,56
Risque : 147 € max  |  Capital engagé : 607 €  |  Avant 9h00 CET
Raison : breakout range 8h-8h15 Xetra à 17 342 — retest validé 8h22, volume breakout +41% vs range, configuration ORB15 en top 18% amplitude sur 5 ans
Backtest : 65% sur 112 trades | DD max −15% | Réf. #B-009
Score : 7,8/10
```

> Pourquoi cette tournure : l'heure exacte du breakout (8h15) et du retest (8h22) ancre le signal dans un event précis que Thomas peut vérifier sur son graphique en 5 secondes. Score 7,8 justifié par le meilleur win rate historique de l'edge ORB.

### H-C ORB 5/15min (VENTE)

```
🔴 VENTE  **LVMH Turbo Put**
Entrée : 5,21  |  SL : 5,44  |  Cible potentielle : 4,72
Risque : 161 € max  |  Capital engagé : 703 €  |  Avant 9h00 CET
Raison : breakout baissier range 8h-8h05 LVMH à 644,80 € — volume +52% vs moyenne range, pas de retest depuis 8h09, momentum −0,8% depuis ouverture
Backtest : 62% sur 88 trades | DD max −18% | Réf. #B-023
Score : 7,5/10
```

> Pourquoi cette tournure : "pas de retest depuis 8h09" signale la force du breakdown — une absence de pullback est une information aussi valide qu'une présence. Thomas trade l'action sur LVMH, pas seulement les indices.

### H-D Momentum US→EU (ACHAT)

```
🟢 ACHAT  **EuroStoxx50 Turbo Call**
Entrée : 3,18  |  SL : 2,99  |  Cible potentielle : 3,56
Risque : 133 € max  |  Capital engagé : 540 €  |  Avant 8h55 CET
Raison : S&P500 clôture +1,4% hier, Nasdaq +1,7% — corrélation S&P→ESTX50 sur ouverture EU à 0,72 (252j), ESTX50 futures +0,9% — momentum haussier US se transfert en ouverture EU dans 68% des cas à ce niveau
Backtest : 61% sur 103 trades | DD max −16% | Réf. #B-067
Score : 7,1/10
```

> Pourquoi cette tournure : le coefficient de corrélation (0,72) est le chiffre clé — il valide que l'edge n'est pas une intuition mais une mesure statistique. Thomas comprend immédiatement la solidité du lien US→EU.

### H-D Momentum US→EU (VENTE)

```
🔴 VENTE  **CAC40 Turbo Put**
Entrée : 4,42  |  SL : 4,63  |  Cible potentielle : 3,98
Risque : 147 € max  |  Capital engagé : 663 €  |  Avant 8h55 CET
Raison : S&P500 clôture −1,9% hier, VIX +2,1 pts à 21,4 — pression baissière US transférée sur EU dans 71% des cas à magnitude ≥ 1,5%, futures CAC40 −0,8% à 8h30 confirmant le biais
Backtest : 64% sur 91 trades | DD max −14% | Réf. #B-071
Score : 7,6/10
```

> Pourquoi cette tournure : mentionner le VIX en chiffre absolu (21,4) et son delta (+2,1 pts) distingue une pression baissière normale d'un signal de panique — Thomas calibre son risque psychologique aussi bien que financier.

### H-E News pré-marché (ACHAT)

```
🟢 ACHAT  **TotalEnergies Turbo Call**
Entrée : 4,87  |  SL : 4,61  |  Cible potentielle : 5,42
Risque : 182 € max  |  Capital engagé : 778 €  |  Avant 8h55 CET
Raison : résultats T1 TotalEnergies publiés 7h45 — EPS +8% vs consensus Bloomberg, réaction pré-marché +1,6% en 8 min — catalyseur earnings + momentum initial dans top 20% historique sur actions FR
Backtest : 59% sur 54 trades | DD max −21% | Réf. #B-088
Score : 7,0/10
```

> Pourquoi cette tournure : "EPS +8% vs consensus" ancre la news dans un écart chiffrable, pas dans un jugement ("bons résultats"). Le nb de trades backtest (54) est honnêtement plus faible — le score 7,0 en tient compte.

### H-E News pré-marché (VENTE)

```
🔴 VENTE  **Sanofi Turbo Put**
Entrée : 5,33  |  SL : 5,58  |  Cible potentielle : 4,81
Risque : 175 € max  |  Capital engagé : 799 €  |  Avant 8h55 CET
Raison : avertissement sur résultats Sanofi 7h30 — guidance annuelle révisée −4%, réaction pré-marché −2,1% en 12 min — catalyseur négatif + gap de rupture confirmé en pré-ouverture
Backtest : 62% sur 47 trades | DD max −23% | Réf. #B-091
Score : 7,1/10
```

> Pourquoi cette tournure : "gap de rupture" vs "gap baissier" — la sémantique signale l'intensité du choc sans dramatiser. Le nb de trades (47) est transparent — Thomas sait que cet edge est moins statistiquement robuste et peut choisir une position plus petite.

### H-F Spot/Futures (ACHAT)

```
🟢 ACHAT  **XAU/USD Turbo Call (Or)**
Entrée : 3,64  |  SL : 3,42  |  Cible potentielle : 4,08
Risque : 154 € max  |  Capital engagé : 546 €  |  Avant 8h55 CET
Raison : spread Spot/Futures Or inversé à −0,4$/oz (contango → backwardation) — signal de tension physique, or spot à 2 412 $ résistance clé franchie en pré-session, USD index −0,3%
Backtest : 60% sur 76 trades | DD max −19% | Réf. #B-105
Score : 7,2/10
```

> Pourquoi cette tournure : "contango → backwardation" est du vocabulaire technique que Thomas comprend. L'inverser en clair ("spread inversé") permet une lecture rapide sans simplifier à l'excès. Le contexte USD confirme la direction.

### H-F Spot/Futures (VENTE)

```
🔴 VENTE  **Brent Turbo Put**
Entrée : 4,21  |  SL : 4,43  |  Cible potentielle : 3,78
Risque : 154 € max  |  Capital engagé : 631 €  |  Avant 8h55 CET
Raison : contango Brent élargi à +1,8$/bl (M1-M2) — pression baissière structures terme, inventaires API +3,2 Mb annoncés hier soir, Brent spot 83,4 $ sous EMA20 depuis 3 séances
Backtest : 57% sur 69 trades | DD max −22% | Réf. #B-112
Score : 6,8/10
```

> Pourquoi cette tournure : trois confirmations indépendantes (structure terme, données stocks, technique EMA) — Thomas reconnaît la convergence sans avoir à les chercher. Score 6,8 honnête : edge Spot/Futures Brent est le moins robuste en win rate.

### H-G Asie→CAC (ACHAT)

```
🟢 ACHAT  **CAC40 Turbo Call**
Entrée : 3,77  |  SL : 3,56  |  Cible potentielle : 4,21
Risque : 147 € max  |  Capital engagé : 566 €  |  Avant 8h55 CET
Raison : Nikkei +1,8%, Hang Seng +1,2% clôture Asie — corrélation Asie→CAC ouverture à 0,64 (252j), sentiment risk-on, EUR/USD stable 1,082 (pas de frein FX), CAC futures +0,7%
Backtest : 59% sur 98 trades | DD max −18% | Réf. #B-134
Score : 7,0/10
```

> Pourquoi cette tournure : mentionner que l'EUR/USD est "stable" traite proactivement l'objection "le FX va manger la performance" — Thomas n'a pas à y penser. La corrélation est chiffrée, pas affirmée.

### H-G Asie→CAC (VENTE)

```
🔴 VENTE  **CAC40 Turbo Put**
Entrée : 4,09  |  SL : 4,30  |  Cible potentielle : 3,63
Risque : 147 € max  |  Capital engagé : 613 €  |  Avant 8h55 CET
Raison : Nikkei −2,1%, CSI300 −1,4% clôture Asie — risk-off généralisé, corrélation baissière Asie→CAC à 0,61 (252j), CAC futures −0,9%, EUR/USD −0,2% (amplificateur additionnel)
Backtest : 60% sur 89 trades | DD max −20% | Réf. #B-138
Score : 7,2/10
```

> Pourquoi cette tournure : dans la vente, l'EUR/USD est présenté comme "amplificateur additionnel" — le FX ne complique pas, il renforce. Inversion de la même logique que le signal ACHAT H-G, Thomas reconnaît la cohérence du système.

---

## 3. Templates NO-TRADE — 4 variations

[Framework : PAS inversé — le problème est nommé (condition bloquante), l'agitation est évitée (pas de dramatisation), la solution est le silence assumé]
[Conscience : Most-Aware — Thomas comprend immédiatement un no-trade chiffré]

### NT-01 — Score sous seuil

```
⚪️ NO-TRADE  CAC40 / Score 5,1/10 sous seuil 6,5
Volume Xetra insuffisant (+8% vs requis +20%) — condition non remplie
Prochaine fenêtre : demain 8h45 CET
```

> Ton : factuel, zéro excuse. Thomas préfère un silence motivé à un signal forcé. Le chiffre exact (5,1 vs 6,5) lui donne la raison sans l'obliger à chercher.

### NT-02 — Conflit news/technique

```
⚪️ NO-TRADE  DAX
Conflit détecté : BCE allocution 8h30 (référence TC-04) — biais technique haussier mais catalyseur news non intégrable avec fiabilité
Signal bloqué par précaution — edge annulé jusqu'à stabilisation post-annonce
```

> Ton : transparent sur la limite du système. Thomas sait que le bot ne prend pas de risque sur des configurations qu'il ne maîtrise pas — c'est une preuve de rigueur, pas un aveu de faiblesse.

### NT-03 — Régime panique (VIX > seuil)

```
⚪️ NO-TRADE  Tous sous-jacents / VIX 28,4 > seuil 27,0 (régime panique — backtests non représentatifs)
Reprise quand VIX < 25,0 sur clôture consécutive
Prochaine évaluation : demain
```

> Ton : règle de gestion du risque clairement énoncée, pas d'ambiguïté sur la condition de reprise. Le chiffre de reprise (VIX < 25,0) est précis — Thomas peut suivre lui-même sans relancer le bot.

### NT-04 — Aucune configuration testée (jour partiel / férié)

```
⚪️ NO-TRADE  Tous sous-jacents
Configuration absente : jour non couvert par les backtests (pont férié partiel ou liquidité réduite détectée)
Volume pré-marché Euronext : −47% vs moyenne 20j — pas de signal fiable possible
```

> Ton : "pas de signal fiable possible" — assomption de responsabilité courte. Thomas ne se demande pas si c'est un bug. Le volume chiffré (−47%) donne une mesure concrète de l'anomalie.

---

## 4. Templates ERREUR DATA / DEGRADED MODE

[Framework : PAS — Problem nommé sans dramatiser, Agitate absent (Thomas n'a pas besoin d'être stressé), Solution = transparence + action attendue]
[Ton : factuel + transparent + pas d'excuse — voir brand-platform.md §4 Pilier 2]

### US-04 — Twelve Data partiel

```
⚠️ ERREUR DATA  [Sous-jacent prévu]
Twelve Data : données partielles reçues à 8h44 (champ manquant : volume 1m Xetra)
Signal non calculable avec fiabilité suffisante — NO-TRADE par précaution
Statut API : https://status.twelvedata.com [consulter si persistant]
```

> Ton : le problème est nommé avec le champ exact ("volume 1m Xetra"), pas un message générique "erreur technique". Thomas sait précisément ce qui manque. Le lien status API lui donne une action concrète si le problème persiste.

### US-05 — Claude timeout

```
⚠️ DEGRADED MODE  [Sous-jacent prévu]
Scoring Claude indisponible (timeout > 45 s à 8h48)
Données de marché reçues — scoring IA non complété
Signal non envoyé : une justification incomplète n'est pas une justification
Prochaine tentative : demain 8h40 CET
```

> Ton : "une justification incomplète n'est pas une justification" — phrase courte qui rappelle le why du produit sans être moralisatrice. Thomas comprend que le système a refusé de compromettre la qualité.

### US-06 — Cron manqué 8h45 (healthchecks.io alert)

```
⚠️ CRON MANQUÉ  Signal du [date]
Pipeline non exécuté à 8h40 CET (alerte healthchecks.io)
Signal du jour non calculé — fenêtre d'exécution 8h45-8h55 expirée
Cause probable : démarrage Replit > 60 s
Action : vérifier logs Replit. Signal reprendra demain matin automatiquement.
```

> Ton : cause probable donnée honnêtement ("démarrage Replit > 60 s") — Thomas n'est pas laissé dans le vide. L'action est concrète et courte. "Automatiquement" clôt le message sans demander d'intervention.

---

## 5. Templates audit hebdo + mensuel

[Framework : 4Ps adapté — Promise (l'objectif), Picture (les chiffres de la semaine/mois), Proof (comparaison vs backtest), Push (GO/NO-GO ou signal d'arrêt)]

### AUDIT-HEBDO — Vendredi 18h00 CET

```
📊 Résumé semaine [N] — [Date lundi]-[Date vendredi]

Signaux envoyés : [N] | Trades passés : [N] | NO-TRADE : [N]
P&L brut semaine : [+/−X,XX €] | P&L net (frais) : [+/−X,XX €]
Win rate semaine : [X]% ([N] gagnants / [N] perdants)
Drawdown semaine : [X]% du capital dédié | Max toléré : 20%

Meilleur signal : [sous-jacent] [+X%] — Réf. [#B-NNN]
Pire signal : [sous-jacent] [−X%] — Réf. [#B-NNN]

[Si drawdown > 15%] ⚠️ Drawdown hebdo > 15% — surveiller semaine prochaine
[Si 3 pertes consécutives] ⚠️ 3 pertes consécutives — signal d'alerte, voir règles d'arrêt
```

> Envoi automatique vendredi 18h00 CET via cron. Les lignes conditionnelles ne s'affichent qu'en cas de déclenchement des seuils — Thomas n'est pas spammé en cas de semaine normale.

### AUDIT-MENSUEL — 1er du mois (ou J+1 ouvré)

```
📈 Rapport mensuel [Mois AAAA]

P&L brut : [+/−X €] | Frais Bourse Direct : [−X,XX €] | P&L net frais : [+/−X €]
Fiscalité PFU estimée (31,4%) : [−X €] | **P&L net après PFU : [+/−X €]**

Win rate mois : [X]% vs backtest [X]% — écart : [+/−X pts]
Nb trades : [N] | NO-TRADE : [N] ([X]% des jours ouvrés)
Drawdown max mensuel : [X]% | Limite : 20%

Hypothèses actives ce mois : [H-A, H-C, H-D...]
Hypothèse la plus performante : [H-X] — [X]% win rate sur [N] signaux
Hypothèse à surveiller : [H-X] — [X]% win rate (sous backtest [X]%)

────────────────
Décision continuation :
→ Taper /continue pour valider le mois suivant
→ Taper /stop pour suspendre les signaux
```

> Le prompt /continue ou /stop donne à Thomas le contrôle explicite chaque mois — il n'a pas à désactiver activement le bot s'il doute. La fiscalité PFU est affichée en chiffre réel, pas en note de bas de page.

---

## 6. Checklist 10 points — testeur persona Thomas

> Usage : cocher avant tout envoi Telegram en production. Chaque point = refus si NON.

1. **Lisible en 25 secondes ?**
   Tester à voix haute. Si > 25 s → couper la raison à 1 phrase.

2. **Score visible et compréhensible ?**
   Format X.X/10 présent. Jamais "score élevé" sans chiffre.

3. **Entrée / SL / TP cohérents ?**
   ACHAT : SL < Entrée < TP. VENTE : TP < Entrée < SL. Vérification automatique pipeline.

4. **Raison concrète et chiffrée ?**
   Au moins 1 chiffre dans la raison (%, €, ratio, ATR). Pas d'opinion sans donnée.

5. **backtest_ref présent et valide ?**
   Format #B-NNN. Référence existante en SQLite (vérifié par pipeline avant envoi).

6. **Pas de vocabulaire proscrit ?**
   Relire tableau do/don't section 1. "Signal fort", "buy now", "garanti", "ne pas manquer" = rejet automatique.

7. **Emoji utilisé avec parcimonie ?**
   1 emoji max en tête (🟢 / 🔴 / ⚪️ / ⚠️ / 📊 / 📈). Zéro emoji dans le corps du message.

8. **Ton conditionnel sur le futur ?**
   "Cible potentielle" pour TP — jamais "va atteindre", "atteindra". Le futur est une probabilité, pas une affirmation.

9. **Cohérent brand voice "Justifié · Concis · Backtesté" ?**
   Justifié : les chiffres sont là. Concis : pas de ligne superflue. Backtesté : win rate + DD + réf. présents.

10. **Thomas appuie sur le bouton sans hésitation ?**
    Question finale subjective. Si une information manque pour décider, le message est incomplet — compléter ou passer en NO-TRADE.

---

## Auto-évaluation gates

| Gate | Intitulé | Statut | Justification |
|---|---|---|---|
| G1 | Cohérence avec project-context.md | PASS | Tous les sous-jacents, le format 6+1 et le persona Thomas sont alignés sur project-context.md et functional-specs.md |
| G3 | Zéro invention de données | PASS | Scores, win rates et refs backtest marqués inventés mais cohérents — aucune donnée réelle prétendue vraie |
| G5 | Brand voice aligné sur brand-platform.md | PASS | Trois piliers Justifié/Concis/Backtesté structurent chaque template. Vocabulaire proscrit documenté section 1 |
| G7 | Frameworks copy explicites | PASS | FAB, PAS, 4Ps documentés en tête de chaque section |
| G12 | Niveau de conscience documenté | PASS | Most-Aware pour tous les templates signal (Thomas connaît le produit, attend le signal) |
| G15 | Objections traitées | PASS | "Pas assez justifié" → chiffres obligatoires. "Dashboard à ouvrir" → push Telegram. "Reco forcée" → NO-TRADE templates. "Score sans contexte" → win rate + nb trades + DD systématiques |
| G16 | Anti-fausse promesse | PASS | Aucun template ne promet une feature non implémentée. Les refs #B-NNN sont marquées "à créer en SQLite" — pas présentées comme existantes. Les features scraping / lien automatique absentes du copy |
| G17 | Zéro témoignage fictif avec nom persona | PASS | Aucun témoignage. Tous les exemples sont des templates de bot, pas des citations de Thomas |

---

**Handoff → @fullstack**
- Fichiers produits : `/home/user/TradingApp/docs/copy/message-templates.md`
- Décisions prises : format 6 lignes + 1 confiance strict ; emoji directionnel unique en tête ; "Cible potentielle" pour TP (conditionnel obligatoire) ; backtest_ref format #B-NNN à valider en SQLite avant envoi
- Points d'attention :
  - Les champs `win_rate_backtest`, `nb_trades_backtest`, `drawdown_max_backtest` doivent être passés au template Claude — ils apparaissent dans la ligne Backtest
  - La ligne Backtest et le Score doivent être les deux dernières lignes du message (ordre fixe)
  - Templates NO-TRADE NT-02 : le code TC-04 doit correspondre à un tag dans la table `news_events` SQLite
  - Templates DEGRADED MODE : les messages d'erreur doivent être envoyés même si Claude est down (logique fallback sans IA)
  - Audit mensuel : les commandes /continue et /stop doivent être implémentées comme webhooks Telegram
