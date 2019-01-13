# Date: 07/02/2018
# Author: Pure-L0G1C
# Description: DBMS

import bcrypt
import sqlite3
from . import const
from time import time
from os import urandom
from hashlib import sha256
from base64 import b64encode
from datetime import datetime

class Database(object):

    def __init__(self):
        self.db_path = const.DATABASE
        self.create_tables()
        self.create_default_account()

    def create_tables(self):
        self.db_create('''
         CREATE TABLE IF NOT EXISTS
         Account(
                 user_id TEXT PRIMARY KEY,
                 username TEXT,
                 password TEXT
                );
         ''')

        self.db_create('''
         CREATE TABLE IF NOT EXISTS
         Status(
                last_online INTEGER,
                date_created INTEGER,
                stat_id TEXT NOT NULL,
                FOREIGN KEY(stat_id) REFERENCES Account(user_id)
               );
         ''')

        self.db_create('''
         CREATE TABLE IF NOT EXISTS
         Attempt(
                 last_attempt INTEGER,
                 attempts_made INTEGER,
                 ampt_id TEXT NOT NULL,
                 FOREIGN KEY(ampt_id) REFERENCES Account(user_id)
                );
         ''')

        self.db_create('''
         CREATE TABLE IF NOT EXISTS
         Lock(
              time_locked INTEGER DEFAULT 0,
              lock_id TEXT NOT NULL,
              FOREIGN KEY(lock_id) REFERENCES Account(user_id)
             );
         ''')

    def add_account(self, username, password):
        username = username.lower()
        user_id = self.gen_user_id(username, password)
        hashed_password = self.hash_password(password)

        self.db_update('''
         INSERT INTO Account(user_id, username, password)
         VALUES(?, ?, ?);
         ''', [user_id, username, hashed_password])

        self.db_update('''
         INSERT INTO Status(last_online, date_created, stat_id)
         VALUES(?, ?, ?);
        ''', [time(), time(), user_id])

        self.db_update('''
         INSERT INTO Attempt(last_attempt, attempts_made, ampt_id)
         VALUES(?, ?, ?);
        ''', [time(), 0, user_id])

        self.db_update('''
         INSERT INTO Lock(lock_id)
         VALUES(?);
        ''', [user_id])

    def account_exists(self, username):
        database = sqlite3.connect(self.db_path)
        data = self.db_query('SELECT * FROM Account WHERE username=?;', [username], False)
        return True if len(data) else False

    def compare_passwords(self, user_id, password):
        hashed_password = self.db_query('SELECT password FROM Account WHERE user_id=?;', [user_id])
        return True if bcrypt.hashpw(password.encode('utf-8'), hashed_password) == hashed_password else False

    def check_password(self, username, password):
        hashed_password = self.db_query('SELECT password FROM Account WHERE username=?;', [username])
        return True if bcrypt.hashpw(password.encode('utf-8'), hashed_password) == hashed_password else False

    def authenticate(self, username, password):
        username = username.lower()
        if self.account_exists(username):
            user_id = self.get_user_id(username)
            if not self.is_locked(user_id):
                if self.check_password(username, password):
                    return self.get_user_id(username)
                else:
                    self.failed_attempt(user_id)
        return None

    def is_empty(self):
        data = self.db_query('SELECT * FROM Account;', [], False)
        return False if len(data) else True

    def create_default_account(self):
        if self.is_empty():
            self.add_account('loki', 'ikol')

    # -------- Attempts -------- #

    def lock_account(self, user_id):
        self.db_update('UPDATE Lock SET time_locked=? WHERE lock_id=?;', [time(), user_id])

    def failed_attempt(self, user_id):
        current_value = self.failed_attempts_counts(user_id)
        if current_value >= const.MAX_FAILED_ATTEMPTS:
            self.lock_account(user_id)
        else:
            self.db_update('UPDATE Attempt SET attempts_made=? WHERE ampt_id=?;', [current_value + 1, user_id])

    def failed_attempts_counts(self, user_id):
        return self.db_query('SELECT attempts_made FROM Attempt WHERE ampt_id=?;', [user_id])

    def is_locked(self, user_id):
        time_locked = self.locked(user_id)
        if time_locked:
            if (time() - time_locked) >= const.LOCK_TIME:
                self.remove_locked_account(user_id)
                return False
            else:
                return True
        else:
            return False

    def locked(self, user_id):
        return self.db_query('''
         SELECT time_locked
         FROM Lock
         INNER JOIN Account ON account.user_id = Lock.lock_id
         WHERE Lock.lock_id=?;
         ''', [user_id])

    def remove_locked_account(self, user_id):
        self.db_update('UPDATE Attempt SET attempts_made=? WHERE ampt_id=?;', [0, user_id])

# -------- Database Wrappers -------- #

    def db_query(self, cmd, args, fetchone=True):
        database = sqlite3.connect(self.db_path)
        sql = database.cursor().execute(cmd, args)
        data = sql.fetchone()[0] if fetchone else sql.fetchall()
        database.close()
        return data

    def db_update(self, cmd, args):
        database = sqlite3.connect(self.db_path)
        database.cursor().execute(cmd, args)
        database.commit()
        database.close()

    def db_create(self, cmd):
        database = sqlite3.connect(self.db_path)
        database.cursor().execute(cmd)
        database.commit()
        database.close()

# -------- Update -------- #

    def update_password(self, user_id, password):
        hashed_password = self.hash_password(password)
        self.db_update('UPDATE Account SET password=? WHERE user_id=?;', [hashed_password, user_id])

    def update_username(self, user_id, username):
        self.db_update('UPDATE Account SET username=? WHERE user_id=?;', [username.lower(), user_id])

# -------- Misc -------- #

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def gen_user_id(self, username, password):
        _username = username.encode('utf-8') + urandom(64 * 1024)
        _password = password.encode('utf-8') + urandom(64 * 1024)
        _username_password = b64encode(_username + _password + urandom(64 * 64))
        secure_hash = sha256(_username_password).digest().hex()
        return secure_hash

    def get_date_created(self, user_id):
        return self.db_query('SELECT date_created FROM Status WHERE stat_id=?;', [user_id])

    def get_user_id(self, username):
        return self.db_query('SELECT user_id FROM Account WHERE username=?;', [username])

    def get_last_active(self, user_id):
        epoch_time = self.db_query('SELECT last_online FROM Status WHERE stat_id=?;', [user_id])
        self.db_update('UPDATE Status SET last_online=? WHERE stat_id=?;', [time(), user_id])
        return datetime.fromtimestamp(epoch_time).strftime('%b %d, %Y at %I:%M %p')

    def get_account_status(self, user_id, username):
        default_username = 'loki'
        default_password = 'ikol'

        username = username.lower()
        is_same_password = self.compare_passwords(user_id, default_password)

        if all([username == default_username, is_same_password]):
            status = '** Please consider changing your username and password **'
        elif username == default_username:
            status = '** Please consider changing your username **'
        elif is_same_password:
            status = '** Please consider changing your passsword **'
        else:
            status = None
        return status