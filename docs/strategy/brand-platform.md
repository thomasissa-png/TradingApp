# Brand Platform — TradingApp

> Framework utilisé : **Golden Circle (Sinek)** + **Voice & Tone specs**
> Justification : projet personnel à mission-first (l'outil existe pour résoudre une frustration précise de Thomas, pas pour générer du revenu). Le Golden Circle force à articuler le "pourquoi tu l'as construit" avant "ce qu'il fait" — ce qui devient le test de cohérence de chaque décision produit.
> Date : 2026-05-01 | Agent : @creative-strategy

---

## 1. Positionnement (1 phrase)

**Un co-pilote de décision pour trader les turbos à l'ouverture européenne : un signal par jour, justifié chiffres à l'appui, ou silence assumé.**

---

## 2. Golden Circle

### Why — Pourquoi il existe

Thomas veut trader les turbos à l'ouverture EU avec du capital réel et du levier. Il ne manque pas de données. Il manque d'une raison suffisante pour appuyer sur le bouton. La plupart des alertes de marché sont des opinions habillées en signaux. TradingApp ne formule une recommandation que lorsque la configuration a une trace statistique sur 5 ans — et dit explicitement "pas de trade" quand ce n'est pas le cas.

### How — Comment

- Calcul automatique chaque matin ouvré à 8h40-8h55 CET
- Scoring multi-dimension (technique + contexte + score de confiance chiffré)
- Backtest 5 ans sur Twelve Data avant qu'un seul pattern soit qualifié de signal
- Livraison push sur Telegram : une seule alerte, structure fixe, lisible en 30 secondes
- Exécution manuelle chez Bourse Direct en < 5 min

### What — Quoi

Un bot Telegram qui envoie chaque jour ouvré, entre 8h45 et 8h55 CET, soit un signal turbo structuré (sous-jacent + sens + entrée + SL + TP + raison + score + ref backtest), soit un message "pas de trade aujourd'hui" explicitement motivé.

---

## 3. Promesse interne

> Placée ici pour servir de test de cohérence à chaque décision produit — jamais dans les messages Telegram.

**« Je n'envoie un signal que si j'ai une raison chiffrée de le faire. Sinon je me tais. »**

Critère de trahison de la promesse : envoyer un signal avec un score de confiance < seuil défini en backtest pour "remplir" la journée.

---

## 4. Les 3 piliers de marque

### Pilier 1 — Justifié

Chaque signal inclut les chiffres qui ont conduit à la décision. Win rate backtest. Score de confiance. Niveau d'entrée, SL, TP. La raison humaine en une phrase. Thomas peut reconstituer le raisonnement sans ouvrir un autre outil.

**RTB (Reason To Believe)** : le module de scoring Claude reçoit les données brutes et produit une justification structurée — pas un commentaire éditorial, un raisonnement traçable.

### Pilier 2 — Concis

Un message. Une décision. Trente secondes de lecture maximum. Pas de tableau de bord à ouvrir, pas d'indicateurs contradictoires à réconcilier. TradingApp a fait le travail de synthèse en amont.

**RTB** : format Telegram fixe, limité à 6 lignes de signal + 1 ligne de confiance. Aucune section optionnelle.

### Pilier 3 — Backtesté

Aucun pattern n'est qualifié de signal sans validation sur 5 ans d'historique Twelve Data. Le numéro de référence backtest figure dans chaque alerte pour retrouver le dossier de test correspondant.

**RTB** : journal de backtest versionné en SQLite, accessible à tout moment pour audit. Toute modification de l'edge déclenche un nouveau backtest complet avant retour en production.

---

## 5. Anti-personnalité (ce que TradingApp n'est PAS)

| Ce qu'on refuse | Pourquoi c'est un renoncement assumé |
|---|---|
| **Hype / FOMO** | "Signal fort !" sans chiffres = exactement la friction que Thomas fuit |
| **Verbeux** | Un message de 20 lignes n'est pas lu à 8h48 avant d'entrer en position |
| **Boîte noire** | Si Thomas ne comprend pas pourquoi le signal a été émis, il ne peut pas décider d'y aller ou non |
| **Exhaustif** | 10 indicateurs affichés = responsabilité renvoyée à Thomas. TradingApp tranche |
| **Optimiste par défaut** | "Pas de trade" est une réponse valide et respectée, pas un aveu d'échec |

---

## 6. Tone of Voice

### Voice (constante)

TradingApp parle comme un analyste quantitatif qui respecte le temps de son interlocuteur : précis, factuel, sans fioritures, transparent sur l'incertitude.

**5 Do's**

1. **Chiffrer** — donner le score, le win rate, le SL exact. Pas "risque maîtrisé", mais "SL : 2,15 € / risque max : 87 €".
2. **Assumer le no-trade** — "Pas de trade aujourd'hui — aucune config au-dessus du seuil" est une phrase complète et respectable.
3. **Nommer la raison** — "Gap haussier sur résistance hebdo + momentum > seuil backtest #B-042" : une phrase, une cause.
4. **Utiliser le conditionnel de l'incertitude** — "Cible potentielle : 2,45 €" pas "cible : 2,45 €". Le marché n'est pas certifié.
5. **Être court par discipline, pas par paresse** — chaque ligne doit mériter sa place. Couper ce qui ne change pas la décision.

**5 Don'ts**

1. Ne jamais écrire "signal fort", "opportunité exceptionnelle", "ne pas manquer" — tout mot de marketing est proscrit.
2. Ne pas afficher d'indicateurs contradictoires sans les avoir réconciliés en amont — la synthèse est le travail du bot, pas de Thomas.
3. Ne pas minimiser le risque — SL et risque max en euros sont obligatoires dans chaque signal.
4. Ne pas justifier un signal par un seul indicateur — le scoring multi-dimension est la règle.
5. Ne pas envoyer un "signal" de remplacement si le seuil n'est pas atteint — le silence est préféré à la médiocrité.

### Tone (variable par contexte)

| Contexte | Adaptation |
|---|---|
| Signal GO | Factuel, structuré, neutre. Pas de ponctuation enthousiaste. |
| No-trade du jour | Sobre, direct, sans excuse. "Pas de trade aujourd'hui — [raison]." |
| Message d'erreur technique | Transparent sur la cause + estimation de résolution. Jamais "problème technique" vague. |
| Résumé hebdo / mensuel | Légèrement plus analytique, chiffres P&L et drawdown en tête, commentaire factuel. |

### Vocabulaire prescrit / proscrit

**Utiliser** : score de confiance, seuil, configuration, sous-jacent, sens (achat/vente), niveau d'entrée, SL, TP, référence backtest, fenêtre d'exécution, capital engagé, risque max, no-trade.

**Interdire** : signal fort, forte conviction, opportunité, ne pas manquer, buy the dip, momentum haussier (sans chiffre), "le marché devrait", setup parfait, valider (pour décrire une hausse).

### Exemples avant/après

**Avant (style à bannir)**
> Signal fort ! CAC40 momentum haussier — bonne opportunité d'entrée ce matin. Ne pas manquer.

**Après (style TradingApp)**
> ACHAT — CAC40 Turbo Call
> Entrée : 2,18 € | SL : 2,05 € | Cible : 2,45 €
> Raison : gap haussier clôture US + résistance hebdo franchie + score 7,2/10 (réf. backtest #B-042, win rate 58 % / 112 trades)
> Risque max : 104 € sur 800 € engagés
> Fenêtre : 8h48-8h55 CET

---

**Avant (no-trade mal formulé)**
> Pas grand chose ce matin, marché hésitant, peut-être plus tard dans la journée...

**Après (style TradingApp)**
> Pas de trade aujourd'hui.
> Score max relevé : 5,1/10 — en dessous du seuil 6,5. Prochaine fenêtre demain 8h45.

---

## 7. Benchmark concurrentiel

> Outil personnel non commercialisé. Benchmark réalisé sur les alternatives fonctionnelles que Thomas pourrait utiliser ou a utilisées — pas des concurrents commerciaux directs.

### Alternatives fonctionnelles analysées

| Alternative | Positionnement déclaré | Ce qu'ils font tous | Ce que TradingApp fait différemment |
|---|---|---|---|
| Alertes TradingView | "Soyez alerté dès qu'un niveau est touché" | Déclencher l'alerte, laisser l'analyse à l'utilisateur | TradingApp fournit la synthèse et la justification — pas seulement le déclenchement |
| Screeners/scanners (type Trade Ideas) | "Trouver les meilleures opportunités" | Multi-signaux, multi-timeframes, dashboard actif | Un seul signal, push passif, décision déjà prise en amont |
| Repo Finance existant (thomasissa-png) | Multi-agents, multi-teams, 4 scans/jour | Données riches mais justification insuffisante + dashboard actif | Justification structurée + canal push + no-trade assumé |
| Trading "au feeling" | N/A | Dépend de l'humeur et du contexte du matin | Règles fixes backtestées, indépendantes du biais du jour |

**Ce que toutes les alternatives font** : soit elles bombardent de données (en délégant la synthèse), soit elles génèrent des alertes sans justification suffisante pour engager du capital avec levier.

**Espace libre non occupé** : un signal unique, passif (push Telegram), avec justification chiffrée complète et autorisation explicite de ne rien envoyer. Aucune alternative actuelle de Thomas ne combine ces trois attributs.

---

## 8. Triggers de réévaluation stratégique

- Win rate live diverge de > 10 pts du backtest sur 3 mois consécutifs
- Drawdown mensuel dépasse 20 % du capital dédié 2 mois de suite
- Thomas change de broker ou de fenêtre de trading
- Un nouveau projet personnel couvre le même cas d'usage

---

## 9. Agents spécialisés recommandés pour ce projet

| Agent proposé | Type | Rôle | Justification | Priorité |
|---|---|---|---|---|
| @testeur-persona-thomas | Testeur persona | Incarner Thomas à 8h48, évaluer chaque livrable (format signal, justification, message no-trade) du point de vue "est-ce que j'appuierais sur le bouton avec ça ?" | Thomas est l'unique utilisateur. Tout livrable non validé par son point de vue est un risque de non-usage, comme avec le projet Finance. | Haute |
| @testeur-backtest-edge | Validateur quantitatif | Challenger les hypothèses d'edge (gap follow/fade, ORB, momentum overnight) avec des critères statistiques stricts (robustesse, overfitting, walk-forward) | Le risque n°1 du projet est un edge sur-fitté qui ne tient pas en live. Un agent dédié à la critique du backtest est le garde-fou central. | Haute |

**Justification de l'absence de @testeur-client-du-persona** : outil 100 % personnel, Thomas n'a pas de clients ou d'interlocuteurs professionnels impactés par l'outil. Le cas B2C direct / outil interne s'applique.

### Specs complémentaires pour @agent-factory

**@testeur-persona-thomas**
- Inputs : tout livrable format Telegram (signal, no-trade, résumé hebdo), specs fonctionnelles du bot, format de backtest report
- Outputs : verdict GO/AJUSTER/NO-GO + liste des frictions identifiées + reformulation suggérée du message si applicable
- Critère de succès : Thomas dirait "avec ce message, je sais si je trade ou non en moins de 30 secondes"

**@testeur-backtest-edge**
- Inputs : résultats backtest (win rate, drawdown max, Sharpe, nombre de trades, période testée), paramètres de l'edge
- Outputs : diagnostic overfitting (walk-forward split, IS/OOS), robustesse par année (pas de cherry-picking période), recommandation GO backtest / RETRAVAILLER / NO-GO edge
- Critère de succès : aucun edge ne passe en production sans avoir passé le filtre walk-forward OOS

→ Handoff @agent-factory : créer ces deux agents à partir des specs ci-dessus et du brand-platform produit.

---

## Auto-évaluation (gates critiques)

- [x] Positionnement occupe un espace libre identifié dans le benchmark (push passif + justification chiffrée + no-trade assumé)
- [x] Promesse de marque différenciante ET crédible (ancrée sur le backtest 5 ans + silence si seuil non atteint)
- [x] Benchmark identifie ce que TOUTES les alternatives font (déléguer la synthèse à l'utilisateur)
- [x] Voice & Tone : 5 Do's / 5 Don'ts, vocabulaire prescrit/proscrit, 2 exemples avant/après
- [x] Anti-personnalité documentée avec justification des renoncements
- [x] Brief créatif minimal : positionnement (1 phrase), promesse (1 phrase), ton (5+5), territoire sémantique (≥ 10 mots), exclusions explicites
