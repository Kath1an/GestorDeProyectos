import pwinput
import bcrypt
import re
import os
import json
from datetime import datetime

ARCHIVO_USUARIOS = "registro.txt"
ARCHIVO_SESION = "sesion_actual.json"
ARCHIVO_PROYECTOS = "proyectos.json"

def validarSesion(rolRequerido):
    if not os.path.exists(ARCHIVO_SESION):
        print("❌ Error: No hay una sesión activa. Por favor, inicie sesión con 'inicio.py'.")
        return None
    try:
        with open(ARCHIVO_SESION, "r", encoding="utf-8") as f:
            sesion = json.load(f)
        if sesion.get('rol', '').lower() == rolRequerido.lower():
            return sesion
        else:
            print(f"❌ Acceso denegado. Rol '{sesion.get('rol')}' no tiene permiso para este módulo.")
            os.remove(ARCHIVO_SESION)
            return None
    except (json.JSONDecodeError, FileNotFoundError):
        print("❌ Error de sesión. Por favor, inicie sesión de nuevo.")
        return None

def validar_cedula(cedula: str) -> bool:
    return len(cedula) == 10 and cedula.isdigit()

def validar_contraseña(contraseña: str) -> tuple[bool, str]:
    if len(contraseña) < 8:
        return False, "Debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", contraseña):
        return False, "Debe tener al menos una letra en mayúscula."
    if not re.search(r"[a-z]", contraseña):
        return False, "Debe tener al menos una letra en minúscula."
    if not re.search(r"[0-9]", contraseña):
        return False, "Debe tener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contraseña):
        return False, "Debe tener al menos un carácter especial."
    return True, ""

def hash_contraseña(contraseña: str) -> str:
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return hash_bytes.decode('utf-8')

def registrar_usuario():
    print("\n--- Registro de Nuevo Usuario ---")
    nombre = input("Ingrese el nombre: ")
    apellido = input("Ingrese el apellido: ")
    while True:
        cedula = input("Ingrese la cédula de identidad: ")
        if validar_cedula(cedula):
            break
        print("Cédula inválida. Debe tener 10 dígitos.")
    correo = input("Ingrese el correo electrónico: ")
    while True:
        contraseña = pwinput.pwinput("Ingrese una contraseña: ")
        es_valida, mensaje = validar_contraseña(contraseña)
        if not es_valida:
            print("Contraseña inválida:", mensaje)
            continue
        confirmar = pwinput.pwinput("Vuelva a ingresar la contraseña: ")
        if contraseña == confirmar:
            hash_str = hash_contraseña(contraseña)
            break
        print("Las contraseñas no coinciden.")
    while True:
        rol_opcion = input("Elija un rol:\n1.- Administrador\n2.- Estudiante\nOpción [1/2]: ")
        if rol_opcion == "1":
            rol = "Administrador"
            break
        elif rol_opcion == "2":
            rol = "Estudiante"
            break
        print("Opción de rol inválida, vuelva a intentarlo.")
    with open(ARCHIVO_USUARIOS, "a") as archivo:
        archivo.write(f"{nombre},{apellido},{cedula},{correo},{hash_str},{rol}\n")
    print("✅ Usuario registrado exitosamente.")

def leer_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        return []
    with open(ARCHIVO_USUARIOS, "r") as archivo:
        lineas = archivo.readlines()
    usuarios = []
    for linea in lineas:
        nombre, apellido, cedula, correo, hash_str, rol = linea.strip().split(',')
        usuarios.append({
            "nombre": nombre,
            "apellido": apellido,
            "cedula": cedula,
            "correo": correo,
            "contraseña": hash_str,
            "rol": rol
        })
    return usuarios

def guardar_usuarios(usuarios: list):
    with open(ARCHIVO_USUARIOS, "w") as archivo:
        for u in usuarios:
            archivo.write(f"{u['nombre']},{u['apellido']},{u['cedula']},{u['correo']},{u['contraseña']},{u['rol']}\n")

def mostrar_usuarios():
    print("\n--- Lista de Usuarios ---")
    usuarios = leer_usuarios()
    if not usuarios:
        print("No hay usuarios registrados.")
        return
    for i, usuario in enumerate(usuarios, 1):
        print(f"--- Usuario {i} ---")
        print(f"  Nombre: {usuario['nombre']} {usuario['apellido']}")
        print(f"  Cédula: {usuario['cedula']}")
        print(f"  Correo: {usuario['correo']}")
        print(f"  Rol: {usuario['rol']}")
    print("-" * 25)

def actualizar_usuario():
    print("\n--- Actualizar Usuario ---")
    cedula_buscar = input("Ingrese la cédula del usuario a actualizar: ")
    usuarios = leer_usuarios()
    usuario_encontrado = None
    for i, usuario in enumerate(usuarios):
        if usuario["cedula"] == cedula_buscar:
            usuario_encontrado = usuario
            indice = i
            break
    if not usuario_encontrado:
        print("❌ Usuario no encontrado.")
        return
    print(f"Usuario encontrado: {usuario_encontrado['nombre']} {usuario_encontrado['apellido']}")
    print("Deje el campo vacío si no desea modificarlo.")
    nuevo_nombre = input(f"Nuevo nombre ({usuario_encontrado['nombre']}): ")
    if nuevo_nombre:
        usuario_encontrado['nombre'] = nuevo_nombre
    nuevo_apellido = input(f"Nuevo apellido ({usuario_encontrado['apellido']}): ")
    if nuevo_apellido:
        usuario_encontrado['apellido'] = nuevo_apellido
    nuevo_correo = input(f"Nuevo correo ({usuario_encontrado['correo']}): ")
    if nuevo_correo:
        usuario_encontrado['correo'] = nuevo_correo
    cambiar_contraseña = input("¿Desea cambiar la contraseña? (s/n): ").lower()
    if cambiar_contraseña == 's':
        while True:
            nueva_contraseña = pwinput.pwinput("Ingrese la nueva contraseña: ")
            es_valida, mensaje = validar_contraseña(nueva_contraseña)
            if not es_valida:
                print("Contraseña inválida:", mensaje)
                continue
            confirmar_nueva = pwinput.pwinput("Confirme la nueva contraseña: ")
            if nueva_contraseña == confirmar_nueva:
                usuario_encontrado['contraseña'] = hash_contraseña(nueva_contraseña)
                break
            print("Las contraseñas no coinciden.")
    usuarios[indice] = usuario_encontrado
    guardar_usuarios(usuarios)
    print("✅ Usuario actualizado exitosamente.")

def eliminar_usuario():
    print("\n--- Eliminar Usuario ---")
    cedula_eliminar = input("Ingrese la cédula del usuario a eliminar: ")
    usuarios = leer_usuarios()
    usuarios_filtrados = [u for u in usuarios if u['cedula'] != cedula_eliminar]
    if len(usuarios_filtrados) == len(usuarios):
        print("❌ Usuario no encontrado.")
    else:
        guardar_usuarios(usuarios_filtrados)
        print("✅ Usuario eliminado exitosamente.")

def cargar_proyectos():
    if not os.path.exists(ARCHIVO_PROYECTOS) or os.stat(ARCHIVO_PROYECTOS).st_size == 0:
        return []
    try:
        with open(ARCHIVO_PROYECTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def mostrar_proyectos(proyectos):
    if not proyectos:
        print("No hay proyectos para mostrar.")
        return
    
    print("\n===== Reporte de Proyectos =====")
    for i, p in enumerate(proyectos, 1):
        tareas = p.get("tareas", [])
        total_tareas = len(tareas)
        tareas_completadas = sum(1 for t in tareas if t.get("estado") == "Completada")
        avance = (tareas_completadas / total_tareas) * 100 if total_tareas > 0 else 0
        
        print(f"\n--- Proyecto {i} ---")
        print(f"  Nombre: {p.get('proyecto', 'N/A')}")
        print(f"  Costo: {p.get('costo', 'N/A')}")
        print(f"  Categoría: {p.get('categoria', 'N/A')}")
        print(f"  Descripción: {p.get('descripcion', 'N/A')}")
        print(f"  Materiales: {p.get('materiales', 'N/A')}")
        print(f"  Fecha de Inicio: {p.get('fechaInicio', 'N/A')}")
        print(f"  Fecha de Fin: {p.get('fechaFin', 'N/A')}")
        resp = p.get("responsableProyecto", {})
        print(f"  Responsable: {resp.get('nombre', 'N/A')} (Cédula: {resp.get('cedula', 'N/A')})")
        print(f"  Avance: {avance:.2f}% ({tareas_completadas}/{total_tareas} tareas completadas)")
        
        print("  Tareas:")
        if not tareas:
            print("   - No hay tareas asignadas.")
        else:
            for t in tareas:
                r = t.get("responsable", {})
                print(f"   - Nombre: {t.get('nombre', 'N/A')}")
                print(f"     Descripción: {t.get('descripcion', 'N/A')}")
                print(f"     Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')}")
                print(f"     Estado: {t.get('estado', 'N/A')}")
                print(f"     Responsable: {r.get('nombre', 'N/A')}")
    print("=" * 30)

def generarResumenProyectos():
    proyectos = cargar_proyectos()
    if not proyectos:
        print("No hay proyectos registrados.")
        return
    
    print("\n===== Resumen de Proyectos =====")
    for i, p in enumerate(proyectos, 1):
        tareas = p.get("tareas", [])
        total_tareas = len(tareas)
        tareas_completadas = sum(1 for t in tareas if t.get("estado") == "Completada")
        tareas_no_completadas = total_tareas - tareas_completadas
        avance = (tareas_completadas / total_tareas) * 100 if total_tareas > 0 else 0
        
        print(f"\n--- Proyecto {i}: {p.get('proyecto', 'N/A')} ---")
        print(f"  Total de tareas: {total_tareas}")
        print(f"  Tareas completadas: {tareas_completadas}")
        print(f"  Tareas no completadas: {tareas_no_completadas}")
        print(f"  Porcentaje de avance: {avance:.2f}%")
        
        print("  Estado de las tareas:")
        if not tareas:
            print("   - No hay tareas asignadas.")
        else:
            for t in tareas:
                print(f"   - {t.get('nombre', 'N/A')}: {t.get('estado', 'N/A')}")
    print("=" * 30)

def verReportesProyectos():
    proyectos = cargar_proyectos()
    if not proyectos:
        print("No hay proyectos registrados.")
        return
    
    while True:
        print("\n--- Reportes de Proyectos ---")
        print("1. Ver todos los proyectos")
        print("2. Filtrar proyectos por nombre")
        print("3. Ordenar proyectos")
        print("4. Generar resumen de proyectos")
        print("5. Volver al menú principal")
        opcion = input("Elija una opción: ").strip()
        
        if opcion == "1":
            mostrar_proyectos(proyectos)
        elif opcion == "2":
            nombre_buscar = input("Ingrese el nombre del proyecto a filtrar: ").strip().lower()
            proyectos_filtrados = [p for p in proyectos if p.get('proyecto', '').lower() == nombre_buscar]
            mostrar_proyectos(proyectos_filtrados)
        elif opcion == "3":
            print("\n--- Ordenar Proyectos por ---")
            print("1. Nombre (Alfabético)")
            print("2. Fecha de inicio")
            print("3. Responsable")
            opcion_ordenar = input("Elija una opción: ").strip()
            
            proyectos_ordenados = proyectos[:]
            
            if opcion_ordenar == "1":
                proyectos_ordenados.sort(key=lambda p: p.get('proyecto', '').lower())
                mostrar_proyectos(proyectos_ordenados)
            elif opcion_ordenar == "2":
                proyectos_ordenados.sort(key=lambda p: datetime.strptime(p.get('fechaInicio', '01/01/1900'), '%d/%m/%Y'))
                mostrar_proyectos(proyectos_ordenados)
            elif opcion_ordenar == "3":
                proyectos_ordenados.sort(key=lambda p: p.get('responsableProyecto', {}).get('nombre', '').lower())
                mostrar_proyectos(proyectos_ordenados)
            else:
                print("Opción inválida.")
        elif opcion == "4":
            generarResumenProyectos()
        elif opcion == "5":
            break
        else:
            print("Opción inválida.")

def menuAdministrador():
    while True:
        print("\n--- Sistema de Gestión de Usuarios y Proyectos ---")
        print("1. Registrar nuevo usuario")
        print("2. Ver todos los usuarios")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("5. Ver reportes de proyectos")
        print("6. Salir")
        opcion = input("Elija una opción: ")
        if opcion == "1":
            registrar_usuario()
        elif opcion == "2":
            mostrar_usuarios()
        elif opcion == "3":
            actualizar_usuario()
        elif opcion == "4":
            eliminar_usuario()
        elif opcion == "5":
            verReportesProyectos()
        elif opcion == "6":
            print("👋 Cerrando sesión...")
            os.remove(ARCHIVO_SESION)
            break
        else:
            print("Opción inválida, por favor intente de nuevo.")

if __name__ == "__main__":
    if validarSesion("Administrador"):
        menuAdministrador()