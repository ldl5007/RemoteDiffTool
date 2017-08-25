# Remote Diff Tool program using PyQt

import sys
import os
import subprocess
import Logger

from PyQt5 import QtWidgets, QtGui, uic

from RemoteBrowse import RemoteBrowseClass
from MyFTP import myFtpClass
from Config import ConfigDialog
from About import AboutDialog

logger = Logger.setup_custom_logger(__name__)

from_class = uic.loadUiType("ui\RemoteDiffTool.ui")[0]   # load the ui

class RemoteDiffTool(QtWidgets.QMainWindow, from_class):

    __PRODUCT_VERSION = '1.4'
    __PRODUCT_NAME    = 'Remote Diff Tool'

    compareDir   = os.getcwd() + '\Temp'
    compareFile1 = 'tempFile1'
    compareFile2 = 'tempFile2'

    winMergeDir = os.getcwd() + '\winMerge\WinMergePortable.exe'

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.ftp1 = None
        self.ftp2 = None        

        self.setWindowIcon(QtGui.QIcon('img/RDT.ico'))
        self.setWindowTitle('{}   Ver {}'.format(self.__PRODUCT_NAME, self.__PRODUCT_VERSION))

        self.radioButton_Path1_Local.setChecked(True)
        self.radioButton_Path2_Local.setChecked(True)

        self.pushButton_Compare.clicked.connect(self.btn_Compare_Clicked) # Compare button is clicked
        self.pushButton_Browse1.clicked.connect(self.btn_Browse1_Clicked) # Browse 1 button is clicked
        self.pushButton_Browse2.clicked.connect(self.btn_Browse2_Clicked) # Browse 1 button is clicked

        self.radioButton_Path1_Remote.clicked.connect(self.btn_Remoted1_Clicked)
        self.radioButton_Path2_Remote.clicked.connect(self.btn_Remoted2_Clicked)
        
        self.menuConfig.triggered.connect(self.menu_Config_clicked)
        self.menuAbout.triggered.connect(self.menu_About_Clicked)


    def btn_Compare_Clicked(self):
        file1 = self.comboBox_Path1.currentText()
        file2 = self.comboBox_Path2.currentText()

        if not file1:
            self.logError('File 1 is empty')
            return
        if not file2:
            self.logError('File 2 is empty')
            return

        self.logMessage('File 1: ' + file1)
        self.logMessage('File 2: ' + file2)

        if self.radioButton_Path1_Local.isChecked():
            self.compareFile1 = file1

        else:
            file1 = "'" + file1 + "'"

            if not (os.path.exists(self.compareDir)):
                os.makedirs(self.compareDir)

            os.chdir(self.compareDir)

            self.logMessage("Downloading {} ...".format(file1))
            if not self.ftp1.downloadFile(file1, self.compareFile1):
                self.logError("Download {} failed".format(file1))
                self.logError("Error info: {}".format(self.ftp1.errMsg))
                return
            else:
                self.logMessage("Download {} completed".format(file1))

        if self.radioButton_Path2_Local.isChecked():
            self.compareFile2 = file2

        else:
            file2 = "'" + file2 + "'"

            if not (os.path.exists(self.compareDir)):
                os.makedirs(self.compareDir)

            os.chdir(self.compareDir)

#            if self.ftp2.validateRemoteFile(file2):
            self.logMessage("Downloading {} ...".format(file2))
            if not self.ftp2.downloadFile(file2, self.compareFile2):
                self.logError("Download {} failed".format(file2))
                return
            else:
                self.logMessage("Download {} completed".format(file2))

        self.logMessage('Start comparing 2 files')
        self.invokeCompare(self.compareFile1, self.compareFile2)


    def btn_Browse1_Clicked(self):
        fileName = ''
        currentText = self.comboBox_Path1.currentText()
        logger.debug(currentText);
        
        if self.radioButton_Path1_Local.isChecked():
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', currentText)

        else:
            fileName = RemoteBrowseClass.getRemotePath(None, self.ftp1.ftpInfo, currentText)


        if fileName:
            index = self.comboBox_Path1.findText(fileName)
            if index == -1:
                self.comboBox_Path1.addItem(fileName)

            self.comboBox_Path1.setCurrentIndex(self.comboBox_Path1.findText(fileName))
            self.logMessage('Set File 1 to: {}'.format(fileName))


    def btn_Browse2_Clicked(self):
        fileName = ''
        currentText = self.comboBox_Path2.currentText()
        logger.debug(currentText)
        
        if self.radioButton_Path2_Local.isChecked():
            fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',currentText)

        else:
            fileName = RemoteBrowseClass.getRemotePath(None, self.ftp2.ftpInfo, currentText)

        if fileName:
            index = self.comboBox_Path2.findText(fileName)
            if index == -1:
                index = self.comboBox_Path2.addItem(fileName)

            self.comboBox_Path2.setCurrentIndex(self.comboBox_Path2.findText(fileName))
            self.logMessage('Set File 2 to: {}'.format(fileName))


    def btn_Remoted1_Clicked(self):
        self.ftp1 = myFtpClass(None)
        if not self.ftp1.ftpInfo:
            self.radioButton_Path1_Local.toggle()
            self.logWarning("Remote system 1 is not set")
        else:
            label = "Remote: {}".format(self.ftp1.ftpInfo.remoteSystem)
            self.radioButton_Path1_Remote.setText(label)
            self.logMessage("Remote System 1: " + self.ftp1.ftpInfo.remoteSystem)


    def btn_Remoted2_Clicked(self):
        self.ftp2 = myFtpClass(None)
        if not self.ftp2.ftpInfo:
            self.radioButton_Path2_Local.toggle()
            self.logWarning("Remote system 2 is not set")
        else:
            label = "Remote: {}".format(self.ftp2.ftpInfo.remoteSystem)
            self.radioButton_Path2_Remote.setText(label)
            self.logMessage("Remote System 1: " + self.ftp1.ftpInfo.remoteSystem)

    def menu_About_Clicked(self):
        self.logMessage("Menu about is clicked")
        aboutDlg = AboutDialog()
        aboutDlg.setTitle(self.__PRODUCT_NAME)
        aboutDlg.setVersion(self.__PRODUCT_VERSION)
        aboutDlg.setName(self.__PRODUCT_NAME)
        aboutDlg.exec_()

    def menu_Config_clicked(self):
        self.logMessage("Menu config is clicked")
        ConfigDialog().exec_()

    def logWarning(self, message):
        self.logMessage(message, "WARNING")

    def logError(self, message):
        self.logMessage(message, "ERROR")

    def logMessage(self, message, *msgType):
        if ('WARNING' in msgType):
            self.textEdit_Log.setTextColor(QtGui.QColor('blue'))
        elif ('ERROR' in msgType):
            self.textEdit_Log.setTextColor(QtGui.QColor('red'))

        self.textEdit_Log.insertPlainText(message + "\n")
        self.textEdit_Log.moveCursor(QtGui.QTextCursor.EndOfLine)
        self.textEdit_Log.setTextColor(QtGui.QColor('black'))
        logger.info(message)

    def invokeCompare(self, file1, file2):
        subprocess.call([self.winMergeDir, file1, file2])


app = QtWidgets.QApplication(sys.argv)
myWindow = RemoteDiffTool(None)
myWindow.show()
app.exec_()
