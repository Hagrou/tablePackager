import logging

from tkinter import ttk
from tkinter import *

from packager.view.installedTablesView import *
from packager.view.packagedTablesView import *
from packager.view.packageEditorViewer import *
from packager.view.logViewer import *
from packager.view.configViewer import *


class MainWindow(Observer,Observable):
    def __init__(self, baseModel, logHandler):
        Observer.__init__(self, baseModel.installedTablesModel)
        Observable.__init__(self)

        baseModel.packagedTablesModel.attach(self)
        self.__backupState={}
        self.__baseModel=baseModel
        self.__window=Tk()

        # create a toplevel menu
        self.__menubar = Menu(self.__window)
        self.__menubar.add_command(label="Options", command=self.onOptionMenu)

        self.__helpMenu = Menu(self.__menubar, tearoff=0)
        self.__helpMenu.add_command(label="Getting Start", command=self.onHelpMenu)
        self.__helpMenu.add_separator()
        self.__helpMenu.add_command(label="About", command=self.onHelpMenu)
        self.__menubar.add_cascade(label="Help", menu=self.__helpMenu)


        # display the menu
        self.__window.configure(menu=self.__menubar)
        self.__window.title("Pincab Table Packager")
        self.__separator=Separator(self.__window, orient=HORIZONTAL)

        self.__installedTablesView=InstalledTablesView(self.__window, self.__baseModel)
        self.__configViewer=ConfigViewer(self.__window, self.__baseModel)
        self.__progressBar = ttk.Progressbar(self.__window,orient ="horizontal", mode ="indeterminate")
        self.__progressBar["value"] = 0
        self.__progressBar["maximum"]=800


        self.__extractAppChoice={ 'visual_pinball':IntVar(),
                                   'futurPinball':IntVar(),
                                   'pinupSystem':IntVar(),
                                   'pinballX':IntVar()}

        self.__extractAppChoice['visual_pinball'].set(True)
        self.__extractAppChoice['futurPinball'].set(False)
        self.__extractAppChoice['pinupSystem'].set(True)
        self.__extractAppChoice['pinballX'].set(True)

        self.__extractFrame=Frame(self.__window, width=2,relief=GROOVE,borderwidth=4)
        self.__cbExVisualPinball= Checkbutton(self.__extractFrame, variable=self.__extractAppChoice['visual_pinball'], onvalue = True, offvalue = False, text='Visual Pinball')
        self.__cbExVisualPinball.grid(column=0, row=0, sticky='NW')

        self.__cbExFuturPinball = Checkbutton(self.__extractFrame, variable=self.__extractAppChoice['futurPinball'],onvalue = True, offvalue = False,text='Futur Pinball', state=DISABLED)
        self.__cbExFuturPinball.grid(column=0, row=1, sticky='NW')
        self.__cbExFuturPinballToolTip = CreateToolTip(self.__cbExFuturPinball, 'Not Yet Implemented')
        self.__cbExPinupSystem  = Checkbutton(self.__extractFrame, variable=self.__extractAppChoice['pinupSystem'],onvalue = True, offvalue = False,text='PinUp System')
        self.__cbExPinupSystem.grid(column=0, row=2, sticky='NW')
        self.__cbExPinupSystemToolTip = CreateToolTip(self.__cbExPinupSystem, 'Not Yet Implemented')
        self.__cbExPinballX     = Checkbutton(self.__extractFrame, variable=self.__extractAppChoice['pinballX'],onvalue = True, offvalue = False,text='Pinball X')

        self.__cbExPinballX.grid(column=0, row=3, sticky='NW')

        self.__btExtractImage = PhotoImage(file=baseModel.baseDir+"images/btExtract.png")
        self.__btInstallImage = PhotoImage(file=baseModel.baseDir+"images/btInstall.png")

        self.__btExtract = Button(self.__extractFrame, image=self.__btExtractImage, command=self.extractOnClick,
                                 state=DISABLED)

        self.__btExtract.grid(column=1, row=0, rowspan=4, sticky='NW')

        self.__installAppChoice = {'visual_pinball': IntVar(),
                                   'futurPinball': IntVar(),
                                   'pinupSystem': IntVar(),
                                   'pinballX': IntVar()}
        self.__installAppChoice['visual_pinball'].set(True)
        self.__installAppChoice['futurPinball'].set(False)
        self.__installAppChoice['pinupSystem'].set(True)
        self.__installAppChoice['pinballX'].set(False)

        self.__installFrame = Frame(self.__window, width=2, relief=GROOVE, borderwidth=4)
        self.__cbInsVisualPinball = Checkbutton(self.__installFrame, text='Visual Pinball', variable=self.__installAppChoice['visual_pinball'], onvalue = True, offvalue = False)
        self.__cbInsVisualPinball.grid(column=0, row=4, sticky='NW')
        self.__cbInsFuturPinball = Checkbutton(self.__installFrame, text='Futur Pinball',variable=self.__installAppChoice['futurPinball'], onvalue = True, offvalue = False, state=DISABLED)
        self.__cbInsFuturPinballToolTip = CreateToolTip(self.__cbInsFuturPinball, 'Not Yet Implemented')

        self.__cbInsFuturPinball.grid(column=0, row=5, sticky='NW')
        self.__cbInsPinupSystem = Checkbutton(self.__installFrame, text='PinUp System', variable=self.__installAppChoice['pinupSystem'], onvalue = True, offvalue = False)
        self.__cbInsPinupSystem.grid(column=0, row=6, sticky='NW')
        self.__cbInsPinballX = Checkbutton(self.__installFrame, text='Pinball X',variable=self.__installAppChoice['pinballX'], onvalue = True, offvalue = False, state=DISABLED)
        self.__cbInsPinballXToolTip = CreateToolTip(self.__cbInsPinballX, 'Not Yet Implemented')
        self.__cbInsPinballX.grid(column=0, row=7, sticky='NW')


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

        self.attach(self.__packagedTablesView)

    def mainLoop(self):
        try:
            self.__window.mainloop()
        except Exception as Err:
            print(Err)

    def onOptionMenu(self):
        print("onMenuOption")
        self.__configViewer.show()

    def onHelpMenu(self):
        print("onHelpMenu")

    def extractOnClick(self):
        self.__baseModel.installedTablesModel.extract_tables(self.__extractAppChoice)

    def installOnClick(self):
        self.__baseModel.packagedTablesModel.deployPackage(self.__installAppChoice)


    def update(self, observable, *args, **kwargs):
        events=kwargs['events']
        logging.debug('MainWindow: rec event [%s] from %s' % (events,observable))
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
                self.notify_all(self, events=['<<DISABLE_ALL>>'])
                self.__menubar.entryconfig('Options', state='disabled')
                self.__menubar.entryconfig('Help', state='disabled')
            if '<<ENABLE_ALL>>' in event:
                self.__btExtract['state']=self.__backupState['btExtract']
                self.__btInstall['state']=self.__backupState['btInstall']
                self.__menubar.entryconfig('Options', state='normal')
                self.__menubar.entryconfig('Help', state='normal')
            if '<<BEGIN_ACTION>>' in event:
                self.__progressBar.start()
            if '<<END_ACTION>>' in event:
                self.__progressBar["value"] = 0
                self.__progressBar.stop()