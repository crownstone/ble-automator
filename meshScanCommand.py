#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from Bluenet import *


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address>\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -c 0',
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
		parser.add_option('-c', '--command',
				action='store',
				dest="command",
				type="string",
				default=None,
				help='Command to set (0=stop, 1=start)'
				)

		options, args = parser.parse_args()

	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)

	if (not options.address or options.command == None):
		parser.print_help()
		exit(2)

	ble = BleAutomator(options.interface, options.verbose)

	# Connect to peer device.
	if (not ble.connect(options.address)):
		exit(1)

	commandInt = 0
	try:
		commandInt = int(options.command)
	except ValueError:
		pass

	if (options.command == "start"):
		commandInt = 1

	arr8 = [MeshHandleType.DATA, 0] # Handle
	arr8.extend(Conversion.uint16_to_uint8_array(6+2+2+2+1)) # Length of target address + message type + command type + par
	arr8.extend([0,0,0,0,0,0]) # target address: all 0 to target any node
	arr8.extend(Conversion.uint16_to_uint8_array(MeshDataMessageType.COMMAND_MESSAGE))
	arr8.extend(CommandTypes.CMD_ENABLE_SCANNER) # command
	arr8.extend(0) # byte alignment
	arr8.extend(Conversion.uint16_to_uint8_array(1)) # length
	arr8.extend([commandInt])

	if (not ble.writeCharacteristic(CHAR_MESH_CONTROL, arr8)):
		exit(1)

	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()

	exit(0)
