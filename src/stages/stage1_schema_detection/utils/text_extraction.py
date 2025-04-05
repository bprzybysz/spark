"""
Text extraction utilities for PDF processing.
"""

import os
import re
import tempfile
import json
from typing import Dict, List, Optional, Union
import datetime

def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract simple entities from text.
    
    Args:
        text: Text to extract entities from
        
    Returns:
        Dictionary of entity types to lists of entities
    """
    entities = {
        "emails": [],
        "urls": [],
        "dates": []
    }
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, text)
    
    # Extract URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[\w=&]*)?'
    entities["urls"] = re.findall(url_pattern, text)
    
    # Extract dates (simple patterns)
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}'     # YYYY/MM/DD
    ]
    
    all_dates = []
    for pattern in date_patterns:
        all_dates.extend(re.findall(pattern, text))
    
    entities["dates"] = all_dates
    
    return entities

def calculate_text_stats(text: str) -> Dict[str, Union[int, float]]:
    """Calculate basic statistics about text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of text statistics
    """
    stats = {}
    
    # Word count
    words = re.findall(r'\w+', text)
    stats["word_count"] = len(words)
    
    # Character count
    stats["char_count"] = len(text)
    
    # Sentence count (approximate)
    sentences = re.split(r'[.!?]+', text)
    stats["sentence_count"] = len([s for s in sentences if s.strip()])
    
    # Average word length
    if words:
        stats["avg_word_length"] = sum(len(word) for word in words) / len(words)
    else:
        stats["avg_word_length"] = 0
    
    return stats 