import threading
import logging
from packager.tools.chrome_client import chrome_client
import time
import sys

from cefpython3 import cefpython as cef


logger = logging.getLogger('fc')


# https://realpython.com/intro-to-python-threading/#starting-a-thread
class Pipeline:
    """
    Class to allow a single element pipeline between producer and consumer.
    """

    def __init__(self):
        self.message = ''
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_url(self):
        self.consumer_lock.acquire()
        message = self.message
        self.producer_lock.release()
        return message

    def put_url(self, message):
        self.producer_lock.acquire()
        self.message = message
        self.consumer_lock.release()


class BrowserService(object):
    def __init__(self):
        self.__is_alive = True
        self.__pipeline = Pipeline()
        self.__page_event = threading.Event()
        self.__consummer_thread = threading.Thread(target=self.consumer)
        self.__browser_thread = threading.Thread(target=self.engine)
        self.__browser = None
        self.__page = ''

    def start(self):
        self.__is_alive = True
        self.__browser_thread.start()
        time.sleep(1)
        self.__consummer_thread.start()

    def stop(self):
        print('Stopping Browser service')
        self.__is_alive = False
        self.__pipeline.put_url(None)
        logger.debug('Message loop end!')
        self.__consummer_thread.join()

    def load_url(self, url: str) -> None:
        self.__pipeline.put_url(url)

    def engine(self):
        self.__browser = chrome_client(logger, width=640, height=480, headless=False).getBrowser()
        cef.MessageLoop()  # blocking until browser closed
        self.__browser = None
        cef.Shutdown()

    def consumer(self):
        print('Starting Browser Service')
        while self.__is_alive:
            url = self.__pipeline.get_url()
            if url is not None:
                print("Load %s" % url)
                self.__browser.ready = False
                self.__browser.LoadUrl(url, True)  # True = synchronous call
                self.__page = self.__browser.getSource(True)
                self.__page_event.set()
        self.__browser.CloseBrowser()

    def get_page(self):
        if not self.__page_event.is_set():
            self.__page_event.wait()
        return self.__page


if __name__ == '__main__':
    browser_service = BrowserService()
    browser_service.start()

    browser_service.load_url('https://192.168.1.10')
    print('page=%s' % browser_service.get_page())

    browser_service.load_url('https://www.google.com')
    print('page=%s' % browser_service.get_page())
    browser_service.load_url('https://realpython.com')
    print('page=%s' % browser_service.get_page())
    print('Stopping...')
    browser_service.stop()
