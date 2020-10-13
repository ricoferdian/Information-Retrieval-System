from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, StopWordRemoverFactory, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import Stemmer, StemmerFactory

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from collections import Counter

import re
import os
import sys
import random
import plot
import summarize

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        v_layout_l = QVBoxLayout()
        v_layout_m = QVBoxLayout()
        h_layout = QHBoxLayout()
        h_l_btnlayout = QHBoxLayout()
        h_r_btnlayout = QHBoxLayout()

        self.editor = QPlainTextEdit()  # Could also use a QTextEdit and set self.editor.setAcceptRichText(False)
        self.raw = QPlainTextEdit()
        self.textResult = QPlainTextEdit()
        self.dictionary = QPlainTextEdit()
        self.countFreq = QPlainTextEdit()

        self.textCount = QLabel()
        self.textCount.setText("Jumlah Kata : 0")

        self.textFreq = QLabel()
        self.textFreq.setWordWrap(True)
        self.textFreq.setText("Frekuensi kata : 0")

        self.textCountResult = QLabel()
        self.textCountResult.setText("Jumlah Kata : 0")

        self.textFreqResult = QLabel()
        self.textFreqResult.setWordWrap(True)
        self.textFreqResult.setText("Frekuensi kata : 0")

        self.calculateButton = QPushButton()
        self.calculateButton.setText("Hitung kata")

        self.calculateButtonResult = QPushButton()
        self.calculateButtonResult.setText("Hitung kata")

        self.dictButton = QPushButton()
        self.dictButton.setText("Buka File Kamus")

        self.openFileButton = QPushButton()
        self.openFileButton.setText("Buka File")

        self.stopWordButton = QPushButton()
        self.stopWordButton.setText("Hasil Stopword")

        self.stemButton = QPushButton()
        self.stemButton.setText("Hasil Stem")

        self.matplotlibButton = QPushButton()
        self.matplotlibButton.setText("Grafik Frekuensi Awal")

        self.matplotlibButtonResult = QPushButton()
        self.matplotlibButtonResult.setText("Grafik Frekuensi Hasil")

        self.summarizebutton = QPushButton()
        self.summarizebutton.setText("Summarize")

        # Setup the QTextEdit editor configuration
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)
        self.textResult.setFont(fixedfont)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        h_l_btnlayout.addWidget(self.textCount)
        h_l_btnlayout.addWidget(self.openFileButton)
        h_l_btnlayout.addWidget(self.calculateButton)
        h_l_btnlayout.addWidget(self.matplotlibButton)
        h_l_btnlayout.addWidget(self.dictButton)

        h_r_btnlayout.addWidget(self.textCountResult)
        h_r_btnlayout.addWidget(self.stopWordButton)
        h_r_btnlayout.addWidget(self.calculateButtonResult)
        h_r_btnlayout.addWidget(self.stemButton)
        h_r_btnlayout.addWidget(self.matplotlibButtonResult)
        h_r_btnlayout.addWidget(self.summarizebutton)

        v_layout_l.addWidget(self.editor)
        v_layout_l.addLayout(h_l_btnlayout)
        v_layout_l.addWidget(self.textFreq)
        v_layout_m.addWidget(self.textResult)
        v_layout_m.addLayout(h_r_btnlayout)
        v_layout_m.addWidget(self.textFreqResult)

        h_layout.addLayout(v_layout_l)
        h_layout.addLayout(v_layout_m)

        container = QWidget()
        container.setLayout(h_layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.calculateButton.clicked.connect(self.reCalculate)

        self.calculateButtonResult.clicked.connect(self.reCalculateResult)

        self.dictButton.clicked.connect(self.dict_open)

        self.stemButton.clicked.connect(self.stem_word)

        self.stopWordButton.clicked.connect(self.remove_stopword)

        self.matplotlibButton.clicked.connect(self.showPlot)

        self.matplotlibButtonResult.clicked.connect(self.showPlotResult)

        self.openFileButton.clicked.connect(self.file_open)

        self.summarizebutton.clicked.connect(self.tfIdf)

        self.plotWindow = plot.PlotWindow(self)

        self.plotWindowResult = plot.PlotWindow(self)

        self.summaryWindow = summarize.SummarizeWindow(self)

        file_toolbar = QToolBar("Dokumen")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&Dokumen")

        open_file_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Buka dokumen...", self)
        open_file_action.setStatusTip("Buka dokumen")
        open_file_action.triggered.connect(self.file_open)
        file_menu.addAction(open_file_action)
        file_toolbar.addAction(open_file_action)

        open_dict_action = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Buka kamus...",
                                   self)
        open_dict_action.setStatusTip("Buka kamus")
        open_dict_action.triggered.connect(self.dict_open)
        file_menu.addAction(open_dict_action)
        file_toolbar.addAction(open_dict_action)

        save_file_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Simpan", self)
        save_file_action.setStatusTip("Simpan teks awal pada bagian kiri jendela")
        save_file_action.triggered.connect(self.file_save)
        file_menu.addAction(save_file_action)
        file_toolbar.addAction(save_file_action)

        saveas_file_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Simpan sebagai...", self)
        saveas_file_action.setStatusTip("Simpan sebagai.. teks awal pada bagian kiri jendela")
        saveas_file_action.triggered.connect(self.file_saveas)
        file_menu.addAction(saveas_file_action)
        file_toolbar.addAction(saveas_file_action)

        print_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Cetak teks awal...", self)
        print_action.setStatusTip("Cetak teks awal pada bagian kiri jendela")
        print_action.triggered.connect(self.file_print)
        file_menu.addAction(print_action)
        file_toolbar.addAction(print_action)

        edit_toolbar = QToolBar("Sunting")
        edit_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(edit_toolbar)
        edit_menu = self.menuBar().addMenu("&Sunting")

        undo_action = QAction(QIcon(os.path.join('images', 'arrow-curve-180-left.png')), "Urungkan", self)
        undo_action.setStatusTip("Urungkan perubahan terakhir")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Batal urungkan", self)
        redo_action.setStatusTip("Batal urungkan perubahan terakhir")
        redo_action.triggered.connect(self.editor.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Potong", self)
        cut_action.setStatusTip("Potong teks dipilih")
        cut_action.triggered.connect(self.editor.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Salin", self)
        copy_action.setStatusTip("Salin teks dipilih")
        copy_action.triggered.connect(self.editor.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Tempel", self)
        paste_action.setStatusTip("Tempel dari clipboard")
        paste_action.triggered.connect(self.editor.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Pilih semua", self)
        select_action.setStatusTip("Pilih semua teks")
        select_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        file_result_toolbar = QToolBar("Dokumen")
        file_result_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_result_toolbar)
        file_menu = self.menuBar().addMenu("&Hasil")

        save_file_result_action = QAction(QIcon(os.path.join('images', 'disk.png')), "Simpan hasil", self)
        save_file_result_action.setStatusTip("Simpan teks hasil pada bagian kanan jendela")
        save_file_result_action.triggered.connect(self.file_result_save)
        file_menu.addAction(save_file_result_action)
        file_result_toolbar.addAction(save_file_result_action)

        saveas_file_result_action = QAction(QIcon(os.path.join('images', 'disk--pencil.png')), "Simpan hasil sebagai...", self)
        saveas_file_result_action.setStatusTip("Simpan sebagai.. teks hasil pada bagian kanan jendela")
        saveas_file_result_action.triggered.connect(self.file_result_saveas)
        file_menu.addAction(saveas_file_result_action)
        file_result_toolbar.addAction(saveas_file_result_action)

        print_result_action = QAction(QIcon(os.path.join('images', 'printer.png')), "Cetak hasil...", self)
        print_result_action.setStatusTip("Cetak teks hasil pada bagian kanan jendela")
        print_result_action.triggered.connect(self.file_print_result)
        file_menu.addAction(print_result_action)
        file_result_toolbar.addAction(print_result_action)

        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Wrap teks ke jendela", self)
        wrap_action.setStatusTip("Wrap teks")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        self.update_title()
        self.show()

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def showPlot(self):
        self.countFreq.setPlainText(self.editor.toPlainText())
        self.plotWindow.show()

    def showPlotResult(self):
        self.countFreq.setPlainText(self.textResult.toPlainText())
        self.plotWindowResult.show()

    def tfIdf(self):
        self.raw.setPlainText(self.editor.toPlainText())
        self.summaryWindow.show()

    def reCalculate(self):
        text = self.editor.toPlainText()
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        kalimat = removed_number.split('.')
        num_kalimat = len(kalimat)
        splitted = removed_number.split()
        num_words = len(splitted)
        # splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCount.setText("Total Kata : " + str(num_words)+" Total Kalimat : "+str(num_kalimat))
        self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq)))

    def reCalculateResult(self):
        text = self.textResult.toPlainText()
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        kalimat = removed_number.split('.')
        num_kalimat = len(kalimat)
        splitted = removed_number.split()
        num_words = len(splitted)
        # splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCountResult.setText("Total Kata : " + str(num_words)+" Total Kalimat : "+str(num_kalimat))
        self.textFreqResult.setText("Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq)))

    def stem_word(self):
        raw = self.textResult.toPlainText()
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        result = stemmer.stem(raw)
        self.textResult.setPlainText(result)
        self.reCalculateResult()

    def remove_stopword(self):
        # Data teks diambil dari widget
        dict = self.dictionary.toPlainText()
        raw = self.editor.toPlainText()

        # Contoh kata untuk demonstrasi
        # contoh_kata = "Ini adalah contoh kata dalam bahasa indonesia yang digunakan untuk stopword"

        # Ambil dari dict sendiri
        stop_factory = re.findall(r'\w+', dict)

        # Stopword bawaan sastrawi
        # stop_factory = StopWordRemoverFactory().get_stop_words()

        dictionary = ArrayDictionary(stop_factory)

        # Membuat stopword remover
        remover = StopWordRemover(dictionary)
        self.textResult.setPlainText(remover.remove(raw))
        self.reCalculateResult()

    def dict_open(self):
        # Membuka file txt kamus
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt);All files (*.*)")

        # Memvalidasi data kemudian melakukan pembacaan data file txt
        if path:
            try:
                with open(path, 'rt') as f:
                    dict = f.read()

            except Exception as e:
                self.dialog_critical(str(e))

            else:
                self.path = path
                self.dictionary.setPlainText(dict)
                self.textResult.setPlainText(dict)

    # Membuka file raw yang akan dilakukan pengecekan
    def file_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt);All files (*.*)")
        if path:
            try:
                with open(path, 'rt') as f:
                    text = f.read()
                removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
                kalimat = removed_number.split('.')
                num_kalimat = len(kalimat)
                splitted = removed_number.split()
                num_words = len(splitted)
                # splitted = re.findall(r'\w+', removed_number)
                freq = Counter(splitted)
                self.textCount.setText("Total Kata : " + str(num_words)+" Total Kalimat : "+str(num_kalimat))
                self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq)))
                # self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common(100)))

            except Exception as e:
                self.dialog_critical(str(e))

            else:
                self.path = path

                # Menampilkan data teks ke widget editor -> QPlain
                self.editor.setPlainText(text)
                self.update_title()

    def file_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        self._save_to_path(self.path)

    def file_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text documents (*.txt)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_to_path(path)

    def file_result_save(self):
        if self.path is None:
            # If we do not have a path, we need to use Save As.
            return self.file_saveas()

        self._save_result_to_path(self.path)

    def file_result_saveas(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Text documents (*.txt)")

        if not path:
            # If dialog is cancelled, will return ''
            return

        self._save_result_to_path(path)

    def _save_to_path(self, path):
        text = self.editor.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def _save_result_to_path(self, path):
        text = self.textResult.toPlainText()
        try:
            with open(path, 'w') as f:
                f.write(text)

        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.update_title()

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def file_print_result(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.textResult.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle(
            "%s - Sistem Temu Kembali Informasi" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Sistem Temu Kembali Informasi")

    window = MainWindow()
    app.exec_()
