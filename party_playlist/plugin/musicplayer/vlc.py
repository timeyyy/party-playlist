import os
import queue
import _thread as thread
import subprocess
import time 
from glob import glob
import re
from multiprocessing.pool import ThreadPool
import requests
import string
import unicodedata

class MusicPlayer():
	def __init__(self, CFG):
		self.features = ('stream', 'local', 'http', 'all_formats')
		self.CFG = CFG
		#~ self.output_dir = output_dir
		#~ self.input_dir = input_dir
		self.track_queue = queue.Queue()
		thread.start_new_thread(self.read_queue,())

	def start(self):
		#~ mode = kwargs.get('mode')
		port = self.CFG['playing']['port']
		if not port:
			port = 1250
		cmd = 'vlc -I rc --rc-host localhost:' + str(port)
		return cmd
		#~ args = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr= subprocess.PIPE).communicate()
		#~ print('finished communicatieng',args)
	def http_pause(self):
		self.http('pause')
	def http_next(self):
		self.http('next')
	def http_prev(self):
		self.http('prev')
	def http_play(self, track=None):
		if track:
			self.http('add '+ track)
		else:
			self.http('play')
	def http_add(self, arg):
		self.http('enque ' + arg)
	def add_track(self, tracks):
		self.track_queue.put(tracks)
	def read_queue(self):
		while 1:
			try:
				track = self.track_queue.get(block=False)
			except queue.Empty:
				pass
			else:	
				print('enquing the track now!')
				self.http('enque ' + track)
				#~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
				print('Finished enqueuing ..')
			time.sleep(1)
			
def add_tracks(tracks):
	self.dl()
	self.convert()
	self.queue.put(track)
from pydub import AudioSegment		
def convert():
	filenames = []						# Get all files in the cwd		#http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
	for root, dirs, files in os.walk(MUSIC_DIR):	# add to tims tools for listing files...
		root_and_files = [os.path.join(root, file) for file in files]
		filenames.extend(root_and_files)
		break
	
	for file in filenames:
		print("Transcodeing into wav", file)
		try:
			pass
			song = AudioSegment.from_mp3(file)
		except Exception as err:
			print(err)
			print('Problems happend')
			continue
		EXPORT_NAME = file.split(os.sep)[-1]
		#print(EXPORT_NAME)
		song.export(EXPORT_NAME, format="wav")
		#play(EXPORT_NAME)
	
def dummy(self):
	while 1:
		print('Waiting for input!')
		print(self.input_dir)
		for file in glob(self.input_dir+"/*.wav"):
			print('putting on the queue',file)
			self.queue.put(os.path.join(self.input_dir, file))
		time.sleep(2)
	while 1:
		try:
			track = self.track_queue.get(block=False)
		except queue.Empty:
			pass
		else:	
			print('playing song now!')
			print(track)
			#~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
			subprocess.call(['aplay',track])
			print('Finished playing song ..')
		time.sleep(1)

if __name__ == '__main__':		
	with open("config.conf", 'r') as ymlfile:
		CFG = yaml.load(ymlfile)
	mplayer = MusicPlayer()
