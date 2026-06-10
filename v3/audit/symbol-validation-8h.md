# Sonde 8h Paris — futures indices/VIX (ES=F / NQ=F / VX=F) — VERDICT

_Audit 10/06, Lot 1, étape 1 (PROVE-FIRST). Rédigé par @infrastructure._
_Statut des mesures réseau : **EN ATTENTE DU RUN CI RÉEL** (clé Twelve absente de l'environnement d'analyse — zéro invention de prix)._

> **PROVE-FIRST** : ce document MESURE la disponibilité. Il ne touche NI aux fiches
> NI à `v3/config/suivi.yaml`. Aucun mapping (ticker de mesure, groupe `continu`,
> `ref_changed`) ne sera fait avant validation explicite de Thomas. Aucun poids /
> critère / seuil n'a été modifié (gel scoring respecté).

---

## 1. Le besoin

Thomas entre à **8h Paris** sur des turbos qui répliquent les **futures Globex**
(ES/NQ) et le **VIX future**. Aujourd'hui, S&P 500 / Nasdaq / VIX sont notés
depuis la **référence cash US 15h30** (groupe `us` de `suivi.yaml`, ligne 31-32).
Objectif : pouvoir noter ces 3 actifs depuis une **référence 8h Paris**.

Verrou technique connu : à 8h Paris, **seuls les futures Globex cotent**. Les ETF
proxies actuellement utilisés en CI (SPY/QQQ/VIXY via `_TICKER_MAP`) ne cotent
**pas encore** (ouverture cash US à 15h30). Il faut donc un instrument qui donne
un **prix FRAIS à 8h**, pas un close de la veille.

---

## 2. Constat FACTUEL depuis le code (vérifiable ici, sans réseau)

### 2.1 `_TICKER_MAP` (market_data.py) ne contient AUCUN future indice/VIX

Inspection ligne par ligne de `_TICKER_MAP` (market_data.py L106-186) :

- Les seuls symboles `=F` mappés sont des **matières premières** routées en
  `type=commodities` (CL1, CO1, NG, HG1, W_1, CC1, KC1…) ou des métaux en
  forex spot (GC=F → XAU/USD, SI=F → XAG/USD).
- **Aucun future indice actions** (ES/NQ) ni **future VIX** (VX) n'est présent.
- Indices/VIX sont servis via **ETF proxies** : `^GSPC→SPY`, `^IXIC→QQQ`,
  `^NDX→QQQ`, `^VIX→VIXY`. Ces ETF **ne cotent pas à 8h Paris** → inutiles pour
  la référence 8h.

### 2.2 Comportement de `_map_ticker` pour un `=F` non mappé

`market_data._map_ticker` (L204-217) :

```python
# Futures not in _TICKER_MAP: don't guess — fall back to yfinance
if yf_ticker.endswith("=F") or ".CBT" in yf_ticker:
    return None
```

Donc `ES=F`, `NQ=F`, `VX=F` (absents du map) → `return None` → **fallback
yfinance**. Or **yfinance est bloqué sur les runners GitHub Actions** (Yahoo
refuse les IP datacenter). Conclusion mécanique : **en l'état du code, ces 3
symboles sortent `n/a` en CI.**

### 2.3 Ce que la sonde teste réellement

`validate_symbols.probe_futures_8h` ne passe **PAS** par `_TICKER_MAP`. Elle
teste, pour chaque actif, plusieurs **variantes pures** directement contre
l'endpoint Twelve `/quote` :

| Actif | Yahoo | Variantes Twelve testées |
|---|---|---|
| S&P 500 future | `ES=F` | `ES=F`, `ES`, `ES1!`, `ES1`, `/ES` |
| Nasdaq 100 future | `NQ=F` | `NQ=F`, `NQ`, `NQ1!`, `NQ1`, `/NQ` |
| VIX future | `VX=F` | `VX=F`, `VX`, `VX1!`, `VX1`, `/VX` |

Pour chaque variante, deux tests : **(a) répond** (close > 0) et **(b) frais**
(`timestamp` Twelve daté de < 18h → daté du jour, pas un close veille).

### 2.4 Recherche documentaire Twelve Data (non concluante)

La doc publique Twelve (twelvedata.com/docs, /market-data, /indices) liste
stocks, forex, crypto, ETF, indices, et des futures **matières premières** /
métaux. Elle **ne confirme NI n'infirme** explicitement la présence des futures
**indices actions** (ES/NQ) et **VIX future** (VX) sur le plan free/Grow.
→ **Point non tranchable sans appel API réel** (red line zéro invention). Le run
CI le tranchera.

---

## 3. VERDICT par symbole

Légende : `Twelve` = répond sur Twelve free/Grow. `Frais 8h` = prix daté du jour
à 8h Paris. **PROUVÉ-CODE** = certain depuis l'analyse statique. **À MESURER** =
exige le run CI réel (clé Twelve, 08h00-08h30 Paris).

| Symbole | Dispo Twelve | yfinance-only → CI | Frais 8h possible | Recommandation |
|---|---|---|---|---|
| **ES=F** (S&P futures) | ❓ À MESURER (variantes ES/ES1!) | Si Twelve KO → **n/a en CI** (PROUVÉ-CODE) | ❓ À MESURER | **Conditionnel** : mapping 8h SI une variante répond ET frais. Sinon shadow-only 15h30. |
| **NQ=F** (Nasdaq futures) | ❓ À MESURER (variantes NQ/NQ1!) | Si Twelve KO → **n/a en CI** (PROUVÉ-CODE) | ❓ À MESURER | **Conditionnel** : idem ES=F. |
| **VX=F** (VIX future) | ❓ À MESURER (variantes VX/VX1!) | Si Twelve KO → **n/a en CI** (PROUVÉ-CODE) | ❓ À MESURER | **Conditionnel** : idem. VIX future souvent moins couvert que ES/NQ sur les APIs grand public → probabilité KO la plus élevée. |

### Hypothèse la plus probable (à CONFIRMER ou INFIRMER par le run CI)

> Twelve free/Grow couvre surtout les futures **matières premières**, pas les
> futures **indices actions / VIX**. Si c'est le cas :
> `ES/NQ/VX → KO Twelve → fallback yfinance → n/a sur GitHub Actions`
> → **pas de référence 8h gratuite** → S&P 500 / Nasdaq / VIX **restent à
> 15h30** (cash US), documenté **shadow-only**.
>
> C'est un **résultat valide** (mesurer avant d'agir). Si confirmé, le coût d'une
> réf 8h = passer sur un provider payant qui expose les futures CME (Databento,
> CME direct, Polygon futures…) — décision budget/ROI à part, hors de ce lot.

---

## 4. Décision de mapping — **NON, pas encore**

Aucun mapping n'est appliqué. Deux branches selon le run CI :

- **Branche A — au moins une variante répond ET frais 8h ✅**
  → mapping 8h **envisageable**. À soumettre à Thomas AVANT toute écriture dans
  les fiches / `suivi.yaml`. Détailler alors : ticker de mesure retenu, groupe
  `continu`/`globex`, flag `ref_changed`.
- **Branche B — aucune variante frais 8h (hypothèse probable)**
  → **shadow-only** : S&P 500 / Nasdaq / VIX restent notés à 15h30. Documenter la
  limite : « réf 8h non exécutable gratuitement, future Globex non exposé par
  Twelve free/Grow, yfinance bloqué en CI ».

---

## 5. Comment trancher (run CI réel — OBLIGATOIRE)

1. GitHub → **Actions** → workflow **`probe-futures-8h`** → **Run workflow**.
2. **Lancer ENTRE 08h00 et 08h30 heure de Paris** (sinon le test de fraîcheur ne
   prouve rien : un run à 15h verrait un prix « frais » même pour un instrument
   qui ne cote pas la nuit).
3. Lire le **log du step « Run sonde 8h »** ou télécharger l'**artifact
   `symbol-validation-8h`** (= `v3/audit/symbol-validation-8h-run.md`, généré par
   la sonde). **Ce VERDICT (`symbol-validation-8h.md`) n'est jamais écrasé** par
   la sonde — l'analyse PROVE-FIRST reste traçable séparément des mesures.
4. Reporter le tableau §3 rempli avec les vraies valeurs → Thomas tranche A/B.

Le workflow est **read-only** (`permissions: contents: read`), **ne commit
rien**, publie en artifact + log. Aucun risque de toucher fiches/suivi.

Pré-requis : secret repo **`TWELVE_DATA_API_KEY`** présent (déjà utilisé par
`validate-symbols.yml`). _NB : le brief évoque `TWELVE_API_KEY` ; le code et les
workflows existants utilisent `TWELVE_DATA_API_KEY`. Vérifier le nom réel du
secret côté repo avant le run — un alias divergent ferait sortir « SKIP »._

---

## 6. Ce qui reste vérifiable ICI vs run CI

| Élément | Statut ici |
|---|---|
| Outbound `api.twelvedata.com:443` | ✅ ouvert (testé) — la sonde TOURNERAIT si la clé était présente |
| Clé `TWELVE_DATA_API_KEY` dans l'env d'analyse | ❌ absente → mesures réseau impossibles ici |
| Logique sonde (réponse + fraîcheur) | ✅ implémentée + couverte par 8 tests mockés (pytest vert) |
| Step CI 8h (read-only, artifact, no-commit) | ✅ créé (`probe-futures-8h.yml`) |
| Constat `_TICKER_MAP` / fallback `=F` | ✅ prouvé par lecture code |
| Dispo réelle ES/NQ/VX sur Twelve | ❌ exige le run CI à 8h Paris |
