#!/usr/bin/env python
"""
Bible Knowledge Graph - Test Context Generation Script

This script tests the context generation with the local LLM.
"""

import os
import sys
import logging
import json
import time
import requests

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bible_kg.context_gen import ContextGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_llm_availability(url: str) -> bool:
    """Check if the local LLM is available.
    
    Args:
        url: URL of the local LLM API.
        
    Returns:
        True if the LLM is available, False otherwise.
    """
    try:
        # Extract the base URL (without the endpoint)
        base_url = url.rsplit('/', 1)[0]
        
        # Check if the LLM is available
        response = requests.get(f"{base_url}/health")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def main():
    """Main function to test the context generation with the local LLM."""
    # LLM API URL
    llm_api_url = "http://localhost:11434/api/generate"
    
    # Check if the LLM is available
    logger.info(f"Checking if the local LLM is available at {llm_api_url}")
    if not check_llm_availability(llm_api_url):
        logger.error("Local LLM is not available. Make sure it's running on port 11434.")
        return
    
    logger.info("Local LLM is available")
    
    # Sample chunk
    sample_chunk = {
        'chunk_id': 'genesis_1_1-5',
        'reference': 'Genesis 1:1-5',
        'text': 'In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters. And God said, Let there be light: and there was light. And God saw the light, that it was good: and God divided the light from the darkness. And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.',
        'metadata': {
            'book': 'Genesis',
            'start_chapter': 1,
            'start_verse': 1,
            'end_chapter': 1,
            'end_verse': 5,
            'verse_count': 5
        }
    }
    
    # Create a context generator
    logger.info("Creating context generator")
    context_generator = ContextGenerator(
        llm_api_url=llm_api_url,
        model="qwen3-14b-custom",
        batch_size=1
    )
    
    # Generate context for the sample chunk
    logger.info("Generating context for the sample chunk")
    start_time = time.time()
    
    try:
        chunk_with_context = context_generator._generate_context_for_chunk(sample_chunk)
        
        generation_time = time.time() - start_time
        logger.info(f"Generated context in {generation_time:.2f} seconds")
        
        # Print the generated context
        logger.info(f"Generated context: {chunk_with_context.get('context', 'No context generated')}")
        
        logger.info("Test completed successfully")
    except Exception as e:
        logger.error(f"Error generating context: {str(e)}")

if __name__ == '__main__':
    main()
