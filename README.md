# Loki

Loki is a simple **R**emote **A**ccess **T**ool.<br/>
Loki uses **RSA-2048** with **AES-256** to keep your communication with infected machines secure.<br/>

[![Version](https://img.shields.io/badge/Version-v0.1.1-blue)]()
[![Python](https://img.shields.io/badge/Python-v3.6%2B-blue)]()
[![Discord](https://img.shields.io/badge/Discord-server-blue)](https://discord.gg/Qnvw43r)
[![Donate](https://img.shields.io/badge/PayPal-Donate-orange.svg)](https://www.paypal.me/Msheikh03)
<br/><br/>

<img src="Screenshots/bots.png" atl=""/>

### Requirements

-   Python **3.6.x** | **3.7.x** | **3.8.x**

### Server tested on

-   Windows 10
-   Kali Linux

### Bot tested on

-   Windows 10

### Payload generator tested on

-   Windows 10

### Features

-   Upload & Download
-   Chrome Launching
-   Persistence
-   Screenshare
-   Screenshot
-   Keylogger
-   SFTP
-   SSH

### Video

https://www.youtube.com/watch?v=UTfZlXGoJ5Y

### Installation

```shell
$> pip install -r requirements.txt
```

### Server side

1. Open `/lib/const.py` & configure your private and public IP's
2. Start loki.py
3. Navigate to http://localhost:5000
4. Login

    ```
    Username: loki
    Password: ikol
    ```

5. Start the server on the same IP as your private IP

### Generate a payload

Navigate to agent directory and run the following command

```shell
$> python builder.py -h
```

**It will not compile inside a virtual environment**

### After connection

-   You can click the id of the bot once it connects

### FYI

-   The bot will call the server using the Public IP, not the private IP
-   The bot will call the server using the port specified on the server tab
