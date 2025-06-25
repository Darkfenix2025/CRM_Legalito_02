from app import db
import datetime

class InvolvedParty(db.Model):
    __tablename__ = 'involved_parties'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Usuario que registró la parte

    nombre_completo = db.Column(db.String(200), nullable=False)
    rol_en_caso = db.Column(db.String(100), nullable=False, index=True) # Ej: "Actor/Demandante", "Demandado", "Tercero Interesado", "Testigo", "Perito", "Abogado Contraparte"

    # Información de contacto
    domicilio_real = db.Column(db.String(255))
    domicilio_procesal = db.Column(db.String(255)) # Si aplica
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(120))

    # Datos identificatorios
    dni_cuit_cuil = db.Column(db.String(30)) # Para personas físicas o jurídicas

    # Información del abogado (si la parte es un abogado o tiene uno propio que no es el usuario)
    abogado_nombre = db.Column(db.String(200))
    abogado_matricula = db.Column(db.String(50))
    abogado_domicilio_procesal = db.Column(db.String(255))
    abogado_telefono = db.Column(db.String(50))
    abogado_email = db.Column(db.String(120))

    notas = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación
    # El backref 'case_involved_party' para la relación con Case se define en case_model.Case.involved_parties
    # El backref 'registrar_user' para la relación con User se define en user_model.User.involved_parties


    def __repr__(self):
        return f'<InvolvedParty {self.id}: {self.nombre_completo} ({self.rol_en_caso}) - Case {self.case_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_involved_party.caratula if self.case_involved_party else "N/A", # Usar el nombre del backref
            'user_id': self.user_id,
            'user_username': self.registrar_user.username if self.registrar_user else "N/A", # Usar el nombre del backref
            'nombre_completo': self.nombre_completo,
            'rol_en_caso': self.rol_en_caso,
            'domicilio_real': self.domicilio_real,
            'domicilio_procesal': self.domicilio_procesal,
            'telefono': self.telefono,
            'email': self.email,
            'dni_cuit_cuil': self.dni_cuit_cuil,
            'abogado_nombre': self.abogado_nombre,
            'abogado_matricula': self.abogado_matricula,
            'abogado_domicilio_procesal': self.abogado_domicilio_procesal,
            'abogado_telefono': self.abogado_telefono,
            'abogado_email': self.abogado_email,
            'notas': self.notas,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
