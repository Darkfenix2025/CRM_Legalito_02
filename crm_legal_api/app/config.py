import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
# Esto es útil para desarrollo. En producción, las variables de entorno
# suelen configurarse directamente en el servidor o plataforma de despliegue.
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv_path = os.path.join(basedir, '..', '.env') # Sube un nivel para encontrar .env
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Si estás en un subdirectorio de app, puede que necesites ajustar la ruta.
    # Por ejemplo, si config.py está en app/ y .env en el root del proyecto.
    dotenv_path_alt = os.path.join(basedir, '..', '..', '.env') # Sube dos niveles
    if os.path.exists(dotenv_path_alt):
        load_dotenv(dotenv_path_alt)
    else:
        print(f"Advertencia: Archivo .env no encontrado en {dotenv_path} ni en {dotenv_path_alt}")


class Config:
    """Clase base de configuración."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-llave-secreta-muy-dificil-de-adivinar'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'otra-llave-secreta-para-jwt'

    # Configuración para la API de Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # Prompt Maestro (se cargará en app/__init__.py pero podría definirse aquí también)
    # IA_MASTER_PROMPT = "Tu prompt maestro aquí..."

    # Configuración de la base de datos
    # Por defecto usa SQLite si no se especifica DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'crm_dev.db') # Guarda crm_dev.db en el directorio raíz del backend

    # Podríamos añadir más configuraciones aquí, como para email, etc.

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    SQLALCHEMY_ECHO = False # Poner a True para ver las consultas SQL generadas por SQLAlchemy

class TestingConfig(Config):
    """Configuración para pruebas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'crm_test.db') # Base de datos separada para tests
    WTF_CSRF_ENABLED = False # Deshabilitar CSRF para tests de formularios si se usa Flask-WTF

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    # Aquí se deberían usar variables de entorno robustas para producción.
    # Por ejemplo, la DATABASE_URL debería apuntar a un servidor PostgreSQL.
    # SECRET_KEY y JWT_SECRET_KEY deben ser fuertes y únicas.

# Diccionario para seleccionar la configuración basada en una variable de entorno
# Por ejemplo, FLASK_CONFIG=development o FLASK_CONFIG=production
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)

# Función para obtener la configuración actual (se podría usar en create_app)
def get_config():
    config_name = os.getenv('FLASK_ENV', 'default')
    return config_by_name.get(config_name, DevelopmentConfig)
