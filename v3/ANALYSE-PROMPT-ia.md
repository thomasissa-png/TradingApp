# Analyse prompt DeepSeek — TradingApp v3 (angle LLM / prompt-engineering)

## Verdict

**Le prompt actuel est un bon EXTRACTEUR mais un mauvais ROUTEUR directionnel.** Il décrit
la news (taxonomie, zone, latence) mais ne produit AUCUN des 3 signaux dont le système a
besoin pour trader : **direction (LONG/SHORT), matérialité (signal vs bruit), fiabilité
(fait vs rumeur)**. Résultat : la direction est devinée en aval par keyword-matching, alors
que le LLM qui a déjà LU et COMPRIS la news est le seul endroit où l'inférer correctement.
On paie le LLM pour comprendre, puis on jette sa compréhension. Le surcoût tokens d'ajouter
ces champs est marginal (~+40-60 tokens out/news, < +0,5 $/mois au volume cité) face au gain :
suppression d'une couche de matching fragile + signal directionnel natif.

**Note globale : 6/10.** Fiable sur le JSON, sous-spécifié sur l'objectif métier.

## Faiblesses classées

**P0 — bloquantes pour l'objectif directionnel**
1. **Pas de direction.** Aucun champ bullish/bearish par actif. C'est LE trou. La direction
   pricée par keyword-matching aval est fragile (négations, contexte, ironie, double effet).
2. **Mono-actif.** `cours` est un string unique. Or un même event touche souvent
   Brent + Or + VIX + EUR/USD. Le mapping vers les 12 actifs cibles est perdu.
3. **Pas de matérialité ni fiabilité.** "Rumeur de deal" et "deal signé confirmé" sortent
   identiques → impossible de pondérer signal vs bruit, ni de filtrer le déjà-pricé.

**P1 — qualité / robustesse**
4. **Pas d'ancrage sur les 12 actifs.** Le prompt laisse `cours` en texte libre ("Nvidia
   (NVDA)") qui n'est dans AUCUN des 12 actifs tradés → news non routable mais quand même payée.
5. **Zéro few-shot.** À temp=0 le format tient, mais le JUGEMENT (direction, matérialité,
   choix L1) dérive sans exemples calibrés. C'est le plus gros levier de cohérence.
6. **Redondance L1 / news_category.** 14 vs 11 valeurs, ~70 % de chevauchement sémantique
   (Géopolitique≈geopolitical, Énergie≈commodity, Earnings≈earnings…). Double taxonomie =
   double surface d'incohérence pour un gain analytique nul.

**P2 — mineur**
7. `latence` mélange durée d'effet et timing de marché (intraday/overnight/weekend vs jours).
8. Pas de garde explicite sur la langue mixte FR/EN (titres EN, prompt FR).

## Risques de dérive JSON (Q1)

`json_object` + temp=0 garantit du JSON **syntaxiquement** valide, PAS sémantiquement conforme :
les énumérations ne sont pas contraintes côté API (DeepSeek ne supporte pas un json_schema
strict comme OpenAI). Risques réels : valeur hors-énum (`"central_bank"` au lieu de
`central_bank_subtle`), champ absent (le code gère via `.get(..., "")`, bon réflexe), L2 inventé
malgré la règle 3. → Mitigation : few-shot + validation aval contre les énums (rejet/normalisation).

---

## Proposition : system prompt amélioré + schéma JSON (copiable)

Schéma orienté ROUTAGE DIRECTIONNEL. `impacts[]` remplace `cours` mono-actif et porte la
direction. `materiality` + `reliability` permettent de filtrer le bruit en aval.

```text
Tu es un analyste senior d'un desk de news trading institutionnel.
Pour chaque news (titre + snippet), tu COMPRENDS l'événement, tu identifies quels actifs
parmi la liste fermée sont impactés, et DANS QUEL SENS. Tu retournes UNIQUEMENT un JSON strict.

ACTIFS TRADABLES (liste FERMÉE — n'utilise QUE ces ids, sinon n'inclus pas l'actif) :
CAC40, SP500, NASDAQ, EURUSD, BRENT, VIX, GOLD, SILVER, COPPER, COFFEE, COCOA, WHEAT

SCHEMA :
{
  "category": "<geopolitical | macro | central_bank | earnings | commodity | regulatory | m_a | weather | supply_chain | other>",
  "subcat": "<sous-thème précis, ex: 'Iran-Moyen-Orient', 'Fed-FOMC'. Vide si incertain.>",
  "trigger": "<fait déclencheur factuel, max 200 chars>",
  "zone": "<US | EU | EU-FR | BR | CN | RU | UA | AU | Moyen-Orient | Global>",
  "horizon": "<intraday | overnight | days>",
  "reliability": "<confirmed | reported | rumor>",
  "materiality": "<high | medium | low>",
  "already_priced": <true | false>,
  "impacts": [
    { "asset": "<id de la liste fermée>",
      "direction": "<bullish | bearish>",
      "confidence": "<high | medium | low>" }
  ]
}

RÈGLES :
1. AUCUNE INVENTION. Doute -> champ vide / impacts:[] / materiality:"low".
2. impacts = SEULEMENT des actifs de la liste fermée réellement et directionnellement
   impactés. Un event peut en toucher plusieurs (ex: risque géopol -> GOLD bullish,
   BRENT bullish, VIX bullish, SP500 bearish). Aucun actif clair -> impacts:[].
3. direction = sens du PRIX de l'actif (hausse=bullish). Réfléchis à l'effet réel,
   ignore le ton du titre.
4. reliability: fait officiel="confirmed", presse/source citée="reported", "selon des
   sources"/spéculation="rumor". materiality="high" seulement si surprise/ampleur notable.
5. already_priced=true si la news est une confirmation d'attendu déjà connu du marché.
6. News non-tradable (sport, lifestyle, opinion) -> category:"other", impacts:[].
7. Le titre peut être en EN ou FR : raisonne, réponds toujours dans ce schéma.

Réponds avec UNIQUEMENT le JSON.
```

### Few-shot à injecter (1 message user/assistant calibré, exemple)

```text
USER: TITRE : Iran retaliates with airstrikes on US bases, Brent jumps 5%
ASSISTANT: {"category":"geopolitical","subcat":"Iran-Moyen-Orient","trigger":"Frappes iraniennes sur bases US, escalade militaire","zone":"Moyen-Orient","horizon":"intraday","reliability":"confirmed","materiality":"high","already_priced":false,"impacts":[{"asset":"BRENT","direction":"bullish","confidence":"high"},{"asset":"GOLD","direction":"bullish","confidence":"high"},{"asset":"VIX","direction":"bullish","confidence":"medium"},{"asset":"SP500","direction":"bearish","confidence":"medium"}]}
```

Ajouter 2 autres few-shots : (a) une news **non-tradable** → `impacts:[]`, (b) une **rumeur
M&A** → `reliability:"rumor"`, `materiality:"medium"`. 3 exemples suffisent à ancrer le jugement.

## Coût / tokens (Q5)

- Schéma actuel : ~80-110 tokens out/news. Nouveau schéma avec `impacts[]` : ~130-180 tokens
  out/news. Delta ≈ +50-70 out. À 0,28 $/M out et volume cité (~2-3 €/mois) → **surcoût < +0,5 $/mois**.
- Few-shot ajoute ~250 tokens INPUT/appel non cachés (in à 0,14 $/M = négligeable) ; DeepSeek
  facture le cache hit ~10x moins → le system prompt + few-shot bénéficient du context caching.
- **Trade-off net : POSITIF.** On supprime la couche keyword-matching directionnel (code +
  source de bugs) contre un coût quasi nul. Le LLM fait le travail une fois, proprement.

## Réponses synthèse aux questions

- **Q2 (taxonomie)** : FUSIONNER. Garder `category` (~10 valeurs) + `subcat` libre. Supprimer
  L1/L2 dédoublés. La granularité fine vit dans `subcat`, pas dans une 2e énumération.
- **Q3 (champs manquants)** : ajouter `impacts[]{asset,direction,confidence}`, `reliability`,
  `materiality`, `already_priced`. Coût marginal, valeur métier majeure.
- **Q4 (few-shot)** : OUI, 3 exemples calibrés. Premier levier de cohérence du jugement.
- **Q6 (failure modes)** : ambiguë → `impacts:[]` + materiality:low ; multi-tickers → array
  natif ; FR/EN → règle 7 explicite ; déjà pricée → `already_priced:true`.
