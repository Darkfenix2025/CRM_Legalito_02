from app import db
import datetime

# --- Modelos para el Módulo Financiero ---
# Estos son modelos básicos. Se pueden expandir con más campos según necesidad.

class Fee(db.Model):
    __tablename__ = 'fees' # Honorarios

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False) # Ej: 12345678.90
    moneda = db.Column(db.String(10), default='ARS') # ARS, USD, etc.
    fecha = db.Column(db.Date, nullable=False, index=True) # Fecha del honorario (devengado o pactado)

    # Estado del honorario
    # Ej: "Pactado", "Facturado", "Cobrado Parcialmente", "Cobrado Totalmente", "Vencido", "Anulado"
    estado = db.Column(db.String(50), default='Pactado', index=True)

    # Tipo de honorario
    # Ej: "Consulta Inicial", "Redacción Demanda", "Representación Audiencia", "Cuota Litis", "Abono Mensual"
    tipo_honorario = db.Column(db.String(100))

    factura_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True) # Si este honorario está incluido en una factura

    notas = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    # El backref 'case_fee' para Case se define en case_model.Case.fees
    # El backref 'user_fee' para User se define en user_model.User.fees
    # El backref 'invoice_fee' para Invoice se define en Invoice.fees_covered (si se invierte la relación)
    # Opcionalmente, si una Fee pertenece a una Invoice:
    # invoice = db.relationship('Invoice', backref=db.backref('fees_covered_by_invoice', lazy='dynamic'))


    def __repr__(self):
        return f'<Fee {self.id}: {self.descripcion} - {self.monto} {self.moneda}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_fee.caratula if self.case_fee else "N/A",
            'user_id': self.user_id,
            'user_username': self.user_fee.username if self.user_fee else "N/A",
            'descripcion': self.descripcion,
            'monto': str(self.monto), # Convertir Decimal a string para JSON
            'moneda': self.moneda,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado,
            'tipo_honorario': self.tipo_honorario,
            'factura_id': self.factura_id,
            'notas': self.notas,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Expense(db.Model):
    __tablename__ = 'expenses' # Gastos

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=True, index=True) # Puede ser un gasto general del estudio
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    descripcion = db.Column(db.String(255), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    moneda = db.Column(db.String(10), default='ARS')
    fecha = db.Column(db.Date, nullable=False, index=True)

    # Categoría del gasto
    # Ej: "Movilidad", "Fotocopias", "Sellados", "Peritos", "Gastos Administrativos", "Tasas de Justicia"
    categoria = db.Column(db.String(100), index=True)

    es_reembolsable_cliente = db.Column(db.Boolean, default=False) # Si el cliente debe reembolsarlo
    estado_reembolso = db.Column(db.String(50), default='Pendiente') # Ej: "Pendiente", "Reembolsado", "No Aplica"

    factura_proveedor_id = db.Column(db.String(100)) # Nro de factura o comprobante del proveedor
    proveedor_nombre = db.Column(db.String(150))

    notas = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    # El backref 'case_expense' para Case se define en case_model.Case.expenses
    # El backref 'user_expense' para User se define en user_model.User.expenses

    def __repr__(self):
        return f'<Expense {self.id}: {self.descripcion} - {self.monto} {self.moneda}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_expense.caratula if self.case_expense else "N/A",
            'user_id': self.user_id,
            'user_username': self.user_expense.username if self.user_expense else "N/A",
            'descripcion': self.descripcion,
            'monto': str(self.monto),
            'moneda': self.moneda,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'categoria': self.categoria,
            'es_reembolsable_cliente': self.es_reembolsable_cliente,
            'estado_reembolso': self.estado_reembolso,
            'factura_proveedor_id': self.factura_proveedor_id,
            'proveedor_nombre': self.proveedor_nombre,
            'notas': self.notas,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Invoice(db.Model):
    __tablename__ = 'invoices' # Facturas (emitidas por el estudio)

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=True, index=True) # Puede ser una factura no ligada a un caso específico
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True, index=True) # Cliente al que se factura
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    numero_factura = db.Column(db.String(50), nullable=False, unique=True, index=True)
    fecha_emision = db.Column(db.Date, nullable=False, default=datetime.date.today, index=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True)

    monto_total = db.Column(db.Numeric(12, 2), nullable=False) # Suma de items o monto fijo
    moneda = db.Column(db.String(10), default='ARS')

    # Estado de la factura
    # Ej: "Borrador", "Emitida", "Enviada", "Pagada Parcialmente", "Pagada Totalmente", "Vencida", "Anulada"
    estado = db.Column(db.String(50), default='Emitida', index=True)

    descripcion_general = db.Column(db.Text) # Concepto general de la factura

    # Enlace a archivo PDF de la factura (si se genera o sube)
    # ruta_archivo_pdf_local = db.Column(db.String(500))

    # Información fiscal (podría ser más detallada)
    # tipo_comprobante_afip = db.Column(db.String(10)) # Ej: "001" para Factura A, etc.
    # cae_afip = db.Column(db.String(50))
    # fecha_vto_cae_afip = db.Column(db.Date)

    notas_internas = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relaciones
    # El backref 'case_invoice' para Case se define en case_model.Case.invoices
    # El backref 'client_invoice' para Client se define en client_model.Client.invoices
    # El backref 'user_invoice' para User se define en user_model.User.invoices

    # Relación uno-a-muchos: una factura puede tener muchos items/líneas (si se crea InvoiceItem)
    # invoice_items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade="all, delete-orphan")

    # Relación uno-a-muchos: una factura puede tener muchos pagos aplicados (si se crea Payment)
    # payments_received = db.relationship('Payment', backref='invoice', lazy='dynamic', cascade="all, delete-orphan")

    # Honorarios cubiertos por esta factura (Fee tiene un invoice_id que apunta aquí)
    # El backref 'invoice' en Fee.invoice ya establece esta conexión.
    # fees_covered = db.relationship('Fee', foreign_keys='Fee.factura_id', backref='invoice_fee_covers', lazy='dynamic')


    def __repr__(self):
        return f'<Invoice {self.id}: {self.numero_factura} - Monto: {self.monto_total} {self.moneda}>'

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'case_caratula': self.case_invoice.caratula if self.case_invoice else "N/A",
            'client_id': self.client_id,
            'client_nombre': self.client_invoice.nombre_completo if self.client_invoice else "N/A",
            'user_id': self.user_id,
            'user_username': self.user_invoice.username if self.user_invoice else "N/A",
            'numero_factura': self.numero_factura,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'monto_total': str(self.monto_total),
            'moneda': self.moneda,
            'estado': self.estado,
            'descripcion_general': self.descripcion_general,
            'notas_internas': self.notas_internas,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # 'items': [item.to_dict() for item in self.invoice_items],
            # 'payments': [payment.to_dict() for payment in self.payments_received]
        }

# Podríamos añadir InvoiceItem y Payment si se necesita ese nivel de detalle.
# class InvoiceItem(db.Model): ...
# class Payment(db.Model): ... (pagos recibidos contra una factura)
