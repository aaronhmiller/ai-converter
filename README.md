# Dockerfile Converter with AI

## How to Use

1. Run `docker compose up`
1. Ensure Ollama container is up and running. If model doesn't pull, exec in and run `ollama pull llama3.2`.
1. In a separate terminal, run `docker exec -it rag-playground-dockerfile-converter-1 python rag_ollama_chainguard.py`
