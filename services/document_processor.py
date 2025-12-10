import base64

class DocumentProcessor:
    """
    Prepares files for Gemini Native Multimodality.
    """
    
    # Supported by Gemini 1.5
    SUPPORTED_MIMES = {
        "application/pdf": "application/pdf",
        "image/png": "image/png",
        "image/jpeg": "image/jpeg",
        "image/webp": "image/webp",
        "image/heic": "image/heic"
    }

    def process(self, uploaded_file) -> dict:
        """
        Reads bytes and returns base64 payload.
        """
        if not uploaded_file:
            return {"error": "No file provided"}
            
        mime = uploaded_file.type
        
        # Validation
        if mime not in self.SUPPORTED_MIMES:
             return {"error": f"Unsupported file type: {mime}. Supported: {list(self.SUPPORTED_MIMES.keys())}"}

        try:
            # Read bytes
            uploaded_file.seek(0)
            bytes_data = uploaded_file.read()
            b64_data = base64.b64encode(bytes_data).decode("utf-8")
            
            return {
                "mime_type": mime,
                "data": b64_data
            }
        except Exception as e:
            return {"error": f"Failed to process file: {str(e)}"}