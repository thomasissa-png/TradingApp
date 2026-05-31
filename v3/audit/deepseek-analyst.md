# Audit systémique — DeepSeek extraction directionnelle
_222 news · 94 avec impact · 128 sans · temperature=0 · prompt v2.1_

---

## 1. Couverture / biais d'échantillon

**Distribution par actif :** SP500 (56), BRENT (41), GOLD (40), NASDAQ (40), EURUSD (34), VIX (20), CAC40 (3), COPPER (3), agri (0 : Café, Cacao, Blé absents).

**Biais structurel confirmé.** Les sources (`cnbc_top`, `cnbc_economy`, `cnbc_finance`, `eia_*`, `fed_press_all`, `newsapi`) sont massivement US-centrées et énergie-centrées. Ce n'est pas un défaut du LLM — c'est un défaut d'alimentation amont.

- CAC40, COPPER : 3 signals chacun sur 94 — insuffisant pour un scoring fiable. Toute cellule "bulletin" sur ces actifs sera statistiquement vide ou biaisée par 1-2 news atypiques.
- Agri (Café, Cacao, Blé) : 0 signal sur 222 news. Le système ne peut pas scorer ces actifs. Absent des sources = absent du bulletin.
- BOE, BOJ, ECB : présents mais quasi-totalité classée `low/confirmed` → 0 impact généré. Sources institutionnelles trop arides pour produire des signaux directionnels.

**Conclusion :** le système alimente correctement 6 actifs sur 12. Les 6 autres (CAC40, COPPER, Café, Cacao, Blé + partiellement VIX) sont sous-alimentés structurellement.

---

## 2. Cohérence des distributions

**Matérialité :** 39 high / 62 med / 121 low — ratio 18/28/54%. Plausible. La majorité des news financières est du bruit de fond (rapports BOJ, communiqués FED secondaires, news newsapi hors-sujet comme "7k-Mile 2009 Mercedes" #184 ou "Oven Liners" #194). Le filtre pré-LLM laisse passer du bruit résiduel — 20-25 news newsapi sans rapport (loisirs, tech consumer) → bonne nouvelle : le LLM les classe correctement `low/other` et génère 0 impact.

**Fiabilité :** dominée par `confirmed` (sources EIA, Fed, ECB officielles). Cohérent avec la composition des sources. La présence de `rumor` est limitée et bien corrélée aux news Iran deal non-vérifiées (news 2, 50, 61, 175). Pas de sur-confiance détectée.

**Ratio filtrage :** 128/222 = 58% écartées. Taux sain — un système trop permissif génère du bruit, trop restrictif manque des signaux.

---

## 3. Reproductibilité (temperature=0)

**Cohérence interne bonne sur le pattern dominant.** Les 8-10 news Iran/Hormuz LONG génèrent systématiquement BRENT L, GOLD L, VIX L, SP500 S — pattern stable, identique entre news 3, 27, 39, 82, 92, 97, 166, 172, 181.

**Incohérence détectée — cas Iran deal :** deux news quasi-identiques donnent des décisions opposées sur GOLD :
- News 61 (`Dollar slips after US-Iran ceasefire deal`) → BRENT S, GOLD S, VIX S, SP500 L — matérialité high/rumor
- News 67 (`Oil falls on hopes for US-Iran ceasefire`) → BRENT S, GOLD S, VIX S, SP500 L — cohérent

Mais news 69 (`Gold ticks up amid weaker dollar as Trump says to make final decision on Iran deal`) → GOLD L. Même contexte Iran deal, même période, GOLD change de direction selon l'angle de la news (dollar faible vs deal potentiel). Comportement défendable analytiquement mais crée une ambiguïté sur GOLD quand deux news contemporaines s'annulent.

**Incohérence Fed Warsh :** News 16 (Warsh nommé) → SP500 L, NASDAQ L. News 43 (analyse régime Warsh hawkish) → SP500 S, NASDAQ S, VIX L. Logique narrative distincte, mais si les deux arrivent le même cycle, le scoring SP500 sera nul par contradiction — signal annulé sans alerte.

---

## 4. Asymétrie directionnelle

**Décompte global :** 114 LONG / 123 SHORT (48%/52%) — équilibre satisfaisant, KPI 30-70% respecté.

**Asymétries par actif (estimées depuis table récap) :**
- GOLD : ~30L / ~10S — biais LONG structurel (safe haven dominant dans le contexte Iran + inflation)
- VIX : ~18L / ~2S — biais LONG massif (~90%) — logique : les sources couvrent le risque, pas la détente
- SP500 : ~22L / ~34S — biais SHORT modéré, dû au contexte macro inflationniste de l'échantillon
- BRENT : ~22L / ~19S — équilibré (Hormuz fermé vs deal Iran)
- NASDAQ : suit SP500, biais SHORT similaire
- EURUSD : équilibré (Fed hawkish → EUR S, mais BCE hawkish → EUR L)

**Risque :** si le contexte géopolitique change (deal Iran confirmé), les biais GOLD et VIX s'inverseront — le système doit être re-testé sur un échantillon post-crise pour valider la symétrie hors-crise.

---

## 5. Exploitabilité downstream

**Actifs bien alimentés (scoring fiable) :** SP500, NASDAQ, BRENT, GOLD, EURUSD — volume suffisant, diversité de sources, cohérence directionnelle vérifiée.

**VIX :** 20 signals mais biais LONG >85% — exploitable seulement comme indicateur de risque élévé, pas comme signal directionnel neutre.

**Actifs non exploitables dans l'état :** CAC40 (3 signals), COPPER (3), Café/Cacao/Blé (0). Un bulletin sur ces actifs serait basé sur 0-3 données — non représentatif, potentiellement trompeur.

**Qualité du JSON :** structure stable sur 222 appels, 0 erreur de parsing, 0 hallucination de format. La consistance technique du LLM est exemplaire.

**Signaux contradictoires non agrégés :** le système produit des signals individuels mais n'a pas de couche d'agrégation. Quand 3 news s'annulent sur SP500 dans le même cycle (2 SHORT, 1 LONG), le scoring dépend entièrement de la logique aval — ce risque doit être géré par la couche scoring, pas par le LLM.

---

## VERDICT

**EXPLOITABLE SYSTÉMATIQUEMENT : SOUS CONDITIONS**

Note : **6,5 / 10**

- Signal exploitable sur 5-6 actifs (SP500, NASDAQ, BRENT, GOLD, EURUSD, partiellement VIX) — qualité LLM solide, cohérence directionnelle validée, 0 erreur technique
- **Risque systémique n°1 — sources** : 6 actifs sur 12 sont structurellement non alimentés (CAC40, COPPER, agri x3, VIX partiel) ; tant que les flux RSS n'incluent pas de sources spécialisées (LME pour COPPER, ICE pour agri, presse EU pour CAC40), ces cellules du bulletin sont creuses et induisent un faux sentiment de couverture complète
- Signal contradictoire non géré : deux news contemporaines peuvent s'annuler sur le même actif (cas GOLD/Iran deal, cas Warsh) sans alerte — la couche scoring doit implémenter une détection de conflit et geler le signal plutôt que de moyenner
- Biais de contexte échantillon : les ratios directionnels (VIX 90% LONG, GOLD 75% LONG) sont corrects pour le contexte Iran-crise actuel mais ne sont pas généralisables — re-tester sur 2 semaines hors-crise avant mise en production
