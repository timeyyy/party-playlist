import os

import pyaudio
import wave

from pydub import AudioSegment

FILE = 'waves1.wav'
FILE_SIZE = os.path.getsize(FILE)
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

chunk = 1024
def run():
	song = AudioSegment.from_mp3()
	print(song.__dict__)
def play():
	wf = wave.open(FILE, 'rb')
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
