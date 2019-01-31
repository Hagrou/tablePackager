import logging
from tkinter import *
from tkinter import messagebox

from packager.tools.observer import Observer


class PackagedTablesView(Frame, Observer):
    def __init__(self, mainWindow, window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.packagedTablesModel)

        self.__mainWindow=mainWindow
        self.__packagedTablesModel = baseModel.packagedTablesModel
        self.__baseModel= baseModel
        self.__label = Label(self, text="Packaged Tables")
        self.__backupState={}
        self.__label.pack(side=TOP)

        frameBt=Frame(self)
        self.__btEdit = Button(frameBt, text="Edit", command=self.editOnClick, state=DISABLED)
        self.__btEdit.pack(side=LEFT)
        self.__btDel = Button(frameBt, text="Del", command=self.delOnClick, state=DISABLED)
        self.__btDel.pack(side=LEFT)
        self.__btNew = Button(frameBt, text="New", command=self.newOnClick, state=NORMAL)
        self.__btNew.pack(side=LEFT)

        frameBt.pack(side=BOTTOM)

        scrollbar = Scrollbar(self, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.__listPackages = Listbox(self, width=20, selectmode=EXTENDED, yscrollcommand=scrollbar.set, font=("Helvetica", 10))
        self.__listPackages.pack(expand=True, fill=Y)
        self.__listPackages.bind('<<ListboxSelect>>', self.on_select)
        scrollbar.config(command=self.__listPackages.yview)
        self.__listPackages.config(yscrollcommand=scrollbar.set)

    def editOnClick(self):
        if len(self.__packagedTablesModel.selectedPackage)==0:
            messagebox.showerror('Package Edition', 'You must select a package to edit it')
            return
        self.__baseModel.packageEditorModel.edit_package(self.__packagedTablesModel.selectedPackage[0])

    def newOnClick(self):
        self.__baseModel.packageEditorModel.new_package()

    def delOnClick(self):
        self.__packagedTablesModel.deletePackages(self)

    def on_select(self,evt):
        selection=self.__listPackages.curselection()
        if len(selection)==0:  # no selection
            self.__packagedTablesModel.unSelectPackages()
            return
        self.__packagedTablesModel.selectPackages(selection)

    def update(self, observable, *args, **kwargs):
        events=kwargs['events']
        logging.debug('PackageTablesView: rec event [%s]' % events)
        for event in events:
            if '<<UPDATE PACKAGES>>' in event:
                self.__listPackages.delete(0, END)
                for package in kwargs['packages']:
                    self.__listPackages.insert(END, package['name'])
            elif '<<DISABLE_ALL>>' in event:
                self.__backupState['btEdit']=self.__btEdit['state']
                self.__btEdit['state']='disabled'
                self.__backupState['btNew'] = self.__btNew['state']
                self.__btNew['state'] = 'disabled'
                self.__backupState['btDel'] = self.__btDel['state']
                self.__btDel['state'] = 'disabled'
            elif '<<ENABLE_ALL>>' in event:
                self.__btEdit['state']=self.__backupState['btEdit']
                self.__btNew['state'] = self.__backupState['btNew']
                self.__btDel['state'] = self.__backupState['btDel']
            elif '<<PACKAGE SELECTED>>' in event:
                self.__btEdit['state'] = 'normal'
                self.__btDel['state'] = 'normal'
            elif '<<PACKAGE UNSELECTED>>' in event:
                self.__btEdit['state'] = 'disabled'
                self.__btDel['state'] = 'disabled'
                self.__btNew['state'] = 'normal'