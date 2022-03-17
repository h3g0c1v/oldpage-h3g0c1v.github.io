---
layout: single
title: Ransom - Hack The Box
excerpt: "La máquina Ransom es una máquina bastante original, ya que toca un tema bastante interesante, y que personalmente, no sabia que se podía hacer. No voy a decir nada más porque quiero que lo veáis, así que vamos alla."
date: 2022-03-17
classes: wide
header:
  teaser: /assets/images/htb-writeup-ransom/ransom_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - linux
   - Type Juggling Attack
   - Text Plain Attack - Conti Ransomware
   - Information Leakage
---

![](/assets/images/htb-writeup-ransom/ransom_logo.png)


# Reconocimiento

Vamos a empezar escaneando todo el rango de puertos por el protocolo **TCP**, donde el output lo redirigiremos al fichero `allPorts`.

```bash

h3g0c1v@kali:~/htb/ransom$ nmap -p- --open -T5 -v -n 10.10.11.153 -oG allPorts
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-17 12:13 CET
Initiating Ping Scan at 12:13
Scanning 10.10.11.153 [4 ports]
Completed Ping Scan at 12:13, 0.07s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 12:13
Scanning 10.10.11.153 [65535 ports]
Discovered open port 80/tcp on 10.10.11.153
Discovered open port 22/tcp on 10.10.11.153
Completed SYN Stealth Scan at 12:13, 11.83s elapsed (65535 total ports)
Nmap scan report for 10.10.11.153
Host is up (0.031s latency).
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Read data files from: /usr/bin/../share/nmap
Nmap done: 1 IP address (1 host up) scanned in 12.07 seconds
           Raw packets sent: 65872 (2.898MB) | Rcvd: 65536 (2.621MB)


```

Quiero ver un poco más de información sobre esos puertos, por lo que voy a detectar la versión y servicio para los puertos abiertos y lanzaré unos scripts básicos de enumeración.

```bash

h3g0c1v@kali:~/htb/ransom$ nmap -sCV -p22,80 10.10.11.153 -oN targeted
Starting Nmap 7.92 ( https://nmap.org ) at 2022-03-17 12:15 CET
Nmap scan report for 10.10.11.153
Host is up (0.030s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ea:84:21:a3:22:4a:7d:f9:b5:25:51:79:83:a4:f5:f2 (RSA)
|   256 b8:39:9e:f4:88:be:aa:01:73:2d:10:fb:44:7f:84:61 (ECDSA)
|_  256 22:21:e9:f4:85:90:87:45:16:1f:73:36:41:ee:3b:32 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
| http-title:  Admin - HTML5 Admin Template
|_Requested resource was http://10.10.11.153/login
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.09 seconds

```

Y utilizaré la herramienta **whatweb**.

```bash
h3g0c1v@kali:~/htb/ransom$ whatweb http://10.10.11.153
http://10.10.11.153 [302 Found] Apache[2.4.41], Cookies[XSRF-TOKEN,laravel_session], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.10.11.153], Laravel, Meta-Refresh-Redirect[http://10.10.11.153/login], RedirectLocation[http://10.10.11.153/login], Title[Redirecting to http://10.10.11.153/login]
http://10.10.11.153/login [200 OK] Apache[2.4.41], Bootstrap, Cookies[XSRF-TOKEN,laravel_session], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.10.11.153], JQuery[1.9.1], Laravel, PasswordField[password], Script[text/javascript], Title[Admin - HTML5 Admin Template], X-UA-Compatible[IE=edge]
```

Y vemos que nos aplica una redirección a un login, vamos a verlo más en detalle.

![](/assets/images/htb-writeup-ransom/login.png)

Vale, vamos a ver como se tramita la petición, así que vamos a abrir **burpsuite**.

![](/assets/images/htb-writeup-ransom/burp.png)

Y vemos que la petición se tramita por **GET**, así que vamos a intentar cambiar el método.

![](/assets/images/htb-writeup-ransom/changemethod.png)

Y nos dice que el método no está permitido. Si intentamos volver al método **GET** , pero manteniendo la estructura de petición del método **POST**.

![](/assets/images/htb-writeup-ransom/getpost.png)

Observamos que error cambia. Como el error está en **JSON** , voy a intentar enviar la petición con esa estructura, y como ahora la petición está en **JSON** tendremos que ajustar el **Content Type** a *application/json*.

![](/assets/images/htb-writeup-ransom/requestjson.png)

# Type Juggling Attack

¡Ojo! Ahora sí que nos admite la petición. Esto huele un poco a un **Type Juggling Attack**, así que voy a intentarlo.

Para efectuar un **Type Juggling** me ayudé de la siguiente tabla, para realizar distintas inyecciones.

![](/assets/images/htb-writeup-ransom/jugglingtable.png)

Si como contraseña, le enviamos un *true*, y seguimos la petición, vemos que hemos logrado *bypassear* el panel de inicio de sesión.

![](/assets/images/htb-writeup-ransom/attack.png)

![](/assets/images/htb-writeup-ransom/bypass.png)

Y vemos un comprimido, así que vamos a ver que contiene y si podemos abrirlo.

```bash
h3g0c1v@kali:~/htb/ransom$ 7z l uploaded-file-3422.zip     

7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
p7zip Version 16.02 (locale=es_ES.utf8,Utf16=on,HugeFiles=on,64 bits,8 CPUs Intel(R) Core(TM) i5-8265U CPU @ 1.60GHz (806EC),ASM,AES-NI)

Scanning the drive for archives:
1 file, 7735 bytes (8 KiB)

Listing archive: uploaded-file-3422.zip

--
Path = uploaded-file-3422.zip
Type = zip
Physical Size = 7735

   Date      Time    Attr         Size   Compressed  Name
------------------- ----- ------------ ------------  ------------------------
2020-02-25 13:03:22 .....          220          170  .bash_logout
2020-02-25 13:03:22 .....         3771         1752  .bashrc
2020-02-25 13:03:22 .....          807          404  .profile
2021-07-02 19:58:14 D....            0            0  .cache
2021-07-02 19:58:14 .....            0           12  .cache/motd.legal-displayed
2021-07-02 19:58:19 .....            0           12  .sudo_as_admin_successful
2022-03-07 13:32:54 D....            0            0  .ssh
2022-03-07 13:32:25 .....         2610         1990  .ssh/id_rsa
2022-03-07 13:32:46 .....          564          475  .ssh/authorized_keys
2022-03-07 13:32:54 .....          564          475  .ssh/id_rsa.pub
2022-03-07 13:32:54 .....         2009          581  .viminfo
------------------- ----- ------------ ------------  ------------------------
2022-03-07 13:32:54              10545         5871  9 files, 2 folders

```

Para ver un poco más sobre este fichero vamos a utilizar el parámetro *-slt* al final.

```bash
h3g0c1v@kali:~/htb/ransom$ 7z l uploaded-file-3422.zip -slt

7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
p7zip Version 16.02 (locale=es_ES.utf8,Utf16=on,HugeFiles=on,64 bits,8 CPUs Intel(R) Core(TM) i5-8265U CPU @ 1.60GHz (806EC),ASM,AES-NI)

Scanning the drive for archives:
1 file, 7735 bytes (8 KiB)

Listing archive: uploaded-file-3422.zip

--
Path = uploaded-file-3422.zip
Type = zip
Physical Size = 7735

----------
Path = .bash_logout
Folder = -
Size = 220
Packed Size = 170
Modified = 2020-02-25 13:03:22
Created = 
Accessed = 
Attributes = _ -rw-r--r--
Encrypted = +
Comment = 
CRC = 6CE3189B
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .bashrc
Folder = -
Size = 3771
Packed Size = 1752
Modified = 2020-02-25 13:03:22
Created = 
Accessed = 
Attributes = _ -rw-r--r--
Encrypted = +
Comment = 
CRC = AB254644
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .profile
Folder = -
Size = 807
Packed Size = 404
Modified = 2020-02-25 13:03:22
Created = 
Accessed = 
Attributes = _ -rw-r--r--
Encrypted = +
Comment = 
CRC = D1B22A87
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .cache
Folder = +
Size = 0
Packed Size = 0
Modified = 2021-07-02 19:58:14
Created = 
Accessed = 
Attributes = D_ drwx------
Encrypted = -
Comment = 
CRC = 
Method = Store
Host OS = Unix
Version = 10
Volume Index = 0

Path = .cache/motd.legal-displayed
Folder = -
Size = 0
Packed Size = 12
Modified = 2021-07-02 19:58:14
Created = 
Accessed = 
Attributes = _ -rw-r--r--
Encrypted = +
Comment = 
CRC = 00000000
Method = ZipCrypto Store
Host OS = Unix
Version = 10
Volume Index = 0

Path = .sudo_as_admin_successful
Folder = -
Size = 0
Packed Size = 12
Modified = 2021-07-02 19:58:19
Created = 
Accessed = 
Attributes = _ -rw-r--r--
Encrypted = +
Comment = 
CRC = 00000000
Method = ZipCrypto Store
Host OS = Unix
Version = 10
Volume Index = 0

Path = .ssh
Folder = +
Size = 0
Packed Size = 0
Modified = 2022-03-07 13:32:54
Created = 
Accessed = 
Attributes = D_ drwxrwxr-x
Encrypted = -
Comment = 
CRC = 
Method = Store
Host OS = Unix
Version = 10
Volume Index = 0

Path = .ssh/id_rsa
Folder = -
Size = 2610
Packed Size = 1990
Modified = 2022-03-07 13:32:25
Created = 
Accessed = 
Attributes = _ -rw-------
Encrypted = +
Comment = 
CRC = 38804579
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .ssh/authorized_keys
Folder = -
Size = 564
Packed Size = 475
Modified = 2022-03-07 13:32:46
Created = 
Accessed = 
Attributes = _ -rw-------
Encrypted = +
Comment = 
CRC = CB143C32
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .ssh/id_rsa.pub
Folder = -
Size = 564
Packed Size = 475
Modified = 2022-03-07 13:32:54
Created = 
Accessed = 
Attributes = _ -rw-------
Encrypted = +
Comment = 
CRC = CB143C32
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

Path = .viminfo
Folder = -
Size = 2009
Packed Size = 581
Modified = 2022-03-07 13:32:54
Created = 
Accessed = 
Attributes = _ -rw-------
Encrypted = +
Comment = 
CRC = 396B04B4
Method = ZipCrypto Deflate
Host OS = Unix
Version = 20
Volume Index = 0

```

Y vemos que el comprimido está encriptado, si intentamos crackear el hash que nos da la herramienta **zip2john**, no conseguimos nada.

```bash
h3g0c1v@kali:~/htb/ransom$ john --wordlist=/usr/share/wordlists/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
0g 0:00:00:01 DONE (2022-03-17 12:53) 0g/s 12581Kp/s 12581Kc/s 12581KC/s "33Cooper"..*7¡Vamos!
Session completed. 
```

Si analizamos el comprimido encriptado de nuevo, podemos ver que contiene un fichero que probablemente sea igual al que tengamos nosotros. Ese fichero es el `.bash_logout`.
Bien, esto puede ser un problema porque con una herramienta que se llama **bkcrack** , podremos intentar sacar unas *keys* del fichero comprimido encriptado, para poder sacar esos archivos que hay dentro. Vamos a verlo mejor en la práctica.

Primero, tendremos que crear un comprimido con el fichero que creamos que será igual al nuestro, en este caso, el **.bash_logout**.

![](/assets/images/htb-writeup-ransom/textoplanozip.png)

Ahora con la herramienta **bkcrack** sacaremos las **keys** correspondientes al contenido del comprimido encriptado, indicándole el contenido que pensamos que es igual al nuestro, el comprimido que hemos generado que tiene ese contenido igual al del comprimido encriptado, y el nombre de ese archivo que es igual. Sé que es un poco raro, pero ahora cuando lo veais lo vais a entender mejor.

![](/assets/images/htb-writeup-ransom/keys.png)

Bien, nos ha conseguido las keys al archivo comprimido encriptado. Solo queda generar otro archivo comprimido con las keys que hemos sacado, poniéndole una contraseña que nosotros queramos.

![](/assets/images/htb-writeup-ransom/igualzip.png)

Ahora, si visualizamos el contenido del *.zip* que hemos generado con las *keys*, vemos que contiene el mismo contenido, que el comprimido encriptado.

![](/assets/images/htb-writeup-ransom/mismocontenidozip.png)

Únicamente nos queda descomprimir el *.zip* que hemos generado con la contraseña que le hemos puesto. Y veremos que se nos ha descomprimido el contenido del comprimido, que contiene lo mismo que el comprimido encriptado.

![](/assets/images/htb-writeup-ransom/descomprimirzip.png)

En este punto, nos podremos ir a ese directorio **.ssh** tan jugoso, y visualizar la **id_rsa**.

```bash
h3g0c1v@kali:~/htb/ransom$ cd .ssh 
h3g0c1v@kali:~/htb/ransom$ cat id_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

Pero claro, con que usuario nos conectamos. Bueno, pues podemos irnos a la **id_rsa.pub** que normalmente contiene el usuario con el que podemos conectarnos por **SSH** con la **id_rsa**.

![](/assets/images/htb-writeup-ransom/id_rsa_pub.png)

Vemos que es el usuario **htb** con el que nos podemos conectar, así que vamos a ello.

![](/assets/images/htb-writeup-ransom/ssh.png)

En este punto ya podemos visualizar la `user.txt`.

![](/assets/images/htb-writeup-ransom/usertxt.png)

Como estamos en la máquina víctima, podemos intentar encontrar cuál es la contraseña que está igualando, y que es vulnerable a **Type Juggling Attack** en el panel de inicio de sesión. Podemos ver donde se encuentra el **directorio root** de la página web en la ruta de `/etc/apache2/sites-enabled/000-default.conf`.

![](/assets/images/htb-writeup-ransom/documentroot.png)

Y vemos que el **directorio root** está en `/srv/prod/public`. Así que nos movemos a él y nos vamos a un directorio atrás para filtrar por *login*. Y encontramos **AuthController** , por lo que esta vez en vez de filtrar por login, filtraré por **AuthController**.

![](/assets/images/htb-writeup-ransom/filtrar.png)

Si observamos bien, podemos ver que hay un directorio que se encuentra un fichero con el nombre de `AuthController`, así que nos movemos a el, para ver que contiene.

![](/assets/images/htb-writeup-ransom/auth.png)

Contiene un fichero `AuthController.php`, vamos a visualizarlo.

```bash
htb@ransom:/srv/prod/app/Http/Controllers$ cat AuthController.php 
<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use App\Http\Requests\RegisterRequest;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;



class AuthController extends Controller
{
    /**
     * Display login page.
     * 
     * @return \Illuminate\Http\Response
     */
    public function show_login()
    {
        return view('auth.login');
    }



    /**
     * Handle account login
     * 
     */
    public function customLogin(Request $request)
    {
        $request->validate([
            'password' => 'required',
        ]);

        if ($request->get('password') == "UHC-March-Global-PW!") {
            session(['loggedin' => True]);
            return "Login Successful";
        }
  
        return "Invalid Password";
    }

}

```

Y bueno, vemos que la contraseña a la que la está comparando, está en el fichero. Ese el problema del panel de inicio de sesión, como está comparando dos cadenas de caracteres con un **doble igual** , supone que sea vulnerable a **Type Juggling Attack** . Para sanitizar ese problema, únicamente tendríamos que compararlo con un **triple igual**, de esta forma ya no tendremos esa vulnerabilidad.
Si probamos esa misma contraseña que vemos en el fichero para el usuario **root**, vemos que, efectivamente, es la contraseña de root. Por lo que en este punto podremos irnos al directorio `/root/` y visualizar la `root.txt`.

![](/assets/images/htb-writeup-ransom/roottxt.png)

Esta es la máquina *Ransom*, espero que te haya gustado la máquina y te haya parecido interesante la parte del **desencriptado** del comprimido encriptado. Puedes ver más *write-ups* como estos en mi página web.
