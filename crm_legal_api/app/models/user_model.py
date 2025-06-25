from app import db  # Importa la instancia de SQLAlchemy desde app/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(db.Model):
    __tablename__ = 'users'  # Nombre explícito de la tabla

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False) # Aumentado para hashes más largos
    full_name = db.Column(db.String(120))

    # Datos del estudio/profesional (ejemplos, se pueden expandir)
    estudio_nombre = db.Column(db.String(150))
    estudio_matricula = db.Column(db.String(50)) # Matrícula principal
    estudio_cuit = db.Column(db.String(20))
    estudio_domicilio = db.Column(db.String(255))
    estudio_telefono = db.Column(db.String(50))
    # Podríamos usar un campo JSON para más flexibilidad si la BD lo soporta bien (PostgreSQL sí)
    # estudio_additional_data = db.Column(db.JSON)

    # Clave API de Gemini (encriptada en un futuro, por ahora texto plano para simplicidad)
    # Considerar almacenar esto de forma más segura si es por usuario.
    # Si es una clave global del sistema, mejor en config o variable de entorno.
    # gemini_api_key = db.Column(db.String(255)) # Comentado por ahora, usar global

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    clients = db.relationship('Client', backref='user', lazy=True, cascade="all, delete-orphan")
    # Relación directa con Casos (un usuario puede tener muchos casos, independientemente del cliente si fuera necesario o para acceso rápido)
    # Esto es adicional a la relación Caso -> Cliente -> Usuario. Directamente Case.user_id apunta aquí.
    cases = db.relationship('Case', foreign_keys='Case.user_id', backref='responsible_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Audiencias (un usuario puede crear/gestionar muchas audiencias)
    audiences = db.relationship('Audience', foreign_keys='Audience.user_id', backref='creator_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Tareas
    tasks = db.relationship('Task', foreign_keys='Task.user_id', backref='assigned_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Documentos
    documents = db.relationship('Document', foreign_keys='Document.user_id', backref='uploader_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Partes Intervinientes
    involved_parties = db.relationship('InvolvedParty', foreign_keys='InvolvedParty.user_id', backref='registrar_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Análisis de IA
    ia_analyses = db.relationship('CaseIAAnalysis', foreign_keys='CaseIAAnalysis.user_id', backref='requestor_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relación con Etiquetas (un usuario es dueño de sus etiquetas)
    tags = db.relationship('Tag', foreign_keys='Tag.user_id', backref='owner_user', lazy='dynamic', cascade="all, delete-orphan")

    # Relaciones con Módulo Financiero
    fees = db.relationship('Fee', foreign_keys='Fee.user_id', backref='user_fee', lazy='dynamic', cascade="all, delete-orphan")
    expenses = db.relationship('Expense', foreign_keys='Expense.user_id', backref='user_expense', lazy='dynamic', cascade="all, delete-orphan")
    invoices = db.relationship('Invoice', foreign_keys='Invoice.user_id', backref='user_invoice', lazy='dynamic', cascade="all, delete-orphan")


    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'estudio_nombre': self.estudio_nombre,
            'estudio_matricula': self.estudio_matricula,
            'estudio_cuit': self.estudio_cuit,
            'estudio_domicilio': self.estudio_domicilio,
            'estudio_telefono': self.estudio_telefono,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
