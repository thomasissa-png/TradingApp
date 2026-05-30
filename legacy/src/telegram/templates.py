"""Templates Telegram (Phase 2c — formats stricts cf docs/copy/message-templates.md v1.2).

Format strict 6L+1 pour ACHAT/VENTE (cf brand-platform.md §6 + section 1 du message-templates).
Format 3L strict pour NO-TRADE.
Format 4L pour ERREUR DATA / DEGRADED MODE.

Vocabulaire proscrit (rejet automatique) :
- "signal fort", "buy now", "guaranteed"/"garanti", "perfect entry", "opportunity", "ne pas manquer"
- Futur affirmatif ("va monter", "atteindra") => utiliser "Cible potentielle" / conditionnel.

UTF-8 natif obligatoire (é, è, à) — pas d'\\uXXXX (cf CLAUDE.md règle UTF-8).
"""

from __future__ import annotations

import html
from typing import Any, Final, Literal

from src.ai.tools import ScoringSignalOutput


def _esc(text: str | None) -> str:
    """Escape HTML pour parse_mode='HTML' Telegram (R2 audit @design).

    Echappe `<`, `>`, `&` dans les champs free-form (raison, asset, no_trade_reason)
    qui peuvent contenir du contenu Claude non controle. Renvoie chaine vide si None.
    """
    if text is None:
        return ""
    return html.escape(str(text), quote=False)

# ---- Mini-jalon J+7 : message hello-world (conserve pour mode hello) ----

HELLO_WORLD_TEMPLATE: Final[str] = (
    "TradingApp cron OK — {ts}\n"
    "Mode: {mode}\n"
    "Mini-jalon J+7 actif. Le bot est en place, R&D edge a venir (30-90j)."
)


def render_hello_world(ts: str, mode: str) -> str:
    """Rendu du message du mini-jalon J+7."""
    return HELLO_WORLD_TEMPLATE.format(ts=ts, mode=mode)


# ---------------------------------------------------------------------------
# Helpers internes
# ---------------------------------------------------------------------------


def _fmt_decimal(value: float | None, decimals: int = 2) -> str:
    """Format décimale avec virgule française (3.42 -> "3,42")."""
    if value is None:
        return "—"
    return f"{value:.{decimals}f}".replace(".", ",")


def _fmt_eur(value: float | None) -> str:
    """Format euros entier (126.4 -> "126 €")."""
    if value is None:
        return "—"
    return f"{round(value)} €"


def _expiration_line_for_edge(edge_id: str) -> str:
    """Retourne la ligne d'expiration selon l'edge.

    H-C ORB 5/15min => 9h00 CET (breakout range 8h-8h15).
    Tous les autres edges => 8h55 CET.
    """
    if edge_id == "H-C":
        return "Avant 9h00 CET — au-delà, ne pas exécuter"
    return "Avant 8h55 CET — au-delà, ne pas exécuter"


def _backtest_line(signal: ScoringSignalOutput) -> str:
    """Ligne 5 du template ACHAT/VENTE (Phase 2d-bis — R1 audit @design).

    Si stats backtest disponibles (alimentees par engine.py via get_backtest_stats) :
        "Backtest : 63% sur 81 trades | DD max -17% | Ref. #B-031"
    Sinon (lookup rnd_results KO) : fallback minimal pour ne pas bloquer le signal :
        "Backtest : Ref. #B-031"

    Format conforme docs/copy/message-templates.md v1.2 §2 (3 stats + ref).
    Note : le caractere MINUS SIGN typographique (U+2212) est intentionnel pour
    rendu Telegram (convention financiere : "-XX %").
    """
    if (
        signal.win_rate_backtest is not None
        and signal.nb_trades_backtest is not None
        and signal.drawdown_max_backtest is not None
    ):
        return (
            f"Backtest : {signal.win_rate_backtest:.0f}% sur "
            f"{signal.nb_trades_backtest} trades | "
            f"DD max −{signal.drawdown_max_backtest:.0f}% | "  # noqa: RUF001
            f"Réf. {signal.backtest_ref}"
        )
    return f"Backtest : Réf. {signal.backtest_ref}"


def _paper_prefix(paper_mode: bool) -> str:
    """Préfixe [PAPER TRADING] si mode paper actif (US-11)."""
    return "[PAPER TRADING] " if paper_mode else ""


def _extract_risk_capital(signal: ScoringSignalOutput) -> tuple[float | None, float | None]:
    """Extrait risque max + capital engagé depuis signal (champ optionnel via raison)."""
    # MVP : valeurs business par défaut (pas dans ScoringSignalOutput v1.2 strict 15 champs).
    # Convention : risque ~= |entry - sl| * quantity_default (estimation 600€ / écart),
    #             capital ~= entry * quantity_default.
    if signal.entry is None or signal.sl is None:
        return None, None
    spread = abs(signal.entry - signal.sl)
    if spread <= 0:
        return None, None
    # Hypothèse persona Thomas : risque max ~150€/trade, position sizée pour respecter ce risque.
    quantity = max(1, int(150 / spread))
    risque_eur = spread * quantity
    capital_eur = signal.entry * quantity
    return risque_eur, capital_eur


# ---------------------------------------------------------------------------
# Templates ACHAT / VENTE (format 6L + 1)
# ---------------------------------------------------------------------------


def format_buy_signal(signal: ScoringSignalOutput, paper_mode: bool = False) -> str:
    """Template ACHAT — 6 lignes signal + 1 ligne score.

    Conforme docs/copy/message-templates.md v1.2 section 1 (format strict).
    Si paper_mode True : préfixe "[PAPER TRADING] " sur la 1re ligne (US-11).
    """
    if signal.direction != "BUY":
        raise ValueError(f"format_buy_signal attend direction=BUY, recu: {signal.direction}")

    risque, capital = _extract_risk_capital(signal)
    expiration = _expiration_line_for_edge(signal.edge_id)
    prefix = _paper_prefix(paper_mode)

    lines = [
        f"{prefix}🟢 ACHAT  <b>{_esc(signal.asset)}</b>",
        (
            f"Entrée : {_fmt_decimal(signal.entry)}  |  "
            f"SL : {_fmt_decimal(signal.sl)}  |  "
            f"Cible potentielle : {_fmt_decimal(signal.tp)}"
        ),
        (
            f"Risque : {_fmt_eur(risque)} max  |  "
            f"Capital engagé : {_fmt_eur(capital)}  |  "
            f"{expiration}"
        ),
        f"Raison : {_esc(signal.raison)}",
        _backtest_line(signal),
        f"Score : {_fmt_decimal(signal.score, 1)}/10",
    ]
    return "\n".join(lines)


def format_sell_signal(signal: ScoringSignalOutput, paper_mode: bool = False) -> str:
    """Template VENTE — 6 lignes signal + 1 ligne score.

    Identique ACHAT mais emoji 🔴 et libellé VENTE.
    """
    if signal.direction != "SELL":
        raise ValueError(f"format_sell_signal attend direction=SELL, recu: {signal.direction}")

    risque, capital = _extract_risk_capital(signal)
    expiration = _expiration_line_for_edge(signal.edge_id)
    prefix = _paper_prefix(paper_mode)

    lines = [
        f"{prefix}🔴 VENTE  <b>{_esc(signal.asset)}</b>",
        (
            f"Entrée : {_fmt_decimal(signal.entry)}  |  "
            f"SL : {_fmt_decimal(signal.sl)}  |  "
            f"Cible potentielle : {_fmt_decimal(signal.tp)}"
        ),
        (
            f"Risque : {_fmt_eur(risque)} max  |  "
            f"Capital engagé : {_fmt_eur(capital)}  |  "
            f"{expiration}"
        ),
        f"Raison : {_esc(signal.raison)}",
        _backtest_line(signal),
        f"Score : {_fmt_decimal(signal.score, 1)}/10",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Templates NO-TRADE (format 3L strict)
# ---------------------------------------------------------------------------


def format_no_trade(
    signal: ScoringSignalOutput,
    max_score: float | None = None,
) -> str:
    """Template NO-TRADE — 3 lignes strict (NT-01 à NT-04 cf message-templates §3).

    La raison est extraite de signal.no_trade_reason ou signal.raison.
    Si max_score fourni : permet de contextualiser (NT-01 score sous seuil).

    Phase 2d-bis (R3 audit @design) : pour les cas VIX (NT-03), la condition de
    reprise chiffree (`Reprise quand VIX < 25,0 sur clôture consécutive`) est
    appendue automatiquement a la ligne 2 si elle n'est pas deja presente — Thomas
    doit pouvoir suivre le VIX sans relancer le bot (brand-platform §6 Do#1).
    """
    raison = signal.no_trade_reason or signal.raison or "Conditions non remplies"
    raison = raison[:200]  # Garde-fou longueur

    # R3 — enrichissement automatique cas VIX
    if "VIX" in raison and "Reprise" not in raison:
        # Format 3L strict respecte : on append en fin de ligne 2 (separateur ` — `)
        raison_enriched = f"{raison} — Reprise quand VIX < 25,0 sur clôture consécutive"
        # Garde-fou longueur (pour ne pas exploser sur Telegram 4096 chars)
        raison = raison_enriched[:300]

    # Ligne 1 : asset + score si pertinent (escape HTML pour parse_mode HTML)
    asset_safe = _esc(signal.asset)
    if max_score is not None:
        line1 = f"⚪️ NO-TRADE  {asset_safe} / Score {_fmt_decimal(max_score, 1)}/10"
    else:
        line1 = f"⚪️ NO-TRADE  {asset_safe}"

    # Ligne 2 : raison concrète (escape HTML)
    line2 = _esc(raison)

    # Ligne 3 : prochaine fenêtre (constante)
    line3 = "Prochaine fenêtre : demain 8h45 CET"

    return "\n".join([line1, line2, line3])


# ---------------------------------------------------------------------------
# Templates ERREUR DATA / DEGRADED MODE
# ---------------------------------------------------------------------------


def format_data_error(error_context: dict[str, Any]) -> str:
    """Template ERREUR DATA US-04 — Twelve Data partiel.

    error_context attendu :
      - asset (str) : sous-jacent prévu
      - missing_field (str) : champ manquant (ex "volume 1m Xetra")
      - hour (str) : heure de la détection (ex "8h44")
    """
    asset = _esc(error_context.get("asset", "Sous-jacent prévu"))
    missing = _esc(error_context.get("missing_field", "champ inconnu"))
    hour = _esc(error_context.get("hour", "8h45"))

    lines = [
        f"⚠️ ERREUR DATA  {asset}",
        f"Twelve Data : données partielles reçues à {hour} (champ manquant : {missing})",
        "Signal non calculable avec fiabilité suffisante — NO-TRADE par précaution",
        "Statut API : https://status.twelvedata.com",
    ]
    return "\n".join(lines)


def format_degraded_mode(
    reason: Literal["claude_timeout", "twelvedata_partial", "cron_late"],
    context: dict[str, Any] | None = None,
) -> str:
    """Template DEGRADED MODE US-05 — fallback IA / pipeline dégradé.

    3 variantes :
    - claude_timeout : Sonnet > 45s + Haiku timeout aussi
    - twelvedata_partial : données marché incomplètes (alias de format_data_error)
    - cron_late : cron démarré > 8h55 (US-06)
    """
    ctx = context or {}
    asset = _esc(ctx.get("asset", "Signal du jour"))

    if reason == "claude_timeout":
        return "\n".join(
            [
                f"⚠️ DEGRADED MODE  {asset}",
                "Scoring Claude indisponible (timeout &gt; 45 s)",
                "Données de marché reçues — scoring IA non complété",
                "Signal non envoyé : une justification incomplète n'est pas une justification",
                "Prochaine tentative : demain 8h40 CET",
            ]
        )

    if reason == "twelvedata_partial":
        missing = _esc(ctx.get("missing_field", "données partielles"))
        hour = _esc(ctx.get("hour", "8h44"))
        return "\n".join(
            [
                f"⚠️ DEGRADED MODE  {asset}",
                f"Twelve Data partiel à {hour} ({missing}) — pipeline dégradé",
                "Signal non calculable avec fiabilité suffisante — NO-TRADE par précaution",
                "Prochaine tentative : demain 8h40 CET",
            ]
        )

    # cron_late
    date_str = _esc(ctx.get("date", "aujourd'hui"))
    return "\n".join(
        [
            f"⚠️ CRON MANQUÉ  Signal du {date_str}",
            "Pipeline non exécuté à 8h40 CET (alerte healthchecks.io)",
            "Signal du jour non calculé — fenêtre d'exécution 8h45-8h55 expirée",
            "Cause probable : démarrage Replit &gt; 60 s",
            "Action : vérifier logs Replit. Signal reprendra demain matin automatiquement.",
        ]
    )


# ---------------------------------------------------------------------------
# Audit hebdo (US-09) + audit mensuel (US-10/US-11)
# ---------------------------------------------------------------------------


def format_weekly_summary(stats: dict[str, Any], paper_mode: bool = False) -> str:
    """Résumé semaine — vendredi 18h00 CET (US-09).

    stats attendu :
      - week_n (int), week_start (str), week_end (str)
      - signaux (int), trades (int), no_trades (int)
      - pnl_brut (float), pnl_net (float)
      - win_rate (float 0-100), gagnants (int), perdants (int)
      - drawdown (float 0-100)
      - meilleur_signal (str), meilleur_pct (float), meilleur_ref (str)
      - pire_signal (str), pire_pct (float), pire_ref (str)
      - pertes_consecutives (int)
    """
    week_n = stats.get("week_n", "?")
    week_start = stats.get("week_start", "?")
    week_end = stats.get("week_end", "?")
    prefix = _paper_prefix(paper_mode)

    lines: list[str] = [
        f"{prefix}📊 Résumé semaine {week_n} — {week_start} -> {week_end}",
        "",
        (
            f"Signaux envoyés : {stats.get('signaux', 0)} | "
            f"Trades passés : {stats.get('trades', 0)} | "
            f"NO-TRADE : {stats.get('no_trades', 0)}"
        ),
        (
            f"P&amp;L brut semaine : {_fmt_decimal(stats.get('pnl_brut'), 2)} € | "
            f"P&amp;L net (frais) : {_fmt_decimal(stats.get('pnl_net'), 2)} €"
        ),
        (
            f"Win rate semaine : {stats.get('win_rate', 0):.0f}% "
            f"({stats.get('gagnants', 0)} gagnants / {stats.get('perdants', 0)} perdants)"
        ),
        (
            f"Drawdown semaine : {stats.get('drawdown', 0):.0f}% du capital dédié | "
            "Max toléré : 20%"
        ),
        "",
        (
            f"Meilleur signal : {stats.get('meilleur_signal', '—')} "
            f"({stats.get('meilleur_pct', 0):+.1f}%) — Réf. {stats.get('meilleur_ref', '—')}"
        ),
        (
            f"Pire signal : {stats.get('pire_signal', '—')} "
            f"({stats.get('pire_pct', 0):+.1f}%) — Réf. {stats.get('pire_ref', '—')}"
        ),
    ]

    # Lignes conditionnelles d'alerte
    drawdown = float(stats.get("drawdown", 0) or 0)
    if drawdown > 15:
        lines.append("")
        lines.append(
            f"⚠️ Drawdown hebdo {drawdown:.0f}% &gt; 15% — surveiller semaine prochaine"
        )
    pertes = int(stats.get("pertes_consecutives", 0) or 0)
    if pertes >= 3:
        lines.append(
            f"⚠️ {pertes} pertes consécutives — signal d'alerte, voir règles d'arrêt"
        )

    return "\n".join(lines)


def format_monthly_report(stats: dict[str, Any], prompt_continue: bool = True) -> str:
    """Rapport mensuel — 1er du mois (US-10/US-11).

    stats attendu :
      - mois (str ex "Mai 2026")
      - pnl_brut (float), frais (float), pnl_net (float)
      - pfu (float), pnl_net_pfu (float)
      - win_rate (float), backtest_win_rate (float)
      - nb_trades (int), no_trades (int), no_trade_pct (float)
      - drawdown_max (float)
      - hypotheses_actives (list[str])
      - meilleure_hypothese (str), meilleure_wr (float), meilleure_n (int)
      - hypothese_a_surveiller (str), surveiller_wr (float), surveiller_backtest (float)
    """
    mois = stats.get("mois", "?")
    win_rate = float(stats.get("win_rate", 0) or 0)
    backtest_wr = float(stats.get("backtest_win_rate", 0) or 0)
    ecart = win_rate - backtest_wr
    hypotheses = ", ".join(stats.get("hypotheses_actives") or [])

    lines: list[str] = [
        f"📈 Rapport mensuel {mois}",
        "",
        (
            f"P&amp;L brut : {_fmt_decimal(stats.get('pnl_brut'), 2)} € | "
            f"Frais Bourse Direct : {_fmt_decimal(stats.get('frais'), 2)} € | "
            f"P&amp;L net frais : {_fmt_decimal(stats.get('pnl_net'), 2)} €"
        ),
        (
            f"Fiscalité PFU estimée (31,4%) : {_fmt_decimal(stats.get('pfu'), 2)} € | "
            f"<b>P&amp;L net après PFU : {_fmt_decimal(stats.get('pnl_net_pfu'), 2)} €</b>"
        ),
        "",
        (
            f"Win rate mois : {win_rate:.0f}% vs backtest {backtest_wr:.0f}% — "
            f"écart : {ecart:+.0f} pts"
        ),
        (
            f"Nb trades : {stats.get('nb_trades', 0)} | "
            f"NO-TRADE : {stats.get('no_trades', 0)} "
            f"({stats.get('no_trade_pct', 0):.0f}% des jours ouvrés)"
        ),
        (
            f"Drawdown max mensuel : {stats.get('drawdown_max', 0):.0f}% | "
            "Limite : 20%"
        ),
        "",
        f"Hypothèses actives ce mois : {hypotheses or '—'}",
        (
            f"Hypothèse la plus performante : {stats.get('meilleure_hypothese', '—')} — "
            f"{stats.get('meilleure_wr', 0):.0f}% win rate sur "
            f"{stats.get('meilleure_n', 0)} signaux"
        ),
        (
            f"Hypothèse à surveiller : {stats.get('hypothese_a_surveiller', '—')} — "
            f"{stats.get('surveiller_wr', 0):.0f}% win rate "
            f"(sous backtest {stats.get('surveiller_backtest', 0):.0f}%)"
        ),
    ]

    if prompt_continue:
        lines.extend(
            [
                "",
                "────────────────",
                "Décision continuation :",
                "→ Taper /continue pour valider le mois suivant",
                "→ Taper /stop pour suspendre les signaux",
            ]
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Backward-compat (Phase 2a stubs remplacés)
# ---------------------------------------------------------------------------


def render_buy_signal(signal: ScoringSignalOutput, paper_mode: bool = False) -> str:
    """Alias backward-compat — utiliser format_buy_signal."""
    return format_buy_signal(signal, paper_mode)


def render_sell_signal(signal: ScoringSignalOutput, paper_mode: bool = False) -> str:
    """Alias backward-compat — utiliser format_sell_signal."""
    return format_sell_signal(signal, paper_mode)


def render_no_trade(
    signal: ScoringSignalOutput, max_score: float | None = None
) -> str:
    """Alias backward-compat — utiliser format_no_trade."""
    return format_no_trade(signal, max_score)


def render_error_data(error_context: dict[str, Any]) -> str:
    """Alias backward-compat — utiliser format_data_error."""
    return format_data_error(error_context)


def render_degraded_mode(
    reason: Literal["claude_timeout", "twelvedata_partial", "cron_late"],
    context: dict[str, Any] | None = None,
) -> str:
    """Alias backward-compat — utiliser format_degraded_mode."""
    return format_degraded_mode(reason, context)


__all__ = [
    "HELLO_WORLD_TEMPLATE",
    "format_buy_signal",
    "format_data_error",
    "format_degraded_mode",
    "format_monthly_report",
    "format_no_trade",
    "format_sell_signal",
    "format_weekly_summary",
    "render_buy_signal",
    "render_degraded_mode",
    "render_error_data",
    "render_hello_world",
    "render_no_trade",
    "render_sell_signal",
]
