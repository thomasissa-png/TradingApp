# Audit Elon — TradingApp v3 (premiers principes, brutal)

> AVIS CONSULTATIF. 30/05/2026. Lu : README, ACTIVATION, RECO-ARCHI, ANALYSE-PROMPT-v2, survol scripts + fiches.

## La question à 1 ligne
Est-ce un EDGE pour un retail à exécution manuelle, ou de l'ingénierie qui *ressemble* à un edge ?
**Réponse : aujourd'hui, ça ressemble à un edge. La preuve d'un edge réel n'existe pas encore — et le design rend cette preuve difficile à obtenir.**

## Le piège du pivot a-t-il été contourné ? Non, reconstruit en plus gros.
Le pivot disait : « edge informationnel ≈ nul sur sources publiques ». Vrai. La parade construite, c'est :
RSS publics (BBC/CNBC/Investing) → DeepSeek → triplets directionnels. C'est **exactement la même source publique**, juste passée dans un LLM qui ajoute de la latence, pas de l'information. Une news que tu lis à 7h via BBC RSS est déjà dans le prix depuis la veille au soir. Tu ne bats pas le marché avec une info que tout le monde a, structurée 4h plus tard. L'edge ne peut PAS venir des news publiques. S'il existe, il vient du **scoring multi-critères macro/prix structuré** — et ça, le système le fait aussi. Donc : la moitié news = théâtre, la moitié scoring = peut-être de la valeur.

## Théâtre vs Valeur
| Brique | Verdict | Pourquoi |
|---|---|---|
| 26 sources / blacklist / dédup Jaccard | THÉÂTRE | sources publiques, lag structurel, no edge informationnel |
| Prompt v2 8 dimensions DeepSeek | 80% THÉÂTRE | ton propre audit le dit : 4/8 dimensions jetées, `confidence` 0-100 ignorée, triplet final = ±1 fixe. Tu paies des tokens pour du signal non consommé |
| Pondération A/B materiality×reliability | THÉÂTRE tant que non mesuré | pondérer un signal dont on n'a pas prouvé le lift = polir du bruit |
| Scoring déterministe 114 critères / prix+macro | VALEUR POTENTIELLE | seul endroit où un edge est plausible (mean-reversion, régimes macro). Mais 30% des critères restent `n/a` (pas d'API) |
| Journaliste / Brier / git-as-storage | VALEUR | la mesure honnête est la meilleure pièce du système. C'est ce qui te dira la vérité |

## Le KPI 70% : on se ment
- **36 cellules × 3 cycles/jour ≈ 108 prédictions/jour.** Pour qu'une cellule atteigne 30 conclusions terminées (seuil Brier), il faut du temps — OK.
- **Le seuil de réussite est l'arnaque cachée.** Fiche Or : 24h = 0,5% de mouvement. Un actif liquide bouge de >0,5% en 24h **par pur bruit** ~50% du temps dans le bon sens. Atteindre 70% directionnel sur un seuil aussi bas, c'est demander de prédire le bruit. Soit le seuil est trop bas (tu mesures du coin-flip), soit 70% est inatteignable. **70% directionnel soutenu sur 36 cellules est, en finance, un niveau de hedge fund quant top-décile.** Un retail avec des RSS publics ne l'atteint pas. Si tu l'atteins en shadow, suspecte un biais de mesure avant de fêter.
- Brier < 0,25 est trivial à atteindre (0,25 = coin-flip à proba 0,5). Mauvais garde-fou. **Ton vrai KPI doit être Brier < 0,20 ET réussite > 60% sur ≥100 conclusions/cellule.**

## Risque n°1 + test le moins cher
**Risque n°1 : le système produit 70% de cellules `n/a`/neutres/coin-flip et tu confonds "ça tourne" avec "ça prédit".** Le shadow va te donner des chiffres qui *ressemblent* à du signal alors que c'est du bruit échantillonné.
**Test le moins cher (1 journée, zéro nouvelle ligne de code) :** backtest "papier" sur les 90 derniers jours. Tu as les fiches + Twelve Data historique. Calcule le bulletin qu'AURAIT produit le système chaque jour des 90 derniers, mesure réussite + Brier rétroactivement. Si < 60% sur du data passé que tu connais déjà → le live ne fera jamais mieux. **Tu sauras en 1 jour ce que le shadow te dirait en 90.** Fais ça AVANT de lancer le shadow.

## Si je coupe encore 50%
1. **Couper toute la couche news/LLM** (extractor, news_collector, agent_news, 26 sources, prompt v2). Edge informationnel nul prouvé par toi-même. -50% de complexité, -tokens, -surface de bug. Tu le rallumes UNIQUEMENT si le backtest montre que les critères événementiels ajoutent du lift de Brier.
2. **Couper les 30% de critères `n/a`** (AAII, ETF, breadth, WGC…). Un critère à poids 0 est une fiche morte qui donne l'illusion de richesse.
3. Garder : scoring déterministe sur prix+macro structurée + Journaliste + git-storage. C'est le seul candidat-edge testable.

## Modèles mentaux
- **First principles** : l'info publique ne crée pas d'alpha. Seule une asymétrie de *traitement* (modèle de régime macro) le peut. Le système confond les deux.
- **Kill criterion (manquant !)** : la reco disait « écris-le AVANT le shadow ». Il n'est toujours pas écrit. Inacceptable. Sans seuil d'arrêt, un projet qui ne marche pas tourne 18 mois.
- **Opportunity cost** : chaque semaine sur le pipeline news = une semaine pas passée à prouver/réfuter l'edge de scoring.

## Hypothèses à valider
- [HYPOTHÈSE] Aucun backtest historique n'a été fait — la perf prédictive est totalement inconnue. À confirmer avec Thomas.
- [HYPOTHÈSE] Le kill criterion n'est pas écrit.
