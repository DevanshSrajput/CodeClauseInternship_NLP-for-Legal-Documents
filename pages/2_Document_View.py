import streamlit as st
import pandas as pd
import time
from backend.database.db_handler import db_handler
from backend.processors.summarizer import Summarizer
from backend.processors.entity_extractor import EntityExtractor
from backend.processors.clause_identifier import ClauseIdentifier

# Set page configuration
st.set_page_config(
    page_title="Document View - LegalEase",
    page_icon="⚖️",
    layout="wide",
)

# Initialize processors
summarizer = Summarizer()
entity_extractor = EntityExtractor()
clause_identifier = ClauseIdentifier()

# Initialize session state if not exists
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Get query parameters - use st.query_params
try:
    query_params = st.query_params
    doc_id = query_params.get("doc_id", None)
    analyze = query_params.get("analyze", "false") == "true"
except:
    # Fallback for older Streamlit versions
    import urllib.parse
    query_string = st.experimental_get_query_params()
    doc_id = query_string.get("doc_id", [None])[0]
    analyze = query_string.get("analyze", ["false"])[0] == "true"

# If no document_id provided, show document selection
if doc_id is None:
    st.title("📋 Document Library")
    
    # Get list of documents
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
            } for doc in documents
        ])
        
        # Use simple dataframe display
        st.dataframe(doc_df, height=300)
        
        # Add a view button for each document
        selected_doc_id = st.selectbox("Select a document to view:", 
                                      options=[doc['id'] for doc in documents],
                                      format_func=lambda x: next((doc['filename'] for doc in documents if doc['id'] == x), x))
        
        if selected_doc_id:
            # Use markdown link for compatibility
            st.markdown(f"[View Document](/Document_View?doc_id={selected_doc_id})")
else:
    # Get document from database
    document = db_handler.get_document(doc_id)
    
    if document is None:
        st.error(f"Document with ID {doc_id} not found")
        st.markdown("[Return to Document Library](/Document_View)")
    else:
        # Document found, display it
        st.title(f"📄 {document['filename']}")
        
        # Check if analysis exists for this document
        analysis = db_handler.get_analysis(doc_id)
        
        # Check if we need to refresh the page after analysis
        if st.session_state.analysis_complete:
            st.success("Analysis complete! Displaying results.")
            analysis = db_handler.get_analysis(doc_id)  # Refresh analysis
            st.session_state.analysis_complete = False
        
        # If analysis button was clicked or analyze parameter is true, run analysis
        if analysis is None and (st.button("🔍 Analyze Document") or analyze):
            with st.spinner("Analyzing document..."):
                # Get document text
                document_text = document['content']
                
                # Identify document type
                from backend.processors.document_processor import DocumentProcessor
                document_processor = DocumentProcessor()
                document_type = document_processor.identify_document_type(document_text)
                
                # Generate summary
                summary = summarizer.generate_summary(document_text)
                
                # Extract entities
                entities = entity_extractor.extract_entities(document_text)
                
                # Identify key clauses
                key_clauses = clause_identifier.identify_key_clauses(document_text, document_type)
                
                # Save analysis
                analysis_result = {
                    "document_id": doc_id,
                    "summary": summary,
                    "key_clauses": key_clauses,
                    "entities": entities,
                    "document_type": document_type
                }
                db_handler.save_analysis(doc_id, analysis_result)
                
                # Update analysis variable
                analysis = analysis_result
                st.session_state.analysis_complete = True
                
                # Try to use rerun if available, otherwise use JavaScript
                try:
                    st.rerun()
                except:
                    st.markdown(
                        """
                        <script>
                            window.location.reload();
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Create tabs for different views
        doc_tab, summary_tab, clauses_tab, entities_tab = st.tabs(["Document", "Summary", "Key Clauses", "Entities"])
        
        # Document tab
        with doc_tab:
            # Add text search functionality
            search_term = st.text_input("Search in document:")
            
            # Display document content
            if search_term:
                import re
                # Highlight search terms
                content = document['content']
                matches = list(re.finditer(search_term, content, re.IGNORECASE))
                
                if matches:
                    st.success(f"Found {len(matches)} matches")
                    # Show context around first few matches
                    for i, match in enumerate(matches[:5]):
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]
                        highlighted = context.replace(match.group(), f"**{match.group()}**")
                        st.markdown(f"Match {i+1}: ...{highlighted}...")
                else:
                    st.info("No matches found")
            
            # Always show document content
            with st.expander("Full Document", expanded=not search_term):
                st.text_area("Document Content", document['content'], height=500)
        
        # Summary tab
        with summary_tab:
            if analysis:
                st.subheader("Document Summary")
                st.write(analysis['summary'])
                
                st.subheader("Document Type")
                st.info(analysis['document_type'].replace('_', ' ').title())
            else:
                st.info("Please analyze the document to view the summary")
                if st.button("Generate Summary"):
                    # Use URL for navigation
                    st.markdown(f"[Generating Summary...](/Document_View?doc_id={doc_id}&analyze=true)")
                    # JavaScript fallback
                    st.markdown(
                        f"""
                        <script>
                            window.location.href = "/Document_View?doc_id={doc_id}&analyze=true";
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
        
        # Key clauses tab
        with clauses_tab:
            if analysis:
                st.subheader("Key Clauses")
                
                for i, clause in enumerate(analysis['key_clauses']):
                    with st.expander(f"{i+1}. {clause['title']} ({clause['type'].replace('_', ' ').title()})"):
                        st.progress(clause['importance'])
                        st.write(f"**Importance:** {int(clause['importance']*100)}%")
                        st.write(f"**Type:** {clause['type'].replace('_', ' ').title()}")
                        st.write(clause['text'])
            else:
                st.info("Please analyze the document to view key clauses")
        
        # Entities tab
        with entities_tab:
            if analysis:
                st.subheader("Legal Entities")
                
                # Filter entities by type
                entity_types = set(e['label'] for e in analysis['entities'])
                selected_type = st.selectbox("Filter by entity type:", ["All Types"] + sorted(list(entity_types)))
                
                # Create dataframe for entities
                filtered_entities = [e for e in analysis['entities'] 
                                    if selected_type == "All Types" or e['label'] == selected_type]
                
                # Group similar entities
                entity_groups = {}
                for e in filtered_entities:
                    key = (e['text'], e['label'])
                    if key in entity_groups:
                        entity_groups[key]['count'] += 1
                    else:
                        entity_groups[key] = {
                            'text': e['text'],
                            'label': e['label'],
                            'definition': e.get('definition', ''),
                            'count': 1
                        }
                
                # Convert to list
                grouped_entities = list(entity_groups.values())
                
                # Create dataframe
                if grouped_entities:
                    df = pd.DataFrame(grouped_entities)
                    # Use simple dataframe display
                    st.dataframe(df, height=400)
                    
                    # Create a simple table view as an alternative
                    st.markdown("### Entity Details")
                    for entity in grouped_entities[:10]:  # Limit to first 10
                        st.markdown(f"**{entity['text']}** ({entity['label']}) - {entity['count']} occurrences")
                        if entity['definition']:
                            st.markdown(f"*Definition:* {entity['definition']}")
                        st.markdown("---")
                else:
                    st.info(f"No entities of type '{selected_type}' found")
            else:
                st.info("Please analyze the document to view entities")     