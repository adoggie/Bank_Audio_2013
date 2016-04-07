# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_lockscreen_settings.ui'
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

class Ui_DialogLockScreenSettings(object):
    def setupUi(self, DialogLockScreenSettings):
        DialogLockScreenSettings.setObjectName(_fromUtf8("DialogLockScreenSettings"))
        DialogLockScreenSettings.resize(337, 182)
        self.label = QtGui.QLabel(DialogLockScreenSettings)
        self.label.setGeometry(QtCore.QRect(20, 36, 54, 12))
        self.label.setObjectName(_fromUtf8("label"))
        self.edtOld = QtGui.QLineEdit(DialogLockScreenSettings)
        self.edtOld.setGeometry(QtCore.QRect(104, 32, 191, 20))
        self.edtOld.setEchoMode(QtGui.QLineEdit.Password)
        self.edtOld.setObjectName(_fromUtf8("edtOld"))
        self.edtNew = QtGui.QLineEdit(DialogLockScreenSettings)
        self.edtNew.setGeometry(QtCore.QRect(104, 70, 191, 20))
        self.edtNew.setEchoMode(QtGui.QLineEdit.Password)
        self.edtNew.setObjectName(_fromUtf8("edtNew"))
        self.label_2 = QtGui.QLabel(DialogLockScreenSettings)
        self.label_2.setGeometry(QtCore.QRect(20, 72, 54, 12))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.edtNew2 = QtGui.QLineEdit(DialogLockScreenSettings)
        self.edtNew2.setGeometry(QtCore.QRect(104, 102, 191, 20))
        self.edtNew2.setEchoMode(QtGui.QLineEdit.Password)
        self.edtNew2.setObjectName(_fromUtf8("edtNew2"))
        self.label_3 = QtGui.QLabel(DialogLockScreenSettings)
        self.label_3.setGeometry(QtCore.QRect(20, 104, 81, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.btnOk = QtGui.QPushButton(DialogLockScreenSettings)
        self.btnOk.setGeometry(QtCore.QRect(136, 148, 75, 23))
        self.btnOk.setObjectName(_fromUtf8("btnOk"))
        self.label_4 = QtGui.QLabel(DialogLockScreenSettings)
        self.label_4.setGeometry(QtCore.QRect(104, 128, 145, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(DialogLockScreenSettings)
        QtCore.QMetaObject.connectSlotsByName(DialogLockScreenSettings)

    def retranslateUi(self, DialogLockScreenSettings):
        DialogLockScreenSettings.setWindowTitle(_translate("DialogLockScreenSettings", "锁屏密码", None))
        self.label.setText(_translate("DialogLockScreenSettings", "旧密码", None))
        self.label_2.setText(_translate("DialogLockScreenSettings", "新密码", None))
        self.label_3.setText(_translate("DialogLockScreenSettings", "重复新密码", None))
        self.btnOk.setText(_translate("DialogLockScreenSettings", "确 定", None))
        self.label_4.setText(_translate("DialogLockScreenSettings", "(密码需是字母+数字)", None))

