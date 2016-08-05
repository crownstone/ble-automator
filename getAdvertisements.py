#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import bluepy.btle
from Bluenet import *
from ConversionUtils import *
import matplotlib.pyplot as plt
import random
import numpy as np

targets = ["E3:F5:C5:FF:23:40", "E5:20:4D:1D:CD:6C", "FB:8D:71:D5:6B:C1", "CD:0D:98:06:6A:42"]
hci = 1

class ScanDelegate(bluepy.btle.DefaultDelegate):
	def __init__(self):
		bluepy.btle.DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if (dev.addr in targets):
			print "Advertisements from:", dev.addr, "rssi:", dev.rssi
			for (adtype, desc, value) in dev.getScanData():
				print "type:", adtype, "description:", desc
				if (adtype == 22): # ServiceData
					serviceData = Conversion.hex_string_to_uint8_array(value)
					print "Service data:", list(serviceData)

					ind = 0
					uuid = Conversion.uint8_array_to_uint16(serviceData[ind:ind+2])
					ind += 2

					print "UUID:", uuid # Crownstone uuid = 49153, Guidestone uuid = 49154

				if (adtype == 8): # Name
					print "Name:", value
			print ""


for i in range(0, len(targets)):
	targets[i] = targets[i].lower()
scanner = bluepy.btle.Scanner(hci).withDelegate(ScanDelegate())
scanner.start()
while True:
	scanner.process(0.5)
scanner.stop()