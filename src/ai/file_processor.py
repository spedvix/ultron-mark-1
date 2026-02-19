"""
File processing utilities for Ultron chat
Handles various file types: PDF, images, text, etc.
"""
import base64
import io
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import pypdf
from loguru import logger


class FileProcessor:
    """Process uploaded files for AI analysis"""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    SUPPORTED_DOCUMENT_FORMATS = {'.pdf', '.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.html', '.css'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def process_file(file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Process an uploaded file
        
        Args:
            file_data: Raw file bytes
            filename: Original filename
            
        Returns:
            Processed file data with content and metadata
        """
        
        try:
            file_ext = Path(filename).suffix.lower()
            file_size = len(file_data)
            
            if file_size > FileProcessor.MAX_FILE_SIZE:
                return {
                    "success": False,
                    "error": f"File too large. Maximum size is {FileProcessor.MAX_FILE_SIZE / 1024 / 1024}MB"
                }
            
            result = {
                "success": True,
                "filename": filename,
                "size": file_size,
                "type": None,
                "content": None,
                "base64_data": None
            }
            
            # Process image files
            if file_ext in FileProcessor.SUPPORTED_IMAGE_FORMATS:
                result.update(FileProcessor._process_image(file_data, file_ext))
            
            # Process PDF files
            elif file_ext == '.pdf':
                result.update(FileProcessor._process_pdf(file_data))
            
            # Process text files
            elif file_ext in {'.txt', '.md', '.py', '.js', '.java', '.cpp', '.c', '.html', '.css'}:
                result.update(FileProcessor._process_text(file_data, file_ext))
            
            else:
                result["success"] = False
                result["error"] = f"Unsupported file format: {file_ext}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _process_image(file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Process image files"""
        
        try:
            # Open and validate image
            image = Image.open(io.BytesIO(file_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 2048x2048 for GPT-4 Vision)
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                "type": "image",
                "content": f"Image: {image.width}x{image.height} pixels",
                "base64_data": base64_data,
                "dimensions": {"width": image.width, "height": image.height}
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return {
                "success": False,
                "error": f"Failed to process image: {str(e)}"
            }
    
    @staticmethod
    def _process_pdf(file_data: bytes) -> Dict[str, Any]:
        """Process PDF files"""
        
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num} ---\n{text}")
            
            full_text = "\n\n".join(text_content)
            
            # Limit text length
            max_chars = 50000
            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + f"\n\n... (truncated, original length: {len(full_text)} characters)"
            
            return {
                "type": "pdf",
                "content": full_text,
                "page_count": len(pdf_reader.pages),
                "metadata": {
                    "pages": len(pdf_reader.pages),
                    "text_length": len(full_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                "success": False,
                "error": f"Failed to process PDF: {str(e)}"
            }
    
    @staticmethod
    def _process_text(file_data: bytes, file_ext: str) -> Dict[str, Any]:
        """Process text-based files"""
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            text_content = None
            
            for encoding in encodings:
                try:
                    text_content = file_data.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                return {
                    "success": False,
                    "error": "Unable to decode file with supported encodings"
                }
            
            # Limit text length
            max_chars = 50000
            if len(text_content) > max_chars:
                text_content = text_content[:max_chars] + f"\n\n... (truncated, original length: {len(text_content)} characters)"
            
            return {
                "type": "text",
                "content": text_content,
                "language": file_ext[1:] if file_ext else "text",
                "metadata": {
                    "length": len(text_content),
                    "lines": text_content.count('\n') + 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            return {
                "success": False,
                "error": f"Failed to process text file: {str(e)}"
            }
    
    @staticmethod
    def encode_image_from_path(image_path: str) -> Optional[str]:
        """
        Encode an image file to base64
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string or None if error
        """
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            result = FileProcessor._process_image(image_data, Path(image_path).suffix)
            return result.get("base64_data")
            
        except Exception as e:
            logger.error(f"Error encoding image from path: {e}")
            return None
