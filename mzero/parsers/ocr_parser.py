"""OCR Image Parser for mzero."""

import os
from mzero.types import Document, DocumentType
from mzero.utils.logger import logger


class OCRParser:
    @staticmethod
    def parse_image(file_path: str) -> Document:
        content = ""
        try:
            from PIL import Image
            import pytesseract
            img = Image.open(file_path)
            content = pytesseract.image_to_string(img)
        except Exception as e:
            logger.warning(f"Tesseract OCR not installed or error processing image {file_path}: {e}")
            content = f"[Image File: {os.path.basename(file_path)} - OCR text extraction requires pytesseract]"

        return Document(
            id=file_path,
            source_path=file_path,
            content=content,
            doc_type=DocumentType.IMAGE
        )
