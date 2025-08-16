from datetime import datetime
proyeto="proyetos.txt"
estudiantes="registro.txt"
def crearProyecto():
    print("=====Creacion de proyectos=====")
    proyecto = input("Ingrese el nombre del Proyecto: ")
    costo = input("Ingrese el costo del proyecto: ")
    fehceInicio = input("Ingrese la fecha de inicio del proyecto (dd/mm/yyyy): ")
    fechaFin = input("Ingrese la fecha de finalizacion del proyecto (dd/mm/yyyy): ")
    tareas = []
    while True:
        tarea = input("Ingrese una tarea (o deje en blanco para terminar): ")
        if tarea == "":
            break
        else:
            Descripcion = input("Ingrese la descripcion de la tarea: ")
            while True:
                responsable = input("Ingrese el responsable de la tarea (Cedula): ")
                cedula_valida = False
                with open(estudiantes, "r") as archivo:
                    for linea in archivo:
                        datos = linea.strip().split(",")
                        if len(datos) > 5 and datos[2] == responsable:
                            if datos[5].strip() == "Estudiante":
                                cedula_valida = True
                            break
                if cedula_valida:
                    break
                else:
                    print("Cédula no encontrada o rol no válido. Intente de nuevo.")
        tareas.append({"nombre": tarea, "descripcion": Descripcion, "responsable": responsable})
    with open(proyeto, "a") as archivo:
        for t in tareas:
            archivo.write(f"{proyecto},{costo},{fehceInicio},{fechaFin},{t['nombre']},{t['descripcion']},{t['responsable']}\n")
        print("Proyecto creado exitosamente.")


def verEstudiantes():
            with open(estudiantes, "r") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if datos[5]=="Estudiante":
                        print(f"Cedula: {datos[2]} Nombre: {datos[0].title()} {datos[1].title()}")

crearProyecto()                    
