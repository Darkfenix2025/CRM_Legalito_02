from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.gemini_service import reformular_hechos_con_ia, generar_carta_documento_con_ia # Importar la nueva función
from app.models.case_model import Case # Para obtener contexto del caso y guardar resultados
from app import db

ia_bp = Blueprint('ia_bp', __name__)

@ia_bp.route('/reformular_hechos', methods=['POST'])
@jwt_required()
def handle_reformular_hechos():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'texto_hechos_brutos' not in data:
        return jsonify({"msg": "Falta 'texto_hechos_brutos' en la solicitud"}), 400

    texto_bruto = data['texto_hechos_brutos']
    case_id = data.get('case_id') # Opcional, para dar contexto y guardar

    contexto_caso_dict = None
    if case_id:
        caso = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
        if caso:
            contexto_caso_dict = {
                "caratula": caso.caratula,
                # Se podrían añadir más datos del caso si son útiles para la IA
                # "etapa_procesal": caso.etapa_procesal,
                # "juzgado": caso.juzgado
            }
        else:
            # No es un error fatal si el caso no se encuentra, la IA aún puede procesar el texto.
            # Pero no se guardará el resultado en el caso.
            current_app.logger.warn(f"Caso ID {case_id} no encontrado para usuario {current_user_id} al reformular hechos.")

    # Llamar al servicio de IA
    try:
        # current_app.logger.info(f"Usuario {current_user_id} solicitando reformulación de hechos para caso ID: {case_id if case_id else 'N/A'}.")
        print(f"INFO: Usuario {current_user_id} solicitando reformulación de hechos para caso ID: {case_id if case_id else 'N/A'}.")

        hechos_reformulados = reformular_hechos_con_ia(texto_bruto, contexto_caso=contexto_caso_dict)

        if hechos_reformulados.startswith("Error:"):
            # current_app.logger.error(f"Error de IA al reformular hechos: {hechos_reformulados}")
            print(f"ERROR: Error de IA al reformular hechos: {hechos_reformulados}")
            return jsonify({"msg": "Error al procesar con IA", "error_detail": hechos_reformulados}), 500

        # Si se proporcionó un case_id y el caso existe, guardar el resultado
        if case_id and contexto_caso_dict: # contexto_caso_dict implica que el caso fue encontrado
            caso_a_actualizar = Case.query.get(case_id) # Volver a obtener para asegurar sesión
            if caso_a_actualizar:
                caso_a_actualizar.hechos_reformulados_ia = hechos_reformulados
                caso_a_actualizar.last_activity_at = db.func.now() # Actualizar timestamp
                try:
                    db.session.commit()
                    # current_app.logger.info(f"Hechos reformulados guardados para caso ID {case_id}.")
                    print(f"INFO: Hechos reformulados guardados para caso ID {case_id}.")
                except Exception as e_db:
                    db.session.rollback()
                    # current_app.logger.error(f"Error al guardar hechos reformulados en BD para caso {case_id}: {e_db}")
                    print(f"ERROR: Error al guardar hechos reformulados en BD para caso {case_id}: {e_db}")
                    # No devolver error al cliente por esto, pero loguearlo. El resultado de IA ya se tiene.

        return jsonify({"hechos_reformulados": hechos_reformulados}), 200

    except RuntimeError as r_err: # Error de configuración de Gemini
        # current_app.logger.critical(f"Error crítico en servicio Gemini: {r_err}")
        print(f"CRITICAL: Error crítico en servicio Gemini: {r_err}")
        return jsonify({"msg": "Error interno del servidor de IA (configuración)"}), 503 # Service Unavailable
    except Exception as e:
        # current_app.logger.error(f"Excepción inesperada en handle_reformular_hechos: {e}")
        import traceback
        print(f"ERROR: Excepción inesperada en handle_reformular_hechos: {e}\n{traceback.format_exc()}")
        return jsonify({"msg": "Error interno del servidor al procesar la solicitud de IA"}), 500


@ia_bp.route('/generar_carta_documento', methods=['POST'])
@jwt_required()
def handle_generar_carta_documento():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"msg": "Cuerpo de la solicitud JSON faltante"}), 400

    # Datos necesarios para la CD
    destinatario_nombre = data.get('destinatario_nombre')
    destinatario_domicilio = data.get('destinatario_domicilio')
    cuerpo_reclamo = data.get('cuerpo_reclamo')
    plazo_respuesta = data.get('plazo_respuesta') # Ej. "48 horas", "10 días hábiles"

    if not all([destinatario_nombre, destinatario_domicilio, cuerpo_reclamo]):
        return jsonify({"msg": "Faltan datos obligatorios para la Carta Documento: destinatario_nombre, destinatario_domicilio, cuerpo_reclamo"}), 400

    datos_cd = {
        "destinatario_nombre": destinatario_nombre,
        "destinatario_domicilio": destinatario_domicilio,
        "cuerpo_reclamo": cuerpo_reclamo,
        "plazo_respuesta": plazo_respuesta
    }

    # Contexto del caso (opcional pero muy útil)
    case_id = data.get('case_id')
    contexto_caso_dict = None
    if case_id:
        caso = Case.query.filter_by(id=case_id, user_id=current_user_id).first()
        if caso:
            # Aquí podrías añadir más información del caso que sea relevante para la CD
            # como el nombre del cliente (remitente implícito a través del abogado), etc.
            # El Prompt Maestro debería guiar a la IA sobre cómo usar el contexto del caso.
            contexto_caso_dict = {"caratula": caso.caratula, "cliente_nombre": caso.client.nombre_completo if caso.client else "Cliente del Caso"}
            # También podrías pasar datos del abogado/estudio desde el perfil del usuario.
            # user = User.query.get(current_user_id)
            # contexto_caso_dict['abogado_remitente'] = user.full_name o user.estudio_nombre
            # contexto_caso_dict['domicilio_remitente'] = user.estudio_domicilio
        else:
            current_app.logger.warn(f"Caso ID {case_id} no encontrado para usuario {current_user_id} al generar CD.")

    try:
        # current_app.logger.info(f"Usuario {current_user_id} solicitando generación de CD para caso ID: {case_id if case_id else 'N/A'}.")
        print(f"INFO: Usuario {current_user_id} solicitando generación de CD para caso ID: {case_id if case_id else 'N/A'}.")

        borrador_cd = generar_carta_documento_con_ia(datos_cd, contexto_caso=contexto_caso_dict)

        if borrador_cd.startswith("Error:"):
            # current_app.logger.error(f"Error de IA al generar CD: {borrador_cd}")
            print(f"ERROR: Error de IA al generar CD: {borrador_cd}")
            return jsonify({"msg": "Error al procesar con IA", "error_detail": borrador_cd}), 500

        # Aquí podrías decidir si guardar el borrador de la CD como un nuevo "Documento" asociado al caso.
        # Por ahora, solo lo devolvemos.
        # if case_id and contexto_caso_dict:
        #   ...lógica para crear un nuevo Documento en la BD...

        return jsonify({"carta_documento_borrador": borrador_cd}), 200

    except RuntimeError as r_err:
        # current_app.logger.critical(f"Error crítico en servicio Gemini para CD: {r_err}")
        print(f"CRITICAL: Error crítico en servicio Gemini para CD: {r_err}")
        return jsonify({"msg": "Error interno del servidor de IA (configuración)"}), 503
    except Exception as e:
        # current_app.logger.error(f"Excepción inesperada en handle_generar_carta_documento: {e}")
        import traceback
        print(f"ERROR: Excepción inesperada en handle_generar_carta_documento: {e}\n{traceback.format_exc()}")
        return jsonify({"msg": "Error interno del servidor al procesar la solicitud de IA para CD"}), 500

# Aquí se añadirían más endpoints para otras funcionalidades de IA
# como /resumir_texto, /analizar_caso, /generar_contrato, etc.
# cada uno con su lógica para preparar el prompt y llamar al servicio Gemini.
