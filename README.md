# AlphaLLM API

# 📝 **Language** | [🇬🇧](#english) | [🇫🇷](#français)

---

## English

# AlphaLLM API

A powerful and flexible API for integrating Large Language Models (LLM) and image generation. Built with FastAPI, AlphaLLM API provides a unified interface to access multiple AI models.

## 🚀 Features

- **Text Generation** : Access to multiple LLM models for text content generation
- **Image Generation** : Create images from textual descriptions
- **Image Editing** : Modify existing images with textual instructions
- **RESTful API** : Simple and well-documented interface with FastAPI/Swagger
- **Model Management** : Support for multiple models with flexible configuration
- **Security** : Built-in authentication and request validation
- **Advanced Logging** : Colored logs and Grafana integration

## 📋 Prerequisites

- Python 3.9+
- pip (Python package manager)

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YoannDev90/AlphaLLM-API.git
cd AlphaLLM-API
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Edit the `config.toml` file to adapt the configuration to your environment:

```toml
[server]
host = "0.0.0.0"
port = 8000
reload = false

[logging]
level = "INFO"
console = true
grafana = true

[data]
base_url = "http://your-data-server:port/"
```

## ▶️ Usage

### Start the server

```bash
python main.py
```

The server will start on `http://0.0.0.0:8000` by default.

### Access the Swagger interface

Once the server is running, visit:

```
http://localhost:8000/docs
```

You will find the interactive documentation of all available endpoints.

### Usage examples

#### Text generation

```bash
curl -X POST "http://localhost:8000/api/text-gen" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms",
    "model": "gpt-3.5-turbo"
  }'
```

#### Image generation

```bash
curl -X POST "http://localhost:8000/api/image-gen" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city at sunset",
    "model": "stable-diffusion"
  }'
```

#### Image editing

```bash
curl -X POST "http://localhost:8000/api/image-edit" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@image.png" \
  -F "prompt=Make it brighter"
```

## 📁 Project structure

```
AlphaLLM-API/
├── api/
│   ├── endpoints/          # API endpoints
│   │   ├── image_edit.py   # Image editing
│   │   ├── image_gen.py    # Image generation
│   │   ├── text_gen.py     # Text generation
│   │   ├── info.py         # API information
│   │   ├── misc.py         # Miscellaneous endpoints
│   │   └── main.py         # Main router
│   ├── models/             # Model configuration
│   │   ├── image_models.json
│   │   └── text_models.json
│   ├── utils/              # Utilities
│   │   ├── app_config.py   # App configuration
│   │   ├── models_utils.py # Model utilities
│   │   ├── security_utils.py # Security
│   │   └── server_utils.py # Server utilities
│   └── api.py              # FastAPI entry point
├── main.py                 # Main entry point
├── config.py               # Configuration management
├── config.toml             # Configuration file
├── log.py                  # Logging configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔐 Security

- Input request validation
- Configurable authentication
- Rate limiting recommended
- Check security documentation in `docs.md`

## 🤝 Contributing

Contributions are welcome! Please see the contribution guidelines in `docs.md`.

## 📄 License

This project is under the MIT License. See the `LICENSE` file for more details.

## 📞 Support

For any questions or issues, please open an issue on the GitHub repository.

## ✨ Author

YoannDev90

---

<div id="français"></div>

## Français

# AlphaLLM API

Une API puissante et flexible pour l'intégration de modèles de langage de grande taille (LLM) et de génération d'images. Construite avec FastAPI, AlphaLLM API offre une interface unifiée pour accéder à plusieurs modèles d'IA.

## 🚀 Fonctionnalités

- **Génération de texte** : Accès à plusieurs modèles LLM pour la génération de contenu textuel
- **Génération d'images** : Créez des images à partir de descriptions textuelles
- **Édition d'images** : Modifiez des images existantes avec des instructions textuelles
- **API RESTful** : Interface simple et bien documentée avec FastAPI/Swagger
- **Gestion des modèles** : Support de multiples modèles avec configuration flexible
- **Sécurité** : Authentification et validation des requêtes intégrées
- **Logging avancé** : Logs colorés et intégration Grafana

## 📋 Prérequis

- Python 3.9+
- pip (gestionnaire de paquets Python)

## 🔧 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/YoannDev90/AlphaLLM-API.git
cd AlphaLLM-API
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

Modifiez le fichier `config.toml` pour adapter la configuration à votre environnement :

```toml
[server]
host = "0.0.0.0"
port = 8000
reload = false

[logging]
level = "INFO"
console = true
grafana = true

[data]
base_url = "http://your-data-server:port/"
```

## ▶️ Utilisation

### Démarrer le serveur

```bash
python main.py
```

Le serveur démarrera sur `http://0.0.0.0:8000` par défaut.

### Accéder à l'interface Swagger

Une fois le serveur démarré, visitez :

```
http://localhost:8000/docs
```

Vous trouverez la documentation interactive de toutes les endpoints disponibles.

### Exemples d'utilisation

#### Génération de texte

```bash
curl -X POST "http://localhost:8000/api/text-gen" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain machine learning in simple terms",
    "model": "gpt-3.5-turbo"
  }'
```

#### Génération d'images

```bash
curl -X POST "http://localhost:8000/api/image-gen" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city at sunset",
    "model": "stable-diffusion"
  }'
```

#### Édition d'images

```bash
curl -X POST "http://localhost:8000/api/image-edit" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@image.png" \
  -F "prompt=Make it brighter"
```

## 📁 Structure du projet

```
AlphaLLM-API/
├── api/
│   ├── endpoints/          # Points de terminaison API
│   │   ├── image_edit.py   # Édition d'images
│   │   ├── image_gen.py    # Génération d'images
│   │   ├── text_gen.py     # Génération de texte
│   │   ├── info.py         # Informations de l'API
│   │   ├── misc.py         # Points de terminaison divers
│   │   └── main.py         # Router principal
│   ├── models/             # Configuration des modèles
│   │   ├── image_models.json
│   │   └── text_models.json
│   ├── utils/              # Utilitaires
│   │   ├── app_config.py   # Configuration de l'app
│   │   ├── models_utils.py # Utilitaires des modèles
│   │   ├── security_utils.py # Sécurité
│   │   └── server_utils.py # Utilitaires du serveur
│   └── api.py              # Point d'entrée FastAPI
├── main.py                 # Point d'entrée principal
├── config.py               # Gestion de la configuration
├── config.toml             # Fichier de configuration
├── log.py                  # Configuration du logging
├── requirements.txt        # Dépendances Python
└── README.md               # Ce fichier
```

## 🔐 Sécurité

- Validations des requêtes entrantes
- Authentification configurable
- Rate limiting recommandé
- Vérifiez la documentation de sécurité dans `docs.md`

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez consulter les directives de contribution dans `docs.md`.

## 📄 Licence

Ce projet est sous une licence MIT modifiée. Consultez le fichier `LICENSE` pour plus de détails.

**Restriction importante** : Ce logiciel ne peut pas être publié ou redistribué en tant que projet open-source sans l'autorisation explicite de l'auteur.

## 📞 Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt GitHub.

## ✨ Auteur

YoannDev90

---

**Dernière mise à jour** : Novembre 2025

---

[⬆ Back to top / Retour en haut](#alphallm-api)
