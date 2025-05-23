
# 📚 QR Code Book Manager

A modern, feature-rich application for generating and managing QR codes for library books. This application provides a user-friendly interface for creating, storing, and managing QR codes for books with comprehensive book information. The application includes a database for persistent storage and offers various customization options for QR codes.

<img width="954" alt="image" src="https://github.com/user-attachments/assets/01079a95-0d56-4040-93c6-d1f4938a411b" />


## ✨ Features

### 📱 QR Code Generation and Management
- **Customizable QR Codes**: Adjust colors, size, error correction level, and add custom logos
- **Batch QR Code Viewing**: View multiple QR codes at once
- **Print Support**: Print QR codes directly from the application
- **QR Code Preview**: Instantly preview generated QR codes

### 📚 Book Management
- **Comprehensive Book Details**: Store book name, author, year, description, and category
- **Search Functionality**: Search books by any field (name, author, year, etc.)
- **Edit and Delete**: Easily modify or remove book entries
- **Sorting**: Sort book list by any column

### 💾 Data Management
- **Database Storage**: SQLite database for efficient data storage
- **Import/Export**: Import and export book data in CSV or JSON formats
- **Data Integrity**: Proper database management with error handling

### 🎨 User Interface
- **Modern UI**: Clean, intuitive interface with emoticons for better visual cues
- **Dark Mode**: Toggle between light and dark themes
- **Responsive Layout**: Properly sized elements and organized layout
- **Keyboard Shortcuts**: Efficient navigation with keyboard shortcuts

## 🚀 Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/zinzied/Les-codes-QR-sur-vos-livres.git
    cd Les-codes-QR-sur-vos-livres
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

## 🔧 Usage

1. **Run the application**:
    ```sh
    python main.py
    ```

2. **Creating a QR Code**:
   - Enter book details (name, author, year, description, category)
   - Click "📱 Generate QR Code"
   - The QR code will be displayed and saved to the database

3. **Searching for Books**:
   - Enter search text in the search field
   - Click "🔍 Search Book" to find matching books
   - Results will be displayed in the table

4. **Customizing QR Codes**:
   - Click "⚙️ QR Code Settings"
   - Adjust colors, size, error correction level, and add a logo
   - Settings will be applied to newly generated QR codes

5. **Importing/Exporting Data**:
   - Click "📤 Export Books" to save your book data
   - Click "📥 Import Books" to load book data from a file

6. **Toggle Dark Mode**:
   - Click "🌓 Toggle Dark Mode" or use Ctrl+D shortcut
   - The application theme will switch between light and dark modes

## ⌨️ Keyboard Shortcuts

- **Ctrl+G**: Generate QR code
- **Ctrl+F**: Focus search field
- **F5**: Refresh book list
- **Ctrl+D**: Toggle dark mode

## 🛠️ Technologies Used

- **Python**: Core programming language
- **PyQt5**: GUI framework
- **SQLite**: Database management
- **qrcode**: QR code generation library
- **Pillow**: Image processing

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
