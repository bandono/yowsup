#!/bin/bash
#
# yowsup-relay-watch.sh
#
# Copyright (c) <2014> Arif Kusbandono <arif.imap@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software 
# without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to 
# permit persons to whom the Software is furnished to do so, subject to the following 
# conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
# A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# -------------------------------------------------------------------------------------
# "scriptFolder" must match yowsup tree location
# in this case yowsup tree is under /usr/local/yowsup
# the script will maintain connection by:
# 1. starting yowsup-relay.py
# 2. monitoring "Disconnection" status
# 3. kill yowsup-relay.py process and then restarting it if disconnection
#    detected
# 4. new yowsup-relay.py process will not be started if there is already previous process
#    detected (this script will exit)

scriptFolder='/usr/local/yowsup/src'
pythonEnv='python'
yowsupRelay='yowsup-relay.py'
yowsupArg=''
logFolder=$scriptFolder
connStatFile='yowsup-conn.status'
pidFile="$logFolder/yowsup-relay.pid"

# switch to script folder location
cd $scriptFolder

while true; do
	# check whether previous relay process exist
	pidCheck=`ps auxx | grep $yowsupRelay | grep -v grep | awk '{print $2}' | wc -l`
	if [ "$pidCheck" == "0" ]; then
		if [ -f $pidFile ]; then
		
			# remove PID file and empty connection status file
			rm $pidFile
		fi
		if [ -f $connStatFile ]; then		
			# remove PID file and empty connection status file
			cat /dev/null > $connStatFile
		fi
		
		# run yowsup relay, fork, and record PID in file		
		$pythonEnv $yowsupRelay $yowsupArg &
		echo $! > $pidFile
		
		# check connection status thrown to file
		sleep 4
		connStatus=`tail -1 $connStatFile | grep Disconnected | wc -l`
		while [ "$connStatus" == "0" ]; do
			sleep 1
			connStatus=`tail -1 $connStatFile | grep Disconnected | wc -l`
		done
		
		kill -9 `cat $pidFile`
		sleep 5 
	else
		# previous relay process exists, exiting
		echo "[yowsup-relay]: yowsup-relay already running"
		exit 1
	fi
done
