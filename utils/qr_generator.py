import qrcode
import io
import tempfile
import re
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradientColorMask
import requests
from config import QR_DEFAULT_SIZE, QR_DEFAULT_BORDER

class QRGenerator:
    """Utility class for generating and reading QR codes"""
    
    @staticmethod
    def generate_text_qr(text: str) -> io.BytesIO:
        """Generate a QR code from plain text"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=QR_DEFAULT_BORDER,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    @staticmethod
    def generate_url_qr(url: str) -> io.BytesIO:
        """Generate a QR code from a URL"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=QR_DEFAULT_BORDER,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create stylish QR code
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradientColorMask(),
        )
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    @staticmethod
    def generate_wifi_qr(ssid: str, password: str, encryption_type: str = "WPA") -> io.BytesIO:
        """Generate a QR code for WiFi connection"""
        wifi_string = f"WIFI:T:{encryption_type};S:{ssid};P:{password};;"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=QR_DEFAULT_BORDER,
        )
        qr.add_data(wifi_string)
        qr.make(fit=True)
        
        # Custom colors for WiFi QR
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradientColorMask(
                back_color=(255, 255, 255),
                center_color=(33, 150, 243),
                edge_color=(25, 118, 210)
            ),
        )
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    @staticmethod
    def generate_contact_qr(name: str, phone: str, email: str = None) -> io.BytesIO:
        """Generate a QR code for contact information (vCard)"""
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL:{phone}
{'EMAIL:' + email if email else ''}
END:VCARD"""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=QR_DEFAULT_BORDER,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        
        # Custom colors for contact QR
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=RadialGradientColorMask(
                back_color=(255, 255, 255),
                center_color=(76, 175, 80),
                edge_color=(27, 94, 32)
            ),
        )
        
        # Save to BytesIO
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes
    
    @staticmethod
    def read_qr_from_image(photo_file) -> str:
        """Read and decode QR code from an image file"""
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            
            # Download the image to a temporary file
            with tempfile.NamedTemporaryFile(delete=True, suffix='.jpg') as tmp_file:
                # Download photo
                photo_file.download_to_drive(tmp_file.name)
                
                # Open image with PIL
                img = Image.open(tmp_file.name)
                
                # Decode QR code
                decoded_objects = decode(img)
                
                if decoded_objects:
                    return decoded_objects[0].data.decode('utf-8')
                else:
                    return None
                    
        except ImportError:
            return "QR reading requires pyzbar. Please install: pip install pyzbar"
        except Exception as e:
            raise Exception(f"Failed to read QR code: {str(e)}")
