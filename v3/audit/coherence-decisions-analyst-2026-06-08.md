# Audit cohérence décisions — Analyst — 2026-06-08 · 07h04

> Source : `v3/data/bulletins/bulletin-2026-06-08-07h.md` + `v3/data/decision-log/2026-06-08-0704.jsonl`
> 36 cellules auditées (12 actifs × 3 horizons)
> Convention verdict : ✅ cohérent | ⚠️ fragile | ❌ incohérent

## Tableau des 36 décisions

| Actif | Horizon | Décision | Verdict | Raison (si ≠ ✅) |
|---|---|---|---|---|
| Argent | 24h | SHORT (-5.69) | ✅ | |
| Argent | 7j | SHORT (-8.16) | ✅ | |
| Argent | 1m | SHORT (-3.90) | ✅ | |
| Blé | 24h | LONG (+0.84) | ⚠️ | Mono-critère (sécheresse US, 59% du score) + coverage 65% + signal faible : direction portée par 1 seul critère à z-score modeste (+0.18), tous autres critères absents ou quasi-nuls |
| Blé | 7j | LONG (+2.55) | ⚠️ | Mono-critère même origine ; p2_shadow_contrib_exclu=3.73 supérieur au score (2.55) : si les critères exclus étaient actifs, la direction serait instable |
| Blé | 1m | LONG (+2.77) | ⚠️ | Même fragilité mono-critère ; cohérence inter-horizons 24h/7j/1m tous LONG = alignement mais tous dépendent du même critère unique |
| CAC 40 | 24h | SHORT (-0.03) | ❌ | coin_flip=true ET quasi_neutre=true : score = -0.026, pratiquement zéro — direction non-actionnable présentée comme SHORT ; incoherence_inter_horizons=true |
| CAC 40 | 7j | LONG (+0.95) | ⚠️ | Mono-critère (sur-performance CAC/S&P à norm=+0.99, presque saturé) ; incoherence_inter_horizons=true : 7j LONG entre deux horizons SHORT (⇆ zigzag) |
| CAC 40 | 1m | SHORT (-0.12) | ⚠️ | quasi_neutre=true + neutral_band=true : |score|=0.122, direction marginale non-actionnable ; incoherence_inter_horizons=true |
| Cacao | 24h | LONG (+1.51) | ⚠️ | Coverage 50%, confidence faible ; divergence_quant_news : quant=+2.55 mais news=-1.04 (news SHORT sur EUDR/maladies déjà cotés ⌛) ; p2_shadow_flip_potential=true |
| Cacao | 7j | LONG (+5.90 pond) | ⚠️ | News dominant (ratio 0.53) + divergence_quant_news (quant=+7.58 vs news=-4.0) ; news cap non appliqué 7j ; coverage 50% ; ↯ masqué par pertinence amplifiée 7j |
| Cacao | 1m | LONG (+6.65 pond) | ⚠️ | News dominant (ratio 0.81), news_cap_applied=true ; quant=+10.05 vs news=-8.10 (divergence majeure) ; score pondéré 6.65 très éloigné du brut 2.01 — direction portée par critères pos. spéculatif à pertinence max, sans couverture météo/ports (poids 20 absents) |
| Café (Arabica) | 24h | SHORT (-0.93 pond) | ⚠️ | News dominant (ratio 1.83) : quant=-0.66 SHORT et news=-1.20 SHORT — direction cohérente mais le quant seul est faible ; score pondéré -0.93 ≠ score brut -1.86 (écart normal : cap news) ; coverage 60% |
| Café (Arabica) | 7j | SHORT (-1.64 pond) | ⚠️ | News dominant (ratio 4.02) : quant=-0.87 SHORT, news=-3.50 SHORT — cohérent en signe mais score quant très faible ; direction pilotée quasi-exclusivement par les news structurelles (maladies/cycle brésilien) déjà cotées ⌛ |
| Café (Arabica) | 1m | SHORT (-2.41 pond) | ✅ | News dominant (2.09) mais quant et news alignés SHORT ; p2_shadow_flip_potential=true (indicatif) mais signe cohérent ; coverage 60% acceptable |
| Cuivre | 24h | LONG (+2.35 pond) | ⚠️ | News dominant extrême (ratio 11.92) : quant=+0.29, news=+3.44 — signal LONG porté quasi-entièrement par les news (grèves minières ⌛ déjà cotées) ; coverage 48% faible |
| Cuivre | 7j | SHORT (-0.20) | ❌ | quasi_neutre=true + neutral_band=true : score=-0.20, signal quasi-nul ; mais divergence_quant_news flagrant (quant=-1.00 vs news=+6.50 LONG) — news cap appliqué ramène SHORT mais la direction est opposée à la news dominante confirmée, signal non-actionnable |
| Cuivre | 1m | SHORT (-0.52) | ❌ | Divergence_quant_news : quant=-2.59 vs news=+6.10 LONG (confirmée, même event) — news cap appliqué maintient SHORT, mais le score pondéré -0.52 repose sur un bras quant très concentré sur le COT saturé (norm=+1.00 = saturation maximale) contre des news LONG multi-critères ; sens contra-intuitif non justifié par la méthode |
| EUR/USD | 24h | SHORT (-5.39) | ⚠️ | Mono-critère (différentiel taux 2Y US-DE, 84% du score quant) ; coverage 73% correcte ; signal économiquement solide mais dépendance unique à un critère de taux |
| EUR/USD | 7j | SHORT (-9.78) | ⚠️ | Mono-critère identique (9.06/9.78 = 93% du score) ; même remarque structurelle ; conviction forte mais fragilité si le critère taux venait à manquer |
| EUR/USD | 1m | SHORT (-9.48) | ⚠️ | Mono-critère (9.06/9.48 = 96%) ; cohérence inter-horizons parfaite (SHORT 24h/7j/1m) ; signal robuste mais mono-source confirmée |
| Nasdaq | 24h | SHORT (-5.67 pond) | ✅ | Signal large : taux réels (-3.83) + flux QQQ saturé (-2.00) + news SHORT (-4.00) convergents ; coverage 77% ; news dominant mais cohérent avec quant |
| Nasdaq | 7j | SHORT (-12.89) | ✅ | Signal le plus fort du bulletin ; taux réels (-7.65) + flux (-5.00) + SOX (+3.47 contre mais minoritaire) ; cohérence solide ; mono_critere=false |
| Nasdaq | 1m | SHORT (-10.87) | ⚠️ | Mono-critère (taux réels = 7.65/10.87 = 70%) ; cohérence inter-horizons SHORT partout = ✅ directionnel ; fragilité structurelle sur 1m si TIPS bougent |
| Or | 24h | SHORT (-2.88) | ⚠️ | Divergence_quant_news : quant=-5.38 SHORT vs news=+2.50 LONG (géopolitique Iran-Israël, freshness 0.21j) ; ↯ flagué correctement ; coverage 82% bonne ; direction quant convaincante mais news contra-trend significatives |
| Or | 7j | SHORT (-8.33) | ⚠️ | Mono-critère (taux réels = 8.35/9.33 = 89%) + divergence_quant_news (news=+1.00 LONG géopol) ; signal fort mais dépendance structurelle identique sur TIPS |
| Or | 1m | SHORT (-7.42) | ⚠️ | Mono-critère (8.35/7.64 — taux réels > score total car compensés par autres) + divergence_quant_news résiduelle ; cohérence directionnelle 24h/7j/1m = ok |
| Pétrole (Brent) | 24h | LONG (+4.51 pond) | ⚠️ | Mono-critère (tension géopol Moyen-Orient = 4.20/6.91 brut = 61%) ; news dominant extrême (ratio 6.56) ; quant=+0.91 faible seul ; sign_conflict présent (EIA rules → SHORT vs IA → LONG) ; news fraiches (0.21j) mais toute la conviction repose sur 1 critère événementiel |
| Pétrole (Brent) | 7j | LONG (+4.28 pond) | ✅ | Deux news sources (géopol + OPEC+) alignées LONG, quant>0 ; coverage 85% ; sign_conflict non bloquant (EIA rules interprétation inversée, DeepSeek arbitre correctement) ; score distribué sur plusieurs critères |
| Pétrole (Brent) | 1m | LONG (+1.58 pond) | ⚠️ | News dominant (ratio 1.21) sur nature ponctuel avec coef_nature=0.15 (decay fort à 1m) ; score pondéré 1.58 très différent brut 2.03 ; quant seul = +0.92 ; sign_conflict présent ; direction tenue par une accumulation de critères faibles |
| S&P 500 | 24h | LONG (+2.46) | ⚠️ | VIX régime = 7.02 (72% du score) critère dominant ; mais taux réels = -3.48 (contre-signal fort) ; 2 critères majeurs s'opposent — direction LONG tenue par le VIX qui compense ; coverage 93% bonne ; p2_shadow_flip_potential=false mais tension interne élevée ; historique récent 10 FAUX S&P LONG suggère fragilité systémique |
| S&P 500 | 7j | SHORT (-4.12) | ✅ | Taux réels (-6.96) + flux (-3.89) convergent SHORT ; VIX régime partiellement neutralisé à pertinence 0.6 ; signal distribué sur plusieurs critères |
| S&P 500 | 1m | SHORT (-7.76) | ✅ | Signal fort, taux réels (-6.96) + flux (-2.72) + CAPE (-4.00) alignés ; coverage 93% ; cohérence avec zigzag inter-horizon : 24h LONG / 7j-1m SHORT = instabilité notée mais chaque horizon tient sa logique |
| VIX | 24h | LONG (+3.36) | ⚠️ | Divergence_quant_news majeure (quant=-0.24 SHORT vs news=+3.60 LONG) ; news_cap_override=true (override actif, high+confirmed) ; la conclusion LONG repose intégralement sur la news géopolitique, le quant seul serait SHORT ; cohérence dépend de la validité de l'override |
| VIX | 7j | LONG (+1.60) | ⚠️ | Même structure : quant=+0.40 faible LONG, news=+1.20 dominant ; news_cap_override=true ; signal tenu mais conviction modeste (+1.60) |
| VIX | 1m | LONG (+0.43) | ⚠️ | |note|=0.43 très faible ; score pondéré = brut (pas de cap news) ; quant=+0.37, news=+0.06 ; news_cap_override=true mais contribution news quasi-nulle à 1m (coef_nature=0.15) ; direction LONG tenue par un fil — quasi-neutre non flagué (|score|>0.30 donc flag non déclenché mais très proche) |

## Compte final

- ✅ Cohérent : **9** cellules
- ⚠️ Fragile : **22** cellules
- ❌ Incohérent : **3** cellules (CAC 24h, Cuivre 7j, Cuivre 1m)

---

## Détail des ❌

**CAC 40 24h — SHORT (-0.03)** : coin_flip=true + quasi_neutre=true. Score = -0.026, indistinguable de zéro. La direction n'est pas portée par un signal — c'est du bruit numérique. Présenter comme "SHORT" avec ⚑ et ⇆ ne change pas le fait que la décision est statistiquement vide.

**Cuivre 7j — SHORT (-0.20)** : quasi_neutre=true + neutral_band=true + divergence_quant_news avec news=+6.50 LONG (grèves confirmées, freshness 5.2j). Le cap news ramène le score à -0.20 mais le signal news dominant est opposé et substantiel. La décision SHORT sur un score proche de zéro contre une news LONG forte = incohérence interne.

**Cuivre 1m — SHORT (-0.52)** : même event news LONG (+6.10 confirmé) contre quant=-2.59 concentré sur COT saturé (norm=+1.00). News cap appliqué produit un score -0.52 SHORT, mais le critère COT est à saturation maximale (z-score = +1.00 normalisé) — un critère seul à la borne, direction contraire à une news multi-sources confirmée, coverage 48%.

---

## Détail des ⚠️ principaux

**Blé 24h/7j/1m** : cohérence interne correcte mais toutes trois portées par un seul critère (sécheresse NOAA, z=+0.18 modeste). L'historique récent montre 9 FAUX consécutifs sur Blé 24h LONG — signal mono-critère fragile face à la réalité de marché.

**Cacao 7j/1m** : quant et news opposés (quant LONG fort, news SHORT) avec news dominant. La direction LONG à 7j/1m résulte du positioning spéculatif et des critères COT, mais les news sur l'EUDR et maladies cabosses poussent SHORT. Tension non résolue, coverage 50%.

**EUR/USD 24h/7j/1m** : mono-critère (différentiel taux 2Y) à 84-96% du score. Signal économiquement défendable mais fragile en cas d'indisponibilité de la source FRED (historique FRED 429 du 02/06).

**VIX 24h** : news_cap_override force LONG contre quant SHORT. Cohérence dépend entièrement de la validité de l'override géopolitique Iran-Israël.

**S&P 24h** : VIX régime +7.02 vs taux réels -3.48 — deux critères majeurs s'opposent. LONG tenu par le VIX seul à 24h, SHORT à 7j/1m. Tension inter-horizons réelle.
