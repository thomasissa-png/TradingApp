# Forcer le rafraîchissement de la page live (trading.issa-capital.com)

> Découvert en S10 (25/06) : le chemin de service de la page n'était documenté nulle part.

## Où la page est servie sur le VPS

- **Checkout git servi** : `/srv/tradingapp` (clone du repo TradingApp).
- **Fichier servi** : `/srv/tradingapp/v3/data/index.html` (Caddy le sert sur `trading.issa-capital.com`).
- Le VPS **tire `main` tout seul** (cron de pull côté VPS) : après un push sur `main`, la page se rafraîchit en quelques minutes sans rien faire.

⚠️ `forcer_deploiement` (outil MCP « VPS - débogage ») cible l'app **Anya**, PAS la page TradingApp : il répond « déjà à jour » même quand la page doit changer. Ne pas compter dessus pour la page.

## Forcer immédiatement (SSH `root@82.165.168.92`)

```bash
git -C /srv/tradingapp pull origin main
```

Pas de build : `index.html` est déjà commité par le cycle (GitHub Actions). Recharger ensuite (Ctrl/Cmd+Shift+R pour le cache navigateur).

## Commande auto-localisante (si le chemin a changé)

```bash
p=$(find /opt /home /srv /var/www /root -type f -path '*v3/data/index.html' 2>/dev/null | head -1)
git -C "$(git -C "$(dirname "$p")" rev-parse --show-toplevel)" pull origin main
```
