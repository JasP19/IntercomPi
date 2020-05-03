import serial
import os, time
import RPi.GPIO as GPIO
from pad4pi import rpi_gpio
import json

command = ""
units = {}
ready = False
ser = None

def makeCall(number):
	global ser

	ser.write(b"ATZ\r\n")
	time.sleep(1)
	print(ser.read(50).decode())

	print("Calling " + number)
	msg = "ATD" + number + ";\r\n"
	ser.write(msg.encode("utf-8"))
	time.sleep(1)
	ended = ""

	startTime = time.time()
	duration = 0

	answered = False

	# limit call to 60 seconds
	while duration < 60:
		ended = ""

		ser.write(b"AT+CLCC")

		ended = ser.read(50).decode(encoding = "utf-8")
		ended = ended + ser.read(50).decode(encoding = "utf-8")
		print(ended)

		if "NO CARRIER" in ended:
			print("No carrier")
			return True

		if "BUSY" in ended:
			print("Line busy")
			return True

		if "ERROR" in ended:
			print("Error occurred")
			return True

		if "+CLCC:" in ended:
			answered = True
			print("Connected " + ended)

		time.sleep(0.5)
		duration = time.time() - startTime

	return True

def handleKeyPress(key):
	global command
	global units
	global ready

	if not ready:
		print("Not connected to network yet")
		return

	if key == "#":
		print("unit"+command)

		try:
			callNext = True;

			for number in units["unit"+command]["numbers"]:
				if callNext:
					callNext = makeCall(number)

		except Exception as e:
			print("Unit not found. Please try again. Error: " + str(e))

		command = ""
		return

	command = command + key

def setup():
	global units
	global ready
	global ser

	ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=2)

	KEYPAD = [
		["1", "2", "3"],
		["4", "5", "6"],
		["7", "8", "9"],
		["*", "0", "#"]
	]

	ROW_PINS = [21, 20, 16, 12]
	COL_PINS = [26, 19, 13]

	factory = rpi_gpio.KeypadFactory()
	keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
	keypad.registerKeyPressHandler(handleKeyPress)

	GPIO.setup(4, GPIO.OUT)

	GPIO.output(4, GPIO.LOW)
	time.sleep(4)
	GPIO.output(4, GPIO.HIGH)
	time.sleep(15)

	with open("config.json", "r") as config:
		units = json.load(config)

	registered = ""
	ser.write(b"AT+CREG?\r\n")
	registered = ser.read(50).decode(encoding="utf-8")
	print(registered)

	while "OK" not in registered:
		registered = ""
		GPIO.output(4, GPIO.LOW)
		time.sleep(4)
		GPIO.output(4, GPIO.HIGH)
		time.sleep(15)
		ser.write(b"AT+CREG?\r\n")
		registered = ser.read(50).decode(encoding="utf-8")
		print(registered)

	ready = True

def loop():
	while True:
		pass
		#check if network lost, set ready to false and attempt to reconnect?
#		time.sleep(1)
#		print("looping")
#		phone = "ATD123456789;\r\n"
#	
#		ser.write(phone)
#		ser.flushInput()
#		break;

def main():
	setup()
	loop()
	GPIO.cleanup()

if __name__ == "__main__":
	main()
