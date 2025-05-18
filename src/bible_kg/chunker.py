"""Bible text chunking module.

This module provides functionality to chunk the parsed Bible verses into logical
passages and sliding window chunks, implementing a hybrid chunking strategy.
"""

import logging
from typing import Dict, List, Tuple, Any
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BibleChunker:
    """Chunker for Bible verses.
    
    This class implements a hybrid chunking strategy that combines passage-level
    chunking and sliding window chunking.
    """
    
    def __init__(
        self, 
        verses: List[Dict],
        window_size: int = 7,
        overlap_percentage: float = 0.5,
        max_passage_size: int = 15
    ):
        """Initialize the BibleChunker.
        
        Args:
            verses: List of parsed verse objects.
            window_size: Size of the sliding window in verses.
            overlap_percentage: Percentage of overlap between adjacent windows.
            max_passage_size: Maximum size of a passage chunk before applying
                sliding window.
        """
        self.verses = verses
        self.window_size = window_size
        self.overlap_percentage = overlap_percentage
        self.max_passage_size = max_passage_size
        
        # Calculate step size for sliding window
        self.step_size = max(1, int(window_size * (1 - overlap_percentage)))
        
        # Group verses by book and chapter for easier access
        self.verses_by_book_chapter = self._group_verses_by_book_chapter()
        
    def _group_verses_by_book_chapter(self) -> Dict[str, Dict[int, List[Dict]]]:
        """Group verses by book and chapter.
        
        Returns:
            A nested dictionary with books as keys, chapters as sub-keys,
            and lists of verses as values.
        """
        grouped = {}
        
        for verse in self.verses:
            book = verse['book']
            chapter = verse['chapter']
            
            if book not in grouped:
                grouped[book] = {}
                
            if chapter not in grouped[book]:
                grouped[book][chapter] = []
                
            grouped[book][chapter].append(verse)
            
        # Sort verses by verse number within each chapter
        for book in grouped:
            for chapter in grouped[book]:
                grouped[book][chapter].sort(key=lambda v: v['verse'])
                
        return grouped
    
    def create_chunks(self) -> List[Dict]:
        """Create chunks using the hybrid approach.
        
        Returns:
            A list of chunk objects, each containing verses, reference, and text.
        """
        # First, create passage-level chunks
        passage_chunks = self._create_passage_chunks()
        logger.info(f"Created {len(passage_chunks)} passage-level chunks")
        
        # Apply sliding window to large passages
        final_chunks = []
        large_passages = 0
        
        for chunk in passage_chunks:
            if len(chunk['verses']) <= self.max_passage_size:
                final_chunks.append(chunk)
            else:
                large_passages += 1
                # Apply sliding window to this large passage
                sliding_chunks = self._create_sliding_window_chunks(chunk['verses'])
                final_chunks.extend(sliding_chunks)
        
        logger.info(f"Applied sliding window to {large_passages} large passages")
        logger.info(f"Final chunk count: {len(final_chunks)}")
        
        return final_chunks
    
    def _create_passage_chunks(self) -> List[Dict]:
        """Create chunks based on logical passages.
        
        This method groups verses into logical passages based on narrative
        coherence and traditional passage divisions.
        
        Returns:
            A list of passage chunk objects.
        """
        passage_chunks = []
        current_passage = []
        current_book = None
        current_chapter = None
        
        # Process verses in order
        for book in sorted(self.verses_by_book_chapter.keys()):
            for chapter in sorted(self.verses_by_book_chapter[book].keys()):
                verses = self.verses_by_book_chapter[book][chapter]
                
                for verse in verses:
                    # Check for passage boundary
                    if self._is_passage_boundary(verse, current_book, current_chapter, current_passage):
                        # Complete current passage if it's not empty
                        if current_passage:
                            chunk = self._create_chunk_from_verses(current_passage)
                            passage_chunks.append(chunk)
                            current_passage = []
                    
                    # Add verse to current passage
                    current_passage.append(verse)
                    current_book = verse['book']
                    current_chapter = verse['chapter']
                
                # Complete passage at end of chapter
                if current_passage:
                    chunk = self._create_chunk_from_verses(current_passage)
                    passage_chunks.append(chunk)
                    current_passage = []
        
        # Handle any remaining verses
        if current_passage:
            chunk = self._create_chunk_from_verses(current_passage)
            passage_chunks.append(chunk)
        
        return passage_chunks
    
    def _is_passage_boundary(
        self, 
        verse: Dict, 
        current_book: str, 
        current_chapter: int,
        current_passage: List[Dict]
    ) -> bool:
        """Determine if a verse represents a passage boundary.
        
        Args:
            verse: The current verse.
            current_book: The book of the previous verse.
            current_chapter: The chapter of the previous verse.
            current_passage: The current passage being built.
            
        Returns:
            True if the verse represents a passage boundary, False otherwise.
        """
        # Always start a new passage for a new book
        if current_book is not None and verse['book'] != current_book:
            return True
        
        # Always start a new passage for a new chapter
        if current_chapter is not None and verse['chapter'] != current_chapter:
            return True
        
        # If this is the first verse, it's not a boundary
        if not current_passage:
            return False
        
        # Check for narrative or thematic shifts
        # This is a simplified approach - in a real implementation, this would
        # involve more sophisticated analysis of the text
        
        # Check for verse 1, which often starts a new passage
        if verse['verse'] == 1:
            return True
        
        # Check for common passage boundary indicators in the text
        boundary_phrases = [
            "And it came to pass",
            "Now it came to pass",
            "After these things",
            "Then",
            "Behold",
            "Verily, verily",
            "Thus saith the Lord"
        ]
        
        for phrase in boundary_phrases:
            if verse['text'].startswith(phrase):
                return True
        
        return False
    
    def _create_sliding_window_chunks(self, verses: List[Dict]) -> List[Dict]:
        """Create overlapping chunks using sliding window approach.
        
        Args:
            verses: List of verses to chunk.
            
        Returns:
            A list of sliding window chunk objects.
        """
        chunks = []
        
        # Apply sliding window
        for i in range(0, len(verses), self.step_size):
            window = verses[i:i + self.window_size]
            
            # Only create a chunk if we have at least 2 verses
            if len(window) >= 2:
                chunk = self._create_chunk_from_verses(window)
                chunks.append(chunk)
        
        return chunks
    
    def _create_chunk_from_verses(self, verses: List[Dict]) -> Dict:
        """Create a chunk object from a list of verses.
        
        Args:
            verses: List of verses to include in the chunk.
            
        Returns:
            A chunk object containing verses, reference, and text.
        """
        if not verses:
            raise ValueError("Cannot create a chunk from an empty list of verses")
        
        # Sort verses by book, chapter, and verse
        sorted_verses = sorted(
            verses, 
            key=lambda v: (v['book'], v['chapter'], v['verse'])
        )
        
        # Create reference string
        first_verse = sorted_verses[0]
        last_verse = sorted_verses[-1]
        
        if first_verse['book'] == last_verse['book']:
            if first_verse['chapter'] == last_verse['chapter']:
                # Same book, same chapter
                reference = f"{first_verse['book']} {first_verse['chapter']}:{first_verse['verse']}-{last_verse['verse']}"
            else:
                # Same book, different chapters
                reference = f"{first_verse['book']} {first_verse['chapter']}:{first_verse['verse']}-{last_verse['chapter']}:{last_verse['verse']}"
        else:
            # Different books
            reference = f"{first_verse['reference']}-{last_verse['reference']}"
        
        # Combine verse texts
        text = " ".join([verse['text'] for verse in sorted_verses])
        
        # Create chunk ID
        chunk_id = reference.lower().replace(" ", "_").replace(":", "_").replace("-", "_")
        
        return {
            'chunk_id': chunk_id,
            'verses': sorted_verses,
            'reference': reference,
            'text': text,
            'metadata': {
                'book': first_verse['book'],
                'start_chapter': first_verse['chapter'],
                'start_verse': first_verse['verse'],
                'end_chapter': last_verse['chapter'],
                'end_verse': last_verse['verse'],
                'verse_count': len(sorted_verses)
            }
        }
    
    def save_chunks(self, chunks: List[Dict], output_path: str) -> None:
        """Save chunks to a JSON file.
        
        Args:
            chunks: List of chunk objects to save.
            output_path: Path to save the chunks to.
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert to serializable format
        serializable_chunks = []
        for chunk in chunks:
            serializable_chunk = {
                'chunk_id': chunk['chunk_id'],
                'reference': chunk['reference'],
                'text': chunk['text'],
                'metadata': chunk['metadata'],
                'verses': [
                    {
                        'reference': verse['reference'],
                        'text': verse['text']
                    }
                    for verse in chunk['verses']
                ]
            }
            serializable_chunks.append(serializable_chunk)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_chunks, f, indent=2)
            
        logger.info(f"Saved {len(chunks)} chunks to {output_path}")


def create_chunks(
    verses: List[Dict],
    window_size: int = 7,
    overlap_percentage: float = 0.5,
    max_passage_size: int = 15
) -> List[Dict]:
    """Create chunks from parsed Bible verses.
    
    This is a convenience function that creates a BibleChunker instance
    and calls its create_chunks method.
    
    Args:
        verses: List of parsed verse objects.
        window_size: Size of the sliding window in verses.
        overlap_percentage: Percentage of overlap between adjacent windows.
        max_passage_size: Maximum size of a passage chunk before applying
            sliding window.
            
    Returns:
        A list of chunk objects.
    """
    chunker = BibleChunker(
        verses=verses,
        window_size=window_size,
        overlap_percentage=overlap_percentage,
        max_passage_size=max_passage_size
    )
    return chunker.create_chunks()
