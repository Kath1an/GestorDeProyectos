from datetime import datetime
proyeto="proyetos.txt"
estudiantes="registro.txt"
def crearProyecto():
    print("=====Creacion de proyectos=====")
    proyecto=input("Ingrese el nombre del Proyecto: ")
    costo=input("Ingrese el costo del proyecto: ")
    fehceInicio=input("Ingrese la fecha de inicio del proyecto (dd/mm/yyyy): ")
    fechaFin=input("Ingrese la fecha de finalizacion del proyecto (dd/mm/yyyy): ")
    tareas=[]
    while True:
        tarea=input("Ingrese una tarea (o deje en blanco para terminar): ")
        if tarea=="":
            break
        else:
            verEstudiantes()

    with open(proyeto, "a") as archivo:
        archivo.write(f"{proyecto},{costo},{fehceInicio},{fechaFin}\n")
        print("Proyecto creado exitosamente.")

def verEstudiantes():
            with open(estudiantes, "r") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if datos[5]=="Estudiante":
                        print(f"Cedula: {datos[2]} Nombre: {datos[0].title()} {datos[1].title()}")
                      
verEstudiantes()