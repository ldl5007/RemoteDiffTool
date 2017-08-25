# Config module.

import sys
from PyQt5 import QtWidgets, QtGui, uic

from_class = uic.loadUiType('ui/Config.ui')[0]

class ConfigDialog(QtWidgets.QDialog, from_class):
    
    def __init__(self, parent = None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/RDT.ico'))
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = ConfigDialog(None)
    dialog.exec_()