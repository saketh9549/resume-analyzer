import logging
import pypdfium2 as pdfium
from PIL import Image

logger = logging.getLogger(__name__)

def convert_pdf_to_images(pdf_path: str, max_pages: int = 2) -> list:
    """
    Asynchronously/synchronously convert PDF pages to a list of PIL Images.
    Uses pypdfium2 to avoid system-level Poppler dependencies.
    """
    images = []
    try:
        doc = pdfium.PdfDocument(pdf_path)
        pages_count = min(len(doc), max_pages)
        for i in range(pages_count):
            page = doc[i]
            # Render page to a bitmap (scale=2 for high resolution crispness)
            bitmap = page.render(scale=2)
            pil_image = bitmap.to_pil()
            images.append(pil_image)
        logger.info(f"Converted {len(images)} PDF pages to images for {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
    return images
