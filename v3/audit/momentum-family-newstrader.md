# Momentum-prix v2 × news — critique News Trader
**Auteur** : @news-trader (trio audit v3) · **Date** : 2026-06-10
**Mode** : critique contradictoire notée /10, angle momentum × news. AUCUN code/YAML modifié.

---

## Verdict : **5,5 / 10**

Le design corrige le bon problème (absence de tendance-prix propre, cf. sweep 8/12 ABSENT) mais
**aggrave mécaniquement le bridage des news SHORT** sur le scénario qui a justement coulé le cacao.
Bon réflexe trend-following, mauvaise interaction avec le cap α=0.8. GO sous conditions (amendements ci-dessous).

---

## 1. Le momentum aggrave-t-il le bridage des news ? — OUI, chiffré

Le cap est `cap_abs = |quant_total| × 0.8` (ligne 1073). `quant_total` inclut désormais la contribution
du momentum-prix. Donc **plus le momentum est fort dans le sens du quant, plus le plafond laissé aux news monte**.

Mais le piège est asymétrique. Deux régimes :
- **Tendance + news alignés** (momentum baissier + news SHORT) : le momentum POUSSE `quant_total` vers le
  négatif → pas de signes opposés → le cap ne s'active même pas (condition L1072). Bénéfice net. C'est le
  cas cacao réécrit : momentum −1,5σ × poids 9 ≈ −4,3 bascule le quant SHORT, les news SHORT ne sont plus
  bridées du tout. **Le design RÉSOUT le cas cacao par ce canal.**
- **Tendance finissante** (momentum encore +1 haussier par inertie, news SHORT précoces) : le momentum
  ALIMENTE `quant_total > 0`. Exemple : quant sans momentum = +1,2 ; momentum +1,0σ × poids 9 × pert 0,8
  ≈ +7,2 → quant_total = +8,4. Cap news = 8,4 × 0,8 = **6,7** au lieu de 0,96 sans momentum. En valeur
  absolue le plafond grimpe, MAIS le quant à battre a grimpé encore plus : pour inverser il faut désormais
  news < −8,4 (au lieu de < −1,2). **Le retournement news devient ~7× plus difficile.** Confirmé : le
  momentum, au pic d'une tendance, BLINDE le quant directionnel pile quand les news signalent (à raison)
  le retournement.

**Verdict point 1** : aggravation RÉELLE et la plus dangereuse aux sommets/creux de tendance — exactement
le moment où une news fondamentale a le plus de valeur prédictive.

## 2. Retournement piloté par news (WASDE, OPEC, choc géopol) — qui gagne ?

Le momentum 20j est en retard structurel sur un choc de news (c'est sa nature : inertie 20 jours). Sur un
WASDE baissier ou un OPEC+ qui ouvre les vannes, jour J : momentum toujours +1 (20j de hausse non encore
digérés), news SHORT high. Avec poids 9 (cacao), le momentum domine et le cap réduit la news → **le système
reproduit le bug cacao, mais côté momentum cette fois.** L'`override_high_confirmed` (L1055-1064) est le seul
garde-fou : il exempte la news du cap si `materiality=high` + `reliability≠rumor` + `nature∈{structurel,ponctuel}`
+ `freshness ≤ 72h`. **C'est le bon outil mais il ne neutralise QUE le cap — il ne neutralise PAS le poids 9
du momentum dans `quant_total`.** Une news high exemptée du cap se bat quand même contre un quant gonflé par
le momentum. Insuffisant aux retournements brutaux.

## 3. Faut-il ajuster α / exempter les news face au momentum ? — OUI

Le cap a été conçu AVANT le momentum-prix. Avec un momentum poids 6-9 dans le quant, α=0.8 fixe devient trop
protecteur. Recommandation (pas d'implémentation) : **rendre le cap aveugle au momentum** — calculer
`cap_abs` sur `quant_total HORS contribution momentum-prix`. Ainsi le momentum décide de la direction quant
mais ne sert pas à étouffer une news qui le contredit. Subsidiairement, élargir l'override aux news
`high+confirmed` même `medium` quand un `contre_momentum` est détecté.

## 4. Interaction avec `is_news_regime` — le momentum l'éteint, c'est ambigu

`is_news_regime` ne se déclenche QUE si `coverage < COVERAGE_MIN` (0.40) ET carry échoué (L1143, L1194).
Ajouter un critère momentum poids 9 (toujours dispo via Twelve) **augmente la couverture pondérée** →
fait repasser des cellules au-dessus du plancher → **`is_news_regime` se déclenchera MOINS souvent.** Or sur
cacao c'est précisément `is_news_regime` qui rendait la voix aux news quand le quant manquait. On remplace
un filet news (📰) par un momentum directionnel : bon en tendance suivie, dangereux si le momentum est en
retard sur un choc. À surveiller en shadow : taux de déclenchement 📰 avant/après momentum.

---

## Amendements concrets (recommandations, zéro implémentation)

1. **Cap aveugle au momentum** (P0) : `cap_abs = |quant_total − contrib_momentum_prix| × α`. Le momentum
   fixe la direction quant, jamais le plafond anti-news. Corrige directement le point 1.
2. **Override anti-momentum** (P0) : si `contre_momentum[h]=True` (déjà calculé, L258-303) ET news
   `materiality=high & reliability≠rumor & freshness≤72h`, exempter la news du cap ET pondérer la contribution
   momentum × 0,5 sur cet horizon (l'inertie 20j est suspecte quand une news fraîche la contredit).
3. **Plafond de poids momentum** (P1) : capper le poids effectif du momentum à ~20% du poids total de la
   fiche. Poids 9 sur cacao (total ~48) ≈ 19% → OK ; vérifier les autres fiches du sweep avant rollout.
4. **Garde-fou `is_news_regime`** (P1) : pour les `NEWS_DRIVEN_ASSETS` (cuivre/cacao/cafe), exclure le
   momentum-prix du calcul de `coverage` OU baisser sa pertinence si un biais news net+confirmed existe —
   pour ne pas éteindre le filet 📰 qui a sauvé le diagnostic cacao.
5. **Mesure shadow obligatoire** (P0) : avant tout passage live, logger sur ≥20 jours par actif :
   (a) fréquence où momentum gonfle `quant_total` côté opposé à une news high (point 1), (b) delta de
   déclenchement `is_news_regime`, (c) WR des cellules `contre_momentum=True`. WIN RATE ONLY — pas de ROI.

---

## Synthèse une ligne

Le momentum-prix v2 répare le cacao quand tendance et news convergent, mais **transforme le cap α=0.8 en
bouclier renforcé contre les news aux retournements** : exempter le momentum du calcul du cap est le
correctif prioritaire avant tout GO live.

*Audit News Trader — analyse pure, aucun code/YAML modifié. 2026-06-10*
