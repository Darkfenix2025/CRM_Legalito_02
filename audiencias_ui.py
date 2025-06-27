import tkinter as tk
from tkinter import ttk, messagebox, simpledialog # simpledialog para _seleccionar_caso_para_audiencia
import datetime
import re
# import threading # No usado en este archivo
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

    def _create_widgets(self):
        # Configurar el frame principal de AudienciasTab
        self.columnconfigure(0, weight=1) # Panel Izquierdo: Calendario
        self.columnconfigure(1, weight=2) # Panel Derecho: Lista y Detalles (más espacio)
        self.rowconfigure(0, weight=1)    # Fila única para ambos paneles

        # --- Panel Izquierdo: Calendario ---
        # CORRECCIÓN: calendar_frame debe estar en row=0, column=0 de AudienciasTab
        calendar_frame_container = ttk.Frame(self) # Contenedor para mejor padding si es necesario
        calendar_frame_container.grid(row=0, column=0, sticky='nsew', padx=(0,5), pady=5)
        calendar_frame_container.rowconfigure(0, weight=1)
        calendar_frame_container.columnconfigure(0, weight=1)

        calendar_frame = ttk.LabelFrame(calendar_frame_container, text="Calendario de Audiencias", padding="5")
        calendar_frame.grid(row=0, column=0, sticky='nsew')
        
        calendar_frame.columnconfigure(0, weight=1) # Para el widget Calendar
        calendar_frame.rowconfigure(0, weight=1)  # Para el widget Calendar (expansión vertical)
        calendar_frame.rowconfigure(1, weight=0)  # Para add_aud_frame (sin expansión vertical)

        # Calendario
        self.calendar = Calendar(calendar_frame, selectmode='day', date_pattern='yyyy-mm-dd', 
                                 tooltipforeground='black', tooltipbackground='#FFFFE0', locale='es_ES')
        self.calendar.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.calendar.bind("<<CalendarSelected>>", self.actualizar_lista_audiencias)
        self.calendar.tag_config('audiencia_marcador', background='lightblue', foreground='black')

        # --- Frame para el botón de agregar audiencia ---
        # CORRECCIÓN: add_aud_frame es hijo de calendar_frame, y el botón es hijo de add_aud_frame
        add_aud_frame = ttk.Frame(calendar_frame)
        add_aud_frame.grid(row=1, column=0, sticky='ew', pady=(5, 0), padx=5) # Debajo del calendario

        self.add_audiencia_btn = ttk.Button(add_aud_frame, text="Agregar Audiencia", 
                                        command=lambda: self.abrir_dialogo_audiencia(), state=tk.NORMAL)
        # CORRECCIÓN: .pack() es correcto aquí porque add_aud_frame es su padre dedicado
        self.add_audiencia_btn.pack(fill=tk.X, padx=0, pady=0) # padx/pady dentro de add_aud_frame

        # CORRECCIÓN: Llamada a método no existente comentada. Implementar si es necesario.
        self.update_add_audiencia_button_state() # Call it at init

        # --- Panel Derecho: Lista y Detalles ---
        right_panel = ttk.Frame(self)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=5)
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)  # Lista de audiencias (más peso)
        right_panel.rowconfigure(1, weight=0)  # Botones
        right_panel.rowconfigure(2, weight=0)  # Detalles (altura fija o mínima)

        # --- Lista de Audiencias ---
        audiencias_list_frame = ttk.LabelFrame(right_panel, text="Audiencias del Día", padding="5")
        audiencias_list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        audiencias_list_frame.columnconfigure(0, weight=1)
        audiencias_list_frame.rowconfigure(0, weight=1)

        audiencias_cols = ('ID', 'Hora', 'Caso', 'Descripción')
        self.audiencias_tree = ttk.Treeview(audiencias_list_frame, columns=audiencias_cols, show='headings', selectmode='browse')
        
        self.audiencias_tree.heading('ID', text='ID')
        self.audiencias_tree.heading('Hora', text='Hora')
        self.audiencias_tree.heading('Caso', text='Caso')
        self.audiencias_tree.heading('Descripción', text='Descripción')

        self.audiencias_tree.column('ID', width=30, stretch=tk.NO, anchor=tk.W)
        self.audiencias_tree.column('Hora', width=60, stretch=tk.NO, anchor=tk.CENTER)
        self.audiencias_tree.column('Caso', width=150, stretch=tk.YES)
        self.audiencias_tree.column('Descripción', width=200, stretch=tk.YES)

        audiencias_scrollbar_y = ttk.Scrollbar(audiencias_list_frame, orient=tk.VERTICAL, command=self.audiencias_tree.yview)
        self.audiencias_tree.configure(yscrollcommand=audiencias_scrollbar_y.set)
        audiencias_scrollbar_y.grid(row=0, column=1, sticky='ns')
        # Scrollbar X para audiencias_tree (opcional, si el contenido puede ser muy ancho)
        audiencias_scrollbar_x = ttk.Scrollbar(audiencias_list_frame, orient=tk.HORIZONTAL, command=self.audiencias_tree.xview)
        self.audiencias_tree.configure(xscrollcommand=audiencias_scrollbar_x.set)
        audiencias_scrollbar_x.grid(row=1, column=0, sticky='ew')


        self.audiencias_tree.grid(row=0, column=0, sticky='nsew')

        self.audiencias_tree.bind('<<TreeviewSelect>>', self.on_audiencia_tree_select)
        self.audiencias_tree.bind('<Double-1>', self.abrir_link_audiencia_seleccionada)

        # --- Botones de Acción ---
        audiencias_buttons_frame = ttk.Frame(right_panel)
        audiencias_buttons_frame.grid(row=1, column=0, sticky='ew', pady=5)
        # Configurar columnas para que los botones se distribuyan
        audiencias_buttons_frame.columnconfigure(0, weight=1)
        audiencias_buttons_frame.columnconfigure(1, weight=1)
        audiencias_buttons_frame.columnconfigure(2, weight=1)
        audiencias_buttons_frame.columnconfigure(3, weight=1)

        self.edit_audiencia_btn = ttk.Button(audiencias_buttons_frame, text="Editar", 
                                           command=self.editar_audiencia_seleccionada, state=tk.DISABLED)
        self.edit_audiencia_btn.grid(row=0, column=0, sticky='ew', padx=(0, 2))

        self.delete_audiencia_btn = ttk.Button(audiencias_buttons_frame, text="Eliminar", 
                                             command=self.eliminar_audiencia_seleccionada, state=tk.DISABLED)
        self.delete_audiencia_btn.grid(row=0, column=1, sticky='ew', padx=2)

        self.open_link_btn = ttk.Button(audiencias_buttons_frame, text="Abrir Link", 
                                       command=self.abrir_link_audiencia_seleccionada, state=tk.DISABLED)
        self.open_link_btn.grid(row=0, column=2, sticky='ew', padx=2)

        self.share_btn = ttk.Button(audiencias_buttons_frame, text="Compartir", 
                                   command=self.mostrar_menu_compartir_audiencia, state=tk.DISABLED)
        self.share_btn.grid(row=0, column=3, sticky='ew', padx=(2, 0))

        # --- Detalles de Audiencia ---
        detalles_frame = ttk.LabelFrame(right_panel, text="Detalles de la Audiencia", padding="5")
        detalles_frame.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        detalles_frame.columnconfigure(1, weight=1) # Para que los labels de datos se expandan

        row_det = 0
        ttk.Label(detalles_frame, text="Fecha:").grid(row=row_det, column=0, sticky=tk.W, pady=2, padx=5)
        self.audiencia_fecha_lbl = ttk.Label(detalles_frame, text="")
        self.audiencia_fecha_lbl.grid(row=row_det, column=1, sticky=tk.EW, pady=2, padx=5)
        row_det += 1

        ttk.Label(detalles_frame, text="Hora:").grid(row=row_det, column=0, sticky=tk.W, pady=2, padx=5)
        self.audiencia_hora_lbl = ttk.Label(detalles_frame, text="")
        self.audiencia_hora_lbl.grid(row=row_det, column=1, sticky=tk.EW, pady=2, padx=5)
        row_det += 1

        ttk.Label(detalles_frame, text="Caso:").grid(row=row_det, column=0, sticky=tk.W, pady=2, padx=5)
        self.audiencia_caso_lbl = ttk.Label(detalles_frame, text="", wraplength=300) # wraplength ajustado
        self.audiencia_caso_lbl.grid(row=row_det, column=1, sticky=tk.EW, pady=2, padx=5)
        row_det += 1

        ttk.Label(detalles_frame, text="Descripción:").grid(row=row_det, column=0, sticky=tk.NW, pady=2, padx=5)
        self.audiencia_desc_lbl = ttk.Label(detalles_frame, text="", wraplength=300) # wraplength ajustado
        self.audiencia_desc_lbl.grid(row=row_det, column=1, sticky=tk.EW, pady=2, padx=5)
        row_det += 1

        ttk.Label(detalles_frame, text="Link:").grid(row=row_det, column=0, sticky=tk.W, pady=2, padx=5)
        self.audiencia_link_lbl = ttk.Label(detalles_frame, text="", foreground="blue", cursor="hand2", wraplength=300)
        self.audiencia_link_lbl.grid(row=row_det, column=1, sticky=tk.EW, pady=2, padx=5)
        self.audiencia_link_lbl.bind("<Button-1>", lambda e: self.abrir_link_audiencia_seleccionada()) # Asegurar que llama al método
        row_det += 1
        
        self.cargar_audiencias_fecha_actual()
        self.marcar_dias_audiencias_calendario() # Llamar después de cargar

    def update_add_audiencia_button_state(self):
        """Actualiza el estado del botón 'Agregar Audiencia'."""
        if hasattr(self.app_controller, 'selected_case') and self.app_controller.selected_case:
            self.add_audiencia_btn.config(state=tk.NORMAL)
        else:
            self.add_audiencia_btn.config(state=tk.DISABLED)


    def cargar_audiencias_fecha_actual(self):
        self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
        # Asegurarse que el calendario visualmente muestra la fecha actual al inicio
        try:
            current_date = datetime.datetime.strptime(self.fecha_seleccionada_agenda, "%Y-%m-%d").date()
            self.calendar.selection_set(current_date)
        except Exception as e:
            print(f"Error setting calendar initial date: {e}")
        self.actualizar_lista_audiencias()
        # self.marcar_dias_audiencias_calendario() # Se llama al final de _create_widgets

    def actualizar_lista_audiencias(self, event=None):
        if hasattr(self.calendar, 'selection_get') and self.calendar.selection_get():
            try:
                fecha_sel = self.calendar.selection_get()
                self.fecha_seleccionada_agenda = fecha_sel.strftime("%Y-%m-%d")
            except Exception as e: # Podría ser None si no hay selección
                print(f"Error obteniendo fecha del calendario: {e}")
                self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")
        else: # Si no hay event o selection_get no funciona como se espera
             self.fecha_seleccionada_agenda = datetime.date.today().strftime("%Y-%m-%d")


        for item in self.audiencias_tree.get_children():
            self.audiencias_tree.delete(item)
        
        self.limpiar_detalles_audiencia() # Limpiar detalles al cambiar de día
        self.deshabilitar_botones_audiencia() # Deshabilitar botones

        try:
            audiencias = self.db_crm.get_audiencias_by_date(self.fecha_seleccionada_agenda)
            for audiencia in audiencias:
                caso_info = "Sin caso asociado"
                if audiencia.get('caso_id'):
                    try:
                        caso = self.db_crm.get_case_by_id(audiencia['caso_id'])
                        if caso:
                            caso_info = f"{caso.get('caratula', 'Sin carátula')}"
                        else:
                            caso_info = f"Caso ID: {audiencia['caso_id']} (No encontrado)"
                    except Exception as e_caso:
                        print(f"Error obteniendo info del caso {audiencia['caso_id']}: {e_caso}")
                        caso_info = f"Caso ID: {audiencia['caso_id']} (Error)"

                self.audiencias_tree.insert('', 'end', values=(
                    audiencia['id'],
                    audiencia.get('hora', ''),
                    caso_info,
                    audiencia.get('descripcion', '')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar audiencias: {e}")

    def marcar_dias_audiencias_calendario(self):
        try:
            # Limpiar marcas anteriores para evitar duplicados si se llama múltiples veces
            # Es importante que el tag 'audiencia' (o el que uses en calevent_create)
            # sea el mismo que se usa en tag_config.
            #calevent_remove(tag=None) removes all events.
            self.calendar.calevent_remove(tag='audiencia') # Solo remueve los eventos con este tag específico.

            fechas_con_audiencias = self.db_crm.get_dates_with_audiencias()
            
            for fecha_str in fechas_con_audiencias:
                try:
                    fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
                    # Usar un tag consistente, por ejemplo "audiencia_marcador"
                    self.calendar.calevent_create(fecha, "Audiencia", tags='audiencia')
                except ValueError: # Si la fecha_str no es válida
                    print(f"Formato de fecha inválido en base de datos: {fecha_str}")
                    continue
            
            # La configuración del tag debe hacerse una vez, idealmente en _create_widgets,
            # pero aquí está bien si se asegura que no cause problemas.
            # self.calendar.tag_config('audiencia', background="lightblue", foreground="darkblue")
            # El tag_config ya está en _create_widgets, así que no es necesario repetirlo.
            
        except Exception as e:
            print(f"Error al marcar días con audiencias: {e}")

    def on_audiencia_tree_select(self, event=None):
        selected_items = self.audiencias_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            audiencia_id_str = self.audiencias_tree.item(selected_item, 'values')[0]
            
            try:
                audiencia_id = int(audiencia_id_str)
                self.selected_audiencia_id = audiencia_id # Guardar como int
                self.mostrar_detalles_audiencia(audiencia_id)
                self.habilitar_botones_audiencia()
            except ValueError:
                 messagebox.showerror("Error", f"ID de audiencia inválido: {audiencia_id_str}")
                 self.selected_audiencia_id = None
                 self.limpiar_detalles_audiencia()
                 self.deshabilitar_botones_audiencia()
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener detalles de la audiencia: {e}")
                self.selected_audiencia_id = None
                self.limpiar_detalles_audiencia()
                self.deshabilitar_botones_audiencia()
        else:
            self.selected_audiencia_id = None
            self.limpiar_detalles_audiencia()
            self.deshabilitar_botones_audiencia()

    def mostrar_detalles_audiencia(self, audiencia_id):
        try:
            audiencia = self.db_crm.get_audiencia_by_id(audiencia_id)
            if audiencia:
                self.audiencia_fecha_lbl.config(text=audiencia.get('fecha', 'N/A'))
                self.audiencia_hora_lbl.config(text=audiencia.get('hora', 'N/A'))
                self.audiencia_desc_lbl.config(text=audiencia.get('descripcion', 'N/A'))
                
                caso_info = "Sin caso asociado"
                if audiencia.get('caso_id'):
                    try:
                        caso = self.db_crm.get_case_by_id(audiencia['caso_id'])
                        if caso:
                            caso_info = f"{caso.get('caratula', 'Sin carátula')}"
                        else:
                             caso_info = f"Caso ID: {audiencia['caso_id']} (No encontrado)"
                    except:
                        caso_info = f"Caso ID: {audiencia['caso_id']} (Error al cargar)"
                self.audiencia_caso_lbl.config(text=caso_info)
                
                link = audiencia.get('link', '')
                self.audiencia_link_lbl.config(text=link if link else "Sin link")
            else:
                self.limpiar_detalles_audiencia()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
            self.limpiar_detalles_audiencia()


    def limpiar_detalles_audiencia(self):
        self.audiencia_fecha_lbl.config(text="")
        self.audiencia_hora_lbl.config(text="")
        self.audiencia_caso_lbl.config(text="")
        self.audiencia_desc_lbl.config(text="")
        self.audiencia_link_lbl.config(text="")

    def habilitar_botones_audiencia(self):
        self.edit_audiencia_btn.config(state=tk.NORMAL)
        # Habilitar delete_audiencia_btn si se considera seguro.
        # Por ahora, lo dejo como estaba en tu código original (deshabilitado hasta que se corrija en el código).
        # Si quieres habilitarlo:
        self.delete_audiencia_btn.config(state=tk.NORMAL) 
        self.share_btn.config(state=tk.NORMAL) 
        
        try:
            if self.selected_audiencia_id:
                audiencia = self.db_crm.get_audiencia_by_id(self.selected_audiencia_id)
                if audiencia and audiencia.get('link'):
                    self.open_link_btn.config(state=tk.NORMAL)
                else:
                    self.open_link_btn.config(state=tk.DISABLED)
            else: # No debería llegar aquí si se llama después de una selección válida
                self.open_link_btn.config(state=tk.DISABLED)
        except Exception: # Captura general por si get_audiencia_by_id falla
            self.open_link_btn.config(state=tk.DISABLED)


    def deshabilitar_botones_audiencia(self):
        self.edit_audiencia_btn.config(state=tk.DISABLED)
        self.delete_audiencia_btn.config(state=tk.DISABLED)
        self.open_link_btn.config(state=tk.DISABLED)
        self.share_btn.config(state=tk.DISABLED)

    def abrir_dialogo_audiencia(self, audiencia_id=None, parent_window=None):
        parent = parent_window if parent_window else self.app_controller.root
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
            audiencia_data = self.db_crm.get_audiencia_by_id(audiencia_id)
            if audiencia_data:
                caso_id_var.set(str(audiencia_data.get('caso_id', '')))
                if audiencia_data.get('caso_id'):
                    caso = self.db_crm.get_case_by_id(audiencia_data['caso_id'])
                    if caso:
                        caso_nombre_var.set(caso.get('caratula', f"ID: {audiencia_data['caso_id']} (No encontrado)"))
                    else:
                        caso_nombre_var.set(f"ID: {audiencia_data['caso_id']} (No encontrado)")
                else:
                    caso_nombre_var.set("Ninguno asignado")
                    
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
        else: # Nueva audiencia
            fecha_var.set(self.fecha_seleccionada_agenda if self.fecha_seleccionada_agenda else datetime.date.today().strftime("%Y-%m-%d"))
            if self.app_controller.selected_case:
                caso_id_var.set(str(self.app_controller.selected_case['id']))
                caso_nombre_var.set(self.app_controller.selected_case.get('caratula', 'Caso seleccionado'))
            else:
                caso_nombre_var.set("Ninguno (Haga clic en Buscar)")

        row = 0
        # Mostrar nombre del caso (si está preseleccionado)
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
            # Esta es una implementación muy simple. Podrías crear un diálogo más complejo
            # que muestre una lista de casos para seleccionar.

            # --- MODIFIED TO USE SelectCaseDialog ---
            dialog = SelectCaseDialog(parent_dialog, self.app_controller) # parent_dialog is the Audiencia Dialog
            selected_info = dialog.selected_case_info # This will block until dialog is closed

            if selected_info:
                caso_id_var.set(str(selected_info['id']))
                caso_nombre_var.set(selected_info['caratula'])
                # No need for messagebox here, selection happens in the dialog
            # If selected_info is None, it means cancel was pressed, so no change.
            # --- END MODIFICATION ---

        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar caso: {e}", parent=parent_dialog)


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

class SelectCaseDialog(tk.Toplevel):
    """
    A dialog window for selecting a case from a filterable list.
    Used when associating an audiencia with a case if one isn't already selected,
    or if the user wishes to change the associated case.

    Attributes:
        selected_case_info (dict | None): After the dialog closes, this attribute
                                          holds {'id': case_id, 'caratula': caratula}
                                          if a case was selected, or None if canceled.
    """
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.selected_case_info = None # Will store {'id': case_id, 'caratula': caratula}

        self.title("Seleccionar Caso")
        self.transient(parent)
        self.grab_set()
        self.geometry("600x400")
        self.resizable(True, True)

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1) # Treeview row

        # Search/Filter (Optional - Basic for now)
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        ttk.Label(search_frame, text="Buscar Carátula:").pack(side=tk.LEFT, padx=(0,5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_entry.bind("<KeyRelease>", self._filter_cases)

        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        cols = ('ID', 'Carátula', 'Cliente')
        self.case_tree = ttk.Treeview(tree_frame, columns=cols, show='headings', selectmode='browse')
        self.case_tree.heading('ID', text='ID')
        self.case_tree.heading('Carátula', text='Carátula')
        self.case_tree.heading('Cliente', text='Cliente')

        self.case_tree.column('ID', width=50, stretch=tk.NO, anchor=tk.CENTER)
        self.case_tree.column('Carátula', width=300, stretch=True)
        self.case_tree.column('Cliente', width=200, stretch=True)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.case_tree.yview)
        self.case_tree.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.case_tree.xview)
        self.case_tree.configure(xscrollcommand=scrollbar_x.set)

        self.case_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.case_tree.bind("<Double-1>", self._on_select_button)


        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, sticky="e", pady=(10,0))

        ttk.Button(buttons_frame, text="Seleccionar", command=self._on_select_button).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancelar", command=self._on_cancel_button).pack(side=tk.LEFT)

        self._load_all_cases()
        self.search_entry.focus_set()

        # Make dialog modal
        self.protocol("WM_DELETE_WINDOW", self._on_cancel_button)
        self.wait_window(self) # Crucial for modal behavior

    def _load_all_cases(self, filter_text=""):
        for item in self.case_tree.get_children():
            self.case_tree.delete(item)

        try:
            all_cases = self.db_crm.get_all_cases() # This already joins with client name
            for case in all_cases:
                caratula = case.get('caratula', '').lower()
                cliente_nombre = case.get('nombre_cliente', '').lower()
                if filter_text.lower() in caratula or filter_text.lower() in cliente_nombre:
                    self.case_tree.insert('', 'end', iid=case['id'], values=(
                        case['id'],
                        case.get('caratula', 'N/A'),
                        case.get('nombre_cliente', 'N/A')
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar casos: {e}", parent=self)

    def _filter_cases(self, event=None):
        filter_text = self.search_var.get()
        self._load_all_cases(filter_text)

    def _on_select_button(self, event=None):
        selected_items = self.case_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un caso de la lista.", parent=self)
            return

        selected_iid = selected_items[0]
        case_id = self.case_tree.item(selected_iid, 'values')[0]
        caratula = self.case_tree.item(selected_iid, 'values')[1]

        self.selected_case_info = {'id': case_id, 'caratula': caratula}
        self.destroy()

    def _on_cancel_button(self):
        self.selected_case_info = None
        self.destroy()