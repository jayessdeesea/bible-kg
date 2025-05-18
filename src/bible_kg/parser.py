"""Bible text parser module.

This module provides functionality to parse the King James Version (KJV) Bible
text file into structured verse objects.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BibleParser:
    """Parser for the KJV Bible text file.
    
    This class provides methods to parse the KJV Bible text file into structured
    verse objects, handling special formatting and extracting metadata.
    """
    
    def __init__(self, file_path: str):
        """Initialize the BibleParser.
        
        Args:
            file_path: Path to the KJV Bible text file.
        """
        self.file_path = file_path
        # Regular expression to match Bible verses in format: "Book Chapter:Verse Text"
        # This pattern captures:
        # - Book name (may contain spaces)
        # - Chapter number
        # - Verse number
        # - Verse text
        # The pattern handles both standard format and Song of Solomon format
        self.verse_pattern = re.compile(r'^([1-3]?\s*[A-Za-z]+(?:\s+[oO]f\s+[A-Za-z]+)?)\s+(\d+):(\d+)\s*(.+)$')
        
    def parse(self) -> List[Dict]:
        """Parse the KJV Bible text file into structured verse objects.
        
        Returns:
            A list of verse objects, each containing book, chapter, verse, text,
            implied_words, and reference.
        """
        verses = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                # Skip header lines (first two lines)
                next(file)
                next(file)
                
                line_count = 0
                for line in file:
                    line_count += 1
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                    
                    # Parse the line into a verse object
                    verse = self._parse_line(line)
                    if verse:
                        verses.append(verse)
                    else:
                        logger.warning(f"Failed to parse line {line_count}: {line}")
                
                logger.info(f"Successfully parsed {len(verses)} verses from {self.file_path}")
                
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            
        return verses
    
    def _parse_line(self, line: str) -> Optional[Dict]:
        """Parse a single line of text into a verse object.
        
        Args:
            line: A line of text from the KJV Bible file.
            
        Returns:
            A verse object containing book, chapter, verse, text, implied_words,
            and reference, or None if parsing fails.
        """
        match = self.verse_pattern.match(line)
        if not match:
            return None
        
        book = match.group(1).strip()
        chapter = int(match.group(2))
        verse = int(match.group(3))
        text = match.group(4).strip()
        
        # Extract implied words (words in square brackets)
        implied_words = self._extract_implied_words(text)
        
        # Create reference string (e.g., "Genesis 1:1")
        reference = f"{book} {chapter}:{verse}"
        
        return {
            'book': book,
            'chapter': chapter,
            'verse': verse,
            'text': text,
            'implied_words': implied_words,
            'reference': reference
        }
    
    def _extract_implied_words(self, text: str) -> List[str]:
        """Extract words in square brackets (implied words) from the verse text.
        
        Args:
            text: The verse text.
            
        Returns:
            A list of implied words (words in square brackets).
        """
        # Find all words in square brackets
        implied_pattern = re.compile(r'\[([^\]]+)\]')
        return implied_pattern.findall(text)


def parse_bible(file_path: str) -> List[Dict]:
    """Parse the KJV Bible text file into structured verse objects.
    
    This is a convenience function that creates a BibleParser instance
    and calls its parse method.
    
    Args:
        file_path: Path to the KJV Bible text file.
        
    Returns:
        A list of verse objects.
    """
    parser = BibleParser(file_path)
    return parser.parse()
