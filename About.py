# About Module

import sys
from PyQt5 import QtWidgets, QtGui, uic

from_class = uic.loadUiType('ui/About.ui')[0]

class AboutDialog(QtWidgets.QDialog, from_class):
    
    def __init__(self, parent = None):
        QtWidgets.QDialog.__init__(self, parent)
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
    app = QtWidgets.QApplication(sys.argv)
    dialog = AboutDialog(None)
    dialog.exec_()