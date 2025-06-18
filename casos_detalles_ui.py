# casos_detalles_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os # Para os.path.exists y os.startfile
import subprocess # Para abrir carpetas en Linux/macOS
import sys # Para sys.platform

class CasosDetallesTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.current_case_data = None # Para almacenar los datos del caso actual
        self._create_widgets()
        self.display_no_case() # Estado inicial

    def _create_widgets(self):
        # Configurar el frame principal para que el canvas se expanda
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Crear canvas y scrollbar para scroll vertical
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas) # Frame que contendrá todos los widgets

        # Vincular el tamaño del scrollable_frame al scrollregion del canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Configurar el frame scrollable para que su única columna se expanda
        self.scrollable_frame.columnconfigure(0, weight=1)

        # Usaremos un contador de filas para facilitar la adición de nuevos frames
        current_row_sf = 0 # current_row_scrollable_frame

        # --- Frame de Estado ---
        self.status_frame = ttk.LabelFrame(self.scrollable_frame, text="Estado del Caso", padding="10")
        self.status_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.status_frame.columnconfigure(0, weight=1) # Para que el label interno se expanda
        current_row_sf += 1

        self.status_label = ttk.Label(self.status_frame, text="Ningún caso seleccionado", 
                                     font=('', 12), foreground='gray')
        self.status_label.pack(fill=tk.X, expand=True) # Usar pack para centrar y expandir

        # --- Información Básica ---
        self.info_frame = ttk.LabelFrame(self.scrollable_frame, text="Información Básica", padding="10")
        self.info_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.info_frame.columnconfigure(1, weight=1) # Columna de valores expandible
        current_row_sf += 1

        # Labels para Información Básica (etiqueta en col 0, valor en col 1)
        fields_info_basica = [
            ("ID:", "id_label"), ("Carátula:", "caratula_label"), ("Cliente:", "cliente_label"),
            ("Nº Expediente:", "num_exp_label"), ("Año Carát.:", "anio_label")
        ]
        for i, (text, attr_name) in enumerate(fields_info_basica):
            ttk.Label(self.info_frame, text=text, font=('', 9, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2, padx=2)
            label_widget = ttk.Label(self.info_frame, text="", wraplength=450) # wraplength para carátula y cliente
            label_widget.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=2)
            setattr(self, attr_name, label_widget)

        # --- Información Jurisdiccional ---
        self.juris_frame = ttk.LabelFrame(self.scrollable_frame, text="Información Jurisdiccional", padding="10")
        self.juris_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.juris_frame.columnconfigure(1, weight=1)
        current_row_sf += 1

        fields_jurisdiccional = [
            ("Juzgado:", "juzgado_label"), ("Jurisdicción:", "jurisdiccion_label"), ("Etapa Procesal:", "etapa_label")
        ]
        for i, (text, attr_name) in enumerate(fields_jurisdiccional):
            ttk.Label(self.juris_frame, text=text, font=('', 9, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2, padx=2)
            label_widget = ttk.Label(self.juris_frame, text="", wraplength=450)
            label_widget.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=2)
            setattr(self, attr_name, label_widget)

        # --- Gestión de Archivos ---
        self.files_frame = ttk.LabelFrame(self.scrollable_frame, text="Gestión de Archivos", padding="10")
        self.files_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.files_frame.columnconfigure(1, weight=1)
        current_row_sf += 1

        ttk.Label(self.files_frame, text="Carpeta:", font=('', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2, padx=2)
        self.ruta_label = ttk.Label(self.files_frame, text="", wraplength=450, foreground="blue", cursor="hand2")
        self.ruta_label.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=2)
        self.ruta_label.bind("<Button-1>", self._open_case_folder_event) # Renombrado para claridad

        # --- Alertas y Notificaciones ---
        self.alerts_frame = ttk.LabelFrame(self.scrollable_frame, text="Alertas", padding="10")
        self.alerts_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.alerts_frame.columnconfigure(1, weight=1)
        current_row_sf += 1
        
        ttk.Label(self.alerts_frame, text="Alerta Inactividad:", font=('', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2, padx=2)
        self.inactividad_label = ttk.Label(self.alerts_frame, text="")
        self.inactividad_label.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=2)

        # --- Etiquetas ---
        self.etiquetas_frame_display = ttk.LabelFrame(self.scrollable_frame, text="Etiquetas del Caso", padding="10") # Nombre cambiado
        self.etiquetas_frame_display.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.etiquetas_frame_display.columnconfigure(0, weight=1) # Para que el Text se expanda
        current_row_sf += 1

        self.etiquetas_display_text = tk.Text(self.etiquetas_frame_display, height=2, wrap=tk.WORD, state=tk.DISABLED, relief=tk.FLAT, background=self.app_controller.root.cget('bg')) # Usar color de fondo del root
        self.etiquetas_display_text.grid(row=0, column=0, sticky='ew', pady=2, padx=2)
        # Podríamos añadir un scrollbar si las etiquetas son muchas y no caben en height=2, pero con wraplength en el Label del diálogo de edición debería ser suficiente.

        # --- Notas ---
        self.notas_display_frame = ttk.LabelFrame(self.scrollable_frame, text="Notas del Caso", padding="10") # Nombre cambiado
        self.notas_display_frame.grid(row=current_row_sf, column=0, sticky='nsew', pady=(0, 10), padx=5)
        self.notas_display_frame.columnconfigure(0, weight=1)
        self.notas_display_frame.rowconfigure(0, weight=1) # Permitir que el Text de notas se expanda verticalmente
        self.scrollable_frame.rowconfigure(current_row_sf, weight=1) # Permitir que esta fila del scrollable_frame se expanda
        current_row_sf += 1

        self.notas_display_text = tk.Text(self.notas_display_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.notas_display_text.grid(row=0, column=0, sticky='nsew', pady=2, padx=2)

        notas_scrollbar = ttk.Scrollbar(self.notas_display_frame, orient="vertical", command=self.notas_display_text.yview)
        self.notas_display_text.configure(yscrollcommand=notas_scrollbar.set)
        notas_scrollbar.grid(row=0, column=1, sticky='ns', pady=2, padx=(0,2))
        
        # --- Estadísticas del Caso ---
        self.stats_frame = ttk.LabelFrame(self.scrollable_frame, text="Resumen del Caso", padding="10") # Título cambiado
        self.stats_frame.grid(row=current_row_sf, column=0, sticky='ew', pady=(0, 10), padx=5)
        self.stats_frame.columnconfigure(1, weight=1)
        current_row_sf += 1

        stats_fields = [
            ("Creado:", "fecha_creacion_label"), ("Tareas:", "num_tareas_label"),
            ("Partes:", "num_partes_label"), ("Audiencias:", "num_audiencias_label"),
            ("Actividades:", "num_actividades_label")
        ]
        for i, (text, attr_name) in enumerate(stats_fields):
            ttk.Label(self.stats_frame, text=text, font=('', 9, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2, padx=2)
            label_widget = ttk.Label(self.stats_frame, text="N/A") # Valor inicial
            label_widget.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=2)
            setattr(self, attr_name, label_widget)
            
    def on_case_changed(self, case_data):
        """Llamado por main_app cuando el caso seleccionado cambia."""
        self.current_case_data = case_data # Guardar los datos del caso actual
        if case_data:
            print(f"[CasosDetallesTab] Recibido caso ID: {case_data.get('id')}") # DEBUG
            self.display_case_details(case_data)
        else:
            print("[CasosDetallesTab] Recibido None para caso. Limpiando detalles.") # DEBUG
            self.display_no_case()

    def display_case_details(self, case_data):
        """Mostrar los detalles del caso en los widgets."""
        if not case_data: # Seguridad adicional
            self.display_no_case()
            return

        try:
            self.status_label.config(text=f"Detalles del Caso: {case_data.get('caratula', 'Sin carátula')}", 
                                    foreground='darkgreen', font=('', 11, 'bold'))

            # Información básica
            self.id_label.config(text=str(case_data.get('id', 'N/A')))
            self.caratula_label.config(text=case_data.get('caratula', 'N/A'))
            
            cliente_info = "N/A"
            if case_data.get('cliente_id'):
                try:
                    cliente = self.db_crm.get_client_by_id(case_data['cliente_id'])
                    if cliente:
                        cliente_info = f"{cliente.get('nombre', 'Sin nombre')} (ID: {cliente['id']})"
                except Exception as e_cli:
                    print(f"Error al cargar info del cliente para detalles del caso: {e_cli}")
                    cliente_info = f"ID Cliente: {case_data['cliente_id']} (Error)"
            self.cliente_label.config(text=cliente_info)

            self.num_exp_label.config(text=case_data.get('numero_expediente', 'N/A'))
            self.anio_label.config(text=case_data.get('anio_caratula', 'N/A'))

            # Información jurisdiccional
            self.juzgado_label.config(text=case_data.get('juzgado', 'N/A'))
            self.jurisdiccion_label.config(text=case_data.get('jurisdiccion', 'N/A'))
            self.etapa_label.config(text=case_data.get('etapa_procesal', 'N/A'))

            # Gestión de archivos (usando 'ruta_carpeta')
            ruta = case_data.get('ruta_carpeta', '') 
            if ruta and os.path.exists(ruta):
                self.ruta_label.config(text=ruta, foreground="blue")
            elif ruta: # Si hay ruta pero no existe
                self.ruta_label.config(text=f"Ruta no encontrada: {ruta}", foreground="red")
            else: # No hay ruta
                self.ruta_label.config(text="Sin carpeta asignada", foreground="gray")

            # Alertas y notificaciones (usando nombres correctos de la BD)
            inactividad_activa = bool(case_data.get('inactivity_enabled', 0))
            dias_inactividad = case_data.get('inactivity_threshold_days', 30)
            if inactividad_activa:
                self.inactividad_label.config(text=f"Activa - Umbral: {dias_inactividad} días", foreground="orange")
            else:
                self.inactividad_label.config(text="Desactivada", foreground="gray")

            # Etiquetas (obteniendo de la tabla de unión)
            nombres_etiquetas_caso = []
            case_id_for_tags = case_data.get('id')
            if case_id_for_tags:
                etiquetas_obj_list = self.db_crm.get_etiquetas_de_caso(case_id_for_tags)
                nombres_etiquetas_caso = [e['nombre_etiqueta'] for e in etiquetas_obj_list]
            
            self.etiquetas_display_text.config(state=tk.NORMAL)
            self.etiquetas_display_text.delete(1.0, tk.END)
            if nombres_etiquetas_caso:
                self.etiquetas_display_text.insert(1.0, ", ".join(nombres_etiquetas_caso).capitalize())
            else:
                self.etiquetas_display_text.insert(1.0, "Sin etiquetas asignadas")
            self.etiquetas_display_text.config(state=tk.DISABLED)

            # Notas
            notas_caso = case_data.get('notas', '')
            self.notas_display_text.config(state=tk.NORMAL)
            self.notas_display_text.delete(1.0, tk.END)
            if notas_caso:
                self.notas_display_text.insert(1.0, notas_caso)
            else:
                self.notas_display_text.insert(1.0, "Sin notas registradas.")
            self.notas_display_text.config(state=tk.DISABLED)

            # Estadísticas
            timestamp_creacion = case_data.get('created_at')
            fecha_creacion_display = "N/A"
            if timestamp_creacion:
                try:
                    fecha_creacion_display = datetime.datetime.fromtimestamp(timestamp_creacion).strftime("%d-%m-%Y %H:%M")
                except Exception: pass # Dejar N/A si hay error
            self.fecha_creacion_label.config(text=fecha_creacion_display)
            
            # Cargar estadísticas relacionadas
            if case_data.get('id'):
                self._load_case_statistics(case_data['id'])
            else: # Limpiar estadísticas si no hay ID de caso (no debería pasar si case_data existe)
                self._clear_statistics_labels()


        except Exception as e:
            messagebox.showerror("Error en Detalles del Caso", f"Ocurrió un error al mostrar los detalles:\n{e}", parent=self.app_controller.root)
            print(f"Error detallado en display_case_details: {e}")
            import traceback
            traceback.print_exc()
            self.display_no_case() # Volver a un estado limpio si hay error

    def _load_case_statistics(self, case_id):
        """Cargar y mostrar estadísticas del caso (conteos de entidades relacionadas)."""
        if not case_id:
            self._clear_statistics_labels()
            return

        try:
            # Tareas
            tareas = self.db_crm.get_tareas_by_caso_id(case_id, incluir_completadas=True)
            self.num_tareas_label.config(text=str(len(tareas)) if tareas is not None else "Error")
        except Exception as e_t:
            print(f"Error cargando stats tareas: {e_t}")
            self.num_tareas_label.config(text="Error")

        try:
            # Partes
            partes = self.db_crm.get_partes_by_caso_id(case_id)
            self.num_partes_label.config(text=str(len(partes)) if partes is not None else "Error")
        except Exception as e_p:
            print(f"Error cargando stats partes: {e_p}")
            self.num_partes_label.config(text="Error")
        
        try:
            # Audiencias (asumiendo que tienes una función get_audiencias_by_caso_id)
            if hasattr(self.db_crm, 'get_audiencias_by_caso_id'): # Verificar si existe la función
                audiencias = self.db_crm.get_audiencias_by_caso_id(case_id)
                self.num_audiencias_label.config(text=str(len(audiencias)) if audiencias is not None else "Error")
            else: # Si no existe la función, poner N/A
                 print("Advertencia: db_crm.get_audiencias_by_caso_id no existe.")
                 self.num_audiencias_label.config(text="N/A (func. faltante)")
        except Exception as e_a:
            print(f"Error cargando stats audiencias: {e_a}")
            self.num_audiencias_label.config(text="Error")

        try:
            # Actividades
            actividades = self.db_crm.get_actividades_by_caso_id(case_id) # Asumiendo que quieres todas, no solo DESC
            self.num_actividades_label.config(text=str(len(actividades)) if actividades is not None else "Error")
        except Exception as e_ac:
            print(f"Error cargando stats actividades: {e_ac}")
            self.num_actividades_label.config(text="Error")

    def _clear_statistics_labels(self):
        """Limpia los labels de estadísticas."""
        self.num_tareas_label.config(text="N/A")
        self.num_partes_label.config(text="N/A")
        self.num_audiencias_label.config(text="N/A")
        self.num_actividades_label.config(text="N/A")


    def display_no_case(self):
        """Limpia todos los campos cuando no hay un caso seleccionado."""
        self.status_label.config(text="Ningún caso seleccionado", foreground='gray', font=('', 11))
        self.current_case_data = None # Asegurar que no hay datos de caso

        labels_to_clear_text = [
            self.id_label, self.caratula_label, self.cliente_label, self.num_exp_label,
            self.anio_label, self.juzgado_label, self.jurisdiccion_label, self.etapa_label,
            self.ruta_label, self.inactividad_label, self.fecha_creacion_label
        ]
        for label in labels_to_clear_text:
            label.config(text="N/A") # Usar N/A en lugar de "" para más claridad
        
        self.ruta_label.config(foreground="gray") # Color por defecto para ruta vacía

        for text_widget in [self.etiquetas_display_text, self.notas_display_text]:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, "N/A") # Insertar N/A
            text_widget.config(state=tk.DISABLED)
        
        self._clear_statistics_labels()


    def _open_case_folder_event(self, event): # Renombrado para ser un manejador de evento
        """Abre la carpeta del caso en el explorador de archivos."""
        if not self.current_case_data:
            messagebox.showinfo("Sin Caso", "No hay un caso seleccionado para abrir su carpeta.", parent=self.app_controller.root)
            return

        ruta_carpeta = self.current_case_data.get('ruta_carpeta', '') # Usar el nombre correcto
        if not ruta_carpeta:
            messagebox.showinfo("Sin Carpeta", "Este caso no tiene una carpeta asignada.", parent=self.app_controller.root)
            return

        if not os.path.exists(ruta_carpeta):
            messagebox.showerror("Carpeta no Encontrada", f"La carpeta asignada no existe en la ruta:\n{ruta_carpeta}", parent=self.app_controller.root)
            return

        try:
            if sys.platform == "win32":
                os.startfile(os.path.realpath(ruta_carpeta)) # os.path.realpath para resolver links simbólicos si los hubiera
            elif sys.platform == "darwin": # macOS
                subprocess.call(["open", ruta_carpeta])
            else: # Linux y otros
                subprocess.call(["xdg-open", ruta_carpeta])
        except Exception as e:
            messagebox.showerror("Error al Abrir Carpeta", f"No se pudo abrir la carpeta:\n{e}", parent=self.app_controller.root)

    def refresh_data(self):
        """Refresca los datos del caso actualmente visible."""
        print("[CasosDetallesTab] Refresh_data llamado.") # DEBUG
        if self.current_case_data and self.current_case_data.get('id'):
            try:
                # Volver a obtener los datos del caso desde la BD
                updated_case_data = self.db_crm.get_case_by_id(self.current_case_data['id'])
                if updated_case_data:
                    self.current_case_data = updated_case_data # Actualizar datos internos
                    self.display_case_details(updated_case_data)
                    print(f"[CasosDetallesTab] Datos refrescados para caso ID: {updated_case_data['id']}") #DEBUG
                else:
                    # El caso ya no existe o no se pudo obtener
                    print(f"[CasosDetallesTab] No se pudo recargar caso ID: {self.current_case_data['id']}. Limpiando.") #DEBUG
                    self.display_no_case()
            except Exception as e:
                print(f"[CasosDetallesTab] Error durante refresh_data: {e}")
                self.display_no_case() # Limpiar si hay error
        else:
            # No hay caso actual, asegurarse de que la UI esté limpia
            self.display_no_case()

    def get_current_case(self):
        """Obtener el caso actual"""
        return self.current_case
