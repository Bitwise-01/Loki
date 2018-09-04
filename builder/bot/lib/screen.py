# Date: 08/13/2018
# Author: Pure-L0G1C
# Description: Screen shot

from mss import mss
from os import path, remove

file = path.dirname(sys.executable[:-2]) + path.sep + 'screen.png' if hasattr(sys, 'frozen') else 'screen.png' 

def screenshot():
 with mss() as sct:
  sct.shot(mon=-1, output=file) 
  
def clean_up():
 if path.exists(file):
  try:
   remove(file)
  except:
   pass 
