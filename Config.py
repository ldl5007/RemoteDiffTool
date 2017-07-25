# Config module.

import sys
from PyQt4 import QtGui, uic

from_class = uic.loadUiType('ui/Config.ui')[0]

class ConfigDialog(QtGui.QDialog, from_class):
    
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/RDT.ico'))
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = ConfigDialog(None)
    dialog.exec_()