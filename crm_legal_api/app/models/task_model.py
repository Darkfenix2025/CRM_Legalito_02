from app import db
import datetime

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True) # Usuario asignado o creador

    descripcion = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True, index=True)

    prioridad = db.Column(db.String(20), default='Media', index=True)  # Ej: 'Alta', 'Media', 'Baja'
    estado = db.Column(db.String(30), default='Pendiente', nullable=False, index=True) # Ej: 'Pendiente', 'En Progreso', 'Completada', 'Cancelada', 'Esperando Tercero'

    es_plazo_procesal = db.Column(db.Boolean, default=False)

    # Para recordatorios de tareas (diferente de audiencias)
    recordatorio_tarea_activo = db.Column(db.Boolean, default=False)
    dias_antes_recordatorio_tarea = db.Column(db.Integer, default=1)
    # fecha_ultimo_recordatorio_tarea = db.Column(db.DateTime, nullable=True)

    notas = db.Column(db.Text)

    # Campos de auditoría (updated_at se actualiza automáticamente)
    # created_at ya está en fecha_creacion
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relación
    # El backref 'case_task' para la relación con Case se define en case_model.Case.tasks
    # El backref 'assigned_user' para la relación con User se define en user_model.User.tasks

    def __repr__(self):
        return f'<Task {self.id}: {self.descripcion[:50]}... (Case {self.case_id})>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_task.caratula if self.case_task else "N/A", # Usar el nombre del backref
            'user_id': self.user_id,
            'user_username': self.assigned_user.username if self.assigned_user else "N/A", # Usar el nombre del backref
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'prioridad': self.prioridad,
            'estado': self.estado,
            'es_plazo_procesal': self.es_plazo_procesal,
            'recordatorio_tarea_activo': self.recordatorio_tarea_activo,
            'dias_antes_recordatorio_tarea': self.dias_antes_recordatorio_tarea,
            'notas': self.notas,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
