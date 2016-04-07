# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_client_select.ui'
#
# Created: Wed Nov 20 11:05:11 2013
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_FrameClientSelect(object):
    def setupUi(self, FrameClientSelect):
        FrameClientSelect.setObjectName(_fromUtf8("FrameClientSelect"))
        FrameClientSelect.setWindowModality(QtCore.Qt.ApplicationModal)
        FrameClientSelect.resize(434, 416)
        FrameClientSelect.setFrameShape(QtGui.QFrame.StyledPanel)
        FrameClientSelect.setFrameShadow(QtGui.QFrame.Raised)
        self.verticalLayout_2 = QtGui.QVBoxLayout(FrameClientSelect)
        self.verticalLayout_2.setContentsMargins(2, 2, 3, 2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(FrameClientSelect)
        self.widget.setMinimumSize(QtCore.QSize(0, 45))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(13, 15, 91, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtContent = QtGui.QLineEdit(self.widget)
        self.edtContent.setGeometry(QtCore.QRect(100, 14, 201, 20))
        self.edtContent.setObjectName(_fromUtf8("edtContent"))
        self.btnQuery = QtGui.QPushButton(self.widget)
        self.btnQuery.setGeometry(QtCore.QRect(305, 12, 51, 23))
        self.btnQuery.setObjectName(_fromUtf8("btnQuery"))
        self.btnThatIs = QtGui.QPushButton(self.widget)
        self.btnThatIs.setGeometry(QtCore.QRect(360, 12, 51, 23))
        self.btnThatIs.setObjectName(_fromUtf8("btnThatIs"))
        self.verticalLayout.addWidget(self.widget)
        self.tvClients = QtGui.QTreeWidget(FrameClientSelect)
        self.tvClients.setObjectName(_fromUtf8("tvClients"))
        self.tvClients.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout.addWidget(self.tvClients)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(FrameClientSelect)
        QtCore.QMetaObject.connectSlotsByName(FrameClientSelect)

    def retranslateUi(self, FrameClientSelect):
        FrameClientSelect.setWindowTitle(_translate("FrameClientSelect", "选择客户", None))
        self.label.setText(_translate("FrameClientSelect", "客户名称 / ID", None))
        self.btnQuery.setText(_translate("FrameClientSelect", "查找", None))
        self.btnThatIs.setText(_translate("FrameClientSelect", "选择", None))

