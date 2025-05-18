# Bible Knowledge Graph

A Retrieval Augmented Generation (RAG) system for the King James Bible using Anthropic's Contextual Retrieval approach to maintain context awareness when querying biblical content.

## Overview

This project implements a data ingestion pipeline for creating a Bible Knowledge Graph, following the specifications in [docs/prompts/data-ingress.md](docs/prompts/data-ingress.md). The pipeline includes:

1. **Text Parsing**: Parse the KJV Bible text file into structured verse objects
2. **Chunking Strategy**: Implement a hybrid chunking approach combining passage-level and sliding window chunking
3. **Context Generation**: Generate contextual information for each chunk using a local LLM
4. **Indexing**: Create contextual embeddings and BM25 index (future implementation)
5. **Retrieval System**: Implement a hybrid retrieval system (future implementation)

## Project Structure

```
bible-kg/
├── src/
│   └── bible_kg/
│       ├── __init__.py
│       ├── parser.py       # Bible text parsing module
│       ├── chunker.py      # Chunking strategy implementation
│       ├── context_gen.py  # Context generation module
│       ├── indexing.py     # Vector and BM25 indexing (future)
│       └── retrieval.py    # Hybrid retrieval system (future)
├── tests/
│   └── bible_kg/
│       ├── __init__.py
│       └── ...
├── data/
│   └── processed/          # For storing intermediate results
├── scripts/
│   ├── process_bible.py    # Main script to run the pipeline
│   ├── test_sample.py      # Test script for parser and chunker
│   └── test_context_gen.py # Test script for context generation
├── docs/
│   ├── data/
│   │   └── kjv.txt         # Source data file
│   └── prompts/
│       └── data-ingress.md # Project specification
├── local-llm/              # Local LLM setup
├── .gitignore              # Git ignore file
├── requirements.txt        # Python dependencies
├── setup.py                # Package installation script
└── LICENSE                 # License file
```

## Requirements

- Python 3.8+
- Local LLM running on port 11434 (see [docs/prompts/local-llm.md](docs/prompts/local-llm.md) for setup)
- Required Python packages:
  - requests >= 2.32.0

- Optional dependencies (for future features):
  - **Embeddings**:
    - sentence-transformers >= 2.2.0
    - faiss-cpu >= 1.7.0
  - **Indexing**:
    - rank-bm25 >= 0.2.2
    - numpy >= 1.24.0
    - pandas >= 2.0.0
  - **Development**:
    - pytest >= 7.0.0
    - black >= 23.0.0
    - flake8 >= 6.0.0

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/bible-kg.git
   cd bible-kg
   ```

2. Set up a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```
   pip install -e .
   ```
   
   For development with additional tools:
   ```
   pip install -e ".[dev]"
   ```

5. Ensure the local LLM is running on port 11434 (see [docs/prompts/local-llm.md](docs/prompts/local-llm.md))

## Usage

### Testing the Parser and Chunker

To test the parser and chunker with a small sample:

```
python scripts/test_sample.py
```

### Testing Context Generation

To test the context generation with the local LLM:

```
python scripts/test_context_gen.py
```

### Running the Full Pipeline

To run the full data ingestion pipeline:

```
python scripts/process_bible.py
```

This will:
1. Parse the KJV Bible text file
2. Create chunks using the hybrid chunking strategy
3. Generate contextual information for each chunk using the local LLM
4. Save the results to the `data/processed` directory

#### Command-line Options

The `process_bible.py` script supports several command-line options:

- `--input-file`: Path to the KJV Bible text file (default: `docs/data/kjv.txt`)
- `--output-dir`: Directory to save processed data (default: `data/processed`)
- `--window-size`: Size of the sliding window in verses (default: 7)
- `--overlap-percentage`: Percentage of overlap between adjacent windows (default: 0.5)
- `--max-passage-size`: Maximum size of a passage chunk before applying sliding window (default: 15)
- `--llm-api-url`: URL of the local LLM API (default: `http://localhost:11434/api/generate`)
- `--model`: Name of the model to use (default: `qwen3-14b-custom`)
- `--batch-size`: Number of chunks to process in a batch for context generation (default: 5)
- `--skip-context-generation`: Skip context generation step
- `--sample-size`: Process only a sample of verses (0 for all)

Example:

```
python scripts/process_bible.py --sample-size 100 --skip-context-generation
```

## Implementation Details

### Text Parsing

The `parser.py` module implements a `BibleParser` class that:
- Reads the KJV Bible text file
- Skips header lines
- Parses each line into a structured verse object
- Extracts book, chapter, verse, and text
- Identifies implied words (words in square brackets)

### Chunking Strategy

The `chunker.py` module implements a `BibleChunker` class that:
- Groups verses by book and chapter
- Creates passage-level chunks based on narrative coherence
- Applies sliding window chunking to large passages
- Creates a hybrid approach that balances natural text divisions with manageable chunk sizes

### Context Generation

The `context_gen.py` module implements a `ContextGenerator` class that:
- Connects to a local LLM running on port 11434
- Generates contextual information for each chunk
- Processes chunks in batches to avoid overwhelming the LLM
- Handles retries and error cases

## Future Work

1. **Indexing Implementation**:
   - Implement contextual embedding generation
   - Set up a vector database (e.g., FAISS, Chroma)
   - Create a BM25 index

2. **Retrieval System**:
   - Implement the hybrid retrieval function
   - Create a simple API for querying the system

3. **Metadata Enrichment**:
   - Add testament classification
   - Add book type categorization
   - Implement entity extraction

4. **Evaluation**:
   - Create test queries and expected results
   - Evaluate retrieval accuracy and relevance
   - Measure performance metrics

## License

This project is licensed under the MIT License - see the LICENSE file for details.
