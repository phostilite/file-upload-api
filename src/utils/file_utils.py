import os
import re
import magic
from typing import Tuple, Dict, Any
from datetime import datetime
import uuid

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_filename(filename: str) -> str:
    """Sanitize the filename to remove any path components and non-alphanumeric characters."""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9.-]', '_', filename)
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:196] + ext
    return filename

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Get file metadata including MIME type."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    file_size = os.path.getsize(file_path)
    return {'type': file_type, 'size': file_size}

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the original extension."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    _, ext = os.path.splitext(original_filename)
    return f"{timestamp}_{unique_id}{ext}"

def validate_file_content(file_path: str) -> Tuple[bool, str]:
    """Basic file content validation."""
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        unsafe_types = {'application/x-dosexec', 'application/x-executable'}
        if file_type in unsafe_types:
            return False, "File type not allowed for security reasons"
        return True, file_type
    except Exception as e:
        return False, f"Error validating file content: {str(e)}"