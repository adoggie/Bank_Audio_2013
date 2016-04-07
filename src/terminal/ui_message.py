# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_message.ui'
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

class Ui_FrameMessage(object):
    def setupUi(self, FrameMessage):
        FrameMessage.setObjectName(_fromUtf8("FrameMessage"))
        FrameMessage.setWindowModality(QtCore.Qt.NonModal)
        FrameMessage.resize(319, 130)
        FrameMessage.setFrameShape(QtGui.QFrame.Box)
        FrameMessage.setFrameShadow(QtGui.QFrame.Sunken)
        self.text = QtGui.QLabel(FrameMessage)
        self.text.setGeometry(QtCore.QRect(20, 20, 285, 69))
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setWordWrap(True)
        self.text.setObjectName(_fromUtf8("text"))
        self.btnOk = QtGui.QPushButton(FrameMessage)
        self.btnOk.setGeometry(QtCore.QRect(120, 92, 75, 25))
        self.btnOk.setObjectName(_fromUtf8("btnOk"))

        self.retranslateUi(FrameMessage)
        QtCore.QMetaObject.connectSlotsByName(FrameMessage)

    def retranslateUi(self, FrameMessage):
        FrameMessage.setWindowTitle(_translate("FrameMessage", "Frame", None))
        self.text.setText(_translate("FrameMessage", "TextLabel", None))
        self.btnOk.setText(_translate("FrameMessage", "确 定", None))

