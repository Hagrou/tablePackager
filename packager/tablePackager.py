import logging

from packager.view.mainWindow import *
from packager.model.config import *
from packager.model.baseModel import *
from packager.tools.logHandler import *

version='0.4'

#https://datastudio.google.com/reporting/13ua5g7jmoyHovP4hrqk48HBYGeQbpJ1Z/page/55yX

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            #logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(__name__)

    logHandler = QueueHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    config=Config()
    logger.info('Started')
    baseModel=BaseModel(logger, config)
    mainWindow = MainWindow(baseModel, logHandler)
    baseModel.installedTablesModel.update()
    baseModel.packagedTablesModel.update()
    mainWindow.mainLoop()

import os

if __name__ == '__main__':
    main()
