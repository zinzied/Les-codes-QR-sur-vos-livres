import sys
from PyQt5 import QtWidgets
from qr_code_app import QRCodeApp
from database import close_connection

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = QRCodeApp()
    ex.show()
    sys.exit(app.exec_())
close_connection()