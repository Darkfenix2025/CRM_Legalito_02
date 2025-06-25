from app import db
import datetime

class Audience(db.Model):
    __tablename__ = 'audiences'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Usuario que creó/gestiona la audiencia

    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_audiencia = db.Column(db.String(100)) # Ej: "Testimonial", "Confesional", "Conciliación", "Vista de Causa"
    ubicacion = db.Column(db.String(255)) # Puede ser física o virtual (ej. "Sala 3, Tribunales" o "Zoom")
    link_virtual = db.Column(db.String(500))

    recordatorio_activo = db.Column(db.Boolean, default=False)
    minutos_antes_recordatorio = db.Column(db.Integer, default=30)
    # fecha_recordatorio_enviado = db.Column(db.DateTime, nullable=True) # Para evitar enviar múltiples veces

    notas = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación
    # El backref 'case_audience' para la relación con Case se define en case_model.Case.audiences
    # El backref 'creator_user' para la relación con User se define en user_model.User.audiences

    def __repr__(self):
        return f'<Audience {self.id} - Case {self.case_id} - {self.fecha_hora.strftime("%Y-%m-%d %H:%M")}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_audience.caratula if self.case_audience else "N/A", # Usar el nombre del backref
            'user_id': self.user_id,
            'user_username': self.creator_user.username if self.creator_user else "N/A", # Usar el nombre del backref
            'fecha_hora': self.fecha_hora.isoformat(),
            'descripcion': self.descripcion,
            'tipo_audiencia': self.tipo_audiencia,
            'ubicacion': self.ubicacion,
            'link_virtual': self.link_virtual,
            'recordatorio_activo': self.recordatorio_activo,
            'minutos_antes_recordatorio': self.minutos_antes_recordatorio,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
