# Remote Browser Dialog using PyQt
#_member is protected
#__member is private

import sys
import Logger
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4.QtGui  import QStandardItem, QAbstractItemView
from MyFTP import myFtpClass, FtpResult
from Logger import MessageBox

logger = Logger.setup_custom_logger(__name__)

from_class = uic.loadUiType("ui\RemoteBrowse.ui")[0]   #load the ui

class TreeRow(object):
    def __init__(self, nameCol, typeCol):
        self.nameCol = nameCol
        self.typeCol = typeCol

class RemoteBrowseClass(QtGui.QDialog, from_class):
    selectedString = ''

    __NAME_COLUMN = 0
    __TYPE_COLUMN = 1
    
    __ACCEPTING_TYPES = ['MEMBER', 'PS', 'FILE']

    def __init__(self, parent = None, ftpInfo = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        self.itemDict = {}
        self.ftpClass = myFtpClass(ftpInfo)

        comboBox = self.comboBox_Path
        comboBox.connect(comboBox,SIGNAL("currentIndexChanged(int)"),
					self, SLOT("onIndexChange(int)"))

        self.pushButton_Ok.clicked.connect(self.btn_Ok_Clicked)
        self.pushButton_Cancel.clicked.connect(self.btn_Cancel_Clicked)

        systemLabel = 'Remote System: {}      Type: {}'.format(self.ftpClass.ftpInfo.remoteSystem, 
                                                               self.ftpClass.ftpInfo.systemType)
        self.label_System.setText(systemLabel)

        view = self.treeView_Browse
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name','Type'])
        view.setModel(self.model)
        view.setColumnWidth(0,400);
        view.setColumnWidth(1,20);
        view.setUniformRowHeights(True)
        view.setSortingEnabled(True)
        view.sortByColumn(0, QtCore.Qt.AscendingOrder)

        self.treeView_Browse.expanded.connect(self.treeView_Expanded)

    @staticmethod
    def getRemotePath(parent = None, ftpInfo = None):
        
        dialog = RemoteBrowseClass(parent, ftpInfo)
        dialog.exec_()

        return dialog.selectedString

    @pyqtSlot(int)
    def onIndexChange(self, i):
        comboBox = self.comboBox_Path

        newPath = comboBox.currentText()
        logger.info(newPath)

        listOutput = self.ftpClass.listRemotePath(newPath)
        self.updateTreeView(listOutput)

    def treeView_Expanded(self, index):
        item = index.model().itemFromIndex(index)
        if item.hasChildren():
            child = item.child(0, self.__TYPE_COLUMN)
            if (child.text() == 'TEMP'):
                item.removeRow(0)
                newList = self.ftpClass.listRemotePath(item.accessibleText())
                self.updateTreeView(newList)

    def setDefaultPath(self, newPath):
        index = self.comboBox_Path.findText(newPath)
        if index == -1:
            self.comboBox_Path.addItem(newPath)
            
        self.comboBox_Path.setCurrentIndex(self.comboBox_Path.findText(newPath))


    def updateTreeView(self, newList):
        scrollItem = None
        isExpand   = False
        parentItem = None
        
        if (newList.dsType == FtpResult.PDS):
            # Handle directory level
            path = newList.currentDir
            if path not in self.itemDict:
                newItem = QStandardItem(newList.currentDir)
                newType = QStandardItem('PO')
                newItem.setAccessibleText(path)
                                
                self.itemDict[path] = newItem
                parentItem = newItem
                self.model.appendRow([newItem, newType])
            else:
                parentItem = self.itemDict[path]
            
            # Handle member level
            for member in newList.data:
                memberPath = '{}({})'.format(path, member.name)
                
                if memberPath not in self.itemDict:
                    newItem = QStandardItem(member.name)
                    newType = QStandardItem(member.type)
                    newItem.setAccessibleText(memberPath)
                    
                    self.itemDict[memberPath] = newItem
                    parentItem.appendRow([newItem, newType])

            scrollItem = parentItem
            isExpand   = True
            
        elif (newList.dsType == FtpResult.PS):
            # for each member check to see if they already existed in the tree                
            for member in newList.data:
                memberPath = member.name
                
                if memberPath not in self.itemDict:
                    newItem = QStandardItem(memberPath)
                    newType = QStandardItem(member.type)
                    newItem.setAccessibleText(memberPath)
                    
                    if (member.type == 'PO'):
                        self.addDummyChild(newItem)
                
                    self.itemDict[memberPath] = newItem
                    self.model.appendRow([newItem, newType])
            
                else:
                    newItem = self.itemDict[memberPath]
                
                if not scrollItem:
                    scrollItem = newItem
            
        elif (newList.dsType == FtpResult.USS):
            path = ''
            
            dirArr = newList.currentDir.split('/')
            dirArr.pop(0)
            
            for dirMember in dirArr:
                path = path + '/' + dirMember
                
                #build the directory path
                if path not in self.itemDict:
                    newItem = QStandardItem(dirMember)
                    newType = QStandardItem('DIR')
                    newItem.setAccessibleText(path)
                    
                    if not parentItem:
                        self.model.appendRow([newItem, newType])
                    else:
                        parentItem.appendRow([newItem, newType])
                
                    self.itemDict[path] = newItem
                    parentItem = newItem
                
                else:
                    parentItem = self.itemDict[path]
                
            scrollItem = parentItem
            isExpand = True
                
            for member in newList.data:
                memberPath = path + '/' + member.name
                
                if memberPath not in self.itemDict:
                    newItem = QStandardItem(member.name)
                    newType = QStandardItem(member.type)
                    newItem.setAccessibleText(memberPath)
                    
                    if (member.type == 'DIR'):
                        self.addDummyChild(newItem)
                    
                    if not parentItem:
                        self.model.appendRow([newItem, newType])
                    else:
                        parentItem.appendRow([newItem, newType])
                        
                    self.itemDict[memberPath] = newItem
                                
                        
        self.treeView_Browse.sortByColumn(self.__NAME_COLUMN)
        scrollIndex = self.model.indexFromItem(scrollItem)
        self.treeView_Browse.reset()

        self.treeView_Browse.scrollTo(scrollIndex, QAbstractItemView.PositionAtTop)
        if isExpand:
            self.treeView_Browse.expand(scrollIndex)        
        
        

    def btn_Ok_Clicked(self):
        selectedIndexList = self.treeView_Browse.selectedIndexes()

        if selectedIndexList:
            selectedItem = self.model.itemFromIndex(selectedIndexList[self.__NAME_COLUMN])
            selectedType = self.model.itemFromIndex(selectedIndexList[self.__TYPE_COLUMN])

            if selectedType.text() in self.__ACCEPTING_TYPES:
                   
                self.selectedString = selectedItem.accessibleText()
                self.close()        
            
            else:
                MessageBox("{} is not downloadable file".format(selectedItem.text()))
                
        else:
            pass    
        
    def btn_Cancel_Clicked(self):
        self.selectedString = ''
        self.close()

    def addDummyChild(self, parent):
        newItem = QStandardItem('DUMMY')
        newType = QStandardItem('TEMP')
        parent.appendRow([newItem, newType])


if __name__ == '__main__':        
    app = QtGui.QApplication(sys.argv)
    RemoteBrowseClass.getRemotePath(None)
