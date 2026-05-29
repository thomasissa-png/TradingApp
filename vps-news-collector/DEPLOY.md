# Déploiement Phase 2.1 — News Collector VPS

> Code de la Phase 2.1 v3 (extraction DeepSeek) du service `tradingapp-news-collector`.
> Cible : `/opt/tradingapp/` sur le VPS (Ubuntu 24.04, user `tradingapp`, venv en place).
> Ces fichiers ne tournent PAS dans ce repo — ils sont versionnés ici comme record + transport.

## Fichiers (vérifiés byte-identiques au scratchpad Cowork du 27/05/2026)

| Fichier | Rôle | Marqueur v2.1 |
|---|---|---|
| `extractor.py` | Extraction structurée DeepSeek V4 Flash (mode JSON, temp=0) | classe `Extractor`, system prompt 14 valeurs L1, `get_stats()` coût |
| `news_collector.py` | Polling RSS BBC+CNBC+Investing (Reuters exclu, mort) + pré-filtre finance | `is_finance_relevant()`, `collect_rss_phase21()` |
| `agent_news.py` | Orchestrateur loop 15 min + métriques coût/cycle | `from extractor import Extractor`, `MAX_EXTRACTIONS_PER_CYCLE=50` |
| `requirements.txt` | Dépendances | `openai==1.55.0` (activé) |

Audit pré-déploiement : `py_compile` OK sur les 3 modules · aucun `rm` hors `/tmp` · `set -e` présent.

## Procédure VPS (à exécuter en root sur le VPS)

```bash
# 0. BACKUP des fichiers Phase 1 avant écrasement (réversibilité)
sudo -u tradingapp mkdir -p /opt/tradingapp/.backup-phase1
sudo -u tradingapp cp -f /opt/tradingapp/news_collector.py /opt/tradingapp/agent_news.py \
   /opt/tradingapp/requirements.txt /opt/tradingapp/.backup-phase1/ 2>/dev/null
echo "backup Phase 1 OK"

# 1-7. Déploiement (DEPLOY1.SH porte les 4 fichiers vérifiés en base64)
sudo bash DEPLOY1.SH
```

`DEPLOY1.SH` enchaîne : décode le tarball → `cp` + `chown tradingapp:tradingapp` →
`pip install -r requirements.txt` (active `openai`) → **test extracteur** (`python extractor.py`,
3 cas : Iran-Brent, Nvidia, King Charles) → `systemctl restart tradingapp-news-collector` →
`journalctl --since '2 minutes ago'`.

## Validation (tests PROMPT1.MD §10)

1. **Test extracteur** : les 3 JSON sortent propres. Le 3ᵉ (King Charles) doit avoir
   `news_category: "other"` et `cours`/`L1` vides.
2. **Cycle suivant (~15 min)** : `Bourse/Live/events-log.md` reçoit des lignes avec
   `L1 | L2 | trigger | cours | news_zone` **remplis** (≥ 80 % des items finance).
3. **Coût** : le log `agent_news` affiche `cost ~$X.XXXX` par cycle. Cible < $0.05/cycle.

## Rollback

```bash
sudo -u tradingapp cp -f /opt/tradingapp/.backup-phase1/* /opt/tradingapp/
sudo systemctl restart tradingapp-news-collector
```

## À remonter à Thomas après le 1er cycle (format §11)

- Coût observé : tokens in/out, $/cycle, $/jour, $/mois projeté
- % items écartés par le pré-filtre finance (`skipped_non_finance`)
- % erreurs LLM (`cycle_errors`)
- Extrait de 2-3 lignes `events-log.md` enrichies (preuve)
