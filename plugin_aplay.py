import os
from contextlib import contextmanager
from collections import deque
import queue
import _thread as thread
import subprocess
import time 

from pydub import AudioSegment

MUSIC_DIR = "/home/pi/music"
FILE = 'waves1.wav'
FILE_SIZE = os.path.getsize(FILE)
CHUNK_SIZE = 2048
FORMAT = pyaudio.paInt16
RATE = 44100

chunk = 1024

class MusicPlayer():
	def __init__(self, output_dir, input_dir):
		self.output_dir = outpud_dir
		self.input_dir = input_dir
		self.tracks_to_play = deque()
		self.queue = queue.Queue()
		thread.start_new_thread(play,())
		
	def add_tracks(tracks):
		for track in tracks:
			self.dl()
			self.convert()
			self.queue.put(track)
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
			
		
	def play(self):
		while 1:
			try:
				track = self.queue.get(block=False)
			except queue.Empty:
				pass
			else:	
				print('playing song now!')
				subprocess.call(['aplay',os.path.join(self.input_dir,track)])
				print('Finished playing song ..')
			time.sleep(1)
		
		#~ wf = wave.open(song, 'rb')
		#~ p = pyaudio.PyAudio()
		#~ stream = p.open(
			#~ format = p.get_format_from_width(wf.getsampwidth()),
			#~ channels = wf.getnchannels(),
			#~ rate = wf.getframerate(),
			#~ output = True)
		#~ data = wf.readframes(chunk)
	 #~ 
		#~ while data != '':
			#~ stream.write(data)
			#~ data = wf.readframes(chunk) 
		#~ stream.close()
		#~ p.terminate()
