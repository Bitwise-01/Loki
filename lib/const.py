# Date: 08/13/2018
# Author: Pure-L0G1C
# Description: Config file

from os import path, makedirs

# database 
DATABASE = 'lib/database.db'

# account
LOCK_TIME = 300 # in seconds
MAX_FAILED_ATTEMPTS = 3 # attempts before locking

# ip 
PRIVATE_IP = '127.0.0.1' 
PUBLIC_IP = '127.0.0.1'

# port
FTP_PORT = 128
SSH_PORT = 256
CNC_PORT = 512 # command and control port

if not path.exists('lib/cert'):
 makedirs('lib/cert')

CERT_FILE = 'lib/cert/public.crt'
KEY_FILE = 'lib/cert/private.key'