#!/usr/bin/env python

__author__ = 'Bart van Vliet'

import bluepy.btle
from Bluenet import *
from ConversionUtils import *
import matplotlib.pyplot as plt
# from matplotlib import gridspec
import random
import numpy as np

# UUID: 0681db7270e8f0844440ca871397b7dd
# dev bart:     F9:72:31:61:3D:E1
# plugin 1:     CF:75:73:30:69:86   minor=4   id=502
# plugin black: DC:1A:C0:64:1A:8B
# bathroom:     CD:0D:98:06:6A:42   minor=3   id=503
# kitchen:      E3:F5:C5:FF:23:40   minor=0   id=500
# garage:       E5:20:4D:1D:CD:6C   minor=1   id=501
# living room:  FB:8D:71:D5:6B:C1   minor=2   id=502
#targets = ["D0:E8:42:71:C2:5D"]
targets = ["E3:F5:C5:FF:23:40", "E5:20:4D:1D:CD:6C", "FB:8D:71:D5:6B:C1", "CD:0D:98:06:6A:42"]
#targets = ["E3:F5:C5:FF:23:40", "E5:20:4D:1D:CD:6C", "CF:75:73:30:69:86", "CD:0D:98:06:6A:42"]
targets = ["E3:F5:C5:FF:23:40", "DB:4C:5F:9F:AA:52", "CF:75:73:30:69:86", "DC:1A:C0:64:1A:8B"]

names = ["Kitchen", "Garage", "Living room", "Bathroom"]
positions = [(900,345), (900,785), (430,390), (315,835), (590, 750)]
for i in range(0, len(targets)):
	targets[i] = targets[i].lower()

dataLength = 1000 # About 100s
movingAvgWindow = 50 # About 5s

data = {}
for target in targets:
	data[target] = {
		"rssi": [0]*dataLength,
		"switch": [0]*dataLength,
		"power": [0]*dataLength,
		"energy": [0]*dataLength,
		"powerMovingAvg": [0]*dataLength,
	}

lastPhonePos = {"num": 4, "prev": -1}

class ScanDelegate(bluepy.btle.DefaultDelegate):
	def __init__(self):
		bluepy.btle.DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if (dev.addr in targets):
			data[dev.addr]["rssi"].append(dev.rssi)
			data[dev.addr]["rssi"] = data[dev.addr]["rssi"][-dataLength:]
			for (adtype, desc, value) in dev.getScanData():
				if (adtype == 22):
					serviceData = Conversion.hex_string_to_uint8_array(value)
					print dev.addr, list(serviceData)
					ind = 0
					uuid = Conversion.uint8_array_to_uint16(serviceData[ind:ind+2])
					ind += 2
					csId = Conversion.uint8_array_to_uint16(serviceData[ind:ind+2])
					ind += 2
					csStateId = Conversion.uint8_array_to_uint16(serviceData[ind:ind+2])
					ind += 2
					switchState = serviceData[ind]
					print switchState
					ind += 1
					eventBitmask = serviceData[ind]
					ind += 1
					ind += 2 # Reserved
					powerUsage = Conversion.uint32_to_int32(Conversion.uint8_array_to_uint32(serviceData[ind:ind+4]))
					ind += 4
					accEnergy = Conversion.uint32_to_int32(Conversion.uint8_array_to_uint32(serviceData[ind:ind+4]))
					ind += 4

					data[dev.addr]["switch"].append(switchState)
					data[dev.addr]["power"].append(powerUsage)
					data[dev.addr]["energy"].append(accEnergy)

					data[dev.addr]["switch"] = data[dev.addr]["switch"][-dataLength:]
					data[dev.addr]["power"]  = data[dev.addr]["power"][-dataLength:]
					data[dev.addr]["energy"] = data[dev.addr]["energy"][-dataLength:]

					power = data[dev.addr]["power"][-movingAvgWindow:]
					powerNoOutliers = []
					meanPower = np.mean(power)
					stdPower = np.std(power)
					for i in range(0, len(power)):
						if (abs(power[i] - meanPower) < 1*stdPower):
							powerNoOutliers.append(power[i])
						# else:
						# 	print "removed outlier"
					if (len(powerNoOutliers)):
						# print "mean:", meanPower, " mean without outliers:", np.mean(powerNoOutliers)
						meanPower = np.mean(powerNoOutliers)
					data[dev.addr]["powerMovingAvg"].append(np.mean(meanPower))
					data[dev.addr]["powerMovingAvg"] = data[dev.addr]["powerMovingAvg"][-dataLength:]

					if (switchState & 2):
					# if (switchState == 3):
						lastPhonePos["num"] = targets.index(dev.addr)


dpi = 80
pixWidth = 1920
pixHeight = 1080
# pixWidth = 800
# pixHeight = 600

inchWidth = float(pixWidth)/dpi
inchHeight = float(pixHeight)/dpi

floorplanFileName = "/home/vliedel/dev/crownstone/ble-automator/data/demo-image.png"
floorplanImg = plt.imread(floorplanFileName)
imgSize = floorplanImg.shape

rows = 6
# cols = 8
cols = rows+4
#imgFig = plt.figure(frameon=False, figsize=(inchWidth,inchHeight), dpi=dpi, tight_layout=True)
imgFig = plt.figure(frameon=False, figsize=(inchWidth,inchHeight), dpi=dpi)

axFig =       plt.subplot2grid((rows, cols), (0,2),            colspan=rows, rowspan=rows)
axTopLeft =   plt.subplot2grid((rows, cols), (0,0),            colspan=2, rowspan=2)
axTopRight =  plt.subplot2grid((rows, cols), (0, cols-2),      colspan=2, rowspan=2)
axDownLeft =  plt.subplot2grid((rows, cols), (rows-2, 0),      colspan=2, rowspan=2)
axDownRight = plt.subplot2grid((rows, cols), (rows-2, cols-2), colspan=2, rowspan=2)

axFig.imshow(floorplanImg)
axFig.scatter(positions[lastPhonePos["num"]][0], positions[lastPhonePos["num"]][1], c="r", marker="o", s=500, alpha=0.1)
axFig.set_axis_off()

axTopLeft.get_xaxis().set_visible(False)
axDownLeft.get_xaxis().set_visible(False)
axTopRight.get_xaxis().set_visible(False)
axDownRight.get_xaxis().set_visible(False)
axTopRight.get_yaxis().tick_right()
axDownRight.get_yaxis().tick_right()

axesGraphs = [axTopRight, axDownRight, axTopLeft, axDownLeft]

#plt.draw()
#plt.show(block=False)
# plt.show()
# exit(1)

hci = 1
scanner = bluepy.btle.Scanner(hci).withDelegate(ScanDelegate())
scanner.start()

while True:
	scanner.process(0.5)

	for i in range(0, 4):
		axesGraphs[i].cla()
		#axesGraphs[i].plot(range(0, len(data[targets[i]]["power"])), data[targets[i]]["power"], label="power")
		axesGraphs[i].plot(range(0, len(data[targets[i]]["powerMovingAvg"])), data[targets[i]]["powerMovingAvg"], label="powerMovingAvg")
		# axesGraphs[i].plot(range(0, len(data[targets[i]]["rssi"])), data[targets[i]]["rssi"], label="rssi")
#		axesGraphs[i].plot(range(0, len(data[targets[i]]["switch"])), np.array(data[targets[i]]["switch"])*10, label="switch")
		# axesGraphs[i].set_title(targets[i])
		name = names[i]
		if (data[targets[i]]["switch"][-1] & 1):
			name += " (on)"
		else:
			name += " (off)"
		axesGraphs[i].set_title(name)
		maxY = np.max([100, np.max(data[targets[i]]["powerMovingAvg"])])
		axesGraphs[i].set_ylim([-10, maxY])
		axesGraphs[i].set_ylabel("Power usage (W)")
		# axesGraphs[i].set_xlabel("Time")

	numPhonePresent = 0
	for target in targets:
		if (data[target]["switch"][-1] & 2):
		# if (data[target]["switch"][-1] == 3):
			numPhonePresent += 1
	print "numPhonePresent:", numPhonePresent
	if (numPhonePresent != 1):
		lastPhonePos["num"] = 4
	if (lastPhonePos["num"] != lastPhonePos["prev"]):
		axFig.cla()
		axFig.imshow(floorplanImg)
		if (numPhonePresent == 1):
			axFig.scatter(positions[lastPhonePos["num"]][0], positions[lastPhonePos["num"]][1], c="r", marker="o", s=500)
		else:
			axFig.scatter(positions[lastPhonePos["num"]][0], positions[lastPhonePos["num"]][1], c="r", marker="o", s=500, alpha=0.1)
		axFig.set_axis_off()

	lastPhonePos["prev"] = lastPhonePos["num"]

	plt.draw()
	plt.show(block=False)
scanner.stop()
