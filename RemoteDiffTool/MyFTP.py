# My FTP module.  This module is responsible to communicate with the remote server

import sys
from PyQt4 import QtCore, QtGui, uic
from ftplib import FTP, error_perm

from_class = uic.loadUiType("ui\FtpInfo.ui")[0]

class ListMember(object):
    def __init__(self, fname, ftype):
        self.name = fname
        self.type = ftype

class FtpInfo(object):
    def __init__(self, system, name, password):
        self.remoteSystem = system
        self.userName     = name
        self.password     = password

class FtpResult(object):
    def __init__(self):
        self.isPds  = False
        self.currentDir = ''
        self.data = []

class FtpInfoDialog(QtGui.QDialog, from_class):

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.errMessage = ''
        self.ftpInfo = None
        self.pushButton_Ok.clicked.connect(self.btn_Ok_Clicked)
        self.pushButton_Cancel.clicked.connect(self.btn_Cancel_Clicked)

        self.lineEdit_Password.setEchoMode(QtGui.QLineEdit.Password)

    def btn_Ok_Clicked(self):
        system = self.lineEdit_System.text()
        userName = self.lineEdit_UserName.text()
        password = self.lineEdit_Password.text()

        self.ftpInfo = FtpInfo(system, userName, password)

        # validate user input info
        if myFtpClass.validateFtpInfo(self.ftpInfo):
            self.close()

    def btn_Cancel_Clicked(self):
        self.close()
        

class myFtpClass(FtpInfo):
    
    def __init__(self, ftpInfo):
        
        self.listOutput = FtpResult()
        if not ftpInfo:
            self.ftpInfo = self.getFtpInfo()
        else:
            self.ftpInfo = ftpInfo

    @staticmethod
    def getFtpInfo(parent = None):
        dialog = FtpInfoDialog(parent)
        dialog.exec_()
        
        return dialog.ftpInfo

    @staticmethod
    def validateFtpInfo(ftpInfo):
        returnStatus = False
        ftp = FTP(ftpInfo.remoteSystem)

        try:
            rc = ftp.login(user=ftpInfo.userName, passwd=ftpInfo.password)
            print(rc)

            returnStatus = True
            
        except error_perm as e:
            print('Error :' + str(e))

        ftp.quit()
        return returnStatus

    def validateRemoteFile(self, remoteFile):
        returnStatus = False;

        print('Validate ' + remoteFile);

        ftp = FTP(self.ftpInfo.remoteSystem) #For now just use CA11
        try:
            rc = ftp.login(user=self.ftpInfo.userName, passwd=self.ftpInfo.password)
            print(rc)

            rc = ftp.cwd(remoteFile)
            print(rc)

            del self.listOutput[:]
            rc = ftp.retrlines('LIST', self.listCallBack)
            print(rc)
            
            returnStatus = True;

        except error_perm as e: #you can specify type of Exception also
            print(str(e))

        rc = ftp.quit()
        print(rc)

        return returnStatus


    def listRemotePath(self, newPath):	
        ftp = FTP(self.ftpInfo.remoteSystem)
        del self.listOutput.data[:]
        
        try:
            rc = ftp.login(user=self.ftpInfo.userName, passwd=self.ftpInfo.password)
            print(rc)
            
            rc = ftp.cwd("'" + newPath + "'")
            if 'partitioned data set' in rc:
                self.listOutput.isPds = True
            else:
                self.listOutput.isPds = False
            print(rc)
            
            strArr = rc.split("\"")
            self.listOutput.currentDir = strArr[1]

            rc = ftp.retrlines('LIST', self.listCallBack)
            print('LISTRC :' + rc)
            
        except error_perm as e:
            print('Error :' + str(e))

        ftp.quit()   
        return self.listOutput


    def downloadFile(self, fileName, destName):
        returnStatus = False;

        ftp = FTP(self.ftpInfo.remoteSystem) #For now just use CA11
        try:
            rc = ftp.login(user=self.ftpInfo.userName, passwd=self.ftpInfo.password)
            print(rc)

            print('Downloading : ' + fileName)

            file = open(destName, 'w')
            del self.listOutput.data[:]
            rc = ftp.retrlines('RETR '+ fileName, self.downloadCallBack)
            print(rc)

            for msg in self.listOutput.data:
                file.write(msg + '\n')

            file.close()

            returnStatus = True;

        except error_perm as e: #you can specify type of Exception also
            print(str(e))

        rc = ftp.quit()
        print(rc)

        return returnStatus
        
    # Process the call back from list 
    def listCallBack(self, string):
        string = string.strip()
        strArr = string.split(' ')
        
        if self.listOutput.isPds:        
            newMember = ListMember(strArr[0], 'MEMBER')
            self.listOutput.data.append(newMember)    
        else:
            name = self.listOutput.currentDir + strArr[len(strArr) - 1]

            if 'Not Direct Access Device' in string:
                dsType = strArr[0]
            elif 'Error' in string:
                dsType = 'UNKNOWN'
            else:
                dsType = strArr[len(strArr) - 3]
            
            newMember = ListMember(name, dsType)
            self.listOutput.data.append(newMember)

    def downloadCallBack(self, string):
        self.listOutput.data.append(string)

      
if __name__ == '__main__':        
    app = QtGui.QApplication(sys.argv)
    myFtpClass(None)

