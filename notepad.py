from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, StopWordRemoverFactory, ArrayDictionary
# from Sastrawi.Stemmer.StemmerFactory import Stemmer, StemmerFactory
from nltk.stem import PorterStemmer
from nltk import sent_tokenize, word_tokenize

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from collections import Counter

import re
import os
import sys
import random
import plot
import summarize

import tfidfbackend_query as tfidf_backend
import booleanbackend_query as bool_backend
import summarize_file

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class TfIdfTableDialog(QDialog):
    def __init__(self, tabledata, parent=None):
        super(TfIdfTableDialog, self).__init__(parent)
        self.result = ""
        mainLayout = QVBoxLayout()

        self.table = QTableView()

        self.model = TableModel(tabledata)
        self.table.setModel(self.model)

        self.btnJalankan = QPushButton("OK")
        self.btnJalankan.clicked.connect(self.OnOk)

        mainLayout.addWidget(self.table)
        mainLayout.addWidget(self.btnJalankan)

        self.setLayout(mainLayout)

    def OnOk(self):
        self.close()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mainlayout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.resize(300,200)
        self.tabs.addTab(self.tab1, "Membuat Summary")
        self.tabs.addTab(self.tab2, "Mesin Pencari")

        self.init_search_engine_tab()
        self.init_summarization_tab()

        self.mainlayout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(self.mainlayout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

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

    def init_search_engine_tab(self):
        self.document_list = []
        self.dictfile = ''
        self.currentAlgorithm = 1

        h_layout_main = QHBoxLayout()

        v_layout_left = QVBoxLayout()
        v_layout_center = QVBoxLayout()
        v_layout_right = QVBoxLayout()

        h_layout_left_top = QHBoxLayout()
        h_layout_left_center = QHBoxLayout()
        h_layout_left_bottom = QHBoxLayout()

        h_layout_center_top = QHBoxLayout()
        h_layout_center_center = QHBoxLayout()
        h_layout_center_bottom = QHBoxLayout()

        h_layout_right_top = QHBoxLayout()
        h_layout_right_center = QHBoxLayout()
        h_layout_right_bottom = QHBoxLayout()

        #LEFT
        self.openmultifilebutton = QPushButton('Pilih Beberapa Dokumen')
        self.opendirectorybutton = QPushButton('Pilih Direktori')
        h_layout_left_top.addWidget(self.openmultifilebutton)
        h_layout_left_top.addWidget(self.opendirectorybutton)
        self.listfilesdir = QListWidget()
        h_layout_left_center.addWidget(self.listfilesdir)
        self.opendirfilebutton = QPushButton('Buka File')
        self.cleardirfilebutton = QPushButton('Kosongkan List')
        h_layout_left_bottom.addWidget(self.opendirfilebutton)
        h_layout_left_bottom.addWidget(self.cleardirfilebutton)

        self.openmultifilebutton.clicked.connect(self.multiple_file_open)
        self.opendirectorybutton.clicked.connect(self.directory_open)

        self.opendirfilebutton.clicked.connect(self.open_file_with_default_program)
        self.cleardirfilebutton.clicked.connect(self.clear_file_lists)

        #CENTER
        self.searchBox = QLineEdit()
        self.searchbutton = QPushButton('Cari')
        self.algoritmaComboBox = QComboBox()
        self.algoritmaComboBox.addItem('Algoritma TF-IDF')
        self.algoritmaComboBox.addItem('Algoritma Boolean')
        h_layout_center_top.addWidget(self.searchBox)
        h_layout_center_top.addWidget(self.searchbutton)
        h_layout_center_top.addWidget(self.algoritmaComboBox)
        self.listfilesresult = QListWidget()
        h_layout_center_center.addWidget(self.listfilesresult)
        self.selectdictfilebutton = QPushButton('Pilih File Dictionary')
        self.showtfidftablebuton = QPushButton('Lihat Tabel TF-IDF')
        h_layout_center_bottom.addWidget(self.selectdictfilebutton)
        # h_layout_center_bottom.addWidget(self.showtfidftablebuton)

        self.searchbutton.clicked.connect(self.search_term)
        self.algoritmaComboBox.currentIndexChanged.connect(self.algoritmaChanged)

        self.selectdictfilebutton.clicked.connect(self.dictfile_open)
        self.showtfidftablebuton.clicked.connect(self.show_tfidf_table)

        #RIGHT
        self.previewfilebox = QPlainTextEdit()
        h_layout_right_center.addWidget(self.previewfilebox)
        self.previewsummarybutton = QPushButton('Lihat Summary Hasil')
        h_layout_right_bottom.addWidget(self.previewsummarybutton)

        self.previewsummarybutton.clicked.connect(self.summarize_selection_result)

        v_layout_left.addLayout(h_layout_left_top)
        v_layout_left.addLayout(h_layout_left_center)
        v_layout_left.addLayout(h_layout_left_bottom)

        v_layout_center.addLayout(h_layout_center_top)
        v_layout_center.addLayout(h_layout_center_center)
        v_layout_center.addLayout(h_layout_center_bottom)

        v_layout_right.addLayout(h_layout_right_top)
        v_layout_right.addLayout(h_layout_right_center)
        v_layout_right.addLayout(h_layout_right_bottom)

        h_layout_main.addLayout(v_layout_left)
        h_layout_main.addLayout(v_layout_center)
        h_layout_main.addLayout(v_layout_right)

        self.tab2.setLayout(h_layout_main)

    def summarize_selection_result(self):
        print('Summary Hasil Lihat')
        selectedItem = self.listfilesresult.currentItem()
        if(selectedItem):
            if(self.dictfile):
                selectedItem = selectedItem.text()
                selectedItem = selectedItem.split(",")[0]
                summary = summarize_file.summary_file(selectedItem,self.dictfile)
                self.previewfilebox.setPlainText(summary)
            else:
                self.dialog_critical("Belum ada kamus yang digunakan !")
        else:
            self.dialog_critical("Tidak ada hasil yang dipilih !")

    def show_tfidf_table(self):
        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]
        dlg = TfIdfTableDialog(data)
        dlg.exec_()

    def dictfile_open(self):
        # Membuka file txt kamus
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt)")

        # Memvalidasi data kemudian melakukan pembacaan data file txt
        if path:
            self.dictfile = path

    def algoritmaChanged(self, i):
        self.currentAlgorithm = i+1
        print('self.currentAlgorithm',self.currentAlgorithm)

    def search_term(self):
        term_dicari = self.searchBox.text()
        print(term_dicari)
        if(term_dicari and len(self.document_list) and self.dictfile):
            if(self.currentAlgorithm==1):
                print('tf idf')
                dictrank = tfidf_backend.search_tf_idf(term_dicari, self.document_list, self.dictfile)
                print('dictrank',dictrank)
                self.listfilesresult.clear()
                for key, weight in dictrank.items():
                    print('key',key)
                    print('weight',weight)
                    self.listfilesresult.addItem(str(self.document_list[key])+", score : "+str(weight))
            elif(self.currentAlgorithm==2):
                file_result = bool_backend.search_boolean(term_dicari, self.document_list)
                self.listfilesresult.clear()
                for file in file_result:
                    self.listfilesresult.addItem(str(file))


        else:
            self.dialog_critical("Tidak ada file yang dapat dicari, atau file kamus belum dibuka !")


    def open_file_with_default_program(self):
        selectedItem = self.listfilesdir.currentItem()
        if(selectedItem):
            selectedItem = selectedItem.text()
            print('selectedItem',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def clear_file_lists(self):
        self.document_list = []
        self.listfilesdir.clear()

    def update_file_lists(self):
        for filedir in self.document_list:
            self.listfilesdir.addItem(filedir)

    def directory_open(self):
        path = QFileDialog.getExistingDirectory(self,"Select Directory")
        if(path):
            print('pathdir',path)
            for file in os.listdir(path):
                if file.endswith(".txt"):
                    print(os.path.join(path, file))
                    self.document_list.append(path+'/'+ file)
                elif file.endswith(".pdf"):
                    print(os.path.join(path, file))
                    self.document_list.append(path+'/'+ file)
                # elif file.endswith(".doc"):
                #     print(os.path.join(path, file))
                #     self.document_list.append(path+'/'+ file)
                # elif file.endswith(".docx"):
                #     print(os.path.join(path, file))
                #     self.document_list.append(path+'/'+ file)
            self.update_file_lists()


    def multiple_file_open(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open file", "", "Text documents (*.txt);PDF documents (*.pdf)")
        print('paths',paths)
        for path in paths:
            print('path', path)
            if path:
                self.document_list.append(path)
        self.update_file_lists()
                # try:
                #     print('opening file in path', path)
                #     with open(path, 'rt') as f:
                #         text = f.read()
                #         new_obj = {path:text}
                #         self.document_list.update(new_obj)
                #     print('doclist',self.document_list)
                #
                # except Exception as e:
                #     self.dialog_critical(str(e))
                #
                # else:
                #     self.path = path
                #
                #     # Menampilkan data teks ke widget editor -> QPlain
                #     self.editor.setPlainText(text)
                #     self.update_title()

    def init_summarization_tab(self):
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

        self.tab1.setLayout(h_layout)

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
        text = text.lower()
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        kalimat = removed_number.split('.')
        if(len(kalimat)==1):
            num_kalimat = 1
        else:
            num_kalimat = len(kalimat)-1
        splitted = removed_number.split()
        num_words = len(splitted)
        # splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCount.setText("Total Kata : " + str(num_words)+" Total Kalimat : "+str(num_kalimat))
        self.textFreq.setText("Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq)))

    def reCalculateResult(self):
        text = self.textResult.toPlainText()
        text = text.lower()
        removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
        kalimat = removed_number.split('.')
        if(len(kalimat)==1):
            num_kalimat = 1
        else:
            num_kalimat = len(kalimat)-1
        splitted = removed_number.split()
        num_words = len(splitted)
        # splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        self.textCountResult.setText("Total Kata : " + str(num_words)+" Total Kalimat : "+str(num_kalimat))
        self.textFreqResult.setText("Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq)))

    def stem_word(self):
        raw = self.textResult.toPlainText()
        # factory = StemmerFactory()
        stemmer = PorterStemmer()
        # stemmer = factory.create_stemmer()
        sentences = sent_tokenize(raw)
        print('sentences',sentences)
        stem_sentence = []
        for sent in sentences:
            print('sent',sent)
            words = word_tokenize(sent)
            for word in words:
                print('word',word)
                word = word.lower()
                stem_sentence.append(stemmer.stem(word))
                print('word stemmed',word)
                if(word!='.'):
                    stem_sentence.append(" ")
        stem_sentence = "".join(stem_sentence)
        print("STEMMING PORTER")
        # result = stemmer.stem(raw)
        self.textResult.setPlainText(stem_sentence)
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
        # remover = StopWordRemover(dictionary)
        print('try to remove stopword')
        self.textResult.setPlainText(self.remove_stopword_text(raw, dictionary))
        self.reCalculateResult()

    def remove_stopword_text(self, text, dictionary):
        """Remove stop words."""
        words = text.split(' ')
        print('word', words)
        print('dictionary',dictionary)
        stopped_words = []
        for word in words:
            cword = word.lower()
            print('cword',cword)
            if not dictionary.contains(cword):
                stopped_words.append(word)
        # stopped_words = [word for word in words if not dictionary.contains(word)]

        return ' '.join(stopped_words)

    def dict_open(self):
        # Membuka file txt kamus
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt)")

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
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt)")
        if path:
            try:
                with open(path, 'rt', encoding="utf8") as f:
                    text = f.read()
                text = text.lower()
                removed_number = re.sub("^\d+\s|[0-9]|\s\d+\s|\s\d+$", "", text)
                kalimat = removed_number.split('.')
                if(len(kalimat)==1):
                    num_kalimat = 1
                else:
                    num_kalimat = len(kalimat)-1
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
