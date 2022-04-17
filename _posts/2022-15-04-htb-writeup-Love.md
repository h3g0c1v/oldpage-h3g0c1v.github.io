---
layout: single
title: Love - Hack The Box
excerpt: ""
date: 2022-04-15
classes: wide
header: 
  teaser: /assets/images/htb-writeup-love/love_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - Windows
   - Server Side Request Forguery (SSRF)
   - Exploiting Voting System
   - Abusing AlwaysInstallElevated
---

![](/assets/images/htb-writeup-love/love_logo.png)

# Reconocimiento

Empezaremos con la fase de reconocimiento, para ello escanearemos todos los **65536** puertos TCP que hay.

```bash
❯ nmap -sS --min-rate 5000 -p- --open -vvv -Pn 10.10.10.239 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-16 10:53 CEST
Initiating Parallel DNS resolution of 1 host. at 10:53
Completed Parallel DNS resolution of 1 host. at 10:53, 0.32s elapsed
DNS resolution of 1 IPs took 0.32s. Mode: Async [#: 1, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 10:53
Scanning 10.10.10.239 [65535 ports]
Discovered open port 445/tcp on 10.10.10.239
Discovered open port 443/tcp on 10.10.10.239
Discovered open port 80/tcp on 10.10.10.239
Discovered open port 139/tcp on 10.10.10.239
Discovered open port 135/tcp on 10.10.10.239
Discovered open port 3306/tcp on 10.10.10.239
Discovered open port 49666/tcp on 10.10.10.239
Discovered open port 5000/tcp on 10.10.10.239
Discovered open port 49669/tcp on 10.10.10.239
Discovered open port 5040/tcp on 10.10.10.239
Discovered open port 5985/tcp on 10.10.10.239
Discovered open port 5986/tcp on 10.10.10.239
Discovered open port 7680/tcp on 10.10.10.239
Discovered open port 47001/tcp on 10.10.10.239
Discovered open port 49665/tcp on 10.10.10.239
Discovered open port 49667/tcp on 10.10.10.239
Discovered open port 49664/tcp on 10.10.10.239
Discovered open port 49668/tcp on 10.10.10.239
Discovered open port 49670/tcp on 10.10.10.239
Completed SYN Stealth Scan at 10:53, 25.48s elapsed (65535 total ports)
Nmap scan report for 10.10.10.239
Host is up, received user-set (0.11s latency).
Scanned at 2022-04-16 10:53:10 CEST for 26s
Not shown: 63885 closed tcp ports (reset), 1631 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT      STATE SERVICE      REASON
80/tcp    open  http         syn-ack ttl 127
135/tcp   open  msrpc        syn-ack ttl 127
139/tcp   open  netbios-ssn  syn-ack ttl 127
443/tcp   open  https        syn-ack ttl 127
445/tcp   open  microsoft-ds syn-ack ttl 127
3306/tcp  open  mysql        syn-ack ttl 127
5000/tcp  open  upnp         syn-ack ttl 127
5040/tcp  open  unknown      syn-ack ttl 127
5985/tcp  open  wsman        syn-ack ttl 127
5986/tcp  open  wsmans       syn-ack ttl 127
7680/tcp  open  pando-pub    syn-ack ttl 127
47001/tcp open  winrm        syn-ack ttl 127
49664/tcp open  unknown      syn-ack ttl 127
49665/tcp open  unknown      syn-ack ttl 127
49666/tcp open  unknown      syn-ack ttl 127
49667/tcp open  unknown      syn-ack ttl 127
49668/tcp open  unknown      syn-ack ttl 127
49669/tcp open  unknown      syn-ack ttl 127
49670/tcp open  unknown      syn-ack ttl 127
```

Ahora, detectaremos la versión y servicio que corren bajo todos los puertos abiertos que nos ha reportado *nmap*.


```bash
❯ nmap -sCV -p80,135,139,443,445,3306,5000,5040,5985,5986,7680,47001,49664,49665,49666,49667,49668,49669,49670 10.10.10.239 -oN targeted
Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-16 11:00 CEST
Nmap scan report for 10.10.10.239
Host is up (0.11s latency).

PORT      STATE  SERVICE      VERSION
80/tcp    open   http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Voting System using PHP
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
135/tcp   open   msrpc        Microsoft Windows RPC
139/tcp   open   netbios-ssn  Microsoft Windows netbios-ssn
443/tcp   open   ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: 403 Forbidden
| tls-alpn: 
|_  http/1.1
|_ssl-date: TLS randomness does not represent time
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Not valid before: 2021-01-18T14:00:16
|_Not valid after:  2022-01-18T14:00:16
445/tcp   open   microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
3306/tcp  open   mysql?
| fingerprint-strings: 
|   DNSStatusRequestTCP, Help, RTSPRequest, SSLSessionReq, TerminalServerCookie, X11Probe, afp, giop: 
|_    Host '10.10.14.6' is not allowed to connect to this MariaDB server
5000/tcp  open   http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: 403 Forbidden
5040/tcp  open   unknown
5985/tcp  closed wsman
5986/tcp  closed wsmans
7680/tcp  open   pando-pub?
47001/tcp closed winrm
49664/tcp open   msrpc        Microsoft Windows RPC
49665/tcp open   msrpc        Microsoft Windows RPC
49666/tcp open   msrpc        Microsoft Windows RPC
49667/tcp open   msrpc        Microsoft Windows RPC
49668/tcp open   msrpc        Microsoft Windows RPC
49669/tcp open   msrpc        Microsoft Windows RPC
49670/tcp open   msrpc        Microsoft Windows RPC
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3306-TCP:V=7.92%I=7%D=4/16%Time=625A85BC%P=x86_64-pc-linux-gnu%r(RT
SF:SPRequest,49,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x2
SF:0allowed\x20to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(DNSSta
SF:tusRequestTCP,49,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20no
SF:t\x20allowed\x20to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(He
SF:lp,49,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x20allowe
SF:d\x20to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(SSLSessionReq
SF:,49,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x20allowed\
SF:x20to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(TerminalServerC
SF:ookie,49,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x20all
SF:owed\x20to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(X11Probe,4
SF:9,"E\0\0\x01\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x20allowed\x2
SF:0to\x20connect\x20to\x20this\x20MariaDB\x20server")%r(afp,49,"E\0\0\x01
SF:\xffj\x04Host\x20'10\.10\.14\.6'\x20is\x20not\x20allowed\x20to\x20conne
SF:ct\x20to\x20this\x20MariaDB\x20server")%r(giop,49,"E\0\0\x01\xffj\x04Ho
SF:st\x20'10\.10\.14\.6'\x20is\x20not\x20allowed\x20to\x20connect\x20to\x2
SF:0this\x20MariaDB\x20server");
Service Info: Hosts: www.example.com, LOVE, www.love.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time: 
|   date: 2022-04-16T09:24:48
|_  start_date: N/A
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled but not required
|_clock-skew: mean: 2h41m34s, deviation: 4h02m31s, median: 21m32s
| smb-os-discovery: 
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: Love
|   NetBIOS computer name: LOVE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2022-04-16T02:24:50-07:00
```

Como veo que hay una página web por **HTTP** utilizaré la herramienta *whatweb* para ver un poco mas de información sobre ella.

```bash
❯ whatweb http://10.10.10.239
http://10.10.10.239 [200 OK] Apache[2.4.46], Bootstrap, Cookies[PHPSESSID], Country[RESERVED][ZZ], HTML5, HTTPServer[Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27], IP[10.10.10.239], JQuery, OpenSSL[1.1.1j], PHP[7.3.27], PasswordField[password], Script, Title[Voting System using PHP], X-Powered-By[PHP/7.3.27], X-UA-Compatible[IE=edge]
```
No nos dice mucha información, así que vamos a verla mas detalladamente desde el navegador.

![](/assets/images/htb-writeup-love/votingSystem.png)

Y vemos un panel de logueo. Si probamos a buscar vulnerabilidades sobre *Voting System*, vemos que hay unas cuantas.

![](/assets/images/htb-writeup-love/searchSploit.png)

Si nos fijamos en el resultado de *nmap* veremos que en el puerto **443** que es por **HTTPS**, hay un dominio, por lo que lo añadiré al fichero `/etc/hosts/`

```bash
❯ cat /etc/hosts
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: /etc/hosts
       │ Size: 224 B
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   kali
   3   │ 
   4   │ # The following lines are desirable for IPv6 capable hosts
   5   │ ::1     localhost ip6-localhost ip6-loopback
   6   │ ff02::1 ip6-allnodes
   7   │ ff02::2 ip6-allrouters
   8   │ 
   9   │ 10.10.10.239    love.htb staging.love.htb
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Y si ahora probamos a acceder con el dominio *staging.love.htb*, nos aparecerá un resultado distinto.

![](/assets/images/htb-writeup-love/domain.png)

Investigando la página veremos que hay un campo donde podemos hacer pruebas, por lo que vamos a probar algunas cosas.

![](/assets/images/htb-writeup-love/vulnerable.png)

Voy a montarme un servidor en *python3* para ver si me llega una posible petición, introduciendo mi dirección IP en el campo.

![](/assets/images/htb-writeup-love/proofget.png)

Vemos que nos llega la petición *GET* que hemos tramitado, pero, de momento, poco podemos hacer con esto.

![](/assets/images/htb-writeup-love/get.png)


# Server Side Request Forgery (SSRF)

Si miramos la página por el puerto **443** sin introducir los dominios, vemos que nos pone *Forbidden*, pero que pasa si intento ver el contenido desde el propio panel que hemos encontrado, para ver si es vulnerable a un posible *Server Side Request Forgery*

![](/assets/images/htb-writeup-love/nada.png)

No pasa nada, pero si nos volvemos al fichero `targeted`, veremos que hay otra página web por **HTTP** por el puerto **5000**. Vamos a ver que hay dentro de ella.

![](/assets/images/htb-writeup-love/forbidden5000.png)

Bien, y si probamos ahora con el campo del *File Security Checker*, mirar si podemos ver el contenido real de esa página..

![](/assets/images/htb-writeup-love/creds.png)

Y bueno, es vulnerable parece ser, asi que nos vamos a guardar las credenciales que hemos encontrado.

Si probamos las credenciales para conectarnos a **SMB** vemos que no podemos.

```bash
❯ smbmap -H 10.10.10.239 -u 'admin' -p '@LoveIsInTheAir!!!!'
[!] Authentication error on 10.10.10.239
```


# Remote Code Execution (RCE)

Volviendo al panel del *Voting System*, vimos que había algunas vulnerabilidades, pero en las mas jugosas necesitabamos de credenciales. Ahora que tenemos credenciales, vamos a volver a mirar y a ver cual puede ser funcional.

![](/assets/images/htb-writeup-love/searchSploit.png)

Vemos que hay una vulnerabilidad que nos permite ejecutar comandos de forma remota (**RCE**) a través de la subida de un fichero, asi que vamos a probarlo.

![](/assets/images/htb-writeup-love/script.png)

Tendremos que configurar el script con los correspondientes datos.

Algo importante aquí es que si miramos el script en que ruta está intentando subir el fichero, vemos que lo está intentando hacer sobre `/votesystem/admin/loquesea`. Si miramos nuestra página veremos que no existe la direccion de *votesystem*, así que tendremos que eliminar dicha palabra para que pueda funcinar el exploit. El script debería de quedar de la siguiente forma adecuando los parametros a los suyos correspondientes.

![](/assets/images/htb-writeup-love/rce.png)

Ahora nos pondremos en escucha por el puerto indicado en el script (haciendo uso de **rlwrap** ya que es una máquina Windows) para que el exploit nos mande la *reverse shell*.

![](/assets/images/htb-writeup-love/reverse.png)


# Acceso a la Máquina Víctima (user.txt)

Y estamos dentro. Ahora si nos vamos al directorio del usuario con pocos privilegios, podremos visualizar la flag.

![](/assets/images/htb-writeup-love/usertxt.png)


# Abusing AlwaysInstallElevated

Vamos a realizar un reconocimiento exaustivo del sistema, para ello utilizare **WinPEAS**, y cuando terminemos lo investigaremos a fondo a ver como podemos escalar privilegios.

Investigando lo que nos ha reportado el *WinPEAS* vemos que la variable **AlwaysInstallElevated** está activada, y con eso se puede tensar la cosa, ya que se puede exploitar para conseguir escalar privilegios.

![](/assets/images/htb-writeup-love/alwaysinstallelevated.png)

Para asegurarnos que está activo podemos ejecutar los siguientes comandos y veremos que las dos variables estan habilitadas.

![](/assets/images/htb-writeup-love/variables.png)

Para exploitar esto, primero debemos de crear un payload malicioso que se encargue de entablarnos una reverse shell a nuestro equipo, y lo exportaremos en formato *.msi*.

![](/assets/images/htb-writeup-love/always.png)


# NT AUTHORITY\SYSTEM (root.txt)

De esta forma si ahora nos lo compartimos a la máquina victima y lo instalamos haciendo uso de **msiexec**, vemos como si nos ponemos en escucha por el puerto indicado en el payload, nos va a entablar una reverse shell para ganar acceso a la máquina como **NT AUTHORITY\SYSTEM**.

![](/assets/images/htb-writeup-love/nt.png)

Ahora si nos vamos al directorio `C:\Users\Administrator\Desktop` podremos visualizar la flag de altos privilegios.

![](/assets/images/htb-writeup-love/roottxt.png)

Espero que te haya gustado esta máquina, habiendo explotado algo diferente. Yo la verdad que no lo conocía y se me hizo bastante interesante.
