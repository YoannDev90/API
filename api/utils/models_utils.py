"""
Utilitaires pour les modèles
"""
import json
from pathlib import Path

def load_models_data(model_type: str):
    """Charge les données des modèles depuis les fichiers JSON"""
    model_files = {
        "text": "text_models.json",
        "image": "image_models.json"
    }
    
    if model_type not in model_files:
        raise ValueError(f"Type de modèle invalide: {model_type}")
    
    file_path = Path(__file__).parent.parent / "models" / model_files[model_type]
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Fichier de modèles non trouvé: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Erreur de décodage JSON dans {file_path}")