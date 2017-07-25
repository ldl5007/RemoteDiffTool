# My FTP module.  This module is responsible to communicate with the remote server

import sys
import Logger
from PyQt4 import QtGui, uic
from ftplib import FTP, all_errors
from Logger import MessageBox

logger = Logger.setup_custom_logger(__name__)
from_class = uic.loadUiType("ui\FtpInfo.ui")[0]

class ListMember(object):
    def __init__(self, fname, ftype):
        self.name = fname
        self.type = ftype

class FtpInfo(object):
    ZVM = 'zVM'
    ZOS = 'zOS'
    USS = 'USS'

    def __init__(self, system, name, password):
        self.remoteSystem = system
        self.userName     = name
        self.password     = password
        self.systemType   = None

class FtpResult(object):
    PDS = 'PDS'
    PS  = 'PS'
    USS = 'USS'

    def __init__(self):
        self.dsType = None
        self.isPds  = False
        self.currentDir = ''
        self.data = []

class FtpInfoDialog(QtGui.QDialog, from_class):

    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('img/RDT.ico'))

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
        else:
            del self.ftpInfo
            self.lineEdit_UserName.setText('')
            self.lineEdit_Password.setText('')
            self.ftpInfo = None


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

        logger.info('validateFtpInfo: {}'.format(ftpInfo.remoteSystem))
        try:
            ftp = FTP(ftpInfo.remoteSystem)
            ftp.login(user=ftpInfo.userName, passwd=ftpInfo.password)

            rc = ftp.getwelcome()
            logger.info(rc)

            if   ('IBM VM' in rc):
                ftpInfo.systemType = FtpInfo.ZVM
            elif ('IBM FTP' in rc):
                ftpInfo.systemType = FtpInfo.ZOS
            else:
                ftpInfo.systemType = FtpInfo.USS

            ftp.quit()

            returnStatus = True

        except all_errors as e:
            MessageBox(str(e))
            logger.error('Error :' + str(e))

        return returnStatus

    def listRemotePath(self, newPath):
        del self.listOutput.data[:]

        logger.info('listRemotePath: {}'.format(newPath))
        try:
            ftp = FTP(self.ftpInfo.remoteSystem)
            ftp.login(user=self.ftpInfo.userName, passwd=self.ftpInfo.password)

            rc = ftp.cwd("'" + newPath + "'")
            logger.info(rc)

            if 'partitioned data set' in rc:
                self.listOutput.isPds = True
                self.listOutput.dsType = FtpResult.PDS

                strArr = rc.split("\"")
                self.listOutput.currentDir = strArr[1]
            elif 'name prefix' in rc:
                self.listOutput.isPds = False
                self.listOutput.dsType = FtpResult.PS

                strArr = rc.split("\"")
                self.listOutput.currentDir = strArr[1]
            else:
                self.listOutput.dsType = FtpResult.USS

                strArr = rc.split(' ')
                self.listOutput.currentDir = strArr[3]

            ftp.retrlines('LIST', self.listCallBack)

            ftp.quit()

        except all_errors as e:
            MessageBox(str(e))
            logger.error('Error :' + str(e))

        return self.listOutput

    def downloadFile(self, fileName, destName):
        returnStatus = False;

        logger.info('downloadFile: {} to {}'.format(fileName, destName))
        try:
            ftp = FTP(self.ftpInfo.remoteSystem) #For now just use CA11

            ftp.login(user=self.ftpInfo.userName, passwd=self.ftpInfo.password)
            file = open(destName, 'w')

            del self.listOutput.data[:]
            ftp.retrlines('RETR '+ fileName, self.downloadCallBack)

            logger.info('write data to file')
            for msg in self.listOutput.data:
                file.write(msg + '\n')

            file.close()

            ftp.quit()

            returnStatus = True;

        except all_errors as e: #you can specify type of Exception also
            MessageBox(str(e))
            logger.error(str(e))

        return returnStatus

    # Process the call back from list
    def listCallBack(self, string):
        newMember = self.parseListMsg(string)
        if newMember:
            self.listOutput.data.append(newMember)

    def downloadCallBack(self, string):
        self.listOutput.data.append(string)


    def parseListMsg(self, string):
        newMember = None
        if (self.ftpInfo.systemType == FtpInfo.ZOS):
            string = string.strip()
            strArr = string.split(' ')

            if (self.listOutput.dsType == FtpResult.PDS):
                if 'Name' not in string:
                    newMember = ListMember(strArr[0], 'MEMBER')

            elif (self.listOutput.dsType == FtpResult.PS):
                name = self.listOutput.currentDir + strArr[len(strArr) - 1]

                if 'Dsname' not in name:
                    if 'Not Direct Access Device' in string:
                        dsType = strArr[0]
                    elif 'Error' in string:
                        dsType = 'UNKNOWN'
                    else:
                        dsType = strArr[len(strArr) - 3]

                    newMember = ListMember(name, dsType)

            elif (self.listOutput.dsType == FtpResult.USS):
                if not (strArr[0] == 'total'):
                    name = strArr[len(strArr) - 1]

                    if 'd' in strArr[0]:
                        dsType = 'DIR'
                    else:
                        dsType = 'FILE'

                    newMember = ListMember(name, dsType)

        elif (self.ftpInfo.systemType == FtpInfo.ZVM):
            string = string.strip()
            strArr = string.split(' ')

            print(strArr)

        return newMember


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myFtpClass(None)

