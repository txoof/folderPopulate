

from Tkinter import Frame, Tk, BOTH, Text, Menu, END
import tkFileDialog 

import csv
import sys
import os
import re
import datetime
import unicodedata


# In[2]:

class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent)   
         
        self.parent = parent        
        self.initUI()
        
        
    def initUI(self):
      
        self.parent.title("File dialog")
        self.pack(fill=BOTH, expand=1)
        
        try:
            #self.parent.attributes('-topmost', True)
            self.parent.lift()
        except Exception as e:
            print e
            
        menubar = Menu(self.parent)
        
        self.parent.config(menu=menubar)

        
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label = 'foobar', command = self.onOpen)
        menubar.add_cascade(label="File", menu=fileMenu)        
        
        
        
        self.txt = Text(self)
        self.txt.pack(fill=BOTH, expand=1)


    def onOpen(self):
      
        ftypes = [('All', '*'), ('txt files', '*.txt'), ('text files', '*.text'), ('csv files', '*.csv')]
# #         ftypes = (('csv files', '*.csv'),('txt files', '*.txt*'),('text files', '*.text'),('all files', '*.*'))
#         try:
#             dlg = tkFileDialog.Open(self, filetypes = ftypes, initialdir = '~/src/')
#             fl = dlg.show()
#         except (OSError, IOError) as e:
#             fl = 'Error opening file', e

        fl = tkFileDialog.askopenfilename()
        
        if fl != '':
            text = self.readFile(fl)
            self.txt.insert(END, 'Loaded file:\n')
            self.txt.insert(END, text)
            
            

    def readFile(self, filename):

        try:
            f = open(filename, "rU")
            text = f.read()
        except (OSError, IOError) as e:
            text = e

        return text
         



# In[3]:

root = Tk()
ex = Example(root)
root.geometry("600x600+10+10")
# root.attributes('-topmost', True)
#     google_main()
root.mainloop()  

