from app import db
import datetime

# Tabla de asociación para la relación muchos-a-muchos entre Caso y Etiqueta
case_tags_association = db.Table('case_tags',
    db.Column('case_id', db.Integer, db.ForeignKey('cases.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Case(db.Model):
    __tablename__ = 'cases'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Para identificar al usuario/abogado responsable

    caratula = db.Column(db.String(255), nullable=False, index=True)
    numero_expediente = db.Column(db.String(50), index=True)
    anio_expediente = db.Column(db.String(10)) # O Integer si siempre es numérico
    juzgado = db.Column(db.String(150))
    jurisdiccion = db.Column(db.String(100))
    etapa_procesal = db.Column(db.String(100))

    # Hechos
    descripcion_hechos_brutos = db.Column(db.Text) # Hechos según el cliente o primera carga
    hechos_reformulados_ia = db.Column(db.Text)   # Hechos procesados por IA

    notas_generales = db.Column(db.Text)
    ruta_carpeta_documentos_local = db.Column(db.String(500)) # Ruta en el servidor local

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_activity_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True) # Para alertas de inactividad

    # Relaciones
    # El backref 'client_associated_case' para la relación con Client se define en client_model.Client.cases
    # El backref 'responsible_user' para la relación con User se define en user_model.User.cases

    audiences = db.relationship('Audience', foreign_keys='Audience.case_id', backref='case_audience', lazy='dynamic', cascade="all, delete-orphan")
    tasks = db.relationship('Task', foreign_keys='Task.case_id', backref='case_task', lazy='dynamic', cascade="all, delete-orphan")
    documents = db.relationship('Document', foreign_keys='Document.case_id', backref='case_document', lazy='dynamic', cascade="all, delete-orphan")
    involved_parties = db.relationship('InvolvedParty', foreign_keys='InvolvedParty.case_id', backref='case_involved_party', lazy='dynamic', cascade="all, delete-orphan")
    ia_analyses = db.relationship('CaseIAAnalysis', foreign_keys='CaseIAAnalysis.case_id', backref='case_ia_analysis', lazy='dynamic', cascade="all, delete-orphan")

    tags = db.relationship('Tag', secondary=case_tags_association,
                           lazy='subquery',
                           backref=db.backref('cases_associated', lazy='dynamic'))

    # Relaciones con el módulo financiero
    fees = db.relationship('Fee', foreign_keys='Fee.case_id', backref='case_fee', lazy='dynamic', cascade="all, delete-orphan")
    expenses = db.relationship('Expense', foreign_keys='Expense.case_id', backref='case_expense', lazy='dynamic', cascade="all, delete-orphan")
    invoices = db.relationship('Invoice', foreign_keys='Invoice.case_id', backref='case_invoice', lazy='dynamic', cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Case {self.id}: {self.caratula}>'

    def to_dict(self, include_tags=False, include_client=False):
        data = {
            'id': self.id,
            'client_id': self.client_id,
            'user_id': self.user_id,
            'caratula': self.caratula,
            'numero_expediente': self.numero_expediente,
            'anio_expediente': self.anio_expediente,
            'juzgado': self.juzgado,
            'jurisdiccion': self.jurisdiccion,
            'etapa_procesal': self.etapa_procesal,
            'descripcion_hechos_brutos': self.descripcion_hechos_brutos,
            'hechos_reformulados_ia': self.hechos_reformulados_ia,
            'notas_generales': self.notas_generales,
            'ruta_carpeta_documentos_local': self.ruta_carpeta_documentos_local,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_activity_at': self.last_activity_at.isoformat() if self.last_activity_at else None,
        }
        if include_tags:
            data['tags'] = [tag.to_dict() for tag in self.tags]
        if include_client and self.client: # self.client viene del backref
            data['client'] = self.client.to_dict_short() # Asume método to_dict_short en Client

        # Se podrían añadir listas de IDs o resúmenes de otras relaciones si es necesario
        # data['audiences_count'] = self.audiences.count()
        # data['tasks_count'] = self.tasks.count()
        return data

    def to_dict_short(self): # Para listas o cuando no se necesita todo el detalle
        return {
            'id': self.id,
            'caratula': self.caratula,
            'numero_expediente': self.numero_expediente,
            'anio_expediente': self.anio_expediente,
            'etapa_procesal': self.etapa_procesal,
            'client_id': self.client_id,
            'client_nombre': self.client.nombre_completo if self.client else "N/A" # Accede al cliente a través del backref
        }
