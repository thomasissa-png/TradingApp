# Audit juridique — TradingApp

> **Statut** : Draft de référence — pas un avis juridique formel. Validation par un avocat recommandée avant toute évolution du périmètre (redistribution, monétisation).
> **Date** : 2026-05-01
> **Périmètre** : Bot Telegram de trading personnel, usage 100% privé, France, Thomas, capital 20-30 k€, turbos via Bourse Direct, données Twelve Data, IA Claude (Anthropic API).

---

## Risques en 5 points (résumé exécutif)

| # | Risque | Criticité | Statut actuel |
|---|--------|-----------|---------------|
| R1 | Requalification en conseil en investissement (CIF/AMF) si redistribution | CRITIQUE si redistribution | CONFORME tant que 100% personnel |
| R2 | Fuite de données financières personnelles depuis le repo GitHub | ELEVE | A sécuriser (.gitignore strict + secrets) |
| R3 | Non-conformité Twelve Data en cas de redistribution future | MODERE | Conforme usage personnel ; redistribution = accord séparé requis |
| R4 | Fiscalité turbos mal déclarée (PFU, formulaire 2074) | MODERE | Journal trades obligatoire pour déclaration correcte |
| R5 | Données envoyées à Claude API (prompts) non couvertes par ZDR | FAIBLE | API standard : rétention 7 jours ; ZDR disponible en option |

---

## 1. Statut AMF / MiFID II — Usage personnel vs redistribution

### 1.1 Cadre légal applicable

Le service d'investissement de **conseil en investissement** est défini à l'article **L. 321-1 du Code monétaire et financier (CMF)** comme l'un des services d'investissement soumis à agrément. L'article **D. 321-1 CMF** le définit précisément comme « la fourniture de recommandations personnalisées à un tiers, soit à sa demande, soit à l'initiative de l'entreprise qui fournit le conseil, concernant une ou plusieurs transactions portant sur des instruments financiers ».

**Trois critères cumulatifs** font basculer une activité dans le périmètre réglementé :
1. Une **recommandation personnalisée** (adaptée à la situation d'un individu ou présentée comme telle)
2. Destinée à un **tiers** (une personne autre que soi-même)
3. Portant sur des **transactions en instruments financiers** (turbos = instruments financiers complexes au sens MiFID II — Directive 2014/65/UE)

**Position AMF DOC-2008-23** (modifiée 13 février 2024, Q&R sur le conseil en investissement) : une recommandation adressée à soi-même, sans aucun tiers, ne constitue pas un service d'investissement au sens de L. 321-1 CMF.

### 1.2 Situation actuelle de TradingApp — CONFORME

Le bot TradingApp répond aux caractéristiques suivantes :
- **Destinataire unique** : Thomas, seul utilisateur, identifié par son propre chat_id Telegram
- **Usage 100% personnel** : capital propre 20-30 k€, jamais redistribué, repo GitHub privé
- **Pas de tiers** : aucune recommandation envoyée à un investisseur autre que le créateur

**Conclusion** : en l'état actuel, le bot ne fournit pas de conseil en investissement à un tiers. Il est assimilable à un outil d'aide à la décision personnelle. **Aucun agrément AMF, CIF ou PSI n'est requis.**

Source principale : [Article L321-1 CMF — Légifrance](https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000006139972/) ; [Position AMF DOC-2008-23 v4.3](https://www.amf-france.org/sites/institutionnel/files/private/2024-02/doc-2008-23_vf4_3.pdf)

### 1.3 Conditions d'agrément si redistribution future (CIF)

Si Thomas souhaitait un jour partager les signaux avec d'autres personnes (même à titre gratuit), il entrerait dans le périmètre du **statut CIF — Conseiller en Investissements Financiers** (articles **L. 541-1 à L. 541-9 CMF**) ou, selon l'ampleur, du **prestataire de services d'investissement (PSI)** agréé par l'AMF.

Obligations CIF minimales (article L. 541-1 et ss CMF) :
- Adhésion à une association professionnelle agréée AMF (ex : CNCIF, ANACOFI-CIF, CNCGP)
- Souscription d'une assurance responsabilité civile professionnelle
- Respect des obligations de connaissance client (KYC), d'adéquation du conseil, et de transparence sur les conflits d'intérêts
- Inscription au registre ORIAS

**Seuil de déclenchement** : dès le premier signal envoyé à un tiers, même bénévole, même à un seul ami. La gratuité n'exonère pas du statut CIF.

> **Alerte** : toute redistribution, même partielle ou temporaire, est un risque de requalification en exercice illégal de service d'investissement (article **L. 573-1 CMF** — sanctions pénales jusqu'à 3 ans de prison et 375 000 € d'amende).

---

## 2. RGPD — chat_id Telegram et journal P&L

### 2.1 Le RGPD s'applique-t-il à TradingApp ?

**Oui, mais avec l'exemption "activité purement personnelle"** (article **2 §2 c) RGPD — Règlement UE 2016/679**) : le RGPD ne s'applique pas aux traitements effectués par une personne physique dans le cadre d'une activité **strictement personnelle ou domestique**.

**Conditions de l'exemption** : l'activité ne doit avoir aucune connexion avec une activité professionnelle ou commerciale, et les données ne doivent pas être accessibles à un nombre indéterminé de personnes.

**Pour TradingApp** : le bot traite uniquement des données de Thomas, pour Thomas, sans redistribution. L'exemption s'applique **tant que le périmètre reste 100% personnel**.

### 2.2 Nature des données traitées

Même sous exemption, identifier les données traitées est une bonne pratique (conformité proactive si le périmètre évolue) :

| Donnée | Qualification RGPD | Catégorie |
|--------|-------------------|-----------|
| `chat_id` Telegram | **Identifiant indirect** — permet d'identifier Thomas via Telegram | Données personnelles ordinaires (Art. 4 §1 RGPD) |
| Journal des trades (dates, P&L, positions) | **Données financières personnelles** — reliables à une personne identifiable | Données personnelles ordinaires |
| Capital total, drawdown | **Données financières sensibles** au sens pratique | Données personnelles ordinaires (pas catégorie spéciale Art. 9) |
| Prompts envoyés à Claude | Données opérationnelles — peuvent contenir des éléments personnalisés | Voir section 6 |

Le `chat_id` Telegram est un **identifiant indirect** au sens de l'article 4 §1 RGPD : il ne révèle pas directement l'identité civile, mais combiné avec l'accès au compte Telegram, il permet d'identifier Thomas sans effort raisonnable. La [CNIL confirme](https://www.cnil.fr/fr/identifier-les-donnees-personnelles) que les identifiants techniques constituent des données personnelles.

### 2.3 Bonnes pratiques (conformité proactive)

1. **Ne pas stocker le `chat_id` en clair dans le code source** : utiliser une variable d'environnement (`TELEGRAM_CHAT_ID`) — critique pour la sécurité repo (voir section 3)
2. **Journal trades en SQLite local** : ne pas l'exposer via une API publique, ne pas le synchroniser sur un cloud non chiffré
3. **Durée de conservation** : fixer une durée raisonnable pour le journal (ex : 10 ans, aligné sur les obligations fiscales — voir section 7) et archiver au-delà
4. **Chiffrement du fichier SQLite** : envisager SQLCipher ou chiffrement au repos sur Replit (variable d'environnement pour la clé)
5. **Si redistribution future** : obligation immédiate de rédiger une politique de confidentialité, un registre des traitements (Art. 30 RGPD), et une bannière cookies si interface web

**Base légale si périmètre évolue** : intérêt légitime (Art. 6 §1 f RGPD) pour les analytics internes ; exécution du contrat (Art. 6 §1 b) pour les données compte utilisateur en cas de SaaS.

---

## 3. Repo GitHub privé — règles de sécurité et risques de fuite

### 3.1 Obligation de confidentialité du repo

Le repo `TradingApp` contient des **données financières personnelles** (capital, P&L, journal trades, identifiants API). Conformément aux décisions structurantes du projet, il **doit rester privé en permanence**. Un basculement public accidentel constituerait :
- Une **fuite de données personnelles financières**
- Une exposition des clés API (Twelve Data, Anthropic, Telegram Bot Token) — risque de coût financier immédiat (appels API frauduleux)
- Un risque de sécurité sur le compte Bourse Direct si des identifiants y sont mentionnés

### 3.2 Secrets à ne JAMAIS commiter — liste exhaustive

Les éléments suivants ne doivent jamais apparaître dans aucun fichier du repo, y compris les fichiers de configuration, les tests, et les commentaires :

| Secret | Variable d'environnement recommandée |
|--------|-------------------------------------|
| Token Bot Telegram | `TELEGRAM_BOT_TOKEN` |
| Chat ID Telegram de Thomas | `TELEGRAM_CHAT_ID` |
| Clé API Twelve Data | `TWELVE_DATA_API_KEY` |
| Clé API Anthropic | `ANTHROPIC_API_KEY` |
| Identifiants Bourse Direct | `BOURSE_DIRECT_LOGIN` / `BOURSE_DIRECT_PASSWORD` (si jamais utilisés) |
| Clé chiffrement SQLite | `SQLITE_ENCRYPTION_KEY` |

### 3.3 .gitignore strict — éléments obligatoires

Le `.gitignore` doit impérativement couvrir :

```
# Secrets et configuration locale
.env
.env.*
*.env
secrets/
config/local*

# Base de données (journal trades = données financières personnelles)
*.db
*.sqlite
*.sqlite3
data/

# Résultats backtest (peuvent contenir P&L historique)
results/
backtest_results/
*.csv

# Logs (peuvent contenir des données de marché et identifiants)
*.log
logs/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node/Bun (selon stack retenu)
node_modules/
.next/
dist/
```

### 3.4 GitHub Secret Scanning

GitHub propose nativement le **Secret Scanning** sur les repos privés (fonctionnalité disponible sur tous les plans depuis 2023). Activer dans Settings > Security > Secret scanning pour recevoir une alerte immédiate si un secret est commité par erreur.

### 3.5 Risques résiduels à monitorer

- **Historique git** : un secret commité puis retiré reste dans l'historique git. En cas de commit accidentel, révoquer immédiatement la clé compromise et utiliser `git filter-branch` ou BFG Repo Cleaner pour purger l'historique
- **Collaborateurs** : ne jamais ajouter de collaborateur externe sans nécessité absolue
- **GitHub Actions** : si un workflow CI/CD est ajouté, s'assurer que les secrets sont injectés via GitHub Secrets (jamais en dur dans `.yml`)

---

## 4. Twelve Data CGU — usage personnel autorisé, restrictions redistribution

### 4.1 Usage personnel — CONFORME

[HYPOTHÈSE : fondée sur les CGU Twelve Data publiquement accessibles à twelvedata.com/terms au 2026-05-01 — vérifier que votre plan actuel correspond aux termes ci-dessous.]

Les plans individuels Twelve Data sont **strictement réservés à un usage personnel ou interne**. La définition contractuelle d'"Internal Use" exclut explicitement la redistribution ou tout usage commercial externe.

**Pour TradingApp dans son état actuel** : usage interne unique (Thomas), données consommées par un bot personnel, aucune redistribution. **Conforme aux CGU Twelve Data.**

Source : [Commercial and personal usage — Twelve Data Support](https://support.twelvedata.com/en/articles/5332349-commercial-and-personal-usage) ; [Terms of use — Twelve Data](https://twelvedata.com/terms)

### 4.2 Restrictions redistribution

Les CGU Twelve Data imposent les restrictions suivantes sur la redistribution :

- **Toute redistribution des données requiert un accord séparé** avec Twelve Data (contact : sales@twelvedata.com)
- Certains niveaux d'abonnement permettent une redistribution limitée sous conditions d'attribution et de respect des règles des bourses sources
- Les données de certaines bourses (notamment Euronext pour les actions françaises) peuvent être soumises à des **règles d'échange supplémentaires** et à des **frais de redistribution professionnels** indépendants de l'abonnement Twelve Data
- L'attribution ("Powered by Twelve Data") est requise pour tout affichage public, sauf clause contractuelle contraire

### 4.3 Vérification plan actuel — action requise

**[HYPOTHÈSE H2 du project-context.md]** : le plan Twelve Data actuel de Thomas couvre indices EU + actions FR + FX + commodities en intraday 1m sur 5 ans. Cette hypothèse doit être vérifiée dans le compte Twelve Data.

Points à vérifier :
- Le plan couvre-t-il les données **intraday 1m sur 5+ ans d'historique** pour indices EU (CAC40, DAX, EuroStoxx50) et FX ?
- Existe-t-il une limite de requêtes par minute/jour susceptible de bloquer la phase R&D edge (100-500 appels/jour selon project-context.md) ?
- Les données de commodités (or, brent, gaz) sont-elles incluses ou soumises à des frais supplémentaires ?

Si le plan actuel est insuffisant : contacter Twelve Data pour upgrader avant d'engager la R&D edge.

### 4.4 EU AI Act — données d'entraînement

TradingApp n'entraîne pas de modèle IA avec les données Twelve Data. Claude est utilisé comme LLM tiers via API (scoring, justification). Pas de conflit avec les CGU Twelve Data sur ce point.

---

## 5. Bourse Direct — exécution manuelle et conformité broker

### 5.1 Modèle d'exécution de TradingApp — CONFORME

Le bot TradingApp **ne se connecte pas à l'API Bourse Direct** et **n'exécute aucun ordre** de manière automatique. Son rôle est exclusivement :
- Calculer un signal (données Twelve Data + scoring Claude)
- Envoyer ce signal sur Telegram
- Thomas exécute **manuellement** l'ordre dans son interface Bourse Direct

Ce modèle d'exécution manuelle est **sans risque de conformité du côté broker** :
- Aucun accès programmatique au compte de trading
- Aucun risque de trading algorithmique non déclaré
- Aucune question de latence / co-location / HFT
- Pas d'obligation de déclaration d'algorithme de trading (Art. 17 MiFID II — ne concerne que les PSI exécutant des ordres automatiques)

### 5.2 CGU Bourse Direct — usage normal du compte

[HYPOTHÈSE : les CGU Bourse Direct standard autorisent l'utilisation d'outils d'aide à la décision personnels. Vérifier les CGU en vigueur si une automatisation de l'exécution est envisagée à l'avenir.]

L'utilisation d'outils personnels d'aide à la décision (alertes, screeners, bots de signaux) n'est pas soumise à des obligations contractuelles spécifiques envers le broker dans un compte CTO personnel. Bourse Direct agit comme **simple intermédiaire d'exécution** — il n'a pas à connaître la méthode de décision de son client.

### 5.3 Point de vigilance — passage futur à l'exécution automatique

Si Thomas souhaitait à terme automatiser l'exécution via l'API Bourse Direct (ou un broker alternatif avec API publique comme Interactive Brokers) :
- Vérifier les CGU du broker sur le trading algorithmique
- S'assurer que la qualité d'exécution respecte les obligations MiFID II best execution (article L. 533-18 CMF) — même pour un compte personnel avec un PSI agréé
- Les ordres automatiques génèrent des obligations de test et de contrôle renforcées côté broker (Art. 17 MiFID II)

---

## 6. Anthropic Claude API — données envoyées, rétention, ZDR

### 6.1 Nature des données envoyées à Claude

Selon le design prévu de TradingApp, les prompts envoyés à l'API Claude contiennent :
- **Données de marché publiques** : cours, indicateurs techniques (RSI, MACD, etc.) sur sous-jacents publics (CAC40, DAX, EUR/USD, etc.)
- **Signaux calculés** : résultats des algorithmes de scoring internes
- **Aucune PII directe** : pas de nom, prénom, numéro de compte, IBAN, identifiant Bourse Direct

**Niveau de risque données** : faible. Les prompts sont de nature opérationnelle-marché, pas personnelle au sens RGPD. Ils ne permettent pas d'identifier Thomas directement.

**Vigilance** : ne jamais inclure dans les prompts Claude le chat_id Telegram, le capital exact, le solde du compte, ni d'informations d'identification.

### 6.2 Politique de rétention API Anthropic (état au 2026-05-01)

Pour l'API commerciale Anthropic (hors Claude.ai consumer) :

| Situation | Rétention des logs | Usage pour l'entraînement |
|-----------|-------------------|--------------------------|
| API standard sans ZDR | **7 jours** (depuis le 15 septembre 2025) | **Jamais** — les données API ne sont pas utilisées pour l'entraînement |
| API avec accord ZDR | **0 jour** (suppression après réponse, hors obligations légales) | Jamais |
| Claude.ai (consumer) | 30 jours (ou 5 ans si opt-in entraînement) | Opt-in utilisateur |

Pour TradingApp utilisant l'API commerciale Anthropic : les prompts sont automatiquement supprimés après 7 jours. Les données ne sont **jamais utilisées pour entraîner les modèles Anthropic**.

Sources : [API and data retention — Anthropic Docs](https://platform.claude.com/docs/en/build-with-claude/api-and-data-retention) ; [How long do you store my organization's data — Anthropic Privacy Center](https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data)

### 6.3 Zero Data Retention (ZDR) — option disponible

Anthropic propose un **addendum ZDR** pour les organisations ayant des exigences de conformité strictes. Avec ZDR :
- Les données sont **supprimées immédiatement** après retour de la réponse API (sauf obligations légales et contrôle d'abus)
- ZDR s'applique aux APIs Anthropic éligibles et aux produits utilisant la clé API commerciale (y compris Claude Code)

**Recommandation pour TradingApp** : la rétention de 7 jours est acceptable pour un usage personnel sans PII dans les prompts. Si Thomas intègre à terme des données plus sensibles dans les prompts (ex : P&L précis, identifiants), demander un accord ZDR via le support Anthropic.

Source : [Zero Data Retention — Anthropic Privacy Center](https://privacy.claude.com/en/articles/8956058-i-have-a-zero-data-retention-agreement-with-anthropic-what-products-does-it-apply-to) ; [Zero Data Retention — Claude API Docs](https://platform.claude.com/docs/en/build-with-claude/api-and-data-retention)

### 6.4 EU AI Act — classification TradingApp

Selon le tableau de classification EU AI Act (Règlement UE 2024/1689) :

| Critère | Situation TradingApp |
|---------|---------------------|
| Système IA interdit ? | Non — pas de scoring social, pas de manipulation subliminale |
| Système IA à haut risque ? | Non — ne concerne pas le recrutement, le crédit scoring accordé à des tiers, ni le médical |
| Risque limité (chatbot/contenu généré IA) ? | **Oui** — Claude génère la justification textuelle du signal |
| Risque minimal ? | Partiellement — la recommandation de signal (même personnelle) sort du "risque minimal" |

**Classification : Risque limité** — obligation de transparence uniquement.

**Obligation concrète** : puisque l'usage est 100% personnel (Thomas est le seul destinataire et l'auteur du système), l'obligation de transparence "ce contenu est généré par IA" est de facto satisfaite. Elle deviendrait obligatoire formellement en cas de redistribution à des tiers.

---

## 7. Fiscalité — PFU 31,4%, formulaire 2074, journal trades

### 7.1 Régime fiscal applicable aux turbos sur CTO

Les turbos (et warrants) sont des **valeurs mobilières à bons d'option** (bons d'option au sens fiscal). Leurs plus-values relèvent du régime des **plus-values de cession de valeurs mobilières** (articles **150-0 A et suivants du Code général des impôts — CGI**).

**Depuis le 1er janvier 2025** : le taux global du **Prélèvement Forfaitaire Unique (PFU)** est passé de 30% à **31,4%**, soit :
- 12,8% d'impôt sur le revenu
- 17,2% de prélèvements sociaux (CSG/CRDS)
- + 1,4% de contribution supplémentaire sur les hauts revenus (CSHR) intégrée au nouveau taux

**Option barème progressif** : sur option irrévocable lors de la déclaration, les plus-values peuvent être imposées au barème progressif de l'IR. Recommandé uniquement si le taux marginal d'imposition de Thomas est inférieur à 12,8%.

### 7.2 Imputation des moins-values

Les moins-values sur turbos sont **déductibles des plus-values de valeurs mobilières de la même année** (article 150-0 D CGI). En cas de solde négatif persistant :
- Les moins-values sont **reportables 10 ans** sur les plus-values futures de même nature
- Le report de moins-values est automatiquement pré-rempli par le formulaire 2074 les années suivantes

### 7.3 Déclaration — formulaire 2074

Les plus-values et moins-values sur turbos/warrants doivent être déclarées via le **formulaire 2074** (annexe à la déclaration 2042). Ce formulaire est obligatoire pour :
- Déclarer chaque cession de valeurs mobilières (dont turbos)
- Calculer le net imposable (plus-values – moins-values)
- Reporter les moins-values antérieures

Téléchargement : [Formulaire 2074 — impots.gouv.fr](https://www.impots.gouv.fr/formulaire/2074/declaration-des-plus-ou-moins-values-realisee)

**Déclaration annuelle** : dépôt avec la déclaration de revenus (formulaire 2042), généralement en mai-juin de l'année N+1.

[HYPOTHÈSE : Bourse Direct, en tant que PSI français, délivre un **IFU (Imprimé Fiscal Unique)** annuel récapitulant toutes les cessions. Ce document pré-remplit partiellement le formulaire 2074. Vérifier auprès de Bourse Direct que l'IFU couvre bien les turbos.]

### 7.4 Journal des trades — obligation pratique

Bien que l'IFU Bourse Direct résume les cessions, un **journal personnel des trades** est fortement recommandé pour :

1. **Vérification de cohérence** avec l'IFU (erreurs de calcul du broker sont rares mais possibles)
2. **Analyse de performance** (MAE/MFE, win rate, drawdown — KPI North Star du projet)
3. **Traçabilité en cas de contrôle fiscal** : le fisc peut demander justification des plus/moins-values déclarées
4. **Report de moins-values** : identifier précisément les moins-values reportables des années antérieures

**Éléments minimum à journaliser** pour chaque trade :

| Champ | Exemple |
|-------|---------|
| Date d'ouverture | 2026-05-12 08:52 |
| Date de clôture | 2026-05-12 09:03 |
| Sous-jacent | CAC40 |
| Sens | Achat / Vente |
| Instrument | CALL Turbo 7800 échéance XX/XX |
| Prix d'entrée | 1,45 € |
| Prix de sortie | 1,78 € |
| Quantité | 1 000 |
| Frais (0,99 € Bourse Direct + spread) | 0,99 € + 0,03 € |
| Plus-value / moins-value nette | +326,01 € |
| Signal source (backtest ref, score confiance) | REF-BT-042, confiance 7/10 |

**Durée de conservation recommandée** : 10 ans (aligné sur le délai de report des moins-values et sur la prescription fiscale étendue — article L. 169 du Livre des Procédures Fiscales).

Sources : [Impôt sur le revenu — Plus-values valeurs mobilières — Service-public.fr](https://www.service-public.gouv.fr/particuliers/vosdroits/F21618) ; [Fiscalité turbos et warrants — Boursorama](https://www.boursorama.com/patrimoine/fiches-pratiques/fiscalite-des-warrants-comment-sont-ils-imposes-a5f1e59768f197a6f5141958cf34b462) ; [Formulaire 2074 — cleerly.fr](https://cleerly.fr/impots/declaration-2074)

---

## 8. Risques en cas de redistribution future — paliers vers CIF

### 8.1 Le premier signal partagé change tout

Le passage du statut "outil personnel" au statut "service de conseil" est **binaire et immédiat** : il suffit d'un seul signal envoyé à un tiers pour que l'activité entre dans le périmètre réglementé, quelle que soit la nature de ce tiers (ami, groupe Telegram, forum).

**Scénarios déclencheurs** (non exhaustifs) :
- Partage du signal Telegram avec 1 ami
- Publication d'un screenshot du signal sur Twitter/X, Discord, un forum de trading
- Création d'un groupe Telegram semi-privé
- Vente d'accès au bot, même à 1 €/mois

### 8.2 Parcours de conformité vers redistribution légale

**Palier 1 — CIF (Conseiller en Investissements Financiers)** : pour un service de signaux à un nombre limité d'abonnés particuliers.

Étapes :
1. Adhérer à une association professionnelle agréée AMF : [CNCIF](https://www.cncif.org/), [ANACOFI-CIF](https://www.anacofi.fr/), [CNCGP](https://www.cncgp.fr/) (~500-1000 €/an d'adhésion)
2. Justifier de la compétence professionnelle (diplôme Bac+3 finance ou expérience équivalente)
3. Souscrire une RCP (Responsabilité Civile Professionnelle) — ~1000-3000 €/an
4. S'inscrire au registre [ORIAS](https://www.orias.fr/)
5. Respecter les obligations MiFID II : connaissance client, adéquation du conseil, transparence sur les risques (turbos = produits complexes avec avertissement obligatoire)
6. Réviser les CGU Twelve Data pour redistribution (accord commercial séparé requis)
7. Conformité RGPD complète : politique de confidentialité, registre des traitements, bannière cookies si UI web

**Délai minimal réaliste** : 3-6 mois (constitution du dossier, validation ORIAS, mise en conformité des CGU fournisseurs).

**Palier 2 — PSI agréé AMF** : si le service dépasse le périmètre CIF (gestion sous mandat, exécution d'ordres pour compte de tiers, etc.). Agrément AMF direct, beaucoup plus lourd (capital minimum, contrôle interne, commissaire aux comptes). Hors de portée pour un particulier sans structure juridique (SAS/SA minimum).

### 8.3 Risques juridiques d'une redistribution non conforme

| Infraction | Base légale | Sanction maximale |
|------------|-------------|-------------------|
| Exercice illégal de service d'investissement | Art. L. 573-1 CMF | 3 ans d'emprisonnement + 375 000 € d'amende |
| Démarchage financier non autorisé | Art. L. 572-1 CMF | 2 ans + 30 000 € |
| Manquement RGPD (redistribution sans conformité) | Art. 83 RGPD | 20 M€ ou 4% CA mondial |

> **Recommandation** : ne redistribuer sous aucune forme avant d'avoir obtenu le statut CIF et l'accord de redistribution Twelve Data. Consulter un avocat spécialisé en droit financier avant toute évolution du périmètre.

---

## 9. Limitation de responsabilité — disclaimer README repo

### 9.1 Pourquoi un disclaimer dans le README ?

Bien que le repo soit privé et l'usage 100% personnel, l'ajout d'un disclaimer dans le README présente deux avantages :

1. **Protection réflexive** : cadre clairement l'intention de l'outil (usage personnel, pas conseil) si le repo était un jour accidentellement rendu public ou transmis
2. **Hygiène de projet** : formalise la conscience du risque financier inhérent aux turbos (produits à effet de levier pouvant mener à une perte totale du capital investi)

### 9.2 Texte recommandé — disclaimer README

Insérer le bloc suivant en début de README.md :

---

```markdown
## Avertissement légal / Legal Disclaimer

Ce projet est un outil d'aide à la décision de trading **strictement personnel**, développé et utilisé exclusivement par son auteur pour son propre compte. Il ne constitue en aucun cas :

- Un conseil en investissement au sens de l'article L. 321-1 du Code monétaire et financier
- Un service de gestion de portefeuille
- Une recommandation destinée à des tiers

**Les turbos sont des instruments financiers complexes à effet de levier. Ils peuvent entraîner la perte totale du capital investi, voire au-delà.** L'auteur ne garantit aucun résultat financier. Tout signal produit par ce bot est à apprécier dans le cadre d'une stratégie personnelle de gestion du risque.

Ce repo est **privé** et ne doit en aucun cas être redistribué, partagé ou rendu public sans l'accord explicite de l'auteur et sans mise en conformité préalable avec la réglementation AMF applicable.
```

---

### 9.3 Licences open source — vérification des dépendances

[HYPOTHÈSE : le stack n'est pas encore arbitré (Python vs Node/Bun) au stade actuel du projet. La vérification des licences open source doit être effectuée par @fullstack lors de l'arbitrage du stack.]

Points d'attention selon le stack probable :

**Si Python** : les bibliothèques clés (pandas, vectorbt, backtesting.py, python-telegram-bot, anthropic) sont sous licences permissives (MIT, BSD, Apache 2.0). Aucune dépendance GPL connue dans ces packages. Conforme pour un usage propriétaire personnel.

**Si Node/Bun** : vérifier les licences de toute dépendance ajoutée. Éviter les packages sous GPL v3 qui imposeraient de rendre le code source public si redistribué.

**Outil de vérification recommandé** : `pip-licenses` (Python) ou `license-checker` (Node) à intégrer dans le workflow de développement.

> Action @fullstack : lors de l'arbitrage du stack, lancer un audit de licences sur le `package.json` ou `requirements.txt` et signaler toute dépendance GPL.

---

## Handoff

---

**Handoff → @orchestrator**

- Fichiers produits : `/home/user/TradingApp/docs/legal/legal-audit.md`
- Décisions prises :
  - Statut AMF/MiFID II : CONFORME en usage personnel — aucun agrément requis tant que 100% perso
  - RGPD : exemption activité personnelle (Art. 2 §2 c RGPD) applicable — bonnes pratiques documentées
  - EU AI Act : classification risque limité (obligation de transparence, satisfaite de facto en usage perso)
  - PFU 2025 : taux corrigé à 31,4% (hausse effective depuis 01/01/2025)
  - Rétention Claude API : 7 jours, jamais utilisé pour entraînement — acceptable sans ZDR tant que pas de PII dans les prompts
- Points d'attention :
  - **R1 CRITIQUE** : toute redistribution d'un signal à un tiers = requalification immédiate en CIF — parcours 3-6 mois minimum
  - **R2 ELEVÉ** : sécurité repo GitHub — liste des secrets à externaliser en variables d'environnement transmise à @fullstack
  - **R4 MODERE** : PFU à 31,4% (pas 30%) depuis 01/01/2025 — journal des trades obligatoire pour formulaire 2074
  - Hypothèse H2 (plan Twelve Data) à valider par Thomas avant R&D edge
  - Licences open source à auditer par @fullstack lors de l'arbitrage du stack
  - Ce document est un draft de référence — validation par un avocat recommandée avant toute évolution du périmètre

**Handoff → @fullstack** (sécurité repo)

- Implémenter le `.gitignore` strict documenté en section 3.3
- Externaliser TOUS les secrets en variables d'environnement Replit (liste section 3.2)
- Activer GitHub Secret Scanning (Settings > Security > Secret scanning)
- Lors de l'arbitrage du stack : lancer `pip-licenses` ou `license-checker` et signaler toute dépendance GPL
- Ajouter le disclaimer README (section 9.2) au `README.md`

**Handoff → @ia** (politique Claude)

- Confirmer que les prompts envoyés à Claude n'incluront jamais de PII (chat_id, capital, identifiants)
- Évaluer si la rétention 7 jours de l'API standard est suffisante ou si un accord ZDR est requis selon l'architecture des prompts
- Si des données financières précises (P&L, capital) apparaissent dans les prompts : demander un accord ZDR à Anthropic

---
