#!/usr/bin/env python

__author__ = 'Bart van Vliet'

from bleAutomator2 import *
import matplotlib.pyplot as plt
from Bluenet import *

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage="%prog [-v] [-i <interface>] [-a <address>] \n\nExample:\n\t%prog -i hci0 -a 01:23:45:67:89:AB",
									version="0.1")

		parser.add_option('-i', '--interface',
				action="store",
				dest="interface",
				type="string",
				default="hci0",
				help="Interface to be used."
				)
		parser.add_option('-v', '--verbose',
				action="store_true",
				dest="verbose",
				help="Be verbose."
				)
		parser.add_option('-a', '--address',
				action="store",
				dest="address",
				type="string",
				default=None,
				help="Target bluetooth address."
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

	# Make the crownstone sample the current
	if (not ble.writeCharacteristic(CHAR_SAMPLE_POWER, [3])):
		exit(1)

	time.sleep(0.5)

	arr8 = ble.readCharacteristic(CHAR_READ_POWER_CURVE)
	if (not arr8):
		exit(1)

	curve = Bluenet.getPowerCurve(arr8)
	if (not curve):
		exit(1)

	ble.disconnect()

	plt.plot(curve["currentTimestamps"], curve["currentSamples"])
	plt.plot(curve["voltageTimestamps"], curve["voltageSamples"])
	plt.show()

	exit(0)