import logging
from tkinter import *

import webbrowser
from tkinter.constants import *

from tkinter import filedialog
from tkinter.ttk import *
import tkinter.scrolledtext as st

from packager.model.baseModel import BaseModel
from packager.tools.observer import Observer
from packager.tools.toolTip import *
from packager.tools.toolbox import *


# https://flylib.com/books/en/2.723.1/text.html

class SearchViewer(Frame, Observer):
    def __init__(self, window, base_model, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)
        Observer.__init__(self, base_model.search_model)
        self.__parent = window
        self.__baseModel = base_model
        self.__root = window
        self.__topLevel = None
        # self.__btDirImage = PhotoImage(file=base_model.base_dir + "images/btDir.png")
        self.__is_hide = True

    def hide(self):
        self.__topLevel.withdraw()
        self.__is_hide = True

    def show(self):
        if not self.__is_hide:
            return
        self.__is_hide = False
        self.__topLevel = Toplevel(self.__parent)
        self.__topLevel.wm_title("Search")
        self.__topLevel.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.__topLevel.iconbitmap(self.__baseModel.base_dir + "images/tablePackager_128x128.ico")

        # =================================================================
        self.__search_frame = Frame(self.__topLevel)
        self.__search_entry = Entry(self.__search_frame)
        self.__search_entry.grid(row=0, column=0, columnspan=2, padx=2, pady=2, sticky='nesw')

        self.__count_label = Label(self.__search_frame, text="0 results")
        self.__count_label.grid(row=0, column=2, sticky='W', padx=2, pady=2)

        self.__filter = IntVar()
        self.__filter.set(1)

        self.__only_vpx = Radiobutton(self.__search_frame, variable=self.__filter, text="Only VPX", value=1,
                                      command=self.on_search_domain)
        self.__only_vpx_toolTip = CreateToolTip(self.__only_vpx, 'Only existing VPX files')
        self.__all_cab = Radiobutton(self.__search_frame, variable=self.__filter, text="All Cab", value=2,
                                     command=self.on_search_domain)
        self.__all_cab_toolTip = CreateToolTip(self.__all_cab, 'Looking for all existing pinball machine')
        self.__only_vpx.grid(row=1, column=0, sticky='W', padx=2, pady=2)
        self.__all_cab.grid(row=1, column=1, sticky='W', padx=2, pady=2)
        # self.__search_entry.insert(END, self.__baseModel.visual_pinball_path)
        self.__update_bt = Button(self.__search_frame, text='update db',  # image=self.__btDirImage,
                                  command=self.on_update_db)
        self.__update_bt_toolTip = CreateToolTip(self.__update_bt, 'Search new tables on the web and update database')
        self.__update_bt.grid(row=0, column=3, sticky=E, padx=2, pady=2)
        yDefilB = Scrollbar(self.__search_frame, orient='vertical')
        yDefilB.grid(row=2, column=3, sticky='ns')

        xDefilB = Scrollbar(self.__search_frame, orient='horizontal')
        xDefilB.grid(row=3, column=0, sticky='ew')

        self.__pinball_listBox = Listbox(self.__search_frame,
                                         xscrollcommand=xDefilB.set,
                                         yscrollcommand=yDefilB.set,
                                         selectmode='single')
        self.__pinball_listBox.grid(row=2, column=0, columnspan=4, sticky='nsew')
        self.__pinball_listBox.bind('<<ListboxSelect>>', self.on_select)
        xDefilB['command'] = self.__pinball_listBox.xview
        yDefilB['command'] = self.__pinball_listBox.yview
        self.__scrolled_text = st.ScrolledText(self.__search_frame, state='disabled', height=10, width=99)
        self.scrolled_text = st.ScrolledText(self, state='disabled', height=10, width=99)
        self.__scrolled_text.grid(row=3, column=0, columnspan=4, sticky=(N, S, W, E))
        self.__scrolled_text.configure(font='TkFixedFont')

        self.__search_frame.grid(row=0, column=0, sticky=E + W)
        self.__baseModel.search_model.update()
        self.__search_entry.bind("<KeyRelease>", self.on_entry_search_key)

    def on_entry_search_key(self, key: str) -> None:
        self.__baseModel.search_model.update(self.__search_entry.get().upper())

    def on_search_domain(self) -> None:
        self.__baseModel.search_model.update(contains=self.__search_entry.get().upper(),
                                             only_with_vpx=self.__filter.get() == 1)

    def on_url_tag(self, event):
        logging.info('%s' % (event.widget.tag_names(CURRENT)[0]))
        webbrowser.open_new_tab(event.widget.tag_names(CURRENT)[0])

    def display_url(self, url: str) -> None:
        begin_pos = self.__scrolled_text.index(INSERT)
        self.__scrolled_text.insert(INSERT, url)
        end_pos = self.__scrolled_text.index(INSERT)
        self.__scrolled_text.tag_add(url, begin_pos, end_pos)  # tag url
        self.__scrolled_text.tag_config(url, foreground='blue')  # change colors in tag
        self.__scrolled_text.tag_bind(url, '<Double-Button-1>', self.on_url_tag)  # bind events in tag
        self.__scrolled_text.insert(INSERT, '\n')

    def justify_text(self, field: str, text: str, max_col=50) -> None:
        self.__scrolled_text.insert(INSERT, field)
        tab = len(field) + 1
        txt = justify_text(text, tab, max_col=90)

        if len(txt) == 0:
            self.__scrolled_text.insert(INSERT, '\n')
        else:
            is_first = True
            for line in txt:
                if is_first:
                    self.__scrolled_text.insert(INSERT, ' ' + line + '\n')
                    is_first = False
                else:
                    self.__scrolled_text.insert(INSERT, ' ' * tab + line + '\n')

    def display_info(self, pinball_machine: dict) -> None:
        """
        Print pinball machine info into scroll_text
        :param pinball_machine:
        :return:
        """
        begin_pos = self.__scrolled_text.index(INSERT)
        self.__scrolled_text.delete('1.0', END)
        self.__scrolled_text.configure(state='normal')
        # index = self.__scrolled_text.size()
        self.__scrolled_text.insert(INSERT, 'Name.........: %s\n' % pinball_machine['Table Name'])
        self.__scrolled_text.insert(INSERT, 'Theme........: %s\n' % pinball_machine['Theme'])
        self.__scrolled_text.insert(INSERT, 'Manufacturer.: %s\n' % pinball_machine['Manufacturer'])
        self.__scrolled_text.insert(INSERT, 'Year.........: %s\n' % pinball_machine['Year'])
        self.justify_text('Description..:', pinball_machine['Description(s)'])
        self.__scrolled_text.insert(INSERT, 'Ipdb.........: ')

        if pinball_machine['IPDB Number'] >= 0:
            self.display_url('https://www.ipdb.org/machine.cgi?id=%s' % pinball_machine['IPDB Number'])
        else:
            self.__scrolled_text.insert(INSERT, '\n')

        self.__scrolled_text.insert(INSERT, 'Player(s)....: %s\n' % pinball_machine['Player(s)'])
        self.__scrolled_text.insert(INSERT, 'Type.........: %s\n' % pinball_machine['Type'])
        #self.__scrolled_text.insert(INSERT, 'Update.......: %s\n' % pinball_machine['Update'])
        self.__scrolled_text.insert(INSERT, 'Fun Rating...: %s\n' % pinball_machine['Fun Rating'])
        self.justify_text('Notes........:', pinball_machine['Notes'])
        self.__scrolled_text.insert(INSERT, 'Design by....: %s\n' % pinball_machine['Design by'])
        self.__scrolled_text.insert(INSERT, 'Art by.......: %s\n' % pinball_machine['Art by'])

        for file in pinball_machine['Urls']:
            self.__scrolled_text.insert(INSERT, '--[%s]---------------------------------------------\n' % file['type'])
            self.__scrolled_text.insert(INSERT, 'Name.....: %s\n' % file['name'])
            self.justify_text('Author: ', file['Author'].replace('\n', ' / '))
            self.__scrolled_text.insert(INSERT, 'Version..: %s\n' % file['version'])
            self.__scrolled_text.insert(INSERT, 'Size.....: %s\n' % file['size'])
            #struct_time_2_datetime(str_2_struct_time('2021-04-03T23:01:06Z')).strftime('%Y-%m-%d')
            self.__scrolled_text.insert(INSERT, 'Updated..: %s\n' % struct_time_2_datetime(file['Updated']).strftime('%Y-%m-%d'))
            self.__scrolled_text.insert(INSERT, 'Url..... : ')
            self.display_url(file['url'])
        # Autoscroll to the bottom
        self.__scrolled_text.yview(END)

    def on_closing(self):
        self.hide()

    def on_update_db(self):
        self.__baseModel.search_model.update_database()

    def on_cancel(self):
        self.hide()

    def on_select(self, evt):
        selection = self.__pinball_listBox.curselection()
        if len(selection) == 0:  # no selection
            self.__baseModel.search_model.unselect_pinball_machine()
            return
        self.__baseModel.search_model.select_pinball_machine(self.__pinball_listBox.get(selection))

    def update(self, observable, *args, **kwargs):
        events = kwargs['events']
        logging.debug('SearchViewer: rec event [%s] from %s' % (events, observable))
        for event in events:
            if '<<UPDATE TABLES>>' in event:
                self.__pinball_listBox.delete(0, END)
                list = kwargs['pinball_machines']
                nb_result = kwargs['nb_result']
                total = kwargs['total']  # update listeners
                self.__count_label['text'] = '%d / %d results' % (nb_result, total)
                for index, pincab in enumerate(list):
                    self.__pinball_listBox.insert(index, pincab)
            elif '<<ENABLE_ALL>>' in event:
                pass
                # self.__btRefreshTables['state'] = 'normal'
                # self.__listTables.bind('<<ListboxSelect>>', self.on_select)
            elif '<<DISABLE_ALL>>' in event:
                pass
                # self.__btDelTable['state'] = 'disabled'
                # self.__btRefreshTables['state'] = 'disabled'
                # self.__listTables.unbind('<<ListboxSelect>>')
            elif '<<PINBALL SELECTED>>' in event:
                self.display_info(kwargs['pinball_machine'])
            elif '<<PINBALL UNSELECTED>>' in event:
                pass
