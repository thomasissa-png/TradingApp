# Concertation 3 experts — design momentum-prix v2 (synthèse)

# Date : 2026-06-10 · Panel : Analyst / News Trader / Spéculateur
# Verdicts : Analyst 6/10 · News Trader 5,5/10 · Spéculateur 6/10 → **GO-MODIFIÉ** (pas GO sec)

> Docs sources : `momentum-family-{analyst,newstrader,spec}.md`. Aucun YAML/code modifié par la concertation.

## Constat BLOQUANT (Analyst A1, vérifié code)

Le critère `momentum_prix_20j_*` déployé est routé vers `_twelve_zscore_from_symbol` → z-score du **NIVEAU** de close (60j), **PAS** de la variation 20j. **La v2 « déployée » est fonctionnellement identique à la v1** (le nom est trompeur). Or le z-score de niveau est un **laggard** : en début de baisse, le prix reste au-dessus de sa moyenne 60j plusieurs semaines → reste LONG → **reproduit le bug cacao**. Tel quel, le momentum n'aide pas — il faut le corriger ou le retirer.

## Piège systémique (News Trader, vérifié code)

Le momentum gonfle `quant_total` → le cap anti-inversion `cap_abs = |quant_total|×0,8` rend l'inversion par les news **~7× plus difficile** en tendance finissante (poids 9 : exige une news < −8,4 vs −1,2 pour inverser). **Le momentum naïf RENFORCE le quant directionnel pile aux retournements où la news a raison** — l'autre face du bug cacao. + il augmente la couverture → `is_news_regime` (filet 📰) se déclenche moins.

## Convergence des 3 experts (amendements)

| # | Amendement | Source | Nature |
|---|---|---|---|
| **A1** | Dispatcher : calculer la VARIATION 20j (`close/close[-20]-1`) puis z-scorer la série de rendements — pas le niveau | Analyst (BLOQUANT) | **moteur** |
| **A2** | Cap **aveugle au momentum** : `cap_abs = |quant_total − contrib_momentum|×α` (le momentum décide la direction, jamais l'étouffement des news) | News Trader (P0) | **moteur** |
| **A3** | Poids **conservateurs ≤ 6** tant que non prouvé (cacao 9 → 6) ; cible ~15-20 % du total de fiche ; promotion 6→9 seulement si preuve | Spéculateur + Analyst + NT | fiches |
| **A4** | Override anti-momentum : news high/confirmed/≤72h contre la tendance → exempte du cap ET pondère momentum ×0,5 | News Trader | moteur |
| **A5** | **Métrique « FAUSSES aux retournements »** distincte du WR + forward-test J+60 (ne pas croire un gain in-sample, backtest OOS=46%) | Spéculateur + Analyst | mesure |
| **A6** | Exclure le momentum du calcul de couverture pour les actifs news-driven (préserver le filet 📰) | News Trader | moteur |
| **A7** | Vérifier que `fetch_twelve_series` rend le close J-1 définitif (pas intraday J0) au run 7h | Analyst | look-ahead |
| **A8** | Indices : garder RSI poids 2, plafonner tout momentum ajouté à 4-5 | Analyst | fiches |
| **A9** | VIX exclu (mean-reverting) | unanime | — |

## Le point qui dérange (Spéculateur)

« Si les news font 68-80 % et le quant 46 % sur le cacao, pourquoi empiler un critère **quant** avant d'avoir prouvé que **laisser parler les news** (corriger le cap) ne suffisait pas ? » → Le **cap aveugle au momentum (A2)** est peut-être le levier le plus important, plus que le momentum lui-même. C'est une **correction de COHÉRENCE, pas de l'alpha** — la barre en shadow = « moins de FAUSSES aux retournements », jamais le PnL.

## Verdict de synthèse

Le momentum déployé **ne doit pas rester tel quel** (laggard + gonfle le cap = peut re-créer cacao). Deux engine-fixes (A1 + A2) sont **nécessaires** pour que le design soit cohérent, pas optionnels. Avec A1+A2+A3 (poids ≤6) + A5 (métrique), le design monte à ~9/10. **Décision Thomas requise** : lever le gel moteur sur dispatcher + cap, politique de poids (≤6 prove-first), nouvelle métrique. Sinon : retirer le momentum shippé.
