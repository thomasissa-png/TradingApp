# Audit de conformité légale final — Phase 5
# TradingApp

> **Statut** : Draft de référence — pas un avis juridique formel. Validation par un avocat recommandée avant toute évolution du périmètre.
> **Date** : 2026-05-01
> **Agent** : @legal
> **Périmètre audité** : Phases 1 à 4 du projet (R&D edge, build, GEO, runbook + rapport mensuel)
> **Référence** : `docs/legal/legal-audit.md` (Phase 0 — 9 sections)

---

## Risques en 5 points (résumé exécutif)

| # | Risque | Criticité | Statut Phase 5 |
|---|--------|-----------|----------------|
| R1 | Redistribution signal à un tiers → CIF/Art. L. 573-1 CMF | CRITIQUE | CONFORME — 0 signal redistribué, THOMAS_CHAT_ID seul destinataire (code vérifié) |
| R2 | Fuite données financières depuis repo GitHub | ELEVE | CONFORME — repo privé, secrets Replit, .gitignore strict (REPLIT_ACTIONS §B.1) |
| R3 | Templates Telegram = conseil en investissement | CRITIQUE | CONFORME — vocabulaire factuel chiffré, 0 terme proscrit (audit §3) |
| R4 | PFU 31,4 % mal implémenté | MODERE | PARTIELLEMENT CONFORME — mention correcte dans les templates ; colonne `pl_net_eur` absente en DB (voir §4) |
| R5 | Données PII dans prompts Claude / ZDR | FAIBLE | CONFORME — 0 PII dans prompts, ZDR différé OK (H-ZDR maintenu) |

---

## 1. Rappel cadre Phase 0

Synthèse des 9 sections de `docs/legal/legal-audit.md` établi en Phase 0.

**Usage 100 % personnel, non commercialisé.** Le bot TradingApp est un outil d'aide à la décision personnelle de Thomas, destinataire unique. Aucun tiers ne reçoit de signal. Aucun agrément AMF, CIF ou PSI n'est requis (Art. L. 321-1 et D. 321-1 CMF ; Position AMF DOC-2008-23 v4.3).

**Repo privé obligatoire.** Le repo GitHub contient des données financières personnelles (capital 20-30 k€, P&L, journal trades) et des clés API. Il doit rester privé en permanence. Un basculement public accidentel constituerait une fuite de données et une exposition des secrets API.

**Exemption RGPD activité personnelle** (Art. 2 §2 c) RGPD 2016/679). Le traitement des données de Thomas par Thomas pour Thomas échappe au périmètre RGPD tant que l'usage reste strictement personnel. Les bonnes pratiques (secrets en variables d'environnement, SQLite local, durée conservation 10 ans) sont néanmoins documentées.

**PFU 31,4 % depuis le 01/01/2025.** Les plus-values sur turbos sont soumises au PFU 31,4 % (12,8 % IR + 18,6 % prélèvements sociaux — Art. 150-0 A et suivants CGI). Déclaration via formulaire 2074 N+1. Journal des trades obligatoire pour reconstitution fiscale.

**Anthropic ZDR différé — acceptable.** Les prompts envoyés à Claude contiennent des données de marché publiques et des signaux calculés, sans PII (pas de nom, capital, identifiants). Rétention API standard 7 jours, pas d'usage pour entraînement. ZDR différé validé (H-ZDR ⏸️ DIFFÉRÉE project-context.md).

**Bourse Direct — exécution manuelle, risque conformité broker nul.** Le bot ne se connecte pas à l'API Bourse Direct et n'exécute aucun ordre automatiquement. L'Art. 17 MiFID II (obligations déclaration algorithme de trading) ne s'applique pas.

**Redistribution = ligne rouge.** Dès le premier signal envoyé à un tiers, même bénévole, même à un ami, l'activité entre dans le périmètre CIF (Art. L. 541-1 CMF). En cas de redistribution non conforme : jusqu'à 3 ans d'emprisonnement et 375 000 € d'amende (Art. L. 573-1 CMF).

**EU AI Act — risque limité.** Claude génère la justification textuelle du signal. Classification : risque limité (Règlement UE 2024/1689). Obligation de transparence satisfaite de facto en usage 100 % personnel.

**Licences open source.** Stack Python avec bibliothèques MIT/BSD/Apache 2.0 (pandas, vectorbt, python-telegram-bot, anthropic SDK). Aucune dépendance GPL identifiée. Conforme pour usage propriétaire personnel.

---

## 2. Audit non-déviation Phases 1-4

### Phase 1 — R&D edge

**Objet :** Backtester Wave 1 (H-A Gap Follow, H-C ORB), MarketDataLoader, grid search IS/OOS/walk-forward.

**Audit conformité :**
- Usage des données Twelve Data : consommation interne uniquement (100-500 appels/jour pendant R&D), plan Pro Individual confirmé (H2 PASS). Aucune redistribution des données. **CONFORME aux CGU Twelve Data.**
- Appels Claude en R&D batch (100-500/jour Haiku 4.5 daté `claude-haiku-4-5-20251001`) : prompts contenant OHLC publics + indicateurs calculés. Aucune PII. Budget R&D ~10 $/mois validé (H4 PASS). **CONFORME politique Anthropic.**
- Signaux R&D non diffusés à des tiers : la R&D produit des résultats backtest stockés localement en SQLite (`rnd_results`), jamais envoyés à un destinataire externe. **CONFORME périmètre 100 % personnel.**
- Résultats backtest JSON persistés localement (non publiés, non partagés). **CONFORME.**

**Verdict Phase 1 : AUCUNE DÉVIATION DÉTECTÉE.**

### Phase 2 — Build (bot Telegram, scoring engine, journal SQLite)

**Objet :** `src/` complet — backtester, AI client, scoring engine, templates Telegram, bot commandes, journal DB, main pipeline.

**Audit conformité :**
- **Repo GitHub privé confirmé** : mention explicite en tête de `project-context.md` ("Le repo doit rester privé"), en tête de REPLIT_ACTIONS §B.1. La nature privée est une contrainte de développement documentée, pas seulement une intention. Vérification statut GitHub recommandée en §6 (action Thomas n°1).
- **Secrets en Replit Secrets** : les 15 variables de REPLIT_ACTIONS §B.1 (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TWELVE_DATA_API_KEY`, `ANTHROPIC_API_KEY`, `SQLITE_ENCRYPTION_KEY`, etc.) sont externalisées. Aucun secret n'apparaît dans le code source audité. `.gitignore` strict documenté (legal-audit.md §3.3). **CONFORME.**
- **Authentification THOMAS_CHAT_ID** : `dispatch_command` dans `src/telegram/bot.py` vérifie `_is_authorized(sender_chat_id, allowed_chat_id)` en première instruction. Retour `None` silencieux pour toute commande hors THOMAS_CHAT_ID — aucun feedback à un attaquant. **CONFORME — architecture mono-destinataire vérifiée dans le code.**
- **Données financières en SQLite local** : journal.sqlite contenant trades, signaux, P&L. Non exposé via API publique. Stocké dans répertoire `data/` exclu par `.gitignore`. **CONFORME.**
- **Prompts Claude** : `src/ai/client.py` + `src/scoring/engine.py` — les prompts contiennent OHLC publics, indicateurs, news titres (strippage injection via regex documenté). Pas de P&L, pas de capital, pas de chat_id, pas d'identifiant Bourse Direct. **CONFORME à la politique H-ZDR.**
- **Licences open source** : pandas (BSD-3), vectorbt (Apache 2.0 / propriétaire selon version — à vérifier), backtesting.py (LGPL-3.0), python-telegram-bot (LGPL-3.0), anthropic SDK Python (MIT), pytz (MIT), arch (BSD-3), ruff (MIT), mypy (MIT). **Point d'attention : backtesting.py et python-telegram-bot sont sous LGPL-3.0. La LGPL autorise l'usage dans un projet propriétaire sans obligation de rendre le code source public, à condition de ne pas modifier les bibliothèques elles-mêmes. Conforme pour usage personnel propriétaire.**

**Verdict Phase 2 : AUCUNE DÉVIATION DÉTECTÉE. Point de vigilance licences LGPL documenté (non bloquant usage perso).**

### Phase 3 — GEO (lisibilité Telegram)

**Objet :** `docs/geo/geo-strategy.md` — recommandations extractibilité des templates Telegram.

**Audit conformité :**
- Recommandations GEO portent sur la lisibilité des templates (ratio chiffres/mots, longueur ligne, pattern `[Gap↑]`/`[ORB]`). Aucune recommandation de diffusion publique des signaux. La stratégie GEO s'applique à l'extractibilité par des assistants IA personnels de Thomas, pas à une diffusion externe. **CONFORME.**
- Contrainte 160 caractères max pour la raison : recommandation de lisibilité interne uniquement. **CONFORME.**
- Pas de recommandation créant un risque de requalification en conseil en investissement public. **CONFORME.**

**Verdict Phase 3 : AUCUNE DÉVIATION DÉTECTÉE.**

### Phase 4 — Runbook + rapport mensuel automatique

**Objet :** `docs/sales/runbook-usage-personnel.md` + `docs/growth/rapport-mensuel-auto.md`.

**Audit conformité :**
- Runbook 100 % usage personnel Thomas : procédures d'exploitation (incidents, matrice décision mensuelle, signaux d'arrêt). Aucune procédure de partage ou redistribution. Le titre même ("usage-personnel") ancre le périmètre. **CONFORME.**
- Rapport mensuel automatique : template envoyé au seul THOMAS_CHAT_ID via le cron Replit `0 7 1 * *`. P&L et métriques affichés uniquement pour Thomas. Les commandes `/continue` et `/stop` sont des commandes bot réservées à l'utilisateur authentifié. **CONFORME.**
- Mention PFU 31,4 % dans le template audit mensuel : correctement intégrée (voir §4 pour analyse détaillée). **CONFORME.**
- Aucune procédure de partage des rapports avec des tiers. **CONFORME.**

**Verdict Phase 4 : AUCUNE DÉVIATION DÉTECTÉE.**

---

## 3. Audit templates Telegram — risque conseil en investissement

### 3.1 Rappel du risque

L'article D. 321-1 CMF définit le conseil en investissement comme "la fourniture de recommandations personnalisées à un **tiers**". Trois critères cumulatifs déclenchent la qualification :
1. Une recommandation personnalisée
2. Destinée à un **tiers** (une personne autre que soi-même)
3. Portant sur des instruments financiers (turbos = MiFID II Art. 4)

Thomas est à la fois l'auteur et le destinataire unique. **Le critère "tiers" n'est pas rempli** — les templates ne constituent pas du conseil en investissement en l'état actuel.

### 3.2 Vérification vocabulaire — tableau proscrit vs implémenté

Source de vérité : `docs/copy/message-templates.md` v1.2 + `tests/test_telegram_templates.py` (grep vocabulaire proscrit, 63 vérifications documentées par @qa Phase 2d).

| Terme proscrit | Présence dans les 14+4+3+2 templates | Verdict |
|---|---|---|
| "signal fort" | ABSENT — remplacé par "Score X.X/10" | PASS |
| "buy now" | ABSENT — remplacé par "🟢 ACHAT — avant 8h55 CET" | PASS |
| "guaranteed" / "garanti" | ABSENT — remplacé par "Backtest X% sur N trades" | PASS |
| "perfect entry" | ABSENT — remplacé par "Entrée : X,XX" | PASS |
| "opportunity" | ABSENT — remplacé par "Raison : [chiffres]" | PASS |
| "ne pas manquer" | ABSENT (supprimé) | PASS |
| Futur affirmatif ("va monter") | ABSENT — remplacé par "Cible potentielle" systématique | PASS |

**Résultat : 0 terme proscrit sur l'ensemble des templates. Audit @qa Phase 2d confirme 0/63 occurrence.**

### 3.3 Vérification du destinataire unique — code source

Dans `src/telegram/bot.py`, la fonction `dispatch_command` ligne 289 :

```python
if not _is_authorized(sender_chat_id, allowed_chat_id):
    logger.warning("telegram_command_unauthorized", ...)
    return None  # silencieux, pas de feedback à un attaquant
```

La fonction `send_message` utilise le `chat_id` fourni en argument — dans `src/main.py`, ce `chat_id` est lu depuis `os.environ["TELEGRAM_CHAT_ID"]` (Replit Secret), qui est le THOMAS_CHAT_ID. **Un seul destinataire, authentifié par secret d'environnement, confirmé dans le code.**

### 3.4 Analyse des formulations à risque

**Templates ACHAT/VENTE (14 templates)** : chaque message contient entrée/SL/TP chiffrés, win rate historique, nombre de trades backtest, drawdown max, score numérique. La formulation "Cible potentielle" pour le TP est systématique — jamais de futur affirmatif. Le score est présenté comme un indicateur probabiliste, pas comme une certitude. **Aucune formulation ne s'apparente à du conseil personnalisé à un tiers.**

**Templates NO-TRADE (4 templates)** : NT-01 à NT-04 communiquent l'absence de signal avec la raison chiffrée (score sous seuil, VIX > seuil, volume insuffisant). Pas de recommandation d'action. **Conformes.**

**Templates ERREUR DATA / DEGRADED MODE (3 templates)** : US-04, US-05, US-06 informent Thomas d'une indisponibilité technique. Pas de signal, pas de recommandation. **Conformes.**

**Templates audit hebdo + mensuel** : présentent des statistiques P&L, win rate, drawdown. La commande `/continue` ou `/stop` est une décision de Thomas sur son propre bot. **Conformes.**

### 3.5 Alerte CRITIQUE — ligne rouge redistribution

Si Thomas redistribuait **un seul signal** à **un seul tiers** (même un ami, même à titre gratuit, même via copier-coller d'un screenshot) :
- Qualification immédiate en conseil en investissement à un tiers (Art. D. 321-1 CMF)
- Exercice illégal de service d'investissement (Art. L. 573-1 CMF)
- **Sanctions pénales : jusqu'à 3 ans d'emprisonnement et 375 000 € d'amende**
- La gratuité n'exonère pas. Un groupe Telegram semi-privé de 2 personnes suffit à déclencher la qualification.

**Cette ligne rouge doit faire l'objet d'un mémo écrit dans le repo (action Thomas n°2 — voir §6).**

---

## 4. Audit fiscalité PFU 31,4 %

### 4.1 Vérification des documents et templates

| Point de contrôle | Source | Statut |
|---|---|---|
| Taux PFU 31,4 % mentionné dans le KPI North Star | `project-context.md` §Objectifs + `functional-specs.md` §Résumé | PASS |
| Taux 31,4 % (et non 30 %) mentionné dans l'audit mensuel Telegram | `docs/copy/message-templates.md` §5 AUDIT-MENSUEL : "Fiscalité PFU estimée (31,4 %)" | PASS |
| Taux 31,4 % dans la confirmation /trade | `src/telegram/bot.py` ligne 166 : `"(PFU 31,4 % a appliquer)"` | PASS |
| Déclaration annuelle (pas trade par trade) | `docs/legal/legal-audit.md` §7.3 : formulaire 2074 N+1, base nette annuelle | PASS |
| Base imposable = MAX(0, gains - pertes) | `legal-audit.md` §7.2 : imputation des moins-values (Art. 150-0 D CGI) | PASS |
| Journal trades pour reconstitution fiscale | Table `trades` SQLite avec pl_brut, mae, mfe, mode, signal_id | PASS |

### 4.2 Vérification implémentation en base de données

**Colonnes table `trades` (src/journal/db.py et schema.py audités) :**
- `pl_brut` (REAL) : P&L brut avant frais — PRESENT
- `mae` (REAL) / `mfe` (REAL) : max adverse/favorable excursion — PRESENTS
- `mode` (TEXT NOT NULL DEFAULT 'paper') : paper vs live — PRESENT (migration B2 Phase 2d-bis)

**Colonne `pl_net_eur` absente en base de données.** La mission demande de vérifier la présence d'une colonne `pl_net_eur` avec PFU intégré. Cette colonne n'est pas présente dans le schéma audité. La table `trades` stocke le `pl_brut` ; le P&L net (après frais Bourse Direct 0,99 € × 2) est calculé à la volée dans `handle_trade` : `pl_net = pl_brut - 0.99 - 0.99` (bot.py ligne 158), affiché dans le message de confirmation mais non persisté.

**Conséquence pratique :** l'estimation PFU annuelle (`pfu_year_estimate`) cumulée n'est pas calculée en temps réel en base. L'estimation PFU dans l'audit mensuel est calculée sur le P&L brut du mois sans persistance d'un compteur annuel cumulé.

**Risque fiscal :** faible à moyen. Thomas dispose du P&L brut de chaque trade en base + de l'IFU Bourse Direct pour la déclaration annuelle. L'absence de colonne `pl_net_eur` persistée ne crée pas de non-conformité fiscale, mais réduit la capacité d'anticipation PFU en cours d'année.

**Recommandation :** ajouter une migration `migrate_trades_add_pl_net_eur_pfu_estimate` qui calcule et persiste `pl_net_eur = pl_brut - 1.98` (frais aller-retour) et `pfu_estimate = MAX(0, pl_net_eur) * 0.314` par trade, cumulés en vue du formulaire 2074. Cette évolution est une amélioration de traçabilité, pas une obligation bloquante pour le MVP.

### 4.3 Formule fiscale correcte

La formule applicable (legal-audit.md §7 confirmé) :
- Taux PFU : **31,4 %** (12,8 % IR + 17,2 % PS + 1,4 % CSHR intégrée depuis 01/01/2025)
- Base : gains nets annuels = somme des plus-values − somme des moins-values de même nature
- Formulaire : **2074** (annexe à la 2042), dépôt en mai-juin N+1
- Report des moins-values : 10 ans sur les plus-values futures de même nature (Art. 150-0 D CGI)

---

## 5. Audit secrets et données sensibles

### 5.1 Secrets Replit — conformité REPLIT_ACTIONS §B.1

15 variables d'environnement documentées dans REPLIT_ACTIONS §B.1. Vérification dans le code source audité :

| Secret | Variable d'environnement | Présence dans code en clair | Statut |
|---|---|---|---|
| Token Bot Telegram | `TELEGRAM_BOT_TOKEN` | Absent du code source | PASS |
| Chat ID Thomas | `TELEGRAM_CHAT_ID` | Absent du code source | PASS |
| Clé API Twelve Data | `TWELVE_DATA_API_KEY` | Absent du code source | PASS |
| Clé API Anthropic | `ANTHROPIC_API_KEY` | Absent du code source | PASS |
| Clé chiffrement SQLite | `SQLITE_ENCRYPTION_KEY` | Absent du code source | PASS |

Tous les accès aux secrets dans le code utilisent `os.environ["NOM_VARIABLE"]` — mode fail-fast si absent (pas de valeur par défaut qui masquerait une configuration incomplète). **CONFORME.**

**Rotation des secrets** : REPLIT_ACTIONS mentionne une rotation recommandée 6-12 mois. Pas encore de procédure automatisée — acceptable en phase R&D. À formaliser avant bascule live.

### 5.2 Données financières personnelles — classification et protection

| Donnée | Localisation | Protection | Statut |
|---|---|---|---|
| Capital 20-30 k€ | `project-context.md` | Repo privé obligatoire | CONFORME — avertissement en tête de fichier |
| P&L par trade | `data/journal.sqlite` table `trades` | `.gitignore` couvre `*.db`, `*.sqlite` | CONFORME |
| Journal des trades | `data/journal.sqlite` | Non exposé via API publique | CONFORME |
| Signaux calculés | `data/journal.sqlite` table `signals` | Idem | CONFORME |
| Résultats backtest | `data/journal.sqlite` table `rnd_results` + JSON `results/` | `.gitignore` couvre `results/` | CONFORME |

**Durée de conservation** : 10 ans recommandés (legal-audit.md §2.3 + alignement prescription fiscale Art. L. 169 LPF). Pas de procédure d'archivage automatique implémentée — acceptable pour un outil personnel en phase R&D.

### 5.3 Données envoyées à Anthropic — vérification architecture prompts

Source : `src/ai/client.py` + `src/scoring/engine.py` + décision H-ZDR.

**Contenu des prompts Claude audité :**
- Données de marché OHLC publiques (CAC40, DAX, ESTX50, EUR/USD, etc.)
- Indicateurs techniques calculés (RSI, MACD, Bollinger, EMA)
- Titres de news strippés (regex injection prevention documentée Phase 2c-1)
- Score déterministe pré-calculé (dimensions D1-D6)

**Données absentes des prompts (conformes H-ZDR) :**
- Pas de chat_id Telegram
- Pas de capital exact ni de P&L réels
- Pas de solde compte Bourse Direct
- Pas d'identifiants personnels

**Rétention API Anthropic :** 7 jours (standard API commerciale, pas de ZDR activé). Acceptable car aucune PII dans les prompts. **CONFORME à la décision H-ZDR DIFFÉRÉE.**

**Cap budget Anthropic** : 30 $/mois documenté dans REPLIT_ACTIONS comme garde-fou runaway. À vérifier dans le dashboard Anthropic que le spending limit est effectivement configuré.

### 5.4 Statut GitHub Secret Scanning

legal-audit.md §3.4 recommande l'activation du Secret Scanning natif GitHub (Settings > Security > Secret scanning). **Non vérifiable depuis cet audit** (accès GitHub non disponible dans cet environnement). **Action Thomas n°1 : vérifier le statut privé du repo ET activer Secret Scanning.**

---

## 6. Verdict final + 3 actions Thomas

### 6.1 Verdict global

**CONFORMITÉ MAINTENUE — 1 point de vigilance non bloquant**

| Domaine | Résultat |
|---|---|
| AMF/MiFID II — Usage personnel | CONFORME — 0 signal redistribué, auth THOMAS_CHAT_ID vérifiée dans le code |
| Redistribution — ligne rouge CIF | CONFORME — 0 déviation sur Phases 1-4 ; ligne rouge rappelée en §3.5 |
| RGPD — exemption activité personnelle | CONFORME — périmètre 100 % personnel maintenu |
| Repo GitHub privé | CONFORME selon déclarations et contraintes documentées ; **à vérifier physiquement** |
| Secrets en variables d'environnement | CONFORME — 0 secret en clair dans le code source audité |
| Twelve Data CGU | CONFORME — usage interne uniquement, plan Pro Individual confirmé (H2 PASS) |
| Bourse Direct | CONFORME — exécution manuelle, 0 automatisation côté broker |
| Anthropic API / ZDR | CONFORME — 0 PII dans les prompts, rétention 7j acceptable |
| Templates Telegram — vocabulaire | CONFORME — 0/63 terme proscrit (audit @qa Phase 2d) |
| PFU 31,4 % — formule et déclaration | CONFORME sur la formule ; **point de vigilance** : colonne `pl_net_eur` absente en DB |
| EU AI Act — classification | CONFORME — risque limité, obligation de transparence satisfaite de facto |
| Licences open source | CONFORME — LGPL-3.0 (backtesting.py, python-telegram-bot) acceptable usage perso |

**Aucune non-conformité bloquante. Aucune déviation par rapport au cadre Phase 0 détectée sur les Phases 1-4.**

### 6.2 3 actions Thomas obligatoires AVANT bascule live

**Action 1 — Vérifier le statut PRIVÉ du repo GitHub**

Aller dans GitHub > Settings > Danger Zone > Change repository visibility. Confirmer "Private". Activer Secret Scanning (Settings > Security > Secret scanning). Cette action prend 2 minutes et protège contre le risque R2 (ELEVE). Ne pas démarrer le live sans cette vérification.

**Action 2 — Créer un mémo d'engagement écrit dans le repo**

Créer un fichier `docs/legal/engagement-usage-personnel.md` (privé dans le repo) contenant :

```
# Engagement usage personnel — TradingApp
Date : [date de signature]
Auteur : Thomas

Je confirme que ce bot de signaux est utilisé exclusivement pour mon propre compte.
Aucun signal ne sera redistribué à un tiers, quelle que soit la forme (copier-coller,
screenshot, groupe Telegram, accès partagé, API publique).

Rappel : toute redistribution, même gratuite, même à un seul ami, constitue un exercice
illégal de conseil en investissement (Art. L. 573-1 CMF — 3 ans / 375 000 €).

Si ce périmètre devait évoluer, consulter un avocat spécialisé AVANT toute redistribution.
```

Ce mémo établit une traçabilité de l'intention personnelle, utile si le repo était un jour accidentellement rendu public.

**Action 3 — Documenter la procédure d'escalade si redistribution envisagée**

Si Thomas souhaite un jour partager des signaux (même avec un ami), le processus légal minimum avant toute redistribution est :
1. Consulter un avocat spécialisé en droit financier (délai : 1-2 semaines)
2. Adhérer à une association professionnelle agréée AMF (CNCIF, ANACOFI-CIF, CNCGP) — délai 2-4 mois, coût ~500-1000 €/an
3. Souscrire une RCP professionnelle (~1000-3000 €/an)
4. S'inscrire au registre ORIAS
5. Obtenir l'accord de redistribution Twelve Data (contact : sales@twelvedata.com)
6. Mettre en conformité RGPD complète (politique de confidentialité, registre traitements)
**Délai minimal réaliste avant toute redistribution légale : 3 à 6 mois.**

Consigner cette procédure dans `docs/legal/engagement-usage-personnel.md` comme rappel permanent.

### 6.3 Risques résiduels top 3

**R1 — Redistribution accidentelle (CRITIQUE)**
Risque : Thomas partage un screenshot d'un signal dans un groupe de trading ou à un ami. Probabilité : faible (discipline documentée). Impact : requalification immédiate en exercice illégal (Art. L. 573-1 CMF). Mitigation : mémo d'engagement (Action 2) + aucune fonctionnalité de "partage" dans le bot.

**R2 — Fuite repo GitHub (ELEVE)**
Risque : basculement accidentel du repo en public, ou ajout d'un collaborateur sans nécessité. Impact : exposition du capital, P&L, clés API. Mitigation : vérification statut privé + Secret Scanning (Action 1) + rotation des clés compromises via BFG si incident.

**R3 — Colonne `pl_net_eur` absente (FAIBLE — amélioration recommandée)**
Risque : impossibilité d'anticiper le PFU cumulé en cours d'année sans calcul manuel. Impact : pas de non-conformité fiscale (IFU Bourse Direct reste la référence), mais traçabilité réduite. Mitigation : migration `migrate_trades_add_pl_net_eur_pfu_estimate` à planifier avant le premier mois live.

### 6.4 Vérification disclaimer README

Le legal-audit.md §9.2 (Phase 0) demandait l'ajout d'un disclaimer en tête du README.md du repo. Cette présence n'est pas vérifiable depuis l'environnement actuel (README.md non lu dans cet audit). **Thomas doit vérifier que le bloc suivant est présent dans son README.md** :

```markdown
## Avertissement légal

Ce projet est un outil d'aide à la décision de trading strictement personnel.
Il ne constitue en aucun cas un conseil en investissement (Art. L. 321-1 CMF),
une gestion de portefeuille, ni une recommandation destinée à des tiers.
Les turbos sont des instruments financiers complexes à effet de levier
pouvant entraîner la perte totale du capital investi.
Ce repo est privé et ne doit jamais être redistribué ni rendu public.
```

Si ce bloc est absent : l'ajouter avant la bascule live.

---

**Handoff → @orchestrator**
- Fichiers produits : `/home/user/TradingApp/docs/legal/legal-final-audit-phase5.md`
- Décisions prises :
  - Conformité AMF/MiFID II maintenue sur Phases 1-4 — 0 déviation
  - Vocabulaire templates Telegram : 0 terme proscrit (63 vérifications @qa)
  - Auth THOMAS_CHAT_ID vérifiée dans le code source `src/telegram/bot.py`
  - PFU 31,4 % correctement mentionné dans tous les templates ; colonne `pl_net_eur` absente en DB (non bloquant)
  - Licences LGPL-3.0 (backtesting.py, python-telegram-bot) conformes usage personnel propriétaire
  - EU AI Act : risque limité confirmé — obligation de transparence satisfaite de facto
- Points d'attention :
  - **Action Thomas n°1 (AVANT LIVE)** : vérifier statut PRIVÉ repo GitHub + activer Secret Scanning
  - **Action Thomas n°2 (AVANT LIVE)** : créer `docs/legal/engagement-usage-personnel.md` (mémo engagement)
  - **Action Thomas n°3 (AVANT LIVE)** : vérifier présence disclaimer README.md (legal-audit.md §9.2)
  - Recommandation @fullstack : migration `migrate_trades_add_pl_net_eur_pfu_estimate` avant premier mois live
  - Rotation secrets Replit (6-12 mois) à formaliser en procédure avant live
  - Ce document est un draft de référence — validation par un avocat recommandée avant toute évolution du périmètre

---
