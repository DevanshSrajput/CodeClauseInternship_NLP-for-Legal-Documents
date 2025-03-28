import fitz  # PyMuPDF
import docx
import re
from typing import Optional

class DocumentProcessor:
    """
    Handles document parsing and text extraction from various file formats.
    """
    
    def extract_text(self, content: bytes, filename: str) -> str:
        """Extract text from various document formats"""
        file_extension = filename.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self._extract_from_pdf(content)
        elif file_extension in ['doc', 'docx']:
            return self._extract_from_docx(content)
        elif file_extension in ['txt', 'text']:
            return content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF documents"""
        text = ""
        with fitz.open(stream=content, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    
    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX documents"""
        import io
        from tempfile import NamedTemporaryFile
        
        # Save bytes to temporary file
        with NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract text from the temporary file
        doc = docx.Document(tmp_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
        # Clean up temporary file
        import os
        os.unlink(tmp_path)
        
        return text
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for improved NLP performance"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Replace common legal abbreviations
        abbreviations = {
            "w.r.t.": "with respect to",
            "i.e.": "that is",
            "e.g.": "for example",
        }
        
        for abbr, expansion in abbreviations.items():
            text = text.replace(abbr, expansion)
            
        return text
    
    def identify_document_type(self, text: str) -> str:
        """Identify the type of legal document based on content analysis"""
        # Define patterns for different document types
        patterns = {
            "contract": [r"agreement", r"between parties", r"terms and conditions", r"hereby agree", r"in witness whereof"],
            "court_filing": [r"in the court", r"plaintiff", r"defendant", r"case no", r"jurisdiction"],
            "legislation": [r"act ", r"statute", r"be it enacted", r"section \d+", r"amendment"],
            "legal_opinion": [r"opinion", r"advised", r"recommendation", r"conclude", r"analysis"]
        }
        
        # Count pattern matches for each document type
        scores = {doc_type: 0 for doc_type in patterns}
        for doc_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text.lower()):
                    scores[doc_type] += 1
        
        # Return the document type with the highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return "general_legal_document"         