import qrcode
import io

def generate_qr_code(book_name, year, author):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr_data = f"Name: {book_name}\nYear: {year}\nAuthor: {author}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    
    # Save QR code to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = buffer.getvalue()
    
    return qr_code_data