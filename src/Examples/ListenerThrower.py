'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this 
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, 
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
permit persons to whom the Software is furnished to do so, subject to the following 
conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
import datetime, sys
openStatus = True

if sys.version_info >= (3, 0):
	raw_input = input

from Yowsup.connectionmanager import YowsupConnectionManager

class WhatsappListenerThrower(object):
	
	def __init__(self, keepAlive = False, sendReceipts = False, recipientNumber = '0', chatLog = 'yowsup-chat.log'):
		
		# in class 'global' constants
		self.sendReceipts = sendReceipts
		self.recipientNumber = recipientNumber
		self.chatLog = chatLog
		
		connectionManager = YowsupConnectionManager()
		connectionManager.setAutoPong(keepAlive)

		self.signalsInterface = connectionManager.getSignalsInterface()
		self.methodsInterface = connectionManager.getMethodsInterface()
		
		self.signalsInterface.registerListener("message_received", self.onMessageReceived)
		self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
		self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
		self.signalsInterface.registerListener("disconnected", self.onDisconnected)
		
		self.cm = connectionManager
    
	
	def login(self, username, password):
		self.username = username
		self.methodsInterface.call("auth_login", (username, password))
		while openStatus:
			raw_input()


	def onAuthSuccess(self, username):
		print("Authed %s" % username)
		self.methodsInterface.call("ready")

	def onAuthFailed(self, username, err):
		print("Auth Failed!")

	def onDisconnected(self, reason):
		print("Disconnected because %s" %reason)
		print("hell")
		#if reason == 'close':
		sys.exit("exiting")

	def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadCast):
		formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
		print("%s [%s]:%s"%(jid, formattedDate, messageContent))
		
		# for saving to log find/replace:
		# 	; to \c
		#	" (double quote) to \q
		#	, to ;
		# and then saving in CSV format
		sanitizedMessage = messageContent.replace(';','\c')	
		sanitizedMessage = sanitizedMessage.replace('"','\q')
		sanitizedMessage = sanitizedMessage.replace(',',';')
		sanitizedMessage = "\\n".join(sanitizedMessage.split("\n"))
		with open(self.chatLog, 'a') as chatlog:
				chatlog.write("%s,%s,%s,%s\n"%(timestamp, jid, formattedDate, sanitizedMessage))
				
		# the message received from a Tx number is then relayed to an Rx number
		# that is Jabber ID e.g. "6281xxxxx@s.whatsapp.net'
		if self.recipientNumber != '0':
			self.TxJID = jid.split('@')[0]
			self.jDomain = 's.whatsapp.net'
			self.Rx = [self.recipientNumber, self.jDomain]
			self.RxJID = "@".join(self.Rx)
			self.TxMessage = [self.TxJID, messageContent]
			self.relayedMessage = " - ".join(self.TxMessage)
			self.methodsInterface.call("message_send", (self.RxJID, self.relayedMessage))
		if wantsReceipt and self.sendReceipts:
			self.methodsInterface.call("message_ack", (jid, messageId))

	
