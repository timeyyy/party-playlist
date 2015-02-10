import os

import pyaudio
import wave

from pydub import AudioSegment

MUSIC_DIR = "~/music"
FILE = 'waves1.wav'
FILE_SIZE = os.path.getsize(FILE)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

chunk = 1024
def run():
	filenames = []						# Get all files in the cwd		#http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
	for root, dirs, files in os.walk(MUSIC_DIR):	# add to tims tools for listing files...
		root_and_files = [os.path.join(root, file) for file in files]
		filenames.extend(root_and_files)
		break
	
	for file in filenames:
		print("Transcodeing into wav", file)
		try:
			song = AudioSegment.from_mp3(file)
		except Exception:
			print('Problems happend')
			continue
		EXPORT_NAME = "exported.wav"
		song.export(EXPORT_NAME, format="wav")
		play(EXPORT_NAME)
		
	
def play(song):
	print('playing song now!')
	wf = wave.open(song, 'rb')
	p = pyaudio.PyAudio()
	stream = p.open(
		format = p.get_format_from_width(wf.getsampwidth()),
		channels = wf.getnchannels(),
		rate = wf.getframerate(),
		output = True)
	data = wf.readframes(chunk)
 
	while data != '':
		stream.write(data)
		data = wf.readframes(chunk) 
	stream.close()
	p.terminate()
