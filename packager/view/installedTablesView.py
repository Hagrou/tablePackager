import logging
from tkinter import *

from packager.tools.observer import Observer
from packager.tools.toolTip import *


class InstalledTablesView(Frame, Observer):
    def __init__(self, window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.installedTablesModel)

        self.__baseModel = baseModel
        self.__btDelTableImage = PhotoImage(file=self.__baseModel.base_dir + "images/btDelTable.png")
        self.__btRefreshTableImage = PhotoImage(file=self.__baseModel.base_dir + "images/btRefreshTable.png")
        self.__installedTablesModel = self.__baseModel.installedTablesModel
        self.__label = Label(self, text="Installed Tables")
        self.__label.pack(side=TOP)

        frameBt = Frame(self)

        self.__btDelTable = Button(frameBt, image=self.__btDelTableImage, command=self.on_deleteTable, state=DISABLED)
        self.__btDelTableTip = CreateToolTip(self.__btDelTable, 'Delete installed table or package')
        self.__btDelTable.pack(side=LEFT)

        self.__btRefreshTables = Button(frameBt, image=self.__btRefreshTableImage, command=self.on_refreshTable,
                                        state=NORMAL)
        self.__btRefreshTip = CreateToolTip(self.__btRefreshTables, 'Refresh Installed Table')
        self.__btRefreshTables.pack(side=RIGHT)
        frameBt.pack(side=BOTTOM)

        self.__vScrollbar = Scrollbar(self, orient="vertical")
        self.__vScrollbar.pack(side=RIGHT, fill='y')

        self.__hScrollbar = Scrollbar(self, orient="horizontal")
        self.__hScrollbar.pack(side=BOTTOM, fill='x')

        self.__listTables = Listbox(self, width=34, height=15, selectmode=EXTENDED,
                                    xscrollcommand=self.__hScrollbar.set, yscrollcommand=self.__vScrollbar.set,
                                    font=baseModel.config.get('font'))
        self.__listTables.pack(expand=True, fill=Y)
        self.__listTables.bind('<<ListboxSelect>>', self.on_select)
        self.__vScrollbar.config(command=self.__listTables.yview)
        self.__hScrollbar.config(command=self.__listTables.xview)
        self.__listTables.config(yscrollcommand=self.__vScrollbar.set, xscrollcommand=self.__hScrollbar.set)

    def on_select(self, evt):
        selection = self.__listTables.curselection()
        if len(selection) == 0:  # no selection
            self.__installedTablesModel.unSelectTable()
            self.__btDelTable['state'] = 'disabled'
            return
        self.__installedTablesModel.selectTable(selection)
        self.__btDelTable['state'] = 'normal'

    def on_deleteTable(self):
        self.__installedTablesModel.delete_tables(self)

    def on_refreshTable(self):
        self.__installedTablesModel.update()

    def update(self, observable, *args, **kwargs):
        events = kwargs['events']
        logging.debug('InstalledTablesView: rec event [%s] from %s' % (events, observable))
        for event in events:
            if '<<UPDATE TABLES>>' in event:
                self.__listTables.delete(0, END)
                for table in kwargs['tables']:
                    self.__listTables.insert(END, table['name'])
            elif '<<ENABLE_ALL>>' in event:
                self.__btRefreshTables['state'] = 'normal'
                self.__listTables.bind('<<ListboxSelect>>', self.on_select)
            elif '<<DISABLE_ALL>>' in event:
                self.__btDelTable['state'] = 'disabled'
                self.__btRefreshTables['state'] = 'disabled'
                self.__listTables.unbind('<<ListboxSelect>>')
