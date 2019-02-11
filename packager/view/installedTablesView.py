import logging
from tkinter import *

from packager.tools.observer import Observer
from packager.tools.toolTip import *

class InstalledTablesView(Frame, Observer):
    def __init__(self, window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.installedTablesModel)

        self.__baseModel=baseModel
        self.__backupState = {}
        self.__btDelTableImage = PhotoImage(file=self.__baseModel.baseDir+"images/btDelTable.png")
        self.__installedTablesModel=self.__baseModel.installedTablesModel
        self.__label = Label(self, text="Installed Tables")
        self.__label.pack(side=TOP)

        frameBt = Frame(self)

        self.__btDelTable = Button(frameBt, image=self.__btDelTableImage, command=self.on_deleteTable, state=DISABLED)
        self.__btDelTableTip = CreateToolTip(self.__btDelTable, 'Delete installed table or package')
        self.__btDelTable.pack(side=LEFT)
        frameBt.pack(side=BOTTOM)

        scrollbar = Scrollbar(self, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.__listTables = Listbox(self, width=30, height=15, selectmode=EXTENDED, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        self.__listTables.pack(expand=True, fill=Y)
        self.__listTables.bind('<<ListboxSelect>>', self.on_select)
        scrollbar.config(command=self.__listTables.yview)
        self.__listTables.config(yscrollcommand=scrollbar.set)

    def on_select(self,evt):
        selection=self.__listTables.curselection()
        if len(selection)==0:  # no selection
            self.__installedTablesModel.unSelectTable()
            self.__btDelTable['state'] = 'disabled'
            return
        self.__installedTablesModel.selectTable(selection)
        self.__btDelTable['state'] = 'normal'

    def on_deleteTable(self):
        self.__installedTablesModel.delete_Tables(self)

    def update(self, observable, *args, **kwargs):
        events=kwargs['events']
        logging.debug('InstalledTablesView: rec event [%s] from %s' % (events,observable))
        for event in events:
            if '<<UPDATE TABLES>>' in event:
                self.__listTables.delete(0, END)
                for table in kwargs['tables']:
                    self.__listTables.insert(END, table['name'])
            elif '<<DISABLE_ALL>>' in event:
                self.__backupState['__btDelTable']=self.__btDelTable['state']
                self.__btDelTable['state']='disabled'
            elif '<<ENABLE_ALL>>' in event:
                self.__btDelTable['state']=self.__backupState['__btDelTable']
