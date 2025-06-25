import os
from app import create_app, db # Importa create_app y db desde app/__init__.py
# from app.models import User, Client, Case # Descomentar cuando los modelos estén definidos

# Determinar qué configuración usar (development, production, etc.)
# Puedes establecer la variable de entorno FLASK_ENV
# Si no está definida, usará la configuración por defecto (DevelopmentConfig)
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

# Contexto para el shell de Flask (útil para pruebas y debugging)
@app.shell_context_processor
def make_shell_context():
    """
    Permite acceder a la instancia de la app y la bd en el shell de Flask
    sin necesidad de importarlos manualmente.
    Ejemplo: flask shell
    """
    # Descomentar y añadir modelos a medida que se creen
    # return {'app': app, 'db': db, 'User': User, 'Client': Client, 'Case': Case}
    return {'app': app, 'db': db}


if __name__ == '__main__':
    # app.run() lo toma de las variables de entorno FLASK_APP, FLASK_ENV, DEBUG
    # Para ejecutar directamente con `python run.py`, puedes usar:
    # app.run(debug=app.config.get('DEBUG', True), host='0.0.0.0', port=os.environ.get('FLASK_RUN_PORT', 5000))
    # Pero es más común usar `flask run`

    # Si quieres que Flask-Migrate cree las tablas automáticamente al iniciar (si no existen)
    # esto es más para desarrollo rápido, en producción se usan migraciones.
    # with app.app_context():
    #     db.create_all() # Cuidado: no maneja cambios en modelos existentes, para eso son las migraciones

    app.run(host='0.0.0.0', port=int(os.environ.get('FLASK_RUN_PORT', 5000)))
