import spacy
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class ClauseIdentifier:
    """
    Identifies key clauses and sections in legal documents.
    """
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            import os
            os.system("python -m spacy download en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
            
        # Define patterns for identifying clause boundaries
        self.section_patterns = [
            r"(?<!\w)Section \d+\.?(?:\d+)?",
            r"(?<!\w)Article \d+\.?(?:\d+)?",
            r"(?<!\w)\d+\.\s+[A-Z][A-Za-z\s]+",
            r"(?<!\w)[IVXLCDM]+\.\s+[A-Z][A-Za-z\s]+",
        ]
        
        # Define key clause types by document type
        self.key_clause_types = {
            "contract": {
                "indemnification": ["indemnify", "hold harmless", "indemnification"],
                "termination": ["terminate", "termination", "expiration"],
                "payment": ["payment", "consideration", "fee", "compensation"],
                "confidentiality": ["confidential", "disclose", "proprietary", "secret"],
                "force_majeure": ["force majeure", "act of god", "beyond control"],
                "governing_law": ["govern", "jurisdiction", "venue", "law"],
            },
            "court_filing": {
                "relief_sought": ["relief", "request", "demand", "seeks", "prays"],
                "jurisdiction": ["jurisdiction", "venue", "forum"],
                "facts": ["facts", "factual", "background"],
                "legal_argument": ["argument", "assert", "contend"],
                "conclusion": ["conclusion", "wherefore", "therefore"],
            }
        }
        
        # Add default clause types for any document type
        self.default_clause_types = {
            "definitions": ["mean", "defined", "shall have the meaning", "definition"],
            "obligations": ["shall", "must", "required to", "obligation"],
            "warranties": ["warrant", "represent", "guarantee", "assure"],
            "limitations": ["limit", "limitation", "except", "exclude"]
        }
    
    def identify_key_clauses(self, text: str, document_type: str) -> List[Dict[str, Any]]:
        """
        Identify key clauses in a legal document.
        
        Args:
            text (str): The legal document text
            document_type (str): Type of legal document
            
        Returns:
            List of identified clauses with metadata
        """
        # Split text into sections
        sections = self._split_into_sections(text)
        
        # Get relevant clause types for this document
        clause_types = self.default_clause_types.copy()
        if document_type in self.key_clause_types:
            clause_types.update(self.key_clause_types[document_type])
        
        # Identify clauses
        clauses = []
        for section in sections:
            # Calculate section importance
            importance = self._calculate_section_importance(section, document_type)
            
            # Identify which clause type this section may represent
            clause_type, confidence = self._identify_clause_type(section, clause_types)
            
            # Only include sections that exceed a minimum confidence threshold
            if confidence > 0.3:
                clause_info = {
                    "title": self._extract_section_title(section),
                    "text": section,
                    "type": clause_type,
                    "confidence": confidence,
                    "importance": importance,
                    "start_char": text.find(section),
                    "end_char": text.find(section) + len(section),
                }
                clauses.append(clause_info)
        
        # Sort clauses by importance
        clauses.sort(key=lambda x: x["importance"], reverse=True)
        
        # Only return top clauses
        max_clauses = 10
        return clauses[:max_clauses]
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split document into logical sections based on section headers"""
        sections = []
        
        # Create combined regex pattern for section headers
        pattern = '|'.join(self.section_patterns)
        
        # Find all potential section headers
        matches = list(re.finditer(pattern, text))
        
        # Create sections based on header positions
        for i in range(len(matches)):
            start_pos = matches[i].start()
            if i < len(matches) - 1:
                end_pos = matches[i+1].start()
                section_text = text[start_pos:end_pos].strip()
            else:
                section_text = text[start_pos:].strip()
            
            # Add if section has sufficient content
            if len(section_text) > 20:  # Avoid empty or very short sections
                sections.append(section_text)
        
        # If no sections were found, try paragraph splitting
        if not sections:
            paragraphs = text.split('\n\n')
            sections = [p for p in paragraphs if len(p) > 100]
        
        return sections
    
    def _extract_section_title(self, section: str) -> str:
        """Extract the title from a section"""
        lines = section.split('\n')
        first_line = lines[0].strip()
        
        # If first line looks like a title (not too long, maybe has a number)
        if len(first_line) < 100 and (re.match(r'\d+\.|\([a-z]\)|[A-Z]+\.', first_line) or first_line.isupper()):
            return first_line
        
        # Try to find a title in the first sentence
        doc = self.nlp(first_line)
        sents = list(doc.sents)
        if sents and len(sents[0].text) < 100:
            return sents[0].text
        
        # Default - return beginning of section
        return first_line[:50] + "..." if len(first_line) > 50 else first_line
    
    def _calculate_section_importance(self, section: str, document_type: str) -> float:
        """Calculate the importance of a section based on content and keywords"""
        importance = 0.0
        
        # Check for important legal keywords
        legal_keywords = [
            "shall", "must", "required", "agreement", "obligation", "warranty",
            "indemnification", "termination", "material breach", "governing law"
        ]
        
        for keyword in legal_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', section.lower()):
                importance += 0.2  # Increase importance for each keyword
        
        # Check if the section contains monetary values
        if re.search(r'\$\d+|\d+ dollars|\d+ USD', section):
            importance += 0.5
        
        # Check if the section contains dates
        if re.search(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', section):
            importance += 0.3
        
        # Check if the section has legal references
        if re.search(r'U\.S\.C\.|CFR|Fed\. Reg\.', section):
            importance += 0.4
        
        return min(importance, 1.0)  # Cap at 1.0
    
    def _identify_clause_type(self, section: str, clause_types: Dict[str, List[str]]) -> tuple:
        """Identify the clause type and confidence score"""
        max_confidence = 0.0
        identified_type = "general"
        
        section_lower = section.lower()
        
        # Check for each clause type
        for clause_type, keywords in clause_types.items():
            confidence = 0.0
            for keyword in keywords:
                # Count occurrences of the keyword
                count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', section_lower))
                if count > 0:
                    # More occurrences increase confidence
                    confidence += 0.15 * min(count, 3)  # Cap at 3 occurrences
                    
                    # Title matches are stronger indicators
                    if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', section_lower[:100]):
                        confidence += 0.25
            
            if confidence > max_confidence:
                max_confidence = confidence
                identified_type = clause_type
        
        return identified_type, min(max_confidence, 1.0)  # Cap at 1.0