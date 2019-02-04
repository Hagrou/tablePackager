import logging
from pprint import pprint
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
from packager.tools.observer import *
from packager.tools.toolbox import *
from packager.tools.toolTip import *

class ConfigViewer(Frame):
    def __init__(self,window,baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)

        self.__parent=window
        self.__baseModel=baseModel
        self.__root=window
        self.__topLevel=None
        self.__btDirImage = PhotoImage(file=baseModel.baseDir+"images/btDir.png")


    def hide(self):
        self.__topLevel.withdraw()

    def show(self):
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("Configuration")
        self.__topLevel.protocol('WM_DELETE_WINDOW',self.onClosing)

        #=================================================================
        self.__infoFrame=Frame(self.__topLevel)

        self.__visualPinballPathLabel=Label(self.__infoFrame, text="visual pinball path: ")
        self.__visualPinballPathLabel.grid(column=0, row=0, sticky='W',padx=2, pady=2)
        self.__visualPinballPathEntry = Entry(self.__infoFrame)
        self.__visualPinballPathEntry.grid(column=1, row=0,padx=2, pady=2)
        self.__visualPinballPathEntry.insert(END, self.__baseModel.visual_pinball_path)
        self.__visualPinballPathDirBt=Button(self.__infoFrame,image=self.__btDirImage, command=self.onChooseVisualPinballPathDir)
        self.__visualPinballPathDirBt.grid(column=2, row=0, sticky=E,padx=2, pady=2)



        self.__pinballXPathLabel = Label(self.__infoFrame, text="Pinball X path: ")
        self.__pinballXPathLabel.grid(column=0, row=1, sticky='W', padx=2, pady=2)
        self.__pinballXPathPathEntry = Entry(self.__infoFrame)
        self.__pinballXPathPathEntry.grid(column=1, row=1, padx=2, pady=2)
        self.__pinballXPathPathEntry.insert(END, self.__baseModel.pinballX_path)
        self.__pinballXPathPathDirBt = Button(self.__infoFrame, image=self.__btDirImage,
                                               command=self.onChoosePinballXPathDir)
        self.__pinballXPathPathDirBt.grid(column=2, row=1, sticky=E, padx=2, pady=2)

        self.__pinupSystemPathLabel = Label(self.__infoFrame, text="Pinball X path: ")
        self.__pinupSystemPathLabel.grid(column=0, row=2, sticky='W', padx=2, pady=2)
        self.__pinupSystemPathEntry = Entry(self.__infoFrame)
        self.__pinupSystemPathEntry.grid(column=1, row=2, padx=2, pady=2)
        self.__pinupSystemPathEntry.insert(END, self.__baseModel.pinupSystem_path)
        self.__pinupSystemPathDirBt = Button(self.__infoFrame, image=self.__btDirImage,
                                               command=self.onChoosePinupSystemPathDir)
        self.__pinupSystemPathDirBt.grid(column=2, row=2, sticky=E, padx=2, pady=2)

        #=====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__btSave = Button(self.__topLevel, text="Save", command=self.onSave)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.onCancel)
        self.__btSave.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)

    def onClosing(self):
        print("closing")
        self.hide()

    def onChooseVisualPinballPathDir(self):
        path = filedialog.askdirectory(initialdir= self.__visualPinballPathEntry.get())
        if path != '':
            self.__visualPinballPathEntry.delete(0, 'end')
            self.__visualPinballPathEntry.insert(END, path)

    def onChoosePinballXPathDir(self):
        path = filedialog.askdirectory(initialdir= self.__pinballXPathPathEntry.get())
        if path != '':
            self.__pinballXPathPathEntry.delete(0, 'end')
            self.__pinballXPathPathEntry.insert(END, path)



    def onChoosePinupSystemPathDir(self):
        path = filedialog.askdirectory(initialdir=self.__pinupSystemPathEntry.get())
        if path != '':
            self.__pinupSystemPathEntry.delete(0, 'end')
            self.__pinupSystemPathEntry.insert(END, path)

    def onSave(self):
        self.__baseModel.config.set('visual_pinball_path', self.__visualPinballPathEntry.get())
        self.__baseModel.config.set('pinballX_path', self.__pinballXPathPathEntry.get())
        self.__baseModel.config.set('pinupSystem_path', self.__pinupSystemPathEntry.get())
        self.__baseModel.config.save()
        self.hide()

    def onCancel(self):
        self.hide()