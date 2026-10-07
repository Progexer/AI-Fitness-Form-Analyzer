"""
Security utilities — Supabase Auth integration and request validation.
"""

import os
import re
import uuid
import mimetypes
from pathlib import Path
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("security")

# Allowed MIME types for video uploads
ALLOWED_VIDEO_MIMES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}

# Dangerous filename patterns
DANGEROUS_PATTERNS = re.compile(r"[<>:\"/\\|?*\x00-\x1f]")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and special character attacks.
    Returns a safe filename with a UUID prefix to prevent collisions.
    """
    # Strip path components
    filename = Path(filename).name

    # Remove dangerous characters
    filename = DANGEROUS_PATTERNS.sub("_", filename)

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    # Add UUID prefix for uniqueness
    safe_name = f"{uuid.uuid4().hex[:8]}_{name}{ext}"
    return safe_name


def validate_video_file(
    filename: str,
    content_type: Optional[str],
    file_size: int,
) -> tuple[bool, Optional[str]]:
    """
    Validate an uploaded video file.
    Returns (is_valid, error_message).
    """
    settings = get_settings()

    # Check file size
    if file_size > settings.max_video_size_bytes:
        return False, f"File size ({file_size // (1024*1024)}MB) exceeds maximum allowed ({settings.MAX_VIDEO_SIZE_MB}MB)."

    if file_size == 0:
        return False, "File is empty."

    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_extensions:
        return False, f"File extension '{ext}' is not supported. Allowed: {', '.join(settings.allowed_extensions)}"

    # Check MIME type
    if content_type:
        # Normalize content type
        mime = content_type.split(";")[0].strip().lower()
        if mime not in ALLOWED_VIDEO_MIMES:
            # Try to guess from extension
            guessed_mime, _ = mimetypes.guess_type(filename)
            if guessed_mime and guessed_mime in ALLOWED_VIDEO_MIMES:
                pass  # Extension-based MIME is valid
            else:
                return False, f"MIME type '{content_type}' is not supported."

    return True, None


def validate_file_extension(filename: str, allowed_extensions: Optional[set] = None) -> bool:
    settings = get_settings()
    allowed = allowed_extensions or settings.allowed_extensions
    ext = Path(filename).suffix.lower()
    if ext not in allowed:
        raise ValueError(f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed)}")
    return True


def generate_storage_path(user_id: str, video_id: str, filename: str) -> str:
    """Generate a secure storage path for a video file."""
    safe_name = sanitize_filename(filename)
    return f"{user_id}/{video_id}/{safe_name}"


def generate_report_path(user_id: str, analysis_id: str) -> str:
    """Generate a storage path for an analysis report."""
    return f"{user_id}/{analysis_id}/report.pdf"
