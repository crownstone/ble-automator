#!/usr/bin/env python

import os
import optparse
import time
from intelhex import IntelHex
import bleLog
from bleAutomator2 import *
from Bluenet import *
from ConversionUtils import *

# DFU Opcodes
# See https://developer.nordicsemi.com/nRF51_SDK/nRF51_SDK_v8.x.x/doc/8.1.0/s130/html/a00107.html#ota_spec_control_state
class DfuOpcode:
	START_DFU = 1
	INITIALIZE_DFU = 2
	RECEIVE_FIRMWARE_IMAGE = 3
	VALIDATE_FIRMWARE_IMAGE = 4
	ACTIVATE_FIRMWARE_AND_RESET = 5
	SYSTEM_RESET = 6
	REPORT_RECEIVED_IMAGE_SIZE = 7
	PACKET_RECEIPT_NOTIFICATION_REQUEST = 8
	RESPONSE_CODE = 16
	PACKET_RECEIPT_NOTIFICATION = 17

class DfuImageType:
	NONE = 0
	SOFTDEVICE = 1
	BOOTLOADER = 2
	SOFTDEVICE_WITH_BOOTLOADER = 3
	APPLICATION = 4

class DfuResponseValue:
	SUCCESS = 1
	INVALID_STATE = 2
	NOT_SUPPORTED = 3
	DATA_SIZE_EXCEEDS_LIMIT = 4
	CRC_ERROR = 5
	OPERATION_FAILED = 6

class DfuInitPacket:
	RECEIVE_INIT_PACKET = 0
	INIT_PACKET_COMPLETE = 1

class DfuSoftDeviceVersion:
# See https://developer.nordicsemi.com/nRF51_SDK/nRF51_SDK_v8.x.x/doc/8.1.0/s130/html/a00101.html#dfu_init_sd_list_sec
	S110_V7_0_0 = 0x004F
	S110_V7_1_0 = 0x005A
	S110_V8_0_0 = 0x0064
	ANY         = 0xFFFE

# different CHUNK_SIZE does not work somehow
# CHUNK_SIZE = 15
CHUNK_SIZE = 20



class BleDfuUploader(object):

	def __init__(self, bleAddress, hexfilePath, interface, Logger, imageType=DfuImageType.APPLICATION):
		"""
		:param bleAddress:  Bluetooth address of the target device
		:type bleAddress:   str
		:param hexfilePath: Path where the .hex file to upload can be found
		:type hexfilePath:  str
		:param interface:   Interface to use (for example: hci0)
		:type interface:    str
		:param Logger:
		:type Logger:       bleLog.Logger
		:param imageType:   Type of image to be sent (app, bootloader, softdevice)
		:type imageType:    DfuImageType
		:return:
		"""
		self.hexfilePath = hexfilePath
		self.address = bleAddress
		self.interface = interface
		self.log = Logger
		self.imageType = imageType
		self.enableDfuAttemptNum = 0
		self.ble = BleAutomator(self.interface)

	def connect(self):
		return self.ble.connect(self.address)

	def _checkDfuMode(self):
		#look for DFU switch characteristic
		resetHandle = self.ble.getHandle(CHAR_RESET)

		if not resetHandle:

			controlHandle = self.ble.getHandle(CHAR_CONTROL)

			if not controlHandle:

				# maybe it already is IN DFU mode
				ctrlptHandle = self.ble.getHandle(CHAR_DFU_CONTROL_POINT)
				if not ctrlptHandle:
					self.log.e("Not in DFU, nor has the toggle characteristic, aborting..")
					return False
				else:
					self.log.i("Node is in DFU mode", bleLog.LogType.SUCCESS)
					return True

			else:
				if (self.enableDfuAttemptNum >= 3):
					self.log.e("Stopped trying to enable DFU after 3 attempts")
					return False
				self.enableDfuAttemptNum += 1
				self.log.i("Switching device into DFU mode")
				self.ble.writeCharacteristic(CHAR_CONTROL, [CommandTypes.CMD_GOTO_DFU, 0])
				time.sleep(0.2)

		else:
			if (self.enableDfuAttemptNum >= 3):
				self.log.e("Stopped trying to enable DFU after 3 attempts")
				return False
			self.enableDfuAttemptNum += 1
			self.log.i("Switching device into DFU mode")
			self.ble.writeCharacteristic(CHAR_RESET, [RESET_CODE_DFU])
			time.sleep(0.2)

		self.log.i("Node is being restarted")
		self.ble.disconnect()

		# wait for restart
		time.sleep(5)

		# reconnect
		self.log.i("Reconnecting...")
		retry = 0
		while (retry < 3):
			if (self.connect()):
				return self._checkDfuMode()
			else:
				retry += 1
				print self.log.i("retry %i ..." %retry)
		return False

	def _sendOpcode(self, opcode, extra=None):
		res = False
		if (extra == None):
			self.log.d("Send opcode %i" % (opcode))
			res = self.ble.writeCharacteristic(CHAR_DFU_CONTROL_POINT, [opcode])
		else:
			self.log.d("Send opcode %i %i" % (opcode, extra))
			res = self.ble.writeCharacteristic(CHAR_DFU_CONTROL_POINT, [opcode, extra])
#		time.sleep(0.1)
		return res

	def _sendImageSize(self, softdeviceSize, bootloaderSize, applicationSize):
		self.log.i("Send image size")
		# See: https://developer.nordicsemi.com/nRF51_SDK/nRF51_SDK_v8.x.x/doc/8.1.0/s130/html/a00107.html#bledfu_bleservice_size
		arr8 = Conversion.uint32_to_uint8_array(softdeviceSize)
		arr8.extend(Conversion.uint32_to_uint8_array(bootloaderSize))
		arr8.extend(Conversion.uint32_to_uint8_array(applicationSize))
		res = self.ble.writeCharacteristic(CHAR_DFU_PACKET, arr8)
#		time.sleep(0.1)
		return res

	def _sendInitPacket(self, deviceType, deviceRev, appVersion, softdevice, crc):
		self.log.i("Send init packet")
		# See https://developer.nordicsemi.com/nRF51_SDK/nRF51_SDK_v8.x.x/doc/8.1.0/s130/html/a00395.html
		#uint16_t device_type;       /**< Device type (2 bytes), for example Heart Rate. This number must be defined by the customer before production. It can be located in UICR or FICR. */
		#uint16_t device_rev;        /**< Device revision (2 bytes), for example major revision 1, minor revision 0. This number must be defined by the customer before production. It can be located in UICR or FICR. */
		#uint32_t app_version;       /**< Application version for the image software. This field allows for additional checking, for example ensuring that a downgrade is not allowed. */
		#uint16_t softdevice_len;    /**< Number of different SoftDevice revisions compatible with this application. The list of SoftDevice firmware IDs is defined in @ref softdevice. */
		#uint16_t softdevice[1];     /**< Variable length array of SoftDevices compatible with this application. The length of the array is specified in the length field. SoftDevice firmware id 0xFFFE indicates any SoftDevice. */
		#uint16_t CRC                /**< CRC 16 CCITT of the image. */
		arr8 = Conversion.uint16_to_uint8_array(deviceType)
		arr8.extend(Conversion.uint16_to_uint8_array(deviceRev))
		arr8.extend(Conversion.uint32_to_uint8_array(appVersion))
		arr8.extend(Conversion.uint16_to_uint8_array(1))
		arr8.extend(Conversion.uint16_to_uint8_array(softdevice))
		arr8.extend(Conversion.uint16_to_uint8_array(crc))
		res = self.ble.writeCharacteristic(CHAR_DFU_PACKET, arr8)
#		time.sleep(0.1)
		return res

	def _sendData(self, arr8):
		return self.ble.writeCharacteristic(CHAR_DFU_PACKET, arr8)

	def _enableCccd(self):
		self.log.i("Enable cccd")
		cccdEnableHandle = self.ble.getHandle(CHAR_DFU_CONTROL_POINT) + 1
		return self.ble.writeCharacteristicHandle(cccdEnableHandle, [1])


	# Transmit the hex image to peer device.
	def update(self):
		# Make sure the device is in dfu mode
		if not self._checkDfuMode():
			return False

		# Enable Notifications - Setting the DFU Control Point CCCD to 0x0001
		if not self._enableCccd():
			return False

		# General procedure
		# See: https://developer.nordicsemi.com/nRF51_SDK/nRF51_SDK_v8.x.x/doc/8.1.0/s130/html/a00106.html#ota_profile_updater_role_transfering

		# Open the hex file to be sent
		ih = IntelHex(self.hexfilePath)
		binArray = ih.tobinarray()
		binSize = len(binArray)
		crc = Bluenet.crc16_ccitt(binArray, binSize)
		self.log.i("Hex file size: %i crc: %i" % (binSize, crc))

		# Start DFU
		if not self._sendOpcode(DfuOpcode.START_DFU, self.imageType):
			return False

		# Send image size
		softdeviceSize=0
		bootloaderSize=0
		appSize=0
		if (self.imageType == DfuImageType.APPLICATION):
			appSize = binSize
		elif (self.imageType == DfuImageType.BOOTLOADER):
			bootloaderSize = binSize

		if not self._sendImageSize(softdeviceSize, bootloaderSize, appSize):
			return False

		# Seems like we need to wait for pstorage clear to be done here
		time.sleep(10)

		# Send init packet
		if not self._sendOpcode(DfuOpcode.INITIALIZE_DFU, DfuInitPacket.RECEIVE_INIT_PACKET):
			return False
		if not self._sendInitPacket(0, 0, 0, DfuSoftDeviceVersion.ANY, crc):
			return False
		if not self._sendOpcode(DfuOpcode.INITIALIZE_DFU, DfuInitPacket.INIT_PACKET_COMPLETE):
			return False

		# Send command to set DFU in firmware receive state.
		if not self._sendOpcode(DfuOpcode.RECEIVE_FIRMWARE_IMAGE):
			return False

		self.log.i("Start sending data")
		# Send hex file data packets
		timeStart = time.time()
		chunk = 1
		for i in range(0, binSize, CHUNK_SIZE):
			if not self._sendData(binArray[i:i + CHUNK_SIZE]):
				return False
			if (chunk % 100 == 0):
				self.log.d("Chunk #%i / %i" % (chunk, binSize / CHUNK_SIZE))
			chunk += 1
		self.log.i("Firmware transferred in %f seconds" % (time.time() - timeStart))

		# Send Validate Command
		self.log.i("Validating...")
		if not self._sendOpcode(DfuOpcode.VALIDATE_FIRMWARE_IMAGE):
			self.log.e("Could not validate firmware.")
			return False

		# Wait a bit for copy on the peer to be finished
		time.sleep(3)

		# Send Activate and Reset Command
		if not self._sendOpcode(DfuOpcode.ACTIVATE_FIRMWARE_AND_RESET):
			self.log.e("Could not activate.")
			return False

		self.log.i("Validated. Rebooting application.", bleLog.LogType.SUCCESS)

		return True


	# Disconnect from peer device if not done already and clean up.
	def disconnect(self):
		self.ble.disconnect()


if __name__ == '__main__':
	log = bleLog.Logger(bleLog.LogLevel.INFO)
	try:
		parser = optparse.OptionParser(usage='%prog -f <hex_file> -a <dfu_target_address>\n\nExample:\n\tdfu.py -f blinky.hex -a cd:e3:4a:47:1c:e4',
									   version='0.1')

		parser.add_option('-a', '--address',
				action='store',
				dest="address",
				type="string",
				default=None,
				help='DFU target address. (Can be found by running "hcitool lescan")'
		)
		parser.add_option('-f', '--file',
				action='store',
				dest="hex_file",
				type="string",
				default=None,
				help='Hex file to be uploaded.'
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
		parser.add_option('-d', '--debug',
				action='store_true',
				dest="debug",
				help='Debug mode.'
		)
		parser.add_option('-B', '--bootloader',
				action='store_true',
				dest="bootloader",
				help='Upload new bootloader.'
		)

		options, args = parser.parse_args()

	except Exception, e:
		log.e(str(e))
		log.i("For help use --help")
		exit(2)

	if (not options.hex_file) or (not options.address):
		parser.print_help()
		exit(2)

	if not os.path.isfile(options.hex_file):
		log.e("Error: Hex file not found!")
		exit(2)

	if (options.verbose):
		log.setLogLevel(bleLog.LogLevel.DEBUG)
	if (options.debug):
		log.setLogLevel(bleLog.LogLevel.DEBUG2)

	imageType = DfuImageType.APPLICATION
	if (options.bootloader):
		imageType = DfuImageType.BOOTLOADER

	ble_dfu = BleDfuUploader(options.address.upper(), options.hex_file, options.interface, log, imageType)

	# Connect to peer device.
	if not ble_dfu.connect():
		ble_dfu.log.e("Connect failed");
		exit(1)

	# Transmit the hex image to peer device.
	if not ble_dfu.update():
		ble_dfu.log.e("Update failed");
		exit(1)

	# wait a second to be able to recieve the disconnect event from peer device.
	time.sleep(1)

	# Disconnect from peer device if not done already and clean up.
	ble_dfu.disconnect()

	if (not options.bootloader):
		time.sleep(5)

		ble_dfu.log.d("Reconnecting to device to verify firmware.", bleLog.LogType.SUCCESS)

		if (ble_dfu.connect() and (ble_dfu.ble.getHandle(CHAR_RESET) or ble_dfu.ble.getHandle(CHAR_CONTROL))):

			time.sleep(1)

			ble_dfu.log.d("Success!!", bleLog.LogType.SUCCESS)

			ble_dfu.disconnect()

		else:

			ble_dfu.log.e("Failure!!")
