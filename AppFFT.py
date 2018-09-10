from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QApplication, QFileDialog, QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap
from numpy.fft import fft2, fftshift
from numpy import log, array, pi, exp, zeros, dot
#from matplotlib.pyplot import imread, imsave
from os import path
###PyQImageViewer
from PyQt5.QtCore import Qt, QT_VERSION_STR, QAbstractListModel, QVariant
from PyQt5.QtGui import QImage, QPainter
from QtImageViewer import QtImageViewer
#####3
from PyQt5 import QtCore, QtGui, QtWidgets
from qimage2ndarray import imsave, imread, gray2qimage
import webbrowser as wb

class image(object):
    dist = 0
    X=-1
    Y=-1

    def __init__(self, raw_data=zeros((2048,2048)), name='', sign='+', averagable=True, fft=None):
        nn = 2048
        l = 0.633
        mesh = 3.45
        self.k = 2 * pi / l

        if len(raw_data.shape) == 2:
            self.data = raw_data
        elif self.data.shape[2] == 3:
            print("converting from RGB to greyscale")
            self.data = dot(self.data[..., :3], [0.299, 0.587, 0.114])

        self.x = self.data.shape[0]
        self.y = self.data.shape[1]
        if image.X > 0 and image.Y > 0:
            if self.x != image.X or self.y != image.Y:
                raise ValueError("Images shapes do not match")
        else:
            image.X = self.x
            image.Y = self.y

        kmesh_x = 2 * pi / mesh / self.x
        kmesh_y = 2 * pi / mesh / self.y

        kx = array([i * kmesh_y for i in range(1, self.y + 1)])
        ky = array([kmesh_x for i in range(1, self.y + 1)])

        self.kkx = array([kx for i in range(1, self.x + 1)]) - (self.x + 1) / 2 * kmesh_x
        self.kky = array([ky * i for i in range(1, self.x + 1)]) - (self.y + 1) / 2 * kmesh_y

        self.sign = sign
        self.name = name.strip('.bmp')
        self.parsed_data = fft
        self.averagable = averagable

    def fft(self):
        data = self.data * exp(1j * (self.k ** 2 - self.kkx ** 2 - self.kky ** 2) ** (0.5 * image.dist))
        self.parsed_data = log(abs(fftshift(fft2(data))))
        return self.parsed_data

    def add(self, n=1):
        if self.sign == '+':
            return self.parsed_data/n
        return -self.parsed_data

    def save(self, name=None):
        if not name:
            name = self.name
        if not self.parsed_data is None:
            print("save"+name)
            imsave(name+'.png', self.parsed_data, normalize=True, format='PNG')
        else:
            print("brak transformaty")

    def ffted(self):
        if self.parsed_data is None:
            return False
        return True

    def __str__(self):
        printable = self.sign + ' ' + path.basename(self.name)
        if self.parsed_data is None:
            return printable  + ' *'
        return printable

class imagelist(QAbstractListModel):
    def __init__(self, parent=None):
        super(imagelist, self).__init__(parent)
        self.container = []
        self.last_selected = 0

    def empty(self):
        end = len(self.container) - 1
        self.container = []
        self.rowsInserted.emit(QtCore.QModelIndex(), 0, end)
        image.X = -1
        image.Y = -1

    def data(self, i, role=QtCore.Qt.DisplayRole):
        if i.row() < len(self.container):
            if role == QtCore.Qt.DisplayRole:
                return QVariant(str(self.container[i.row()]))
            if role == QtCore.Qt.EditRole:
                return QVariant(self.container[i.row()].name)
        return QVariant()

    def get_by_index(self, i):
        if i.row() < len(self.container):
            return self.container[i.row()]
        return None

    def rowCount(self, parent=None):
        return len(self.container)

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.container[index.row()].name = value
            self.dataChanged.emit(index, index, [])
            return True
        return False

    def insertRows(self, data, count=None, parent=None):
        self.container.append(data)
        self.rowsInserted.emit(QtCore.QModelIndex(), len(self.container) - 1, len(self.container) - 1)

    def get_raw(self, i, role=None):
        return gray2qimage(self.container[i.row()].data)

    def get_fft(self, i, role=None):
        pdata = self.container[i.row()].parsed_data
        if pdata is None:
            return QImage()
        return gray2qimage(pdata, normalize=True)

    def fft_all(self):
        for i in self.container:
            if i.sign != '=':
                i.fft()

    def save_all(self):
        for i in self.container:
            i.save()

    def average(self):
        avg = zeros((image.X, image.Y))
        pluses = sum([1 for i in self.container if i.sign == '+' and i.averagable])
        minuses = sum([1 for i in self.container if i.sign == '-' and i.averagable])
        for i in self.container:
            if not i.averagable:
                continue
            i.fft()
            if i.sign == '+':
                avg += i.add(pluses)
            else:
                avg += i.add(minuses)
        self.insertRows(image(fft=avg, averagable=False, name=path.dirname(self.container[-1].name) + '/average', sign='='),count=None, parent=None)

class Ui_AppFFT(QtWidgets.QMainWindow):
    def setupUi(self, AppFFT):
        AppFFT.setObjectName("AppFFT")
        AppFFT.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("logoUJ.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AppFFT.setWindowIcon(icon)
        AppFFT.setIconSize(QtCore.QSize(30, 30))
        self.centralwidget = QtWidgets.QWidget(AppFFT)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setContentsMargins(-1, 30, -1, 30)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.AddButton = QtWidgets.QPushButton(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.AddButton.setFont(font)
        self.AddButton.setObjectName("AddButton")
        self.verticalLayout_7.addWidget(self.AddButton, 0, QtCore.Qt.AlignHCenter)
        self.SubstractButton = QtWidgets.QPushButton(self.groupBox_2)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.SubstractButton.setFont(font)
        self.SubstractButton.setObjectName("SubstractButton")
        self.verticalLayout_7.addWidget(self.SubstractButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.AverageButton = QtWidgets.QPushButton(self.groupBox_2)
        self.AverageButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.AverageButton.setFont(font)
        self.AverageButton.setObjectName("AverageButton")
        self.verticalLayout_7.addWidget(self.AverageButton, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setInputMethodHints(QtCore.Qt.ImhNone)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.FFTSingleButton = QtWidgets.QPushButton(self.groupBox)
        self.FFTSingleButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.FFTSingleButton.setFont(font)
        self.FFTSingleButton.setObjectName("FFTSingleButton")
        self.verticalLayout_6.addWidget(self.FFTSingleButton)
        self.FFTSeriesButton = QtWidgets.QPushButton(self.groupBox)
        self.FFTSeriesButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.FFTSeriesButton.setFont(font)
        self.FFTSeriesButton.setObjectName("FFTSeriesButton")
        self.verticalLayout_6.addWidget(self.FFTSeriesButton)
        self.FFTSaveSeriesButton = QtWidgets.QPushButton(self.groupBox)
        self.FFTSaveSeriesButton.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.FFTSaveSeriesButton.setFont(font)
        self.FFTSaveSeriesButton.setObjectName("FFTSaveSeriesButton")
        self.verticalLayout_6.addWidget(self.FFTSaveSeriesButton)
        self.horizontalLayout.addWidget(self.groupBox)
        self.gridLayout_6.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.ResetButton = QtWidgets.QPushButton(self.groupBox_3)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.ResetButton.setFont(font)
        self.ResetButton.setObjectName("ResetButton")
        self.gridLayout_4.addWidget(self.ResetButton, 2, 0, 1, 1)
        self.listView = QtWidgets.QListView(self.groupBox_3)
        self.listView.setObjectName("listView")
        self.gridLayout_4.addWidget(self.listView, 0, 0, 1, 1, QtCore.Qt.AlignHCenter)
        self.verticalLayout_5.addWidget(self.groupBox_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label, 0, QtCore.Qt.AlignRight)
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox.setMinimumSize(QtCore.QSize(110, 30))
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.doubleSpinBox.setFont(font)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout_5.addWidget(self.doubleSpinBox, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.verticalLayout_5.addLayout(self.horizontalLayout_5)
        self.SaveButton = QtWidgets.QPushButton(self.centralwidget)
        self.SaveButton.setEnabled(False)
        self.SaveButton.setDefault(False)
        self.SaveButton.setFlat(False)
        self.SaveButton.setObjectName("SaveButton")
        self.verticalLayout_5.addWidget(self.SaveButton, 0, QtCore.Qt.AlignHCenter)
        self.gridLayout_6.addLayout(self.verticalLayout_5, 2, 0, 1, 1)
        self.gridLayout_7 = QtWidgets.QGridLayout()
        self.gridLayout_7.setContentsMargins(80, -1, 80, -1)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.HelpButton = QtWidgets.QPushButton(self.centralwidget)
        self.HelpButton.setMouseTracking(False)
        self.HelpButton.setAccessibleDescription("")
        self.HelpButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.HelpButton.setAutoFillBackground(False)
        self.HelpButton.setInputMethodHints(QtCore.Qt.ImhNone)
        self.HelpButton.setIconSize(QtCore.QSize(20, 20))
        self.HelpButton.setAutoRepeatDelay(300)
        self.HelpButton.setAutoDefault(False)
        self.HelpButton.setObjectName("HelpButton")
        self.gridLayout_7.addWidget(self.HelpButton, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_7, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout_6, 0, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.tabWidget.setFont(font)
        self.tabWidget.setInputMethodHints(QtCore.Qt.ImhNone)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.graphicsViewUp = QtImageViewer()
        self.graphicsViewUp.setObjectName("graphicsViewUp")
        self.graphicsViewUp.setMouseTracking(True)
        self.graphicsViewUp.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.gridLayout_3.addWidget(self.graphicsViewUp, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.graphicsViewDw = QtImageViewer()
        self.graphicsViewDw.setObjectName("graphicsViewDw")
        self.gridLayout_2.addWidget(self.graphicsViewDw, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.gridLayout_5.addLayout(self.gridLayout, 0, 1, 1, 1)
        AppFFT.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(AppFFT)
        self.statusbar.setObjectName("statusbar")
        AppFFT.setStatusBar(self.statusbar)
        ####
        self.HelpButton.clicked.connect(self.click_Help)
        self.FFTSingleButton.clicked.connect(self.click_FFT_single)
        self.FFTSeriesButton.clicked.connect(self.click_FFT_series)
        self.FFTSaveSeriesButton.clicked.connect(self.click_FFT_save_series)
        self.AddButton.clicked.connect(self.click_Add)
        self.SubstractButton.clicked.connect(self.click_Subtract)
        self.AverageButton.clicked.connect(self.click_Average)
        self.ResetButton.clicked.connect(self.click_Reset)
        self.SaveButton.clicked.connect(self.click_save)
        ####
        self.retranslateUi(AppFFT)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(AppFFT)
        self.selected = None

        def set_images(x=None):
            if x is None:
                x = self.images.last_selected
            self.graphicsViewUp.setImage(self.images.get_raw(x))
            self.graphicsViewUp.show()
            self.graphicsViewDw.setImage(self.images.get_fft(x))
            self.images.last_selected = x
            self.selected = self.images.get_by_index(x)
            self.tabWidget.setTabText(1, "FFT: " + path.basename(self.selected.name))
            self.tabWidget.setTabText(0, "Bitmap: " + path.basename(self.selected.name))
            self.buttons_enabled()

        self.set_images = set_images
        self.images = imagelist(parent=self.listView)
        self.listView.setModel(self.images)
        self.listView.activated.connect(self.set_images)
        self.buttons_enabled()
        ########QtImageViewer
        self.graphicsViewUp.aspectRatioMode = Qt.KeepAspectRatio
        self.graphicsViewDw.aspectRatioMode = Qt.KeepAspectRatio
        ############

    def buttons_enabled(self):
        if self.selected and self.images.rowCount():
            self.FFTSingleButton.setEnabled(True)
            if self.selected.ffted:
                self.SaveButton.setEnabled(True)
            if self.images.rowCount() > 1:
                self.FFTSeriesButton.setEnabled(True)
                self.FFTSaveSeriesButton.setEnabled(True)
                self.AverageButton.setEnabled(True)
            else:
                self.FFTSeriesButton.setEnabled(False)
                self.FFTSaveSeriesButton.setEnabled(False)
                self.AverageButton.setEnabled(False)
        else:
            self.SaveButton.setEnabled(False)
            self.FFTSingleButton.setEnabled(False)
            self.AverageButton.setEnabled(False)
            self.FFTSeriesButton.setEnabled(False)
            self.FFTSaveSeriesButton.setEnabled(False)

    def click_Help(self):
        print('HelpButton click')
        wb.open_new(r'help.pdf')

    def click_FFT_single(self):
        print('FFTSingleButton click')
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        image.dist = self.doubleSpinBox.value()
        if self.selected.sign != '=':
            self.selected.fft()
        self.set_images()
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()
        self.tabWidget.setCurrentIndex(1)

    def click_FFT_series(self):
        print('FFTSeriesButtion click')
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        image.dist = self.doubleSpinBox.value()
        self.images.fft_all()
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()

    def click_FFT_save_series(self):
        print('FFTSaveSeriesButton click')
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        image.dist = self.doubleSpinBox.value()
        self.images.fft_all()
        self.images.save_all()
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()

    def click_Add(self):
        print('AddButton click')
        fileNames = \
            QFileDialog.getOpenFileNames(self, 'Open file', '', 'Images (*.bmp)', None,
                                         QFileDialog.DontUseNativeDialog)[0]
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if fileNames:
            try:
                for i in fileNames:
                    self.images.insertRows(image(imread(i), i, sign='+'))
            except ValueError as e:
                QMessageBox.about(self, "Error", str(e))
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()

    def click_Subtract(self):
        print('SubtractButton click')
        fileNames = \
            QFileDialog.getOpenFileNames(self, 'Open file', '', 'Images (*.bmp)', None,
                                         QFileDialog.DontUseNativeDialog)[0]
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if fileNames:
            try:
                for i in fileNames:
                    self.images.insertRows(image(imread(i), i, sign='-'))
            except ValueError as e:
                QMessageBox.about(self, "Error", str(e))
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()

    def click_Average(self):
        print('AverageButton click')
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.images.average()
        self.buttons_enabled()
        QApplication.restoreOverrideCursor()
        self.tabWidget.setCurrentIndex(1)

    def click_Reset(self):
        print('ResetButton click')
        self.images.empty()
        self.tabWidget.setTabText(0, "Bitmap")
        self.tabWidget.setTabText(1, "FFT")
        self.graphicsViewDw.setImage(QImage())
        self.graphicsViewUp.setImage(QImage())
        self.graphicsViewUp.show()
        self.buttons_enabled()

    def click_save(self):
        print('SaveButton click')
        fileName = QFileDialog.getSaveFileName(self, 'Save file', '', '', None, QFileDialog.DontUseNativeDialog)[0]
        if fileName:
            self.selected.save(fileName)

    def retranslateUi(self, AppFFT):
        _translate = QtCore.QCoreApplication.translate
        AppFFT.setWindowTitle(_translate("AppFFT", "AppFFT"))
        self.groupBox.setTitle(_translate("AppFFT", "FFT"))
        self.FFTSingleButton.setText(_translate("AppFFT", "FFT Single"))
        self.FFTSeriesButton.setText(_translate("AppFFT", "FFT Series"))
        self.FFTSaveSeriesButton.setText(_translate("AppFFT", "Save FFT Series"))
        self.groupBox_2.setTitle(_translate("AppFFT", "Operations"))
        self.AddButton.setText(_translate("AppFFT", "Add"))
        self.SubstractButton.setText(_translate("AppFFT", "Substract"))
        self.AverageButton.setText(_translate("AppFFT", "Average"))
        self.groupBox_3.setTitle(_translate("AppFFT", "File List"))
        self.ResetButton.setText(_translate("AppFFT", "Reset File List"))
        self.label.setText(_translate("AppFFT", "Distance"))
        self.SaveButton.setText(_translate("AppFFT", "Save FFT Window"))
        self.HelpButton.setText(_translate("AppFFT", "Help"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("AppFFT", "Bitmap"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("AppFFT", "FFT"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AppFFT = QtWidgets.QMainWindow()
    ui = Ui_AppFFT()
    ui.setupUi(AppFFT)
    AppFFT.show()
    sys.exit(app.exec_())
