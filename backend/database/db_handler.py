import os
import json
import datetime
from typing import Dict, List, Any, Optional

class DatabaseHandler:
    """
    Simple file-based database handler for storing documents and analyses.
    In a production environment, this would be replaced with a proper database.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.documents_dir = os.path.join(data_dir, "documents")
        self.analyses_dir = os.path.join(data_dir, "analyses")
        
        # Create directories if they don't exist
        os.makedirs(self.documents_dir, exist_ok=True)
        os.makedirs(self.analyses_dir, exist_ok=True)
    
    def save_document(self, document: Dict[str, Any]) -> str:
        """
        Save a document to the database
        
        Args:
            document: Dictionary containing document data
            
        Returns:
            Document ID
        """
        document_id = document.get("id")
        
        # Create metadata and content files
        metadata = document.copy()
        # Store content separately to avoid large metadata files
        content = metadata.pop("content")
        
        # Save metadata
        metadata_path = os.path.join(self.documents_dir, f"{document_id}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save content
        content_path = os.path.join(self.documents_dir, f"{document_id}.txt")
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return document_id
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        metadata_path = os.path.join(self.documents_dir, f"{document_id}.json")
        content_path = os.path.join(self.documents_dir, f"{document_id}.txt")
        
        # Check if document exists
        if not os.path.exists(metadata_path) or not os.path.exists(content_path):
            return None
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            document = json.load(f)
        
        # Load content
        with open(content_path, 'r', encoding='utf-8') as f:
            document["content"] = f.read()
        
        return document
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents (without content)"""
        documents = []
        
        for filename in os.listdir(self.documents_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.documents_dir, filename)
                with open(file_path, 'r') as f:
                    document = json.load(f)
                    documents.append(document)
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x.get("upload_date", ""), reverse=True)
        
        return documents
    
    def save_analysis(self, document_id: str, analysis: Dict[str, Any]) -> None:
        """Save analysis results for a document"""
        analysis_path = os.path.join(self.analyses_dir, f"{document_id}.json")
        
        # Add timestamp to analysis
        analysis["timestamp"] = self.get_current_time()
        
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
    
    def get_analysis(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis for a document"""
        analysis_path = os.path.join(self.analyses_dir, f"{document_id}.json")
        
        if not os.path.exists(analysis_path):
            return None
        
        with open(analysis_path, 'r') as f:
            return json.load(f)
    
    def get_current_time(self) -> str:
        """Get current time in ISO format"""
        return datetime.datetime.now().isoformat()


# Singleton instance
db_handler = DatabaseHandler()