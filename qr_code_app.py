from PyQt5 import QtWidgets, QtGui, QtCore
from database import (save_book, search_book, delete_book, get_all_books,
                     get_book_categories, get_preference, set_preference)
from qr_code_generator import generate_qr_code
from qr_code_window import QRCodeWindow
import threading
import json
import csv
from PyQt5.QtWidgets import QFileDialog, QColorDialog, QMessageBox, QStatusBar, QShortcut
from PyQt5.QtGui import QKeySequence

class CreditsWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('👨‍💻 Credits')
        self.resize(500, 400)

        layout = QtWidgets.QVBoxLayout()

        # Add a title with emoji
        title_label = QtWidgets.QLabel('📚 QR Code Book Manager', self)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add version info
        version_label = QtWidgets.QLabel('Version 2.0', self)
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(version_label)

        # Add a separator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

        # Add developer info with emojis
        credits_label = QtWidgets.QLabel('This application was developed by:\n\n👨‍💻 Zied Boughdir 2024\n\n🌐 <a href="https://github.com/zinzied">https://github.com/zinzied</a>\n\n✨ Enhanced with new features in 2024', self)
        credits_label.setOpenExternalLinks(True)
        credits_label.setAlignment(QtCore.Qt.AlignCenter)
        credits_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(credits_label)

        # Add a close button
        close_button = QtWidgets.QPushButton('✖️ Close', self)
        close_button.setFixedWidth(150)
        close_button.clicked.connect(self.close)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(close_button)
        button_layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.addLayout(button_layout)

        self.setLayout(layout)

class QRCodeApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.qr_settings = {
            'fill_color': 'black',
            'back_color': 'white',
            'error_correction': 'L',
            'box_size': 10,
            'border': 4,
            'logo_path': None
        }
        self.dark_mode = get_preference('dark_mode', 'false') == 'true'
        self.initUI()

    def initUI(self):
        self.setWindowTitle('📚 QR Code Book Manager')
        self.resize(800, 600)  # Initial window size

        # Center the window
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.center())

        # Apply the appropriate stylesheet based on mode
        self.apply_stylesheet()

        # Create a main layout with a status bar
        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Create a status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready")

        # Create the main content layout
        self.layout = QtWidgets.QVBoxLayout()

        # Create a form layout for book details
        form_layout = QtWidgets.QFormLayout()

        self.bookNameInput = QtWidgets.QLineEdit(self)
        self.bookNameInput.setPlaceholderText('Enter book name')
        form_layout.addRow("Book Name:", self.bookNameInput)

        self.yearInput = QtWidgets.QLineEdit(self)
        self.yearInput.setPlaceholderText('Enter year')
        form_layout.addRow("Year:", self.yearInput)

        self.authorInput = QtWidgets.QLineEdit(self)
        self.authorInput.setPlaceholderText('Enter author name')
        form_layout.addRow("Author:", self.authorInput)

        # Add description field
        self.descriptionInput = QtWidgets.QTextEdit(self)
        self.descriptionInput.setPlaceholderText('Enter book description (optional)')
        self.descriptionInput.setMaximumHeight(100)
        form_layout.addRow("Description:", self.descriptionInput)

        # Add category field
        self.categoryCombo = QtWidgets.QComboBox(self)
        self.categoryCombo.addItem("None")

        # Add categories from database
        categories = get_book_categories()
        for category in categories:
            self.categoryCombo.addItem(category)

        # Add option to create new category
        self.categoryCombo.addItem("Add New Category...")
        self.categoryCombo.currentIndexChanged.connect(self.handle_category_change)
        form_layout.addRow("Category:", self.categoryCombo)

        self.layout.addLayout(form_layout)

        self.generateButton = QtWidgets.QPushButton('📱 Generate QR Code', self)
        self.generateButton.setFixedWidth(250)  # Set fixed width
        self.generateButton.clicked.connect(self.generate_qr_code)
        self.layout.addWidget(self.generateButton)

        self.searchInput = QtWidgets.QLineEdit(self)
        self.searchInput.setPlaceholderText('Search book name')
        self.layout.addWidget(self.searchInput)

        searchLayout = QtWidgets.QHBoxLayout()
        self.searchButton = QtWidgets.QPushButton('🔍 Search Book', self)
        self.searchButton.setFixedWidth(250)  # Set fixed width
        self.searchButton.clicked.connect(self.search_qr_code)
        searchLayout.addWidget(self.searchButton)

        self.searchBookButton = QtWidgets.QPushButton('📱 Search QR Code', self)
        self.searchBookButton.setFixedWidth(250)  # Set fixed width
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

        self.refreshButton = QtWidgets.QPushButton('🔄 Refresh Book List', self)
        self.refreshButton.setFixedWidth(250)  # Set fixed width
        self.refreshButton.clicked.connect(self.refresh_book_list)
        self.layout.addWidget(self.refreshButton)

        # Add "Show Credits" button
        # Add bottom buttons layout
        bottom_buttons = QtWidgets.QHBoxLayout()

        self.creditsButton = QtWidgets.QPushButton('ℹ️ Show Credits', self)
        self.creditsButton.setFixedWidth(250)  # Set fixed width
        self.creditsButton.clicked.connect(self.show_credits)
        bottom_buttons.addWidget(self.creditsButton)

        self.darkModeButton = QtWidgets.QPushButton('🌓 Toggle Dark Mode', self)
        self.darkModeButton.setFixedWidth(250)  # Set fixed width
        self.darkModeButton.clicked.connect(self.toggle_dark_mode)
        bottom_buttons.addWidget(self.darkModeButton)

        self.layout.addLayout(bottom_buttons)

        # Add QR code settings button
        self.qrSettingsButton = QtWidgets.QPushButton('⚙️ QR Code Settings', self)
        self.qrSettingsButton.setFixedWidth(250)  # Set fixed width
        self.qrSettingsButton.clicked.connect(self.show_qr_settings)
        self.layout.addWidget(self.qrSettingsButton)

        # Add export/import buttons
        export_import_layout = QtWidgets.QHBoxLayout()

        self.exportButton = QtWidgets.QPushButton('📤 Export Books', self)
        self.exportButton.setFixedWidth(250)  # Set fixed width
        self.exportButton.clicked.connect(self.export_books)
        export_import_layout.addWidget(self.exportButton)

        self.importButton = QtWidgets.QPushButton('📥 Import Books', self)
        self.importButton.setFixedWidth(250)  # Set fixed width
        self.importButton.clicked.connect(self.import_books)
        export_import_layout.addWidget(self.importButton)

        self.layout.addLayout(export_import_layout)

        # Create a container widget for the main content
        content_widget = QtWidgets.QWidget()
        content_widget.setLayout(self.layout)

        # Add the content widget and status bar to the main layout
        self.main_layout.addWidget(content_widget)
        self.main_layout.addWidget(self.status_bar)

        # Set up keyboard shortcuts
        self.setup_shortcuts()

        # Refresh the book list
        self.refresh_book_list()

    def generate_qr_code(self):
        book_name = self.bookNameInput.text()
        year = self.yearInput.text()
        author = self.authorInput.text()

        # Get description and category if we add those fields later
        description = getattr(self, 'descriptionInput', None)
        description = description.toPlainText() if description else None

        category = getattr(self, 'categoryCombo', None)
        category = category.currentText() if category and category.currentText() != "None" else None

        if book_name and year and author:
            # Generate QR code with current settings
            qr_code_data = generate_qr_code(
                book_name, year, author, description, category,
                self.qr_settings['fill_color'],
                self.qr_settings['back_color'],
                self.qr_settings['error_correction'],
                self.qr_settings['box_size'],
                self.qr_settings['border'],
                self.qr_settings['logo_path']
            )

            # Save to database
            save_book(book_name, year, author, qr_code_data, description, category)

            # Refresh the book list
            self.refresh_book_list()

            # Display the QR code
            img = search_book(book_name)
            if img:
                img.save('temp_qr_code.png')
                pixmap = QtGui.QPixmap('temp_qr_code.png')
                self.qrCodeLabel.setPixmap(pixmap)
                self.status_bar.showMessage(f"QR code generated for '{book_name}'")
            else:
                self.qrCodeLabel.setText('Book not found')
                self.status_bar.showMessage("Error: Book not found after saving")
        else:
            self.qrCodeLabel.setText('Please enter all book details')
            self.status_bar.showMessage("Error: Missing required book details")

    def search_qr_code(self):
        search_text = self.searchInput.text().lower()
        if search_text:
            # Clear the table
            self.bookTable.setRowCount(0)

            # Make sure the table has the correct columns
            if self.bookTable.columnCount() < 6:
                self.bookTable.setColumnCount(6)
                self.bookTable.setHorizontalHeaderLabels(['Name', 'Year', 'Author', 'Description', 'Category', 'QR Code'])

            # Get all books from the database
            books = get_all_books()
            found_count = 0

            # Search in all fields
            for book in books:
                # Check if search text is in any of the book fields
                if (search_text in book[0].lower() or  # Name
                    search_text in str(book[1]).lower() or  # Year
                    search_text in book[2].lower() or  # Author
                    (len(book) > 3 and book[3] and search_text in book[3].lower()) or  # Description
                    (len(book) > 4 and book[4] and search_text in book[4].lower())):  # Category

                    row_position = self.bookTable.rowCount()
                    self.bookTable.insertRow(row_position)

                    # Add book details to the table
                    self.bookTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(book[0]))  # Name
                    self.bookTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(book[1])))  # Year
                    self.bookTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(book[2]))  # Author

                    # Add description if available
                    if len(book) > 3 and book[3]:
                        self.bookTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(book[3]))
                    else:
                        self.bookTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(""))

                    # Add category if available
                    if len(book) > 4 and book[4]:
                        self.bookTable.setItem(row_position, 4, QtWidgets.QTableWidgetItem(book[4]))
                    else:
                        self.bookTable.setItem(row_position, 4, QtWidgets.QTableWidgetItem(""))

                    # Add QR code image
                    img = search_book(book[0])
                    if img:
                        img.save('temp_qr_code.png')
                        pixmap = QtGui.QPixmap('temp_qr_code.png')
                        pixmap = pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                        qr_label = QtWidgets.QLabel()
                        qr_label.setPixmap(pixmap)
                        self.bookTable.setCellWidget(row_position, 5, qr_label)
                        self.bookTable.setRowHeight(row_position, 30)  # Adjust row height

                    found_count += 1

            # Update status bar with search results
            self.status_bar.showMessage(f"Found {found_count} books matching '{search_text}'")
        else:
            self.status_bar.showMessage("Please enter a search term")
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
        # Clear the table
        self.bookTable.setRowCount(0)

        # Update column count and headers for new fields
        if self.bookTable.columnCount() < 6:
            self.bookTable.setColumnCount(6)
            self.bookTable.setHorizontalHeaderLabels(['Name', 'Year', 'Author', 'Description', 'Category', 'QR Code'])

        # Get all books from the database
        books = get_all_books()

        # Add each book to the table
        for book in books:
            row_position = self.bookTable.rowCount()
            self.bookTable.insertRow(row_position)

            # Add book details to the table
            self.bookTable.setItem(row_position, 0, QtWidgets.QTableWidgetItem(book[0]))  # Name
            self.bookTable.setItem(row_position, 1, QtWidgets.QTableWidgetItem(str(book[1])))  # Year
            self.bookTable.setItem(row_position, 2, QtWidgets.QTableWidgetItem(book[2]))  # Author

            # Add description if available
            if len(book) > 3 and book[3]:
                self.bookTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(book[3]))
            else:
                self.bookTable.setItem(row_position, 3, QtWidgets.QTableWidgetItem(""))

            # Add category if available
            if len(book) > 4 and book[4]:
                self.bookTable.setItem(row_position, 4, QtWidgets.QTableWidgetItem(book[4]))
            else:
                self.bookTable.setItem(row_position, 4, QtWidgets.QTableWidgetItem(""))

            # Add QR code image
            img = search_book(book[0])
            if img:
                img.save('temp_qr_code.png')
                pixmap = QtGui.QPixmap('temp_qr_code.png')
                # Resize the pixmap to a smaller size
                pixmap = pixmap.scaled(30, 30, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                qr_label = QtWidgets.QLabel()
                qr_label.setPixmap(pixmap)
                self.bookTable.setCellWidget(row_position, 5, qr_label)
                self.bookTable.setRowHeight(row_position, 30)  # Adjust row height

        # Update status bar
        self.status_bar.showMessage(f"Loaded {self.bookTable.rowCount()} books")

    def show_context_menu(self, position):
        items = self.bookTable.selectedItems()
        if not items:
            return  # No item selected

        menu = QtWidgets.QMenu()
        modify_action = menu.addAction("✏️ Modify Book Infos")
        show_qr_action = menu.addAction("📱 Show QR Code")
        delete_action = menu.addAction("🗑️ Delete Book")

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

        # Create a dialog for editing book details
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Book Details")
        dialog.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Book name
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Book Name:")
        name_input = QtWidgets.QLineEdit()
        name_input.setText(self.bookTable.item(row, 0).text())
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)

        # Year
        year_layout = QtWidgets.QHBoxLayout()
        year_label = QtWidgets.QLabel("Year:")
        year_input = QtWidgets.QLineEdit()
        year_input.setText(self.bookTable.item(row, 1).text())
        year_layout.addWidget(year_label)
        year_layout.addWidget(year_input)
        layout.addLayout(year_layout)

        # Author
        author_layout = QtWidgets.QHBoxLayout()
        author_label = QtWidgets.QLabel("Author:")
        author_input = QtWidgets.QLineEdit()
        author_input.setText(self.bookTable.item(row, 2).text())
        author_layout.addWidget(author_label)
        author_layout.addWidget(author_input)
        layout.addLayout(author_layout)

        # Description
        desc_layout = QtWidgets.QVBoxLayout()
        desc_label = QtWidgets.QLabel("Description:")
        desc_input = QtWidgets.QTextEdit()
        if self.bookTable.columnCount() > 3 and self.bookTable.item(row, 3):
            desc_input.setText(self.bookTable.item(row, 3).text())
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(desc_input)
        layout.addLayout(desc_layout)

        # Category
        cat_layout = QtWidgets.QHBoxLayout()
        cat_label = QtWidgets.QLabel("Category:")
        cat_input = QtWidgets.QComboBox()

        # Add categories from database
        categories = get_book_categories()
        cat_input.addItem("None")
        for category in categories:
            cat_input.addItem(category)

        # Set current category if available
        if self.bookTable.columnCount() > 4 and self.bookTable.item(row, 4):
            current_cat = self.bookTable.item(row, 4).text()
            index = cat_input.findText(current_cat)
            if index >= 0:
                cat_input.setCurrentIndex(index)

        cat_layout.addWidget(cat_label)
        cat_layout.addWidget(cat_input)
        layout.addLayout(cat_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")
        cancel_button = QtWidgets.QPushButton("Cancel")

        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_name = name_input.text()
            year = year_input.text()
            author = author_input.text()
            description = desc_input.toPlainText() if desc_input.toPlainText() else None
            category = cat_input.currentText() if cat_input.currentText() != "None" else None

            if new_name and year and author:
                # Delete old book
                delete_book(old_name)

                # Generate new QR code with current settings
                qr_code_data = generate_qr_code(
                    new_name, year, author, description, category,
                    self.qr_settings['fill_color'],
                    self.qr_settings['back_color'],
                    self.qr_settings['error_correction'],
                    self.qr_settings['box_size'],
                    self.qr_settings['border'],
                    self.qr_settings['logo_path']
                )

                # Save new book
                save_book(new_name, year, author, qr_code_data, description, category)

                # Refresh the book list
                self.refresh_book_list()

                # Update status bar
                self.status_bar.showMessage(f"Book '{old_name}' updated to '{new_name}'")
            else:
                self.status_bar.showMessage("Error: Book name, year, and author are required")

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
        # Get unique book names from selected items
        book_names = set()
        for item in items:
            row = item.row()
            book_name = self.bookTable.item(row, 0).text()
            book_names.add(book_name)

        # Show confirmation dialog
        if len(book_names) == 1:
            message = f"Are you sure you want to delete the book '{list(book_names)[0]}'?"
        else:
            message = f"Are you sure you want to delete {len(book_names)} books?"

        confirm = QMessageBox.question(
            self, "Confirm Delete", message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            # Delete books
            for book_name in book_names:
                delete_book(book_name)

            # Refresh the book list
            self.refresh_book_list()

            # Update status bar
            if len(book_names) == 1:
                self.status_bar.showMessage(f"Book '{list(book_names)[0]}' deleted")
            else:
                self.status_bar.showMessage(f"{len(book_names)} books deleted")

    def sort_table(self, index):
        self.bookTable.sortItems(index, QtCore.Qt.AscendingOrder)

    def show_credits(self):
        self.creditsWindow = CreditsWindow()
        self.creditsWindow.show()

    def apply_stylesheet(self):
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    font-size: 14px;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #3D3D3D;
                    border: 1px solid #5D5D5D;
                    color: #FFFFFF;
                    padding: 5px;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #0D47A1;
                    color: white;
                    border: none;
                    padding: 8px;
                    font-size: 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QTableWidget {
                    background-color: #3D3D3D;
                    color: #FFFFFF;
                    gridline-color: #5D5D5D;
                    font-size: 16px;
                }
                QTableWidget::item {
                    padding: 10px;
                }
                QTableWidget QHeaderView::section {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    padding: 5px;
                    border: 1px solid #5D5D5D;
                }
                QMenu {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    border: 1px solid #5D5D5D;
                }
                QMenu::item:selected {
                    background-color: #0D47A1;
                }
                QStatusBar {
                    background-color: #1D1D1D;
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    font-size: 14px;
                }
                QLineEdit, QPushButton, QLabel, QTableWidget, QComboBox, QSpinBox {
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1E88E5;
                }
                QPushButton:pressed {
                    background-color: #1976D2;
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
                QStatusBar {
                    background-color: #f0f0f0;
                }
            """)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        set_preference('dark_mode', str(self.dark_mode).lower())
        self.apply_stylesheet()
        self.status_bar.showMessage("Theme changed to " + ("Dark" if self.dark_mode else "Light") + " mode")

    def handle_category_change(self, _):
        if self.categoryCombo.currentText() == "Add New Category...":
            # Prompt user for new category
            category, ok = QtWidgets.QInputDialog.getText(
                self, 'New Category', 'Enter new category name:'
            )

            if ok and category:
                # Add new category to combo box
                self.categoryCombo.insertItem(self.categoryCombo.count() - 1, category)
                self.categoryCombo.setCurrentIndex(self.categoryCombo.count() - 2)
            else:
                # User cancelled, revert to "None"
                self.categoryCombo.setCurrentIndex(0)

    def setup_shortcuts(self):
        # Generate QR code - Ctrl+G
        self.shortcut_generate = QShortcut(QKeySequence("Ctrl+G"), self)
        self.shortcut_generate.activated.connect(self.generate_qr_code)

        # Search - Ctrl+F
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(lambda: self.searchInput.setFocus())

        # Refresh - F5
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        self.shortcut_refresh.activated.connect(self.refresh_book_list)

        # Toggle dark mode - Ctrl+D
        self.shortcut_dark_mode = QShortcut(QKeySequence("Ctrl+D"), self)
        self.shortcut_dark_mode.activated.connect(self.toggle_dark_mode)

    def show_qr_settings(self):
        # Create a dialog for QR code settings
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("QR Code Settings")
        dialog.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Error correction level
        error_layout = QtWidgets.QHBoxLayout()
        error_label = QtWidgets.QLabel("Error Correction Level:")
        error_combo = QtWidgets.QComboBox()
        error_combo.addItems(["L (7%)", "M (15%)", "Q (25%)", "H (30%)"])

        # Set current value
        current_error = self.qr_settings['error_correction']
        error_index = {"L": 0, "M": 1, "Q": 2, "H": 3}.get(current_error, 0)
        error_combo.setCurrentIndex(error_index)

        error_layout.addWidget(error_label)
        error_layout.addWidget(error_combo)
        layout.addLayout(error_layout)

        # Box size
        box_layout = QtWidgets.QHBoxLayout()
        box_label = QtWidgets.QLabel("Box Size:")
        box_spin = QtWidgets.QSpinBox()
        box_spin.setRange(5, 20)
        box_spin.setValue(self.qr_settings['box_size'])
        box_layout.addWidget(box_label)
        box_layout.addWidget(box_spin)
        layout.addLayout(box_layout)

        # Border
        border_layout = QtWidgets.QHBoxLayout()
        border_label = QtWidgets.QLabel("Border Size:")
        border_spin = QtWidgets.QSpinBox()
        border_spin.setRange(1, 10)
        border_spin.setValue(self.qr_settings['border'])
        border_layout.addWidget(border_label)
        border_layout.addWidget(border_spin)
        layout.addLayout(border_layout)

        # Fill color
        fill_layout = QtWidgets.QHBoxLayout()
        fill_label = QtWidgets.QLabel("Fill Color:")
        fill_button = QtWidgets.QPushButton()
        fill_button.setStyleSheet(f"background-color: {self.qr_settings['fill_color']};")
        fill_button.clicked.connect(lambda: self.choose_color(fill_button, "fill_color"))
        fill_layout.addWidget(fill_label)
        fill_layout.addWidget(fill_button)
        layout.addLayout(fill_layout)

        # Background color
        back_layout = QtWidgets.QHBoxLayout()
        back_label = QtWidgets.QLabel("Background Color:")
        back_button = QtWidgets.QPushButton()
        back_button.setStyleSheet(f"background-color: {self.qr_settings['back_color']};")
        back_button.clicked.connect(lambda: self.choose_color(back_button, "back_color"))
        back_layout.addWidget(back_label)
        back_layout.addWidget(back_button)
        layout.addLayout(back_layout)

        # Logo
        logo_layout = QtWidgets.QHBoxLayout()
        logo_label = QtWidgets.QLabel("Logo:")
        logo_path = QtWidgets.QLineEdit()
        logo_path.setText(self.qr_settings['logo_path'] or "")
        logo_browse = QtWidgets.QPushButton("Browse")
        logo_browse.clicked.connect(lambda: self.browse_logo(logo_path))
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(logo_path)
        logo_layout.addWidget(logo_browse)
        layout.addLayout(logo_layout)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        save_button = QtWidgets.QPushButton("Save")
        cancel_button = QtWidgets.QPushButton("Cancel")

        save_button.clicked.connect(lambda: self.save_qr_settings(
            error_combo.currentText()[0],
            box_spin.value(),
            border_spin.value(),
            logo_path.text(),
            dialog
        ))
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.exec_()

    def choose_color(self, button, color_key):
        color = QColorDialog.getColor()
        if color.isValid():
            self.qr_settings[color_key] = color.name()
            button.setStyleSheet(f"background-color: {color.name()};")

    def browse_logo(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Logo", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            line_edit.setText(file_path)

    def save_qr_settings(self, error_level, box_size, border, logo_path, dialog):
        self.qr_settings['error_correction'] = error_level
        self.qr_settings['box_size'] = box_size
        self.qr_settings['border'] = border
        self.qr_settings['logo_path'] = logo_path if logo_path else None

        self.status_bar.showMessage("QR code settings updated")
        dialog.accept()

    def export_books(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Books", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not file_path:
            return

        books = get_all_books()

        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Name', 'Year', 'Author', 'Description', 'Category'])
                    for book in books:
                        writer.writerow(book)
            elif file_path.endswith('.json'):
                book_list = []
                for book in books:
                    book_dict = {
                        'name': book[0],
                        'year': book[1],
                        'author': book[2],
                        'description': book[3] if len(book) > 3 else None,
                        'category': book[4] if len(book) > 4 else None
                    }
                    book_list.append(book_dict)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(book_list, f, indent=4)

            self.status_bar.showMessage(f"Books exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error exporting books: {str(e)}")

    def import_books(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Books", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)  # Skip header
                    for row in reader:
                        if len(row) >= 3:
                            name, year, author = row[0], row[1], row[2]
                            description = row[3] if len(row) > 3 else None
                            category = row[4] if len(row) > 4 else None

                            qr_code_data = generate_qr_code(
                                name, year, author, description, category,
                                self.qr_settings['fill_color'],
                                self.qr_settings['back_color'],
                                self.qr_settings['error_correction'],
                                self.qr_settings['box_size'],
                                self.qr_settings['border'],
                                self.qr_settings['logo_path']
                            )
                            save_book(name, year, author, qr_code_data, description, category)

            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    books = json.load(f)

                for book in books:
                    name = book.get('name')
                    year = book.get('year')
                    author = book.get('author')
                    description = book.get('description')
                    category = book.get('category')

                    if name and year and author:
                        qr_code_data = generate_qr_code(
                            name, year, author, description, category,
                            self.qr_settings['fill_color'],
                            self.qr_settings['back_color'],
                            self.qr_settings['error_correction'],
                            self.qr_settings['box_size'],
                            self.qr_settings['border'],
                            self.qr_settings['logo_path']
                        )
                        save_book(name, year, author, qr_code_data, description, category)

            self.refresh_book_list()
            self.status_bar.showMessage(f"Books imported from {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error importing books: {str(e)}")