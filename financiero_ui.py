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
        self.categorias_gastos_comunes = [
            "Bono CPACF", "Bono ley 8480", "Jus Anticipo", "Jus Arancelario",
            "Tasa de Justicia", "Aportes a cargo de parte",
            "Aportes a cargo del letrado", "IIBB", "IVA", "Otros"
        ]
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

        # --- Pestaña de Resumen Global ---
        self.resumen_global_frame = ttk.Frame(self.finance_notebook, padding="10")
        self.finance_notebook.add(self.resumen_global_frame, text="Resumen Global")
        self._create_resumen_global_tab() # Call to new method

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

        gastos_cols = ('ID', 'Descripción', 'Monto', 'Moneda', 'Fecha', 'Categoría', 'Reembolsable')
        self.gastos_tree = ttk.Treeview(list_frame, columns=gastos_cols, show='headings', selectmode='browse')

        for col in gastos_cols:
            self.gastos_tree.heading(col, text=col)
        self.gastos_tree.heading('Moneda', text='Moneda')


        self.gastos_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.gastos_tree.column('Descripción', width=200, stretch=True)
        self.gastos_tree.column('Monto', width=100, stretch=tk.NO, anchor=tk.E)
        self.gastos_tree.column('Moneda', width=60, stretch=tk.NO, anchor=tk.CENTER)
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
        """Crear la pestaña de resumen financiero con desglose multimoneda para todas las secciones relevantes."""
        self.resumen_frame.columnconfigure(0, weight=1)
        self.resumen_frame.rowconfigure(0, weight=0) # Info caso
        self.resumen_frame.rowconfigure(1, weight=1) # Panel principal de resumen

        # Información del caso
        info_frame = ttk.LabelFrame(self.resumen_frame, text="Caso Actual", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.resumen_case_label = ttk.Label(info_frame, text="Ningún caso seleccionado", foreground="gray")
        self.resumen_case_label.grid(row=0, column=1, sticky=tk.EW)

        # Panel de resumen principal
        resumen_panel = ttk.Frame(self.resumen_frame)
        resumen_panel.grid(row=1, column=0, sticky='nsew')
        resumen_panel.columnconfigure(0, weight=1) # Columna para Honorarios y Facturación
        resumen_panel.columnconfigure(1, weight=1) # Columna para Gastos y Balance General
        resumen_panel.rowconfigure(0, weight=1)    # Fila para Honorarios y Gastos
        resumen_panel.rowconfigure(1, weight=1)    # Fila para Facturación y Balance

        # --- Resumen de Honorarios ---
        hon_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Honorarios", padding="10")
        hon_resumen_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=(0, 5))

        self.hon_total_ars_label = ttk.Label(hon_resumen_frame, text="Total ARS: $0.00", font=('', 11, 'bold'))
        self.hon_total_ars_label.pack(anchor=tk.W)
        self.hon_cobrado_ars_label = ttk.Label(hon_resumen_frame, text="Cobrado ARS: $0.00")
        self.hon_cobrado_ars_label.pack(anchor=tk.W)
        self.hon_pendiente_ars_label = ttk.Label(hon_resumen_frame, text="Pendiente ARS: $0.00")
        self.hon_pendiente_ars_label.pack(anchor=tk.W, pady=(0,5))

        self.hon_total_usd_label = ttk.Label(hon_resumen_frame, text="Total USD: $0.00", font=('', 11, 'bold'))
        self.hon_total_usd_label.pack(anchor=tk.W)
        self.hon_cobrado_usd_label = ttk.Label(hon_resumen_frame, text="Cobrado USD: $0.00")
        self.hon_cobrado_usd_label.pack(anchor=tk.W)
        self.hon_pendiente_usd_label = ttk.Label(hon_resumen_frame, text="Pendiente USD: $0.00")
        self.hon_pendiente_usd_label.pack(anchor=tk.W)

        # --- Resumen de Gastos ---
        gas_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Gastos", padding="10")
        gas_resumen_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=(0, 5))

        self.gas_total_ars_label = ttk.Label(gas_resumen_frame, text="Total ARS: $0.00", font=('', 11, 'bold'))
        self.gas_total_ars_label.pack(anchor=tk.W)
        self.gas_reembolsable_ars_label = ttk.Label(gas_resumen_frame, text="Reembolsable ARS: $0.00")
        self.gas_reembolsable_ars_label.pack(anchor=tk.W)
        self.gas_no_reembolsable_ars_label = ttk.Label(gas_resumen_frame, text="No Reemb. ARS: $0.00") # Shorter text
        self.gas_no_reembolsable_ars_label.pack(anchor=tk.W, pady=(0,5))

        self.gas_total_usd_label = ttk.Label(gas_resumen_frame, text="Total USD: $0.00", font=('', 11, 'bold'))
        self.gas_total_usd_label.pack(anchor=tk.W)
        self.gas_reembolsable_usd_label = ttk.Label(gas_resumen_frame, text="Reembolsable USD: $0.00")
        self.gas_reembolsable_usd_label.pack(anchor=tk.W)
        self.gas_no_reembolsable_usd_label = ttk.Label(gas_resumen_frame, text="No Reemb. USD: $0.00") # Shorter text
        self.gas_no_reembolsable_usd_label.pack(anchor=tk.W)

        # --- Resumen de Facturación (sin cambios por ahora, mantiene su estructura original) ---
        fac_resumen_frame = ttk.LabelFrame(resumen_panel, text="Resumen de Facturación", padding="10")
        fac_resumen_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 5), pady=(5, 0))

        self.fac_total_label = ttk.Label(fac_resumen_frame, text="Total facturado: $0.00", font=('', 12, 'bold'))
        self.fac_total_label.pack(anchor=tk.W)
        self.fac_pagado_label = ttk.Label(fac_resumen_frame, text="Pagado: $0.00")
        self.fac_pagado_label.pack(anchor=tk.W)
        self.fac_pendiente_label = ttk.Label(fac_resumen_frame, text="Pendiente: $0.00")
        self.fac_pendiente_label.pack(anchor=tk.W)

        # --- Balance General (con nuevas etiquetas para desglose) ---
        balance_frame = ttk.LabelFrame(resumen_panel, text="Balance General", padding="10")
        balance_frame.grid(row=1, column=1, sticky='nsew', padx=(5, 0), pady=(5, 0))

        self.balance_ingresos_ars_label = ttk.Label(balance_frame, text="Ingresos ARS: $0.00", font=('', 11, 'bold'))
        self.balance_ingresos_ars_label.pack(anchor=tk.W)
        self.balance_gastos_ars_label = ttk.Label(balance_frame, text="Gastos ARS: $0.00")
        self.balance_gastos_ars_label.pack(anchor=tk.W)
        self.balance_neto_ars_label = ttk.Label(balance_frame, text="Balance Neto ARS: $0.00", font=('', 12, 'bold'))
        self.balance_neto_ars_label.pack(anchor=tk.W, pady=(0,10))

        self.balance_ingresos_usd_label = ttk.Label(balance_frame, text="Ingresos USD: $0.00", font=('', 11, 'bold'))
        self.balance_ingresos_usd_label.pack(anchor=tk.W)
        self.balance_gastos_usd_label = ttk.Label(balance_frame, text="Gastos USD: $0.00")
        self.balance_gastos_usd_label.pack(anchor=tk.W)
        self.balance_neto_usd_label = ttk.Label(balance_frame, text="Balance Neto USD: $0.00", font=('', 12, 'bold'))
        self.balance_neto_usd_label.pack(anchor=tk.W) # Removed pady=(5,0) to make it consistent

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

                fecha_db = gasto.get('fecha', '')
                fecha_display = ''
                if fecha_db:
                    try:
                        fecha_display = datetime.datetime.strptime(fecha_db, '%Y-%m-%d').strftime('%d/%m/%Y')
                    except ValueError:
                        fecha_display = fecha_db # Show raw if format is wrong

                self.gastos_tree.insert('', 'end', values=(
                    gasto['id'],
                    gasto.get('descripcion', ''),
                    f"${gasto.get('monto', 0.0):.2f}",
                    gasto.get('moneda', 'ARS'), # Display moneda
                    fecha_display,
                    gasto.get('categoria', ''),
                    reembolsable
                ))
        except Exception as e:
            print(f"Error al cargar gastos: {e}")
            messagebox.showerror("Error de Carga", f"No se pudieron cargar los gastos: {e}", parent=self)

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
        if not self.current_case:
            messagebox.showwarning("Sin Caso", "Por favor, seleccione un caso primero.")
            return

        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Nuevo Gasto" if not gasto_id else "Editar Gasto")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("450x400") # Adjusted size

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(1, weight=1)

        # Variables
        descripcion_var = tk.StringVar()
        monto_var = tk.StringVar()
        moneda_gasto_var = tk.StringVar(value="ARS") # Moneda for Gasto
        fecha_var = tk.StringVar()
        categoria_combo_var = tk.StringVar()
        categoria_especificar_var = tk.StringVar()
        reembolsable_var = tk.StringVar(value="Sí")

        gasto_data = None # To store fetched data in edit mode for notas/comprobante

        # Widgets
        row = 0
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=descripcion_var, width=40).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        row += 1

        ttk.Label(main_frame, text="Monto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=monto_var, width=40).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        row += 1

        ttk.Label(main_frame, text="Moneda:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=moneda_gasto_var, values=["ARS", "USD"],
                     state="readonly", width=10).grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10,0))
        row += 1

        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        fecha_entry = DateEntry(main_frame, width=38, background='darkblue', foreground='white', # Adjusted width
                                borderwidth=2, date_pattern='dd/MM/yyyy', textvariable=fecha_var)
        fecha_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        row += 1

        ttk.Label(main_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        categoria_combo = ttk.Combobox(main_frame, textvariable=categoria_combo_var,
                                       values=self.categorias_gastos_comunes, state="readonly", width=38)
        categoria_combo.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        row += 1

        categoria_especificar_label = ttk.Label(main_frame, text="Especificar Categoría:")
        categoria_especificar_entry = ttk.Entry(main_frame, textvariable=categoria_especificar_var, width=40, state=tk.DISABLED)
        # Grid for these will be managed by _toggle_categoria_especificar

        current_categoria_row = row # Save for toggling

        def _toggle_categoria_especificar(event=None):
            if categoria_combo_var.get() == "Otros":
                categoria_especificar_label.grid(row=current_categoria_row, column=0, sticky=tk.W, pady=5)
                categoria_especificar_entry.config(state=tk.NORMAL)
                categoria_especificar_entry.grid(row=current_categoria_row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
            else:
                categoria_especificar_label.grid_remove()
                categoria_especificar_entry.config(state=tk.DISABLED)
                categoria_especificar_entry.grid_remove()
                categoria_especificar_var.set("")

        categoria_combo.bind('<<ComboboxSelected>>', _toggle_categoria_especificar)
        row +=1 # Increment row for next elements

        ttk.Label(main_frame, text="Reembolsable:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Combobox(main_frame, textvariable=reembolsable_var, values=["Sí", "No"],
                     state="readonly", width=38).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10,0))
        row += 1

        if gasto_id:
            gasto_data = self.db_crm.get_gasto_by_id(gasto_id)
            if gasto_data:
                descripcion_var.set(gasto_data.get('descripcion', ''))
                monto_var.set(str(gasto_data.get('monto', 0.0)))
                moneda_gasto_var.set(gasto_data.get('moneda', 'ARS')) # Pre-fill moneda

                fecha_db = gasto_data.get('fecha')
                if fecha_db:
                    try:
                        fecha_obj = datetime.datetime.strptime(fecha_db, '%Y-%m-%d').date()
                        fecha_entry.set_date(fecha_obj)
                    except ValueError:
                        fecha_var.set(fecha_db) # Fallback
                else:
                    fecha_entry.set_date(datetime.date.today())

                reembolsable_var.set("Sí" if gasto_data.get('reembolsable', 1) else "No")

                saved_categoria = gasto_data.get('categoria', '')
                if saved_categoria in self.categorias_gastos_comunes and saved_categoria != "Otros":
                    categoria_combo_var.set(saved_categoria)
                elif saved_categoria: # Handles custom categories or old "Otros"
                    categoria_combo_var.set("Otros")
                    categoria_especificar_var.set(saved_categoria)
                else: # No category or empty
                    categoria_combo_var.set('') # Or a default if you prefer

                _toggle_categoria_especificar() # Update visibility based on loaded data
            else: # Gasto ID provided but not found
                messagebox.showerror("Error", f"No se encontró el gasto con ID {gasto_id}.", parent=dialog)
                dialog.destroy()
                return
        else: # New gasto
            fecha_entry.set_date(datetime.date.today())
            _toggle_categoria_especificar() # Initial state for new

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(buttons_frame, text="Guardar",
                   command=lambda: self._save_gasto(
                       gasto_id, self.current_case['id'], descripcion_var.get(),
                       monto_var.get(), fecha_var.get(), categoria_combo_var.get(),
                       categoria_especificar_var.get(), reembolsable_var.get(),
                       moneda_gasto_var.get(), # Pass moneda
                       gasto_data.get('notas', '') if gasto_data else "",
                       gasto_data.get('comprobante_path', '') if gasto_data else "",
                       dialog
                   )).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

    def _save_gasto(self, gasto_id, case_id, descripcion, monto_str, fecha_str,
                    categoria_selected, categoria_especificada, reembolsable_str,
                    moneda, notas_val, comprobante_path_val, dialog_ref): # Added moneda
        if not descripcion.strip():
            messagebox.showwarning("Campo Requerido", "La descripción es obligatoria.", parent=dialog_ref)
            return
        try:
            monto_float = float(monto_str) if monto_str else 0.0
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Ingrese un monto válido.", parent=dialog_ref)
            return

        fecha_db_format = ""
        if fecha_str:
            try:
                fecha_db_format = datetime.datetime.strptime(fecha_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            except ValueError:
                messagebox.showwarning("Formato de Fecha Inválido", "La fecha debe estar en formato dd/mm/yyyy.", parent=dialog_ref)
                return
        else:
            messagebox.showwarning("Campo Requerido", "La fecha es obligatoria.", parent=dialog_ref)
            return

        final_categoria = categoria_especificada.strip() if categoria_selected == "Otros" else categoria_selected
        if categoria_selected == "Otros" and not final_categoria:
            messagebox.showwarning("Campo Requerido", "Por favor, especifique la categoría 'Otros'.", parent=dialog_ref)
            return
        if not final_categoria: # Ensure some category is set
             messagebox.showwarning("Campo Requerido", "La categoría es obligatoria.", parent=dialog_ref)
             return

        reembolsable_int = 1 if reembolsable_str == "Sí" else 0

        try:
            if gasto_id:
                self.db_crm.update_gasto(gasto_id, case_id, descripcion, monto_float, fecha_db_format,
                                         final_categoria, reembolsable_int, moneda, notas_val, comprobante_path_val)
            else:
                self.db_crm.add_gasto(case_id, descripcion, monto_float, fecha_db_format,
                                      final_categoria, reembolsable_int, moneda, notas_val, comprobante_path_val)

            dialog_ref.destroy()
            self._load_gastos(case_id)
            self._update_resumen(case_id)
            messagebox.showinfo("Éxito", "Gasto guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar gasto: {e}", parent=dialog_ref)


    def edit_selected_gasto(self):
        """Editar gasto seleccionado"""
        selected_items = self.gastos_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un gasto para editar.", parent=self)
            return

        selected_item = selected_items[0]
        try:
            gasto_id_str = self.gastos_tree.item(selected_item, 'values')[0] # Assuming ID is the first value
            gasto_id = int(gasto_id_str)
            self.open_gasto_dialog(gasto_id=gasto_id)
        except (IndexError, ValueError):
            messagebox.showerror("Error de Selección", "No se pudo obtener el ID del gasto seleccionado.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}", parent=self)

    def delete_selected_gasto(self):
        """Eliminar gasto seleccionado"""
        selected_items = self.gastos_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un gasto para eliminar.", parent=self)
            return

        selected_item = selected_items[0]
        try:
            gasto_id_str = self.gastos_tree.item(selected_item, 'values')[0]
            gasto_descripcion = self.gastos_tree.item(selected_item, 'values')[1]
            gasto_id = int(gasto_id_str)

            confirm = messagebox.askyesno("Confirmar Eliminación",
                                          f"¿Está seguro de que desea eliminar el gasto: '{gasto_descripcion}' (ID: {gasto_id})?",
                                          parent=self)
            if confirm:
                if self.db_crm.delete_gasto(gasto_id):
                    if self.current_case and 'id' in self.current_case:
                        self._load_gastos(self.current_case['id'])
                        self._update_resumen(self.current_case['id'])
                        messagebox.showinfo("Éxito", f"Gasto ID {gasto_id} eliminado correctamente.", parent=self)
                    else:
                        # Fallback: clear lists if no case context
                        for item in self.gastos_tree.get_children(): # Clear only gastos_tree
                            self.gastos_tree.delete(item)
                        # Potentially call _update_resumen with None or handle appropriately
                        self._update_resumen(None) if self.current_case is None else self._update_resumen(self.current_case.get('id'))

                        messagebox.showinfo("Éxito", f"Gasto ID {gasto_id} eliminado. No hay caso activo para recargar completamente.", parent=self)
                else:
                    messagebox.showerror("Error de Eliminación", f"No se pudo eliminar el gasto ID {gasto_id} de la base de datos.", parent=self)
        except (IndexError, ValueError):
            messagebox.showerror("Error de Selección", "No se pudo obtener el ID del gasto seleccionado para eliminar.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al eliminar el gasto: {e}", parent=self)

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
            # Initialize Currency-Specific Accumulators for Fees
            hon_total_ars = 0.0
            hon_cobrado_ars = 0.0
            hon_pendiente_ars = 0.0
            hon_total_usd = 0.0
            hon_cobrado_usd = 0.0
            hon_pendiente_usd = 0.0

            # Initialize Currency-Specific Accumulators for Expenses
            gas_total_ars = 0.0
            gas_reembolsable_ars = 0.0
            gas_no_reembolsable_ars = 0.0
            gas_total_usd = 0.0
            gas_reembolsable_usd = 0.0
            gas_no_reembolsable_usd = 0.0

            if case_id is not None: # Proceed only if there's a case_id
                # Calcular totales de honorarios
                honorarios = self.db_crm.get_honorarios_by_case(case_id)
                for h in honorarios:
                    monto = h.get('monto', 0.0)
                    moneda = h.get('moneda', 'ARS')

                    if moneda == 'ARS':
                        hon_total_ars += monto
                        if h.get('estado') == 'Cobrado':
                            hon_cobrado_ars += monto
                    elif moneda == 'USD':
                        hon_total_usd += monto
                        if h.get('estado') == 'Cobrado':
                            hon_cobrado_usd += monto

                hon_pendiente_ars = hon_total_ars - hon_cobrado_ars
                hon_pendiente_usd = hon_total_usd - hon_cobrado_usd

                # Calcular totales de gastos
                gastos = self.db_crm.get_gastos_by_case(case_id)
                for g in gastos:
                    monto = g.get('monto', 0.0)
                    moneda = g.get('moneda', 'ARS')

                    if moneda == 'ARS':
                        gas_total_ars += monto
                        if g.get('reembolsable'):
                            gas_reembolsable_ars += monto
                    elif moneda == 'USD':
                        gas_total_usd += monto
                        if g.get('reembolsable'):
                            gas_reembolsable_usd += monto

                gas_no_reembolsable_ars = gas_total_ars - gas_reembolsable_ars
                gas_no_reembolsable_usd = gas_total_usd - gas_reembolsable_usd

                # Calcular totales de facturación (assuming single currency for now)
                facturas = self.db_crm.get_facturas_by_case(case_id)
                fac_total = sum(f.get('monto', 0) for f in facturas)
                fac_pagado = sum(f.get('monto', 0) for f in facturas if f.get('estado') == 'Pagada')
                fac_pendiente = fac_total - fac_pagado
            else: # No case_id, so all values are zero
                fac_total = fac_pagado = fac_pendiente = 0.0


            # Actualizar labels de resumen
            self.hon_total_ars_label.config(text=f"Total ARS: ${hon_total_ars:.2f}")
            self.hon_cobrado_ars_label.config(text=f"Cobrado ARS: ${hon_cobrado_ars:.2f}")
            self.hon_pendiente_ars_label.config(text=f"Pendiente ARS: ${hon_pendiente_ars:.2f}")

            self.hon_total_usd_label.config(text=f"Total USD: ${hon_total_usd:.2f}")
            self.hon_cobrado_usd_label.config(text=f"Cobrado USD: ${hon_cobrado_usd:.2f}")
            self.hon_pendiente_usd_label.config(text=f"Pendiente USD: ${hon_pendiente_usd:.2f}")

            self.gas_total_ars_label.config(text=f"Total ARS: ${gas_total_ars:.2f}")
            self.gas_reembolsable_ars_label.config(text=f"Reembolsable ARS: ${gas_reembolsable_ars:.2f}")
            self.gas_no_reembolsable_ars_label.config(text=f"No Reemb. ARS: ${gas_no_reembolsable_ars:.2f}")

            self.gas_total_usd_label.config(text=f"Total USD: ${gas_total_usd:.2f}")
            self.gas_reembolsable_usd_label.config(text=f"Reembolsable USD: ${gas_reembolsable_usd:.2f}")
            self.gas_no_reembolsable_usd_label.config(text=f"No Reemb. USD: ${gas_no_reembolsable_usd:.2f}")

            self.fac_total_label.config(text=f"Total facturado: ${fac_total:.2f}")
            self.fac_pagado_label.config(text=f"Pagado: ${fac_pagado:.2f}")
            self.fac_pendiente_label.config(text=f"Pendiente: ${fac_pendiente:.2f}")

            # Balance general - ARS
            # Assuming fac_pagado is ARS for now, needs currency if multi-currency invoices are implemented
            ingresos_ars = hon_cobrado_ars + (fac_pagado if self.fac_total_label.cget("text").startswith("Total facturado: $") else 0)
            gastos_ars = gas_no_reembolsable_ars
            balance_neto_ars = ingresos_ars - gastos_ars
            self.balance_ingresos_ars_label.config(text=f"Ingresos ARS: ${ingresos_ars:.2f}")
            self.balance_gastos_ars_label.config(text=f"Gastos ARS: ${gastos_ars:.2f}")
            self.balance_neto_ars_label.config(text=f"Balance Neto ARS: ${balance_neto_ars:.2f}", foreground="darkgreen" if balance_neto_ars >= 0 else "darkred")

            # Balance general - USD
            ingresos_usd = hon_cobrado_usd
            gastos_usd = gas_no_reembolsable_usd
            balance_neto_usd = ingresos_usd - gastos_usd
            self.balance_ingresos_usd_label.config(text=f"Ingresos USD: ${ingresos_usd:.2f}")
            self.balance_gastos_usd_label.config(text=f"Gastos USD: ${gastos_usd:.2f}")
            self.balance_neto_usd_label.config(text=f"Balance Neto USD: ${balance_neto_usd:.2f}", foreground="darkgreen" if balance_neto_usd >= 0 else "darkred")

        except Exception as e:
            print(f"Error al actualizar resumen: {e}")
            self._clear_resumen()

    def _clear_resumen(self):
        """Limpiar resumen financiero"""
        labels = [
            self.hon_total_ars_label, self.hon_cobrado_ars_label, self.hon_pendiente_ars_label,
            self.hon_total_usd_label, self.hon_cobrado_usd_label, self.hon_pendiente_usd_label,
            self.gas_total_ars_label, self.gas_reembolsable_ars_label, self.gas_no_reembolsable_ars_label,
            self.gas_total_usd_label, self.gas_reembolsable_usd_label, self.gas_no_reembolsable_usd_label,
            self.fac_total_label, self.fac_pagado_label, self.fac_pendiente_label,
            self.balance_ingresos_ars_label, self.balance_gastos_ars_label, self.balance_neto_ars_label,
            self.balance_ingresos_usd_label, self.balance_gastos_usd_label, self.balance_neto_usd_label
        ]
        
        for label in labels:
            # Extract the part of the text before the colon to keep the label name
            base_text = label.cget("text").split(":")[0]
            label.config(text=f"{base_text}: $0.00", foreground="black" if not ("Neto" in base_text) else ("darkgreen" if 0 >=0 else "darkred") )
            if "Balance Neto" in base_text : # Ensure default color for neto is green for 0
                 label.config(foreground="darkgreen")

    def refresh_data(self):
        """Refrescar los datos del módulo"""
        if self.current_case:
            self._load_financial_data()

    def get_current_case(self):
        """Obtener el caso actual"""
        return self.current_case

    def _create_resumen_global_tab(self):
        """Crear la pestaña de Resumen Financiero Global."""
        self.resumen_global_frame.columnconfigure(0, weight=1) # Allow content to expand

        # Main content frame within the tab
        content_frame = ttk.Frame(self.resumen_global_frame, padding="10")
        content_frame.grid(row=0, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1) # Single column for vertical layout of summaries

        row_idx = 0

        # --- Honorarios Cobrados (Global) ---
        hon_global_frame = ttk.LabelFrame(content_frame, text="Honorarios Cobrados (Global)", padding="10")
        hon_global_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
        hon_global_frame.columnconfigure(0, weight=1) # Ensure labels pack well

        self.global_hon_cobrado_ars_label = ttk.Label(hon_global_frame, text="Total Cobrado ARS: $0.00", font=('', 11))
        self.global_hon_cobrado_ars_label.pack(anchor=tk.W)
        self.global_hon_cobrado_usd_label = ttk.Label(hon_global_frame, text="Total Cobrado USD: $0.00", font=('', 11))
        self.global_hon_cobrado_usd_label.pack(anchor=tk.W)
        row_idx += 1

        # --- Gastos No Reembolsables (Global) ---
        gas_global_frame = ttk.LabelFrame(content_frame, text="Gastos No Reembolsables (Global)", padding="10")
        gas_global_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
        gas_global_frame.columnconfigure(0, weight=1)

        self.global_gas_no_reemb_ars_label = ttk.Label(gas_global_frame, text="Total Gastos ARS: $0.00", font=('', 11))
        self.global_gas_no_reemb_ars_label.pack(anchor=tk.W)
        self.global_gas_no_reemb_usd_label = ttk.Label(gas_global_frame, text="Total Gastos USD: $0.00", font=('', 11))
        self.global_gas_no_reemb_usd_label.pack(anchor=tk.W)
        row_idx += 1

        # --- Facturación Pagada (Global) ---
        fac_global_frame = ttk.LabelFrame(content_frame, text="Facturación Pagada (Global)", padding="10")
        fac_global_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
        fac_global_frame.columnconfigure(0, weight=1)

        self.global_fac_pagado_label = ttk.Label(fac_global_frame, text="Total Pagado (Facturas): $0.00", font=('', 11))
        self.global_fac_pagado_label.pack(anchor=tk.W)
        row_idx += 1

        # --- Balance Neto Global ---
        bal_neto_global_frame = ttk.LabelFrame(content_frame, text="Balance Neto Global", padding="10")
        bal_neto_global_frame.grid(row=row_idx, column=0, sticky="ew", pady=5)
        bal_neto_global_frame.columnconfigure(0, weight=1)

        # ARS Balance
        self.global_ingresos_ars_label = ttk.Label(bal_neto_global_frame, text="Ingresos Totales ARS: $0.00", font=('', 11, 'bold'))
        self.global_ingresos_ars_label.pack(anchor=tk.W)
        self.global_balance_gastos_ars_label = ttk.Label(bal_neto_global_frame, text="Gastos (No Reemb.) ARS: $0.00")
        self.global_balance_gastos_ars_label.pack(anchor=tk.W)
        self.global_balance_neto_ars_label = ttk.Label(bal_neto_global_frame, text="Balance Neto ARS: $0.00", font=('', 12, 'bold'))
        self.global_balance_neto_ars_label.pack(anchor=tk.W, pady=(0,10))

        # USD Balance
        self.global_ingresos_usd_label = ttk.Label(bal_neto_global_frame, text="Ingresos Totales USD: $0.00", font=('', 11, 'bold'))
        self.global_ingresos_usd_label.pack(anchor=tk.W)
        self.global_balance_gastos_usd_label = ttk.Label(bal_neto_global_frame, text="Gastos (No Reemb.) USD: $0.00")
        self.global_balance_gastos_usd_label.pack(anchor=tk.W)
        self.global_balance_neto_usd_label = ttk.Label(bal_neto_global_frame, text="Balance Neto USD: $0.00", font=('', 12, 'bold'))
        self.global_balance_neto_usd_label.pack(anchor=tk.W)
        row_idx += 1

        # --- Botón de Actualizar ---
        self.update_global_resumen_btn = ttk.Button(content_frame, text="Actualizar Resumen Global", command=self._load_resumen_global_data)
        self.update_global_resumen_btn.grid(row=row_idx, column=0, pady=10)
        row_idx += 1

        # Initialize by loading/clearing the data
        self._load_resumen_global_data()

    def _load_resumen_global_data(self):
        """Carga y muestra los datos del Resumen Financiero Global."""
        self._clear_resumen_global_labels() # Start by clearing to reset to $0.00

        try:
            # 1. Get aggregated data from the database
            hon_cobrados_global = self.db_crm.get_total_honorarios_cobrados_global_por_moneda()
            gas_no_reemb_global = self.db_crm.get_total_gastos_no_reembolsables_global_por_moneda()
            fac_pagado_global = self.db_crm.get_total_facturas_pagadas_global() # This is a single float value

            # Extract ARS and USD values, defaulting to 0.0 if a currency is not present
            hc_ars = hon_cobrados_global.get('ARS', 0.0)
            hc_usd = hon_cobrados_global.get('USD', 0.0)

            gnr_ars = gas_no_reemb_global.get('ARS', 0.0)
            gnr_usd = gas_no_reemb_global.get('USD', 0.0)

            # 2. Update labels for Honorarios Cobrados (Global)
            self.global_hon_cobrado_ars_label.config(text=f"Total Cobrado ARS: ${hc_ars:.2f}")
            self.global_hon_cobrado_usd_label.config(text=f"Total Cobrado USD: ${hc_usd:.2f}")

            # 3. Update labels for Gastos No Reembolsables (Global)
            self.global_gas_no_reemb_ars_label.config(text=f"Total Gastos ARS: ${gnr_ars:.2f}")
            self.global_gas_no_reemb_usd_label.config(text=f"Total Gastos USD: ${gnr_usd:.2f}")

            # Also update the specific labels in the Balance General section that show gastos
            self.global_balance_gastos_ars_label.config(text=f"Gastos (No Reemb.) ARS: ${gnr_ars:.2f}")
            self.global_balance_gastos_usd_label.config(text=f"Gastos (No Reemb.) USD: ${gnr_usd:.2f}")


            # 4. Update label for Facturación Pagada (Global)
            #    As fac_pagado_global is a single value, we assume it's ARS for now or the system's primary currency.
            self.global_fac_pagado_label.config(text=f"Total Pagado (Facturas): ${fac_pagado_global:.2f}")

            # 5. Calculate and Update Balance Neto Global
            #    For now, fac_pagado_global is added to ARS ingresos. This is a known limitation.
            ingresos_global_ars = hc_ars + fac_pagado_global
            ingresos_global_usd = hc_usd

            # Gastos for balance are directly the non-reimbursable ones
            gastos_global_ars = gnr_ars
            gastos_global_usd = gnr_usd

            balance_neto_global_ars = ingresos_global_ars - gastos_global_ars
            balance_neto_global_usd = ingresos_global_usd - gastos_global_usd

            self.global_ingresos_ars_label.config(text=f"Ingresos Totales ARS: ${ingresos_global_ars:.2f}")
            self.global_balance_neto_ars_label.config(
                text=f"Balance Neto ARS: ${balance_neto_global_ars:.2f}",
                foreground="darkgreen" if balance_neto_global_ars >= 0 else "darkred"
            )

            self.global_ingresos_usd_label.config(text=f"Ingresos Totales USD: ${ingresos_global_usd:.2f}")
            self.global_balance_neto_usd_label.config(
                text=f"Balance Neto USD: ${balance_neto_global_usd:.2f}",
                foreground="darkgreen" if balance_neto_global_usd >= 0 else "darkred"
            )

        except Exception as e:
            print(f"Error al cargar el resumen financiero global: {e}")
            messagebox.showerror("Error de Resumen Global", f"No se pudo cargar el resumen global: {e}", parent=self)
            # Ensure labels are cleared or show error state if loading fails
            self._clear_resumen_global_labels()

    def _clear_resumen_global_labels(self):
        """Limpia las etiquetas del Resumen Financiero Global."""
        labels_to_clear = [
            self.global_hon_cobrado_ars_label, self.global_hon_cobrado_usd_label,
            self.global_gas_no_reemb_ars_label, self.global_gas_no_reemb_usd_label,
            self.global_fac_pagado_label,
            self.global_ingresos_ars_label, self.global_balance_gastos_ars_label, self.global_balance_neto_ars_label,
            self.global_ingresos_usd_label, self.global_balance_gastos_usd_label, self.global_balance_neto_usd_label
        ]
        for label in labels_to_clear:
            base_text = label.cget("text").split(":")[0]
            default_color = "darkgreen" if "Balance Neto" in base_text else "black"
            label.config(text=f"{base_text}: $0.00", foreground=default_color)
