"""
Resume Parser Module
Handles parsing of different file formats (PDF, DOCX, TXT)
"""
import os
import io
from pdfminer.high_level import extract_text as pdf_extract
from pdfminer.pdfparser import PDFSyntaxError
import docx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_document(file_path):
    """
    Parse document based on file extension
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        str: Extracted text from the document or empty string if parsing fails
    """
    try:
        # Get file extension (lowercase)
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        # Parse based on file extension
        if file_extension == '.pdf':
            return parse_pdf(file_path)
        elif file_extension == '.docx':
            return parse_docx(file_path)
        elif file_extension == '.txt':
            return parse_txt(file_path)
        else:
            logger.error(f"Unsupported file format: {file_extension}")
            return ""
    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        return ""

def parse_pdf(file_path):
    """
    Extract text from PDF files
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        text = pdf_extract(file_path)
        return text
    except PDFSyntaxError as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        return ""

def parse_docx(file_path):
    """
    Extract text from DOCX files
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text from the DOCX
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"Error parsing DOCX: {str(e)}")
        return ""

def parse_txt(file_path):
    """
    Extract text from TXT files
    
    Args:
        file_path (str): Path to the TXT file
        
    Returns:
        str: Content of the TXT file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try different encoding if utf-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error parsing TXT with alternate encoding: {str(e)}")
            return ""
    except Exception as e:
        logger.error(f"Error parsing TXT: {str(e)}")
        return ""