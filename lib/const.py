# Date: 08/13/2018
# Author: Pure-L0G1C
# Description: Config file

from os import path, makedirs

################
#    READ ME   #
################
#######################################################################################################
### This is only required if you are connecting to computers outside of your network ###
#
# If you are connecting to computers outside
# of your network, you must enable port forwarding
# on your router. You must have have the FTP_PORT, SSH_PORT
# and the port you started the server on open on your router. Both the FTP_PORT and SSH_PORT
# can be confirgured below.
#
# You must also set the PRIVATE_IP as the ip of your computer
# and set the PUBLIC_IP as your public ip.
#
#######################################################################################################

# ip
PRIVATE_IP = '127.0.0.1'
PUBLIC_IP = '127.0.0.1'

# ports
FTP_PORT = 128
SSH_PORT = 256

# database
DATABASE = 'database/database.db'

if not path.exists('database'):
    makedirs('database')

# account
LOCK_TIME = 300  # in seconds
MAX_FAILED_ATTEMPTS = 3  # attempts before locking

# cert
if not path.exists('cert'):
    makedirs('cert')

CERT_FILE = 'cert/public.crt'
KEY_FILE = 'cert/private.key'
