# financiero_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

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

        honorarios_cols = ('ID', 'Descripción', 'Monto', 'Fecha', 'Estado', 'Tipo')
        self.honorarios_tree = ttk.Treeview(list_frame, columns=honorarios_cols, show='headings', selectmode='browse')

        for col in honorarios_cols:
            self.honorarios_tree.heading(col, text=col)

        self.honorarios_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.honorarios_tree.column('Descripción', width=200, stretch=True)
        self.honorarios_tree.column('Monto', width=100, stretch=tk.NO, anchor=tk.E)
        self.honorarios_tree.column('Fecha', width=100, stretch=tk.NO)
        self.honorarios_tree.column('Estado', width=80, stretch=tk.NO)
        self.honorarios_tree.column('Tipo', width=100, stretch=tk.NO)

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
        self.honorarios_tree.bind('<Double-1>', self._edit_selected_honorario_wrapper)


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
        self.gastos_tree.bind('<Double-1>', self._edit_selected_gasto_wrapper)


    def _edit_selected_gasto_wrapper(self, event=None):
        selected_items = self.gastos_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione un gasto para editar.", parent=self.app_controller.root)
            return
        gasto_id_str = self.gastos_tree.item(selected_items[0], 'values')[0]
        try:
            gasto_id = int(gasto_id_str)
            self.open_gasto_dialog(gasto_id=gasto_id)
        except ValueError:
            messagebox.showerror("Error", "ID de gasto inválido.", parent=self.app_controller.root)

    def edit_selected_gasto(self): # Kept for explicitness if called from a button not via double-click
        self._edit_selected_gasto_wrapper()


    def delete_selected_gasto(self):
        """Eliminar gasto seleccionado"""
        selected_items = self.gastos_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione un gasto para eliminar.", parent=self.app_controller.root)
            return

        gasto_id_str = self.gastos_tree.item(selected_items[0], 'values')[0]
        gasto_desc = self.gastos_tree.item(selected_items[0], 'values')[1]

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar el gasto:\n'{gasto_desc}'?",
                               parent=self.app_controller.root):
            try:
                gasto_id = int(gasto_id_str)
                if self.db_crm.delete_gasto(gasto_id):
                    messagebox.showinfo("Éxito", "Gasto eliminado correctamente.", parent=self.app_controller.root)
                    self._load_gastos(self.current_case['id'])
                    self._update_resumen(self.current_case['id'])
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el gasto.", parent=self.app_controller.root)
            except ValueError:
                messagebox.showerror("Error", "ID de gasto inválido.", parent=self.app_controller.root)
            except Exception as e:
                 messagebox.showerror("Error", f"Error al eliminar gasto: {e}", parent=self.app_controller.root)


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
        self.facturas_tree.bind('<Double-1>', self._edit_selected_factura_wrapper)


    def _edit_selected_factura_wrapper(self, event=None):
        selected_items = self.facturas_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione una factura para editar.", parent=self.app_controller.root)
            return
        factura_id_str = self.facturas_tree.item(selected_items[0], 'values')[0]
        try:
            factura_id = int(factura_id_str)
            self.open_factura_dialog(factura_id=factura_id)
        except ValueError:
            messagebox.showerror("Error", "ID de factura inválido.", parent=self.app_controller.root)

    def edit_selected_factura(self): # For explicit button call
        self._edit_selected_factura_wrapper()

    def delete_selected_factura(self):
        """Eliminar factura seleccionada"""
        selected_items = self.facturas_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione una factura para eliminar.", parent=self.app_controller.root)
            return

        factura_id_str = self.facturas_tree.item(selected_items[0], 'values')[0]
        factura_num = self.facturas_tree.item(selected_items[0], 'values')[1]

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar la factura Nro: {factura_num}?",
                               parent=self.app_controller.root):
            try:
                factura_id = int(factura_id_str)
                if self.db_crm.delete_factura(factura_id):
                    messagebox.showinfo("Éxito", "Factura eliminada correctamente.", parent=self.app_controller.root)
                    self._load_facturas(self.current_case['id'])
                    self._update_resumen(self.current_case['id'])
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la factura.", parent=self.app_controller.root)
            except ValueError:
                messagebox.showerror("Error", "ID de factura inválido.", parent=self.app_controller.root)
            except Exception as e:
                 messagebox.showerror("Error", f"Error al eliminar factura: {e}", parent=self.app_controller.root)


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

    # Note on Dialogs in FinancieroTab:
    # The pattern for open_honorario_dialog, open_gasto_dialog, and open_factura_dialog
    # is similar:
    # 1. Check if a current_case is selected.
    # 2. Create a Toplevel dialog, modal to the main application window (self.app_controller.root).
    #    (Could be enhanced to be modal to CaseDetailsWindow if this tab is hosted there).
    # 3. Populate dialog fields with existing data if an item_id is provided (editing).
    # 4. Provide a save mechanism that calls the appropriate add_* or update_* method in db_crm.
    # 5. After saving, reload the relevant list in this tab and update the _update_resumen.

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
                    f"${honorario.get('monto', 0):.2f}",
                    honorario.get('fecha', ''),
                    honorario.get('estado', ''),
                    honorario.get('tipo', '')
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
        dialog.geometry("400x350")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        descripcion_var = tk.StringVar()
        monto_var = tk.StringVar()
        fecha_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        estado_var = tk.StringVar(value="Pendiente")
        tipo_var = tk.StringVar(value="Consulta")
        notas_var = tk.StringVar() # Para el campo de notas

        honorario_data = None
        if honorario_id:
            honorario_data = self.db_crm.get_honorario_by_id(honorario_id) # Necesitas esta función en crm_database.py
            if honorario_data:
                descripcion_var.set(honorario_data.get('descripcion', ''))
                monto_var.set(str(honorario_data.get('monto', '0.0')))
                fecha_var.set(honorario_data.get('fecha', datetime.date.today().strftime("%Y-%m-%d")))
                estado_var.set(honorario_data.get('estado', 'Pendiente'))
                tipo_var.set(honorario_data.get('tipo', 'Consulta'))
                notas_var.set(honorario_data.get('notas', ''))
            else:
                messagebox.showerror("Error", "No se pudo cargar el honorario para editar.", parent=dialog)
                dialog.destroy()
                return

        # Formulario
        row = 0
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=descripcion_var, width=40).grid(row=row, column=1, sticky=tk.EW, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Monto:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=monto_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Fecha (YYYY-MM-DD):").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        # Considerar usar tkcalendar.DateEntry si está disponible y se quiere un selector de fecha
        ttk.Entry(main_frame, textvariable=fecha_var, width=15).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Combobox(main_frame, textvariable=estado_var, values=["Pendiente", "Cobrado", "Cancelado"], 
                    state="readonly", width=18).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Combobox(main_frame, textvariable=tipo_var, values=["Consulta", "Representación", "Gestión", "Acuerdo", "Otro"],
                    state="readonly", width=18).grid(row=row, column=1, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=2, padx=5)
        notas_text = tk.Text(main_frame, height=4, width=30, wrap=tk.WORD)
        notas_text.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=5)
        if honorario_data:
            notas_text.insert('1.0', notas_var.get())
        row += 1


        main_frame.columnconfigure(1, weight=1)

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=15, sticky=tk.E)

        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self._save_honorario(honorario_id, self.current_case['id'], 
                                                      descripcion_var.get(), monto_var.get(),
                                                      fecha_var.get(), estado_var.get(), tipo_var.get(),
                                                      notas_text.get('1.0', tk.END).strip(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        dialog.bind("<Return>", lambda event: self._save_honorario(honorario_id, self.current_case['id'],
                                                      descripcion_var.get(), monto_var.get(),
                                                      fecha_var.get(), estado_var.get(), tipo_var.get(),
                                                      notas_text.get('1.0', tk.END).strip(), dialog))


    def _save_honorario(self, honorario_id, case_id, descripcion, monto_str, fecha_str, estado, tipo, notas, dialog):
        """Guardar honorario"""
        if not descripcion.strip():
            messagebox.showwarning("Campo Requerido", "La descripción es obligatoria.", parent=dialog)
            return
        if not fecha_str.strip():
            messagebox.showwarning("Campo Requerido", "La fecha es obligatoria.", parent=dialog)
            return

        try: # Validar formato de fecha
            datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Formato Incorrecto", "La fecha debe estar en formato YYYY-MM-DD.", parent=dialog)
            return

        try:
            monto_float = float(monto_str) if monto_str.strip() else 0.0
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Ingrese un monto numérico válido.", parent=dialog)
            return

        try:
            if honorario_id:
                self.db_crm.update_honorario(honorario_id, case_id, descripcion, monto_float, fecha_str, estado, tipo, notas)
                messagebox.showinfo("Éxito", "Honorario actualizado correctamente.", parent=self.app_controller.root)
            else:
                self.db_crm.add_honorario(case_id, descripcion, monto_float, fecha_str, estado, tipo, notas)
                messagebox.showinfo("Éxito", "Honorario agregado correctamente.", parent=self.app_controller.root)
            
            dialog.destroy()
            self._load_honorarios(case_id)
            self._update_resumen(case_id) # Asegurarse que el resumen se actualice
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar honorario: {e}", parent=dialog)

    def _edit_selected_honorario_wrapper(self, event=None): # Añadido event=None para doble clic
        selected_items = self.honorarios_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione un honorario para editar.", parent=self.app_controller.root)
            return
        honorario_id_str = self.honorarios_tree.item(selected_items[0], 'values')[0]
        try:
            honorario_id = int(honorario_id_str)
            self.open_honorario_dialog(honorario_id=honorario_id)
        except ValueError:
            messagebox.showerror("Error", "ID de honorario inválido.", parent=self.app_controller.root)


    def delete_selected_honorario(self):
        """Eliminar honorario seleccionado"""
        selected_items = self.honorarios_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Seleccione un honorario para eliminar.", parent=self.app_controller.root)
            return

        honorario_id_str = self.honorarios_tree.item(selected_items[0], 'values')[0]
        honorario_desc = self.honorarios_tree.item(selected_items[0], 'values')[1]

        if messagebox.askyesno("Confirmar Eliminación",
                               f"¿Está seguro de que desea eliminar el honorario:\n'{honorario_desc}'?",
                               parent=self.app_controller.root):
            try:
                honorario_id = int(honorario_id_str)
                if self.db_crm.delete_honorario(honorario_id):
                    messagebox.showinfo("Éxito", "Honorario eliminado correctamente.", parent=self.app_controller.root)
                    self._load_honorarios(self.current_case['id'])
                    self._update_resumen(self.current_case['id'])
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el honorario.", parent=self.app_controller.root)
            except ValueError:
                messagebox.showerror("Error", "ID de honorario inválido.", parent=self.app_controller.root)
            except Exception as e:
                 messagebox.showerror("Error", f"Error al eliminar honorario: {e}", parent=self.app_controller.root)


    # --- Métodos de Gastos ---

    def open_gasto_dialog(self, gasto_id=None):
        """Abrir diálogo para agregar o editar un gasto."""
        if not self.current_case:
            messagebox.showwarning("Sin Caso", "Seleccione un caso para gestionar sus gastos.", parent=self.app_controller.root)
            return

        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Nuevo Gasto" if not gasto_id else "Editar Gasto")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("450x450") # Ajustar tamaño según necesidad

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        descripcion_var = tk.StringVar()
        monto_var = tk.StringVar()
        fecha_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        categoria_var = tk.StringVar(value="General")
        reembolsable_var = tk.BooleanVar(value=True)
        notas_var = tk.StringVar()
        comprobante_var = tk.StringVar()

        gasto_data = None
        if gasto_id:
            gasto_data = self.db_crm.get_gasto_by_id(gasto_id) # Necesitas esta función en crm_database.py
            if gasto_data:
                descripcion_var.set(gasto_data.get('descripcion', ''))
                monto_var.set(str(gasto_data.get('monto', '0.0')))
                fecha_var.set(gasto_data.get('fecha', datetime.date.today().strftime("%Y-%m-%d")))
                categoria_var.set(gasto_data.get('categoria', 'General'))
                reembolsable_var.set(bool(gasto_data.get('reembolsable', True)))
                notas_var.set(gasto_data.get('notas', ''))
                comprobante_var.set(gasto_data.get('comprobante_path', ''))
            else:
                messagebox.showerror("Error", "No se pudo cargar el gasto para editar.", parent=dialog)
                dialog.destroy()
                return

        # Formulario
        row = 0
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=descripcion_var, width=40).grid(row=row, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Monto:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=monto_var, width=15).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Fecha (YYYY-MM-DD):").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=fecha_var, width=15).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Combobox(main_frame, textvariable=categoria_var,
                     values=["General", "Viáticos", "Copias", "Tasas Judiciales", "Comunicaciones", "Otros"],
                     state="readonly", width=25).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Checkbutton(main_frame, text="Reembolsable", variable=reembolsable_var).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Comprobante:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        comprobante_entry = ttk.Entry(main_frame, textvariable=comprobante_var, width=30)
        comprobante_entry.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=5)
        ttk.Button(main_frame, text="Buscar...", command=lambda: self._browse_comprobante(comprobante_var)).grid(row=row, column=2, sticky=tk.W, pady=2, padx=2)
        row += 1

        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=2, padx=5)
        notas_gasto_text = tk.Text(main_frame, height=4, width=30, wrap=tk.WORD)
        notas_gasto_text.grid(row=row, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5)
        if gasto_data:
            notas_gasto_text.insert('1.0', notas_var.get())
        row += 1

        main_frame.columnconfigure(1, weight=1)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=15, sticky=tk.E)

        ttk.Button(buttons_frame, text="Guardar",
                  command=lambda: self._save_gasto(gasto_id, self.current_case['id'],
                                                  descripcion_var.get(), monto_var.get(),
                                                  fecha_var.get(), categoria_var.get(),
                                                  reembolsable_var.get(),
                                                  notas_gasto_text.get('1.0', tk.END).strip(),
                                                  comprobante_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        dialog.bind("<Return>", lambda event: self._save_gasto(gasto_id, self.current_case['id'],
                                                  descripcion_var.get(), monto_var.get(),
                                                  fecha_var.get(), categoria_var.get(),
                                                  reembolsable_var.get(),
                                                  notas_gasto_text.get('1.0', tk.END).strip(),
                                                  comprobante_var.get(), dialog))

    def _browse_comprobante(self, path_var):
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(title="Seleccionar archivo de comprobante")
        if filepath:
            path_var.set(filepath)

    def _save_gasto(self, gasto_id, case_id, descripcion, monto_str, fecha_str, categoria, reembolsable, notas, comprobante_path, dialog):
        if not descripcion.strip():
            messagebox.showwarning("Campo Requerido", "La descripción es obligatoria.", parent=dialog)
            return
        if not fecha_str.strip():
            messagebox.showwarning("Campo Requerido", "La fecha es obligatoria.", parent=dialog)
            return

        try:
            datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Formato Incorrecto", "La fecha debe estar en formato YYYY-MM-DD.", parent=dialog)
            return

        try:
            monto_float = float(monto_str) if monto_str.strip() else 0.0
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Ingrese un monto numérico válido.", parent=dialog)
            return

        try:
            if gasto_id:
                self.db_crm.update_gasto(gasto_id, case_id, descripcion, monto_float, fecha_str, categoria, reembolsable, notas, comprobante_path)
                messagebox.showinfo("Éxito", "Gasto actualizado correctamente.", parent=self.app_controller.root)
            else:
                self.db_crm.add_gasto(case_id, descripcion, monto_float, fecha_str, categoria, reembolsable, notas, comprobante_path)
                messagebox.showinfo("Éxito", "Gasto agregado correctamente.", parent=self.app_controller.root)

            dialog.destroy()
            self._load_gastos(case_id)
            self._update_resumen(case_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar gasto: {e}", parent=dialog)


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
    def open_factura_dialog(self, factura_id=None):
        """Abrir diálogo para agregar o editar una factura."""
        if not self.current_case:
            messagebox.showwarning("Sin Caso", "Seleccione un caso para gestionar sus facturas.", parent=self.app_controller.root)
            return

        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Nueva Factura" if not factura_id else "Editar Factura")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("450x450") # Ajustar según necesidad

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        numero_var = tk.StringVar()
        fecha_var = tk.StringVar(value=datetime.date.today().strftime("%Y-%m-%d"))
        monto_var = tk.StringVar()
        fecha_venc_var = tk.StringVar()
        estado_var = tk.StringVar(value="Pendiente")
        descripcion_var = tk.StringVar()
        archivo_path_var = tk.StringVar()
        # Nuevas para edición de pago
        fecha_pago_var = tk.StringVar()
        metodo_pago_var = tk.StringVar()


        factura_data = None
        if factura_id:
            factura_data = self.db_crm.get_factura_by_id(factura_id) # Necesitas get_factura_by_id
            if factura_data:
                numero_var.set(factura_data.get('numero', ''))
                fecha_var.set(factura_data.get('fecha', datetime.date.today().strftime("%Y-%m-%d")))
                monto_var.set(str(factura_data.get('monto', '0.0')))
                fecha_venc_var.set(factura_data.get('fecha_vencimiento', ''))
                estado_var.set(factura_data.get('estado', 'Pendiente'))
                descripcion_var.set(factura_data.get('descripcion', ''))
                archivo_path_var.set(factura_data.get('archivo_path', ''))
                fecha_pago_var.set(factura_data.get('fecha_pago', ''))
                metodo_pago_var.set(factura_data.get('metodo_pago', ''))
            else:
                messagebox.showerror("Error", "No se pudo cargar la factura para editar.", parent=dialog)
                dialog.destroy()
                return

        # Formulario
        row = 0
        ttk.Label(main_frame, text="Número Factura:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=numero_var, width=30).grid(row=row, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Fecha Emisión (YYYY-MM-DD):").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=fecha_var, width=15).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Monto:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=monto_var, width=15).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Fecha Vencimiento (YYYY-MM-DD):").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(main_frame, textvariable=fecha_venc_var, width=15).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Combobox(main_frame, textvariable=estado_var,
                     values=["Pendiente", "Pagada", "Vencida", "Cancelada", "Parcialmente Pagada"],
                     state="readonly", width=25).grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.NW, pady=2, padx=5)
        desc_fact_text = tk.Text(main_frame, height=3, width=30, wrap=tk.WORD)
        desc_fact_text.grid(row=row, column=1, columnspan=2, sticky=tk.EW, pady=2, padx=5)
        if factura_data:
            desc_fact_text.insert('1.0', descripcion_var.get())
        row += 1

        ttk.Label(main_frame, text="Archivo Factura:").grid(row=row, column=0, sticky=tk.W, pady=2, padx=5)
        archivo_entry = ttk.Entry(main_frame, textvariable=archivo_path_var, width=30)
        archivo_entry.grid(row=row, column=1, sticky=tk.EW, pady=2, padx=5)
        ttk.Button(main_frame, text="Buscar...", command=lambda: self._browse_comprobante(archivo_path_var)).grid(row=row, column=2, sticky=tk.W, pady=2, padx=2)
        row += 1

        # Campos para registrar/editar pago
        pago_frame = ttk.LabelFrame(main_frame, text="Información de Pago", padding="5")
        pago_frame.grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Label(pago_frame, text="Fecha Pago (YYYY-MM-DD):").grid(row=0, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Entry(pago_frame, textvariable=fecha_pago_var, width=15).grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(pago_frame, text="Método de Pago:").grid(row=1, column=0, sticky=tk.W, pady=2, padx=5)
        ttk.Combobox(pago_frame, textvariable=metodo_pago_var,
                     values=["Efectivo", "Transferencia", "Cheque", "Tarjeta", "Otro"],
                     width=25).grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        row +=1


        main_frame.columnconfigure(1, weight=1)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=3, pady=15, sticky=tk.E)

        ttk.Button(buttons_frame, text="Guardar",
                  command=lambda: self._save_factura(
                      factura_id, self.current_case['id'], numero_var.get(), fecha_var.get(),
                      monto_var.get(), fecha_venc_var.get(), estado_var.get(),
                      desc_fact_text.get('1.0', tk.END).strip(), archivo_path_var.get(),
                      fecha_pago_var.get(), metodo_pago_var.get(), dialog
                  )).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        dialog.bind("<Return>", lambda event: self._save_factura(
                      factura_id, self.current_case['id'], numero_var.get(), fecha_var.get(),
                      monto_var.get(), fecha_venc_var.get(), estado_var.get(),
                      desc_fact_text.get('1.0', tk.END).strip(), archivo_path_var.get(),
                      fecha_pago_var.get(), metodo_pago_var.get(), dialog
                  ))

    def _save_factura(self, factura_id, case_id, numero, fecha_str, monto_str, fecha_venc_str, estado, descripcion, archivo_path, fecha_pago_str, metodo_pago, dialog):
        if not numero.strip():
            messagebox.showwarning("Campo Requerido", "El número de factura es obligatorio.", parent=dialog)
            return
        if not fecha_str.strip():
            messagebox.showwarning("Campo Requerido", "La fecha de emisión es obligatoria.", parent=dialog)
            return

        try: datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Formato Incorrecto", "La fecha de emisión debe estar en formato YYYY-MM-DD.", parent=dialog)
            return

        if fecha_venc_str.strip():
            try: datetime.datetime.strptime(fecha_venc_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Formato Incorrecto", "La fecha de vencimiento debe estar en formato YYYY-MM-DD (o vacía).", parent=dialog)
                return
        else:
            fecha_venc_str = None # Guardar como NULL si está vacío

        if fecha_pago_str.strip():
            try: datetime.datetime.strptime(fecha_pago_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Formato Incorrecto", "La fecha de pago debe estar en formato YYYY-MM-DD (o vacía).", parent=dialog)
                return
        else:
            fecha_pago_str = None

        try:
            monto_float = float(monto_str) if monto_str.strip() else 0.0
        except ValueError:
            messagebox.showwarning("Monto Inválido", "Ingrese un monto numérico válido.", parent=dialog)
            return

        try:
            if factura_id:
                self.db_crm.update_factura(factura_id, case_id, numero, fecha_str, monto_float, fecha_venc_str, estado, descripcion, archivo_path, fecha_pago_str, metodo_pago)
                messagebox.showinfo("Éxito", "Factura actualizada correctamente.", parent=self.app_controller.root)
            else:
                self.db_crm.add_factura(case_id, numero, fecha_str, monto_float, fecha_venc_str, descripcion, estado, archivo_path, fecha_pago_str, metodo_pago)
                messagebox.showinfo("Éxito", "Factura agregada correctamente.", parent=self.app_controller.root)

            dialog.destroy()
            self._load_facturas(case_id)
            self._update_resumen(case_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar factura: {e}", parent=dialog)


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
