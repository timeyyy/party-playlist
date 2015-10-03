
#http://nbviewer.ipython.org/github/rasbt/python_reference/blob/master/tutorials/key_differences_between_python_2_and_3.ipynb
from __future__ import print_function
from __future__ import with_statement
__version__ = "1.0"
from pprint import pprint
import os

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
import jnius
from jnius import autoclass, cast

import gui_main
import db_utils

class PartyPlaylist(App):
	def build(self):
		#~ return gui_main.MainCarousel()
		l = Button(text="hi")
		l.bind(on_press = lambda wid:self.on_start())
		return l
	
	def on_start(self):
		#~ db_utils.new(overwrite=False)	# make db if it doesnt exist
		#~ self.root.make_music_list()		# root window or parent window i.e our maincoursel
		try:
			#~ f = autoclass("java.io.File")	
			
			#~ print(next(os.walk(os.sep))[1])	# just the dirs
			
			os.chdir(os.sep)
			print(next(os.walk("."))[1])
			print('2222222222222222222222222222222222222222222222222')
			paths = ("/sdcard/media/music","/sdcard/music","/home/alfa/Downloads","/daccc")
			#~ for path in paths:
			for root, dirs, files in os.walk('.'):
				print(root)
				#~ print(root,dirs,files)
				if './mnt/sdcard/medi' in root:continue
				for file in files:
					if '.mp3' in file:
						
						uni = file.decode('utf8')
						print('11111111')
						print(uni)
						#~ print(file.decode("utf-8"))
			#~ for i in next(os.walk(os.getcwd()))[1]:
				#~ os.chdir(i)
				#~ os.chdir('..')
				#~ print("cwd  . ",os.getcwd())
				
				
				
			#~ autoclass('android.speech.tts.TextToSpeech')
			#~ autoclass('File')
		except jnius.JavaException:
			print("ERROR")	
	def on_resume(self):
		print('resuming')
	def on_pause(self):
		print('pausing')
	def on_stop(self):
		print('app closed')
	
if __name__ == '__main__':
	PartyPlaylist().run()
