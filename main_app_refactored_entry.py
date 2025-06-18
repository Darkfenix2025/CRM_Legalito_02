# main_app_refactored_entry.py
"""
Punto de entrada principal para el CRM Legal Refactorizado
Este archivo utiliza la nueva estructura de interfaz con:
- Ventana principal simplificada (columna izquierda: clientes, columna derecha: casos + agenda)
- Ventana Toplevel separada para detalles de casos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Asegurar que el directorio actual esté en el path
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

# Importar la clase principal refactorizada
from main_window_refactored import CRMLegalAppRefactored
import crm_database as db

def initialize_database():
    """Inicializar la base de datos con las tablas necesarias"""
    try:
        print("Inicializando base de datos...")
        db.create_tables()
        print("✅ Base de datos inicializada correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        messagebox.showerror("Error de Base de Datos", 
                           f"No se pudo inicializar la base de datos:\n{e}")
        return False
    return True

def check_dependencies():
    """Verificar que todas las dependencias estén disponibles"""
    required_modules = [
        'tkinter', 'sqlite3', 'PIL', 'plyer', 'pystray', 'tkcalendar'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            elif module == 'tkinter':
                import tkinter
            elif module == 'sqlite3':
                import sqlite3
            elif module == 'plyer':
                import plyer
            elif module == 'pystray':
                import pystray
            elif module == 'tkcalendar':
                import tkcalendar
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Faltan las siguientes dependencias:\n" + "\n".join(missing_modules)
        error_msg += "\n\nInstale las dependencias usando:\npip install pillow plyer pystray tkcalendar"
        messagebox.showerror("Dependencias Faltantes", error_msg)
        return False
    
    print("✅ Todas las dependencias están disponibles")
    return True

def main():
    """Función principal de la aplicación"""
    print("=== Iniciando CRM Legal Refactorizado v2.1 ===")
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    # Inicializar base de datos
    if not initialize_database():
        return
    
    # Crear ventana principal
    try:
        print("Creando ventana principal...")
        root = tk.Tk()
        
        # Configurar estilos básicos
        style = ttk.Style()
        try:
            # Intentar usar un tema moderno si está disponible
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'vista' in available_themes:
                style.theme_use('vista')
            elif 'xpnative' in available_themes:
                style.theme_use('xpnative')
        except Exception as e:
            print(f"Advertencia: No se pudo configurar tema visual: {e}")
        
        # Configurar ventana root
        root.withdraw()  # Ocultar temporalmente mientras se inicializa
        
        # Crear aplicación
        print("Inicializando aplicación...")
        app = CRMLegalAppRefactored(root)
        
        # Mostrar ventana
        root.deiconify()
        print("✅ Aplicación iniciada correctamente")
        print("=== CRM Legal Refactorizado listo para usar ===")
        
        # Iniciar bucle principal
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Error crítico al iniciar la aplicación:\n{e}"
        print(f"❌ {error_msg}")
        try:
            messagebox.showerror("Error Crítico", error_msg)
        except:
            pass
        return

if __name__ == "__main__":
    main()