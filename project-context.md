# Contexte Projet — TradingApp

> Ce fichier est lu par tous les agents avant toute action.
> **ATTENTION** : ce fichier contient des informations financières personnelles (capital, P&L). **Le repo doit rester privé.**
> Dernière mise à jour : 2026-05-01

> **Scope MVP en une phrase** : *Bot Telegram qui envoie un signal turbo par jour ouvré à 8h45-8h55 CET, justifié et backtesté, exécutable manuellement chez Bourse Direct.*

---

## Identité
- **Nom du projet** : TradingApp (provisoire — peut être renommé après MVP)
- **URL (si existante)** : N/A — outil interne, pas de domaine public
- **Secteur** : Day-trading turbos personnel — fenêtre d'ouverture EU
- **Stade** : [x] Idée  [ ] V1  [ ] Production  [ ] Croissance
- **Date de début** : 2026-05-01

---

## Cible
- **Persona principal** : Thomas — trader particulier expérimenté, résident France, dispo entre 8h45 et 9h CET chaque jour ouvré, exécution manuelle chez Bourse Direct (CTO), capital dédié 20-30 k€, levier 5-20 sur turbos, taille de position 1000-2000 € par trade.
- **Problème principal** : Pas de signal d'ouverture **justifié, backtesté, et poussé sur le bon canal** pour engager du capital avec levier en confiance. Les outils existants soit sont des dashboards à ouvrir activement (friction), soit ne fournissent pas une justification suffisante pour engager 1500 € avec levier 10.
- **Alternative actuelle** : Trader manuellement au feeling, ou ne pas trader du tout. Le projet `thomasissa-png/Finance` (multi-agents Python) n'est pas utilisé : recos pas assez justifiées + dashboard à ouvrir activement.
- **Persona secondaire** : N/A (outil 100 % personnel)
- **Verbatims persona** :
  - « Quand je vois un signal du Finance, je n'ai pas assez d'éléments pour engager 1500 € avec levier 10. »
  - « Je n'ai pas envie d'ouvrir un dashboard tous les matins à 8h45 — il faut que ça vienne à moi. »
  - « Je veux un seul signal clair par jour ouvré, pas dix indicateurs qui se contredisent. »
  - « Je préfère un "pas de trade aujourd'hui" honnête à une reco forcée. »

---

## Positionnement
- **Promesse unique** : Un signal turbo par jour ouvré à 8h45-8h55 CET, **justifié** (entrée + SL + TP + raison + score de confiance + référence backtest) et **backtesté sur 5 ans**, livré sur Telegram, exécutable en moins de 5 min chez Bourse Direct.
- **Ton de marque** : Factuel, sans bullshit, transparent sur l'incertitude (probabilités plutôt qu'affirmations). Pas de "buy now / strong signal" sans chiffres.
- **3 mots qui DÉFINISSENT la marque** : Justifié · Concis · Backtesté
- **3 mots qui ne DÉFINISSENT PAS la marque** : Generic · Hype · Boîte noire
- **Concurrent principal** : N/A (outil personnel non commercialisé)
- **Notre différence clé vs lui** : N/A. Références d'inspiration (pour le format) : TradingView alerts (push court), Trade Ideas (justification structurée).

---

## Objectifs
- **Objectif principal à 6 mois** : Edge identifié + backtesté sur 5 ans d'historique + 4-8 semaines de paper-trading concluant (signaux Telegram tradés en simulé, journal complet).
- **KPI North Star** : **P&L net mensuel** après frais (turbos Bourse Direct ~0,99 € + spread émetteur) et fiscalité PFU 30 %.
- **Objectif secondaire** : Drawdown mensuel max < 20 % du capital dédié sur la période de paper-trading + live.
- **Ce que le succès ressemble à 12 mois** : Bot en live, signal Telegram quotidien fiable, P&L net positif sur ≥ 3 mois consécutifs, drawdown maîtrisé, audit du journal des trades < 30 min/semaine.

---

## Stack technique
- **Frontend** : [ ] Next.js  [ ] React  [ ] Expo/React Native  [x] Aucun (bot Telegram, pas de UI web)
- **Backend** : *À arbitrer T0+1 par @fullstack* — Python (continuité Finance, libs trading riches : pandas, vectorbt, backtesting.py) vs Node/Bun + TypeScript (léger, moderne, bot Telegram natif).
- **Base de données** : SQLite minimal pour le journal trades + résultats backtest. Postgres Replit en option si volume R&D le justifie.
- **Authentification** : N/A (un seul utilisateur, identifié par chat_id Telegram)
- **Hébergement** : Replit always-on, déclencheur cron jours ouvrés à 8h40 CET (calcul signal à 8h45-8h55).
- **Outils IA utilisés** : Anthropic Claude (Sonnet ou Haiku selon coût/qualité — à arbitrer en R&D) pour scoring multi-dimension du signal et génération de la justification structurée envoyée sur Telegram.
- **Budget IA mensuel (tokens)** : < 10 €/mois estimé en live (1 appel Claude par signal × 22 jours ouvrés). Phase R&D potentiellement plus consommatrice (à monitorer).
- **Volume d'usage IA prévu** : ~22 appels/mois en live (1 par jour ouvré). 100-500 appels/jour pendant la phase R&D edge.
- **Latence IA cible** : signal calculé en moins de 60 s entre 8h45 et 8h55, push Telegram immédiat. Pas de streaming nécessaire.
- **Outils d'analytics** : Journal interne des trades (MAE/MFE/win rate/drawdown) — pas de Google Analytics ni Mixpanel.
- **Données de marché** : **Twelve Data** (compte payant déjà actif) — multi-asset (indices EU, actions FR, FX, commodities), intraday 1m, historique multi-années.

---

## Modèle économique et juridique
- **Modèle économique** : [x] Autre — Outil interne personnel, non commercialisé, jamais redistribué.
- **Pays de commercialisation** : N/A (usage personnel France)
- **Données sensibles collectées** : [x] Oui — finance personnelle (capital, P&L, journal trades). **Repo doit rester privé sur GitHub.**
- **Utilisation d'IA générative** : [x] Oui — Claude pour scoring du signal et rédaction de la justification livrée sur Telegram.
- **Cadre AMF / MiFID II** : non concerné (pas de conseil en investissement à des tiers, pas de redistribution des signaux).

---

## Contraintes
- **Budget mensuel infrastructure** : Replit (~7-25 €/mois selon plan retenu).
- **Budget mensuel acquisition** : 0 € (outil personnel, pas de marketing).
- **Budget analytics** : 0 € (journal interne SQLite suffit).
- **Budget données de marché** : Twelve Data déjà payé (à vérifier que le plan actuel couvre les besoins — voir hypothèse H2).
- **Budget IA** : < 10 €/mois en live, à monitorer en phase R&D.
- **Timeline de lancement** : Pas d'échéance commerciale. Phase R&D edge = priorité absolue, pas de pression de livraison. **Si l'edge n'est pas trouvé / pas robuste, accepter le no-go plutôt que de sur-fitter.**
- **Contraintes légales ou sectorielles** : Repo privé obligatoire. Aucune obligation AMF tant que l'usage reste personnel.
- **Ressources disponibles** : [x] Solo — toi + agents Gradient (orchestrator, fullstack, data-analyst, qa, ia, reviewer, etc.)

---

## Existant (projets en place uniquement)
- **URL du site actuel** : N/A
- **Comptes sociaux existants** : N/A (outil perso)
- **Outils analytics en place** : N/A
- **Contenu existant** : N/A
- **Historique SEO** : N/A
- **Repo de référence (à NE PAS confondre avec ce projet)** : `https://github.com/thomasissa-png/Finance` branche `claude/review-indicators-timeframe-0XR8K`. Stack : Python/FastAPI, React/Vite, PostgreSQL, Twelve Data, yfinance, APScheduler, Anthropic Claude, 21 agents en 4 teams (news intraday, commodity trend, indicateurs techniques, méta-confluence). **Non utilisé** par le persona — friction "pas confiance" + "pas le bon canal".

### Héritage Finance — quoi reprendre / quoi jeter

| Garde | Jette |
|---|---|
| Journal MAE/MFE + tracker performance (générique, robuste) | Architecture 4 teams + méta-team Team 4 |
| Scoring news Claude + catégorisation (piste edge "news pré-marché") | Scheduler 4 scans/jour à 07:50/11:15/14:50/17:00 |
| Lib indicateurs techniques (RSI / MACD / Bollinger / EMA) | Dashboard React (on est sur Telegram pur) |
| Intégration Anthropic Claude (SDK + prompts scoring) | Monitors positions toutes les 15-30 min |
| Intégration Twelve Data SDK | 17 APIs structurées EIA/USDA/NOAA (overkill pour scope EU 8h45) |

---

## Hypothèses à valider en T0+1

| # | Hypothèse | Action |
|---|-----------|--------|
| H1 | Plan Replit Hacker (~7 €/mois) suffit pour always-on + cron quotidien | @infrastructure audit besoins |
| H2 | Twelve Data plan actuel couvre indices EU + actions FR + FX + commodities en intraday 1m sur 5 ans | Vérifier le plan dans ton compte Twelve Data |
| H3 | Bourse Direct propose des turbos sur tous les sous-jacents retenus (CAC40, DAX, EuroStoxx50, blue chips FR, EUR/USD, or, brent, gaz) | Parcourir le catalogue Bourse Direct |
| H4 | 1 appel Claude / signal × 22 jours = budget IA marginal en live | À monitorer en phase R&D pour ne pas exploser |

---

## Décisions structurantes (règles d'or, ne pas dévier)

1. **Un seul signal par jour ouvré** — pas de multi-scan, pas de multi-team. Lisibilité maximale.
2. **Signal "no-trade" autorisé et explicite** — si aucune config ne dépasse le seuil de confiance, envoyer « pas de trade aujourd'hui » plutôt qu'une reco forcée.
3. **Justification obligatoire dans chaque alerte Telegram** : sous-jacent + sens + niveau d'entrée + SL + TP + raison + score de confiance + référence backtest. Levier n°1 pour résoudre la friction "pas confiance".
4. **R&D edge AVANT tout code de prod** : exploration de plusieurs hypothèses (gap follow / gap fade, Opening Range Breakout, momentum overnight US→EU, news pré-marché, écart spot/futures, sentiment overnight Asie) sur 5 ans d'historique Twelve Data.
5. **Backtest exhaustif obligatoire avant un seul euro réel** — pas de live au feeling. Période de paper-trading 4-8 semaines minimum après backtest.
6. **Pas de réintroduction de complexité Finance** sans justification claire (chaque module repris doit servir l'edge retenu, pas être copié par habitude).

---

## Historique des interventions agents

> Ce tableau est le journal de bord du projet. Chaque agent DOIT le compléter après chaque livrable.
> La colonne "Pourquoi" est obligatoire : elle capture le raisonnement, pas juste la décision.
> Tout agent démarrant une session DOIT lire ce tableau pour comprendre les décisions passées et leur justification.

| Agent | Date | Livrable produit | Décisions clés | Pourquoi / Alternatives écartées |
|-------|------|-----------------|----------------|----------------------------------|
| @orchestrator (cadrage) | 2026-05-01 | `project-context.md` rempli via 5 vagues de questions au persona | Bot Telegram, alerte simple, signal 8h45-8h55, scalp 5-20 min, Twelve Data, Bourse Direct, 20-30 k€, edge à trouver | Écarté : exécution auto via API broker (sécu MVP perso), dashboard web (n'a pas résolu friction Finance), réutilisation pleine du Finance (dette technique) |
| @orchestrator (plan) | 2026-05-01 | `docs/orchestration-plan.md` (plan Phases 0→5 + 6 prompts pré-rédigés Phase 0) | Phase 1 R&D edge structurante (Phase 2 conditionnelle), Phase 2d testeur-client N/A justifié (perso 100%), boucle visuelle adaptée messages Telegram, @sales-enablement transposé en runbook usage perso, @growth en rapport mensuel auto, SEO N/A justifié | Écarté : ordre standard Phase 3 contenu web (pas de site), invocation Tasks directement (sub-agent sans accès Task → prompts pré-rédigés relayés au top-level) |

---

## Performance des agents

> Rempli par l'agent après livraison, validé/corrigé par @reviewer.
> Un agent avec 2+ interventions à <3/5 en spécificité → son prompt doit être revu.

| Agent | Date | Livrable | Complétude | Cohérence | Actionnabilité | Messages | Spécificité | Notes |
|-------|------|----------|------------|-----------|----------------|----------|-------------|-------|
| @orchestrator | 2026-05-01 | project-context.md | 5 | 5 | 5 | 5 | 5 | Cadrage initial via 5 vagues de questions ciblées au persona, hypothèses H1-H4 explicites |
| @orchestrator | 2026-05-01 | docs/orchestration-plan.md | 5 | 5 | 5 | 5 | 5 | Plan Phases 0→5 adapté TradingApp (Telegram pur, perso 100%), 6 prompts Phase 0 pré-rédigés, checkpoint persona explicite après Phase 0 |

**Légende (échelle 1-5 alignée avec CLAUDE.md) :**
- **Complétude** : 1 (sections manquantes) → 3 (sections principales couvertes) → 5 (tout rempli, rien à ajouter)
- **Cohérence** : 1 (contredit des livrables existants) → 3 (pas de contradiction) → 5 (référence explicitement les livrables amont)
- **Actionnabilité** : 1 (trop vague) → 3 (implémentable avec interprétation) → 5 (directement implémentable, zéro ambiguïté)
- **Messages** : 1 (silencieux sur les manques) → 3 (a signalé certains manques) → 5 (a signalé tous les manques, hypothèses marquées)
- **Spécificité** : 1 (générique) → 3 (partiellement spécifique) → 5 (100% taillé pour ce projet)

---

## Notes libres

- **Risque anti-pattern n°1 — re-overengineering** : tentation de coder backtester + R&D edge + bot en parallèle. Discipline : R&D edge → backtester → bot Telegram → live, **en série**. La dette technique du Finance vient de la parallélisation prématurée.
- **Risque anti-pattern n°2 — edge "trop subtil"** : si le backtest ne donne aucun edge robuste sur 5 ans, accepter le no-go. Mieux vaut pas de bot qu'un bot qui fait perdre 2-3 k€/mois.
- **Risque anti-pattern n°3 — Twelve Data limites de rate** : intraday 1m sur 5 ans × N tickers peut taper le rate limit. À vérifier avant d'engager la R&D.
- **Préférence canal** : Telegram (push instantané, archivable, pas de friction d'ouverture). Discord acceptable en alternative.
- **Style des messages Telegram** : court mais structuré. Format à designer en T0+2 (probable : ligne de tête « ACHAT/VENTE [SOUS-JACENT] @ [PRIX] » + bloc justification 4-6 lignes + score de confiance 1-10 + lien vers fiche détaillée si besoin).
- **Prochaine étape suggérée** : invoquer `@orchestrator` pour planifier les phases R&D edge → backtester → bot, puis `@fullstack` pour arbitrer Python vs Node/Bun.
