#~ from __future__ import print_function
#~ from __future__ import with_statement
#http://docopt.org/
__doc__ ="""Party Playlist
Usage:
	party_playlist.py new <name> [--timeout --profile --test]
	party_playlist.py load <name> [--timeout]
	party_playlist.py play <name> [--profile]
	party_playlist.py export <name> 
	party_playlist.py cfg 
	party_playlist.py list [name]
	party_playlist.py [-t | --test]

Options:
	new <name>	Create a new playlist and start listening for new users
	load <name>	Loads a previously created list, use timeout to control how long to set it active
	play <name> Just play Tracks
	list [name] Either list all playlists or enter the name or id of the playlist to view specifics
	-t --test	testing mode will create if doesnt exists, and just load if it does
"""

from pprint import pprint
import time
try:
	import _thread as thread
	import queue
except ImportError:
	import thread
	import Queue as queue
try:
	import RPi.GPIO as GPIO
	GPIO.setmode(GPIO.BCM)
except ImportError:pass

from docopt import docopt

import func
import db_utils
#~ import nxppy

class Party():
	# Scanning for button Presses
	# Scanning for input via web interface or app
	
	# Different Playing modes, either via button press or online config
	# Mode 1 Default, is autonomous, uses the default settings to organize
	# a playlist and play the music,  a genre toggle, and a next button
	# Mode 2 only plays music actuall found on devices, then stops. no Discovery mode
	
	# Need a way to choose music output, either hdmi, cable or plug and play
	
	# User can overide playlist by using app or web interface
	
	def __init__(self, name='test', load=False, timeout=False, profile=False,test=False):
		#~ self.input_actions = {5:lambda:print(5),7:None,12:None}
		#self.check_buttons()		# Buttons change the playback mode
		self.queue = queue.Queue()
		thread.start_new_thread(self.listen_nfc_wifi,())	# Check Server for wifi and for nfc connections
		self.check_new_files(name,load,timeout,profile,test)
	
	#~ def check_buttons(self):		# Maps Input Pins to different actions
		#~ prev_input = 0	
		#~ while 1:
			#~ INPUTS = ((i , GPIO.input(i)) for i in (5,17,12)) #pins to check	
			#~ for pin, result in INPUTS:
				#~ if result and not prev_input:
					#~ self.input_actions(pin)
					#~ prev_input = 1
					#~ break
			#~ prev_input = 0
			#~ time.sleep(0.05)	#should help stop bouncing
	
	def listen_nfc_wifi(self):
		while 1:
			print('waiting for inputs!!! so press 1 to demo')
			if input() == '1':
				print('getting shit')
				time.sleep(.2)
				print('finished getting!!!')
				self.queue.put(1)
				time.sleep(.2)
	
	def check_new_files(self,name,load,timeout,profile,test):
		while 1:
			try:
				data = self.queue.get(block=False)
			except queue.Empty:pass	
			else:
				print('doing')
				func.process_tracks(name,load,timeout,profile,test)
		
	def run_down(self):
		'''	add all the songs from the database to PlayistTrack
			
			parse according to setting and add results to FinalPlayList
			
			Play Songs
		
		
		When Genre Changed
		When A New User Adds Data how to minimze calculations	
		
		'''
		pass
	
	def test(self):		
		#~ import random
		#~ while 1:
			#~ pass
			#~ card = nxppy.Mifare()
			#~ try:
				#~ uid = card.select()
			#~ except nxppy.SelectError:
				#~ print('0   ', random.Random())
			#~ else:
				#~ block10bytes = mifare.read_block(10)
				#~ print('1 : ',block10bytes)
			time.sleep(0.4)

if __name__ == '__main__':
	#~ import sys
	#~ print(sys.argv)
	#~ args = docopt(__doc__,argv=['new','testing','--test'])
	args = docopt(__doc__,argv=['load','testing223'])
	args = docopt(__doc__,argv=['list'])
	#~ print(help(docopt))
	#~ pprint(args)
	
	if args['new'] or args['load']:
		LOAD = True
		TEST = False
		if args['new']:
			LOAD = False
		if args['--test']:
			TEST=True
		Party(load=LOAD, name=args['<name>'], timeout=args['--timeout'], profile=args['--profile'], test=TEST)
	elif args['play']:pass
	elif args['export']:pass
	elif args['list']:
		db_utils.list_playlists(args['name'])
	elif args['cfg']:pass
	#~ elif args['-test']:pass
	#~ Party(new=True)
	#~ app = Party()
	 
