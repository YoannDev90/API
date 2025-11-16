# Documentation AlphaLLM API

# 📝 **Language** | [🇬🇧](#english) | [🇫🇷](#français)

---

## English

# AlphaLLM API Documentation

Detailed documentation for developers and advanced users of the AlphaLLM API.

## Table of contents

1. [Overview](#overview)
2. [Advanced Installation](#advanced-installation)
3. [Configuration](#configuration)
4. [Architecture](#architecture)
5. [API Endpoints](#api-endpoints)
6. [Authentication](#authentication)
7. [Model Management](#model-management)
8. [Logging](#logging)
9. [Troubleshooting](#troubleshooting)
10. [Development](#development)

## Overview

AlphaLLM API is a modern FastAPI application that provides a unified interface for:

- Text generation via LLM models
- Image generation via diffusion models
- Image editing with textual descriptions
- Retrieving information about available models

The API uses:
- **FastAPI** : Modern and high-performance web framework
- **Uvicorn** : ASGI server
- **Python 3.9+** : Programming language
- **Grafana** : Monitoring integration (optional)

## Advanced Installation

### With Docker (recommended for production)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:

```bash
docker build -t alphallm-api .
docker run -p 8000:8000 -v $(pwd)/config.toml:/app/config.toml alphallm-api
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/YoannDev90/AlphaLLM-API.git
cd AlphaLLM-API

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run in development mode
python main.py  # reload=true in config.toml
```

## Configuration

### Environment variables

Create a `.env` file at the project root:

```bash
# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=false

# Logging
LOG_LEVEL=INFO
LOG_CONSOLE=true
LOG_GRAFANA=true

# Grafana
GRAFANA_URL=https://logs-prod-012.grafana.net
GRAFANA_API_KEY=your_api_key

# Data
DATA_BASE_URL=http://de5.azurhosts.com:25692/
```

### config.toml file format

```toml
[grafana]
url = "https://logs-prod-012.grafana.net"
# api_key = "your_api_key"  # Optional, can be set via env

[server]
host = "0.0.0.0"
port = 8000
reload = false  # true in development

[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
console = true
grafana = true

[data]
base_url = "http://de5.azurhosts.com:25692/"
timeout = 30
```

## Architecture

### Package structure

```
api/
├── __init__.py
├── api.py                    # Main FastAPI application
└── endpoints/
    ├── __init__.py
    ├── main.py              # Main routes (GET /)
    ├── info.py              # Information (GET /info)
    ├── text_gen.py          # Text generation (POST /text-gen)
    ├── image_gen.py         # Image generation (POST /image-gen)
    ├── image_edit.py        # Image editing (POST /image-edit)
    └── misc.py              # Miscellaneous routes
└── utils/
    ├── app_config.py        # App configuration
    ├── models_utils.py      # Model utilities
    ├── security_utils.py    # Authentication and validation
    └── server_utils.py      # Server utilities
```

### Request flow

```
HTTP Request
    ↓
FastAPI Router (endpoints/)
    ↓
Validation (Pydantic)
    ↓
Security Check (security_utils)
    ↓
Business Logic
    ↓
External API Call (httpx/requests)
    ↓
JSON Response
```

## API Endpoints

### Available endpoints

#### 1. Get API information

```http
GET /info
```

**Response** :
```json
{
  "api_version": "1.0.0",
  "models": {
    "text": ["gpt-3.5-turbo", "gpt-4"],
    "image": ["stable-diffusion", "dall-e"]
  }
}
```

#### 2. Text generation

```http
POST /api/text-gen
Content-Type: application/json

{
  "prompt": "Your message",
  "model": "gpt-3.5-turbo",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Response** :
```json
{
  "text": "Generated text...",
  "model": "gpt-3.5-turbo",
  "tokens_used": 45
}
```

**Optional parameters** :
- `max_tokens` : Maximum number of tokens (default: 100)
- `temperature` : Creativity (0.0-1.0, default: 0.7)
- `top_p` : Nucleus sampling (0.0-1.0, default: 1.0)

#### 3. Image generation

```http
POST /api/image-gen
Content-Type: application/json

{
  "prompt": "An image description",
  "model": "stable-diffusion",
  "width": 512,
  "height": 512,
  "steps": 50
}
```

**Response** :
```json
{
  "image_url": "https://...",
  "model": "stable-diffusion",
  "seed": 12345
}
```

**Optional parameters** :
- `width` : Width (default: 512)
- `height` : Height (default: 512)
- `steps` : Diffusion steps (default: 50)
- `seed` : Seed for reproducibility (optional)

#### 4. Image editing

```http
POST /api/image-edit
Content-Type: multipart/form-data

image: <image file>
prompt: "Desired modifications"
model: "stable-diffusion"
```

**Response** :
```json
{
  "image_url": "https://...",
  "model": "stable-diffusion"
}
```

## Authentication

### Configure authentication (if implemented)

Credentials must be provided in headers:

```bash
curl -X GET "http://localhost:8000/api/text-gen" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Generate a token (example)

```python
from api.utils.security_utils import create_token

token = create_token(user_id="user123")
print(token)
```

## Model Management

### text_models.json file

```json
{
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "openai",
      "enabled": true,
      "description": "Fast and efficient text model"
    },
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai",
      "enabled": true,
      "description": "Advanced text model"
    }
  ]
}
```

### image_models.json file

```json
{
  "models": [
    {
      "id": "stable-diffusion",
      "name": "Stable Diffusion",
      "provider": "stability-ai",
      "enabled": true,
      "description": "Image generation model"
    },
    {
      "id": "dall-e",
      "name": "DALL-E 3",
      "provider": "openai",
      "enabled": true,
      "description": "Advanced image generation model"
    }
  ]
}
```

### Add a new model

1. Edit the appropriate JSON file (`text_models.json` or `image_models.json`)
2. Add the model entry with its configuration
3. Restart the application (or reload if in development mode)

## Logging

### Log levels

- `DEBUG` : Detailed information for diagnosis
- `INFO` : General events
- `WARNING` : Warnings (default)
- `ERROR` : Errors
- `CRITICAL` : Critical errors

### Logging configuration

```toml
[logging]
level = "DEBUG"      # Display DEBUG and higher logs
console = true       # Colored console logs
grafana = true       # Send logs to Grafana
```

### Using logging in your code

```python
from log import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)
```

### Colored log format

```
2024-11-16 10:30:45 - api.endpoints.text_gen - INFO - Request received for gpt-3.5-turbo
```

## Troubleshooting

### Server won't start

```bash
# Check the logs
python main.py

# Check if port is not in use
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Model not found error

```
Error: Model 'gpt-3.5-turbo' not found
```

**Solution** : Verify that the model is configured in the JSON files and enabled.

### Grafana connection issue

Check the error logs and configuration:

```toml
[grafana]
url = "https://logs-prod-012.grafana.net"
api_key = "your_key"  # Add if missing
```

### Slow performance

- Increase the `max_workers` in server configuration
- Check network load to external service
- Monitor via Grafana

## Development

### Linting and formatting

```bash
# Format the code
black api/ main.py config.py log.py

# Check style
flake8 api/ main.py config.py log.py
```

### Unit tests

```bash
# Run tests
pytest

# With coverage
pytest --cov=api --cov-report=html
```

### Test example

```python
import pytest
from fastapi.testclient import TestClient
from api.api import app

client = TestClient(app)

def test_info_endpoint():
    response = client.get("/info")
    assert response.status_code == 200
    assert "models" in response.json()
```

### Contributing

1. Fork the project
2. Create a branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints (`typing`)
- Document public functions with docstrings

```python
def get_model_info(model_id: str) -> dict:
    """
    Get information about a model.
    
    Args:
        model_id: Unique model ID
        
    Returns:
        Dictionary containing model information
        
    Raises:
        ValueError: If the model does not exist
    """
    pass
```

---

<div id="français"></div>

## Français

# Documentation AlphaLLM API

Documentation détaillée pour développeurs et utilisateurs avancés de l'API AlphaLLM.

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation avancée](#installation-avancée)
3. [Configuration](#configuration)
4. [Architecture](#architecture)
5. [Endpoints API](#endpoints-api)
6. [Authentification](#authentification)
7. [Gestion des modèles](#gestion-des-modèles)
8. [Logging](#logging)
9. [Dépannage](#dépannage)
10. [Développement](#développement)

## Vue d'ensemble

AlphaLLM API est une application FastAPI moderne qui fournit une interface unifiée pour :

- La génération de texte via des modèles LLM
- La génération d'images via des modèles de diffusion
- L'édition d'images avec descriptions textuelles
- La récupération d'informations sur les modèles disponibles

L'API utilise :
- **FastAPI** : Framework web moderne et haute performance
- **Uvicorn** : Serveur ASGI
- **Python 3.9+** : Langage de programmation
- **Grafana** : Intégration de monitoring (optionnel)

## Installation avancée

### Avec Docker (recommandé pour la production)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Construire et exécuter :

```bash
docker build -t alphallm-api .
docker run -p 8000:8000 -v $(pwd)/config.toml:/app/config.toml alphallm-api
```

### Installation pour le développement

```bash
# Cloner le dépôt
git clone https://github.com/YoannDev90/AlphaLLM-API.git
cd AlphaLLM-API

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances de développement
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Exécuter en mode développement
python main.py  # reload=true dans config.toml
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Configuration du serveur
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_RELOAD=false

# Logging
LOG_LEVEL=INFO
LOG_CONSOLE=true
LOG_GRAFANA=true

# Grafana
GRAFANA_URL=https://logs-prod-012.grafana.net
GRAFANA_API_KEY=votre_clé_api

# Données
DATA_BASE_URL=http://de5.azurhosts.com:25692/
```

### Format du fichier config.toml

```toml
[grafana]
url = "https://logs-prod-012.grafana.net"
# api_key = "votre_clé_api"  # Optionnel, peut être défini via env

[server]
host = "0.0.0.0"
port = 8000
reload = false  # true en développement

[logging]
level = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
console = true
grafana = true

[data]
base_url = "http://de5.azurhosts.com:25692/"
timeout = 30
```

## Architecture

### Structure des packages

```
api/
├── __init__.py
├── api.py                    # Application FastAPI principale
└── endpoints/
    ├── __init__.py
    ├── main.py              # Routes principales (GET /)
    ├── info.py              # Informations (GET /info)
    ├── text_gen.py          # Génération de texte (POST /text-gen)
    ├── image_gen.py         # Génération d'images (POST /image-gen)
    ├── image_edit.py        # Édition d'images (POST /image-edit)
    └── misc.py              # Routes diverses
└── utils/
    ├── app_config.py        # Configuration de l'application
    ├── models_utils.py      # Utilitaires des modèles
    ├── security_utils.py    # Authentification et validation
    └── server_utils.py      # Utilitaires du serveur
```

### Flux de requête

```
Requête HTTP
    ↓
FastAPI Router (endpoints/)
    ↓
Validation (Pydantic)
    ↓
Security Check (security_utils)
    ↓
Business Logic
    ↓
External API Call (httpx/requests)
    ↓
Réponse JSON
```

## Endpoints API

### Endpoints disponibles

#### 1. Récupérer les informations de l'API

```http
GET /info
```

**Réponse** :
```json
{
  "api_version": "1.0.0",
  "models": {
    "text": ["gpt-3.5-turbo", "gpt-4"],
    "image": ["stable-diffusion", "dall-e"]
  }
}
```

#### 2. Génération de texte

```http
POST /api/text-gen
Content-Type: application/json

{
  "prompt": "Votre message",
  "model": "gpt-3.5-turbo",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Réponse** :
```json
{
  "text": "Texte généré...",
  "model": "gpt-3.5-turbo",
  "tokens_used": 45
}
```

**Paramètres optionnels** :
- `max_tokens` : Nombre maximum de tokens (défaut: 100)
- `temperature` : Créativité (0.0-1.0, défaut: 0.7)
- `top_p` : Nucleus sampling (0.0-1.0, défaut: 1.0)

#### 3. Génération d'images

```http
POST /api/image-gen
Content-Type: application/json

{
  "prompt": "Une description d'image",
  "model": "stable-diffusion",
  "width": 512,
  "height": 512,
  "steps": 50
}
```

**Réponse** :
```json
{
  "image_url": "https://...",
  "model": "stable-diffusion",
  "seed": 12345
}
```

**Paramètres optionnels** :
- `width` : Largeur (défaut: 512)
- `height` : Hauteur (défaut: 512)
- `steps` : Étapes de diffusion (défaut: 50)
- `seed` : Graine pour la reproductibilité (optionnel)

#### 4. Édition d'images

```http
POST /api/image-edit
Content-Type: multipart/form-data

image: <fichier image>
prompt: "Modifications souhaitées"
model: "stable-diffusion"
```

**Réponse** :
```json
{
  "image_url": "https://...",
  "model": "stable-diffusion"
}
```

## Authentification

### Configurer l'authentification (si implémentée)

Les credentials doivent être fournis dans les headers :

```bash
curl -X GET "http://localhost:8000/api/text-gen" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Générer un token (exemple)

```python
from api.utils.security_utils import create_token

token = create_token(user_id="user123")
print(token)
```

## Gestion des modèles

### Fichier text_models.json

```json
{
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "provider": "openai",
      "enabled": true,
      "description": "Modèle de texte rapide et efficace"
    },
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "provider": "openai",
      "enabled": true,
      "description": "Modèle de texte avancé"
    }
  ]
}
```

### Fichier image_models.json

```json
{
  "models": [
    {
      "id": "stable-diffusion",
      "name": "Stable Diffusion",
      "provider": "stability-ai",
      "enabled": true,
      "description": "Modèle de génération d'images"
    },
    {
      "id": "dall-e",
      "name": "DALL-E 3",
      "provider": "openai",
      "enabled": true,
      "description": "Modèle avancé de génération d'images"
    }
  ]
}
```

### Ajouter un nouveau modèle

1. Modifier le fichier JSON approprié (`text_models.json` ou `image_models.json`)
2. Ajouter l'entrée du modèle avec sa configuration
3. Redémarrer l'application (ou recharger si en mode développement)

## Logging

### Niveaux de log

- `DEBUG` : Informations détaillées pour le diagnostic
- `INFO` : Événements généraux
- `WARNING` : Avertissements (défaut)
- `ERROR` : Erreurs
- `CRITICAL` : Erreurs critiques

### Configuration du logging

```toml
[logging]
level = "DEBUG"      # Afficher les logs DEBUG et supérieurs
console = true       # Logs colorés dans la console
grafana = true       # Envoyer les logs à Grafana
```

### Utiliser le logging dans votre code

```python
from log import logger

logger.info("Message d'information")
logger.warning("Message d'avertissement")
logger.error("Message d'erreur", exc_info=True)
```

### Format des logs colorés

```
2024-11-16 10:30:45 - api.endpoints.text_gen - INFO - Requête reçue pour gpt-3.5-turbo
```

## Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier les logs
python main.py

# Vérifier que le port n'est pas utilisé
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Erreur de modèle non trouvé

```
Error: Model 'gpt-3.5-turbo' not found
```

**Solution** : Vérifier que le modèle est configuré dans les fichiers JSON et activé.

### Problème de connexion Grafana

Vérifier les logs d'erreur et la configuration :

```toml
[grafana]
url = "https://logs-prod-012.grafana.net"
api_key = "votre_clé"  # Ajouter si manquant
```

### Performances lentes

- Augmenter le `max_workers` dans la configuration serveur
- Vérifier la charge réseau vers le service externe
- Monitorer via Grafana

## Développement

### Linter et formatage

```bash
# Formater le code
black api/ main.py config.py log.py

# Vérifier le style
flake8 api/ main.py config.py log.py
```

### Tests unitaires

```bash
# Exécuter les tests
pytest

# Avec couverture
pytest --cov=api --cov-report=html
```

### Exemple de test

```python
import pytest
from fastapi.testclient import TestClient
from api.api import app

client = TestClient(app)

def test_info_endpoint():
    response = client.get("/info")
    assert response.status_code == 200
    assert "models" in response.json()
```

### Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Code Style

- Suivre [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utiliser des types hints (`typing`)
- Documenter les fonctions publiques avec des docstrings

```python
def get_model_info(model_id: str) -> dict:
    """
    Récupère les informations d'un modèle.
    
    Args:
        model_id: ID unique du modèle
        
    Returns:
        Dictionnaire contenant les informations du modèle
        
    Raises:
        ValueError: Si le modèle n'existe pas
    """
    pass
```

---

**Dernière mise à jour** : Novembre 2025

Pour plus d'informations, consultez le [README.md](README.md).

---

[⬆ Retour en haut / Back to top](#documentation-alphallm-api)
