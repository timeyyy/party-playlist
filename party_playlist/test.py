import platform

from kivy.app import App
from os.path import sep, expanduser, isdir, dirname
from kivy.uix.boxlayout import BoxLayout
from kivy.garden.filebrowser import FileBrowser

class GetFolder(BoxLayout):
	def __init__(self, **kwargs):
		FileBrowser.__init__(self,**kwargs)
		self.select_string = 'Select'

		user_path = expanduser('~') + sep + 'Documents'
		self.favorites = [(user_path, 'Documents')]

		self.bind(	on_success=self._fbrowser_success,
					on_canceled=self._fbrowser_canceled)

	def _fbrowser_canceled(self, instance):
		print 'cancelled, Close self.'

	def _fbrowser_success(self, instance):
		print instance.selection


