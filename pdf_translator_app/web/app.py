import streamlit as st
import os
import tempfile
import sys
import shutil

# Ensure core modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pdf_translator_app.core.translator import PDFTranslator

# Page configuration
st.set_page_config(
    page_title="PDF Layout Translator",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #ff00ff;
        color: white;
        border-radius: 20px;
        height: 50px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #aa00ff;
        color: white;
    }
    .uploadedFile {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1 {
        color: #333;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📄 PDF Layout Translator")
    st.markdown("Translate PDF documents while preserving their original layout and formatting.")

    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings")
        
        service = st.selectbox(
            "Translation Service",
            ["google", "deepl", "openai"],
            index=0,
            help="Select the translation engine to use."
        )

        lang_in = st.selectbox(
            "Source Language",
            ["en", "zh-CN", "ja", "ko", "fr", "de", "es", "ru", "pt", "it", "auto"],
            index=0
        )

        lang_out = st.selectbox(
            "Target Language",
            ["zh-CN", "en", "ja", "ko", "fr", "de", "es", "ru", "pt", "it"],
            index=0
        )

        api_key = ""
        base_url = ""

        if service in ["deepl", "openai"]:
            api_key = st.text_input(
                "API Key", 
                type="password",
                help=f"Enter your {service} API Key"
            )
            
            if service == "openai":
                base_url = st.text_input(
                    "Base URL (Optional)",
                    help="Custom API Base URL (e.g. for proxies)"
                )

        st.info("Note: 'google' is free but may be unstable without a proxy. 'deepl' and 'openai' require API keys.")

    # Main area for file upload
    uploaded_files = st.file_uploader(
        "Upload PDF files", 
        type="pdf", 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.write(f"✅ {len(uploaded_files)} files selected")
        
        if st.button("Start Translation"):
            if service in ["deepl", "openai"] and not api_key:
                st.error(f"Please enter an API Key for {service} in the sidebar.")
            else:
                translate_files(uploaded_files, service, lang_in, lang_out, api_key, base_url)

def translate_files(uploaded_files, service, lang_in, lang_out, api_key, base_url):
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        input_files = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Save uploaded files to temp dir
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            input_files.append(file_path)
        
        # Initialize translator
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        translator = PDFTranslator(output_dir=output_dir)
        
        # Define progress callback
        total_files = len(input_files)
        
        def progress_callback(msg):
            status_text.text(msg)
            # You could parse msg to update progress bar more accurately if needed
        
        try:
            status_text.text("Initializing translation...")
            
            # Run translation
            translated_files = translator.translate_files(
                input_files,
                service=service,
                lang_in=lang_in,
                lang_out=lang_out,
                api_key=api_key,
                base_url=base_url,
                progress_callback=progress_callback
            )
            
            progress_bar.progress(100)
            status_text.text("Translation completed!")
            
            if translated_files:
                st.success(f"Successfully translated {len(translated_files)} files.")
                
                # Display download buttons for each translated file
                st.subheader("Download Translated Files")
                for file_path in translated_files:
                    file_name = os.path.basename(file_path)
                    with open(file_path, "rb") as f:
                        btn = st.download_button(
                            label=f"⬇️ Download {file_name}",
                            data=f,
                            file_name=file_name,
                            mime="application/pdf"
                        )
            else:
                st.warning("No translated files were generated. Please check the logs or try a different service.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
