# main_window_refactored.py
import tkinter as tk
from tkinter import ttk, messagebox
import crm_database as db
import os
import datetime
import sys
import threading
import webbrowser

# Importaciones opcionales para funcionalidades avanzadas
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Advertencia: PIL no disponible. Funcionalidad de imágenes limitada.")

try:
    import plyer
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Advertencia: plyer no disponible. Notificaciones deshabilitadas.")

try:
    from pystray import MenuItem as item, Icon as icon
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    print("Advertencia: pystray no disponible. Icono de bandeja deshabilitado.")

# --- Imports de módulos modulares ---
from clientes_ui import ClientesTab
from casos_ui import CasosTab
from audiencias_ui import AudienciasTab
from ia_ui import IAMenu
from case_details_window import CaseDetailsWindow 

# --- Helper para Rutas Relativas (PyInstaller) ---
def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class CRMLegalAppRefactored:
    def __init__(self, root):
        self.root = root
        self.root.title("CRM Legal Local - Gestor Integral v2.1 (Refactorizado)     Powered by Legal-IT-Ø")
        
        # Configurar ventana principal
        try:
            self.root.state('zoomed')
        except tk.TclError:
            print("Advertencia: root.state('zoomed') falló. Intentando alternativa o usando tamaño por defecto.")
            try:
                self.root.attributes('-zoomed', True)
            except:
                self.root.geometry("1400x900")

        # --- Variables de estado CRM ---
        self.selected_client = None
        self.selected_case = None
        self.case_details_windows = {}  # Diccionario para manejar múltiples ventanas de detalles

        # --- Referencia al módulo de base de datos ---
        self.db_crm = db

        # --- Variables para notificaciones y bandeja ---
        self.recordatorios_mostrados_hoy = set()
        self.logo_image_tk = None
        self.tray_icon = None
        self.hilo_recordatorios = None
        self.hilo_bandeja = None
        self.stop_event = threading.Event()

        # --- Crear barra de menú ---
        self.create_menu()

        # --- Crear widgets principales ---
        self.create_main_layout()

        # --- Inicializar módulos ---
        self.initialize_modules()

        # --- Cargar datos iniciales ---
        self.load_initial_data()

        # --- Iniciar hilos para notificaciones y bandeja ---
        self.start_background_threads()

        # --- Manejar cierre de ventana ---
        self.root.protocol("WM_DELETE_WINDOW", self.ocultar_a_bandeja)

        # main_window_refactored.py (dentro de la clase CRMLegalAppRefactored)

    # ===========================================================================
    # === MÉTODOS DE DIÁLOGO PARA ACTIVIDADES (LLAMADOS DESDE SeguimientoTab) ===
    # ===========================================================================

    def open_actividad_dialog(self, actividad_id=None, caso_id=None, parent_window=None):
        """Abre el diálogo para agregar o editar una actividad de seguimiento."""
        if not caso_id:
            messagebox.showwarning("Error", "Se necesita un caso para gestionar sus actividades.")
            return

        parent = parent_window if parent_window else self.root
        dialog = tk.Toplevel(parent) # <-- MODIFICAR AQUÍ
        dialog.transient(parent) # <-- AÑADIR/ASEGURAR ESTO
        
        #dialog = tk.Toplevel(self.root)
        #dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.title("Nueva Actividad" if not actividad_id else "Editar Actividad")
        dialog.geometry("500x400")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        tipo_var = tk.StringVar(value="Llamada Telefónica")
        fecha_hora_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ref_doc_var = tk.StringVar()
        initial_desc = ""

        if actividad_id:
            actividad_data = self.db_crm.get_actividad_by_id(actividad_id)
            if actividad_data:
                tipo_var.set(actividad_data.get('tipo_actividad', ''))
                fecha_hora_var.set(actividad_data.get('fecha_hora', ''))
                ref_doc_var.set(actividad_data.get('referencia_documento', ''))
                initial_desc = actividad_data.get('descripcion', '')

        # Layout del formulario
        row = 0
        ttk.Label(main_frame, text="Tipo de Actividad:").grid(row=row, column=0, sticky=tk.W, pady=5)
        
        # --- INICIO DE LA MODIFICACIÓN ---
        # Lista de actividades comunes
        tipos_de_actividad = [
            "Llamada Telefónica",
            "Reunión con Cliente",
            "Escrito Presentado",
            "Cédula/Notificación Recibida",
            "Email Enviado",
            "Email Recibido",
            "Investigación",
            "Análisis de Documentación",
            "Movimiento en Expediente",
            "Otro"
        ]
        # Reemplazamos el Entry por un Combobox
        ttk.Combobox(main_frame, textvariable=tipo_var, values=tipos_de_actividad).grid(row=row, column=1, sticky="ew", pady=5)
        # --- FIN DE LA MODIFICACIÓN ---
    
        #ttk.Entry(main_frame, textvariable=tipo_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Fecha y Hora (YYYY-MM-DD HH:MM:SS):").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=fecha_hora_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Ref. Documento:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=ref_doc_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        desc_text = tk.Text(main_frame, height=6, width=40)
        desc_text.grid(row=row, column=1, sticky="nsew", pady=5)
        desc_text.insert('1.0', initial_desc)
        main_frame.rowconfigure(row, weight=1)
        row += 1

        main_frame.columnconfigure(1, weight=1)

        def save():
            try:
                descripcion = desc_text.get('1.0', tk.END).strip()
                if actividad_id:
                    self.db_crm.update_actividad_caso(actividad_id, tipo_var.get(), descripcion, ref_doc_var.get())
                else:
                    self.db_crm.add_actividad_caso(caso_id, fecha_hora_var.get(), tipo_var.get(), descripcion, referencia_documento=ref_doc_var.get())
                
                messagebox.showinfo("Éxito", "Actividad guardada correctamente.", parent=dialog)
                if caso_id in self.case_details_windows:
                    self.case_details_windows[caso_id].seguimiento_tab.load_actividades(caso_id)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la actividad:\n{e}", parent=dialog)

        ttk.Button(main_frame, text="Guardar", command=save).grid(row=row, column=1, sticky="e", pady=10)
        ttk.Button(main_frame, text="Cancelar", command=dialog.destroy).grid(row=row, column=0, sticky="w", pady=10)

    def delete_selected_actividad(self, actividad_id, caso_id):
        """Elimina una actividad y refresca la UI."""
        if not actividad_id: return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta actividad?"):
            try:
                self.db_crm.delete_actividad_caso(actividad_id)
                messagebox.showinfo("Éxito", "Actividad eliminada correctamente.")
                if caso_id in self.case_details_windows:
                    self.case_details_windows[caso_id].seguimiento_tab.load_actividades(caso_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la actividad:\n{e}")

    # ===================================================================
    # === MÉTODOS DE DIÁLOGO PARA PARTES (LLAMADOS DESDE PartesTab)   ===
    # ===================================================================

    def open_parte_dialog(self, parte_id=None, caso_id=None, parent_window=None):
        """Abre el diálogo para agregar o editar una parte interviniente."""
        if not caso_id:
            messagebox.showwarning("Error", "Se necesita un caso para gestionar sus partes.")
            return
        
        parent = parent_window if parent_window else self.root
        dialog = tk.Toplevel(parent) # <-- MODIFICAR AQUÍ
        dialog.transient(parent) # <-- AÑADIR/ASEGURAR ESTO
        
        #dialog = tk.Toplevel(self.root)
        #dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.title("Nueva Parte" if not parte_id else "Editar Parte")
        dialog.geometry("500x400")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        nombre_var = tk.StringVar()
        tipo_var = tk.StringVar()
        direccion_var = tk.StringVar()
        contacto_var = tk.StringVar()
        initial_notas = ""

        if parte_id:
            parte_data = self.db_crm.get_parte_by_id(parte_id)
            if parte_data:
                nombre_var.set(parte_data.get('nombre', ''))
                tipo_var.set(parte_data.get('tipo', ''))
                direccion_var.set(parte_data.get('direccion', ''))
                contacto_var.set(parte_data.get('contacto', ''))
                initial_notas = parte_data.get('notas', '')

        # Layout del formulario
        row = 0
        ttk.Label(main_frame, text="Nombre Completo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=nombre_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        ttk.Label(main_frame, text="Tipo/Rol:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=tipo_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Dirección:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=direccion_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Contacto:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=contacto_var, width=40).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        ttk.Label(main_frame, text="Notas:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notas_text = tk.Text(main_frame, height=5, width=40)
        notas_text.grid(row=row, column=1, sticky="ew", pady=5)
        notas_text.insert('1.0', initial_notas)
        row += 1

        main_frame.columnconfigure(1, weight=1)

        def save():
            try:
                notas = notas_text.get('1.0', tk.END).strip()
                if parte_id:
                    self.db_crm.update_parte_interviniente(parte_id, nombre_var.get(), tipo_var.get(), direccion_var.get(), contacto_var.get(), notas)
                else:
                    self.db_crm.add_parte_interviniente(caso_id, nombre_var.get(), tipo_var.get(), direccion_var.get(), contacto_var.get(), notas)
                
                messagebox.showinfo("Éxito", "Parte guardada correctamente.", parent=dialog)
                if caso_id in self.case_details_windows:
                    self.case_details_windows[caso_id].partes_tab.load_partes(caso_id)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la parte:\n{e}", parent=dialog)

        ttk.Button(main_frame, text="Guardar", command=save).grid(row=row, column=1, sticky="e", pady=10)
        ttk.Button(main_frame, text="Cancelar", command=dialog.destroy).grid(row=row, column=0, sticky="w", pady=10)

    def delete_selected_parte(self, parte_id, caso_id):
        """Elimina una parte y refresca la UI."""
        if not parte_id: return
        
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta parte?"):
            try:
                self.db_crm.delete_parte_interviniente(parte_id)
                messagebox.showinfo("Éxito", "Parte eliminada correctamente.")
                if caso_id in self.case_details_windows:
                    self.case_details_windows[caso_id].partes_tab.load_partes(caso_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la parte:\n{e}")    

    # ===================================================================
    # === MÉTODOS DE DIÁLOGO PARA TAREAS (LLAMADOS DESDE TareasTab) ===
    # ===================================================================

    def open_tarea_dialog(self, tarea_id=None, caso_id=None, parent_window=None):
        """Abre el diálogo para agregar o editar una tarea."""
        parent = parent_window if parent_window else self.root
        dialog = tk.Toplevel(parent) # <-- MODIFICAR AQUÍ
        dialog.transient(parent) # <-- AÑADIR/ASEGURAR ESTO

        if not caso_id and not tarea_id:
            messagebox.showwarning("Error", "Se requiere un caso para crear una tarea.")
            return

        #dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.title("Nueva Tarea" if not tarea_id else "Editar Tarea")
        dialog.geometry("550x500")

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        descripcion_var = tk.StringVar()
        notas_var = tk.StringVar()
        vencimiento_var = tk.StringVar()
        prioridad_var = tk.StringVar(value='Media')
        estado_var = tk.StringVar(value='Pendiente')
        plazo_procesal_var = tk.BooleanVar()
        recordatorio_var = tk.BooleanVar()
        dias_recordatorio_var = tk.StringVar(value='1')

        caso_id_actual = caso_id

        if tarea_id:
            tarea_data = self.db_crm.get_tarea_by_id(tarea_id)
            if tarea_data:
                caso_id_actual = tarea_data['caso_id'] # El caso de la tarea prevalece
                descripcion_var.set(tarea_data.get('descripcion', ''))
                notas_var.set(tarea_data.get('notas', ''))
                vencimiento_var.set(tarea_data.get('fecha_vencimiento', ''))
                prioridad_var.set(tarea_data.get('prioridad', 'Media'))
                estado_var.set(tarea_data.get('estado', 'Pendiente'))
                plazo_procesal_var.set(bool(tarea_data.get('es_plazo_procesal', False)))
                recordatorio_var.set(bool(tarea_data.get('recordatorio_activo', False)))
                dias_recordatorio_var.set(str(tarea_data.get('recordatorio_dias_antes', 1)))

        # Layout del formulario (simplificado)
        row = 0
        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.NW, pady=2)
        desc_text = tk.Text(main_frame, height=4, width=50)
        desc_text.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        desc_text.insert('1.0', descripcion_var.get())
        row += 1

        ttk.Label(main_frame, text="Fecha Vencimiento:").grid(row=row, column=0, sticky=tk.W, pady=2)
        # Aquí deberías usar el widget DateEntry de tkcalendar si lo tienes
        from tkcalendar import DateEntry
        DateEntry(main_frame, textvariable=vencimiento_var, date_pattern='dd-mm-yyyy', locale='es_AR').grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1
        
        ttk.Label(main_frame, text="Prioridad:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(main_frame, textvariable=prioridad_var, values=['Alta', 'Media', 'Baja'], state="readonly").grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Estado:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Combobox(main_frame, textvariable=estado_var, values=['Pendiente', 'En Progreso', 'Completada', 'Cancelada'], state="readonly").grid(row=row, column=1, sticky="w", pady=2, padx=5)
        row += 1

        ttk.Label(main_frame, text="Notas Adicionales:").grid(row=row, column=0, sticky=tk.NW, pady=2)
        notas_text = tk.Text(main_frame, height=4, width=50)
        notas_text.grid(row=row, column=1, sticky="ew", pady=2, padx=5)
        notas_text.insert('1.0', notas_var.get())
        row += 1
        
        main_frame.columnconfigure(1, weight=1)

        def save():
            try:
                if tarea_id:
                    self.db_crm.update_tarea(
                        tarea_id=tarea_id,
                        descripcion=desc_text.get('1.0', tk.END).strip(),
                        fecha_vencimiento=vencimiento_var.get(),
                        prioridad=prioridad_var.get(),
                        estado=estado_var.get(),
                        notas=notas_text.get('1.0', tk.END).strip(),
                        es_plazo_procesal=plazo_procesal_var.get(),
                        recordatorio_activo=recordatorio_var.get(),
                        recordatorio_dias_antes=dias_recordatorio_var.get()
                    )                
                else:
                    self.db_crm.add_tarea(
                        caso_id=caso_id_actual,
                        descripcion=desc_text.get('1.0', tk.END).strip(),
                        fecha_vencimiento=vencimiento_var.get(),
                        prioridad=prioridad_var.get(),
                        estado=estado_var.get(),
                        notas=notas_text.get('1.0', tk.END).strip(),
                        es_plazo_procesal=plazo_procesal_var.get(),
                        recordatorio_activo=recordatorio_var.get(),
                        recordatorio_dias_antes=dias_recordatorio_var.get()
                    )
                
                messagebox.showinfo("Éxito", "Tarea guardada correctamente.", parent=dialog)
                # Refrescar la ventana de detalles correcta
                if caso_id_actual in self.case_details_windows:
                    window = self.case_details_windows[caso_id_actual]
                    if window.winfo_exists():
                        window.tareas_tab.load_tareas(caso_id_actual)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la tarea:\n{e}", parent=dialog)

        ttk.Button(main_frame, text="Guardar", command=save).grid(row=row, column=1, sticky="e", pady=10)
        ttk.Button(main_frame, text="Cancelar", command=dialog.destroy).grid(row=row, column=0, sticky="w", pady=10)

    def marcar_tarea_como_completada(self, tarea_id, caso_id):
        """Marca una tarea como completada y refresca la UI."""
        if not tarea_id:
            return
        
        if messagebox.askyesno("Confirmar", "¿Marcar esta tarea como 'Completada'?"):
            try:
                self.db_crm.update_tarea(tarea_id=tarea_id, estado='Completada')
                messagebox.showinfo("Éxito", "Tarea marcada como completada.")
                # Refrescar la ventana de detalles si está abierta
                if caso_id in self.case_details_windows:
                    window = self.case_details_windows[caso_id]
                    if window.winfo_exists():
                        window.tareas_tab.load_tareas(caso_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la tarea:\n{e}")

    def delete_selected_tarea(self, tarea_id, caso_id):
        """Elimina una tarea y refresca la UI."""
        if not tarea_id:
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar esta tarea permanentemente?"):
            try:
                self.db_crm.delete_tarea(tarea_id)
                messagebox.showinfo("Éxito", "Tarea eliminada correctamente.")
                # Refrescar la ventana de detalles si está abierta
                if caso_id in self.case_details_windows:
                    window = self.case_details_windows[caso_id]
                    if window.winfo_exists():
                        window.tareas_tab.load_tareas(caso_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la tarea:\n{e}")


    def create_menu(self):
        """Crear la barra de menú"""
        menubar = tk.Menu(self.root)

        # Menú Archivo
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Mostrar Ventana", command=self._mostrar_ventana_callback)
        filemenu.add_separator()
        filemenu.add_command(label="Ocultar a Bandeja", command=self.ocultar_a_bandeja)
        filemenu.add_separator()
        filemenu.add_command(label="Salir (Cerrar Aplicación)", command=self.cerrar_aplicacion_directamente)
        menubar.add_cascade(label="Archivo", menu=filemenu)

        # Menú IA (usando el módulo ia_ui)
        self.ia_menu = IAMenu(menubar, self)

        # Menú Administración
        adminmenu = tk.Menu(menubar, tearoff=0)
        adminmenu.add_command(label="Crear Copia de Seguridad...", command=self.crear_copia_de_seguridad)
        adminmenu.add_command(label="Configuración del Sistema", command=self.open_config_dialog)
        menubar.add_cascade(label="Administración", menu=adminmenu)

        self.root.config(menu=menubar)

    def create_main_layout(self):
        """
        Crear la nueva estructura de interfaz:
        - Columna izquierda: Gestión de Clientes
        - Columna derecha dividida verticalmente:
          - Parte superior: Gestión de Casos  
          - Parte inferior: Agenda/Audiencias
        """
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear PanedWindow horizontal principal
        self.main_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # === COLUMNA IZQUIERDA: GESTIÓN DE CLIENTES ===
        self.left_frame = ttk.LabelFrame(self.main_paned, text="Gestión de Clientes", padding="5")
        self.main_paned.add(self.left_frame, weight=0)
        
        # === COLUMNA DERECHA: CASOS Y AGENDA ===
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=2)
        
        # Crear PanedWindow vertical para dividir casos y agenda
        self.right_paned = ttk.PanedWindow(self.right_frame, orient=tk.VERTICAL)
        self.right_paned.pack(fill=tk.BOTH, expand=True)
        
        # === PARTE SUPERIOR DERECHA: GESTIÓN DE CASOS ===
        self.cases_frame = ttk.LabelFrame(self.right_paned, text="Gestión de Casos", padding="5")
        self.right_paned.add(self.cases_frame, weight=1)
        
        # === PARTE INFERIOR DERECHA: AGENDA/AUDIENCIAS ===
        self.agenda_frame = ttk.LabelFrame(self.right_paned, text="Agenda/Audiencias", padding="5")
        self.right_paned.add(self.agenda_frame, weight=1)

    def initialize_modules(self):
        """Inicializar los módulos en los frames correspondientes"""
        
        # === MÓDULO DE CLIENTES (Columna izquierda) ===
        self.clientes_module = ClientesTab(self.left_frame, self)
        self.clientes_module.pack(fill=tk.BOTH, expand=True)

        # === MÓDULO DE CASOS (Parte superior derecha) ===
        self.casos_module = CasosTab(self.cases_frame, self)
        self.casos_module.pack(fill=tk.BOTH, expand=True)
        
        # Vincular doble clic en casos para abrir ventana de detalles
        self.casos_module.bind_double_click(self.open_case_details_window)

        # === MÓDULO DE AUDIENCIAS (Parte inferior derecha) ===
        self.audiencias_module = AudienciasTab(self.agenda_frame, self)
        self.audiencias_module.pack(fill=tk.BOTH, expand=True)

    def on_case_double_clicked(self, event=None):
        """Llamado cuando se hace doble clic en un caso en el módulo de casos."""
        selected_case = self.casos_module.get_selected_case()
        if selected_case:
            self.open_case_details_window(selected_case)
        else:
            print("Doble clic en caso, pero no hay selección válida.")

    def open_case_details_window(self, case_data):
        """
        Abrir ventana Toplevel con los detalles del caso
        Si ya existe una ventana para este caso, la enfoca en lugar de crear una nueva
        """
        if not case_data:
            messagebox.showwarning("Advertencia", "No hay caso seleccionado")
            return
            
        case_id = case_data.get('id')
        
        # Si ya existe una ventana para este caso, enfocarla
        if case_id in self.case_details_windows:
            window = self.case_details_windows[case_id]
            if window.winfo_exists():
                print(f"Enfocando ventana existente para caso ID: {case_id}")
                window.lift()
                window.focus()
                return
            else:
                # La ventana fue cerrada manualmente, la eliminamos del diccionario.
                print(f"Eliminando referencia a ventana cerrada para caso ID: {case_id}")
                del self.case_details_windows[case_id]

        # Crear la nueva ventana de detalles del caso
        # Necesitaremos crear el archivo 'case_details_window.py'
        try:
            from case_details_window import CaseDetailsWindow
            print(f"Creando nueva ventana de detalles para caso ID: {case_id}")
            details_window = CaseDetailsWindow(parent=self.root, app_controller=self, case_data=case_data)
            self.case_details_windows[case_id] = details_window        
                        
        # Callback para limpiar referencia cuando se cierre la ventana
            def on_window_close():
                if case_id in self.case_details_windows:
                    del self.case_details_windows[case_id]
                details_window.destroy()
            
            details_window.protocol("WM_DELETE_WINDOW", on_window_close)
        
        except ImportError:
            messagebox.showerror("Error de Módulo", "No se encontró el archivo 'case_details_window.py'.\nLa funcionalidad de detalles de caso no está disponible.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de detalles del caso:\n{e}", parent=self.root)

    def load_initial_data(self):
        """Cargar datos iniciales en todos los módulos"""
        self.clientes_module.load_clients()
        self.audiencias_module.cargar_audiencias_fecha_actual()
        self.audiencias_module.marcar_dias_audiencias_calendario()

    def start_background_threads(self):
        """Iniciar hilos de fondo para notificaciones y bandeja"""
        self.hilo_recordatorios = threading.Thread(target=self.verificar_recordatorios_periodicamente, daemon=True)
        self.hilo_recordatorios.start()

        self.hilo_bandeja = threading.Thread(target=self.setup_tray_icon, daemon=True)
        self.hilo_bandeja.start()

    # === MÉTODOS DE COMUNICACIÓN ENTRE MÓDULOS ===

    def on_client_selected(self, client_data):
        """Manejar selección de cliente desde el módulo de clientes"""
        self.selected_client = client_data
        # Cargar casos del cliente seleccionado
        self.casos_module.on_client_changed(client_data)
        
        # Limpiar selección de caso ya que cambió el cliente
        self.selected_case = None

    def on_client_deleted(self):
        """Manejar eliminación de cliente"""
        self.selected_client = None
        self.selected_case = None
        self.casos_module.clear_case_list()

    def on_case_selected(self, case_data):
        """Manejar selección de caso desde el módulo de casos"""
        self.selected_case = case_data

    def on_case_deleted(self):
        """Manejar eliminación de caso"""
        self.selected_case = None

    def on_case_folder_updated(self, case_data):
        """Manejar actualización de carpeta de caso"""
        self.selected_case = case_data
        # Notificar a todas las ventanas de detalles abiertas
        for case_id, window in self.case_details_windows.items():
            if window.winfo_exists() and hasattr(window, 'refresh_case_data'):
                window.refresh_case_data(case_data)
                
    def refresh_main_window_data(self):
        """Refresca las listas de clientes y casos en la ventana principal."""
        print("Refrescando datos de la ventana principal...")
        self.clientes_module.refresh_data()
        self.casos_module.refresh_data()
        # También podríamos refrescar la agenda si fuera necesario
        # self.audiencias_module.refresh_data()
    # === MÉTODOS DE NOTIFICACIONES Y BANDEJA (mantenidos del original) ===
    
    def verificar_recordatorios_periodicamente(self):
        """Verificar recordatorios cada 60 segundos"""
        import time
        while not self.stop_event.is_set():
            try:
                self.verificar_recordatorios()
                time.sleep(60)
            except Exception as e:
                print(f"Error en verificar_recordatorios_periodicamente: {e}")
                time.sleep(60)

    def verificar_recordatorios(self):
        """Verificar y mostrar recordatorios de audiencias"""
        try:
            audiencias_hoy = self.db_crm.get_audiencias_by_date(datetime.date.today())
            for audiencia in audiencias_hoy:
                audiencia_id = audiencia['id']
                if audiencia['recordatorio_activo'] == 1 and audiencia_id not in self.recordatorios_mostrados_hoy:
                    self.mostrar_notificacion_audiencia(audiencia)
                    self.recordatorios_mostrados_hoy.add(audiencia_id)
        except Exception as e:
            print(f"Error al verificar recordatorios: {e}")

    def mostrar_notificacion_audiencia(self, audiencia):
        """Mostrar notificación de audiencia"""
        try:
            titulo = "Recordatorio de Audiencia"
            mensaje = f"Audiencia: {audiencia['descripcion']}\nFecha: {audiencia['fecha']}\nHora: {audiencia['hora']}"
            
            if PLYER_AVAILABLE:
                plyer.notification.notify(
                    title=titulo,
                    message=mensaje,
                    timeout=10
                )
            else:
                # Fallback: mostrar en consola
                print(f"🔔 {titulo}: {mensaje}")
        except Exception as e:
            print(f"Error al mostrar notificación: {e}")

    def setup_tray_icon(self):
        """Configurar el icono de la bandeja del sistema"""
        if not PYSTRAY_AVAILABLE or not PIL_AVAILABLE:
            print("Icono de bandeja deshabilitado: librerías no disponibles")
            return
            
        try:
            icon_path = self.resource_path("assets/icono.ico")
            if not os.path.exists(icon_path):
                icon_path = self.resource_path("assets/icono.png")
            
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # Crear imagen básica si no se encuentra el archivo
                image = Image.new('RGB', (32, 32), color='blue')
                
            menu = (
                item('Mostrar', self._mostrar_ventana_callback),
                item('Ocultar', self.ocultar_a_bandeja),
                item('Salir', self.cerrar_aplicacion_directamente)
            )
            
            self.tray_icon = icon("CRM Legal", image, menu=menu)
            self.tray_icon.run()
        except Exception as e:
            print(f"Error al configurar icono de bandeja: {e}")

    def _mostrar_ventana_callback(self, icon_ref=None, item_ref=None):
        """Mostrar la ventana principal"""
        self.root.after(0, self.mostrar_ventana)
    
    def resource_path(self, relative_path):
        """Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, relative_path)

    def mostrar_ventana(self):
        """Mostrar la ventana principal"""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)

    def ocultar_a_bandeja(self):
        """Ocultar la ventana a la bandeja del sistema"""
        self.root.withdraw()

    def cerrar_aplicacion_directamente(self, icon_ref=None, item_ref=None):
        """Cerrar completamente la aplicación"""
        self.stop_event.set()
        if self.tray_icon:
            self.tray_icon.stop()
        
        # Cerrar todas las ventanas de detalles
        for window in list(self.case_details_windows.values()):
            if window.winfo_exists():
                window.destroy()
        
        self.root.quit()
        self.root.destroy()

    def crear_copia_de_seguridad(self):
        """Crear copia de seguridad de la base de datos"""
        try:
            from tkinter import filedialog
            archivo_destino = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Base de datos", "*.db"), ("Todos los archivos", "*.*")],
                title="Guardar copia de seguridad"
            )
            
            if archivo_destino:
                import shutil
                shutil.copy2("crm_legal.db", archivo_destino)
                messagebox.showinfo("Éxito", f"Copia de seguridad creada en:\n{archivo_destino}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear copia de seguridad:\n{str(e)}")

    def open_config_dialog(self):
        """Abrir diálogo de configuración del sistema"""
        messagebox.showinfo("Configuración", "Función de configuración en desarrollo")

# === FUNCIÓN PRINCIPAL ===
def main():
    root = tk.Tk()
    app = CRMLegalAppRefactored(root)
    root.mainloop()

if __name__ == "__main__":
    main()
