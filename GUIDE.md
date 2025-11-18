# 🚀 Guide Complet: Du GitHub au Déploiement Azure

AlphaLLM API - Migration complète vers Azure Functions avec CI/CD automatique.

---

## 📊 Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│  1. Push sur GitHub (branche prod)                         │
│         ↓                                                    │
│  2. GitHub Actions déclenche automatiquement                │
│         ↓                                                    │
│  3. Build (install deps, zip artifact)                     │
│         ↓                                                    │
│  4. Login Azure (credentials depuis secrets GitHub)         │
│         ↓                                                    │
│  5. Deploy sur Azure Function App "AlphaLLM"               │
│         ↓                                                    │
│  6. API live sur https://alphallm-api.azurewebsites.net   │
└─────────────────────────────────────────────────────────────┘
```

---

## 1️⃣ Configuration Initiale (Une fois)

### 1.1 Créer la Function App sur Azure

```bash
# Prérequis: Azure CLI installé
az login

# Variables
RESOURCE_GROUP="AlphaLLM-RG"
LOCATION="francecentral"  # 🇫🇷 Région: France (Paris)
APP_NAME="alphallm-api"
STORAGE_ACCOUNT="alphallmstorage"

# Créer le groupe de ressources
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Créer un compte de stockage (nécessaire pour Function App)
az storage account create \
  --name $STORAGE_ACCOUNT \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --sku Standard_LRS

# Créer la Function App
az functionapp create \
  --resource-group $RESOURCE_GROUP \
  --consumption-plan-location $LOCATION \
  --runtime python \
  --runtime-version 3.12 \
  --functions-version 4 \
  --name $APP_NAME \
  --storage-account $STORAGE_ACCOUNT \
  --os-type Linux

echo "✓ Function App créée: $APP_NAME"
```

### 1.2 Obtenir les credentials pour GitHub

```bash
# Créer un Service Principal (pour l'authentification GitHub)
az ad sp create-for-rbac \
  --name "alphallm-github-sp" \
  --role "Contributor" \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP

# Copier la sortie (client_id, password, tenant_id)
```

**Sortie attendue:**
```json
{
  "appId": "00000000-0000-0000-0000-000000000000",
  "displayName": "alphallm-github-sp",
  "password": "xxxxxxxxxxxxxxxxxxxx",
  "tenant": "00000000-0000-0000-0000-000000000000"
}
```

### 1.3 Configurer les Secrets GitHub

1. Aller à: **GitHub → Settings → Secrets and variables → Actions**

2. Ajouter ces secrets (depuis le Service Principal ci-dessus):

| Secret Name                                                       | Valeur                        |
|-------------------------------------------------------------------|-------------------------------|
| `AZUREAPPSERVICE_CLIENTID_A8FB49387A9C456DBE5EA1A6EC23CAA1`       | `appId` du Service Principal  |
| `AZUREAPPSERVICE_TENANTID_BFA22D294095449D872AD632DD0CD69E`       | `tenant` du Service Principal |
| `AZUREAPPSERVICE_SUBSCRIPTIONID_EBDD87DAA7104ECABCE3A6AE78068CC0` | Votre subscription ID Azure   |

**Récupérer la subscription ID:**
```bash
az account show --query id -o tsv
```

### 1.4 Configurer Application Settings sur Azure

```bash
# Ajouter les variables d'environnement à la Function App
# 🇫🇷 Région: francecentral (France - Paris)
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    DATA_SERVICE_BASE_URL="http://de5.azurhosts.com:25692/" \
    FUNCTIONS_WORKER_RUNTIME="python"

# Vérifier la configuration
az functionapp config appsettings list \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP

# ✅ Resources créées en francecentral:
# - Function App: alphallm-api (Paris)
# - Storage Account: alphallmstorage (Paris)
# - Resource Group: AlphaLLM-RG (France)
```

---

## 2️⃣ Structure du Projet

### Fichiers clés

```
AlphaLLM-API/
├── function_app.py              ← Point d'entrée Azure Functions
├── host.json                    ← Config Azure Functions
├── local.settings.json          ← Config locale (dev)
├── requirements.txt             ← Dépendances Python
├── .funcignore                  ← Fichiers exclus du déploiement
│
├── .github/workflows/
│   └── prod_alphallm.yml        ← GitHub Actions CI/CD
│
├── api/
│   ├── endpoints/
│   │   ├── main.py, text_gen.py, image_gen.py, ...
│   │   └── ...
│   │
│   └── utils/
│       ├── azure_config.py      ← Config Azure (variables d'env)
│       ├── app_config.py        ← Config FastAPI
│       └── ...
│
└── [autres fichiers]
```

### Fichiers importants expliqués

#### `function_app.py` (Point d'entrée)
```python
# Crée une app FastAPI wrappée par Azure Functions
fast_app = create_app()  # FastAPI app avec middlewares
app = func.AsgiFunctionApp(app=fast_app, http_auth_level=func.AuthLevel.ANONYMOUS)
```

#### `host.json` (Config Azure Functions)
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "maxTelemetryItemsPerSecond": 20
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "functionTimeout": "00:05:00"
}
```

#### `local.settings.json` (Config locale, ne pas commiter les secrets)
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DATA_SERVICE_BASE_URL": "http://de5.azurhosts.com:25692/"
  }
}
```

#### `requirements.txt` (Dépendances)
```
azure-functions==1.20.0
fastapi==0.104.1
httpx==0.25.2
python-multipart==0.0.6
requests==2.31.0
PyJWT==2.8.0
```

---

## 3️⃣ Workflow GitHub Actions

### Fichier: `.github/workflows/prod_alphallm.yml`

```yaml
name: Build and deploy Python project to Azure Function App - AlphaLLM

on:
  push:
    branches:
      - prod          # ← Déclenche le workflow au push sur 'prod'
  workflow_dispatch:  # ← Permet le déclenchement manuel

env:
  AZURE_FUNCTIONAPP_PACKAGE_PATH: '.'
  PYTHON_VERSION: '3.12'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python version
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Create and start virtual environment
        run: |
          python -m venv venv
          source venv/bin/activate

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Zip artifact for deployment
        run: zip release.zip ./* -r

      - name: Upload artifact for deployment job
        uses: actions/upload-artifact@v4
        with:
          name: python-app
          path: release.zip

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Download artifact from build job
        uses: actions/download-artifact@v4
        with:
          name: python-app

      - name: Unzip artifact for deployment
        run: |
          unzip release.zip
          rm release.zip
        
      - name: Login to Azure
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZUREAPPSERVICE_CLIENTID_A8FB49387A9C456DBE5EA1A6EC23CAA1 }}
          tenant-id: ${{ secrets.AZUREAPPSERVICE_TENANTID_BFA22D294095449D872AD632DD0CD69E }}
          subscription-id: ${{ secrets.AZUREAPPSERVICE_SUBSCRIPTIONID_EBDD87DAA7104ECABCE3A6AE78068CC0 }}

      - name: Deploy to Azure Functions
        uses: Azure/functions-action@v1
        with:
          app-name: 'alphallm-api'
          slot-name: 'Production'
          package: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
```

### Comment ça marche

1. **Trigger**: Un push sur `prod` déclenche le workflow
2. **Build job**: 
   - Checkout le code
   - Setup Python 3.12
   - Install les dépendances
   - Zip le projet
3. **Deploy job** (après Build):
   - Télécharge le zip
   - Unzip et prépare les fichiers
   - **Login Azure** avec les credentials (secrets GitHub)
   - Déploie sur la Function App "alphallm-api"

---

## 4️⃣ Processus de Déploiement Complet

### Étape 1: Développement local

```bash
# Clone le repo
git clone https://github.com/YoannDev90/AlphaLLM-API.git
cd AlphaLLM-API

# Créer venv et installer deps
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Tester localement
func start
# L'API est sur http://localhost:7071
```

### Étape 2: Faire des modifications

```bash
# Faire vos changements dans les endpoints, config, etc.
# Par exemple: api/endpoints/text_gen.py

# Tester localement
func start
# Vérifier que tout marche

# Commiter les changements
git add .
git commit -m "feat: nouvelle fonctionnalité"
```

### Étape 3: Push sur prod

```bash
# Push sur la branche prod (déclenche le workflow)
git push origin main:prod

# Ou, si vous êtes sur main:
git checkout -b prod
git push origin prod
```

**Ou directement depuis GitHub:**
1. Créer une Pull Request vers `prod`
2. Merger la PR
3. Le workflow se déclenche automatiquement

### Étape 4: Monitoring du déploiement

**Sur GitHub:**
1. Aller à: **Actions** dans le repo
2. Voir le workflow en cours: "Build and deploy Python project..."
3. Attendre la completion (~5-10 min)
4. Vérifier que les 2 jobs (build + deploy) sont verts ✅

**Logs du workflow:**
```
Build job:
  ✓ Checkout repository
  ✓ Setup Python version
  ✓ Create and start virtual environment
  ✓ Install dependencies
  ✓ Zip artifact
  ✓ Upload artifact

Deploy job:
  ✓ Download artifact
  ✓ Unzip artifact
  ✓ Login to Azure
  ✓ Deploy to Azure Functions
```

### Étape 5: Vérifier le déploiement

```bash
# Test simple
curl https://alphallm-api.azurewebsites.net/
# Response: {"code":"200","message":"AlphaLLM API","version":"2.0.0",...}

# Voir les logs
az webapp log stream --name alphallm-api --resource-group AlphaLLM-RG
```

---

## 5️⃣ Variables d'Environnement

### Local (`local.settings.json`)

```json
{
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DATA_SERVICE_BASE_URL": "http://de5.azurhosts.com:25692/"
  }
}
```

### Production (Azure Portal - francecentral 🇫🇷)

Function App → **Settings** → **Configuration** → **Application settings**

| Setting                    | Valeur                            |
|----------------------------|-----------------------------------|
| `DATA_SERVICE_BASE_URL`    | `http://de5.azurhosts.com:25692/` |
| `FUNCTIONS_WORKER_RUNTIME` | `python`                          |
| `REGION`                   | `francecentral` (Paris)           |

**Comment les ajouter:**

```bash
# Ajouter une variable (exemple)
az functionapp config appsettings set \
  --name alphallm-api \
  --resource-group AlphaLLM-RG \
  --settings \
    CUSTOM_VAR="ma_valeur"

# Ressources en France:
# Location: francecentral (Paris)
# Région: Europe
```

---

## 6️⃣ Logging et Monitoring

### Local

```bash
func start
# Les logs s'affichent dans la console
```

### Production (Application Insights)

#### Via Azure Portal
1. Function App → **Monitoring** → **Application Insights**
2. Cliquer sur le lien Application Insights
3. **Logs** → Écrire une requête KQL

#### Exemples de requêtes KQL

```kusto
# Tous les logs récents
traces | order by timestamp desc | limit 50

# Erreurs seulement
traces | where severityLevel >= 3 | order by timestamp desc

# Requêtes HTTP
requests | order by timestamp desc | limit 20

# Logs contenant un mot-clé
traces | where message contains "alphallm-api" | order by timestamp desc
```

#### Voir les logs en live

```bash
az webapp log stream --name alphallm-api --resource-group AlphaLLM-RG
```

---

## 7️⃣ Credentials et Secrets

### Service Principal (pour GitHub Actions)

Créé lors de la setup initiale:

```bash
# Afficher le Service Principal
az ad sp show --id YOUR_SERVICE_PRINCIPAL_ID

# Réinitialiser le password si oublié
az ad sp credential reset --id YOUR_SERVICE_PRINCIPAL_ID
```

### Secrets GitHub

Stockés dans: **Settings → Secrets and variables → Actions**

```
AZUREAPPSERVICE_CLIENTID_...        = appId du Service Principal
AZUREAPPSERVICE_TENANTID_...         = tenant du Service Principal
AZUREAPPSERVICE_SUBSCRIPTIONID_...   = subscription ID Azure
```

**Ne jamais commiter ces secrets!**

### Gestion des secrets en production

**Pour les secrets sensibles (API keys, tokens, etc.):**

Option 1: Azure KeyVault (recommandé)
```bash
# Créer un KeyVault
az keyvault create --name alphallm-kv --resource-group AlphaLLM-RG

# Ajouter un secret
az keyvault secret set --vault-name alphallm-kv --name my-secret --value "valeur-secrète"

# Lier à la Function App
az functionapp identity assign --name alphallm-api --resource-group AlphaLLM-RG
az keyvault set-policy --name alphallm-kv --object-id <function-app-identity-object-id> --secret-permissions get
```

Option 2: Application Settings (simple pour développement)
```bash
az functionapp config appsettings set --name alphallm-api --resource-group AlphaLLM-RG --settings MY_SECRET="valeur"
```

---

## 8️⃣ Troubleshooting

### Le déploiement échoue sur GitHub Actions

**Problème**: Workflow en rouge ❌

**Solutions**:
1. Vérifier les secrets GitHub sont bien configurés
2. Vérifier la subscription ID est correcte
3. Vérifier le Service Principal a les bonnes permissions
4. Voir les logs du workflow → Actions → Run details

### Erreur 404 après déploiement

**Problème**: `curl https://alphallm-api.azurewebsites.net/` retourne 404

**Solutions**:
1. Attendre 2-3 minutes après le déploiement
2. Vérifier que `function_app.py` existe et est valide
3. Vérifier que `requirements.txt` a toutes les dépendances
4. Vérifier les logs: `az webapp log stream --name alphallm-api --resource-group AlphaLLM-RG`

### Logs n'apparaissent pas dans Application Insights

**Solutions**:
1. Vérifier que Application Insights est lié à la Function App
2. Attendre 5-10 secondes après une requête
3. Faire une requête à l'API (pour générer des logs)
4. Rafraîchir la page Application Insights

### ModuleNotFoundError lors du déploiement

**Problème**: "No module named 'azure.functions'"

**Solution**: Vérifier que `requirements.txt` a `azure-functions==1.20.0`

---

## 9️⃣ Checklist de Déploiement

```
CONFIGURATION INITIALE:
☐ Service Principal créé sur Azure
☐ Function App créée (alphallm-api)
☐ Secrets GitHub configurés (3 secrets)
☐ Application Settings Azure configurés
☐ Application Insights lié (optionnel mais recommandé)

CODE:
☐ function_app.py existe au root
☐ requirements.txt a azure-functions et fastapi
☐ .funcignore bien configuré
☐ local.settings.json pour développement local

GITHUB:
☐ Branche 'prod' existe
☐ Workflow prod_alphallm.yml existe et est valid
☐ Code commité et pushe sur 'prod'

DÉPLOIEMENT:
☐ GitHub Actions workflow se déclenche
☐ Build job complète ✓
☐ Deploy job complète ✓
☐ API répond sur https://alphallm-api.azurewebsites.net/
☐ Logs visibles dans Application Insights

POST-DÉPLOIEMENT:
☐ Tester les endpoints
☐ Vérifier les logs
☐ Configurer les alertes (optionnel)
```

---

## 🔟 Commandes Utiles

```bash
# === CONFIGURATION AZURE (Région: francecentral 🇫🇷) ===

# Lister les Function Apps
az functionapp list --resource-group AlphaLLM-RG --output table

# Voir les settings
az functionapp config appsettings list --name alphallm-api --resource-group AlphaLLM-RG

# Redémarrer la Function App
az functionapp restart --name alphallm-api --resource-group AlphaLLM-RG

# Voir les logs en live (streaming)
az webapp log stream --name alphallm-api --resource-group AlphaLLM-RG

# === DÉVELOPPEMENT LOCAL ===

# Démarrer localement
func start

# Initialiser un nouveau projet Azure Functions (non-nécessaire ici)
# func init --python

# === GITHUB ===

# Voir l'historique des workflows
gh run list --repo YoannDev90/AlphaLLM-API

# Voir les détails d'un workflow
gh run view <run-id> --repo YoannDev90/AlphaLLM-API

# === DÉPLOIEMENT MANUEL (si besoin) ===

# Déployer directement (sans GitHub Actions)
func azure functionapp publish alphallm-api
```

---

## 📚 Ressources

- [Azure Functions Python Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure Functions + FastAPI](https://learn.microsoft.com/en-us/samples/azure-samples/azure-functions-python-fastapi/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Application Insights KQL](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)

---

## 💡 Résumé

1. **Configuration une fois**: Service Principal + Secrets GitHub + Function App
2. **Développement**: `git push origin main:prod` déclenche le déploiement
3. **Monitoring**: Application Insights collecte automatiquement les logs
4. **Facile**: Aucune configuration manuelle après le premier setup

**Le workflow est complètement automatisé: push → build → deploy ✅**

