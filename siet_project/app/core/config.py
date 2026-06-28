"""
Configuración centralizada del sistema SIET
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuración de la aplicación SIET"""
    
    # Aplicación
    APP_NAME: str = "SIET - Sistema Inteligente de Evaluación de Tecnoestrés"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./siet.db"
    
    # Seguridad
    SECRET_KEY: str = "tu-clave-secreta-muy-segura-para-siet-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Ponderaciones del Motor Analítico (modificables)
    WEIGHT_TECHNOSTRESS: float = 0.40
    WEIGHT_COGNITIVE: float = 0.35
    WEIGHT_BEHAVIOR: float = 0.25
    
    # Límites cognitivos
    STROOP_MAX_TIME: int = 2000  # ms
    NBACK_STIMULUS_TIME: int = 500  # ms
    NBACK_RESPONSE_TIME: int = 2500  # ms
    DIGIT_SPAN_MIN: int = 3
    DIGIT_SPAN_MAX: int = 9
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
