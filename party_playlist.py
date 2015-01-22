import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

while True:
  #take a reading
  input = GPIO.input(17)
  #if the last reading was low and this one high, print
  if ((not prev_input) and input):
    print("Button pressed")
  #update previous input
  prev_input = input
  #slight pause to debounce
  time.sleep(0.05)
import _thread as thread
from queue import Queue

class Party():
	# Scanning for button Presses
	# Scanning for input via web interface or app
	
	# Different Playing modes, either via button press or online config
	# Mode 1 Default, is autonomous, uses the default settings to organize
	# a playlist and play the music,  a genre toggle, and a next button
	# Mode 2 only plays music actuall found on devices, then stops. no Discovery mode
	
	# Need a way to choose music output, either hdmi, cable or plug and play
	
	# User can overide playlist by using app or web interface
	
	def __init__(self):
		self.data = Queue()
		self.input_actions = {5:lambda:print(5),7:None,12:None}
		self.check_buttons()		# Buttons change the playback mode
	
	
	
	def check_buttons(self):		# Maps Input Pins to different actions
		prev_input = 0
		
		while 1:
			INPUTS = (i , GPIO.input(i) for i in (5,17,12) #pins to check	
			for pin, result in INPUTS:
				if result and not prev_input:
					self.input_actions(pin)
					prev_input = 1
					break
			prev_input = 0
			if not prev_input
			time.sleep(0.05)		#should help stop bouncing 
