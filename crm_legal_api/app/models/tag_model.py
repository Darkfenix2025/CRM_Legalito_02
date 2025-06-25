from app import db
import datetime

# Las tablas de asociación client_tags_association y case_tags_association
# ya están definidas en client_model.py y case_model.py respectivamente.
# SQLAlchemy las detectará desde allí. Si prefieres centralizarlas,
# podrías mover sus definiciones aquí y ajustar los imports en los otros modelos.
# Por ahora, se asume que están donde se definieron.

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Cada usuario gestiona sus etiquetas

    nombre = db.Column(db.String(100), nullable=False, index=True)
    color = db.Column(db.String(20))  # Ej. "#RRGGBB" o nombre del color
    descripcion = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Constraint para asegurar que el nombre de la etiqueta sea único por usuario
    __table_args__ = (db.UniqueConstraint('user_id', 'nombre', name='uq_user_tag_nombre'),)

    # Las relaciones 'clients' y 'cases' se establecen mediante los backrefs
    # en client_model.py (tags) y case_model.py (tags) usando las tablas de asociación.

    def __repr__(self):
        return f'<Tag {self.id}: {self.nombre} (User: {self.user_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'nombre': self.nombre,
            'color': self.color,
            'descripcion': self.descripcion,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
