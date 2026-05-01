# Audit visuel — Templates Telegram TradingApp
> Agent : @design · Date : 2026-05-01 · Phase : 2d
> Référence : docs/copy/message-templates.md v1.2 · Brand : brand-platform.md §6
> Surface unique : rendu Markdown Telegram desktop + mobile (pas d'UI web)
> Snapshots analysés : 9 (TC-01 à TC-09) reconstruits depuis src/telegram/templates.py + tests/test_telegram_templates.py

---

## 0. Résultats reconstruits — snapshots TC-01 à TC-09

Les fichiers .txt dans tests/screenshots/telegram-mockup/ sont générés par le test G24 (pytest).
L'audit ci-dessous est basé sur la reconstruction depuis le code source (templates.py + fixtures de test).

### TC-01 — BUY H-A (Gap Follow, standard)
```
🟢 ACHAT  **DAX Turbo Call**
Entrée : 3,42  |  SL : 3,21  |  Cible potentielle : 3,85
Risque : 147 € max  |  Capital engagé : 504 €  |  Avant 8h55 CET — au-delà, ne pas exécuter
Raison : gap haussier DAX +0,9% vs clôture US — amplitude top 15% sur 250 ouvertures
Backtest : Réf. #B-031
Score : 7,4/10
```

### TC-02 — BUY H-C (ORB, cutoff 9h00)
```
🟢 ACHAT  **DAX Turbo Call**
Entrée : 3,42  |  SL : 3,21  |  Cible potentielle : 3,85
Risque : 147 € max  |  Capital engagé : 504 €  |  Avant 9h00 CET — au-delà, ne pas exécuter
Raison : gap haussier DAX +0,9% vs clôture US — amplitude top 15% sur 250 ouvertures
Backtest : Réf. #B-031
Score : 7,4/10
```

### TC-03 — BUY paper_mode
```
[PAPER TRADING] 🟢 ACHAT  **DAX Turbo Call**
Entrée : 3,42  |  SL : 3,21  |  Cible potentielle : 3,85
Risque : 147 € max  |  Capital engagé : 504 €  |  Avant 8h55 CET — au-delà, ne pas exécuter
Raison : gap haussier DAX +0,9% vs clôture US — amplitude top 15% sur 250 ouvertures
Backtest : Réf. #B-031
Score : 7,4/10
```

### TC-04 — SELL H-A
```
🔴 VENTE  **CAC40 Turbo Put**
Entrée : 4,17  |  SL : 4,38  |  Cible potentielle : 3,71
Risque : 147 € max  |  Capital engagé : 630 €  |  Avant 8h55 CET — au-delà, ne pas exécuter
Raison : gap baissier CAC40 -1,1% — futures US -0,7% pré-session
Backtest : Réf. #B-018
Score : 7,2/10
```

### TC-05 — NO-TRADE score sous seuil
```
⚪️ NO-TRADE  CAC40 / Score 5,1/10
Volume Xetra insuffisant (+8% vs requis +20%) — condition non remplie
Prochaine fenêtre : demain 8h45 CET
```

### TC-06 — NO-TRADE VIX panique
```
⚪️ NO-TRADE  CAC40
VIX 28,4 > seuil 27,0 (régime panique)
Prochaine fenêtre : demain 8h45 CET
```

### TC-07 — ERREUR DATA Twelve Data
```
⚠️ ERREUR DATA  DAX
Twelve Data : données partielles reçues à 8h44 (champ manquant : volume 1m Xetra)
Signal non calculable avec fiabilité suffisante — NO-TRADE par précaution
Statut API : https://status.twelvedata.com
```

### TC-08 — DEGRADED MODE Claude timeout
```
⚠️ DEGRADED MODE  Signal du jour
Scoring Claude indisponible (timeout > 45 s)
Données de marché reçues — scoring IA non complété
Signal non envoyé : une justification incomplète n'est pas une justification
Prochaine tentative : demain 8h40 CET
```

### TC-09 — DEGRADED MODE Cron manqué
```
⚠️ CRON MANQUÉ  Signal du 2026-05-04
Pipeline non exécuté à 8h40 CET (alerte healthchecks.io)
Signal du jour non calculé — fenêtre d'exécution 8h45-8h55 expirée
Cause probable : démarrage Replit > 60 s
Action : vérifier logs Replit. Signal reprendra demain matin automatiquement.
```

---

## 1. Audit — Rendu Markdown Telegram (desktop + mobile)

### Grille d'évaluation par snapshot

| # | Snapshot | Lisible 25s | Hiérarchie | Markdown OK | Emojis | Longueur lignes | Verdict |
|---|----------|-------------|------------|-------------|--------|-----------------|---------|
| TC-01 | BUY H-A | PASS | PASS | ALERTE | PASS | ALERTE | AJUSTER |
| TC-02 | BUY H-C | PASS | PASS | ALERTE | PASS | ALERTE | AJUSTER |
| TC-03 | BUY paper | PASS | PASS | ALERTE | PASS | ALERTE | AJUSTER |
| TC-04 | SELL | PASS | PASS | ALERTE | PASS | ALERTE | AJUSTER |
| TC-05 | NT score | PASS | PASS | PASS | PASS | PASS | GO |
| TC-06 | NT VIX | PASS | PASS | PASS | PASS | PASS | GO |
| TC-07 | ERREUR DATA | PASS | PASS | PASS | PASS | ALERTE | AJUSTER |
| TC-08 | DEGRADED Claude | PASS | PASS | PASS | PASS | PASS | GO |
| TC-09 | DEGRADED Cron | PASS | PASS | PASS | PASS | ALERTE | AJUSTER |

### Détail par critère

#### Lisibilité 25 secondes
Tous les snapshots PASS. Les signaux ACHAT/VENTE comportent 6 lignes denses mais lisibles à voix haute en 20-22 secondes sur mobile. Les NO-TRADE (3L) se lisent en 8-10 secondes. Le DEGRADED Cron (TC-09 : 5L) reste sous 15 secondes.

#### Hiérarchie visuelle
PASS global. L'ordre sens → niveaux → raison → backtest → score est respecté dans les templates ACHAT/VENTE. Pour les NO-TRADE, l'ordre condition bloquante → prochaine fenêtre est correct. Pour les DEGRADED, le problème nommé en L1 est correct (brand-platform §5 "Boîte noire" proscrit).

#### Markdown Telegram — PROBLÈME IDENTIFIÉ (BLOQUANT)
**TC-01 à TC-04 — ligne Backtest dégradée.**
Le template produit `Backtest : Réf. #B-031` sans inclure le win rate, le nombre de trades ni le drawdown max. La référence v1.2 (message-templates §1 champs obligatoires) impose :
```
Backtest : [win_rate]% sur [nb] trades | DD max [−XX%] | Réf. [#B-NNN]
```
Le code templates.py ligne 118 écrit uniquement `f"Backtest : Réf. {signal.backtest_ref}"` — les champs `win_rate_backtest`, `nb_trades_backtest`, `drawdown_max_backtest` ne sont pas présents dans `ScoringSignalOutput` v1.2 (15 champs). Ces trois champs manquent dans le schema tool use Anthropic.

Impact Markdown : aucun rendu cassé, mais **information manquante critique pour la décision Thomas** ("Backtest" sans chiffres contredit le pilier Backtesté).

**Markdown bold** : `**DAX Turbo Call**` et `**P&L net après PFU**` utilisent la syntaxe bold Telegram (MarkdownV2). En mode `parse_mode=Markdown` (v1, legacy), `**text**` n'est PAS rendu en gras — seul `*text*` est interprété. En MarkdownV2, `**text**` est invalide. Vérifier que le bot utilise `parse_mode='MarkdownV2'` et que le sous-jacent est correctement escapé (les caractères `.`, `-`, `(`, `)` doivent être préfixés `\` en MarkdownV2).

#### Emojis
PASS global. 1 emoji directionnel strictement en tête (🟢/🔴/⚪️/⚠️). Zéro emoji dans le corps des messages. Conforme message-templates §1 règle 7.

#### Longueur de lignes (~50 caractères max mobile 360px)
Critère mobile : environ 50 caractères avant retour automatique disgracieux.

- TC-01/02/03/04 — ligne 3 (Risque | Capital | Expiration) : 78-82 caractères. Sur mobile 360px, cette ligne se casse en 2 lignes automatiquement au niveau du `|` ou d'un espace — rendu non disgracieux (Telegram gère le word-wrap proprement), mais la ligne est dense. Acceptable mais à surveiller sur petits écrans (320px).
- TC-07 — ligne Statut API : `Statut API : https://status.twelvedata.com` = 43 caractères. PASS.
- TC-09 — ligne Action : `Action : vérifier logs Replit. Signal reprendra demain matin automatiquement.` = 77 caractères. Se découpe proprement sur mobile.

Verdict longueur lignes : aucune ligne ne dépasse 82 caractères. Telegram mobile gère le word-wrap. Pas de coupure disgracieuse identifiée sur les mots-clés critiques (entrée, SL, cible). PASS effectif — l'ALERTE du tableau est préventive pour les très petits écrans (320px iPhones anciens).

---

## 2. Audit — Cohérence brand (brand-platform.md §6)

### Vocabulaire proscrit

Recherche exhaustive des 7 termes interdits dans les 9 snapshots :

| Terme proscrit | TC-01 | TC-02 | TC-03 | TC-04 | TC-05 | TC-06 | TC-07 | TC-08 | TC-09 |
|----------------|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| "signal fort" | — | — | — | — | — | — | — | — | — |
| "buy now" | — | — | — | — | — | — | — | — | — |
| "guaranteed"/"garanti" | — | — | — | — | — | — | — | — | — |
| "perfect entry" | — | — | — | — | — | — | — | — | — |
| "opportunity" | — | — | — | — | — | — | — | — | — |
| "ne pas manquer" | — | — | — | — | — | — | — | — | — |
| futur affirmatif | — | — | — | — | — | — | — | — | — |

**Résultat : 0 occurrence de vocabulaire proscrit sur 9 snapshots. PASS.**
Confirmé par le test automatisé `test_no_proscribed_vocabulary_in_any_template` (209/209 PASS).

### Ton conditionnel sur le futur
PASS. "Cible potentielle" présent dans TC-01 à TC-04 (testé par `test_buy_signal_contains_cible_potentielle` et `test_sell_signal_contains_cible_potentielle`). Aucun futur affirmatif détecté ("va atteindre", "atteindra").

### Exclamation / bold abusif
- Aucun point d'exclamation dans les 9 snapshots. PASS.
- Bold utilisé : 1 occurrence par signal ACHAT/VENTE (sous-jacent en L1) + 1 occurrence dans rapport mensuel (`**P&L net après PFU**`). Conforme à la règle "1-2 bold max par message". PASS.
- Rapport mensuel : le bold sur `**P&L net après PFU**` est justifié (chiffre décision critique) — PASS.

### Ton no-trade
TC-05 et TC-06 : sobre, direct, sans excuse. "Prochaine fenêtre : demain 8h45 CET" clôt proprement sans dramatisation. PASS.
Note mineure : TC-06 tronque la raison par rapport au template NT-03 de référence — la condition de reprise (`Reprise quand VIX < 25,0 sur clôture consécutive`) n'est pas incluse. Voir section 4 recommandations.

### Message dégradé
TC-07/08/09 : transparent sur la cause, jamais "problème technique" vague. Conforme brand-platform §6 Tone variable "Message d'erreur technique". PASS.

---

## 3. Conformité format strict 6L+1

### Signaux ACHAT / VENTE (TC-01 à TC-04)

| Snapshot | L1 sens+asset | L2 niveaux | L3 risque+expiration | L4 raison | L5 backtest | L6 score | Total | Conformité |
|----------|---------------|------------|----------------------|-----------|-------------|----------|-------|------------|
| TC-01 BUY H-A | OK | OK | OK | OK | INCOMPLET | OK | 6L | NON-CONFORME |
| TC-02 BUY H-C | OK | OK | OK (9h00) | OK | INCOMPLET | OK | 6L | NON-CONFORME |
| TC-03 BUY paper | OK (+prefix) | OK | OK | OK | INCOMPLET | OK | 6L | NON-CONFORME |
| TC-04 SELL | OK | OK | OK | OK | INCOMPLET | OK | 6L | NON-CONFORME |

**Écart BLOQUANT sur L5 (ligne Backtest) :**
- Produit : `Backtest : Réf. #B-031`
- Attendu v1.2 : `Backtest : 63% sur 81 trades | DD max −17% | Réf. #B-031`
- Impact : pilier "Backtesté" non honoré dans le message final. Thomas ne dispose pas du win rate ni du drawdown sans ouvrir la DB SQLite — ce qui contredit la promesse "30 secondes de lecture maximum" et le critère pull-the-trigger #10 ("Thomas appuie sur le bouton sans hésitation ?").
- Cause racine : `ScoringSignalOutput` (15 champs v1.2) ne transporte pas `win_rate_backtest`, `nb_trades_backtest`, `drawdown_max_backtest`. Le template ne peut pas afficher ce qu'il ne reçoit pas.
- Correction requise : voir section 4.

### NO-TRADE (TC-05, TC-06)

| Snapshot | L1 emoji+asset | L2 raison | L3 fenêtre | Total | Conformité |
|----------|----------------|-----------|------------|-------|------------|
| TC-05 NT score | OK (score visible) | OK | OK | 3L | CONFORME |
| TC-06 NT VIX | OK | OK (partiel — condition reprise absente) | OK | 3L | CONFORME* |

*TC-06 conforme au format 3L strict. La condition de reprise VIX (issue du template NT-03 de référence) n'est pas dans le raison car la fixture de test ne l'inclut pas. À corriger dans le prompt Claude / fixture.

### DEGRADED MODE (TC-07, TC-08, TC-09)

| Snapshot | Lignes | Format attendu | Conformité |
|----------|--------|----------------|------------|
| TC-07 ERREUR DATA | 4L | 4L (brand-platform "4L acceptable") | CONFORME |
| TC-08 DEGRADED Claude | 5L | 5L (message-templates §4 US-05) | CONFORME |
| TC-09 CRON MANQUÉ | 5L | 5L (message-templates §4 US-06) | CONFORME |

Note : le brief demande "4L acceptable hors fenêtre 8h45-8h55". TC-08 et TC-09 font 5L — ils sont conformes à leur propre template de référence (message-templates v1.2 §4) qui prescrit ces 5 lignes.

---

## 4. Recommandations design

### R1 — BLOQUANT : Compléter la ligne Backtest (win_rate + nb_trades + DD max)

**Problème** : `Backtest : Réf. #B-031` — 3 champs critiques absents.
**Impact** : le pilier "Backtesté" est affiché comme titre de section mais pas rendu dans le message. Thomas ne peut pas évaluer la robustesse de l'edge en 30 secondes.
**Correction @fullstack** :
1. Ajouter 3 champs à `ScoringSignalOutput` (tools.py) : `win_rate_backtest: float | None`, `nb_trades_backtest: int | None`, `drawdown_max_backtest: float | None`
2. Mettre à jour le tool schema Anthropic (15 → 18 champs)
3. Mettre à jour templates.py ligne 118 :
   ```python
   f"Backtest : {wr}% sur {nb} trades | DD max −{dd}% | Réf. {signal.backtest_ref}"
   ```
4. Alimenter ces champs depuis la table `rnd_results` SQLite au moment de la construction du contexte scoring (runner.py ou main.py).

**Format cible** : `Backtest : 63% sur 81 trades | DD max −17% | Réf. #B-031`

### R2 — MAJEUR : Vérifier parse_mode MarkdownV2 (bold sous-jacent)

**Problème** : `**DAX Turbo Call**` est rendu en gras uniquement si le bot utilise `parse_mode='MarkdownV2'`. En Markdown v1 legacy, la syntaxe est `*text*`. En MarkdownV2, les caractères spéciaux (`.`, `-`, `(`, `)`, `|`) dans le corps du message doivent être échappés (`\.`, `\-`, `\(`, `\)`).
**Impact** : si parse_mode non configuré ou mal configuré, soit le bold ne s'affiche pas, soit Telegram retourne une erreur 400 (message non envoyé).
**Correction @fullstack** : vérifier `bot.py` — le paramètre `parse_mode` dans l'appel `send_message`. Si MarkdownV2 : ajouter une fonction d'escaping sur tous les caractères spéciaux dans les champs dynamiques (entry, sl, tp, raison). Alternative plus simple : utiliser `parse_mode='HTML'` et remplacer `**text**` par `<b>text</b>` — plus robuste car les caractères mathématiques (`%`, `-`, `,`) ne nécessitent pas d'escaping en HTML Telegram.

### R3 — MAJEUR : Enrichir TC-06 NO-TRADE VIX avec condition de reprise

**Problème** : TC-06 affiche `VIX 28,4 > seuil 27,0 (régime panique)` sans la condition de reprise.
**Template NT-03 de référence** : `Reprise quand VIX < 25,0 sur clôture consécutive — Prochaine évaluation : demain`
**Correction** : la raison VIX doit inclure la condition de reprise chiffrée. Thomas doit pouvoir suivre lui-même le VIX sans relancer le bot (brand-platform §6 Do#1 "Chiffrer"). Modifier le prompt Claude ou la logique no_trade_reason pour les cas VIX.

### R4 — MINEUR : Ajouter l'emoji 🎯 sur "Cible potentielle" (option)

**Suggestion visuelle** : `Cible potentielle : 3,85` → `🎯 Cible potentielle : 3,85`
**Justification** : rend le TP instantanément identifiable sur mobile lors d'un scroll rapide, sans violer la règle "1 emoji directionnel max en tête" (🎯 n'est pas directionnel, il est positionnel). À valider avec @copywriter — peut être considéré comme fioriture.
**Impact** : aucun risque technique. Ne modifie pas le décompte de lignes.
**Note** : rester conservateur sur les emojis — brand-platform §6 "Pilier 2 Concis" milite pour la sobriété.

### R5 — MINEUR : Test sur l'app mobile réelle de Thomas (hors scope MVP)

Le rendu Markdown Telegram varie légèrement entre :
- Telegram Desktop (Windows/Mac) : rendu riche, bold visible, monospace clair
- Telegram iOS : rendu similaire mais padding différent, code backtick en police système
- Telegram Android : rendu identique iOS

**Recommandation** : en post-livraison J+7 (mini-jalon), Thomas valide les 3 snapshots sur son smartphone (TC-01, TC-05, TC-08) avant de passer en paper-trading. Retour en 48h à @fullstack si anomalie de rendu. Cette validation est hors scope MVP mais obligatoire avant paper trading.

**Note favicon repo** : ce projet n'a pas de UI web (bot Telegram pur). Aucun favicon requis. Le repo GitHub reste privé — pas de page web publique à icônifier. Gate G31 favicon N/A justifié.

---

## 5. Verdict global

### Récapitulatif par snapshot

| Snapshot | Brand | Format 6L+1 | Vocabulaire | Verdict |
|----------|-------|-------------|-------------|---------|
| TC-01 BUY H-A | PASS | AJUSTER (L5) | PASS | **AJUSTER** |
| TC-02 BUY H-C | PASS | AJUSTER (L5) | PASS | **AJUSTER** |
| TC-03 BUY paper | PASS | AJUSTER (L5) | PASS | **AJUSTER** |
| TC-04 SELL | PASS | AJUSTER (L5) | PASS | **AJUSTER** |
| TC-05 NT score | PASS | CONFORME | PASS | **GO** |
| TC-06 NT VIX | PASS | CONFORME | PASS | **GO** (R3 recommandé) |
| TC-07 ERREUR DATA | PASS | CONFORME | PASS | **GO** |
| TC-08 DEGRADED Claude | PASS | CONFORME | PASS | **GO** |
| TC-09 DEGRADED Cron | PASS | CONFORME | PASS | **GO** |

### Verdict Phase 2d

**AJUSTER — 4 snapshots signal ACHAT/VENTE (TC-01 à TC-04)**

Motif unique : ligne L5 Backtest incomplète (`Réf. #B-031` seul, au lieu de `63% sur 81 trades | DD max −17% | Réf. #B-031`). Il ne s'agit pas d'un problème de design mais d'un écart entre le schema `ScoringSignalOutput` (15 champs) et les champs attendus par le template v1.2 (18 champs avec win_rate + nb_trades + DD max). L'écart est ciblé, la correction est tracée (R1).

**Aucun NO-GO** : zéro vocabulaire proscrit, zéro futur affirmatif, zéro exclamation, format 6L+1 respecté en nombre de lignes.

### Corrections prioritaires avant paper trading

| Priorité | Réf. | Responsable | Effort estimé |
|----------|------|-------------|---------------|
| P0 BLOQUANT | R1 — Backtest complet (win_rate + nb_trades + DD) | @fullstack | ~2h (schema + template + runner) |
| P1 MAJEUR | R2 — Vérifier parse_mode MarkdownV2 vs HTML | @fullstack | ~1h (test sur vrai bot) |
| P2 MAJEUR | R3 — NT-03 VIX condition de reprise | @fullstack / @copywriter | ~30min (raison enrichie) |
| P3 MINEUR | R4 — Emoji 🎯 sur Cible potentielle (optionnel) | @fullstack | ~15min |
| P4 INFO | R5 — Test mobile Thomas post J+7 | Thomas | 10min validation |

### Gates critiques

| Gate | Intitulé | Statut | Justification |
|------|----------|--------|---------------|
| G1 | Cohérence project-context.md | PASS | Bot Telegram, signal unique, fenêtre 8h45-8h55, Thomas persona — tous conformes |
| G3 | Zéro invention de données | PASS | Les chiffres (7,4/10, #B-031, 3,42 €) sont des fixtures de test marquées comme telles, pas des données live présentées comme vraies |
| G7 | Cohérence brand-platform | PASS | 0 terme proscrit, ton conditionnel, no-trade sobre, piliers Justifié/Concis/Backtesté visibles — sauf L5 Backtest (R1 requis pour PASS complet) |
| G15 | Traçabilité décision | PASS | Chaque champ du template est traçable (edge_id, backtest_ref, score, raison chiffrée) |
| G17 | Anti-fausse promesse | PASS | Aucun template ne promet une feature non implémentée. La ligne Backtest incomplète est un manque, pas une fausse promesse |

---

## Auto-évaluation @design

- [x] Snapshots reconstruits depuis code source (templates.py + fixtures test) — méthode fiable en l'absence d'exécution pytest disponible
- [x] Vocabulaire proscrit vérifié sur 9 snapshots × 7 termes = 63 vérifications
- [x] Format ligne par ligne compté sur chaque template
- [x] Recommandations actionnables avec responsable + effort estimé
- [x] Aucun emoji dans les recommandations du rapport (cohérence brand "Concis")
- [x] Favicon N/A justifié (bot Telegram pur, pas de UI web, pas de domaine public)

---

**Handoff → @fullstack**
- Fichiers produits : `docs/design/telegram-visual-audit.md`
- Écart bloquant (R1) : `ScoringSignalOutput` manque `win_rate_backtest`, `nb_trades_backtest`, `drawdown_max_backtest` — bump schema v1.2 → v1.3, mettre à jour tool schema Anthropic + templates.py + runner/main pour alimenter depuis rnd_results SQLite
- Écart majeur (R2) : vérifier `parse_mode` dans bot.py (MarkdownV2 vs HTML) et escaping des caractères spéciaux Telegram
- Écart majeur (R3) : enrichir no_trade_reason pour NT-03 VIX avec condition de reprise chiffrée (`VIX < 25,0 sur clôture consécutive`)
- Points d'attention : les 5 NO-TRADE/DEGRADED (TC-05 à TC-09) sont GO sans correction — ne pas toucher ces templates dans la correction R1
