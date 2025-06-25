from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config  # Asegúrate que Config esté definida en config.py
import os

# Inicialización de extensiones (sin app aún)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS() # Se configurará en create_app

# Constante para el Prompt Maestro
# (Se asume que el prompt completo está aquí o se carga desde un archivo de forma segura)
# Por brevedad, aquí solo una referencia. En la implementación real, estaría el prompt completo.
IA_MASTER_PROMPT_V3_6 = """PROMPT MAESTRO - AGENTE IA JURÍDICO ARGENTINO - v3.6
Eres una IA avanzada diseñada para actuar como un Agente Jurídico Argentino. [...] (CONTENIDO COMPLETO DEL PROMPT)
[...] CONTEXTO: Eres un Agente IA Jurídico Argentino interactuando con un abogado humano (Darío). [...]"""

def create_app(config_class=Config):
    """
    Factory function para crear y configurar la aplicación Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configurar CORS
    # Esto permite peticiones desde el frontend de React que corre en un puerto diferente.
    # Para desarrollo, permitir localhost del puerto de Vite (ej. 5173 o 3001).
    # Para producción, se debe configurar con el dominio del frontend.
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173') # Vite usa 5173 por defecto

    # Si FRONTEND_URL_ALT existe (ej. para create-react-app que usa 3000 o 3001)
    frontend_url_alt = os.environ.get('FRONTEND_URL_ALT', None)
    origins = [frontend_url]
    if frontend_url_alt:
        origins.append(frontend_url_alt)

    # Si hay una configuración específica de CORS_ORIGINS en .env, usarla
    env_cors_origins = os.environ.get('CORS_ORIGINS')
    if env_cors_origins:
        origins = [origin.strip() for origin in env_cors_origins.split(',')]

    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)


    # Inicializar extensiones con la app
    db.init_app(app)

    # Importar modelos aquí es crucial para que Flask-Migrate los detecte
    # al generar migraciones, especialmente si __init__.py en models está vacío
    # o no importa todos los modelos explícitamente.
    # Al importar el paquete 'models', se ejecuta su __init__.py, que ahora importa todo.
    from . import models

    migrate.init_app(app, db) # Inicializar Migrate DESPUÉS de db y de importar modelos
    jwt.init_app(app)

    # Configurar CORS
    # Esto permite peticiones desde el frontend de React que corre en un puerto diferente.
    # Para desarrollo, permitir localhost del puerto de Vite (ej. 5173 o 3001).
    # Para producción, se debe configurar con el dominio del frontend.
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173') # Vite usa 5173 por defecto

    # Si FRONTEND_URL_ALT existe (ej. para create-react-app que usa 3000 o 3001)
    frontend_url_alt = os.environ.get('FRONTEND_URL_ALT', None)
    origins = [frontend_url]
    if frontend_url_alt:
        origins.append(frontend_url_alt)

    # Si hay una configuración específica de CORS_ORIGINS en .env, usarla
    env_cors_origins = os.environ.get('CORS_ORIGINS')
    if env_cors_origins:
        origins = [origin.strip() for origin in env_cors_origins.split(',')]

    CORS(app, resources={r"/api/*": {"origins": origins}}, supports_credentials=True)


    # Registrar Blueprints (rutas)
    # Los imports se hacen aquí para evitar importaciones circulares con los modelos
    from .routes.auth_routes import auth_bp
    from .routes.client_routes import client_bp
    from .routes.case_routes import case_bp
    from .routes.ia_routes import ia_bp
    from .routes.tag_routes import tag_bp # Asumiendo que se crea tag_routes.py
    from .routes.audience_routes import audience_bp # Asumiendo que se crea audience_routes.py
    from .routes.task_routes import task_bp # Asumiendo que se crea task_routes.py
    # ... otros blueprints para Document, InvolvedParty, Financials ...

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(client_bp, url_prefix='/api/clients')
    app.register_blueprint(case_bp, url_prefix='/api/cases')
    app.register_blueprint(ia_bp, url_prefix='/api/ia')
    app.register_blueprint(tag_bp, url_prefix='/api/tags')
    app.register_blueprint(audience_bp, url_prefix='/api/audiences')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    # ... registrar otros ...

    # Cargar el Prompt Maestro en la configuración de la app para fácil acceso
    app.config['IA_MASTER_PROMPT'] = IA_MASTER_PROMPT_V3_6

    @app.route('/hello')
    def hello():
        return "Hello, CRM Legal API is running!"

    return app
