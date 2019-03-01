import logging
from pprint import pprint
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
from packager.tools.observer import *
from packager.tools.toolbox import *
from packager.tools.toolTip import *

class RenameFileViewer(Frame,Observable):
    def __init__(self,window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observable.__init__(self)
        self.__parent=window
        self.__baseModel=baseModel
        self.__root=window
        self.__topLevel=None
        self.__currentFile=None
        self.__currentPackage=None

    def hide(self):
        self.__topLevel.withdraw()

    def show(self,package, dataPath, item):
        self.notify_all(self, events=['<<DISABLE_ALL>>'])  # update listeners
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("Rename File")
        self.__topLevel.protocol('WM_DELETE_WINDOW',self.onClosing)

        self.__currentPackage=package
        self.__currentFile=item[0]
        self.__dataPath=dataPath
        #=================================================================
        self.__infoFrame=Frame(self.__topLevel)
        self.__fileNameLabel=Label(self.__infoFrame, text="File: ")
        self.__fileNameLabel.grid(column=0, row=0, sticky='W',padx=2, pady=2)

        self.__fileNameValueLabel=Label(self.__infoFrame, text=dataPath+'/'+unsuffix(self.__currentFile['file']['name']))
        self.__fileNameValueLabel.grid(column=1, row=0,sticky='W',padx=2, pady=2)

        self.__fileNewNameEntry = Entry(self.__infoFrame)
        self.__fileNewNameEntry.grid(column=2, row=0, sticky='W', padx=2, pady=2)

        extension=''.join(Path(self.__currentFile['file']['name']).suffixes)
        self.__fileNewNameEntry.insert(END, extension)

        #=====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__btApply = Button(self.__topLevel, text="Apply", command=self.onApply)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.onCancel)
        self.__btApply.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)

    def onClosing(self):
        self.__currentFile = None
        self.__currentPackage = None
        self.notify_all(self, events=['<<DISABLE_ALL>>'])  # update listeners
        self.hide()

    def onApply(self):
        extension=self.__fileNewNameEntry.get().strip()

        if len(extension)>0:
            if extension[0]!='.':
                extension="."+extension

        dstPath=unsuffix(self.__currentFile['file']['name'])+extension

        self.__currentPackage.rename_file(self.__currentFile['file']['name'], self.__dataPath, dstPath)
        self.__currentPackage.save()
        self.notify_all(self, events=['<<UPDATE_EDITOR>>','<<ENABLE_ALL>>']) # update listeners
        self.__currentFile = None
        self.__currentPackage = None
        self.hide()

    def onCancel(self):
        self.__currentFile = None
        self.__currentPackage = None
        self.notify_all(self, events=['<<ENABLE_ALL>>'])  # update listeners
        self.hide()