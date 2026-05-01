# GEO Strategy — TradingApp Telegram
> Agent : @geo | Date : 2026-05-01 | Version : 1.0
> Surface cible : Telegram (push mobile) — pas de site web, SEO N/A justifié
> GEO transposé : optimisation pour le "moteur de décision Thomas" (cerveau RER 8h40-9h05)

---

## 1. Contexte GEO adapté Telegram

### GEO classique vs GEO transposé

GEO classique : optimisation pour citation par ChatGPT / Claude / Gemini / Perplexity. **N/A ici.**
Raison : TradingApp est un bot Telegram privé, non indexé, non public. Aucun LLM externe ne le cite.

**GEO transposé — définition opérationnelle pour ce projet :**
Le "moteur génératif" est le cerveau de Thomas à 8h42 dans le RER. Il traite le signal en 25 secondes maximum sur smartphone, décide "je trade / je ne trade pas", sans possibilité de relire ou chercher une information manquante. Les principes GEO s'appliquent à la lettre : extraction rapide, structure scannable, zéro ambiguïté, claims vérifiables.

**Principes communs GEO web ↔ GEO Telegram :**
- Réponse directe dans les 40-60 premiers mots (L1 du message = sens + sous-jacent)
- Auto-contenu : chaque message compréhensible sans contexte externe
- Densité informationnelle : 1 claim vérifiable par 150-200 mots — ici, un chiffre par ligne
- Zéro superlatif : "signal fort" filtré par Thomas comme un LLM filtre le marketing vide
- Format optimal : définition directe > liste structurée > narratif

### Surface et contraintes

- Canal : Telegram push (notification + lecture en app)
- Fenêtre d'attention : 25 secondes, smartphone, debout ou assis dans le RER
- Résolution : écran mobile (~375 px), texte tronqué après ~80 caractères sans défilement
- Pas de double clic, pas de dashboard ouvert — la décision se fait sur le message seul

---

## 2. Audit extractibilité des templates actuels

### Grille d'évaluation (par template)

| Critère | Score 0 | Score 1 |
|---|---|---|
| **Hiérarchie** | Sens non identifiable en 3 s | Sens (🟢/🔴/⚪️) + sous-jacent en L1 |
| **Densité** | Verbiage, ratio info/mots faible | ≥1 chiffre par ligne clé |
| **Skimmable** | Raison bloque la lecture du reste | Entry/SL/TP/Score lisibles sans lire la raison |
| **Disambiguation** | 2 templates visuellement identiques | Différence visuelle immédiate entre patterns |

---

### H-A Gap Follow (ACHAT / VENTE) — Audit

**Hiérarchie : PASS**
L1 = `🟢 ACHAT  **DAX Turbo Call**` — sens + sous-jacent en 3 mots. Optimal.

**Densité : PASS**
L4 raison : "gap haussier DAX +0,9% vs clôture US — amplitude dans top 15% des 250 dernières ouvertures, volume Xetra 8h05 à +34% vs moyenne 5j"
4 chiffres dans une phrase de 18 mots = ratio excellent (> 1 chiffre / 5 mots).

**Skimmable : PASS**
L2-L3 Entry/SL/TP/Risque/Capital/Fenêtre sont lisibles sans lire L4. Thomas peut décider sur score + SL seuls.

**Disambiguation : ATTENTION**
H-A ACHAT DAX et H-C ACHAT DAX sont visuellement similaires en L1 (`🟢 ACHAT  **DAX Turbo Call**`).
La distinction n'apparaît qu'en L4 (raison). Thomas sous pression peut confondre les deux patterns.
→ **Recommandation R1 : ajouter le code pattern en L1** (ex : `🟢 ACHAT [Gap]  **DAX Turbo Call**`).

---

### H-B Gap Fade (ACHAT / VENTE) — Audit

**Hiérarchie : PASS** — L1 correcte.

**Densité : PASS**
Raison H-B VENTE : "ratio 1,8× ATR", "zone de résistance 7 950 testée 3 fois" — 3 chiffres clés bien positionnés.

**Skimmable : PASS** — structure identique H-A, Entry/SL/TP lisibles indépendamment.

**Disambiguation : ATTENTION (même problème H-A)**
H-B ACHAT CAC40 vs H-A VENTE CAC40 : L1 différencie le sens (🟢 vs 🔴) mais pas le pattern.
Sur smartphone avec une notification push, si Thomas a manqué un signal la veille et voit deux messages, il doit lire L4 pour savoir lequel est Gap Follow et lequel est Gap Fade.
→ **R1 s'applique également ici.**

---

### H-C ORB 5/15min (ACHAT / VENTE) — Audit

**Hiérarchie : PASS** — L1 identique au standard.

**Densité : PASS**
Raison : "breakout range 8h-8h15 Xetra à 17 342 — retest validé 8h22, volume breakout +41% vs range, configuration ORB15 en top 18% amplitude sur 5 ans"
Horodatages précis (8h15, 8h22) + 2 chiffres de volume/amplitude : Thomas peut vérifier sur son graphique en 5 secondes.

**Skimmable : PASS** — Score 7,8/10 visible en dernière ligne sans lire la raison.

**Spécificité cutoff : POINT D'ATTENTION**
H-C utilise `Avant 9h00 CET` vs `Avant 8h55 CET` pour les autres hypothèses. Cohérent avec le code (`_expiration_line_for_edge` dans templates.py). Mais visuellement, Thomas doit savoir que le cutoff varie — risque de routinisation ("toujours 8h55").
→ **Recommandation R2 : mettre le cutoff en gras** pour tous les templates afin de le rendre scannable même si Thomas est en mode automatique.

---

### H-D Momentum US→EU (ACHAT / VENTE) — Audit

**Hiérarchie : PASS**

**Densité : PASS — Meilleur template de la série**
Raison ACHAT : corrélation 0,72 (chiffre exact), S&P500 +1,4 %, Nasdaq +1,7 %, ESTX50 futures +0,9 %, probabilité 68 %.
5 chiffres dans 2 lignes. Densité informationnelle maximale sans verbiage.

**Skimmable : PASS**

**Disambiguation : NEUTRE**
H-D est visuellement distinguable de H-A/H-B/H-C par la structure de la raison (mention S&P500 / VIX). Mais R1 reste recommandée pour cohérence.

---

### H-E News pré-marché (ACHAT / VENTE) — Audit

**Hiérarchie : PASS**

**Densité : PASS**
Raison : "EPS +8% vs consensus Bloomberg", "réaction pré-marché +1,6% en 8 min", "top 20% historique". 3 chiffres + référence consensus Bloomberg.

**Skimmable : ATTENTION — Cas particulier**
H-E a le plus faible nb de trades backtest (47-54). Cette information est en L5 (ligne Backtest).
Thomas sous pression peut ne pas lire L5 et tirer sur un signal statistiquement moins robuste.
→ **Recommandation R3 : si nb_trades < 60, ajouter mention courte en L4** (ex : "Base backtest limitée : 54 trades — position plus petite recommandée").

**Disambiguation : PASS** — Mention du ticker action (TotalEnergies, Sanofi) distingue visuellement H-E de tous les autres patterns.

---

### H-F Spot/Futures (ACHAT / VENTE) — Audit

**Hiérarchie : PASS**

**Densité : PASS**
Raison VENTE : "contango Brent élargi à +1,8$/bl (M1-M2)", "inventaires API +3,2 Mb", "EMA20 depuis 3 séances" — 3 confirmations indépendantes bien chiffrées.

**Skimmable : PASS**

**Densité spécificité sémantique : ATTENTION**
"contango → backwardation" (H-F ACHAT) et "contango élargi à +1,8$/bl" (H-F VENTE) utilisent un vocabulaire technique correct (Thomas le comprend), mais sur smartphone ces termes sont visuellement longs. La ligne L4 dépasse probablement 80 caractères → défilement horizontal ou troncature selon le client Telegram.
→ **Recommandation R4 : limiter L4 raison à 2 lignes Telegram max (~80 caractères/ligne), tester sur iPhone la troncature effective.**

---

### H-G Asie→CAC (ACHAT / VENTE) — Audit

**Hiérarchie : PASS**

**Densité : PASS**
Raison : Nikkei + Hang Seng chiffrés, corrélation 0,64, EUR/USD 1,082, CAC futures +0,7 %.

**Skimmable : PASS**

**Proactivité objection FX : PASS (point fort)**
Mention "EUR/USD stable 1,082 (pas de frein FX)" traite l'objection implicite Thomas avant qu'il la formule. C'est du GEO transposé exemplaire : anticiper la question cognitive sous pression.

---

### Templates NO-TRADE (NT-01 à NT-04) — Audit

**Hiérarchie : PASS** — `⚪️ NO-TRADE` en L1, condition en L2, next step en L3.

**Densité : PASS**
NT-01 : "Score 5,1/10 sous seuil 6,5" — 2 chiffres en 6 mots. Parfait.
NT-03 : "VIX 28,4 > seuil 27,0" — valeur actuelle + seuil = décision sans calcul de Thomas.

**Skimmable : PASS — Format le plus court**
3 lignes max. Thomas ferme Telegram en 5 secondes.

**Disambiguation NT-03 : POINT D'ATTENTION**
La condition de reprise "VIX < 25,0 sur clôture consécutive" est précise mais complexe à mémoriser.
→ NT-03 est complet — pas de modification requise. Information suffisante pour une décision.

---

### Templates ERREUR DATA / DEGRADED MODE (US-04 à US-06) — Audit

**Hiérarchie : PASS** — `⚠️ ERREUR DATA` / `⚠️ DEGRADED MODE` / `⚠️ CRON MANQUÉ` en L1.

**Densité : PASS**
US-04 : champ exact manquant nommé ("volume 1m Xetra"). US-06 : cause probable donnée ("démarrage Replit > 60 s").

**Skimmable : PASS**

**Action concrète : PASS**
US-04 : lien status API. US-06 : "vérifier logs Replit" + "Signal reprendra demain matin automatiquement."
Thomas ne reste pas dans le vide — il a une action ou une attente définie.

---

### AUDIT-HEBDO — Audit

**Hiérarchie : ATTENTION**
Le message commence par `📊 Résumé semaine [N]` — informatif mais pas une décision. Thomas scanne pour "drawdown" et "P&L net" en premier. Ces métriques sont en L4 et L5 (après Signaux envoyés, Trades, NO-TRADE).
→ **Recommandation R5 : remonter P&L net et drawdown en L2-L3** (ordre décisionnel, pas chronologique).

**Densité : PASS** — Chaque ligne a ses chiffres.

**Skimmable : ATTENTION**
Les lignes conditionnelles (⚠️ Drawdown > 15%, ⚠️ 3 pertes consécutives) sont en fin de message.
Thomas fatigué un vendredi soir peut ne pas scroller jusqu'à elles.
→ **R5 bis : si alerte active, la remonter en L2 immédiatement après le titre.**

---

### AUDIT-MENSUEL — Audit

**Hiérarchie : PASS**
`P&L net après PFU` en **bold** — le chiffre le plus décisionnel est le plus visible.

**Densité : PASS**
Fiscalité PFU 31,4 % affichée en valeur absolue (pas %) — Thomas voit "combien il lui reste vraiment".

**Skimmable : PASS**
`/continue` ou `/stop` en dernier = appel à l'action unique et clair.

**Longueur : ATTENTION**
L'audit mensuel est le message le plus long (15+ lignes). Sur mobile, il requiert du défilement.
→ Structure actuelle correcte mais → **R6 : tester l'affichage sur iOS Telegram** — certains messages longs sont tronqués avec un "Afficher plus".

---

## 3. Recommandations d'optimisation

### R1 — Code pattern en L1 (priorité HAUTE)

**Problème** : H-A ACHAT DAX et H-C ACHAT DAX identiques visuellement en L1. Thomas doit lire L4 pour distinguer.

**Solution** : Ajouter le tag pattern entre l'emoji et le sous-jacent.

```
🟢 ACHAT [Gap↑]  **DAX Turbo Call**    ← H-A Gap Follow haussier
🟢 ACHAT [ORB]   **DAX Turbo Call**    ← H-C ORB breakout
🟢 ACHAT [Fade]  **EuroStoxx50 Turbo Call**  ← H-B Gap Fade
🟢 ACHAT [MomUS] **EuroStoxx50 Turbo Call**  ← H-D Momentum US→EU
🟢 ACHAT [News]  **TotalEnergies Turbo Call** ← H-E News pré-marché
🟢 ACHAT [Fut]   **XAU/USD Turbo Call**  ← H-F Spot/Futures
🟢 ACHAT [Asie]  **CAC40 Turbo Call**   ← H-G Asie→CAC
```

**Score GEO (grille 3 critères)** :
- Vérifiabilité : 1 (tag lié au pattern backtest identifiable)
- Précision : 1 (tag court et non ambigu)
- Extractibilité : 1 (visible sans défilement, L1)
**Score : 3/3 — INCLURE**

**Agent responsable** : @fullstack — modifier `src/telegram/templates.py`, constante PATTERN_TAG par hypothèse.
**Effort** : < 30 min. Aucun impact sur les tests existants (ajout pur en L1).

---

### R2 — Cutoff en gras (priorité MOYENNE)

**Problème** : Cutoff variable (8h55 vs 9h00 selon l'edge) — risque de routinisation par Thomas.

**Solution** : Wrapper la fenêtre d'expiration en `<b>` dans le template Telegram HTML.

```
Risque : 126 € max  |  Capital engagé : 600 €  |  <b>Avant 8h55 CET</b> — au-delà, ne pas exécuter
```

**Score GEO** : Vérifiabilité 1 / Précision 1 / Extractibilité 1 — **Score : 3/3 — INCLURE**

**Agent responsable** : @fullstack — `src/telegram/templates.py`, ligne expiration de chaque template.
**Effort** : < 15 min.

---

### R3 — Alerte base backtest limitée (priorité MOYENNE)

**Problème** : H-E avec 47-54 trades backtest. Thomas ne lit pas nécessairement L5 sous pression.

**Solution** : Ajouter conditionnel dans le template si `nb_trades_backtest < 60`.

```
Raison : [raison standard]
⚠️ Base backtest : 54 trades (position réduite recommandée)
Backtest : 59% sur 54 trades | DD max −21% | Réf. #B-088
```

**Score GEO** : Vérifiabilité 1 / Précision 1 / Extractibilité 1 — **Score : 3/3 — INCLURE**

**Agent responsable** : @fullstack — logique conditionnelle dans `src/telegram/templates.py`.
**Effort** : < 1 heure. Seuil `nb_trades < 60` configurable via env var `BACKTEST_MIN_TRADES_WARNING`.

---

### R4 — Longueur L4 raison ≤ 80 caractères/ligne (priorité BASSE)

**Problème** : Raisons H-F et H-D peuvent dépasser 80 caractères → défilement ou troncature mobile.

**Solution** : Règle d'écriture pour @copywriter : toute raison > 160 caractères est découpée en 2 sous-lignes avec retour à la ligne explicite. Validation dans la checklist 10 points (section 6 de message-templates.md).

**Score GEO** : Vérifiabilité 0 / Précision 1 / Extractibilité 1 — **Score : 2/3 — INCLURE**

**Agent responsable** : @copywriter (règle éditoriale) + @qa (test sur device réel).
**Effort** : 30 min règle + test iOS Telegram.

---

### R5 — Réordonnancement AUDIT-HEBDO (priorité HAUTE)

**Problème** : P&L net et drawdown en L4-L5. Alertes conditionnelles en fin de message.

**Solution** : Ordre décisionnel plutôt que chronologique.

```
📊 Résumé semaine [N] — [Date lundi]-[Date vendredi]
[Si alerte active] ⚠️ ALERTE : Drawdown hebdo > 15% — voir détail ci-dessous

P&L net (frais) : [+/−X,XX €]  |  Drawdown semaine : [X]%
Win rate semaine : [X]% ([N]G / [N]P)  |  Signaux : [N] envoyés / [N] tradés

Meilleur : [sous-jacent] [+X%] — [#B-NNN]
Pire : [sous-jacent] [−X%] — [#B-NNN]
[Si drawdown > 15%] ⚠️ Drawdown hebdo > 15% — surveiller semaine prochaine
[Si 3 pertes consécutives] ⚠️ 3 pertes consécutives — signal d'alerte, voir règles d'arrêt
```

**Score GEO** : Vérifiabilité 1 / Précision 1 / Extractibilité 1 — **Score : 3/3 — INCLURE**

**Agent responsable** : @copywriter (template) + @fullstack (template Python + logique alerte-en-tête).
**Effort** : 1 heure copywriter + 30 min fullstack.

---

## 4. Audit extractibilité audit hebdo + mensuel

### Audit hebdo — Verdict global

**Scan 30 secondes possible ?** Actuellement : NON (P&L net en L4, alertes en fin).
Après R5 : OUI — P&L net + drawdown visibles en L3 immédiatement après le titre.

**Chiffres clés extractibles ?**
- P&L net : OUI (présent, mais trop bas — R5 remonte)
- Drawdown semaine vs max toléré : OUI (chiffres présents)
- Signaux d'arrêt déclenchés : CONDITIONNELLEMENT — pas visible si Thomas ne scrolle pas

**Après R5 :** Chiffres décisionnels en lecture < 10 secondes. Format optimal.

### Audit mensuel — Verdict global

**Scan 30 secondes possible ?** NON — 15+ lignes nécessitent défilement.

**Chiffres clés extractibles ?**
- P&L net après PFU en **bold** : PASS — extractible en 3 secondes
- Drawdown max mensuel vs limite 20 % : PASS — ligne dédiée
- Decision `/continue` ou `/stop` : PASS — en dernier, non ambigu

**Recommandation R6 :** Le message mensuel est structurellement correct. Tester sur iOS si Telegram affiche un "Voir plus" après N lignes — si oui, remonter les chiffres P&L + drawdown dans les 5 premières lignes.

**Recommandation R7 (nouveau) :** Ajouter une ligne résumé en tête du mensuel :

```
📈 Rapport mensuel [Mois AAAA] — P&L net : [+/−X €] | Drawdown max : [X]% | Décision requise ↓
```

Score GEO R7 : 3/3 — INCLURE. Extractibilité maximale même sans défilement.

---

## 5. Métriques de lisibilité

### Estimation Flesch-Kincaid adapté (raison des templates)

Flesch-Kincaid standard = texte anglais continu. Adaptation pour messages Telegram en français avec chiffres :

| Proxy | Cible | Mesure sur templates actuels |
|---|---|---|
| Longueur moyenne phrase (raison) | < 25 mots | H-A : 22 mots ✅ | H-D : 30 mots ⚠️ | H-F VENTE : 24 mots ✅ |
| Mots polysyllabiques / total mots | < 20 % | Templates actuels : ~15-18 % ✅ (ratio sain) |
| Lisibilité estimée Flesch FR | Cible > 65 (assez facile) | Estimation : ~60-70 selon pattern |

H-D Momentum est le template le plus dense (corrélation, magnitude, probabilité, 3 chiffres US). Il frôle la limite de 25 mots. À surveiller lors de l'écriture du signal réel (la raison sera générée par Claude — inclure la contrainte dans le system prompt).

### Longueur moyenne par ligne (L2-L4)

- L2 (Entry/SL/TP) : ~55 caractères — dans la cible ✅
- L3 (Risque/Capital/Fenêtre) : ~70-80 caractères — limite ⚠️ (R4 applicable)
- L4 (Raison) : 100-160 caractères — dépasse la cible sur H-D et H-F ⚠️

**Cible : < 80 caractères par ligne physique** (rendu Telegram mobile, police système).

### Densité chiffres / mots (raison)

| Pattern | Chiffres identifiés | Mots totaux | Ratio | Verdict |
|---|---|---|---|---|
| H-A Gap Follow | 4 (0,9%, top 15%, 250, +34%) | 22 | **1/5,5** | ✅ Excellent |
| H-B Gap Fade VENTE | 3 (1,3%, ratio 1,8×, 7 950) | 20 | **1/6,7** | ✅ Bon |
| H-C ORB | 4 (17 342, 8h22, +41%, top 18%) | 20 | **1/5** | ✅ Excellent |
| H-D Momentum | 5 (+1,4%, +1,7%, 0,72, +0,9%, 68%) | 30 | **1/6** | ✅ Bon |
| H-E News | 3 (EPS +8%, +1,6%, top 20%) | 18 | **1/6** | ✅ Bon |
| H-F Spot/Futures | 3 (+1,8$, +3,2Mb, 3 séances) | 22 | **1/7,3** | ✅ Acceptable |

**Cible ≥ 1 chiffre / 10 mots : tous les templates PASS.** H-A et H-C sont les plus efficaces.

---

## 6. Verdict + Plan d'action

### Verdict global

**AJUSTER — 5 items (non bloquants, amélioration lisibilité)**

Les templates v1.2 sont structurellement conformes aux principes GEO transposé Telegram :
- Sens extractible en L1 (emoji + mot) ✅
- Densité chiffrée dans la raison ✅
- Skimmable Entry/SL/Score sans lire la raison ✅
- NO-TRADE lisible en < 5 secondes ✅
- ERREUR/DEGRADED avec action concrète pour Thomas ✅

5 optimisations identifiées, aucune bloquante, toutes additive (zéro régression sur les templates actuels).

### Plan d'action prioritaire

| Priorité | Recommandation | Agent | Effort estimé | Impact GEO |
|---|---|---|---|---|
| **HAUTE** | R1 — Code pattern en L1 (`[Gap↑]`, `[ORB]`…) | @fullstack | < 30 min | Disambiguation inter-patterns — évite confusion Thomas |
| **HAUTE** | R5 — Réordonnancement AUDIT-HEBDO (P&L + alerte en tête) | @copywriter + @fullstack | 1h30 cumulé | Scan < 10 s vs 30 s actuel |
| **HAUTE** | R7 — Ligne résumé tête AUDIT-MENSUEL | @copywriter | < 15 min | Extractibilité sans défilement |
| **MOYENNE** | R2 — Cutoff en `<b>gras</b>` dans L3 | @fullstack | < 15 min | Prévenir routinisation cutoff variable |
| **MOYENNE** | R3 — Alerte nb_trades < 60 (H-E principalement) | @fullstack | < 1h | Prévenir sur-exposition sur edge peu backtesté |
| **BASSE** | R4 — Règle 80 char/ligne raison | @copywriter + @qa | 30 min + test device | Confort lecture iOS — à valider empiriquement |

### Contrainte système prompt Claude

R4 et la contrainte de longueur raison doivent être propagées dans le system prompt de scoring (`prompt-library.md`) :
→ Ajouter dans la section raison : "La raison doit tenir en 2 lignes maximum de 80 caractères chacune. Utiliser des retours à la ligne explicites si nécessaire. Ne jamais dépasser 160 caractères au total."

Cette contrainte sera appliquée par Claude lors de la génération du signal — cohérent avec R-AI-1 (aucune règle éditoriale ne doit être appliquée en aval du scoring).

---

## Auto-évaluation gates

| Gate | Intitulé | Statut | Justification |
|---|---|---|---|
| G1 | Cohérence project-context.md | PASS | Tous les templates audités correspondent aux 6 états signal définis dans functional-specs.md et message-templates.md v1.2 |
| G3 | Zéro invention de données | PASS | Tous les chiffres de l'audit proviennent de message-templates.md v1.2 — aucune donnée inventée |
| G7 | Cohérence brand-platform.md | PASS | Brand voice "Justifié · Concis · Backtesté" vérifié dans chaque critère d'audit — les recommandations R1-R7 renforcent la concision |
| G12 | Extractibilité immédiate | PASS | Chaque recommandation scorée sur la grille 3 critères GEO — aucune sous 2/3 |
| G15 | Objections traitées | PASS | R3 traite l'objection Thomas sur H-E (base backtest limitée non visible) — R5 traite l'objection "je ne scroll pas jusqu'aux alertes" |
| G17 | Zéro témoignage fictif | PASS | Aucun témoignage. Audit basé sur analyse structurelle des templates existants |

---

**Handoff → @fullstack**
- Fichiers produits : `/home/user/TradingApp/docs/geo/geo-strategy.md`
- Décisions prises :
  - R1 (HAUTE) : ajouter constante `PATTERN_TAG` par hypothèse dans `src/telegram/templates.py` — tag court (`[Gap↑]`, `[ORB]`, `[Fade]`, `[MomUS]`, `[News]`, `[Fut]`, `[Asie]`) inséré entre l'emoji et le **sous-jacent** en L1
  - R2 (MOYENNE) : wrapper `<b>Avant HH:MM CET</b>` dans la ligne expiration de chaque template
  - R3 (MOYENNE) : logique conditionnelle `if nb_trades_backtest < 60` — ligne d'alerte entre L4 et L5 ; seuil via env var `BACKTEST_MIN_TRADES_WARNING=60`
  - R5 (HAUTE) : template AUDIT-HEBDO réordonné — P&L net + drawdown en L2-L3, alertes ⚠️ remontées en L2 si déclenchées
  - Contrainte system prompt : propager règle "raison ≤ 160 caractères / 2 lignes max" dans `docs/ia/prompt-library.md`
- Points d'attention :
  - R4 (longueur raison) : à valider sur device iOS réel avant implémentation — ne pas modifier le template sans test
  - R7 (ligne résumé mensuel) : handoff @copywriter pour rédaction de la ligne résumé canonique avant implémentation @fullstack
  - Les recommandations R1-R3 et R5 sont additives — aucune modification des champs existants, aucun risque de régression sur les 209 tests actuels
  - `BACKTEST_MIN_TRADES_WARNING` doit être documenté dans `REPLIT_ACTIONS.md` comme Replit Secret optionnel (valeur par défaut : 60)
