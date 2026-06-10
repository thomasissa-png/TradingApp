# CHANGELOG — TradingApp v3

> Historique des sessions de travail (le plus récent en haut). Détail technique : `git log` + `v3/audit/`.

## 2026-06-10 (Session 5) — SELECTION-RULE pré-enregistrée (Lot 3, @data-analyst)

**Audit mesure 10/06 — Lot 3.** Création de `v3/SELECTION-RULE.md` : règle de sélection des cellules à trader, **pré-enregistrée et gravée** (modèle `KILL-CRITERION.md`, statut VALIDÉ daté/signé Thomas, anti-post-hoc). Mode shadow, **WIN RATE ONLY**, **gel du scoring** (aucun poids/critère/seuil touché). Branche `claude/tradingapp-s5-shadow-5rapports-lq5g9z`.

- **Règle gravée** : à J+60 du shadow, ne trader QUE les cellules **24h** avec **WR tradable ≥ 70 % sur N ≥ 15 paris non-chevauchants** (N compté depuis `ref_changed` pour les cellules requalifiées). Aucune cellule éligible → pas de trading, revue J+90.
- **Deux métriques distinguées** : WR conclusif `VRAI/(VRAI+FAUSSE)` (kill criterion, moteur vivant) vs **WR tradable** `VRAI/(VRAI+FAUSSE+NC)` (sélection, métrique de décision de trading — introduite par le Lot 2). Décision Thomas validée 2026-06-10.
- **Limité au 24h** (7j/1m : autocorrélation → 15 sem/15 mois pour N indépendant, hors fenêtre J+60). `ref_changed` remet N à zéro dans les deux sens. Procédure J+60 écrite/signée, garde-fou anti-modification silencieuse (toute modif → `selection-rule-v2.md`).

## 2026-06-09 (Session 7b) — Tableau win rate affiché sur la page (@fullstack)

**Manque corrigé** : notre tableau win-rate-only propre (`v3/data/performance.md`, win rate par actif × horizon) n'était référencé **nulle part** dans `build_html.py` — Thomas ne voyait pas « le tableau avec les résultats d'orientation des actifs ». L'onglet Performance n'affichait que l'ancien A/B Taux/Brier (périmé). Mode shadow, WIN RATE ONLY, zéro modification de la logique de mesure, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### `build_html.py` — collecte + vue win-rate
- **`load_performance_md`** (nouveau) : lit `v3/data/performance.md` en markdown brut, ou `None` si absent (dégradation propre). Zéro transformation — réutilise tel quel le markdown du journaliste.
- **Nouvelle vue sidebar « 📈 Résultats / Win rate »** : rend le tableau win-rate-only via le pipeline marked.js existant (colorisation, tooltips, tables). Routage hash `#vue=resultats`. Absent → message de dégradation propre.
- **Onglet Historique modernisé** : le tableau win rate passe **en tête** (`#history-winrate`, résultats principaux) ; l'ancien bloc A/B Taux/Brier est **rétrogradé** dans un `<details>` replié « Détail technique par cellule » (masqué si `PERF_AB` vide). Les vues « Aujourd'hui »/« Bilan semaine » de la passe 1 et l'affichage des bulletins sont intacts.

### Tests — `v3/tests/test_build_html_winrate.py` (8 tests, verts)
- `load_performance_md` lit le MD / absent → `None` ; `render_html` embarque le tableau (`const WINRATE_MD`, grep de l'en-tête `| Actif | Win rate | …`) ; nav + section dédiées ; win rate en tête de l'onglet Historique + A/B rétrogradé ; dégradation propre (`WINRATE_MD = null`, pas de placeholder) ; garde-fou win-rate-only (aucun terme argent injecté par le builder). Suite complète `pytest v3/` : **984 passed, 3 skipped**. `git checkout -- v3/data/` avant commit (pytest régénère l'index).

## 2026-06-09 (Session 7) — Page index.html : affichage des 5 rapports (@fullstack)

**Bug corrigé** : depuis la refonte « 5 rapports », `build_html.py` ne ramassait QUE les `bulletin-*.md` (briefing 7h). Les suivis 12h/18h, le bilan du jour 22h et le bilan de semaine étaient produits mais **invisibles** sur la page. Mode shadow, WIN RATE ONLY, zéro modification de poids/seuils/scoring, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### `build_html.py` — collecte + rendu des nouveaux rapports
- **`build_reports_payload`** (nouveau) : collecte `v3/data/suivi/*.md` (12h/18h) + `v3/data/bilan-jour/*.md` (22h), tri date+heure décroissants, limite aux 30 jours récents. Chaque entrée porte `kind` (suivi/bilan-jour), `date`, `slot`. Dossier absent/vide → liste vide (dégradation propre, zéro crash).
- **`build_weekly_payload`** (nouveau) : renvoie le bilan de semaine le plus récent (`win-rate-YYYY-S##.md`, tri ISO année+semaine), ou `None`.
- **Sérialisation JS** factorisée (`_entries_to_js`) ; `REPORTS` + `WEEKLY` embarqués comme `BULLETINS`.
- **2 nouvelles vues** dans la sidebar : « 📅 Aujourd'hui » (briefing 7h + suivis + bilan du jour **regroupés par jour**, jour le plus récent ouvert par défaut, rendu MD paresseux par rapport) et « 🗓️ Bilan semaine ». Réutilisent le pipeline MD existant (marked.js + colorisation LONG/SHORT + tooltips + tables). Refacto : `showHistory`/`hideHistory` → `showAuxView`/`hideAuxViews` mutualisés (today/week/history).
- Dégradation propre : pas de bulletin mais des suivis → ouvre « Aujourd'hui » ; `WEEKLY` absent → section vide ; routage hash `#vue=aujourdhui` / `#vue=semaine`.

### Tests — `v3/tests/test_build_html_reports.py` (9 tests, verts)
- Collecte suivis+bilan (tri bilan 22h avant suivis, slots 12h/18h/22h), tri multi-jours, dossiers absents, fichiers hors format ignorés ; weekly le plus récent / absent ; rendu HTML inclut les 3 types ; dégradation propre sans rapports (`const WEEKLY = null`) ; garde-fou win-rate-only sur fixtures. Suite complète `pytest v3/` : **977 passed, 3 skipped**. JS embarqué validé (parse Node OK).

## 2026-06-08 (Session 6) — Finalisation refonte 5 rapports : CA-M7 + CA-B2 (@fullstack)

**Les 2 restes de la refonte implémentés** (spec §7 CA-M7/CA-B2). Mode shadow, WIN RATE ONLY, zéro modification silencieuse de poids/seuils/scoring, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### CA-M7 — Compteur de jours de bourse exclus (férié partiel) — `journaliste.py`
- **`is_partial_holiday(d)`** (nouveau, pur) : True si `is_trading_day(d)` exclut le run (jour de semaine férié de marché) alors qu'AU MOINS UN marché (NYSE/XNYS OU Euronext/XECB) est ouvert. Distinction des deux calendriers via la lib `holidays` (vérifié : Memorial Day = NYSE fermé/Euronext ouvert ; 1er Mai = inverse ; Noël = les deux). Fallback sans lib → False (zéro invention : on ne prétend pas savoir qu'un marché était ouvert ; le compteur sous-estime plutôt que de sur-compter).
- **`compter_jours_bourse_exclus(date_debut, date_fin)`** (nouveau) : compte les jours partiels sur la fenêtre inclusive.
- **`render_performance`** : nouvelle ligne « Jours de bourse exclus (férié partiel, un marché ouvert) : **N** sur la fenêtre {min émission} → {aujourd'hui} ». Fenêtre = de la 1ère date d'émission mesurée à aujourd'hui ; rien d'affiché si aucune mesure (pas de fenêtre inventée).

### CA-B2 — Clôture CAC officielle 17h30 (fallback robuste Q5) — `bilan_jour.py`
- Pour les actifs **EU (CAC)**, la clôture de référence du 24h = **close officiel 17h30** (bougie `1day` du jour J via `fetch_twelve_series`), PAS le spot 22h. Groupe EU résolu par `mesure_ouverture.actif_group` (override « CAC 40 → eu », heures depuis suivi.yaml — **zéro heure codée en dur**).
- **Fallback robuste (Q5 non validé en shadow)** : si Twelve ne renvoie pas de bougie datée du jour J (close 17h30 pas encore publié le soir même pour FCHI/ETF), on retombe sur le **dernier prix disponible + marqueur `[close approx]`** dans le tableau + note « À valider en live (Q5) ». **Zéro invention** : aucun close fabriqué.
- `build_bilan_jour` : nouveau param `fetch_series` (injectable, Twelve Data par défaut) + champ `BilanJour.close_approx_tickers`. Enveloppe `fetch_price` ; tous les autres actifs (US/continus) inchangés (spot 22h).

### Tests — `v3/tests/test_bilan_jour_cam7_cab2.py` (11 tests, verts)
- CA-M7 : `is_partial_holiday` (Memorial Day, 1er Mai, Noël non partiel, week-end non partiel), `compter_jours_bourse_exclus` (2 partiels sur mai, fenêtre vide, bornes inversées), affichage dans performance.md.
- CA-B2 : close officiel 17h30 utilisé si dispo (spot 22h ignoré), fallback `[close approx]` + note Q5 sinon, aucune mention monétaire.
- Gate `python3 -m pytest v3/ -q` : **968 passed, 3 skipped** (pré-existants). `git checkout -- v3/data/` avant commit.

## 2026-06-08 (Session 5) — Câblage cron/workflows des 5 rapports + stamps d'ouverture (@infrastructure)

**Routage des créneaux → bons runners + stamps d'ouverture aux VRAIES ouvertures** (spec §5 + CA-I*). Aucun run déclenché, mode shadow préservé, branche `claude/elegant-ramanujan-OIKms` (pas de PR).

### Routage par heure de Paris (cycle.yml — un seul workflow, runner selon l'heure réelle, DST-safe)
- **Nouveau step `Route`** : après la garde, calcule l'heure de Paris réelle et choisit le runner (`slot`) : **07h→`run_bulletin.py`** (R1 complet, stampe déjà les continus) · **08h05/09h05/15h35→`run_stamp.py`** (stamps d'ouverture prix-only) · **12h→`run_suivi.py 12h`** (R2 léger, PAS le bulletin, Q9) · **18h→`run_suivi.py 18h`** (R3) · **22h15 Paris→`run_bilan.py`** (R4, note les 24h). Les plages horaires absorbent l'écart été/hiver ; **jamais d'offset UTC en dur** (22h15 Paris = 20h15 UTC été / 21h15 UTC hiver — un `20h UTC` fixe noterait avant la clôture NYSE 5 mois/an).
- **Cron étendu** : créneaux historiques 7h/12h/18h **inchangés** (UTC fixe `5,10,16`, ne pas churner). Nouveaux créneaux (stamps + bilan) = **cron horaire `12,27,42 6,7,8,13,14,20,21`** + garde heure-Paris dans le step Route. Anti-doublon ×3 étendu (grep stamp/suivi/bilan). Steps conditionnés au `slot` (bulletin = ingest→bulletin→mesure→html ; stamp/suivi12/suivi18/bilan = runner unique). Garde `is_trading_day` (jours de bourse + fériés) + `force` **inchangée** pour tous les créneaux cycle.yml.
- **`v3/scripts/run_stamp.py`** (nouveau) : runner léger prix-only qui appelle `mesure_ouverture.stamp_prix_ouverture(now=...)` — AUCUN scoring/DeepSeek, idempotent + entry-lock (re-déclencher est sans effet). `stamp_prix_ouverture` ne stampe que les marchés ouverts à `now` → à 08h05 EU/US skippés, à 15h35 continus/EU déjà verrouillés. Aucune liste d'actifs codée (filtre par groupe de marché).

### Bilan semaine dimanche (workflow SÉPARÉ — choix Q7)
- **`.github/workflows/weekly-summary.yml`** (nouveau) : `schedule "12,27,42 16 * * 0"` (dim 16h UTC = 18h Paris) + `workflow_dispatch`(input `force`) + push `v3/RUN-WEEKLY.txt`. **Garde INVERSÉE vs cycle.yml** : bypass `is_trading_day`, ne tourne QUE le dimanche (`weekday()==6`/`%u==7`), `force=true` bypass (CA-W1.c). Anti-doublon ×3. Step `run_weekly.py`. **Garde-fou CA-W4 au commit** : refuse si `git diff v3/config/` non vide (le Manager n'applique rien).

### VPS Anya (horloge — routage autoritaire côté workflow)
- **`trigger-cycle.sh`** : créneaux Paris étendus à `07/08/09/12/15/18/22` (jours ouvrés → cycle.yml) + **dimanche 18h → weekly-summary.yml** (workflow cible choisi dans le script). Samedi muet. Flag **`--check`** (sortie parseable des créneaux, CA-I3). **`crontab.tradingapp`** : minute `0`→**`15`** (`15 * * * *`) pour que le tir 22h tombe à 22h15 Paris (≥ garde routage) — jamais un UTC fixe.

### Table de vérité (`test-guard-logic.sh`) — tous verts
- Ajout `route_slot` (miroir du step Route) + `weekly_decision` (garde workflow dimanche). Nouveaux cas : 7 créneaux de routage (été+hiver), bilan 22h15 vs 22h00→none, 8 cas weekly (dimanche/lundi/samedi/force/push). **ALL PASS.**

### CA-I* couverts / restants
Couverts : **CA-I1** (22h → R4 seul, pas de re-scoring) · **CA-I2** (dimanche → R5 seul, bypass bourse, weekday()==6) · **CA-I3** (VPS `--check` parseable : `22h15-paris-jours-bourse` + `18h-dimanche`) · **CA-I4** (anti-doublon ×3 sur 22h). **Restants @fullstack** (logique de MESURE, hors périmètre infra — touchent `bilan_jour.py`/`journaliste.py`, et CA-B2 dépend de Q5 non validé en shadow) : **CA-M7** (compteur `jours_bourse_exclus` dans performance.md) · **CA-B2** (close CAC officiel 17h30 dans le bilan). **Gates** : `pytest v3/ -q` 957 verts · `test-guard-logic.sh` ALL PASS · cycle.yml + weekly-summary.yml YAML valides · trigger `bash -n` OK. **Aucun run déclenché.**

## 2026-06-08 (Session 5) — Phase 3 refonte 5 rapports : bilan de la semaine dimanche 18h + le Manager (@fullstack)

Implémentation de la **Phase 3** (dernière) de `v3/docs/reco/spec-refonte-5-rapports.md` (v2, §4 + CA-W*) : le **bilan de la semaine (R5)** produit dimanche 18h + **le Manager**, 4e agent historique du système (Veilleur / Analyste / Journaliste / **Manager**), enfin implémenté. Le Manager est la couche apprentissage/pilotage : il LIT les résultats de la semaine et **PROPOSE des ajustements de config — Thomas VALIDE à la main, jamais d'application silencieuse**. **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention.**

### Livrables (@fullstack)
- **`v3/scripts/run_weekly.py`** (nouveau, R5 + Manager) — `build_bilan_semaine(now=...)` produit `v3/data/bilan-semaine/{AAAA-Sxx}.md`. Sections : (1) **win rate de la semaine** (archive hebdo `win-rate-{ISO}.md` reprise **telle quelle**, CA-W2) ; (2) **win rate par conviction** forte/faible (§4.7/CA-W6 — réutilise `bilan_jour.win_rate_par_conviction` + `load_conviction_map`, zéro nouveau champ ; conviction lue au decision-log du jour de décision) ; (3) **cellules porteuses** = ce qui MARCHE (§4.6, win rate ≥ 65% sur N_eff ≥ 5) ; (4) cellules à surveiller ; (5) **propositions d'ajustement** (format strict §4.5) ; (6) observations sans proposition ; (7) **dates de sortie de warm-up** par horizon (24h ~juillet, 7j ~octobre, 1m hors portée). **Réutilise `journaliste.measure()`** pour les KPIs (zéro recalcul custom). `wilson_low` du KPI ∈ [0,1] → converti en %. Fuseaux `ZoneInfo`, jamais d'offset en dur. CLI `python3 run_weekly.py`.
- **Le Manager — détection (le P0 corrigé du trio)** : une cellule est **faible** (→ proposition) UNIQUEMENT si **N_eff ≥ 10 ET Wilson_low < 50% ET observé sur ≥ 2 semaines CONSÉCUTIVES**. Entre N_eff 5-9 → **observation, PAS de proposition** (« mesurer avant d'agir »). Persistance inter-semaines via snapshots `v3/data/bilan-semaine/.state/{ISO}.json` (candidates faibles de la semaine), relus pour confirmer la 2e semaine — **donnée de mesure, jamais de la config**. Chaque proposition est justifiée par les **chiffres réels du KPI** (win rate, N_eff, Wilson) — zéro invention. **Le Manager n'applique RIEN** (CA-W4 : `git diff v3/config/` vide après run, **testé**).
- **Tests** — `test_run_weekly.py` (14 cas dérivés des CA-W* : petit N → pas de proposition, 1ère semaine → observation, **2 semaines consécutives → proposition**, champs obligatoires CA-W3, **`git diff v3/config/` vide après run** CA-W4, cellules porteuses §4.6, win rate par conviction CA-W6 + N insuffisant, **zéro montant** WIN-RATE-ONLY, persistance inter-semaines roundtrip, archive hebdo reprise telle quelle CA-W2). **957 tests verts** (+14), `v3/data/` non pollué (`git checkout` + dossier `bilan-semaine/` + `.state/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-W* couverts / restants
Couverts : **CA-W1 (guard dimanche — logique build, le déclenchement infra restant), CA-W2, CA-W3, CA-W4, CA-W5, CA-W6**. Restants (dépendent de l'infra — @infrastructure) : **CA-I2** (schedule dimanche 16h UTC + bypass `is_trading_day` + guard `weekday()==6` dans `cycle.yml`), **CA-I3** (créneau dimanche VPS Anya). Le cron dimanche 18h = infra, séparé (pas de PR, pas de run déclenché).

## 2026-06-08 (Session 5) — Phase 2 refonte 5 rapports : suivis 12h/18h légers + runner bilan 22h (@fullstack)

Implémentation de la **Phase 2** de `v3/docs/reco/spec-refonte-5-rapports.md` (v2, §3.2/§3.3) : les rapports de **SUIVI 12h (R2) et 18h (R3)**, courts (Thomas lit en 2 min), + le **runner CLI du bilan 22h** (R4). **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention. Le suivi N'ÉCRIT PAS dans measures-log (pas de cellule mesurée, pas de re-scoring DeepSeek).** Phase 3 (Manager dimanche) NON faite.

### Livrables (@fullstack)
- **`v3/scripts/run_suivi.py`** (nouveau, R2/R3) — `build_suivi(report_type, now=...)` lit les positions 24h du **Briefing 7h du jour** (`load_briefing_cells`, exclut INSUFFISANT) et produit `v3/data/suivi/{date}-{12h|18h}.md`. Pour chaque actif : **statut vs SON ouverture** (`(prix − ouverture)/ouverture` % → ✅ gagne / ⚠️ perd / — neutre sous `neutral_band_pct`), **dynamique de tendance** (↑ s'accélère / ↓ s'essouffle / ⇄ se retourne vs le suivi précédent — snapshot 12h relu au 18h ; flags US ↗ confirmé / ↘ infirmé au 18h), **suggestion de sortie** (`Sortie à envisager` si `|Delta%| ≥ SEUIL_PCT_actif` CONTRE le call — **drapeau, jamais un ordre** ; sinon Hold/Surveiller), **news à impact** (court, best-effort depuis le decision-log 7h, zéro DeepSeek). **Marchés US à 12h** : affichés explicitement `🕐 pas encore ouvert` (ouverture 15h30) — pas de ligne trompeuse ; 1er statut US au 18h. Heures via `mesure_ouverture.actif_group`/`is_open_for_stamp` (ZoneInfo, **jamais d'offset en dur**). **Léger** : prix + news, PAS de matrice LONG/SHORT, PAS de scoring (Q9). CLI : `python3 run_suivi.py 12h|18h`.
- **`v3/scripts/run_bilan.py`** (nouveau, runner R4) — appelle `bilan_jour.build_bilan_jour(now=...)` (Phase 1) + `write_bilan_jour`. CLI `--date`. Le **déclenchement 22h15 Paris = infra (séparé)**.
- **Tests** — `test_run_suivi.py` (15 cas dérivés des CA-S* : briefing 24h actionnables, statut vs ouverture ✅/⚠️/neutre, dynamique ↑/↓/⇄ + Δ vs 12h au 18h, flag US confirmé/infirmé, drapeau sortie au seuil contre le call, US pas-ouvert à 12h (🕐) puis ouvert à 18h, **run_suivi n'écrit pas measures-log**, rapport court sans matrice, zéro mention monétaire, ouverture absente → —, runner bilan smoke). **943 tests verts** (+15), `v3/data/` non pollué (`git checkout` + dossier `suivi/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-S* couverts / restants
Couverts : **CA-S1, CA-S2, CA-S3, CA-S4, CA-S5, CA-S6, CA-S6b** + runner R4 (CA-B* déjà couverts en Phase 1). Restants (dépendent de l'infra — @infrastructure) : **CA-I1/I3/I4** (steps cycle 12h/18h/22h appellent run_suivi/run_bilan, anti-doublon, créneaux VPS), **Q9** (les créneaux 12h/18h lancent-ils encore run_bulletin complet ? — décision Thomas/infra).

## 2026-06-08 (Session 5) — Phase 1 refonte 5 rapports : mesure ouverture→clôture + bilan 22h (@fullstack)

Implémentation de la **Phase 1** de `v3/docs/reco/spec-refonte-5-rapports.md` (v2) : le prix de référence du 24h passe de « prix au run 7h » (souvent marché fermé / prix de nuit) à l'**ouverture propre de chaque marché → clôture, jugée à 22h le jour même**. Corrige l'artefact signalé par Thomas (call jugé FAUX à cause du prix de nuit). **WIN RATE ONLY, mode shadow, zéro modif silencieuse, zéro invention.** Phases 2 (suivis 12h/18h) et 3 (Manager dimanche) NON faites.

### Avant / après (Or 24h, démontré)
Même mouvement réel, call LONG : **ancien** modèle réf=3500 (prix 7h nuit) → clôture 3420 = −2.3 % → **FAUSSE** (artefact). **Nouveau** modèle réf=3400 (ouverture propre 8h) → clôture 3420 = +0.59 % → **VRAI** (vraie tendance de session).

### Livrables (@fullstack)
- **`v3/scripts/mesure_ouverture.py`** (nouveau) — `stamp_prix_ouverture(date_j, now=...)` écrit `v3/data/prix-ouverture/{YYYY-MM-DD}.json` (1/jour, clé par date, distinct de prix-emission). Stampe chaque actif **après l'ouverture de son marché + délai 5 min** (continus 08h05, CAC 09h05, US 15h35 — heures Paris via `ZoneInfo`, **jamais d'offset codé en dur**). Idempotent + entry-lock (ré-écriture refusée). Twelve KO → ticker **absent** du JSON (zéro invention → suivi-interrompu). Mapping groupe EU/US/Continu par **famille de fiche** + override par nom (CAC=eu, S&P/Nasdaq/VIX=us, reste=continu). **Convention 08h des continus = référence conventionnelle assumée (Q10, décision Thomas), PAS close-to-close** — documentée. Config `v3/config/suivi.yaml` (`neutral_band_pct`, `open_stamp_delay_min`, heures, mapping).
- **`v3/scripts/journaliste.py`** — (1) **Référence 24h/7j/1m = prix d'ouverture** du jour de décision (`_resolve_prix_reference`), **fallback prix-emission + WARNING** si ouverture absente (Q3/CA-M5). Champ `prix_reference_source` (`ouverture`/`emission`) tracé dans `measures-log.jsonl`. (2) **Filtre 7h (CA-M6/M6b)** : `is_seven_am_bulletin` (reconnaît `07h` Paris, `05h` UTC historique, ancien nommage) + `measure(only_seven_am=True)` → seul le Briefing 7h est noté ; les suivis 12h/18h sont marqués `non-noté` (exclus des KPIs). **Fin du gonflement N_brut ×3.** (3) `run()` stampe l'ouverture (continus à 7h, EU/US complétés aux runs ultérieurs), param `prix_ouverture_dir` isolable.
- **`v3/scripts/bilan_jour.py`** (nouveau, R4) — `build_bilan_jour(now=...)` note les calls 24h du 7h (ouverture→clôture), produit le markdown R4 : résultat par actif, **win rate du jour**, **win rate par conviction** forte/faible (CA-W6, depuis decision-log : `score_pm1` + drapeaux `coin_flip`/`quasi_neutre`/`mono_critere_dominant`/`diverge`), **FAUX à gros mouvement** (flag `⚡` si |delta| ≥ 2×seuil, tri par **amplitude % — PAS d'argent**), news qui ont compté (Option C croisement, zéro DeepSeek), catalyseurs J+1 best-effort. **Le déclenchement 22h15 Paris = infra (à faire), la FONCTION est construite et paramétrable par `now`.** Config `v3/config/manager.yaml` (`score_fort_seuil`). **Aucune mention monétaire** (test garde-fou).
- **Tests** — `test_mesure_ouverture.py` (15 cas dérivés des CA-M*/CA-B*/CA-W6 : mapping groupe, délai+DST, stamp idempotent/entry-lock, Twelve KO absent, 24h=ouverture, fallback émission, filtre 7h reconnaissance + fin ×3, conviction forte/faible, bilan note 24h, zéro montant, flag gros move). `conftest.py` autouse anti-pollution prix-ouverture. 2 tests adaptés au nouveau modèle (multislot : 16h désormais `non-noté` ; audit veille : bulletin 7h). **928 tests verts** (+15), `v3/data/` non pollué (`git checkout` + dossiers `prix-ouverture/`+`bilan-jour/` avec `.gitkeep`). Shadow préservé, aucun run déclenché.

### CA-M* couverts / restants
Couverts : **CA-M1, CA-M2, CA-M3, CA-M4, CA-M5 (Q3), CA-M6, CA-M6b, CA-B1, CA-B3, CA-B4, CA-B5, CA-W6**. Restants (dépendent de l'infra — @infrastructure) : **CA-M7** (compteur `jours_bourse_exclus` dans performance.md), **CA-B2** (clôture CAC=17h30 — comportement Twelve à valider Q5), **CA-I1/I4** (cron 22h + anti-doublon), créneau VPS 22h15.

## 2026-06-08 (Session 4) — `performance.md` refondu en tableau WIN RATE propre + archive hebdo figée

Thomas trouvait `performance.md` illisible (colonne « Alertes » = pavé répété sur chaque ligne, Brier inutile, double colonne de taux, 1m absent). **Présentation + nouveau fichier hebdo uniquement — zéro changement de la logique de mesure** (entry-lock, look-ahead, N_eff, seuils VRAI/FAUX, decision-log inchangés).

### Correctif (@fullstack)
- **`v3/scripts/journaliste.py`** — `render_performance` réécrit en **tableau win-rate-only** : colonnes `Actif | Win rate | Paris (réels) | Non notés | Statut`, **groupé par horizon (24h → 7j → 1m), trié par win rate décroissant**, **36 cellules (12 actifs × 3 horizons) toujours visibles dont le 1m** (`⏳ en attente`). Win rate = `taux_eff` (N_eff indépendants, pas le N_brut gonflé ×3). Statuts win-rate-only sans aucune notion d'argent : `⏳ trop peu (N/15)` / `✅ objectif atteint` (N_eff ≥ 15 ET ≥ 70 % ET Wilson_low > 50 %) / `❌ sous l'objectif` / `⏳ en attente`. Ligne de synthèse en tête (`X / 36 cellules fiables`). **Retirés de l'affichage** : Brier, `Taux_brut`, colonne « Alertes » (pavé), `LONG/SHORT`, statut shadow répété, P&L (jamais présent) — **conservés dans `measures-log.jsonl`/decision-log pour le technique**. Section « Flip vs continuation » réduite à 2 lignes d'agrégats (omise si pas de données).
- **Archive hebdomadaire figée** — nouvelle `render_weekly_winrate` + `write_weekly_winrate` : à chaque run, écrit le même tableau (win rate **cumulé** + colonne **« Nouveaux paris (semaine) »**) dans `v3/data/performance/weekly/win-rate-{AAAA-Sxx}.md` (semaine ISO Europe/Paris). Réécrit pendant la semaine, **figé** dès qu'elle est passée (plus aucun run ne le touche) → historique semaine par semaine. Helpers `iso_week_label` / `iso_week_bounds`. Dossier `v3/data/performance/weekly/` créé (`.gitkeep`).
- **`build_html.py` inchangé** : la page ne rend PAS la matrice de `performance.md` (l'onglet Historique lit `measures-log.jsonl` + `performance-ab.md`, tous deux intacts) → aucune incohérence introduite.
- **Tests** : `test_winrate_view_weekly.py` neuf (18 cas : colonnes, tri décroissant, 36 lignes dont 1m, statuts, synthèse, semaine ISO, archive au bon chemin, colonne nouveaux paris, run bout-en-bout). Tests asservis à l'ancien format mis à jour (`test_journaliste_v2.py`, `test_lot6_publication_observabilite.py`, `test_journaliste.py`). **913 tests verts**, `v3/data/` non pollué (`git checkout` post-run, dossier `weekly/` préservé). Shadow préservé, aucun run déclenché.

## 2026-06-08 (Session 4) — Détail par actif : synthèse directionnelle 24h/7j/1m placée avant le tableau de chaque actif

Thomas voulait voir la **décision des 3 horizons d'abord**, puis le détail des critères qui la justifie. Avant : sous `### {nom}` on enchaînait directement le tableau, et la ligne « Scores » arrivait après. **Mise en page uniquement — zéro changement de chiffre, score, logique ou conclusion.**

### Correctif (@fullstack)
- **`v3/scripts/scoring_analyste.py`** — ligne de synthèse directionnelle insérée juste après `### {nom}` et **avant** le tableau de critères : `**24h : LONG (+20.00) · 7j : SHORT (−8.16) · 1m : SHORT (−3.90)**` (direction `r.conclusions[h]` + note signée `r.scores[h]` à 2 décimales, séparateurs `·` cohérents avec le bulletin). L'ancienne ligne `- Scores : 24h=… · 7j=… · 1m=…` placée **après** le tableau (désormais redondante) a été **retirée** (pas de doublon).
- **Tests** : `test_detail_synthese_avant_tableau` (neuf) vérifie l'ordre titre < synthèse < en-tête de tableau, les 3 horizons avec note signée 2 décimales, et l'absence de l'ancienne ligne « - Scores : ». **898 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Mesure VRAI/FAUX et decision-log identiques. Shadow préservé, aucun run déclenché.

## 2026-06-06 (Session 4) — Noms des 100 critères reformulés en langage trader

Thomas ne comprenait pas les noms de critères (« NOAA drought % Midwest+Plains D2+ », « USDA WASDE stocks-to-use mondial », « CFTC COT nets »…). Implémentation de la spec @copywriter `v3/audit/reco-wording-noms-criteres.md` — **champ `nom:` uniquement**, zéro modification de `cle_courante`, poids, signe, source, normalisation, seuils, logique, score ou conclusion.

### Correctif (@fullstack)
- **`v3/config/fiches/*.yml` (12 fiches)** — les **noms des 100 critères** (115 libellés `nom:` gates inclus) reformulés en langage trader : **acronymes de sources retirés** (NOAA, WASDE, COT/CFTC, COMEX, LME, SHFE, EIA, API, DXY, GATE, NASS, GASC, EUDR, FedWatch, Caixin…) → libellés clairs (ex. « NOAA drought % Midwest+Plains D2+ » → « Sécheresse dans les plaines céréalières US » ; « CFTC COT nets » → « Positionnement des gros spéculateurs (or) » ; « DXY trend 20j » → « Tendance du dollar (20 jours) »). **Acronymes porteurs d'info conservés** (PMI, RSI, VIX/VXN/V2X, SKEW/VVIX, ICE, CAPE) + **mini-glossaire** ajouté 1× en pied de la section « Détail par actif » (`v3/scripts/scoring_analyste.py`, `DETAIL_TABLE_GLOSSARY_LINES`).
- **Tests** : `v3/tests/test_fiches_wording.py` (neuf, 4 cas) — aucun acronyme de source dans les `nom:` des fiches réelles, blé sans « NOAA », COT or traduit, glossaire citant PMI/RSI/VIX/SKEW/VVIX. **897 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Shadow préservé, aucun run déclenché.

## 2026-06-06 (Session 4) — Tableau « Détail par actif » reformulé en langage trader

Thomas ne comprenait pas les lignes critères du tableau (`zscore`, `Norm.`, `Signe -1`, `lineaire centre=75 echelle=12`…). Implémentation de la spec @copywriter `v3/audit/reco-wording-detail-bulletin.md` — refonte des libellés/colonnes uniquement, **zéro changement de chiffre, score, logique ou conclusion**.

### Correctif (@fullstack)
- **`v3/scripts/scoring_analyste.py`** — en-têtes reformulés (9 colonnes, « Note » supprimée) : `Critère | Comment c'est lu | Valeur actuelle | Penchant | Importance | Sens | Effet 24h | Effet 7j | Effet 1m`. Types traduits via `TYPE_NORM_LABELS` (zscore→Écart à la normale, lineaire→Échelle graduée, mapping_non_monotone→Régime par seuils, composite→Signal combiné, triplet→Direction news, gate→Drapeau régime ; fallback sur le brut si type inconnu, pas de crash). Colonne **Sens** humaine : `normal` (signe +1) / `inversé` (signe -1), `—` pour les gates. **Gate actif préservé** : « Drapeau régime ⚑ actif » affiché dans « Comment c'est lu » (info de risque ex-portée par la colonne Note). Paramètres techniques `centre=X echelle=Y` retirés de la vue (restent au decision-log). Encart **« Comment lire ce tableau »** statique inséré 1× avant le 1er actif.
- **`v3/scripts/build_html.py`** — masquage mobile recalé sur le tableau 9 colonnes : 3e (« Valeur actuelle ») + 4e (« Penchant ») au lieu de l'ex-10e (« Note » disparue). Tableau lisible sur mobile (Critère + Sens + 3 colonnes Effet conservés).
- **Tests** : assertions des en-têtes / Note / masquage mobile mises à jour (`test_bulletin_top3_fusion.py`, `test_build_html_multislot.py`), + 2 tests neufs (`test_detail_table_wording_humain`, `test_detail_table_sens_inverse`) vérifiant nouveaux en-têtes, traduction de type, Sens normal/inversé et encart unique. **893 tests verts**, `v3/data/` non pollué (`git checkout` post-run). Mesure VRAI/FAUX et decision-log identiques. Shadow préservé.

## 2026-06-06 (Session 4) — Fériés de marché AUTO via lib `holidays` (NYSE XNYS + Euronext XECB) — fin de la maintenance annuelle manuelle

**Demande fondateur** : que la mise à jour des jours fériés de marché soit **automatique chaque année, zéro maintenance manuelle**. Avant : `MARKET_HOLIDAYS` était une liste statique « à étendre chaque année » → dette de maintenance + risque d'oubli (un férié non recopié = run sur prix figés).

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** — `_is_market_holiday` refondu : **source PRIMAIRE = lib `holidays`**, calendrier **XNYS** (NYSE) **∪ XECB** (TARGET/ECB = exactement les fermetures Euronext : 1 Jan, Vendredi saint, Lundi de Pâques, 1 Mai, 25 Déc, 26 Déc), **calculé pour l'année de la date testée** → valable 2026/2027/2028… **automatiquement**, plus de liste à étendre. `_is_market_holiday(d) = d ∈ (XNYS(d.year) ∪ XECB(d.year)) ∪ MARKET_HOLIDAYS`.
- **`MARKET_HOLIDAYS` (statique)** → devient (1) **fallback déterministe** anti-crash si la lib est absente/échoue, (2) **filet d'override manuel** pour fermetures ad-hoc hors lib (deuil national, etc.). Commentaire « à étendre chaque année » remplacé par « la lib couvre l'auto ; ce set = overrides exceptionnels + fallback ». Couverture 2026 conservée pour le fallback.
- **ROBUSTESSE (garde-fou critique)** : tout échec (ImportError, code financier absent de la version, API différente) → `_is_market_holiday` retombe **proprement** sur le socle statique, **JAMAIS de crash** (un crash dans la garde = NO-OP permanent du pipeline). Pattern try/except import préservé et durci.
- **`.github/workflows/cycle.yml`** — étape Guard : `pip install -q holidays || echo …` ajouté **juste avant** l'appel `python3 -c is_trading_day` (la garde tourne AVANT le setup des deps). Si ce pip échoue (réseau), `|| true` n'interrompt rien → fallback statique. Table de vérité + commentaires mis à jour (source des fériés devient auto ; logique conceptuelle inchangée). YAML revalidé (`yaml.safe_load`).
- **`v3/requirements.txt`** : `holidays==0.98` ajouté (pure-python) pour le pipeline de mesure.
- **Tests `v3/tests/test_is_trading_day.py`** (7 → **12 cas verts**) : **PREUVE de l'automatisme** — fériés **2027** (Noël 24/12, Thanksgiving 25/11, Lundi de Pâques 29/03) et **2028** (Vendredi saint 14/04, Thanksgiving 23/11, 1 Mai) calculés par la lib, **absents du statique** → `is_trading_day=False` ; **cohérence croisée** lib (XNYS ∪ XECB) vs statique **2026** (identiques, zéro divergence) ; **fallback ImportError** via monkeypatch → pas de crash, jour ouvré non bloqué. Simulation du chemin CI exact (`python3 -c`) : Noël 2026/2027, Thanksgiving 2027, Vendredi saint 2028 → NO-OP ; mardis ordinaires 2026/2028 → run. **Aucune régression** (174 tests journaliste/mesure verts). `v3/data/` non pollué.
- **Garde-fous** : zéro invention, mode shadow, logique de compute non touchée (calendrier de garde uniquement), aucun jour ouvré normal bloqué, fallback anti-crash testé. **Aucun run déclenché.** `test_scoring.py` non touché (autre agent en parallèle).

## 2026-06-06 (Session 4) — Test audit-veille rendu déterministe (date figée jour ouvré) — fin du faux rouge week-end

**Bug du test (pas du code)** : `test_audit_veille_liste_conviction_normale_vrai` et `test_audit_veille_exclut_faible_carry_news` (`v3/tests/test_scoring.py`) ancraient `now = datetime.now()` puis `bdate = now - 1 jour`. Le **samedi**, `bdate` = vendredi et la logique d'échéance 24h jour-ouvré/fériés (ajoutée en S3) reporte au lundi → la cellule n'est « pas encore » mesurable → l'assertion `assert "Pas encore" not in txt` casse. Le test échouait donc **uniquement selon le jour réel d'exécution** (rouge le samedi 06/06, vert en semaine).

### Correctif (@fullstack)
- **`v3/tests/test_scoring.py`** : `now` figé sur **`datetime(2026, 6, 9, 12, 0)`** (mardi) → `bdate` = **lundi 2026-06-08** (jour ouvré, NI week-end NI férié de marché) → échéance 24h mûre quel que soit le jour réel. **2 tests corrigés**. Assertions métier intactes (✅, VRAI, +5.00%, exclusion faible/carry/news). `test_audit_veille_warmup_message` laissé tel quel (indépendant du jour : vérifie le message warm-up sans cellule à mesurer).
- **Gate** : `python3 -m pytest v3/tests/test_scoring.py -q` → **33 passed, 100% vert** (dont les 3 `test_audit_veille_*`). `v3/data/` non pollué (`git checkout` post-run).

## 2026-06-06 (Session 4) — Garde de run étendue aux jours fériés de marché (réutilise `MARKET_HOLIDAYS`)

**Demande fondateur (« point final »)** : des rapports **uniquement les jours où la bourse est OUVERTE**. Le week-end était déjà coupé ; il manquait les **jours fériés de marché** — un lundi férié (NYSE/Euronext fermés) produisait encore un bulletin sur **prix figés à la clôture précédente** + mesures 24h dégénérées (« +0.0% ») qui polluent le shadow.

### Correctif (@infrastructure)
- **`v3/scripts/journaliste.py`** : nouvelle fonction importable **`is_trading_day(d: date) -> bool`** = `jour ouvré (lun-ven) and not _is_market_holiday(d)`. **SOURCE DE VÉRITÉ UNIQUE** : réutilise EXACTEMENT le calendrier existant `_is_market_holiday` / `MARKET_HOLIDAYS` (NYSE ∪ Euronext) — **zéro liste de dates dupliquée**, une seule à maintenir. La fonction ne juge QUE le jour (le bypass `force` reste dans la garde YAML).
- **`.github/workflows/cycle.yml`** — étape Guard : le test week-end bash pur est remplacé par un appel **Python** à `is_trading_day(today Europe/Paris)` (stdlib + `MARKET_HOLIDAYS` statique, aucune dépendance réseau/pip — `python3` est dispo sur les runners avant le setup deps). Conservé : échappatoire `force`/`RUN-CYCLE.txt` (bypass tout), anti-doublon ×3 schedule-only. Si bourse fermée (week-end **OU** férié) et pas de force → `run=false` (NO-OP) avec log clair (« week-end » / « férié de marché AAAA-MM-JJ »). Table de vérité mise à jour (ligne « dispatch (VPS) / jour férié / false → NON ← FIX »).
- **VPS (`trigger-cycle.sh`)** : la garde week-end bash y reste (fast-path) ; les **fériés** sont gérés de façon **autoritaire au niveau du workflow** (le VPS n'a pas l'env Python du repo et NE recopie AUCUNE liste de fériés). Le VPS peut tirer un lundi férié → le workflow NO-OP. Documenté dans `v3/ops/vps-trigger/README.md`.
- **Tests** : `v3/tests/test_is_trading_day.py` (7 cas : mardi True, samedi/dimanche False, **férié réel de `MARKET_HOLIDAYS`** False, cohérence calendrier, signature `is_trading_day(d)` sans `force`). `test-guard-logic.sh` étendu (param `holiday`) → **13 cas verts** dont férié schedule/dispatch/force/push. `v3/data/` non pollué (vérifié).
- **Garde-fous** : zéro duplication du calendrier, zéro invention, mode shadow, aucun jour ouvré normal bloqué, logique de compute non touchée (garde de déclenchement uniquement). Aucun run déclenché.

## 2026-06-06 (Session 4) — Garde week-end étendue à `workflow_dispatch` (VPS) + input `force` + garde jour-ouvré VPS

**Bug** : un briefing a été produit **samedi 06/06 07h** alors que le week-end doit être coupé. **Cause racine** (diagnostiquée, non ré-enquêtée) : la garde week-end de `cycle.yml` ne s'appliquait qu'aux événements `schedule`. Or le **driver réel** est le **pinger VPS**, qui déclenche en **`workflow_dispatch`**. L'early-exit en tête de garde (`if event != schedule → run=true; exit`) traitait `workflow_dispatch` comme un forçage manuel → le NO-OP week-end (plus bas) n'était jamais atteint pour le VPS. Résultat : run samedi sur prix figés (clôture vendredi) → mesures 24h dégénérées polluant le shadow.

### Correctif (@infrastructure)
- **`.github/workflows/cycle.yml`** : input booléen **`force`** (défaut `false`) ajouté à `workflow_dispatch`. Garde **restructurée** (table de vérité en commentaire) : (1) **forçage explicite** = `inputs.force=='true'` **OU** push `RUN-CYCLE.txt` → `run=true`, bypass tout (week-end inclus) = échappatoire humaine ; (2) **sinon** (schedule OU dispatch-VPS sans force) → **garde week-end** (sam/dim Europe/Paris → `run=false`) ; (3) jour ouvré → **anti-doublon ×3 pour le schedule uniquement** (VPS = 1 tir/créneau, toujours passé, comportement préservé). **Aucun run de semaine affecté.**
- **`v3/ops/vps-trigger/trigger-cycle.sh`** : **garde jour-ouvré** ajoutée (`TZ=Europe/Paris date +%u ≥ 6 → exit 0`) → le pinger ne dispatche même pas le week-end (économise un no-op, cohérence). `TRADINGAPP_FORCE=1` bypass aussi. Garde week-end côté `cycle.yml` conservée en **défense en profondeur**.
- **`v3/ops/vps-trigger/test-guard-logic.sh`** : nouveau script de test (miroir exact de la décision YAML) — **10 cas verts** dont les 6 clés de la table de vérité. README VPS documenté.
- **Garde-fous respectés** : aucun run déclenché (logique seule), compute du pipeline non touché (garde de déclenchement uniquement), mode shadow préservé.

## 2026-06-06 (Session 4) — `mining_com` retiré (403 Cloudflare persistant CI, retry inefficace)

**Contexte** : le retry 403 borné posé le 05/06 (`RETRY_STATUS_WITH_403`, cf. Bug 2 plus bas) **n'a PAS résolu** le problème. Le run live frais du 06/06 07h montre `mining_com` **toujours ❌ HTTP 403**. **Diagnostic confirmé** (pas ré-enquêté) : blocage **Cloudflare PERSISTANT sur la plage d'IP des runners GitHub Actions** — le feed répond 200 ailleurs, jamais depuis CI. Le retry ne peut rien faire si TOUTE la plage d'IP est bloquée (≠ 403 intermittent par requête, hypothèse du 05/06 invalidée). **Décision (avec Thomas) : retirer la source** (poids faible ~1.1, redondante avec `investing_commodities`/`investing_metals` poids 0.9 + `oilprice`).

### Retrait (@fullstack)
- **`v3/scripts/config.py`** : ligne `("mining_com", …)` retirée de `EARLY_SIGNAL_FEEDS` + poids `"mining_com": 1.1` retiré de `SOURCE_WEIGHTS`. Commentaire de retrait documenté in-place (pourquoi). Le **total de flux n'est PAS figé** (`source_monitor.summary()` = `len(self.by_name)` dynamique) → il se décrémente seul, plus de faux « partiel ». Plus aucun appel `mining_com` → plus de ❌ 403 dans `source-health.md`.
- **Aucun critère cassé** : les news sont poolées + matchées par mots-clés. Les critères `mining_strikes_*`/`demande_pv_mining_strikes` (cuivre/argent) matchent sur le **pool global** de news, sans dépendance au flux `mining_com` (vérifié : zéro mapping nommé vers le flux). Le retrait enlève quelques items, ne touche ni scoring ni mesure.
- **Mécanisme retry 403 conservé** pour les autres RSS scrapables (`RETRY_STATUS_WITH_403` reste utile si un flux a un 403 *réellement* intermittent) — commentaires généralisés (plus de dépendance à mining.com comme exemple).
- **Pas de remplacement câblé** : aucun flux métaux/mining RSS gratuit n'a de certitude de marcher depuis les runners CI (c'est le piège exact qui a tué mining_com). Candidats à TESTER avant câblage : `kitco.com` RSS, `investing.com/rss/commodities_Industrial_Metals.rss`. Retrait net = objectif minimal atteint.
- **Tests** : références flux→config remplacées (`investing_metals` / nom générique) ; assertions `mining_com not in feeds/polled` ajoutées. Suites ingestion+http_retry+source_monitor **61 verts**. Suite `v3/` complète : **878 passed** (1 échec **pré-existant** `test_audit_veille_liste_conviction_normale_vrai`, date-dépendant samedi, sans lien). `v3/data/` restauré après pytest (pas de pollution des runs réels).

## 2026-06-05 (Session 4) — Corrections audit trio bulletins live (A1/A2 flag-only) + recos Lot 4b/ticket C

**Contexte** : audit trio des bulletins live 04-05/06 (Analyst/News Trader/Spéculateur). Verdict unanime **AJUSTER**. Corrections appliquées = **flag-only, zéro impact conclusion/mesure**. Tout ce qui touchait une DÉCISION (Lot 4b contre-momentum, ticket C calibration) → **reco À VALIDER THOMAS**, pas appliqué (garde-fous fondateur). 870 → 873 → **879 tests** (+6 : 2 micro-bugs run live 18h04, voir bas de section), 0 régression. Doc clé : `v3/audit/reco-corrections-2026-06-05.md`.

### Outil — relancer le backtest quant v2 AVEC FRED (@infrastructure)
- **Nouveau workflow `.github/workflows/backtest-v2.yml`** (job `backtest-v2-fred`, `workflow_dispatch` **MANUEL uniquement**, jamais de cron → ne concurrence pas `cycle-decision`, mode shadow préservé). Expose `FRED_API_KEY` (secret), lance `backtest_quant.py`, publie le log/REPORT en **artifact** (`upload-artifact`). But : clore le verdict sur l'arm d'ablation **`+FRED`** (le run de réf a tourné sans clé → `+FRED` == `price-only`).
- **Stratégie cache** : yfinance étant **bloqué sur les runners CI**, le **cache prix/COT** (`v3/backtest/.cache/*.csv`, 35 fichiers, 3,6 Mo, OHLCV/COT publics, **0 secret**) est **committé** (`git add -f`, dossier gitignored). Le CI lit ce cache (0 appel yfinance) + appelle **FRED réellement** (les `fred__*.csv` sont **volontairement NON committés**) + CFTC Socrata. Step sanity qui abort si cache absent. Fallback documenté : VPS Anya.
- **Garde-fous** : `permissions: contents: read`, **AUCUN commit auto** (l'exécution salit `v3/data/` via import `scripts/` → un commit écraserait les runs réels de `cycle-decision`). Doc « Comment relancer avec FRED » ajoutée à `v3/backtest/REPORT.md`. Tests `test_backtest.py` **21 verts**. **Non déclenché** (Thomas décide du lancement).

### Vrais bugs corrigés (affichage uniquement)
- **A1 — mono-critère rendu VISIBLE** (`◧`) : la détection `mono_critere_dominant` fonctionnait déjà (CAC 7j ET EUR/USD 7j = True au decision-log — l'« incohérence d'affichage » de l'audit n'existait pas), mais le flag était SHADOW decision-log only, jamais affiché. Les 3 experts jugent le mono-critère trop fragile pour rester invisible (EUR/USD 7j = 96% sur 1 critère). Ajouté : drapeau `◧` dans la matrice + section « Cellules à surveiller » + légende. **Conclusion/mesure inchangées.**
- **A2 — champ shadow `quasi_neutre`** au decision-log (`|score| < NEUTRAL_BAND=0.30`) : englobe coin-flip strict ET bande `≈`. Cuivre 7j (-0.22) était raté par `coin_flip` (seuil 0.05) → désormais `quasi_neutre=True`. **Le seuil `coin_flip`/`EPSILON_CARRY` (0.05) N'A PAS bougé** (il est couplé à la contradiction du carry-forward = seuil décisionnel, garde-fou).

### Enquêtes → reportées (pas de bug → reco)
- **B1 CAC « à l'envers »** : signe spread OAT-Bund **vérifié CORRECT** (élargissement → SHORT = risque France baissier, conforme). SHORT = contre-momentum pur (déjà flaggé `⇄`). Faire agir le `⇄` = **Lot 4b → reco À VALIDER THOMAS** (cap contre-momentum), non appliqué.
- **B2 Cuivre SHORT 7j/1m** : mono-critère COT + couverture 48%. Marquage déjà correct (`≈`+`⚠️`+`↯`). Abaisser couverture = **ticket C → reco**.
- **C1 S&P 7j / C2 Argent 1m / C3 échelles saturées** : pertinence par horizon + échelles. Aucun bug technique trouvé (fenêtres/séries correctes, saturation modérée ~1.1-1.3σ non absurde) → **ticket C → recos**, non appliqué.
- **DXY 118.9** (bonus News Trader) : **faux positif d'audit** — `dxy_trend_20j` câblé sur FRED DTWEXBGS (base 2006=100, ~120-130 normal), PAS le DXY classique. z-score = tendance 20j (pas niveau). Donnée + signe **sains** → aucune correction.
- **#8 Or SHORT « à contre-sens »** (backtest 1m 18.2 %) : enquête signe complète (`v3/audit/enquete-or-2026-06-05.md`). SHORT piloté à ~60 % par le critère **TIPS** (taux réels), signe `-1` **macro-canonique vérifié CORRECT** (taux réels hauts → coût d'opportunité or → baissier). **PAS un bug de signe.** Les 7 signes Or sont corrects. Le backtest « sent l'inversion » à tort : (a) il **ne teste pas le TIPS** (run sans `FRED_API_KEY` → poids 0, le 18 % = COT+price-only), (b) il est **news-blind** sur un or **+70 % en 2025 MALGRÉ des TIPS au plus haut** = **rupture de régime** (or-refuge/dédollarisation a découplé la relation or/taux-réels). Inverser le signe = overfit au régime 2025 (l'Or basculerait +12.6/+13.4 LONG). → **RÉGIME/CALIBRATION → reco À VALIDER THOMAS** (ticket C : rééquilibrer poids/pertinence TIPS vs géopol-refuge ; re-run backtest avec FRED). **Aucune correction de code.** Impact décision : NON (Or reste SHORT, `↯` signale déjà le piège).

### 2 micro-bugs du run live 18h04 (audit infra/affichage — zéro impact décision, mode shadow)
- **Bug 1 — nom de fichier du bulletin en UTC au lieu de Paris** (`scoring_analyste.py`). Le run 18h04 Paris produisait `bulletin-2026-06-05-16h.md` (heure UTC) alors que le **titre interne** (« 18h04 (Paris) ») et le **decision-log** (`...-1804.jsonl`) sont en heure Paris → fichier incohérent avec son contenu. **Cause racine** : `out_path` utilisait `now.astimezone(timezone.utc)` au lieu de `now` (Europe/Paris), la même source d'heure que le titre. **Fix** : construire le créneau du nom depuis `now` (Paris) → `bulletin-...-18h.md`. Le `bulletin_id` (stem) est une clé d'identité opaque (prix d'émission, tri, parsing) jamais réinterprétée comme une heure UTC → changement sûr. **Les bulletins déjà produits ne sont PAS renommés** (rétro-compat, historique préservé). +1 test (run 18h04 Paris → `-18h.md` + cohérence titre). Commit `e5f849b`.
- **Bug 2 — `mining_com` 403 revenu malgré l'UA Chrome**. **Diagnostic** : l'UA Chrome ÉTAIT bien propagé sur ce flux (`_fetch_rss` → `http_get_retry(headers=…)`), et `mining.com/feed/` répond **200** depuis cet environnement (les 3 jeux de headers testés passent). Le 403 n'est donc **PAS** « header non propagé » ni un **blocage durable** : c'est un **403 WAF (Cloudflare) intermittent** (challenge transitoire selon l'IP/géo des runners GitHub Actions). Le problème : le 403 était traité comme **non-retriable** → un 403 ponctuel devenait un échec définitif sur le cycle. **Fix mesuré, sans forçage** : (a) en-têtes navigateur enrichis sur les RSS (`config.BROWSER_HEADERS` = UA + `Accept` + `Accept-Language`, certains WAF inspectent `Accept*`) ; (b) nouveau paramètre `retry_status` sur `http_get_retry` + set `RETRY_STATUS_WITH_403` appliqué **au seul flux RSS** → un 403 transitoire est retenté (borné par `max_retries`), pas FRED/GNews/NewsAPI (défaut inchangé, zéro régression). Si le 403 **persiste** après retries → `source_monitor` signale le flux **muet** = dégradation propre déjà en place (zéro acharnement, zéro invention de news). +6 tests (3 http_retry, 2 ingestion RSS, +helpers). Commit séparé.

## 2026-06-03 (Session 3) — Audits trio, refonte page de rendu & comblement des données

**Contexte** : revue fondateur du bulletin frais + audits par le trio + le designer. Beaucoup de polissage, de fiabilisation et de **branchement de données** (le gros levier de qualité). 684 → **859 tests**, 0 régression.

### Bulletin — polissage post-audit trio (affichage/shadow, 0 impact conclusions)
- **Top 3 convictions = actifs distincts** ; **régime news** affiché sans contradiction de signe (`LONG [quant -0.08] 📰`) ; **bande quasi-neutre `≈`** (shadow, |note|<0.30) ; **mono-critère dominant** loggé (shadow). (`f19face`)
- **Fix mesure** : les cellules news (`📰 régime news` + `(brut LONG +X)`) n'étaient PAS mesurées → parsers corrigés. (`e2b3e18`)

### Page de rendu (`build_html`) — audit designer 6.5/10 → ~8.5
- **Favicon** (base64 — les entités HTML ne s'affichaient pas), **dark mode auto**, **onglet « 📊 Historique / Performance »** + persistance `measures-log.jsonl`, tooltips symboles, fusion en 1 table, ⚑ dégonflé. (`120df61`,`6c33b2f`,`9d8726b`,`1ec3158`)
- Bulletin : **décimales 4 sig figs**, section **« Audit de la veille 24h »** (réel %+VRAI/FAUX), **flux muets** reclassés (≠ pannes), ligne **Fraîcheur lisible**, légende d'échelle. (`0eb4bab`,`120df61`,`4f49f14`,`0c307b3`)

### Fiabilité mesure
- **Le système ne tourne plus le week-end** (garde jours-ouvrés cron) ; **échéance 24h sur jour ouvré** (vendredi→lundi) **+ jours fériés** NYSE/Euronext ; **verrou look-ahead C5 armé** (date du tick) ; **filet anti-mesure dégénérée** (prix figé = non-conclusive). (`875722c`,`f629fff`)
- **Dédup news inter-jours** verrouillée (event_id SHA-256 + event_date + Levenshtein 48h, rapidfuzz). (`e64a7b5`)

### Données comblées (gros gain de couverture)
- Récupérés via fix composite/mapping + source VIX unifiée : café météo (p11), VIX régime S&P (p8), HF cacao… (`7bbe128`)
- **Caixin PMI** via extraction news (`f0a9790`) ; **DXY**/**taux 10Y delta 5j**/**spread OAT-Bund** via FRED (`45dd253`) ; **Shiller CAPE** via scraper multpl défensif (`38fdded`) ; **différentiel taux 2Y US-DE** (EUR/USD, **poids 12**) via FRED+ECB Data Portal (`2197e1f`).
- ⚠️ Signe/échelle de ces nouveaux critères = **hypothèses à valider en shadow** (comme le proxy breadth).

## 2026-06-02 (Session 2) — Gate intelligent (anti-biais de survie) + audits reproductibles

**Contexte** : revue des 6 points fondateur + audits par le trio (Analyst/Spéculateur/NewsTrader). La P1 « calibration coverage » (12 actifs muets en INSUFFISANT) est attaquée non par un seuil arbitraire mais par un **gate à priorités**.

### Gate de suffisance — nouvelle logique à priorités (`scoring_analyste.py`)
- **Hystérésis de maintien** (carry-forward, horizon-aware) : `0.25 ≤ cov < 0.40` + dernière direction valide non contredite + non périmée → **⏸ maintenu** au lieu de 🚫 (`COVERAGE_FLOOR=0.25`, `CARRY_MAX_AGE_H={24h:24,7j:48,1m:24}`). Source = decision-log scanné. Smoke réel : **9 cellules récupérées**. (`b868b6d`)
- **Régime news-driven** (cuivre/cacao/café) : couverture quant insuffisante + biais news net (`ratio_news>0.5`) → **📰 direction news** au lieu de 🚫. Helper `compute_news_bias` factorisé. (`2b209d8`)
- Ordre final : quant ≥40% → ⏸ carry → 📰 news → 🚫. Cellules ⏸/📰 portent une vraie direction → **mesurées** (tags `is_carry`/`is_news_regime` pour audit hit-rate futur).

### Bulletins & monitoring
- **3 briefings/jour distincts** `bulletin-{date}-{HH}h.md` (fin du biais de survie : matin/midi/soir s'écrasaient) ; prix d'émission re-clés par créneau ; chacun mesuré. (`7df13ce`)
- **Monitoring sources 3 états** : OK / ⚠️ partiel (R/N) / ❌ — fin des faux ❌ GNews quand 13/14 requêtes passent. (`8b172c2`)
- Note + **confiance%** au lieu de force ●/○, + légende d'échelle. (`040f687`, `0c307b3`)

### Bug & audits
- **🐛 Bug VIX** : `vix_regime` renvoyait +1.0 (plateau 14-25) au lieu du triangle des fiches → faux signal **haussier** systémique sur S&P/Nasdaq/CAC dès que VIX∈[14,25]. Corrigé en triangle (VIX 23.9 : +1.0→-0.36). (`5719cde`)
- **Audit S&P reproductible** (`v3/audit/sp500-explication-reproductible.md`) : la formule `signe×poids×pertinence×norm` reconstitue les scores au centième. Drivers réels = taux réels TIPS + breadth (pas le VIX, absent du run). A corrigé une narration initiale erronée (crédit HY mal signé) ET un angle mort de l'audit lui-même.
- Vérifié : `compute_coverage` pondère déjà par poids (ticket E, rien à faire) ; horodatage = faux problème.
- **684 tests**, 0 régression (8 échecs pré-existants env-only).
- **Différé → C** : calibrer `COVERAGE_MIN` (0.40) sur hit-rate réel — rouvrir ~2026-06-23 quand les tags `is_carry`/`is_news_regime` auront accumulé assez de mesures.

### Polissage post-audit du bulletin (trio → consensus en 3 rounds)
Audit forme+fond du bulletin par le trio : Fond **6/10** (méthode 8, mais données qui la nourrissent 4), Forme **6/10** (transparence forte, mais dense/bruitée). Plan de 6 actions re-priorisé par « impact/effort », exécuté en autopilote :
- **🔴 #1 Bug normalisation** : `normalise()` jetait en silence les critères `composite`/`mapping_non_monotone` (« type inconnu ») → critères à fort poids récupérés : café météo (+11), S&P VIX régime (+8), CAC V2X (+8), Nasdaq VXN (+7), cacao HF (+7). Bug côté consommateur seul (émission déjà correcte). (`7bbe128`)
- **🔴 #2 Incohérence VIX** : `vix_regime` lisait 23.6 (Twelve) vs 14.95 (CBOE) pour le même VIX → unifié sur la source CBOE fraîche (14.95 → +0.975 régime sain). (`7bbe128`)
- **🟡 #6 News** : dédup des news identiques au sein d'un actif (doublon SoftBank CAC) + troncature propre sur frontière de phrase (140→240). (`4e737e0`)
- **🟢 #4/#5 Forme** : bloc **🎯 Top 3 convictions** en tête ; **fusion des 2 tables** de synthèse en une ; **⚑ régime extrême** annoncé 1× au lieu de 12× ; « à surveiller » resserrée (27→6-7 lignes, alertes directionnelles seules). (`1ec3158`)
- **⏸ Différé → #3** : combler les vraies données absentes (Caixin PMI cuivre p.12, diff. taux EUR/USD p.12, etc.) = chantier sources (nouvelles intégrations), non autopilotable.
- **716 tests** verts, 0 régression (8 échecs pré-existants env-only).

## 2026-06-01 (soir) — Observabilité news + optimisation requêtes (10/10)

- **Bilan des news** : bloc dans le bulletin marquant les calls portés par les news qui ont marché/raté (juger le jugement DeepSeek).
- **source_monitor** : santé des flux par cycle (appelé/OK/échec/muet + reçus vs gardés + raison) → `v3/data/source-health.md` + bloc « Santé des sources » dans le briefing + kit d'analyse. Fix 4 flux muets (gnews_cac40 FR, gnews_wheat query, investing_stocks doublon ; mining_com 403 visible).
- **Optimisation requêtes news (audit 3 experts, 3 rounds → 10/10 côté news)** : comble Nasdaq (Nvidia/IA/semi) + VIX (volatilité + causes amont war/escalation), retire DAX, supprime Q3 redondante, dégroupe Or/Argent/Cuivre, sépare Fed/BCE, S&P earnings-driver, enrichit CB-gold/solaire/EUDR/WASDE/café-gel/blé-GASC/CAC-SBF120. 14 requêtes, 22 flux. Plafond news 9,5-10 (reste = pipeline data : CFTC COT, ETF, CBOE, GASC).
- **Kit d'analyse du matin** : `python3 v3/scripts/analyse_complete.py` (matrice, bilan news, mesure, Phase 2 T1/T2, biais, flips, santé sources, backtest).
- **Backtest quant v1** : `v3/backtest/` — moteur historique no-look-ahead ; v1 (price-only, 4 actifs × 24h) = NO-GO (50.8% OOS, partiel). v2 (COT+FRED+horizons) = prochain chantier.

## 2026-06-01 — Fiabilisation run quotidien + plan horizon

**Contexte** : répétition des cycles quotidiens pour débusquer les défauts cachés, audit par les 3 experts, correction en autopilote.

### Correctifs pipeline
- **Routing IA-first réparé** : le parser ignorait les impacts DeepSeek → la synthèse directionnelle (LONG/SHORT par actif) pilote désormais les critères news.
- **Prix d'émission réparés** : la boucle prédiction→mesure (Journaliste) est fermée — conclusions VRAI/FAUX réelles.
- **Indices via ETF Twelve Data** : `^GSPC→SPY`, `^IXIC→QQQ`, `^FCHI→FCHI`, `^VIX→VIXY`, etc. (yfinance bloqué sur les runners GitHub). Débloque CAC/S&P/Nasdaq (0 tie-break).
- **Rate-limiter Twelve** : `_acquire_rate_limit` attend un slot au lieu de rejeter (→ fallback yfinance bloqué) ; `TWELVE_RPM=55` (plan Grow). Cause racine des indices n/a en CI.
- **PROBA_SCALE 10→15** (anti-saturation Brier), propagation `reliability`, garde chevauchement 7j/1m.

### Audits (3 experts : Analyst / News Trader / Spéculateur)
- Audit des runs dans l'ordre d'édition (`v3/audit/chaine-*.md`).
- **Audit de cohérence** (`coherence-3-experts.md`) : 2 faux positifs écartés sur preuve (signe géopol déjà câblé `ia_synthese` ; events 2025 filtrés par cutoff lookback).
- Trio formalisé comme panel d'audit officiel (`v3/audit/README.md`).

### Plan horizon (validé Thomas + 3 experts)
- **Constat** : DeepSeek produit 1 direction/actif **horizon-agnostique** ; sur cellules faibles/longues la news domine voire inverse le quant (Or 24h 43%, VIX 1m 480%).
- **Décision** : PAS de decay global (casserait l'OPEC). Recalibrage `pertinence` (or/petrole/vix) + cap anti-inversion α=0.8 (override si high+confirmed) + `ratio_news`/drapeau 📰.
- **Preuve** : Or 24h +0.17→−1.33 SHORT, VIX 1m +0.25→−0.55 SHORT, Pétrole/S&P inchangés. 360 tests.

### Infra
- `schedule` GitHub diagnostiqué **retardé de 1-3h** (6 runs prouvés les 30-31/05), pas une panne. Redondance cron ×3 (`:12/:27/:42`) + garde-fou anti-doublon. Permissions read/write activées.
- **À faire (Phase 2)** : tracer `event_id`/date + flag nature news (structurel/ponctuel/déjà-price) — cause racine du biais news.
