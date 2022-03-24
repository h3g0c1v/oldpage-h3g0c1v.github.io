---
layout: single
title: Shocker - Hack The Box
excerpt: "Máquina muy sencilla, bastante buena para los que estén empezando. Vamos a estar tocando un ShellShock Attack y una vez que estemos dentro vamos a ver como abusar de un privilegio de sudoers para escalar privilegios."
date: 2022-03-24
classes: wide
header:
  teaser: /assets/images/htb-writeup-Shocker/shocker_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
    - linux
    - ShellShock Attack (CVE-2014-6271)
    - Abusing Sudoers Privilege (Perl)
---

![](/assets/images/htb-writeup-Shocker/shocker_logo.png)

# Reconocimiento

Empezaremos como siempre escaneando todo el rango de puertos, por **TCP**.

```bash

h3g0c1v@kali:~/htb/shocker$ nmap -sS --min-rate 5000 -p- --open -n -vvv -Pn 10.10.10.56 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-24 11:21 CET
Initiating SYN Stealth Scan at 11:21
Scanning 10.10.10.56 [65535 ports]
Discovered open port 80/tcp on 10.10.10.56
Discovered open port 2222/tcp on 10.10.10.56
Completed SYN Stealth Scan at 11:21, 10.22s elapsed (65535 total ports)
Nmap scan report for 10.10.10.56
Host is up, received user-set (0.034s latency).
Scanned at 2022-03-24 11:21:36 CET for 10s
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE      REASON
80/tcp   open  http         syn-ack ttl 63
2222/tcp open  EtherNetIP-1 syn-ack ttl 63

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 10.36 seconds
           Raw packets sent: 65535 (2.884MB) | Rcvd: 65535 (2.621MB)

```

Y vamos a detectar la versión y servicio que corren para esos dos puertos abiertos, además de lanzarle unos scripts básicos de enumeración.

```bash

h3g0c1v@kali:~/htb/shocker$ nmap -sCV -p80,2222 10.10.10.56 -oN targeted
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-24 11:23 CET
Nmap scan report for 10.10.10.56
Host is up (0.034s latency).

PORT     STATE SERVICE VERSION
80/tcp   open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
2222/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 c4:f8:ad:e8:f8:04:77:de:cf:15:0d:63:0a:18:7e:49 (RSA)
|   256 22:8f:b1:97:bf:0f:17:08:fc:7e:2c:8f:e9:77:3a:48 (ECDSA)
|_  256 e6:ac:27:a3:b5:a9:f1:12:3c:34:a5:5d:5b:eb:3d:e9 (ED25519)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.10 seconds

```

Seguiremos con la enumeración lanzándole la herramienta **whatweb** a ese puerto **80/TCP HTTP** para ver un poco más de información sobre esa página web.

```bash
h3g0c1v@kali:~/htb/shocker$ whatweb http://10.10.10.56
http://10.10.10.56 [200 OK] Apache[2.4.18], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.18 (Ubuntu)], IP[10.10.10.56]
```

Si nos fijamos en el nombre de la máquina, vemos que se llama *Shocker*, eso ya me hace pensar en un ataque llamado **ShellShock Attack** , así que vamos a *fuzzear* un poco, a ver si encontramos una ruta de tipo `/cgi-bin/`.

```bash
h3g0c1v@kali:~/htb/shocker$ wfuzz -c -t 200 --hh=137 --hc=404 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt http://10.10.10.56/FUZZ/
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.10.10.56/FUZZ/
Total requests: 220560

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                           
=====================================================================

000000083:   403        11 L     32 W       292 Ch      "icons"                                                                           
000000035:   403        11 L     32 W       294 Ch      "cgi-bin"            
```

Es importante, poner la barra del final, en el lugar donde le indicamos que queremos fuzzear, ya que si no la ponemos, no nos encontrará la ruta.

Y bueno, vemos que hay un directorio **cgi-bin** , así que vamos a fuzzear por él, con otro diccionario extra de extensiones que son probables que se encuentren, en caso de que sea vulnerables al **ShellShock Attack** (sh, pl, cgi ...).

```bash
h3g0c1v@kali:~/htb/shocker$ wfuzz -c -t 200 --hh=294 --hc=404 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -w extensions.txt http://10.10.10.56/cgi-bin/FUZZ.FUZ2Z
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://10.10.10.56/cgi-bin/FUZZ.FUZ2Z
Total requests: 882240

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                           
=====================================================================

000000500:   200        7 L      17 W       118 Ch      "user - sh"      
```

Y vemos que nos ha encontrado un fichero `user.sh`, que si nos vamos a la página web, veremos que nos lo descarga. Voy a hacerle un **curl** para ver realmente que tiene ese fichero.

```bash
h3g0c1v@kali:~/htb/shocker$ curl -s -X GET "http://10.10.10.56/cgi-bin/user.sh"
Content-Type: text/plain

Just an uptime test script

 06:32:28 up  1:22,  0 users,  load average: 0.00, 0.00, 0.00
```

Si le volvemos a hacer un **curl** , veremos que es un fichero que se actualiza continuamente. Para probar la inyección, y realmente saber si es vulnerable o no, voy a mandarle en el *User Agent*, un payload especial.

![](/assets/images/htb-writeup-Shocker/shellshock_vulnerable.png)

Y, efectivamente, es vulnerable. En este punto, me podría mandar una **reverse shell** a mi equipo por cualquier puerto que esté en escucha.

![](/assets/images/htb-writeup-Shocker/reverseshell.png)

Pero voy a usar un exploit de *GitHub*, que me pareció curioso.

	- https://github.com/b4keSn4ke/shellshock

Este script simplemente le tendríamos que indicar nuestra IP de atacante, con el puerto en el que estemos en escucha, y seguidamente le indicaremos cualquier fichero que se encuentre dentro del directorio `/cgi-bin` que encontramos en la web. En este caso será el fichero `user.sh`.

![](/assets/images/htb-writeup-Shocker/exploit.png)

Ahora que estamos dentro, realizaremos un tratamiento de la **tty** para tener una tty completamente interactiva.

![](/assets/images/htb-writeup-Shocker/tty.png)

Y exportaremos las dos variables, junto a ajustar el tamaño de las filas y columnas de la terminal.

![](/assets/images/htb-writeup-Shocker/export.png)

En este punto, ya podemos irnos al directorio `/home/shelly` y visualizar la flag de bajos privilegios.

![](/assets/images/htb-writeup-Shocker/usertxt.png)

Si miramos los binarios **SUID** que hay, no vemos gran cosa, pero ejecutamos el comando **sudo -l** para ver los binarios que tenemos permisos para ejecutar como **sudo**, vemos que está el binario `/usr/bin/perl`.

![](/assets/images/htb-writeup-Shocker/sudoers.png)

Esto está fatal, ya que este binario, si nos vamos a la página de **gtfobins.io** , podremos observar como se puede abusar de él en caso de que podamos ejecutarlo como **sudo**, que es el caso.

	- https://gtfobins.github.io/gtfobins/perl/#sudo

![](/assets/images/htb-writeup-Shocker/gtfobins.png)


Vamos a ejecutar lo que nos dice en la página comentada, vemos como nos convertimos directamente en **root**.

![](/assets/images/htb-writeup-Shocker/root.png)

Ahora, podremos irnos al directorio `/root/` y visualizar la flag de altos privilegios.

![](/assets/images/htb-writeup-Shocker/roottxt.png)

Espero que te haya servido de ayuda este *write-up*, si quieres más como estos puedes visitar mi página web.
