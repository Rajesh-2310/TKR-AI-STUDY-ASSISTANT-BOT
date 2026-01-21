import PyPDF2
import pdfplumber
from PIL import Image
import io
import os
from config import Config
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Process PDF files to extract text and images"""
    
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.chunk_overlap = Config.CHUNK_OVERLAP
    
    def extract_text(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text_content = []
            page_texts = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        page_texts.append({
                            'page': page_num,
                            'text': text.strip()
                        })
                        text_content.append(text.strip())
            
            full_text = '\n\n'.join(text_content)
            logger.info(f"Extracted text from {len(page_texts)} pages")
            return full_text, page_texts
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise
    
    def extract_images(self, pdf_path, material_id):
        """Extract images from PDF file"""
        try:
            extracted_images = []
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract images from page
                    if hasattr(page, 'images') and page.images:
                        for img_idx, img in enumerate(page.images):
                            try:
                                # Get image from page
                                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                                cropped = page.within_bbox((x0, y0, x1, y1))
                                
                                # Save image
                                image_filename = f"material_{material_id}_page_{page_num}_img_{img_idx}.png"
                                image_path = os.path.join(Config.IMAGES_FOLDER, image_filename)
                                
                                # Convert to image and save
                                img_obj = cropped.to_image(resolution=150)
                                img_obj.save(image_path, format='PNG')
                                
                                extracted_images.append({
                                    'path': image_path,
                                    'page': page_num,
                                    'type': 'png'
                                })
                                
                            except Exception as img_error:
                                logger.warning(f"Failed to extract image {img_idx} from page {page_num}: {img_error}")
                                continue
            
            # Also try PyPDF2 method for embedded images
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        if '/XObject' in page['/Resources']:
                            xObject = page['/Resources']['/XObject'].get_object()
                            
                            for obj_idx, obj in enumerate(xObject):
                                if xObject[obj]['/Subtype'] == '/Image':
                                    try:
                                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                                        data = xObject[obj].get_data()
                                        
                                        image_filename = f"material_{material_id}_page_{page_num}_embedded_{obj_idx}.png"
                                        image_path = os.path.join(Config.IMAGES_FOLDER, image_filename)
                                        
                                        # Check if already extracted
                                        if not any(img['path'] == image_path for img in extracted_images):
                                            if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                                                mode = "RGB"
                                            else:
                                                mode = "P"
                                            
                                            img = Image.frombytes(mode, size, data)
                                            img.save(image_path)
                                            
                                            extracted_images.append({
                                                'path': image_path,
                                                'page': page_num,
                                                'type': 'png'
                                            })
                                    except Exception as embed_error:
                                        logger.warning(f"Failed to extract embedded image: {embed_error}")
                                        continue
            except Exception as pypdf_error:
                logger.warning(f"PyPDF2 image extraction failed: {pypdf_error}")
            
            logger.info(f"Extracted {len(extracted_images)} images from PDF")
            return extracted_images
            
        except Exception as e:
            logger.error(f"Image extraction failed: {e}")
            return []
    
    def chunk_text(self, text, page_texts):
        """Split text into chunks for embedding"""
        chunks = []
        
        for page_data in page_texts:
            page_num = page_data['page']
            page_text = page_data['text']
            
            # Split by sentences or paragraphs
            paragraphs = page_text.split('\n\n')
            
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) < self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'page': page_num
                        })
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'page': page_num
                })
        
        logger.info(f"Created {len(chunks)} text chunks")
        return chunks
    
    def process_pdf(self, pdf_path, material_id):
        """Complete PDF processing pipeline"""
        try:
            # Extract text
            full_text, page_texts = self.extract_text(pdf_path)
            
            # Extract images
            images = self.extract_images(pdf_path, material_id)
            
            # Chunk text
            chunks = self.chunk_text(full_text, page_texts)
            
            return {
                'full_text': full_text,
                'page_texts': page_texts,
                'chunks': chunks,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise
