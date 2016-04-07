# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dial.ui'
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

class Ui_FrameDial(object):
    def setupUi(self, FrameDial):
        FrameDial.setObjectName(_fromUtf8("FrameDial"))
        FrameDial.setWindowModality(QtCore.Qt.NonModal)
        FrameDial.resize(371, 193)
        FrameDial.setFrameShape(QtGui.QFrame.StyledPanel)
        FrameDial.setFrameShadow(QtGui.QFrame.Raised)
        self.label_6 = QtGui.QLabel(FrameDial)
        self.label_6.setGeometry(QtCore.QRect(20, 96, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(FrameDial)
        self.label_7.setGeometry(QtCore.QRect(10, 40, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.btnDial = QtGui.QPushButton(FrameDial)
        self.btnDial.setGeometry(QtCore.QRect(130, 140, 121, 31))
        self.btnDial.setObjectName(_fromUtf8("btnDial"))
        self.cbxClients = QtGui.QComboBox(FrameDial)
        self.cbxClients.setGeometry(QtCore.QRect(90, 80, 251, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.cbxClients.setFont(font)
        self.cbxClients.setEditable(False)
        self.cbxClients.setFrame(True)
        self.cbxClients.setObjectName(_fromUtf8("cbxClients"))
        self.cbxPhoneNum = QtGui.QComboBox(FrameDial)
        self.cbxPhoneNum.setGeometry(QtCore.QRect(90, 30, 251, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.cbxPhoneNum.setFont(font)
        self.cbxPhoneNum.setInputMethodHints(QtCore.Qt.ImhDigitsOnly|QtCore.Qt.ImhPreferNumbers)
        self.cbxPhoneNum.setEditable(True)
        self.cbxPhoneNum.setFrame(True)
        self.cbxPhoneNum.setObjectName(_fromUtf8("cbxPhoneNum"))

        self.retranslateUi(FrameDial)
        QtCore.QMetaObject.connectSlotsByName(FrameDial)

    def retranslateUi(self, FrameDial):
        FrameDial.setWindowTitle(_translate("FrameDial", "拨号", None))
        self.label_6.setText(_translate("FrameDial", "客    户", None))
        self.label_7.setText(_translate("FrameDial", "拨打号码", None))
        self.btnDial.setText(_translate("FrameDial", "拨号", None))

