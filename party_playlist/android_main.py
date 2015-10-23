
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

import android_gui_main as gui_main
import android_db_utils as db_utils

class PartyPlaylist(App):
    def build(self):
        b1 = Button(id='collection')
        b1.bind(on_press=lambda wid:print('ass'))
        return gui_main.MainGui()
        l = Button(text="hi")
        l.bind(on_press = lambda wid:self.on_start())
        return l

    def on_start(self):
        #~ db_utils.new(overwrite=False)    # make db if it doesnt exist
        #~ self.root.make_music_list()      # root window or parent window i.e our maincoursel
        print('on_start')
        # import time;time.sleep(30)
        return
        try:
            #~ f = autoclass("java.io.File")

            #~ print(next(os.walk(os.sep))[1])  # just the dirs
            
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

'''
interfaces include, cli, gli, and android,
pre much can just have 3 executables,
pass in an argument that specifies the mode otherwise they are all the same?
otherwise need a way to detect mm
for the android version will just pawn off to here?
'''
