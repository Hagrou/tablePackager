import logging

from tkinter import ttk
from tkinter import *

from packager.view.installedTablesView import *
from packager.view.packagedTablesView import *
from packager.view.packageEditorViewer import *
from packager.view.logViewer import *


class MainWindow(Observer):
    def __init__(self, baseModel, logHandler):
        Observer.__init__(self, baseModel.installedTablesModel)

        baseModel.packagedTablesModel.attach(self)
        self.__backupState={}
        self.__baseModel=baseModel
        self.__window=Tk()

        # create a toplevel menu
        menubar = Menu(self.__window)
        menubar.add_command(label="Options", command=self.onOptionMenu)

        helpMenu = Menu(menubar, tearoff=0)
        helpMenu.add_command(label="Getting Start", command=self.onHelpMenu)
        helpMenu.add_separator()
        helpMenu.add_command(label="About", command=self.onHelpMenu)
        menubar.add_cascade(label="Help", menu=helpMenu)


        # display the menu
        self.__window.configure(menu=menubar)
        self.__window.title("Pincab Table Packager")
        self.__separator=Separator(self.__window, orient=HORIZONTAL)

        self.__installedTablesView=InstalledTablesView(self.__window, self.__baseModel.installedTablesModel)

        self.__progressBar = ttk.Progressbar(self.__window,orient ="horizontal", mode ="indeterminate")
        self.__progressBar["value"] = 0
        self.__progressBar["maximum"]=800


        self.__extractFrame=Frame(self.__window, width=2,relief=GROOVE,borderwidth=4)
        self.__cbExVisualPinball= Checkbutton(self.__extractFrame, text='Visual Pinball1')
        self.__cbExVisualPinball.grid(column=0, row=0, sticky='NW')
        self.__cbExFuturPinball = Checkbutton(self.__extractFrame, text='Futur Pinball', state=DISABLED)
        self.__cbExFuturPinball.grid(column=0, row=1, sticky='NW')
        self.__cbExPinupSystem  = Checkbutton(self.__extractFrame, text='PinUp System')
        self.__cbExPinupSystem.grid(column=0, row=2, sticky='NW')
        self.__cbExPinballX     = Checkbutton(self.__extractFrame, text='Pinball X')
        self.__cbExPinballX.grid(column=0, row=3, sticky='NW')

        self.__btExtractImage = PhotoImage(file="images/btExtract.png")
        self.__btInstallImage = PhotoImage(file="images/btInstall.png")


        #self.__btExtract = Button(self.__extractFrame, text="-- extract -->", command=self.extractOnClick, state=DISABLED)
        self.__btExtract = Button(self.__extractFrame, image=self.__btExtractImage, command=self.extractOnClick,
                                 state=DISABLED)

        self.__btExtract.grid(column=1, row=0, rowspan=4, sticky='NW')

        self.__installFrame = Frame(self.__window, width=2, relief=GROOVE, borderwidth=4)
        self.__cbInsVisualPinball = Checkbutton(self.__installFrame, text='Visual Pinball2')
        self.__cbInsVisualPinball.grid(column=0, row=4, sticky='NW')
        self.__cbInsFuturPinball = Checkbutton(self.__installFrame, text='Futur Pinball', state=DISABLED)
        self.__cbInsFuturPinball.grid(column=0, row=5, sticky='NW')
        self.__cbInsPinupSystem = Checkbutton(self.__installFrame, text='PinUp System')
        self.__cbInsPinupSystem.grid(column=0, row=6, sticky='NW')
        self.__cbInsPinballX = Checkbutton(self.__installFrame, text='Pinball X')
        self.__cbInsPinballX.grid(column=0, row=7, sticky='NW')




        #bt = Button(self.__window, image=self.__btImage, state=NORMAL)
        #bt.grid(row=2, column=1)
        #self.__btInstall = Button(self.__installFrame, text="<-- install --", command=self.installOnClick, state=DISABLED)
        self.__btInstall = Button(self.__installFrame, image= self.__btInstallImage, command=self.installOnClick,
                                  state=DISABLED)

        self.__btInstall.grid(column=1, row=4, rowspan=4, sticky='NW', padx=2, pady=2)

        self.__packagedTablesView = PackagedTablesView(self, self.__window, self.__baseModel)

        self.__logViewer = LogViewer(self.__separator, logHandler)

        self.__installedTablesView.grid(row=0, column=0, sticky=N + S)
        self.__extractFrame.grid(row=0, column=1, sticky=N, pady=22)
        self.__installFrame.grid(row=0, column=1, sticky=S, pady=37)
        self.__packagedTablesView.grid(row=0, column=2, sticky=N + S)
        self.__separator.grid(row=1, column=0,  columnspan=3, padx=5, pady=5, sticky='ns')
        self.__logViewer.grid(row=2, column=0, columnspan=3, sticky=S+E+W)
        self.__progressBar.grid(row=3, column=0, columnspan=3, stick=S+E+W)
        self.__packageEditorViewer = PackageEditorViewer(self.__window, self.__baseModel)
        self.__baseModel.packageEditorModel.attach(self)
        self.__baseModel.packageEditorModel.attach(self.__packagedTablesView)

    def mainLoop(self):
        try:
            self.__window.mainloop()
        except Exception as Err:
            print(Err)

    def onOptionMenu(self):
        print("onMenuOption")

    def onHelpMenu(self):
        print("onHelpMenu")

    def extractOnClick(self):
        self.__baseModel.installedTablesModel.extract_tables()

    def installOnClick(self):
        self.__baseModel.packagedTablesModel.deployPackage()


    def update(self, observable, *args, **kwargs):
        events=kwargs['events']
        logging.debug('MainWindow: rec event [%s]' % events)
        for event in events:
            if '<<TABLE SELECTED>>' in event:
                self.__btExtract['state'] = 'normal'
            if '<<TABLE UNSELECTED>>' in event:
                self.__btExtract['state'] = 'disabled'
            if '<<PACKAGE SELECTED>>' in event:
                self.__btInstall['state'] = 'normal'
            if '<<PACKAGE UNSELECTED>>' in event:
                self.__btInstall['state'] = 'disabled'
            if '<<DISABLE_ALL>>' in event:
                self.__backupState['btExtract']=self.__btExtract['state']
                self.__backupState['btInstall']=self.__btInstall['state']
                self.__btExtract['state']='disabled'
                self.__btInstall['state']='disabled'
            if '<<ENABLE_ALL>>' in event:
                self.__btExtract['state']=self.__backupState['btExtract']
                self.__btInstall['state']=self.__backupState['btInstall']
            if '<<BEGIN_ACTION>>' in event:
                self.__progressBar.start()
            if '<<END_ACTION>>' in event:
                self.__progressBar["value"] = 0
                self.__progressBar.stop()