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

## Produit (spécifique TradingApp, mais révèle son mindset)

- [PRÉFÉRENCE FONDATEUR] : Objectif **non négociable = justesse de TENDANCE** (trend-following directionnel), PAS la vitesse de capture des news. Un retard de 4h sur une news n'est pas grave. Tout raisonnement qui optimise la *vitesse* est hors-sujet.
- [PRÉFÉRENCE FONDATEUR] : **Zéro invention de donnée** — source absente → n/a, jamais combler. Et **zéro modification silencieuse** des poids/seuils/prompts (changelog + validation).
- [PRÉFÉRENCE FONDATEUR] : Thomas valide **uniquement en conditions réelles (shadow live)** — le **backtest ne l'intéresse pas** (rejeu historique news-blind, ne capte pas la valeur réelle du système, qui vient de la couche news). Seuls comptent les **bulletins réels mesurés en forward** (boucle prédiction→mesure, KPI > 70 % / Brier < 0,25). Ne plus proposer le backtest comme jalon ni relancer dessus.
