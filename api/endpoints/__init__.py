"""
Fichier d'initialisation pour les endpoints de l'API AlphaLLM
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from typing import Optional