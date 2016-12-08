__author__ = 'Bart van Vliet'

import binascii
import struct

class Conversion:

	####################################
	# Conversions between uint and int #
	####################################
	@staticmethod
	def uint8_to_int8(byte):
		"""	Convert an unsigned byte to a signed byte """
		res = byte
		if (res > 127):
			res -= 256
		return res

	@staticmethod
	def uint16_to_int16(val):
		""" Convert an uint16 to a int16 """
		res = val
		if (res > 32767):
			res -= 65536
		return res

	@staticmethod
	def uint32_to_int32(val):
		""" Convert an uint32 to a int32 """
		res = val
		if (res > 2147483647):
			res -= 4294967296
		return res

	@staticmethod
	def int8_to_uint8(byte):
		"""	Convert a signed byte to an unsigned byte """
		res = byte
		if (res < 0):
			res += 256
		return res

	#######################################
	# Conversions between uint8 and float #
	#######################################
	@staticmethod
	def uint8_array_to_float(arr8):
		""" Convert an array of 4 bytes to a float """
		return struct.unpack('<f', bytearray(arr8))[0]

	@staticmethod
	def float_to_uint8_array(val):
		""" Convert a float to an array of 4 bytes """
		return bytearray(struct.pack('<f', val))

	########################################
	# Conversions between uint8 and uint16 #
	########################################
	@staticmethod
	def uint8_to_uint16(byte0, byte1):
		""" Convert 2 bytes to a uint16 """
		return (byte1 << 8) + byte0

	@staticmethod
	def uint8_array_to_uint16(arr8):
		""" Convert an array of 2 bytes to a uint16 """
		return (arr8[1] << 8) + arr8[0]

	@staticmethod
	def uint16_to_uint8_array(value):
		""" Convert a number into an array of 2 bytes. """
		return [
			(value >> 0 & 0xFF),
			(value >> 8 & 0xFF)
		]

	@staticmethod
	def uint8_array_to_uint16_array(arr8):
		"""	Convert a uint8 array to a uint16 array	"""
		arr16 = []
		for i in range(1, len(arr8), 2):
#			arr16.append(Conversion.uint8_array_to_uint16(arr8[i-1 : i+1]))
			arr16.append(Conversion.uint8_to_uint16(arr8[i-1], arr8[i]))
		return arr16

	@staticmethod
	def uint16_array_to_uint8_array(arr16):
		"""	Convert a uint16 array to a byte array """
		arr8 = []
		for val in arr16:
			arr8.extend(Conversion.uint16_to_uint8_array(val))
		return arr8


	########################################
	# Conversions between uint8 and uint32 #
	########################################
	@staticmethod
	def uint8_to_uint32(byte0, byte1, byte2, byte3):
		""" Convert 4 bytes to a uint32 """
		return (byte3 << 24) + (byte2 << 16) + (byte1 << 8) + byte0

	@staticmethod
	def uint8_array_to_uint32(arr8):
		""" Convert an array of 4 bytes to a uint32 """
		return (arr8[3] << 24) + (arr8[2] << 16) + (arr8[1] << 8) + arr8[0]

	@staticmethod
	def uint32_to_uint8_array(value):
		""" Convert a number into an array of 4 bytes. """
		return [
			(value >> 0 & 0xFF),
			(value >> 8 & 0xFF),
			(value >> 16 & 0xFF),
			(value >> 24 & 0xFF)
		]

	@staticmethod
	def uint8_array_to_uint32_array(arr8):
		"""	Convert a uint8 array to a uint16 array	"""
		arr32 = []
		for i in range(3, len(arr8), 4):
#			arr32.append(Conversion.uint8_array_to_uint32(arr8[i-3 : i+1]))
			arr32.append(Conversion.uint8_to_uint32(arr8[i-3], arr8[i-2], arr8[i-1], arr8[i]))
		return arr32

	@staticmethod
	def uint32_array_to_uint8_array(arr32):
		"""	Convert a uint32 array to a byte array """
		arr8 = []
		for val in arr32:
			arr8.extend(Conversion.uint32_to_uint8_array(val))
		return arr8


	##############################
	# uint8 array to/from string #
	##############################
	@staticmethod
	def uint8_array_to_string(arr8):
#		string = ""
#		for i in range(0, len(arr8)):
#			string += chr(arr8[i])
#		return string
		return str(bytearray(arr8))

	@staticmethod
	def string_to_uint8_array(string):
#		arr8 = []
#		for i in range(0, len(string)):
#			arr8.append(ord(string[i]))
#		return arr8
		return bytearray(string)


	########################
	# Number to hex string #
	########################
	@staticmethod
	def uint8_to_hex_string(val):
		if (val > 255 or val < 0):
			raise Exception("Value must be of type uint8")
		hex_str = "%02x" % val
		return hex_str

	@staticmethod
	def uint8_array_to_hex_string(arr):
#		hex_str = Conversion.uint8_to_hex_string(arr[0])
#		for i in range(1, len(arr)):
#			hex_str += Conversion.uint8_to_hex_string(arr[i])
#		return hex_str
		return binascii.b2a_hex(bytearray(arr)).decode('utf-8')

	@staticmethod
	def uint16_to_hex_string(val):
		arr8 = Conversion.uint16_to_uint8_array(val)
		return Conversion.uint8_array_to_hex_string(arr8)

	@staticmethod
	def uint32_to_hex_string(val):
		arr8 = Conversion.uint32_to_uint8_array(val)
		return Conversion.uint8_array_to_hex_string(arr8)


	#######################
	# Hex string to array #
	#######################
	@staticmethod
	def hex_string_to_uint8_array(hexStr):
#		""" Convert a string which represents a hex byte buffer to an uint8 array """
#		""" Only converts buffer from start to start+size bytes """
#		buf = buffer_str.split(" ")
#		if (size == False):
#			size=len(buf)
#		arr = []
#		for i in range(start, start+size):
#			arr.append(int(buf[i], 16))
#		return arr
		"""
		Converts a hexadecimal string to a byte array
		:param hexStr: hexadecimal string to be converted
		:type hexStr: str
		:rtype: bytearray
		"""
		return bytearray(binascii.a2b_hex(hexStr.encode('utf-8')))

	@staticmethod
	def hex_string_to_uint16_array(hexStr):
#	def hex_string_to_uint16_array(buffer_str, start=0, size=False):
#		""" Convert a string which represents a hex byte buffer to an uint16 array """
#		""" Only converts buffer from start to start+size*2 bytes """
#		buf = buffer_str.split(" ")
#		if (size == False):
#			size=len(buf)/2
#		arr16 = []
#		for i in range(0, size):
#			arr16.append(Conversion.uint8_array_to_uint16([int(buf[start+2*i], 16), int(buf[start+2*i+1], 16)]))
#		return arr16
		"""
		Converts a hexadecimal string to a uint16 array
		:param hexStr: hexadecimal string to be converted
		:type hexStr: str
		:rtype: list
		"""
		arr8 = bytearray(binascii.a2b_hex(hexStr.encode('utf-8')))
		return Conversion.uint8_to_uint16(arr8)

	@staticmethod
	def hex_string_to_uint32_array(hexStr):
#	def hex_string_to_uint32_array(buffer_str, start=0, size=False):
#		""" Convert a string which represents a hex byte buffer to an uint32 array """
#		""" Only converts buffer from start to start+size*4 bytes """
#		buf = buffer_str.split(" ")
#		if (size == False):
#			size=len(buf)/4
#		arr32 = []
#		for i in range(0, size):
#			arr32.append(Conversion.uint8_array_to_uint32([int(buf[start+4*i], 16), int(buf[start+4*i+1], 16), int(buf[start+4*i+2], 16), int(buf[start+4*i+3], 16)]))
#		return arr32
		"""
		Converts a hexadecimal string to a uint32 array
		:param hexStr: hexadecimal string to be converted
		:type hexStr: str
		:rtype: list
		"""
		arr8 = bytearray(binascii.a2b_hex(hexStr.encode('utf-8')))
		return Conversion.uint8_to_uint32(arr8)

	@staticmethod
	def address_to_uint8_array(addressStr):
		"""
		Converts a bluetooth address string to a uint8 array
		:param addressStr: address string to be converted, must be like: "01:23:45:67:89:AB"
		:type addressStr: str
		:rtype: list
		"""
		hexStrArr = addressStr.split(":")
		if (len(hexStrArr) != 6):
			return []

		arr8 = []
		for p in reversed(hexStrArr):
			arr8.append(Conversion.hex_string_to_uint8_array(p)[0])
		return bytearray(arr8)

