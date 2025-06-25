from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user_model import User
from app.models.client_model import Client
from app.models.case_model import Case
from app.models.tag_model import Tag # Para manejar etiquetas de casos
import datetime

case_bp = Blueprint('case_bp', __name__)

# Crear un nuevo caso para un cliente específico
@case_bp.route('/by_client/<int:client_id>', methods=['POST'])
@jwt_required()
def create_case(client_id):
    current_user_id = get_jwt_identity()

    # Verificar que el cliente pertenece al usuario actual
    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado para este usuario"}), 404

    data = request.get_json()
    if not data or not data.get('caratula'):
        return jsonify({"msg": "La carátula del caso es requerida"}), 400

    new_case = Case(
        client_id=client_id,
        user_id=current_user_id, # Asociar también el caso directamente al usuario
        caratula=data['caratula'],
        numero_expediente=data.get('numero_expediente'),
        anio_expediente=data.get('anio_expediente'),
        juzgado=data.get('juzgado'),
        jurisdiccion=data.get('jurisdiccion'),
        etapa_procesal=data.get('etapa_procesal'),
        descripcion_hechos_brutos=data.get('descripcion_hechos_brutos'),
        # hechos_reformulados_ia se llenará a través de la función de IA
        notas_generales=data.get('notas_generales'),
        ruta_carpeta_documentos_local=data.get('ruta_carpeta_documentos_local'),
        last_activity_at=datetime.datetime.utcnow()
    )

    # Manejo de etiquetas para el caso (opcional al crear)
    tag_names = data.get('tags', []) # Espera una lista de nombres de etiquetas
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
            if not tag:
                tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color="#aabbcc") # Color por defecto
                db.session.add(tag)
            new_case.tags.append(tag)

    try:
        db.session.add(new_case)
        db.session.commit()
        return jsonify(new_case.to_dict(include_tags=True, include_client=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear caso", "error": str(e)}), 500

# Obtener todos los casos de un cliente específico
@case_bp.route('/by_client/<int:client_id>', methods=['GET'])
@jwt_required()
def get_cases_for_client(client_id):
    current_user_id = get_jwt_identity()

    client = Client.query.filter_by(id=client_id, user_id=current_user_id).first()
    if not client:
        return jsonify({"msg": "Cliente no encontrado o no autorizado"}), 404

    # Paginación para casos
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_term = request.args.get('search', None, type=str)

    query = Case.query.filter_by(client_id=client_id, user_id=current_user_id) # Asegurar que el caso también es del usuario

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            (Case.caratula.ilike(search_pattern)) |
            (Case.numero_expediente.ilike(search_pattern)) |
            (Case.juzgado.ilike(search_pattern))
        )

    query = query.order_by(Case.last_activity_at.desc()) # O por caratula, fecha_creacion, etc.

    paginated_cases = query.paginate(page=page, per_page=per_page, error_out=False)

    cases_data = [case.to_dict_short() for case in paginated_cases.items] # Usar to_dict_short para listas

    return jsonify({
        "cases": cases_data,
        "total": paginated_cases.total,
        "pages": paginated_cases.pages,
        "current_page": paginated_cases.page
    }), 200

# Obtener un caso específico por su ID
@case_bp.route('/<int:case_id>', methods=['GET'])
@jwt_required()
def get_case(case_id):
    current_user_id = get_jwt_identity()
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404
    # Devolver el diccionario completo, incluyendo cliente y etiquetas
    return jsonify(case.to_dict(include_tags=True, include_client=True)), 200

# Actualizar un caso existente
@case_bp.route('/<int:case_id>', methods=['PUT'])
@jwt_required()
def update_case(case_id):
    current_user_id = get_jwt_identity()
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    case.caratula = data.get('caratula', case.caratula)
    case.numero_expediente = data.get('numero_expediente', case.numero_expediente)
    case.anio_expediente = data.get('anio_expediente', case.anio_expediente)
    case.juzgado = data.get('juzgado', case.juzgado)
    case.jurisdiccion = data.get('jurisdiccion', case.jurisdiccion)
    case.etapa_procesal = data.get('etapa_procesal', case.etapa_procesal)
    case.descripcion_hechos_brutos = data.get('descripcion_hechos_brutos', case.descripcion_hechos_brutos)
    case.hechos_reformulados_ia = data.get('hechos_reformulados_ia', case.hechos_reformulados_ia) # Permitir actualizarlo
    case.notas_generales = data.get('notas_generales', case.notas_generales)
    case.ruta_carpeta_documentos_local = data.get('ruta_carpeta_documentos_local', case.ruta_carpeta_documentos_local)
    case.last_activity_at = datetime.datetime.utcnow() # Actualizar timestamp de actividad

    # Actualización de etiquetas para el caso
    if 'tags' in data:
        tag_names = data['tags']
        case.tags.clear()
        for tag_name in tag_names:
            tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
            if not tag:
                tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color="#aabbcc")
                db.session.add(tag)
            case.tags.append(tag)

    try:
        db.session.commit()
        return jsonify(case.to_dict(include_tags=True, include_client=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar caso", "error": str(e)}), 500

# Eliminar un caso
@case_bp.route('/<int:case_id>', methods=['DELETE'])
@jwt_required()
def delete_case(case_id):
    current_user_id = get_jwt_identity()
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404

    try:
        # ON DELETE CASCADE en los modelos relacionados (audiencias, tareas, etc.) debería manejarlos.
        db.session.delete(case)
        db.session.commit()
        return jsonify({"msg": "Caso eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar caso", "error": str(e)}), 500


# --- Rutas para manejar etiquetas de un caso específico ---
# (Similares a las de cliente, pero para casos)

@case_bp.route('/<int:case_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_case(case_id):
    current_user_id = get_jwt_identity()
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404

    data = request.get_json()
    tag_name = data.get('tag_nombre')
    if not tag_name:
        return jsonify({"msg": "Nombre de etiqueta requerido"}), 400

    tag = Tag.query.filter_by(user_id=current_user_id, nombre=tag_name.strip().lower()).first()
    if not tag:
        tag_color = data.get('tag_color', '#aabbcc')
        tag = Tag(user_id=current_user_id, nombre=tag_name.strip().lower(), color=tag_color)
        db.session.add(tag)

    if tag not in case.tags:
        case.tags.append(tag)
        try:
            db.session.commit()
            return jsonify(case.to_dict(include_tags=True)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error al agregar etiqueta al caso", "error": str(e)}), 500
    else:
        return jsonify({"msg": "La etiqueta ya está asignada a este caso"}), 409


@case_bp.route('/<int:case_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_case(case_id, tag_id):
    current_user_id = get_jwt_identity()
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404

    tag = Tag.query.filter_by(id=tag_id, user_id=current_user_id).first()
    if not tag:
        return jsonify({"msg": "Etiqueta no encontrada"}), 404

    if tag in case.tags:
        case.tags.remove(tag)
        try:
            db.session.commit()
            return jsonify(case.to_dict(include_tags=True)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Error al quitar etiqueta del caso", "error": str(e)}), 500
    else:
        return jsonify({"msg": "La etiqueta no está asignada a este caso"}), 404
