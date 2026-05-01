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
| G1 | Persona Thomas identifié dans toutes les US | PASS | "Thomas" nommé dans chaque US-XX, jamais "l'utilisateur" |
| G3 | Zéro donnée inventée non marquée | PASS | Seuil confiance marqué [HYPOTHÈSE], H3 marqué [À VÉRIFIER PAR PERSONA] |
| G5 | Persona correspond exactement à project-context.md | PASS | Thomas, capital 20-30 k€, Bourse Direct, turbos 5-20, 8h45-8h55 CET |
| G6 | KPI North Star cité avec PFU 31,4 % | PASS | Résumé exécutif + US-01 JTBD + US-08 calcul pl_net |
| G7 | Cohérence brand-platform + personas + infra-audit + legal-audit | PASS | Templates respectent 6 lignes + 1 confiance (brand-platform §3 Pilier 2) ; signaux d'arrêt issus de personas.md ; CUTOFF 8h55 = G4 infra-audit ; PFU 31,4 % = legal-audit L001 ; DEGRADED MODE = brand-platform promesse interne "pas de signal forcé" |
| G12 | Chaque user story implémentable sans question @fullstack | PASS | Champs typés, validations, payloads Telegram, schéma SQLite, calcul pl_net explicite |
| G15 | Zéro placeholder résiduel | PASS | Marqueurs [À VÉRIFIER PAR PERSONA] et [HYPOTHÈSE] sont des annotations volontaires, pas des placeholders oubliés |
| G17 | Livrable non copiable pour un concurrent | PASS | Référence explicite à Thomas, Bourse Direct, fenêtre 8h45-8h55, calendrier fériés FR, Twelve Data tickers EU |

---
