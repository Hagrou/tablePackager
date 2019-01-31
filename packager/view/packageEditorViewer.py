import logging
from pprint import pprint
from tkinter import filedialog
from tkinter import *
from tkinter.ttk import *
from packager.tools.observer import *
from packager.tools.toolbox import *

class PackageEditorViewer(Frame, Observer):
    def __init__(self,window,baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.packageEditorModel)
        self.__parent=window
        self.__baseModel=baseModel
        self.__packageEditorModel=baseModel.packageEditorModel
        self.__root=window
        self.__backupState = {'btAddFile': 'disable', 'btDelFile': 'disable','btRename':'disable'}
        self.__topLevel=None
        self.__visible = False

    @property
    def packageEditorModel(self):
        return self.__packageEditorModel

    def hide(self):
        self.__visible = False
        self.__topLevel.withdraw()

    def show(self):
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("%s package" % self.packageEditorModel.currentPackage['name'])
        self.__topLevel.protocol('WM_DELETE_WINDOW',self.on_closing)

        #=================================================================
        self.__infoFrame=Frame(self.__topLevel)
        self.__packageNameLabel=Label(self.__infoFrame, text="Package Name: ")
        self.__packageNameLabel.grid(column=0, row=0, sticky='W',padx=2, pady=2)
        self.__packageNameEntry = Entry(self.__infoFrame)
        self.__packageNameEntry.bind('<KeyRelease>', self.tableNameKeyEvent)
        self.__packageNameEntry.grid(column=1, row=0,padx=2, pady=2)
        self.__packageNameEntry.insert(END, self.packageEditorModel.currentPackage['name'])
        self.__btRename= Button(self.__infoFrame, text="Rename", command=self.renameOnClick, state='disable')
        self.__btRename.grid(column=2, row=0,padx=0, pady=2)

        self.__creationDateLabel = Label(self.__infoFrame, text="Creation date: ")
        self.__creationDateLabel.grid(column=0, row=1, sticky='W',padx=2, pady=2)

        creationDate=self.packageEditorModel.package.get_field('info/creation date')
        self.__creationDateValueLabel = Label(self.__infoFrame,
                                              text=utcTime2Str(strIsoUTCTime2DateTime(creationDate)))

        self.__creationDateValueLabel.grid(column=1, row=1, sticky='W',padx=2, pady=2)

        self.__lastModificationDateLabel = Label(self.__infoFrame, text="Last Modification: ")
        self.__lastModificationDateLabel.grid(column=2, row=1, sticky='W',padx=2, pady=2)
        lastModDate = self.packageEditorModel.package.get_field('info/lastmod')
        self.__lastModificationDateValueLabel = Label(self.__infoFrame, text=utcTime2Str(strIsoUTCTime2DateTime(lastModDate)))
        self.__lastModificationDateValueLabel.grid(column=3, row=1,padx=2, pady=2)

        self.__packageVersionLabel = Label(self.__infoFrame, text="Version: ")
        self.__packageVersionLabel.grid(column=4, row=1, sticky='W', padx=2, pady=2)
        self.__packageVersionEntry = Entry(self.__infoFrame)
        self.__packageVersionEntry.grid(column=5, row=1, padx=2, pady=2)
        self.__packageVersionEntry.insert(END, self.packageEditorModel.package.get_field('info/package version'))

        self.__tableNameLabel = Label(self.__infoFrame, text="Table Name: ")
        self.__tableNameLabel.grid(column=0, row=2, sticky='W',padx=2, pady=2)
        self.__tableNameEntry = Entry(self.__infoFrame)
        self.__tableNameEntry.grid(column=1, row=2,padx=2, pady=2)
        self.__tableNameEntry.insert(END, self.packageEditorModel.package.get_field('info/table name'))

        self.__tableDesignerLabel= Label(self.__infoFrame, text="Table Designer: ")
        self.__tableDesignerLabel.grid(column=0, row=3, sticky='W',padx=2, pady=2)
        self.__tableDesignerEntry = Entry(self.__infoFrame)
        self.__tableDesignerEntry.grid(column=1, row=3,padx=2, pady=2)
        self.__tableDesignerEntry.insert(END, self.packageEditorModel.package.get_field('info/table designer(s)'))

        self.__tableYearLabel = Label(self.__infoFrame, text="Year: ")
        self.__tableYearLabel.grid(column=2, row=3, sticky='W',padx=2, pady=2)
        self.__tableYearEntry = Entry(self.__infoFrame)
        self.__tableYearEntry.grid(column=3, row=3,padx=2, pady=2)
        self.__tableYearEntry.insert(END, self.packageEditorModel.package.get_field('info/year'))

        self.__themeLabel=Label(self.__infoFrame, text="Theme: ")
        self.__themeLabel.grid(column=0, row=4, sticky='NW',padx=2, pady=2)
        self.__themeLabelText = Text(self.__infoFrame, width=44, height=2)
        self.__themeLabelText.grid(column=1, row=4, sticky='NW',columnspan=4,padx=2, pady=2)
        self.__themeLabelText.insert(END, self.packageEditorModel.package.get_field('info/theme'))

        #=================================================================
        self.__contentFrame = Frame(self.__topLevel, width=200, height=50)


        self.__label = Label(self.__contentFrame, text="Content")
        self.__label.grid(row=1, column=0, sticky=E + W + N)
        self.__tree = Treeview(self.__contentFrame)
        self.__tree.bind('<ButtonRelease-1>', self.on_select)
        self.__tree["columns"] = ("1", "2", "3","4","5")
        self.__tree.column("#0", width=270, minwidth=270)
        self.__tree.column("1", width=70, minwidth=50)
        self.__tree.column("2", width=120)
        self.__tree.column("3", width=120, minwidth=50)
        self.__tree.column("4", width=70, minwidth=50)
        self.__tree.column("5", width=250, minwidth=250)
        self.__tree.heading("#0", text="File", anchor=W)
        self.__tree.heading("1", text="Size", anchor=W)
        self.__tree.heading("2", text="Last Modification", anchor=W)
        self.__tree.heading("3", text="Author(s)", anchor=W)
        self.__tree.heading("4", text="Version", anchor=W)
        self.__tree.heading("5", text="sha1", anchor=W)
        self.__tree.tag_configure('info', foreground='grey')
        scrollbar = Scrollbar(self.__contentFrame, orient="vertical")
        scrollbar.config(command=self.__tree.yview)
        self.__tree.config(yscrollcommand=scrollbar.set)

        self.__tree.grid(row=2, column=0, sticky=E + W)
        scrollbar.grid(row=2, column=1, sticky=N + S)
        self.__btAddFile = Button(self.__contentFrame, text="+", command=self.on_addFile, state='disable')
        self.__btAddFile.grid(row=1, column=2, sticky=N )
        self.__btDelFile = Button(self.__contentFrame, text="-", command=self.on_delFile, state='disable')
        self.__btDelFile.grid(row=2, column=2, sticky=N)



        #=====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__contentFrame.grid(row=1, column=0, sticky=E + W)
        self.__btSave = Button(self.__topLevel, text="Save", command=self.saveOnClick)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.cancelOnClick)
        self.__btSave.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)
        self.__visible = True
        self.refresh_files()

    def askokcancel(self, title, message):
        return messagebox.askokcancel(title, message, parent=self.__topLevel)

    #    def refreshTree(self): # TODO : deprecated?
    #    content=self.packageEditorModel.manifest.content

    def tableNameKeyEvent(self,event):
        if self.packageEditorModel.package.name !=  self.__packageNameEntry.get():
            self.__btRename['state'] = 'enable'
        else:
            self.__btRename['state']='disable'


    def saveOnClick(self):
        info={'info/table name': self.__tableNameEntry.get(),
              'info/table designer(s)': self.__tableDesignerEntry.get(),
              'info/year': self.__tableYearEntry.get(),
              'info/theme': self.__themeLabelText.get('1.0','end'),
              'info/package version':self.__packageVersionEntry.get(),
              }
        self.__packageEditorModel.save_package(info)

    def cancelOnClick(self):
        self.__packageEditorModel.cancel_edition()

    def renameOnClick(self):
        self.__packageEditorModel.rename_package(self.__packageNameEntry.get())

    def on_closing(self):
        self.__packageEditorModel.cancel_edition()


    def on_select(self,evt):
        item=self.__tree.item(self.__tree.focus())
        print(item)
        if  'info' in item['tags']:
            self.__btAddFile['state'] = 'disable'
            self.__btDelFile['state'] = 'disable'
        else:
            if 'file' in item['tags'] or 'category' in item['tags']:
                self.__btAddFile['state'] = 'normal'
            if 'file' in item['tags']:
                self.__btDelFile['state'] = 'normal'
            if 'product' in item['tags']:
                self.__btAddFile['state'] = 'disable'
            if 'product' in item['tags'] or 'category' in item['tags']:
                self.__btDelFile['state'] = 'disable'

    def on_addFile(self):
        item = self.__tree.item(self.__tree.focus())

        acceptedFiles = (("all files", "*.*"))
        requiredName = self.packageEditorModel.package.name
        if 'VPinMAME/cfg' in item['tags']:
            acceptedFiles=(('rom config files', '*.cfg'),("all files", "*.*"))
            requiredName = self.packageEditorModel.package.get_field('visual pinball/info/romName')
        elif 'VPinMAME/nvram' in item['tags']:
            acceptedFiles = (('nvram files', '*.nv'), ("all files", "*.*"))
            requiredName = self.packageEditorModel.package.get_field('visual pinball/info/romName')
        elif 'VPinMAME/roms' in item['tags']:
            acceptedFiles = (('roms files', '*.zip'), ("all files", "*.*"))
            requiredName = self.packageEditorModel.package.get_field('visual pinball/info/romName')
        elif 'VPinMAME/memcard' in item['tags']:
            acceptedFiles = (('memcard files', '*.prt'), ("all files", "*.*"))
            requiredName = self.packageEditorModel.package.get_field('visual pinball/info/romName')
        elif 'visual pinball/tables' in item['tags']:
            acceptedFiles = (('vpx files', '*.vpx'),('directb2s files', '*.directb2s'),("all files", "*.*"))

        if acceptedFiles==(("all files", "*.*")):
            srcFile = filedialog.askopenfilename(parent=self.__topLevel,
                                                 initialdir=self.__baseModel.package_path,
                                                 title="Select file")       # crash if filetypes contain only ("all files", "*.*") !?
        else:
            srcFile = filedialog.askopenfilename(parent=self.__topLevel,
                                                  initialdir=self.__baseModel.package_path,
                                                  title="Select file",
                                                  filetypes=acceptedFiles)

        if srcFile!='':
            self.__packageEditorModel.add_file(self.__topLevel, item['tags'][-1],srcFile,requiredName)

    def on_delFile(self):
        item = self.__tree.item(self.__tree.focus())
        self.__packageEditorModel.del_file(self.__topLevel, item['tags'][-1], item['text'])


    def refresh_files(self):
        self.__btAddFile['state'] = 'disabled'
        self.__btDelFile['state'] = 'disabled'
        content = self.__packageEditorModel.package.manifest.content
        self.__tree.delete(*self.__tree.get_children())

        for product in content:
            if product != 'info':
                productNode = self.__tree.insert("", "end", tag=['product',product], text=product, values=('', '', ''), open=True)
                for category in content[product]:
                    if category=='info':
                        infoFolder = self.__tree.insert(productNode, "end",
                                                            tag=['info','category', product + '/' + category], text=category,
                                                            values=('', '', ''), open=True)
                        for infoName in content[product][category]:
                            self.__tree.insert(infoFolder, "end", tag=['info',product+'/'+infoName], text=infoName+': '+content[product][category][infoName], values=('','',''),open=True)
                    else:
                        categoryFolder=self.__tree.insert(productNode, "end", tag=['category',product+'/'+category], text=category, values=('','',''),open=True)
                        for element in content[product][category]:
                            if element.get('file') is not None:
                                file=element['file']
                                lastMod =  file['lastmod']
                                self.__tree.insert(categoryFolder, "end", text=file['name'], tag=['file',product+'/'+category],
                                                   values=(convert_size(file['size']),  utcTime2Str(strIsoUTCTime2DateTime(lastMod)), 'author','1.0', file['sha1']))


        # => tags=['roms'] <= sous element de roms
        # => tags=['node'] && text='roms' <= noeud roms

    def update(self, observable, *args, **kwargs):
        events = kwargs['events']
        logging.debug('VisualPinballEditor: rec event [%s]' % events)
        for event in events:
            if '<<VIEW EDITOR>>' in event:
                self.show()
            elif '<<HIDE EDITOR>>' in event:
                self.hide()
            elif '<<UPDATE VIEW>>' in event:
                print("UDATE VIEW")
            elif '<<DISABLE_ALL>>' in event:
                if self.__visible:
                    self.__backupState['btAddFile'] = self.__btAddFile['state']
                    self.__btAddFile['state'] = 'disabled'
                    self.__backupState['btDelFile'] = self.__btDelFile['state']
                    self.__btDelFile['state'] = 'disabled'
            elif '<<ENABLE_ALL>>' in event:
                if self.__visible:
                    self.__btAddFile['state'] = self.__backupState['btAddFile']
                    self.__btDelFile['state'] = self.__backupState['btDelFile']
            elif '<<UPDATE_EDITOR>>':
                if self.__visible:
                    self.refresh_files()

