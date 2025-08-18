# AI Dockerfile Converter

To run, run `docker run --rm -it -p 11434:11434 cgr.dev/chainguard-private/ollama:latest-dev` and exec into container, then run `ollama pull llama3.2`. After that, create a venv and `pip install -r requirements.txt` and `python rag_ollama_chainguard.py Dockerfile.backend.test`.