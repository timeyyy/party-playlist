"""
Example module for testing this should work fine on 2 and 3
"""

import past

import sys
import time

try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk

LABELS = ['ham', 'spam', 'foo', 'bar']

#~ time.sleep(0.1)
#~ sys.exit()

root = tk.Tk()
for text in LABELS:
	tk.Label(root, text=text).pack()
root.after(100, sys.exit)
root.mainloop()
