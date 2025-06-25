from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tag_model import Tag

tag_bp = Blueprint('tag_bp', __name__)

# Crear una nueva etiqueta global para el usuario
@tag_bp.route('', methods=['POST'])
@jwt_required()
def create_tag():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('nombre'):
        return jsonify({"msg": "El nombre de la etiqueta es requerido"}), 400

    nombre = data['nombre'].strip().lower() # Guardar en minúsculas para consistencia
    color = data.get('color', '#cccccc') # Color por defecto
    descripcion = data.get('descripcion')

    # Verificar si ya existe una etiqueta con el mismo nombre para este usuario
    existing_tag = Tag.query.filter_by(user_id=current_user_id, nombre=nombre).first()
    if existing_tag:
        return jsonify({"msg": f"La etiqueta '{nombre}' ya existe para este usuario"}), 409

    new_tag = Tag(
        user_id=current_user_id,
        nombre=nombre,
        color=color,
        descripcion=descripcion
    )

    try:
        db.session.add(new_tag)
        db.session.commit()
        return jsonify(new_tag.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear etiqueta", "error": str(e)}), 500

# Obtener todas las etiquetas globales del usuario actual
@tag_bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    current_user_id = get_jwt_identity()

    # Opcional: Paginación si un usuario puede tener muchísimas etiquetas globales
    # page = request.args.get('page', 1, type=int)
    # per_page = request.args.get('per_page', 20, type=int) # Ajustar según necesidad
    # query = Tag.query.filter_by(user_id=current_user_id).order_by(Tag.nombre.asc())
    # paginated_tags = query.paginate(page=page, per_page=per_page, error_out=False)
    # tags_data = [tag.to_dict() for tag in paginated_tags.items]
    # return jsonify({
    #     "tags": tags_data,
    #     "total": paginated_tags.total,
    #     "pages": paginated_tags.pages,
    #     "current_page": paginated_tags.page
    # }), 200

    tags = Tag.query.filter_by(user_id=current_user_id).order_by(Tag.nombre.asc()).all()
    return jsonify([tag.to_dict() for tag in tags]), 200


# Obtener una etiqueta específica por ID
@tag_bp.route('/<int:tag_id>', methods=['GET'])
@jwt_required()
def get_tag(tag_id):
    current_user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    if not tag:
        return jsonify({"msg": "Etiqueta no encontrada o no autorizada"}), 404
    return jsonify(tag.to_dict()), 200

# Actualizar una etiqueta existente
@tag_bp.route('/<int:tag_id>', methods=['PUT'])
@jwt_required()
def update_tag(tag_id):
    current_user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    if not tag:
        return jsonify({"msg": "Etiqueta no encontrada o no autorizada"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    new_nombre = data.get('nombre', tag.nombre).strip().lower()

    # Verificar si el nuevo nombre ya existe para otra etiqueta del mismo usuario
    if new_nombre != tag.nombre and \
       Tag.query.filter(Tag.user_id == current_user_id, Tag.nombre == new_nombre, Tag.id != tag_id).first():
        return jsonify({"msg": f"Ya existe otra etiqueta con el nombre '{new_nombre}'"}), 409

    tag.nombre = new_nombre
    tag.color = data.get('color', tag.color)
    tag.descripcion = data.get('descripcion', tag.descripcion)

    try:
        db.session.commit()
        return jsonify(tag.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar etiqueta", "error": str(e)}), 500

# Eliminar una etiqueta global
@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def delete_tag(tag_id):
    current_user_id = get_jwt_identity()
    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    if not tag:
        return jsonify({"msg": "Etiqueta no encontrada o no autorizada"}), 404

    try:
        # Las relaciones con client_tags y case_tags deberían eliminarse automáticamente
        # si las tablas de asociación tienen ON DELETE CASCADE en sus claves foráneas
        # o si SQLAlchemy maneja la eliminación de la relación 'secondary'.
        # Si no, habría que eliminar las asociaciones manualmente:
        # client_tags_association.delete().where(client_tags_association.c.tag_id == tag_id)
        # case_tags_association.delete().where(case_tags_association.c.tag_id == tag_id)
        # Sin embargo, SQLAlchemy con `db.relationship(secondary=...)` suele manejar bien esto.

        db.session.delete(tag)
        db.session.commit()
        return jsonify({"msg": "Etiqueta eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar etiqueta. Asegúrate que no esté en uso o revisa las cascadas.", "error": str(e)}), 500
        # Si hay error de FK, es porque la etiqueta está en uso y no hay ON DELETE CASCADE en las tablas de unión.
        # El modelo Tag actual no define cascade para las relaciones inversas 'clients_associated' y 'cases_associated'
        # porque son backrefs de relaciones many-to-many. La eliminación de la etiqueta debería
        # hacer que las entradas en las tablas de asociación se eliminen. Si la BD no lo hace
        # automáticamente (SQLite podría no hacerlo por defecto sin PRAGMA foreign_keys=ON y FKs bien definidas),
        # tendríamos que iterar y quitarla de client.tags y case.tags.
        # Pero con SQLAlchemy, db.session.delete(tag) debería ser suficiente si las relaciones
        # están bien configuradas. El problema podría surgir si la BD a nivel de DDL no tiene las cascadas.
        # Para SQLite, las cascadas en tablas de asociación many-to-many pueden ser complicadas de asegurar
        # solo con SQLAlchemy sin FKs explícitas con ON DELETE CASCADE en la DDL de la tabla de asociación.
        # Por ahora, confiamos en que SQLAlchemy maneje la eliminación de las asociaciones.
        # Si falla, el mensaje de error de la BD indicará una restricción de FK.
