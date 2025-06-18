# documentos_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
import datetime # Añadido para _get_modification_time

class DocumentosTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.current_case_data = None # Para guardar los datos del caso actual
        self.current_display_folder_path = None # La carpeta que se está mostrando actualmente en el Treeview
        self._create_widgets()

    def _create_widgets(self):
        # ... (configuración de info_frame, case_info_lbl, folder_path_lbl como estaba) ...
        # --- Información del Caso Actual ---
        info_frame = ttk.LabelFrame(self, text="Información del Caso", padding="5")
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Caso:").grid(row=0, column=0, sticky=tk.W, pady=2, padx=5)
        self.case_info_lbl = ttk.Label(info_frame, text="Ningún caso seleccionado", wraplength=400)
        self.case_info_lbl.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(info_frame, text="Mostrando Carpeta:").grid(row=1, column=0, sticky=tk.W, pady=2, padx=5) # Cambiado texto
        self.folder_display_lbl = ttk.Label(info_frame, text="N/A", wraplength=400, foreground="gray")
        self.folder_display_lbl.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)


        # --- Lista de Documentos ---
        docs_frame = ttk.LabelFrame(self, text="Archivos y Carpetas", padding="5")
        docs_frame.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        docs_frame.columnconfigure(0, weight=1) # Columna para el Treeview y scrollbar_x
        docs_frame.columnconfigure(1, weight=0) # Columna para scrollbar_y
        
        docs_frame.rowconfigure(0, weight=1)    # Fila para el Treeview (expandible)
        docs_frame.rowconfigure(1, weight=0)    # Fila para el Scrollbar X (altura fija)
        docs_frame.rowconfigure(2, weight=1)    # Fila para el buttons_frame (altura fija) <--- AÑADIDO/ASEGURADO
        
        docs_frame.rowconfigure(0, weight=0) 
         # La altura del Treeview se controlará por su contenido o un 'height'
        docs_frame.rowconfigure(1, weight=0)    # Fila para el Scrollbar X (altura fija)
        docs_frame.rowconfigure(2, weight=0)    # Fila para el buttons_frame (altura fija)

        # TreeView de documentos
        # La columna '#0' (tree) mostrará el nombre con el icono. Las 'values' son para las otras columnas.
        docs_cols = ('Tipo', 'Tamaño', 'Modificado') # Ya no necesitamos 'Nombre' como columna separada aquí
        self.docs_tree = ttk.Treeview(docs_frame, columns=docs_cols, show='tree headings', selectmode='browse', height=4)
        
        self.docs_tree.heading('#0', text='Nombre / Estructura') # Columna del árbol
        self.docs_tree.heading('Tipo', text='Tipo')
        self.docs_tree.heading('Tamaño', text='Tamaño')
        self.docs_tree.heading('Modificado', text='Modificado')

        self.docs_tree.column('#0', width=300, stretch=True, anchor=tk.W) # Más ancho para nombre y estructura
        self.docs_tree.column('Tipo', width=100, stretch=tk.NO, anchor=tk.W)
        self.docs_tree.column('Tamaño', width=100, stretch=tk.NO, anchor=tk.E) # Alineado a la derecha
        self.docs_tree.column('Modificado', width=150, stretch=tk.NO, anchor=tk.W)

        # Scrollbars
        docs_scrollbar_y = ttk.Scrollbar(docs_frame, orient=tk.VERTICAL, command=self.docs_tree.yview)
        self.docs_tree.configure(yscrollcommand=docs_scrollbar_y.set)
        
        docs_scrollbar_x = ttk.Scrollbar(docs_frame, orient=tk.HORIZONTAL, command=self.docs_tree.xview)
        self.docs_tree.configure(xscrollcommand=docs_scrollbar_x.set)
        
        # Ubicación de los widgets dentro de docs_frame
        self.docs_tree.grid(row=0, column=0, sticky='ewns')
        docs_scrollbar_y.grid(row=0, column=1, sticky='ns')
        docs_scrollbar_x.grid(row=1, column=0, columnspan=2, sticky='ew') # columnspan=2 para abarcar debajo del tree y scroll_y

        self.docs_tree.bind('<Double-1>', self.on_document_double_click)
        self.docs_tree.bind('<<TreeviewSelect>>', self.on_document_select)

        # --- Botones de Acción ---
        buttons_frame = ttk.Frame(docs_frame) 
        buttons_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0)) # Fila 2
        
        buttons_frame.columnconfigure(0, weight=1) 
        buttons_frame.columnconfigure(1, weight=1) 
        buttons_frame.columnconfigure(2, weight=1)

        self.refresh_btn = ttk.Button(buttons_frame, text="Actualizar Vista", command=self.refresh_documents_display)
        self.refresh_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.open_item_btn = ttk.Button(buttons_frame, text="Abrir Selección", command=self.open_selected_item, state=tk.DISABLED)
        self.open_item_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.open_root_folder_btn = ttk.Button(buttons_frame, text="Abrir Carpeta Raíz", command=self.open_case_root_folder, state=tk.DISABLED)
        self.open_root_folder_btn.grid(row=0, column=2, sticky='ew', padx=(5,0))

        self.update_action_buttons_state()

    def on_case_changed(self, case_data):
        """Manejar cambio de caso seleccionado desde main_app."""
        print(f"[DocumentosTab] on_case_changed recibido. Caso: {'ID ' + str(case_data['id']) if case_data else 'Ninguno'}")
        self.current_case_data = case_data
        if case_data:
            self.case_info_lbl.config(text=f"{case_data.get('caratula', 'N/A')} (ID: {case_data.get('id')})")
            root_folder = case_data.get('ruta_carpeta') # Usar la clave correcta
            if root_folder and os.path.isdir(root_folder):
                self.current_display_folder_path = root_folder # Empezar mostrando la raíz del caso
                self.folder_display_lbl.config(text=self.current_display_folder_path, foreground="black")
                self.load_documents_from_path(self.current_display_folder_path)
            else:
                self.folder_display_lbl.config(text="Carpeta del caso no asignada o no existe.", foreground="red")
                self.current_display_folder_path = None
                self.clear_document_list()
                self.docs_tree.insert('', 'end', text="Carpeta del caso no válida.", values=('', '', ''), tags=('error',))
        else:
            self.case_info_lbl.config(text="Ningún caso seleccionado")
            self.folder_display_lbl.config(text="N/A", foreground="gray")
            self.current_display_folder_path = None
            self.clear_document_list()
        
        self.update_action_buttons_state()

    def load_documents_from_path(self, folder_path_to_load):
        """Carga el contenido del folder_path_to_load en el Treeview."""
        self.clear_document_list()
        self.current_display_folder_path = folder_path_to_load # Actualizar la carpeta que se está mostrando
        self.folder_display_lbl.config(text=self.current_display_folder_path) # Actualizar label

        if not folder_path_to_load or not os.path.isdir(folder_path_to_load):
            self.docs_tree.insert('', 'end', text="Ruta no válida o no accesible.", values=('', '', ''), tags=('error',))
            self.update_action_buttons_state()
            return

        # Añadir opción para subir un nivel si no estamos en la carpeta raíz del caso actual
        if self.current_case_data:
            root_case_folder = self.current_case_data.get('ruta_carpeta')
            if root_case_folder and os.path.normpath(folder_path_to_load) != os.path.normpath(root_case_folder) and \
               folder_path_to_load.startswith(root_case_folder): # Solo si estamos dentro de la jerarquía del caso
                parent_dir = os.path.dirname(folder_path_to_load)
                if os.path.isdir(parent_dir) and parent_dir != folder_path_to_load : # Evitar bucle en raíz de disco
                     self.docs_tree.insert('', '0', iid=parent_dir, text="⬆️ [..] Subir Nivel", 
                                          values=("Carpeta Padre", "", ""), tags=('parent_folder',))

        self._populate_treeview_recursive(folder_path_to_load, '') # '' es el parent_item para la raíz del tree
        
        if not self.docs_tree.get_children(''): # Si después de cargar, la raíz del treeview no tiene hijos
            self.docs_tree.insert('', 'end', text="Carpeta vacía.", values=('', '', ''), tags=('empty',))
        
        self.update_action_buttons_state()


    def _populate_treeview_recursive(self, directory_path, parent_iid, max_depth=3, current_depth=0):
        """Popula el Treeview recursivamente. El parent_iid es el iid del item padre en el Treeview."""
        if current_depth >= max_depth:
            # Opcional: Añadir un item placeholder para indicar que hay más pero no se muestra
            # self.docs_tree.insert(parent_iid, 'end', text="[...]", values=("Más...", "", ""), state='disabled')
            return

        try:
            # Ordenar para consistencia: directorios primero, luego archivos, ambos alfabéticamente
            items = sorted(os.listdir(directory_path), key=lambda x: (not os.path.isdir(os.path.join(directory_path, x)), x.lower()))

            for item_name in items:
                item_path = os.path.join(directory_path, item_name)
                
                if os.path.isdir(item_path):
                    try:
                        # item_count = len(os.listdir(item_path)) # Puede ser lento para directorios grandes
                        # Para directorios, la columna "Tamaño" puede quedar vacía o indicar "Carpeta"
                        dir_node_iid = item_path # RUTA COMPLETA ES EL IID
                        node = self.docs_tree.insert(parent_iid, 'end', iid=dir_node_iid, 
                                               text=f"📁 {item_name}", 
                                               values=("Carpeta", "", self._get_modification_time(item_path)), 
                                               tags=('directory',))
                        self._populate_treeview_recursive(item_path, node, max_depth, current_depth + 1)
                    except PermissionError:
                        self.docs_tree.insert(parent_iid, 'end', iid=item_path + "_noaccess", # IID único
                                            text=f"🚫 {item_name} (Sin acceso)", 
                                            values=("Carpeta", "Sin acceso", ""), 
                                            tags=('no_access',))
                elif os.path.isfile(item_path):
                    try:
                        file_size_str = self._format_file_size(os.path.getsize(item_path))
                        file_ext = os.path.splitext(item_name)[1].lower()
                        file_type_str = self._get_file_type_description(file_ext)
                        icon = self._get_file_icon(file_ext)
                        file_node_iid = item_path # RUTA COMPLETA ES EL IID

                        self.docs_tree.insert(parent_iid, 'end', iid=file_node_iid,
                                            text=f"{icon} {item_name}", 
                                            values=(file_type_str, file_size_str, self._get_modification_time(item_path)), 
                                            tags=('file',))
                    except (PermissionError, OSError) as e_file:
                        print(f"Error procesando archivo {item_path}: {e_file}")
                        self.docs_tree.insert(parent_iid, 'end', iid=item_path + "_error", # IID único
                                            text=f"⚠️ {item_name} (Error)", 
                                            values=("Error", "N/A", ""), 
                                            tags=('error_file',))
            
            # Configurar tags (esto podría hacerse una sola vez en _create_widgets)
            self.docs_tree.tag_configure('directory', foreground='blue')
            # self.docs_tree.tag_configure('file', foreground='black') # Ya es el color por defecto
            self.docs_tree.tag_configure('parent_folder', foreground='darkgreen', font=('TkDefaultFont', 9, 'italic'))
            self.docs_tree.tag_configure('no_access', foreground='red')
            self.docs_tree.tag_configure('error_file', foreground='orange')
            self.docs_tree.tag_configure('error', foreground='red')
            self.docs_tree.tag_configure('empty', foreground='gray')
            self.docs_tree.tag_configure('no_folder', foreground='red')


        except Exception as e:
            print(f"Error al cargar contenido del directorio {directory_path}: {e}")
            # Podrías insertar un item de error en el treeview si lo deseas
            # self.docs_tree.insert(parent_iid, 'end', text=f"Error al leer {os.path.basename(directory_path)}", tags=('error',))


    def clear_document_list(self):
        for item in self.docs_tree.get_children(): # Limpiar hijos de la raíz
            self.docs_tree.delete(item)
        # Si el treeview tiene una raíz explícita con iid='', puedes usar:
        # for item in self.docs_tree.get_children(''):
        #    self.docs_tree.delete(item)


    def on_document_select(self, event):
        self.update_action_buttons_state()

    def on_document_double_click(self, event):
        self.open_selected_item()

    def open_selected_item(self):
        selected_iids = self.docs_tree.selection()
        if not selected_iids:
            return

        item_iid = selected_iids[0] # El iid es la ruta completa o la ruta al padre para "subir"
        item_tags = self.docs_tree.item(item_iid, 'tags')

        if not os.path.exists(item_iid) and 'parent_folder' not in item_tags: # Chequeo extra
            messagebox.showerror("Error", f"La ruta del elemento no es válida o no existe:\n{item_iid}", parent=self)
            self.refresh_documents_display() # Recargar por si el sistema de archivos cambió
            return

        if 'directory' in item_tags or 'parent_folder' in item_tags:
            # Navegar a la carpeta (el iid es la ruta a la carpeta)
            print(f"[DocumentosTab] Navegando a carpeta por doble clic/botón: {item_iid}")
            self.load_documents_from_path(item_iid)
        elif 'file' in item_tags:
            # Abrir archivo
            try:
                if sys.platform == "win32":
                    os.startfile(os.path.normpath(item_iid))
                elif sys.platform == "darwin":
                    subprocess.call(["open", item_iid])
                else:
                    subprocess.call(["xdg-open", item_iid])
            except Exception as e:
                messagebox.showerror("Error al Abrir", f"No se pudo abrir el archivo:\n{item_iid}\n\nError: {e}", parent=self)
        # else: # Podría ser un item de error o 'no_folder', 'empty'
            # messagebox.showinfo("Información", "No se puede abrir este tipo de elemento.", parent=self)


    def open_case_root_folder(self):
        """Abrir la carpeta raíz asignada al caso actual en el explorador de archivos."""
        if self.current_case_data:
            root_folder = self.current_case_data.get('ruta_carpeta')
            if root_folder and os.path.isdir(root_folder):
                try:
                    if sys.platform == "win32": os.startfile(os.path.normpath(root_folder))
                    elif sys.platform == "darwin": subprocess.call(["open", root_folder])
                    else: subprocess.call(["xdg-open", root_folder])
                except Exception as e:
                    messagebox.showerror("Error al Abrir Carpeta", f"No se pudo abrir la carpeta raíz del caso:\n{root_folder}\n\nError: {e}", parent=self)
            else:
                messagebox.showinfo("Sin Carpeta", "El caso actual no tiene una carpeta raíz asignada o válida.", parent=self)
        else:
            messagebox.showinfo("Sin Caso", "No hay un caso seleccionado para abrir su carpeta raíz.", parent=self)


    def refresh_documents_display(self): # Renombrado para claridad
        """Refresca la vista actual de documentos (la carpeta que se está mostrando)."""
        if self.current_display_folder_path and os.path.isdir(self.current_display_folder_path):
            print(f"[DocumentosTab] Actualizando vista de: {self.current_display_folder_path}")
            self.load_documents_from_path(self.current_display_folder_path)
        elif self.current_case_data and self.current_case_data.get('ruta_carpeta'):
            # Si la carpeta actual no es válida, intenta volver a la raíz del caso
            print(f"[DocumentosTab] Vista actual no válida, intentando recargar raíz del caso.")
            self.on_case_changed(self.current_case_data)
        else:
            print(f"[DocumentosTab] No hay carpeta válida para actualizar.")
            self.clear_document_list()
            self.docs_tree.insert('', 'end', text="No hay carpeta para mostrar o actualizar.", values=('', '', ''), tags=('error',))
            self.update_action_buttons_state()


    def update_action_buttons_state(self):
        """Actualiza el estado de los botones de acción de esta pestaña."""
        selected_iids = self.docs_tree.selection()
        item_selected = bool(selected_iids)
        
        can_open_item = False
        if item_selected:
            item_tags = self.docs_tree.item(selected_iids[0], 'tags')
            if 'file' in item_tags or 'directory' in item_tags or 'parent_folder' in item_tags:
                can_open_item = True
        
        self.open_item_btn.config(state=tk.NORMAL if can_open_item else tk.DISABLED)
        # self.show_path_btn.config(state=tk.NORMAL if item_selected else tk.DISABLED) # Si lo reactivas

        # El botón de abrir carpeta raíz del caso depende de si hay un caso con ruta
        case_has_valid_root_folder = False
        if self.current_case_data:
            root_folder = self.current_case_data.get('ruta_carpeta')
            if root_folder and os.path.isdir(root_folder):
                case_has_valid_root_folder = True
        self.open_root_folder_btn.config(state=tk.NORMAL if case_has_valid_root_folder else tk.DISABLED)

        # El botón de refrescar siempre está activo si hay una carpeta mostrándose o un caso con carpeta
        can_refresh = bool(self.current_display_folder_path and os.path.isdir(self.current_display_folder_path)) or case_has_valid_root_folder
        self.refresh_btn.config(state=tk.NORMAL if can_refresh else tk.DISABLED)


    # Los siguientes métodos ya no son necesarios aquí si _get_full_path_from_tree_item usa el iid.
    # _get_modification_time, _format_file_size, _get_file_type_description, _get_file_icon
    # Se llaman desde _populate_treeview_recursive y pueden quedarse allí o moverse a helpers si se usan en otros sitios.
    # Por ahora los dejo aquí.

    def _get_modification_time(self, file_path):
        try:
            timestamp = os.path.getmtime(file_path)
            return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
        except: return "N/A"

    def _format_file_size(self, size_bytes):
        if size_bytes < 1024: return f"{size_bytes} B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0: return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB" # Si llega aquí, es enorme

    def _get_file_type_description(self, extension):
        # ... (tu diccionario file_types como estaba) ...
        file_types = {'.pdf': 'PDF', '.doc': 'Word', '.docx': 'Word', '.xls': 'Excel', '.xlsx': 'Excel', '.txt': 'Texto', '.jpg': 'Imagen', '.png': 'Imagen', '.zip': 'Archivo Comprimido'} # Ejemplo abreviado
        return file_types.get(extension.lower(), extension.upper()[1:] if extension else 'Archivo')


    def _get_file_icon(self, extension):
        # ... (tu diccionario icons como estaba) ...
        icons = {'.pdf': '📄', '.doc': '📝', '.docx': '📝', '.xls': '📊', '.xlsx': '📊', '.txt': '📄', '.jpg': '🖼️', '.png': '🖼️', '.zip': '📦'} # Ejemplo abreviado
        return icons.get(extension.lower(), '❓')

    # Método refresh_data para consistencia con otros módulos, si main_app lo llama.
    def refresh_data(self):
        """Llamado desde main_app para refrescar el contenido de esta pestaña si es necesario."""
        print(f"[DocumentosTab] refresh_data llamado. Caso actual: {self.current_case_data.get('id') if self.current_case_data else 'Ninguno'}")
        if self.current_case_data:
            # Recargar basado en la carpeta raíz del caso actual
            self.on_case_changed(self.current_case_data) 
        else:
            self.on_case_changed(None)


    # Los métodos get_current_case y get_current_folder_path que tenías son útiles para depuración
    # o si otros módulos necesitaran preguntar a DocumentosTab por su estado. Los mantengo.
    def get_current_case(self):
        return self.current_case_data

    def get_current_folder_path(self):
        return self.current_display_folder_path