# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_tone_dial.ui'
#
# Created: Wed Jan 08 14:38:09 2014
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

class Ui_FrameToneDial(object):
    def setupUi(self, FrameToneDial):
        FrameToneDial.setObjectName(_fromUtf8("FrameToneDial"))
        FrameToneDial.setWindowModality(QtCore.Qt.NonModal)
        FrameToneDial.resize(354, 120)
        FrameToneDial.setFrameShape(QtGui.QFrame.StyledPanel)
        FrameToneDial.setFrameShadow(QtGui.QFrame.Raised)
        self.label = QtGui.QLabel(FrameToneDial)
        self.label.setGeometry(QtCore.QRect(4, 48, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label.setObjectName(_fromUtf8("label"))
        self.btnHangOn = QtGui.QPushButton(FrameToneDial)
        self.btnHangOn.setGeometry(QtCore.QRect(268, 12, 80, 30))
        self.btnHangOn.setObjectName(_fromUtf8("btnHangOn"))
        self.btnHangUp = QtGui.QPushButton(FrameToneDial)
        self.btnHangUp.setGeometry(QtCore.QRect(268, 44, 80, 30))
        self.btnHangUp.setObjectName(_fromUtf8("btnHangUp"))
        self.label_2 = QtGui.QLabel(FrameToneDial)
        self.label_2.setGeometry(QtCore.QRect(4, 16, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.txtPhoneNum = QtGui.QLabel(FrameToneDial)
        self.txtPhoneNum.setGeometry(QtCore.QRect(96, 40, 209, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.txtPhoneNum.setFont(font)
        self.txtPhoneNum.setStyleSheet(_fromUtf8("color: rgb(0, 0, 255);"))
        self.txtPhoneNum.setObjectName(_fromUtf8("txtPhoneNum"))
        self.txtStatus = QtGui.QLabel(FrameToneDial)
        self.txtStatus.setGeometry(QtCore.QRect(96, 8, 205, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.txtStatus.setFont(font)
        self.txtStatus.setStyleSheet(_fromUtf8("color: rgb(0, 0, 255);"))
        self.txtStatus.setObjectName(_fromUtf8("txtStatus"))
        self.txtClientName = QtGui.QLabel(FrameToneDial)
        self.txtClientName.setGeometry(QtCore.QRect(96, 72, 185, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.txtClientName.setFont(font)
        self.txtClientName.setStyleSheet(_fromUtf8("color: rgb(0, 0, 255);"))
        self.txtClientName.setObjectName(_fromUtf8("txtClientName"))
        self.label_6 = QtGui.QLabel(FrameToneDial)
        self.label_6.setGeometry(QtCore.QRect(6, 80, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.labDuration = QtGui.QLabel(FrameToneDial)
        self.labDuration.setGeometry(QtCore.QRect(12, 400, 70, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.labDuration.setFont(font)
        self.labDuration.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.labDuration.setObjectName(_fromUtf8("labDuration"))
        self.txtDuration = QtGui.QLabel(FrameToneDial)
        self.txtDuration.setGeometry(QtCore.QRect(100, 400, 129, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.txtDuration.setFont(font)
        self.txtDuration.setStyleSheet(_fromUtf8("color: rgb(255, 0, 0);"))
        self.txtDuration.setObjectName(_fromUtf8("txtDuration"))
        self.btnMemo = QtGui.QPushButton(FrameToneDial)
        self.btnMemo.setGeometry(QtCore.QRect(268, 76, 80, 30))
        self.btnMemo.setObjectName(_fromUtf8("btnMemo"))

        self.retranslateUi(FrameToneDial)
        QtCore.QMetaObject.connectSlotsByName(FrameToneDial)

    def retranslateUi(self, FrameToneDial):
        FrameToneDial.setWindowTitle(_translate("FrameToneDial", "通话提示", None))
        self.label.setText(_translate("FrameToneDial", "电    话", None))
        self.btnHangOn.setText(_translate("FrameToneDial", "    接 听    ", None))
        self.btnHangUp.setText(_translate("FrameToneDial", "   挂 机   ", None))
        self.label_2.setText(_translate("FrameToneDial", "状    态", None))
        self.txtPhoneNum.setText(_translate("FrameToneDial", "01034558897", None))
        self.txtStatus.setText(_translate("FrameToneDial", "来电...", None))
        self.txtClientName.setText(_translate("FrameToneDial", "上海国贸-小李", None))
        self.label_6.setText(_translate("FrameToneDial", "客    户", None))
        self.labDuration.setText(_translate("FrameToneDial", "通话时长", None))
        self.txtDuration.setText(_translate("FrameToneDial", "00:00:00", None))
        self.btnMemo.setText(_translate("FrameToneDial", "   备 注   ", None))

