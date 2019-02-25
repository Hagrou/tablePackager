import logging
import tkinter as tk

from pprint import pprint
from tkinter import filedialog
from tkinter import simpledialog

import PIL.Image
import PIL.ImageTk


from packager.tools.observer import *
from packager.tools.toolbox import *
from packager.tools.toolTip import *
from packager.view.fileInfoViewer import *
from packager.view.renamefileViewer import *

class PackageEditorViewer(Frame, Observer):
    def __init__(self,window,baseModel, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, baseModel.packageEditorModel)
        self.__parent=window
        self.__baseModel=baseModel
        self.__packageEditorModel=baseModel.packageEditorModel
        self.__root=window
        self.__backupState = {'btAddFile': 'disable', 'btDelFile': 'disable','btRename':'disable','btSave':'normal', 'btCancel':'normal'}
        self.__btAddFileImage = PhotoImage(file=baseModel.baseDir+"images/btAddFile.png")
        self.__btDelFileImage = PhotoImage(file=baseModel.baseDir+"images/btDelFile.png")
        self.__btRenameFileImage = PhotoImage(file=baseModel.baseDir + "images/btRenameFile.png")
        self.__btUpFileImage = PhotoImage(file=baseModel.baseDir + "images/btUpFile.png")
        self.__btDownFileImage = PhotoImage(file=baseModel.baseDir + "images/btDownFile.png")
        self.__topLevel=None
        self.__fileInfoViewer=FileInfoViewer(self, baseModel)
        self.__fileInfoViewer.attach(self)
        self.__fileMoved = None
        self.__renameFileViewer=RenameFileViewer(self, baseModel)
        self.__renameFileViewer.attach(self)
        self.__visible = False

    @property
    def baseModel(self):
        return self.__baseModel

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
        self.__packageNameLabel.grid(column=0, row=0, sticky='W',padx=2, pady=0)
        self.__packageNameEntry = Entry(self.__infoFrame,width=50)
        self.__packageNameEntry.bind('<KeyRelease>', self.tableNameKeyEvent)
        self.__packageNameEntry.grid(column=1, sticky='W', row=0,padx=2, pady=0)
        self.__packageNameEntry.insert(END, self.packageEditorModel.currentPackage['name'])
        self.__btRename= Button(self.__infoFrame, text="Rename", command=self.renameOnClick, state='disable')
        self.__btRename.grid(column=2, row=0,padx=0, pady=0)

        self.__creationDateLabel = Label(self.__infoFrame, text="Creation date: ")
        self.__creationDateLabel.grid(column=0, row=1, sticky='NW',padx=2, pady=0)

        creationDate=self.packageEditorModel.package.get_field('info/creation date')
        self.__creationDateValueLabel = Label(self.__infoFrame,
                                              text=utcTime2Str(strIsoUTCTime2DateTime(creationDate)))

        self.__creationDateValueLabel.grid(column=1, row=1, sticky='NW',padx=2, pady=0)

        self.__lastModificationDateLabel = Label(self.__infoFrame, text="Last Modification: ")
        self.__lastModificationDateLabel.grid(column=0, row=2, sticky='NW',padx=2, pady=0)
        lastModDate = self.packageEditorModel.package.get_field('info/lastmod')
        self.__lastModificationDateValueLabel = Label(self.__infoFrame, text=utcTime2Str(strIsoUTCTime2DateTime(lastModDate)))
        self.__lastModificationDateValueLabel.grid(column=1, sticky='NW', row=2,padx=2, pady=0)

        self.__packageVersionLabel = Label(self.__infoFrame, text="Version: ")
        self.__packageVersionLabel.grid(column=0, row=3, sticky='NW', padx=2, pady=0)
        self.__packageVersionEntry = Entry(self.__infoFrame)
        self.__packageVersionEntry.grid(column=1, row=3, sticky='NW', padx=2, pady=0)
        self.__packageVersionEntry.insert(END, self.packageEditorModel.package.get_field('info/package version'))

        self.__tableNameLabel = Label(self.__infoFrame, text="Table Name: ")
        self.__tableNameLabel.grid(column=0, row=4, sticky='NW',padx=2, pady=0)
        self.__tableNameEntry = Entry(self.__infoFrame,width=50)
        self.__tableNameEntry.grid(column=1, row=4,padx=2, pady=0, sticky='NW')
        self.__tableNameEntry.insert(END, self.packageEditorModel.package.get_field('info/table name'))

        self.__tableManufacturerLabel = Label(self.__infoFrame, text="Manufacturer: ")
        self.__tableManufacturerLabel.grid(column=0, row=5, sticky='NW', padx=2, pady=0)
        self.__tableManufacturerEntry = Entry(self.__infoFrame, width=50)
        self.__tableManufacturerEntry.grid(column=1, row=5, padx=2,sticky='NW', pady=0)
        self.__tableManufacturerEntry.insert(END, self.packageEditorModel.package.get_field('info/manufacturer'))

        self.__tableYearLabel = Label(self.__infoFrame, text="Year: ")
        self.__tableYearLabel.grid(column=0, row=6, sticky='NW',padx=2, pady=0)
        self.__tableYearEntry = Entry(self.__infoFrame)
        self.__tableYearEntry.grid(column=1, row=6,sticky='NW',padx=2, pady=0)
        self.__tableYearEntry.insert(END, self.packageEditorModel.package.get_field('info/year'))

        self.__tableDesignerLabel = Label(self.__infoFrame, text="Table Designer: ")
        self.__tableDesignerLabel.grid(column=0, row=7, sticky='NW', padx=2, pady=0)
        self.__tableDesignerEntry = Entry(self.__infoFrame, width=50)
        self.__tableDesignerEntry.grid(column=1, row=7, padx=2, pady=0, sticky='NW')
        self.__tableDesignerEntry.insert(END, self.packageEditorModel.package.get_field('info/table designer(s)'))

        self.__themeLabel=Label(self.__infoFrame, text="Theme: ")
        self.__themeLabel.grid(column=0, row=8, sticky='NW',padx=2, pady=0)
        self.__themeLabelText = Text(self.__infoFrame, width=44, height=0, font=("Helvetica", 10))
        self.__themeLabelText.grid(column=1, row=8, sticky='NW',columnspan=2,padx=2, pady=0)
        self.__themeLabelText.insert(END, self.packageEditorModel.package.get_field('info/theme'))

        self.__imageCanvasViewer=Canvas(self.__infoFrame,width=300, height=300,bg="grey", borderwidth=2)
        self.__imageCanvasViewer.grid(column=3, row=0, columnspan=4, rowspan=8, sticky='NSW',padx=50, pady=10)

        #======================================
        (dataPath,name)=self.packageEditorModel.get_first_image()
        if (dataPath!=None):
            imagePreviewPath = self.__packageEditorModel.package.directory + '/' + \
                       self.__packageEditorModel.package.name + '/' + \
                       dataPath + '/' + name
        else:
            imagePreviewPath=self.baseModel.baseDir+"images/Super Orbit (Gottlieb 1983).jpg"

        pilImage = PIL.Image.open(imagePreviewPath)
        pilImage.thumbnail((300, 300), PIL.Image.ANTIALIAS)
        tkImage = PIL.ImageTk.PhotoImage(pilImage)
        self.__tkImagePreview = self.__imageCanvasViewer.create_image(150, 150, image=tkImage)

        self.__imageCanvasViewer.itemconfig(self.__tkImagePreview, image=tkImage)
        self.__imageCanvasViewer.image = tkImage

        #=================================================================
        self.__contentFrame = Frame(self.__topLevel, width=200, height=50)
        self.__label = Label(self.__contentFrame, text="Content")
        self.__label.grid(row=0, column=0, sticky=E + W + N)
        self.__tree = Treeview(self.__contentFrame)
        self.__tree.bind('<ButtonRelease-1>', self.on_select)
        self.__tree.bind('<Double-1>', self.on_doubleClick)

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
        self.__tree.heading("5", text="url", anchor=W)
        self.__tree.tag_configure('info', foreground='grey')
        scrollbar = Scrollbar(self.__contentFrame, orient="vertical")
        scrollbar.config(command=self.__tree.yview)
        self.__tree.config(yscrollcommand=scrollbar.set)

        self.__tree.grid(row=1, column=0, rowspan=6, sticky=E + W)
        scrollbar.grid(row=1, column=1, rowspan=6, sticky=N + S)

        self.__btAddFile = Button(self.__contentFrame, image=self.__btAddFileImage, command=self.on_addFile, state='disable')
        self.__btAddFileTip = CreateToolTip(self.__btAddFile, 'Add a file to package')
        self.__btAddFile.grid(row=1, column=2, sticky=N)
        self.__btDelFile = Button(self.__contentFrame, image=self.__btDelFileImage, command=self.on_delFile, state='disable')
        self.__btDelFileTip = CreateToolTip(self.__btAddFile, 'Delete a file from package')
        self.__btDelFile.grid(row=2, column=2, sticky=N)
        self.__btRenameFile = Button(self.__contentFrame, image=self.__btRenameFileImage, command=self.on_renameFile,
                                  state='disable')
        self.__btRenameFileTip = CreateToolTip(self.__btAddFile, 'Rename a file into package')
        self.__btRenameFile.grid(row=3, column=2, sticky=N)

        self.__btUpFile= Button(self.__contentFrame, image=self.__btUpFileImage, command=self.on_upFile, state='disable')
        self.__btUpFile.grid(row=4, column=2, sticky=N)
        self.__btDownFile = Button(self.__contentFrame, image=self.__btDownFileImage, command=self.on_downFile, state='disable')
        self.__btDownFile.grid(row=5, column=2, sticky=N)

        #=====================================================================
        self.__infoFrame.grid(row=0, column=0, sticky=E + W)
        self.__contentFrame.grid(row=1, column=0, sticky=E + W,padx=2, pady=10)
        self.__btSave = Button(self.__topLevel, text="Save", command=self.saveOnClick)
        self.__btCancel = Button(self.__topLevel, text="Cancel", command=self.cancelOnClick)
        self.__btSave.grid(row=2, column=0, sticky=E)
        self.__btCancel.grid(row=2, column=0, sticky=W)
        self.__visible = True

        self.refresh_files()

    def askokcancel(self, title, message):
        return messagebox.askokcancel(title, message, parent=self.__topLevel)

    def tableNameKeyEvent(self,event):
        if self.packageEditorModel.package.name !=  self.__packageNameEntry.get():
            self.__btRename['state'] = 'enable'
        else:
            self.__btRename['state']='disable'


    def saveOnClick(self):
        info={'info/table name': self.__tableNameEntry.get(),
              'info/manufacturer': self.__tableManufacturerEntry.get(),
              'info/table designer(s)': self.__tableDesignerEntry.get(),
              'info/year': self.__tableYearEntry.get(),
              'info/theme': self.__themeLabelText.get('1.0','end'),
              'info/package version':self.__packageVersionEntry.get(),
              }
        self.__packageEditorModel.save_package(info)

    def cancelOnClick(self):
        self.__packageEditorModel.cancel_edition()

    def renameOnClick(self):
        if (self.baseModel.packagedTablesModel.isExists(self.__packageNameEntry.get())):
            if not self.askokcancel("Rename Conflict",
                                    "The Package '%s' already exists. Do you want to continue (Only apply on Save) ?" % self.__packageNameEntry.get()):
                return
        self.__packageEditorModel.rename_package(self.__packageNameEntry.get())

    def on_closing(self):
        self.__packageEditorModel.cancel_edition()

    def preview(self, file, path):
        extension=Path(file).suffix.lower()
        filePath=self.__packageEditorModel.package.directory+'/'+\
                 self.__packageEditorModel.package.name+'/'+\
                 path+'/'+file

        if extension=='.jpg' or extension=='.png' or extension=='.gif':
            pilImage = PIL.Image.open(filePath)
        else:
            pilImage = PIL.Image.open('images/noPreview.png')
        pilImage.thumbnail((300, 300), PIL.Image.ANTIALIAS)
        tkImage = PIL.ImageTk.PhotoImage(pilImage)
        self.__imageCanvasViewer.itemconfig(self.__tkImagePreview, image=tkImage)
        self.__imageCanvasViewer.image = tkImage

    def on_select(self,evt):
        item=self.__tree.item(self.__tree.focus())
        if  'info' in item['tags']:
            self.__btAddFile['state'] = 'disable'
            self.__btDelFile['state'] = 'disable'
            self.__btRenameFile['state'] = 'disable'
            self.__btUpFile['state'] = 'disable'
            self.__btDownFile['state'] = 'disable'
        else:
            if 'file' in item['tags'] or 'category' in item['tags']:
                self.__btAddFile['state'] = 'normal'
            if 'file' in item['tags']:
                self.__btDelFile['state'] = 'normal'
                self.__btRenameFile['state']='normal'
                self.__btUpFile['state']='normal'
                self.__btDownFile['state']='normal'
                self.__btDownFile
                self.preview(item['text'], item['tags'][-1])

            if 'product' in item['tags']:
                self.__btAddFile['state'] = 'disable'
            if 'product' in item['tags'] or 'category' in item['tags']:
                self.__btDelFile['state'] = 'disable'
                self.__btRenameFile['state'] = 'disable'
                self.__btUpFile['state'] = 'disable'
                self.__btDownFile['state'] = 'disable'

    def on_doubleClick(self,evt):
        item = self.__tree.item(self.__tree.focus())
        if 'file' in item['tags']:
            self.__fileInfoViewer.show(self.__packageEditorModel.package,
                                       item['tags'][-1],
                                       self.__packageEditorModel.get_fileInfo(self.__topLevel, item['tags'][-1], item['text']))

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

    def on_renameFile(self):
        item = self.__tree.item(self.__tree.focus())
        if 'file' in item['tags']:
            self.__renameFileViewer.show(self.__packageEditorModel.package,
                                       item['tags'][-1],
                                       self.__packageEditorModel.get_fileInfo(self.__topLevel, item['tags'][-1],
                                                                              item['text']))

    def on_upFile(self):
        item = self.__tree.item(self.__tree.focus())
        self.__packageEditorModel.up_file(self, item['tags'][-1], item['text'])


    def on_downFile(self):
        item = self.__tree.item(self.__tree.focus())
        item = self.__tree.item(self.__tree.focus())
        self.__packageEditorModel.down_file(self, item['tags'][-1], item['text'])

    def refresh_files(self,selection_set=None):
        self.__btAddFile['state'] = 'disabled'
        self.__btDelFile['state'] = 'disabled'
        self.__btRenameFile['state']='disabled'

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
                                node_id=self.__tree.insert(categoryFolder, "end", text=file['name'], tag=['file',product+'/'+category],
                                                   values=(convert_size(file['size']),  utcTime2Str(strIsoUTCTime2DateTime(lastMod)), file['author(s)'],file['version'], file['url']))
                                if selection_set!=None:
                                    dataPath=product + '/' + category
                                    if dataPath==selection_set[0] and file['name']==selection_set[1]:
                                        self.__tree.selection_set(node_id)
                                        self.__tree.focus(node_id)


    def update(self, observable, *args, **kwargs):
        events = kwargs['events']
        logging.debug('PackageEditorViewer: rec event [%s] from %s' % (events,observable))
        for event in events:
            if '<<VIEW EDITOR>>' in event:
                self.show()
            elif '<<HIDE EDITOR>>' in event:
                self.hide()
            elif '<<DISABLE_ALL>>' in event:
                if self.__visible:
                    self.__backupState['btAddFile'] = self.__btAddFile['state']
                    self.__btAddFile['state'] = 'disabled'
                    self.__backupState['btDelFile'] = self.__btDelFile['state']
                    self.__btDelFile['state'] = 'disabled'
                    self.__backupState['btRenameFile'] = self.__btRenameFile['state']
                    self.__btRenameFile['state'] = 'disabled'
                    self.__backupState['btSave'] = self.__btSave['state']
                    self.__btSave['state'] = 'disabled'
                    self.__backupState['btCancel'] = self.__btCancel['state']
                    self.__btCancel['state'] = 'disabled'

                    self.__backupState['btUpFile'] = self.__btUpFile['state']
                    self.__btUpFile['state'] = 'disable'
                    self.__backupState['btDownFile'] = self.__btDownFile['state']
                    self.__btDownFile['state'] = 'disable'

                    self.__tree.unbind('<ButtonRelease-1>')
                    self.__tree.unbind('<Double-1>')

            elif '<<ENABLE_ALL>>' in event:
                if self.__visible:
                    self.__btAddFile['state'] = self.__backupState['btAddFile']
                    self.__btDelFile['state'] = self.__backupState['btDelFile']
                    self.__btRename['state'] = self.__backupState['btRename']
                    self.__btSave['state']    = self.__backupState['btSave']
                    self.__btCancel['state']  = self.__backupState['btCancel']
                    self.__btRenameFile['state'] = self.__backupState['btRenameFile']
                    self.__btUpFile['state']= self.__backupState['btUpFile']
                    self.__btDownFile['state']= self.__backupState['btDownFile']
                    self.__tree.bind('<ButtonRelease-1>', self.on_select)
                    self.__tree.bind('<Double-1>', self.on_doubleClick)
            elif '<<UPDATE_EDITOR>>':
                if self.__visible:
                    selection_set=None
                    if kwargs.get('selection_set'):
                        selection_set=kwargs['selection_set']
                    self.refresh_files(selection_set)

