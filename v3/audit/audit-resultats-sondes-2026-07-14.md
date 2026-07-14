# Audit des résultats liés aux sondes — 2026-07-14

_Audit sur pièces (decision-log, sortie-timing-log, bilans, CHANGELOG, code). Aucun signal modifié._

## 1. Ce que sont les sondes (rappel)

Trois « thermomètres » posés le 11/07 (GO fondateur, panel « tendance mûre ») pour chiffrer
les risques identifiés par l'autopsie de la semaine 06-10/07. **Shadow pur** : elles observent,
elles ne changent rien aux signaux. Verdict uniquement à **N ≥ 15** observations par sonde.

| Sonde | Question posée | Champs | Où |
|---|---|---|---|
| 1 — Confirmation post-flip | Un flip vaut-il mieux joué le jour J ou une fois confirmé le lendemain ? | `shadow_flip_j0` / `shadow_flip_conf` | decision-log |
| 2 — Catalyseur épuisé | Quand le 3j saturé est seul contre news+7j+20j, qui a raison ? | `shadow_cat_epuise` / `shadow_sens_fond` | decision-log |
| 3 — KO virtuel | Le pari a-t-il touché -3 % adverse AVANT +1 % favorable (barrière turbo) ? Segmenté mûrs ⌛ vs frais | `ko_virtuel` / `pari_mur` | sortie-timing-log |

## 2. Résultats au 14/07 (constats factuels)

- **Les sondes ne tournent en production que depuis le 13/07** (livrées samedi 11/07). Deux
  séances de données : aucun verdict possible, tout est « en chauffe ».
- **Sonde 3** : 3 paris mesurés le 13/07 (Blé LONG, CAC 40 SHORT, Coton LONG) →
  `ko_virtuel = False` sur les 3, `pari_mur = False` sur les 3. **N = 3/15**, segment « mûr ⌛ » à
  **N = 0**. La ligne 🧨 du bilan du soir ne s'affiche que sur un KO avéré → absence normale le 13/07.
  Les 42 lignes antérieures du sortie-timing-log n'ont pas le champ (pré-sonde, attendu).
- **Sonde 2** : zéro divergence live/fond détectée (`shadow_cat_epuise` = False partout,
  `shadow_sens_fond` = None). **N = 0/15**. Rare par construction, pas un défaut.
- **Sonde 1** : `shadow_flip_j0` = 6 le 13/07, 0 le 14/07, `shadow_flip_conf` = 0 partout.
  **Données 13-14/07 CONTAMINÉES** par le bug du badge ⇌ (voir §3).
- **Lecture hebdo** : câblée dans `run_weekly.py` (compteurs + « en chauffe (N=x/15) »).
  Le bilan S28 (semaine 06-10/07) est antérieur aux sondes → première lecture publique au **bilan S29**.

## 3. Le bug trouvé (et corrigé) — badge ⇌

- Depuis ~20/06 (rendu S9), le badge de flip `⇌` préfixait la conclusion dans la Synthèse →
  le parseur de la veille ratait TOUTE ligne d'actif ayant flippé (6/15 actifs parsés le 13/07).
- Conséquences : `is_flip` aveugle le lendemain d'un flip pendant ~3 semaines (stats
  flips/continuations sous-comptées) et **sonde 1 structurellement incapable de voir un
  « flip confirmé »**.
- Fix `9bc8a18` (strip du span avant parsing) mergé le **14/07 à 15:46 UTC**, soit APRÈS le
  bulletin 7h23 du 14/07 (commit log 05:29 UTC) → le decision-log du 14/07 est encore pré-fix
  (`is_flip: None` sur Argent, pourtant flip confirmé au rejeu).
- Rejoué sur bulletins réels : 15/15 actifs parsés, Argent 14/07 correctement « flip confirmé ».
  Tests-verrous posés.
- **Première journée PROPRE pour la sonde 1 = 15/07.** Les valeurs `shadow_flip_j0` des
  13-14/07 sont à traiter comme suspectes dans tout comptage.

## 4. Contexte — les résultats que les sondes doivent expliquer (autopsie 06-10/07, N=56)

- Top 3 en métrique turbo : **3/12** ; direction à l'échéance : **4/7** ; **12 FAUX évités**
  en 3 jours par les écartements ↯ (les garde-fous sont les héros de la semaine).
- Intuition « plus c'est monté, plus ça corrige » : **non supportée en direction**. Vrais risques :
  flips à contretemps (1/6 — café flip SHORT le 09/07 pile sur +12,3 %) et asymétrie d'ampleur
  (cacao 10/07 : conviction record +12.31, max favorable +0,01 %, max adverse **-9,28 %** =
  barrière turbo). Angle mort structurel : penchant 3j plafonné à ±1, l'ampleur parcourue est effacée.
- Signes positifs hors sondes : stocks blé USDA vivant (920M t, penchant -0.537) ; **zéro
  « suivi-interrompu » depuis le 10/07** (fix échéance sucre/USD-JPY effectif).

## 5. Sondes plus anciennes (pour mémoire, toutes closes ou en veille)

- **Sonde 8h** (futures ES/NQ/VX via Twelve, 10/06) : verdict NÉGATIF (Twelve free ne les sert
  pas) → échafaudage retiré le 20/06. Clos. Rapport : `v3/audit/symbol-validation-8h.md`.
- **Sonde 23/06** (US overnight, clé Grow réelle) : Twelve ne sert AUCUN US overnight →
  décision OANDA (`fetch_us_index.py`). Reste dépendant du secret `OANDA_API_TOKEN`.
- **Sonde de couverture données** (`probe_data_coverage.py` + workflow `probe-data`, 22/06) :
  à lancer manuellement ; aucun rapport commité à ce jour.

## 6. Recommandations

1. **Ne rien conclure avant N ≥ 15 par sonde** (~2-3 semaines de séances au rythme actuel).
2. **Sonde 1** : démarrer le comptage propre au 15/07 ; exclure (ou flagger) les 13-14/07 de
   toute lecture hebdo.
3. **Vérifier au bulletin du 15/07** : 15/15 actifs parsés à la veille, `is_flip` non-None sur
   les actifs concernés, premier `shadow_flip_conf` plausible.
4. **Sonde 3** : le segment « mûr ⌛ » (cœur de la question fondateur) est à N=0 — c'est LE
   compteur à surveiller au fil des bilans hebdo.
5. Aucune règle à coder à chaud : doctrine « mesurer avant d'agir » respectée, zéro impact signal
   vérifié sur les logs.

---

**Handoff** : lecture suivante = bilan hebdo S29 (compteurs sondes) + vérification bulletin 15/07
(point 3). Aucune action code requise par cet audit (le fix ⇌ est déjà mergé sur main).
