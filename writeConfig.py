#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *



charac='f5f90007-59f9-11e4-aa15-123b93f75cba'

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address> -t <type> -d <value>\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4 -t 0 -d myCrown',
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
	
	ble_rec = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	if (not ble_rec.connect(options.address)):
		exit(1)
	
	# First byte is the type
	hexStr = convert_uint8_to_hex_string(options.configType)
	
	# Second and third bytes is the length of the data, as uint16_t
	hexStr += convert_uint16_to_hex_string(len(options.configValue))
	
	if (options.as_number):
		# Write value as number
		valInt = int(options.configValue)
		if (valInt < 0):
			print "Cannot write values lower than 0!"
			exit(1)
		
		arr8 = []
		if (valInt > 65535):
			arr8 = convert_uint32_to_uint8_array(valInt)
		elif (valInt > 255):
			arr8 = convert_uint16_to_uint8_array(valInt)
		else:
			arr8.append(valInt)
		hexStr += convert_uint8_array_to_hex_string(arr8)
	else:
		# Write value as string
		arr8 = convert_string_to_uint8_array(options.configValue)
		hexStr += convert_uint8_array_to_hex_string(arr8)
	
	if (not ble_rec.writeString(charac, hexStr)):
		exit(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
	
	exit(0)
