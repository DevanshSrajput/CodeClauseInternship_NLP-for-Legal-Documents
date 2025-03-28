import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="About - LegalEase",
    page_icon="⚖️",
    layout="wide",
)

# Page header
st.title("ℹ️ About LegalEase")

st.markdown("""
## Project Overview

LegalEase is an AI-powered system for extracting and summarizing key legal information from complex legal documents. 
The system uses advanced NLP techniques to process legal language, identify key clauses, extract important entities, 
and generate concise summaries.

### Features

- **Document Analysis**: Extract key information from legal documents
- **Summarization**: Generate concise summaries of complex legal texts
- **Entity Extraction**: Identify important legal entities, parties, dates, and monetary values
- **Clause Identification**: Highlight and categorize important clauses by type
- **Intuitive UI**: Modern, responsive interface for document management and analysis

## Technical Implementation

LegalEase combines several technologies to provide comprehensive legal document analysis:

### Backend Components

1. **Document Processor**
   - Extracts text from various file formats (PDF, DOCX, TXT)
   - Identifies document types based on content analysis

2. **Summarizer**
   - Uses BART transformer model for abstractive summarization
   - Handles long documents by chunking text
   - Can focus on specific topics of interest

3. **Entity Extractor**
   - Extracts named entities and legal concepts using SpaCy and custom rules
   - Identifies people, organizations, locations, dates
   - Recognizes legal-specific entities like case citations and statutes

4. **Clause Identifier**
   - Identifies key clauses in legal documents
   - Categorizes clauses by type and importance
   - Extracts section titles and boundaries

### Frontend

- Built with Streamlit for a responsive, interactive user experience
- Multi-page application for document upload, viewing, and analysis

## Technologies Used

- **Python**: Core programming language
- **Streamlit**: Frontend user interface
- **SpaCy**: NLP processing and entity recognition
- **Transformers**: BART model for text summarization
- **PyMuPDF & python-docx**: Document parsing
- **scikit-learn**: Text classification and feature extraction

## Future Improvements

1. Document comparison functionality
2. Contract risk assessment
3. Legal precedent matching
4. Integration with legal databases
5. Custom model training for specific legal domains

## Credits

LegalEase was developed as an AI project to demonstrate the application of natural language 
processing techniques to the legal domain.

For more information or to contribute to the project, please contact the development team.
""")

# Add team information
st.sidebar.title("Project Information")
st.sidebar.info(
    """
    **LegalEase**  
    AI Legal Document Analyzer
    
    Version: 1.0.0
    
    [View Source Code](https://github.com/yourusername/legalease)
    """
)