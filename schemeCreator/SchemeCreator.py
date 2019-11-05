import csv
import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QFileDialog, QMainWindow, QTableWidgetItem, \
    QDesktopWidget, QColorDialog
from ini import Ui_Form as Ui_Form1
from fin import Ui_Form as Ui_Form3
from main1 import Ui_Form as Ui_Form2


class Initialization(QMainWindow, Ui_Form1):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.fname = ''
        self.y_x = (0, 0)
        msg = QMessageBox.question(self, 'Импорт', f'Импортировать файл со схемой?', QMessageBox.Open, QMessageBox.No)
        if msg == QMessageBox.Open:
            self.fname = QFileDialog.getOpenFileName(self, 'Выбрать файл со схемой', '', "Схема(*.csv)")[0]
        if self.fname == '':
            self.setupUi(self)
            self.center()
            self.show()
            self.pushButton.clicked.connect(lambda: self.next_step(True))
        else:
            self.next_step()

    def next_step(self, new=False):
        if new:
            self.y_x = (self.spinBox.value(), self.spinBox_2.value())
        self.close()
        self.next_form = MainProgramme(self.y_x, self.fname)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MainProgramme(QWidget, Ui_Form2):
    def __init__(self, y_x, fname):
        super().__init__()
        self.fname = fname
        self.y_x = y_x
        self.initUI()

    def loadTable(self):
        myFont = QtGui.QFont()
        myFont.setBold(True)
        max_x = QDesktopWidget().availableGeometry().getRect()[2]
        max_y = QDesktopWidget().availableGeometry().getRect()[3]
        if self.fname:
            with open(self.fname, encoding="utf8") as csvfile:
                reader = csv.reader(csvfile, delimiter=';', quotechar='"')
                scheme = list(enumerate(reader))
                self.tableWidget.setColumnCount(len(scheme[0][1]))
                self.tableWidget.setRowCount(len(scheme))
                for i, row in scheme:
                    for j, elem in enumerate(row):
                        elem = elem.split()
                        if len(elem) == 2:
                            symbol, forecolor, backcolor = '', elem[0], elem[1]
                        else:
                            symbol, forecolor, backcolor = elem[0], elem[1], elem[2]
                        self.tableWidget.setItem(i, j, QTableWidgetItem(symbol))
                        if i == 0:
                            self.tableWidget.setColumnWidth(j, 30)
                        self.tableWidget.item(i, j).setTextAlignment(Qt.AlignCenter)
                        self.tableWidget.item(i, j).setFont(myFont)
                        self.tableWidget.item(i, j).setForeground(QBrush(QColor(forecolor)))
                        self.tableWidget.item(i, j).setBackground(QBrush(QColor(backcolor)))
                x = 30 * (len(scheme[0][1]) + 1) + 5
                y = 30 * (len(scheme) + 1) + 5
        else:
            self.tableWidget.setColumnCount(self.y_x[1])
            self.tableWidget.setRowCount(self.y_x[0])
            for j in range(self.y_x[1]):
                self.tableWidget.setColumnWidth(j, 30)
                for i in range(self.y_x[0]):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(''))
                    self.tableWidget.item(i, j).setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.item(i, j).setFont(myFont)
                    self.tableWidget.item(i, j).setBackground(QBrush(Qt.white))
            x = 30 * (self.y_x[1] + 1) + 5
            y = 30 * (self.y_x[0] + 1) + 5
        x = x if x < max_x else max_x
        y = y if y < max_y - 65 else max_y - 65
        self.resize(x, y)
        self.tableWidget.resize(x, y)
        self.center()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.next_form = Exit(self)
        selected = self.tableWidget.selectedItems()
        if selected:
            if event.key() == Qt.Key_Control:
                for cell in selected:
                    cell.setBackground(QBrush(Qt.white))
                    cell.setForeground(QBrush(Qt.black))
                self.tableWidget.clearSelection()
            elif event.key() == Qt.Key_Shift:
                color = QColorDialog.getColor()
                if color.isValid():
                    for cell in selected:
                        cell.setBackground(QBrush(color))
                    self.tableWidget.clearSelection()
            elif event.key() == Qt.Key_Alt:
                color = QColorDialog.getColor()
                if color.isValid():
                    for cell in selected:
                        cell.setForeground(QBrush(color))
                    self.tableWidget.clearSelection()

    def initUI(self):
        self.setupUi(self)
        self.loadTable()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Exit(QMainWindow, Ui_Form3):
    def __init__(self, prev):
        super().__init__()
        self.prev = prev
        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.show()
        self.pushButton_2.clicked.connect(self.start_anew)
        self.pushButton.clicked.connect(self.export)
        self.pushButton_3.clicked.connect(self.image)
        self.pushButton_4.clicked.connect(self.exit)

    def image(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.prev.tableWidget.winId())
        name = QFileDialog.getSaveFileName(self, 'Сохранить как', '', "Картинка(*.jpg)")[0]
        if name:
            screenshot.save(name, 'jpg')

    def start_anew(self):
        self.close()
        self.next_form = Initialization()
        self.prev.close()

    def export(self):
        self.outname = QFileDialog.getSaveFileName(self, 'Сохранить как', '', "Схема(*.csv)")[0]
        if self.outname:
            self.create_file()

    def exit(self):
        self.close()
        self.prev.close()

    def create_file(self):
        with open(self.outname, 'w', encoding='UTF-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"')
            for i in range(self.prev.tableWidget.rowCount()):
                row = []
                for j in range(self.prev.tableWidget.columnCount()):
                    item = self.prev.tableWidget.item(i, j)
                    row.append(' '.join([item.text(), item.foreground().color().name(),
                                         item.background().color().name()]))
                writer.writerow(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Initialization()
    sys.exit(app.exec_())
