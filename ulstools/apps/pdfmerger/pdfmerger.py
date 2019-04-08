# -*- coding: utf-8 -*-
"""
PDF file merger

@author: Jussi (jnu@iki.fi)
"""

import sys

from pkg_resources import resource_filename, resource_stream
from PyQt5 import QtWidgets, uic

from PyPDF2 import PdfFileMerger, utils


def message_dialog(msg):
    """ Show message with an 'OK' button. """
    dlg = QtWidgets.QMessageBox()
    dlg.setWindowTitle('Message')
    dlg.setText(msg)
    dlg.addButton(QtWidgets.QPushButton('Ok'),
                  QtWidgets.QMessageBox.YesRole)
    dlg.exec_()


class MergeDialog(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        # load user interface made with designer
        uifile = resource_stream('ulstools', 'apps/pdfmerger/pdfmerger.ui')
        uic.loadUi(uifile, self)
        self.btnAddFiles.clicked.connect(self._add_pdfs)
        self.btnMerge.clicked.connect(self._merge)
        self.btnClearAll.clicked.connect(self._clear_list)
        self.btnQuit.clicked.connect(self.close)
        self._files = list()

    def _add_pdfs(self):
        pdfs = QtWidgets.QFileDialog.getOpenFileNames(None, 'Load PDF file',
                                                      '',
                                                      'PDF files (*.pdf)')[0]
        for pdf in pdfs:
            if pdf not in self._files:
                self._files.append(pdf)

        self._update_list()

    def _update_list(self):
        self.lblFiles.setText(u'\n'.join(self._files))

    def _clear_list(self):
        self._files = list()
        self._update_list()

    def _merge(self):
        if not self._files:
            return

        merger = PdfFileMerger(strict=False)

        for pdf in self._files:
            try:
                merger.append(pdf)
            except utils.PdfReadError:
                message_dialog('Cannot read %s - possibly an encrypted file'
                               % pdf)
                return

        outfn = QtWidgets.QFileDialog.getSaveFileName(None, 'Save PDF file',
                                                      '',
                                                      'PDF files (*.pdf)')[0]
        if outfn:
            try:
                merger.write(outfn)
                message_dialog('Successfully wrote %s' % outfn)

            except IOError:
                message_dialog('Cannot write %s, file may already be open'
                               % outfn)


def main():
    print(__name__)
    app = QtWidgets.QApplication(sys.argv)
    md = MergeDialog()
    md.show()
    app.exec_()


if __name__ == '__main__':
    main()
