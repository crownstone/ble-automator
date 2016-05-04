#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import time
from bleAutomator2 import *
from ConversionUtils import *
from Bluenet import *
import random


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
		exit(1)

	# Get unix time
	currentTime = int(time.time())
	random.seed(currentTime)
	id = random.randint(0, 20)
#	id = 19
	overrideMask = ScheduleOverride.PRESENCE
	timeType = ScheduleTimeType.TIME_REPEAT
	actionType = ScheduleActionType.PWM
	type = timeType + (actionType << 4)
	nextTimestamp = currentTime+60
#	nextTimestamp = 0
#	repeatTime = random.randint(0,60)
	repeatTime = 1 # Every 1 minute
	pwm = random.randint(0,100)

	arr8 = [id, type, overrideMask]
	arr8.extend(Conversion.uint32_to_uint8_array(nextTimestamp))
	arr8.extend(Conversion.uint16_to_uint8_array(repeatTime))
	arr8.extend([pwm, 0, 0]) # schedule_action_pwm_t has 2 reserved bytes

	print arr8

	# Write to characteristic
	if (not ble.writeCharacteristic(CHAR_WRITE_SCHEDULE, arr8)):
		exit(1)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
