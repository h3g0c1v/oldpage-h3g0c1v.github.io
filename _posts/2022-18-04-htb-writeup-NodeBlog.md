---
layout: single
title: NodeBlog - Hack The Box
excerpt: ""
date: 2022-04-18
classes: wide
header: 
  teaser: /assets/images/htb-writeup-nodeblog/nodeblog_logo.png
  teaser_home_page: true
  icon: /assets/images/hackthebox.webp
categories:
   - hackthebox
   - infosec
tags:
   - NoSQL Injection (Authentication Bypass)
   - XXE File Read
   - NodeJS Deserialization Attack
   - Mongo Database Enumeration
---

![](/assets/images/htb-writeup-nodeblog/nodeblog_logo.png)

# Reconocimiento

Empezaremos reralizando un escaneo de los **65525** puertos **TCP** , en caso de que no haya por TCP podremos escanear por **UDP**.

```bash
❯ nmap -sS --min-rate 5000 -p- --open -vvv -Pn 10.10.11.139 -oG allPorts
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-18 12:01 CEST
Initiating Parallel DNS resolution of 1 host. at 12:01
Completed Parallel DNS resolution of 1 host. at 12:01, 0.00s elapsed
DNS resolution of 1 IPs took 0.00s. Mode: Async [#: 2, OK: 0, NX: 1, DR: 0, SF: 0, TR: 1, CN: 0]
Initiating SYN Stealth Scan at 12:01
Scanning 10.10.11.139 [65535 ports]
Discovered open port 22/tcp on 10.10.11.139
Discovered open port 5000/tcp on 10.10.11.139
Completed SYN Stealth Scan at 12:02, 10.39s elapsed (65535 total ports)
Nmap scan report for 10.10.11.139
Host is up, received user-set (0.035s latency).
Scanned at 2022-04-18 12:01:59 CEST for 10s
Not shown: 65533 closed tcp ports (reset)
PORT     STATE SERVICE REASON
22/tcp   open  ssh     syn-ack ttl 63
5000/tcp open  upnp    syn-ack ttl 63
```

Para despues detectar la versión y servicio que corren para los puertos abiertos reportados en el escaneo de *nmap*.

```bash
❯ nmap -sCV -p22,5000 10.10.11.139 -oN targeted
Starting Nmap 7.92 ( https://nmap.org ) at 2022-04-18 12:03 CEST
Nmap scan report for 10.10.11.139
Host is up (0.033s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 ea:84:21:a3:22:4a:7d:f9:b5:25:51:79:83:a4:f5:f2 (RSA)
|   256 b8:39:9e:f4:88:be:aa:01:73:2d:10:fb:44:7f:84:61 (ECDSA)
|_  256 22:21:e9:f4:85:90:87:45:16:1f:73:36:41:ee:3b:32 (ED25519)
5000/tcp open  http    Node.js (Express middleware)
|_http-title: Blog
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Vemos que en el puerto **5000** corre **HTTP** , por lo que, con la herramienta **whatweb** veré un poco mas de información sobre ella.

```bash
❯ whatweb http://10.10.11.139:5000
http://10.10.11.139:5000 [200 OK] Bootstrap, Country[RESERVED][ZZ], HTML5, IP[10.10.11.139], Script[JavaScript], Title[Blog], X-Powered-By[Express], X-UA-Compatible[IE=edge]
```
Y bueno, no nos dice gran cosa, así que vamos a verlo mejor desde el navegador.

![](/assets/images/htb-writeup-nodeblog/node.png)

Vemos que hay un boton para registrarnos. Si probamos a hacer un poco de **password guessing** conseguiremos saber cual es el usuario, ya que si introducimos de usuario *admin* y de contraseña cualquier contraseña, podremos ver que nos pone *Invalid Password*.

![](/assets/images/htb-writeup-nodeblog/login.png)

En caso de que probemos cualquier combinación veremos que nos pondrá *Invalid Username*.

![](/assets/images/htb-writeup-nodeblog/invalid.png)

Voy a hacer unas cuantas pruebas con este panel de registro, por lo que me abriré el **BurpSuite Comunity Edition** para capturar la petición.

![](/assets/images/htb-writeup-nodeblog/burp.png)


