# Loki

Loki is Remote Access Tool.<br/>
Loki uses **RSA-2048** with **AES-256** to keep your communication secure.

__Warning:__ 
* This program is still in beta mode; I'm not done yet.
* Communication will be a bit slow due to the security.

### Requirements
* Python **3.x.x**

### Installation
```sh
pip install -r requirements.txt
```

### Server side
1) open /lib/const.py & configure your private and public IP's
2) start loki.py
3) navigate to http://127.0.0.1:5000
4) login, Username: loki Password: ikol
5) navigate to settings, selected server tab and start the server on the same IP as your private IP
6) Click the home button 

### Client side
1) open /bot/bot.py and scroll to the bottom and change the ip and port
2) start the bot.py

### After connection
1) You can click the hostname of the bot once it connects 
2) Explore 

### Contribution
If you can Python or Web-dev, I need your help.