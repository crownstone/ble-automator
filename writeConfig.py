#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from ConversionUtils import *
from Bluenet import *


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='''%prog [-v] [-i <interface>] -a <ble address> -t <type> -d <value> [-n]
											\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 0 -d myCrown
											Example:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 3 -d 2 -n''',
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
		parser.add_option('-t', '--type',
				action='store',
				dest="configType",
				type="int",
				default=0,
				help='What configuration to read (integer)'
				)
		parser.add_option('-n', '--number',
				action='store_true',
				dest="as_number",
				help='Write value as number, not as string'
				)
		parser.add_option('-d', '--data',
				action='store',
				dest="configValue",
				type="string",
				default=None,
				help='Value to set'
				)
		
		options, args = parser.parse_args()
	
	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)
	
	if (not options.address or options.configType == None or options.configValue == None):
		parser.print_help()
		exit(2)
	
	ble = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	if (not ble.connect(options.address)):
		exit(1)
	
	# First byte is the type
	arr8 = [options.configType]

	# Second byte is reserved for byte alignment
	arr8.append(0)
	
	data = []
	if (options.as_number):
		# Write value as number
		valInt = int(options.configValue)
		if (valInt < 0):
			print "Cannot write values lower than 0!"
			exit(1)
		
		if (valInt > 65535):
			data = Conversion.uint32_to_uint8_array(valInt)
		elif (valInt > 255):
			data = Conversion.uint16_to_uint8_array(valInt)
		else:
			data.append(valInt)
	else:
		# Write value as string
		data = Conversion.string_to_uint8_array(options.configValue)
	
	# Third and fourth bytes is the length of the data, as uint16_t
	arr8.extend(Conversion.uint16_to_uint8(len(data)))

	# Add the data
	arr8.extend(data)

	if (not ble.writeCharacteristic(CHAR_CONFIG_WRITE, arr8)):
		exit(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()
	
	exit(0)
