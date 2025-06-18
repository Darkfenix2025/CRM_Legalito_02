import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
# Nota: Calendar, DateEntry no se usan en este módulo

class CasosTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.selected_case = None
        self.current_client_id = None
        self._create_widgets()

    def set_double_click_handler(self, handler):
        """Vincula una función al evento de doble clic del Treeview de casos."""
        self.case_tree.bind('<Double-1>', handler)    

    def _create_widgets(self):
        # Configurar el frame principal de CasosTab para que main_frame se expanda
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Frame principal para casos
        main_frame = ttk.Frame(self)
        # CORRECCIÓN: main_frame debe estar en column=0 si es el widget principal de CasosTab
        main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        main_frame.columnconfigure(0, weight=1) # Para la columna que contiene case_list_frame y case_buttons_frame
        main_frame.rowconfigure(0, weight=1) # Lista casos (con más peso para expandirse)
        main_frame.rowconfigure(1, weight=0) # Botones casos

        # --- Lista de Casos ---
        case_list_frame = ttk.LabelFrame(main_frame, text="Casos Cliente", padding="5")
        case_list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        case_list_frame.columnconfigure(0, weight=1)
        case_list_frame.rowconfigure(0, weight=1)
        case_list_frame.rowconfigure(1, weight=0) # Para scrollbar X

        case_cols = ('ID', 'Número/Año', 'Carátula')
        self.case_tree = ttk.Treeview(case_list_frame, columns=case_cols, show='headings', selectmode='browse')
        self.case_tree.heading('ID', text='ID')
        self.case_tree.heading('Número/Año', text='Nro/Año')
        self.case_tree.heading('Carátula', text='Carátula')
        
        self.case_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.W) # Anchor W para mejor alineación
        self.case_tree.column('Número/Año', width=100, stretch=tk.NO, anchor=tk.W) # Aumentado un poco el ancho
        self.case_tree.column('Carátula', width=200, stretch=tk.YES) # Permitir que se expanda y más ancho inicial

        case_scrollbar_Y = ttk.Scrollbar(case_list_frame, orient=tk.VERTICAL, command=self.case_tree.yview)
        self.case_tree.configure(yscrollcommand=case_scrollbar_Y.set)
        
        case_scrollbar_x = ttk.Scrollbar(case_list_frame, orient=tk.HORIZONTAL, command=self.case_tree.xview)
        self.case_tree.configure(xscrollcommand=case_scrollbar_x.set)
        
        self.case_tree.grid(row=0, column=0, sticky='nsew')
        case_scrollbar_Y.grid(row=0, column=1, sticky='ns')
        case_scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        self.case_tree.bind('<<TreeviewSelect>>', self.on_case_select)

        # --- Botones de Acción ---
        case_buttons_frame = ttk.Frame(main_frame)
        case_buttons_frame.grid(row=1, column=0, sticky='ew', pady=5)
        # Configurar botones para que se expandan uniformemente
        case_buttons_frame.columnconfigure(0, weight=1)
        case_buttons_frame.columnconfigure(1, weight=1)
        case_buttons_frame.columnconfigure(2, weight=1)
        case_buttons_frame.columnconfigure(3, weight=1) # Para select_folder_btn
        case_buttons_frame.columnconfigure(4, weight=1) # Para open_folder_btn


        self.add_case_btn = ttk.Button(case_buttons_frame, text="Alta", command=lambda: self.open_case_dialog(), state=tk.DISABLED)
        self.add_case_btn.grid(row=0, column=0, sticky='ew', padx=(0,2))

        self.edit_case_btn = ttk.Button(case_buttons_frame, text="Modificar", command=lambda: self.open_case_dialog(self.selected_case['id'] if self.selected_case else None), state=tk.DISABLED)
        self.edit_case_btn.grid(row=0, column=1, sticky='ew', padx=2)

        self.delete_case_btn = ttk.Button(case_buttons_frame, text="Baja", command=self.delete_case, state=tk.DISABLED)
        self.delete_case_btn.grid(row=0, column=2, sticky='ew', padx=2)
        
        # Botones de carpeta que estaban comentados en la traza original, los incluyo si eran intencionales
        self.select_folder_btn = ttk.Button(case_buttons_frame, text="Carpeta", command=self.select_case_folder, state=tk.DISABLED)
        self.select_folder_btn.grid(row=0, column=3, sticky='ew', padx=2)

        self.open_folder_btn = ttk.Button(case_buttons_frame, text="Abrir Carpeta", command=self.open_case_folder, state=tk.DISABLED)
        #self.open_folder_btn.grid(row=0, column=4, sticky='ew', padx=(2,0))


        # El calendario y botón de agregar audiencia se movieron a audiencias_ui.py
        # Si update_add_audiencia_button_state es específico para CasosTab, debería quedarse.
        # Si era para AudienciasTab, debe moverse o eliminarse de allí.
        # Por ahora, lo dejo aquí, ya que no se llama desde CasosTab.
    
    # def update_add_audiencia_button_state(self):
    #    # Esta función parece pertenecer más a audiencias_ui.py o su lógica ser manejada allí
    #    # Si el botón "Agregar Audiencia" depende de un caso seleccionado,
    #    # el módulo de audiencias debería consultar al app_controller.selected_case
    #    # Por ahora, la comento aquí para evitar confusiones.
    #    pass


    def load_cases_by_client(self, client_id):
        """Cargar casos del cliente especificado"""
        self.current_client_id = client_id
        
        for item in self.case_tree.get_children():
            self.case_tree.delete(item)

        if not client_id:
            self.disable_case_buttons()
            self.add_case_btn.config(state=tk.DISABLED) 
            return

        try:
            cases = self.db_crm.get_cases_by_client(client_id)
            for case_data in cases: # Renombrado a case_data para evitar conflicto con el módulo 'case'
                # Formatear Número/Año
                num_exp = case_data.get('numero_expediente', '')
                anio = case_data.get('anio_caratula', '')
                numero_anio = f"{num_exp}/{anio}" if num_exp and anio else num_exp or anio

                self.case_tree.insert('', 'end', values=(
                    case_data['id'],
                    numero_anio, # Columna combinada
                    case_data.get('caratula', '')
                    # Los campos comentados abajo no coinciden con case_cols
                    # case_data.get('num_expediente', ''),
                    # case_data.get('anio_caratula', ''),
                    # case_data.get('juzgado', ''),
                    # case_data.get('etapa_procesal', ''),
                    # case_data.get('etiquetas', '')
                ))
            
            self.add_case_btn.config(state=tk.NORMAL)
            self.disable_case_buttons() # Asegurarse que los botones de editar/borrar están deshabilitados hasta seleccionar un caso
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar casos: {e}")
            self.add_case_btn.config(state=tk.DISABLED)

    def clear_case_list(self):
        for item in self.case_tree.get_children():
            self.case_tree.delete(item)
        self.selected_case = None
        self.disable_case_buttons()
        self.add_case_btn.config(state=tk.DISABLED if not self.current_client_id else tk.NORMAL)
        if hasattr(self.app_controller, 'on_case_selected'):
            self.app_controller.on_case_selected(None)

    def on_case_select(self, event):
        selected_items = self.case_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            # El primer valor ('values'[0]) es el ID
            case_id_str = self.case_tree.item(selected_item, 'values')[0] 
            
            try:
                case_id = int(case_id_str) # Convertir a int
                case_data = self.db_crm.get_case_by_id(case_id)
                if case_data:
                    self.selected_case = case_data
                    self.enable_case_buttons()
                    if hasattr(self.app_controller, 'on_case_selected'):
                        self.app_controller.on_case_selected(case_data)
                else:
                    self.selected_case = None
                    self.disable_case_buttons()
                    if hasattr(self.app_controller, 'on_case_selected'):
                        self.app_controller.on_case_selected(None)
            except ValueError:
                messagebox.showerror("Error", f"ID de caso inválido: {case_id_str}")
                self.selected_case = None
                self.disable_case_buttons()
                if hasattr(self.app_controller, 'on_case_selected'):
                    self.app_controller.on_case_selected(None)
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener detalles del caso: {e}")
                self.selected_case = None
                self.disable_case_buttons()
                if hasattr(self.app_controller, 'on_case_selected'):
                    self.app_controller.on_case_selected(None)
        else:
            self.selected_case = None
            self.disable_case_buttons()
            if hasattr(self.app_controller, 'on_case_selected'):
                self.app_controller.on_case_selected(None)


    def enable_case_buttons(self):
        self.edit_case_btn.config(state=tk.NORMAL)
        self.delete_case_btn.config(state=tk.NORMAL)
        self.select_folder_btn.config(state=tk.NORMAL)
        
        if self.selected_case and self.selected_case.get('ruta_documentos') and os.path.exists(self.selected_case['ruta_documentos']):
            self.open_folder_btn.config(state=tk.NORMAL)
        else:
            self.open_folder_btn.config(state=tk.DISABLED)

    def disable_case_buttons(self):
        self.edit_case_btn.config(state=tk.DISABLED)
        self.delete_case_btn.config(state=tk.DISABLED)
        self.select_folder_btn.config(state=tk.DISABLED)
        self.open_folder_btn.config(state=tk.DISABLED)

    def open_case_dialog(self, case_id=None):
        if not self.current_client_id and not case_id:
            messagebox.showwarning("Sin Cliente", "Seleccione un cliente primero.")
            return

        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Alta/Edición de Caso")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("600x500") # Considerar hacerlo un poco más alto (e.g., 600x550)
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        caratula_var = tk.StringVar()
        num_exp_var = tk.StringVar()
        anio_var = tk.StringVar()
        juzgado_var = tk.StringVar()
        jurisdiccion_var = tk.StringVar()
        etapa_var = tk.StringVar()
        # notas_var = tk.StringVar() # No necesario si se usa Text widget directamente
        ruta_var = tk.StringVar()
        inact_days_var = tk.StringVar()
        inact_enabled_var = tk.BooleanVar()
        etiquetas_var = tk.StringVar()

        cliente_id_for_case = self.current_client_id # ID del cliente para el caso
        
        if case_id:
            try:
                case_data = self.db_crm.get_case_by_id(case_id)
                if case_data:
                    cliente_id_for_case = case_data['cliente_id'] # Usar el ID del cliente del caso que se edita
                    caratula_var.set(case_data.get('caratula', ''))
                    num_exp_var.set(case_data.get('numero_expediente', ''))
                    anio_var.set(case_data.get('anio_caratula', ''))
                    juzgado_var.set(case_data.get('juzgado', ''))
                    jurisdiccion_var.set(case_data.get('jurisdiccion', ''))
                    etapa_var.set(case_data.get('etapa_procesal', ''))
                    # Para notas_text, se setea después de crear el widget
                    ruta_var.set(case_data.get('ruta_documentos', ''))
                    inact_days_var.set(str(case_data.get('inactividad_dias', 0)))
                    inact_enabled_var.set(bool(case_data.get('alerta_inactividad', False)))
                    etiquetas_var.set(case_data.get('etiquetas', ''))
                    initial_notas = case_data.get('notas', '')
                else:
                    messagebox.showerror("Error", "No se pudieron cargar los datos del caso.")
                    dialog.destroy()
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar datos del caso: {e}")
                dialog.destroy()
                return
        else:
            initial_notas = ""


        row = 0
        
        ttk.Label(main_frame, text="Carátula:").grid(row=row, column=0, sticky=tk.W, pady=5)
        caratula_entry = ttk.Entry(main_frame, textvariable=caratula_var, width=50)
        caratula_entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        row += 1

        ttk.Label(main_frame, text="Nº Expediente:").grid(row=row, column=0, sticky=tk.W, pady=5)
        num_exp_entry = ttk.Entry(main_frame, textvariable=num_exp_var, width=20)
        num_exp_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Año:").grid(row=row, column=2, sticky=tk.W, pady=5, padx=(10, 0)) # padx corregido
        anio_entry = ttk.Entry(main_frame, textvariable=anio_var, width=10)
        anio_entry.grid(row=row, column=3, sticky=tk.W, pady=5, padx=(5, 0)) # padx corregido
        row += 1

        ttk.Label(main_frame, text="Juzgado:").grid(row=row, column=0, sticky=tk.W, pady=5)
        juzgado_entry = ttk.Entry(main_frame, textvariable=juzgado_var, width=50)
        juzgado_entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        row += 1

        ttk.Label(main_frame, text="Jurisdicción:").grid(row=row, column=0, sticky=tk.W, pady=5)
        jurisdiccion_entry = ttk.Entry(main_frame, textvariable=jurisdiccion_var, width=50)
        jurisdiccion_entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        row += 1

        ttk.Label(main_frame, text="Etapa Procesal:").grid(row=row, column=0, sticky=tk.W, pady=5)
        etapa_entry = ttk.Entry(main_frame, textvariable=etapa_var, width=50)
        etapa_entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        row += 1

        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notas_text = tk.Text(main_frame, height=4, width=50, wrap=tk.WORD)
        notas_text.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        if initial_notas: # Usar la variable cargada
            notas_text.insert('1.0', initial_notas)
        row += 1

        ttk.Label(main_frame, text="Ruta Documentos:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ruta_entry = ttk.Entry(main_frame, textvariable=ruta_var, width=40)
        ruta_entry.grid(row=row, column=1, columnspan=2, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 2
        ttk.Button(main_frame, text="Seleccionar", 
                  command=lambda: self._select_folder_for_dialog(ruta_var)).grid(row=row, column=3, pady=5, padx=(5, 0)) # column a 3
        row += 1

        inact_frame = ttk.LabelFrame(main_frame, text="Alerta de Inactividad") # Usar LabelFrame
        inact_frame.grid(row=row, column=0, columnspan=4, sticky=tk.EW, pady=10, padx=(0,0)) # columnspan a 4
        
        inact_check = ttk.Checkbutton(inact_frame, text="Activar Alerta", variable=inact_enabled_var) # Texto más claro
        inact_check.pack(side=tk.LEFT, padx=5) # Usar pack dentro de este frame simple
        
        ttk.Label(inact_frame, text="Días:").pack(side=tk.LEFT, padx=(5, 2))
        inact_days_entry = ttk.Entry(inact_frame, textvariable=inact_days_var, width=5) # Ancho ajustado
        inact_days_entry.pack(side=tk.LEFT, padx=(0,5))
        row += 1

        ttk.Label(main_frame, text="Etiquetas:").grid(row=row, column=0, sticky=tk.W, pady=5)
        etiquetas_entry = ttk.Entry(main_frame, textvariable=etiquetas_var, width=50)
        etiquetas_entry.grid(row=row, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=(10, 0)) # columnspan a 3
        
        ttk.Label(main_frame, text="(Separadas por comas)", font=('', 8)).grid(row=row+1, column=1, columnspan=3, sticky=tk.W, padx=(10, 0)) # columnspan a 3
        row += 2

        main_frame.columnconfigure(1, weight=3) # Dar más peso a la columna de los entries
        main_frame.columnconfigure(3, weight=1) # Para el botón seleccionar y año

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=4, pady=20) # columnspan a 4

        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self.save_case(case_id, cliente_id_for_case, caratula_var.get(), num_exp_var.get(),
                                                anio_var.get(), juzgado_var.get(), jurisdiccion_var.get(),
                                                etapa_var.get(), notas_text.get('1.0', tk.END).strip(),
                                                ruta_var.get(), inact_days_var.get(), inact_enabled_var.get(),
                                                etiquetas_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        caratula_entry.focus_set()

    def _select_folder_for_dialog(self, ruta_var):
        folder = filedialog.askdirectory(title="Seleccionar Carpeta de Documentos")
        if folder:
            ruta_var.set(folder)

    def save_case(self, case_id, cliente_id, caratula, num_exp, anio, juzgado, jurisdiccion, etapa, notas, ruta, inact_days_str, inact_enabled, etiquetas_str, dialog):
        if not caratula.strip():
            messagebox.showwarning("Campo Requerido", "La carátula del caso es obligatoria.", parent=dialog)
            return
        if not cliente_id: # Asegurarse que hay un cliente ID
            messagebox.showerror("Error", "No se ha especificado un ID de cliente para este caso.", parent=dialog)
            return

        try:
            inact_days_int = int(inact_days_str) if inact_days_str.strip() else 0
        except ValueError:
            messagebox.showwarning("Dato Inválido", "Los días de inactividad deben ser un número. Se usará 0.", parent=dialog)
            inact_days_int = 0

        try:
            if case_id:
                self.db_crm.update_case(case_id, caratula, num_exp, anio, juzgado, 
                                       jurisdiccion, etapa, notas, ruta, inact_days_int, inact_enabled)
                messagebox.showinfo("Éxito", "Caso actualizado correctamente.", parent=dialog)
            else:
                self.db_crm.add_case(cliente_id, caratula, num_exp, anio, juzgado, 
                                    jurisdiccion, etapa, notas, ruta, inact_days_int, inact_enabled, etiquetas_str)
                messagebox.showinfo("Éxito", "Caso creado correctamente.", parent=dialog)

            dialog.destroy()
            self.load_cases_by_client(self.current_client_id)
            # Si se actualizó el caso actualmente seleccionado, refrescar la vista de detalles
            if self.selected_case and (not case_id or int(case_id) == self.selected_case['id']):
                updated_case_data = self.db_crm.get_case_by_id(self.selected_case['id'] if case_id else self.db_crm.get_last_inserted_case_id())
                if updated_case_data and hasattr(self.app_controller, 'on_case_selected'):
                     self.app_controller.on_case_selected(updated_case_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar caso: {e}", parent=dialog)

    def delete_case(self):
        if not self.selected_case:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un caso para eliminar.")
            return

        response = messagebox.askyesno("Confirmar Eliminación", 
                                     f"¿Está seguro de que desea eliminar el caso '{self.selected_case['caratula']}'?\n\n"
                                     "ADVERTENCIA: Se eliminarán también todas las tareas, partes y actividades asociadas.")

        if response:
            try:
                self.db_crm.delete_case(self.selected_case['id'])
                messagebox.showinfo("Éxito", "Caso eliminado correctamente.")
                
                # Guardar el current_client_id antes de que selected_case se vuelva None
                client_id_to_reload = self.current_client_id
                
                self.selected_case = None # Limpiar la selección
                self.disable_case_buttons()
                
                if hasattr(self.app_controller, 'on_case_deleted'):
                    self.app_controller.on_case_deleted() # Esto podría limpiar más cosas
                
                # Recargar casos del cliente. Es importante hacerlo después de on_case_deleted
                # por si on_case_deleted afecta a current_client_id a través de alguna cadena de llamadas.
                # Pero on_client_changed es más robusto si la lógica de selección de cliente es compleja.
                if client_id_to_reload:
                    self.load_cases_by_client(client_id_to_reload)
                else:
                    self.clear_case_list()

            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar caso: {e}")

    def select_case_folder(self):
        if not self.selected_case:
            messagebox.showwarning("Sin Selección", "Seleccione un caso primero.")
            return

        folder = filedialog.askdirectory(title="Seleccionar Carpeta de Documentos del Caso")
        if folder:
            try:
                self.db_crm.update_case_folder(self.selected_case['id'], folder)
                messagebox.showinfo("Éxito", f"Carpeta asignada: {folder}")
                
                case_data = self.db_crm.get_case_by_id(self.selected_case['id'])
                if case_data:
                    self.selected_case = case_data
                    self.enable_case_buttons() 
                    if hasattr(self.app_controller, 'on_case_folder_updated'):
                        self.app_controller.on_case_folder_updated(case_data)
                        
            except Exception as e:
                messagebox.showerror("Error", f"Error al asignar carpeta: {e}")

    def open_case_folder(self):
        if not self.selected_case or not self.selected_case.get('ruta_documentos'):
            messagebox.showwarning("Sin Carpeta", "No hay carpeta asignada a este caso.")
            return

        folder_path = self.selected_case['ruta_documentos']
        if not os.path.exists(folder_path):
            messagebox.showerror("Carpeta no Encontrada", f"La carpeta no existe: {folder_path}")
            return

        try:
            import subprocess # Mover import aquí para que sea usado solo cuando es necesario
            import sys
            
            if sys.platform == "win32":
                os.startfile(os.path.normpath(folder_path)) # os.path.normpath para asegurar formato correcto
            elif sys.platform == "darwin": # macOS
                subprocess.call(["open", folder_path])
            else: # Linux y otros Unix
                subprocess.call(["xdg-open", folder_path])
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir carpeta: {e}")

    def refresh_data(self):
        current_selected_case_id = self.selected_case['id'] if self.selected_case else None
        
        if self.current_client_id:
            self.load_cases_by_client(self.current_client_id)
            
            if current_selected_case_id:
                # Intentar re-seleccionar el caso si aún existe
                for item in self.case_tree.get_children():
                    if int(self.case_tree.item(item, 'values')[0]) == current_selected_case_id:
                        self.case_tree.selection_set(item)
                        self.case_tree.focus(item) # Opcional: para darle foco visual
                        # La selección disparará on_case_select, que actualizará self.selected_case y botones
                        break 
                else: # Si el caso ya no está en la lista
                    self.selected_case = None
                    self.disable_case_buttons()
                    if hasattr(self.app_controller, 'on_case_selected'):
                         self.app_controller.on_case_selected(None)
            else:
                self.selected_case = None
                self.disable_case_buttons()

    def get_selected_case(self):
        return self.selected_case

    def on_client_changed(self, client_data):
        if client_data:
            self.load_cases_by_client(client_data['id'])
        else:
            self.clear_case_list()

    def bind_double_click(self, callback):
        """
        Vincular evento de doble clic en la lista de casos
        El callback recibe case_data como parámetro
        """
        def on_double_click(event):
            if self.selected_case:
                callback(self.selected_case)
        
        self.case_tree.bind('<Double-1>', on_double_click)