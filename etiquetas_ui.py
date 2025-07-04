# etiquetas_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class EtiquetasTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.selected_etiqueta_id = None
        self._create_widgets()

    def _create_widgets(self):
        # Configurar el frame principal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Panel Izquierdo: Gestión de Etiquetas ---
        left_panel = ttk.LabelFrame(self, text="Gestión de Etiquetas Globales", padding="5")
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=0)
        left_panel.rowconfigure(2, weight=0)

        # TreeView de etiquetas
        etiquetas_cols = ('ID', 'Nombre', 'Color', 'Tipo', 'Usos')
        self.etiquetas_tree = ttk.Treeview(left_panel, columns=etiquetas_cols, show='headings', selectmode='browse')
        
        self.etiquetas_tree.heading('ID', text='ID')
        self.etiquetas_tree.heading('Nombre', text='Nombre')
        self.etiquetas_tree.heading('Color', text='Color')
        self.etiquetas_tree.heading('Tipo', text='Tipo')
        self.etiquetas_tree.heading('Usos', text='Usos')

        self.etiquetas_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.etiquetas_tree.column('Nombre', width=150, stretch=True)
        self.etiquetas_tree.column('Color', width=80, stretch=tk.NO)
        self.etiquetas_tree.column('Tipo', width=80, stretch=tk.NO)
        self.etiquetas_tree.column('Usos', width=60, stretch=tk.NO, anchor=tk.CENTER)

        # Scrollbars para etiquetas
        etiquetas_scrollbar_y = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, command=self.etiquetas_tree.yview)
        self.etiquetas_tree.configure(yscrollcommand=etiquetas_scrollbar_y.set)
        etiquetas_scrollbar_y.grid(row=0, column=1, sticky='ns')

        self.etiquetas_tree.grid(row=0, column=0, sticky='nsew')

        # Bind para selección
        self.etiquetas_tree.bind('<<TreeviewSelect>>', self.on_etiqueta_select)

        # Botones de gestión
        buttons_frame = ttk.Frame(left_panel)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)

        self.add_etiqueta_btn = ttk.Button(buttons_frame, text="Nueva Etiqueta", command=self.open_etiqueta_dialog)
        self.add_etiqueta_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.edit_etiqueta_btn = ttk.Button(buttons_frame, text="Editar", command=self.edit_selected_etiqueta, state=tk.DISABLED)
        self.edit_etiqueta_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.delete_etiqueta_btn = ttk.Button(buttons_frame, text="Eliminar", command=self.delete_selected_etiqueta, state=tk.DISABLED)
        self.delete_etiqueta_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

        # --- Panel Derecho: Aplicación de Etiquetas ---
        right_panel = ttk.Frame(self)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=0)
        right_panel.rowconfigure(1, weight=1)
        right_panel.rowconfigure(2, weight=1)

        # Selector de entidad
        selector_frame = ttk.LabelFrame(right_panel, text="Aplicar Etiquetas", padding="5")
        selector_frame.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        selector_frame.columnconfigure(1, weight=1)

        ttk.Label(selector_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.entity_type_var = tk.StringVar(value="clientes")
        entity_combo = ttk.Combobox(selector_frame, textvariable=self.entity_type_var, 
                                   values=["clientes", "casos"], state="readonly")
        entity_combo.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        entity_combo.bind('<<ComboboxSelected>>', self.on_entity_type_change)

        ttk.Button(selector_frame, text="Cargar", command=self.load_entities).grid(row=0, column=2)

        # Lista de entidades (clientes/casos)
        entities_frame = ttk.LabelFrame(right_panel, text="Entidades", padding="5")
        entities_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 5))
        entities_frame.columnconfigure(0, weight=1)
        entities_frame.rowconfigure(0, weight=1)

        entities_cols = ('ID', 'Nombre', 'Etiquetas Actuales')
        self.entities_tree = ttk.Treeview(entities_frame, columns=entities_cols, show='headings', selectmode='browse')
        
        self.entities_tree.heading('ID', text='ID')
        self.entities_tree.heading('Nombre', text='Nombre')
        self.entities_tree.heading('Etiquetas Actuales', text='Etiquetas Actuales')

        self.entities_tree.column('ID', width=40, stretch=tk.NO, anchor=tk.CENTER)
        self.entities_tree.column('Nombre', width=200, stretch=True)
        self.entities_tree.column('Etiquetas Actuales', width=200, stretch=True)

        entities_scrollbar_y = ttk.Scrollbar(entities_frame, orient=tk.VERTICAL, command=self.entities_tree.yview)
        self.entities_tree.configure(yscrollcommand=entities_scrollbar_y.set)
        entities_scrollbar_y.grid(row=0, column=1, sticky='ns')

        self.entities_tree.grid(row=0, column=0, sticky='nsew')

        # Aplicación de etiquetas
        apply_frame = ttk.LabelFrame(right_panel, text="Aplicar/Quitar Etiquetas", padding="5")
        apply_frame.grid(row=2, column=0, sticky='nsew')
        apply_frame.columnconfigure(0, weight=1)

        # Lista de etiquetas disponibles
        ttk.Label(apply_frame, text="Etiquetas disponibles:").pack(anchor=tk.W)
        
        available_frame = ttk.Frame(apply_frame)
        available_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        available_frame.columnconfigure(0, weight=1)
        available_frame.rowconfigure(0, weight=1)

        self.available_listbox = tk.Listbox(available_frame, selectmode=tk.MULTIPLE)
        self.available_listbox.grid(row=0, column=0, sticky='nsew')

        available_scroll = ttk.Scrollbar(available_frame, orient=tk.VERTICAL, command=self.available_listbox.yview)
        self.available_listbox.configure(yscrollcommand=available_scroll.set)
        available_scroll.grid(row=0, column=1, sticky='ns')

        # Botones de aplicación
        apply_buttons_frame = ttk.Frame(apply_frame)
        apply_buttons_frame.pack(fill=tk.X)
        apply_buttons_frame.columnconfigure(0, weight=1)
        apply_buttons_frame.columnconfigure(1, weight=1)

        self.apply_btn = ttk.Button(apply_buttons_frame, text="Aplicar Etiquetas", 
                                   command=self.apply_selected_etiquetas, state=tk.DISABLED)
        self.apply_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.remove_btn = ttk.Button(apply_buttons_frame, text="Quitar Etiquetas", 
                                    command=self.remove_selected_etiquetas, state=tk.DISABLED)
        self.remove_btn.grid(row=0, column=1, sticky='ew', padx=(5, 0))

        # Bind para selección de entidades
        self.entities_tree.bind('<<TreeviewSelect>>', self.on_entity_select)

        # Cargar datos iniciales
        self.load_etiquetas()
        self.load_available_etiquetas()

    def load_etiquetas(self):
        """Cargar todas las etiquetas en el TreeView"""
        # Limpiar TreeView
        for item in self.etiquetas_tree.get_children():
            self.etiquetas_tree.delete(item)

        try:
            etiquetas = self.db_crm.get_all_etiquetas()
            for etiqueta in etiquetas:
                # Contar usos de la etiqueta
                usos = self._count_etiqueta_usage(etiqueta['nombre'])
                
                self.etiquetas_tree.insert('', 'end', values=(
                    etiqueta['id'],
                    etiqueta['nombre'],
                    etiqueta['color'],
                    etiqueta['tipo'],
                    usos
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar etiquetas: {e}")

    def _count_etiqueta_usage(self, etiqueta_nombre):
        """Contar cuántas veces se usa una etiqueta"""
        try:
            count = 0
            # Contar en clientes
            clientes = self.db_crm.get_clients()
            for cliente in clientes:
                etiquetas_str = cliente.get('etiquetas', '')
                if etiquetas_str and etiqueta_nombre in etiquetas_str.split(','):
                    count += 1
            
            # Contar en casos
            casos = self.db_crm.get_all_cases()
            for caso in casos:
                etiquetas_str = caso.get('etiquetas', '')
                if etiquetas_str and etiqueta_nombre in etiquetas_str.split(','):
                    count += 1
                    
            return count
        except:
            return 0

    def load_available_etiquetas(self):
        """Cargar etiquetas disponibles en el Listbox"""
        self.available_listbox.delete(0, tk.END)
        try:
            etiquetas = self.db_crm.get_all_etiquetas()
            for etiqueta in etiquetas:
                display_text = f"{etiqueta['nombre']} ({etiqueta['tipo']}) - {etiqueta['color']}"
                self.available_listbox.insert(tk.END, display_text)
        except Exception as e:
            print(f"Error al cargar etiquetas disponibles: {e}")

    def on_entity_type_change(self, event):
        """Manejar cambio de tipo de entidad"""
        self.entities_tree.delete(*self.entities_tree.get_children())
        self.disable_apply_buttons()

    def load_entities(self):
        """Cargar entidades según el tipo seleccionado"""
        # Limpiar TreeView
        for item in self.entities_tree.get_children():
            self.entities_tree.delete(item)

        entity_type = self.entity_type_var.get()
        
        try:
            if entity_type == "clientes":
                entities = self.db_crm.get_clients()
                for entity in entities:
                    self.entities_tree.insert('', 'end', values=(
                        entity['id'],
                        entity.get('nombre', ''),
                        entity.get('etiquetas', 'Sin etiquetas')
                    ))
            elif entity_type == "casos":
                entities = self.db_crm.get_all_cases()
                for entity in entities:
                    # Obtener nombre del cliente para mostrar más información
                    cliente_nombre = "Cliente desconocido"
                    if entity.get('cliente_id'):
                        try:
                            cliente = self.db_crm.get_client_by_id(entity['cliente_id'])
                            if cliente:
                                cliente_nombre = cliente.get('nombre', 'Sin nombre')
                        except:
                            pass
                    
                    display_name = f"{entity.get('caratula', 'Sin carátula')} ({cliente_nombre})"
                    self.entities_tree.insert('', 'end', values=(
                        entity['id'],
                        display_name,
                        entity.get('etiquetas', 'Sin etiquetas')
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar {entity_type}: {e}")

    def on_etiqueta_select(self, event):
        """Manejar selección de etiqueta"""
        selected_items = self.etiquetas_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            self.selected_etiqueta_id = self.etiquetas_tree.item(selected_item, 'values')[0]
            self.enable_etiqueta_buttons()
        else:
            self.selected_etiqueta_id = None
            self.disable_etiqueta_buttons()

    def on_entity_select(self, event):
        """Manejar selección de entidad"""
        selected_items = self.entities_tree.selection()
        if selected_items:
            self.enable_apply_buttons()
        else:
            self.disable_apply_buttons()

    def enable_etiqueta_buttons(self):
        """Habilitar botones de etiqueta"""
        self.edit_etiqueta_btn.config(state=tk.NORMAL)
        self.delete_etiqueta_btn.config(state=tk.NORMAL)

    def disable_etiqueta_buttons(self):
        """Deshabilitar botones de etiqueta"""
        self.edit_etiqueta_btn.config(state=tk.DISABLED)
        self.delete_etiqueta_btn.config(state=tk.DISABLED)

    def enable_apply_buttons(self):
        """Habilitar botones de aplicación"""
        self.apply_btn.config(state=tk.NORMAL)
        self.remove_btn.config(state=tk.NORMAL)

    def disable_apply_buttons(self):
        """Deshabilitar botones de aplicación"""
        self.apply_btn.config(state=tk.DISABLED)
        self.remove_btn.config(state=tk.DISABLED)

    def open_etiqueta_dialog(self, etiqueta_id=None):
        """Abrir diálogo para crear o editar etiqueta"""
        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Nueva Etiqueta" if not etiqueta_id else "Editar Etiqueta")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables para los campos
        nombre_var = tk.StringVar()
        descripcion_var = tk.StringVar()
        color_var = tk.StringVar(value="#3498db")
        tipo_var = tk.StringVar(value="general")

        # Si estamos editando, cargar datos existentes
        if etiqueta_id:
            try:
                etiqueta_data = self.db_crm.get_etiqueta_by_id(etiqueta_id)
                if etiqueta_data:
                    nombre_var.set(etiqueta_data.get('nombre', ''))
                    descripcion_var.set(etiqueta_data.get('descripcion', ''))
                    color_var.set(etiqueta_data.get('color', '#3498db'))
                    tipo_var.set(etiqueta_data.get('tipo', 'general'))
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar datos de la etiqueta: {e}")
                dialog.destroy()
                return

        # Campos del formulario
        row = 0

        ttk.Label(main_frame, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        nombre_entry = ttk.Entry(main_frame, textvariable=nombre_var, width=30)
        nombre_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Descripción:").grid(row=row, column=0, sticky=tk.W, pady=5)
        descripcion_entry = ttk.Entry(main_frame, textvariable=descripcion_var, width=30)
        descripcion_entry.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Tipo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var, 
                                 values=["general", "estado", "prioridad", "categoria"], state="readonly")
        tipo_combo.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        row += 1

        ttk.Label(main_frame, text="Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        color_frame = ttk.Frame(main_frame)
        color_frame.grid(row=row, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        color_frame.columnconfigure(0, weight=1)

        color_entry = ttk.Entry(color_frame, textvariable=color_var, width=20)
        color_entry.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))

        # Botones de colores predefinidos
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c", "#34495e", "#e67e22"]
        color_buttons_frame = ttk.Frame(main_frame)
        color_buttons_frame.grid(row=row+1, column=0, columnspan=2, pady=10)

        for i, color in enumerate(colors):
            btn = tk.Button(color_buttons_frame, bg=color, width=3, height=1,
                           command=lambda c=color: color_var.set(c))
            btn.grid(row=0, column=i, padx=2)

        row += 2

        # Configurar expansión de columnas
        main_frame.columnconfigure(1, weight=1)

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self.save_etiqueta(etiqueta_id, nombre_var.get(), descripcion_var.get(),
                                                    color_var.get(), tipo_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        # Focus en el primer campo
        nombre_entry.focus_set()

    def save_etiqueta(self, etiqueta_id, nombre, descripcion, color, tipo, dialog):
        """Guardar etiqueta (crear o actualizar)"""
        if not nombre.strip():
            messagebox.showwarning("Campo Requerido", "El nombre de la etiqueta es obligatorio.")
            return

        try:
            if etiqueta_id:  # Editar etiqueta existente
                self.db_crm.update_etiqueta(etiqueta_id, nombre, descripcion, color, tipo)
                messagebox.showinfo("Éxito", "Etiqueta actualizada correctamente.")
            else:  # Crear nueva etiqueta
                self.db_crm.add_etiqueta(nombre, descripcion, color, tipo)
                messagebox.showinfo("Éxito", "Etiqueta creada correctamente.")

            dialog.destroy()
            self.load_etiquetas()  # Recargar la lista
            self.load_available_etiquetas()  # Recargar lista disponible
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar etiqueta: {e}")

    def edit_selected_etiqueta(self):
        """Editar la etiqueta seleccionada"""
        if not self.selected_etiqueta_id:
            messagebox.showwarning("Sin Selección", "Seleccione una etiqueta para editar.")
            return
        self.open_etiqueta_dialog(self.selected_etiqueta_id)

    def delete_selected_etiqueta(self):
        """Eliminar la etiqueta seleccionada"""
        if not self.selected_etiqueta_id:
            messagebox.showwarning("Sin Selección", "Seleccione una etiqueta para eliminar.")
            return

        # Confirmar eliminación
        response = messagebox.askyesno("Confirmar Eliminación", 
                                     "¿Está seguro de que desea eliminar esta etiqueta?\n\n"
                                     "Se eliminará de todos los clientes y casos que la tengan asignada.")

        if response:
            try:
                self.db_crm.delete_etiqueta(self.selected_etiqueta_id)
                messagebox.showinfo("Éxito", "Etiqueta eliminada correctamente.")
                self.load_etiquetas()  # Recargar la lista
                self.load_available_etiquetas()  # Recargar lista disponible
                self.load_entities()  # Recargar entidades para actualizar etiquetas
                self.selected_etiqueta_id = None
                self.disable_etiqueta_buttons()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar etiqueta: {e}")

    def apply_selected_etiquetas(self):
        """Aplicar etiquetas seleccionadas a la entidad seleccionada"""
        # Obtener entidad seleccionada
        selected_entities = self.entities_tree.selection()
        if not selected_entities:
            messagebox.showwarning("Sin Selección", "Seleccione una entidad para aplicar etiquetas.")
            return

        # Obtener etiquetas seleccionadas
        selected_etiquetas_indices = self.available_listbox.curselection()
        if not selected_etiquetas_indices:
            messagebox.showwarning("Sin Etiquetas", "Seleccione al menos una etiqueta para aplicar.")
            return

        try:
            entity_item = selected_entities[0]
            entity_id = self.entities_tree.item(entity_item, 'values')[0]
            entity_type = self.entity_type_var.get()

            # Obtener nombres de etiquetas seleccionadas
            etiquetas_to_add = []
            etiquetas = self.db_crm.get_all_etiquetas()
            for index in selected_etiquetas_indices:
                if index < len(etiquetas):
                    etiquetas_to_add.append(etiquetas[index]['nombre'])

            # Obtener etiquetas actuales de la entidad
            if entity_type == "clientes":
                entity_data = self.db_crm.get_client_by_id(entity_id)
            else:  # casos
                entity_data = self.db_crm.get_case_by_id(entity_id)

            if not entity_data:
                messagebox.showerror("Error", "No se pudo encontrar la entidad seleccionada.")
                return

            current_etiquetas = entity_data.get('etiquetas', '')
            current_etiquetas_list = [tag.strip() for tag in current_etiquetas.split(',') if tag.strip()]

            # Agregar nuevas etiquetas (evitar duplicados)
            for etiqueta in etiquetas_to_add:
                if etiqueta not in current_etiquetas_list:
                    current_etiquetas_list.append(etiqueta)

            # Actualizar entidad
            new_etiquetas_str = ', '.join(current_etiquetas_list)
            
            if entity_type == "clientes":
                self.db_crm.update_client_etiquetas(entity_id, new_etiquetas_str)
            else:  # casos
                self.db_crm.update_case_etiquetas(entity_id, new_etiquetas_str)

            messagebox.showinfo("Éxito", f"Etiquetas aplicadas correctamente a {entity_type[:-1]}.")
            self.load_entities()  # Recargar para mostrar cambios
            self.load_etiquetas()  # Recargar para actualizar contadores
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar etiquetas: {e}")

    def remove_selected_etiquetas(self):
        """Quitar etiquetas seleccionadas de la entidad seleccionada"""
        # Obtener entidad seleccionada
        selected_entities = self.entities_tree.selection()
        if not selected_entities:
            messagebox.showwarning("Sin Selección", "Seleccione una entidad para quitar etiquetas.")
            return

        # Obtener etiquetas seleccionadas
        selected_etiquetas_indices = self.available_listbox.curselection()
        if not selected_etiquetas_indices:
            messagebox.showwarning("Sin Etiquetas", "Seleccione al menos una etiqueta para quitar.")
            return

        try:
            entity_item = selected_entities[0]
            entity_id = self.entities_tree.item(entity_item, 'values')[0]
            entity_type = self.entity_type_var.get()

            # Obtener nombres de etiquetas seleccionadas
            etiquetas_to_remove = []
            etiquetas = self.db_crm.get_all_etiquetas()
            for index in selected_etiquetas_indices:
                if index < len(etiquetas):
                    etiquetas_to_remove.append(etiquetas[index]['nombre'])

            # Obtener etiquetas actuales de la entidad
            if entity_type == "clientes":
                entity_data = self.db_crm.get_client_by_id(entity_id)
            else:  # casos
                entity_data = self.db_crm.get_case_by_id(entity_id)

            if not entity_data:
                messagebox.showerror("Error", "No se pudo encontrar la entidad seleccionada.")
                return

            current_etiquetas = entity_data.get('etiquetas', '')
            current_etiquetas_list = [tag.strip() for tag in current_etiquetas.split(',') if tag.strip()]

            # Quitar etiquetas
            for etiqueta in etiquetas_to_remove:
                if etiqueta in current_etiquetas_list:
                    current_etiquetas_list.remove(etiqueta)

            # Actualizar entidad
            new_etiquetas_str = ', '.join(current_etiquetas_list)
            
            if entity_type == "clientes":
                self.db_crm.update_client_etiquetas(entity_id, new_etiquetas_str)
            else:  # casos
                self.db_crm.update_case_etiquetas(entity_id, new_etiquetas_str)

            messagebox.showinfo("Éxito", f"Etiquetas quitadas correctamente de {entity_type[:-1]}.")
            self.load_entities()  # Recargar para mostrar cambios
            self.load_etiquetas()  # Recargar para actualizar contadores
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al quitar etiquetas: {e}")

    def refresh_data(self):
        """Refrescar los datos del módulo"""
        self.load_etiquetas()
        self.load_available_etiquetas()
        if hasattr(self, 'entities_tree') and self.entities_tree.get_children():
            self.load_entities()

    def get_selected_etiqueta(self):
        """Obtener la etiqueta seleccionada actualmente"""
        if self.selected_etiqueta_id:
            try:
                return self.db_crm.get_etiqueta_by_id(self.selected_etiqueta_id)
            except:
                return None
        return None
