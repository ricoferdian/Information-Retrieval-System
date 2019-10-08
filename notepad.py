from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, StopWordRemoverFactory, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import Stemmer, StemmerFactory

from nltk import sent_tokenize, word_tokenize

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from collections import Counter

import re
import os
import sys
import random
import math


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        self.axis = self.figure.add_subplot(111)

        self.layoutVertical = QVBoxLayout(self)
        self.layoutVertical.addWidget(self.canvas)


class ThreadSample(QThread):
    newSample = pyqtSignal(list)

    def __init__(self, parent=None):
        super(ThreadSample, self).__init__(parent)

    def run(self):
        randomSample = random.sample(range(0, 10), 10)

        self.newSample.emit(randomSample)


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
        #v_layout_l.addWidget(self.textFreq)
        v_layout_m.addWidget(self.textResult)
        v_layout_m.addLayout(h_r_btnlayout)
        #v_layout_m.addWidget(self.textFreqResult)

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

        self.plotWindow = PlotWindow(self)

        self.plotWindowResult = PlotWindow(self)

        self.summaryWindow = SummarizeWindow(self)

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
        num_words = 0
        text = self.editor.toPlainText()
        num_words += len(text.split())
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCount.setText("Jumlah Kata : " + str(len(freq)))
        self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common()))

    def reCalculateResult(self):
        num_words = 0
        text = self.textResult.toPlainText()
        num_words += len(text.split())
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCountResult.setText("Jumlah Kata : " + str(len(freq)))
        self.textFreqResult.setText("Frekuensi Kata : " + str(freq.most_common()))

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
        num_words = 0
        if path:
            try:
                with open(path, 'rt') as f:
                    text = f.read()
                    num_words += len(text.split())
                removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
                splitted = re.findall(r'\w+', removed_number)
                freq = Counter(splitted)
                self.textCount.setText("Jumlah Kata : " + str(len(freq)))
                self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common(100)))

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
            "%s - Natural Language Processing" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

class SummarizeWindow(QMainWindow):
    def __init__(self,parent):
        super(SummarizeWindow, self).__init__(parent)

        self.parentWindow = parent

        v_layout = QVBoxLayout()

        self.material = QPlainTextEdit()  # Could also use a QTextEdit and set self.editor.setAcceptRichText(False)


        self.textCount = QLabel()
        self.textCount.setText("")

        self.textFreq = QLabel()
        self.textFreq.setWordWrap(True)
        self.textFreq.setText("Frekuensi kata : 0")

        self.calculateButton = QPushButton()
        self.calculateButton.setText("Summarize")

        # Setup the QTextEdit editor configuration
        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.material.setFont(fixedfont)

        # self.path holds the path of the currently open file.
        # If none, we haven't got a file open yet (or creating new).
        self.path = None

        v_layout.addWidget(self.material)
        v_layout.addWidget(self.textCount)
        v_layout.addWidget(self.textFreq)
        v_layout.addWidget(self.calculateButton)

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.calculateButton.clicked.connect(self.summarize)

        file_toolbar = QToolBar("Dokumen")
        file_toolbar.setIconSize(QSize(14, 14))
        self.addToolBar(file_toolbar)
        file_menu = self.menuBar().addMenu("&Dokumen")

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
        undo_action.triggered.connect(self.material.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction(QIcon(os.path.join('images', 'arrow-curve.png')), "Batal urungkan", self)
        redo_action.setStatusTip("Batal urungkan perubahan terakhir")
        redo_action.triggered.connect(self.material.redo)
        edit_toolbar.addAction(redo_action)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction(QIcon(os.path.join('images', 'scissors.png')), "Potong", self)
        cut_action.setStatusTip("Potong teks dipilih")
        cut_action.triggered.connect(self.material.cut)
        edit_toolbar.addAction(cut_action)
        edit_menu.addAction(cut_action)

        copy_action = QAction(QIcon(os.path.join('images', 'document-copy.png')), "Salin", self)
        copy_action.setStatusTip("Salin teks dipilih")
        copy_action.triggered.connect(self.material.copy)
        edit_toolbar.addAction(copy_action)
        edit_menu.addAction(copy_action)

        paste_action = QAction(QIcon(os.path.join('images', 'clipboard-paste-document-text.png')), "Tempel", self)
        paste_action.setStatusTip("Tempel dari clipboard")
        paste_action.triggered.connect(self.material.paste)
        edit_toolbar.addAction(paste_action)
        edit_menu.addAction(paste_action)

        select_action = QAction(QIcon(os.path.join('images', 'selection-input.png')), "Pilih semua", self)
        select_action.setStatusTip("Pilih semua teks")
        select_action.triggered.connect(self.material.selectAll)
        edit_menu.addAction(select_action)

        edit_menu.addSeparator()

        wrap_action = QAction(QIcon(os.path.join('images', 'arrow-continue.png')), "Wrap teks ke jendela", self)
        wrap_action.setStatusTip("Wrap teks")
        wrap_action.setCheckable(True)
        wrap_action.setChecked(True)
        wrap_action.triggered.connect(self.edit_toggle_wrap)
        edit_menu.addAction(wrap_action)

        self.update_title()

    def summarize(self):
        sentences = sent_tokenize(self.parentWindow.raw.toPlainText())
        total_documents = len(sentences)
        frequency_matrix = self._create_frequency_matrix(sentences)
        tf_matrix = self._create_tf_matrix(frequency_matrix)
        word_per_doc_table = self._create_documents_per_words(frequency_matrix)
        idf_matrix = self._create_idf_matrix(frequency_matrix, word_per_doc_table, total_documents)
        tf_idf_matrix = self._create_tf_idf_matrix(tf_matrix, idf_matrix)
        sentence_value = self._score_sentences(tf_idf_matrix)
        average_score = self._find_average_score(sentence_value)
        summary = self._generate_summary(sentences, sentence_value, average_score)
        print(summary)
        self.material.setPlainText(summary)

    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()

    def reCalculate(self):
        num_words = 0
        text = self.editor.toPlainText()
        num_words += len(text.split())
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCount.setText("Jumlah Kata : " + str(len(freq)))
        self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common()))

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

    def file_print(self):
        dlg = QPrintDialog()
        if dlg.exec_():
            self.editor.print_(dlg.printer())

    def update_title(self):
        self.setWindowTitle(
            "Summary of %s - Natural Language Processing" % (os.path.basename(self.path) if self.path else "Untitled"))

    def edit_toggle_wrap(self):
        self.editor.setLineWrapMode(1 if self.editor.lineWrapMode() == 0 else 0)

    def _create_frequency_matrix(self,sentences):
        frequency_matrix = {}
        dict = self.parentWindow.dictionary.toPlainText()
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()

        for sent in sentences:
            freq_table = {}
            words = word_tokenize(sent)
            for word in words:
                word = word.lower()
                word = stemmer.stem(word)
                if word in dict:
                    continue

                if word in freq_table:
                    freq_table[word] += 1
                else:
                    freq_table[word] = 1

            frequency_matrix[sent[:15]] = freq_table

        return frequency_matrix

    def _create_tf_matrix(self,freq_matrix):
        tf_matrix = {}

        for sent, f_table in freq_matrix.items():
            tf_table = {}

            count_words_in_sentence = len(f_table)
            for word, count in f_table.items():
                tf_table[word] = count / count_words_in_sentence

            tf_matrix[sent] = tf_table

        return tf_matrix

    def _create_documents_per_words(self,freq_matrix):
        word_per_doc_table = {}

        for sent, f_table in freq_matrix.items():
            for word, count in f_table.items():
                if word in word_per_doc_table:
                    word_per_doc_table[word] += 1
                else:
                    word_per_doc_table[word] = 1

        return word_per_doc_table

    def _create_idf_matrix(self,freq_matrix, count_doc_per_words, total_documents):
        idf_matrix = {}

        for sent, f_table in freq_matrix.items():
            idf_table = {}

            for word in f_table.keys():
                idf_table[word] = math.log10(total_documents / float(count_doc_per_words[word]))

            idf_matrix[sent] = idf_table

        return idf_matrix

    def _create_tf_idf_matrix(self,tf_matrix, idf_matrix):
        tf_idf_matrix = {}

        for (sent1, f_table1), (sent2, f_table2) in zip(tf_matrix.items(), idf_matrix.items()):

            tf_idf_table = {}

            for (word1, value1), (word2, value2) in zip(f_table1.items(),
                                                        f_table2.items()):  # here, keys are the same in both the table
                tf_idf_table[word1] = float(value1 * value2)

            tf_idf_matrix[sent1] = tf_idf_table

        return tf_idf_matrix

    def _score_sentences(self,tf_idf_matrix) -> dict:
        """
        score a sentence by its word's TF
        Basic algorithm: adding the TF frequency of every non-stop word in a sentence divided by total no of words in a sentence.
        :rtype: dict
        """

        sentenceValue = {}

        for sent, f_table in tf_idf_matrix.items():
            total_score_per_sentence = 0

            count_words_in_sentence = len(f_table)
            for word, score in f_table.items():
                total_score_per_sentence += score

            if(count_words_in_sentence!=0):
                sentenceValue[sent] = total_score_per_sentence / count_words_in_sentence
            else:
                sentenceValue[sent] = 0

        return sentenceValue

    def _find_average_score(self,sentenceValue) -> int:
        """
        Find the average score from the sentence value dictionary
        :rtype: int
        """
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]

        # Average value of a sentence from original summary_text
        if(len(sentenceValue)==0):
            average = 0
        else:
            average = (sumValues / len(sentenceValue))

        return average

    def _generate_summary(self,sentences, sentenceValue, threshold):
        sentence_count = 0
        summary = ''

        for sentence in sentences:
            if sentence[:15] in sentenceValue and sentenceValue[sentence[:15]] >= (threshold):
                summary += " " + sentence
                sentence_count += 1

        return summary

class PlotWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PlotWindow, self).__init__(parent)
        self.parentWindow = parent

        self.textdata = self.parentWindow.textResult.toPlainText()
        self.matplotlibwidget = MatplotlibWidget(self)

        self.matplotlibButton = QPushButton()
        self.matplotlibButton.setText("Hitung Ulang Frekuensi")

        self.matplotlibButton.clicked.connect(self.wordFreqPlot)

        # self.threadSample = ThreadSample(self)
        # self.threadSample.newSample.connect(self.on_threadSample_newSample)
        # self.threadSample.finished.connect(self.on_threadSample_finished)

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.matplotlibButton)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.wordFreqPlot()

    def wordFreqPlot(self):
        # random data

        #splitted = re.findall(r'\w+', self.parentWindow.countFreq.toPlainText())
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", self.parentWindow.countFreq.toPlainText())
        splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)

        # demo plot data
        #t = np.arange(0.0, 1.0, 0.01)
        #s = 1 + np.sin(2 * np.pi * t)
        t = [lis[0] for lis in freq.most_common()]
        s = [lis[1] for lis in freq.most_common()]
        #t = [1,2,3,4,5]
        #s = [1,2,3,4,5]

        # create an axis
        ax = self.figure.add_subplot(111)
        #ax = self.figure.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        #ax.plot(data, '*-')
        ax.plot(t, s)

        ax.set(xlabel='Kata', ylabel='Frekuensi',
               title='Frekuensi jumlah kata dalam teks')
        ax.grid()

        # refresh canvas
        self.canvas.draw()

    @pyqtSlot()
    def on_pushButtonPlot_clicked(self):
        self.sample = 10
        self.matplotlibWidget.axis.clear()
        self.threadSample.start()

    @pyqtSlot()
    def on_threadSample_newSample(self, sample):
        self.matplotlibWidget.axis.plot(self.sample)
        self.matplotlibWidget.canvas.draw()

    @pyqtSlot()
    def on_threadSample_finished(self):
        self.samples += 1
        if self.samples <= 2:
            self.threadSample.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Natural Language Processing")

    window = MainWindow()
    app.exec_()
