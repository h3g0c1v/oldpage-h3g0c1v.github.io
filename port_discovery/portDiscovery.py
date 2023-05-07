#!/usr/bin/python3

import requests, signal, time, socket, colorama, argparse, ping3, re

# Definiendo que hacer cuando se pulse el Ctrl + C
def def_handler(sig, frame):
    print(colorama.Fore.RED + "\n[+] Saliendo ..." + colorama.Style.RESET_ALL)
    exit(1)

# Capturando el Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# Funcion para validar si la IP introducida es valida
def validate_ip(ip):
    pattern_ip = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

    if not re.match(pattern_ip, ip): 
        print(colorama.Fore.RED + "\n[!] Introduce una IP valida ...\n" + colorama.Style.RESET_ALL)
        exit(1)

parser = argparse.ArgumentParser(description='Script para el reconocimiento de puertos abiertos', epilog='¡Gracias por usar el script <3!')

parser.add_argument('-H', '--ayuda', action='help', help='Mostrar el panel de ayuda')
parser.add_argument('-i', '--ip', type=str, help='Direccion IP')

args = parser.parse_args()

# Variables Globales
ip = args.ip

# Funcion de validacion si el host esta encendido
def check_host(ip):
    
    success = 0

    # Intentando resolver el host
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

    if success == 0:
        print("No se pudo resolver el host: %s" % ip)
        exit(1)

# Funcion global
def portDiscovery():
    
    counter_port = 0
    tail = 0

    for port in range(1,65536):

        try:
            socket.create_connection((ip, port), timeout=3)
            counter_port+=1

            print("\n[+] Puerto " + colorama.Fore.YELLOW + "%s" % port + colorama.Style.RESET_ALL + " - ABIERTO")

        except:
            tail=tail

if __name__ == '__main__':

    validate_ip(ip)
    check_host(ip)
    portDiscovery()
