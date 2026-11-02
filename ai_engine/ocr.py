
from pathlib import Path
import pymupdf
from PIL import Image
import pytesseract


def extract_text(file_path):
    """
    Extract text from TXT, PDF, and image files.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extension = path.suffix.lower()

    # 1. Plain text files
    if extension == ".txt":
        return path.read_text(encoding="utf-8")

    # 2. PDF files
    elif extension == ".pdf":
        extracted_text = []

        with pymupdf.open(path) as pdf:
            for page in pdf:
                text = page.get_text()

                # OCR scanned PDF pages if text is unavailable
                if not text.strip():
                    pix = page.get_pixmap()
                    image = Image.frombytes(
                        "RGB",
                        [pix.width, pix.height],
                        pix.samples
                    )
                    text = pytesseract.image_to_string(image)

                extracted_text.append(text)

        return "\n".join(extracted_text)

    # 3. Image files
    elif extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        image = Image.open(path)
        return pytesseract.image_to_string(image)

    else:
        raise ValueError(f"Unsupported file format: {extension}")
