"""TradingApp v3 — Extractor via DeepSeek V4 Flash

Pour chaque news (titre + snippet), appelle DeepSeek en mode JSON-structuré et
retourne un ExtractedEvent avec les colonnes du tableau events-log.md.

API DeepSeek = OpenAI-compatible. On utilise le SDK openai.
- Modèle : deepseek-chat (le moins cher de leur gamme, équivalent V4 Flash)
- Tarif : 0,14 $/M tokens input + 0,28 $/M tokens output
- Mode : JSON structuré, temperature=0 (reproductible)

Si DEEPSEEK_API_KEY est vide → extracteur désactivé (mode passive, le service
tourne quand même, lignes events-log avec colonnes vides).
"""

import json
import logging
import os
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEvent:
    L1: str = ""
    L2: str = ""
    trigger: str = ""
    cours: str = ""
    consequence: str = ""
    latence: str = ""
    duree: str = ""
    fin: str = ""
    news_zone: str = ""
    news_category: str = "other"
    confirmed_event: bool = False
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
  "consequence": "<mouvement observé chiffré si donné, sinon vide>",
  "latence": "<intraday | overnight | weekend | jours>",
  "duree": "<séance | quelques jours | semaine | mois | persistant>",
  "fin": "<ce qui a stoppé le mouvement, vide sinon>",
  "news_zone": "<US | EU | EU-FR | BR | CN | RU | UA | AU | Moyen-Orient | Global>",
  "news_category": "<earnings | macro | geopolitical | regulatory | m_a | sector | commodity | weather | supply_chain | central_bank_subtle | other>",
  "confirmed_event": <true/false>
}

RÈGLES :
1. AUCUNE INVENTION. Info manquante → champ vide.
2. News non-trading (lifestyle, sport, opinion) → news_category="other", L1/L2/cours vides.
3. Pas de L2 inventée si tu hésites → vide.
4. cours = sous-jacent FINANCIER (ticker/indice/devise/commodity). Sinon vide.
5. confirmed_event=true seulement si fait avéré/chiffré. Forecast/rumeur → false.

Réponds avec UNIQUEMENT le JSON."""


class Extractor:
    def __init__(self):
        api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY non défini → extracteur désactivé")
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

        logger.info("Extractor init: model=%s base_url=%s", self.model, base_url)

    def is_enabled(self) -> bool:
        return self.client is not None

    def extract(self, title: str, snippet: str = "") -> ExtractedEvent:
        if not self.is_enabled():
            return ExtractedEvent(trigger=title[:200], error="extractor disabled")

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
                max_tokens=400,
                timeout=20,
            )
            duration_ms = int((time.monotonic() - start) * 1000)
            data = json.loads(response.choices[0].message.content)

            tokens_in = response.usage.prompt_tokens if response.usage else 0
            tokens_out = response.usage.completion_tokens if response.usage else 0
            self.total_calls += 1
            self.total_tokens_in += tokens_in
            self.total_tokens_out += tokens_out

            return ExtractedEvent(
                L1=data.get("L1", "")[:80],
                L2=data.get("L2", "")[:80],
                trigger=data.get("trigger", title)[:250],
                cours=data.get("cours", "")[:80],
                consequence=data.get("consequence", "")[:150],
                latence=data.get("latence", "")[:30],
                duree=data.get("duree", "")[:30],
                fin=data.get("fin", "")[:150],
                news_zone=data.get("news_zone", "")[:30],
                news_category=data.get("news_category", "other")[:30],
                confirmed_event=bool(data.get("confirmed_event", False)),
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
        if not self.is_enabled():
            return {"enabled": False}
        cost_in = self.total_tokens_in * 0.14 / 1_000_000
        cost_out = self.total_tokens_out * 0.28 / 1_000_000
        return {
            "enabled": True,
            "calls": self.total_calls,
            "errors": self.total_errors,
            "tokens_in": self.total_tokens_in,
            "tokens_out": self.total_tokens_out,
            "estimated_cost_usd": round(cost_in + cost_out, 4),
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ext = Extractor()
    if not ext.is_enabled():
        print("Extractor disabled. Vérifie DEEPSEEK_API_KEY dans .env.")
        exit(1)

    test_cases = [
        ("Iran retaliates with airstrikes on US bases, Brent jumps 5%",
         "Tehran launched drone attacks; Brent crude surges past $110 in pre-market."),
        ("Nvidia beats Q1 earnings, raises guidance on AI demand",
         "NVDA reported revenue of $32B vs consensus $30B; CEO sees AI strong through 2027."),
        ("King Charles attends garden party at Buckingham Palace",
         "Royal event featured 8000 guests from UK charity organisations."),
    ]

    for title, snippet in test_cases:
        print(f"\n=== TITRE : {title}")
        e = ext.extract(title, snippet)
        print(f"  L1: {e.L1} | L2: {e.L2}")
        print(f"  cours: {e.cours} | category: {e.news_category} | confirmed: {e.confirmed_event}")
        print(f"  trigger: {e.trigger[:120]}")
        print(f"  tokens: in={e.tokens_in} out={e.tokens_out} ({e.duration_ms}ms)")
        if e.error:
            print(f"  ERROR: {e.error}")

    print(f"\n=== STATS ===\n{ext.get_stats()}")
