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

	# Read characteristic
	arr8 = ble.readCharacteristic(CHAR_LIST_SCHEDULE)
	if (not arr8):
		exit(1)

	print Conversion.uint8_array_to_hex_string(arr8)
	size = arr8[0]
	print "size:", size
	for i in range(0,size):
		offset = 1 + i*12
		id = arr8[offset]
		offset += 1

		type = arr8[offset]
		offset += 1

		overrideMask = arr8[offset]
		offset += 1

		nextTimestamp = Conversion.uint8_array_to_uint32(arr8[offset : offset+4])
		offset += 4

		timeData = arr8[offset : offset+2]
		offset += 2

		actionData = arr8[offset : offset+3]
		offset += 3

		timeType = type & 0x00FF
		actionType = (type & 0xFF00) >> 4

		print "id:", id, " overrideMask: ", overrideMask, " nextTimestamp:", nextTimestamp, " timeType:", timeType, " timeData:", Conversion.uint8_array_to_hex_string(timeData), " actionType:", actionType, " actionData:" , Conversion.uint8_array_to_hex_string(actionData)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
