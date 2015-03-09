#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] \n\nExample:\n\tdfu.py -i hci0 -f data.txt',
									version='0.1')
		
		parser.add_option('-i', '--interface',
				action='store',
				dest="interface",
				type="string",
				default="hci0",
				help='HCI interface to be used.'
				)
		parser.add_option('-f', '--file',
				action='store',
				dest="data_file",
				type="string",
				default="data.txt",
				help='File to store the data'
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
	
	#if (not options.address):
		#parser.print_help()
		#exit(2)
	
	ble_rec = BleAutomator(options.interface, options.verbose)
	
	# addresses = ['FD:C2:0E:76:C7:61', 'E5:C8:68:8A:BB:9C']
	addresses = ['E5:C8:68:8A:BB:9C']
	address_ind = 0
	
	# Endless loop:
	while (True):
		# Connect to peer device.
		ble_rec.connect(addresses[address_ind])
		
		# Get all handles and cache them
		ble_rec.getHandles()
	
		# Make the crownstone sample the current, give it some time to sample
		ble_rec.writeString('5b8d0002-6f20-11e4-b116-123b93f75cba', '03')
		time.sleep(1)
		
		# Read the current curve
		uuid = '5b8d0003-6f20-11e4-b116-123b93f75cba'
		curve = ble_rec.readString(uuid)
		if (curve != False):
			f = open(options.data_file, 'a')
			f.write('%f %s %s' % (time.time(), addresses[address_ind], uuid))
			curve_array = convert_buffer_to_uint16_array(curve)
			for i in curve_array:
				f.write(' %i' % (i))
			f.write('\n')
			f.close()
		
		# wait a second to be able to receive the disconnect event from peer device.
		time.sleep(1)
		
		# Disconnect from peer device if not done already and clean up.
		ble_rec.disconnect()
		
		time.sleep(1)
		address_ind = (address_ind+1) % len(addresses)
