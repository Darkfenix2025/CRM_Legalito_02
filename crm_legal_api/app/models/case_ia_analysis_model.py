from app import db
import datetime

class CaseIAAnalysis(db.Model):
    __tablename__ = 'case_ia_analyses' # Plural para el nombre de la tabla

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Usuario que solicitó el análisis

    # Tipo de análisis realizado por la IA (podría ser un enum o string flexible)
    # Ej: "Reformulacion Hechos", "Analisis Preliminar", "Riesgos Procesales",
    #     "Sugerencia Estrategia", "Resumen Documento", "Borrador Carta Documento", "Borrador Contrato"
    tipo_analisis = db.Column(db.String(100), nullable=False, index=True)

    # El prompt o input específico que el usuario proporcionó para este análisis particular,
    # si es diferente del input principal del caso (ej. un texto a resumir).
    # Podría ser el comando usado, ej. "[ANALIZAR RIESGOS]".
    input_usuario_especifico = db.Column(db.Text, nullable=True)

    # El resultado completo devuelto por la IA
    resultado_ia_generado = db.Column(db.Text, nullable=False)

    # Versión editada o comentada por el usuario sobre el resultado de la IA
    # Esto permite al usuario refinar o corregir la salida de la IA y guardarla.
    resultado_editado_usuario = db.Column(db.Text, nullable=True)

    # Feedback del usuario sobre la utilidad del análisis (opcional)
    # Podría ser una calificación (1-5) o un texto breve.
    # feedback_rating = db.Column(db.Integer)
    # feedback_comments = db.Column(db.Text)

    # Referencia al prompt maestro o versión del prompt usado (opcional, para trazabilidad)
    # prompt_maestro_version = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación
    # El backref 'case_ia_analysis' para la relación con Case se define en case_model.Case.ia_analyses
    # El backref 'requestor_user' para la relación con User se define en user_model.User.ia_analyses


    def __repr__(self):
        return f'<CaseIAAnalysis {self.id} - Case {self.case_id} - Tipo: {self.tipo_analisis}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_ia_analysis.caratula if self.case_ia_analysis else "N/A", # Usar nombre de backref
            'user_id': self.user_id,
            'user_username': self.requestor_user.username if self.requestor_user else "N/A", # Usar nombre de backref
            'tipo_analisis': self.tipo_analisis,
            'input_usuario_especifico': self.input_usuario_especifico,
            'resultado_ia_generado': self.resultado_ia_generado,
            'resultado_editado_usuario': self.resultado_editado_usuario,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
