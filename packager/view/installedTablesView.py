from tkinter import *

from packager.tools.observer import Observer

class InstalledTablesView(Frame, Observer):
    def __init__(self, window, installedTablesModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, installedTablesModel)

        self.__installedTablesModel=installedTablesModel
        self.__label = Label(self, text="Installed Tables")
        self.__label.pack(side=TOP)
        scrollbar = Scrollbar(self, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.__listTables = Listbox(self, width=20, selectmode=EXTENDED, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        self.__listTables.pack(expand=True, fill=Y)
        self.__listTables.bind('<<ListboxSelect>>', self.on_select)
        scrollbar.config(command=self.__listTables.yview)
        self.__listTables.config(yscrollcommand=scrollbar.set)

    def update(self, observable, *args, **kwargs):
        events=kwargs['events']
        for event in events:
            if '<<UPDATE TABLES>>' in event:
                self.__listTables.delete(0, END)
                for table in kwargs['tables']:
                    self.__listTables.insert(END, table['name'])


    def on_select(self,evt):
        selection=self.__listTables.curselection()
        if len(selection)==0:  # no selection
            self.__installedTablesModel.unSelectTable()
            return
        self.__installedTablesModel.selectTable(selection)

