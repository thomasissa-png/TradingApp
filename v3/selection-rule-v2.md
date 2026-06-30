# SELECTION-RULE v2 — diplômation glissante (PROPOSITION, shadow mode)

> **STATUT : BROUILLON — en attente de signature Thomas.**
> Rédigé le **2026-06-29**, AVANT toute consultation des WR tradable par cellule
> (anti-post-hoc : la justification ci-dessous ne regarde AUCUN résultat courant).
> Ne remplace `SELECTION-RULE.md` (v1, gravée) qu'une fois daté + signé. Tant que
> non signé, **v1 reste en vigueur** (snapshot unique au J+60 = 2026-08-08).

---

## Pourquoi une v2 (justification écrite, pré-résultats)

v1 fixe un **snapshot unique au J+60 (2026-08-08)** : on ne regarde qu'à cette date
si une cellule passe `WR tradable ≥ 70 % / N ≥ 15`. Deux limites, indépendantes de
tout résultat :

1. **Une cellule prête plus tôt attend une date arbitraire.** Si une cellule atteint
   N ≥ 15 avec un WR solide le 20/07, rien ne justifie d'attendre le 08/08 pour la
   trader. Le 08/08 était un point de contrôle commode, pas une vérité statistique.
2. **Les resets ont décalé les compteurs.** La plupart des cellules comptent depuis
   le 11/06, les continus depuis le 17/06, les 3 nouveaux actifs depuis le 26/06. Le
   08/08 est en réalité **le premier moment** où certaines atteignent péniblement
   N ≥ 15 — d'autres ne l'atteindront pas. Un snapshot fixe gaspille le temps des
   cellules mûres sans aider les retardataires.

**Ce que la v2 NE fait PAS** : elle **ne baisse pas** le plancher statistique. N ≥ 15
reste le minimum (en dessous, un WR mesuré est indistinguable d'un pile-ou-face), et
le seuil de justesse reste exigeant. La v2 change **quand** on regarde (en continu,
par cellule), pas **à quel niveau** on valide.

---

## Règle v2 (formule, à graver si signée)

Évaluation **quotidienne**, par cellule 24h. Une cellule devient **tradable** le
PREMIER jour ouvré D où elle satisfait SIMULTANÉMENT :

> **(1)** `N ≥ 15` paris non-chevauchants (comptés depuis `ref_changed` si applicable) ;
> **(2)** `WR tradable` (point) `≥ 70 %` ;
> **(3)** **borne basse Wilson 95 % du WR tradable ≥ 0,55** (garde-fou multiple-testing).

Une fois diplômée, la cellule est tradable **chaque jour ouvré**, tant qu'elle ne
tombe pas sous le kill criterion (`KILL-CRITERION.md`, inchangé). Si elle repasse
sous (1)/(3) après diplômation (ex. série de NC), elle est **dé-diplômée** le jour
où la condition casse (la discipline vaut dans les deux sens, comme `ref_changed` en v1).

### Pourquoi le garde-fou Wilson ≥ 0,55 (et pas juste « point ≥ 70 % »)

En glissant, on teste 15 cellules × N jours → **multiple-testing** : une cellule peut
franchir 70 % un jour par chance. Exiger que la **borne basse** Wilson 95 % dépasse
0,55 impose que le WR soit **statistiquement séparable d'un coin flip**, pas seulement
un point estimé chanceux. Conséquence concrète : à N = 15, un point à 70 % (≈ borne
basse 48 %) **ne diplôme PAS** ; il faut soit plus de N, soit un WR plus haut (~12-13/15).
C'est le garde-fou qui rend la glissière aussi sûre que le snapshot unique de v1.

*(Le seuil 0,55 est le paramètre de décision à verrouiller avec Thomas. Alternative
plus stricte : 0,60. À fixer AVANT de regarder les WR courants.)*

---

## Ce qui reste identique à v1 (inchangé)

- **WR tradable = VRAI / (VRAI + FAUSSE + non-conclusif)** (NC au dénominateur).
- **24h-only** : la sélection ne porte que sur l'horizon 24h (non-chevauchement garanti).
- **`ref_changed`** : N repart de zéro à la date de changement de référence ; registre
  `v3/data/ref-changed.json` clé par `ticker_principal`.
- **Kill criterion** : s'applique indépendamment (la v2 ne le touche pas).
- **Pas d'assouplissement post-hoc** : à 68 %, la cellule n'est pas diplômée. Pas de
  « c'est proche ».

---

## Procédure (si signée)

1. Calcul quotidien, par cellule 24h : `N`, `WR tradable`, borne basse Wilson 95 %.
2. Marquer « diplômée » la cellule qui passe (1)+(2)+(3) ; consigner la date de
   diplômation dans `v3/data/selection-graduation-log.jsonl` (append-only, daté).
3. Trading réel autorisé sur les cellules diplômées, **et elles seules**.
4. Dé-diplômation tracée de la même façon (date + raison) si une condition casse.
5. Le J+60 (08/08) n'est plus un couperet mais un **point de revue** : on fait le
   bilan des diplômations à cette date (combien, lesquelles), sans rien y déclencher
   de spécial.

---

## Toute modification ultérieure

Comme v1 : nouveau fichier `selection-rule-v3.md`, justification écrite avant
résultats, daté + signé. Jamais d'édition silencieuse de ce fichier.

---

## Signature

- [ ] **Thomas valide v2** (diplômation glissante, garde-fou Wilson à fixer) · date : __________
- [ ] **Thomas refuse** · on garde v1 (snapshot 08/08)
- [ ] **Thomas demande ajustement** (seuil Wilson, autre) : __________
