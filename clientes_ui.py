# clientes_ui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ClientesTab(ttk.Frame):
    def __init__(self, parent, app_controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.app_controller = app_controller
        self.db_crm = self.app_controller.db_crm
        self.selected_client = None
        self._create_widgets()

    def _create_widgets(self):
        # Configurar el frame principal
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Frame principal para clientes
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        main_frame.columnconfigure(0, weight=0, minsize=350)
        main_frame.rowconfigure(0, weight=1)  # Lista de clientes
        main_frame.rowconfigure(1, weight=0)  # Botones
        main_frame.rowconfigure(2, weight=0)  # Detalles

        # --- Lista de Clientes ---
        client_list_frame = ttk.LabelFrame(main_frame, text="Lista de Clientes", padding="5")
        client_list_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        client_list_frame.columnconfigure(0, weight=1)
        client_list_frame.rowconfigure(0, weight=1, minsize=300)

        # TreeView de clientes
        client_cols = ('ID', 'Nombre') #, 'Email', 'WhatsApp', 'Etiquetas')
        self.client_tree = ttk.Treeview(client_list_frame, columns=client_cols, show='headings', selectmode='browse')
        
        self.client_tree.heading('ID', text='ID')
        self.client_tree.heading('Nombre', text='Nombre Completo')
        #self.client_tree.heading('Email', text='Email')
        #self.client_tree.heading('WhatsApp', text='WhatsApp')
        #self.client_tree.heading('Etiquetas', text='Etiquetas')

        self.client_tree.column('ID', width=50, stretch=tk.NO, anchor=tk.CENTER)
        self.client_tree.column('Nombre', width=250, stretch=True)
        #self.client_tree.column('Email', width=200, stretch=True)
        #self.client_tree.column('WhatsApp', width=120, stretch=tk.NO)
        #self.client_tree.column('Etiquetas', width=150, stretch=True)

        # Scrollbars para la lista de clientes
        client_scrollbar_y = ttk.Scrollbar(client_list_frame, orient=tk.VERTICAL, command=self.client_tree.yview)
        self.client_tree.configure(yscrollcommand=client_scrollbar_y.set)
        client_scrollbar_y.grid(row=0, column=1, sticky='ns')

        client_scrollbar_x = ttk.Scrollbar(client_list_frame, orient=tk.HORIZONTAL, command=self.client_tree.xview)
        self.client_tree.configure(xscrollcommand=client_scrollbar_x.set)
        client_scrollbar_x.grid(row=1, column=0, sticky='ew')

        self.client_tree.grid(row=0, column=0, sticky='nsew')

        # Bind para selección de cliente
        self.client_tree.bind('<<TreeviewSelect>>', self.on_client_select)

        # --- Botones de Acción ---
        client_buttons_frame = ttk.Frame(main_frame)
        client_buttons_frame.grid(row=1, column=0, sticky='ew', pady=5)
        client_buttons_frame.columnconfigure(0, weight=1)
        client_buttons_frame.columnconfigure(1, weight=1)
        client_buttons_frame.columnconfigure(2, weight=1)

        self.add_client_btn = ttk.Button(client_buttons_frame, text="ALTA", command=lambda: self.open_client_dialog())
        self.add_client_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.edit_client_btn = ttk.Button(client_buttons_frame, text="MODIFICAR", command=lambda: self.open_client_dialog(self.selected_client['id'] if self.selected_client else None), state=tk.DISABLED)
        self.edit_client_btn.grid(row=0, column=1, sticky='ew', padx=5)

        self.delete_client_btn = ttk.Button(client_buttons_frame, text="ELIMINAR", command=self.delete_client, state=tk.DISABLED)
        self.delete_client_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

        # --- Detalles del Cliente ---
        client_details_frame = ttk.LabelFrame(main_frame, text="Detalles del Cliente", padding="5")
        client_details_frame.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        client_details_frame.columnconfigure(1, weight=1)

        ttk.Label(client_details_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=1, padx=5)
        self.client_detail_name_lbl = ttk.Label(client_details_frame, text="", wraplength=300)
        self.client_detail_name_lbl.grid(row=0, column=1, sticky=tk.EW, pady=1, padx=5)

        ttk.Label(client_details_frame, text="Dirección:").grid(row=1, column=0, sticky=tk.W, pady=1, padx=5)
        self.client_detail_address_lbl = ttk.Label(client_details_frame, text="", wraplength=200)
        self.client_detail_address_lbl.grid(row=1, column=1, sticky=tk.EW, pady=1, padx=5)

        ttk.Label(client_details_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=1, padx=5)
        self.client_detail_email_lbl = ttk.Label(client_details_frame, text="", wraplength=200)
        self.client_detail_email_lbl.grid(row=2, column=1, sticky=tk.EW, pady=1, padx=5)

        ttk.Label(client_details_frame, text="WhatsApp:").grid(row=3, column=0, sticky=tk.W, pady=1, padx=5)
        self.client_detail_whatsapp_lbl = ttk.Label(client_details_frame, text="")
        self.client_detail_whatsapp_lbl.grid(row=3, column=1, sticky=tk.EW, pady=1, padx=5)

        ttk.Label(client_details_frame, text="Etiquetas:").grid(row=4, column=0, sticky=tk.W, pady=1, padx=5)
        self.client_detail_etiquetas_lbl = ttk.Label(client_details_frame, text="", wraplength=300)
        self.client_detail_etiquetas_lbl.grid(row=4, column=1, sticky=tk.EW, pady=1, padx=5)

    def load_clients(self):
        """Cargar la lista de clientes en el TreeView"""
        # Limpiar el TreeView
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        try:
            clients = self.db_crm.get_clients()
            for client in clients:
                # Insertar cliente en el TreeView
                self.client_tree.insert('', 'end', values=(
                    client['id'],
                    client.get('nombre', ''),
                    #client.get('email', ''),
                    #client.get('whatsapp', ''),
                    #client.get('etiquetas', '')
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")

    def on_client_select(self, event):
        """Manejar la selección de un cliente"""
        selected_items = self.client_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            client_id = self.client_tree.item(selected_item, 'values')[0]
            
            try:
                client_data = self.db_crm.get_client_by_id(client_id)
                if client_data:
                    self.selected_client = client_data
                    self.display_client_details(client_data)
                    self.enable_client_buttons()
                    # Notificar al controlador principal sobre la selección
                    if hasattr(self.app_controller, 'on_client_selected'):
                        self.app_controller.on_client_selected(client_data)
                else:
                    self.clear_client_details()
                    self.disable_client_buttons()
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener detalles del cliente: {e}")
        else:
            self.selected_client = None
            self.clear_client_details()
            self.disable_client_buttons()

    def display_client_details(self, client_data):
        """Mostrar los detalles del cliente seleccionado"""
        if client_data:
            self.client_detail_name_lbl.config(text=client_data.get('nombre', 'N/A'))
            self.client_detail_address_lbl.config(text=client_data.get('direccion', 'N/A'))
            self.client_detail_email_lbl.config(text=client_data.get('email', 'N/A'))
            self.client_detail_whatsapp_lbl.config(text=client_data.get('whatsapp', 'N/A'))
            self.client_detail_etiquetas_lbl.config(text=client_data.get('etiquetas', 'Sin etiquetas'))

    def clear_client_details(self):
        """Limpiar los detalles del cliente"""
        self.client_detail_name_lbl.config(text="")
        self.client_detail_address_lbl.config(text="")
        self.client_detail_email_lbl.config(text="")
        self.client_detail_whatsapp_lbl.config(text="")
        self.client_detail_etiquetas_lbl.config(text="")

    def enable_client_buttons(self):
        """Habilitar botones cuando hay un cliente seleccionado"""
        self.edit_client_btn.config(state=tk.NORMAL)
        self.delete_client_btn.config(state=tk.NORMAL)

    def disable_client_buttons(self):
        """Deshabilitar botones cuando no hay cliente seleccionado"""
        self.edit_client_btn.config(state=tk.DISABLED)
        self.delete_client_btn.config(state=tk.DISABLED)

    def open_client_dialog(self, client_id=None):
        """Abrir diálogo para crear o editar cliente"""
        dialog = tk.Toplevel(self.app_controller.root)
        dialog.title("Alta/Edición de Cliente")
        dialog.transient(self.app_controller.root)
        dialog.grab_set()
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Variables para los campos
        nombre_var = tk.StringVar()
        direccion_var = tk.StringVar()
        email_var = tk.StringVar()
        whatsapp_var = tk.StringVar()
        etiquetas_var = tk.StringVar()

        # Si estamos editando, cargar datos existentes
        if client_id:
            try:
                client_data = self.db_crm.get_client_by_id(client_id)
                if client_data:
                    nombre_var.set(client_data.get('nombre', ''))
                    direccion_var.set(client_data.get('direccion', ''))
                    email_var.set(client_data.get('email', ''))
                    whatsapp_var.set(client_data.get('whatsapp', ''))
                    etiquetas_var.set(client_data.get('etiquetas', ''))
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar datos del cliente: {e}")
                dialog.destroy()
                return

        # Campos del formulario
        ttk.Label(main_frame, text="Nombre Completo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        nombre_entry = ttk.Entry(main_frame, textvariable=nombre_var, width=40)
        nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Dirección:").grid(row=1, column=0, sticky=tk.W, pady=5)
        direccion_entry = ttk.Entry(main_frame, textvariable=direccion_var, width=40)
        direccion_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="WhatsApp:").grid(row=3, column=0, sticky=tk.W, pady=5)
        whatsapp_entry = ttk.Entry(main_frame, textvariable=whatsapp_var, width=40)
        whatsapp_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Etiquetas:").grid(row=4, column=0, sticky=tk.W, pady=5)
        etiquetas_entry = ttk.Entry(main_frame, textvariable=etiquetas_var, width=40)
        etiquetas_entry.grid(row=4, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="(Separadas por comas)", font=('', 8)).grid(row=5, column=1, sticky=tk.W, padx=(10, 0))

        # Configurar expansión de columnas
        main_frame.columnconfigure(1, weight=1)

        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(buttons_frame, text="Guardar", 
                  command=lambda: self.save_client(client_id, nombre_var.get(), direccion_var.get(), 
                                                  email_var.get(), whatsapp_var.get(), etiquetas_var.get(), dialog)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT)

        # Focus en el primer campo
        nombre_entry.focus_set()

    def save_client(self, client_id, nombre, direccion, email, whatsapp, etiquetas_str, dialog):
        """Guardar cliente (crear o actualizar)"""
        if not nombre.strip():
            messagebox.showwarning("Campo Requerido", "El nombre del cliente es obligatorio.")
            return

        try:
            if client_id:  # Editar cliente existente
                self.db_crm.update_client(client_id, nombre, direccion, email, whatsapp, etiquetas_str)
                messagebox.showinfo("Éxito", "Cliente actualizado correctamente.")
            else:  # Crear nuevo cliente
                self.db_crm.add_client(nombre, direccion, email, whatsapp, etiquetas_str)
                messagebox.showinfo("Éxito", "Cliente creado correctamente.")

            dialog.destroy()
            self.load_clients()  # Recargar la lista
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {e}")

    def delete_client(self):
        """Eliminar el cliente seleccionado"""
        if not self.selected_client:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un cliente para eliminar.")
            return

        # Confirmar eliminación
        response = messagebox.askyesno("Confirmar Eliminación", 
                                     f"¿Está seguro de que desea eliminar el cliente '{self.selected_client['nombre']}'?\n\n"
                                     "ADVERTENCIA: Se eliminarán también todos los casos asociados a este cliente.")

        if response:
            try:
                self.db_crm.delete_client(self.selected_client['id'])
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente.")
                self.load_clients()  # Recargar la lista
                self.clear_client_details()
                self.disable_client_buttons()
                self.selected_client = None
                
                # Notificar al controlador principal
                if hasattr(self.app_controller, 'on_client_deleted'):
                    self.app_controller.on_client_deleted()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {e}")

    def refresh_data(self):
        """Refrescar los datos del módulo"""
        self.load_clients()
        if self.selected_client:
            # Intentar mantener la selección actual
            try:
                client_data = self.db_crm.get_client_by_id(self.selected_client['id'])
                if client_data:
                    self.selected_client = client_data
                    self.display_client_details(client_data)
                else:
                    self.selected_client = None
                    self.clear_client_details()
                    self.disable_client_buttons()
            except:
                self.selected_client = None
                self.clear_client_details()
                self.disable_client_buttons()

    def get_selected_client(self):
        """Obtener el cliente seleccionado actualmente"""
        return self.selected_client
