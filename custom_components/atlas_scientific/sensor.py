# Under MIT licence
# Release 0.1 (06/08/2019) by segalion at gmail
# ORP & pH tested. DO & EC from datasheets, so possible errors like ORP/OR


import logging
import serial
import io
import fcntl
import string
import time

from homeassistant.helpers.entity import Entity
from homeassistant.const import (
	CONF_NAME, CONF_UNIT_OF_MEASUREMENT, CONF_PORT)
from homeassistant.components.sensor import PLATFORM_SCHEMA
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
#from homeassistant.const import TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)
CONF_OFFSET = 'offset'
# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_PORT): cv.string,
	vol.Optional(CONF_NAME, default='ezo'): cv.string,
	vol.Optional(CONF_OFFSET, default=0.0): vol.Coerce(float)
})

def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Setup the sensor platform."""
	add_devices([AtlasSensor(
		name=config.get(CONF_NAME),
		port=config.get(CONF_PORT),
		offset=config.get(CONF_OFFSET)
	)])

class AtlasSensor(Entity):
	"""Representation of a Sensor."""
	io_mode = 0					# 0 = serial, 1 = I2C
	long_timeout = 1.5         	# the timeout needed to query readings and calibrations
	short_timeout = .5         	# timeout for regular commands
	default_i2dev = "/dev/i2c-1"    # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
	auto_sleep = 1              # enable auto sleep mode after readings

	def __init__(self, name, port, offset):
		"""Initialize the sensor."""
		self._state = None
		self._name = name
		self._offset = offset
		# Identifiers: [ name (from I?), units, icon, auto_sleep ]
		ezos = {"ph": ['ph', 'pH', 'mdi:alpha-h-circle', 1],
			   "orp": ['orp', 'mV', 'mdi:alpha-r-circle', 1],
			   "or": ['orp', 'mV', 'mdi:alpha-r-circle', 1],
			   "orp": ['orp', 'mV', 'mdi:alpha-r-circle', 1],
			   "do": ['dissolved_oxygen','mV', 'mdi:alpha-x-circle', 0],
			   "d.o.": ['dissolved_oxygen','mV', 'mdi:alpha-x-circle', 0],
			   "ec": ['conductivity', "EC", 'mdi:alpha-c-circle', 0],
			   "rtd": [ 'temperature', 'ºC', 'mdi:oil-temperature', 0]}

		_LOGGER.debug("Checking port %s", port)
		self.port = int(port,0)
		if(self.port > 0):
			self.io_mode = 1 # switch to I2C communication
			_LOGGER.info("I2C for Atlas EZO @%02x", self.port)
			self.file_read = io.open(self.default_i2dev, "rb", buffering=0)
			self.file_write = io.open(self.default_i2dev, "wb", buffering=0)

			# initializes I2C to the given port/address
			self.set_i2c_address(self.port)

		else:
			self.io_mode = 0 # serial
			self.port = port
			_LOGGER.info("Serial for Atlas EZO @%s",port)
			self.ser = serial.Serial(port, 9600, timeout=3, write_timeout=3)

			# Reset buffer
			self._read("")
			# Get Status
			status = self._read("Status")
			# Set response ON
			ok = self._read("*OK,1")
			ok += self._read("RESPONSE,1")
			# Set continuos  mode OFF
			c = self._read("C,0")

		# Get kind of EZO
		self._ezo_dev = None
		for i in range(5):
			ezo = self._read("I")
			_LOGGER.debug("I -> check: "+ezo)
			if ezo is not None:
				ezo = ezo.lower().split(',')
				if len(ezo)>2 and ezo[1] in ezos:
					self._ezo_dev = ezos[ezo[1]][0]
					self._ezo_uom = ezos[ezo[1]][1]
					self._ezo_icon = ezos[ezo[1]][2]
					self.auto_sleep = ezos[ezo[1]][3]
					self._ezo_fwversion = ezo[2]
					self._name += ("_" + self._ezo_dev)
					_LOGGER.info("Atlas EZO '%s' version %s detected" % (self._ezo_dev, self._ezo_fwversion ) )
					break
		if self._ezo_dev is None:
			_LOGGER.error("Atlas EZO device error or unsupported: "+ezo )

	def set_i2c_address(self, addr):
		# set the I2C communications to the slave specified by the address
		# The commands for I2C dev using the ioctl functions are specified in
		# the i2c-dev.h file from i2c-tools
		I2C_SLAVE = 0x703
		fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
		fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

	@property
	def name(self):
		"""Return the name of the sensor."""
		# return "Atlas Scientific"
		return self._name

	@property
	def device_class(self):
		"""Return the device class of the sensor."""
		return self._ezo_dev

	@property
	def icon(self):
		"""Return the icon of the sensor."""
		return self._ezo_icon

	@property
	def fw_version(self):
		"""Return the firmware version of the sensor."""
		return self._ezo_fwversion

	@property
	def state(self):
		"""Return the state of the sensor."""
		return self._state

	@property
	def unit_of_measurement(self):
		"""Return the unit of measurement."""
		return self._ezo_uom

	def i2c_write(self, cmd):
		# appends the null character and sends the string over I2C
		cmd += "\00"
		cmd = cmd.encode()
		return self.file_write.write(cmd)

	def i2c_read(self, num_of_bytes=31):
		# reads a specified number of bytes from I2C, then parses and displays the result
		res = self.file_read.read(num_of_bytes)         # read from the board
		response = list(filter(lambda x: x != '\x00', res))     # remove the null characters to get the response
		if response[0] == 1:             # if the response isn't an error
			# change MSB to 0 for all received characters except the first and get a list of characters
			char_list = map(lambda x: chr(x & ~0x80), list(response[1:]))
			# NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, and you shouldn't have to do this!
			return ''.join(char_list)     # convert the char list to a string and returns it
		else:
			_LOGGER.error("I2C read error: " + str(response[0]))
			return ''

	def _read(self,command="R",terminator="\r*OK\r"):
		line = ""
		if self.io_mode == 0:
			self.ser.write((command + "\r").encode())
			for i in range(50):
				line += self.ser.read().decode()
				if ( line[0]=="*" and line[-1]=="\r") or terminator in line: break
			line.replace(terminator,"")
		else:
			self.i2c_write(command)
			# the read and calibration commands require a longer timeout
			if((command.upper().startswith("R")) or
				(command.upper().startswith("CAL"))):
				time.sleep(self.long_timeout)
			elif command.upper().startswith("SLEEP"):
				return "sleep mode"
			else:
				time.sleep(self.short_timeout)
			line = self.i2c_read().rstrip('\x00')
		return line

	def update(self):
		"""Fetch new state data for the sensor.
		"""
		try:
			r = self._read()
			self._state = float(r) + self._offset
			_LOGGER.debug("update %s => '%s'" % ( self.name, self._state ) )
			if self.auto_sleep==1:
				self._read("SLEEP")
		except Exception as e:
			_LOGGER.error("Exception: "+e+"! read '%s'" % r)
		return

	def __del__(self):
		"""close the sensor."""
		if self.io_mode == 1:
			self.file_read.close()
			self.file_write.close()
		else:
			self.ser.close()
