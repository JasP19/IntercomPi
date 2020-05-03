import serial
import time

ser = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=2)
ser.write(b"AT\n")
time.sleep(1)
rec = ser.read(50)
print(rec)
