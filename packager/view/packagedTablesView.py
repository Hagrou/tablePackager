import logging

from pathlib import *
from packager.tools.toolTip import *
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

from packager.tools.observer import Observer


class PackagedTablesView(Frame, Observer):
    def __init__(self, mainWindow, window, baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.packagedTablesModel)

        self.__mainWindow = mainWindow
        self.__btEditImage = PhotoImage(file=baseModel.base_dir + "images/btEdit.png")
        self.__btAddImage = PhotoImage(file=baseModel.base_dir + "images/btAdd.png")
        self.__btDelImage = PhotoImage(file=baseModel.base_dir + "images/btDel.png")
        self.__bt_restore_Image = PhotoImage(file=baseModel.base_dir + "images/btRestorePackage.png")
        self.__bt_backup_image = PhotoImage(file=baseModel.base_dir + "images/btBackupPackage.png")
        self.__btRefreshImage = PhotoImage(file=baseModel.base_dir + "images/btRefresh.png")
        self.__packagedTablesModel = baseModel.packagedTablesModel
        self.__baseModel = baseModel
        self.__label = Label(self, text="Packaged Tables")
        self.__backupState = {}
        self.__label.pack(side=TOP)

        frameBt = Frame(self)
        self.__btEdit = Button(frameBt, image=self.__btEditImage, command=self.edit_on_click, state=DISABLED)
        self.__btEdit.pack(side=LEFT)
        self.__btEditToolTip = CreateToolTip(self.__btEdit, 'Edit a package')
        self.__btDel = Button(frameBt, image=self.__btDelImage, command=self.del_on_click, state=DISABLED)
        self.__btDelToolTip = CreateToolTip(self.__btDel, 'Delete package(s)')
        self.__btDel.pack(side=LEFT)
        self.__btNew = Button(frameBt, image=self.__btAddImage, command=self.new_on_click, state=NORMAL)
        self.__btNewToolTip = CreateToolTip(self.__btNew, 'Create empty package')
        self.__btNew.pack(side=LEFT)

        self.__btRestore = Button(frameBt, image=self.__bt_restore_Image, command=self.restore_on_click, state=NORMAL)
        self.__btRestoreToolTip = CreateToolTip(self.__btRestore, 'Restore a package')
        self.__btRestore.pack(side=LEFT)

        self.__btBackup = Button(frameBt, image=self.__bt_backup_image, command=self.backup_on_click, state=DISABLED)
        self.__btBackupToolTip = CreateToolTip(self.__btBackup, 'Backup a package')
        self.__btBackup.pack(side=LEFT)

        self.__btUpdateView = Button(frameBt, image=self.__btRefreshImage, command=self.refresh_view_on_click,
                                     state=NORMAL)
        self.__btUpdateTip = CreateToolTip(self.__btUpdateView, 'Refresh Package View')
        self.__btUpdateView.pack(side=LEFT)

        frameBt.pack(side=BOTTOM)

        self.__vScrollbar = Scrollbar(self, orient="vertical")
        self.__vScrollbar.pack(side=RIGHT, fill='y')

        self.__hScrollbar = Scrollbar(self, orient="horizontal")
        self.__hScrollbar.pack(side=BOTTOM, fill='x')

        self.__listPackages = Listbox(self, width=34, height=15, selectmode=EXTENDED,
                                      xscrollcommand=self.__hScrollbar.set, yscrollcommand=self.__vScrollbar.set,
                                      font=baseModel.config.get('font'))
        self.__listPackages.pack(expand=True, fill=Y)
        self.__listPackages.bind('<<ListboxSelect>>', self.on_select)
        self.__vScrollbar.config(command=self.__listPackages.yview)
        self.__hScrollbar.config(command=self.__listPackages.xview)
        self.__listPackages.config(xscrollcommand=self.__hScrollbar.set, yscrollcommand=self.__vScrollbar.set)

    def edit_on_click(self):
        if len(self.__packagedTablesModel.selectedPackage) == 0:
            messagebox.showerror('Package Edition', 'You must select a package to edit it')
            return
        self.__baseModel.packageEditorModel.edit_package(self.__packagedTablesModel.selectedPackage[0])

    def new_on_click(self):
        self.__baseModel.packageEditorModel.new_package()

    def del_on_click(self):
        self.__packagedTablesModel.deletePackages(self)

    def restore_on_click(self):
        accepted_files = (('package files', '*.zip'), ("all files", "*.*"))  # TODO: use package extension
        package_file = filedialog.askopenfile(parent=self,
                                              initialdir=self.__baseModel.package_path,
                                              title="Select a table package",
                                              filetypes=accepted_files)
        if package_file is None or package_file == '':
            return

        self.__packagedTablesModel.restore_package(self, package_file.name)

    def backup_on_click(self):
        backup_path = filedialog.askdirectory()
        if backup_path != '':
            self.__packagedTablesModel.backupPackages(self, backup_path)

    def refresh_view_on_click(self):
        self.__packagedTablesModel.update()

    def on_select(self, evt):
        selection = self.__listPackages.curselection()
        if len(selection) == 0:  # no selection
            self.__packagedTablesModel.unSelectPackages()
            return
        self.__packagedTablesModel.selectPackages(selection)

    def update(self, observable, *args, **kwargs):
        events = kwargs['events']
        logging.debug('PackageTablesView: rec event [%s]' % events)
        for event in events:
            if '<<UPDATE PACKAGES>>' in event:
                self.__listPackages.delete(0, END)
                index = 0
                for package in kwargs['packages']:
                    self.__listPackages.insert(index, package['name'])
                    if package['protected']:
                        self.__listPackages.itemconfig(index, {'fg': 'blue'})
                    else:
                        self.__listPackages.itemconfig(index, {'fg': 'black'})
                    index = index + 1

            elif '<<DISABLE_ALL>>' in event:
                self.__backupState['btEdit'] = self.__btEdit['state']
                self.__btEdit['state'] = 'disabled'
                self.__backupState['btNew'] = self.__btNew['state']
                self.__btNew['state'] = 'disabled'
                self.__backupState['btDel'] = self.__btDel['state']
                self.__btDel['state'] = 'disabled'
                self.__backupState['btBackup'] = self.__btUpdateView
                self.__btUpdateView['state'] = 'disabled'
                self.__backupState['btBackup'] = self.__btBackup['state']
                self.__btBackup['state'] = 'disabled'
                self.__backupState['btRestore'] = self.__btRestore['state']
                self.__btRestore['state'] = 'disabled'
                self.__listPackages.unbind('<<ListboxSelect>>')
            elif '<<ENABLE_ALL>>' in event:
                self.__btEdit['state'] = self.__backupState['btEdit']
                self.__btNew['state'] = self.__backupState['btNew']
                self.__btDel['state'] = self.__backupState['btDel']
                self.__btBackup['state'] = self.__backupState['btBackup']
                self.__btRestore['state'] = self.__backupState['btRestore']
                self.__btUpdateView['state'] = 'normal'
                self.__btRestore['state'] = 'normal'
                self.__listPackages.bind('<<ListboxSelect>>', self.on_select)
            elif '<<PACKAGE SELECTED>>' in event:
                self.__btEdit['state'] = 'normal'
                self.__btDel['state'] = 'normal'
                self.__btBackup['state'] = 'normal'
            elif '<<PACKAGE UNSELECTED>>' in event:
                self.__btEdit['state'] = 'disabled'
                self.__btDel['state'] = 'disabled'
                self.__btNew['state'] = 'normal'
                self.__btBackup['state'] = 'disabled'
