#!/usr/bin/env python
"""
Bible Knowledge Graph - Test Sample Script

This script tests the parser and chunker with a small sample of the Bible.
"""

import os
import sys
import logging
import json
import time

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bible_kg.parser import parse_bible
from src.bible_kg.chunker import BibleChunker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to test the parser and chunker with a sample."""
    # Sample Bible text (first few verses of Genesis)
    sample_text = """KJV
Public Domain

Genesis 1:1 In the beginning God created the heaven and the earth.
Genesis 1:2 And the earth was without form, and void; and darkness [was] upon the face of the deep. And the Spirit of God moved upon the face of the waters.
Genesis 1:3 And God said, Let there be light: and there was light.
Genesis 1:4 And God saw the light, that [it was] good: and God divided the light from the darkness.
Genesis 1:5 And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.
Genesis 1:6 And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters.
Genesis 1:7 And God made the firmament, and divided the waters which [were] under the firmament from the waters which [were] above the firmament: and it was so.
Genesis 1:8 And God called the firmament Heaven. And the evening and the morning were the second day.
Genesis 1:9 And God said, Let the waters under the heaven be gathered together unto one place, and let the dry [land] appear: and it was so.
Genesis 1:10 And God called the dry [land] Earth; and the gathering together of the waters called he Seas: and God saw that [it was] good."""
    
    # Create a temporary file with the sample text
    sample_file = 'sample_bible.txt'
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    try:
        # Step 1: Parse the sample
        logger.info("Parsing sample Bible text")
        verses = parse_bible(sample_file)
        logger.info(f"Parsed {len(verses)} verses")
        
        # Print the first verse
        if verses:
            logger.info(f"First verse: {json.dumps(verses[0], indent=2)}")
        
        # Step 2: Create chunks
        logger.info("Creating chunks")
        chunker = BibleChunker(
            verses=verses,
            window_size=3,
            overlap_percentage=0.5,
            max_passage_size=5
        )
        chunks = chunker.create_chunks()
        logger.info(f"Created {len(chunks)} chunks")
        
        # Print the first chunk
        if chunks:
            # Convert to a more readable format
            readable_chunk = {
                'chunk_id': chunks[0]['chunk_id'],
                'reference': chunks[0]['reference'],
                'text': chunks[0]['text'],
                'metadata': chunks[0]['metadata'],
                'verses': [
                    {
                        'reference': verse['reference'],
                        'text': verse['text']
                    }
                    for verse in chunks[0]['verses']
                ]
            }
            logger.info(f"First chunk: {json.dumps(readable_chunk, indent=2)}")
        
        logger.info("Test completed successfully")
        
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)

if __name__ == '__main__':
    main()
