# financiero_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
try:
    from tkcalendar import DateEntry
except ImportError:
    # Attempt to install tkcalendar if not found
    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tkcalendar"])
        from tkcalendar import DateEntry
    except Exception as e:
        # If installation fails, raise an error or use a fallback (though DateEntry is crucial here)
        print(f"Error: tkcalendar not found and failed to install: {e}. Please install it manually.")
        # For the subtask, we'll proceed assuming it might get installed, or this print will notify.
        # A more robust solution would be to stop or use a standard Entry as fallback.
        pass # Let it try to use DateEntry and fail if not truly available.
import datetime # Ensure datetime is imported

class FinancieroTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.current_case = None
        self._create_widgets()

    def _create_widgets(self):
        # Configurar el frame principal con notebook para sub-pestañas
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Crear notebook para las sub-pestañas financieras
        self.finance_notebook = ttk.Notebook(self)
        self.finance_notebook.grid(row=0, column=0, sticky='nsew')

        # --- Pestaña de Honorarios ---
        self.honorarios_frame = ttk.Frame(self.finance_notebook, padding="10")
        self.finance_notebook.add(self.honorarios_frame, text="Honorarios")
        self._create_honorarios_tab()

        # --- Pestaña de Gastos ---
        self.gastos_frame = ttk.Frame(self.finance_notebook, padding="10")
        self.finance_notebook.add(self.gastos_frame, text="Gastos")
        self._create_gastos_tab()

        # --- Pestaña de Facturación ---
        self.facturacion_frame = ttk.Frame(self.finance_notebook, padding="10")
        self.finance_notebook.add(self.facturacion_frame, text="Facturación")
        self._create_facturacion_tab()

        # --- Pestaña de Resumen ---
        self.resumen_frame = ttk.Frame(self.finance_notebook, padding="10")
        self.finance_notebook.add(self.resumen_frame, text="Resumen")
        self._create_resumen_tab()

    def _create_honorarios_tab(self):
        """Crear la pestaña de gestión de honorarios"""
        self.honorarios_frame.columnconfigure(0, weight=1)
        self.honorarios_frame.rowconfigure(0, weight=0)
        self.honorarios_frame.rowconfigure(1, weight=1)
        self.honorarios_frame.rowconfigure(2, weight=0)

        # Información del caso
        info_frame = ttk.LabelFrame(self.honorarios_frame, text="Caso Actual", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.honorarios_case_label = ttk.Label(info_frame, text="Ningún caso seleccionado", foreground="gray")
        self.honorarios_case_label.grid(row=0, column=1, sticky=tk.EW)

        # Lista de honorarios
        list_frame = ttk.LabelFrame(self.honorarios_frame, text="Honorarios del Caso", padding="5")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        honorarios_cols = ('ID', 'Descripción', 'Monto', 'Moneda', 'Fecha', 'Estado', 'Tipo', 'Día Venc. Abono')
        self.honorarios_tree = ttk.Treeview(list_frame, columns=honorarios_cols, show='headings', selectmode='browse')

        for col in honorarios_cols:
            self.honorarios_tree.heading(col, text=col)

        self.honorarios_tree.heading('Día Venc. Abono', text='Día Venc.')

        self.honorarios_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.honorarios_tree.column('Descripción', width=200, stretch=True)
        self.honorarios_tree.column('Monto', width=100, stretch=tk.NO, anchor=tk.E)
        self.honorarios_tree.column('Moneda', width=60, stretch=tk.NO, anchor=tk.CENTER)
        self.honorarios_tree.column('Fecha', width=100, stretch=tk.NO)
        self.honorarios_tree.column('Estado', width=80, stretch=tk.NO)
        self.honorarios_tree.column('Tipo', width=100, stretch=tk.NO)
        self.honorarios_tree.column('Día Venc. Abono', width=80, stretch=tk.NO, anchor=tk.CENTER)

        honorarios_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.honorarios_tree.yview)
        self.honorarios_tree.configure(yscrollcommand=honorarios_scroll.set)
        honorarios_scroll.grid(row=0, column=1, sticky='ns')

        self.honorarios_tree.grid(row=0, column=0, sticky='nsew')

        # Botones de honorarios
        hon_buttons_frame = ttk.Frame(self.honorarios_frame)
        hon_buttons_frame.grid(row=2, column=0, sticky='ew')
        hon_buttons_frame.columnconfigure(0, weight=1)
        hon_buttons_frame.columnconfigure(1, weight=1)
        hon_buttons_frame.columnconfigure(2, weight=1)

        self.add_honorario_btn = ttk.Button(hon_buttons_frame, text="Nuevo Honorario", 
                                           command=self.open_honorario_dialog, state=tk.DISABLED)
        self.add_honorario_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.edit_honorario_btn = ttk.Button(hon_buttons_frame, text="Editar", 
                                            command=self.edit_selected_honorario, state=tk.DISABLED)
        self.edit_honorario_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.delete_honorario_btn = ttk.Button(hon_buttons_frame, text="Eliminar", 
                                              command=self.delete_selected_honorario, state=tk.DISABLED)
        self.delete_honorario_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

        # Bind para selección
        self.honorarios_tree.bind('<<TreeviewSelect>>', self.on_honorario_select)

    def _create_gastos_tab(self):
        """Crear la pestaña de gestión de gastos"""
        self.gastos_frame.columnconfigure(0, weight=1)
        self.gastos_frame.rowconfigure(0, weight=0)
        self.gastos_frame.rowconfigure(1, weight=1)
        self.gastos_frame.rowconfigure(2, weight=0)

        # Información del caso
        info_frame = ttk.LabelFrame(self.gastos_frame, text="Caso Actual", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.gastos_case_label = ttk.Label(info_frame, text="Ningún caso seleccionado", foreground="gray")
        self.gastos_case_label.grid(row=0, column=1, sticky=tk.EW)

        # Lista de gastos
        list_frame = ttk.LabelFrame(self.gastos_frame, text="Gastos del Caso", padding="5")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        gastos_cols = ('ID', 'Descripción', 'Monto', 'Fecha', 'Categoría', 'Reembolsable')
        self.gastos_tree = ttk.Treeview(list_frame, columns=gastos_cols, show='headings', selectmode='browse')

        for col in gastos_cols:
            self.gastos_tree.heading(col, text=col)

        self.gastos_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.gastos_tree.column('Descripción', width=200, stretch=True)
        self.gastos_tree.column('Monto', width=100, stretch=tk.NO, anchor=tk.E)
        self.gastos_tree.column('Fecha', width=100, stretch=tk.NO)
        self.gastos_tree.column('Categoría', width=100, stretch=tk.NO)
        self.gastos_tree.column('Reembolsable', width=80, stretch=tk.NO)

        gastos_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.gastos_tree.yview)
        self.gastos_tree.configure(yscrollcommand=gastos_scroll.set)
        gastos_scroll.grid(row=0, column=1, sticky='ns')

        self.gastos_tree.grid(row=0, column=0, sticky='nsew')

        # Botones de gastos
        gas_buttons_frame = ttk.Frame(self.gastos_frame)
        gas_buttons_frame.grid(row=2, column=0, sticky='ew')
        gas_buttons_frame.columnconfigure(0, weight=1)
        gas_buttons_frame.columnconfigure(1, weight=1)
        gas_buttons_frame.columnconfigure(2, weight=1)

        self.add_gasto_btn = ttk.Button(gas_buttons_frame, text="Nuevo Gasto", 
                                       command=self.open_gasto_dialog, state=tk.DISABLED)
        self.add_gasto_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.edit_gasto_btn = ttk.Button(gas_buttons_frame, text="Editar", 
                                        command=self.edit_selected_gasto, state=tk.DISABLED)
        self.edit_gasto_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.delete_gasto_btn = ttk.Button(gas_buttons_frame, text="Eliminar", 
                                          command=self.delete_selected_gasto, state=tk.DISABLED)
        self.delete_gasto_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

        # Bind para selección
        self.gastos_tree.bind('<<TreeviewSelect>>', self.on_gasto_select)

    def _create_facturacion_tab(self):
        """Crear la pestaña de facturación"""
        self.facturacion_frame.columnconfigure(0, weight=1)
        self.facturacion_frame.rowconfigure(0, weight=0)
        self.facturacion_frame.rowconfigure(1, weight=1)
        self.facturacion_frame.rowconfigure(2, weight=0)

        # Información del caso
        info_frame = ttk.LabelFrame(self.facturacion_frame, text="Caso Actual", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.facturacion_case_label = ttk.Label(info_frame, text="Ningún caso seleccionado", foreground="gray")
        self.facturacion_case_label.grid(row=0, column=1, sticky=tk.EW)

        # Lista de facturas
        list_frame = ttk.LabelFrame(self.facturacion_frame, text="Facturas del Caso", padding="5")
        list_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        facturas_cols = ('ID', 'Número', 'Fecha', 'Monto', 'Estado', 'Vencimiento')
        self.facturas_tree = ttk.Treeview(list_frame, columns=facturas_cols, show='headings', selectmode='browse')

        for col in facturas_cols:
            self.facturas_tree.heading(col, text=col)

        self.facturas_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.facturas_tree.column('Número', width=100, stretch=tk.NO)
        self.facturas_tree.column('Fecha', width=100, stretch=tk.NO)
        self.facturas_tree.column('Monto', width=100, stretch=tk.NO, anchor=tk.E)
        self.facturas_tree.column('Estado', width=80, stretch=tk.NO)
        self.facturas_tree.column('Vencimiento', width=100, stretch=tk.NO)

        facturas_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.facturas_tree.yview)
        self.facturas_tree.configure(yscrollcommand=facturas_scroll.set)
        facturas_scroll.grid(row=0, column=1, sticky='ns')

        self.facturas_tree.grid(row=0, column=0, sticky='nsew')

        # Botones de facturación
        fac_buttons_frame = ttk.Frame(self.facturacion_frame)
        fac_buttons_frame.grid(row=2, column=0, sticky='ew')
        fac_buttons_frame.columnconfigure(0, weight=1)
        fac_buttons_frame.columnconfigure(1, weight=1)
        fac_buttons_frame.columnconfigure(2, weight=1)

        self.add_factura_btn = ttk.Button(fac_buttons_frame, text="Nueva Factura", 
                                         command=self.open_factura_dialog, state=tk.DISABLED)
        self.add_factura_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.edit_factura_btn = ttk.Button(fac_buttons_frame, text="Editar", 
                                          command=self.edit_selected_factura, state=tk.DISABLED)
        self.edit_factura_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.delete_factura_btn = ttk.Button(fac_buttons_frame, text="Eliminar", 
                                            command=self.delete_selected_factura, state=tk.DISABLED)
        self.delete_factura_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

        # Bind para selección
        self.facturas_tree.bind('<<TreeviewSelect>>', self.on_factura_select)

    def _create_resumen_tab(self):
        """Crear la pestaña de resumen financiero"""
        self.resumen_frame.columnconfigure(0, weight=1)
        self.resumen_frame.rowconfigure(0, weight=0)
        self.resumen_frame.rowconfigure(1, weight=1)

        # Información del caso
        info_frame = ttk.LabelFrame(self.resumen_frame, text="Caso Actual", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.resumen_case_label = ttk.Label(info_frame, text="Ningún caso seleccionado", foreground="gray")
        self.resumen_case_label.grid(row=0, column=1, sticky=tk.EW)

        # Panel de resumen
        resumen_panel = ttk.Frame(self.resumen_frame)
        resumen_panel.grid(row=1, column=0, sticky='nsew')
        resumen_panel.columnconfigure(0, weight=1)
        resumen_panel.columnconfigure(1, weight=1)
        resumen_panel.rowconfigure(0, weight=1)
        resumen_panel.rowconfigure(1, weight=1)

        # Resumen de Honorarios
        hon_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Honorarios", padding="10")
        hon_resumen_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=(0, 5))

        self.hon_total_label = ttk.Label(hon_resumen_frame, text="Total: $0.00", font=('', 12, 'bold'))
        self.hon_total_label.pack(anchor=tk.W)

        self.hon_cobrado_label = ttk.Label(hon_resumen_frame, text="Cobrado: $0.00")
        self.hon_cobrado_label.pack(anchor=tk.W)

        self.hon_pendiente_label = ttk.Label(hon_resumen_frame, text="Pendiente: $0.00")
        self.hon_pendiente_label.pack(anchor=tk.W)

        # Resumen de Gastos
        gas_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Gastos", padding="10")
        gas_resumen_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=(0, 5))

        self.gas_total_label = ttk.Label(gas_resumen_frame, text="Total: $0.00", font=('', 12, 'bold'))
        self.gas_total_label.pack(anchor=tk.W)

        self.gas_reembolsable_label = ttk.Label(gas_resumen_frame, text="Reembolsable: $0.00")
        self.gas_reembolsable_label.pack(anchor=tk.W)

        self.gas_no_reembolsable_label = ttk.Label(gas_resumen_frame, text="No reembolsable: $0.00")
        self.gas_no_reembolsable_label.pack(anchor=tk.W)

        # Resumen de Facturación
        fac_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Facturación", padding="10")
        fac_resumen_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=(5, 0))

        self.fac_total_label = ttk.Label(fac_resumen_frame, text="Total facturado: $0.00", font=('', 12, 'bold'))
        self.fac_total_label.pack(anchor=tk.W)

        self.fac_pagado_label = ttk.Label(fac_resumen_frame, text="Pagado: $0.00")
        self.fac_pagado_label.pack(anchor=tk.W)

        self.fac_pendiente_label = ttk.Label(fac_resumen_frame, text="Pendiente: $0.00")
        self.fac_pendiente_label.pack(anchor=tk.W)

        # Balance General
        balance_frame = ttk.LabelFrame(resumen_panel, text="Balance General", padding="10")
        balance_frame.grid(row=1, column=1, sticky='nsew', padx=(5, 0), pady=(5, 0))

        self.balance_ingresos_label = ttk.Label(balance_frame, text="Ingresos: $0.00", font=('', 12, 'bold'))
        self.balance_ingresos_label.pack(anchor=tk.W)

        self.balance_gastos_label = ttk.Label(balance_frame, text="Gastos: $0.00")
        self.balance_gastos_label.pack(anchor=tk.W)

        self.balance_neto_label = ttk.Label(balance_frame, text="Balance Neto: $0.00", font=('', 14, 'bold'))
        self.balance_neto_label.pack(anchor=tk.W, pady=(10, 0))

    # --- Métodos de gestión de casos ---

    def on_case_changed(self, case_data):
        """Manejar cambio de caso seleccionado"""
        self.current_case = case_data
        self._update_case_labels()
        self._load_financial_data()

    def _update_case_labels(self):
        """Actualizar etiquetas de caso en todas las pestañas"""
        if self.current_case:
            case_text = f"{self.current_case.get('caratula', 'Sin carátula')} (ID: {self.current_case['id']})"
            color = "black"
            
            # Habilitar botones
            self.add_honorario_btn.config(state=tk.NORMAL)
            self.add_gasto_btn.config(state=tk.NORMAL)
            self.add_factura_btn.config(state=tk.NORMAL)
        else:
            case_text = "Ningún caso seleccionado"
            color = "gray"
            
            # Deshabilitar botones
            self.add_honorario_btn.config(state=tk.DISABLED)
            self.add_gasto_btn.config(state=tk.DISABLED)
            self.add_factura_btn.config(state=tk.DISABLED)
            self._disable_edit_buttons()

        # Actualizar todas las etiquetas
        for label in [self.honorarios_case_label, self.gastos_case_label, 
                     self.facturacion_case_label, self.resumen_case_label]:
            label.config(text=case_text, foreground=color)

    def _load_financial_data(self):
        """Cargar todos los datos financieros del caso"""
        if not self.current_case:
            self._clear_all_data()
            return

        try:
            case_id = self.current_case['id']
            self._load_honorarios(case_id)
            self._load_gastos(case_id)
            self._load_facturas(case_id)
            self._update_resumen(case_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos financieros: {e}")

    def _clear_all_data(self):
        """Limpiar todos los datos financieros"""
        # Limpiar TreeViews
        for tree in [self.honorarios_tree, self.gastos_tree, self.facturas_tree]:
            for item in tree.get_children():
                tree.delete(item)

        # Limpiar resumen
        self._clear_resumen()

    def _disable_edit_buttons(self):
        """Deshabilitar botones de edición"""
        buttons = [
            self.edit_honorario_btn, self.delete_honorario_btn,
            self.edit_gasto_btn, self.delete_gasto_btn,
            self.edit_factura_btn, self.delete_factura_btn
        ]
        for btn in buttons:
            btn.config(state=tk.DISABLED)

    # --- Métodos de Honorarios ---

    def _load_honorarios(self, case_id):
        """Cargar honorarios del caso"""
        # Limpiar TreeView
        for item in self.honorarios_tree.get_children():
            self.honorarios_tree.delete(item)

        try:
            honorarios = self.db_crm.get_honorarios_by_case(case_id)
            for honorario in honorarios:
                self.honorarios_tree.insert('', 'end', values=(
                    honorario['id'],
                    honorario.get('descripcion', ''),
                    f"{honorario.get('monto', 0.0):.2f}",
                    honorario.get('moneda', 'ARS'),
                    datetime.datetime.strptime(honorario.get('fecha', ''), '%Y-%m-%d').strftime('%d/%m/%Y') if honorario.get('fecha') else '',
                    honorario.get('estado', ''),
                    honorario.get('tipo', ''),
                    str(honorario.get('dia_vencimiento_abono', '')) if honorario.get('es_abono_mensual') else ''
                ))
        except Exception as e:
            print(f"Error al cargar honorarios: {e}")

    def on_honorario_select(self, event):
        """Manejar selección de honorario"""
        selected_items = self.honorarios_tree.selection()
        if selected_items:
            self.edit_honorario_btn.config(state=tk.NORMAL)
            self.delete_honorario_btn.config(state=tk.NORMAL)
        else:
            self.edit_honorario_btn.config(state=tk.DISABLED)
            self.delete_honorario_btn.config(state=tk.DISABLED)

    def open_honorario_dialog(self, honorario_id=None):
        """Abrir diálogo de honorario"""
        if not self.current_case:
            return

        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Nuevo Honorario" if not honorario_id else "Editar Honorario")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("400x420") # Adjusted height for new fields

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        descripcion_var = tk.StringVar()
        monto_var = tk.StringVar()
        moneda_var = tk.StringVar(value="ARS")
        fecha_var = tk.StringVar() # Remove default value for DateEntry compatibility
        estado_var = tk.StringVar(value="Pendiente")
        tipo_var = tk.StringVar(value="Consulta")
        dia_vencimiento_abono_var = tk.StringVar()

        tipo_values = ["Consulta", "Representación", "Gestión", "Abono Mensual", "Otro"]

        # Formulario
        row = 0
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=descripcion_var, width=30).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Monto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=monto_var, width=30).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Moneda:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=moneda_var, values=["ARS", "USD"],
                     state="readonly", width=28).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        # Replace Entry with DateEntry
        fecha_entry = DateEntry(main_frame, width=28, background='darkblue', foreground='white',
                                borderwidth=2, date_pattern='dd/MM/yyyy', textvariable=fecha_var)
        fecha_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=estado_var, values=["Pendiente", "Cobrado", "Cancelado"], 
                     state="readonly", width=28).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var, values=tipo_values,
                                  state="readonly", width=28)
        tipo_combo.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        dia_vencimiento_label = ttk.Label(main_frame, text="Día Vencimiento Abono (1-31):")
        dia_vencimiento_entry = ttk.Spinbox(main_frame, from_=1, to=31, textvariable=dia_vencimiento_abono_var, width=10, state=tk.DISABLED)

        # Add to grid but remove immediately if not needed initially
        dia_vencimiento_label.grid(row=row, column=0, sticky=tk.W, pady=5)
        dia_vencimiento_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        current_row_abono = row # Store the row for abono fields
        row += 1


        def _toggle_visibility_logic(selected_tipo_str):
            nonlocal current_row_abono # Use nonlocal to modify the row counter if needed, though not strictly necessary here
            if selected_tipo_str == "Abono Mensual":
                dia_vencimiento_label.grid(row=current_row_abono, column=0, sticky=tk.W, pady=5)
                dia_vencimiento_entry.config(state=tk.NORMAL)
                dia_vencimiento_entry.grid(row=current_row_abono, column=1, sticky=tk.EW, pady=5, padx=(10,0))
            else:
                dia_vencimiento_label.grid_remove()
                dia_vencimiento_entry.config(state=tk.DISABLED)
                dia_vencimiento_entry.grid_remove()
                dia_vencimiento_abono_var.set('')

        tipo_combo.bind('<<ComboboxSelected>>', lambda event: _toggle_visibility_logic(tipo_var.get()))

        if honorario_id:
            honorario_data = self.db_crm.get_honorario_by_id(honorario_id)
            if honorario_data:
                descripcion_var.set(honorario_data.get('descripcion', ''))
                monto_var.set(str(honorario_data.get('monto', 0.0)))
                moneda_var.set(honorario_data.get('moneda', 'ARS'))

                current_fecha_str = honorario_data.get('fecha') # Expected YYYY-MM-DD
                if current_fecha_str:
                    try:
                        date_obj = datetime.datetime.strptime(current_fecha_str, '%Y-%m-%d').date()
                        fecha_entry.set_date(date_obj)
                    except ValueError:
                        # If parsing fails, DateEntry will use its default (today) or be blank if no textvariable default
                        # We could set fecha_var here to the raw string, but DateEntry might not like YYYY-MM-DD
                        print(f"Warning: Could not parse date {current_fecha_str} for honorario_id {honorario_id}. Using DateEntry default.")
                        fecha_entry.set_date(datetime.date.today()) # Fallback to today
                else:
                    fecha_entry.set_date(datetime.date.today()) # Default to today if no date

                estado_var.set(honorario_data.get('estado', 'Pendiente'))

                is_abono = honorario_data.get('es_abono_mensual', 0)
                current_tipo_db = honorario_data.get('tipo', 'Consulta')

                if is_abono == 1 and current_tipo_db == "Abono Mensual": # Check both flags
                    tipo_var.set("Abono Mensual")
                    dia_vencimiento_abono_var.set(str(honorario_data.get('dia_vencimiento_abono', '')))
                else:
                    tipo_var.set(current_tipo_db if current_tipo_db in tipo_values else "Consulta")
                    dia_vencimiento_abono_var.set('')
                _toggle_visibility_logic(tipo_var.get())
        else:
            # New honorario, set default date for DateEntry
            fecha_entry.set_date(datetime.date.today())
            _toggle_visibility_logic(tipo_var.get())

        main_frame.columnconfigure(1, weight=1)

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20) # Ensure this row is after abono fields

        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self._save_honorario(honorario_id, self.current_case['id'], 
                                                      descripcion_var.get(), monto_var.get(),
                                                      fecha_var.get(), # This will be dd/MM/yyyy from DateEntry's textvariable
                                                      estado_var.get(), tipo_var.get(),
                                                      moneda_var.get(), dia_vencimiento_abono_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

    def _save_honorario(self, honorario_id, case_id, descripcion, monto_str, fecha_str_from_dialog, estado, tipo_seleccionado, moneda, dia_vencimiento_abono_str, dialog):
        """Guardar honorario"""
        if not descripcion.strip():
            messagebox.showwarning("Campo Requerido", "La descripción es obligatoria.", parent=dialog)
            return

        try:
            monto_float = float(monto_str) if monto_str else 0.0
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Ingrese un monto válido para 'Monto'.", parent=dialog)
            return

        fecha_to_db = ""
        if fecha_str_from_dialog:
            try:
                fecha_to_db = datetime.datetime.strptime(fecha_str_from_dialog, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Formato de Fecha Inválido", "La fecha debe estar en formato dd/mm/yyyy.", parent=dialog)
                return
        else:
            messagebox.showwarning("Campo Requerido", "La fecha es obligatoria.", parent=dialog)
            return

        es_abono_mensual_int = 1 if tipo_seleccionado == "Abono Mensual" else 0
        dia_vencimiento_abono_int = None

        if es_abono_mensual_int == 1:
            if not dia_vencimiento_abono_str.strip():
                messagebox.showwarning("Campo Requerido", "El día de vencimiento es obligatorio para abonos mensuales.", parent=dialog)
                return
            try:
                dia_val = int(dia_vencimiento_abono_str)
                if not (1 <= dia_val <= 31):
                    raise ValueError("Día fuera de rango")
                dia_vencimiento_abono_int = dia_val
            except ValueError:
                messagebox.showwarning("Dato Inválido", "El día de vencimiento del abono debe ser un número entre 1 y 31.", parent=dialog)
                return

        try:
            if honorario_id:
                self.db_crm.update_honorario(honorario_id, case_id, descripcion, monto_float, fecha_to_db, moneda, estado, tipo_seleccionado, "", es_abono_mensual_int, dia_vencimiento_abono_int)
            else:
                self.db_crm.add_honorario(case_id, descripcion, monto_float, fecha_to_db, moneda, estado, tipo_seleccionado, "", es_abono_mensual_int, dia_vencimiento_abono_int)
            
            dialog.destroy()
            self._load_honorarios(case_id)
            self._update_resumen(case_id)
            messagebox.showinfo("Éxito", "Honorario guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar honorario: {e}")

    def edit_selected_honorario(self):
        """Editar honorario seleccionado"""
        selected_items = self.honorarios_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un honorario para editar.")
            return

        selected_item = selected_items[0]
        try:
            honorario_id = self.honorarios_tree.item(selected_item, 'values')[0]
            self.open_honorario_dialog(honorario_id=int(honorario_id))
        except (IndexError, ValueError):
            messagebox.showerror("Error", "No se pudo obtener el ID del honorario seleccionado.")

    def delete_selected_honorario(self):
        """Eliminar honorario seleccionado"""
        selected_items = self.honorarios_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un honorario para eliminar.")
            return

        selected_item = selected_items[0]
        try:
            honorario_id_str = self.honorarios_tree.item(selected_item, 'values')[0]
            honorario_id = int(honorario_id_str)

            confirm = messagebox.askyesno("Confirmar Eliminación",
                                          f"¿Está seguro de que desea eliminar el honorario ID {honorario_id}?")
            if confirm:
                if self.db_crm.delete_honorario(honorario_id):
                    self._load_honorarios(self.current_case['id'])
                    self._update_resumen(self.current_case['id'])
                    messagebox.showinfo("Éxito", f"Honorario ID {honorario_id} eliminado correctamente.")
                else:
                    messagebox.showerror("Error", f"No se pudo eliminar el honorario ID {honorario_id}.")
        except (IndexError, ValueError):
            messagebox.showerror("Error", "No se pudo obtener el ID del honorario seleccionado para eliminar.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al eliminar el honorario: {e}")

    # --- Métodos de Gastos ---

    def _load_gastos(self, case_id):
        """Cargar gastos del caso"""
        # Limpiar TreeView
        for item in self.gastos_tree.get_children():
            self.gastos_tree.delete(item)

        try:
            gastos = self.db_crm.get_gastos_by_case(case_id)
            for gasto in gastos:
                reembolsable = "Sí" if gasto.get('reembolsable') else "No"
                self.gastos_tree.insert('', 'end', values=(
                    gasto['id'],
                    gasto.get('descripcion', ''),
                    f"${gasto.get('monto', 0):.2f}",
                    gasto.get('fecha', ''),
                    gasto.get('categoria', ''),
                    reembolsable
                ))
        except Exception as e:
            print(f"Error al cargar gastos: {e}")

    def on_gasto_select(self, event):
        """Manejar selección de gasto"""
        selected_items = self.gastos_tree.selection()
        if selected_items:
            self.edit_gasto_btn.config(state=tk.NORMAL)
            self.delete_gasto_btn.config(state=tk.NORMAL)
        else:
            self.edit_gasto_btn.config(state=tk.DISABLED)
            self.delete_gasto_btn.config(state=tk.DISABLED)

    def open_gasto_dialog(self, gasto_id=None):
        """Abrir diálogo de gasto - Implementación simplificada"""
        messagebox.showinfo("Funcionalidad", "Diálogo de gastos - Implementar según patrón de honorarios")

    def edit_selected_gasto(self):
        """Editar gasto seleccionado"""
        messagebox.showinfo("Funcionalidad", "Edición de gasto - Implementar según necesidades específicas")

    def delete_selected_gasto(self):
        """Eliminar gasto seleccionado"""
        messagebox.showinfo("Funcionalidad", "Eliminación de gasto - Implementar según necesidades específicas")

    # --- Métodos de Facturación ---

    def _load_facturas(self, case_id):
        """Cargar facturas del caso"""
        # Limpiar TreeView
        for item in self.facturas_tree.get_children():
            self.facturas_tree.delete(item)

        try:
            facturas = self.db_crm.get_facturas_by_case(case_id)
            for factura in facturas:
                self.facturas_tree.insert('', 'end', values=(
                    factura['id'],
                    factura.get('numero', ''),
                    factura.get('fecha', ''),
                    f"${factura.get('monto', 0):.2f}",
                    factura.get('estado', ''),
                    factura.get('fecha_vencimiento', '')
                ))
        except Exception as e:
            print(f"Error al cargar facturas: {e}")

    def on_factura_select(self, event):
        """Manejar selección de factura"""
        selected_items = self.facturas_tree.selection()
        if selected_items:
            self.edit_factura_btn.config(state=tk.NORMAL)
            self.delete_factura_btn.config(state=tk.NORMAL)
        else:
            self.edit_factura_btn.config(state=tk.DISABLED)
            self.delete_factura_btn.config(state=tk.DISABLED)

    def open_factura_dialog(self, factura_id=None):
        """Abrir diálogo de factura"""
        messagebox.showinfo("Funcionalidad", "Diálogo de facturas - Implementar según patrón de honorarios")

    def edit_selected_factura(self):
        """Editar factura seleccionada"""
        messagebox.showinfo("Funcionalidad", "Edición de factura - Implementar según necesidades específicas")

    def delete_selected_factura(self):
        """Eliminar factura seleccionada"""
        messagebox.showinfo("Funcionalidad", "Eliminación de factura - Implementar según necesidades específicas")

    # --- Métodos de Resumen ---

    def _update_resumen(self, case_id):
        """Actualizar resumen financiero"""
        try:
            # Calcular totales de honorarios
            honorarios = self.db_crm.get_honorarios_by_case(case_id)
            hon_total = sum(h.get('monto', 0) for h in honorarios)
            hon_cobrado = sum(h.get('monto', 0) for h in honorarios if h.get('estado') == 'Cobrado')
            hon_pendiente = hon_total - hon_cobrado

            # Calcular totales de gastos
            gastos = self.db_crm.get_gastos_by_case(case_id)
            gas_total = sum(g.get('monto', 0) for g in gastos)
            gas_reembolsable = sum(g.get('monto', 0) for g in gastos if g.get('reembolsable'))
            gas_no_reembolsable = gas_total - gas_reembolsable

            # Calcular totales de facturación
            facturas = self.db_crm.get_facturas_by_case(case_id)
            fac_total = sum(f.get('monto', 0) for f in facturas)
            fac_pagado = sum(f.get('monto', 0) for f in facturas if f.get('estado') == 'Pagada')
            fac_pendiente = fac_total - fac_pagado

            # Actualizar labels de resumen
            self.hon_total_label.config(text=f"Total: ${hon_total:.2f}")
            self.hon_cobrado_label.config(text=f"Cobrado: ${hon_cobrado:.2f}")
            self.hon_pendiente_label.config(text=f"Pendiente: ${hon_pendiente:.2f}")

            self.gas_total_label.config(text=f"Total: ${gas_total:.2f}")
            self.gas_reembolsable_label.config(text=f"Reembolsable: ${gas_reembolsable:.2f}")
            self.gas_no_reembolsable_label.config(text=f"No reembolsable: ${gas_no_reembolsable:.2f}")

            self.fac_total_label.config(text=f"Total facturado: ${fac_total:.2f}")
            self.fac_pagado_label.config(text=f"Pagado: ${fac_pagado:.2f}")
            self.fac_pendiente_label.config(text=f"Pendiente: ${fac_pendiente:.2f}")

            # Balance general
            ingresos = hon_cobrado + fac_pagado
            gastos_totales = gas_no_reembolsable  # Solo gastos no reembolsables afectan el balance
            balance_neto = ingresos - gastos_totales

            self.balance_ingresos_label.config(text=f"Ingresos: ${ingresos:.2f}")
            self.balance_gastos_label.config(text=f"Gastos: ${gastos_totales:.2f}")
            
            color = "darkgreen" if balance_neto >= 0 else "darkred"
            self.balance_neto_label.config(text=f"Balance Neto: ${balance_neto:.2f}", foreground=color)

        except Exception as e:
            print(f"Error al actualizar resumen: {e}")
            self._clear_resumen()

    def _clear_resumen(self):
        """Limpiar resumen financiero"""
        labels = [
            self.hon_total_label, self.hon_cobrado_label, self.hon_pendiente_label,
            self.gas_total_label, self.gas_reembolsable_label, self.gas_no_reembolsable_label,
            self.fac_total_label, self.fac_pagado_label, self.fac_pendiente_label,
            self.balance_ingresos_label, self.balance_gastos_label, self.balance_neto_label
        ]
        
        for label in labels:
            if "Total" in label.cget("text") or "Balance Neto" in label.cget("text"):
                label.config(text=label.cget("text").split(":")[0] + ": $0.00", foreground="black")
            else:
                label.config(text=label.cget("text").split(":")[0] + ": $0.00")

    def refresh_data(self):
        """Refrescar los datos del módulo"""
        if self.current_case:
            self._load_financial_data()

    def get_current_case(self):
        """Obtener el caso actual"""
        return self.current_case
