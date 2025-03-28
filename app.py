import streamlit as st
import os
import pandas as pd
from backend.database.db_handler import db_handler

# Set page configuration
st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure data directories exist
os.makedirs("data/documents", exist_ok=True)
os.makedirs("data/analyses", exist_ok=True)

# Application header and description
st.title("⚖️ LegalEase: AI Legal Document Analyzer")
st.markdown("""
LegalEase helps you extract key information from complex legal documents. 
Upload your legal documents and let our AI analyze them to provide summaries, 
identify important clauses, and extract key entities.
""")

# Display recently analyzed documents
st.subheader("Recent Documents")

# Get list of documents from database
documents = db_handler.list_documents()

if not documents:
    st.info("No documents have been uploaded yet. Go to the Upload page to add documents.")
else:
    # Create a dataframe for display
    doc_df = pd.DataFrame([
        {
            "Filename": doc['filename'],
            "Upload Date": doc['upload_date'].split('T')[0],
            "Document ID": doc['id']
        } for doc in documents[:5]  # Show only the 5 most recent
    ])
    
    # Use simple dataframe display
    st.dataframe(doc_df, height=200)
    
    # Add a view button for each document
    selected_doc_id = st.selectbox("Select a document to view:", 
                                  options=[doc['id'] for doc in documents],
                                  format_func=lambda x: next((doc['filename'] for doc in documents if doc['id'] == x), x))
    
    if selected_doc_id:
        # Use markdown link instead of page_link
        st.markdown(f"[View Document Analysis](/Document_View?doc_id={selected_doc_id})")

# Quick actions section
st.subheader("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📄 Upload New Document"):
        # Try to use switch_page if available, otherwise fall back to markdown
        try:
            st.switch_page("pages/1_Upload.py")
        except:
            st.markdown('[Go to Upload Page](/Upload)', unsafe_allow_html=True)

with col2:
    if st.button("📋 Browse All Documents"):
        try:
            st.switch_page("pages/2_Document_View.py")
        except:
            st.markdown('[Go to Document View](/Document_View)', unsafe_allow_html=True)

with col3:
    if st.button("ℹ️ About LegalEase"):
        try:
            st.switch_page("pages/3_About.py")
        except:
            st.markdown('[Go to About Page](/About)', unsafe_allow_html=True)

# Add helpful information at the bottom
st.markdown("---")
st.markdown("""
### 🔍 How It Works

1. **Upload** - Upload your legal documents (PDF, DOCX, TXT)
2. **Analyze** - Our AI analyzes the content to extract key information
3. **Review** - View summaries, key clauses, and extracted entities

### 📝 Features

- Document summarization
- Legal entity extraction
- Key clause identification
- Document type classification
""")