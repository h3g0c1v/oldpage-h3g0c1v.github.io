#!/usr/bin/python3

from pwn import *
import subprocess, time, signal, colorama

def def_handler(sig, frame):
    print(colorama.Fore.RED + "\n[+] Saliendo ...\n" + colorama.Style.RESET_ALL)
    exit(1)

signal.signal(signal.SIGINT, def_handler)

# Variables Globales
usuario = "a"
password = "a"

flight_info = {
    "Madrid": ["Hyatt Centric", "Riu", "Novotel"],
    "Barcelona": ["Renaissance Fira", "Front Maritim", "Travelodge Poblenou"],
    "Sevilla": ["San Pablo", "For You Hostel", "Pasarela"]
}

def dobleFactor():
    print("")

    try:
        with open(".pin.tmp", "r") as pin_generator:
            pin = pin_generator.read()
    except FileNotFoundError:
        print(colorama.Fore.RED + "\n[!] Ejecuta el programa generador de PIN primero\n" + colorama.Style.RESET_ALL)
        exit(1)
    
    while True:
        user_login = input(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + " Introduce el nombre de usuario: ")
        
        user_login = user_login.strip()

        if str(user_login) == str(usuario):
            break
        else:
            print(colorama.Fore.RED + "\n[!] Usuario incorrecto ...\n" + colorama.Style.RESET_ALL)

    while True:
        pass_login = input(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + " Introduce la contraseña: ")
        
        pass_login = pass_login.strip()

        if str(pass_login) == str(password):
            break
        else:
            print(colorama.Fore.RED + "\n[!] Contraseña incorrecta ...\n" + colorama.Style.RESET_ALL)

    print("")

    while True:
        user_pin = input(colorama.Fore.GREEN + "[+] " + colorama.Style.RESET_ALL + " Introduce el PIN: ")
        
        user_pin = user_pin.strip()

        if user_pin == pin:
            # Eliminando el fichero creado por el programa pin_generator.py
            #subprocess.run(["rm", ".pin.tmp"])
            
            print(colorama.Fore.GREEN + "\n[+]" + colorama.Style.RESET_ALL + " ¡Bienvenido de nuevo %s!" % usuario)

            aplication()
        else:
            print(colorama.Fore.RED + "\n[!] El PIN es incorrecto\n" + colorama.Style.RESET_ALL)

def aplication():

    print(colorama.Fore.GREEN + "\n[+] " + colorama.Style.RESET_ALL + " Opciones disponibles:\n")
    print(colorama.Fore.YELLOW + "\t[1] " + colorama.Style.RESET_ALL + " Ver vuelos disponibles")
    print(colorama.Fore.YELLOW + "\t[2] " + colorama.Style.RESET_ALL + " Ver hoteles disponibles")
    print(colorama.Fore.YELLOW + "\t[3] " + colorama.Style.RESET_ALL + " Reservar un vuelo")
    print(colorama.Fore.YELLOW + "\t[4] " + colorama.Style.RESET_ALL + " Reservar un hotel")
    print(colorama.Fore.YELLOW + "\t[5] " + colorama.Style.RESET_ALL + " Salir de la aplicacion\n")
    
    while True:
        user_option = input(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " ¿Que desea hacer? (1-6): ")

        user_option = user_option.strip()
        
        if user_option.isdigit():
            
            num = int(user_option)

            if num >= 1 and num <= 5:
               break 
            else:
                print(colorama.Fore.RED + "\n[!] Introduce una opcion disponible (1-6)\n" + colorama.Style.RESET_ALL)
        else:
            print(colorama.Fore.RED + "[!] Introduce una opcion disponible (1-6)" + colorama.Style.RESET_ALL)
    
    if num == 1:
        volver = aplication
        show_flights(volver)
    elif num == 2:
        volver = aplication
        show_hotels(volver)
    elif num == 3:
        volver = book_fly
        show_flights(volver)
        book_fly()
    elif num == 4:
        volver = book_hotel
        show_hotels(volver)
        book_hotel()
    elif num == 5:
        print(colorama.Fore.RED + "\n[+] Saliendo ...\n" + colorama.Style.RESET_ALL)
        exit(0)

def show_flights(volver):
   
    counter = 1
    print(colorama.Fore.GREEN + "\n[+]" + colorama.Style.RESET_ALL + " Vuelos disponibles:")
    
    for city in flight_info.keys():
        print(colorama.Fore.YELLOW + "\t[%s]" % counter + colorama.Style.RESET_ALL + " %s" % city) 
        counter+=1

    volver()

def book_fly():
    
    while True:
        book = input(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " ¿Que vuelo deseas reservar?: ") 
        
        book = book.strip()

        if book.isdigit():
            book = int(book)

            if book == 1:
                book = "Madrid"
            elif book == 2:
                book = "Barcelona"
            elif book == 3:
                book = "Sevilla"
            else:
                print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")

            print(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " El vuelo a %s se ha reservado correctamente" % book)
            break
        else:
            print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible") 
    
    aplication()

def show_hotels(volver):
    
    counter = 1

    print(colorama.Fore.GREEN + "\n[+]" + colorama.Style.RESET_ALL + " Hoteles disponibles:")

    for city, hotels in flight_info.items():

        print(colorama.Fore.YELLOW + "\t[%s]" % counter + colorama.Style.RESET_ALL + " %s" % city)
        
        letter = "A"

        for hotel in hotels:
            print(colorama.Fore.BLUE + "\t\t[%s]" % letter + colorama.Style.RESET_ALL + " %s" % hotel)
            letter = chr(ord(letter) + 1)

        counter += 1

    volver()

def book_hotel():
    
    while True:
        # Preguntando por el Pais
        book = input(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " ¿A que pais desea ir?: ") 
        
        book = book.strip()

        if book.isdigit():
            book = int(book)

            if book == 1:
                book = "Madrid"
                break
            elif book == 2:
                book = "Barcelona"
                break
            elif book == 3:
                book = "Sevilla"
                break
            else:
                print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")
        else:
            print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")
    
    while True:
        # Preguntando por el hotel
        book2 = input(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " ¿Que hotel deseas reservar?: ") 
        
        book2 = book.strip()
        book2 = book2.upper()

        if isinstance(book2, str):
            book2 = str(book2)
            book_hotel = "" 

            if book == 1:
                if book2 == "A":
                    book_hotel = "Hyatt Centric"
                if book2 == "B":
                    book_hotel = "Riu"
                if book2 == "C":
                    book_hotel = "Novotel"
                else:
                    print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")
            elif book == 2:
                if book2 == "A":
                    book_hotel = "Renaissance Fira"
                if book2 == "B":
                    book_hotel = "Front Maritim"
                if book2 == "C":
                    book_hotel = "Travelodge Poblenou"
                else:
                    print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")
            elif book == 3:
                if book2 == "A":
                    book_hotel = "San Pablo"
                if book2 == "B":
                    book_hotel = "For You Hostel"
                if book2 == "C":
                    book_hotel = "Pasarela"
                else:
                    print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")
            
            print(colorama.Fore.GREEN + "[+]" + colorama.Style.RESET_ALL + " El hotel de %s se ha reservado correctamente" % book)
            break
        else:
            print(colorama.Fore.RED + "[!]" + colorama.Style.RESET_ALL + " Introduce una opcion disponible")

    aplication()

if __name__ == '__main__':
    dobleFactor()
