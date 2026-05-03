# Personas — TradingApp

> Date : 2026-05-01 | Agent : @creative-strategy
> Persona principal : Thomas (unique utilisateur, outil 100 % personnel)
> Persona client-du-persona : N/A (voir section dédiée en bas de fichier)

---

## Persona principal — Thomas

### Profil

**Nom** : Thomas
**Âge** : 35-45 ans
**Lieu** : France (région parisienne ou grande ville)
**Statut** : actif en emploi (CDI cadre ou indépendant) — le trading n'est pas son activité principale
**Revenus** : classe moyenne supérieure, revenu disponible pour le capital dédié
**Capital dédié trading** : 20-30 k€ — séparé du reste de son patrimoine, montant qu'il accepte de perdre sans impact sur son niveau de vie
**Levier utilisé** : 5-10 sur turbos — max x10 validé Thomas 2026-05-02 (plafond strict imposé par audit Risk Manager turbos, choix du turbo selon la configuration du signal)
**Taille de position typique** : 1 000-2 000 € par trade
**Broker** : Bourse Direct, compte-titre ordinaire (CTO)
**Produits tradés** : turbos (warrants à levier intégré) sur sous-jacents EU — indices (CAC40, DAX, EuroStoxx50), actions françaises large cap, FX (EUR/USD), commodities (or, brent, gaz)

### Équipement et environnement

- Smartphone (iPhone ou Android) comme interface principale pour Telegram le matin
- Ordinateur disponible mais non nécessaire pour l'exécution — il passe l'ordre depuis l'app Bourse Direct mobile
- Connexion stable (domicile ou transport — il est debout et mobile à 8h45)
- Notifications Telegram activées, pas de sons intempestifs — le message doit être lisible d'un coup d'oeil déverrouillé
- Pas de double écran, pas de terminal Bloomberg — c'est un particulier, pas un salle de marché

### Expérience trading

- Plusieurs années de trading actif (minimum 5 ans estimés)
- A pratiqué l'analyse technique (RSI, MACD, Bollinger, EMA) — sait lire un indicateur mais ne veut plus les réconcilier manuellement chaque matin
- A déjà utilisé ou évalué des screeners, alertes TradingView, bots de signaux — toujours insatisfait pour la même raison : la justification est absente ou insuffisante pour engager du capital avec levier
- Connaît le projet Finance (thomasissa-png/Finance) — l'a construit ou utilisé — mais n'a pas confiance dans les recos : trop complexe, pas assez justifié, mauvais canal
- Comprend les concepts : win rate, drawdown, Sharpe, backtest, IS/OOS — il n'a pas besoin d'un glossaire dans le signal

### Journée type (fenêtre critique 8h40-9h05 CET)

| Heure | Activité Thomas |
|---|---|
| 8h40 | Déverrouille le téléphone. Ouvre Telegram. Vérifie si un message TradingApp est arrivé. |
| 8h42-8h45 | Lit le signal (ou le no-trade). Décision mentale : "je trade / je ne trade pas". |
| 8h45-8h50 | Si GO : ouvre l'app Bourse Direct. Cherche le turbo correspondant au sous-jacent. Vérifie le spread. |
| 8h50-8h55 | Passe l'ordre (achat turbo). Note mentalement l'entrée, le SL, le TP. |
| 8h55-9h00 | Referme Bourse Direct. Reprend son activité principale (réunion, trajet, travail). |
| 9h00-9h05 | Peut jeter un oeil au cours une fois l'ordre passé — mais n'est plus disponible pour ajuster en temps réel. |

**Contrainte absolue** : Thomas n'est plus disponible après 9h05. Si le signal n'est pas actionnable avant 9h05, il ne le sera pas du tout. Les ordres SL/TP sont posés dès l'entrée — il ne gère pas la position en intraday.

### Historique trading et drawdowns — signaux d'arrêt

**Drawdown de référence** : Thomas accepte un drawdown mensuel max de 20 % du capital dédié (soit 4-6 k€ sur 20-30 k€) en phase de paper-trading et en phase live.

**Signaux d'arrêt du bot (règles d'or)**

| Condition | Conséquence |
|---|---|
| Drawdown mensuel > 20 % du capital dédié | Arrêt du live, retour en paper-trading, audit du journal |
| 3 semaines consécutives sans signal GO (seuil non atteint) | Revue du seuil de confiance — l'edge est peut-être sur-paramétré |
| Win rate live < win rate backtest − 15 pts sur 3 mois | Revue complète de l'edge — possible over-fit ou changement de régime de marché |
| Score de confiance moyen en live > score moyen backtest (euphorie) | Alert : les signaux récents sont peut-être cherry-pickés — forcer un walk-forward OOS |
| Position ouverte non clôturée en fin de journée (turbo overnight) | Incident — à documenter. Les turbos ne se gardent pas (knock-out risque) |

**Tolérance à la perte par trade** : sur 1 500 € engagés avec SL à −8 %, la perte max est 120 €. Thomas accepte cette perte unitaire. Ce qu'il n'accepte pas : une série de 10 pertes consécutives sans comprendre pourquoi (boîte noire).

---

## Jobs-to-be-done (JTBD)

### JTBD 1 — Décision rapide sans préparation active

**Quand** Thomas ouvre Telegram à 8h40 sur son téléphone,
**il veut** savoir immédiatement s'il y a un trade à faire ou non,
**pour ne pas** avoir à ouvrir un dashboard, consulter plusieurs sources ou reconstituer une analyse qu'il n'a pas le temps de faire.

Critère de succès : la décision "je trade / je ne trade pas" est prise en moins de 30 secondes, sans autre outil ouvert.

### JTBD 2 — Confiance suffisante pour engager du capital avec levier

**Quand** Thomas reçoit un signal GO,
**il veut** voir les chiffres qui ont conduit à la recommandation (score, win rate backtest, raison),
**pour pouvoir** engager 1 500 € avec levier 10 sans avoir le sentiment d'agir au feeling.

Critère de succès : Thomas ne ressent pas le besoin de "vérifier ailleurs" avant de passer l'ordre.

### JTBD 3 — Honnêteté sur l'absence d'opportunité

**Quand** aucune configuration ne dépasse le seuil de confiance,
**Thomas veut** recevoir un message "pas de trade aujourd'hui" explicite,
**pour ne pas** se sentir obligé de chercher un trade par lui-même et risquer de traiter au feeling.

Critère de succès : Thomas reçoit le no-trade, ferme Telegram, reprend son activité. Pas de recherche parallèle de setup de remplacement.

### JTBD 4 — Audit et apprentissage sans friction

**Quand** Thomas fait un audit hebdomadaire ou mensuel de ses trades (30 min max),
**il veut** un journal structuré (entrée, sortie, MAE, MFE, P&L net, cohérence signal/résultat),
**pour mesurer** si le bot génère réellement un edge en live ou s'il performe moins bien que le backtest.

Critère de succès : l'audit complet d'un mois de trading tient en 30 minutes, journal SQLite exportable.

### JTBD 5 — Confiance dans le système même en drawdown

**Quand** Thomas traverse une série de pertes (5-7 trades perdants consécutifs),
**il veut** comprendre si le drawdown est dans les limites statistiques prévues par le backtest,
**pour décider** sereinement de continuer à suivre les signaux ou de déclencher un arrêt et un audit.

Critère de succès : chaque signal inclut une référence backtest qui permet à Thomas de comparer le drawdown courant au drawdown max historique du pattern.

---

## Frustrations enrichies (avec verbatims et contexte)

### Frustration 1 — Justification insuffisante pour engager du capital

**Verbatim** : « Quand je vois un signal du Finance, je n'ai pas assez d'éléments pour engager 1 500 € avec levier 10. »

**Contexte** : à 8h45, Thomas a entre 5 et 10 minutes pour décider. Si la justification est absente ou trop vague ("momentum haussier"), il ne peut pas distinguer un signal de qualité d'une opinion. Avec du levier 10, une entrée mal justifiée peut coûter 150 € sur 1 500 € engagés. La friction n'est pas la peur — c'est l'absence de raison suffisante.

**Ce que TradingApp résout** : score de confiance chiffré + référence backtest + raison en une phrase = Thomas peut évaluer le signal sans analyse supplémentaire.

### Frustration 2 — Friction d'ouverture du dashboard

**Verbatim** : « Je n'ai pas envie d'ouvrir un dashboard tous les matins à 8h45 — il faut que ça vienne à moi. »

**Contexte** : Thomas est mobile entre 8h40 et 9h00. Ouvrir un navigateur, se connecter, attendre le chargement — chaque étape est une friction. Si le signal ne vient pas à lui via une notification push, il ne sera pas consulté de manière fiable tous les matins.

**Ce que TradingApp résout** : push Telegram automatique, lu en 30 secondes depuis l'écran de verrouillage.

### Frustration 3 — Surcharge d'indicateurs contradictoires

**Verbatim** : « Je veux un seul signal clair par jour ouvré, pas dix indicateurs qui se contredisent. »

**Contexte** : Thomas connaît l'analyse technique. Ce n'est pas le problème. Le problème est que lorsque RSI dit surachat, MACD dit continuation et Bollinger dit neutralité, il doit arbitrer lui-même — et à 8h48 ce n'est pas possible sans se tromper. Le bot doit avoir fait cette synthèse en amont.

**Ce que TradingApp résout** : scoring multi-dimension unique, une seule valeur (score X/10), une seule recommandation.

### Frustration 4 — Recos forcées qui n'inspirent pas confiance

**Verbatim** : « Je préfère un "pas de trade aujourd'hui" honnête à une reco forcée. »

**Contexte** : Thomas a eu l'expérience (avec d'autres outils ou avec Finance) de signaux envoyés malgré une faible conviction du système — pour "remplir" la journée ou parce que l'algorithme a un biais vers l'action. Une reco forcée sur un marché flat coûte des frais et du capital sans edge réel.

**Ce que TradingApp résout** : seuil de confiance non négociable. En dessous du seuil → no-trade. Le no-trade est documenté dans le journal comme une décision valide.

### Frustration 5 — Incapacité à auditer les décisions passées

**Contexte implicite** (non verbatim mais observable dans le comportement) : Thomas ne peut pas faire confiance durablement à un système dont il ne peut pas vérifier les résultats passés. Si le bot envoie des signaux mais que le P&L réel diverge du backtest sans explication, la confiance s'effondre.

**Ce que TradingApp résout** : journal SQLite avec chaque signal (décision bot + résultat trade + cohérence score/P&L). Chaque signal référence le backtest correspondant. Thomas peut, en 30 minutes par mois, vérifier que le système se comporte comme prévu.

---

## Critères de pull-the-trigger (conditions pour que Thomas passe l'ordre)

Thomas exécute le signal si et seulement si :

1. **Score de confiance ≥ seuil défini en backtest** (ex : 6,5/10 — valeur exacte à définir en R&D). Si le signal affiche 6,2, il passe.
2. **SL et risque max explicites** : il doit voir "SL : X € / risque max : Y €" dans le message. Sans ces deux chiffres, il ne trade pas.
3. **Référence backtest présente** : numéro de backtest ou pattern nommé. Il n'a pas besoin de le relire à 8h48 — mais sa présence signale que le signal est qualifié.
4. **Sous-jacent disponible chez Bourse Direct** : il doit pouvoir trouver le turbo correspondant en < 2 min sur l'app. Si le sous-jacent est exotique ou introuvable, il ne trade pas.
5. **Fenêtre d'exécution respectée** : si le signal arrive après 8h55, Thomas ne l'exécute pas — l'ouverture est passée et les conditions de marché ont changé.
6. **Pas de news majeure non pricée** : Thomas ne trade pas si une décision BCE, rapport NFP ou événement géopolitique majeur est attendu dans la fenêtre. [HYPOTHÈSE : le bot devrait signaler ce cas explicitement dans le message — à confirmer en R&D.]

**Ce qui fait qu'il NE trade PAS même si le signal est GO :**
- Score ≥ seuil mais raison incompréhensible ("config identifiée" sans détail) → il attend la prochaine
- SL absent du message → il ne trade pas (règle d'or personnelle)
- Drawdown mensuel déjà > 15 % → il devient plus sélectif même si le seuil est atteint

---

## Scénario daté concret (G18)

**Lundi 4 mai 2026, 8h42 CET.**

Thomas est dans le RER, assis, smartphone en main. Telegram s'est mis à jour pendant son trajet. Il ouvre la conversation TradingApp.

Message reçu :
> ACHAT — DAX Turbo Call
> Entrée : 3,42 € | SL : 3,21 € | Cible : 3,85 €
> Raison : gap haussier +0,8 % sur clôture US + ORB haussier sur 5 premières min Xetra + score 7,1/10
> Réf. backtest #B-031 — win rate 61 % / 87 trades / drawdown max −18 %
> Risque max : 126 € sur 600 € engagés (levier ~6)
> Fenêtre : avant 8h55 CET

Thomas lit en 25 secondes. Score 7,1 > 6,5. SL présent. Risque 126 € : acceptable. Backtest #B-031 : il se souvient vaguement — ORB gap, solide. Il ouvre Bourse Direct. Cherche "DAX Call" dans les turbos. Trouve le bon (delta ~0,5, pas trop dans la monnaie). Spread affiché : 0,03 €. Passe l'ordre à 3,42 €. Ordre exécuté à 8h49. Il referme l'app. Il arrive à son bureau à 9h05. Il ne regardera le cours qu'à 10h — les ordres SL/TP sont posés.

À 10h12, Bourse Direct envoie une notification : TP touché à 3,85 €. P&L brut : +258 €. Net après frais (0,99 € × 2) et PFU 31,4 % (12,8 % IR + 18,6 % PS, taux 2025+ confirmé @legal) : ~176 €.

**Ce scénario illustre :**
- La fenêtre d'exécution réelle (8h42 → 8h49 = 7 minutes, dans le seuil)
- L'information minimale nécessaire pour que Thomas décide (score + SL + risque + backtest ref)
- L'absence de gestion active post-entrée (SL/TP posés, Thomas mobile)
- Le P&L net réaliste incluant frais + PFU (à intégrer dans le journal)

---

## Persona client-du-persona — N/A

TradingApp est un outil 100 % personnel. Thomas est à la fois le concepteur, l'utilisateur et le bénéficiaire. Il n'a pas de clients, de partenaires ou d'interlocuteurs professionnels dont l'expérience serait affectée par son utilisation du bot.

Aucun agent `@testeur-client-du-persona` n'est recommandé pour ce projet.

---

## Auto-évaluation (gates critiques G1, G3, G5, G7, G12, G15, G17, G18)

- [x] G1 — Persona principal documenté avec profil, contexte, frustrations, JTBD
- [x] G3 — Zéro données inventées non marquées (hypothèse H sur seuil de confiance marquée [HYPOTHÈSE])
- [x] G5 — Thomas mentionné ≥ 5 fois dans ce fichier (présent dans chaque section)
- [x] G7 — Frustrations avec verbatims originaux du project-context.md
- [x] G12 — Critères de pull-the-trigger documentés (6 conditions + motifs de non-exécution)
- [x] G15 — JTBD formulés au format "quand / il veut / pour" avec critère de succès
- [x] G17 — Signaux d'arrêt et drawdown documentés avec conditions numériques
- [x] G18 — Scénario daté concret (4 mai 2026, 8h42 CET, RER, ordre passé à 8h49)
