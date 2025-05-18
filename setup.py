from setuptools import setup, find_packages

setup(
    name="bible-kg",
    version="0.1.0",
    description="Bible Knowledge Graph using Contextual Retrieval",
    author="Bible KG Team",
    author_email="example@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.32.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "embeddings": [
            "sentence-transformers>=2.2.0",
            "faiss-cpu>=1.7.0",
        ],
        "indexing": [
            "rank-bm25>=0.2.2",
            "numpy>=1.24.0",
            "pandas>=2.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
