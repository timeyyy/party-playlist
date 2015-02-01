from __future__ import print_function
from __future__ import with_statement
import os

from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView


# this will update the graphics automatically (75% done)
#~ pb.value = 750
class Main(Carousel):
	#http://kivy.org/docs/api-kivy.uix.carousel.html?highlight=.uix#kivy.uix.carousel
	def __init__(self, **kwargs):
		Carousel.__init__(self,**kwargs)
		self.direction = 'right'
		self.loop = 1
		self.screen_1 = Welcome()
		self.screen_2 = ViewList()
		self.add_widget(self.screen_1)
		self.add_widget(self.screen_2)
		
		#~ self.cols = 3 
		#~ b1 = Button(text='Create List')
		#~ b1.bind(on_press=lambda s:print('create'))
		#~ self.add_widget(b1)
		#~ 
		#~ b2 = Button(text='Push')
		#~ b2.bind(on_press=lambda s:print('push to server'))
		#~ self.add_widget(b2)
		#~ 
		#~ b3 = Button(text='View List')
		#~ b3.bind(on_press=lambda s:print('view list'))
		#~ self.add_widget(b3)
		
		#~ self.username = Label(multiline=False)
		#~ self.add_widget(self.username)
		#~ self.add_widget(Label(text='password'))
		#~ self.password = TextInput(password=True, multiline=False)
		#~ self.add_widget(self.password)

#http://kivy.org/docs/api-kivy.uix.pagelayout.html?highlight=.uix#kivy.uix.pagelayout
#http://kivy.org/docs/api-kivy.uix.codeinput.html?highlight=.uix#kivy.uix.codeinput

class Welcome(GridLayout):
	intro_text = """
	Welcome to Party Playlist!
	
	Your music playlist will automatically be created if one is not present.
	
	If you have Nfc on your android phone, after enabling it you can put your
	phone next to the rasperry pi to transfer songs!
	
	Otherwise click transfer over internet!
	
	To view your Playlist swipe to the side
	"""
	def __init__(self, **kwargs):
		GridLayout.__init__(self, **kwargs)
		self.cols = 1
		self.spacing = 10
		self.label = Label(text=self.intro_text)
		self.add_widget(self.label)
		self.recreate_list = Button(text='New List')
		self.recreate_list.bind(on_press=self.make_music_list)
		self.add_widget(self.recreate_list)
		self.transfer_wifi = Button(text='Transfer over Net')
		self.add_widget(self.transfer_wifi)

		self.make_music_list()
		
	def make_music_list(self, *args):
		def hard_drive():
			pass
		def facebook():
			pass
		print('Making new music ')
		print(os.listdir(os.getcwd()))

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
