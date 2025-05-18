# Local LLM Implementation with Open WebUI and Ollama

## Overview

This document outlines the implementation of a local Large Language Model (LLM) environment using Open WebUI with Ollama support, specifically configured to run the Qwen3:14b model. This setup provides a user-friendly interface for interacting with local language models without requiring GPU acceleration, making it accessible on standard hardware configurations.

## Components

### Open WebUI

Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform designed to operate entirely offline. It provides a modern interface for interacting with various LLM runners, including Ollama.

Key features include:
- Effortless setup using Docker
- Ollama integration for local model hosting
- Responsive design that works across desktop and mobile devices
- Full Markdown and LaTeX support
- Local RAG (Retrieval Augmented Generation) capabilities
- Web browsing capability
- Multi-model conversations

### Ollama

Ollama is a lightweight framework for running large language models locally. It simplifies the process of downloading, setting up, and running various open-source language models on consumer hardware.

Benefits of Ollama:
- Runs models locally without requiring cloud services
- Supports a wide range of open-source models
- Optimized for CPU usage when GPU is not available
- Simple API for integration with other tools

## Docker Implementation

The implementation uses Docker Compose to create a containerized environment with separate containers for Open WebUI and Ollama. This approach offers several advantages:

- Simplified setup with minimal configuration
- Isolation from the host system
- Consistent environment across different machines
- Easy updates and maintenance
- Better resource allocation and scaling
- Independent lifecycle management for each service

### System Requirements

- Docker Desktop installed and running
- 32GB of RAM required for Qwen3:14b
- At least 20GB of free disk space (Qwen3:14b requires approximately 15GB)
- Multi-core CPU (8+ cores recommended for reasonable performance)
- Internet connection for initial setup and model downloads

### Container Configuration

The Docker container is configured with the following specifications:

- Port mapping: Host port 3000 mapped to container port 8080
- Volume mounts:
  - Ollama data volume for storing models
  - Open WebUI data volume for storing user preferences and conversation history
- Automatic restart policy to ensure availability

### Data Structure

The implementation maintains two primary data volumes:

1. **Ollama Data Volume**:
   Stores downloaded models and Ollama configuration.

   ```json
   {
     "models": [
       {
         "name": "model_name",
         "size": "size_in_gb",
         "parameters": "parameter_count",
         "quantization": "quantization_method",
         "lastUsed": "timestamp"
       }
     ],
     "config": {
       "cpu_threads": 4,
       "context_size": 4096
     }
   }
   ```

2. **Open WebUI Data Volume**:
   Stores user preferences, conversation history, and application settings.

   ```json
   {
     "conversations": [
       {
         "id": "conversation_id",
         "title": "Conversation Title",
         "messages": [
           {
             "role": "user|assistant",
             "content": "message_content",
             "timestamp": "timestamp"
           }
         ],
         "model": "model_name",
         "created_at": "timestamp"
       }
     ],
     "settings": {
       "theme": "light|dark",
       "language": "en",
       "defaultModel": "model_name"
     }
   }
   ```

## Setup Process

The setup process involves the following steps:

1. **Prerequisite Check**:
   - Verify Docker Desktop is installed and running
   - Ensure sufficient system resources are available (32GB RAM required)

2. **File Preparation**:
   - Create a `local-llm` directory to organize all related files
   - Create a `docker-compose.yml` file in the `local-llm` directory with the following content:
   
   ```yaml
   version: '3'

   services:
     ollama:
       image: ollama/ollama:latest
       container_name: ollama
       volumes:
         - ollama_data:/root/.ollama
         - ./qwen3-14b.modelfile:/mnt/qwen3-14b.modelfile
       ports:
         - "11434:11434"
       restart: unless-stopped
       deploy:
         resources:
           reservations:
             memory: 32G
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"

     open-webui:
       image: ghcr.io/open-webui/open-webui:latest
       container_name: open-webui
       volumes:
         - open-webui_data:/app/backend/data
       ports:
         - "3000:8080"
       environment:
         - OLLAMA_BASE_URL=http://ollama:11434
         - OLLAMA_API_BASE_URL=http://ollama:11434/api
       depends_on:
         - ollama
       restart: unless-stopped
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"

   volumes:
     ollama_data:
       name: ollama_data
     open-webui_data:
       name: open-webui_data
   ```
   
   - Create a `qwen3-14b.modelfile` in the `local-llm` directory with the following content:
   
   ```
   FROM qwen3:14b

   PARAMETER num_ctx 16384
   PARAMETER num_thread 8
   PARAMETER num_batch 512
   PARAMETER num_gpu 0
   PARAMETER num_keep 48
   PARAMETER seed 42
   PARAMETER f16_kv true
   PARAMETER logits_all false
   PARAMETER vocab_only false
   PARAMETER use_mmap true
   PARAMETER use_mlock false
   ```

3. **Container Deployment**:
   - Navigate to the `local-llm` directory:
   ```
   cd local-llm
   ```
   - Start the Docker Compose services with:
   ```
   docker-compose up -d
   ```
   - This command:
     - Starts both the Ollama and Open WebUI containers
     - Sets up the networking between them
     - Mounts the necessary volumes
     - Configures the memory allocation (32GB for Ollama)

4. **Initial Configuration**:
   - Wait for the services to start (may take a few minutes)
   - Access the Open WebUI interface at http://localhost:3000
   - Complete the initial setup wizard

5. **Model Management**:
   - Create the custom Qwen3:14b model with:
   ```
   docker exec -it ollama ollama create qwen3-14b-custom -f /mnt/qwen3-14b.modelfile
   ```
   - This will download the base model and apply your custom configuration
   - The download may take some time depending on your internet connection (approximately 15GB)

## Startup and Operation

### Starting the Docker Compose Environment

1. **Launch Docker Desktop**:
   - Ensure Docker Desktop is running on your system
   - Verify it has access to sufficient system resources (32GB RAM required)

2. **Start the Docker Compose Services**:
   - Navigate to the `local-llm` directory:
   ```
   cd local-llm
   ```
   - If the services are not already running, start them with:
   ```
   docker-compose up -d
   ```
   - If you need to restart the services:
   ```
   docker-compose restart
   ```

3. **Access the Web Interface**:
   - Open a web browser and navigate to http://localhost:3000
   - You should see the Open WebUI login screen or setup wizard
   - Complete the initial setup if this is your first time

### Using Qwen3:14b with Open WebUI

1. **Create the Custom Model** (if not already created):
   - Execute the following command to create the custom model:
   ```
   docker exec -it ollama ollama create qwen3-14b-custom -f /mnt/qwen3-14b.modelfile
   ```
   - This will download the base model and apply your custom configuration
   - The download may take some time depending on your internet connection (approximately 15GB)

2. **Run the Model**:
   - Once the model is built, you can run it directly from the Open WebUI interface
   - In the model selection dropdown, select "qwen3-14b-custom"
   - Alternatively, you can run it from the command line:
   ```
   docker exec -it ollama ollama run qwen3-14b-custom
   ```
   - The first startup will take longer as the model loads into memory

### Memory Allocation for Qwen3:14b

1. **Docker Container Memory Allocation**:
   - By default, Docker allocates memory dynamically based on system availability
   - To explicitly set memory limits, modify the run command:
   ```
   docker run -d -p 3000:8080 -v ollama:/root/.ollama -v open-webui:/app/backend/data --name open-webui --restart always --memory=32g --memory-swap=36g ghcr.io/open-webui/open-webui:latest
   ```
   - This allocates 32GB of RAM and 4GB of swap space to the container
   - This configuration is recommended for optimal performance with Qwen3:14b
   - Adjust these values based on your system's available resources if needed

2. **Ollama Memory Usage Configuration**:
   - Qwen3:14b with default settings requires approximately:
     - 12-15GB for the model weights (depending on quantization)
     - 2-3GB for key/value cache with the recommended context size
     - 1-2GB for application overhead
   - Total memory requirement: 15-20GB

3. **Memory Optimization Strategies**:
   - **Recommended: 32GB RAM system** (selected configuration):
     - Use Q8_0 quantization for best quality: `ollama pull qwen3:14b-q8_0`
     - Keep context window at 16384: `PARAMETER num_ctx 16384`
     - Allocate 32GB to Docker container
     - Expected performance: Good (5-15s per response)
     - This configuration provides the best balance of performance and quality
   
   - **Alternative: For 24GB RAM systems**:
     - Use Q5_K_M quantization: `ollama pull qwen3:14b-q5_k_m`
     - Keep context window at 16384: `PARAMETER num_ctx 16384`
     - Allocate 20GB to Docker container
     - Expected performance: Reasonable (10-30s per response)
   
   - **Minimum: For 16GB RAM systems**:
     - Use Q4_0 quantization: `ollama pull qwen3:14b-q4_0`
     - Reduce context window to 8192: `PARAMETER num_ctx 8192`
     - Increase swap space to at least 8GB
     - Close other memory-intensive applications
     - Expected performance: Functional but slow (30-60s per response)

4. **Monitoring Memory Usage**:
   - Monitor container memory usage: `docker stats open-webui`
   - If you see "Out of Memory" errors, increase swap space or reduce parameters
   - Consider using `--cpus` parameter to limit CPU usage if needed

### Connecting Open WebUI to Ollama

1. **Configure Ollama Connection in Open WebUI**:
   - In the Open WebUI interface, navigate to Settings
   - Under "Model Providers", select "Ollama"
   - Set the Ollama API URL to `http://localhost:11434` (default)
   - Click "Save" or "Connect"

2. **Select Qwen3:14b as Default Model**:
   - In the models list, find "qwen3-14b-custom"
   - Set it as the default model
   - You can verify it's working by starting a new conversation

3. **Test the Setup**:
   - Create a new conversation
   - Type a test message to verify the model responds
   - The first response may take 10-30 seconds as the model processes your input

### Running the System

1. **Starting the Complete System**:
   - To start the entire system after a reboot:
     1. Start Docker Desktop
     2. Navigate to the `local-llm` directory containing your docker-compose.yml file
     3. Start the services: `docker-compose up -d`
     4. Access the web interface at http://localhost:3000

2. **Stopping the System**:
   - To stop the system:
     1. Close any active conversations
     2. Stop the services: `docker-compose down`
     3. Shut down Docker Desktop if desired

3. **Checking System Status**:
   - To check if the services are running:
     ```
     docker-compose ps
     ```
   - To view logs from the services:
     ```
     docker-compose logs
     ```
   - To view logs from a specific service:
     ```
     docker-compose logs ollama
     ```
     or
     ```
     docker-compose logs open-webui
     ```

## Performance Considerations

When running Qwen3:14b without GPU acceleration, consider the following:

- Response times will be significantly slower than with GPU acceleration (expect 10-30 seconds per response)
- Memory usage will be substantial (16-32GB RAM depending on configuration)
- Quantized versions (Q4_0 or Q5_K_M) are strongly recommended for CPU-only systems
- Reducing the context window size (`num_ctx`) can significantly improve performance
- First inference after loading will be slower; subsequent queries will be faster
- Background processes should be minimized during model inference
- Consider using swap space or virtual memory to prevent out-of-memory errors
- For time-sensitive applications, consider using a smaller model like Qwen3:7b

## Qwen3:14b Model Configuration

### Model Overview

Qwen3:14b is selected as the default model for this implementation due to its strong capabilities that align well with the Bible Knowledge Graph project requirements:

- **Large context window**: 32K tokens capacity, sufficient for processing lengthy Bible passages
- **Good contextual understanding**: As a 14B parameter model, it provides a good balance between performance and capability for comprehending complex texts
- **Local deployment**: Can be run entirely locally via Ollama without API costs or latency issues
- **Multilingual capabilities**: Supports potential future extensions to non-English Bible versions

### Recommended Configuration

For optimal performance with Qwen3:14b on CPU-only systems, the following configuration is recommended:

```json
{
  "model": "qwen3:14b",
  "parameters": {
    "num_ctx": 16384,
    "num_thread": 8,
    "num_batch": 512,
    "num_gpu": 0,
    "num_keep": 48,
    "seed": 42,
    "f16_kv": true,
    "logits_all": false,
    "vocab_only": false,
    "use_mmap": true,
    "use_mlock": false
  }
}
```

Key configuration parameters:
- `num_ctx`: Context window size (reduced from maximum to optimize for CPU performance)
- `num_thread`: Number of CPU threads to utilize (adjust based on your system)
- `num_batch`: Batch size for processing (smaller values use less memory)
- `num_gpu`: Set to 0 for CPU-only operation
- `f16_kv`: Use half-precision for key/value cache to reduce memory usage

### Quantization Options

For systems with limited memory, Ollama supports various quantization levels for Qwen3:14b:

- **Q4_0**: Highest compression, lowest memory usage, moderate quality reduction
- **Q5_K_M**: Balanced compression with minimal quality loss
- **Q8_0**: Lowest compression, highest memory usage, best quality preservation

The recommended quantization for CPU-only systems is Q5_K_M, which provides a good balance between performance and quality.

## Integration with Bible Knowledge Graph

This local LLM implementation can be integrated with the Bible Knowledge Graph project to provide:

1. **Context Generation**:
   - Generate contextual descriptions for Bible passages
   - Create embeddings for vector search capabilities

2. **Query Processing**:
   - Process natural language queries about biblical content
   - Enhance retrieval with local language model capabilities

3. **Content Augmentation**:
   - Provide additional context and explanations for retrieved passages
   - Generate summaries and thematic analyses

## Maintenance and Updates

To maintain the implementation:

1. **Container Updates**:
   - Periodically check for new Open WebUI container images
   - Update the container using Docker Desktop

2. **Model Updates**:
   - Monitor for new or improved model versions
   - Update models through the Open WebUI interface

3. **Backup Strategy**:
   - Regularly backup the data volumes
   - Export important conversations and configurations

## Troubleshooting

Common issues and their resolutions:

1. **Connection Issues**:
   - Verify Docker container is running
   - Check port mappings and firewall settings
   - Ensure host has sufficient resources

2. **Model Loading Failures**:
   - Verify sufficient disk space for models
   - Check system memory availability
   - Review model compatibility with Ollama

3. **Performance Issues**:
   - Adjust model parameters for better CPU performance
   - Consider using smaller or more optimized models
   - Close unnecessary applications to free system resources

## Conclusion

This implementation provides a robust, self-contained environment for running Qwen3:14b locally without GPU acceleration. By combining Open WebUI's user-friendly interface with Ollama's efficient model management, users can leverage powerful AI capabilities while maintaining complete data privacy and control.

For the Bible Knowledge Graph project, Qwen3:14b offers an ideal balance of capabilities:
- Its large context window handles lengthy biblical passages effectively
- Its good contextual understanding generates useful descriptions of biblical content
- Its local deployment ensures privacy and eliminates API costs
- Its performance, even on CPU-only systems, is sufficient for the context generation tasks required by the project

While running a 14B parameter model on CPU presents performance challenges, the configuration recommendations in this document provide a practical approach to leveraging Qwen3:14b's capabilities within reasonable hardware constraints.
