import streamlit as st
import requests
import json
from PIL import Image
import pandas as pd
import io

# Config
API_URL = "http://127.0.0.1:8001/api/v1/process"
st.set_page_config(page_title="Offline OCR Engine", layout="wide")

st.title("📄 Offline Document Intelligence Engine")

st.sidebar.header("Processing Options")
process_mode = st.sidebar.selectbox("Mode", ["Auto", "Invoice", "Form", "ID Card"])
debug_visuals = st.sidebar.checkbox("Show Debug Visuals", value=True)

uploaded_file = st.file_uploader("Upload Document Image", type=["jpg", "png", "jpeg", "tif"])

if uploaded_file is not None:
    # Layout: Split 50/50
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Document")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    
    with col2:
        st.subheader("Extracted Data")
        
        # Initialize session state for results if not present
        if "ocr_result" not in st.session_state:
            st.session_state.ocr_result = None
            
        
        if st.button("Run Processing Pipeline", type="primary"):
            with st.spinner("Processing (Ingest -> Vision -> OCR -> Layout -> NLP)..."):
                try:
                    # Reset pointer
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    
                    response = requests.post(API_URL, files=files)
                    
                    if response.status_code == 200:
                        st.session_state.ocr_result = response.json()
                        st.success("Processing Complete!")
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to Backend API. Is `uvicorn` running on port 8000?")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        # Display results if they exist in session state
        if st.session_state.ocr_result:
            data = st.session_state.ocr_result
            json_str = json.dumps(data, indent=2)
            
            st.download_button(
                label="📥 Download JSON Result",
                data=json_str,
                file_name="ocr_output.json",
                mime="application/json"
            )
            
            # Tabs for different result views
            tab_text, tab_json, tab_tables, tab_entities = st.tabs(["Full Text", "JSON", "Tables", "Entities"])
            
            with tab_text:
                st.text_area("Extracted Text", data["text_content"]["full_text"], height=300)
            
            with tab_json:
                st.json(data)
            
            with tab_tables:
                if data["tables"]:
                    st.success(f"Detected {len(data['tables'])} tables")
                    for i, table in enumerate(data["tables"]):
                        st.write(f"Table {i+1} (Confidence: {table['confidence']})")
                        st.code(json.dumps(table, indent=2))
                else:
                    st.info("No tables detected.")
            
            with tab_entities:
                 ents = data["entities"]
                 if ents:
                     st.write("### Recognized Entities")
                     st.write(f"**Dates:** {', '.join(ents['dates'])}")
                     st.write(f"**Amounts:** {', '.join(ents['amounts'])}")
                     st.write(f"**Emails:** {', '.join(ents['emails'])}")
                 else:
                     st.info("No named entities found.")
