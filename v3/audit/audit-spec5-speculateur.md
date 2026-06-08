# Audit Spéculateur — Spec « 5 rapports/jour »

> Expert : **Spéculateur trend-follower** (« est-ce utilisable pour mettre du cash ? »).
> Angle : utilité réelle / exploitabilité, PAS rigueur stat (Analyst) ni défendabilité desk (News Trader).
> Cibles : `spec-refonte-5-rapports.md` + `-RESOLUTIONS.md`. Branche `claude/elegant-ramanujan-OIKms`.
> Date : 2026-06-08.

## Note globale : 7,5 / 10

Verdict : **GO**. Le flux décision→suivi→bilan→bilan-semaine est une vraie progression
vs « 3 bulletins identiques ». Mais 4 trous m'empêcheraient de m'en servir à plein pour
décider d'engager du cash. Détaillés ci-dessous, avec correctifs pour 10/10.

---

## 1. Ce que ça m'apporte vs avant (3 bulletins identiques)

PROGRÈS RÉELS (je le dis franchement) :

- **Fin du leurre des 3 bulletins/jour.** Avant, 12h et 18h re-scoraient et me sortaient
  une matrice qui pouvait flipper sur du bruit intraday. Maintenant : **1 décision/jour (7h)**,
  les 12h/18h ne sont QUE du suivi de cette décision. C'est exactement comme je trade :
  je prends ma position le matin, je la surveille, je ne me re-pose pas la question toutes les 4h.
- **Prix de référence = vraie ouverture marché** (et pas le prix de 7h marché fermé).
  Ça c'est du concret : mon turbo, je l'achète à l'ouverture, pas à 7h. Mesurer
  ouverture→clôture colle à ma réalité d'exécution. Gros point.
- **Bilan du soir qui clôt le 24h le jour même** (22h), au lieu d'attendre J+1. Je sais
  le soir si mon call du matin était bon. Boucle courte = j'apprends vite.
- **Win rate only, zéro P&L** : respecté partout (CA-B5, CA-W5). C'est ce que je veux.

CONCLUSION : oui, ça m'aide à mieux trader. Le squelette est bon.

## 2. Le suivi intraday (R2/R3) — me dit-il si je gagne/perds + quand sortir ?

CLAIR pour « est-ce que je gagne » : OUI. La colonne `Statut` (✅ gagne / ⚠️ perd /
— neutre) avec Delta% vs ouverture me dit en un coup d'œil l'état de chaque position.
Tableau court, 2 min de lecture (CA-S5 : max 50 lignes). Bien calibré pour le rythme
d'un trader qui regarde son téléphone à midi.

MAIS — 3 manques qui me gênent pour DÉCIDER de sortir :

**M-A (important) — Delta% vs ouverture seul ne me dit pas si je dois sortir.**
Le signal de sortie d'un trend-follower n'est pas « je suis à −0,3% » dans l'absolu.
C'est : **est-ce que la TENDANCE se retourne ?** Or le suivi ne me donne aucun
contexte de tendance : pas de plus-haut/plus-bas du jour, pas de « le mouvement
s'essouffle vs s'accélère », pas de comparaison au delta du suivi précédent (12h→18h).
La spec dit même explicitement (R3) : « Delta% toujours vs l'ouverture, pas vs le prix
de 12h ». Donc entre midi et 18h je ne vois PAS si ça empire ou se redresse. Pour un
trend-follower c'est le signal le plus utile, et il est absent.

**M-B (important) — La suggestion de sortie est sous-spécifiée et timide.**
Resolutions Q4 = « drapeau-suggestion seulement, jamais un ordre » : bon principe
(le système ne place pas d'ordre, je garde la main, d'accord). MAIS le seuil reste
flou : spec §3.2 propose « perte > seuil_actif × 0.5 », Q4 dit « au-delà du seuil
d'amplitude de l'actif » — deux formulations, aucun chiffre arrêté. Résultat : soit la
suggestion `sortie à envisager` ne se déclenche presque jamais (seuil 24h trop haut
en intraday), soit elle se déclenche mécaniquement sur du bruit de midi. Tel quel,
je ne ferais pas confiance à cette colonne — donc je l'ignorerais.

**M-C (moyen) — Aucune notion de « stop invalidé ».** Quand je mets du cash sur un
turbo, ce qui me sort, c'est un niveau d'invalidation (la tendance est cassée), pas un
% arbitraire. Le suivi pourrait au minimum flaguer « le call du matin est-il toujours
cohérent avec les critères, ou un critère majeur a-t-il flippé depuis 7h ? ».
Actuellement R2/R3 ne re-regardent AUCUN critère (Q9 : pas de scoring à 12h/18h).
Je comprends le choix coût/simplicité, mais ça veut dire que le suivi est purement
« prix », aveugle au fait qu'une news de 11h ait pu invalider la thèse. Le bloc
« News à impact depuis 7h » compense partiellement, mais en texte libre, pas relié
à un statut « thèse encore valide / thèse fragilisée » par actif.

VERDICT section 2 : le suivi me dit si je gagne (bien), mais PAS clairement quand
sortir (le cœur de mon métier). C'est le principal manque utilité.

## 3. Le Manager (R5) — vraie boucle d'amélioration ou cosmétique ?

PLUTÔT VRAIE BOUCLE, et c'est ce qui me plaît le plus dans la refonte. Les propositions
ont un format actionnable et concret (§4.5) : Type / Actif / Critère exact / Constat
chiffré / Proposition précise (« réduire poids `taux_reel_us` de 12 à 8 pour Or 7j ») /
Risque / validation Thomas. Ça c'est une proposition que je peux juger et appliquer, pas
du blabla. Le garde-fou « PROPOSE, Thomas valide, jamais silencieux » (CA-W4 : git diff
config = vide) est exactement ce qu'il faut. **Pas cosmétique.**

MAIS — 2 réserves d'exploitabilité :

**M-D (important) — Boucle trop lente pour être utile au début, et seuils d'activation
trop hauts.** Une « cellule faible » exige win rate < 50% sur **N_eff ≥ 5** (§4.3).
Avec 1 décision/jour, N_eff = 5 ≈ **une semaine entière** par cellule, et le warm-up
officiel c'est 15 (≈ 3 semaines). Donc les **premières semaines, le Manager n'aura
quasi rien à proposer** (tout en warm-up → « observations sans proposition »). Pendant
la phase où j'ai le plus besoin d'ajuster (le rodage), le Manager est muet. Ce n'est pas
faux statistiquement (Analyst validera), mais côté utilité : si pendant 1 mois le bilan
dimanche ne me sort que des « observations sans proposition », je vais arrêter de le lire.

**M-E (moyen) — Le Manager détecte les critères/cellules faibles, mais ne me dit pas
ce qui MARCHE.** Pour mettre du cash, j'ai autant besoin de savoir « sur quoi le système
est fiable » (mes cellules à win rate élevé, mes critères porteurs) que « ce qui foire ».
La spec §4 est 100% orientée détection de faiblesse (cellule faible, critère faible,
sous-performant). Aucune section « cellules fortes / critères porteurs ». Un trend-follower
veut concentrer le cash là où l'edge est prouvé — le Manager devrait me le pointer.

## 4. Win rate only — suffisant pour passer en réel un jour ?

D'abord, la doctrine est claire et je la respecte : Thomas se fiche du P&L, seule la
DIRECTION compte. Préférence fondateur répétée. Donc « mesurer combien ça rapporte »
= hors-sujet, je ne le reproposerai pas.

MAIS pour décider de passer en RÉEL (engager du vrai cash), le win rate brut a deux
angles morts qui, eux, restent dans le périmètre direction et sont exploitables :

**M-F (important) — Win rate global par cellule, mais pas conditionné à la CONVICTION.**
Pour mettre du cash, ce qui me décide ce n'est pas « le système est juste à 68% en
moyenne », c'est « **quand le système est en forte conviction (signal large, |score|
élevé, multi-critères, pas de drapeau ◧/⇆), quel est son win rate ?** ». Un système à
60% global mais 80% sur ses calls à forte conviction est tradable (je ne joue que les
forts). Un système à 60% partout est inutilisable. La spec mesure tout uniformément.
Le decision-log a déjà les drapeaux (quasi_neutre, mono-critère ◧, coin_flip) — il
manque juste un **win rate segmenté par niveau de conviction** dans le bilan. C'est LE
chiffre qui me ferait passer en réel, et il n'est pas là. **Reste 100% win-rate / zéro
argent** — c'est juste un découpage du même taux.

**M-G (moyen) — Seuil de réussite (SEUIL_PCT) flou côté trader.** Une cellule est NC
si delta < seuil. Mais ce seuil ne tient pas compte de l'amplitude qu'il me FAUT pour
qu'un turbo soit gagnant (un turbo a une barrière). Je ne demande PAS de mesurer le gain
(hors-sujet) — je demande juste que le seuil « VRAI » ne valide pas des micro-mouvements
de +0,12% que je n'aurais jamais pu exploiter avec un turbo. Sinon le win rate affiché
est gonflé par des « VRAI » que je n'aurais pas pu trader. Reste dans le direction.

VERDICT section 4 : win rate only me va, mais **non segmenté par conviction**, il ne me
suffit pas pour décider de passer en réel. C'est le manque le plus stratégique.

## 5. Un trou qui ferait que je n'utiliserais PAS ces rapports ?

Pas de trou rédhibitoire qui invaliderait tout le flux — le squelette tient. Mais
DEUX points pratiques qui, non corrigés, me feraient décrocher du suivi à l'usage :

**M-H (le trou pratique principal) — Le timing du suivi 12h tombe AVANT l'ouverture US.**
Les actifs US (S&P, Nasdaq, VIX) ouvrent à 15h30 Paris. Donc au suivi 12h, **un tiers de
mes positions (les 3 actifs US) n'a même pas d'ouverture stampée** → colonne `Ouverture`
= `—`, statut vide. Le suivi 12h ne me sert que pour EU + continus. Mon premier vrai
point de situation sur le S&P/Nasdaq c'est 18h… soit 2h30 après l'ouverture US, quand le
plus gros du move est souvent déjà passé. Pour les actifs US, le « suivi » arrive trop
tard pour décider d'une sortie. Ce n'est pas un bug, c'est la conséquence des créneaux
fixes — mais ça limite réellement l'utilité du suivi sur 3 de mes 12 actifs.

**M-I (cohérence référence vs exécution réelle) — L'ouverture stampée n'est pas forcément
celle où j'achète.** La résolution Q1 stampe à la vraie ouverture (bien). Mais moi je lis
le briefing à 7h et j'exécute mes turbos… quand ? Si j'achète le CAC à 9h05 (ouverture
EU) le prix de référence colle. Si j'achète à 7h30 sur le marché continu / pré-ouverture
(ce que beaucoup font pour les turbos indices), ma référence d'entrée ≠ celle du système.
Le gap d'ouverture (spec §2.6 : « aucun traitement spécial ») peut alors faire diverger
le win rate mesuré de MON résultat réel. À clarifier : le système mesure la qualité de
la DIRECTION sur la journée de bourse (légitime), pas mon point d'entrée perso. Tant que
c'est explicite, OK — mais ce n'est pas dit, et un trader naïf croira que « ouverture »
= son prix d'achat.

Aucun de ces deux points n'est bloquant. Ils plafonnent l'utilité, ils ne la cassent pas.

---

## Manques à corriger pour 10/10

Classés par impact sur MON utilité (mettre du cash). Tous restent win-rate-only / zéro argent.

| # | Manque | Gravité | Correctif pour 10/10 |
|---|---|---|---|
| **M-F** | Win rate non segmenté par conviction | **P0** | Ajouter au bilan (R4 quotidien + R5 hebdo) un **win rate par niveau de conviction** : forte (|score| élevé, multi-critères, 0 drapeau ◧/⇆/↯) vs faible (quasi-neutre, mono-critère, coin-flip). Le decision-log a déjà les champs. C'est LE chiffre go/no-go réel. |
| **M-A** | Suivi aveugle à la dynamique de tendance | **P0** | Dans R2/R3 : ajouter colonne **Delta vs suivi précédent** (12h→18h) + flag « s'accélère ↑ / s'essouffle ↓ / se retourne ⇄ ». C'est le signal de sortie d'un trend-follower. |
| **M-B** | Suggestion de sortie sous-spécifiée | **P1** | Arrêter UN seuil chiffré unique (résoudre la contradiction §3.2 « ×0.5 » vs Q4 « seuil amplitude »). Drapeau, pas ordre — d'accord. Mais un drapeau qui ne se déclenche jamais ou se déclenche au hasard = inutile. |
| **M-D** | Manager muet pendant le warm-up (1er mois) | **P1** | Abaisser le seuil d'« observation actionnable » : dès N_eff ≥ 3, sortir une **pré-alerte** (« tendance défavorable, à confirmer S+1 ») plutôt que de tout ranger en « observations sans proposition ». Garde le bilan dimanche utile dès la S1. |
| **M-H** | Suivi 12h inutile sur les 3 actifs US | **P1** | Acter que le 1er point US est à 18h (déjà la conséquence des créneaux). Au minimum : afficher explicitement « US : ouverture à 15h30, suivi à partir de 18h » dans R2 pour ne pas laisser de cases vides muettes. Option : mini-stamp US 15h35 déjà prévu Q1 → ajouter un flag « US ouvert depuis Xh » dès R2. |
| **M-E** | Manager ne pointe que les faiblesses | **P2** | Ajouter section « **Cellules/critères porteurs** » (win rate élevé sur N_eff ≥ 5) dans R5 → je sais où concentrer le cash. |
| **M-C** | Suivi aveugle à l'invalidation de thèse par news | **P2** | Relier le bloc « News à impact » à un statut par actif : **thèse encore valide / fragilisée** (sans re-scoring complet — juste « une news majeure contredit-elle le call ? »). |
| **M-G** | Seuil VRAI/NC peut valider des micro-moves non tradables | **P2** | Vérifier que SEUIL_PCT par actif ≥ amplitude minimale exploitable en turbo. Reste de la direction (pas du gain), juste un seuil plus honnête. |
| **M-I** | « Ouverture » ≠ prix d'entrée perso (pédagogie) | **P3** | Une ligne dans R2/R4 : « référence = ouverture marché, mesure la justesse de DIRECTION sur la journée, pas votre point d'entrée ». Évite la confusion. |

**Pour 10/10** : corriger M-F + M-A (les deux P0) suffirait à passer de 7,5 à ~9. Les deux
ensemble transforment « rapports informatifs » en « outil de décision d'engagement ».
Les P1 montent à 9,5. Le reste = polish.

## Tableau de notation

| Critère d'utilité (angle Spéculateur) | Note | Commentaire |
|---|---|---|
| Flux décision→suivi→bilan vs 3 bulletins identiques | 9/10 | Vrai progrès, fin du re-scoring intraday trompeur |
| Référence = vraie ouverture marché | 9/10 | Colle à l'exécution réelle (M-I à clarifier) |
| Suivi : « est-ce que je gagne ? » | 8/10 | Clair et rapide |
| Suivi : « quand sortir ? » | 4/10 | Aveugle à la dynamique de tendance (M-A) + suggestion floue (M-B) |
| Bilan du jour 22h (boucle courte) | 8/10 | Bien, clôt le 24h le soir même |
| Manager : boucle d'amélioration concrète | 7/10 | Pas cosmétique, mais muet au début (M-D) + que des faiblesses (M-E) |
| Win rate only : suffisant pour passer en réel | 5/10 | Non segmenté par conviction (M-F) = angle mort go/no-go |
| Pas de trou rédhibitoire | 8/10 | Aucun blocage ; M-H plafonne l'utilité sur 3 actifs |
| **GLOBAL** | **7,5/10** | **GO**. Corriger M-F + M-A pour viser 10/10. |

---

*Audit Spéculateur — `v3/audit/audit-spec5-speculateur.md`. Zéro invention : tout point*
*non tranché renvoie à la spec/résolutions. Pressurisable par Analyst + News Trader.*
