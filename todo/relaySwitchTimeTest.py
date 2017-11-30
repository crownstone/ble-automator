#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from Bluenet import *
import time
import datetime

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address>\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4',
									version='0.1')

		parser.add_option('-a', '--address',
				action='store',
				dest="address",
				type="string",
				default=None,
				help='DFU target address. (Can be found by running "hcitool lescan")'
				)
		parser.add_option('-i', '--interface',
				action='store',
				dest="interface",
				type="string",
				default="hci0",
				help='HCI interface to be used.'
				)
		parser.add_option('-v', '--verbose',
				action='store_true',
				dest="verbose",
				help='Be verbose.'
				)

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)

	if (not options.address):
		parser.print_help()
		exit(2)

	ble = BleAutomator(options.interface, options.verbose)

	# Connect to peer device.
	if (not ble.connect(options.address)):
		print "failed to connect"
		exit(1)

	# Switch the relay on and off quickly until the crownstone resets
#	for t in range(10,0,-1):
	turnOnCount = 1
	turnOffCount = 1
	while (True):
		# timeSkip = time between on and off
		#timeSkip = t/10.0
		timeSkip = 0.1

		# chargeTime = time between off and on
		chargeTime = 0.1
		#chargeTime = t/10.0

		print str(datetime.datetime.now()), 'turn on', turnOnCount
		turnOnCount += 1
		startTime = time.time()
		if (not ble.writeCharacteristic(CHAR_RELAY, [1])):
#		if (not ble.writeCharacteristic(CHAR_PWM, [1])):
			exit(1)
		
		print "took", (time.time() - startTime), "s. Wait", timeSkip, "s"

#		print 'time delay %f' %timeSkip
		time.sleep(timeSkip)

		print str(datetime.datetime.now()), 'turn off', turnOffCount
		turnOffCount += 1
		startTime = time.time()
		if (not ble.writeCharacteristic(CHAR_RELAY, [0])):
#		if (not ble.writeCharacteristic(CHAR_PWM, [0])):
			"failed to write char"
			exit(1)

		print "took", (time.time() - startTime), "s. Wait", timeSkip, "s"

#		print 'charge Time %f' %chargeTime
		time.sleep(chargeTime)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
