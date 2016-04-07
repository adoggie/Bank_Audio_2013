# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_change_pwd.ui'
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

class Ui_FrameChangePasswd(object):
    def setupUi(self, FrameChangePasswd):
        FrameChangePasswd.setObjectName(_fromUtf8("FrameChangePasswd"))
        FrameChangePasswd.setWindowModality(QtCore.Qt.NonModal)
        FrameChangePasswd.resize(371, 179)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        FrameChangePasswd.setFont(font)
        FrameChangePasswd.setModal(True)
        self.label_7 = QtGui.QLabel(FrameChangePasswd)
        self.label_7.setGeometry(QtCore.QRect(10, 32, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.btnDone = QtGui.QPushButton(FrameChangePasswd)
        self.btnDone.setGeometry(QtCore.QRect(130, 140, 121, 31))
        self.btnDone.setObjectName(_fromUtf8("btnDone"))
        self.edt_old = QtGui.QLineEdit(FrameChangePasswd)
        self.edt_old.setGeometry(QtCore.QRect(100, 32, 241, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.edt_old.setFont(font)
        self.edt_old.setText(_fromUtf8(""))
        self.edt_old.setMaxLength(20)
        self.edt_old.setEchoMode(QtGui.QLineEdit.Password)
        self.edt_old.setObjectName(_fromUtf8("edt_old"))
        self.edt_new = QtGui.QLineEdit(FrameChangePasswd)
        self.edt_new.setGeometry(QtCore.QRect(100, 62, 241, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.edt_new.setFont(font)
        self.edt_new.setInputMask(_fromUtf8(""))
        self.edt_new.setText(_fromUtf8(""))
        self.edt_new.setMaxLength(20)
        self.edt_new.setEchoMode(QtGui.QLineEdit.Password)
        self.edt_new.setObjectName(_fromUtf8("edt_new"))
        self.label_8 = QtGui.QLabel(FrameChangePasswd)
        self.label_8.setGeometry(QtCore.QRect(10, 62, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_8.setFont(font)
        self.label_8.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.edt_new2 = QtGui.QLineEdit(FrameChangePasswd)
        self.edt_new2.setGeometry(QtCore.QRect(100, 92, 241, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.edt_new2.setFont(font)
        self.edt_new2.setText(_fromUtf8(""))
        self.edt_new2.setMaxLength(20)
        self.edt_new2.setEchoMode(QtGui.QLineEdit.Password)
        self.edt_new2.setObjectName(_fromUtf8("edt_new2"))
        self.label_9 = QtGui.QLabel(FrameChangePasswd)
        self.label_9.setGeometry(QtCore.QRect(10, 92, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.label_9.setFont(font)
        self.label_9.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.label = QtGui.QLabel(FrameChangePasswd)
        self.label.setGeometry(QtCore.QRect(92, 120, 241, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(FrameChangePasswd)
        QtCore.QMetaObject.connectSlotsByName(FrameChangePasswd)

    def retranslateUi(self, FrameChangePasswd):
        FrameChangePasswd.setWindowTitle(_translate("FrameChangePasswd", "修改密码", None))
        self.label_7.setText(_translate("FrameChangePasswd", "原密码", None))
        self.btnDone.setText(_translate("FrameChangePasswd", "修 改", None))
        self.label_8.setText(_translate("FrameChangePasswd", "新密码", None))
        self.label_9.setText(_translate("FrameChangePasswd", "确认密码", None))
        self.label.setText(_translate("FrameChangePasswd", "(密码需是字母+数字)", None))

