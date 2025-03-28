from transformers import BartForConditionalGeneration, BartTokenizer, pipeline
import torch
import spacy
from typing import List, Dict, Any, Optional

class Summarizer:
    """
    Handles generation of summaries from legal documents using
    both extractive and abstractive summarization techniques.
    """
    
    def __init__(self):
        # Initialize BART model for abstractive summarization
        self.tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # Initialize spaCy for text processing
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            # If model not installed, download it
            import os
            os.system("python -m spacy download en_core_web_lg")
            self.nlp = spacy.load("en_core_web_lg")
    
    def generate_summary(self, text: str, max_length: int = 500, focus_areas: Optional[List[str]] = None) -> str:
        """
        Generate a summary of the legal document.
        
        Args:
            text (str): The text to summarize
            max_length (int): Maximum length of the summary in words
            focus_areas (List[str], optional): Areas to focus on in the summary
            
        Returns:
            str: The generated summary
        """
        # Preprocess: break long text into manageable chunks
        chunks = self._chunk_text(text)
        
        # Generate summary for each chunk
        chunk_summaries = []
        for chunk in chunks:
            chunk_summaries.append(self._summarize_chunk(chunk))
        
        # Combine chunk summaries
        combined_summary = " ".join(chunk_summaries)
        
        # If focus areas are specified, extract relevant information
        if focus_areas:
            focused_summary = self._focus_summary(combined_summary, focus_areas)
            return focused_summary
        
        return combined_summary
    
    def _chunk_text(self, text: str, max_chunk_length: int = 1024) -> List[str]:
        """Break text into manageable chunks for the model"""
        # Use spaCy to split into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            # Tokenize to estimate token count
            tokens = self.tokenizer(sentence, return_tensors="pt", truncation=False)
            sentence_length = len(tokens.input_ids[0])
            
            if current_length + sentence_length > max_chunk_length:
                # Start new chunk if adding this sentence would exceed max length
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _summarize_chunk(self, text: str) -> str:
        """Generate summary for a single chunk of text"""
        inputs = self.tokenizer(text, max_length=1024, return_tensors="pt", truncation=True).to(self.device)
        
        # Generate summary
        summary_ids = self.model.generate(
            inputs.input_ids,
            max_length=150,
            min_length=40,
            length_penalty=2.0,
            num_beams=4,
            early_stopping=True
        )
        
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary
    
    def _focus_summary(self, summary: str, focus_areas: List[str]) -> str:
        """Filter or enhance summary to focus on specific areas"""
        # Create spaCy document
        doc = self.nlp(summary)
        
        # Extract sentences containing focus areas
        focused_sentences = []
        for sent in doc.sents:
            for area in focus_areas:
                if area.lower() in sent.text.lower():
                    focused_sentences.append(sent.text)
                    break
        
        if focused_sentences:
            return " ".join(focused_sentences)
        else:
            # If no sentences match focus areas, return the original summary
            return summary