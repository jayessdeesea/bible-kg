"""Bible chunk context generation module.

This module provides functionality to generate contextual information for Bible
chunks using a local LLM.
"""

import logging
import json
import time
import requests
from typing import Dict, List, Optional, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContextGenerator:
    """Generator for contextual information for Bible chunks.
    
    This class uses a local LLM to generate contextual information for Bible
    chunks, following Anthropic's Contextual Retrieval approach.
    """
    
    def __init__(
        self, 
        llm_api_url: str = "http://localhost:11434/api/generate",
        model: str = "qwen3-14b-custom",
        batch_size: int = 5,
        max_retries: int = 3,
        retry_delay: int = 5
    ):
        """Initialize the ContextGenerator.
        
        Args:
            llm_api_url: URL of the local LLM API.
            model: Name of the model to use.
            batch_size: Number of chunks to process in a batch.
            max_retries: Maximum number of retries for API calls.
            retry_delay: Delay between retries in seconds.
        """
        self.llm_api_url = llm_api_url
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    def generate_contexts(self, chunks: List[Dict]) -> List[Dict]:
        """Generate contextual information for a list of chunks.
        
        Args:
            chunks: List of chunk objects.
            
        Returns:
            List of chunks with added contextual information.
        """
        total_chunks = len(chunks)
        logger.info(f"Generating context for {total_chunks} chunks")
        
        chunks_with_context = []
        batch_count = 0
        
        # Process chunks in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_count += 1
            
            logger.info(f"Processing batch {batch_count}/{(total_chunks + self.batch_size - 1) // self.batch_size}")
            
            # Process each chunk in the batch
            for chunk in batch:
                chunk_with_context = self._generate_context_for_chunk(chunk)
                chunks_with_context.append(chunk_with_context)
                
            # Add a small delay between batches to avoid overwhelming the LLM
            if i + self.batch_size < total_chunks:
                time.sleep(1)
        
        logger.info(f"Completed context generation for {len(chunks_with_context)} chunks")
        return chunks_with_context
    
    def _generate_context_for_chunk(self, chunk: Dict) -> Dict:
        """Generate contextual information for a single chunk.
        
        Args:
            chunk: A chunk object.
            
        Returns:
            The chunk object with added contextual information.
        """
        reference = chunk['reference']
        text = chunk['text']
        
        logger.info(f"Generating context for chunk: {reference}")
        
        # Create prompt for the LLM
        prompt = self._create_context_prompt(reference, text)
        
        # Call the LLM API
        context = self._call_llm_api(prompt)
        
        # Add context to the chunk
        chunk_with_context = chunk.copy()
        chunk_with_context['context'] = context
        
        return chunk_with_context
    
    def _create_context_prompt(self, reference: str, text: str) -> str:
        """Create a prompt for generating contextual information.
        
        Args:
            reference: Reference string for the chunk.
            text: Text of the chunk.
            
        Returns:
            A prompt string for the LLM.
        """
        return f"""You are a biblical scholar with extensive knowledge of the King James Bible. 
Your task is to provide succinct contextual information for the following Bible passage:

Reference: {reference}
Text: {text}

Please provide a brief (50-100 words) contextual description that includes:
1. Where this passage fits in the biblical narrative
2. Key figures or events mentioned
3. Theological significance or themes
4. Historical or cultural context if relevant

Focus only on information that helps situate this passage within the Bible and would be useful for retrieval. 
Do not include commentary, interpretation, or application.

Contextual description:"""
    
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call the local LLM API to generate context.
        
        Args:
            prompt: Prompt string for the LLM.
            
        Returns:
            Generated context string.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.llm_api_url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                return result.get('response', '').strip()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries exceeded. Using fallback context.")
                    return "Context generation failed. This passage is from the King James Bible."
        
        # This should not be reached, but just in case
        return "Context generation failed. This passage is from the King James Bible."
    
    def save_chunks_with_context(self, chunks: List[Dict], output_path: str) -> None:
        """Save chunks with context to a JSON file.
        
        Args:
            chunks: List of chunk objects with context.
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
                'context': chunk.get('context', ''),
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
            
        logger.info(f"Saved {len(chunks)} chunks with context to {output_path}")


def generate_contexts(
    chunks: List[Dict],
    llm_api_url: str = "http://localhost:11434/api/generate",
    model: str = "qwen3-14b-custom",
    batch_size: int = 5
) -> List[Dict]:
    """Generate contextual information for Bible chunks.
    
    This is a convenience function that creates a ContextGenerator instance
    and calls its generate_contexts method.
    
    Args:
        chunks: List of chunk objects.
        llm_api_url: URL of the local LLM API.
        model: Name of the model to use.
        batch_size: Number of chunks to process in a batch.
        
    Returns:
        List of chunks with added contextual information.
    """
    generator = ContextGenerator(
        llm_api_url=llm_api_url,
        model=model,
        batch_size=batch_size
    )
    return generator.generate_contexts(chunks)
