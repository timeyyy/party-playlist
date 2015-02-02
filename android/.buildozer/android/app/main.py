
#http://nbviewer.ipython.org/github/rasbt/python_reference/blob/master/tutorials/key_differences_between_python_2_and_3.ipynb
from __future__ import print_function
from __future__ import with_statement
import kivy
#~ kivy.require('1.0.6') # replace with your current kivy version !
__version__ = "1.0"
from kivy.app import App

import gui_main
from kivy.uix.button import Button
from kivy.uix.label import Label


class PartyPlaylist(App):
    def build(self):
        return gui_main.Main()

	def on_resume(self):
		print('resuming')
	def on_pause(self):
		print('pausing')
	def on_stop(self):
		print('app closed')
	
if __name__ == '__main__':
    PartyPlaylist().run()
