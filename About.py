# About Module

import sys
from PyQt4 import QtGui, uic

from_class = uic.loadUiType('ui/About.ui')[0]

class AboutDialog(QtGui.QDialog, from_class):
    
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/RDT.ico'))
        self.pushButton_Ok.clicked.connect(self.close)
        
    def setTitle(self, title):
        self.setWindowTitle("About {}".format(title))

    def setVersion(self, version):
        self.label_Version.setText("Version: {}".format(version))
        
    def setName(self, name):
        self.label_Name.setText(name)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = AboutDialog(None)
    dialog.exec_()