from datetime import datetime
import json
import os
import bcrypt
import pwinput

ARCHIVO_PROYECTOS = "proyectos.json"
ARCHIVO_REGISTRO = "registro.txt"
ARCHIVO_SESION = "sesion_actual.json"

# Variable global para almacenar el usuario de la sesión
usuarioActual = None

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

def cargarDatos(archivo):
    if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
        return []
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def guardarDatos(data, archivo):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def buscarProyectoPorNombre(nombreProyecto):
    data = cargarDatos(ARCHIVO_PROYECTOS)
    for i, p in enumerate(data):
        if p.get("proyecto", "").strip().lower() == nombreProyecto.strip().lower():
            return i, p
    return None, None

def obtenerDatosUsuarioPorCedula(cedula):
    try:
        with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split(",")
                if len(datos) > 5 and datos[2].strip().lower() == cedula.strip().lower():
                    return {
                        "nombre": f"{datos[0].strip()} {datos[1].strip()}",
                        "cedula": datos[2].strip(),
                        "correo": datos[3].strip(),
                        "contraseña_hash": datos[4].strip(),
                        "rol": datos[5].strip()
                    }
    except FileNotFoundError:
        pass
    return None

def pedirFechaValida(prompt, minDtStr=None):
    while True:
        txt = input(prompt).strip()
        try:
            dt = datetime.strptime(txt, "%d/%m/%Y")
            if minDtStr:
                minDt = datetime.strptime(minDtStr, "%d/%m/%Y")
                if dt < minDt:
                    print("La fecha no puede ser anterior a la fecha mínima permitida.")
                    continue
            return txt
        except ValueError:
            print("Fecha inválida. Use el formato dd/mm/yyyy y una fecha existente.")

def calcularAvanceProyecto(proyecto):
    tareas = proyecto.get("tareas", [])
    if not tareas:
        return 0
    tareasCompletadas = [t for t in tareas if t.get("estado") == "Completada"]
    return (len(tareasCompletadas) / len(tareas)) * 100

# Funciones de Gestión de Proyectos (exclusivas para Estudiantes)
def crearProyecto():
    print("\n--- Crear Nuevo Proyecto ---")
    nombre = input("Nombre del proyecto: ").strip()
    costo = input("Costo del proyecto: ").strip()
    categoria = input("Categoría del proyecto: ").strip()
    descripcion = input("Descripción del proyecto: ").strip()
    materiales = input("Materiales requeridos: ").strip()
    
    fechaInicio = pedirFechaValida("Fecha de inicio (dd/mm/yyyy): ")
    fechaFin = pedirFechaValida("Fecha de fin (dd/mm/yyyy): ", minDtStr=fechaInicio)

    cedulaResponsable = usuarioActual['cedula']
    datosResp = obtenerDatosUsuarioPorCedula(cedulaResponsable)
    if not datosResp:
        print("Error: No se pudieron obtener los datos de la sesión actual.")
        return

    nuevoProyecto = {
        "proyecto": nombre,
        "costo": costo,
        "categoria": categoria,
        "descripcion": descripcion,
        "materiales": materiales,
        "fehceInicio": fechaInicio,
        "fechaFin": fechaFin,
        "responsableProyecto": {
            "cedula": cedulaResponsable,
            "nombre": datosResp['nombre']
        },
        "tareas": []
    }
    data = cargarDatos(ARCHIVO_PROYECTOS)
    data.append(nuevoProyecto)
    guardarDatos(data, ARCHIVO_PROYECTOS)
    print("✅ Proyecto creado exitosamente.")

def actualizarProyecto():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos para actualizar.")
        return
    nombre_buscar = input("Nombre del proyecto a actualizar: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre_buscar)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    
    if proj.get('responsableProyecto', {}).get('cedula') != usuarioActual['cedula']:
        print("❌ No tiene permisos para actualizar este proyecto.")
        return

    print("\n--- Actualizar Proyecto ---")
    print("Deje el campo vacío si no desea modificarlo.")
    
    nuevo_nombre = input(f"Nuevo nombre ({proj['proyecto']}): ")
    if nuevo_nombre:
        proj['proyecto'] = nuevo_nombre
    
    nuevo_costo = input(f"Nuevo costo ({proj['costo']}): ")
    if nuevo_costo:
        proj['costo'] = nuevo_costo
    
    nueva_categoria = input(f"Nueva categoría ({proj['categoria']}): ")
    if nueva_categoria:
        proj['categoria'] = nueva_categoria

    nueva_descripcion = input(f"Nueva descripción ({proj['descripcion']}): ")
    if nueva_descripcion:
        proj['descripcion'] = nueva_descripcion

    nuevos_materiales = input(f"Nuevos materiales ({proj['materiales']}): ")
    if nuevos_materiales:
        proj['materiales'] = nuevos_materiales

    cambiar_fechas = input("¿Desea cambiar las fechas? (s/n): ").lower()
    if cambiar_fechas == 's':
        proj['fehceInicio'] = pedirFechaValida(f"Nueva fecha de inicio ({proj['fehceInicio']}): ")
        proj['fechaFin'] = pedirFechaValida(f"Nueva fecha de fin ({proj['fechaFin']}): ", minDtStr=proj['fehceInicio'])
    
    data[idx] = proj
    guardarDatos(data, ARCHIVO_PROYECTOS)
    print("✅ Proyecto actualizado exitosamente.")

def eliminarProyecto():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos para eliminar.")
        return
    nombre_eliminar = input("Nombre del proyecto a eliminar: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre_eliminar)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    
    if proj.get('responsableProyecto', {}).get('cedula') != usuarioActual['cedula']:
        print("❌ No tiene permisos para eliminar este proyecto.")
        return

    confirmacion = input(f"¿Está seguro de que desea eliminar el proyecto '{proj['proyecto']}' y todas sus tareas? (s/n): ").lower()
    if confirmacion == 's':
        data.pop(idx)
        guardarDatos(data, ARCHIVO_PROYECTOS)
        print("✅ Proyecto eliminado exitosamente.")
    else:
        print("Operación cancelada.")

# Funciones de Gestión de Tareas
def listarProyectos():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos registrados.")
        return
    print("===== Lista de Proyectos =====")
    for i, p in enumerate(data, 1):
        avance = calcularAvanceProyecto(p)
        print(f"{i}. {p.get('proyecto','(sin nombre)')} - Categoría: {p.get('categoria','?')} | Costo: {p.get('costo','?')} | Avance: {avance:.2f}%")

def verProyecto():
    nombre = input("Nombre del proyecto a visualizar: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    
    avance = calcularAvanceProyecto(proj)
    
    print("===== Detalle del Proyecto =====")
    print(f"Proyecto: {proj.get('proyecto')} (Avance: {avance:.2f}%)")
    print(f"Costo: {proj.get('costo')}")
    print(f"Categoría: {proj.get('categoria')}")
    print(f"Fecha de inicio: {proj.get('fehceInicio')}")
    print(f"Fecha de fin: {proj.get('fechaFin')}")
    resp = proj.get("responsableProyecto", {})
    print(f"Responsable: {resp.get('nombre','')} (Cédula: {resp.get('cedula','')})")
    print("\nTareas:")
    tareas = proj.get("tareas", [])
    if not tareas:
        print("   - No hay tareas registradas.")
    else:
        for i, t in enumerate(tareas, 1):
            r = t.get("responsable", {})
            print(f"   {i}. {t.get('nombre')} - {t.get('descripcion')}")
            print(f"      Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')} | Estado: {t.get('estado', 'N/A')}")
            print(f"      Responsable: {r.get('nombre','')} ({r.get('cedula','')})")

def listarTareas():
    nombre = input("Nombre del proyecto: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    tareas = proj.get("tareas", [])
    print(f"===== Tareas de '{proj.get('proyecto')}' =====")
    if not tareas:
        print("No hay tareas registradas.")
        return
    for i, t in enumerate(tareas, 1):
        r = t.get("responsable", {})
        print(f"{i}. {t.get('nombre')} - {t.get('descripcion')} | Inicio: {t.get('fecha_inicio','?')} | Fin: {t.get('fecha_fin','?')} | Estado: {t.get('estado', 'N/A')}")
        print(f"   Responsable: {r.get('nombre','')} ({r.get('cedula','')})")

def agregarTarea():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos. No se puede agregar una tarea.")
        return
    nombre = input("Nombre del proyecto: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    tarea = input("Nombre de la tarea: ").strip()
    if not tarea:
        print("Nombre de tarea inválido.")
        return
    descripcion = input("Descripción de la tarea: ").strip()
    fechaInicio = pedirFechaValida("Fecha de inicio (dd/mm/yyyy): ")
    fechaFin = pedirFechaValida("Fecha de fin (dd/mm/yyyy): ", minDtStr=fechaInicio)
    while True:
        cedResponsable = input("Cédula del responsable: ").strip()
        datosResp = obtenerDatosUsuarioPorCedula(cedResponsable)
        if datosResp and datosResp['rol'].lower() == "estudiante":
            break
        print("Cédula no encontrada o rol no válido. Intente de nuevo.")
    nuevaTarea = {
        "nombre": tarea,
        "descripcion": descripcion,
        "fecha_inicio": fechaInicio,
        "fecha_fin": fechaFin,
        "responsable": {
            "cedula": cedResponsable,
            "nombre": datosResp['nombre']
        },
        "estado": "Asignada"  # Nuevo campo: estado de la tarea
    }
    proj.setdefault("tareas", []).append(nuevaTarea)
    data[idx] = proj
    guardarDatos(data, ARCHIVO_PROYECTOS)
    print("✅ Tarea agregada exitosamente.")

def editarTarea():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos.")
        return
    nombre = input("Nombre del proyecto: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    tareas = proj.get("tareas", [])
    if not tareas:
        print("El proyecto no tiene tareas.")
        return
    for i, t in enumerate(tareas, 1):
        print(f"{i}. {t.get('nombre')} - {t.get('descripcion')}")
    try:
        sel = int(input("Seleccione el número de la tarea a editar: ").strip())
        if sel < 1 or sel > len(tareas):
            print("Selección inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    tarea = tareas[sel - 1]
    print("Deje en blanco lo que no desea cambiar.")
    nuevoNombre = input(f"Nuevo nombre [{tarea.get('nombre')}]: ").strip()
    if nuevoNombre:
        tarea["nombre"] = nuevoNombre
    nuevaDesc = input(f"Nueva descripción [{tarea.get('descripcion')}]: ").strip()
    if nuevaDesc:
        tarea["descripcion"] = nuevaDesc
    cambiarFechas = input("¿Cambiar fechas? (s/n): ").strip().lower()
    if cambiarFechas == "s":
        fechaInicio = pedirFechaValida(f"Nueva fecha de inicio [{tarea.get('fecha_inicio', 'N/A')}] (dd/mm/yyyy): ")
        fechaFin = pedirFechaValida(f"Nueva fecha de fin [{tarea.get('fecha_fin', 'N/A')}] (dd/mm/yyyy): ", minDtStr=fechaInicio)
        tarea["fecha_inicio"] = fechaInicio
        tarea["fecha_fin"] = fechaFin
    cambiarResp = input("¿Cambiar responsable de la tarea? (s/n): ").strip().lower()
    if cambiarResp == "s":
        while True:
            cedResponsable = input("Cédula del nuevo responsable: ").strip()
            datosResp = obtenerDatosUsuarioPorCedula(cedResponsable)
            if datosResp and datosResp['rol'].lower() == "estudiante":
                tarea["responsable"] = {"cedula": cedResponsable, "nombre": datosResp['nombre']}
                break
            print("Cédula no encontrada o rol no válido. Intente de nuevo.")
    tareas[sel - 1] = tarea
    proj["tareas"] = tareas
    data[idx] = proj
    guardarDatos(data, ARCHIVO_PROYECTOS)
    print("✅ Tarea actualizada exitosamente.")

def eliminarTarea():
    data = cargarDatos(ARCHIVO_PROYECTOS)
    if not data:
        print("No hay proyectos.")
        return
    nombre = input("Nombre del proyecto: ").strip()
    idx, proj = buscarProyectoPorNombre(nombre)
    if proj is None:
        print("Proyecto no encontrado.")
        return
    tareas = proj.get("tareas", [])
    if not tareas:
        print("El proyecto no tiene tareas.")
        return
    for i, t in enumerate(tareas, 1):
        print(f"{i}. {t.get('nombre')} - {t.get('descripcion')}")
    try:
        sel = int(input("Seleccione el número de la tarea a eliminar: ").strip())
        if sel < 1 or sel > len(tareas):
            print("Selección inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
    t = tareas[sel - 1]
    conf = input(f"Confirme eliminación de '{t.get('nombre')}' (s/n): ").strip().lower()
    if conf == "s":
        tareas.pop(sel - 1)
        proj["tareas"] = tareas
        data[idx] = proj
        guardarDatos(data, ARCHIVO_PROYECTOS)
        print("✅ Tarea eliminada.")
    else:
        print("Operación cancelada.")

def marcarTarea():
    ced = usuarioActual['cedula']
    data = cargarDatos(ARCHIVO_PROYECTOS)
    
    misTareas = []
    for p in data:
        for t in p.get("tareas", []):
            if t.get('responsable', {}).get('cedula') == ced:
                misTareas.append({'proyecto': p, 'tarea': t})
    
    if not misTareas:
        print("No tiene tareas asignadas para marcar.")
        return
        
    print("===== Mis Tareas =====")
    for i, item in enumerate(misTareas, 1):
        proy_nombre = item['proyecto']['proyecto']
        tarea_nombre = item['tarea']['nombre']
        tarea_estado = item['tarea'].get('estado', 'N/A')
        print(f"{i}. [{proy_nombre}] {tarea_nombre} - Estado: {tarea_estado}")

    try:
        sel = int(input("Seleccione el número de la tarea a actualizar: ").strip())
        if sel < 1 or sel > len(misTareas):
            print("Selección inválida.")
            return
    except ValueError:
        print("Entrada inválida.")
        return
        
    tarea_seleccionada = misTareas[sel - 1]['tarea']
    proyecto_seleccionado = misTareas[sel - 1]['proyecto']
    
    print("\n--- Opciones de Estado ---")
    print("1. En ejecución")
    print("2. Completada")
    estado_opcion = input("Elija un nuevo estado [1/2]: ").strip()
    
    nuevo_estado = ""
    if estado_opcion == "1":
        nuevo_estado = "En ejecución"
    elif estado_opcion == "2":
        nuevo_estado = "Completada"
    else:
        print("Opción inválida.")
        return
    
    tarea_seleccionada['estado'] = nuevo_estado
    
    # Encontrar el índice de la tarea en el proyecto para actualizar
    for i, t in enumerate(proyecto_seleccionado['tareas']):
        if t['nombre'] == tarea_seleccionada['nombre'] and t['responsable']['cedula'] == ced:
            proyecto_seleccionado['tareas'][i] = tarea_seleccionada
            break
            
    # Encontrar el índice del proyecto en los datos generales
    for i, p in enumerate(data):
        if p['proyecto'] == proyecto_seleccionado['proyecto']:
            data[i] = proyecto_seleccionado
            break
    
    guardarDatos(data, ARCHIVO_PROYECTOS)
    print(f"✅ Estado de la tarea '{tarea_seleccionada['nombre']}' actualizado a '{nuevo_estado}'.")

def verMisProyectosYMisTareas():
    ced = usuarioActual['cedula']
    data = cargarDatos(ARCHIVO_PROYECTOS)
    misProyectos = []
    misTareas = []
    for p in data:
        rp = p.get("responsableProyecto", {})
        if rp.get("cedula", "").strip() == ced:
            misProyectos.append(p)
        for t in p.get("tareas", []):
            r = t.get("responsable", {})
            if r.get("cedula", "").strip() == ced:
                misTareas.append((p.get("proyecto",""), t))
    print("===== Proyectos creados por mí =====")
    if not misProyectos:
        print("No tiene proyectos como responsable.")
    else:
        for i, p in enumerate(misProyectos, 1):
            avance = calcularAvanceProyecto(p)
            print(f"{i}. {p.get('proyecto')} | Avance: {avance:.2f}% | Costo: {p.get('costo')} | Inicio: {p.get('fehceInicio')} | Fin: {p.get('fechaFin')}")
    print("===== Tareas asignadas a mí =====")
    if not misTareas:
        print("No tiene tareas asignadas.")
    else:
        for i, (nombreProy, t) in enumerate(misTareas, 1):
            print(f"{i}. [{nombreProy}] {t.get('nombre')} - {t.get('descripcion')}")
            print(f"   Inicio: {t.get('fecha_inicio', 'N/A')} | Fin: {t.get('fecha_fin', 'N/A')} | Estado: {t.get('estado', 'N/A')}")

def menuEstudiante():
    while True:
        print("\n===== Gestor de Proyectos de Estudiante =====")
        print("1. Crear nuevo proyecto")
        print("2. Actualizar un proyecto")
        print("3. Eliminar un proyecto")
        print("4. Agregar una tarea")
        print("5. Editar una tarea")
        print("6. Eliminar una tarea")
        print("7. Marcar tarea como completada/en ejecución")
        print("8. Listar todos los proyectos")
        print("9. Ver detalle de un proyecto")
        print("10. Ver mis proyectos y mis tareas")
        print("11. Salir")
        
        op = input("Opción: ").strip()
        if op == "1":
            crearProyecto()
        elif op == "2":
            actualizarProyecto()
        elif op == "3":
            eliminarProyecto()
        elif op == "4":
            agregarTarea()
        elif op == "5":
            editarTarea()
        elif op == "6":
            eliminarTarea()
        elif op == "7":
            marcarTarea()
        elif op == "8":
            listarProyectos()
        elif op == "9":
            verProyecto()
        elif op == "10":
            verMisProyectosYMisTareas()
        elif op == "11":
            print("👋 Cerrando sesión...")
            os.remove(ARCHIVO_SESION)
            break
        else:
            print("Opción inválida.")

def iniciarModuloEstudiante():
    global usuarioActual
    try:
        with open(ARCHIVO_SESION, "r", encoding="utf-8") as f:
            usuarioActual = json.load(f)
        menuEstudiante()
    except FileNotFoundError:
        print("❌ No hay una sesión activa. Por favor, inicie sesión con 'inicio.py' primero.")

if __name__ == "__main__":
    if validarSesion("Estudiante"):
        iniciarModuloEstudiante()