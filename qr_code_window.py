from PyQt5 import QtWidgets, QtGui, QtPrintSupport, QtCore

class QRCodeWindow(QtWidgets.QWidget):
    def __init__(self, pixmaps):
        super().__init__()
        self.initUI(pixmaps)
    
    def initUI(self, pixmaps):
        self.setWindowTitle('QR Codes')
        layout = QtWidgets.QVBoxLayout()
        
        grid_layout = QtWidgets.QGridLayout()
        row = 0
        col = 0
        for i, pixmap in enumerate(pixmaps):
            label = QtWidgets.QLabel(self)
            label.setPixmap(pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            grid_layout.addWidget(label, row, col)
            col += 1
            if col == 4:  # Change this value to adjust the number of QR codes per row
                col = 0
                row += 1
        
        layout.addLayout(grid_layout)
        
        print_button = QtWidgets.QPushButton('Print QR Codes', self)
        print_button.clicked.connect(self.print_qr_codes)
        layout.addWidget(print_button)
        
        self.setLayout(layout)
        self.resize(600, 400)
    
    def print_qr_codes(self):
        printer = QtPrintSupport.QPrinter()
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            painter = QtGui.QPainter(printer)
            rect = painter.viewport()
            size = self.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.rect())
            self.render(painter)
            painter.end()