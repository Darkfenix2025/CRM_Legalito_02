# case_details_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import os

# Imports de todas las pestañas de detalles del caso
from casos_detalles_ui import CasosDetallesTab
from documentos_ui import DocumentosTab
from tareas_ui import TareasTab
from partes_ui import PartesTab
from seguimiento_ui import SeguimientoTab
from etiquetas_ui import EtiquetasTab
from financiero_ui import FinancieroTab

class CaseDetailsWindow(tk.Toplevel):
    """
    Ventana Toplevel que contiene el notebook con todas las pestañas
    de detalles del caso seleccionado.
    """
    
    def __init__(self, parent, app_controller, case_data):
        super().__init__(parent)
        
        self.app_controller = app_controller
        self.case_data = case_data
        self.parent_window = parent
        
        # Configurar la ventana
        self.setup_window()
        
        # Crear la interfaz
        self.create_interface()
        
        # Cargar datos del caso en todas las pestañas
        self.load_case_data()
    
    def setup_window(self):
        """Configurar propiedades de la ventana"""
        # Título con información del caso
        case_title = self.case_data.get('caratula', 'Caso sin carátula')
        case_number = self.case_data.get('num_expediente', '')
        case_year = self.case_data.get('anio_caratula', '')
        
        title_parts = ["Detalles del Caso"]
        if case_number or case_year:
            title_parts.append(f"[{case_number}/{case_year}]")
        if case_title:
            title_parts.append(f"- {case_title}")
        
        self.title(" ".join(title_parts))
        
        # Configurar tamaño y posición
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configurar la ventana como modal (opcional)
        # self.transient(self.parent_window)
        # self.grab_set()
        
        # Centrar en pantalla
        self.center_window()
        
        # Configurar icono si existe
        try:
            if hasattr(self.app_controller, 'resource_path'):
                icon_path = self.app_controller.resource_path("assets/icono.ico")
                if not os.path.exists(icon_path):
                    icon_path = self.app_controller.resource_path("assets/icono.png")
            else:
                icon_path = "assets/icono.ico"
                if not os.path.exists(icon_path):
                    icon_path = "assets/icono.png"
            
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
    
    def center_window(self):
        """Centrar la ventana en la pantalla"""
        self.update_idletasks()
        
        # Obtener dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Obtener dimensiones de la ventana
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # Calcular posición centrada
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def create_interface(self):
        """Crear la interfaz de la ventana con el notebook y pestañas"""
        
        # Frame principal con padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear el notebook principal
        self.details_notebook = ttk.Notebook(main_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear todas las pestañas
        self.create_tabs()
        
        # Frame inferior con botones de acción (opcional)
        self.create_action_buttons(main_frame)
    
    def create_tabs(self):
        """Crear todas las pestañas del notebook de detalles"""
        
        # Pestaña Detalles del Caso
        self.casos_detalles_tab = CasosDetallesTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.casos_detalles_tab, text='Detalles del Caso')
        
        # Pestaña Documentos
        self.documentos_tab = DocumentosTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.documentos_tab, text='Documentación')
        
        # Pestaña Tareas/Plazos
        self.tareas_tab = TareasTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.tareas_tab, text="Tareas/Plazos")
        
        # Pestaña Partes
        self.partes_tab = PartesTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.partes_tab, text="Partes")
        
        # Pestaña Seguimiento
        self.seguimiento_tab = SeguimientoTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.seguimiento_tab, text="Seguimiento")
        
        # Pestaña Etiquetas Globales
        self.etiquetas_tab = EtiquetasTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.etiquetas_tab, text="Etiquetas")
        
        # Pestaña Financiero
        self.financiero_tab = FinancieroTab(self.details_notebook, self.app_controller)
        self.details_notebook.add(self.financiero_tab, text="Financiero")
    
    def create_action_buttons(self, parent):
        """Crear botones de acción en la parte inferior (opcional)"""
        
        # Frame para botones
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botón de actualizar/refrescar
        refresh_btn = ttk.Button(
            buttons_frame, 
            text="Actualizar", 
            command=self.refresh_all_tabs
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de cerrar
        close_btn = ttk.Button(
            buttons_frame, 
            text="Cerrar", 
            command=self.close_window
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Información del caso en el centro
        case_info = f"Caso ID: {self.case_data.get('id', 'N/A')}"
        if self.case_data.get('num_expediente') and self.case_data.get('anio_caratula'):
            case_info += f" | Expediente: {self.case_data['num_expediente']}/{self.case_data['anio_caratula']}"
        
        info_label = ttk.Label(buttons_frame, text=case_info, font=('TkDefaultFont', 8))
        info_label.pack(side=tk.LEFT, expand=True)
    
    def load_case_data(self):
        """Cargar los datos del caso en todas las pestañas"""
        
        # Lista de pestañas que necesitan ser notificadas del caso
        tabs_with_case_awareness = [
            self.casos_detalles_tab,
            self.documentos_tab,
            self.tareas_tab,
            self.partes_tab,
            self.seguimiento_tab,
            self.financiero_tab
        ]
        
        # Notificar a todas las pestañas sobre el caso
        for tab in tabs_with_case_awareness:
            if hasattr(tab, 'on_case_changed'):
                try:
                    tab.on_case_changed(self.case_data)
                except Exception as e:
                    print(f"Error al cargar datos del caso en {tab.__class__.__name__}: {e}")
        
        # Habilitar pestañas
        self.enable_all_tabs()
    
    def enable_all_tabs(self):
        """Habilitar todas las pestañas para el caso actual"""
        for i in range(self.details_notebook.index("end")):
            self.details_notebook.tab(i, state="normal")
    
    def disable_all_tabs(self):
        """Deshabilitar todas las pestañas (útil si no hay caso)"""
        for i in range(self.details_notebook.index("end")):
            if i > 0:  # No deshabilitar la primera pestaña (Detalles)
                self.details_notebook.tab(i, state="disabled")
    
    def refresh_case_data(self, updated_case_data=None):
        """Actualizar los datos del caso y refrescar todas las pestañas"""
        
        if updated_case_data:
            self.case_data = updated_case_data
        else:
            # Recargar datos de la base de datos
            try:
                case_id = self.case_data.get('id')
                if case_id:
                    updated_data = self.app_controller.db_crm.get_case_by_id(case_id)
                    if updated_data:
                        self.case_data = updated_data
            except Exception as e:
                print(f"Error al recargar datos del caso: {e}")
                return
        
        # Actualizar título de la ventana
        self.setup_window_title()
        
        # Recargar datos en todas las pestañas
        self.load_case_data()
    
    def setup_window_title(self):
        """Actualizar el título de la ventana con datos del caso actual"""
        case_title = self.case_data.get('caratula', 'Caso sin carátula')
        case_number = self.case_data.get('num_expediente', '')
        case_year = self.case_data.get('anio_caratula', '')
        
        title_parts = ["Detalles del Caso"]
        if case_number or case_year:
            title_parts.append(f"[{case_number}/{case_year}]")
        if case_title:
            title_parts.append(f"- {case_title}")
        
        self.title(" ".join(title_parts))
    
    def refresh_all_tabs(self):
        """Refrescar todas las pestañas con datos actualizados"""
        self.refresh_case_data()
    
    def close_window(self):
        """Cerrar la ventana"""
        self.destroy()
    
    def get_case_data(self):
        """Obtener los datos del caso actual"""
        return self.case_data
    
    def get_case_id(self):
        """Obtener el ID del caso actual"""
        return self.case_data.get('id') if self.case_data else None
