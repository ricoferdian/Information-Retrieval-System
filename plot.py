from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from collections import Counter

import re

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