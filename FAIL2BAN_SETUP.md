# Installation et Configuration Fail2ban pour AlphaLLM API

## 📋 Prérequis
- Linux (Debian/Ubuntu recommandé)
- Fail2ban >= 0.11
- iptables ou nftables
- 1GB RAM + bon CPU ✅

## 🚀 Installation

### 1. Installer Fail2ban
```bash
sudo apt-get update
sudo apt-get install fail2ban iptables
```

### 2. Copier les filtres
```bash
sudo cp fail2ban/alphallm.conf /etc/fail2ban/filter.d/
sudo cp fail2ban/alphallm-endpoint-abuse.conf /etc/fail2ban/filter.d/
sudo cp fail2ban/alphallm-bruteforce.conf /etc/fail2ban/filter.d/
```

### 3. Copier la configuration des jails
```bash
sudo cp fail2ban/jail.conf /etc/fail2ban/jail.d/alphallm.conf
```

### 4. Configurer le chemin des logs
Édite `/etc/fail2ban/jail.d/alphallm.conf` et assure-toi que:
```ini
logpath = /var/log/alphallm.log
```

Correspond au chemin où tu écris tes logs AlphaLLM.

## 📝 Configuration de l'Application

### Étape 1 : Configure ton logger pour écrire dans un fichier
Dans `log.py`, ajoute un FileHandler:

```python
# Ajouter après le handler console
file_handler = logging.FileHandler('/var/log/alphallm.log')
file_handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)
```

### Étape 2 : Assure les permissions
```bash
sudo mkdir -p /var/log/alphallm
sudo chown -R alphallm:alphallm /var/log/alphallm  # ou ton user
sudo chmod 750 /var/log/alphallm
```

### Étape 3 : Lance l'API avec les logs dirigés vers le fichier
```bash
python main.py 2>&1 | tee /var/log/alphallm/api.log
```

## ✅ Vérification

### Tester Fail2ban
```bash
# Vérifier le statut
sudo fail2ban-client status

# Vérifier les jails AlphaLLM
sudo fail2ban-client status alphallm-ratelimit
sudo fail2ban-client status alphallm-endpoint-abuse
sudo fail2ban-client status alphallm-bruteforce

# Voir les IPs bannies
sudo iptables -L -n | grep -i alphallm
```

### Simuler une violation de rate limit
```bash
# Dans le code test, faire 10 requêtes rapides depuis la même IP
for i in {1..10}; do curl http://localhost:8000/; done
```

L'IP devrait être bannie après 8 violations !

## 🔧 Ajustements pour ton serveur

### Paramètres optimisés (bon CPU + 1GB RAM):

| Paramètre  | Valeur  | Raison                                 |
|------------|---------|----------------------------------------|
| `maxlines` | 500     | Ton CPU peut parser beaucoup de lignes |
| `findtime` | 60-120s | Fenêtres courtes = détection rapide    |
| `maxretry` | 8       | Agressif mais juste                    |
| `bantime`  | 3600s   | 1h standard (modifiable)               |

### Si tu veux plus agressif:
```ini
maxretry = 5        # Ban après 5 violations
bantime = 7200      # 2h de ban
findtime = 60       # Fenêtre 1 min
```

### Si tu veux plus permissif:
```ini
maxretry = 15       # Tolérer 15 violations
bantime = 1800      # 30 min
findtime = 180      # Fenêtre 3 min
```

## 📊 Monitoring

### Afficher les logs Fail2ban en temps réel:
```bash
sudo tail -f /var/log/fail2ban.log | grep alphallm
```

### Compter les bans:
```bash
sudo fail2ban-client status alphallm-ratelimit
```

### Débannir une IP manuellement:
```bash
sudo fail2ban-client set alphallm-ratelimit unbanip 192.168.1.100
```

## 🛡️ Sécurité supplémentaire

### Whitelist les IPs de confiance
Ajoute dans `/etc/fail2ban/jail.d/alphallm.conf`:
```ini
[DEFAULT]
ignoreip = 127.0.0.1/8 192.168.1.0/24 10.0.0.0/8
```

### Désactiver les alertes email (si pas de serveur SMTP)
Remplace dans `jail.conf`:
```ini
action = iptables-multiport[name=AlphaLLM, port="80,443"]
         # Retire la ligne sendmail si pas de SMTP configuré
```

## 🔄 Redémarrage de Fail2ban
```bash
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban  # Auto-start au boot
```

## ❌ Troubleshooting

### Fail2ban ne détecte rien
1. Vérifie que les logs arrivent dans `/var/log/alphallm.log`
2. Test les regex: `sudo fail2ban-regex /var/log/alphallm.log /etc/fail2ban/filter.d/alphallm.conf`
3. Regarde `/var/log/fail2ban.log` pour les erreurs

### Trop de faux positifs
- Baisse `maxretry`
- Augmente `findtime`
- Ajoute les IPs légitimes à `ignoreip`

### iptables saturé
- Nettoie les règles vieilles: `sudo iptables -F`
- Bascule à `nftables` (plus moderne)

---

**Tes 3 jails activées:**
1. ✅ **alphallm-ratelimit** → Détecte les 429 (rate limit)
2. ✅ **alphallm-endpoint-abuse** → Protège image_gen/text_gen
3. ✅ **alphallm-bruteforce** → Détecte les attaques brutes

Avec ton CPU bon + 1GB RAM, zéro impact perfs! 🚀
