import os
import time
import threading
import shutil
from typing import List, Optional, Callable
try:
    from pdf2zh.pdf2zh import extract_text as pdf2zh_translate
except ImportError:
    # Fallback or error handling if import fails differently
    raise ImportError("Could not import extract_text from pdf2zh.pdf2zh. Please ensure pdf2zh is installed correctly.")

class PDFTranslator:
    """
    Wrapper for pdf2zh library to handle PDF translation tasks.
    """
    def __init__(self, output_dir: str = "output"):
        self.output_dir = os.path.abspath(output_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def translate_files(
        self, 
        files: List[str], 
        service: str = "google",
        lang_in: str = "en", 
        lang_out: str = "zh",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> List[str]:
        """
        Translate a list of PDF files.
        
        Args:
            files: List of file paths to translate.
            service: Translation service ('google', 'deepl', 'openai', etc.).
            lang_in: Source language code.
            lang_out: Target language code.
            api_key: API Key for services like OpenAI or DeepL.
            base_url: Custom API Base URL (e.g. for OpenAI proxy).
            progress_callback: Function to call with (message, progress_percentage).
            
        Returns:
            List of paths to translated files.
        """
        translated_files = []
        total_files = len(files)
        
        # Set environment variables for API keys if provided
        if api_key:
            if service == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
                if base_url:
                    os.environ["OPENAI_API_BASE"] = base_url
            elif service == "deepl":
                os.environ["DEEPL_AUTH_KEY"] = api_key
        
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            
            # Calculate current progress (start of file)
            current_progress = int((idx / total_files) * 100)
            
            if progress_callback:
                progress_callback(f"Translating {idx + 1}/{total_files}: {filename}", current_progress)
            
            try:
                # Check if file exists
                if not os.path.exists(file_path):
                    if progress_callback:
                        progress_callback(f"Error: File not found: {file_path}")
                    continue
                
                # Get absolute path
                abs_file_path = os.path.abspath(file_path)
                
                # Change CWD to output directory because pdf2zh outputs to CWD
                original_cwd = os.getcwd()
                os.chdir(self.output_dir)
                
                # Map 'zh' to 'zh-CN' for better compatibility
                if lang_out == "zh":
                    lang_out = "zh-CN"
                
                print(f"Debug: calling pdf2zh with service={service}, lang_in={lang_in}, lang_out={lang_out}")

                try:
                    # Call pdf2zh extract_text function
                    # It generates {filename}-zh.pdf and {filename}-dual.pdf in CWD
                    pdf2zh_translate(
                        files=[abs_file_path],
                        service=service,
                        lang_in=lang_in,
                        lang_out=lang_out,
                        thread=4
                    )
                except Exception as e:
                    print(f"Error in pdf2zh_translate: {e}")
                    # Capture inner exception from pdf2zh
                    raise e
                finally:
                    os.chdir(original_cwd)
                
                # Construct expected output filename
                # pdf2zh usually appends -zh.pdf or -dual.pdf
                # We prioritize the dual version if available, or the translated version
                name, ext = os.path.splitext(filename)
                
                # Check for possible output names
                # pdf2zh seems to use -zh.pdf hardcoded or based on lang?
                # We check multiple patterns
                candidates = [
                    os.path.join(self.output_dir, f"{name}-dual.pdf"),
                    os.path.join(self.output_dir, f"{name}-zh.pdf"),
                    os.path.join(self.output_dir, f"{name}-{lang_out}.pdf"),
                    os.path.join(self.output_dir, f"{name}_zh.pdf"), # Some versions might use underscore
                ]
                
                found = False
                for expected_output in candidates:
                    if os.path.exists(expected_output):
                        translated_files.append(expected_output)
                        found = True
                        break
                
                if progress_callback:
                    # Update progress after file completion
                    completed_progress = int(((idx + 1) / total_files) * 100)
                    progress_callback(f"Completed: {filename}", completed_progress)

                if not found:
                    if progress_callback:
                        progress_callback(f"Warning: Output file not found for {filename}. Checked: {', '.join([os.path.basename(c) for c in candidates])}")
                        
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error translating {filename}: {str(e)}")
        
        return translated_files

class TranslationWorker(threading.Thread):
    """
    Worker thread to run translation in background.
    """
    def __init__(
        self, 
        translator: PDFTranslator, 
        files: List[str], 
        service: str, 
        lang_in: str,
        lang_out: str,
        api_key: str,
        base_url: str,
        callback: Callable[[str, int], None],
        finished_callback: Callable[[], None]
    ):
        super().__init__()
        self.translator = translator
        self.files = files
        self.service = service
        self.lang_in = lang_in
        self.lang_out = lang_out
        self.api_key = api_key
        self.base_url = base_url
        self.callback = callback
        self.finished_callback = finished_callback
        self._stop_event = threading.Event()

    def run(self):
        self.translator.translate_files(
            self.files, 
            service=self.service, 
            lang_in=self.lang_in,
            lang_out=self.lang_out,
            api_key=self.api_key,
            base_url=self.base_url,
            progress_callback=self.callback
        )
        if self.finished_callback:
            self.finished_callback()

    def stop(self):
        self._stop_event.set()
