#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *



charac='5b8d0001-6f20-11e4-b116-123b93f75cba'

if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <dfu_target_address>\n\nExample:\n\tdfu.py -i hci0 -a cd:e3:4a:47:1c:e4',
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
	
	ble_rec = BleAutomator(options.interface, options.verbose)
	
	# Connect to peer device.
	if (not ble_rec.connect(options.address)):
		exit(1)
	
	# Make the crownstone sample the current, give it some time to sample
	if (not ble_rec.writeString(charac, '00')):
		exit(1)
	time.sleep(1)
	
	# Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
	
	exit(0)
