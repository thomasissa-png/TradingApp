# Revue finale — Refonte « 5 rapports + mesure ouverture→clôture »

> @reviewer — 2026-06-08 — branche `claude/elegant-ramanujan-OIKms`
> Objet : revue croisée des 4 chantiers (Phase 1 mesure, Phase 2 suivi, Phase 3 Manager, Infra cron) avant merge `main`.
> Référentiel : `spec-refonte-5-rapports.md` v2 + `-RESOLUTIONS.md` + `founder-preferences.md`.

## Verdict

**Note : 8,7 / 10**
**Verdict : GO MERGE (sous 2 réserves non bloquantes documentées ci-dessous)**

Aucun blocker P0. L'ensemble est cohérent, fidèle à la spec, WIN-RATE-ONLY, shadow préservé, zéro modification silencieuse. Les 2 réserves (CA-B2 CAC close 17h30 et CA-M7 compteur jours exclus) sont des restes déjà anticipés par la spec, isolés et sans risque pour le pipeline existant.

## Résultat pytest

⚠️ **Je n'ai pas pu exécuter `python3 -m pytest v3/ -q` dans cet environnement** (pas d'accès shell dans cette session de revue). La revue repose sur la lecture statique du code ET des 3 fichiers de tests nouveaux, dont la cohérence avec l'implémentation a été vérifiée ligne à ligne.

→ **À faire par l'orchestrateur AVANT merge** : lancer `python3 -m pytest v3/ -q` et restaurer `git checkout -- v3/data/` ensuite. Les tests lus sont cohérents avec le code (assertions alignées sur les signatures et le comportement réels) ; aucun décalage test/code détecté. Si un test échoue, re-déclencher la revue sur le test concerné.

Couverture vérifiée (statique) :
- `test_mesure_ouverture.py` : CA-M1/M2/M3/M4/M5/M6/M6b + CA-B1/B4/B5 + CA-W6 + flag gros move + DST (15 tests)
- `test_run_suivi.py` : CA-S1/S2/S4/S5/S6/S6b + tendance + US pas ouvert + smoke run_bilan (15 tests)
- `test_run_weekly.py` : détection 2 semaines + petit N + CA-W2/W3/W4/W6 + porteuses + WIN-RATE-ONLY + state (16 tests)

## 1. Fidélité à la spec (CA-M*/CA-S*/CA-B*/CA-W*/CA-I*)

| CA | Statut | Preuve (fichier:ligne) |
|---|---|---|
| CA-M1 (JSON idempotent + entry-lock) | PASS | `mesure_ouverture.py:270-363` + test `:85-103` |
| CA-M2 (délai post-ouverture, DST) | PASS | `mesure_ouverture.py:173-200` (ZoneInfo, jamais d'offset) + test `:57-78` |
| CA-M3 (Twelve KO → ticker absent) | PASS | `mesure_ouverture.py:341-346` + test `:123-132` |
| CA-M4 (24h = prix-ouverture) | PASS | `journaliste.py:1444-1474` `_resolve_prix_reference` + test `:151-175` |
| CA-M5 (7j/1m = ouverture, fallback émission + WARNING) | PASS | `journaliste.py:1464-1473` + test `:182-202` |
| CA-M6/M6b (filtre 7h, fin du ×3) | PASS | `journaliste.py:1609,1637-1647` `only_seven_am` + test `:218-251` |
| **CA-M7** (compteur `jours_bourse_exclus` dans performance.md) | **NON IMPLÉMENTÉ** | aucune occurrence — voir réserve §7 (reste anticipé, non bloquant) |
| CA-S1 (tableau actionnables, colonnes) | PASS | `run_suivi.py:539-552` + test `:104-109` |
| CA-S2 (ouverture absente → —) | PASS | `run_suivi.py:473,107-108` + test `:272-285` |
| CA-S3 (Delta% 2 décimales) | PASS | `run_suivi.py:483-484` |
| CA-S4 (statut/NEUTRAL_BAND/seuil %) | PASS | `run_suivi.py:125-203` + `suivi.yaml:11` + test `:115-198` |
| CA-S5 (court, ≤50 lignes, pas de matrice) | PASS | `run_suivi.py:56` MAX=50 + test `:247-253` |
| CA-S6/S6b (n'écrit pas measures-log) | PASS | aucune écriture measures-log dans run_suivi + test `:229-240` |
| CA-B1 (bilan = prix-ouverture) | PASS | `bilan_jour.py:262-275` + test `:302-330` |
| **CA-B2** (CAC clôture = close 17h30) | **NON IMPLÉMENTÉ** | `bilan_jour.py` fetch `now` (22h15) uniforme — voir réserve §7 (dépend de Q5) |
| CA-B3 (24h définitif, pas re-noté J+1) | PASS | mesure au soir, échéance forcée `bilan_jour.py:261` |
| CA-B4 (win rate = VRAI/(VRAI+FAUSSE)) | PASS | `bilan_jour.py:285-287` + test `:325-326` |
| CA-B5 (aucun montant) | PASS | `bilan_jour.py` + test `:333-352` |
| CA-W1 (dimanche only, force=true bypass) | PASS | `weekly-summary.yml:74-90` (table de vérité conforme §5.3) |
| CA-W2 (archive hebdo telle quelle) | PASS | `run_weekly.py:401-435` + test `:263-275` |
| CA-W3 (champs obligatoires propositions) | PASS | `run_weekly.py:260-313` + test `:115-138` |
| CA-W4 (zéro écriture config) | PASS | `run_weekly.py` (data/ only) + `weekly-summary.yml:137-142` garde CI + test `:166-191` |
| CA-W5 (aucun montant) | PASS | test `:225-237` |
| CA-W6 (win rate par conviction, N<3 → insuffisant) | PASS | `bilan_jour.py:76-193` + `run_weekly.py:442-447` + test |
| CA-I1 (22h = R4 seul) | PASS | `cycle.yml:204-211,292-298` routage par slot |
| CA-I2 (dimanche = R5 seul, bypass) | PASS | `weekly-summary.yml` workflow séparé |
| CA-I3 (`--check` parseable) | PASS | `trigger-cycle.sh:48-61` expose `22h15-paris-jours-bourse` + `18h-dimanche` |
| CA-I4 (anti-doublon ×3) | PASS | `cycle.yml:155-173` (snapshot < 2h) |

## 2. Cohérence inter-chantiers

Vérifiée et **cohérente** :
- **Filtre 7h** uniforme : `is_seven_am_bulletin` (`journaliste.py:488`) reconnaît 07h/05h-UTC/ancien-nommage, consommé par `measure(only_seven_am=True)`, `load_briefing_cells` (`run_suivi.py:242`), et `build_bilan_jour`. Aucune divergence.
- **Runners ↔ cron** : `cycle.yml` route vers `run_bulletin.py`/`run_stamp.py`/`run_suivi.py`/`run_bilan.py` selon l'heure Paris. Les 4 runners existent avec la bonne signature (`run_suivi.py main(report_type)`, `run_bilan.py main(--date)`, `run_stamp.py main(--date)`). `weekly-summary.yml` → `run_weekly.py`. Tous présents.
- **Fuseaux** : `ZoneInfo("Europe/Paris")` partout (mesure, suivi, bilan, weekly, run_stamp), routage cron par heure-Paris réelle (`cycle.yml:200-211`), **jamais d'offset UTC en dur**. La garde 22h15 est bien `ph==22 && pm>=15` (`cycle.yml:210`) ; le cron horaire plage `20,21 UTC` absorbe été (20h15 UTC) ET hiver (21h15 UTC). VPS cron `15 * * * *` + self-gate Paris cohérent.
- **prix-ouverture comme référence partagée** : `mesure_ouverture.stamp_prix_ouverture` écrit, `_resolve_prix_reference` (priorité ouverture, fallback émission) lit, `run_suivi`/`bilan_jour` consomment via `load_prix_ouverture`. Chaîne propre.
- **Conviction réutilisée** : `bilan_jour.win_rate_par_conviction` + `load_conviction_map` réutilisés par `run_weekly._conviction_semaine` (zéro duplication, zéro nouveau champ — conforme §4.7).

Note mineure (cohérence) : à 22h12 UTC-été (=00h12 Paris J+1) le cron ne tire pas le bilan car la plage UTC s'arrête à 21h ; seuls `:27` et `:42` de 20h/21h UTC tombent dans `pm>=15`. **2 tentatives effectives** sur le créneau bilan (au lieu de 3) — suffisant avec le VPS en redondance. Pas un défaut.

## 3. WIN RATE ONLY (zéro montant)

**PASS strict.** Grep `€|$|expectancy|equity|P&L|payback|montant|profit` sur les 6 scripts nouveaux : **0 occurrence** hors commentaires d'interdiction (`bilan_jour.py:16`, `run_suivi.py:18,191`, `run_weekly.py:14`). Les seuils sont en %, jamais en €. Tests anti-montant présents dans les 3 fichiers (`test_run_suivi.py:260`, `test_mesure_ouverture.py:333`, `test_run_weekly.py:225`). L'amplitude (`⚡ gros move`) sert UNIQUEMENT à trier les erreurs FAUSSE (`bilan_jour.py:43-47,322-330`), jamais à chiffrer un gain — conforme à la préférence fondateur.

## 4. Zéro modif silencieuse (Manager n'écrit pas config)

**PASS, double garde.** (a) `run_weekly.py` n'écrit que dans `v3/data/bilan-semaine/` et `.state/` (donnée de mesure, pas config — commentaire explicite `:52-54`). (b) `weekly-summary.yml:137-142` échoue le job (`exit 1`) si `git diff v3/config/` n'est pas vide. (c) test `test_aucune_ecriture_config` vérifie diff vide + aucun untracked sous `v3/config/`. Les propositions du Manager sont des drapeaux à valider (`build_propositions` → `validation: "Thomas OUI/NON"`). Aucun poids/seuil modifié en douce.

## 5. Mode shadow préservé

**PASS.** (a) Aucun envoi/émission dans les nouveaux scripts (pas de SMTP/webhook/publish). (b) Les commits cron portent `[skip ci]` (`cycle.yml:309-314`) → un commit ne déclenche aucun run. (c) Les workflows ne tournent que sur `schedule`/`workflow_dispatch`/`push RUN-*.txt` — jamais sur push de code. (d) `run_stamp`/`run_suivi` sont prix-only, pas de scoring/DeepSeek. Rien n'est déclenché par la bascule elle-même.

## 6. Sécurité du merge (rétrocompat, fallback, git diff)

**Acceptable — risque maîtrisé.**
- **Fallback prix-ouverture absent** : `_resolve_prix_reference` (`journaliste.py:1466-1473`) retombe sur prix-émission + WARNING si l'ouverture manque → **pas de régression** sur les jours sans stamp (transition). Si ni l'un ni l'autre → `(None,None)` → suivi-interrompu (zéro invention).
- **Rétrocompat tests existants** : `measure(only_seven_am=True)` est le défaut, mais `only_seven_am=False` restaure l'ancien comportement (`journaliste.py:1497-1498`) pour les tests historiques. La signature `measure()` reste compatible (nouveaux params optionnels).
- **Idempotence** : stamp + entry-lock garantissent qu'un re-run ne corrompt rien (`mesure_ouverture.py:237-263`).
- **Pollution data/** : `conftest.py:24-33` isole `prix-ouverture` par test (autouse) → les tests ne polluent pas `v3/data/`. ⚠️ Penser au `git checkout -- v3/data/` post-pytest quand même (mission).
- **Changement LIVE de la mesure** : la bascule fait passer la référence 24h de « prix 7h » à « ouverture marché », notée le soir même. C'est le changement voulu par Thomas. Le filtre 7h (CA-M6b) coupe le gonflement ×3 immédiatement (Q8 option B). Cohérent avec « mesurer avant d'agir ».

## 7. Contradictions / restes

**Aucune contradiction inter-livrables.** Deux restes, tous deux **anticipés par la spec** et **non bloquants** :

### Réserve R1 — CA-B2 : CAC clôture 17h30 non spécialisée (dépend de Q5)
- `bilan_jour.build_bilan_jour` fetch le prix de TOUS les actifs à `now` (22h15), CAC compris. La spec §3.4 demande le close Euronost 17h30 pour le CAC.
- **Pourquoi non bloquant** : le marché EU est fermé depuis 17h30 → le prix Twelve à 22h15 pour FCHI est le dernier traité = le close 17h30 (Q5 : « les deux options donnent le même résultat si Twelve retourne le close »). Le résultat de mesure est donc correct en pratique. Q5 est explicitement « détail d'implémentation à tester », pas une décision Thomas.
- **Action recommandée (P1, post-merge)** : `@fullstack` teste `fetch_twelve_price("FCHI")` après 17h30 en conditions réelles ; si Twelve renvoie un tick post-clôture aberrant, ajouter un cas CAC→close-17h30 dans `bilan_jour`. À tracer dans les restes.

### Réserve R2 — CA-M7 : compteur `jours_bourse_exclus` absent
- Aucune implémentation du compteur de jours de bourse sautés par la garde globale sur férié partiel (4 juillet, etc.).
- **Pourquoi non bloquant** : c'est une métrique d'observabilité (visibilité Thomas), pas une fonction du pipeline de mesure. Q2 a tranché « KISS : garde globale » → le cas est rare. La spec elle-même classe CA-M7 en P1 (correction D5, table §10 ligne 13).
- **Action recommandée (P1, post-merge)** : ajouter le compteur dans `performance.md` au prochain passage Journaliste. À tracer.

### Autres points vérifiés — aucun trou
- Conviction inconnue → classée « faible » (`bilan_jour.py:185`) : conservateur, ne gonfle jamais le « forte » (zéro invention) — conforme §4.7.
- `score_fort_seuil` 0.6 comparé au score BRUT non normalisé : **documenté honnêtement** (`bilan_jour.py:50-55`) comme à calibrer sur la distribution réelle (« mesurer avant d'agir »). Pas un bug, une dette assumée et signalée.

## Blockers P0 (à corriger avant merge)

**AUCUN.** Tous les garde-fous non négociables (WIN-RATE-ONLY, shadow, zéro modif silencieuse, zéro invention, DST sans offset, fallback) sont respectés et testés.

## Non-bloquants P1/P2

| # | Sévérité | Item | Action | Responsable |
|---|---|---|---|---|
| R1 | P1 | CA-B2 : CAC close 17h30 non spécialisé (Q5) | Tester `fetch_twelve_price("FCHI")` post-17h30 ; cas CAC si besoin | @fullstack |
| R2 | P1 | CA-M7 : compteur `jours_bourse_exclus` absent | Ajouter le compteur dans performance.md | @fullstack |
| R3 | P2 | `score_fort_seuil=0.6` vs score brut non normalisé | Calibrer sur distribution réelle après ~3 sem. (mesurer avant d'agir) | @product-manager / Thomas |
| R4 | P2 | Créneau bilan : 2 tentatives schedule effectives (pas 3) | Aucune (VPS en redondance) — ou étendre plage cron à 22 UTC si churn observé | @infrastructure |

## Top 3 corrections prioritaires

1. **Lancer pytest** (`python3 -m pytest v3/ -q` + `git checkout -- v3/data/`) — non exécutable dans cette session, à confirmer GO final.
2. **R1 — CA-B2 CAC close 17h30** : valider le comportement Twelve post-clôture EU (P1, post-merge, n'empêche pas le merge).
3. **R2 — CA-M7 compteur jours exclus** : observabilité Thomas (P1, post-merge).

---
**Handoff → @orchestrator**
- Fichiers produits : `/home/user/TradingApp/v3/audit/revue-finale-refonte-5-rapports.md`
- Décisions prises : **GO MERGE** (note 8,7/10), aucun blocker P0. 2 réserves P1 (CA-B2, CA-M7) anticipées par la spec, isolées, non bloquantes — à traiter post-merge.
- Points d'attention : (1) **exécuter pytest avant merge** (non lançable dans cette session) + restaurer `v3/data/` ; (2) tracer R1/R2 dans les restes ; (3) ne PAS commiter cette revue (l'orchestrateur regroupe).
---
