#!/usr/bin/env python

# THIS SCRIPT SHOULD BE RUN WITH ADMINISTRATOR RIGHTS
# this script scans for bluetooth advertisements and filters them to check if they:
#- are a crownstone
#- are a plug version of that
#- are in setup mode (by checking serviceData in some points (is powerUsage 0 & is energyUsage 0)
#- have rssi above -85dB
#- have name containing 'ACR0'
# If those requirements are met, the script toggles an LED through the GPIO on the raspberrypi

__author__ = 'Marc Hulscher'

import bluepy.btle
from bleAutomator2 import *
from Bluenet import *
from ConversionUtils import *
import time
import RPi.GPIO as GPIO
from subprocess import check_output

typeRequired="plug"		# should be 'plug', 'builtin' or 'guidestone'
#nameRequired="ACR0"		# this is required to be IN the name
minRSSI=-85

lastShowUp = 0
GPIO.setmode(GPIO.BCM)
LEDPin=4	#BCM GPIO04
GPIO.setup(LEDPin,GPIO.OUT)
LEDstate = False

# show some blinking to indicate startup
for i in [1,2,3,4]:
	GPIO.output(LEDPin,GPIO.LOW)
	time.sleep(0.5)
	GPIO.output(LEDPin,GPIO.HIGH)
	time.sleep(0.5)


def isCrownstone(serviceData):
	if (not serviceData):
		return False
	serviceDataList = list(serviceData)
	if (len(serviceDataList) > 1 and serviceDataList[1]==192):
		return True
	return False
	
def isCorrectCrownstone(serviceData):
	if (not isCrownstone(serviceData)):
		return False
	serviceDataList = list(serviceData)
	CsType=""
	# Check which crownstone type
	if(serviceDataList[0]==1):
		CsType="plug"
	elif(serviceDataList[0]==2):
		CsType="builtin"
	elif(serviceDataList[0]==3):
		CsType="guidestone"
	return  CsType==typeRequired

def handleLED(showUpConfirmed):
	global lastShowUp, LEDPin, LEDstate
	#print time.time()-lastShowUp
	if(showUpConfirmed):
		lastShowUp=time.time()
		print "Turn LED on"
		LEDstate=True
		GPIO.output(LEDPin,GPIO.LOW)
	elif(time.time()-lastShowUp>1 and LEDstate):
		print "Turn LED off"
		LEDstate=False
		GPIO.output(LEDPin,GPIO.HIGH)
	return 0

class ScanDelegate(bluepy.btle.DefaultDelegate):
	def __init__(self):
		bluepy.btle.DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		macAddress = 0
		rssi=0
		name=""
		isCs=False
		serviceData=""
		uuid=""
		protocolVersion=""
		crownstoneId=""
		switchState=""
		eventBitmask=""
		temperature=""
		powerUsage=""
		energyUsage=""
		randNr=""
		
		if (((len(targets) == 0) or (dev.addr in targets)) and dev.rssi>minRSSI):
			macAddress=dev.addr
			rssi=dev.rssi
			serviceData = None
			#print "Advertisements from:", dev.addr, "rssi:", dev.rssi
			for (adtype, desc, value) in dev.getScanData():
				#print "type:", adtype, "description:", desc
				if (adtype == 8): # Name
					name = value
				if (adtype == 22): # ServiceData
					serviceData = Conversion.hex_string_to_uint8_array(value)
					isCs = isCrownstone(serviceData)
					if (len(serviceData) >= 19):
						uuid = Conversion.uint8_array_to_uint16(serviceData[0:2])
						protocolVersion = serviceData[2]
						crownstoneId = Conversion.uint8_array_to_uint16(serviceData[3:5])
						switchState = serviceData[5]
						eventBitmask = serviceData[6]
						temperature = Conversion.uint8_to_int8(serviceData[7])
						powerUsage = Conversion.uint8_array_to_uint32(serviceData[8:12])
						energyUsage = Conversion.uint8_array_to_uint32(serviceData[12:16])
						randNr = list(serviceData[16:19])
					
#						print "UUID:", uuid # Crownstone uuid = 49153, Guidestone uuid = 49154
#						print "crownstoneId:", crownstoneId
#						print "switchState:", switchState
#						print "eventBitmask:", "{0:08b}".format(eventBitmask)
#						print "temperature:", temperature
#						print "powerUsage:", powerUsage
#						print "energyUsage:", energyUsage
#						print "randNr:", randNr
			
#			if(nameRequired in name and powerUsage==0 and energyUsage==0 and isCorrectCrownstone(serviceData)):
			if (powerUsage==0 and energyUsage==0 and isCorrectCrownstone(serviceData)):
				handleLED(True)
				if(options.verbose):
					print "Advertisements from:", macAddress, "rssi:", rssi
					print "Name:", name
					print "isCrownstone?:", isCs
					print "service data:" , list(serviceData)
					print "Crownstone Type:", isCorrectCrownstone(serviceData)
					print "UUID:", uuid # Crownstone uuid = 49153, Guidestone uuid = 49154
					print "crownstoneId:", crownstoneId
					print "switchState:", switchState
					print "eventBitmask:", "{0:08b}".format(eventBitmask)
					print "temperature:", temperature
					print "powerUsage:", powerUsage
					print "energyUsage:", energyUsage
					print "randNr:", randNr
					print ""


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(usage='%prog [-v] [-i <interface>] [-a <ble address>]\n\nExample:\n\t%prog -i hci0 -a CD:E3:4A:47:1C:E4',
									version='0.1')

		parser.add_option('-a', '--address',
				action='store',
				dest="address",
				type="string",
				default=None,
				help='Target address. (Can be found by running "hcitool lescan")'
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

	targets = []
	if (options.address):
		targets = [options.address]

	for i in range(0, len(targets)):
		targets[i] = targets[i].lower()

	# recast the bluetooth device to use the USB dongle since we can't rely on it staying hci1
	hcitoolCheck = check_output(["hcitool", "dev"])
	hciDevice = "hci0"
	for line in hcitoolCheck.split('\n'):
		if "00:1A:7D:DA:71:13" in line:
			hciDevice=line.split('\t')[1]
	options.interface=hciDevice

	# create scanner instances
	scanner = bluepy.btle.Scanner(options.interface[3:]).withDelegate(ScanDelegate())
	scanner.start()
	while True:
		scanner.process(0.5)
		handleLED(False)
	
	scanner.stop()
	GPIO.output(LEDPin,GPIO.HIGH)
	GPIO.cleanup()

