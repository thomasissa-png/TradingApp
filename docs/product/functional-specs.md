<!-- Version: 2026-05-01T00:00 — @product-manager — Création initiale functional-specs V1 -->

# Spécifications fonctionnelles — TradingApp V1

> **KPI North Star** : P&L net mensuel après frais Bourse Direct (~0,99 € × 2 par trade) et fiscalité PFU 31,4 % (12,8 % IR + 18,6 % PS, taux 2025+ confirmé @legal).
> **Persona** : Thomas — trader particulier, capital 20-30 k€, turbos levier 5-20, exécution manuelle Bourse Direct, fenêtre 8h40-9h05 CET.
> **Périmètre** : Bot Telegram, usage 100 % personnel, non redistribué.
> Date : 2026-05-01 | Agent : @product-manager

---

## Résumé exécutif

- **Objectif** : Définir les comportements V1 du bot Telegram de façon implémentable sans ambiguïté par @fullstack, testable sans question par @qa.
- **Décisions clés** : 8 user stories couvrant les 6 états du signal (ACHAT, VENTE, NO-TRADE, ERREUR DATA, DEGRADED MODE + CUTOFF) ; format message Telegram 6 lignes max + 1 confiance ; seuil de confiance paramètre configurable (non fixé en dur) ; cutoff 8h55 CET strict ; journal SQLite obligatoire.
- **Dépendances** : H1 NEEDS-DECISION (hébergement), H2 NEEDS-DECISION (plan Twelve Data 1m), H3 [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct], seuil de confiance [HYPOTHÈSE : 6,5/10 — à calibrer en R&D].

---

## 1. User Stories V1

### US-01 : Envoyer un signal ACHAT/VENTE sur jour ouvré avec edge validé

**Persona** : Thomas
**Epic** : Signal quotidien
**Dépendances** : Aucune
**Priorité RICE** : R=22 I=10 C=9 E=1 → Score=198

#### Job-to-be-done
En tant que Thomas, je veux recevoir un signal structuré ACHAT ou VENTE sur Telegram entre 8h45 et 8h55 CET afin de décider en moins de 30 secondes si je passe un ordre chez Bourse Direct et contribuer positivement à mon P&L net mensuel (après PFU 31,4 %).

#### Contexte de navigation
- **Page/écran d'origine** : N/A — Thomas ouvre Telegram, le message arrive en push
- **Déclencheur** : Cron jours ouvrés EU déclenche le pipeline à 8h40 CET ; signal calculé entre 8h45 et 8h55
- **Page/écran de destination (succès)** : Conversation Telegram TradingApp — message ACHAT ou VENTE affiché
- **Page/écran de destination (échec)** : Voir US-04 (ERREUR DATA) et US-05 (Claude timeout)

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| sens | enum | Oui | ACHAT ou VENTE | exactement l'un des deux | ACHAT |
| sous_jacent | string | Oui | Doit figurer dans la liste V1 (section 3) | max 30 chars | DAX Turbo Call |
| entree | number | Oui | > 0, décimale 2 chiffres | > 0 | 3,42 |
| sl | number | Oui | > 0, < entree si ACHAT ; > entree si VENTE | > 0 | 3,21 |
| tp | number | Oui | > entree si ACHAT ; < entree si VENTE | > 0 | 3,85 |
| raison | string | Oui | 1 à 3 lignes max, pas de mots proscrits | 10–200 chars | gap haussier +0,8 % clôture US + ORB Xetra + score 7,1/10 |
| score_confiance | number | Oui | ≥ seuil_confiance, format X.X/10 | 0.0–10.0 | 7,1 |
| backtest_ref | string | Oui | Format #B-NNN, NNN = 3 chiffres, doit exister en SQLite | exactement #B-NNN | #B-031 |
| win_rate_backtest | number | Oui | 0–100, en % | entier | 61 |
| nb_trades_backtest | integer | Oui | ≥ 30 | ≥ 30 | 87 |
| drawdown_max_backtest | number | Oui | 0–100, négatif en %, format −XX % | | −18 |
| risque_max_eur | number | Oui | Calculé : (entree − sl) × nb_turbos ; > 0 | > 0 | 126 |
| capital_engage | number | Oui | Calculé : entree × nb_turbos | > 0 | 600 |
| fenetre_execution | string | Oui | Format "avant HH:MM CET" | | avant 8h55 CET |
| timestamp_calcul | datetime | Oui | ISO 8601, UTC | | 2026-05-04T06:42:00Z |

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Aucun message avant 8h45 — Telegram silencieux | Rien |
| Loading | Pipeline en cours 8h40-8h45 (calcul interne, Thomas ne voit pas cet état) | N/A côté Thomas |
| Vide | Edge calculé mais score < seuil → déclenche US-02 (NO-TRADE) | Voir US-02 |
| Erreur | Twelve Data fail → US-04 ; Claude timeout → US-05 | Voir US-04 / US-05 |
| Succès | Message ACHAT ou VENTE reçu entre 8h45 et 8h55 CET | Template section 2 |

#### Critères d'acceptance (Given/When/Then)

**Happy path :**
- [ ] GIVEN jour ouvré EU non férié FR, WHEN le pipeline cron s'exécute à 8h40 et produit un score ≥ seuil_confiance avant 8h55, THEN Thomas reçoit un message Telegram conforme au template ACHAT/VENTE dans la fenêtre 8h45-8h55 CET.
- [ ] GIVEN un signal ACHAT valide, WHEN Thomas lit le message, THEN le message contient exactement : sens, sous_jacent, entree, sl, tp, raison (1-3 lignes), score_confiance, backtest_ref, win_rate_backtest, nb_trades_backtest, drawdown_max_backtest, risque_max_eur, capital_engage, fenetre_execution — aucun champ manquant.
- [ ] GIVEN un signal émis, WHEN le pipeline a fini d'écrire en SQLite, THEN un enregistrement est créé dans la table `signals` avec tous les champs du message + timestamp_calcul + statut "envoyé".

**Cas d'erreur :**
- [ ] GIVEN score < seuil_confiance, WHEN le pipeline finit le calcul, THEN aucun message ACHAT/VENTE n'est envoyé — US-02 (NO-TRADE) est déclenchée à la place.
- [ ] GIVEN sl ≥ entree sur un signal ACHAT, WHEN le pipeline tente d'envoyer, THEN le signal est bloqué en interne, aucun message Telegram envoyé, erreur loguée en SQLite avec motif "SL invalide", US-04 déclenchée.

**Cas limites :**
- [ ] GIVEN le pipeline calcule le signal à 8h54:59 CET, WHEN l'envoi Telegram réussit avant 8h55:00, THEN le signal est valide et envoyé.
- [ ] GIVEN le pipeline calcule le signal à 8h55:01 CET (cutoff dépassé), WHEN le signal serait normalement envoyé, THEN le signal est invalidé (US-06 CUTOFF déclenchée), aucun message de trading envoyé.
- [ ] GIVEN un double appel cron (edge case relance infra), WHEN un signal a déjà été envoyé ce jour, THEN le pipeline détecte l'existant en SQLite et n'envoie pas de second signal.

**Permissions :**
- [ ] GIVEN une tentative d'envoi Telegram vers un chat_id différent du chat_id Thomas configuré, WHEN le pipeline tente l'envoi, THEN l'envoi est refusé (validation chat_id avant envoi).

**Données existantes :**
- [ ] GIVEN backtest_ref=#B-031 absent de la table `backtests` SQLite, WHEN le pipeline tente d'émettre le signal, THEN le signal est bloqué, erreur loguée "backtest_ref introuvable", US-04 déclenchée.

#### Payload API (pipeline interne — pas d'API publique)
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Authentification** : Token Bearer (variable d'environnement `TELEGRAM_BOT_TOKEN` — jamais en clair)
- **Rate limit** : 1 message/jour (enforced en interne par vérification SQLite)
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[message template]", "parse_mode": "Markdown" }`
- **Response succès** : `{ "ok": true, "result": { "message_id": ... } }` HTTP 200
- **Response erreur** : `{ "ok": false, "description": "..." }` HTTP 4xx/5xx → logguer + déclencher US-04

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| signal_envoyé | Message Telegram envoyé avec succès | sens, sous_jacent, score_confiance, backtest_ref, timestamp | activation |
| signal_lu_par_thomas | Inferred via Telegram read receipt (si disponible — API non garantie) | message_id, timestamp_read | activation |

#### Scénarios persona concrets
1. Thomas est dans le RER le lundi 4 mai 2026 à 8h42. Il déverrouille son téléphone et voit la notification TradingApp. Il lit le signal DAX Call — score 7,1, SL 3,21, risque 126 €. Il ouvre Bourse Direct à 8h45. Ordre exécuté à 8h49. Résultat attendu : message reçu conforme au template, ordre passable en < 10 min.
2. Thomas reçoit un signal à 8h46. Il est en réunion. Il lit le message à 8h58 — après le cutoff 8h55. Résultat attendu : le message indique "avant 8h55 CET" — Thomas sait que la fenêtre est passée et ne passe pas l'ordre.
3. Thomas reçoit un signal ACHAT sur EUR/USD. Il cherche le turbo sur Bourse Direct et ne le trouve pas. Résultat attendu : le message indique le sous-jacent tel que listé en section 3, qui a déjà été vérifié comme disponible [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct].
4. Thomas reçoit un signal à 8h47 avec score 7,3 et backtest_ref #B-031. Il se souvient avoir perdu sur ce pattern la semaine dernière. Il regarde le drawdown_max_backtest (−18 %). Son drawdown actuel est −12 %. Il décide de trader. Résultat attendu : toutes les infos pour comparer avec son historique sont dans le message.
5. Thomas fait son audit mensuel le 31 mai. Il ouvre le journal SQLite. Il retrouve les 18 signaux émis en mai, les 4 NO-TRADE, les P&L réels vs P&L attendus, les backtest_ref. Résultat attendu : journal complet, chaque signal traçable.

#### Definition of Done (checklist @fullstack)
- [ ] Pipeline cron déclenché jours ouvrés EU uniquement (calendrier férié FR intégré)
- [ ] Message Telegram envoyé dans la fenêtre 8h45-8h55 si score ≥ seuil
- [ ] Tous les champs du tableau "Données et champs" présents dans le message
- [ ] Enregistrement SQLite créé avec statut "envoyé"
- [ ] Test E2E : simuler un signal valide, vérifier présence dans Telegram + SQLite
- [ ] Validation chat_id avant envoi

#### Notes pour @qa
- Tester l'idempotence : deux appels cron le même jour → 1 seul signal envoyé.
- Tester la validation SL/TP (ACHAT : sl < entree < tp ; VENTE : tp < entree < sl).
- Vérifier que backtest_ref doit exister en SQLite avant envoi.

#### Notes pour @ia
- Le prompt Claude doit retourner un JSON structuré avec exactement les champs du tableau.
- Forcer la validation schema côté Python/Node avant l'envoi Telegram (jamais envoyer un champ manquant).

#### Notes pour @fullstack
- seuil_confiance = variable d'environnement `CONFIDENCE_THRESHOLD` (float, pas hardcodé).
- TELEGRAM_BOT_TOKEN et THOMAS_CHAT_ID en variables d'environnement, jamais en clair dans le code.

---

### US-02 : Envoyer un message NO-TRADE explicite quand aucun edge ne passe le seuil

**Persona** : Thomas
**Epic** : Signal quotidien
**Dépendances** : US-01 (pipeline partagé)
**Priorité RICE** : R=22 I=9 C=10 E=1 → Score=198

#### Job-to-be-done
En tant que Thomas, je veux recevoir un message "pas de trade aujourd'hui" clair avec la raison (score max relevé, seuil) afin de fermer Telegram sans chercher un trade alternatif, conformément à JTBD 3.

#### Contexte de navigation
- **Page/écran d'origine** : Telegram — Thomas ouvre la conv le matin
- **Déclencheur** : Pipeline complète le calcul, score max < seuil_confiance, avant 8h55 CET
- **Page/écran de destination (succès)** : Message NO-TRADE reçu — Thomas ferme Telegram
- **Page/écran de destination (échec)** : N/A

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| score_max_releve | number | Oui | 0.0–10.0 | décimale 1 chiffre | 5,1 |
| seuil_confiance | number | Oui | Valeur du paramètre CONFIDENCE_THRESHOLD | décimale 1 chiffre | 6,5 |
| prochaine_fenetre | string | Oui | Format "demain HH:MM" ou "lundi HH:MM" selon calendrier | | demain 8h45 |

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Silence avant que le pipeline finisse | Rien |
| Loading | Calcul en cours (interne) | N/A Thomas |
| Vide | N/A — le NO-TRADE est lui-même l'état "vide d'edge" | N/A |
| Erreur | Si le pipeline échoue avant de pouvoir calculer → US-04 à la place | Voir US-04 |
| Succès | Message NO-TRADE reçu avec score_max et seuil | Template section 2 |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN score max relevé < seuil_confiance, WHEN le pipeline termine le calcul avant 8h55, THEN Thomas reçoit le message NO-TRADE avec score_max_releve et seuil_confiance affichés.
- [ ] GIVEN un jour ouvré normal (lundi-vendredi, non férié FR), WHEN le pipeline envoie un NO-TRADE, THEN prochaine_fenetre indique "demain 8h45".
- [ ] GIVEN un vendredi, WHEN le pipeline envoie un NO-TRADE, THEN prochaine_fenetre indique "lundi 8h45".

**Cas d'erreur :**
- [ ] GIVEN pipeline qui plante après calcul mais avant envoi Telegram, WHEN le cron se termine en erreur, THEN l'absence de message est loguée en SQLite comme "signal_manqué" avec timestamp, et US-04 est déclenchée.

**Cas limites :**
- [ ] GIVEN score_max_releve = seuil_confiance exactement (égalité), WHEN le pipeline évalue, THEN le signal passe (≥ seuil = GO, pas NO-TRADE).
- [ ] GIVEN 3 semaines consécutives de NO-TRADE, WHEN le pipeline envoie le 15e NO-TRADE consécutif (estimé), THEN un flag `revue_seuil_requise=true` est enregistré en SQLite (trigger de la condition signaux d'arrêt personas.md).

**Permissions :**
- [ ] GIVEN chat_id invalide, WHEN envoi Telegram du NO-TRADE, THEN erreur loguée — même traitement que US-01.

**Données existantes :**
- [ ] GIVEN un NO-TRADE déjà envoyé aujourd'hui (double cron), WHEN le pipeline tente un second envoi, THEN aucun second message envoyé (idempotence).

#### Payload API
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[no-trade template]", "parse_mode": "Markdown" }`

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| no_trade | Message NO-TRADE envoyé avec succès | score_max_releve, seuil_confiance, timestamp | activation |

#### Scénarios persona concrets
1. Thomas ouvre Telegram le mercredi 6 mai 2026 à 8h43. Il voit "Pas de trade aujourd'hui — score max 5,1/10, seuil 6,5." Il ferme Telegram et prend son café. Résultat attendu : aucune recherche alternative de trade.
2. C'est vendredi. Le NO-TRADE indique "prochaine fenêtre lundi 8h45". Thomas sait qu'il n'y a rien jusqu'à lundi. Résultat attendu : message de prochaine fenêtre adapté au calendrier.
3. Thomas est en drawdown à −12 %. Il reçoit un NO-TRADE. Il est soulagé — aucune pression de trader dans un contexte défavorable. Résultat attendu : le NO-TRADE est présenté comme une décision neutre, sans connotation d'échec.
4. Thomas vérifie son journal en fin de mois. Il voit 4 NO-TRADE en mai. Il vérifie si le seuil est trop élevé. Résultat attendu : chaque NO-TRADE est enregistré en SQLite avec score_max_releve.
5. Troisième semaine consécutive sans signal GO. Thomas voit le 15e NO-TRADE. Le journal indique `revue_seuil_requise=true`. Résultat attendu : Thomas est alerté que le seuil doit être revu.

#### Definition of Done (checklist @fullstack)
- [ ] Message NO-TRADE envoyé si score max < seuil
- [ ] prochaine_fenetre calculée dynamiquement (calendrier EU)
- [ ] Enregistrement SQLite créé avec statut "no_trade"
- [ ] Flag revue_seuil_requise déclenché après 15 NO-TRADE consécutifs (paramètre configurable)
- [ ] Test E2E : forcer score à 0, vérifier NO-TRADE reçu

---

### US-03 : Inhiber le cron sur jours fériés FR

**Persona** : Thomas
**Epic** : Fiabilité du signal
**Dépendances** : US-01, US-02
**Priorité RICE** : R=22 I=8 C=10 E=1 → Score=176

#### Job-to-be-done
En tant que Thomas, je veux que le bot ne s'exécute pas les jours fériés français (marchés EU fermés) afin de ne pas recevoir de signal inutile ou basé sur des données absentes.

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Jour férié FR détecté en amont du cron | Rien envoyé |
| Loading | N/A — cron inhibé avant démarrage pipeline | N/A |
| Vide | N/A | N/A |
| Erreur | Erreur dans la lecture du calendrier férié → cron se comporte comme jour normal + log d'avertissement | Log interne uniquement |
| Succès | Silence Telegram — aucun message envoyé | Aucun message |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN le 8 mai 2026 (Victoire 1945, férié FR), WHEN le cron est planifié à 8h40, THEN le cron est inhibé : aucun pipeline lancé, aucun message Telegram envoyé.
- [ ] GIVEN le 19 mai 2026 (Pentecôte, férié FR), WHEN le cron est planifié, THEN même comportement.
- [ ] GIVEN le calendrier des jours fériés FR est chargé au démarrage du service, WHEN une nouvelle année commence, THEN le calendrier est mis à jour automatiquement (source : API ou fichier statique annuel).

**Cas d'erreur :**
- [ ] GIVEN une erreur de lecture du fichier/API calendrier, WHEN le cron démarre, THEN une alerte est loguée "calendrier_error" en SQLite et le pipeline est lancé normalement (fail-open pour ne pas manquer un signal réel).

**Cas limites :**
- [ ] GIVEN un samedi ou dimanche, WHEN le cron serait planifié, THEN le cron scheduler ne déclenche pas (jours ouvrés = lundi-vendredi non fériés FR uniquement).

**Permissions :**
- [ ] N/A — story backend sans UI

**Données existantes :**
- [ ] GIVEN calendrier chargé de l'année N, WHEN on est en janvier N+1 avant la mise à jour, THEN le système logue un avertissement "calendrier_expiration" mais continue avec l'ancien calendrier.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| cron_inhibé_férié | Cron skippé pour jour férié | date, motif="férié_FR" | activation |

#### Notes pour @fullstack
- Source calendrier fériés FR recommandée : bibliothèque `workalendar` (Python) ou API `date.nager.at` (gratuit, REST). Paramètre `COUNTRY=FR`.
- Stocker les fériés de l'année en cache SQLite au démarrage, rechargement annuel.

---

### US-04 : Envoyer un message ERREUR DATA si Twelve Data est indisponible

**Persona** : Thomas
**Epic** : Fiabilité du signal
**Dépendances** : US-01
**Priorité RICE** : R=22 I=9 C=9 E=1 → Score=178

#### Job-to-be-done
En tant que Thomas, je veux être informé explicitement si les données de marché sont indisponibles afin de ne pas recevoir de silence ambiguë et de savoir que le bot a bien tourné ce matin.

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| motif_erreur | string | Oui | Description technique compréhensible | max 100 chars | Twelve Data timeout après 30 s |
| heure_erreur | string | Oui | Format HH:MM CET | | 8h47 |
| retry_tenté | boolean | Oui | true si retry effectué | | true |

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Twelve Data répond normalement | N/A (pipeline normal) |
| Loading | Retry en cours (max 2 retries, 5 s entre chaque) | Interne uniquement |
| Vide | N/A | N/A |
| Erreur | Tous les retries épuisés → message ERREUR DATA envoyé | Template section 2 |
| Succès | Twelve Data répond avant épuisement retries → pipeline normal | N/A (signal normal) |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN Twelve Data retourne une erreur HTTP 5xx ou timeout > 30 s, WHEN le pipeline a épuisé 2 retries (5 s entre chaque), THEN Thomas reçoit un message ERREUR DATA avec motif_erreur et heure_erreur.
- [ ] GIVEN message ERREUR DATA envoyé, WHEN l'erreur est loguée, THEN SQLite enregistre statut="erreur_data", motif, heure, retry_tenté=true.

**Cas d'erreur :**
- [ ] GIVEN Twelve Data retourne HTTP 429 (rate limit), WHEN le pipeline reçoit la réponse, THEN le pipeline attend 60 s avant un unique retry supplémentaire, puis envoie ERREUR DATA si échec.

**Cas limites :**
- [ ] GIVEN Twelve Data répond après le 1er retry, WHEN le signal est calculé avant 8h55, THEN le pipeline continue normalement, aucun message ERREUR DATA envoyé.
- [ ] GIVEN timeout 8h55 atteint pendant le retry, WHEN le calcul n'est pas terminé, THEN CUTOFF s'applique (US-06) — pas de message ERREUR DATA, mais US-06.

**Permissions :**
- [ ] N/A — story backend

**Données existantes :**
- [ ] GIVEN ERREUR DATA déjà loguée aujourd'hui, WHEN un second cron tente de s'exécuter, THEN idempotence : aucun second message envoyé.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| erreur_twelvedata | Message ERREUR DATA envoyé | motif_erreur, retry_tenté, timestamp | activation |

#### Notes pour @fullstack
- Implémenter un circuit breaker : si Twelve Data échoue 3 jours consécutifs, logguer une alerte critique en SQLite.
- Ne jamais envoyer un signal calculé sur des données partielles ou en cache périmé (G7 brand-platform : pas de signal forcé).

---

### US-05 : Gérer le timeout Claude et envoyer un message DEGRADED MODE

**Persona** : Thomas
**Epic** : Fiabilité du signal
**Dépendances** : US-01, US-04
**Priorité RICE** : R=22 I=8 C=9 E=1 → Score=158

#### Job-to-be-done
En tant que Thomas, je veux être informé explicitement si le scoring Claude a échoué afin de savoir que les données de marché étaient disponibles mais que la justification structurée n'a pas pu être générée — sans recevoir de signal forcé sans justification.

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| motif_erreur_claude | string | Oui | "timeout", "erreur_api", "réponse_invalide" | enum | timeout |
| données_marché_ok | boolean | Oui | true si Twelve Data a répondu | | true |
| heure_erreur | string | Oui | Format HH:MM CET | | 8h49 |

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Claude répond en < 30 s | N/A (pipeline normal) |
| Loading | Attente réponse Claude (timeout = 45 s max) | Interne |
| Vide | N/A | N/A |
| Erreur | Timeout ou erreur API Claude → message DEGRADED MODE envoyé | Template section 2 |
| Succès | Claude répond, JSON valide retourné → pipeline normal | N/A |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN Claude ne répond pas dans 45 s, WHEN le timeout est atteint, THEN Thomas reçoit un message DEGRADED MODE avec motif "timeout" — aucun signal de trading envoyé.
- [ ] GIVEN Claude retourne une réponse JSON invalide (champ manquant ou score hors format), WHEN le pipeline valide le schema, THEN le pipeline rejette la réponse, log "réponse_invalide", envoie DEGRADED MODE.

**Cas d'erreur :**
- [ ] GIVEN erreur Anthropic API (HTTP 5xx), WHEN le pipeline reçoit la réponse, THEN 1 retry après 10 s, puis DEGRADED MODE si échec.

**Cas limites :**
- [ ] GIVEN timeout Claude atteint à 8h54 (juste avant cutoff), WHEN le DEGRADED MODE serait envoyé, THEN DEGRADED MODE envoyé (pas CUTOFF — le pipeline a bien tourné, c'est Claude qui a failli).
- [ ] GIVEN réponse Claude avec score_confiance = null, WHEN validation schema, THEN rejeté comme "réponse_invalide".

**Permissions :**
- [ ] N/A — story backend

**Données existantes :**
- [ ] GIVEN DEGRADED MODE loggué aujourd'hui, WHEN double cron, THEN idempotence maintenue.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| erreur_claude | Message DEGRADED MODE envoyé | motif_erreur_claude, données_marché_ok, timestamp | activation |

#### Notes pour @ia
- Le prompt Claude doit inclure un JSON schema strict en output avec types obligatoires.
- En cas de réponse partielle (streaming coupé), le pipeline doit rejeter et logger — jamais envoyer un signal incomplet.

---

### US-06 : Invalider tout signal calculé après 8h55 CET (CUTOFF strict)

**Persona** : Thomas
**Epic** : Fiabilité du signal
**Dépendances** : US-01
**Priorité RICE** : R=22 I=10 C=10 E=1 → Score=220

#### Job-to-be-done
En tant que Thomas, je veux que le bot n'envoie jamais un signal calculé après 8h55 CET afin de ne pas être incité à passer un ordre hors fenêtre d'ouverture, où les conditions de marché ont changé.

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Calcul terminé avant 8h55 → signal envoyé normalement | N/A (pipeline normal) |
| Loading | Calcul en cours à 8h54:59 — fenêtre encore ouverte | N/A |
| Vide | N/A | N/A |
| Erreur | Calcul terminé après 8h55:00 → message CUTOFF loggué, aucun signal envoyé | Silence Telegram (pas de message CUTOFF à Thomas — il ne doit pas être incité à trader) |
| Succès | Signal envoyé avant 8h55 | Template normal |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN calcul terminé à 8h54:59 CET, WHEN le timestamp_calcul est vérifié avant envoi Telegram, THEN le signal est envoyé.

**Cas d'erreur :**
- [ ] GIVEN calcul terminé à 8h55:01 CET, WHEN le timestamp_calcul est vérifié avant envoi Telegram, THEN le signal est bloqué, SQLite enregistre statut="cutoff_invalide" avec timestamp_calcul, aucun message Telegram envoyé.
- [ ] GIVEN Twelve Data lent (réponse reçue à 8h53) + Claude lent (réponse reçue à 8h55:30), WHEN le pipeline vérifie le cutoff, THEN signal invalidé, statut="cutoff_invalide".

**Cas limites :**
- [ ] GIVEN le cron démarre à 8h40 mais le serveur est en retard de 20 min (8h60 = 9h00), WHEN le calcul se termine à 9h00, THEN signal invalidé par cutoff (8h55 passé).
- [ ] GIVEN horloge serveur non synchronisée (drift > 1 min), WHEN le pipeline vérifie le cutoff, THEN utiliser toujours le timestamp NTP serveur (jamais l'heure locale non synchronisée). @fullstack doit s'assurer que NTP est actif sur l'hébergeur.

**Permissions :**
- [ ] N/A — story backend

**Données existantes :**
- [ ] GIVEN 3 CUTOFF consécutifs (pipeline systématiquement trop lent), WHEN le 3e cutoff est logué, THEN flag `pipeline_trop_lent=true` enregistré en SQLite — alerte pour @fullstack.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| cutoff_invalide | Signal bloqué après 8h55 | timestamp_calcul, motif="cutoff", sous_jacent | activation |

#### Notes pour @fullstack
- Le timestamp de référence est `datetime.utcnow()` converti en CET (UTC+1 ou UTC+2 selon DST).
- La vérification cutoff se fait AVANT l'appel Telegram sendMessage, jamais après.
- NTP obligatoire sur le serveur (Replit gère cela nativement ; Hetzner : vérifier ntpd actif).

---

### US-07 : Journaliser chaque signal (envoyé, no-trade, erreur) en SQLite

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-01, US-02, US-03, US-04, US-05, US-06
**Priorité RICE** : R=22 I=8 C=10 E=1 → Score=176

#### Job-to-be-done
En tant que Thomas, je veux que chaque signal (y compris les NO-TRADE et erreurs) soit enregistré en SQLite afin de pouvoir auditer mes 30 minutes mensuelles et comparer le P&L net réel (après PFU 31,4 %) au P&L backtest.

#### Schéma SQLite — table `signals`
| Colonne | Type | Obligatoire | Description |
|---|---|---|---|
| id | INTEGER PRIMARY KEY | Oui | Auto-increment |
| date | DATE | Oui | Date du signal (YYYY-MM-DD) |
| timestamp_calcul | DATETIME | Oui | ISO 8601 UTC |
| statut | TEXT | Oui | envoyé / no_trade / erreur_data / erreur_claude / cutoff_invalide / cron_inhibé_férié |
| sens | TEXT | Si statut=envoyé | ACHAT ou VENTE |
| sous_jacent | TEXT | Si statut=envoyé | ex: DAX Turbo Call |
| entree | REAL | Si statut=envoyé | |
| sl | REAL | Si statut=envoyé | |
| tp | REAL | Si statut=envoyé | |
| score_confiance | REAL | Si statut=envoyé | |
| backtest_ref | TEXT | Si statut=envoyé | #B-NNN |
| score_max_releve | REAL | Si statut=no_trade | |
| motif_erreur | TEXT | Si statut=erreur_* | |
| pl_brut_eur | REAL | Non (rempli post-trade) | Rempli par Thomas via US-08 |
| pl_net_eur | REAL | Non (calculé) | pl_brut − frais − PFU 31,4 % |
| mae_eur | REAL | Non (rempli post-trade) | Maximum Adverse Excursion |
| mfe_eur | REAL | Non (rempli post-trade) | Maximum Favorable Excursion |
| trade_effectué | BOOLEAN | Non (rempli post-trade) | true si Thomas a exécuté |
| revue_seuil_requise | BOOLEAN | Non | true si 3 semaines consécutives NO-TRADE |
| pipeline_trop_lent | BOOLEAN | Non | true si 3 CUTOFF consécutifs |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN n'importe quel état de signal (envoyé, no_trade, erreur, cutoff), WHEN le pipeline termine, THEN un enregistrement est créé dans `signals` avec au minimum : id, date, timestamp_calcul, statut.
- [ ] GIVEN un signal envoyé, WHEN l'enregistrement est créé, THEN tous les champs "Si statut=envoyé" sont remplis (valeurs non nulles).

**Cas d'erreur :**
- [ ] GIVEN une erreur d'écriture SQLite, WHEN le pipeline tente d'insérer, THEN l'erreur est loguée dans un fichier log local (fallback), Telegram reçoit un message ERREUR DATA si ce n'est pas déjà fait.

**Cas limites :**
- [ ] GIVEN double écriture le même jour (double cron), WHEN le pipeline détecte un enregistrement existant pour `date=today`, THEN aucun second enregistrement créé (contrainte UNIQUE sur `date`).

**Permissions :**
- [ ] Accès SQLite lecture/écriture par le pipeline uniquement. Jamais exposé en HTTP public.

**Données existantes :**
- [ ] GIVEN migration depuis un ancien schéma (si applicable), WHEN le service démarre, THEN migration appliquée sans perte de données (`ALTER TABLE ADD COLUMN IF NOT EXISTS`).

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| journal_écrit | Enregistrement SQLite créé | statut, date, sous_jacent (si applicable) | retention |

---

### US-08 : Permettre à Thomas de logguer le résultat de son trade (post-exécution)

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-07
**Priorité RICE** : R=22 I=7 C=8 E=1 → Score=123

#### Job-to-be-done
En tant que Thomas, je veux pouvoir enregistrer le P&L réel de mon trade (brut, net PFU 31,4 %, MAE, MFE) dans le journal afin de comparer les résultats live aux prévisions backtest lors de mes audits mensuels (JTBD 4).

#### Contexte de navigation
- **Page/écran d'origine** : N/A — Thomas envoie une commande Telegram (ex: `/trade 2026-05-04 +258 MAE=-50 MFE=+265`) ou interface CLI
- **Déclencheur** : Thomas veut logguer un trade après clôture (en soirée ou le lendemain matin)
- **Page/écran de destination (succès)** : Confirmation Telegram "Journal mis à jour pour le [date]."
- **Page/écran de destination (échec)** : Telegram "Erreur : aucun signal envoyé le [date]." ou "Format invalide."

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| date_trade | DATE | Oui | YYYY-MM-DD, doit exister dans signals avec statut=envoyé | | 2026-05-04 |
| pl_brut_eur | number | Oui | Peut être négatif (perte) | décimale 2 chiffres | +258.00 |
| mae_eur | number | Oui | ≤ 0 (drawdown en cours de trade) | décimale 2 chiffres | −50.00 |
| mfe_eur | number | Oui | ≥ 0 (gain max en cours de trade) | décimale 2 chiffres | +265.00 |
| trade_effectué | boolean | Oui | true si trade passé, false si signal ignoré | | true |

#### 5 états du signal Telegram
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Attente commande Thomas | N/A |
| Loading | Écriture SQLite en cours | N/A |
| Vide | Aucun signal ce jour-là → message d'erreur | "Aucun signal envoyé le [date]." |
| Erreur | Format commande invalide | "Format invalide. Usage : /trade YYYY-MM-DD [+/-PL] MAE=[val] MFE=[val]" |
| Succès | Enregistrement mis à jour | "Journal mis à jour pour le 4 mai. P&L net : +176 € (après PFU 31,4 %)." |

#### Critères d'acceptance

**Happy path :**
- [ ] GIVEN signal envoyé le 4 mai (statut=envoyé en SQLite), WHEN Thomas envoie `/trade 2026-05-04 +258 MAE=-50 MFE=+265 trade=true`, THEN pl_brut, mae, mfe, trade_effectué sont mis à jour dans `signals`, pl_net calculé (pl_brut − 1,98 € frais − PFU 31,4 % sur la plus-value positive).
- [ ] GIVEN mise à jour réussie, WHEN le bot répond, THEN message de confirmation avec pl_net_eur affiché.

**Cas d'erreur :**
- [ ] GIVEN date_trade inexistante en SQLite, WHEN Thomas envoie la commande, THEN message "Aucun signal envoyé le [date]."
- [ ] GIVEN format de commande invalide (champ manquant), WHEN Thomas envoie la commande, THEN message d'aide avec format attendu.

**Cas limites :**
- [ ] GIVEN trade_effectué=false (Thomas n'a pas tradé malgré signal GO), WHEN journal mis à jour, THEN pl_brut=0, pl_net=0, statut conservé "envoyé" mais champ trade_effectué=false.
- [ ] GIVEN pl_brut négatif (perte), WHEN pl_net calculé, THEN pas de PFU appliqué sur les pertes (PFU s'applique uniquement sur les gains — cohérence fiscale PFU 31,4 %).

**Permissions :**
- [ ] GIVEN commande /trade envoyée depuis un chat_id différent de THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN commande ignorée silencieusement (sécurité).

**Données existantes :**
- [ ] GIVEN un trade déjà logué pour cette date, WHEN Thomas renvoie la commande, THEN mise à jour (update, pas création d'un doublon).

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| trade_logué | Commande /trade traitée avec succès | date, pl_brut, pl_net, trade_effectué | retention |

#### Notes pour @fullstack
- Calcul pl_net : si pl_brut > 0 → `pl_net = pl_brut - (0.99 × 2) - (pl_brut × 0.314)`. Si pl_brut ≤ 0 → `pl_net = pl_brut - (0.99 × 2)`.
- Frais Bourse Direct = 0,99 € × 2 (entrée + sortie), valeur constante `BOURSE_DIRECT_FRAIS_ALLER_RETOUR = 1.98`.

---

### US-09 : Envoyer l'audit hebdomadaire automatique et répondre à `/journal-week`

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-07, US-08
**Priorité RICE** : R=22 I=8 C=9 E=1 → Score=158

#### Job-to-be-done
En tant que Thomas, je veux recevoir un résumé hebdomadaire automatique chaque vendredi à 18h00 CET (et pouvoir le demander à tout moment via `/journal-week`) afin de piloter ma stratégie semaine par semaine et détecter les signaux d'arrêt avant qu'ils ne deviennent critiques.

#### Contexte de navigation
- **Page/écran d'origine** : N/A — push automatique (cron vendredi 18h00 CET) ou Thomas envoie `/journal-week` manuellement dans Telegram
- **Déclencheur** : (a) cron vendredi 18h00 CET ; (b) commande Telegram `/journal-week` à tout moment
- **Page/écran de destination (succès)** : Conversation Telegram TradingApp — message résumé hebdo affiché
- **Page/écran de destination (échec)** : Telegram — message d'erreur si calcul impossible (données insuffisantes)

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| date_lundi | DATE | Oui | YYYY-MM-DD, lundi de la semaine calculée | | 2026-04-27 |
| date_vendredi | DATE | Oui | YYYY-MM-DD, vendredi de la semaine calculée | | 2026-05-01 |
| nb_signaux_go | integer | Oui | ≥ 0 | | 3 |
| nb_no_trade | integer | Oui | ≥ 0 | | 2 |
| nb_erreurs | integer | Oui | ≥ 0 | | 0 |
| nb_trades_loggues | integer | Oui | ≥ 0, ≤ nb_signaux_go | | 3 |
| pl_brut_semaine | number | Oui | Somme pl_brut_eur des trades de la semaine (0 si aucun trade logué) | décimale 2 chiffres | +580.00 |
| pl_net_semaine | number | Oui | Somme pl_net_eur des trades de la semaine après frais + PFU 31,4 % proportionnel | décimale 2 chiffres | +412.00 |
| drawdown_max_semaine | number | Oui | Min MAE cumulé de la semaine en % du capital dédié ; 0 si aucun trade | 0–100 | 7 |
| win_rate_semaine | number | Oui | % trades gagnants sur la semaine (null si nb_trades_loggues = 0) | 0–100 | 67 |
| win_rate_backtest_ref | number | Oui | Win rate backtest moyen des signaux GO de la semaine | 0–100 | 61 |
| statut_semaine | enum | Oui | OK / ALERTE / ARRÊT | | OK |
| signaux_arret_actifs | string | Non | Liste des flags R7 actifs (drawdown_alerte, win_rate_alerte, etc.) ou null | max 200 chars | null |

#### 5 états UI (Gate G21)
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Silence Telegram jusqu'au vendredi 18h00 | Rien |
| Loading | Calcul du résumé en cours (agrégation SQLite) | Interne — durée max 10 s |
| Vide | Aucun signal cette semaine (ex : semaine de jours fériés) | "Aucune activité cette semaine. Prochaine fenêtre : lundi 8h45." |
| Erreur | Erreur d'agrégation SQLite ou calcul impossible | "Résumé hebdomadaire indisponible. Données SQLite inaccessibles à [HEURE] CET." |
| Succès | Message résumé conforme au template section 2 envoyé | Template RÉSUMÉ HEBDO (docs/copy/message-templates.md section 5) |

#### Critères d'acceptance (Given/When/Then)

**Happy path :**
- [ ] GIVEN vendredi 1er mai 2026 à 18h00:00 CET (heure NTP serveur), WHEN le cron hebdo se déclenche, THEN Thomas reçoit le message résumé hebdo dans la fenêtre 18h00-18h01 CET (± 1 min).
- [ ] GIVEN un message résumé envoyé, WHEN Thomas lit le message, THEN il contient exactement : période (date_lundi à date_vendredi), nb_signaux_go, nb_no_trade, nb_erreurs, nb_trades_loggues, pl_brut_semaine, pl_net_semaine, drawdown_max_semaine, win_rate_semaine vs win_rate_backtest_ref, statut_semaine — aucun champ manquant.
- [ ] GIVEN Thomas envoie `/journal-week` un mardi à 14h00, WHEN le bot reçoit la commande, THEN le bot répond avec le résumé de la semaine en cours (du lundi précédent au jour J inclus) en < 10 s.
- [ ] GIVEN calcul terminé, WHEN les données sont agrégées, THEN le temps de calcul total est < 10 s (agrégation SQLite sur 7 jours max).
- [ ] GIVEN statut_semaine = ALERTE ou ARRÊT, WHEN le message est envoyé, THEN le message contient une section P0 supplémentaire indiquant le flag R7 actif et l'action requise (cf. user-flows.md Flow 4 étape 3).

**Cas d'erreur :**
- [ ] GIVEN erreur d'accès SQLite lors du calcul, WHEN le cron tente d'agréger les données, THEN Thomas reçoit "Résumé hebdomadaire indisponible. Données SQLite inaccessibles à [HH:MM] CET." — aucun message partiel envoyé.
- [ ] GIVEN `/journal-week` envoyée depuis un chat_id différent de THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN la commande est ignorée silencieusement (sécurité — même règle que US-08).

**Cas limites :**
- [ ] GIVEN semaine sans aucun trade logué (nb_trades_loggues = 0), WHEN le résumé est calculé, THEN pl_brut_semaine = 0, pl_net_semaine = 0, win_rate_semaine = null, message affiché sans ces métriques (ou mention "aucun trade logué cette semaine").
- [ ] GIVEN cron vendredi 18h00 et jour férié FR (ex : 1er mai — Fête du Travail), WHEN le cron est planifié, THEN le résumé hebdo est envoyé quand même (le résumé de semaine n'est pas inhibé par le calendrier ouvré — contrairement au signal quotidien US-03 qui l'est).
- [ ] GIVEN double appel cron le même vendredi soir, WHEN un résumé a déjà été envoyé ce vendredi, THEN aucun second résumé envoyé (idempotence : vérification via SQLite colonne `journal_week_sent_at`).
- [ ] GIVEN `/journal-week` envoyée un lundi en début de semaine (0 signal depuis lundi), WHEN le bot calcule, THEN le bot répond "Semaine en cours : aucun signal depuis le lundi [DATE]. Prochaine fenêtre : demain 8h45."

**Permissions :**
- [ ] GIVEN commande `/journal-week` envoyée depuis un chat_id non autorisé, WHEN le bot reçoit la commande, THEN ignorée silencieusement — aucun message de réponse.

**Données existantes :**
- [ ] GIVEN trades loggués avec pl_brut négatif (pertes), WHEN pl_net_semaine est calculé, THEN PFU 31,4 % n'est PAS appliqué sur les trades en perte (cohérence fiscale US-08 règle pl_net) — seuls les gains positifs sont taxés.

#### Payload API (pipeline interne)
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Authentification** : Token Bearer (`TELEGRAM_BOT_TOKEN`)
- **Rate limit** : 1 message résumé/vendredi + réponses à commandes illimitées (Thomas seul utilisateur)
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[résumé hebdo template]", "parse_mode": "Markdown" }`
- **Response succès** : `{ "ok": true, "result": { "message_id": ... } }` HTTP 200 — logguer `journal_week_sent_at` en SQLite
- **Response erreur** : `{ "ok": false, "description": "..." }` HTTP 4xx/5xx → logguer erreur en SQLite, ne pas retry (résumé hebdo non bloquant)

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| `journal_week_pushed` | Résumé hebdo automatique envoyé (cron vendredi 18h) | statut_semaine, nb_signaux_go, pl_net_semaine, win_rate_semaine, timestamp | retention |
| `journal_week_command_invoked` | Thomas envoie `/journal-week` manuellement | timestamp, jour_semaine, nb_signaux_depuis_lundi | retention |
| `weekly_alert_triggered` | statut_semaine = ALERTE ou ARRÊT dans le résumé | flags_actifs, drawdown_max_semaine, win_rate_semaine, timestamp | retention |

#### Scénarios persona concrets
1. Thomas est chez lui vendredi 1er mai 2026 à 18h00. Son téléphone vibre. Il voit sur l'écran de verrouillage "TradingApp — Semaine 27 avr.-1 mai | GO : 3 | P&L net : +412 € | Statut : OK". Il déverrouille, lit le résumé en 2 min. Aucune alerte. Il remet son téléphone. Résultat attendu : message complet reçu à 18h00 ± 1 min, statut OK visible sans action.
2. Thomas a oublié de logger ses trades de la semaine (nb_trades_loggues = 0). Il reçoit le résumé vendredi 18h. Le message indique "Trades loggués : 0/3 — P&L indisponible. Envoie /trade [date] [résultat] pour compléter." Résultat attendu : message incite Thomas à logger sans bloquer l'envoi du résumé.
3. Thomas est en déplacement vendredi soir. Il reçoit le push mais n'ouvre pas Telegram. Il voit sur l'écran verrouillé "Statut : ALERTE — Drawdown 18 %". Il ouvre immédiatement. Résultat attendu : statut visible sans déverrouiller, ALERTE pousse Thomas à ouvrir.
4. Thomas envoie `/journal-week` un mercredi à 10h00 après une mauvaise journée. Il veut voir l'état de la semaine. Le bot répond avec les données du lundi au mercredi inclus (3 signaux, 2 trades loggués, P&L partiel). Résultat attendu : réponse en < 10 s avec données semaine en cours.
5. Semaine de 1er mai (férié lundi). Le bot envoie le résumé vendredi 18h pour la semaine du 27 avr.-1 mai — seulement 3 jours ouvrés, 0 signal lundi (cron inhibé par US-03), 3 signaux mar-jeu. Résultat attendu : résumé cohérent avec les jours effectivement traités.

#### Definition of Done (checklist @fullstack)
- [ ] Cron vendredi 18h00 CET configuré (séparé du cron quotidien 8h40)
- [ ] Agrégation SQLite sur la semaine courante (lundi 00h00 → vendredi 23h59) en < 10 s
- [ ] Calcul pl_net_semaine avec règle fiscale PFU (gains uniquement)
- [ ] Commande `/journal-week` reconnue par le bot handler, réponse en < 10 s
- [ ] Idempotence : colonne `journal_week_sent_at` en SQLite (table `journal_weeks`)
- [ ] Test E2E : simuler une semaine complète (3 GO + 2 NO-TRADE), vérifier message conforme

#### Notes pour @qa
- Tester idempotence : deux appels cron vendredi même soir → 1 seul résumé envoyé.
- Tester calcul PFU sur semaine mixte (trades gagnants + perdants) → PFU sur gains uniquement.
- Tester `/journal-week` un lundi à J+0 (0 signal) → message "aucun signal depuis lundi".
- Tester `/journal-week` depuis chat_id non autorisé → silence.

#### Notes pour @ux
- Template résumé hebdo : conforme wireframe ASCII user-flows.md Template 5. Statut en dernière ligne (visible sans scroll mobile).
- Si statut ALERTE ou ARRÊT : section P0 en dessous du résumé standard, séparée par "---".

#### Notes pour @fullstack
- Nouveau cron à créer : `CRON_WEEKLY="0 17 * * 5"` (UTC, vendredi 17h00 UTC = 18h00 CET hiver, ajuster pour heure d'été : `0 16 * * 5`). Ou utiliser la même logique DST que le cron quotidien.
- Table SQLite : `journal_weeks (id, week_start DATE, week_end DATE, journal_week_sent_at DATETIME, statut TEXT)`.
- Calcul `win_rate_semaine` : NULL si `nb_trades_loggues = 0` (ne pas afficher "0 %", afficher "aucun trade logué").

---

### US-10 : Confirmer la poursuite mensuelle via `/continue`

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-07, US-08, US-09
**Priorité RICE** : R=22 I=9 C=9 E=1 → Score=178

#### Job-to-be-done
En tant que Thomas, je veux répondre `/continue` au rapport mensuel afin de confirmer formellement que je poursuis la stratégie pour le mois suivant, avec trace écrite en SQLite de ma décision.

#### Contexte de navigation
- **Page/écran d'origine** : Telegram — Thomas lit le rapport mensuel automatique (1er jour ouvré du mois, 8h00 CET)
- **Déclencheur** : Thomas envoie `/continue` en réponse au rapport mensuel
- **Page/écran de destination (succès)** : Telegram — confirmation "Stratégie poursuivie pour le mois de [MOIS]."
- **Page/écran de destination (échec)** : Telegram — erreur si commande envoyée sans rapport mensuel préalable ou contexte invalide

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| mois_concerne | string | Oui | Format "MOIS ANNEE" (mois en cours au moment de la commande) | | Mai 2026 |
| decision | enum | Oui | continue / stop | | continue |
| decided_at | DATETIME | Oui | ISO 8601 UTC — timestamp de réception de la commande | | 2026-05-01T08:05:00Z |
| nb_criteres_ko | integer | Oui | Nombre de critères KO dans le rapport mensuel (0 = chemin OK, ≥ 1 = chemin DECISION REQUIRED) | 0–5 | 0 |
| double_confirmation_requise | boolean | Oui | true si nb_criteres_ko ≥ 2 (friction volontaire user-flows.md Flow 5 F20) | | false |
| confirmation_step | integer | Non | 1 = première confirmation, 2 = deuxième confirmation (si double_confirmation_requise=true) | 1–2 | 1 |

#### 5 états UI (Gate G21)
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Attente commande Thomas après rapport mensuel | Rapport mensuel affiché — Thomas choisit |
| Loading | Écriture SQLite `strategy_decisions` en cours | N/A — immédiat |
| Vide | N/A (la commande est toujours suivie d'une réponse) | N/A |
| Erreur | Commande `/continue` envoyée hors contexte mensuel (aucun rapport reçu ce mois-ci) | "Aucun rapport mensuel reçu ce mois-ci. Le rapport est envoyé le 1er jour ouvré du mois à 8h00." |
| Succès (chemin simple) | nb_criteres_ko = 0 ou 1 → confirmation directe | "Stratégie poursuivie pour le mois de [MOIS]. Signaux GO reprennent normalement." |
| Succès (double confirmation) | nb_criteres_ko ≥ 2, premier /continue reçu → demande deuxième confirmation | "Confirme-tu la reprise avec [N] critères hors seuil ? Renvoie /continue pour confirmer." |
| Succès (double confirmation step 2) | Deuxième /continue reçu → reprise effective | "Stratégie poursuivie pour le mois de [MOIS] — décision assumée avec [N] critères hors seuil. Signaux GO reprennent." |

#### Critères d'acceptance (Given/When/Then)

**Happy path :**
- [ ] GIVEN rapport mensuel envoyé le 1er mai 2026 avec statut CONTINUE (0 critère KO), WHEN Thomas envoie `/continue`, THEN le bot répond "Stratégie poursuivie pour le mois de Mai 2026. Signaux GO reprennent normalement." et enregistre en SQLite : `{ mois: "2026-05", decision: "continue", decided_at: "2026-05-01T...", nb_criteres_ko: 0 }`.
- [ ] GIVEN enregistrement SQLite créé avec succès, WHEN `STRATEGY_ACTIVE` est vérifié, THEN la variable d'environnement (ou flag SQLite) est `true` — les signaux GO du mois reprennent normalement.
- [ ] GIVEN rapport mensuel avec 2 critères KO (chemin DECISION REQUIRED), WHEN Thomas envoie le premier `/continue`, THEN le bot répond "Confirme-tu la reprise avec 2 critères hors seuil ? Renvoie /continue pour confirmer." — pas encore d'enregistrement SQLite définitif.
- [ ] GIVEN double confirmation requise et premier /continue reçu, WHEN Thomas envoie le deuxième `/continue`, THEN reprise effective, SQLite enregistre `{ decision: "continue", nb_criteres_ko: 2, confirmation_step: 2 }`, message de confirmation envoyé.

**Cas d'erreur :**
- [ ] GIVEN `/continue` envoyé sans rapport mensuel reçu ce mois-ci (ex : Thomas envoie /continue un 15 du mois sans raison), WHEN le bot reçoit la commande, THEN "Aucun rapport mensuel reçu ce mois-ci. Le rapport est envoyé le 1er jour ouvré du mois à 8h00."
- [ ] GIVEN `/continue` envoyé depuis un chat_id différent de THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN ignoré silencieusement.

**Cas limites :**
- [ ] GIVEN Thomas envoie `/continue` deux fois le même mois (après confirmation déjà enregistrée), WHEN le bot reçoit la commande, THEN "Stratégie déjà confirmée pour Mai 2026 (décision du [DATE])." — idempotence, pas de doublon SQLite.
- [ ] GIVEN 3 critères KO et Thomas envoie `/continue` une seule fois, WHEN le bot attend le deuxième /continue, THEN le timeout de double confirmation est de 24h. Après 24h sans second /continue, le bot envoie un rappel : "Décision en attente — renvoie /continue pour confirmer ou /stop pour basculer en paper-trading."

**Permissions :**
- [ ] GIVEN commande `/continue` depuis chat_id non autorisé, WHEN le bot reçoit la commande, THEN ignorée silencieusement — aucune trace en SQLite.

**Données existantes :**
- [ ] GIVEN mois précédent avec décision /stop enregistrée (STRATEGY_ACTIVE = false), WHEN Thomas envoie `/continue` au rapport du mois suivant, THEN STRATEGY_ACTIVE repasse à true, mode paper-trading désactivé, signaux GO reprennent avec préfixe normal (sans [PAPER TRADING]).

#### Payload API (pipeline interne)
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Authentification** : Token Bearer (`TELEGRAM_BOT_TOKEN`)
- **Rate limit** : 1 confirmation/mois (idempotence enforced)
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[message confirmation]", "parse_mode": "Markdown" }`
- **Response succès** : HTTP 200 → écriture SQLite `strategy_decisions`
- **Response erreur** : HTTP 4xx/5xx → logguer erreur, réessayer une fois après 5 s

#### Schéma SQLite — table `strategy_decisions`
| Colonne | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Auto-increment |
| month | TEXT | Format "YYYY-MM" (ex : "2026-05") |
| decision | TEXT | "continue" ou "stop" |
| decided_at | DATETIME | ISO 8601 UTC |
| nb_criteres_ko | INTEGER | Nombre de critères KO au moment de la décision |
| confirmation_step | INTEGER | 1 (simple) ou 2 (double confirmation) |

Contrainte : UNIQUE sur `(month, decision)` — une seule décision finale par mois.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| `monthly_continue_invoked` | Thomas envoie `/continue` et confirmation enregistrée | mois_concerne, nb_criteres_ko, confirmation_step, decided_at | retention |

#### Scénarios persona concrets
1. Thomas reçoit le rapport du 1er mai 2026 à 8h00. P&L net : +820 €, drawdown max : 9 %, win rate : 65 % vs 61 % backtest. Statut : CONTINUE. Thomas envoie `/continue` à 8h07. Le bot confirme "Stratégie poursuivie pour le mois de Mai 2026." Thomas reçoit son signal GO normalement à 8h47. Résultat attendu : décision tracée, signaux non interrompus.
2. Thomas reçoit un rapport avec 1 critère KO (win rate live 44 % vs backtest 61 % — écart 17 pts). Statut : DECISION REQUIRED. Thomas lit l'alerte, décide de continuer quand même. Il envoie `/continue`. Bot confirme sans double confirmation (1 seul critère KO). Résultat attendu : 1 critère KO → confirmation simple suffisante.
3. Thomas reçoit un rapport avec 2 critères KO (drawdown 22 % + win rate déviation 16 pts). Statut : DECISION REQUIRED. Il envoie `/continue`. Bot répond "Confirme-tu la reprise avec 2 critères hors seuil ?" Thomas réfléchit 2h, renvoie `/continue`. Bot confirme avec mention "décision assumée avec 2 critères hors seuil". Résultat attendu : friction volontaire bien présente, Thomas a été forcé de confirmer deux fois.
4. Thomas tente `/continue` le 15 mai sans raison (teste la commande). Bot répond "Aucun rapport mensuel reçu ce mois-ci." Résultat attendu : commande hors contexte gérée proprement.
5. Thomas avait envoyé `/stop` en mars. En avril, rapport OK, Thomas envoie `/continue`. STRATEGY_ACTIVE repasse à true. Les signaux du jour n'ont plus le préfixe [PAPER TRADING]. Résultat attendu : retour au live fluide depuis paper-trading.

#### Definition of Done (checklist @fullstack)
- [ ] Commande `/continue` reconnue par le bot handler
- [ ] Table `strategy_decisions` créée avec contrainte UNIQUE sur `(month, decision)`
- [ ] STRATEGY_ACTIVE mis à jour (flag SQLite ou variable d'environnement rechargée)
- [ ] Double confirmation implémentée si nb_criteres_ko ≥ 2 (avec timeout 24h et rappel)
- [ ] Idempotence : second /continue le même mois → réponse "déjà confirmé" sans doublon
- [ ] Test E2E : simuler rapport OK → /continue → vérifier SQLite + signaux reprennent

#### Notes pour @qa
- Tester transition paper-trading → live : /stop en mois M, /continue en mois M+1 → signaux sans [PAPER TRADING].
- Tester double confirmation : 2 critères KO → 1er /continue → attente → 2e /continue → confirmation.
- Tester timeout 24h double confirmation → rappel envoyé.
- Tester idempotence : deux /continue le même mois → deuxième ignoré avec message.

#### Notes pour @fullstack
- `STRATEGY_ACTIVE` : stocker en SQLite dans `strategy_decisions` (colonne `is_active BOOLEAN`), rechargé à chaque exécution du pipeline. Ne pas utiliser variable d'environnement pour ce flag (volatil au redémarrage) — source de vérité = SQLite.
- Cron mensuel (rapport mensuel) : `0 7 1 * *` (UTC, 1er du mois à 7h00 UTC = 8h00 CET hiver). Si le 1er est samedi/dimanche, reporter au lundi (même logique calendrier ouvré US-03).

---

### US-11 : Basculer en paper-trading via `/stop`

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-07, US-08, US-09, US-10
**Priorité RICE** : R=22 I=9 C=9 E=1 → Score=178

#### Job-to-be-done
En tant que Thomas, je veux répondre `/stop` au rapport mensuel afin de suspendre les signaux live et basculer en paper-trading, tout en continuant à recevoir les signaux pour comparaison — sans arrêt définitif du bot.

#### Contexte de navigation
- **Page/écran d'origine** : Telegram — Thomas lit le rapport mensuel (1er jour ouvré du mois, 8h00 CET), contexte chemin (b) DECISION REQUIRED
- **Déclencheur** : Thomas envoie `/stop` en réponse au rapport mensuel
- **Page/écran de destination (succès)** : Telegram — confirmation "Stratégie en pause — bascule en paper-trading." + explication du mode paper-trading
- **Page/écran de destination (échec)** : Telegram — erreur si commande hors contexte

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| mois_concerne | string | Oui | Format "MOIS ANNEE" | | Mai 2026 |
| decision | enum | Oui | "stop" | | stop |
| decided_at | DATETIME | Oui | ISO 8601 UTC | | 2026-05-01T08:12:00Z |
| nb_criteres_ko | integer | Oui | ≥ 1 (le /stop intervient sur chemin DECISION REQUIRED ou volontaire) | 0–5 | 2 |
| paper_trading_activated_at | DATETIME | Oui | Timestamp de bascule en paper-trading (= decided_at) | | 2026-05-01T08:12:00Z |

#### 5 états UI (Gate G21)
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Attente commande Thomas après rapport mensuel | Rapport mensuel affiché |
| Loading | Écriture SQLite + mise à jour STRATEGY_ACTIVE = false | N/A — immédiat |
| Vide | N/A | N/A |
| Erreur | `/stop` envoyé hors contexte mensuel | "Aucun rapport mensuel reçu ce mois-ci. Le rapport est envoyé le 1er jour ouvré du mois à 8h00." |
| Succès | STRATEGY_ACTIVE = false, mode paper-trading actif | "Stratégie en pause — bascule en paper-trading. Les signaux continuent à arriver avec le préfixe [PAPER TRADING]. Pour reprendre le live, envoie /continue au prochain rapport mensuel." |

#### Critères d'acceptance (Given/When/Then)

**Happy path :**
- [ ] GIVEN rapport mensuel envoyé avec statut DECISION REQUIRED, WHEN Thomas envoie `/stop`, THEN le bot répond "Stratégie en pause — bascule en paper-trading. Les signaux continuent à arriver avec le préfixe [PAPER TRADING]. Pour reprendre le live, envoie /continue au prochain rapport mensuel."
- [ ] GIVEN `/stop` confirmé, WHEN SQLite est mis à jour, THEN `strategy_decisions` enregistre `{ mois: "2026-05", decision: "stop", decided_at: "...", paper_trading_activated_at: "..." }` et `STRATEGY_ACTIVE = false`.
- [ ] GIVEN STRATEGY_ACTIVE = false (paper-trading actif), WHEN le pipeline envoie un signal GO le lendemain, THEN le signal est préfixé `[PAPER TRADING]` — toutes les données du signal sont présentes (sens, SL, TP, score, backtest_ref) mais Thomas sait qu'il ne doit pas exécuter.
- [ ] GIVEN mode paper-trading actif, WHEN le pipeline calcule un NO-TRADE, THEN le NO-TRADE est envoyé normalement (sans préfixe — ce n'est pas un signal de trading).
- [ ] GIVEN mode paper-trading actif, WHEN le pipeline calcule une ERREUR DATA ou DEGRADED MODE, THEN ces messages sont envoyés normalement (sans préfixe — ce sont des messages techniques).

**Cas d'erreur :**
- [ ] GIVEN `/stop` envoyé sans rapport mensuel reçu ce mois-ci, WHEN le bot reçoit la commande, THEN "Aucun rapport mensuel reçu ce mois-ci. Le rapport est envoyé le 1er jour ouvré du mois à 8h00."
- [ ] GIVEN `/stop` envoyé depuis un chat_id différent de THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN ignoré silencieusement.

**Cas limites :**
- [ ] GIVEN `/stop` envoyé alors que STRATEGY_ACTIVE est déjà false (paper-trading déjà actif), WHEN le bot reçoit la commande, THEN "Paper-trading déjà actif depuis le [DATE]. Pour reprendre le live, envoie /continue au prochain rapport mensuel." — idempotence, pas de doublon SQLite.
- [ ] GIVEN mode paper-trading actif depuis 2 mois consécutifs, WHEN le 3e rapport mensuel est envoyé, THEN le rapport contient une note : "Paper-trading actif depuis [N] mois — les données de P&L en paper-trading sont enregistrées mais ne reflètent pas le P&L live. Envoie /continue pour reprendre."
- [ ] GIVEN signal GO en paper-trading avec score 7,1 suivi d'un /trade logué (Thomas a quand même tradé par curiosité), WHEN /trade est reçu, THEN le journal accepte la mise à jour — le champ `trade_effectué` peut être true même en paper-trading (Thomas a le contrôle).
- [ ] GIVEN `/stop` envoyé sur chemin (a) CONTINUE (0 critère KO — Thomas veut volontairement s'arrêter), WHEN le bot reçoit la commande, THEN la commande est acceptée (Thomas a toujours le droit de s'arrêter volontairement même si les critères sont OK).

**Permissions :**
- [ ] GIVEN commande `/stop` depuis chat_id non autorisé, WHEN le bot reçoit la commande, THEN ignorée silencieusement — aucune trace en SQLite.

**Données existantes :**
- [ ] GIVEN décision /continue déjà enregistrée pour Mai 2026, WHEN Thomas envoie /stop le même mois, THEN le bot demande confirmation : "Tu as déjà confirmé /continue pour Mai 2026. Confirmes-tu le passage en paper-trading ? Renvoie /stop pour confirmer." — friction volontaire, overwrite possible.

#### Payload API (pipeline interne)
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Authentification** : Token Bearer (`TELEGRAM_BOT_TOKEN`)
- **Rate limit** : N/A (commande manuelle, fréquence très faible)
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[message paper-trading]", "parse_mode": "Markdown" }`
- **Response succès** : HTTP 200 → écriture SQLite `strategy_decisions`, STRATEGY_ACTIVE = false
- **Response erreur** : HTTP 4xx/5xx → logguer erreur, réessayer une fois après 5 s

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| `monthly_stop_invoked` | Thomas envoie `/stop` et bascule paper-trading confirmée | mois_concerne, nb_criteres_ko, decided_at | retention |
| `paper_trading_mode_activated` | STRATEGY_ACTIVE passe à false | mois_concerne, paper_trading_activated_at, nb_criteres_ko | retention |

#### Scénarios persona concrets
1. Thomas reçoit le rapport du 1er mai 2026 avec drawdown 22 % (critère KO). Statut : DECISION REQUIRED. Thomas décide de marquer une pause. Il envoie `/stop`. Bot confirme "Stratégie en pause — bascule en paper-trading. Les signaux continuent à arriver avec le préfixe [PAPER TRADING]." Le lendemain, Thomas reçoit "[PAPER TRADING] ACHAT — DAX Turbo Call..." Il lit, ne trade pas, note mentalement le résultat. Résultat attendu : bascule propre, signaux formatés [PAPER TRADING], Thomas ne ressent pas de pression à exécuter.
2. Thomas est en mode paper-trading depuis mars. Le rapport d'avril montre P&L paper +1 200 € simulé. Il reprend confiance. Il répond /continue au rapport de mai. Le bot confirme, les signaux reprennent sans [PAPER TRADING]. Résultat attendu : retour au live fluide, historique paper-trading conservé en SQLite.
3. Thomas envoie `/stop` un mardi matin sans avoir reçu de rapport mensuel. Bot répond "Aucun rapport mensuel reçu ce mois-ci." Résultat attendu : commande hors contexte refusée proprement.
4. Thomas est en paper-trading depuis 1 mois. Il reçoit le résumé hebdo vendredi. Le résumé indique les trades [PAPER TRADING] de la semaine avec P&L simulé. Drawdown paper = 5 %. Thomas relit ses décisions. Résultat attendu : résumé hebdo cohérent avec mode paper-trading, métriques calculées sur les signaux [PAPER TRADING].
5. Thomas envoie `/stop` alors qu'il avait déjà envoyé /continue ce mois-ci. Bot demande confirmation "Tu as déjà confirmé /continue pour Mai 2026. Confirmes-tu le passage en paper-trading ? Renvoie /stop pour confirmer." Thomas renvoie /stop. Bascule effective. Résultat attendu : friction de confirmation présente avant overwrite d'une décision active.

#### Definition of Done (checklist @fullstack)
- [ ] Commande `/stop` reconnue par le bot handler
- [ ] STRATEGY_ACTIVE = false enregistré en SQLite `strategy_decisions`
- [ ] Pipeline vérifie STRATEGY_ACTIVE avant envoi de chaque signal GO : si false → préfixe [PAPER TRADING] ajouté
- [ ] NO-TRADE, ERREUR DATA, DEGRADED MODE envoyés sans modification de format en paper-trading
- [ ] Idempotence : second /stop alors que paper-trading déjà actif → message "déjà actif depuis [DATE]"
- [ ] Résumé hebdo (US-09) adapté au mode paper-trading : mention "paper-trading actif" dans le message
- [ ] Test E2E : /stop → signal GO du lendemain → vérifier préfixe [PAPER TRADING] présent

#### Notes pour @qa
- Tester transition live → paper-trading → live : /stop mois M → signals [PAPER TRADING] → /continue mois M+1 → signals normaux.
- Tester que ERREUR DATA et DEGRADED MODE n'ont PAS le préfixe [PAPER TRADING] en mode pause.
- Tester overwrite /continue → /stop le même mois : friction de confirmation avant bascule.
- Tester `/stop` depuis chat_id non autorisé → silence.

#### Notes pour @ux
- Le message de confirmation /stop doit expliquer explicitement que ce n'est PAS un arrêt définitif (F21 user-flows.md). Formulation : "Les signaux continuent à arriver avec le préfixe [PAPER TRADING]. Pour reprendre le live, envoie /continue au prochain rapport mensuel."
- Le préfixe [PAPER TRADING] en tête de signal doit être visible sur l'écran de verrouillage iOS/Android sans déverrouiller (première ligne du message).

#### Notes pour @fullstack
- `STRATEGY_ACTIVE` : même source de vérité SQLite que US-10 (table `strategy_decisions`, colonne `is_active`). Rechargé à chaque exécution pipeline.
- Logique préfixe : `if not STRATEGY_ACTIVE: message = "[PAPER TRADING]\n" + message_standard` — aucune autre modification du contenu du signal.
- Résumé hebdo US-09 : si paper-trading actif, ajouter en entête du résumé "Mode paper-trading actif depuis [DATE]."

---

### US-12 : Mettre le bot en pause via `/pause [YYYY-MM-DD YYYY-MM-DD]`

**Persona** : Thomas
**Epic** : Journal et audit
**Dépendances** : US-03 (calendrier jours ouvrés), US-07 (cron pipeline)
**Priorité RICE** : R=22 I=8 C=9 E=1 → Score=158

#### Job-to-be-done
En tant que Thomas, je veux envoyer une commande `/pause 2026-07-15 2026-07-29` afin de suspendre tous les signaux pendant mes vacances et ne pas dégrader la saillance du bot à mon retour (bruit de 10+ signaux ignorés).

#### Contexte de navigation
- **Page/écran d'origine** : Telegram — Thomas envoie la commande depuis la conversation TradingApp, n'importe quel moment
- **Déclencheur** : Thomas envoie `/pause YYYY-MM-DD YYYY-MM-DD` (2 dates ISO 8601, intervalle inclusif)
- **Page/écran de destination (succès)** : Telegram — confirmation de la pause avec les dates reformatées en JJ/MM
- **Page/écran de destination (échec)** : Telegram — message d'erreur avec format requis

#### Données et champs
| Champ | Type | Obligatoire | Validation | Limites | Exemple |
|---|---|---|---|---|---|
| start_date | date | Oui | Format ISO 8601 YYYY-MM-DD, ≤ end_date, ≥ aujourd'hui | date valide | 2026-07-15 |
| end_date | date | Oui | Format ISO 8601 YYYY-MM-DD, ≥ start_date, ≤ start_date + 30 jours | date valide | 2026-07-29 |
| requested_at | datetime | Oui | ISO 8601 UTC, auto-généré au moment de la commande | | 2026-07-10T18:32:00Z |
| status | enum | Oui | "active", "expired", "cancelled" | | active |

#### 5 états UI (Gate G21)
| État | Comportement | Message/Affichage |
|---|---|---|
| Défaut | Aucune pause active — bot envoie les signaux normalement | N/A |
| Loading | Écriture SQLite table `strategy_pauses` | N/A — immédiat |
| Vide | N/A | N/A |
| Erreur | Format invalide, dates incohérentes, ou plage > 30 jours | Message d'erreur explicite (voir critères d'erreur) |
| Succès | Pause enregistrée en SQLite, pipeline la vérifiera chaque matin | "Bot en pause du {start_date_FR} au {end_date_FR}. Aucun signal envoyé pendant cette période." |

#### Critères d'acceptance (Given/When/Then)

**Happy path :**
- [ ] GIVEN Thomas envoie `/pause 2026-07-15 2026-07-29` depuis THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN le bot répond "Bot en pause du 15/07 au 29/07. Aucun signal envoyé pendant cette période." et la table `strategy_pauses` enregistre `{ start_date: "2026-07-15", end_date: "2026-07-29", requested_at: "...", status: "active" }`.
- [ ] GIVEN une pause active en SQLite (`status = "active"`, date du jour ≥ start_date ET ≤ end_date), WHEN le cron 8h40 s'exécute, THEN le pipeline ne calcule aucun signal et n'envoie aucun message Telegram pour cette journée.
- [ ] GIVEN date du jour = end_date − 1 jour (veille de fin de pause), WHEN le cron 8h40 vérifie la table `strategy_pauses`, THEN le bot envoie à Thomas le message "Bot reprend demain 8h45 CET." (rappel de fin de pause — envoyé une seule fois).
- [ ] GIVEN date du jour > end_date, WHEN le cron 8h40 vérifie la table `strategy_pauses`, THEN la pause est marquée `status = "expired"` et le pipeline reprend normalement.

**Cas d'erreur :**
- [ ] GIVEN Thomas envoie `/pause` sans arguments, WHEN le bot reçoit la commande, THEN "Format requis : /pause YYYY-MM-DD YYYY-MM-DD (ex : /pause 2026-07-15 2026-07-29)".
- [ ] GIVEN Thomas envoie `/pause 2026-07-29 2026-07-15` (start > end), WHEN le bot reçoit la commande, THEN "Dates invalides : la date de début doit être antérieure ou égale à la date de fin."
- [ ] GIVEN Thomas envoie `/pause 2026-07-01 2026-08-15` (plage > 30 jours), WHEN le bot reçoit la commande, THEN "Pause limitée à 30 jours maximum."
- [ ] GIVEN Thomas envoie `/pause abc 2026-07-29` (format de date invalide), WHEN le bot reçoit la commande, THEN "Format requis : /pause YYYY-MM-DD YYYY-MM-DD (ex : /pause 2026-07-15 2026-07-29)".

**Cas limites :**
- [ ] GIVEN une pause active déjà en SQLite, WHEN Thomas envoie une nouvelle commande `/pause` avec de nouvelles dates, THEN le bot met à jour la pause existante (status = "active", nouvelles dates) et répond "Pause mise à jour : bot en pause du {nouvelle_start_FR} au {nouvelle_end_FR}."
- [ ] GIVEN Thomas envoie `/cancel-pause` pendant une pause active, WHEN le bot reçoit la commande, THEN la pause passe à `status = "cancelled"`, le bot répond "Pause annulée. Le bot reprend normalement dès demain 8h45."
- [ ] GIVEN Thomas envoie `/cancel-pause` sans pause active, WHEN le bot reçoit la commande, THEN "Aucune pause active en cours."
- [ ] GIVEN date start_date = aujourd'hui (pause immédiate), WHEN le pipeline cron 8h40 s'exécute le même matin, THEN si la commande /pause a été enregistrée avant 8h40, le pipeline respecte la pause ; si enregistrée après 8h40, le signal du jour est déjà envoyé — pas de rétroactivité, la pause s'applique à partir du lendemain.

**Permissions :**
- [ ] GIVEN commande `/pause` depuis chat_id différent de THOMAS_CHAT_ID, WHEN le bot reçoit la commande, THEN ignorée silencieusement.

**Données existantes :**
- [ ] GIVEN une pause `status = "expired"` en SQLite, WHEN Thomas envoie une nouvelle commande `/pause`, THEN un nouvel enregistrement est créé (pas d'overwrite de l'historique).

#### Payload API (pipeline interne)
- **Endpoint** : Telegram Bot API `POST /bot{TOKEN}/sendMessage`
- **Authentification** : Token Bearer (`TELEGRAM_BOT_TOKEN`)
- **Rate limit** : N/A (commande manuelle)
- **Request body** : `{ "chat_id": "{THOMAS_CHAT_ID}", "text": "[message confirmation pause]", "parse_mode": "Markdown" }`
- **Response succès** : HTTP 200 → écriture SQLite `strategy_pauses`
- **Response erreur** : HTTP 4xx/5xx → logguer erreur, réessayer une fois après 5 s

#### Schéma SQLite — table `strategy_pauses`
| Colonne | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Auto-increment |
| start_date | TEXT | Format "YYYY-MM-DD" |
| end_date | TEXT | Format "YYYY-MM-DD" |
| requested_at | DATETIME | ISO 8601 UTC |
| status | TEXT | "active", "expired", "cancelled" |

Logique pipeline : `SELECT * FROM strategy_pauses WHERE status = "active" AND date("now") BETWEEN start_date AND end_date` — si résultat non vide, pipeline s'arrête avant tout calcul de signal.

#### Events analytics
| Event | Trigger | Propriétés | Funnel |
|---|---|---|---|
| `pause_command_invoked` | Thomas envoie `/pause` et confirmation enregistrée | start_date, end_date, duration_days, requested_at | retention |
| `pause_active` | Cron 8h40 détecte une pause active et n'envoie pas de signal | start_date, end_date, current_date | retention |
| `pause_ended` | Cron 8h40 détecte fin de pause (status → "expired") | end_date, total_days_paused | retention |

#### Scénarios persona concrets
1. Thomas part en vacances le 15 juillet. Le 10 juillet au soir, il envoie `/pause 2026-07-15 2026-07-29` depuis son canapé. Bot répond "Bot en pause du 15/07 au 29/07. Aucun signal envoyé pendant cette période." Thomas part l'esprit tranquille. Résultat attendu : 0 signal envoyé du 15 au 29 juillet.
2. Thomas est en pause du 15 au 29 juillet. Le 28 juillet (veille de fin), le cron 8h40 envoie "Bot reprend demain 8h45 CET." Thomas, qui revient de vacances, sait qu'il doit se repositionner mentalement. Résultat attendu : rappel reçu une seule fois la veille.
3. Thomas avait prévu une pause du 15 au 22 juillet, mais ses vacances sont prolongées. Le 20 juillet, il renvoie `/pause 2026-07-15 2026-07-29`. Bot répond "Pause mise à jour : bot en pause du 15/07 au 29/07." Résultat attendu : mise à jour propre sans doublon SQLite.
4. Thomas est en pause, mais un flash macro important tombe et il veut reprendre. Il envoie `/cancel-pause`. Bot répond "Pause annulée. Le bot reprend normalement dès demain 8h45." Résultat attendu : reprise le lendemain, pas rétroactive.
5. Thomas envoie `/pause` sans dates (il teste). Bot répond "Format requis : /pause YYYY-MM-DD YYYY-MM-DD (ex : /pause 2026-07-15 2026-07-29)". Résultat attendu : erreur explicite, pas de crash.

#### Definition of Done (checklist @fullstack)
- [ ] Commandes `/pause`, `/cancel-pause` reconnues par le bot handler
- [ ] Table `strategy_pauses` créée avec colonnes `id, start_date, end_date, requested_at, status`
- [ ] Logique pipeline : vérification table `strategy_pauses` avant tout calcul de signal à 8h40
- [ ] Rappel veille de fin de pause implémenté (envoi unique J-1)
- [ ] Expiration automatique au retour : status → "expired" le jour J > end_date
- [ ] Idempotence : `/cancel-pause` sans pause active → message "Aucune pause active"
- [ ] Test E2E : /pause → vérifier 0 signal pendant la fenêtre → expiration → signal reprend

#### Notes pour @qa
- Tester que le signal du lendemain de fin de pause reprend normalement (status "expired" → pipeline actif).
- Tester le rappel veille de fin : envoyé une seule fois même si le cron tourne plusieurs fois (idempotence du rappel).
- Tester `/pause` avec start_date = hier (date passée) → erreur ou acceptation ? Décision : refuser si start_date < aujourd'hui (pas de rétroactivité).
- Tester conflit pause + signal d'arrêt (drawdown > 20 %) : les deux peuvent coexister — la pause prime côté signal, l'alerte drawdown reste loguée.

#### Notes pour @ux
- Le message de confirmation doit reformater les dates ISO 8601 en JJ/MM lisible (15/07 et non 2026-07-15).
- Le rappel de veille de fin doit être sobre — pas alarmiste. Formulation : "Bot reprend demain 8h45 CET." (pas de "Attention !" ou emoji).

#### Notes pour @fullstack
- Vérification de pause : première instruction du pipeline avant tout appel Twelve Data ou Claude. Si pause active → log SQLite `statut = "pause"` pour la journée + arrêt. Pas de message Telegram (silence total pendant la pause).
- Le rappel veille est envoyé par le cron 8h40 J-1 uniquement si `reminder_sent` est null dans `strategy_pauses` — ajouter colonne `reminder_sent DATETIME NULL` pour idempotence.
- `/cancel-pause` : UPDATE `strategy_pauses SET status = "cancelled" WHERE status = "active"` — si 0 row updated, répondre "Aucune pause active en cours."

---

## 2. Format Message Telegram — Templates V1

Contrainte brand-platform : **6 lignes max signal + 1 ligne confiance**. Zéro mot de marketing. Conditionnel de l'incertitude obligatoire sur le TP.

### Template ACHAT

```
ACHAT — {sous_jacent}
Entrée : {entree} € | SL : {sl} € | Cible potentielle : {tp} €
{raison_ligne_1}
{raison_ligne_2 — si présente}
{raison_ligne_3 — si présente}
Risque max : {risque_max_eur} € sur {capital_engage} € engagés
Réf. backtest {backtest_ref} — win rate {win_rate_backtest} % / {nb_trades_backtest} trades / drawdown max {drawdown_max_backtest} %
Score : {score_confiance}/10 | Fenêtre : avant {cutoff_heure} CET
```

**Règles template ACHAT :**
- "Cible potentielle" et non "Cible" (conditionnel obligatoire)
- Risque max calculé et affiché — jamais absent
- Backtest_ref présent — toujours
- Score sur 10 en dernière ligne
- Pas de point d'exclamation, pas de mise en gras des mots "signal" ou "fort"
- Maximum 8 lignes totales (6 signal + 1 confiance + 1 backtest)

**Exemple concret (scénario Thomas, lundi 4 mai 2026) :**
```
ACHAT — DAX Turbo Call
Entrée : 3,42 € | SL : 3,21 € | Cible potentielle : 3,85 €
Gap haussier +0,8 % sur clôture US + ORB haussier 5 premières min Xetra
Score 7,1/10 confirmé par momentum > seuil backtest
Réf. backtest #B-031 — win rate 61 % / 87 trades / drawdown max −18 %
Risque max : 126 € sur 600 € engagés (levier ~6)
Score : 7,1/10 | Fenêtre : avant 8h55 CET
```

---

### Template VENTE

```
VENTE — {sous_jacent}
Entrée : {entree} € | SL : {sl} € | Cible potentielle : {tp} €
{raison_ligne_1}
{raison_ligne_2 — si présente}
{raison_ligne_3 — si présente}
Risque max : {risque_max_eur} € sur {capital_engage} € engagés
Réf. backtest {backtest_ref} — win rate {win_rate_backtest} % / {nb_trades_backtest} trades / drawdown max {drawdown_max_backtest} %
Score : {score_confiance}/10 | Fenêtre : avant {cutoff_heure} CET
```

**Règles spécifiques VENTE :**
- SL > entrée (turbo put : SL au-dessus du niveau d'entrée)
- TP < entrée (cible en dessous — vente à découvert via turbo put)
- Même structure que ACHAT — cohérence de format

---

### Template NO-TRADE

```
Pas de trade aujourd'hui.
Score max relevé : {score_max_releve}/10 — en dessous du seuil {seuil_confiance}.
Prochaine fenêtre : {prochaine_fenetre}.
```

**Règles template NO-TRADE :**
- Exactement 3 lignes
- Pas de "désolé", pas de "peut-être demain", pas de commentaire éditorial
- Prochaine fenêtre calculée dynamiquement (lendemain si lundi-jeudi ; lundi si vendredi)

---

### Template ERREUR DATA (Twelve Data fail)

```
Données de marché indisponibles ce matin ({heure_erreur} CET).
Motif : {motif_erreur}.
Aucun signal émis aujourd'hui. Prochaine tentative demain 8h45.
```

---

### Template DEGRADED MODE (Claude timeout/fail)

```
Scoring IA indisponible ce matin ({heure_erreur} CET).
Données de marché reçues — justification structurée non générée.
Aucun signal émis aujourd'hui (règle : pas de signal sans justification).
```

**Note brand-platform :** le DEGRADED MODE confirme explicitement que le principe "pas de signal forcé" est respecté — cohérence avec la promesse de marque (section 3 brand-platform.md).

---

## 3. Liste des sous-jacents V1

Base issue de l'héritage Finance (project-context.md) et de l'infra-audit (H3).

**Hypothèse H3** : Bourse Direct propose des turbos sur tous ces sous-jacents. À VÉRIFIER PAR THOMAS avant la R&D edge.

| # | Sous-jacent | Ticker Twelve Data | Catégorie | Statut Bourse Direct |
|---|---|---|---|---|
| 1 | CAC40 | ^FCHI | Indice EU | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 2 | DAX | ^GDAXI | Indice EU | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 3 | EuroStoxx50 | ^STOXX50E | Indice EU | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 4 | LVMH | MC.PA | Blue chip FR | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 5 | TotalEnergies | TTE.PA | Blue chip FR | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 6 | Sanofi | SAN.PA | Blue chip FR | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 7 | Air Liquide | AI.PA | Blue chip FR | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 8 | Schneider Electric | SU.PA | Blue chip FR | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 9 | EUR/USD | EUR/USD | FX | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 10 | GBP/USD | GBP/USD | FX | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 11 | Or (XAU/USD) | XAU/USD | Commodité | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 12 | Brent crude | BRN | Commodité | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |
| 13 | Gaz naturel (TTF ou Henry Hub) | TTF ou NG | Commodité | [À VÉRIFIER PAR PERSONA — catalogue Bourse Direct] |

**Action requise par Thomas avant R&D edge :**
> Ouvrir l'app Bourse Direct > Recherche turbos > Vérifier que chaque sous-jacent a au minimum 3 turbos call et 3 turbos put avec spread < 0,05 € et volume > 0 sur les 3 derniers mois. Rayer de la liste ceux qui ne satisfont pas ce critère.

**Priorité R&D edge :** CAC40 et DAX en priorité (marchés EU liquides avec forte activité 8h45-9h15), puis EuroStoxx50, puis blue chips FR, puis FX et commodities.

---

## 4. Règles métier

### R1 — Un seul signal par jour ouvré

Le pipeline ne peut émettre qu'un seul message Telegram par jour calendaire, quelle que soit la nature (ACHAT, VENTE, NO-TRADE, ERREUR DATA, DEGRADED MODE). Implémentation : contrainte UNIQUE sur la colonne `date` dans la table `signals`. Si un enregistrement existe déjà pour `date=today`, le pipeline s'arrête.

### R2 — NO-TRADE autorisé et documenté comme décision valide

Un NO-TRADE n'est pas un échec. Il est enregistré en SQLite avec statut="no_trade" et le score_max_releve. Il compte dans les statistiques mensuelles comme "jour sans trade — décision correcte si score < seuil". Le journal ne doit jamais afficher le NO-TRADE comme une anomalie.

### R3 — Justification obligatoire : backtest_ref dans chaque signal

Tout signal ACHAT ou VENTE doit contenir un backtest_ref valide (existant dans la table `backtests` SQLite). Un signal sans backtest_ref est bloqué avant envoi. Cette règle est non contournable — cohérence avec le pilier "Backtesté" brand-platform.md.

### R4 — Cutoff 8h55 CET strict

Tout signal dont le timestamp_calcul est ≥ 8h55:00 CET est invalidé avant envoi Telegram. Le silence Telegram (pas de message) est préféré à un signal hors fenêtre. Aucun message "signal tardif" n'est envoyé à Thomas — la fenêtre est fermée, point.

### R5 — Calendrier jours ouvrés EU (fériés FR)

Le cron ne s'exécute pas les samedis, dimanches, et jours fériés français. Source de référence : bibliothèque calendrier FR (workalendar ou date.nager.at). Mise à jour annuelle au démarrage du service.

### R6 — Seuil de confiance configurable (paramètre — pas valeur fixe)

Le seuil de confiance est stocké dans une variable d'environnement `CONFIDENCE_THRESHOLD` (float, ex : 6.5). Il n'est jamais hardcodé dans le code source. [HYPOTHÈSE : valeur initiale 6,5/10 — à calibrer lors de la R&D edge avant toute mise en production. Cette valeur est une hypothèse de départ, non une décision définitive.]

### R7 — Signaux d'arrêt automatiques (basés sur personas.md)

Le pipeline vérifie ces 5 conditions à chaque exécution et enregistre les flags en SQLite :

| Condition (personas.md) | Flag SQLite | Comportement pipeline |
|---|---|---|
| Drawdown mensuel > 20 % capital dédié | `drawdown_alerte=true` | Signal bloqué — message DÉGRADÉ envoyé à Thomas : "Drawdown mensuel > 20 %. Bot en pause — audit du journal requis." |
| 3 semaines consécutives NO-TRADE | `revue_seuil_requise=true` | Signal envoyé normalement + note en bas de message : "Seuil à revoir — 15+ NO-TRADE consécutifs." |
| Win rate live < win rate backtest − 15 pts sur 3 mois | `win_rate_alerte=true` | Signal bloqué — message envoyé : "Win rate live dévie de > 15 pts du backtest sur 3 mois. Revue edge requise." |
| Score confiance moyen en live > score moyen backtest (euphorie) | `euphorie_alerte=true` | Signal envoyé + note : "Alerte euphorie — scores récents > backtest. Walk-forward OOS recommandé." |
| Position ouverte non clôturée en fin de journée | `incident_overnight=true` | Log SQLite uniquement — pas de signal bloqué (Thomas gère ses ordres manuellement) |

**Note importante :** le calcul des signaux d'arrêt nécessite que Thomas alimente le journal (US-08). Sans données réelles de P&L et win rate, ces contrôles ne peuvent pas s'exécuter. Le pipeline gère le cas "données insuffisantes" (< 10 trades loggués) en n'activant pas les seuils d'arrêt.

---

## 5. Hors scope V1

Les éléments suivants sont **explicitement exclus** du périmètre V1. Toute demande d'implémentation de ces fonctionnalités doit être rejetée jusqu'à V2 ou V1.1.

| Feature exclue | Justification d'exclusion | Scope cible |
|---|---|---|
| Exécution automatique des ordres (API broker) | Sécurité : Thomas préfère l'exécution manuelle pour contrôle et légalité. Aucune API broker Bourse Direct disponible publiquement. | Jamais (décision structurante project-context.md) |
| Multi-signaux par jour | Décision structurante #1 project-context.md. Un signal = lisibilité max. | Jamais |
| Dashboard web ou interface React | Friction éliminée volontairement. Telegram push = canal irremplaçable pour Thomas. Le projet Finance a montré que le dashboard n'est pas utilisé. | Jamais en V1 |
| Monitoring positions intraday | Thomas pose SL/TP à l'entrée et ne revient qu'à 10h minimum. Monitoring = compléxité inutile. | V2 si besoin prouvé |
| Alertes mid-day ("lunch fade" ou autre) | Hors fenêtre Thomas (9h05 = indisponible). À valider par R&D si edge "lunch fade" trouvé. | V2 conditionnel |
| Redistribution des signaux à des tiers | Risque juridique R1 (legal-audit) : art. L.573-1 CMF, jusqu'à 3 ans prison + 375 k€ amende. | Jamais sans statut CIF + accord Twelve Data |
| Notifications de performance mid-trade | Thomas ne gère pas la position en intraday. | V1.1 uniquement si Thomas le demande |
| Export PDF / rapport formaté | Hors scope V1. Journal SQLite suffit pour l'audit 30 min/mois (JTBD 4). | V2 |
| Gestion multi-comptes ou multi-personas | Outil 100 % personnel. | Jamais |
| Interface de configuration des paramètres | Variables d'environnement suffisent pour le solo-utilisateur technique. | V2 si nécessaire |

---

## 6. Roadmap

La roadmap est orientée par dépendances, pas par timeline. Chaque jalon conditionne le suivant.

### Jalon 0 — Prérequis non négociables (avant tout code)
- [ ] Thomas vérifie le catalogue Bourse Direct (H3) — liste sous-jacents validée
- [ ] Thomas vérifie le plan Twelve Data (H2) — intraday 1m confirmé ou plan upgradé
- [ ] Thomas décide H1 — Replit Core vs Hetzner CX11

### V1 — Bot + Backtester + Journal SQLite
**Condition d'entrée** : Jalon 0 complet + edge identifié en R&D avec walk-forward OOS PASS (@testeur-backtest-edge).

Livrables V1 :
- Pipeline cron → Twelve Data → Backtester → Claude → Telegram
- US-01 à US-08 implémentées
- Journal SQLite avec schéma complet
- Prompt library Claude (@ia) validée par @testeur-persona-thomas
- 4-8 semaines paper-trading avec signaux Telegram réels (exécution simulée)

**Critères go/no-go V1 → live :**
- Edge robuste sur 5 ans + walk-forward OOS (win rate OOS ≥ win rate IS − 10 pts)
- Paper-trading 4-8 semaines concluant (P&L net simulé positif sur ≥ 3 semaines consécutives, drawdown max < 20 %)
- 0 bug critique sur les 5 états du signal (US-04, US-05, US-06 testés en conditions réelles)

### V1.1 — Boucle de rétroaction (Thomas alimente le journal)
**Condition d'entrée** : V1 en live depuis ≥ 4 semaines, ≥ 20 trades loggués par Thomas.

Livrables V1.1 :
- US-08 pleinement opérationnelle (commande /trade)
- Pipeline lisant le journal pour calculer win rate live vs backtest
- Signaux d'arrêt automatiques R7 activés (nécessitent données réelles)
- Ajustement automatique du CONFIDENCE_THRESHOLD si trop de NO-TRADE consécutifs (alerte à Thomas, pas d'auto-modification sans validation)
- Rapport hebdomadaire automatique : P&L semaine, drawdown courant, win rate live, comparaison backtest

### V2 — Évolutions conditionnelles (R&D requise avant décision)
**Condition d'entrée** : V1.1 stable + ≥ 3 mois live P&L net positif.

Pistes V2 (à valider par R&D — pas de promesse) :
- Notification mi-journée si edge "lunch fade" trouvé et backtesté sur 5 ans (Xetra/CAC40 12h45-13h15)
- Export rapport mensuel auto (PDF ou message Telegram structuré)
- Ajout de sous-jacents si H3 élargi (validation Bourse Direct requise)

---

## 7. Agents spécialisés recommandés

| Agent proposé | Type | Rôle | Justification | Priorité |
|---|---|---|---|---|
| @testeur-persona-thomas | Testeur persona | Évaluer chaque format de message Telegram (ACHAT, VENTE, NO-TRADE, ERREUR DATA, DEGRADED MODE) du point de vue "est-ce que j'appuierais sur le bouton avec ça ?" — verdict GO/AJUSTER/NO-GO | Thomas est l'unique utilisateur. Le risque de non-usage (comme avec Finance) est critique. Chaque format de message doit passer ce filtre avant code. | Haute |
| @testeur-backtest-edge | Validateur quantitatif | Challenger les hypothèses d'edge avant V1 : walk-forward split IS/OOS, robustesse par année, detection sur-fit. Aucun edge ne passe en production sans ce filtre. | Risque anti-pattern n°2 project-context.md : edge "trop subtil" ou sur-fitté. Coût d'un edge invalide en live : 2-3 k€/mois. | Haute |
| @ia | Expert LLM | Produire la prompt library Claude (scoring + justification) AVANT que @fullstack code l'intégration. Le prompt est le coeur du système — une prompt non validée = signal non fiable. | L'intégration Claude (US-01, US-05) dépend d'un JSON schema strict et d'un prompt robuste. @ia doit livrer `docs/ia/prompt-library.md` avant le sprint @fullstack. | Haute |

**Agent non recommandé :**
- @testeur-client-du-persona : N/A — outil 100 % personnel, Thomas n'a pas de clients. Confirmé par @creative-strategy et cohérent avec project-context.md.

### Specs complémentaires pour @agent-factory

**@testeur-persona-thomas** (confirmé depuis brand-platform.md)
- Inputs : templates Telegram sections 2, user stories US-01 à US-08, scénario daté personas.md
- Outputs : verdict GO/AJUSTER/NO-GO par template + liste frictions + reformulation suggérée
- Critère de succès : Thomas dirait "avec ce message, je sais si je trade ou non en moins de 30 secondes"

**@testeur-backtest-edge** (confirmé depuis brand-platform.md)
- Inputs : résultats backtest R&D (win rate, drawdown max, Sharpe, nb trades, période testée, IS/OOS split)
- Outputs : diagnostic overfitting, robustesse par année, recommandation GO/RETRAVAILLER/NO-GO
- Critère de succès : aucun edge ne passe en V1 sans avoir passé le filtre walk-forward OOS

**@ia** (ajouté par @product-manager)
- Inputs : US-01 (champs JSON attendus), US-05 (contraintes timeout/fallback), brand-platform.md (ton Voice & Tone), personas.md (critères pull-the-trigger de Thomas)
- Outputs : `docs/ia/prompt-library.md` contenant le prompt Claude de scoring + le JSON schema de réponse attendu + les tests de validation (inputs/outputs exemples)
- Critère de succès : le prompt retourne un JSON valide avec tous les champs US-01 dans ≥ 95 % des tests sur données Twelve Data simulées, sans champ manquant ni mot proscrit (brand-platform.md liste)

---

## Auto-évaluation — Gates BLOQUANT

| Gate | Critère | Verdict | Évidence |
|---|---|---|---|
| G1 | Persona Thomas identifié dans toutes les US | PASS | "Thomas" nommé dans chaque US-01 à US-11, jamais "l'utilisateur" |
| G3 | Zéro donnée inventée non marquée | PASS | Seuil confiance marqué [HYPOTHÈSE], H3 marqué [À VÉRIFIER PAR PERSONA] ; US-09/10/11 sans hypothèse non marquée |
| G5 | Persona correspond exactement à project-context.md | PASS | Thomas, capital 20-30 k€, Bourse Direct, turbos 5-20, 8h45-8h55 CET |
| G6 | KPI North Star cité avec PFU 31,4 % | PASS | Résumé exécutif + US-01 JTBD + US-08 calcul pl_net + US-09 pl_net_semaine (règle fiscale PFU gains uniquement) |
| G7 | Cohérence brand-platform + personas + user-flows.md + legal-audit | PASS | US-09 conforme Flow 4 user-flows.md (cron vendredi 18h, commande /journal-week, statut OK/ALERTE/ARRÊT) ; US-10 conforme Flow 5 (chemin a /continue, double confirmation si ≥ 2 KO, F20 mitigation) ; US-11 conforme Flow 5 (chemin b /stop = paper-trading pas arrêt définitif, F21 mitigation) ; PFU 31,4 % US-09 cohérent legal-audit L001 ; signaux d'arrêt R7 functional-specs §4 intégrés dans US-09 statut_semaine |
| G12 | Chaque user story implémentable sans question @fullstack | PASS | US-09 : schéma `journal_weeks`, cron CRON_WEEKLY, calcul PFU, idempotence `journal_week_sent_at` ; US-10 : schéma `strategy_decisions`, double confirmation, timeout 24h ; US-11 : STRATEGY_ACTIVE SQLite, logique préfixe [PAPER TRADING], résumé hebdo adapté |
| G15 | Zéro placeholder résiduel | PASS | Marqueurs [À VÉRIFIER PAR PERSONA] et [HYPOTHÈSE] sont des annotations volontaires. US-09/10/11 : aucun placeholder non justifié |
| G17 | Livrable non copiable pour un concurrent | PASS | Référence explicite à Thomas, Bourse Direct, fenêtre 8h45-8h55, calendrier fériés FR, Twelve Data tickers EU, commandes /journal-week /continue /stop spécifiques au workflow Thomas |

---
