from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *


class ConfigViewer(Frame):
    def __init__(self, window, base_model, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)

        self.__parent = window
        self.__baseModel = base_model
        self.__root = window
        self.__topLevel = None
        self.__btDirImage = PhotoImage(file=base_model.base_dir + "images/btDir.png")
        self.__is_hide = True

    def hide(self):
        self.__topLevel.withdraw()
        self.__is_hide = True

    def show(self):
        if not self.__is_hide:
            return
        self.__is_hide = False
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("Configuration")
        self.__topLevel.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.__topLevel.iconbitmap(self.__baseModel.base_dir + "images/tablePackager_128x128.ico")

        # =================================================================
        self.__infoFrame = Frame(self.__topLevel)

        self.__visualPinballPathLabel = Label(self.__infoFrame, text="visual pinball path: ")
        self.__visualPinballPathLabel.grid(column=0, row=0, sticky='W', padx=2, pady=2)
        self.__visualPinballPathEntry = Entry(self.__infoFrame)
        self.__visualPinballPathEntry.grid(column=1, row=0, padx=2, pady=2)
        self.__visualPinballPathEntry.insert(END, self.__baseModel.visual_pinball_path)
        self.__visualPinballPathDirBt = Button(self.__infoFrame, image=self.__btDirImage,
                                               command=self.on_choose_visual_pinball_path_dir)
        self.__visualPinballPathDirBt.grid(column=2, row=0, sticky=E, padx=2, pady=2)

        self.__pinballXPathLabel = Label(self.__infoFrame, text="Pinball X path: ")
        self.__pinballXPathLabel.grid(column=0, row=1, sticky='W', padx=2, pady=2)
        self.__pinballXPathPathEntry = Entry(self.__infoFrame)
        self.__pinballXPathPathEntry.grid(column=1, row=1, padx=2, pady=2)
        self.__pinballXPathPathEntry.insert(END, self.__baseModel.pinballX_path)
        self.__pinballXPathPathDirBt = Button(self.__infoFrame, image=self.__btDirImage,
                                              command=self.on_choose_pinball_x_path_dir)
        self.__pinballXPathPathDirBt.grid(column=2, row=1, sticky=E, padx=2, pady=2)

        self.__pinupSystemPathLabel = Label(self.__infoFrame, text="Pinball X path: ")
        self.__pinupSystemPathLabel.grid(column=0, row=2, sticky='W', padx=2, pady=2)
        self.__pinupSystemPathEntry = Entry(self.__infoFrame)
        self.__pinupSystemPathEntry.grid(column=1, row=2, padx=2, pady=2)
        self.__pinupSystemPathEntry.insert(END, self.__baseModel.pinupSystem_path)
        self.__pinupSystemPathDirBt = Button(self.__infoFrame, image=self.__btDirImage,
                                             command=self.on_choose_pinup_system_path_dir)
        self.__pinupSystemPathDirBt.grid(column=2, row=2, sticky=E, padx=2, pady=2)

        # =====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__btSave = Button(self.__topLevel, text="Save", command=self.on_save)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.on_cancel)
        self.__btSave.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)

    def on_closing(self):
        self.hide()

    def on_choose_visual_pinball_path_dir(self):
        self.__is_hide = True
        path = filedialog.askdirectory(initialdir=self.__visualPinballPathEntry.get())
        if path is None or path == '':
            return
        self.__visualPinballPathEntry.delete(0, 'end')
        self.__visualPinballPathEntry.insert(END, path)

    def on_choose_pinball_x_path_dir(self):
        self.__is_hide = True
        path = filedialog.askdirectory(initialdir=self.__pinballXPathPathEntry.get())
        if path is None or path == '':
            return
        self.__pinballXPathPathEntry.delete(0, 'end')
        self.__pinballXPathPathEntry.insert(END, path)

    def on_choose_pinup_system_path_dir(self):
        self.__is_hide = True
        path = filedialog.askdirectory(initialdir=self.__pinupSystemPathEntry.get())
        if path is None or path == '':
            return
        self.__pinupSystemPathEntry.delete(0, 'end')
        self.__pinupSystemPathEntry.insert(END, path)

    def on_save(self):
        self.__baseModel.config.set('visual_pinball_path', self.__visualPinballPathEntry.get())
        self.__baseModel.config.set('pinballX_path', self.__pinballXPathPathEntry.get())
        self.__baseModel.config.set('pinupSystem_path', self.__pinupSystemPathEntry.get())
        self.__baseModel.config.save()
        self.hide()

    def on_cancel(self):
        self.hide()
