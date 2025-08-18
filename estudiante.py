from datetime import datetime
import json, os
proyeto="proyetos.json"
estudiantes="registro.txt"
def crearProyecto():
    print("=====Creacion de proyectos=====")
    proyecto = input("Ingrese el nombre del Proyecto: ").strip()
    costo = input("Ingrese el costo del proyecto: ").strip()
    while True:
        fehceInicio = input("Ingrese la fecha de inicio del proyecto (dd/mm/yyyy): ").strip()
        try:
            fecha_inicio_dt = datetime.strptime(fehceInicio, "%d/%m/%Y")
            break
        except:
            print("Fecha inválida. Use el formato dd/mm/yyyy y una fecha existente.")
    while True:
        fechaFin = input("Ingrese la fecha de finalizacion del proyecto (dd/mm/yyyy): ").strip()
        try:
            fecha_fin_dt = datetime.strptime(fechaFin, "%d/%m/%Y")
            if fecha_fin_dt < fecha_inicio_dt:
                print("La fecha de finalización no puede ser anterior a la fecha de inicio.")
                continue
            break
        except:
            print("Fecha inválida. Use el formato dd/mm/yyyy y una fecha existente.")
    while True:
        responsableProyecto = input("Ingrese la cédula del responsable del proyecto: ").strip()
        cedula_valida = False
        nombreResponsableProyecto = ""
        with open(estudiantes, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                datos = linea.strip().split(",")
                if len(datos) > 5 and datos[2].strip() == responsableProyecto:
                    if datos[5].strip().lower() == "estudiante":
                        cedula_valida = True
                        nombreResponsableProyecto = f"{datos[0].strip()} {datos[1].strip()}"
                        break
        if cedula_valida:
            break
        else:
            print("Cédula no encontrada o rol no válido para responsable del proyecto. Intente de nuevo.")
    tareas = []
    while True:
        tarea = input("Ingrese una tarea (o deje en blanco para terminar): ").strip()
        if tarea == "":
            break
        Descripcion = input("Ingrese la descripcion de la tarea: ").strip()
        while True:
            responsable = input("Ingrese el responsable de la tarea (Cedula): ").strip()
            Estudiante=""
            cedula_valida = False
            with open(estudiantes, "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if len(datos) > 5 and datos[2].strip() == responsable:
                        if datos[5].strip().lower() == "estudiante":
                            cedula_valida = True
                            Estudiante = f"{datos[0].strip()} {datos[1].strip()}"
                            break
            if cedula_valida:
                break
            else:
                print("Cédula no encontrada o rol no válido. Intente de nuevo.")
        tareas.append({"nombre": tarea, "descripcion": Descripcion, "responsable": responsable, "estudiante": Estudiante})
    proyecto_obj = {
        "proyecto": proyecto,
        "costo": costo,
        "fehceInicio": fehceInicio,
        "fechaFin": fechaFin,
        "responsableProyecto": {
            "cedula": responsableProyecto,
            "nombre": nombreResponsableProyecto
        },
        "tareas": [
            {
                "nombre": t["nombre"],
                "descripcion": t["descripcion"],
                "responsable": {
                    "cedula": t["responsable"],
                    "nombre": t["estudiante"]
                }
            } for t in tareas
        ]
    }
    data = []
    if os.path.exists(proyeto):
        try:
            with open(proyeto, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if contenido:
                    data = json.loads(contenido)
        except:
            data = []
    data.append(proyecto_obj)
    with open(proyeto, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Proyecto creado exitosamente.")

def verEstudiantes():
    with open(estudiantes, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            datos = linea.strip().split(",")
            if len(datos) > 5 and datos[5].strip().lower() == "estudiante":
                print(f"Cedula: {datos[2].strip()} Nombre: {datos[0].strip().title()} {datos[1].strip().title()}")

crearProyecto()
