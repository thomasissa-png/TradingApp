"""TradingApp v3 — Extractor via DeepSeek (schéma 7 champs optimisé).

Schéma optimisé (11 -> 7 champs) :
  Gardés   : L1, L2, trigger, cours, latence, news_zone, news_category
  Supprimés: fin, duree, consequence, confirmed_event
  -> -36% tokens output, ~2-3 €/mois sur volume cible.

API DeepSeek = OpenAI-compatible. SDK openai.
- Modèle : deepseek-chat (le moins cher)
- Tarif  : 0,14 $/M tokens input + 0,28 $/M tokens output
- Mode   : JSON structuré, temperature=0 (reproductible)

GARDES-FOUS COÛT (persistants dans v3/data/cost-ledger.json) :
- soft cap  ~0,50 $/jour : log WARN, on continue d'appeler le LLM
- hard cap  ~0,80 $/jour : bascule fallback (extracteur désactivé pour la journée
  -> news_collector écrit en mode brut)

Si DEEPSEEK_API_KEY est vide -> extracteur désactivé (mode passive).
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from config import COST_LEDGER_PATH

logger = logging.getLogger(__name__)

# ============================================================
# Caps coût (USD/jour)
# ============================================================
SOFT_CAP_USD_PER_DAY = float(os.environ.get("LLM_SOFT_CAP_USD", "0.50"))
HARD_CAP_USD_PER_DAY = float(os.environ.get("LLM_HARD_CAP_USD", "0.80"))


@dataclass
class ExtractedEvent:
    L1: str = ""
    L2: str = ""
    trigger: str = ""
    cours: str = ""
    latence: str = ""
    news_zone: str = ""
    news_category: str = "other"
    error: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: int = 0


SYSTEM_PROMPT = """Tu es un analyste senior d'un desk de news trading institutionnel.

Pour chaque news financière (titre + snippet), tu retournes un JSON STRICT au format ci-dessous.

SCHEMA :
{
  "L1": "<une des 14 valeurs : Géopolitique | Macro-indicateurs | Banques-centrales | Énergie-Matières-premières | Earnings-Corporate | Indices-Sentiment | Tech-IA | Crypto | Devises-FX | Notations-souveraines-Dette | Politique | Immobilier | Fiscalité-Régulation | Commerce-Tariffs>",
  "L2": "<sous-catégorie précise, ex: 'Iran-Moyen-Orient', 'Fed-FOMC', 'Pétrole-EIA'>",
  "trigger": "<le fait déclencheur, factuel, max 200 chars>",
  "cours": "<sous-jacent impacté avec ticker, ex: 'Brent (BZ=F)', 'S&P 500 (^GSPC)', 'Nvidia (NVDA)'>",
  "latence": "<intraday | overnight | weekend | jours>",
  "news_zone": "<US | EU | EU-FR | BR | CN | RU | UA | AU | Moyen-Orient | Global>",
  "news_category": "<earnings | macro | geopolitical | regulatory | m_a | sector | commodity | weather | supply_chain | central_bank_subtle | other>"
}

RÈGLES :
1. AUCUNE INVENTION. Info manquante -> champ vide.
2. News non-trading (lifestyle, sport, opinion) -> news_category="other", L1/L2/cours vides.
3. Pas de L2 inventée si tu hésites -> vide.
4. cours = sous-jacent FINANCIER (ticker/indice/devise/commodity). Sinon vide.

Réponds avec UNIQUEMENT le JSON."""


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_ledger() -> dict:
    try:
        if COST_LEDGER_PATH.exists():
            return json.loads(COST_LEDGER_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("cost-ledger lecture KO: %s", e)
    return {}


def _save_ledger(ledger: dict) -> None:
    try:
        COST_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        COST_LEDGER_PATH.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    except Exception as e:
        logger.warning("cost-ledger écriture KO: %s", e)


class Extractor:
    def __init__(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY non défini -> extracteur désactivé")
            self.client = None
            return

        from openai import OpenAI
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

        self.total_calls = 0
        self.total_tokens_in = 0
        self.total_tokens_out = 0
        self.total_errors = 0
        self.hard_capped = False  # bascule fallback si hard cap atteint

        self.ledger = _load_ledger()
        self.day_key = _today_key()
        self.day_cost_usd = float(self.ledger.get(self.day_key, {}).get("cost_usd", 0.0))
        self._check_caps_initial()

        logger.info(
            "Extractor init: model=%s base_url=%s | cost_today=$%.4f (soft=$%.2f hard=$%.2f)",
            self.model, base_url, self.day_cost_usd, SOFT_CAP_USD_PER_DAY, HARD_CAP_USD_PER_DAY,
        )

    def _check_caps_initial(self):
        if self.day_cost_usd >= HARD_CAP_USD_PER_DAY:
            self.hard_capped = True
            logger.error(
                "HARD CAP atteint au boot : cost_today=$%.4f >= $%.2f -> fallback mode brut",
                self.day_cost_usd, HARD_CAP_USD_PER_DAY,
            )
        elif self.day_cost_usd >= SOFT_CAP_USD_PER_DAY:
            logger.warning(
                "SOFT CAP dépassé au boot : cost_today=$%.4f >= $%.2f (on continue)",
                self.day_cost_usd, SOFT_CAP_USD_PER_DAY,
            )

    def is_enabled(self) -> bool:
        return self.client is not None and not self.hard_capped

    def _update_cost(self, tokens_in: int, tokens_out: int):
        delta = (tokens_in * 0.14 + tokens_out * 0.28) / 1_000_000
        self.day_cost_usd += delta
        self.ledger[self.day_key] = {
            "cost_usd": round(self.day_cost_usd, 6),
            "calls": int(self.ledger.get(self.day_key, {}).get("calls", 0)) + 1,
            "tokens_in": int(self.ledger.get(self.day_key, {}).get("tokens_in", 0)) + tokens_in,
            "tokens_out": int(self.ledger.get(self.day_key, {}).get("tokens_out", 0)) + tokens_out,
        }
        _save_ledger(self.ledger)

        if self.day_cost_usd >= HARD_CAP_USD_PER_DAY and not self.hard_capped:
            self.hard_capped = True
            logger.error(
                "HARD CAP franchi : cost_today=$%.4f >= $%.2f -> bascule fallback brut",
                self.day_cost_usd, HARD_CAP_USD_PER_DAY,
            )
        elif self.day_cost_usd >= SOFT_CAP_USD_PER_DAY:
            logger.warning(
                "SOFT CAP dépassé : cost_today=$%.4f >= $%.2f",
                self.day_cost_usd, SOFT_CAP_USD_PER_DAY,
            )

    def extract(self, title: str, snippet: str = "") -> ExtractedEvent:
        if not self.is_enabled():
            return ExtractedEvent(trigger=title[:200], error="extractor disabled or hard-capped")

        start = time.monotonic()
        user_content = f"TITRE : {title.strip()}"
        if snippet and snippet.strip():
            user_content += f"\n\nSNIPPET : {snippet.strip()[:1500]}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0,
                response_format={"type": "json_object"},
                max_tokens=300,
                timeout=20,
            )
            duration_ms = int((time.monotonic() - start) * 1000)
            data = json.loads(response.choices[0].message.content)

            tokens_in = response.usage.prompt_tokens if response.usage else 0
            tokens_out = response.usage.completion_tokens if response.usage else 0
            self.total_calls += 1
            self.total_tokens_in += tokens_in
            self.total_tokens_out += tokens_out
            self._update_cost(tokens_in, tokens_out)

            return ExtractedEvent(
                L1=data.get("L1", "")[:80],
                L2=data.get("L2", "")[:80],
                trigger=data.get("trigger", title)[:250],
                cours=data.get("cours", "")[:80],
                latence=data.get("latence", "")[:30],
                news_zone=data.get("news_zone", "")[:30],
                news_category=data.get("news_category", "other")[:30],
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                duration_ms=duration_ms,
            )
        except json.JSONDecodeError as e:
            self.total_errors += 1
            logger.warning("DeepSeek invalid JSON for '%s...': %s", title[:60], e)
            return ExtractedEvent(trigger=title[:200], error=f"invalid JSON: {e}"[:200])
        except Exception as e:
            self.total_errors += 1
            logger.warning("DeepSeek extract failed for '%s...': %s", title[:60], str(e)[:200])
            return ExtractedEvent(trigger=title[:200], error=str(e)[:200])

    def get_stats(self) -> dict:
        if self.client is None:
            return {"enabled": False, "reason": "no_api_key"}
        cost_in = self.total_tokens_in * 0.14 / 1_000_000
        cost_out = self.total_tokens_out * 0.28 / 1_000_000
        return {
            "enabled": not self.hard_capped,
            "hard_capped": self.hard_capped,
            "calls": self.total_calls,
            "errors": self.total_errors,
            "tokens_in": self.total_tokens_in,
            "tokens_out": self.total_tokens_out,
            "cycle_cost_usd": round(cost_in + cost_out, 4),
            "day_cost_usd": round(self.day_cost_usd, 4),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ext = Extractor()
    if ext.client is None:
        print("Extractor disabled. Vérifie DEEPSEEK_API_KEY.")
        raise SystemExit(1)
    e = ext.extract(
        "Iran retaliates with airstrikes on US bases, Brent jumps 5%",
        "Tehran launched drone attacks; Brent crude surges past $110 in pre-market.",
    )
    print(e)
    print(ext.get_stats())
