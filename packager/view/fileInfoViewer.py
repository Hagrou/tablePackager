from tkinter import *
from tkinter.ttk import *

from packager.tools.observer import *
from packager.tools.toolbox import *


class FileInfoViewer(Frame, Observable):
    def __init__(self, window, base_model, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observable.__init__(self)
        self.__parent = window
        self.__base_model = base_model
        self.__root = window
        self.__topLevel = None
        self.__currentFile = None
        self.__currentPackage = None

    def hide(self):
        self.__topLevel.withdraw()

    def show(self, package, dataPath, item):
        self.notify_all(self, events=['<<DISABLE_ALL>>'])  # update listeners
        self.__topLevel = Toplevel(self.__parent)

        self.__topLevel.iconbitmap(self.__base_model.base_dir + "images/tablePackager_128x128.ico")
        self.__topLevel.wm_title("File ")
        self.__topLevel.protocol('WM_DELETE_WINDOW', self.onClosing)

        self.__currentPackage = package
        self.__currentFile = item[0]
        # =================================================================
        self.__infoFrame = Frame(self.__topLevel)
        self.__fileNameLabel = Label(self.__infoFrame, text="File: ")
        self.__fileNameLabel.grid(column=0, row=0, sticky='W', padx=2, pady=2)
        self.__fileNameValueLabel = Label(self.__infoFrame, text=dataPath + '/' + self.__currentFile['file']['name'] + (
                    ' (%s)' % convert_size(self.__currentFile['file']['size'])))
        self.__fileNameValueLabel.grid(column=1, row=0, sticky='W', padx=2, pady=2)

        self.__sha1Label = Label(self.__infoFrame, text="SHA1: ")
        self.__sha1Label.grid(column=0, row=1, sticky='W', padx=2, pady=2)
        self.__sha1ValueLabel = Label(self.__infoFrame, text=self.__currentFile['file']['sha1'])
        self.__sha1ValueLabel.grid(column=1, row=1, sticky='W', padx=2, pady=2)

        self.__versionLabel = Label(self.__infoFrame, text="Version: ")
        self.__versionLabel.grid(column=0, row=2, sticky='W', padx=2, pady=2)
        self.__versionEntry = Entry(self.__infoFrame)
        self.__versionEntry.grid(column=1, row=2, sticky='W', padx=2, pady=2)
        self.__versionEntry.insert(END, self.__currentFile['file']['version'])

        self.__authorLabel = Label(self.__infoFrame, text="Author(s): ")
        self.__authorLabel.grid(column=0, row=3, sticky='W', padx=2, pady=2)
        self.__authorEntry = Entry(self.__infoFrame, width=80)
        self.__authorEntry.grid(column=1, row=3, sticky='W', padx=2, pady=2)
        self.__authorEntry.insert(END, self.__currentFile['file']['author(s)'])

        self.__urlLabel = Label(self.__infoFrame, text="Url: ")
        self.__urlLabel.grid(column=0, row=4, sticky='W', padx=2, pady=2)
        self.__urlEntry = Entry(self.__infoFrame, width=80)
        self.__urlEntry.grid(column=1, row=4, padx=2, pady=2, sticky='W')
        self.__urlEntry.insert(END, self.__currentFile['file']['url'])

        # =====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__btSave = Button(self.__topLevel, text="Save", command=self.onSave)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.on_cancel)
        self.__btSave.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)

    def onClosing(self):
        self.__currentFile = None
        self.__currentPackage = None
        self.notify_all(self, events=['<<ENABLE_ALL>>'])  # update listeners
        self.hide()

    def onSave(self):
        self.__currentFile['file']['author(s)'] = self.__authorEntry.get()
        self.__currentFile['file']['url'] = self.__urlEntry.get()
        self.__currentFile['file']['version'] = self.__versionEntry.get()
        self.__currentPackage.save()
        self.notify_all(self, events=['<<UPDATE_EDITOR>>', '<<ENABLE_ALL>>'])  # update listeners
        self.__currentFile = None
        self.__currentPackage = None
        self.hide()

    def on_cancel(self):
        self.__currentFile = None
        self.__currentPackage = None
        self.notify_all(self, events=['<<ENABLE_ALL>>'])  # update listeners
        self.hide()
