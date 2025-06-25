from app import db
import datetime

# Tabla de asociación para la relación muchos-a-muchos entre Cliente y Etiqueta
client_tags_association = db.Table('client_tags',
    db.Column('client_id', db.Integer, db.ForeignKey('clients.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    nombre_completo = db.Column(db.String(200), nullable=False, index=True)
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(120), index=True)
    whatsapp = db.Column(db.String(50))
    dni_cuit = db.Column(db.String(20), index=True) # DNI, CUIT, CUIL, etc.
    notas_adicionales = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    # El backref 'user' para la relación con User se define en user_model.User.clients
    cases = db.relationship('Case', foreign_keys='Case.client_id', backref='client_associated_case', lazy='dynamic', cascade="all, delete-orphan")

    tags = db.relationship('Tag', secondary=client_tags_association,
                           lazy='subquery', # 'subquery' carga las etiquetas del cliente en la misma consulta que el cliente
                           backref=db.backref('clients_associated', lazy='dynamic')) # 'dynamic' para que se puedan añadir filtros a client.tags.filter_by(...)

    # Relación con Facturas (un cliente puede tener muchas facturas)
    invoices = db.relationship('Invoice', foreign_keys='Invoice.client_id', backref='client_invoice', lazy='dynamic', cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Client {self.id}: {self.nombre_completo}>'

    def to_dict(self, include_cases=False, include_tags=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'nombre_completo': self.nombre_completo,
            'direccion': self.direccion,
            'email': self.email,
            'whatsapp': self.whatsapp,
            'dni_cuit': self.dni_cuit,
            'notas_adicionales': self.notas_adicionales,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_cases:
            data['cases'] = [case.to_dict_short() for case in self.cases] # Asume un método to_dict_short en Case
        if include_tags:
            data['tags'] = [tag.to_dict() for tag in self.tags]
        return data

    def to_dict_short(self): # Un diccionario más breve para listas o referencias
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'whatsapp': self.whatsapp
        }
