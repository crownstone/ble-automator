#!/usr/bin/env python

__author__ = 'Bart van Vliet'


from bleAutomator2 import *
from ConversionUtils import *
from Bluenet import *


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='''%prog [-v] [-i <interface>] -a <ble address> -t <type> [-n]
											\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 0 -s''',
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
				default=None,
				help='What configuration to read (integer)'
				)
		parser.add_option('-n', '--number',
				action='store_true',
				dest="as_number",
				help='Read value as number, not as string'
				)
		
		options, args = parser.parse_args()
	
	except Exception, e:
		print e
		print "For help use --help"
		sys.exit(2)
	
	if (not options.address or options.configType == None):
		parser.print_help()
		exit(2)
	
	ble = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	if (not ble.connect(options.address)):
		exit(1)
	
	# Write type to select
	if (not ble.writeCharacteristic(CHAR_CONFIG_SELECT, [options.configType])):
		exit(1)

	time.sleep(1)
	
	# Read the value of selected type
	arr8 = ble.readCharacteristic(CHAR_CONFIG_READ)
	if (not arr8):
		print "Couldn't read value"
		exit(1)
	
	# First byte is the type
	# Second byte is reserved for byte alignment
	print "Type: %i" % (arr8[0])
	if (options.configType != arr8[0]):
		print "Type mismatch"
		exit(1)

	# Third and fourth bytes is the length of the data, as uint16_t
	length = Conversion.uint8_array_to_uint16(arr8[2:4])

	# Fifth and on bytes is the data
	data = arr8[4:]
	if (len(data) != length):
		print "Size mismatch"
		print "data:", list(arr8)
		exit(1)
	
	# Output as string or as single uint8
	if (options.as_number):
		if (length == 1):
			print "Value: %i" % (data[0])
		elif (length == 2):
			print "Value: %i" % (Conversion.uint8_array_to_uint16(data))
		elif (length == 4):
			print "Value: %i" % (Conversion.uint8_array_to_uint32(data))
		else:
			print "Value:", list(data)
	else:
		valStr = Conversion.uint8_array_to_string(data)
		print "Value: %s" % (valStr)
	
	# Disconnect from peer device if not done already and clean up.
	ble.disconnect()
	
	exit(0)
