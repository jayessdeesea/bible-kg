#!/usr/bin/env python
"""
Bible Knowledge Graph - Data Ingestion Script

This script processes the KJV Bible text file, creating chunks and generating
contextual information for each chunk.
"""

import os
import sys
import logging
import json
import argparse
import time
from typing import Dict, List, Optional

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bible_kg.parser import parse_bible
from src.bible_kg.chunker import create_chunks, BibleChunker
from src.bible_kg.context_gen import generate_contexts, ContextGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bible_kg_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Process KJV Bible text file')
    
    parser.add_argument(
        '--input-file',
        type=str,
        default='docs/data/kjv.txt',
        help='Path to the KJV Bible text file'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/processed',
        help='Directory to save processed data'
    )
    
    parser.add_argument(
        '--window-size',
        type=int,
        default=7,
        help='Size of the sliding window in verses'
    )
    
    parser.add_argument(
        '--overlap-percentage',
        type=float,
        default=0.5,
        help='Percentage of overlap between adjacent windows'
    )
    
    parser.add_argument(
        '--max-passage-size',
        type=int,
        default=15,
        help='Maximum size of a passage chunk before applying sliding window'
    )
    
    parser.add_argument(
        '--llm-api-url',
        type=str,
        default='http://localhost:11434/api/generate',
        help='URL of the local LLM API'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='qwen3-14b-custom',
        help='Name of the model to use'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Number of chunks to process in a batch for context generation'
    )
    
    parser.add_argument(
        '--skip-context-generation',
        action='store_true',
        help='Skip context generation step'
    )
    
    parser.add_argument(
        '--sample-size',
        type=int,
        default=0,
        help='Process only a sample of verses (0 for all)'
    )
    
    return parser.parse_args()

def main():
    """Main function to process the KJV Bible text file."""
    args = parse_arguments()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Step 1: Parse the KJV Bible text file
    logger.info(f"Parsing Bible text file: {args.input_file}")
    start_time = time.time()
    
    verses = parse_bible(args.input_file)
    
    if args.sample_size > 0 and args.sample_size < len(verses):
        logger.info(f"Using sample of {args.sample_size} verses")
        verses = verses[:args.sample_size]
    
    parse_time = time.time() - start_time
    logger.info(f"Parsed {len(verses)} verses in {parse_time:.2f} seconds")
    
    # Save parsed verses
    verses_output_path = os.path.join(args.output_dir, 'verses.json')
    with open(verses_output_path, 'w', encoding='utf-8') as f:
        json.dump(verses, f, indent=2)
    logger.info(f"Saved parsed verses to {verses_output_path}")
    
    # Step 2: Create chunks
    logger.info("Creating chunks")
    start_time = time.time()
    
    chunker = BibleChunker(
        verses=verses,
        window_size=args.window_size,
        overlap_percentage=args.overlap_percentage,
        max_passage_size=args.max_passage_size
    )
    chunks = chunker.create_chunks()
    
    chunk_time = time.time() - start_time
    logger.info(f"Created {len(chunks)} chunks in {chunk_time:.2f} seconds")
    
    # Save chunks
    chunks_output_path = os.path.join(args.output_dir, 'chunks.json')
    chunker.save_chunks(chunks, chunks_output_path)
    logger.info(f"Saved chunks to {chunks_output_path}")
    
    # Step 3: Generate contextual information
    if not args.skip_context_generation:
        logger.info("Generating contextual information")
        start_time = time.time()
        
        context_generator = ContextGenerator(
            llm_api_url=args.llm_api_url,
            model=args.model,
            batch_size=args.batch_size
        )
        chunks_with_context = context_generator.generate_contexts(chunks)
        
        context_time = time.time() - start_time
        logger.info(f"Generated context for {len(chunks_with_context)} chunks in {context_time:.2f} seconds")
        
        # Save chunks with context
        context_output_path = os.path.join(args.output_dir, 'chunks_with_context.json')
        context_generator.save_chunks_with_context(chunks_with_context, context_output_path)
        logger.info(f"Saved chunks with context to {context_output_path}")
    else:
        logger.info("Skipping context generation")
    
    logger.info("Processing complete")

if __name__ == '__main__':
    main()
