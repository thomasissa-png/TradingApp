<!-- Version: 2026-05-01T00:00 — @ux — Création initiale user-flows Phase 1 TradingApp -->

# User Flows — TradingApp

> **Résumé exécutif**
> - **Objectif** : Cartographier exhaustivement les 5 flows du parcours Thomas — journée GO trade, journée NO-TRADE, mode dégradé, audit hebdomadaire vendredi soir, décision mensuelle GO/NO-GO continuer.
> - **Décisions clés** : Aucun écran web — tout passe par Telegram (push + commandes) + Bourse Direct mobile + journal SQLite. Chaque étape est justifiée par JTBD personas.md. Les frictions P0 bloquent l'exécution et sont résolues au niveau produit.
> - **Dépendances** : personas.md (journée 8h40-9h05, scénario 4 mai 2026, signaux d'arrêt), functional-specs.md (8 US, 5 templates, US-08 /trade), brand-platform.md (Voice & Tone, 5 do's / don'ts), kpi-framework.md (signaux d'arrêt SQLite triggers).

---

## Touchpoints — Vue d'ensemble

| Canal | Rôle | Sens |
|---|---|---|
| **Telegram (push automatique)** | Signal quotidien 8h45-8h55, résumé hebdo vendredi 18h, rapport mensuel 1er du mois | Bot → Thomas |
| **Telegram (commande manuelle)** | /trade (logger P&L), /journal-week (audit hebdo), /continue ou /stop (décision mensuelle) | Thomas → Bot |
| **Bourse Direct mobile** | Recherche turbo, passage ordre limite, pose SL/TP, confirmation exécution | Thomas actif |
| **Journal SQLite** | Persistance de tous les événements — jamais accédé directement par Thomas en V1 | Interne pipeline |

**Hors périmètre UX** : aucun dashboard web, aucune interface React, aucune notification email. Le canal Telegram est irremplaçable (frustration 2 personas.md : "il faut que ça vienne à moi").

---

## Flow 1 — Journée type ouvrée GO trade

> **Métrique HEART primaire** : Task success — Thomas exécute un ordre dans la fenêtre 8h45-8h55 sans friction bloquante.
> **Scénario de référence** : lundi 4 mai 2026, RER, 8h42 CET (personas.md scénario daté).

### Étape 0 — Déclenchement pipeline (8h40 CET, invisible pour Thomas)

- **Durée** : 0 s côté Thomas (cron Replit automatique)
- **Action pipeline** : Cron Replit déclenche le pipeline. Vérification jour ouvré EU + non-férié FR (US-03). Si férié → arrêt silencieux (aucun message). Sinon : appel Twelve Data (données intraday DAX, CAC40, etc.), backtester calcule les scores par sous-jacent, appel Claude Sonnet pour scoring multi-dimension + génération justification structurée JSON 15 champs (US-01).
- **Output Telegram** : aucun encore — pipeline en cours.
- **Friction potentielle** : Twelve Data timeout OU Claude timeout → branch vers Flow 3.
- **Mitigation produit** : circuit breaker 2 retries Twelve Data (US-04), 1 retry Claude (US-05), cutoff 8h55 strict (US-06).

---

### Étape 1 — Réception notification Telegram (8h45-8h55 CET)

- **Durée** : instantané — notification push Telegram sur écran de verrouillage
- **Action Thomas** : Thomas est dans le RER (8h42 personas.md). Il voit la notification arriver. Il ne la lit pas encore — il est peut-être debout, téléphone en poche.
- **Output Telegram** : notification système iOS/Android avec prévisualisation partielle du message (2-3 premières lignes visibles sur l'écran de verrouillage).
- **Friction potentielle F1** : la notification est silencieuse ou masquée par une autre app. Thomas rate la fenêtre 8h45-8h55.
  - **Sévérité** : P1
  - **Mitigation** : documentation de configuration (activer notifications Telegram avec prévisualisation, channel dédié TradingApp). Hors scope produit — à documenter dans le runbook Thomas.
- **Friction potentielle F2** : prévisualisation trop courte — Thomas ne sait pas si c'est un GO ou un NO-TRADE sans ouvrir l'app.
  - **Sévérité** : P2
  - **Mitigation** : première ligne du message TOUJOURS "ACHAT — [sous-jacent]" ou "Pas de trade aujourd'hui." — visible sans déverrouiller (brand-platform templates).

---

### Étape 2 — Lecture du signal Telegram (8h45-8h48, ~25 secondes)

- **Durée** : 25 secondes selon scénario personas.md
- **Action Thomas** : Thomas déverrouille, ouvre Telegram conversation TradingApp, lit le message de haut en bas.
- **Output Telegram affiché (template ACHAT, exemple 4 mai 2026)** :

```
ACHAT — DAX Turbo Call
Entrée : 3,42 € | SL : 3,21 € | Cible potentielle : 3,85 €
Gap haussier +0,8 % sur clôture US + ORB haussier 5 premières min Xetra
Score 7,1/10 confirmé par momentum > seuil backtest
Réf. backtest #B-031 — win rate 61 % / 87 trades / drawdown max −18 %
Risque max : 126 € sur 600 € engagés (levier ~6)
Score : 7,1/10 | Fenêtre : avant 8h55 CET
```

- **Décision mentale Thomas** : score 7,1 > 6,5 ✓ / SL présent ✓ / risque 126 € acceptable ✓ / backtest #B-031 présent ✓ → GO. La décision est prise en < 30 s (JTBD 1 critère de succès).
- **Friction potentielle F3** : message tronqué sur mobile (Telegram coupe les longs messages). Score et fenêtre en dernière ligne pourraient être hors viewport.
  - **Sévérité** : P1
  - **Mitigation** : template limité à 8 lignes max (functional-specs §2, règle template ACHAT). Score et fenêtre en ligne 7-8 — visible sans scroll sur iPhone 12 et supérieur (viewport Telegram ≈ 10-12 lignes).
- **Friction potentielle F4** : Thomas ne se souvient pas du backtest #B-031.
  - **Sévérité** : P2
  - **Mitigation** : le message inclut win rate + nb trades + drawdown max du backtest — Thomas n'a pas besoin de se souvenir, les chiffres sont là (JTBD 2 critère de succès : "ne ressent pas le besoin de vérifier ailleurs").

---

### Cognitive walkthrough — Étape 2

| Question | Réponse | Verdict |
|---|---|---|
| Thomas sait-il quoi faire ? | Oui — "ACHAT — DAX Turbo Call" = décision immédiate | PASS |
| L'action est-elle visible ? | Oui — message visible dans Telegram, notification push reçue | PASS |
| Le lien but-action est-il clair ? | Oui — score > seuil + SL + risque → signal complet | PASS |
| Le feedback est-il immédiat ? | Oui — Thomas lit en 25 s, décide mentalement, passe à l'étape suivante | PASS |

---

### Étape 3 — Ouverture Bourse Direct mobile + recherche turbo (8h48-8h50, ~2 min)

- **Durée** : 2 minutes estimées (personas.md : 8h45-8h50 "cherche le turbo correspondant")
- **Action Thomas** : ferme Telegram, ouvre app Bourse Direct, onglet recherche turbos, tape "DAX Call", filtre par delta ~0,5, vérifie le spread affiché (< 0,05 € nominal).
- **Output Bourse Direct** : liste de turbos DAX Call avec prix bid/ask, delta, barrière knock-out.
- **Friction potentielle F5** : Thomas ne trouve pas le bon turbo rapidement (mauvais delta, spread trop large, barrière trop proche).
  - **Sévérité** : P1
  - **Mitigation** : le signal précise le sous-jacent exact (DAX Turbo Call) et le capital engagé (~600 €) — Thomas peut déduire le nombre de turbos et la fourchette de prix. [HYPOTHÈSE : mentionner le type de turbo (call/put) dans le message est suffisant. Si Thomas demande plus de précision sur le turbo exact, envisager d'ajouter delta indicatif dans le message — à valider en R&D.]
- **Friction potentielle F6** : le cours d'entrée indiqué (3,42 €) a bougé depuis le calcul (8h40-8h45).
  - **Sévérité** : P1
  - **Mitigation** : niveau d'entrée = prix indicatif, ordre limite posé à ce niveau ou légèrement au-dessus (Thomas le sait en tant que trader expérimenté). Le message utilise "Entrée : X €" sans garantir l'exécution exacte à ce prix — cohérent avec le conditionnel d'incertitude brand-platform.

---

### Étape 4 — Passage ordre limite + pose SL/TP (8h50-8h54, ~4 min)

- **Durée** : 4 minutes estimées (personas.md : 8h50-8h55 "passe l'ordre")
- **Action Thomas** : saisit ordre d'achat limite (600 € / prix du turbo = nb turbos), pose SL à 3,21 € et TP à 3,85 € sur Bourse Direct mobile.
- **Output Bourse Direct** : confirmation ordre envoyé / en attente d'exécution.
- **Friction potentielle F7** : calcul mental nb turbos (600 € / 3,42 € = 175 turbos ~). Thomas doit faire le calcul lui-même.
  - **Sévérité** : P2
  - **Mitigation** : le message affiche déjà "capital engagé : 600 €" — Thomas fait le calcul une fois. En V1.1, envisager d'ajouter "nb turbos indicatif : 175" dans le message pour éviter l'erreur d'arrondi.
- **Friction potentielle F8** : Thomas pose SL/TP dans le mauvais ordre (TP d'abord, puis SL) et rate la fenêtre.
  - **Sévérité** : P2
  - **Mitigation** : hors scope produit (interface Bourse Direct). Thomas est trader expérimenté — SL/TP simultanés sont un geste habituel.

---

### Étape 5 — Confirmation exécution + remise en poche (8h54, ~30 s)

- **Durée** : 30 secondes
- **Action Thomas** : notification Bourse Direct "ordre exécuté" ou "ordre accepté". Thomas referme l'app. Remet téléphone en poche. Continue son trajet.
- **Output** : notification Bourse Direct push. Téléphone en poche. Thomas n'est plus disponible pour ajuster.
- **Friction potentielle F9** : ordre non exécuté immédiatement (marché peu liquide, prix s'est éloigné).
  - **Sévérité** : P1
  - **Mitigation** : sous-jacents V1 = indices EU liquides (DAX, CAC40) — spread et liquidité vérifiés en R&D. Si ordre non exécuté à 8h55, Thomas annule. Le SL/TP n'est posé qu'après exécution confirmée — Thomas le sait.

---

### Étape 6 — Arrivée bureau, pas de gestion (9h05 CET)

- **Durée** : N/A
- **Action Thomas** : arrivée bureau, reprend activité principale. SL/TP posés = position gérée automatiquement par Bourse Direct. Pas de monitoring intraday (décision structurante project-context.md #1, hors scope functional-specs §5).
- **Output** : aucun. Telegram silencieux jusqu'à 10h-12h.
- **Friction potentielle** : aucune — c'est précisément l'objectif du bot (JTBD 1 : Thomas ne gère pas sa position).

---

### Étape 7 — Clôture position SL ou TP touché (10h-12h CET)

- **Durée** : N/A — notification push Bourse Direct
- **Action Thomas** : notification Bourse Direct "ordre SL exécuté" ou "TP atteint".
- **Output Bourse Direct** : push notification avec prix de sortie et P&L brut indicatif.
- **Friction potentielle** : aucune côté produit TradingApp.

---

### Étape 8 — Log du trade via /trade (soir ou lendemain matin)

- **Durée** : 30 secondes
- **Action Thomas** : ouvre Telegram, envoie `/trade 2026-05-04 +258 MAE=-50 MFE=+265 trade=true`
- **Output Telegram (US-08)** :

```
Journal mis à jour pour le 4 mai.
P&L brut : +258 €
Frais Bourse Direct : −1,98 €
P&L net (après PFU 31,4 %) : +176 €
```

- **Friction potentielle F10** : Thomas oublie de logger le trade. Le journal reste incomplet.
  - **Sévérité** : P1
  - **Mitigation** : en V1.1, le bot rappelle automatiquement à 18h30 CET les jours où un signal GO a été envoyé mais où /trade n'a pas été reçu. ("Pas de log pour le signal du matin — envoie /trade [date] [résultat] quand tu as le résultat.")
- **Friction potentielle F11** : format de commande /trade difficile à mémoriser.
  - **Sévérité** : P2
  - **Mitigation** : si Thomas envoie "/trade" sans paramètres, le bot répond avec le format d'aide : "Usage : /trade YYYY-MM-DD [+/-PL] MAE=[val] MFE=[val] trade=[true/false]".

---

### Audit heuristique Nielsen — Flow 1

| # | Heuristique | Verdict | Évidence |
|---|---|---|---|
| H1 | Visibilité état système | PASS | Pipeline visible via Telegram (message reçu = pipeline OK), Bourse Direct (confirmation ordre) |
| H2 | Correspondance monde réel | PASS | Vocabulaire prescrit brand-platform : "entrée", "SL", "TP", "risque max" — vocabulaire trader Thomas |
| H3 | Contrôle et liberté | PASS | Thomas peut ne pas trader (signal informatif, pas prescriptif). Peut annuler ordre sur Bourse Direct. |
| H4 | Cohérence et standards | PASS | Template ACHAT identique à chaque signal — Thomas sait exactement où trouver chaque info |
| H5 | Prévention des erreurs | PASS | Cutoff 8h55 affiché dans le message ("Fenêtre : avant 8h55 CET") — Thomas ne peut pas ignorer |
| H6 | Reconnaissance plutôt que rappel | PASS | Toutes les infos sont dans le message — win rate, drawdown max, risque max. Pas de mémoire requise |
| H7 | Flexibilité et efficacité | PASS | Thomas expert : message dense et actionnable en 25 s. Pas de wizard, pas de confirmation inutile |
| H8 | Design minimaliste | PASS | 7-8 lignes, zéro ligne de remplissage (brand-platform Pilier 2 : "concis par discipline") |
| H9 | Aide correction erreurs | PASS | /trade sans paramètre → aide format. SL invalide → signal bloqué (US-01 cas d'erreur) |
| H10 | Aide et documentation | PASS | Chaque message auto-documenté (backtest_ref, win_rate, fenêtre) — pas d'aide externe requise |

---

## Flow 2 — Journée NO-TRADE

> **Métrique HEART primaire** : Task success — Thomas reçoit le message, ferme Telegram, ne cherche pas d'alternative. Durée du flow côté Thomas : < 30 s.

### Étape 1 — Réception message NO-TRADE (8h45-8h55 CET)

- **Durée** : 10 secondes de lecture
- **Action Thomas** : ouvre Telegram, lit le message.
- **Output Telegram (template NO-TRADE)** :

```
Pas de trade aujourd'hui.
Score max relevé : 5,1/10 — en dessous du seuil 6,5.
Prochaine fenêtre : demain 8h45.
```

- **Décision mentale Thomas** : seuil non atteint. Pas de recherche alternative (JTBD 3 : "ferme Telegram sans chercher un trade de remplacement").

---

### Étape 2 — Fermeture Telegram (8h46 CET)

- **Durée** : instantané
- **Action Thomas** : referme Telegram. Reprend son activité ou son trajet.
- **Output** : aucun. Journée trading terminée pour Thomas.

---

### Friction et mitigation — Flow 2

**Friction F12** : Thomas pourrait douter ("dommage, j'aurais bien tradé le DAX ce matin — le marché semble monter").
- **Sévérité** : P1 (risque comportemental — Thomas trade manuellement au feeling)
- **Mitigation** : le message NO-TRADE donne le score max relevé (5,1/10) et le seuil (6,5). Thomas peut comparer objectivement. Pas de commentaire éditorial ("marché hésitant", "peut-être demain") — le factuel seul (brand-platform don't n°1). L'absence de signal n'est pas un aveu d'échec (brand-platform pilier "Backtesté" + R2 functional-specs : "décision valide documentée").

**Friction F13** : vendredi, Thomas ne sait pas si le bot reprend lundi.
- **Sévérité** : P2
- **Mitigation** : "Prochaine fenêtre : lundi 8h45" calculé dynamiquement (US-02 critère d'acceptance : vendredi → "lundi 8h45").

---

### Cognitive walkthrough — Flow 2

| Question | Réponse | Verdict |
|---|---|---|
| Thomas sait-il quoi faire ? | Oui — "Pas de trade aujourd'hui" = décision explicite | PASS |
| L'action est-elle visible ? | Oui — message court, 3 lignes, aucun défilement | PASS |
| Le lien but-action est-il clair ? | Oui — raison du no-trade exposée (score vs seuil) | PASS |
| Le feedback est-il immédiat ? | Oui — Thomas ferme l'app, journée trading terminée | PASS |

---

## Flow 3 — Journée DEGRADED MODE (Twelve Data fail OU Claude timeout)

> **Métrique HEART primaire** : Happiness — Thomas garde confiance dans le système même quand il y a une panne.

### Sous-flow 3A — Twelve Data fail (US-04)

**Étape 1 — Réception message ERREUR DATA**

- **Durée** : 10 secondes de lecture
- **Output Telegram** :

```
Données de marché indisponibles ce matin (8h47 CET).
Motif : Twelve Data timeout après 30 s.
Aucun signal émis aujourd'hui. Prochaine tentative demain 8h45.
```

- **Décision Thomas** : pas de trade. Journée terminée.
- **Friction F14** : Thomas ne sait pas si c'est une panne récurrente ou ponctuelle.
  - **Sévérité** : P1
  - **Mitigation** : si 3 pannes Twelve Data consécutives, le bot envoie un message P0 spécifique : "Données indisponibles 3 jours consécutifs. Vérifier le compte Twelve Data (plan Pro Individual — infra-audit §2)." Ce message P0 ne remplace pas le message ERREUR DATA standard — il s'y ajoute.

---

### Sous-flow 3B — Claude timeout (US-05)

**Étape 1 — Réception message DEGRADED MODE**

- **Durée** : 10 secondes de lecture
- **Output Telegram** :

```
Scoring IA indisponible ce matin (8h49 CET).
Données de marché reçues — justification structurée non générée.
Aucun signal émis aujourd'hui (règle : pas de signal sans justification).
```

- **Décision Thomas** : pas de trade. Journée terminée.
- **Friction F15** : Thomas pourrait interprèter "données de marché reçues" comme une invitation à analyser lui-même.
  - **Sévérité** : P1
  - **Mitigation** : la troisième ligne est explicite — "règle : pas de signal sans justification". C'est la promesse de marque (brand-platform §3 promesse interne) verbalisée. Thomas sait que ce n'est pas une invitation à analyser, c'est une règle d'or.
- **Friction F16** : Thomas perd confiance dans le système après plusieurs DEGRADED MODE.
  - **Sévérité** : P0
  - **Mitigation** : healthchecks.io dead man's switch (infra-audit §5) — si le pipeline ne s'exécute pas à 8h40, l'alerte parvient à Thomas avant même que le NO-TRADE soit attendu. Chaque ERREUR DATA et DEGRADED MODE est logué en SQLite (statut "erreur_data" / "erreur_claude"). Si 3 jours consécutifs d'erreur → message Telegram P0 : "Bot en panne 3 jours consécutifs — vérification manuelle requise."

---

### Cognitive walkthrough — Flow 3

| Question | Réponse | Verdict |
|---|---|---|
| Thomas sait-il quoi faire ? | Oui — "Aucun signal émis" = décision explicite | PASS |
| L'action est-elle visible ? | Oui — message 3 lignes, actionnable | PASS |
| Le lien but-action est-il clair ? | Oui — motif technique exposé + règle métier | PASS |
| Le feedback est-il immédiat ? | Oui — Thomas sait ce qui s'est passé et la prochaine tentative | PASS |

---

## Flow 4 — Audit hebdomadaire (vendredi soir, 30 min)

> **Métrique HEART primaire** : Engagement — Thomas fait son audit chaque vendredi soir sans le sauter. Le push automatique est le déclencheur.
> **Commande introduite** : `/journal-week` — analogue à US-08 /trade mais pour la semaine.

### Étape 1 — Push automatique résumé hebdo (vendredi 18h00 CET)

- **Déclencheur** : cron vendredi 18h00 CET (à implémenter en V1.1 selon functional-specs §6 roadmap V1.1)
- **Durée** : instantané — push Telegram
- **Output Telegram** :

```
--- Résumé semaine [DATE LUNDI]-[DATE VENDREDI] ---
Signaux GO : [N] | No-trade : [N] | Erreurs : [N]
Trades loggués : [N sur N signaux GO]

P&L brut semaine : +[X] €
P&L net estimé : +[X] € (après frais + PFU 31,4 % cumulé YTD)
Drawdown max semaine : [X] % (seuil 20 %)
Win rate semaine : [X] % vs backtest [Y] %

Statut : [OK / ALERTE / ARRÊT]
```

- **Friction F17** : Thomas pourrait ne pas ouvrir Telegram le vendredi soir.
  - **Sévérité** : P1
  - **Mitigation** : le push est automatique — Thomas voit la notification même s'il n'ouvre pas l'app. La notification prévisualise le statut (OK / ALERTE / ARRÊT) sur l'écran de verrouillage — si ARRÊT, il ouvrira immédiatement.

---

### Étape 2 — Lecture du résumé (vendredi 18h, ~5 min)

- **Durée** : 5 minutes de lecture et analyse
- **Action Thomas** : lit le résumé, compare win rate semaine vs backtest, vérifie drawdown.
- **Décision** : si statut OK → Thomas remet le téléphone, RAS. Si statut ALERTE ou ARRÊT → Thomas continue au flow décisionnel (étape 3).

---

### Étape 3 — Si signal d'arrêt activé : message P0 explicite

Si l'une des conditions kpi-framework.md §7 est déclenchée (drawdown > 20 %, win rate déviation > 15 pts, etc.), le message hebdo contient une section P0 supplémentaire :

```
ARRÊT REQUIS — Drawdown mensuel a dépassé 20 %.
Action requise : pause du live, retour en paper-trading.
Données complètes : envoie /journal-week pour le rapport détaillé.
```

- **Friction F18** : Thomas ignore le signal d'arrêt (biais confirmation — "la semaine prochaine sera meilleure").
  - **Sévérité** : P0
  - **Mitigation** : le message utilise "ARRÊT REQUIS" (pas "recommandé"). Le bot n'envoie plus de signaux GO tant que Thomas n'a pas répondu (implémenté via flag `drawdown_alerte=true` en SQLite — R7 functional-specs). Thomas est forcé de réagir pour reprendre les signaux.

---

### Étape 4 — Commande /journal-week (optionnel, sur demande)

- **Action Thomas** : envoie `/journal-week` pour obtenir le détail ligne par ligne des trades de la semaine.
- **Output Telegram** : liste des signaux + P&L par trade + cohérence score/résultat.
- **Format** : analogue au rapport mensuel kpi-framework.md §5, limité à la semaine courante.

---

### Audit heuristique Nielsen — Flow 4

| # | Heuristique | Verdict | Évidence |
|---|---|---|---|
| H1 | Visibilité état système | PASS | Statut "OK / ALERTE / ARRÊT" en dernière ligne du résumé |
| H3 | Contrôle et liberté | PASS | Thomas peut ignorer le push (journée RAS) ou creuser avec /journal-week |
| H5 | Prévention des erreurs | PASS | Signal d'arrêt P0 bloque les futurs signaux GO — Thomas ne peut pas ignorer sans action |
| H8 | Design minimaliste | PASS | Résumé compact — seules les métriques décisionnelles (drawdown, win rate, statut) |

---

## Flow 5 — Fin de mois — décision GO/NO-GO continuer

> **Métrique HEART primaire** : Retention — Thomas prend une décision formalisée chaque mois. La décision est tracée en SQLite.
> **Commandes introduites** : `/continue` et `/stop` — Thomas répond au rapport mensuel.

### Étape 1 — Rapport mensuel automatique (1er jour ouvré du mois, 8h00 CET)

- **Déclencheur** : cron 1er jour ouvré du mois à 8h00 CET (avant la fenêtre de signal)
- **Output Telegram** :

```
--- Rapport mensuel [MOIS ANNEE] ---
Signaux envoyés : [N]  | No-trade : [N] ([%] — vertu)
Trades exécutés : [N]  | Win rate : [%]

P&L brut : +[X] €
Frais Bourse Direct : −[X] €
Spread émetteur estimé : −[X] €
PFU estimé (31,4 % cumulé YTD) : −[X] €
P&L net estimé : [X] €

Drawdown max du mois : [X] % (seuil 20 %)
Profit Factor : [X]
Score confiance moyen : [X]/10
Sharpe glissant 3 mois : [X]
Écart win rate live vs backtest : [X] pts (seuil alerte 15 pts)

Statut : [CONTINUE / DECISION REQUIRED]
```

---

### Étape 2 — Chemin (a) : tous critères OK → CONTINUE

- **Output additionnel Telegram** :

```
Tous les critères de continuation sont respectés.
Prochaine revue : 1er [MOIS SUIVANT].
Réponds /continue pour confirmer.
```

- **Action Thomas** : envoie `/continue`. Bot confirme "Signaux GO reprennent normalement."
- **Friction F19** : Thomas ne répond pas à /continue et les signaux continuent quand même.
  - **Sévérité** : P2
  - **Mitigation** : le /continue est optionnel en chemin (a) — les signaux reprennent automatiquement si aucun signal d'arrêt n'est actif. La commande /continue est une confirmation explicite pour le journal, pas un déblocage obligatoire.

---

### Étape 3 — Chemin (b) : ≥ 1 critère KO → DECISION REQUIRED

- **Output additionnel Telegram** :

```
DECISION REQUIRED — [N] critère(s) hors seuil :
• Drawdown max : [X] % > seuil 20 %
• (ou) Win rate live : [X] % vs backtest [Y] % (écart [Z] pts > 15 pts)
• (ou) P&L net : [X] € < 0 sur 3 mois consécutifs

Signaux GO suspendus jusqu'à ta décision.
→ Réponds /continue pour reprendre malgré l'alerte (décision assumée).
→ Réponds /stop pour arrêter le bot et archiver le journal.
```

- **Action Thomas** : choisit /continue (avec awareness du risque) ou /stop.
- **Friction F20** : Thomas envoie /continue par réflexe sans lire le message d'alerte.
  - **Sévérité** : P0
  - **Mitigation** : si ≥ 2 critères KO, le bot demande une confirmation double. Premier /continue → "Confirme-tu la reprise avec [N] critères hors seuil ? Renvoie /continue pour confirmer." Second /continue → reprise effective. Cette friction volontaire est cohérente avec JTBD 5 : Thomas doit "décider sereinement".
- **Friction F21** : Thomas envoie /stop mais veut revenir en paper-trading (pas arrêt définitif).
  - **Sévérité** : P1
  - **Mitigation** : /stop déclenche "Signaux live suspendus. Mode paper-trading activé — les signaux continuent à arriver en simulation, sans que tu passes d'ordres réels. Pour reprendre le live, envoie /continue."

---

### Audit heuristique Nielsen — Flow 5

| # | Heuristique | Verdict | Évidence |
|---|---|---|---|
| H1 | Visibilité état système | PASS | "CONTINUE / DECISION REQUIRED" visible en tête du rapport |
| H3 | Contrôle et liberté | PASS | /continue et /stop = contrôle explicite Thomas, pas décision automatique |
| H5 | Prévention des erreurs | PASS | Double confirmation si ≥ 2 critères KO — évite le /continue réflexe |
| H9 | Aide correction erreurs | PASS | /stop explique la différence live/paper-trading dans le message de confirmation |
| H10 | Aide et documentation | PASS | Chaque critère KO est nommé avec sa valeur et son seuil — Thomas comprend exactement pourquoi |

---

## Synthèse — Friction Map

| # | Friction | Flow | Sévérité | Mitigation produit |
|---|---|---|---|---|
| F1 | Notification Telegram masquée — Thomas rate la fenêtre | Flow 1 | P1 | Runbook configuration Telegram (hors scope produit) |
| F2 | Prévisualisation trop courte — GO ou NO-TRADE non visible sans déverrouiller | Flow 1 | P2 | Première ligne = "ACHAT — [sous-jacent]" ou "Pas de trade" (visible sans déverrouiller) |
| F3 | Message tronqué sur mobile — score et fenêtre hors viewport | Flow 1 | P1 | Template ≤ 8 lignes — score et fenêtre visibles sans scroll (iPhone 12+) |
| F4 | Thomas ne se souvient pas du backtest #B-031 | Flow 1 | P2 | Message inclut win rate + nb trades + drawdown max — pas de mémoire requise |
| F5 | Thomas ne trouve pas rapidement le bon turbo sur Bourse Direct | Flow 1 | P1 | Sous-jacent exact + capital engagé dans le message. V1.1 : delta indicatif |
| F6 | Prix d'entrée a bougé depuis le calcul | Flow 1 | P1 | Conditionnel d'incertitude brand-platform. Thomas pose ordre limite — volatilité acceptée |
| F7 | Calcul mental nb turbos (600 € / prix) | Flow 1 | P2 | Capital engagé affiché. V1.1 : nb turbos indicatif dans le message |
| F8 | Ordre SL/TP dans le mauvais ordre — rate la fenêtre | Flow 1 | P2 | Hors scope produit — Thomas expérimenté, geste habituel |
| F9 | Ordre non exécuté immédiatement (prix éloigné) | Flow 1 | P1 | Sous-jacents V1 = indices liquides. Thomas annule si non exécuté avant 8h55 |
| F10 | Thomas oublie de logger le trade via /trade | Flow 1 | P1 | V1.1 : rappel automatique 18h30 CET si signal GO sans log reçu |
| F11 | Format /trade difficile à mémoriser | Flow 1 | P2 | /trade sans paramètre → aide format automatique |
| F12 | Doute Thomas sur NO-TRADE ("j'aurais bien tradé") | Flow 2 | P1 | Score max affiché + seuil — factuel uniquement, zéro éditorial |
| F13 | Thomas ne sait pas si bot reprend lundi (vendredi) | Flow 2 | P2 | "Prochaine fenêtre : lundi 8h45" calculé dynamiquement |
| F14 | Panne Twelve Data récurrente — perte confiance | Flow 3 | P1 | Message P0 si 3 pannes consécutives + healthchecks.io dead man's switch |
| F15 | DEGRADED MODE interprété comme invitation à analyser soi-même | Flow 3 | P1 | Troisième ligne explicite : "règle : pas de signal sans justification" |
| F16 | Plusieurs DEGRADED MODE consécutifs — perte confiance système | Flow 3 | P0 | Message P0 après 3 erreurs consécutives. Log SQLite + alerte Telegram |
| F17 | Thomas ne voit pas le push résumé hebdo vendredi soir | Flow 4 | P1 | Statut "OK / ALERTE / ARRÊT" visible sur notification push sans ouvrir l'app |
| F18 | Thomas ignore signal d'arrêt hebdo (biais confirmation) | Flow 4 | P0 | Bloc suivants signaux GO tant que `drawdown_alerte=true` — Thomas forcé de réagir |
| F19 | Thomas ne répond pas à /continue (chemin OK) | Flow 5 | P2 | /continue optionnel — signaux reprennent automatiquement si aucun arrêt actif |
| F20 | Thomas envoie /continue par réflexe sans lire l'alerte | Flow 5 | P0 | Double confirmation si ≥ 2 critères KO — friction volontaire |
| F21 | /stop interprété comme arrêt définitif | Flow 5 | P1 | /stop → mode paper-trading (pas arrêt définitif) expliqué dans le message |
| F22 | Changement de téléphone / réinstallation Telegram — Thomas perd son `chat_id`, le bot envoie dans le vide | Transversal | P1 | (a) Message de bienvenue automatique au premier contact `/start` : demande à Thomas de copier son nouveau `chat_id` dans la variable d'env `THOMAS_CHAT_ID` sur Replit. (b) healthchecks.io alerte si aucune delivery confirmation Telegram pendant 5 jours ouvrés consécutifs. (c) Procédure documentée dans le runbook Thomas (Phase 4). |
| F23 | Vacances / déconnexion volontaire — sans pause, Thomas reçoit 10+ signaux GO/NO-TRADE ignorés → bruit, perte de saillance au retour | Transversal | P1 | Commande **US-12 `/pause [YYYY-MM-DD YYYY-MM-DD]`** (cf. functional-specs.md US-12) — Thomas suspend volontairement les signaux avant de partir. Rappel automatique veille de fin de pause : "Bot reprend demain 8h45 CET." |
| F24 | RER bloqué / pas de réseau 4G entre 8h45 et 8h55 — Thomas reçoit la notification à 8h57 (sortie tunnel), fenêtre dépassée, signal horodaté ne dit pas "expiré" → risque d'exécution sur prix obsolète | Flow 1 | P1 | (a) Ajouter ligne explicite dans tous les templates ACHAT/VENTE : "Valable jusqu'à 8h55 CET — au-delà, ne pas exécuter" (à coordonner avec @copywriter). (b) Si Thomas envoie `/trade` après 9h00 sur un signal horodaté avant 8h55, le bot répond "Signal périmé — à ne pas tracker dans le journal." (c) Chaque message Telegram inclut un timestamp ISO 8601 dans les métadonnées pour calcul automatique du staleness. |

---

## Wireframes ASCII — 5 Templates Telegram

### Template 1 — ACHAT (signal GO, mobile + desktop)

**Mobile (viewport ~320px, Telegram iOS/Android) :**
```
┌─────────────────────────────────────┐
│ TradingApp  8h46                  ▾ │
├─────────────────────────────────────┤
│                                     │
│  ACHAT — DAX Turbo Call             │
│  Entrée : 3,42 € │ SL : 3,21 €     │
│  Cible potentielle : 3,85 €         │
│  Gap haussier +0,8 % clôture US +   │
│  ORB haussier 5 premières min Xetra │
│  Réf. #B-031 — 61 % / 87 trades /  │
│  drawdown max −18 %                 │
│  Risque max : 126 € / 600 € engagés │
│  Score : 7,1/10 │ av. 8h55 CET      │
│                                     │
└─────────────────────────────────────┘
Toutes lignes visibles sans scroll (iPhone 12+)
```

**Desktop (Telegram macOS/Windows) :**
```
┌─────────────────────────────────────────────────────────┐
│ TradingApp                                    lun. 8h46 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ACHAT — DAX Turbo Call                                 │
│  Entrée : 3,42 € | SL : 3,21 € | Cible potentielle : 3,85 €  │
│  Gap haussier +0,8 % sur clôture US + ORB haussier 5 premières min Xetra │
│  Score 7,1/10 confirmé par momentum > seuil backtest    │
│  Réf. backtest #B-031 — win rate 61 % / 87 trades / drawdown max −18 %   │
│  Risque max : 126 € sur 600 € engagés (levier ~6)       │
│  Score : 7,1/10 | Fenêtre : avant 8h55 CET              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Template 2 — NO-TRADE

**Mobile :**
```
┌─────────────────────────────────────┐
│ TradingApp  8h48                  ▾ │
├─────────────────────────────────────┤
│                                     │
│  Pas de trade aujourd'hui.          │
│  Score max relevé : 5,1/10 —        │
│  en dessous du seuil 6,5.           │
│  Prochaine fenêtre : demain 8h45.   │
│                                     │
└─────────────────────────────────────┘
3 lignes — aucun scroll requis
```

**Desktop :**
```
┌─────────────────────────────────────────┐
│ TradingApp                   mer. 8h48  │
├─────────────────────────────────────────┤
│  Pas de trade aujourd'hui.              │
│  Score max relevé : 5,1/10 — en dessous du seuil 6,5. │
│  Prochaine fenêtre : demain 8h45.       │
└─────────────────────────────────────────┘
```

---

### Template 3 — ERREUR DATA (Twelve Data fail)

**Mobile :**
```
┌─────────────────────────────────────┐
│ TradingApp  8h47                  ▾ │
├─────────────────────────────────────┤
│                                     │
│  Données de marché indisponibles    │
│  ce matin (8h47 CET).               │
│  Motif : Twelve Data timeout 30 s.  │
│  Aucun signal émis aujourd'hui.     │
│  Prochaine tentative demain 8h45.   │
│                                     │
└─────────────────────────────────────┘
```

---

### Template 4 — DEGRADED MODE (Claude timeout)

**Mobile :**
```
┌─────────────────────────────────────┐
│ TradingApp  8h49                  ▾ │
├─────────────────────────────────────┤
│                                     │
│  Scoring IA indisponible ce matin   │
│  (8h49 CET).                        │
│  Données de marché reçues —         │
│  justification non générée.         │
│  Aucun signal émis aujourd'hui      │
│  (règle : pas de signal sans        │
│  justification).                    │
│                                     │
└─────────────────────────────────────┘
```

---

### Template 5 — RÉSUMÉ HEBDO (vendredi 18h, push auto)

**Mobile :**
```
┌─────────────────────────────────────┐
│ TradingApp  18h00               [•] │
├─────────────────────────────────────┤
│                                     │
│  --- Semaine 27 avr.-1 mai ---      │
│  GO : 3 | No-trade : 2 | Erreurs : 0│
│  Trades loggués : 3/3               │
│                                     │
│  P&L net estimé : +412 €            │
│  Drawdown max : 7 % (seuil 20 %)    │
│  Win rate : 67 % vs 61 % backtest   │
│                                     │
│  Statut : OK                        │
│                                     │
└─────────────────────────────────────┘
Push notification visible sur écran verrou
```

---

## Tests UX — Validation des 5 flows

| Test | Critère de succès | Statut |
|---|---|---|
| Parcours persona Flow 1 : Thomas passe un ordre en < 10 min | Signal reçu → ordre Bourse Direct exécuté avant 8h55 CET | Structurellement PASS (fenêtre 8h45-8h55 = 10 min, étapes 2-4 = 7 min estimées) |
| Charge cognitive Flow 1 : ≤ 3 actions principales par étape | Étape 2 : 1 action (lire). Étape 3 : 1 action (chercher turbo). Étape 4 : 2 actions (passer ordre + SL/TP) | PASS |
| Time-to-value Flow 1 : nombre d'étapes jusqu'à l'ordre | 3 étapes : notification → lecture → Bourse Direct | PASS (≤ 3 étapes) |
| Edge case : état vide (NO-TRADE) | Message 3 lignes, Thomas ferme sans chercher alternative | PASS (Flow 2 documenté) |
| Edge case : erreur pipeline | Message ERREUR DATA / DEGRADED MODE explicite, pas de signal forcé | PASS (Flow 3 documenté) |
| Edge case : Thomas revient après 30 jours d'absence | Rapport mensuel automatique le 1er du mois — Thomas reprend le contexte | PASS (Flow 5 documenté) |
| Edge case : signal d'arrêt activé | Message P0 + blocage signaux GO jusqu'à décision Thomas | PASS (Flow 4 étape 3, Flow 5 étape 3) |
| Accessibilité WCAG 2.2 AA | N/A — interface Telegram (hors scope WCAG, pas de frontend custom) | N/A (Telegram gère l'accessibilité nativement) |

---

## Métriques HEART par flow

| Flow | Dimension | Signal observable | Cible | Méthode |
|---|---|---|---|---|
| Flow 1 GO trade | Task success | Commande /trade reçue le jour J ou J+1 après signal GO | ≥ 80 % des signaux GO loggués | SQLite table trades, champ trade_effectué |
| Flow 2 NO-TRADE | Happiness | Absence de trade manuel de Thomas le jour du NO-TRADE | 100 % (non mesurable directement — proxy : journal trade_effectué=false) | Journal SQLite |
| Flow 3 DEGRADED | Happiness | Absence de perte de confiance = bot reprend normalement le lendemain | Taux erreur < 5 % sur 30 jours glissants (kpi-framework §3.4-3.5) | SQLite statut erreur |
| Flow 4 Audit hebdo | Engagement | Thomas lit le résumé hebdo (proxy : commande /journal-week dans les 24h suivant le push) | ≥ 80 % des vendredis avec ouverture Telegram TradingApp | Log commandes Telegram |
| Flow 5 GO/NO-GO mensuel | Retention | Thomas répond /continue ou /stop dans les 48h suivant le rapport mensuel | 100 % des rapports mensuels ont une réponse explicite | SQLite + log commandes |

---

## Recommandations pour @design — Phase 2

### Maquettes haute fidélité requises

1. **Template ACHAT** — rendu exact sur iPhone 14 Pro (390×844px), Telegram iOS dark mode + light mode. Mettre en évidence la ligne "Fenêtre : avant 8h55 CET" (urgence temporelle) sans mise en gras marketing. Vérifier que les 8 lignes sont entièrement visibles sans scroll.

2. **Template NO-TRADE** — rendu sur iPhone 14 Pro, vérifier que la première ligne est visible sur l'écran de verrouillage iOS (prévisualisation Telegram = ~2 lignes sans déverrouiller). Tonalité visuelle sobre — pas de couleur orange ou rouge (pas d'alerte, décision neutre).

3. **Template ERREUR DATA / DEGRADED MODE** — rendu sur iPhone 14 Pro. Différencier visuellement des templates GO/NO-TRADE (fond légèrement différent dans Telegram ? Pas possible nativement — explorer les emojis sobres type ⚠ ou [X] en préfixe si cohérent avec brand-platform).

4. **Template RÉSUMÉ HEBDO** — rendu desktop (Telegram macOS 1280px) + mobile. Le tableau de métriques doit rester lisible sur mobile — envisager format compact sur 2 colonnes plutôt que tableau.

5. **Notification push (écran verrouillage)** — simuler l'aperçu iOS et Android pour les 5 templates. Vérifier que la première ligne de chaque message permet de distinguer GO / NO-TRADE / ERREUR sans déverrouiller.

**Format pour maquettes** : Figma, export PNG 2x, 3 viewports (375px mobile, 768px tablet, 1280px desktop). Les templates Telegram n'ont pas de CSS custom — les contraintes de rendu sont celles de l'app Telegram native.

**Priorité** : Template ACHAT en premier (Flow 1 = flow critique). Template NO-TRADE en second (Flow 2 = flow le plus fréquent si % no-trade = 30-60 %).

---

## Auto-évaluation gates BLOQUANT

| Gate | Critère | Verdict | Évidence |
|---|---|---|---|
| G1 | Toutes les sections présentes | PASS | 5 flows + friction map + wireframes ASCII + tests UX + HEART + recommandations @design |
| G3 | Bloc Handoff structuré présent | PASS | Section Handoff ci-dessous |
| G5 | Persona Thomas identifié ≥ 2 fois | PASS | Thomas nommé dans chaque flow, scénario 4 mai 2026 RER cité |
| G7 | Zéro contradiction avec livrables amont | PASS | Cohérence personas.md (8h40-9h05), functional-specs.md (templates, US-08 /trade), brand-platform.md (Voice & Tone), kpi-framework.md (signaux d'arrêt) |
| G12 | Chaque flow implémentable sans question | PASS | Étapes titrées, durées, outputs Telegram, frictions et mitigations produit. Commandes /trade, /journal-week, /continue, /stop spécifiées avec comportements |
| G15 | Zéro placeholder résiduel | PASS | Aucun [À REMPLIR] — [HYPOTHÈSE] marqués explicitement |
| G17 | Pas copiable pour un concurrent | PASS | Référence explicite à Thomas, RER, Bourse Direct, Twelve Data, fenêtre 8h45-8h55, DAX Turbo Call, PFU 31,4 %, backtest #B-031 |

---

**Handoff → @orchestrator**

- **Fichiers produits** : `/home/user/TradingApp/docs/ux/user-flows.md`
- **Décisions prises** :
  - 4 commandes Telegram définies : `/trade` (US-08 existant), `/journal-week` (nouveau — analogue hebdomadaire de /trade), `/continue` et `/stop` (nouveau — décision mensuelle Flow 5). Ces commandes doivent être ajoutées aux specs fonctionnelles par @product-manager avant implémentation @fullstack.
  - Rappel automatique /trade à 18h30 CET recommandé en V1.1 (F10 mitigation) — à ajouter dans la roadmap functional-specs.
  - Push automatique résumé hebdo vendredi 18h CET recommandé en V1.1 (F17 mitigation) — cohérent avec functional-specs §6 roadmap V1.1.
  - Double confirmation /continue si ≥ 2 critères KO (F20 mitigation) — sécurité comportementale pour Thomas en drawdown.
- **Points d'attention** :
  - F16 (DEGRADED MODE 3 jours consécutifs) et F18 (signal d'arrêt ignoré) sont des frictions P0 — leurs mitigations (message P0 + blocage signaux GO) DOIVENT être implémentées avant mise en live.
  - Les commandes /journal-week, /continue, /stop ne figurent pas encore dans functional-specs.md — escalade à @product-manager pour ajout en US-09, US-10, US-11 avant que @fullstack implémente.
  - Template RÉSUMÉ HEBDO et Template RAPPORT MENSUEL sont distincts (fréquences différentes) — @copywriter devra rédiger les variantes de chaque template pour les cas OK / ALERTE / ARRÊT.
- **Aucune action Replit requise** (livrable documentation uniquement).

**Vers @copywriter Phase 1** : les 5 flows alimentent les message-templates. En priorité : (1) variantes NO-TRADE selon contexte (série de pertes vs semaine normale), (2) message P0 ARRÊT (ton non alarmiste mais ferme), (3) messages de confirmation /continue et /stop.

**Vers @design Phase 2** : recommandations maquettes documentées en section "Recommandations pour @design". Priorité : Template ACHAT mobile + notification push écran verrouillage.

[LEARNING DÉTECTÉ]
- Description : les commandes /journal-week, /continue, /stop sont nécessaires pour les flows hebdo et mensuel mais absentes des functional-specs.md V1. Elles ont été conçues ici de façon cohérente avec US-08, mais doivent être formalisées en US-09 à US-11 par @product-manager avant implémentation.
- Catégorie : gap de specs
- Sévérité estimée : P1
- Cible propagation : agent-spécifique (@product-manager)
- Fichiers impactés : `docs/product/functional-specs.md` (ajout US-09 /journal-week, US-10 /continue, US-11 /stop)
