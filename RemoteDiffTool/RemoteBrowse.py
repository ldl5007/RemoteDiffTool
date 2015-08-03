# Remote Browser Dialog using PyQt

import sys
import Logger
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4.QtGui  import QStandardItem, QAbstractItemView
from MyFTP import myFtpClass, ListMember

logger = Logger.setup_custom_logger('root')

from_class = uic.loadUiType("ui\RemoteBrowse.ui")[0]   #load the ui

class RemoteBrowseClass(QtGui.QDialog, from_class):
    selectedString = ''

    def __init__(self, parent = None, ftpInfo = None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)


        self.ftpClass = myFtpClass(ftpInfo)

        comboBox = self.comboBox_Path
        comboBox.connect(comboBox,SIGNAL("currentIndexChanged(int)"),
					self, SLOT("onIndexChange(int)"))

        self.pushButton_Ok.clicked.connect(self.btn_Ok_Clicked)
        self.pushButton_Cancel.clicked.connect(self.btn_Cancel_Clicked)

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
        parent = index.model().itemFromIndex(index)
        child = parent.child(0)
        if child.text() == 'DUMMY':
            newList = self.ftpClass.listRemotePath(parent.text())
            self.updateTreeView(newList)

    def setDefaultPath(self, newPath):
        index = self.comboBox_Path.findText(newPath)
        if index == -1:
            self.comboBox_Path.addItem(newPath)
            
        self.comboBox_Path.setCurrentIndex(self.comboBox_Path.findText(newPath))


    def updateTreeView(self, newList):
        # Remove the 1 item from the list
        if newList.data:
            newList.data.pop(0)   

        if newList.isPds:
            # Check and remove dublicate member
            matchList = self.model.findItems(newList.currentDir)
            if matchList:
                self.model.removeRow(matchList[0].index().row())

            # Create new member
            newParent = QStandardItem(newList.currentDir)
            newParentType = QStandardItem('PO')
            
            for member in newList.data:
                newChildName = QStandardItem(member.name)
                newChildType = QStandardItem(member.type)
                    
                newParent.appendRow([newChildName, newChildType])

            # Add new member
            self.model.appendRow([newParent, newParentType])

            self.treeView_Browse.sortByColumn(0)
            scrollIndex = self.model.indexFromItem(newParent)
            self.treeView_Browse.reset()

            self.treeView_Browse.scrollTo(scrollIndex, QAbstractItemView.PositionAtTop)
            self.treeView_Browse.expand(scrollIndex)
            
        else:
            scrollItem = ''
            # for each member check to see if they already existed in the tree
            if not newList:
                newList.data.append(ListMember(self.currentDir.strip('.'), ''))
                
            for member in newList.data:
                matchList = self.model.findItems(member.name)
                oldType = ''
                if matchList:
                    oldType = self.model.item(matchList[0].row(), 1).text()
                    self.model.removeRow(matchList[0].index().row())

                newParent = QStandardItem(member.name)
                if not member.type and oldType:
                    member.type = oldType 
                newParentType = QStandardItem(member.type)

                if member.type == 'PO':
                    newChild = QStandardItem('DUMMY')
                    newParent.appendRow(newChild)
                        
                self.model.appendRow([newParent, newParentType])

                if not scrollItem:
                    scrollItem = newParent 

            self.treeView_Browse.sortByColumn(0)
            self.treeView_Browse.reset()
            scrollIndex = self.model.indexFromItem(scrollItem)
            self.treeView_Browse.scrollTo(scrollIndex, QAbstractItemView.PositionAtTop)

    def btn_Ok_Clicked(self):
        selectedIndexList = self.treeView_Browse.selectedIndexes()
        selectedString    = ''

        if selectedIndexList:
            selectedItem = self.model.itemFromIndex(selectedIndexList[0])

            if selectedItem.parent():
                selectedString = selectedItem.parent().text() + '(' + selectedItem.text() + ')'

            else:
                if not selectedItem.child(0):
                    selectedString = selectedItem.text()
        
        self.selectedString = selectedString;
        self.close()        

    def btn_Cancel_Clicked(self):
        self.selectedString = ''
        self.close()

if __name__ == '__main__':        
    app = QtGui.QApplication(sys.argv)
    RemoteBrowseClass.getRemotePath(None)
