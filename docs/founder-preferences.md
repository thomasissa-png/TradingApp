<!-- Source de vérité CROSS-PROJETS des préférences fondateur. Lu par l'orchestrator au démarrage de toute session (WebFetch raw GitHub). -->
# Préférences fondateur — Thomas

> Format : `[PRÉFÉRENCE FONDATEUR] : Thomas préfère X à Y parce que Z`. Une ligne par observation.
> Mis à jour en fin de session (étape 5b du protocole de clôture). Prioritaire sur les autres learnings en cas de conflit.

## Communication & pilotage

- [PRÉFÉRENCE FONDATEUR] : Thomas veut qu'on **réponde à la question posée**. S'il demande un chiffre précis, donner le chiffre **direct** (puis le contexte), pas du contexte qui noie la réponse. Frustration explicite sinon (« tu n'as pas répondu à ma question »).
- [PRÉFÉRENCE FONDATEUR] : Thomas préfère **l'honnêteté brutale au spin** — verdict NO-GO assumé, point d'attention signalé tel quel, jamais enrobé. Il **refuse les demi-traitements silencieux** (tester/livrer sur la moitié d'un périmètre sans le dire = « tu fais de travers »).
- [PRÉFÉRENCE FONDATEUR] : Thomas n'aime ni la **sur-sollicitation** (trop d'AskUserQuestion, trop d'agents lancés) ni le **sur-cadrage**. Quand un défaut est évident → trancher et avancer. Quand il demande une reco → donner **UNE reco argumentée**, pas un menu A/B/C.

## Méthode & décision

- [PRÉFÉRENCE FONDATEUR] : Thomas privilégie **« mesurer avant d'agir »** — différer une action (ex. Lot 4b gates) pour calibrer ses seuils sur la **fréquence réelle mesurée** plutôt que sur une intuition. Anti-calibration au doigt mouillé.
- [PRÉFÉRENCE FONDATEUR] : Thomas valorise la **concertation contradictoire de 3 experts** (Analyst / News Trader / Spéculateur, chacun conteste les autres) + **itération jusqu'à une note cible** (ex. 10/10) comme mécanisme de décision de conception. À réutiliser pour tout arbitrage à fort enjeu.
- [PRÉFÉRENCE FONDATEUR] : Thomas veut des **garde-fous explicites à chaque étape clé** pour éviter les erreurs de jugement, et qu'ils soient **visibles** (affichés, pas seulement loggés). Le système doit « savoir quand ne pas se faire confiance, et le montrer ».
- [PRÉFÉRENCE FONDATEUR] : Thomas exige qu'on **vérifie sur pièces (données réelles) AVANT d'affirmer** — il rejette frontalement les explications théoriques sorties de mémoire (« ton analyse est fausse », 16/06). Concéder vite et re-vérifier quand il conteste, plutôt que défendre. Il **pousse jusqu'à la cause racine** : il insiste/reformule tant qu'une incohérence n'est pas expliquée par les chiffres.
- [PRÉFÉRENCE FONDATEUR] : Thomas **confronte les chiffres du système à son broker live** ; un écart système↔réalité = signal d'alarme à **investiguer sur pièces**, jamais à expliquer/minimiser. Son instinct sur les données s'est révélé juste 3× (or 11/06, 15/06, source futures).
- [PRÉFÉRENCE FONDATEUR] : le système doit être **HONNÊTE sur ses angles morts** — afficher un ⚠️ quand il décide sur une donnée potentiellement périmée, plutôt que recommander en silence contre un mouvement visible à l'écran (« c'est pas malin », 15/06). L'affichage doit refléter la réalité observable par le trader.

## Produit (spécifique TradingApp, mais révèle son mindset)

- [PRÉFÉRENCE FONDATEUR] : Objectif **non négociable = justesse de TENDANCE** (trend-following directionnel), PAS la vitesse de capture des news. Un retard de 4h sur une news n'est pas grave. Tout raisonnement qui optimise la *vitesse* est hors-sujet.
- [PRÉFÉRENCE FONDATEUR] : La seule métrique qui compte = le **WIN RATE** (taux de bonnes directions). Thomas **se fiche du P&L / argent gagné / expectancy / amplitude / equity** — répété de multiples fois, NE JAMAIS reproposer une mesure de gain. « La direction était-elle juste ? » oui/non, point. (Mesurer l'amplitude pour seuiller VRAI/FAUX est OK ; mesurer « combien ça rapporte » est hors-sujet.)
- [PRÉFÉRENCE FONDATEUR] : **Zéro invention de donnée** — source absente → n/a, jamais combler. Et **zéro modification silencieuse** des poids/seuils/prompts (changelog + validation).
- [PRÉFÉRENCE FONDATEUR] : Thomas valide **uniquement en conditions réelles (shadow live)** — le **backtest ne l'intéresse pas** (NO-GO sur 2 itérations, et rejeu price/news-blind qui ne reflète pas le système réel). Seuls comptent les **rapports réels mesurés en forward** (boucle prédiction→mesure, win rate). Ne plus proposer le backtest comme jalon ni relancer dessus.
- [PRÉFÉRENCE FONDATEUR] : Le **CŒUR du système = la TENDANCE** (critères numériques : prix, momentum, COT). Les **news sont du CONTEXTE secondaire**, pas le moteur. Ne PAS survendre la couche news comme « là où est l'edge » (recadrage Thomas 09/06) — toute amélioration news doit SERVIR la tendance (nettoyer le bruit), jamais la renverser.
- [PRÉFÉRENCE FONDATEUR] : Thomas consomme la **PAGE rendue** (HTML), pas l'arborescence de fichiers. Toute nouvelle sortie (rapport, tableau) doit être **visible sur la page** dans la même livraison, sinon « elle n'existe pas » pour lui (incident 09/06 : 5 rapports produits mais invisibles). Penser UX/affichage, pas seulement backend.
