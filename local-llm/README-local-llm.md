# Open WebUI with Ollama Setup for Bible Knowledge Graph Project

This repository contains the necessary files to set up Open WebUI with Ollama for the Bible Knowledge Graph project, specifically configured to run the Qwen3:14b model on CPU with 12 cores allocated for optimal performance.

## Files Included

- `docker-compose.yml`: Docker Compose configuration for Open WebUI and Ollama
- `qwen3-14b.modelfile`: Ollama model configuration for Qwen3:14b
- `start-llm-environment.sh`: Bash script to start the environment (Linux/macOS)
- `start-llm-environment.bat`: Batch script to start the environment (Windows)

## Prerequisites

- Docker Desktop installed and running
- 32GB RAM required
- At least 20GB of free disk space
- Multi-core CPU (12 cores allocated in configuration)
- Internet connection for initial setup and model downloads

## Quick Start (Windows)

1. Ensure Docker Desktop is running
2. Double-click `start-llm-environment.bat` or run it from Command Prompt
3. Wait for the setup to complete (may take some time for model download)
4. Access Open WebUI at http://localhost:3000

## Quick Start (Linux/macOS)

1. Ensure Docker Desktop is running
2. Make the start script executable: `chmod +x start-llm-environment.sh`
3. Run the script: `./start-llm-environment.sh`
4. Wait for the setup to complete (may take some time for model download)
5. Access Open WebUI at http://localhost:3000

## Manual Setup

If you prefer to set up the environment manually:

1. Start the Docker Compose services:
   ```
   docker-compose up -d
   ```

2. Wait for Ollama to be ready (check with `curl http://localhost:11434/api/version`)

3. Create the custom Qwen3:14b model:
   ```
   docker exec -it ollama ollama create qwen3-14b-custom -f /mnt/qwen3-14b.modelfile
   ```

4. Access Open WebUI at http://localhost:3000

## Using the Environment

1. After setup, access Open WebUI at http://localhost:3000
2. Complete the initial setup wizard if prompted
3. In the model selection dropdown, select `qwen3-14b-custom`
4. Start a new conversation to test the model

## Stopping the Environment

To stop the environment:

```
docker-compose down
```

## Troubleshooting

- If you encounter memory issues, try reducing the memory allocation in docker-compose.yml
- For performance issues, consider adjusting the parameters in the modelfile:
  - Reduce `num_thread` from 12 to a lower value if CPU usage is too high
  - Reduce `num_ctx` from 16384 to 8192 to decrease memory usage
- Check logs with `docker-compose logs` if you encounter any issues

## Documentation

For detailed documentation, see [docs/prompts/local-llm.md](docs/prompts/local-llm.md)
