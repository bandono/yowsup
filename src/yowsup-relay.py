#!/usr/bin/python

'''
Copyright (c) <2014> Arif Kusbandono <arif.imap@gmail.com>
This has been modular block takeout from yowsup-cli in yowsup/src:

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

import os, sys, csv
from Yowsup.Common.utilities import Utilities
from Yowsup.Common.debugger import Debugger
from Examples.ListenerThrower import WhatsappListenerThrower
import base64

DEFAULT_CONFIG = os.path.expanduser("~")+"/.yowsup/auth"
COUNTRIES_CSV = "countries.csv"
def getCredentials(config = DEFAULT_CONFIG):
	if os.path.isfile(config):
		f = open(config)
		
		phone = ""
		idx = ""
		pw = ""
		cc = ""
		
		try:
			for l in f:
				line = l.strip()
				if len(line) and line[0] not in ('#',';'):
					
					prep = line.split('#', 1)[0].split(';', 1)[0].split('=', 1)
					
					varname = prep[0].strip()
					val = prep[1].strip()
					
					if varname == "phone":
						phone = val
					elif varname == "id":
						idx = val
					elif varname =="password":
						pw =val
					elif varname == "cc":
						cc = val

			return (cc, phone, idx, pw);
		except:
			pass

	return 0
def dissectPhoneNumber(phoneNumber):
	try:
		with open(COUNTRIES_CSV, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			for row in reader:
				if len(row) == 3:
					country, cc, mcc = row
				else:
					country,cc = row
					mcc = "000"
				try:
					if phoneNumber.index(cc) == 0:
						print("Detected cc: %s"%cc)
						return (cc, phoneNumber[len(cc):])
                
				except ValueError:
					continue
    
	except:
		pass
	return False

credentials = getCredentials("config.example")
if credentials:
    
    countryCode, login, identity, password = credentials
    
    identity = Utilities.processIdentity(identity)
    password = base64.b64decode(bytes(password.encode('utf-8')))
    
    if countryCode:
        phoneNumber = login[len(countryCode):]
    else:
        dissected = dissectPhoneNumber(login)
        if not dissected:
            sys.exit("ERROR. Couldn't detect cc, you have to manually place it your config")
        countryCode, phoneNumber = dissected

    Debugger.enabled = False
    wa = WhatsappListenerThrower(keepAlive = True, sendReceipts = True, \
		recipientNumber = '62xxxxxxxxx', autoReplyConst = 60, \
		autoReplyMsg = 'This is XXXX\'s bot. Your message will be forwarded to +62xxxxxxxxx' )
    wa.login(login, password)
