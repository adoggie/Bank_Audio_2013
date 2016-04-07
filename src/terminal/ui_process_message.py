# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_process_message.ui'
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

class Ui_FrameProcessMessage(object):
    def setupUi(self, FrameProcessMessage):
        FrameProcessMessage.setObjectName(_fromUtf8("FrameProcessMessage"))
        FrameProcessMessage.setWindowModality(QtCore.Qt.ApplicationModal)
        FrameProcessMessage.resize(405, 98)
        FrameProcessMessage.setFrameShape(QtGui.QFrame.WinPanel)
        FrameProcessMessage.setFrameShadow(QtGui.QFrame.Raised)
        self.message = QtGui.QLabel(FrameProcessMessage)
        self.message.setGeometry(QtCore.QRect(40, 30, 321, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial Black"))
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.message.setFont(font)
        self.message.setObjectName(_fromUtf8("message"))

        self.retranslateUi(FrameProcessMessage)
        QtCore.QMetaObject.connectSlotsByName(FrameProcessMessage)

    def retranslateUi(self, FrameProcessMessage):
        FrameProcessMessage.setWindowTitle(_translate("FrameProcessMessage", "Frame", None))
        self.message.setText(_translate("FrameProcessMessage", "TextLabel", None))

