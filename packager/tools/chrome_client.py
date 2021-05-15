# thanks to  @righthandabacus for crawler into separate script
# https://github.com/righthandabacus/stealweb/blob/master/fakechrome.py

from __future__ import print_function
import json
import logging
import os
import sys
import threading
import time
from cefpython3 import cefpython as cef

#https://developpaper.com/sample-browser-call-from-cefpython-3-qbit/
sys.excepthook = cef.ExceptHook # shutdown CEF processes on exception
logger = logging.getLogger('fc')

class chrome_client_handlers(object):
    '''
    Handler object
    '''
    def __init__(self, chrome_client):
        self.__chrome = chrome_client

    @property
    def chrome(self):
        return self.__chrome

    def GetViewRect(self, rect_out, **kwargs):
        "RenderHandler interface. CEF will call this to read what geometry should the browser be"
        self.chrome.logger.debug('Reset view rect')
        rect_out.extend([0, 0, self.chrome.width, self.chrome.height]) # [x, y, width, height]
        return True

    def OnConsoleMessage(self, browser, message, **kwargs):
        "DisplayHandler interface. Intercept all message printted to console"
        self.chrome.console.append(message)

    def OnLoadError(self, browser, frame, error_code, failed_url, **_):
        print("OnLoadError!!!!")
        self.chrome.ready = error_code # like True
        self.chrome.logger.debug('Load Error')
        self.chrome._getReadyLock.acquire()
        self.chrome._getReadyLock.notify()
        self.chrome._getReadyLock.release()

    def OnLoadingStateChange(self, browser, is_loading, **kwargs):
        "LoadHandler interface. Browser will call when load state change"
        if not is_loading:
            # Loading is complete. DOM is ready.
            self.chrome.ready = True
            self.chrome.logger.debug('Loaded')
            self.chrome._getReadyLock.acquire()
            self.chrome._getReadyLock.notify()
            self.chrome._getReadyLock.release()
        else:
            self.chrome.logger.debug('Loading')
            self.chrome.ready = False

class chrome_client(object):
    # https://stackoverflow.com/questions/472000/usage-of-slots
    __slots__ = ('__logger', 'width','height','headless','browser','source','domArray'
                ,'windowParams','ready','_handler','__weakref__' # weakref for StringVisitor iface
                ,'console','_getSourceLock','_getDOMLock','_getReadyLock')

    def __init__(self, logger:logging, width=1920, height=1080, headless=False):
        self.__logger=logger
        self.width = width
        self.height = height
        self.headless = headless

        # pointer to reusable CEF objects
        self.console = []
        self.browser = None
        self.source = None
        self.domArray = None
        self.windowParams = None
        self.ready = True
        self._getSourceLock = threading.Condition()
        self._getDOMLock = threading.Condition()
        self._getReadyLock = threading.Condition()
        self._handler = chrome_client_handlers(self)

        settings = {
            'user_agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) ' \
                         'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                         'Chrome/64.0.3282.140 Safari/537.36',
            # "Debug": true, debug mode
            # "Log" severity: cef.logsevery "info," output level of log "
            # "Log file": "debug. Log", set log file
        }
        switches = {
            # To cancel obtaining media stream (such as audio and video data), empty string must be used to represent no! ~ ~ ~
            # "enable-media-stream": "",
            # "Proxy server": "socks5://127.0.0.1:10808", set proxy
            # "Disable GPU": "", set rendering mode CPU or GPU
        }
        if self.headless:
            settings['windowless_rendering_enabled'] = True
        cef.Initialize(settings=settings, switches=switches)

    @property
    def logger(self):
        return self.__logger

    def __getattr__(self, name):
        # all unknown attributes/methods will pass through to CEF browser
        return getattr(self.browser, name)

    def getBrowser(self):
        if self.browser:
            return self.browser
        # create browser instance
        if self.headless:
            parent_handle = 0
            winfo = cef.WindowInfo()
            winfo.SetAsOffscreen(parent_handle)
            self.browser = cef.CreateBrowserSync(window_info=winfo)
        else:
            self.browser = cef.CreateBrowserSync()
        # create bindings for DOM walker and handler for browser activities
        self.browser.SetClientHandler(self._handler) # use render handler to resize window
        self.browser.SendFocusEvent(True) # put browser in focus
        self.browser.WasResized() # need to call this at least once in headless mode
        bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=True)
        bindings.SetFunction("get_attr_callback", self._domWalkerCallback)
        self.browser.SetJavascriptBindings(bindings)
        self.logger.debug('Browser created')
        return self

    def LoadUrl(self, url, synchronous=False):
        "Load a URL, pass-through to CEF browser"
        self.ready = False # safe-guard the wait below
        self.browser.LoadUrl(url)
        self.logger.debug('Waiting for %s to load' % url)
        if synchronous:
            self._getReadyLock.acquire()
            if not self.ready:
                self._getReadyLock.wait() # sleep until browser status update, no timeout
            self._getReadyLock.release()

    def getSource(self, synchronous=False):
        'Get HTML source code of the main frame asynchronously. Handled by self.Visit() when ready'
        self.source = None
        self.browser.GetMainFrame().GetSource(self)
        self.logger.debug('Waiting for HTML source ready')
        if synchronous:
            self._getSourceLock.acquire()
            if not self.source:
                self._getSourceLock.wait() # sleep until Visit() populated self.source, no timeout
            self._getSourceLock.release()
        return self.source

    def _domWalkerCallback(self, array, windowparams=None):
        "Bound to Javascript as callback function for DOM walker"
        self.logger.debug('DOM walker called back')
        self.domArray = array
        self.windowParams = windowparams
        self._getDOMLock.acquire()
        self._getDOMLock.notify()
        self._getDOMLock.release()

    def getDOMdata(self, synchronous=False):
        self.domArray = None
        # read JS code that to be executed
        js_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),"cef_walkdom.js")
        js_code = open(js_path).read()
        # make sure the binding is there
        bindings = self.browser.GetJavascriptBindings()
        bindings.SetFunction("get_attr_callback", self._domWalkerCallback)
        bindings.Rebind()
        threading.Timer(1, self.browser.GetMainFrame().ExecuteJavascript, [js_code]).start()
        self.logger.debug('Waiting for DOM data ready')
        if synchronous:
            self._getDOMLock.acquire()
            if self.domArray is None:
                self._getDOMLock.wait() # sleep until JS code callback set self.domArray, no timeout
            self._getDOMLock.release()
        return self.domArray

    def Visit(self, value):
        "StringVisitor interface. GetSource() will call this function with browser's source HTML"
        self.source = value
        self._getSourceLock.acquire()
        self._getSourceLock.notify()
        self._getSourceLock.release()

def runme(browser):
    browser.ready = False
    browser.LoadUrl('https://www.google.com/', True)  # True = synchronous call
    print(browser.getSource(True))
    browser.CloseBrowser()


if __name__ == '__main__':
    import argparse
    import json

    logging.basicConfig(format='%(asctime)-15s %(levelname)s:%(name)s:%(message)s')

    browser = chrome_client(logger, width=640, height=480, headless=True).getBrowser()
    mainthread = threading.Thread(target=runme,args=(browser,))
    mainthread.start()


    logger.debug('Running message loop')
    cef.MessageLoop() # blocking until browser closed
    logger.debug('Message loop end!')
    mainthread.join()
    browser = None
    cef.Shutdown()