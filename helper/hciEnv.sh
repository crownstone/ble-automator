#!/bin/bash
# prints the hci device that supports BLE.
# can be used with other calls for example:
#   sendCommand.py -i`./hciEnv.sh` -a EE:2F:41:99:DE:C0 -m -b -t 1 -d 0 -b

if [[ -n $LEHCI ]]; then
	printf $LEHCI
	exit
fi

for i in `seq 0 10`;
do
	sudo hciconfig hci$i lestates &> /dev/null
	# sudo hciconfig hci$i lestates
	if [[ $? == 0 ]]; then
		export LEHCI=hci$i
		printf "hci$i"
		exit
	fi
done