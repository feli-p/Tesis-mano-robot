import serial
#import time

class manoArduino():
	def __init__(self, puerto, baudaje, tiempoEspera=1):
		"""
        Constructor de clase. Construye el objeto que se comunica con el arduino.
        """
		self.port = puerto
		self.baudrate = baudaje
		self.timeout = tiempoEspera
		self.arduino = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

	def writeArduino(self, x):
		self.arduino.write(bytes(x, 'utf-8'))
		#time.sleep(0.05)

	def readArduino(self):
		while self.arduino.inWaiting() > 0:
			print(self.arduino.readline().decode('utf-8'))


def main():
	# Para provar comandos con un servo motor.
	arduino = manoArduino('COM4', 115200)
	arduino.readArduino()
	#'''
	num = input("Enter a number:")
	value = arduino.writeArduino(num + "\n")
	arduino.readArduino
	#'''
	for i in range (181):
		string = "S1 " + str(i)
		print(string)
		value = arduino.writeArduino(string + "\n")
		arduino.readArduino
		#time.sleep(.5)
	for i in range(181):
		string = "S1 " + str(180-i)
		value = arduino.writeArduino(string + "\n")
		arduino.readArduino
		#time.sleep(.5)
	#'''


if __name__ == "__main__":
	while True:
		main()