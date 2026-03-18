#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - HELPER FUNCTIONS
=============================================================================
- Fungsi-fungsi utilitas umum
- Text processing
- Validation
- Formatting
"""

import re
import time
import random
import string
import hashlib
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import datetime, timedelta
import unicodedata


# =============================================================================
# TEXT PROCESSING
# =============================================================================

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize input text untuk keamanan
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
        
    # Trim whitespace
    text = text.strip()
    
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
        
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to max length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    return text[:max_length - len(suffix)] + suffix


def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords
        
    Returns:
        List of keywords
    """
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    
    # Split into words
    words = text.split()
    
    # Filter by length and common words
    common_words = {'yang', 'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'aku', 'kamu',
                    'adalah', 'untuk', 'dengan', 'pada', 'dalam', 'akan', 'tidak'}
    
    keywords = [w for w in words if len(w) >= min_length and w not in common_words]
    
    # Remove duplicates, preserve order
    seen = set()
    unique_keywords = []
    for word in keywords:
        if word not in seen:
            seen.add(word)
            unique_keywords.append(word)
            
    return unique_keywords[:max_keywords]


def similarity_score(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts (0-1)
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score
    """
    # Simple Jaccard similarity on word sets
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
        
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


# =============================================================================
# FORMATTING
# =============================================================================

def format_number(num: Union[int, float], decimals: int = 1) -> str:
    """
    Format number with K/M/B suffix
    
    Args:
        num: Number to format
        decimals: Number of decimals
        
    Returns:
        Formatted string
    """
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.{decimals}f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M"
    elif num >= 1_000:
        return f"{num/1_000:.{decimals}f}K"
    else:
        return str(num)


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2h 30m")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"
    else:
        days = int(seconds / 86400)
        hours = int((seconds % 86400) / 3600)
        return f"{days}d {hours}h"


def time_ago(timestamp: float) -> str:
    """
    Format timestamp as time ago
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        String like "2 hours ago"
    """
    diff = time.time() - timestamp
    
    if diff < 60:
        return "just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff < 604800:
        days = int(diff / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    else:
        weeks = int(diff / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"


def calculate_age(birth_year: int) -> int:
    """
    Calculate age from birth year
    
    Args:
        birth_year: Birth year
        
    Returns:
        Age
    """
    current_year = datetime.now().year
    return current_year - birth_year


# =============================================================================
# ID GENERATION
# =============================================================================

def generate_temp_id(prefix: str = "TMP") -> str:
    """
    Generate temporary ID
    
    Args:
        prefix: ID prefix
        
    Returns:
        Temporary ID
    """
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_str}"


def generate_hash(text: str) -> str:
    """
    Generate SHA-256 hash of text
    
    Args:
        text: Input text
        
    Returns:
        Hash string
    """
    return hashlib.sha256(text.encode()).hexdigest()


# =============================================================================
# COMMAND PARSING
# =============================================================================

def parse_command_args(text: str) -> Tuple[str, List[str]]:
    """
    Parse command and arguments
    
    Args:
        text: Full command text (e.g., "/command arg1 arg2")
        
    Returns:
        Tuple of (command, args_list)
    """
    parts = text.strip().split()
    
    if not parts:
        return "", []
        
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    return command, args


def parse_hts_call(text: str) -> Optional[Union[int, str]]:
    """
    Parse /hts- call
    
    Args:
        text: Command text
        
    Returns:
        Index (int) or role name (str) or None
    """
    # Format: /hts-1 or /hts- ipar
    match = re.match(r'^/hts-[\s]*(\d+)$', text)
    if match:
        return int(match.group(1))
        
    match = re.match(r'^/hts-[\s]*([a-z_]+)$', text)
    if match:
        return match.group(1)
        
    return None


def parse_continue_call(text: str) -> Optional[Union[int, str]]:
    """
    Parse /continue call
    
    Args:
        text: Command text
        
    Returns:
        Index (int) or session ID (str) or None
    """
    # Format: /continue 1 or /continue MYLOVE-...
    match = re.match(r'^/continue[\s]+(\d+)$', text)
    if match:
        return int(match.group(1))
        
    match = re.match(r'^/continue[\s]+([A-Z0-9-]+)$', text)
    if match:
        return match.group(1)
        
    return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_role(role: str) -> bool:
    """
    Validate role name
    
    Args:
        role: Role name
        
    Returns:
        True if valid
    """
    valid_roles = [
        'ipar', 'janda', 'pelakor', 'istri_orang',
        'pdkt', 'sepupu', 'teman_kantor', 'teman_sma', 'mantan'
    ]
    return role.lower() in valid_roles


def validate_intimacy_level(level: int) -> bool:
    """
    Validate intimacy level
    
    Args:
        level: Intimacy level
        
    Returns:
        True if valid
    """
    return 1 <= level <= 12


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format
    
    Args:
        session_id: Session ID
        
    Returns:
        True if valid format
    """
    # Format: MYLOVE-ROLE-USER-DATE-SEQ
    pattern = r'^MYLOVE-[A-Z]+-\d+-\d{8}-\d{3}$'
    return bool(re.match(pattern, session_id))


# =============================================================================
# RANDOM GENERATORS
# =============================================================================

def random_percentage() -> int:
    """Generate random percentage (0-100)"""
    return random.randint(0, 100)


def random_choice_weighted(items: List[Any], weights: List[float]) -> Any:
    """
    Choose random item with weights
    
    Args:
        items: List of items
        weights: List of weights
        
    Returns:
        Selected item
    """
    return random.choices(items, weights=weights, k=1)[0]


def random_sentence(words: List[str], min_words: int = 3, max_words: int = 8) -> str:
    """
    Generate random sentence from words
    
    Args:
        words: List of words
        min_words: Minimum words
        max_words: Maximum words
        
    Returns:
        Random sentence
    """
    num_words = random.randint(min_words, min(max_words, len(words)))
    selected = random.sample(words, num_words)
    return ' '.join(selected).capitalize()


__all__ = [
    'sanitize_input',
    'truncate_text',
    'extract_keywords',
    'similarity_score',
    'format_number',
    'format_duration',
    'time_ago',
    'calculate_age',
    'generate_temp_id',
    'generate_hash',
    'parse_command_args',
    'parse_hts_call',
    'parse_continue_call',
    'validate_role',
    'validate_intimacy_level',
    'validate_session_id',
    'random_percentage',
    'random_choice_weighted',
    'random_sentence',
]
