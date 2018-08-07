# Date: 06/11/2018
# Author: Pure-L0G1C
# Description: Handshake

from time import sleep 

class Handshake(object):

	def __init__(self, public_key, sess, is_server=False):
		self.public_key = public_key
		self.rec_public_key = None
		self.is_server = is_server
		self.session = sess 

	def public_key_exchange(self):
		if self.is_server:
			sleep(0.1)
			self.session.send(self.public_key)
			self.rec_public_key = self.session.recv(2048)
		else:
			self.rec_public_key = self.session.recv(2048)
			sleep(0.1)
			self.session.send(self.public_key)
		print('Recv Key: {}'.format(self.rec_public_key))

	def handshake(self):
		self.public_key_exchange()
		return self.rec_public_key