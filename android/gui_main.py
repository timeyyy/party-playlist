from __future__ import print_function
from __future__ import with_statement
import os
from os.path import sep, expanduser, isdir, dirname
from pprint import pprint

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView
from kivy.garden.filebrowser import FileBrowser
from kivy.properties import ObjectProperty
import jnius
from jnius import autoclass, cast
		
import func
import db_utils

class MainCarousel(Carousel):	
	
	def make_music_list(self, *args):
		viewer = self.ids['viewer']		
		os.chdir(os.sep)
		paths =("/sdcard/media","/home/alfa/Downloads","/daccc")
		for path in paths:
			for track in func.hard_drive(path):		# this generator auto adds to db and returns the tracks
				try:
					viewer.text = '{0}\n{1} :: {2}'.format(viewer.text, track.artist, track.title)
				except AttributeError:pass	# if any artist or titles are none do not add em to the viewer
			
		for track in db_utils.Track.select().order_by(db_utils.Track.artist):
			print(track.artist)	
				
class Welcome(BoxLayout):
	intro_text = """
	Welcome to Party Playlist!
	
	Your music playlist will automatically be created if one is not present.
	
	If you have Nfc on your android phone, after enabling it you can put your
	phone next to the rasperry pi to transfer songs!
	
	Otherwise click transfer over internet!
	
	To view your Playlist swipe to the side
	"""
	def __init__(self, **kwargs):
		BoxLayout.__init__(self, **kwargs)
		self.orientation = 'vertical'
		#~ self.cols = 1
		#~ self.spacing = 10
		label = Label(text=self.intro_text)
		self.add_widget(label)
		recreate_list = Button(text='New List')
		recreate_list.bind(on_press=self.make_music_list)
		self.add_widget(recreate_list)
		settings=Settings()
		self.add_widget(settings)
		self.transfer_wifi = Button(text='Transfer over Net')
		self.add_widget(self.transfer_wifi)

		
class ViewList(GridLayout):
	def __init__(self, **kwargs):
		GridLayout.__init__(self, **kwargs)
		self.cols = 1
		self.spacing = 10
		self.label = Label(text='Your playlist and stuff')
		
		self.scroll_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
		self.scroll_layout.bind(minimum_height=self.scroll_layout.setter('height'))
		for i in range(30):
			btn = Button(text=str(i), size_hint_y=None, height=40)
			self.scroll_layout.add_widget(btn)
		self.scroll = ScrollView(size_hint=(None, None), size=(400, 400))
		self.scroll.add_widget(self.scroll_layout)
		
		self.add_widget(self.label)
		self.add_widget(self.scroll)
		
		#~ pb = ProgressBar(max=1000)
		#~ pb.value = 750
		#http://kivy.org/docs/api-kivy.uix.progressbar.html?highlight=.uix#kivy.uix.progressbar

class Settings(GridLayout):
	def __init__(self, **kwargs):	
		GridLayout.__init__(self, **kwargs)
		self.cols = 1
		#~ self.spacing = 10
		label = Label(text='Select Music Dir')
		self.add_widget(label)
		browse = GetFolder()
		self.add_widget(browse)

class GetFolder(FileBrowser):
	def __init__(self, **kwargs):
		FileBrowser.__init__(self,**kwargs)
		self.select_string = 'Select'
		self.dirselect = 1

		user_path = expanduser('~') + sep + 'Documents'
		self.favorites = [(user_path, 'Documents')]

		self.bind(on_success=self._fbrowser_success,
				on_canceled=self._fbrowser_canceled)

	def _fbrowser_canceled(self, instance):
		print('cancelled, Close self.')

	def _fbrowser_success(self, instance):
		print(instance.selection)
