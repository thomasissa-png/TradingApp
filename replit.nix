# replit.nix — TradingApp Phase 2a
# Auteur : @infrastructure — Date : 2026-05-01
#
# Dépendances système Nix pour Replit Core. Stack Python pur.
# Documentation associée : REPLIT_ACTIONS.md (guide Thomas), .replit (config Repl)
#
# Channel : stable-24_05 (cohérent avec .replit [nix] channel)

{ pkgs }: {
  deps = [
    # ========================================================================
    # Python 3.12 — runtime principal
    # Requis pour : zoneinfo (TZ-aware datetime), type hints PEP 695,
    # asyncio amélioré, performance (10-15% vs 3.11)
    # ========================================================================
    pkgs.python312
    pkgs.python312Packages.pip
    pkgs.python312Packages.setuptools
    pkgs.python312Packages.wheel

    # ========================================================================
    # uv — package manager rapide (10-100x pip)
    # Recommandé pour Replit Python en 2026, lock file déterministe
    # Cf. REPLIT_ACTIONS.md §A.4
    # ========================================================================
    pkgs.uv

    # ========================================================================
    # SQLite — base de données locale (cache marché + journal trades)
    # Cf. infra-audit.md §2.4 (cache strategy) + §4.3 (persistance)
    # ========================================================================
    pkgs.sqlite
    pkgs.sqlite-interactive

    # ========================================================================
    # Git — clone du repo privé GitHub + commits depuis Replit
    # ========================================================================
    pkgs.git
    pkgs.gitMinimal

    # ========================================================================
    # OpenSSL — TLS pour appels HTTPS (Twelve Data, Anthropic, Telegram, healthchecks.io)
    # Requis par python-telegram-bot, anthropic SDK, requests, httpx
    # ========================================================================
    pkgs.openssl
    pkgs.cacert

    # ========================================================================
    # Curl — debug ad-hoc des appels API depuis le Shell Replit
    # ========================================================================
    pkgs.curl

    # ========================================================================
    # jq — parsing JSON dans les logs structurés
    # Cf. infra-audit.md §4.4 (logs JSON ligne par ligne)
    # ========================================================================
    pkgs.jq

    # ========================================================================
    # Build dependencies — requis pour compiler certains packages Python
    # (numpy, pandas, scipy, arch — utilisés en Phase 1 R&D edge)
    # ========================================================================
    pkgs.gcc
    pkgs.gnumake
    pkgs.pkg-config
    pkgs.libffi
    pkgs.zlib

    # ========================================================================
    # Timezone data — critique pour ZoneInfo("Europe/Paris")
    # Cf. REPLIT_ACTIONS.md §C.2 wrapper TZ-aware
    # ========================================================================
    pkgs.tzdata
  ];

  env = {
    # ==========================================================================
    # Locale — UTF-8 pour gestion correcte des accents (français)
    # Cf. CLAUDE.md règle 8 (UTF-8 dans le code, é è à jamais é)
    # ==========================================================================
    LANG = "C.UTF-8";
    LC_ALL = "C.UTF-8";

    # ==========================================================================
    # Python — désactiver le buffering stdout (logs Replit en temps réel)
    # ==========================================================================
    PYTHONUNBUFFERED = "1";
    PYTHONDONTWRITEBYTECODE = "1";

    # ==========================================================================
    # OpenSSL — chemin des CA certificates (pour HTTPS sortant)
    # ==========================================================================
    SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";

    # ==========================================================================
    # Timezone — référence pour le runtime (le wrapper Python utilise ZoneInfo)
    # Cf. .replit [env] TZ également défini
    # ==========================================================================
    TZ = "Europe/Paris";

    # ==========================================================================
    # uv — cache local (ignoré par .gitignore)
    # ==========================================================================
    UV_CACHE_DIR = "${"$"}{REPL_HOME}/.uv-cache";
  };
}
