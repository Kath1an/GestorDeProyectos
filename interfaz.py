import tkinter as tk
from tkinter import messagebox
import bcrypt

RUTA_USUARIOS = "registro.txt"  # tu archivo con usuarios: nombre,apellido,cedula,correo,hash,rol

# --------- Núcleo reusable: solo verifica credenciales ----------
def verificar_credenciales(correo: str, contrasena: str, ruta_archivo: str = RUTA_USUARIOS) -> bool:
    """
    Retorna True si el correo existe y el hash coincide con la contraseña.
    Formato esperado por línea: nombre,apellido,cedula,correo,hash,rol
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            for linea in f:
                datos = linea.strip().split(",")
                if len(datos) < 6:
                    continue
                correo_guardado = datos[3].strip()
                hash_guardado = datos[4].strip().encode("utf-8")
                if correo == correo_guardado:
                    return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado)
    except FileNotFoundError:
        # Si no existe el archivo, nadie puede iniciar sesión
        return False
    return False

# --------- GUI (Tkinter) ----------
def run_gui():
    inicio = tk.Tk()
    inicio.title("Gestor de Proyectos")
    inicio.geometry("600x360")

    # Tarjeta centrada
    frame = tk.Frame(inicio, bg="white", padx=24, pady=20, bd=1, relief="groove")
    frame.pack(expand=True)

    # Para llevar la cuenta de intentos solo en esta sesión GUI
    run_gui.intentos = 0

    def iniciar():
        correo = entrada_correo.get().strip()
        contrasena = entrada_contrasena.get()

        if not correo or not contrasena:
            messagebox.showwarning("Campos vacíos", "Completa correo y contraseña.")
            return

        ok = verificar_credenciales(correo, contrasena, RUTA_USUARIOS)
        if ok:
            # Limpia y muestra bienvenida
            for w in frame.winfo_children():
                w.destroy()
            tk.Label(frame, text=f"Bienvenido, {correo}", bg="white", font=("Arial", 16)).grid(row=0, column=0, padx=10, pady=20)
        else:
            run_gui.intentos += 1
            restantes = 3 - run_gui.intentos
            messagebox.showerror("Credenciales inválidas", f"Correo o contraseña incorrectos.\nIntentos restantes: {max(restantes,0)}")
            if run_gui.intentos >= 3:
                # Aquí podrías llamar a tu lógica de bloqueo si quieres
                messagebox.showwarning("Bloqueado", "Has excedido el número de intentos.")
                # Deshabilitar botón para simular bloqueo
                btn_iniciar.config(state="disabled")

    # --- Widgets ---
    tk.Label(frame, text="Correo:", bg="white").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entrada_correo = tk.Entry(frame, width=30)
    entrada_correo.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame, text="Contraseña:", bg="white").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entrada_contrasena = tk.Entry(frame, show="*", width=30)
    entrada_contrasena.grid(row=1, column=1, padx=10, pady=10)

    btn_iniciar = tk.Button(frame, text="Iniciar sesión", command=iniciar)
    btn_iniciar.grid(row=2, column=0, padx=10, pady=15, sticky="e")

    btn_recuperar = tk.Button(frame, text="Recuperar contraseña", command=lambda: messagebox.showinfo("Recuperar", "Aquí iría tu flujo de recuperación"))
    btn_recuperar.grid(row=2, column=1, padx=10, pady=15, sticky="w")

    # Enter para iniciar
    inicio.bind("<Return>", lambda _e: iniciar())

    # Focus inicial
    entrada_correo.focus()

    inicio.mainloop()

# --------- Consola (si quieres seguir usando pwinput) ----------
def inicio_consola():
    import pwinput  # solo necesario en consola
    a = RUTA_USUARIOS
    intentos = 0
    print("======= CLINICA GEMELOS =======")
    while True:
        correo = input("Correo electronico: ").strip()
        contr_ingresada = pwinput.pwinput("Contraseña: ")
        autenticado = verificar_credenciales(correo, contr_ingresada, a)

        if autenticado:
            print("Inicio exitoso")
            break
        else:
            intentos += 1
            print("Credenciales inválidas")
            print("Intentos:", intentos)
            if intentos == 3:
                print("Has excedido el número de intentos")
                # bloqueo()  # aquí llamas tu lógica de bloqueo si la tienes
                break

# ----------------- ELIGE UNO -----------------
if __name__ == "__main__":
    # 1) Para GUI:
    run_gui()

    # 2) Si quieres probar consola, comenta la línea de arriba y descomenta esta:
    # inicio_consola()
