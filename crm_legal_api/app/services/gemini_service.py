import google.generativeai as genai
from flask import current_app # Para acceder a app.config

# Variable global para el modelo, se inicializará una vez
model = None

def configure_gemini():
    """Configura la API de Gemini usando la API Key desde la configuración de Flask."""
    global model
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        # current_app.logger.error("GEMINI_API_KEY no configurada.") # Usar logger de Flask
        print("ERROR: GEMINI_API_KEY no configurada en la aplicación Flask.")
        return False

    try:
        genai.configure(api_key=api_key)
        # Para Gemini Flash, el modelo es 'gemini-1.5-flash' o 'gemini-1.5-flash-latest'
        # Para tareas de texto, generalmente 'gemini-pro' también es una opción si 'flash' no está disponible
        # o si se necesita un modelo más potente (aunque Flash es rápido y costo-efectivo).
        # Verificamos la documentación de Gemini para el nombre exacto del modelo "Flash-Lite"
        # Asumiremos 'gemini-1.5-flash-latest' por ahora.
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        # current_app.logger.info("Gemini API configurada exitosamente con modelo 'gemini-1.5-flash-latest'.")
        print("INFO: Gemini API configurada exitosamente con modelo 'gemini-1.5-flash-latest'.")
        return True
    except Exception as e:
        # current_app.logger.error(f"Error al configurar Gemini API: {e}")
        print(f"ERROR al configurar Gemini API: {e}")
        model = None
        return False

def get_gemini_model():
    """Retorna la instancia del modelo Gemini, configurándola si es necesario."""
    global model
    if model is None:
        if not configure_gemini():
            raise RuntimeError("No se pudo configurar el modelo Gemini. Verifica la API Key y la configuración.")
    return model

def reformular_hechos_con_ia(texto_hechos_brutos, contexto_caso=None):
    """
    Utiliza Gemini para reformular los hechos proporcionados.
    Args:
        texto_hechos_brutos (str): El texto original de los hechos.
        contexto_caso (dict, optional): Información adicional del caso para dar contexto a la IA.
                                         Ej: {'caratula': '...', 'partes': '...'}
    Returns:
        str: El texto de los hechos reformulados por la IA, o un mensaje de error.
    """
    try:
        generative_model = get_gemini_model()

        # Obtener el Prompt Maestro desde la configuración de la app Flask
        # (cargado en app/__init__.py)
        prompt_maestro = current_app.config.get('IA_MASTER_PROMPT', "Eres un asistente legal.")

        # Construir el prompt final para Gemini
        # Aquí es donde el Prompt Maestro v3.6 juega un papel crucial.
        # Se combina con la tarea específica.

        # El prompt maestro ya tiene una sección de "TAREAS" que incluye "Análisis de Casos"
        # y "Redacción de Documentos Legales". La reformulación de hechos cae dentro de esto.
        # Podríamos crear un "comando" implícito o una instrucción específica dentro del
        # contexto del prompt maestro.

        # Ejemplo de cómo podríamos estructurar la solicitud a Gemini:
        # 1. Usar el Prompt Maestro como "system prompt" o parte inicial del prompt del usuario.
        # 2. Añadir la instrucción específica para la tarea de reformulación.
        # 3. Proveer los hechos brutos.
        # 4. Proveer contexto adicional del caso si está disponible.

        # Formato del prompt que se enviará a Gemini:
        full_prompt_parts = []

        # 1. Incluir el Prompt Maestro completo.
        full_prompt_parts.append(prompt_maestro)
        full_prompt_parts.append("\n\n--- TAREA ESPECÍFICA ---\n")
        full_prompt_parts.append("A continuación, se presenta un relato de hechos proporcionado por un cliente. "
                                 "Tu tarea es analizarlo y reformularlo en un lenguaje jurídico claro, preciso y formal, "
                                 "adecuado para ser incorporado en una demanda o presentación judicial en Argentina. "
                                 "Identifica los hechos jurídicamente relevantes, ordénalos cronológicamente si es posible, "
                                 "y elimina redundancias o información no pertinente, manteniendo la fidelidad a la narración original. "
                                 "Si es necesario, indica qué información adicional podría ser útil para completar los hechos.")

        if contexto_caso:
            full_prompt_parts.append("\n\n--- CONTEXTO DEL CASO (si aplica) ---")
            if contexto_caso.get('caratula'):
                full_prompt_parts.append(f"Carátula de referencia: {contexto_caso['caratula']}")
            # Se podrían añadir más datos del caso si son relevantes para la reformulación.
            # Por ejemplo, el tipo de proceso o el objeto principal del reclamo.
            # full_prompt_parts.append(f"Objeto del reclamo: {contexto_caso.get('objeto_reclamo', 'No especificado')}")

        full_prompt_parts.append("\n\n--- HECHOS PROPORCIONADOS POR EL CLIENTE (A REFORMULAR) ---")
        full_prompt_parts.append(texto_hechos_brutos)

        full_prompt_parts.append("\n\n--- HECHOS REFORMULADOS (RESPUESTA ESPERADA) ---")
        full_prompt_parts.append("(Por favor, proporciona aquí los hechos reformulados)")

        final_prompt_for_gemini = "\n".join(full_prompt_parts)

        # current_app.logger.debug(f"Enviando a Gemini para reformular: {final_prompt_for_gemini[:500]}...") # Loguear inicio del prompt
        print(f"DEBUG: Enviando a Gemini para reformular (primeros 500 chars): {final_prompt_for_gemini[:500]}...")

        # Configuración de generación (puede ajustarse)
        generation_config = genai.types.GenerationConfig(
            temperature=0.4, # Un valor más bajo para respuestas más deterministas y formales
            top_p=0.9,
            top_k=30,
            max_output_tokens=2048 # Ajustar según la longitud esperada de los hechos
        )

        response = generative_model.generate_content(
            final_prompt_for_gemini,
            generation_config=generation_config
            # safety_settings=... # Considerar ajustes de seguridad si es necesario
        )

        # current_app.logger.debug(f"Respuesta de Gemini recibida.")
        print("DEBUG: Respuesta de Gemini recibida.")

        if response.parts:
            # Asegurarse de que hay texto en la respuesta
            # Gemini puede devolver múltiples partes, usualmente la primera es el texto.
            # También puede haber 'finish_reason' y 'safety_ratings'.
            # print(f"DEBUG: response.prompt_feedback: {response.prompt_feedback}") # Para ver si el prompt fue bloqueado
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 error_msg = f"Prompt bloqueado por Gemini. Razón: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                 # current_app.logger.warning(error_msg)
                 print(f"WARN: {error_msg}")
                 return f"Error: La solicitud a la IA fue bloqueada. Razón: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"

            generated_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))

            if not generated_text.strip():
                # current_app.logger.warning("Gemini devolvió una respuesta vacía después de un prompt válido.")
                print("WARN: Gemini devolvió una respuesta vacía después de un prompt válido.")
                return "Error: La IA devolvió una respuesta vacía."

            return generated_text.strip()
        else:
            # Esto puede ocurrir si el prompt fue bloqueado por seguridad o si no hubo contenido.
            # Revisar response.prompt_feedback para más detalles.
            block_reason_msg = "Razón desconocida o prompt bloqueado."
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason_msg = response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason
            # current_app.logger.error(f"No se pudo obtener respuesta de Gemini. {block_reason_msg}")
            print(f"ERROR: No se pudo obtener respuesta de Gemini. {block_reason_msg}")
            return f"Error al procesar con IA: No se generó contenido. {block_reason_msg}"

    except RuntimeError as r_err: # Captura el error de get_gemini_model
        # current_app.logger.error(f"Error de ejecución de Gemini Service: {r_err}")
        print(f"ERROR: Error de ejecución de Gemini Service: {r_err}")
        return f"Error de configuración del servicio de IA: {r_err}"
    except Exception as e:
        # current_app.logger.error(f"Error inesperado en reformular_hechos_con_ia: {e}")
        import traceback
        print(f"ERROR: Error inesperado en reformular_hechos_con_ia: {e}\n{traceback.format_exc()}")
        return f"Error inesperado al procesar con IA: {str(e)}"

# Aquí se podrían añadir otras funciones para interactuar con Gemini,
# como generar_carta_documento_con_ia, resumir_texto_con_ia, etc.
# cada una construyendo su `final_prompt_for_gemini` de manera similar.
# Por ejemplo:

def generar_carta_documento_con_ia(datos_cd, contexto_caso=None):
    """
    Genera un borrador de Carta Documento usando Gemini.
    Args:
        datos_cd (dict): Un diccionario con los datos para la CD.
                         Ej: {'destinatario_nombre': '', 'destinatario_domicilio': '',
                              'cuerpo_reclamo': '', 'plazo_respuesta': '48 horas'}
        contexto_caso (dict, optional): Información del caso.
    Returns:
        str: El borrador de la CD o un mensaje de error.
    """
    try:
        generative_model = get_gemini_model()
        prompt_maestro = current_app.config.get('IA_MASTER_PROMPT', "Eres un asistente legal.")

        # Validar datos_cd
        if not all(k in datos_cd for k in ['destinatario_nombre', 'destinatario_domicilio', 'cuerpo_reclamo']):
            return "Error: Faltan datos esenciales para la Carta Documento (destinatario, domicilio, cuerpo del reclamo)."

        full_prompt_parts = [prompt_maestro]
        full_prompt_parts.append("\n\n--- TAREA ESPECÍFICA: BORRADOR CARTA DOCUMENTO ---\n")
        full_prompt_parts.append("Por favor, redacta un borrador de Carta Documento formal y legalmente adecuada para el sistema argentino, utilizando los siguientes datos. "
                                 "Asegúrate de incluir todos los elementos formales necesarios (remitente, destinatario, domicilios, intimación clara, plazo, apercibimiento, lugar, fecha, firma).")

        # Datos del remitente (del abogado/estudio, podrían venir del contexto_caso o config)
        # Por ahora, asumimos que la IA los infiere o el prompt maestro los guía.
        # remitente_nombre = contexto_caso.get('abogado_nombre', 'NOMBRE ABOGADO REMITENTE')
        # remitente_domicilio = contexto_caso.get('abogado_domicilio', 'DOMICILIO REMITENTE')
        # full_prompt_parts.append(f"\nREMITENTE:\nNombre: {remitente_nombre}\nDomicilio: {remitente_domicilio}\n")

        full_prompt_parts.append("\nDATOS PARA LA CARTA DOCUMENTO:")
        full_prompt_parts.append(f"DESTINATARIO:\n  Nombre: {datos_cd['destinatario_nombre']}\n  Domicilio: {datos_cd['destinatario_domicilio']}")
        full_prompt_parts.append(f"\nCUERPO DEL RECLAMO / INTIMACIÓN:\n{datos_cd['cuerpo_reclamo']}")
        if datos_cd.get('plazo_respuesta'):
            full_prompt_parts.append(f"\nPLAZO PARA CUMPLIR/RESPONDER: {datos_cd['plazo_respuesta']}")

        # Contexto adicional del caso si es relevante
        if contexto_caso and contexto_caso.get('caratula'):
            full_prompt_parts.append(f"\nCONTEXTO DEL CASO DE REFERENCIA (si es útil para la redacción): {contexto_caso['caratula']}")

        full_prompt_parts.append("\n\n--- BORRADOR DE CARTA DOCUMENTO (RESPUESTA ESPERADA) ---")
        full_prompt_parts.append("(Por favor, proporciona aquí el texto completo de la Carta Documento)")

        final_prompt_for_gemini = "\n".join(full_prompt_parts)
        # current_app.logger.debug(f"Enviando a Gemini para CD: {final_prompt_for_gemini[:300]}...")
        print(f"DEBUG: Enviando a Gemini para CD (primeros 300 chars): {final_prompt_for_gemini[:300]}...")

        generation_config = genai.types.GenerationConfig(temperature=0.3, max_output_tokens=2048)
        response = generative_model.generate_content(final_prompt_for_gemini, generation_config=generation_config)
        # current_app.logger.debug(f"Respuesta de Gemini para CD recibida.")
        print("DEBUG: Respuesta de Gemini para CD recibida.")

        if response.parts and "".join(part.text for part in response.parts if hasattr(part, 'text')).strip():
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                 error_msg = f"Prompt bloqueado por Gemini. Razón: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
                 print(f"WARN: {error_msg}")
                 return f"Error: La solicitud a la IA fue bloqueada. Razón: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
            return "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
        else:
            block_reason_msg = "Razón desconocida o prompt bloqueado."
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason_msg = response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason
            print(f"ERROR: No se pudo generar CD con Gemini. {block_reason_msg}")
            return f"Error al generar Carta Documento con IA: No se generó contenido. {block_reason_msg}"

    except RuntimeError as r_err:
        print(f"ERROR: Error de ejecución de Gemini Service (CD): {r_err}")
        return f"Error de configuración del servicio de IA: {r_err}"
    except Exception as e:
        import traceback
        print(f"ERROR: Error inesperado en generar_carta_documento_con_ia: {e}\n{traceback.format_exc()}")
        return f"Error inesperado al generar Carta Documento con IA: {str(e)}"
