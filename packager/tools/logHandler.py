# https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/
import logging
import queue

class QueueHandler(logging.Handler):
    # Class to send logging records to a queue
    # It can be used from different threads

    def __init__(self):
        super().__init__()
        self.__log_queue = queue.Queue()

    def emit(self, record):
        self.__log_queue.put(record)

    def get(self):
        return self.__log_queue.get(block=False)