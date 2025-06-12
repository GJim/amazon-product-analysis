"""
Utility functions for extracting data from Amazon product pages.
"""
import re
import logging
from typing import Optional, List, Dict, Any, Tuple
from bs4 import BeautifulSoup, Tag


def normalize_text(text: Optional[str]) -> str:
    """
    Normalize text by trimming leading/trailing whitespace and replacing
    multiple consecutive whitespace characters with a single space.
    
    Args:
        text: The text to normalize
        
    Returns:
        Normalized text string
    """
    if not text:
        return ""
    # Replace all whitespace sequences (spaces, tabs, newlines) with a single space
    return re.sub(r"\s+", " ", text).strip()


def extract_text_from_element(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    """
    Extract text from the first matching element using a list of CSS selectors.
    
    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try
        
    Returns:
        Normalized text if found, None otherwise
    """
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return normalize_text(element.get_text(strip=True))
    return None


def extract_elements(soup: BeautifulSoup, selectors: List[str]) -> List[Tag]:
    """
    Extract all elements matching any of the provided selectors.
    
    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try
        
    Returns:
        List of matching BeautifulSoup Tag objects
    """
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            return elements
    return []


def extract_with_regex(pattern: str, text: str, group: int = 1) -> Optional[str]:
    """
    Extract text using a regular expression pattern.
    
    Args:
        pattern: Regex pattern to use
        text: Text to search in
        group: Capture group to return (default: 1)
        
    Returns:
        Matched text if found, None otherwise
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return normalize_text(match.group(group))
    return None


def find_in_html(html_content: str, patterns: List[str]) -> Optional[str]:
    """
    Search for patterns in HTML content and return the first match.
    
    Args:
        html_content: HTML content to search
        patterns: List of regex patterns to try
        
    Returns:
        First matched text if found, None otherwise
    """
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            return normalize_text(match.group(1))
    return None


def extract_key_value_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract key-value pair from text using common separators.
    
    Args:
        text: Text to parse for key-value pair
        
    Returns:
        Tuple of (key, value) if found, (None, None) otherwise
    """
    for separator in [":", "•", "-", "–"]:
        if separator in text:
            parts = text.split(separator, 1)
            if len(parts) == 2:
                key = normalize_text(parts[0])
                value = normalize_text(parts[1])
                if key and value:
                    return key, value
    return None, None
