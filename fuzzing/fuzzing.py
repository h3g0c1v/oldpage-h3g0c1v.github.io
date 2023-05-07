#!/usr/bin/python3

from pwn import *
import signal, requests, time, colorama, argparse, re, socket, ping3, os

# Ctrl + C
def def_handler(sig, frame):
    print(colorama.Fore.RED + "\n[!] Saliendo ...\n" + colorama.Style.RESET_ALL)
    exit(1)

# Capturando el Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# Argumentos del programa
parser = argparse.ArgumentParser(description='Script para reconocimiento de rutas en una URL', epilog='¡Gracias por usar el script <3!')

parser.add_argument('-H', '--ayuda', action='help', help='Panel de Ayuda')
parser.add_argument('-u', '--url', type=str, required=True, help='URL a fuzzear')
parser.add_argument('-w', '--wordlist', type=str, required=True, help='Diccionario de rutas')
parser.add_argument('-e', '--extension', type=str, required=False, help='Extension/es')

args = parser.parse_args()

url = args.url
wordlist = args.wordlist
extension = args.extension

def rootCheck():
    if os.geteuid() != 0:
        print(colorama.Fore.RED + "[!] Necesitas tener privilegios de root para correr este script." + colorama.Style.RESET_ALL)
        exit(1)

def CheckingHost():
    
    check1 = log.progress("Host")
    check1.status("Comprobando conectividad con el host: %s" % url)
    
    time.sleep(1)
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            check1.success("Activo")
    except requests.exceptions.RequestException as e:
        check1.failure("El host " + colorama.Fore.YELLOW + "%s" % url + colorama.Style.RESET_ALL + " no esta activo")
        exit(1)

def makeFuzz(url):
   
    p1 = log.progress("Realizando fuzzing")
    p1.status(colorama.Fore.YELLOW + "%s" % url + colorama.Style.RESET_ALL)

    print("")

    pattern = re.compile(r"^.*/$")
    pattern2 = re.compile(r"^.*$")

    if pattern.match(url):
        url = url[:-1]

    # Abriendo el fichero de rutas
    f = open(wordlist, "r")
    
    for subdirectorio in f.readlines():
        
        subdirectorio = subdirectorio.strip()

        try:
            main_url = url+"/"+subdirectorio
            r = requests.get(main_url)
            
            if r.status_code == 200:
                print(colorama.Fore.GREEN + "[+] %s" % main_url + colorama.Style.RESET_ALL)
            else:
               continue 
        except Exception as e:
            print("Error al conectar con la página: %s" % e)
    
    p1.success("Terminado correctamente")
if __name__ == '__main__':

    print("")

    rootCheck()
    CheckingHost()
    makeFuzz(url)
