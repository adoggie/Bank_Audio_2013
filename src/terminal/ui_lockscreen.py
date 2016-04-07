# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lockscreen.ui'
#
# Created: Wed Nov 20 11:05:12 2013
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

class Ui_DialogLock(object):
    def setupUi(self, DialogLock):
        DialogLock.setObjectName(_fromUtf8("DialogLock"))
        DialogLock.setWindowModality(QtCore.Qt.NonModal)
        DialogLock.resize(313, 138)
        self.edtPasswd = QtGui.QLineEdit(DialogLock)
        self.edtPasswd.setGeometry(QtCore.QRect(60, 40, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.edtPasswd.setFont(font)
        self.edtPasswd.setEchoMode(QtGui.QLineEdit.Password)
        self.edtPasswd.setObjectName(_fromUtf8("edtPasswd"))
        self.label = QtGui.QLabel(DialogLock)
        self.label.setGeometry(QtCore.QRect(10, 47, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.btnUnlock = QtGui.QPushButton(DialogLock)
        self.btnUnlock.setGeometry(QtCore.QRect(120, 90, 75, 31))
        self.btnUnlock.setObjectName(_fromUtf8("btnUnlock"))

        self.retranslateUi(DialogLock)
        QtCore.QMetaObject.connectSlotsByName(DialogLock)

    def retranslateUi(self, DialogLock):
        DialogLock.setWindowTitle(_translate("DialogLock", "超时锁屏", None))
        self.label.setText(_translate("DialogLock", "口 令", None))
        self.btnUnlock.setText(_translate("DialogLock", "解 锁", None))

