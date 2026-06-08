# Audit SPEC « 5 rapports » — point de vue News Trader senior (desk)

> Auditeur : **News Trader senior** (15 ans desk macro/commodities, exécution turbos Bourse Direct).
> Objet : `v3/docs/reco/spec-refonte-5-rapports.md` + `-RESOLUTIONS.md`.
> Angle : **réalisme desk** — horaires marché, mesure ouverture→clôture, actionnabilité des suivis, contenu du bilan soir.
> Date : 2026-06-08. Branche `claude/elegant-ramanujan-OIKms`. Mode shadow.

---

## NOTE GLOBALE : **7,5 / 10**

La spec est **bien pensée pour un trend-follower** : 1 décision/jour, mesure ouverture→clôture, suivis courts, bilan soir, Manager qui propose sans appliquer. Le découpage colle à une vraie journée de desk. Mais **5 erreurs de réalisme horaire/marché** la font perdre 2,5 points — dont 2 qui rendent un rapport partiellement FAUX (mauvaise heure de clôture US, fenêtre DST désynchronisée, et surtout le **20h UTC capté trop tôt**).

**Verdict desk : GO sur le design, NO-GO sur les horaires tels qu'écrits.** À corriger avant implémentation.

---

## CE QUI EST JUSTE (defendable desk)

1. **Découpage 7h / 12h / 18h / 22h / dim** = vraie journée de trader turbos. 7h pour préparer avant l'open EU, 12h check mi-séance EU, 18h check post-clôture EU + US lancé, 22h bilan post-clôture US. Le dimanche bilan-semaine = exactement quand un trader prépare sa semaine. **Rien à redire.**
2. **Mesure ouverture→clôture** plutôt que prix-7h→prix-J+1 = **le bon call de tendance**. Le prix à 7h (marchés EU/US fermés) n'est pas une référence tradable. Mesurer le mouvement réel de la séance est exactement ce qu'un desk regarde. **Excellent.**
3. **« La journée boursière EST le 24h »** (§2.4) = juste. Inutile d'attendre J+1, la nuit les marchés sont fermés.
4. **CAC clôturé à 17h30, pas 22h** (§2.6, CA-B2) = correct, le close officiel Euronext est 17h30. Bien vu de ne pas prendre le prix de 22h sur un marché fermé.
5. **Gap d'ouverture = pas de traitement spécial** (§2.6) = réaliste. Le gap fait partie de la séance.
6. **Suivi = pas un nouveau bulletin, max 50 lignes** = bon réflexe. Un trader ne relit pas une matrice 12×3 à midi, il veut le statut de ses positions.
7. **Suggestion « Sortir » = drapeau jamais ordre** (Q4 résolu) = cohérent avec un système d'aide à la décision.

---

## LES MANQUES À CORRIGER POUR 10/10

### 🔴 M1 — Le run 20h UTC ne capte PAS la clôture US (le plus grave)

**Erreur de fond.** La spec dit « Bilan 22h, après fermeture des marchés US » et place le cron à **`20h UTC`**.

- En **été (CEST = UTC+2)** : 20h UTC = **22h Paris**. NYSE clôture 16h ET (EDT) = 22h Paris. ✅ OK de justesse — mais le close officiel n'est *tamponné/disponible* via les data feeds qu'avec quelques minutes de latence. Stamper **à 22h00 pile** = risque de rater le print de clôture (16h00:00 ET) qui arrive avec retard. Un desk attend **22h10–22h15** pour le close US propre.
- En **hiver (CET = UTC+1)** : 20h UTC = **21h Paris**. Le NYSE est **encore ouvert** (clôture à 22h Paris en hiver). **Le bilan « clôture US » serait pris 1h AVANT la clôture.** ⛔ **Rapport faux la moitié de l'année.**

La spec mentionne bien (§5.1 note) « 20h UTC = 21h CET » mais **ne tire pas la conclusion** : à 21h Paris en hiver, le S&P/Nasdaq tournent encore. Le bilan capterait un prix de mi-séance, pas la clôture.

**Correction 10/10** : le cron du bilan doit être **ancré sur l'heure Paris réelle (Europe/Paris), pas sur un UTC fixe** — exactement la logique déjà adoptée ailleurs dans le projet (garde heure-Paris dans le script, cf. context cron horaire `0 * * * *` + garde DST). Cible : **stamp clôture à 22h15 Paris** (≈ 16h15 ET, close US digéré), été comme hiver. Le run 20h UTC fixe est à proscrire.

### 🔴 M2 — Fenêtre DST désynchronisée US/EU (2× ~2 semaines/an)

Paris et New York ne basculent **pas** le même jour : les US passent à l'heure d'été ~2 semaines avant l'EU (mi-mars) et en sortent ~1 semaine après (début nov). Pendant ces fenêtres, le décalage Paris–NY n'est **pas 6h mais 5h**.

- Conséquence : pendant ~3 semaines/an, **16h ET = 21h Paris** (pas 22h). Un bilan ancré « 22h Paris » prendrait la clôture US **1h trop tard** (acceptable, marché fermé) — mais un suivi/clôture ancré sur un offset 6h codé en dur serait faux.

**Correction 10/10** : ne **jamais** coder un offset Paris↔NY en dur. Convertir via TZ `America/New_York` → `Europe/Paris` (les deux DB tz gèrent la désync). Sinon 3 semaines/an de mesures décalées. À ajouter explicitement comme garde-fou (la spec ne le mentionne nulle part).

### 🟠 M3 — Le prix de référence « ouverture » des Continus (08h) n'est pas une vraie ouverture

§2.2 met EUR/USD, Or, Argent, Cuivre, Pétrole, Blé, Cacao, Café en groupe « Continus, ouverture 08h Paris ». **Faux pour un desk** :

- **EUR/USD, Or, Argent** = FX/métaux spot **24h/24** (ouverture hebdo dimanche 23h Paris). Il n'y a **pas d'ouverture quotidienne** — 08h est arbitraire. Acceptable comme convention (la spec le dit), mais alors la « mesure ouverture→clôture 24h » devient « prix 08h → prix 22h », ce qui **coupe une séance FX en plein milieu** et ignore la session asiatique (la nuit où l'Or bouge le plus sur les news Asie).
- **Pétrole, Blé, Cacao, Café** = **futures avec des horaires CME/ICE précis** : le Brent (ICE) ouvre ~01h Paris, le WTI (CME Globex) ~00h, le blé CBOT a une session de jour qui ouvre **15h30 Paris** (09h30 Chicago) — **pas 08h**. Le café/cacao (ICE US) ouvrent ~10h-11h Paris. **08h ne correspond à AUCUN de ces marchés.**

**Impact tendance** : faible si on reste cohérent (même 08h tous les jours → la tendance jour-sur-jour reste mesurable). Mais le terme « ouverture » est trompeur et la fenêtre 08h→22h rate la partie de séance la plus active de certains commodities. **Pour un call de tendance 24h, mieux vaudrait mesurer close→close (J-1 22h → J 22h) sur les continus**, pas 08h→22h.

**Correction 10/10** : (a) renommer « ouverture » → « prix de référence conventionnel 08h » pour éviter de tromper le lecteur, OU mieux (b) pour les vrais 24h (FX/métaux), mesurer **clôture veille → clôture jour** (close-to-close), qui est la convention desk pour la perf journalière d'un actif continu. Au minimum, documenter que 08h est arbitraire et assumer le biais.

### 🟠 M4 — Le suivi 18h prend la clôture EU mais rate la vraie info US du soir

§3.3 / Q5 : à 18h Paris, le S&P/Nasdaq sont ouverts depuis **15h30** (2h30 de séance). Le suivi 18h donne « prix mid-séance US ». **OK**, mais un desh à 18h veut surtout savoir : **l'open US a-t-il confirmé ou infirmé le call du matin ?** Le tableau actuel (statut ✅/⚠️ vs ouverture) le donne mécaniquement, mais **il manque le signal « retournement intraday »** : un actif US qui a ouvert dans le sens du call puis s'est retourné après l'open US (15h30) est l'info clé de 18h. La spec ne capture que le statut instantané, pas la **dynamique depuis l'open US**.

**Correction 10/10** : pour les actifs US dans R3, ajouter une colonne ou un flag **« depuis open US »** (signe du mouvement 15h30→18h), distinct du statut vs ouverture de référence. C'est ça que le trader regarde à 18h. Sinon R3 ≈ R2 décalé de 6h, faible valeur ajoutée.

### 🟠 M5 — Bilan 22h : il manque ce qu'un trader veut VOIR le soir

§3.4 donne le tableau VRAI/FAUX + win rate + news. Bon socle. Mais pour un desk, **3 manques** :

1. **L'amplitude du move n'est pas montrée** (delta% est là, OK) mais **le « call était juste mais marché plat »** (NC) vs **« call faux et marché a violemment bougé contre »** ne sont pas distingués visuellement. Un FAUX sur gros move = vraie erreur de tendance à creuser ; un NC = non-event. Le bilan devrait **trier/flagger les FAUX à forte amplitude** (les vraies leçons). *(Note : mesurer l'amplitude pour TRIER les erreurs est OK — ce n'est pas du P&L, c'est de la lecture de tendance. Conforme founder-pref.)*
2. **Aucune lecture de cohérence inter-horizons** : si le call 24h sort FAUX mais que le 7j/1m du même actif est dans le même sens, le trader veut savoir si c'est un faux signal court terme ou un vrai retournement. Le bilan 22h ne note que le 24h et n'évoque pas les horizons longs en cours.
3. **Pas de « ce qui attend demain »** : un bilan de desk se termine toujours par les **catalyseurs du lendemain** (NFP, CPI, FOMC, BCE, OPEP, inventaires EIA, WASDE). Le système ingère déjà un calendrier news — le bilan 22h devrait lister **les 2-3 events macro de J+1** qui peuvent invalider les calls. C'est l'info n°1 qu'un trader veut le soir pour décider s'il garde ou allège overnight.

**Correction 10/10** : ajouter au R4 (a) un flag **« FAUX à forte amplitude »** (erreurs prioritaires), (b) une ligne **cohérence avec 7j/1m en cours**, (c) un bloc **« Catalyseurs J+1 »** (2-3 events agenda). Le (c) est le plus important — sans lui, le bilan soir est incomplet pour un desk.

---

## MANQUES SECONDAIRES (n'empêchent pas un rapport d'être utile)

- **M6 — Heure d'ouverture US = 15h30, mais close auction 17h ET ≠ open.** OK pour la référence, RAS, mais le delta de l'open US a 5 min de bruit (15h30-15h35) — le `OPEN_STAMP_DELAY_MIN=5` est bien vu, garder.
- **M7 — Continus à 22h vs sessions futures qui durent après 22h** (WTI/Brent tradent jusqu'à 23h+ Paris). Le « close 22h » des commodities est arbitraire comme le 08h. Cohérent si stable, mais à documenter.
- **M8 — Q6 (news qui ont compté) = croisement temporel** : un desk sait qu'une news de 14h n'explique pas forcément un move de 16h. Le croisement « news du créneau de l'actif » est faible (corrélation ≠ causalité) — acceptable en shadow, mais ne pas survendre ces news comme « déterminantes ».
- **M9 — VIX via VIXY (ETF)** : VIXY ouvre 15h30 (NYSE) mais le VIX *index* est calculé dès l'open SPX. Mesurer le VIX via un ETF qui ouvre à 15h30 rate la session EU où le VIX réagit déjà aux futures US. Mineur (déjà un proxy connu), mais le « VIX 24h » sera tronqué à la session US.

---

## SYNTHÈSE — 10 lignes desk

1. Le design (1 décision/jour, ouverture→clôture, suivis courts, bilan soir, Manager) est **bon pour du trend-following**. Solide.
2. Le découpage horaire 7h/12h/18h/22h/dim **colle à une vraie journée de desk**. Rien à redire sur la cadence.
3. **GROS PROBLÈME** : le cron bilan à **20h UTC fixe** = 21h Paris en hiver → **clôture US ratée d'1h** (marché encore ouvert). Rapport faux 5 mois/an.
4. **Corriger** : ancrer le bilan sur **22h15 Europe/Paris** (heure réelle), jamais sur un UTC fixe. Capter le close US digéré.
5. **DST désynchro US/EU** (~3 sem/an, décalage 5h au lieu de 6h) : ne jamais coder l'offset Paris↔NY en dur. Convertir via fuseaux.
6. Les « ouvertures 08h » des continus (FX/métaux/futures) **ne sont pas de vraies ouvertures** — convention arbitraire à assumer, ou passer en close-to-close.
7. Le suivi 18h doit montrer **la dynamique depuis l'open US** (retournement intraday), pas juste le statut vs ouverture.
8. Le bilan 22h manque **les catalyseurs de demain** (CPI/FOMC/OPEP/EIA) — l'info n°1 d'un desk le soir.
9. Ajouter au bilan : flag **FAUX à forte amplitude** (vraies erreurs) + cohérence avec 7j/1m en cours.
10. Mesurer l'amplitude pour **trier les erreurs** ≠ mesurer le P&L. Conforme founder-pref (win rate only).

**NOTE : 7,5 / 10.**

## TOP 3 CORRECTIONS pour 10/10

1. **(M1+M2) Ancrer le bilan sur 22h15 Europe/Paris réel, pas 20h UTC fixe** — sinon clôture US ratée tout l'hiver + décalages DST. **Bloquant.**
2. **(M5c) Ajouter un bloc « Catalyseurs J+1 »** au bilan 22h (2-3 events agenda macro) — c'est ce qu'un trader veut voir le soir pour décider overnight.
3. **(M3) Assumer/renommer les « ouvertures 08h »** des continus (FX/métaux/futures n'ouvrent pas à 08h) — ou passer en close-to-close pour les vrais 24h.
