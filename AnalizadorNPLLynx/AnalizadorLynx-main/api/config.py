"""
Configuración para el microservicio LYNX LCLN
"""
import os
from typing import Dict, Any

class Config:
    """Configuración base"""
    
    # Configuración del servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configuración de logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/lynx-nlp.log")
    
    # Configuración NLP
    MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", 200))
    DEFAULT_MAX_RECOMMENDATIONS = int(os.getenv("DEFAULT_MAX_RECOMMENDATIONS", 10))
    
    # Configuración de corrección ortográfica
    ENABLE_SPELL_CORRECTION = os.getenv("ENABLE_SPELL_CORRECTION", "true").lower() == "true"
    MIN_CORRECTION_CONFIDENCE = float(os.getenv("MIN_CORRECTION_CONFIDENCE", 0.7))
    
    # Configuración de base de datos
    DB_PRODUCTS_PATH = os.getenv("DB_PRODUCTS_PATH", "productos_lynx_escalable.db")
    DB_SYNONYMS_PATH = os.getenv("DB_SYNONYMS_PATH", "sinonimos_lynx.db")
    
    # Configuración de MySQL (para futuro)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "lynx_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "lynx_password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "lynxshop")
    
    # Rate limiting
    RATE_LIMIT_QUERIES_PER_MINUTE = int(os.getenv("RATE_LIMIT_QPM", 100))
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    @classmethod
    def get_mysql_config(cls) -> Dict[str, Any]:
        """Obtener configuración de MySQL"""
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DATABASE
        }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    CORS_ORIGINS = ["https://lynx-shop.com", "https://admin.lynx-shop.com"]

# Mapeo de configuraciones
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config() -> Config:
    """Obtener configuración según el entorno"""
    env = os.getenv("FLASK_ENV", "default")
    return config_map.get(env, DevelopmentConfig)
