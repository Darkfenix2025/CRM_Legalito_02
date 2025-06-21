import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import re
import webbrowser
import urllib.parse
from tkcalendar import Calendar, DateEntry

class AudienciasTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.selected_audiencia_id = None
        self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
        self._create_widgets()
        # self.update_add_audiencia_button_state() # Se llama al final de _create_widgets

    def _create_widgets(self):
        # El AudienciasTab (self) ahora se dividirá en dos columnas principales.
        # Columna 0: Calendario y botón de agregar.
        # Columna 1: Lista de audiencias, botones de acción y detalles.
        self.columnconfigure(0, weight=1) # Calendario
        self.columnconfigure(1, weight=2) # Lista y detalles
        self.rowconfigure(0, weight=1)    # Fila única

        # --- Columna 0: Calendario y Botón Agregar ---
        col0_frame = ttk.Frame(self)
        col0_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=5)
        col0_frame.rowconfigure(0, weight=1) # Calendario
        col0_frame.rowconfigure(1, weight=0) # Botón
        col0_frame.columnconfigure(0, weight=1)

        calendar_labelframe = ttk.LabelFrame(col0_frame, text="Calendario", padding="5")
        calendar_labelframe.grid(row=0, column=0, sticky='nsew', pady=(0,5))
        calendar_labelframe.rowconfigure(0, weight=1)
        calendar_labelframe.columnconfigure(0, weight=1)

        self.calendar = Calendar(calendar_labelframe, selectmode='day', date_pattern='yyyy-mm-dd',
                                 tooltipforeground='black', tooltipbackground='#FFFFE0', locale='es_ES')
        self.calendar.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.calendar.bind("<<CalendarSelected>>", self.actualizar_lista_audiencias)
        self.calendar.tag_config('audiencia_marcador', background='lightblue', foreground='black')

        add_aud_frame = ttk.Frame(col0_frame)
        add_aud_frame.grid(row=1, column=0, sticky='ew', pady=(5,0), padx=5)
        self.add_audiencia_btn = ttk.Button(add_aud_frame, text="Agregar Audiencia",
                                            command=lambda: self.abrir_dialogo_audiencia())
        self.add_audiencia_btn.pack(fill=tk.X, padx=0, pady=0)


        # --- Columna 1: Lista de Audiencias, Acciones y Detalles ---
        col1_frame = ttk.Frame(self)
        col1_frame.grid(row=0, column=1, sticky='nsew', padx=(5,0), pady=5)
        col1_frame.rowconfigure(0, weight=2) # Lista de audiencias con más peso
        col1_frame.rowconfigure(1, weight=0) # Botones de acción
        col1_frame.rowconfigure(2, weight=1) # Detalles de audiencia
        col1_frame.columnconfigure(0, weight=1)

        # Lista de Audiencias
        audiencias_list_labelframe = ttk.LabelFrame(col1_frame, text="Audiencias del Día", padding="5")
        audiencias_list_labelframe.grid(row=0, column=0, sticky='nsew', pady=(0,5))
        audiencias_list_labelframe.rowconfigure(0, weight=1)
        audiencias_list_labelframe.columnconfigure(0, weight=1)

        audiencias_cols = ("ID", "Hora", "Detalle", "Caso Asociado", "Link")
        self.audiencias_tree = ttk.Treeview(audiencias_list_labelframe, columns=audiencias_cols, show='headings', selectmode="browse")
        self.audiencias_tree.heading("ID", text="ID")
        self.audiencias_tree.heading("Hora", text="Hora")
        self.audiencias_tree.heading("Detalle", text="Detalle")
        self.audiencias_tree.heading("Caso Asociado", text="Caso")
        self.audiencias_tree.heading("Link", text="Link")

        self.audiencias_tree.column("ID", width=30, stretch=tk.NO, anchor=tk.CENTER)
        self.audiencias_tree.column("Hora", width=50, stretch=tk.NO, anchor=tk.CENTER)
        self.audiencias_tree.column("Detalle", width=150, stretch=True)
        self.audiencias_tree.column("Caso Asociado", width=120, stretch=True)
        self.audiencias_tree.column("Link", width=100, stretch=True)

        audiencias_scrollbar_y = ttk.Scrollbar(audiencias_list_labelframe, orient=tk.VERTICAL, command=self.audiencias_tree.yview)
        self.audiencias_tree.configure(yscrollcommand=audiencias_scrollbar_y.set)
        audiencias_scrollbar_y.grid(row=0, column=1, sticky='ns')
        self.audiencias_tree.grid(row=0, column=0, sticky='nsew')
        # Scrollbar X (opcional)
        audiencias_scrollbar_x = ttk.Scrollbar(audiencias_list_labelframe, orient=tk.HORIZONTAL, command=self.audiencias_tree.xview)
        self.audiencias_tree.configure(xscrollcommand=audiencias_scrollbar_x.set)
        audiencias_scrollbar_x.grid(row=1, column=0, sticky='ew')


        self.audiencias_tree.bind('<<TreeviewSelect>>', self.on_audiencia_tree_select)
        self.audiencias_tree.bind("<Double-1>", self.abrir_link_audiencia_seleccionada)

        # Botones de Acción para Audiencias
        audiencia_actions_frame = ttk.Frame(col1_frame)
        audiencia_actions_frame.grid(row=1, column=0, sticky='ew', pady=5)
        # Distribuir espacio equitativamente entre los botones
        for i in range(4): # Asumiendo 4 botones
            audiencia_actions_frame.columnconfigure(i, weight=1)

        self.edit_audiencia_btn = ttk.Button(audiencia_actions_frame, text="Editar",
                                           command=self.editar_audiencia_seleccionada, state=tk.DISABLED)
        self.edit_audiencia_btn.grid(row=0, column=0, sticky='ew', padx=(0,2))
        self.delete_audiencia_btn = ttk.Button(audiencia_actions_frame, text="Eliminar",
                                             command=self.eliminar_audiencia_seleccionada, state=tk.DISABLED)
        self.delete_audiencia_btn.grid(row=0, column=1, sticky='ew', padx=2)
        self.share_btn = ttk.Button(audiencia_actions_frame, text="Compartir",
                                   command=self.mostrar_menu_compartir_audiencia, state=tk.DISABLED)
        self.share_btn.grid(row=0, column=2, sticky='ew', padx=2)
        self.open_link_btn = ttk.Button(audiencia_actions_frame, text="Abrir Link",
                                       command=self.abrir_link_audiencia_seleccionada, state=tk.DISABLED)
        self.open_link_btn.grid(row=0, column=3, sticky='ew', padx=(2,0))


        # Detalles Completos de Audiencia (usando tk.Text)
        audiencia_details_labelframe = ttk.LabelFrame(col1_frame, text="Detalles Completos Audiencia", padding="5")
        audiencia_details_labelframe.grid(row=2, column=0, sticky='nsew', pady=(5,0))
        audiencia_details_labelframe.rowconfigure(0, weight=1)
        audiencia_details_labelframe.columnconfigure(0, weight=1)

        self.audiencia_details_text = tk.Text(audiencia_details_labelframe, height=5, wrap=tk.WORD, state=tk.DISABLED)
        audiencia_details_scroll = ttk.Scrollbar(audiencia_details_labelframe, orient=tk.VERTICAL, command=self.audiencia_details_text.yview)
        self.audiencia_details_text.configure(yscrollcommand=audiencia_details_scroll.set)
        
        self.audiencia_details_text.grid(row=0, column=0, sticky='nsew')
        audiencia_details_scroll.grid(row=0, column=1, sticky='ns')

        self.cargar_audiencias_fecha_actual()
        self.marcar_dias_audiencias_calendario()
        self.update_add_audiencia_button_state()


    def update_add_audiencia_button_state(self):
        # El estado del botón "Agregar Audiencia" depende de si hay un caso seleccionado en el app_controller
        if hasattr(self.app_controller, 'selected_case') and self.app_controller.selected_case:
            self.add_audiencia_btn.config(state=tk.NORMAL)
        else:
            self.add_audiencia_btn.config(state=tk.DISABLED)

    # def update_add_audiencia_button_state(self):
    #     # Implementar si es necesario, por ejemplo:
    #     # if self.app_controller.selected_case:
    #     #     self.add_audiencia_btn.config(state=tk.NORMAL)
    #     # else:
    #     #     self.add_audiencia_btn.config(state=tk.DISABLED) # O siempre NORMAL
    #     pass


    def cargar_audiencias_fecha_actual(self):
        self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
        # Asegurarse que el calendario visualmente muestra la fecha actual al inicio
        try:
            current_date = datetime.datetime.strptime(self.fecha_seleccionada_agenda, "%Y-%m-%d").date()
            self.calendar.selection_set(current_date)
        except Exception as e:
            print(f"Error setting calendar initial date: {e}")
        self.actualizar_lista_audiencias() # Llamar sin argumento de evento para la carga inicial
        self.marcar_dias_audiencias_calendario()

    def actualizar_lista_audiencias(self, event=None):
        if event: # Solo actualizar si es un evento de calendario (selección de fecha)
            if hasattr(self.calendar, 'selection_get') and self.calendar.selection_get():
                try:
                    fecha_sel = self.calendar.selection_get()
                    self.fecha_seleccionada_agenda = fecha_sel.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Error obteniendo fecha del calendario: {e}")
                    self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
            else: # Fallback si no se puede obtener la selección del calendario
                 self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
        # Si no hay evento (ej. carga inicial o refresh_data), usamos la fecha ya almacenada en self.fecha_seleccionada_agenda.

        for item in self.audiencias_tree.get_children():
            self.audiencias_tree.delete(item)
        
        self.limpiar_detalles_audiencia_text()
        self.deshabilitar_botones_audiencia()

        try:
            audiencias = self.db_crm.get_audiencias_by_fecha(self.fecha_seleccionada_agenda)
            for aud in audiencias:
                hora = aud.get('hora', '--:--') or "--:--"
                desc_full = aud.get('descripcion','')
                desc_corta = (desc_full.split('\n')[0])[:60] + ('...' if len(desc_full) > 60 else '')

                caso_caratula_full = aud.get('caso_caratula', 'Caso Desc.')
                if 'caso_caratula' not in aud and aud.get('caso_id'): # Si falta la carátula, buscarla
                     caso_obj = self.db_crm.get_case_by_id(aud['caso_id'])
                     if caso_obj:
                         caso_caratula_full = caso_obj.get('caratula', 'Caso Desc.')

                caso_corto = caso_caratula_full[:50] + ('...' if len(caso_caratula_full) > 50 else '')

                link_full = aud.get('link','') or ""
                link_corto = link_full[:40] + ('...' if len(link_full) > 40 else '')

                self.audiencias_tree.insert("", tk.END, values=(
                    aud['id'],
                    hora,
                    desc_corta,
                    caso_corto,
                    link_corto
                ), iid=str(aud['id']))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar audiencias: {e}", parent=self)

    def marcar_dias_audiencias_calendario(self):
        try:
            self.calendar.calevent_remove(tag='audiencia_marcador') # Usar el tag definido en _create_widgets
            fechas_con_audiencias = self.db_crm.get_fechas_con_audiencias() # get_fechas_con_audiencias en lugar de get_dates_with_audiencias
            
            for fecha_str in fechas_con_audiencias:
                try:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    self.calendar.calevent_create(fecha, "Audiencia", tags='audiencia_marcador') # Usar el tag correcto
                except ValueError:
                    print(f"Formato de fecha inválido en base de datos: {fecha_str}")
                    continue
        except Exception as e:
            print(f"Error al marcar días con audiencias: {e}")

    def on_audiencia_tree_select(self, event=None):
        selected_items = self.audiencias_tree.selection()
        if selected_items:
            selected_item_iid = selected_items[0] # El iid es el ID de la audiencia
            try:
                audiencia_id = int(selected_item_iid)
                self.selected_audiencia_id = audiencia_id
                self.mostrar_detalles_audiencia_text(audiencia_id) # Llamar a la nueva función de detalles
                self.habilitar_botones_audiencia()
            except ValueError:
                 messagebox.showerror("Error", f"ID de audiencia inválido: {selected_item_iid}", parent=self)
                 self.selected_audiencia_id = None
                 self.limpiar_detalles_audiencia_text()
                 self.deshabilitar_botones_audiencia()
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener detalles de la audiencia: {e}", parent=self)
                self.selected_audiencia_id = None
                self.limpiar_detalles_audiencia_text()
                self.deshabilitar_botones_audiencia()
        else:
            self.selected_audiencia_id = None
            self.limpiar_detalles_audiencia_text()
            self.deshabilitar_botones_audiencia()

    def mostrar_detalles_audiencia_text(self, audiencia_id):
        """Muestra los detalles completos de la audiencia en el widget tk.Text."""
        self.limpiar_detalles_audiencia_text()
        self.audiencia_details_text.config(state=tk.NORMAL)
        try:
            audiencia = self.db_crm.get_audiencia_by_id(audiencia_id) # Este método ya hace JOIN con caso y cliente
            if audiencia:
                hora = audiencia.get('hora') or "Sin hora"
                link = audiencia.get('link') or "Sin link"
                rec_activo = "Sí" if audiencia.get('recordatorio_activo') else "No"
                rec_minutos = f" ({audiencia.get('recordatorio_minutos', 15)} min antes)" if audiencia.get('recordatorio_activo') else ""
                
                caso_caratula = audiencia.get('caso_caratula', 'Caso Desconocido')
                # cliente_nombre = audiencia.get('cliente_nombre', 'Cliente Desconocido') # No se usa en el formato de main_app.py

                # Formato similar a main_app.py
                texto_detalle = (
                    f"**Audiencia ID:** {audiencia['id']}\n"
                    # f"**Cliente:** {cliente_nombre}\n" # No presente en la versión original de main_app para detalles
                    f"**Caso:** {caso_caratula} (ID: {audiencia['caso_id']})\n"
                    f"------------------------------------\n"
                    f"**Fecha:** {audiencia.get('fecha', 'N/A')}\n"
                    f"**Hora:** {hora}\n\n"
                    f"**Descripción:**\n{audiencia.get('descripcion', 'N/A')}\n\n"
                    f"**Link:**\n{link}\n\n"
                    f"**Recordatorio:** {rec_activo}{rec_minutos}"
                )
                self.audiencia_details_text.insert('1.0', texto_detalle)
            else:
                self.audiencia_details_text.insert('1.0', "Detalles no disponibles.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}", parent=self)
            self.audiencia_details_text.insert('1.0', "Error al cargar detalles.")
        finally:
            self.audiencia_details_text.config(state=tk.DISABLED)

    def limpiar_detalles_audiencia_text(self):
        """Limpia el widget tk.Text de detalles."""
        if hasattr(self, 'audiencia_details_text'): # Asegurar que el widget existe
            self.audiencia_details_text.config(state=tk.NORMAL)
            self.audiencia_details_text.delete('1.0', tk.END)
            self.audiencia_details_text.config(state=tk.DISABLED)

    def habilitar_botones_audiencia(self):
        self.edit_audiencia_btn.config(state=tk.NORMAL)
        self.delete_audiencia_btn.config(state=tk.NORMAL) 
        self.share_btn.config(state=tk.NORMAL) 
        
        link_presente = False
        if self.selected_audiencia_id:
            try:
                audiencia = self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
                if audiencia and audiencia.get('link') and audiencia.get('link').strip():
                    link_presente = True
            except Exception as e:
                print(f"Error al verificar link de audiencia: {e}")

        self.open_link_btn.config(state=tk.NORMAL if link_presente else tk.DISABLED)


    def deshabilitar_botones_audiencia(self):
        self.edit_audiencia_btn.config(state=tk.DISABLED)
        self.delete_audiencia_btn.config(state=tk.DISABLED)
        self.open_link_btn.config(state=tk.DISABLED)
        self.share_btn.config(state=tk.DISABLED)

    def abrir_dialogo_audiencia(self, audiencia_id=None, parent_window=None): # Mantenemos parent_window por si se usa desde otro lado
        parent_to_use = parent_window if parent_window else self.app_controller.root
        dialog = tk.Toplevel(parent)
        dialog.title("Alta/Edición de Audiencia")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("550x480") # Ajustar tamaño si es necesario
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        caso_id_var = tk.StringVar() # Cambiado de caso_var a caso_id_var para claridad
        caso_nombre_var = tk.StringVar(value="Ninguno (Haga clic en Buscar)") # <-- NUEVA VARIABLE
        fecha_var = tk.StringVar()
        hora_var = tk.StringVar()
        link_var = tk.StringVar()
        # desc_var no es necesaria, se lee directo del Text widget
        recordatorio_var = tk.BooleanVar()
        minutos_var = tk.StringVar(value="30")
        initial_desc = "" # Para el Text widget

        if audiencia_id:
            #try:
            audiencia_data = self.db_crm.get_audiencia_by_id(audiencia_id)
            if audiencia_data:
                caso_id_var.set(str(audiencia_data.get('caso_id', '')))
                # Obtenemos el nombre del caso
                if audiencia_data.get('caso_id'):
                    caso = self.db_crm.get_case_by_id(audiencia_data['caso_id'])
                    if caso:
                        caso_nombre_var.set(caso.get('caratula', 'ID no encontrado'))
                    
                fecha_var.set(audiencia_data.get('fecha', ''))
                hora_var.set(audiencia_data.get('hora', ''))
                link_var.set(audiencia_data.get('link', ''))
                initial_desc = audiencia_data.get('descripcion', '')
                recordatorio_var.set(bool(audiencia_data.get('recordatorio_activo', False)))
                minutos_var.set(str(audiencia_data.get('recordatorio_minutos', 30)))

            else:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la audiencia.", parent=dialog)
                dialog.destroy()
                return
            #except Exception as e:
            #    messagebox.showerror("Error", f"Error al cargar datos de la audiencia: {e}", parent=dialog)
            #    dialog.destroy()
            #    return
        else:
            fecha_var.set(self.fecha_seleccionada_agenda if self.fecha_seleccionada_agenda else datetime.date.today().strftime("%Y-%m-%d"))
            # Si hay un caso seleccionado en la app principal, proponerlo
            if self.app_controller.selected_case:
                caso_id_var.set(str(self.app_controller.selected_case['id']))

        caso_nombre_var.set(self.app_controller.selected_case.get('caratula', '')) # <-- PONER NOMBRE

        row = 0
# --- NUEVO WIDGET DE SOLO LECTURA PARA EL NOMBRE ---
        ttk.Label(main_frame, text="Caso:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=caso_nombre_var, foreground="blue", wraplength=350).grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Caso ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        caso_frame = ttk.Frame(main_frame)
        caso_frame.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        caso_frame.columnconfigure(0, weight=1)
        caso_entry = ttk.Entry(caso_frame, textvariable=caso_id_var, width=10) # Ancho ajustado
        caso_entry.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Button(caso_frame, text="Buscar/Cambiar Caso", command=lambda: self._seleccionar_caso_para_audiencia(caso_id_var, caso_nombre_var, dialog)).grid(row=0, column=1, padx=(5, 0))
        row += 1

        ttk.Label(main_frame, text="Fecha:").grid(row=row, column=0, sticky=tk.W, pady=5)
        fecha_entry = DateEntry(main_frame, textvariable=fecha_var, date_pattern='yyyy-mm-dd', width=18) # Ancho ajustado
        fecha_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Hora (HH:MM):").grid(row=row, column=0, sticky=tk.W, pady=5)
        hora_entry = ttk.Entry(main_frame, textvariable=hora_var, width=20)
        hora_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Link (opcional):").grid(row=row, column=0, sticky=tk.W, pady=5)
        link_entry = ttk.Entry(main_frame, textvariable=link_var, width=40) # Ancho ajustado
        link_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        desc_text = tk.Text(main_frame, height=5, width=40, wrap=tk.WORD) # Ancho ajustado
        desc_text.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        if initial_desc:
            desc_text.insert('1.0', initial_desc)
        row += 1

        recordatorio_frame = ttk.LabelFrame(main_frame, text="Recordatorio", padding="5")
        recordatorio_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        # recordatorio_frame.columnconfigure(1, weight=1) # No es necesario si se usa pack

        recordatorio_check = ttk.Checkbutton(recordatorio_frame, text="Activar recordatorio", variable=recordatorio_var)
        recordatorio_check.pack(side=tk.LEFT, anchor=tk.W, padx=5) # Usar pack

        min_frame = ttk.Frame(recordatorio_frame) # Subframe para minutos
        min_frame.pack(side=tk.LEFT, anchor=tk.W, padx=5)
        ttk.Label(min_frame, text="Minutos antes:").pack(side=tk.LEFT)
        minutos_entry = ttk.Entry(min_frame, textvariable=minutos_var, width=5) # Ancho ajustado
        minutos_entry.pack(side=tk.LEFT, padx=(5,0))
        row += 1 # Aunque no afecta al grid del padre, es conceptualmente la siguiente "fila" de contenido

        main_frame.columnconfigure(1, weight=1)

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)
        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self.guardar_audiencia(audiencia_id, caso_id_var.get(), fecha_var.get(),
                                                        hora_var.get(), link_var.get(), desc_text.get('1.0', tk.END).strip(),
                                                        recordatorio_var.get(), minutos_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        caso_entry.focus_set()

    def _seleccionar_caso_para_audiencia(self, caso_id_var, caso_nombre_var, parent_dialog):
        caso_id_input = simpledialog.askstring("Seleccionar Caso", 
                                                "Ingrese el ID del caso:",
                                                parent=parent_dialog)
        # Esta es una implementación muy simple. Podrías crear un diálogo más complejo
        # que muestre una lista de casos para seleccionar.
        try:
            # Mostrar una lista de casos del cliente actual si está seleccionado
            client_id = None
            if self.app_controller.selected_client:
                client_id = self.app_controller.selected_client.get('id')
            
            # Opcional: Crear un diálogo más avanzado aquí para buscar/seleccionar casos
            # Por ahora, un simple input.
            
            caso_id_input = simpledialog.askstring("Seleccionar Caso", 
                                                "Ingrese el ID del caso:",
                                                parent=parent_dialog)
            if caso_id_input and caso_id_input.strip().isdigit():
                caso_id_int = int(caso_id_input.strip())
                caso = self.db_crm.get_case_by_id(caso_id_int)
                if caso:
                    caso_id_var.set(str(caso_id_int))
                    caso_nombre_var.set(caso.get('caratula', 'N/A')) # <-- ACTUALIZAR NOMBRE
                    messagebox.showinfo("Caso Seleccionado", f"Caso: {caso.get('caratula', 'N/A')}", parent=parent_dialog)
                else:
                    messagebox.showerror("Error", "Caso no encontrado.", parent=parent_dialog)
            else:
                messagebox.showerror("Error", "Caso no encontrado.", parent=parent_dialog)

        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar caso: {e}", parent=parent_dialog)


    def guardar_audiencia(self, audiencia_id, caso_id_str, fecha_str, hora_str, link, desc, r_act, r_min_str, dialog):
        if not fecha_str:
            messagebox.showwarning("Campo Requerido", "La fecha es obligatoria.", parent=dialog)
            return
        if not hora_str:
            messagebox.showwarning("Campo Requerido", "La hora es obligatoria.", parent=dialog)
            return

        parsed_hora = self.parsear_hora(hora_str)
        if not parsed_hora:
            messagebox.showwarning("Formato Incorrecto", "La hora debe estar en formato HH:MM (ej: 09:30 o 14:00).", parent=dialog)
            return
        hora_str = parsed_hora # Usar la hora parseada y formateada

        try:
            minutos_int = int(r_min_str) if r_min_str.strip() else 30
        except ValueError:
            messagebox.showwarning("Dato Inválido", "Minutos de recordatorio debe ser un número. Se usará 30.", parent=dialog)
            minutos_int = 30

        caso_id_int = None
        if caso_id_str and caso_id_str.strip():
            try:
                caso_id_int = int(caso_id_str.strip())
                if not self.db_crm.get_case_by_id(caso_id_int): # Verificar existencia
                    messagebox.showerror("Error", "El caso especificado (ID) no existe.", parent=dialog)
                    return
            except ValueError:
                messagebox.showerror("Error", "El ID del caso debe ser un número.", parent=dialog)
                return
        
        try:
            if audiencia_id:
            # Llamada para ACTUALIZAR (7 argumentos)
                self.db_crm.update_audiencia(
                    audiencia_id, 
                    fecha_str, 
                    hora_str, 
                    link, 
                    desc, 
                    r_act, 
                    minutos_int
                )
                messagebox.showinfo("Éxito", "Audiencia actualizada correctamente.", parent=dialog)
            else:
                # Llamada para CREAR (con caso_id_int)
                self.db_crm.add_audiencia(caso_id_int, fecha_str, hora_str, link, desc, r_act, minutos_int)
                messagebox.showinfo("Éxito", "Audiencia creada correctamente.", parent=dialog)

            dialog.destroy()
            self.actualizar_lista_audiencias()
            self.marcar_dias_audiencias_calendario()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar audiencia: {e}", parent=dialog)


    def parsear_hora(self, hora_str):
        hora_str = hora_str.strip()
        patron = r'^([01]?[0-9]|2[0-3])[:\.]?([0-5][0-9])$' # Permite HH:MM o HH.MM, o incluso HHMM si son 4 digitos
        if len(hora_str) == 4 and hora_str.isdigit(): # Formato HHMM
            match = re.match(r'([01]?[0-9]|2[0-3])([0-5][0-9])', hora_str)
        else: # Formato HH:MM o HH.MM
            match = re.match(patron, hora_str)

        if match:
            horas, minutos = match.groups()
            return f"{int(horas):02d}:{int(minutos):02d}"
        return None


    def editar_audiencia_seleccionada(self):
        if not self.selected_audiencia_id:
            messagebox.showwarning("Sin Selección", "Seleccione una audiencia para editar.")
            return
        self.abrir_dialogo_audiencia(self.selected_audiencia_id)

    def eliminar_audiencia_seleccionada(self):
        if not self.selected_audiencia_id:
            messagebox.showwarning("Sin Selección", "Seleccione una audiencia para eliminar.")
            return

        response = messagebox.askyesno("Confirmar Eliminación", 
                                     "¿Está seguro de que desea eliminar esta audiencia?")
        if response:
            try:
                self.db_crm.delete_audiencia(self.selected_audiencia_id)
                messagebox.showinfo("Éxito", "Audiencia eliminada correctamente.")
                
                # Guardar la fecha seleccionada antes de que se pierda
                fecha_a_recargar = self.fecha_seleccionada_agenda

                self.selected_audiencia_id = None # Limpiar selección
                self.limpiar_detalles_audiencia()
                self.deshabilitar_botones_audiencia()
                
                # Forzar recarga de la fecha que estaba seleccionada
                self.fecha_seleccionada_agenda = fecha_a_recargar 
                try: # Intentar seleccionar la fecha en el calendario
                    date_obj = datetime.datetime.strptime(fecha_a_recargar, "%Y-%m-%d").date()
                    self.calendar.selection_set(date_obj)
                except: pass # Si falla, no importa mucho, actualizar_lista_audiencias usará la fecha guardada
                
                self.actualizar_lista_audiencias() 
                self.marcar_dias_audiencias_calendario()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar audiencia: {e}")

    def abrir_link_audiencia_seleccionada(self, event=None):
        if not self.selected_audiencia_id:
            if event: # Solo mostrar mensaje si fue un click explícito y no hay selección
                 messagebox.showinfo("Sin Selección", "Seleccione una audiencia primero.")
            return

        try:
            audiencia = self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
            if audiencia and audiencia.get('link'):
                link = audiencia['link'].strip()
                if not link.startswith(('http://', 'https://')):
                    link = f"https://{link}" # Asumir https si no hay protocolo
                
                # Validar URL antes de abrir (opcional pero recomendado)
                parsed_url = urllib.parse.urlparse(link)
                if parsed_url.scheme and parsed_url.netloc:
                    webbrowser.open(link)
                else:
                    messagebox.showwarning("Link Inválido", f"El link '{audiencia['link']}' no parece ser una URL válida.")
            else:
                messagebox.showinfo("Sin Link", "Esta audiencia no tiene un link asociado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir link: {e}")


    def mostrar_menu_compartir_audiencia(self):
        if not self.selected_audiencia_id:
            messagebox.showwarning("Sin Selección", "Seleccione una audiencia para compartir.")
            return

        menu = tk.Menu(self.app_controller.root, tearoff=0)
        menu.add_command(label="Compartir por Email", command=self._compartir_audiencia_por_email)
        menu.add_command(label="Compartir por WhatsApp", command=self._compartir_audiencia_por_whatsapp)
        
        try:
            # Posicionar el menú cerca del botón "Compartir" o el cursor
            x = self.share_btn.winfo_rootx()
            y = self.share_btn.winfo_rooty() + self.share_btn.winfo_height()
            menu.tk_popup(x, y)
        except Exception: # Fallback a la posición del cursor si el botón no es localizable
            menu.tk_popup(self.app_controller.root.winfo_pointerx(), self.app_controller.root.winfo_pointery())
        finally:
            menu.grab_release()


    def _formatear_texto_audiencia_para_compartir(self, audiencia):
        caso_info = "Sin caso asociado"
        if audiencia.get('caso_id'):
            try:
                caso = self.db_crm.get_case_by_id(audiencia['caso_id'])
                if caso:
                    caso_info = f"{caso.get('caratula', 'N/A')}"
                else:
                    caso_info = f"ID: {audiencia['caso_id']} (No encontrado)"
            except:
                caso_info = f"ID: {audiencia['caso_id']} (Error)"

        texto = f"""🏛️ RECORDATORIO DE AUDIENCIA

📅 Fecha: {audiencia.get('fecha', 'N/A')}
🕐 Hora: {audiencia.get('hora', 'N/A')}
⚖️ Caso: {caso_info}
📋 Descripción: {audiencia.get('descripcion', 'N/A')}"""

        if audiencia.get('link') and audiencia['link'].strip():
            texto += f"\n🔗 Link: {audiencia['link'].strip()}"
        
        texto += "\n\nPowered by Legal-IT-Ø"
        return texto

    def _compartir_audiencia_por_email(self):
        if not self.selected_audiencia_id: return
        try:
            audiencia = self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
            if audiencia:
                texto = self._formatear_texto_audiencia_para_compartir(audiencia)
                subject = f"Recordatorio Audiencia: {audiencia.get('descripcion', 'N/A')} - {audiencia.get('fecha', '')}"
                body = urllib.parse.quote(texto)
                email_url = f"mailto:?subject={urllib.parse.quote(subject)}&body={body}"
                webbrowser.open(email_url)
        except Exception as e:
            messagebox.showerror("Error", f"Error al compartir por email: {e}")

    def _compartir_audiencia_por_whatsapp(self):
        if not self.selected_audiencia_id: return
        try:
            audiencia = self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
            if audiencia:
                texto = self._formatear_texto_audiencia_para_compartir(audiencia)
                whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(texto)}"
                webbrowser.open(whatsapp_url)
        except Exception as e:
            messagebox.showerror("Error", f"Error al compartir por WhatsApp: {e}")

    def refresh_data(self):
        current_selected_audiencia_id = self.selected_audiencia_id
        fecha_actual_calendario = self.fecha_seleccionada_agenda

        # Actualizar lista y marcas del calendario
        self.actualizar_lista_audiencias() # Esto ya usa self.fecha_seleccionada_agenda
        self.marcar_dias_audiencias_calendario()
        
        if current_selected_audiencia_id:
            # Intentar re-seleccionar la audiencia si aún existe en la fecha actual
            found = False
            for item in self.audiencias_tree.get_children():
                if int(self.audiencias_tree.item(item, 'values')[0]) == current_selected_audiencia_id:
                    # Verificar que la fecha de la audiencia re-seleccionada coincida con la del calendario
                    audiencia_data = self.db_crm.get_audiencia_by_id(current_selected_audiencia_id)
                    if audiencia_data and audiencia_data['fecha'] == fecha_actual_calendario:
                        self.audiencias_tree.selection_set(item)
                        self.audiencias_tree.focus(item)
                        # on_audiencia_tree_select se disparará y actualizará detalles/botones
                        found = True
                        break
            if not found: # Si la audiencia ya no está o no es de esta fecha
                self.selected_audiencia_id = None
                self.limpiar_detalles_audiencia()
                self.deshabilitar_botones_audiencia()
        else:
            self.selected_audiencia_id = None
            self.limpiar_detalles_audiencia()
            self.deshabilitar_botones_audiencia()


    def get_selected_audiencia(self):
        if self.selected_audiencia_id:
            try:
                return self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
            except:
                return None
        return None