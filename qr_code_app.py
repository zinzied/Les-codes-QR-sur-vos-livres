from PyQt5 import QtWidgets, QtGui, QtCore
from database import save_book, search_book, delete_book, get_all_books
from qr_code_generator import generate_qr_code
from qr_code_window import QRCodeWindow
import threading

class CreditsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Credits')
        self.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout()
        
        credits_label = QtWidgets.QLabel('This application was developed by:\n\n Zied Boughdir 2024\n\n https://github.com/zinzied', self)
        credits_label.setOpenExternalLinks(True)
        credits_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(credits_label)
        
        self.setLayout(layout)

class QRCodeApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('QR Code Generator')
        self.resize(800, 600)  # Initial window size

        # Center the window
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.center())

        # Apply a stylesheet for better color contrast and font size
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QLineEdit, QPushButton, QLabel, QTableWidget {
                font-size: 16px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
            }
            QTableWidget {
                gridline-color: #d0d0d0;
            }
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }
        """)

        self.layout = QtWidgets.QVBoxLayout()
        
        self.bookNameInput = QtWidgets.QLineEdit(self)
        self.bookNameInput.setPlaceholderText('Enter book name')
        self.layout.addWidget(self.bookNameInput)
    
        self.yearInput = QtWidgets.QLineEdit(self)
        self.yearInput.setPlaceholderText('Enter year')
        self.layout.addWidget(self.yearInput)
    
        self.authorInput = QtWidgets.QLineEdit(self)
        self.authorInput.setPlaceholderText('Enter author name')
        self.layout.addWidget(self.authorInput)
    
        self.generateButton = QtWidgets.QPushButton('Generate QR Code', self)
        self.generateButton.setFixedWidth(200)  # Set fixed width
        self.generateButton.clicked.connect(self.generate_qr_code)
        self.layout.addWidget(self.generateButton)
    
        self.searchInput = QtWidgets.QLineEdit(self)
        self.searchInput.setPlaceholderText('Search book name')
        self.layout.addWidget(self.searchInput)
    
        searchLayout = QtWidgets.QHBoxLayout()
        self.searchButton = QtWidgets.QPushButton('Search Book', self)
        self.searchButton.setFixedWidth(200)  # Set fixed width
        self.searchButton.clicked.connect(self.search_qr_code)
        searchLayout.addWidget(self.searchButton)
    
        self.searchBookButton = QtWidgets.QPushButton('Search QR Code', self)
        self.searchBookButton.setFixedWidth(200)  # Set fixed width
        self.searchBookButton.clicked.connect(self.search_book)
        searchLayout.addWidget(self.searchBookButton)
    
        self.layout.addLayout(searchLayout)
    
        self.qrCodeLabel = QtWidgets.QLabel(self)
        self.layout.addWidget(self.qrCodeLabel)
        
        self.bookTable = QtWidgets.QTableWidget(self)
        self.bookTable.setColumnCount(4)
        self.bookTable.setHorizontalHeaderLabels(['Name', 'Year', 'Author', 'QR Code'])
        self.bookTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # Adjust table size
        self.bookTable.setSortingEnabled(True)  # Enable sorting
        self.bookTable.horizontalHeader().sectionClicked.connect(self.sort_table)  # Connect header click to sort function
        self.layout.addWidget(self.bookTable)
        self.bookTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bookTable.customContextMenuRequested.connect(self.show_context_menu)
        
        self.refreshButton = QtWidgets.QPushButton('Refresh Book List', self)
        self.refreshButton.setFixedWidth(200)  # Set fixed width
        self.refreshButton.clicked.connect(self.refresh_book_list)
        self.layout.addWidget(self.refreshButton)
        
        # Add "Show Credits" button
        self.creditsButton = QtWidgets.QPushButton('Show Credits', self)
        self.creditsButton.setFixedWidth(200)  # Set fixed width
        self.creditsButton.clicked.connect(self.show_credits)
        self.layout.addWidget(self.creditsButton)
        
        self.setLayout(self.layout)
        self.refresh_book_list()

    def generate_qr_code(self):
        book_name = self.bookNameInput.text()
        year = self.yearInput.text()
        author = self.authorInput.text()
        if book_name and year and author:
            qr_code_data = generate_qr_code(book_name, year, author)
            save_book(book_name, year, author, qr_code_data)
            self.refresh_book_list()
            img = search_book(book_name)
            if img:
                img.save('temp_qr_code.png')
                pixmap = QtGui.QPixmap('temp_qr_code.png')
                self.qrCodeLabel.setPixmap(pixmap)
            else:
                self.qrCodeLabel.setText('Book not found')
        else:
            self.qrCodeLabel.setText('Please enter all book details')
    
    def search_qr_code(self):
        book_name = self.searchInput.text().lower()
        if book_name:
            self.bookTable.setRowCount(0)
            books = get_all_books()
            for book in books:
                if book_name in book[0].lower():
                    row_position = self.bookTable.rowCount()
                    self.bookTable.insertRow(row_position)
                    self.bookTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(book[0]))
                    self.bookTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(book[1])))
                    self.bookTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(book[2]))
                    img = search_book(book[0])
                    if img:
                        img.save('temp_qr_code.png')
                        pixmap = QtGui.QPixmap('temp_qr_code.png')
                        pixmap = pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)  # Smaller size
                        qr_label = QtWidgets.QLabel()
                        qr_label.setPixmap(pixmap)
                        self.bookTable.setCellWidget(row_position, 3, qr_label)
                        self.bookTable.setRowHeight(row_position, 30)  # Adjust row height
        else:
            self.qrCodeLabel.setText('Please enter a book name to search')

    def search_book(self):
        book_name = self.searchInput.text()
        if book_name:
            threading.Thread(target=self._search_qr_code, args=(book_name,)).start()
        else:
            self.qrCodeLabel.setText('Please enter a book name to search')
    
    def _search_qr_code(self, book_name):
        img = search_book(book_name)
        if img:
            img.save('temp_qr_code.png')
            pixmap = QtGui.QPixmap('temp_qr_code.png')
            self.qrCodeLabel.setPixmap(pixmap)
        else:
            self.qrCodeLabel.setText('Book not found')
    
    def refresh_book_list(self):
        self.bookTable.setRowCount(0)
        books = get_all_books()
        for book in books:
            row_position = self.bookTable.rowCount()
            self.bookTable.insertRow(row_position)
            self.bookTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(book[0]))
            self.bookTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(book[1])))
            self.bookTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(book[2]))
            img = search_book(book[0])
            if img:
                img.save('temp_qr_code.png')
                pixmap = QtGui.QPixmap('temp_qr_code.png')
                # Resize the pixmap to a smaller size
                pixmap = pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)  # Smaller size
                qr_label = QtWidgets.QLabel()
                qr_label.setPixmap(pixmap)
                self.bookTable.setCellWidget(row_position, 3, qr_label)
                self.bookTable.setRowHeight(row_position, 30)  # Adjust row height
    
    def show_context_menu(self, position):
        items = self.bookTable.selectedItems()
        if not items:
            return  # No item selected

        menu = QtWidgets.QMenu()
        modify_action = menu.addAction("Modify Book Infos")
        show_qr_action = menu.addAction("Show QR Code")
        delete_action = menu.addAction("Delete Book")
    
        action = menu.exec_(self.bookTable.viewport().mapToGlobal(position))
    
        if action == modify_action:
            self.modify_book_name(items[0])
        elif action == show_qr_action:
            self.show_multiple_qr_codes()
        elif action == delete_action:
            self.delete_books(items)
    
    def modify_book_name(self, item):
        row = item.row()
        old_name = self.bookTable.item(row, 0).text()
        new_name, ok = QtWidgets.QInputDialog.getText(self, 'Modify Book Name', 'Enter new book name:', text=old_name)
        if ok and new_name:
            year, ok = QtWidgets.QInputDialog.getInt(self, 'Modify Year', 'Enter new year:')
            if ok:
                author, ok = QtWidgets.QInputDialog.getText(self, 'Modify Author', 'Enter new author name:')
                if ok:
                    delete_book(old_name)
                    qr_code_data = generate_qr_code(new_name, year, author)
                    save_book(new_name, year, author, qr_code_data)
                    self.refresh_book_list()
    
    def show_multiple_qr_codes(self):
        selected_items = self.bookTable.selectedItems()
        selected_books = set()
        for item in selected_items:
            row = item.row()
            book_name = self.bookTable.item(row, 0).text()
            selected_books.add(book_name)
        
        threading.Thread(target=self._show_multiple_qr_codes, args=(selected_books,)).start()
    
    def _show_multiple_qr_codes(self, book_names):
        qr_pixmaps = []
        for book_name in book_names:
            img = search_book(book_name)
            if img:
                img.save('temp_qr_code.png')
                pixmap = QtGui.QPixmap('temp_qr_code.png')
                qr_pixmaps.append(pixmap)
        
        if qr_pixmaps:
            QtCore.QMetaObject.invokeMethod(self, "show_qr_code_window", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(list, qr_pixmaps))
        else:
            self.qrCodeLabel.setText('No QR codes found for selected books')
    
    @QtCore.pyqtSlot(list)
    def show_qr_code_window(self, pixmaps):
        self.qrCodeWindow = QRCodeWindow(pixmaps)
        self.qrCodeWindow.show()
    
    def delete_books(self, items):
        book_names = set()
        for item in items:
            row = item.row()
            book_name = self.bookTable.item(row, 0).text()
            book_names.add(book_name)
        
        for book_name in book_names:
            delete_book(book_name)
        
        self.refresh_book_list()

    def sort_table(self, index):
        self.bookTable.sortItems(index, QtCore.Qt.AscendingOrder)
    
    def show_credits(self):
        self.creditsWindow = CreditsWindow()
        self.creditsWindow.show()