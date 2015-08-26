#!/usr/bin/env python

__author__ = 'Bart van Vliet'


import os, sys, datetime
from bleAutomator import *


charac='9cf53570-ddd9-47f3-ba63-09acefc60415'

if __name__ == '__main__':
	try:
            parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] -a <ble address>\n\nExample:\n\t%prog -i hci0 -a 00:12:92:08:05:16',
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
	if (not ble_rec.connect(options.address, "")):
		exit(1)
	
   # Make the crownstone sample the current, give it some time to sample
	readStr = ble_rec.readStringsFirst(charac)
		if (readStr == False):
			print "Couldn't read button state"
			exit(1)

		while True:
			button_state = readStr
			print "Button state: %s" % (button_state)
			readStr = ble_rec.readStringsNext(charac)

   # Disconnect from peer device if not done already and clean up.
	ble_rec.disconnect()
	
	exit(0)
