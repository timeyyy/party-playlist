import os
import queue
import _thread as thread
import subprocess
import time 
from glob import glob

from pydub import AudioSegment

class MusicPlayer():
	def __init__(self, output_dir, input_dir):
		self.output_dir = output_dir
		self.input_dir = input_dir
		self.queue = queue.Queue()
		thread.start_new_thread(self.play,())
		self.dummy()
	
	def dummy(self):
		while 1:
			print('Waiting for input!')
			print(self.input_dir)
			for file in glob(self.input_dir+"/*.wav"):
				print('putting on the queue',file)
				self.queue.put(os.path.join(self.input_dir, file))
			time.sleep(2)
			
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
				print(track)
				#~ subprocess.call(['aplay',os.path.join(self.input_dir,track)])
				subprocess.call(['aplay',track])
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
def test()
	import yaml
	with open("config.conf", 'r') as ymlfile:
		CFG = yaml.load(ymlfile)
	player = MusicPlayer(CFG['aplay']['output_dir'], CFG['aplay']['input_dir'])
	
	
if __name__ == '__main__':		
	pass
