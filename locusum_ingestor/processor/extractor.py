
import trafilatura
from loguru import logger

def extract_content(html: str) -> str:
    """
    Extracts main content from raw HTML using Trafilatura.
    Returns cleaned text string.
    """
    if not html:
        return ""
        
    try:
        # include_comments=False, include_tables=True
        text = trafilatura.extract(html, include_comments=False, include_tables=True, no_fallback=False)
        if text:
            return text
        else:
            return ""
    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        return ""
