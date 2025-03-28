import spacy
from transformers import pipeline
from typing import List, Dict, Any

class EntityExtractor:
    """
    Extracts named entities and legal concepts from legal documents.
    """
    
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            import os
            os.system("python -m spacy download en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
            
        # Add legal entity ruler for specialized legal entities
        self._add_legal_entity_patterns()
        
        # Legal terms and their definitions
        self.legal_terminology = self._load_legal_terminology()
    
    def _add_legal_entity_patterns(self):
        """Add custom patterns for legal entity recognition"""
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "LEGAL_REFERENCE", "pattern": [{"LOWER": "section"}, {"SHAPE": "dd"}]},
            {"label": "LEGAL_REFERENCE", "pattern": [{"LOWER": "article"}, {"SHAPE": "d"}]},
            {"label": "LEGAL_REFERENCE", "pattern": [{"LOWER": "paragraph"}, {"SHAPE": "d"}]},
            {"label": "PARTY", "pattern": [{"LOWER": "plaintiff"}]},
            {"label": "PARTY", "pattern": [{"LOWER": "defendant"}]},
            {"label": "PARTY", "pattern": [{"LOWER": "appellant"}]},
            {"label": "PARTY", "pattern": [{"LOWER": "respondent"}]},
            {"label": "COURT", "pattern": [{"LOWER": "court"}, {"LOWER": "of"}, {"POS": "PROPN"}]},
            {"label": "COURT", "pattern": [{"LOWER": "supreme"}, {"LOWER": "court"}]},
            {"label": "LEGAL_TERM", "pattern": [{"LOWER": "force"}, {"LOWER": "majeure"}]},
            {"label": "LEGAL_TERM", "pattern": [{"LOWER": "mutatis"}, {"LOWER": "mutandis"}]},
            {"label": "LEGAL_TERM", "pattern": [{"LOWER": "prima"}, {"LOWER": "facie"}]},
        ]
        ruler.add_patterns(patterns)
    
    def _load_legal_terminology(self) -> Dict[str, str]:
        """Load dictionary of legal terms and definitions"""
        # In a real implementation, this would load from a database or file
        return {
            "force majeure": "Unforeseeable circumstances that prevent someone from fulfilling a contract",
            "prima facie": "Based on the first impression; accepted as correct until proved otherwise",
            "habeas corpus": "A writ requiring a person under arrest to be brought before a judge",
            "mens rea": "The intention or knowledge of wrongdoing that constitutes part of a crime",
            "pro bono": "Work undertaken without charge, especially legal work for a client with limited means",
            # More terms would be included in a real implementation
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities and legal concepts from text.
        
        Args:
            text: The legal document text
            
        Returns:
            List of extracted entities with their types, positions, and relevant information
        """
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entity = {
                "text": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
            }
            
            # Add definition for legal terms if available
            if ent.label_ == "LEGAL_TERM" and ent.text.lower() in self.legal_terminology:
                entity["definition"] = self.legal_terminology[ent.text.lower()]
            
            entities.append(entity)
        
        # Find legal references not caught by spaCy
        legal_references = self._extract_legal_references(text)
        for ref in legal_references:
            # Check if this reference overlaps with existing entities
            if not any(e["start_char"] <= ref["start_char"] <= e["end_char"] for e in entities):
                entities.append(ref)
        
        # Extract money and quantity entities
        for token in doc:
            if token.like_num and token.i < len(doc) - 1:
                next_token = doc[token.i + 1]
                if next_token.text.lower() in ["dollars", "usd", "$", "€", "euro", "euros"]:
                    entity = {
                        "text": f"{token.text} {next_token.text}",
                        "label": "MONEY",
                        "start_char": token.idx,
                        "end_char": next_token.idx + len(next_token.text),
                    }
                    entities.append(entity)
        
        return entities
    
    def _extract_legal_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract legal references from text using regex patterns"""
        import re
        
        references = []
        
        # Pattern for case citations (e.g., "Smith v. Jones, 123 F.3d 456 (9th Cir. 1990)")
        case_pattern = r'([A-Z][a-z]+)\s+v\.\s+([A-Z][a-z]+),\s+(\d+\s+[A-Za-z.]+\s+\d+\s+\([A-Za-z0-9.]+\s+\d{4}\))'
        for match in re.finditer(case_pattern, text):
            references.append({
                "text": match.group(0),
                "label": "CASE_CITATION",
                "start_char": match.start(),
                "end_char": match.end(),
                "plaintiff": match.group(1),
                "defendant": match.group(2),
            })
        
        # Pattern for statutory citations (e.g., "42 U.S.C. § 1983")
        statute_pattern = r'(\d+)\s+([A-Z]\.[A-Z]\.[A-Z]\.)\s+§\s+(\d+(?:\([a-z]\))?)'
        for match in re.finditer(statute_pattern, text):
            references.append({
                "text": match.group(0),
                "label": "STATUTE_CITATION",
                "start_char": match.start(),
                "end_char": match.end(),
                "title": match.group(1),
                "code": match.group(2),
                "section": match.group(3),
            })
        
        return references