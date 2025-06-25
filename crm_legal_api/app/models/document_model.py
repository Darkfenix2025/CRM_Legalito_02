from app import db
import datetime

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Usuario que subió/gestionó el documento

    nombre_archivo_original = db.Column(db.String(255), nullable=False) # Nombre con el que el usuario lo subió
    nombre_archivo_sistema = db.Column(db.String(255), nullable=True, unique=True) # Nombre único en el sistema de archivos (si se guarda localmente)

    descripcion = db.Column(db.Text)
    tipo_documento = db.Column(db.String(100), index=True) # Ej: "Escrito", "Prueba Documental", "Cédula", "Oficio", "Contrato Generado IA"

    # Para almacenamiento local:
    ruta_relativa_local = db.Column(db.String(500)) # Relativa a una carpeta base de documentos del caso o del sistema
    # Para almacenamiento en nube (futuro):
    # url_nube = db.Column(db.String(1024))
    # proveedor_nube = db.Column(db.String(50)) # Ej: "S3", "GoogleCloudStorage"

    hash_contenido = db.Column(db.String(128), nullable=True, index=True) # Para detectar duplicados o verificar integridad (ej. SHA256)
    tamano_bytes = db.Column(db.BigInteger, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True) # Ej: "application/pdf", "image/jpeg"

    fecha_documento = db.Column(db.Date, nullable=True) # Fecha del documento en sí (ej. fecha de una escritura)
    fecha_carga = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Metadatos adicionales pueden ir en un campo JSON si es necesario
    # metadatos_json = db.Column(db.JSON)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación
    # El backref 'case_document' para la relación con Case se define en case_model.Case.documents
    # El backref 'uploader_user' para la relación con User se define en user_model.User.documents

    def __repr__(self):
        return f'<Document {self.id}: {self.nombre_archivo_original} (Case {self.case_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_document.caratula if self.case_document else "N/A", # Usar el nombre del backref
            'user_id': self.user_id,
            'user_username': self.uploader_user.username if self.uploader_user else "N/A", # Usar el nombre del backref
            'nombre_archivo_original': self.nombre_archivo_original,
            'nombre_archivo_sistema': self.nombre_archivo_sistema,
            'descripcion': self.descripcion,
            'tipo_documento': self.tipo_documento,
            'ruta_relativa_local': self.ruta_relativa_local,
            'tamano_bytes': self.tamano_bytes,
            'mime_type': self.mime_type,
            'fecha_documento': self.fecha_documento.isoformat() if self.fecha_documento else None,
            'fecha_carga': self.fecha_carga.isoformat() if self.fecha_carga else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_full_local_path(self):
        # Asume que current_app.config['UPLOAD_FOLDER_BASE'] está definida
        # y que ruta_relativa_local es relativa a esa base.
        # Esta lógica podría estar mejor en un servicio o helper.
        from flask import current_app
        if self.ruta_relativa_local:
            base_folder = current_app.config.get('UPLOAD_FOLDER_BASE', '/path/to/uploads') # Ejemplo
            return os.path.join(base_folder, self.ruta_relativa_local, self.nombre_archivo_sistema or self.nombre_archivo_original)
        return None
