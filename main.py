import sys
from PyQt5 import QtWidgets
from qr_code_app import QRCodeApp

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = QRCodeApp()
    ex.show()
    sys.exit(app.exec_())