import pwinput
import bcrypt
import re
a="registro.txt"
def registrarUsuarios():
    with open(a, "a") as archivo:
        nombre=input("Ingrese el nombre: ")
        apellido=input("Ingrese el apellido: ")
        while True:
            cedula=input("Ingrese la cedula de identidad: ")
            numeroCedula=len(cedula)
            if numeroCedula== 10:
                break 
            else:
                print("Cedula invalida.")            
        correo=input("Ingrese el correo electronico: ")
        while True:
            contraseña = pwinput.pwinput("Ingrese una contraseña: ")
            es_valida, mensaje = validaContraseña(contraseña)
            if not es_valida:
                print("Contraseña inválida:", mensaje)
                continue
            confirmar = pwinput.pwinput("Vuelva a ingresar la contraseña: ")
            if contraseña == confirmar:
                salt = bcrypt.gensalt()
                hash_bytes = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
                hash_str = hash_bytes.decode('utf-8')
                break
            else:
                print("Las contraseñas no coinciden.")            
        print("Rol")
        while True:
            rol=input("""
                    1.- Administrador
                    2.- Estudiante
                    Elija un rol [1/2]""")
            match rol:
                case "1":
                    rol="Administrador"
                    break
                case "2":
                    rol="Estudiante"
                    break
                case _:
                    print("Rol invalido, vuelva a ingresar [1/2]: ")
        
        archivo.write(f"{nombre},{apellido},{cedula},{correo},{hash_str},{rol}\n")        
def validaContraseña(contraseña):
    if len(contraseña)<8:
        return False, "Debe tener minimo 8 caracteres"
    if not re.search(r"[A-Z]",contraseña):
        return False, "Debe tener al menos una letra en mayusucla."
    if not re.search(r"[a-z]", contraseña):
        return False, "Debe tener al menos una letra en minuscula."
    if not re.search(r"[0-9]", contraseña):
        return False, "Debe tener al menos un numero."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", contraseña):
        return False, "Debe tener al menos un caracter especial. "
    
    return True, ""

registrarUsuarios()