import pwinput
import getpass
import bcrypt

a = "registro.txt"

def inicio():
    intentos = 0
    print("=======CLINICA GEMELOS=======")
    while True:
        correo = input("Correo electronico: ")
        contr_ingresada = pwinput.pwinput("Contraseña: ")
        autenticado = False

        with open(a, "r") as archivo:
            for linea in archivo:
                datos = linea.strip().split(",")
                if len(datos) < 6:
                    continue
                if correo == datos[3]:
                    autenticado = bcrypt.checkpw(
                        contr_ingresada.encode('utf-8'),
                        datos[4].encode('utf-8')
                    )
                    break

        if autenticado:
            print("Inicio exitoso")
            break
        else:
            intentos += 1
            print("Credenciales invalidas")
            print(intentos)
            if intentos == 3:
                print("Has excedido el numero de intentos")
                bloqueo()

def bloqueo():
    print("Su cuenta ha sido bloqueada, comuniquese con el administrador")
    codigo = getpass.getpass("Ingrese el codigo de desbloqueo: ")
    while codigo != "1234":
        print("Codigo incorrecto")
        codigo = getpass.getpass("Ingrese el codigo de desbloqueo: ")
    print("Cuenta desbloqueada")

def inicio0():
    print("=======CLINICA GEMELOS=======")
    print("\n=======Gestor de Proyectos=======\n")
    print("1.- Iniciar sesion")
    print("2.- Cambiar contraseña")
    eleccion = input("Elija una opcion [1/2]: ")
    match eleccion:
        case "1":
            inicio()
        case "2":
            cambioDeContraseña()
        case _:
            print("Opcion no valida")
            inicio0()

def cambioDeContraseña():
    print("Cambiar contraseña")
    correo=input("Ingrese su correo: ")
    encontrado=False
    with open (a,"r") as archivo:
        for linea in archivo:
            datos= linea.strip().split(",")
            if correo == datos[3]:
                print("cambio realizado.")
                encontrado=True
                break
    if not encontrado:
        print("correo incorrecto.")
        cambioDeContraseña()

inicio0()
