import qrcode
import io
from PIL import Image, ImageDraw, ImageFont
import os

def generate_qr_code(book_name, year, author, description=None, category=None,
                    fill_color='black', back_color='white',
                    error_correction='L', box_size=10, border=4,
                    logo_path=None):
    # Set error correction level
    error_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,  # 7% of data can be restored
        'M': qrcode.constants.ERROR_CORRECT_M,  # 15% of data can be restored
        'Q': qrcode.constants.ERROR_CORRECT_Q,  # 25% of data can be restored
        'H': qrcode.constants.ERROR_CORRECT_H,  # 30% of data can be restored
    }

    error_level = error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_L)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_level,
        box_size=box_size,
        border=border,
    )

    # Prepare QR code data
    qr_data = f"Name: {book_name}\nYear: {year}\nAuthor: {author}"
    if description:
        qr_data += f"\nDescription: {description}"
    if category:
        qr_data += f"\nCategory: {category}"

    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Add logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)

            # Calculate logo size (max 30% of QR code)
            logo_max_size = img.size[0] // 3
            logo.thumbnail((logo_max_size, logo_max_size))

            # Calculate position to center the logo
            pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

            # Create a white background for the logo
            logo_bg = Image.new('RGBA', logo.size, (255, 255, 255, 255))

            # Paste the logo on the QR code
            img.paste(logo_bg, pos)
            img.paste(logo, pos, logo)
        except Exception as e:
            print(f"Error adding logo: {e}")

    # Save QR code to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_data = buffer.getvalue()

    return qr_code_data