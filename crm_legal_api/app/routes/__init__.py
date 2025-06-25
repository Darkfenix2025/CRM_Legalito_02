# Este archivo __init__.py puede estar vacío si solo contiene módulos de rutas.
# Opcionalmente, podrías usarlo para importar y registrar todos los blueprints
# si prefieres tener esa lógica aquí en lugar de en app/__init__.py,
# pero mantenerla en app/__init__.py es común para la factory function.

# Ejemplo si quisieras registrar BPs aquí (no recomendado con el patrón factory actual):
# from flask import Blueprint
#
# auth_bp = Blueprint('auth', __name__)
# client_bp = Blueprint('clients', __name__)
# ...
#
# from . import auth_routes, client_routes # Asegúrate que los archivos de rutas importen su BP
#
# def register_blueprints(app):
#     app.register_blueprint(auth_bp, url_prefix='/api/auth')
#     app.register_blueprint(client_bp, url_prefix='/api/clients')
#     ...

pass
