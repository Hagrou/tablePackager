import logging

import urllib.request
from tkinterhtml import HtmlFrame
from pprint import pprint
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
from packager.tools.observer import *
from packager.tools.toolbox import *
from packager.tools.toolTip import *

class HelpViewer(Frame):
    def __init__(self,window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        self.__parent=window
        self.__baseModel=baseModel
        self.__root=window
        self.__topLevel=None
        self.__visible=False
        self.__body=''
        with open(self.__baseModel.baseDir + "help/help.html", 'r') as content_file:
            self.__body=content_file.read()

        self.__body=self.__body.replace('@baseDir', self.__baseModel.baseDir)
        print(self.__body)


    def hide(self):
        self.__visible = False
        self.__topLevel.withdraw()

    def show(self):
        if self.__visible:
            return
        self.__visible=True
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("Help ")
        self.__topLevel.protocol('WM_DELETE_WINDOW',self.onClosing)

        frame = HtmlFrame(self.__topLevel, horizontal_scrollbar="auto")
        frame.grid(sticky=tk.NSEW)

        frame.set_content('<html><body>'+self.__body+'</body></html>')

        #frame.set_content(urllib.request.urlopen("http://thonny.cs.ut.ee").read().decode())
        #frame.set_content(urllib.request.urlopen("http://thonny.cs.ut.ee").read().decode())
        # print(frame.html.cget("zoom"))

        #root.columnconfigure(0, weight=1)
        #root.rowconfigure(0, weight=1)
        #root.mainloop()


    def onClosing(self):
        self.hide()
