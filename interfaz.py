import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt
import re
from datetime import datetime

ARCHIVO_REGISTRO = "registro.txt"
ARCHIVO_PROYECTOS = "proyetos.txt"

# ====== FUNCIONES DE UTILIDAD ======
def valida_contraseña(contraseña):
    if len(contraseña) < 8:
        return False, "Debe tener mínimo 8 caracteres"
    if not re.search(r"[A-Z]", contraseña):
        return False, "Debe tener al menos una letra mayúscula."
    if not re.search(r"[a-z]", contraseña):
        return False, "Debe tener al menos una letra minúscula."
    if not re.search(r"[0-9]", contraseña):
        return False, "Debe tener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contraseña):
        return False, "Debe tener al menos un caracter especial."
    return True, ""

def leer_usuarios():
    try:
        with open(ARCHIVO_REGISTRO, "r") as f:
            return [line.strip().split(",") for line in f if line.strip()]
    except FileNotFoundError:
        return []

def guardar_usuario(nombre, apellido, cedula, correo, contraseña, rol):
    salt = bcrypt.gensalt()
    hash_str = bcrypt.hashpw(contraseña.encode('utf-8'), salt).decode('utf-8')
    with open(ARCHIVO_REGISTRO, "a") as f:
        f.write(f"{nombre},{apellido},{cedula},{correo},{hash_str},{rol}\n")

def guardar_proyecto(nombre, costo, fecha_inicio, fecha_fin, tareas):
    with open(ARCHIVO_PROYECTOS, "a") as f:
        for tarea in tareas:
            f.write(f"{nombre},{costo},{fecha_inicio},{fecha_fin},{tarea['nombre']},{tarea['descripcion']},{tarea['responsable']}\n")

# ====== INTERFAZ ======
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Clínica Los Gemelos")
        self.geometry("500x400")
        self.usuario_actual = None
        self.mostrar_login()

    def limpiar_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_frame()
        tk.Label(self, text="Inicio de Sesión", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="Correo:").pack()
        correo_entry = tk.Entry(self)
        correo_entry.pack()

        tk.Label(self, text="Contraseña:").pack()
        contr_entry = tk.Entry(self, show="*")
        contr_entry.pack()

        def intentar_login():
            correo = correo_entry.get()
            contraseña = contr_entry.get()
            for datos in leer_usuarios():
                if correo == datos[3] and bcrypt.checkpw(contraseña.encode('utf-8'), datos[4].encode('utf-8')):
                    self.usuario_actual = datos
                    messagebox.showinfo("Éxito", f"Bienvenido {datos[0]}")
                    if datos[5] == "Administrador":
                        self.menu_admin()
                    else:
                        self.menu_estudiante()
                    return
            messagebox.showerror("Error", "Credenciales inválidas")

        tk.Button(self, text="Ingresar", command=intentar_login).pack(pady=10)
        tk.Button(self, text="Registrar usuario", command=self.registrar_usuario).pack()

    def registrar_usuario(self):
        self.limpiar_frame()
        tk.Label(self, text="Registro de Usuario", font=("Arial", 16)).pack(pady=10)

        campos = {}
        for campo in ["Nombre", "Apellido", "Cédula", "Correo", "Contraseña"]:
            tk.Label(self, text=campo + ":").pack()
            e = tk.Entry(self, show="*" if campo == "Contraseña" else "")
            e.pack()
            campos[campo] = e

        rol_var = tk.StringVar(value="Administrador")
        tk.OptionMenu(self, rol_var, "Administrador", "Estudiante").pack()

        def guardar():
            nombre = campos["Nombre"].get()
            apellido = campos["Apellido"].get()
            cedula = campos["Cédula"].get()
            correo = campos["Correo"].get()
            contraseña = campos["Contraseña"].get()
            es_valida, mensaje = valida_contraseña(contraseña)
            if not es_valida:
                messagebox.showerror("Error", mensaje)
                return
            guardar_usuario(nombre, apellido, cedula, correo, contraseña, rol_var.get())
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            self.mostrar_login()

        tk.Button(self, text="Guardar", command=guardar).pack(pady=10)
        tk.Button(self, text="Volver", command=self.mostrar_login).pack()

    def menu_admin(self):
        self.limpiar_frame()
        tk.Label(self, text="Menú Administrador", font=("Arial", 16)).pack(pady=10)
        tk.Button(self, text="Registrar Usuario", command=self.registrar_usuario).pack()
        tk.Button(self, text="Cerrar sesión", command=self.mostrar_login).pack(pady=10)

    def menu_estudiante(self):
        self.limpiar_frame()
        tk.Label(self, text="Menú Estudiante", font=("Arial", 16)).pack(pady=10)
        tk.Button(self, text="Crear Proyecto", command=self.crear_proyecto).pack()
        tk.Button(self, text="Cerrar sesión", command=self.mostrar_login).pack(pady=10)

    def crear_proyecto(self):
        self.limpiar_frame()
        tk.Label(self, text="Crear Proyecto", font=("Arial", 16)).pack(pady=10)

        campos = {}
        for campo in ["Nombre", "Costo", "Fecha inicio (dd/mm/yyyy)", "Fecha fin (dd/mm/yyyy)"]:
            tk.Label(self, text=campo + ":").pack()
            e = tk.Entry(self)
            e.pack()
            campos[campo] = e

        tareas = []

        def agregar_tarea():
            top = tk.Toplevel(self)
            top.title("Agregar tarea")
            tk.Label(top, text="Nombre tarea:").pack()
            tarea_nom = tk.Entry(top)
            tarea_nom.pack()
            tk.Label(top, text="Descripción:").pack()
            tarea_desc = tk.Entry(top)
            tarea_desc.pack()
            tk.Label(top, text="Cédula responsable:").pack()
            tarea_resp = tk.Entry(top)
            tarea_resp.pack()

            def guardar_tarea():
                tareas.append({
                    "nombre": tarea_nom.get(),
                    "descripcion": tarea_desc.get(),
                    "responsable": tarea_resp.get()
                })
                top.destroy()

            tk.Button(top, text="Guardar", command=guardar_tarea).pack()

        tk.Button(self, text="Agregar tarea", command=agregar_tarea).pack()
        tk.Button(self, text="Guardar proyecto", command=lambda: self.guardar_proyecto_ui(campos, tareas)).pack(pady=10)
        tk.Button(self, text="Volver", command=self.menu_estudiante).pack()

    def guardar_proyecto_ui(self, campos, tareas):
        guardar_proyecto(
            campos["Nombre"].get(),
            campos["Costo"].get(),
            campos["Fecha inicio (dd/mm/yyyy)"].get(),
            campos["Fecha fin (dd/mm/yyyy)"].get(),
            tareas
        )
        messagebox.showinfo("Éxito", "Proyecto guardado correctamente")
        self.menu_estudiante()

if __name__ == "__main__":
    App().mainloop()
