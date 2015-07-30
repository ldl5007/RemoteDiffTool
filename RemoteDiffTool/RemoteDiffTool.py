# Remote Diff Tool program using PyQt

import sys
import os
import subprocess
import Logger

from PyQt4 import QtGui, uic

from RemoteBrowse import RemoteBrowseClass
from MyFTP import myFtpClass

logger = Logger.setup_custom_logger('root')
logger.debug('testing')

from_class = uic.loadUiType("ui\RemoteDiffTool.ui")[0]   # load the ui

class MyWindowClass(QtGui.QMainWindow, from_class):

    compareDir   = os.getcwd() + '\Temp'
    compareFile1 = 'tempFile1'
    compareFile2 = 'tempFile2'
    
    listOutput = []
    winMergeDir = os.getcwd() + '\winMerge\WinMergePortable.exe'
    
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.ftp1 = None
        self.ftp2 = None

        self.radioButton_Path1_Local.setChecked(True)
        self.radioButton_Path2_Local.setChecked(True)
   
        self.pushButton_Compare.clicked.connect(self.btn_Compare_Clicked) # Compare button is clicked
        self.pushButton_Browse1.clicked.connect(self.btn_Browse1_Clicked) # Browse 1 button is clicked
        self.pushButton_Browse2.clicked.connect(self.btn_Browse2_Clicked) # Browse 1 button is clicked

        self.radioButton_Path1_Remote.clicked.connect(self.btn_Remoted1_Clicked)
        self.radioButton_Path2_Remote.clicked.connect(self.btn_Remoted2_Clicked)

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
            os.chdir(self.compareDir)
            self.ftp1.validateRemoteFile(file1)
            if not self.ftp1.downloadFile(file1, self.compareFile1):
                self.logError("Download {} failed".format(file1))
                return

        if self.radioButton_Path2_Local.isChecked():
            self.compareFile2 = file2

        else:
            file2 = "'" + file2 + "'"
            os.chdir(self.compareDir)
            self.ftp2.validateRemoteFile(file2)
            if not self.ftp2.downloadFile(file2, self.compareFile2):
                self.logError("Download {} failed".format(file2))
                return
        
        self.logMessage('Start comparing 2 files')
        self.invokeCompare(self.compareFile1, self.compareFile2)
    
        

    def btn_Browse1_Clicked(self):
        fileName = ''
        if self.radioButton_Path1_Local.isChecked():
            fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File','')

        else:
            fileName = RemoteBrowseClass.getRemotePath(None, self.ftp1.ftpInfo)
            

        if fileName:
            index = self.comboBox_Path1.findText(fileName)
            if index == -1:
                self.comboBox_Path1.addItem(fileName)
    
            self.comboBox_Path1.setCurrentIndex(self.comboBox_Path1.findText(fileName))


    def btn_Browse2_Clicked(self):
        fileName = ''
        if self.radioButton_Path2_Local.isChecked():
            fileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File','')

        else:
            fileName = RemoteBrowseClass.getRemotePath(None, self.ftp2.ftpInfo)
            
        if fileName:
            index = self.comboBox_Path2.findText(fileName)
            if index == -1:
                index = self.comboBox_Path2.addItem(fileName)

            self.comboBox_Path2.setCurrentIndex(self.comboBox_Path2.findText(fileName))


    def btn_Remoted1_Clicked(self):
        self.ftp1 = myFtpClass(None)

    def btn_Remoted2_Clicked(self):
        self.ftp2 = myFtpClass(None)

    def logWarning(self, message):
        self.logMessage(message, "WARNING")
    
    def logError(self, message):
        self.logMessage(message, "ERROR")

    def logMessage(self, message, *msgType): 
        if ('WARNING' in msgType):
            self.textEdit_Log.setTextColor(QtGui.QColor('yellow'))
        elif ('ERROR' in msgType):
            self.textEdit_Log.setTextColor(QtGui.QColor('red'))

        self.textEdit_Log.insertPlainText(message + "\n")
        self.textEdit_Log.moveCursor(QtGui.QTextCursor.EndOfLine)
        self.textEdit_Log.setTextColor(QtGui.QColor('black'))

    def invokeCompare(self, file1, file2):
        subprocess.call([self.winMergeDir, file1, file2])





app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
