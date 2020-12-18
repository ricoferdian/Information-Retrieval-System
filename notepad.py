from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemover, StopWordRemoverFactory, ArrayDictionary
# from Sastrawi.Stemmer.StemmerFactory import Stemmer, StemmerFactory
from nltk.stem import PorterStemmer
from nltk import sent_tokenize, word_tokenize

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from collections import Counter

import pdfplumber

import re
import os
import sys
import random
import plot
import summarize
import imageio

import tfidfbackend_query as tfidf_backend
import booleanbackend_query as bool_backend
import summarize_file
import documentLoader as docloader
import featureExtractionBackend as extract_feature
import euclideanDistanceRank as euclidean_dist

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

class ShowFilePreprocessing(QDialog):
    def __init__(self, extracted_documents,dictfile, parent=None):
        super(ShowFilePreprocessing, self).__init__(parent)

        with open(dictfile, 'rt') as f:
            self.dictionary = f.read()

        self.mainLayout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tab = [0 for i in range(len(extracted_documents))]
        self.tabLayout = [0 for i in range(len(extracted_documents))]
        self.textLayout = [0 for i in range(len(extracted_documents))]
        self.textLeft = [0 for i in range(len(extracted_documents))]
        self.textCenter = [0 for i in range(len(extracted_documents))]
        self.textRight = [0 for i in range(len(extracted_documents))]
        self.btnLayout = [0 for i in range(len(extracted_documents))]
        self.btnJalankan = [0 for i in range(len(extracted_documents))]
        self.btnJalankanStem = [0 for i in range(len(extracted_documents))]
        self.textCount = [0 for i in range(len(extracted_documents))]
        self.textFreq = [0 for i in range(len(extracted_documents))]
        index = 0
        for filepath, document in extracted_documents.items():
            head, tail = os.path.split(filepath)
            self.tab[index] = QWidget()

            self.tabLayout[index] = QVBoxLayout()

            self.textLayout[index] = QHBoxLayout()
            self.btnLayout[index] = QHBoxLayout()

            self.textLeft[index] = QPlainTextEdit()
            self.textCenter[index] = QPlainTextEdit()

            self.textLayout[index].addWidget(self.textLeft[index])
            self.textLayout[index].addWidget(self.textCenter[index])

            self.textCount[index] = QLabel()
            self.textCount[index].setText("Jumlah kata dan token akan muncul disini")
            self.textCount[index].setFixedWidth(1000)
            self.textFreq[index] = QLabel()
            self.textFreq[index].setText("Frekuensi kata akan muncul disini")
            self.textFreq[index].setFixedWidth(1000)

            self.btnJalankan[index] = QPushButton("Jalankan Preprocessing")
            self.btnJalankan[index].clicked.connect(self.processDocument)

            self.btnJalankanStem[index] = QPushButton("Jalankan Stemming")
            self.btnJalankanStem[index].clicked.connect(self.stemDocument)

            self.btnLayout[index].addWidget(self.btnJalankan[index])
            self.btnLayout[index].addWidget(self.btnJalankanStem[index])

            self.tabLayout[index].addLayout(self.textLayout[index])
            self.tabLayout[index].addLayout(self.btnLayout[index])
            self.tabLayout[index].addWidget(self.textCount[index])
            self.tabLayout[index].addWidget(self.textFreq[index])

            self.tab[index].setLayout(self.tabLayout[index])
            self.tabs.addTab(self.tab[index], str(tail))

            self.textLeft[index].setPlainText(document)

            index += 1

        self.tabs.resize(300,200)
        self.mainLayout.addWidget(self.tabs)
        self.setLayout(self.mainLayout)

    def remove_special_characters(self, text):
        regex = re.compile('[^a-zA-Z0-9\s]')
        text_returned = re.sub(regex, '', text)
        return text_returned

    def calculate(self, text):
        removed_number = text.lower()
        kalimat = sent_tokenize(removed_number)
        print("lenkalimat", kalimat)
        if(len(kalimat)==1):
            num_kalimat = 1
        else:
            num_kalimat = len(kalimat)-1
        splitted = removed_number.split()
        num_words = len(splitted)
        # splitted = re.findall(r'\w+', removed_number)
        freq = Counter(splitted)
        hitungKata = "Total Kata : " + str(num_words)
        hitungFrekuensi = "Frekuensi Kata : " + str(freq.most_common())+'\nJumlah kata :'+str(len(freq))
        return hitungKata,hitungFrekuensi

    def updateTextFreq(self, text, index):
        hitungKata, hitungFrekuensi = self.calculate(text)
        self.textCount[index].setText(hitungKata)
        self.textFreq[index].setText(hitungFrekuensi)

    def stem(self, raw):
        stemmer = PorterStemmer()
        sentences = sent_tokenize(raw)
        stem_sentence = []
        words = word_tokenize(raw)
        for word in words:
            print('word',word)
            word = word.lower()
            stem_sentence.append(stemmer.stem(word))
            print('word stemmed',word)
            if(word!='.'):
                stem_sentence.append(" ")
        stem_sentence = "".join(stem_sentence)
        return stem_sentence

    def preprocessDocument(self, text):
        text = self.remove_special_characters(text)
        text = self.remove_stopword(text)
        return text

    def stemDocument(self):
        index = self.tabs.currentIndex()
        text = self.textLeft[index].toPlainText()
        text = self.preprocessDocument(text)
        text = self.stem(text)
        self.updateTextFreq(text, index)
        self.textCenter[index].setPlainText(text)

    def processDocument(self):
        index = self.tabs.currentIndex()
        text = self.textLeft[index].toPlainText()
        text = self.preprocessDocument(text)
        self.updateTextFreq(text, index)
        self.textCenter[index].setPlainText(text)

    def remove_stopword(self, raw):
        # Data teks diambil dari widget
        dict = self.dictionary
        stop_factory = re.findall(r'\w+', dict)

        dictionary = ArrayDictionary(stop_factory)
        print('try to remove stopword')

        return self.remove_stopword_text(raw, dictionary)

    def remove_stopword_text(self, text, dictionary):
        words = word_tokenize(text)
        print('word', words)
        print('dictionary', dictionary)
        stopped_words = []
        for word in words:
            cword = word.lower()
            print('cword', cword)
            if not dictionary.contains(cword):
                stopped_words.append(word)
        return ' '.join(stopped_words)

    def OnOk(self):
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.mainlayout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tabs.resize(300,200)
        self.tabs.addTab(self.tab1, "Membuat Summary")
        self.tabs.addTab(self.tab2, "Mesin Pencari Dokumen Teks")
        self.tabs.addTab(self.tab3, "Mesin Pencari Citra Basis Teks")
        self.tabs.addTab(self.tab4, "Mesin Pencari Citra Basis Konten")

        self.init_search_engine_tab()
        self.init_summarization_tab()
        self.init_search_text_image_tab()
        self.init_search_content_image_tab()

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
        self.preloaded_documents = {}
        self.dictfile = ''
        self.currentAlgorithm = 1

        h_layout_main = QHBoxLayout()

        v_layout_left = QVBoxLayout()
        v_layout_center = QVBoxLayout()
        v_layout_right = QVBoxLayout()

        h_layout_left_top = QHBoxLayout()
        h_layout_left_center = QHBoxLayout()
        h_layout_left_bottom = QHBoxLayout()
        h_layout_left_bottom2 = QHBoxLayout()

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

        self.opentextfilebutton = QPushButton('Lihat Konten dan Preprocessing')
        h_layout_left_bottom2.addWidget(self.opentextfilebutton)

        self.openmultifilebutton.clicked.connect(self.multiple_file_open)
        self.opendirectorybutton.clicked.connect(self.directory_open)

        self.opendirfilebutton.clicked.connect(self.open_file_with_default_program)
        self.cleardirfilebutton.clicked.connect(self.clear_file_lists)
        self.opentextfilebutton.clicked.connect(self.showFileContent)

        #CENTER
        self.searchBox = QLineEdit()
        self.searchbutton = QPushButton('Cari')
        self.algoritmaComboBox = QComboBox()
        self.algoritmaComboBox.addItem('Algoritma TF-IDF')
        self.algoritmaComboBox.addItem('Algoritma Cosine Similarity (Vector Space Model)')
        self.algoritmaComboBox.addItem('Algoritma Dice Similarity (Vector Space Model)')
        self.algoritmaComboBox.addItem('Algoritma Boolean')
        h_layout_center_top.addWidget(self.searchBox)
        h_layout_center_top.addWidget(self.searchbutton)
        h_layout_center_top.addWidget(self.algoritmaComboBox)
        self.listfilesresult = QListWidget()
        self.listfilesresultpath = []
        h_layout_center_center.addWidget(self.listfilesresult)
        self.selectdictfilebutton = QPushButton('Pilih File Dictionary')
        self.openresultfilebutton = QPushButton('Buka File')
        self.showtfidftablebuton = QPushButton('Lihat Tabel TF-IDF')
        h_layout_center_bottom.addWidget(self.selectdictfilebutton)
        h_layout_center_bottom.addWidget(self.openresultfilebutton)
        # h_layout_center_bottom.addWidget(self.showtfidftablebuton)

        self.searchbutton.clicked.connect(self.search_term)
        self.algoritmaComboBox.currentIndexChanged.connect(self.algoritmaChanged)

        self.selectdictfilebutton.clicked.connect(self.dictfile_open)
        self.openresultfilebutton.clicked.connect(self.open_result_file_with_default_program)
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
        v_layout_left.addLayout(h_layout_left_bottom2)

        v_layout_center.addLayout(h_layout_center_top)
        v_layout_center.addLayout(h_layout_center_center)
        v_layout_center.addLayout(h_layout_center_bottom)

        v_layout_right.addLayout(h_layout_right_top)
        v_layout_right.addLayout(h_layout_right_center)
        v_layout_right.addLayout(h_layout_right_bottom)

        h_layout_main.addLayout(v_layout_left, stretch=20)
        h_layout_main.addLayout(v_layout_center, stretch=60)
        h_layout_main.addLayout(v_layout_right, stretch=20)

        self.tab2.setLayout(h_layout_main)

    def init_search_text_image_tab(self):
        self.document_list_tbir = []
        self.preloaded_documents_tbir = {}
        self.dictfile_tbir = ''
        # Main Layout tab 3 : text based image retrieval
        h_layout_main = QHBoxLayout()

        v_layout_left = QVBoxLayout()
        v_layout_center = QVBoxLayout()
        v_layout_right = QVBoxLayout()

        h_layout_left_top = QHBoxLayout()
        h_layout_left_center = QHBoxLayout()
        h_layout_left_bottom = QHBoxLayout()
        h_layout_left_bottom2 = QHBoxLayout()

        h_layout_center_top = QHBoxLayout()
        h_layout_center_center = QHBoxLayout()
        h_layout_center_bottom = QHBoxLayout()

        #LEFT
        self.openmultifilebutton_tbir = QPushButton('Pilih Beberapa Dokumen')
        self.opendirectorybutton_tbir = QPushButton('Pilih Direktori')
        h_layout_left_top.addWidget(self.openmultifilebutton_tbir)
        h_layout_left_top.addWidget(self.opendirectorybutton_tbir)
        self.listfilesdir_tbir = QListWidget()
        h_layout_left_center.addWidget(self.listfilesdir_tbir)
        self.opendirfilebutton_tbir = QPushButton('Buka File')
        self.cleardirfilebutton_tbir = QPushButton('Kosongkan List')
        h_layout_left_bottom.addWidget(self.opendirfilebutton_tbir)
        h_layout_left_bottom.addWidget(self.cleardirfilebutton_tbir)

        self.openmultifilebutton_tbir.clicked.connect(self.multiple_file_open_tbir)
        self.opendirectorybutton_tbir.clicked.connect(self.directory_open_tbir)

        self.opendirfilebutton_tbir.clicked.connect(self.open_file_with_default_program_tbir)
        self.cleardirfilebutton_tbir.clicked.connect(self.clear_file_lists_tbir)

        #CENTER
        self.searchBox_tbir = QLineEdit()
        self.searchbutton_tbir = QPushButton('Cari')
        h_layout_center_top.addWidget(self.searchBox_tbir)
        h_layout_center_top.addWidget(self.searchbutton_tbir)
        self.imageresultscroll_tbir = QScrollArea()
        self.imageresultscroll_tbir.setWidgetResizable(True)
        self.imageresultscrollcontent_tbir = QWidget()
        self.gridimageresult_tbir = QGridLayout(self.imageresultscrollcontent_tbir)
        self.imageresultscroll_tbir.setWidget(self.imageresultscrollcontent_tbir)
        self.imageresult_tbir = []
        self.listfilesresult_tbir = QListWidget()
        self.listfilesresultpath_tbir = []
        h_layout_center_center.addWidget(self.imageresultscroll_tbir)
        # h_layout_center_center.addWidget(self.listfilesresult_tbir)
        self.selectdictfilebutton_tbir = QPushButton('Pilih File Dictionary')
        self.openresultfilebutton_tbir = QPushButton('Buka File TBIR')
        h_layout_center_bottom.addWidget(self.selectdictfilebutton_tbir)
        h_layout_center_bottom.addWidget(self.openresultfilebutton_tbir)

        self.searchbutton_tbir.clicked.connect(self.search_term_tbir)

        self.selectdictfilebutton_tbir.clicked.connect(self.dictfile_open_tbir)
        self.openresultfilebutton_tbir.clicked.connect(self.open_result_file_with_default_program_tbir)

        v_layout_left.addLayout(h_layout_left_top)
        v_layout_left.addLayout(h_layout_left_center)
        v_layout_left.addLayout(h_layout_left_bottom)
        v_layout_left.addLayout(h_layout_left_bottom2)

        v_layout_center.addLayout(h_layout_center_top)
        v_layout_center.addLayout(h_layout_center_center)
        v_layout_center.addLayout(h_layout_center_bottom)

        h_layout_main.addLayout(v_layout_left, stretch=20)
        h_layout_main.addLayout(v_layout_center, stretch=80)
        
        # Set tab layout
        self.tab3.setLayout(h_layout_main)

    def init_search_content_image_tab(self):
        self.document_list_cbir = []
        self.preloaded_documents_cbir = {}
        self.queryimage_cbir = []

        # Main Layout tab 3 : text based image retrieval
        h_layout_main = QHBoxLayout()

        v_layout_left = QVBoxLayout()
        v_layout_center = QVBoxLayout()
        v_layout_right = QVBoxLayout()

        h_layout_left_top = QHBoxLayout()
        h_layout_left_center = QHBoxLayout()
        h_layout_left_bottom = QHBoxLayout()
        h_layout_left_bottom2 = QHBoxLayout()

        h_layout_center_top = QHBoxLayout()
        h_layout_center_center = QHBoxLayout()
        h_layout_center_bottom = QHBoxLayout()

        #LEFT
        self.openmultifilebutton_cbir = QPushButton('Pilih Beberapa Dokumen')
        self.opendirectorybutton_cbir = QPushButton('Pilih Direktori')
        h_layout_left_top.addWidget(self.openmultifilebutton_cbir)
        h_layout_left_top.addWidget(self.opendirectorybutton_cbir)
        self.listfilesdir_cbir = QListWidget()
        h_layout_left_center.addWidget(self.listfilesdir_cbir)
        self.opendirfilebutton_cbir = QPushButton('Buka File')
        self.cleardirfilebutton_cbir = QPushButton('Kosongkan List')
        h_layout_left_bottom.addWidget(self.opendirfilebutton_cbir)
        h_layout_left_bottom.addWidget(self.cleardirfilebutton_cbir)

        self.openmultifilebutton_cbir.clicked.connect(self.multiple_file_open_cbir)
        self.opendirectorybutton_cbir.clicked.connect(self.directory_open_cbir)

        self.opendirfilebutton_cbir.clicked.connect(self.open_file_with_default_program_cbir)
        self.cleardirfilebutton_cbir.clicked.connect(self.clear_file_lists_cbir)

        #CENTER
        self.imagepreview_cbir = QLabel()
        self.openimage_cbir = QPushButton('Buka File')
        self.searchbutton_cbir = QPushButton('Cari')
        h_layout_center_top.addWidget(self.imagepreview_cbir)
        h_layout_center_top.addWidget(self.openimage_cbir)
        h_layout_center_top.addWidget(self.searchbutton_cbir)
        self.imageresultscroll_cbir = QScrollArea()
        self.imageresultscroll_cbir.setWidgetResizable(True)
        self.imageresultscrollcontent_cbir = QWidget()
        self.gridimageresult_cbir = QGridLayout(self.imageresultscrollcontent_cbir)
        self.imageresultscroll_cbir.setWidget(self.imageresultscrollcontent_cbir)
        self.imageresult_cbir = []
        self.listfilesresult_cbir = QListWidget()
        self.listfilesresultpath_cbir = []
        h_layout_center_center.addWidget(self.imageresultscroll_cbir)
        # h_layout_center_center.addWidget(self.listfilesresult_tbir)
        self.openresultfilebutton_cbir = QPushButton('Buka File TBIR')
        h_layout_center_bottom.addWidget(self.openresultfilebutton_cbir)

        self.openimage_cbir.clicked.connect(self.image_query_open)
        self.searchbutton_cbir.clicked.connect(self.search_term_cbir)

        self.openresultfilebutton_cbir.clicked.connect(self.open_result_file_with_default_program_cbir)

        v_layout_left.addLayout(h_layout_left_top)
        v_layout_left.addLayout(h_layout_left_center)
        v_layout_left.addLayout(h_layout_left_bottom)
        v_layout_left.addLayout(h_layout_left_bottom2)

        v_layout_center.addLayout(h_layout_center_top)
        v_layout_center.addLayout(h_layout_center_center)
        v_layout_center.addLayout(h_layout_center_bottom)

        h_layout_main.addLayout(v_layout_left, stretch=20)
        h_layout_main.addLayout(v_layout_center, stretch=80)

        # Set tab layout
        self.tab4.setLayout(h_layout_main)

    def summarize_selection_result(self):
        print('Summary Hasil Lihat')
        selectedItem = self.listfilesresult.currentRow()
        if(selectedItem is not None and len(self.listfilesresultpath)-1>=selectedItem):
            if(self.dictfile):
                selectedItem = self.listfilesresultpath[selectedItem]
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

    def dictfile_open_tbir(self):
        # Membuka file txt kamus
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Text documents (*.txt)")

        # Memvalidasi data kemudian melakukan pembacaan data file txt
        if path:
            self.dictfile_tbir = path

    def algoritmaChanged(self, i):
        self.currentAlgorithm = i+1
        print('self.currentAlgorithm',self.currentAlgorithm)

    def preloadDocuments(self, document_list):
        for document in self.document_list:
            if document in self.preloaded_documents:
                print("self.preloaded_documents[document]", self.preloaded_documents[document])
                if self.preloaded_documents[document] is None:
                    print("NOT PRELOADED. PRELOADING...")
                    self.preloaded_documents[document] = docloader.loadDocuments(document)
                else:
                    print("ALREADY PRELOADED. SKIPPING...")

    def preloadDocuments_tbir(self, document_list_tbir):
        print("self.document_list_tbir",self.document_list_tbir)
        for document in self.document_list_tbir:
            print("self.preloaded_documents_tbir",self.preloaded_documents_tbir)
            if document in self.preloaded_documents_tbir:
                print("self.preloaded_documents[document]", self.preloaded_documents_tbir[document])
                if self.preloaded_documents_tbir[document] is None:
                    print("NOT PRELOADED. PRELOADING...")
                    file_without_extension = os.path.splitext(document)[0]
                    descfname = file_without_extension +'.txt'
                    if os.path.isfile(descfname):
                        self.preloaded_documents_tbir[document] = docloader.loadDocuments(descfname)
                else:
                    print("ALREADY PRELOADED. SKIPPING...")
                print("self.preloaded_documents_tbir",self.preloaded_documents_tbir)

    def preloadDocuments_cbir(self, document_list_cbir):
        for document in self.document_list_cbir:
            if document in self.preloaded_documents_cbir:
                print("self.preloaded_documents[document]", self.preloaded_documents_cbir[document])
                if self.preloaded_documents_cbir[document] is None:
                    print("NOT PRELOADED. PRELOADING...")
                    # Langsung preload
                    # self.preloaded_documents_cbir[document] = docloader.loadImages(document)

                    # Preload dengan ekstarksi fitur, dan fiturnya disimpan
                    image = docloader.loadImages(document)
                    feature = extract_feature.extract_features(image)
                    self.preloaded_documents_cbir[document] = feature
                else:
                    print("ALREADY PRELOADED. SKIPPING...")
                print("self.preloaded_documents_cbir",self.preloaded_documents_cbir)

    def image_query_open(self):
        global screenWidth
        global screenHeight

        path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "Images (*.bmp *.jpg *.png);")
        if path:
            try:
                wlabel, hlabel = 200, 200

                realpixmap = QPixmap(path)
                self.queryimage_cbir = imageio.imread(path).astype('uint8')
                self.imagepreview_cbir.setPixmap(realpixmap.scaled(wlabel,hlabel,Qt.KeepAspectRatio))
            except Exception as e:
                self.dialog_critical(str(e))
            else:
                self.path = path
                self.update_title()

    def search_term_tbir(self):
        global screenWidth
        global screenHeight

        print("screenWidth",screenWidth)
        print("screenHeight",screenHeight)
        print("TBIR")
        term_dicari = self.searchBox_tbir.text()
        print(term_dicari)
        if(term_dicari and len(self.document_list_tbir) and self.dictfile_tbir):
            print('mencarih kwwkkwwkwkwkwk')
            self.preloadDocuments_tbir(self.document_list_tbir)

            print('vsm cosine similarity')
            dictrank, found_sentences, fit_queries = tfidf_backend.search_tf_idf_preloaded(term_dicari.lower(),
                                                                                           self.preloaded_documents_tbir,
                                                                                           self.dictfile_tbir, None, True)
            print('dictrank', dictrank)
            self.listfilesresult_tbir.clear()

            print("self.imageresult_tbir",self.imageresult_tbir)
            for imagewidget in self.imageresult_tbir:
                print("imagewidget",imagewidget)
                self.gridimageresult_tbir.removeWidget(imagewidget)
                imagewidget.deleteLater()
                imagewidget = None

            self.imageresult_tbir = [0 for i in range(len(dictrank))]

            print("self.imageresult_tbir",self.imageresult_tbir)

            idx = 0

            iidx = 0
            jidx = 0
            self.listfilesresultpath_tbir = []
            for key, weight in dictrank.items():
                print('key', key)
                print('weight', weight)
                head, tail = os.path.split(self.document_list_tbir[key])

                self.imageresult_tbir[idx] = QLabel()

                wlabel, hlabel = int(screenWidth * 0.2),int(screenHeight * 0.2)

                realpixmap = QPixmap(self.document_list_tbir[key])
                self.imageresult_tbir[idx].setPixmap(realpixmap.scaled(wlabel,hlabel,Qt.KeepAspectRatio))

                self.gridimageresult_tbir.addWidget(self.imageresult_tbir[idx],iidx,jidx)

                # self.listfilesresult_tbir.addItem(
                #     str(tail) + found_sentences[key] + "\nQuery ditemukan : " + fit_queries[key] + "\nPath : " + str(
                #         self.document_list_tbir[key]) + "\nScore : " + str(weight))
                self.listfilesresultpath_tbir.append(self.document_list_tbir[key])

                if idx % 10 is 0:
                    jidx += 1
                    iidx = 0
                else:
                    iidx += 1
                idx += 1
            print("self.listfilesresultpath_tbir",self.listfilesresultpath_tbir)
        else:
            self.dialog_critical("Tidak ada file yang dapat dicari, atau file kamus belum dibuka !")

    def search_term_cbir(self):
        global screenWidth
        global screenHeight

        print("screenWidth",screenWidth)
        print("screenHeight",screenHeight)
        print("CBIR")

        term_dicari = self.queryimage_cbir
        print(term_dicari)
        if(term_dicari is not None and len(self.document_list_cbir)):
            print('mencarih MENGGUNAKAN CBIR')
            self.preloadDocuments_cbir(self.document_list_cbir)

            query_feature = extract_feature.extract_features(term_dicari)

            dictrank = euclidean_dist.euclideanDistance(query_feature,self.preloaded_documents_cbir)
            print('dictrank', dictrank)
            self.listfilesresult_tbir.clear()

            print("self.imageresult_tbir", self.imageresult_cbir)
            for imagewidget in self.imageresult_cbir:
                print("imagewidget", imagewidget)
                self.gridimageresult_cbir.removeWidget(imagewidget)
                imagewidget.deleteLater()
                imagewidget = None

            self.imageresult_cbir = [0 for i in range(len(dictrank))]

            print("self.imageresult_tbir", self.imageresult_cbir)

            idx = 0

            iidx = 0
            jidx = 0
            self.listfilesresultpath_cbir = []
            for key, weight in dictrank.items():
                print('key', key)
                print('distance', weight)
                head, tail = os.path.split(self.document_list_cbir[key])

                self.imageresult_cbir[idx] = QLabel()

                wlabel, hlabel = int(screenWidth * 0.2), int(screenHeight * 0.2)

                realpixmap = QPixmap(self.document_list_cbir[key])
                self.imageresult_cbir[idx].setPixmap(realpixmap.scaled(wlabel, hlabel, Qt.KeepAspectRatio))

                self.gridimageresult_cbir.addWidget(self.imageresult_cbir[idx], iidx, jidx)

                # self.listfilesresult_tbir.addItem(
                #     str(tail) + found_sentences[key] + "\nQuery ditemukan : " + fit_queries[key] + "\nPath : " + str(
                #         self.document_list_tbir[key]) + "\nScore : " + str(weight))
                self.listfilesresultpath_cbir.append(self.document_list_cbir[key])

                if idx % 10 is 0:
                    jidx += 1
                    iidx = 0
                else:
                    iidx += 1
                idx += 1
            print("self.listfilesresultpath_tbir", self.listfilesresultpath_tbir)
        else:
            self.dialog_critical("Tidak ada file yang dapat dicari !")

    def search_term(self):
        term_dicari = self.searchBox.text()
        print(term_dicari)
        if(term_dicari and len(self.document_list) and self.dictfile):
            self.preloadDocuments(self.document_list)
            if(self.currentAlgorithm==1):
                print('tf idf')
                dictrank, found_sentences, fit_queries = tfidf_backend.search_tf_idf_preloaded(term_dicari, self.preloaded_documents, self.dictfile, None)
                print('dictrank',dictrank)
                self.listfilesresult.clear()
                self.listfilesresultpath = []
                self.listfilesresult.setSpacing(5)
                for key, weight in dictrank.items():
                    print('key',key)
                    print('weight',weight)
                    head, tail = os.path.split(self.document_list[key])
                    self.listfilesresult.addItem(str(tail)+found_sentences[key]+"\nQuery ditemukan : "+fit_queries[key]+"\nPath : "+str(self.document_list[key])+"\nScore : "+str(weight))
                    self.listfilesresultpath.append(self.document_list[key])
            elif(self.currentAlgorithm==2):
                print('vsm cosine similarity')
                dictrank, found_sentences, fit_queries = tfidf_backend.search_tf_idf_preloaded(term_dicari, self.preloaded_documents, self.dictfile, 'cosine')
                print('dictrank',dictrank)
                self.listfilesresult.clear()
                self.listfilesresultpath = []
                for key, weight in dictrank.items():
                    print('key',key)
                    print('weight',weight)
                    head, tail = os.path.split(self.document_list[key])
                    self.listfilesresult.addItem(str(tail)+found_sentences[key]+"\nQuery ditemukan : "+fit_queries[key]+"\nPath : "+str(self.document_list[key])+"\nScore : "+str(weight))
                    self.listfilesresultpath.append(self.document_list[key])
            elif(self.currentAlgorithm==3):
                print('vsm cosine similarity')
                dictrank, found_sentences, fit_queries = tfidf_backend.search_tf_idf_preloaded(term_dicari, self.preloaded_documents, self.dictfile, 'dice')
                print('dictrank',dictrank)
                self.listfilesresult.clear()
                self.listfilesresultpath = []
                for key, weight in dictrank.items():
                    print('key',key)
                    print('weight',weight)
                    head, tail = os.path.split(self.document_list[key])
                    self.listfilesresult.addItem(str(tail)+found_sentences[key]+"\nQuery ditemukan : "+fit_queries[key]+"\nPath : "+str(self.document_list[key])+"\nScore : "+str(weight))
                    self.listfilesresultpath.append(self.document_list[key])
            elif(self.currentAlgorithm==4):
                file_result, found_sentences = bool_backend.search_boolean(term_dicari, self.preloaded_documents)
                self.listfilesresult.clear()
                self.listfilesresultpath = []
                for file in file_result:
                    head, tail = os.path.split(file)
                    self.listfilesresult.addItem(str(tail)+found_sentences[file]+"\nPath : "+str(file))
                    self.listfilesresultpath.append(file)
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

    def open_file_with_default_program_tbir(self):
        selectedItem = self.listfilesdir_tbir.currentItem()
        if(selectedItem):
            selectedItem = selectedItem.text()
            print('selectedItem',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def open_file_with_default_program_cbir(self):
        selectedItem = self.listfilesdir_cbir.currentItem()
        if(selectedItem):
            selectedItem = selectedItem.text()
            print('selectedItem',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def showFileContent(self):
        if (len(self.document_list) and self.dictfile):
            self.preloadDocuments(self.document_list)
            dlg = ShowFilePreprocessing(self.preloaded_documents, self.dictfile)
            if dlg.exec_():
                print("Success exec")
        else:
            self.dialog_critical("Tidak ada file yang dapat dicari, atau file kamus belum dibuka !")

    # def showFileContent_tbir(self):
    #     if (len(self.document_list_tbir) and self.dictfile_tbir):
    #         self.preloadDocuments_tbir(self.document_list_tbir)
    #         dlg = ShowFilePreprocessing(self.preloaded_documents_tbir, self.dictfile_tbir)
    #         if dlg.exec_():
    #             print("Success exec")
    #     else:
    #         self.dialog_critical("Tidak ada file yang dapat dicari, atau file kamus belum dibuka !")
    #
    # def showFileContent_cbir(self):
    #     if (len(self.document_list_cbir) and self.dictfile_cbir):
    #         self.preloadDocuments_cbir(self.document_list_cbir)
    #         dlg = ShowFilePreprocessing(self.preloaded_documents_cbir, self.dictfile_cbir)
    #         if dlg.exec_():
    #             print("Success exec")
    #     else:
    #         self.dialog_critical("Tidak ada file yang dapat dicari, atau file kamus belum dibuka !")

    def open_result_file_with_default_program(self):
        selectedItem = self.listfilesresult.currentRow()
        print('selectedItem_default',selectedItem)
        print('self.listfilesresultpath',self.listfilesresultpath)
        print('len(self.listfilesresultpath)',len(self.listfilesresultpath))
        if(selectedItem is not None and len(self.listfilesresultpath)-1>=selectedItem):
            selectedItem = self.listfilesresultpath[selectedItem]
            print('selectedItem',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def open_result_file_with_default_program_tbir(self):
        selectedItem = self.listfilesresult_tbir.currentRow()
        print('selectedItem_tbir',selectedItem)
        print('self.listfilesresultpath_tbir',self.listfilesresultpath_tbir)
        print('len(self.listfilesresultpath_tbir)',len(self.listfilesresultpath_tbir))
        if(selectedItem is not None and len(self.listfilesresultpath_tbir)-1>=selectedItem):
            selectedItem = self.listfilesresultpath_tbir[selectedItem]
            print('selectedItem_tbir',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def open_result_file_with_default_program_cbir(self):
        selectedItem = self.listfilesresult_cbir.currentRow()
        print('selectedItemteeeess',selectedItem)
        print('self.listfilesresultpath',self.listfilesresultpath_cbir)
        print('len(self.listfilesresultpath)',len(self.listfilesresultpath_cbir))
        if(selectedItem is not None and len(self.listfilesresultpath_cbir)-1>=selectedItem):
            selectedItem = self.listfilesresultpath_cbir[selectedItem]
            print('selectedItem',selectedItem)
            os.startfile(selectedItem)
        else:
            self.dialog_critical("Tidak ada file dipilih !")

    def clear_file_lists(self):
        self.document_list = []
        self.preloaded_documents = {}
        self.listfilesdir.clear()

    def clear_file_lists_tbir(self):
        self.document_list_tbir = []
        self.preloaded_documents_tbir = {}
        self.listfilesdir_tbir.clear()

    def clear_file_lists_cbir(self):
        self.document_list_cbir = []
        self.preloaded_documents_cbir = {}
        self.listfilesdir_cbir.clear()

    def update_file_lists(self):
        self.listfilesdir.clear()
        for filedir in self.document_list:
            self.listfilesdir.addItem(filedir)

    def update_file_lists_tbir(self):
        self.listfilesdir_tbir.clear()
        for filedir in self.document_list_tbir:
            self.listfilesdir_tbir.addItem(filedir.splitlines()[0])

    def update_file_lists_cbir(self):
        self.listfilesdir_cbir.clear()
        for filedir in self.document_list_cbir:
            self.listfilesdir_cbir.addItem(filedir.splitlines()[0])

    def directory_open(self):
        path = QFileDialog.getExistingDirectory(self,"Select Directory")
        if(path):
            print('pathdir',path)
            for file in os.listdir(path):
                if file.endswith(".txt"):
                    print(os.path.join(path, file))
                    self.document_list.append(path+'/'+ file)
                    self.preloaded_documents[path+'/'+ file] = None
                elif file.endswith(".pdf"):
                    print(os.path.join(path, file))
                    self.document_list.append(path+'/'+ file)
                    self.preloaded_documents[path+'/'+ file] = None
            self.update_file_lists()

    def directory_open_tbir(self):
        path = QFileDialog.getExistingDirectory(self,"Select Directory")
        if(path):
            print('pathdir',path)
            for file in os.listdir(path):
                if file.endswith(".jpg"):
                    file_without_extension = os.path.splitext(file)[0]
                    descfname = path+'/'+ file_without_extension +'.txt'
                    if os.path.isfile(descfname):
                        self.preloaded_documents_tbir[path+'/'+ file] = None
                        self.document_list_tbir.append(path+'/'+ file)
                    print(os.path.join(path, file))
                    print(descfname)
                elif file.endswith(".png"):
                    file_without_extension = os.path.splitext(file)[0]
                    descfname = path+'/'+ file_without_extension +'.txt'
                    if os.path.isfile(descfname):
                        self.preloaded_documents_tbir[path+'/'+ file] = None
                        self.document_list_tbir.append(path+'/'+ file)
                    print(os.path.join(path, file))
                    print(descfname)
                elif file.endswith(".bmp"):
                    file_without_extension = os.path.splitext(file)[0]
                    descfname = path+'/'+ file_without_extension +'.txt'
                    if os.path.isfile(descfname):
                        self.preloaded_documents_tbir[path+'/'+ file] = None
                        self.document_list_tbir.append(path+'/'+ file)
                    print(os.path.join(path, file))
                    print(descfname)
            self.update_file_lists_tbir()

    def directory_open_cbir(self):
        path = QFileDialog.getExistingDirectory(self,"Select Directory")
        if(path):
            print('pathdir',path)
            for file in os.listdir(path):
                if file.endswith(".jpg"):
                    self.preloaded_documents_cbir[path+'/'+ file] = None
                    self.document_list_cbir.append(path+'/'+ file)
                elif file.endswith(".png"):
                    self.preloaded_documents_cbir[path+'/'+ file] = None
                    self.document_list_cbir.append(path+'/'+ file)
                elif file.endswith(".bmp"):
                    self.preloaded_documents_cbir[path+'/'+ file] = None
                    self.document_list_cbir.append(path+'/'+ file)
            self.update_file_lists_cbir()

    def multiple_file_open(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open file", "", "Text documents (*.txt);PDF documents (*.pdf)")
        print('paths',paths)
        for path in paths:
            print('path', path)
            if path:
                self.document_list.append(path)
                self.preloaded_documents[path] = None
        self.update_file_lists()

    def multiple_file_open_tbir(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open file", "",
                                                "Images (*.bmp *.jpg *.png);")
        print('paths', paths)
        for path in paths:
            print('path', path)
            if path:
                file_without_extension = os.path.splitext(path)[0]
                descfname = file_without_extension +'.txt'
                if os.path.isfile(descfname):
                    self.document_list_tbir.append(path)
                    self.preloaded_documents_tbir[path] = None
        self.update_file_lists_tbir()

    def multiple_file_open_cbir(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Open file", "",
                                                "Images (*.bmp *.jpg *.png);")
        print('paths', paths)
        for path in paths:
            print('path', path)
            if path:
                self.document_list_cbir.append(path)
                self.preloaded_documents_cbir[path] = None
        self.update_file_lists_cbir()

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

        self.allresulttextwindow = summarize.SummarizeWindow(self)

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
                if path.lower().endswith('.txt'):
                    print('opening text file txt')
                    try:
                        with open(path, 'rt', encoding="utf8") as f:
                            print('reading file')
                            text = f.read()
                    except Exception as e:
                        self.dialog_critical(str(e))
                    else:
                        print('nggak mau wkwkwkwkwk')
                elif (path.lower().endswith('.pdf')):
                    print('pdf', path)
                    try:
                        with pdfplumber.open(path) as pdf:
                            total_pages = len(pdf.pages)
                            text = ''
                            for page in range(total_pages):
                                print('extracting pdf page ', page)
                                loaded_page = pdf.pages[page]
                                text += loaded_page.extract_text()
                    except Exception as e:
                        self.dialog_critical(str(e))
                    else:
                        print('nggak mau wkwkwkwkwk')
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
    global screenWidth
    global screenHeight

    app = QApplication(sys.argv)
    app.setApplicationName("Sistem Temu Kembali Informasi")

    screen = app.primaryScreen()
    size = screen.size()

    screenWidth = size.width()
    screenHeight = size.height()

    window = MainWindow()
    app.exec_()
