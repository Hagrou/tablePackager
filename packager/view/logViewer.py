from tkinter import *
import tkinter.scrolledtext as st
import queue


class LogViewer(Frame):
    def __init__(self, window, logHandler, **kwargs):
        Frame.__init__(self, window, width=200, height=100, **kwargs)

        self.__logHandler=logHandler
        # Create a ScrolledText wdiget
        self.scrolled_text = st.ScrolledText(self, state='disabled', height=10, width  = 99)
        self.scrolled_text.grid(row=0, column=0, sticky=(N, S, W, E))
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='gray')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)

        # Start polling messages from the queue
        self.after(100, self.poll_log_queue)

    @property
    def baseModel(self):
        return self.__baseModel

    def display(self, record):
        msg = self.__logHandler.format(record)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        while True:
            try:
                record = self.__logHandler.get()
            except queue.Empty:
                break
            else:
                self.display(record)
        self.after(100, self.poll_log_queue)