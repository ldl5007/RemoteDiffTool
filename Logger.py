# Logger is a singleton class

import logging
import os
from PyQt5 import QtWidgets

def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    # Check if the log folder is not create then create a new one
    if not os.path.exists('log'):
        os.makedirs('log')

    fldHandler = logging.FileHandler('log\log.txt')
    fldHandler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(fldHandler)

#    customHandler = myHandler()
#    logger.addHandler(customHandler)
    return logger

class myHandler(logging.Handler):

    def close(self):
        pass

    def emit(self, record):
        pass
    #    print("Emit" + record.getMessage());


def MessageBox(message):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setText(message)
    msgBox.exec()
