# -*- coding: utf-8 -*-
"""
Simple GUI for merging PDF files

@author: Jussi (jnu@iki.fi)
"""

import sys

from pkg_resources import resource_stream
from PyQt5 import QtWidgets, uic, QtCore

from ulstools.env import make_shortcut
from PyPDF2 import PdfFileMerger, utils


def make_my_shortcut():
    make_shortcut('ulstools', 'apps/pdfmerger/pdfmerger.py', 'PDF merge tool')


def message_dialog(msg):
    """Show message with an 'OK' button."""
    dlg = QtWidgets.QMessageBox()
    dlg.setWindowTitle('Message')
    dlg.setText(msg)
    dlg.addButton(QtWidgets.QPushButton('Ok'), QtWidgets.QMessageBox.YesRole)
    dlg.exec_()


class MergeDialog(QtWidgets.QMainWindow):

    _pdf_filter = 'PDF files (*.pdf)'

    def __init__(self):

        super(MergeDialog, self).__init__()
        # load user interface made with designer
        uifile = resource_stream('ulstools', 'apps/pdfmerger/pdfmerger.ui')
        uic.loadUi(uifile, self)
        self.btnAddFiles.clicked.connect(self._add_files)
        self.btnMerge.clicked.connect(self._merge)
        self.btnRemoveFile.clicked.connect(self.listFiles.rm_current_item)
        self.listFiles.setDragDropMode(self.listFiles.InternalMove)
        self.actionQuit.triggered.connect(self.close)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.listFiles.rm_current_item()
        event.accept()

    @property
    def _files(self):
        """Return list of filenames from the list widget"""
        return [it.text for it in self.listFiles.items]

    def _add_files(self):
        """Add files to list widget"""
        pdfs = QtWidgets.QFileDialog.getOpenFileNames(
            None, 'Load PDF file', '', MergeDialog._pdf_filter
        )[0]
        for pdf in pdfs:
            if pdf not in self._files:
                self.listFiles.add_item(pdf)

    def _merge(self):
        if len(self._files) < 2:
            message_dialog('Load at least two files first')
            return

        merger = PdfFileMerger(strict=False)

        for pdf in self._files:
            try:
                merger.append(pdf)
            except utils.PdfReadError:
                message_dialog('Cannot read %s - possibly an encrypted file' % pdf)
                return

        outfn = QtWidgets.QFileDialog.getSaveFileName(
            None, 'Save PDF file', '', MergeDialog._pdf_filter
        )[0]
        if outfn:
            try:
                merger.write(outfn)
                message_dialog('Successfully wrote %s' % outfn)
            except IOError:
                message_dialog('Cannot write %s, file may already be open' % outfn)


def main():
    app = QtWidgets.QApplication(sys.argv)
    md = MergeDialog()
    md.show()
    app.exec_()


if __name__ == '__main__':
    main()
