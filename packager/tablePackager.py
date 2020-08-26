import logging

from packager.view.mainWindow import *
from packager.model.baseModel import *
from packager.tools.logHandler import *

# Major.minor.fix; Minor number++ when package format/info change
version = '1.1.2'
package_version = '1.0'


# https://datastudio.google.com/reporting/13ua5g7jmoyHovP4hrqk48HBYGeQbpJ1Z/page/55yX

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        handlers=[
            # logging.FileHandler("{0}/{1}.log".format(logPath, fileName)),
            logging.StreamHandler()
        ])
    logger = logging.getLogger(__name__)

    logHandler = QueueHandler()
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

    logger.info('Started')
    base_model = BaseModel(logger, version, package_version)
    main_window = MainWindow(base_model, logHandler)
    base_model.installedTablesModel.update()
    base_model.packagedTablesModel.update()
    main_window.mainLoop()


if __name__ == '__main__':
    main()
