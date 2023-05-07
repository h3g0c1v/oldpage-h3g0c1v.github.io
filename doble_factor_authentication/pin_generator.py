#!/usr/bin/python3

from pwn import *
import random, signal, time

def def_handler(sig, frame):
    print("\n[+] Saliendo ...")
    exit(1)

signal.signal(signal.SIGINT, def_handler)

def pinGenerator():

    pin = ""

    p1 = log.progress("PIN")
    p1.status("Generando PIN aleatorio ...")

    time.sleep(0.5)

    # Creando una lista de numeros
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    min_lenght = 4
    max_lenght = 9
    
    # Almacenando un lenght aleatorio para el PIN
    random_lenght = random.randint(min_lenght, max_lenght)

    # Generando pin
    for number in numbers:

        # Eligiendo un numero aleatorio de la lista de numeros
        randomNumber = random.choice(numbers)

        pin+=randomNumber
        
        if len(pin) == random_lenght:
            break       
    
    # Mostrando PIN
    p1.success(pin)
    
    # Almacenando el PIN en un fichero oculto para poderlo utilizar en el programa de doble_factor de autenticacion
    with open(".pin.tmp", "w") as fichero:
        fichero.write(pin)

if __name__ == '__main__':
    print("")
    pinGenerator()
