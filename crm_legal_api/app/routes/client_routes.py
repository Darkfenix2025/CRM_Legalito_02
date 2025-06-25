from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user_model import User
from app.models.client_model import Client
from app.models.tag_model import Tag # Necesario para manejar etiquetas

client_bp = Blueprint('client_bp', __name__)

# Crear un nuevo cliente
@client_bp.route('', methods=['POST'])
@jwt_required()
def create_client():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('nombre_completo'):
        return jsonify({"msg": "El nombre completo del cliente es requerido"}), 400

    new_client = Client(
        user_id=current_user_id,
        nombre_completo=data['nombre_completo'],
        direccion=data.get('direccion'),
        email=data.get('email'),
        whatsapp=data.get('whatsapp'),
        dni_cuit=data.get('dni_cuit'),
        notas_adicionales=data.get('notas_adicionales')
    )

    # Manejo de etiquetas (opcional al crear)
    tag_names = data.get('tags', []) # Espera una lista de nombres de etiquetas
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
            if not tag: # Si la etiqueta no existe para este usuario, la creamos (o podrías decidir no hacerlo)
                tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color="#cccccc") # Color por defecto
                db.session.add(tag)
                # db.session.flush() # Para obtener el ID si es necesario inmediatamente, aunque no aquí
            new_client.tags.append(tag)

    try:
        db.session.add(new_client)
        db.session.commit()
        return jsonify(new_client.to_dict(include_tags=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear cliente", "error": str(e)}), 500

# Obtener todos los clientes del usuario actual
@client_bp.route('', methods=['GET'])
@jwt_required()
def get_clients():
    current_user_id = get_jwt_identity()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) # Clientes por página
    search_term = request.args.get('search', None, type=str)

    query = Client.query.filter_by(user_id=current_user_id)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Client.nombre_completo.ilike(search_pattern)) |
            (Client.email.ilike(search_pattern)) |
            (Client.dni_cuit.ilike(search_pattern))
        )

    query = query.order_by(Client.nombre_completo.asc())

    paginated_clients = query.paginate(page=page, per_page=per_page, error_out=False)

    clients_data = [client.to_dict(include_tags=True) for client in paginated_clients.items]

    return jsonify({
        "clients": clients_data,
        "total": paginated_clients.total,
        "pages": paginated_clients.pages,
        "current_page": paginated_clients.page,
        "has_next": paginated_clients.has_next,
        "has_prev": paginated_clients.has_prev
    }), 200


# Obtener un cliente específico por ID
@client_bp.route('/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client(client_id):
    current_user_id = get_jwt_identity()
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404
    return jsonify(client.to_dict(include_cases=True, include_tags=True)), 200 # Incluir casos y etiquetas

# Actualizar un cliente existente
@client_bp.route('/<int:client_id>', methods=['PUT'])
@jwt_required()
def update_client(client_id):
    current_user_id = get_jwt_identity()
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    client.nombre_completo = data.get('nombre_completo', client.nombre_completo)
    client.direccion = data.get('direccion', client.direccion)
    client.email = data.get('email', client.email)
    client.whatsapp = data.get('whatsapp', client.whatsapp)
    client.dni_cuit = data.get('dni_cuit', client.dni_cuit)
    client.notas_adicionales = data.get('notas_adicionales', client.notas_adicionales)

    # Actualización de etiquetas
    if 'tags' in data: # Espera una lista de nombres de etiquetas
        tag_names = data['tags']
        client.tags.clear() # Limpiar etiquetas existentes para este cliente
        for tag_name in tag_names:
            tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
            if not tag:
                tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color="#cccccc")
                db.session.add(tag)
            client.tags.append(tag)

    try:
        db.session.commit()
        return jsonify(client.to_dict(include_tags=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar cliente", "error": str(e)}), 500

# Eliminar un cliente
@client_bp.route('/<int:client_id>', methods=['DELETE'])
@jwt_required()
def delete_client(client_id):
    current_user_id = get_jwt_identity()
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404

    try:
        # ON DELETE CASCADE en el modelo Case debería eliminar los casos asociados.
        # Las etiquetas asociadas a través de la tabla de unión también se manejan.
        db.session.delete(client)
        db.session.commit()
        return jsonify({"msg": "Cliente eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar cliente", "error": str(e)}), 500

# --- Rutas para manejar etiquetas de un cliente específico ---

@client_bp.route('/<int:client_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_client(client_id):
    current_user_id = get_jwt_identity()
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404

    data = request.get_json()
    tag_name = data.get('tag_nombre')
    if not tag_name:
        return jsonify({"msg": "Nombre de etiqueta requerido"}), 400

    tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
    if not tag:
        # Opción 1: Crear la etiqueta si no existe
        tag_color = data.get('tag_color', '#cccccc') # Color por defecto
        tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color=tag_color)
        db.session.add(tag)
        # Opción 2: Devolver error si la etiqueta no existe (requiere que el usuario la cree primero globalmente)
        # return jsonify({"msg": "Etiqueta no encontrada. Créala primero."}), 404

    if tag not in client.tags:
        client.tags.append(tag)
        try:
            db.session.commit()
            return jsonify(client.to_dict(include_tags=True)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error al agregar etiqueta al cliente", "error": str(e)}), 500
    else:
        return jsonify({"msg": "La etiqueta ya está asignada a este cliente"}), 409


@client_bp.route('/<int:client_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_client(client_id, tag_id):
    current_user_id = get_jwt_identity()
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404

    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    if not tag:
        return jsonify({"msg": "Etiqueta no encontrada"}), 404

    if tag in client.tags:
        client.tags.remove(tag)
        try:
            db.session.commit()
            return jsonify(client.to_dict(include_tags=True)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error al quitar etiqueta del cliente", "error": str(e)}), 500
    else:
        return jsonify({"msg": "La etiqueta no está asignada a este cliente"}), 404
