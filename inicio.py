import pwinput
import getpass
import bcrypt
import os
import json
import subprocess
import random
import smtplib
import ssl
from email.message import EmailMessage

ARCHIVO_REGISTRO = "registro.txt"
ARCHIVO_SESION = "sesion_actual.json"

# --- CONFIGURACIÓN DE CORREO ---
# Debes llenar estas variables con tus datos reales.
CORREO_REMITENTE = "cristhianmy@icloud.com"
CONTRASENA_REMITENTE = "zbbb-inqb-fqgv-hqpm"

def enviar_correo_con_codigo(destinatario, codigo):
    """Función para enviar un correo electrónico con el código de seguridad."""
    
    try:
        em = EmailMessage()
        em["From"] = CORREO_REMITENTE
        em["To"] = destinatario
        em["Subject"] = "Código de seguridad para cambiar tu contraseña"
        
        cuerpo_correo = f"""
        Hola,

        Para cambiar tu contraseña, usa el siguiente código de seguridad:

        {codigo}

        Si no solicitaste este cambio, ignora este correo.

        Saludos,
        Equipo de soporte.
        """
        em.set_content(cuerpo_correo, charset="utf-8")
        
        # Conexión segura usando STARTTLS en el puerto 587
        context = ssl.create_default_context()
        
        # --- Configuración para iCloud ---
        server_smtp = "smtp.mail.me.com"
        puerto_smtp = 587
        
        with smtplib.SMTP(server_smtp, puerto_smtp) as smtp:
            smtp.starttls(context=context)
            smtp.login(CORREO_REMITENTE, CONTRASENA_REMITENTE)
            smtp.sendmail(CORREO_REMITENTE, destinatario, em.as_string())
        
        print(f"✅ Se ha enviado un correo con un código de seguridad a {destinatario}.")
        return True
    
    except Exception as e:
        print(f"❌ Error al intentar enviar el correo. Por favor, revisa tus credenciales y configuración.")
        print(f"Detalles del error: {e}")
        return False

def bloqueo():
    print("Su cuenta ha sido bloqueada. Comuníquese con el administrador.")
    codigo = getpass.getpass("Ingrese el código de desbloqueo: ")
    while codigo != "1234":
        print("Código incorrecto.")
        codigo = getpass.getpass("Ingrese el código de desbloqueo: ")
    print("✅ Cuenta desbloqueada.")

def obtenerDatosUsuarioPorCorreo(correo):
    try:
        with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split(",")
                if len(datos) > 5 and datos[3].strip().lower() == correo.strip().lower():
                    return {
                        "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                        "cedula": datos[2].strip(),
                        "correo": datos[3].strip(),
                        "contraseña_hash": datos[4].strip(),
                        "rol": datos[5].strip()
                    }
    except FileNotFoundError:
        return None
    return None

def guardarSesion(datosUsuario):
    with open(ARCHIVO_SESION, "w", encoding="utf-8") as f:
        json.dump(datosUsuario, f, ensure_ascii=False, indent=2)

def iniciarSesion():
    intentos = 0
    print("--- Inicie sesión para continuar ---")
    while intentos < 3:
        correo = input("Correo electrónico: ")
        password = pwinput.pwinput("Contraseña: ")
        
        datosUsuario = obtenerDatosUsuarioPorCorreo(correo)
        
        if datosUsuario:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), datosUsuario['contraseña_hash'].encode('utf-8')):
                    print(f"✅ ¡Inicio de sesión exitoso, {datosUsuario['nombre']}!")
                    guardarSesion(datosUsuario)
                    
                    if datosUsuario['rol'].lower() == 'estudiante':
                        print("Redirigiendo al gestor de proyectos...")
                        subprocess.run(['python', 'estudiante.py'])
                    elif datosUsuario['rol'].lower() == 'administrador':
                        print("Redirigiendo al gestor de usuarios...")
                        subprocess.run(['python', 'administrador.py'])
                    else:
                        print("Rol de usuario no reconocido.")
                    return
                else:
                    print("❌ Credenciales inválidas.")
            except Exception:
                print("❌ Error de autenticación. Contacte a un administrador.")
        else:
            print("❌ Credenciales inválidas.")
        
        intentos += 1
        print(f"Intento {intentos} de 3.")
        if intentos == 3:
            print("Has excedido el número de intentos.")
            bloqueo()
            return

def cambiarContrasena():
    print("--- Cambiar Contraseña ---")
    
    try:
        with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print("No existe el archivo de usuarios.")
        return
    
    correo_destino = input("Ingrese el correo del usuario a quien desea cambiar la contraseña: ").strip()
    datosUsuario = obtenerDatosUsuarioPorCorreo(correo_destino)
    if not datosUsuario:
        print("❌ Correo no encontrado.")
        return
    
    codigo_seguridad = str(random.randint(100000, 999999))
    
    if not enviar_correo_con_codigo(datosUsuario['correo'], codigo_seguridad):
        return
    
    intentos_codigo = 0
    while intentos_codigo < 3:
        codigo_ingresado = input("Ingrese el código de seguridad: ")
        if codigo_ingresado == codigo_seguridad:
            break
        else:
            print("❌ Código de seguridad incorrecto.")
            intentos_codigo += 1
    
    if intentos_codigo == 3:
        print("Demasiados intentos. Proceso de cambio de contraseña cancelado.")
        return
    
    while True:
        nueva = pwinput.pwinput("Nueva contraseña: ")
        confirmar = pwinput.pwinput("Confirmar contraseña: ")
        if not nueva:
            print("La contraseña no puede estar vacía.")
            continue
        if len(nueva) < 8:
            print("La contraseña debe tener al menos 8 caracteres.")
            continue
        if nueva != confirmar:
            print("Las contraseñas no coinciden.")
            continue
        break
    
    salt = bcrypt.gensalt()
    hashBytes = bcrypt.hashpw(nueva.encode("utf-8"), salt)
    
    idxLinea = None
    for i, linea in enumerate(lineas):
        if linea.strip().split(",")[3].strip().lower() == correo_destino.lower():
            idxLinea = i
            break
    
    datos = lineas[idxLinea].strip().split(",")
    datos[4] = hashBytes.decode("utf-8")
    lineas[idxLinea] = ",".join(datos) + "\n"
    
    with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
        f.writelines(lineas)
    print("✅ Contraseña actualizada exitosamente.")

def menuPrincipal():
    print("=======CLINICA GEMELOS=======")
    print("\n=======Gestor de Proyectos=======\n")
    print("1.- Iniciar sesión")
    print("2.- Cambiar contraseña")
    eleccion = input("Elija una opción [1/2]: ")
    
    if eleccion == "1":
        iniciarSesion()
    elif eleccion == "2":
        cambiarContrasena()
    else:
        print("Opción no válida.")
        menuPrincipal()

if __name__ == "__main__":
    menuPrincipal()