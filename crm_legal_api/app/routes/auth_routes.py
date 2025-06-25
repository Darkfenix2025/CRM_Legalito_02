from flask import Blueprint, request, jsonify
from app.models.user_model import User
from app import db, jwt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
import datetime

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not username or not email or not password:
        return jsonify({"msg": "Faltan campos obligatorios (username, email, password)"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "El nombre de usuario ya existe"}), 409 # 409 Conflict
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "El email ya está registrado"}), 409

    new_user = User(
        username=username,
        email=email,
        full_name=full_name
    )
    new_user.set_password(password)

    # Datos del estudio (opcionales al registrar, se pueden completar luego)
    new_user.estudio_nombre = data.get('estudio_nombre')
    new_user.estudio_matricula = data.get('estudio_matricula')
    new_user.estudio_cuit = data.get('estudio_cuit')
    new_user.estudio_domicilio = data.get('estudio_domicilio')
    new_user.estudio_telefono = data.get('estudio_telefono')

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Usuario registrado exitosamente", "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al registrar usuario", "error": str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    identifier = data.get('identifier') # Puede ser username o email
    password = data.get('password')

    if not identifier or not password:
        return jsonify({"msg": "Faltan campos 'identifier' o 'password'"}), 400

    user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        return jsonify(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user.to_dict() # Enviar datos del usuario para el frontend
        ), 200
    else:
        return jsonify({"msg": "Credenciales inválidas"}), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id, fresh=False)
    return jsonify(access_token=new_access_token), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Para implementar un logout real del lado del servidor con JWTs,
    # necesitaríamos una lista de denegación (blocklist).
    # Por simplicidad, a menudo el logout se maneja solo en el frontend
    # eliminando el token. Si se requiere invalidación del token del lado del servidor,
    # se debe implementar una solución de blocklist (ej. con Redis).
    # Aquí simulamos un logout que podría añadir el JTI a una blocklist.

    # jti = get_jwt()['jti']
    # blocklist.add(jti) # Suponiendo que 'blocklist' es un set o BD para JTIs revocados

    return jsonify({"msg": "Logout exitoso (token debe ser descartado por el cliente)"}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    return jsonify(user=user.to_dict()), 200

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    # Campos actualizables
    if 'full_name' in data: user.full_name = data['full_name']
    if 'email' in data:
        # Verificar si el nuevo email ya existe para otro usuario
        if data['email'] != user.email and User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "El nuevo email ya está en uso"}), 409
        user.email = data['email']

    # Actualizar datos del estudio
    if 'estudio_nombre' in data: user.estudio_nombre = data.get('estudio_nombre')
    if 'estudio_matricula' in data: user.estudio_matricula = data.get('estudio_matricula')
    if 'estudio_cuit' in data: user.estudio_cuit = data.get('estudio_cuit')
    if 'estudio_domicilio' in data: user.estudio_domicilio = data.get('estudio_domicilio')
    if 'estudio_telefono' in data: user.estudio_telefono = data.get('estudio_telefono')

    # Actualizar contraseña si se provee
    if 'current_password' in data and 'new_password' in data:
        if not user.check_password(data['current_password']):
            return jsonify({"msg": "La contraseña actual es incorrecta"}), 401
        if not data['new_password']:
            return jsonify({"msg": "La nueva contraseña no puede estar vacía"}), 400
        user.set_password(data['new_password'])
    elif 'new_password' in data and 'current_password' not in data:
        # Permitir cambiar contraseña solo si se da la nueva (ej. admin resetea, o primer seteo)
        # Esto requeriría lógica adicional o un endpoint separado si es un admin.
        # Por ahora, para cambio por el propio usuario, se requiere current_password.
        return jsonify({"msg": "Se requiere la contraseña actual para cambiarla"}), 400


    try:
        db.session.commit()
        return jsonify({"msg": "Perfil actualizado exitosamente", "user": user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar perfil", "error": str(e)}), 500

# (Opcional) Callback para verificar si un token ha sido revocado
# @jwt.token_in_blocklist_loader
# def check_if_token_in_blocklist(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     return jti in blocklist_set # Suponiendo que blocklist_set es un set de JTIs revocados.
                                # Esto requiere una implementación de blocklist.

# (Opcional) Mensajes de error personalizados para JWT
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "El token ha expirado"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    return jsonify({"msg": "Token inválido", "error": error_string}), 422 # 422 Unprocessable Entity

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    return jsonify({"msg": "Falta el token de acceso", "error": error_string}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Se requiere un token 'fresh' para esta operación"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "El token ha sido revocado"}), 401
