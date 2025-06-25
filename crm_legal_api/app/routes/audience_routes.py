from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.case_model import Case
from app.models.audience_model import Audience
import datetime

audience_bp = Blueprint('audience_bp', __name__)

# Crear una nueva audiencia para un caso
@audience_bp.route('/by_case/<int:case_id>', methods=['POST'])
@jwt_required()
def create_audience(case_id):
    current_user_id = get_jwt_identity()

    # Verificar que el caso pertenece al usuario actual
    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado para este usuario"}), 404

    data = request.get_json()
    if not data or not data.get('fecha_hora') or not data.get('descripcion'):
        return jsonify({"msg": "Faltan campos obligatorios (fecha_hora, descripcion)"}), 400

    try:
        fecha_hora_dt = datetime.datetime.fromisoformat(data['fecha_hora'])
    except ValueError:
        return jsonify({"msg": "Formato de fecha_hora inválido. Usar ISO 8601 (ej: YYYY-MM-DDTHH:MM:SS)"}), 400

    new_audience = Audience(
        case_id=case_id,
        user_id=current_user_id, # Usuario que crea la audiencia
        fecha_hora=fecha_hora_dt,
        descripcion=data['descripcion'],
        tipo_audiencia=data.get('tipo_audiencia'),
        ubicacion=data.get('ubicacion'),
        link_virtual=data.get('link_virtual'),
        recordatorio_activo=data.get('recordatorio_activo', False),
        minutos_antes_recordatorio=data.get('minutos_antes_recordatorio', 30),
        notas=data.get('notas')
    )

    case.last_activity_at = datetime.datetime.utcnow() # Actualizar actividad del caso

    try:
        db.session.add(new_audience)
        db.session.add(case) # Para guardar last_activity_at
        db.session.commit()
        return jsonify(new_audience.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al crear audiencia", "error": str(e)}), 500

# Obtener todas las audiencias de un caso específico
@audience_bp.route('/by_case/<int:case_id>', methods=['GET'])
@jwt_required()
def get_audiences_for_case(case_id):
    current_user_id = get_jwt_identity()

    case = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
    if not case:
        return jsonify({"msg": "Caso no encontrado o no autorizado"}), 404

    # Filtros opcionales por rango de fechas
    start_date_str = request.args.get('start_date') # YYYY-MM-DD
    end_date_str = request.args.get('end_date')     # YYYY-MM-DD

    query = Audience.query.filter_by(case_id=case_id, user_id=current_user_id) # También filtrar por user_id en audiencia

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Audience.fecha_hora) >= start_date)
        except ValueError:
            return jsonify({"msg": "Formato de start_date inválido. Usar YYYY-MM-DD"}), 400

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Audience.fecha_hora) <= end_date)
        except ValueError:
            return jsonify({"msg": "Formato de end_date inválido. Usar YYYY-MM-DD"}), 400

    audiences = query.order_by(Audience.fecha_hora.asc()).all()
    return jsonify([audience.to_dict() for audience in audiences]), 200

# Obtener una audiencia específica por su ID
@audience_bp.route('/<int:audience_id>', methods=['GET'])
@jwt_required()
def get_audience(audience_id):
    current_user_id = get_jwt_identity()
    # Asegurarse que la audiencia pertenece a un caso del usuario
    audience = Audience.query.join(Case).filter(
        Audience.id == audience_id,
        Case.user_id == current_user_id,
        Audience.user_id == current_user_id # Y que la audiencia fue creada por el usuario
    ).first()

    if not audience:
        return jsonify({"msg": "Audiencia no encontrada o no autorizada"}), 404
    return jsonify(audience.to_dict()), 200

# Actualizar una audiencia existente
@audience_bp.route('/<int:audience_id>', methods=['PUT'])
@jwt_required()
def update_audience(audience_id):
    current_user_id = get_jwt_identity()
    audience = Audience.query.filter_by(id=audience_id, user_id=current_user_id).first() # Solo el creador puede editar
    if not audience:
        return jsonify({"msg": "Audiencia no encontrada o no autorizado para editar"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    if 'fecha_hora' in data:
        try:
            audience.fecha_hora = datetime.datetime.fromisoformat(data['fecha_hora'])
        except ValueError:
            return jsonify({"msg": "Formato de fecha_hora inválido. Usar ISO 8601"}), 400

    audience.descripcion = data.get('descripcion', audience.descripcion)
    audience.tipo_audiencia = data.get('tipo_audiencia', audience.tipo_audiencia)
    audience.ubicacion = data.get('ubicacion', audience.ubicacion)
    audience.link_virtual = data.get('link_virtual', audience.link_virtual)
    audience.recordatorio_activo = data.get('recordatorio_activo', audience.recordatorio_activo)
    audience.minutos_antes_recordatorio = data.get('minutos_antes_recordatorio', audience.minutos_antes_recordatorio)
    audience.notas = data.get('notas', audience.notas)

    # Actualizar last_activity_at del caso asociado
    if audience.case:
        audience.case.last_activity_at = datetime.datetime.utcnow()

    try:
        db.session.commit()
        return jsonify(audience.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar audiencia", "error": str(e)}), 500

# Eliminar una audiencia
@audience_bp.route('/<int:audience_id>', methods=['DELETE'])
@jwt_required()
def delete_audience(audience_id):
    current_user_id = get_jwt_identity()
    audience = Audience.query.filter_by(id=audience_id, user_id=current_user_id).first() # Solo el creador puede eliminar
    if not audience:
        return jsonify({"msg": "Audiencia no encontrada o no autorizado para eliminar"}), 404

    case_of_audience = audience.case # Guardar referencia al caso antes de eliminar

    try:
        db.session.delete(audience)
        if case_of_audience: # Actualizar last_activity_at del caso
            case_of_audience.last_activity_at = datetime.datetime.utcnow()
        db.session.commit()
        return jsonify({"msg": "Audiencia eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar audiencia", "error": str(e)}), 500

# Obtener todas las audiencias del usuario (para un calendario global, por ejemplo)
@audience_bp.route('/all_for_user', methods=['GET'])
@jwt_required()
def get_all_user_audiences():
    current_user_id = get_jwt_identity()

    start_date_str = request.args.get('start_date') # YYYY-MM-DD
    end_date_str = request.args.get('end_date')     # YYYY-MM-DD

    query = Audience.query.filter_by(user_id=current_user_id)

    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Audience.fecha_hora) >= start_date)
        except ValueError:
            return jsonify({"msg": "Formato de start_date inválido. Usar YYYY-MM-DD"}), 400

    if end_date_str:
        try:
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Audience.fecha_hora) <= end_date)
        except ValueError:
            return jsonify({"msg": "Formato de end_date inválido. Usar YYYY-MM-DD"}), 400

    audiences = query.order_by(Audience.fecha_hora.asc()).all()
    return jsonify([aud.to_dict() for aud in audiences]), 200
