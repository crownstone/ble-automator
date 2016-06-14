#!/usr/bin/env python
__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from Bluenet import *

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
		parser.add_option('-d', '--dfu-mode',
				action='store_true',
				dest="dfu",
				help="Reset and enter dfu mode."
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

	resetCode = RESET_CODE_RESET
	if (options.dfu):
		resetCode = RESET_CODE_DFU

	# Write 1 to reset
	# Write should fail, since we won't get a response
	if (ble.writeCharacteristic(CHAR_RESET, [resetCode])):
		exit(1)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
