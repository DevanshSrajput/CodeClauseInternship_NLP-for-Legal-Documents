import streamlit as st
import tempfile
import os
import uuid
from backend.processors.document_processor import DocumentProcessor
from backend.database.db_handler import db_handler

# Set page configuration
st.set_page_config(
    page_title="Upload Document - LegalEase",
    page_icon="⚖️",
    layout="wide",
)

# Initialize document processor
document_processor = DocumentProcessor()

# Page header
st.title("📄 Upload Legal Document")
st.markdown("Upload your legal documents for analysis. Supported formats: PDF, DOCX, TXT.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    # Display file info
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB",
        "File type": uploaded_file.type
    }
    
    st.write("File Details:", file_details)
    
    # Process document button
    if st.button("Process Document"):
        with st.spinner("Processing document..."):
            try:
                # Create a unique ID for the document
                document_id = str(uuid.uuid4())
                
                # Extract text from document
                content = uploaded_file.getvalue()
                document_text = document_processor.extract_text(content, uploaded_file.name)
                
                # Preprocess text
                document_text = document_processor.preprocess_text(document_text)
                
                # Save document to database
                doc_info = {
                    "id": document_id,
                    "filename": uploaded_file.name,
                    "content": document_text,
                    "upload_date": db_handler.get_current_time()
                }
                db_handler.save_document(doc_info)
                
                # Success message
                st.success(f"Document processed successfully!")
                
                # Create columns for buttons
                col1, col2 = st.columns(2)
                
                # View document button
                with col1:
                    # Use markdown link instead of page_link
                    st.markdown(f"[View Document](/Document_View?doc_id={document_id})")
                
                # Analyze document button
                with col2:
                    st.markdown(f"[Analyze Document](/Document_View?doc_id={document_id}&analyze=true)")
                    
                # Show preview
                with st.expander("Document Preview"):
                    st.text_area("Document content", document_text[:5000] + ("..." if len(document_text) > 5000 else ""), 
                                height=300)
                
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
                st.exception(e)

# Document guidelines
st.markdown("---")
st.subheader("Guidelines for Document Upload")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Supported Documents
    - **Contracts and Agreements**
    - **Legal Opinions**
    - **Court Filings**
    - **Legislation**
    """)

with col2:
    st.markdown("""
    ### Best Practices
    - Ensure documents are properly scanned and OCRed
    - Upload text-searchable PDFs for best results
    - Maximum file size: 15MB
    """)

# Add example document download
st.markdown("---")
st.subheader("Try with an Example Document")
st.markdown("Don't have a legal document ready? Download our sample document to test the system.")

if st.button("Download Sample Contract"):
    # In a real application, you would provide a link to a sample document
    st.markdown("Sample document would download here.")