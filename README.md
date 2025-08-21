# Dockerfile Converter with AI

This CLI tool uses RAG on an Ollama model running in the Chainguard Ollama container to convert a Dockerfile to use equivalent Chainguard base images. It detects the base image in the dockerfile, scrapes for the appropriate docs on `images.chainguard.dev`, creates a new embedding, builds a vectorstore and chain, then produces a result. One container runs the CLI, and one runs the Ollama model.

*Tools*
- langchain
- Python
- Beautiful Soup
- Ollama
- Docker Compose
- Chainguard

## How to Use

1. Run `docker compose up --build`
1. For ease of use, put the Dockerfile(s) you want to convert in the same directory as this project
1. Ensure Ollama container is up and running. If model doesn't pull, exec into the ollama container `docker exec -it ai-converter-ollama-1 bash` and run `ollama pull llama3.2`.
1. In a separate terminal, run `docker exec -it ai-converter-dockerfile-converter-1 python rag_ollama_chainguard.py`
1. Provide the Dockerfile name, or to exit, type `exit` to quit.


### CLI Output Example
```
% docker exec -it rag-playground-dockerfile-converter-1 python rag_ollama_chainguard.py

USER_AGENT environment variable not set, consider setting it to identify your requests.
Chainguard Images Dockerfile Converter CLI
Type the path to a Dockerfile to convert, or 'exit' to quit.

Enter Dockerfile path: Dockerfile.backend.test
Detected base images in Dockerfile: ['python']
Fetching documentation for: ['https://images.chainguard.dev/directory/image/python/overview', 'https://images.chainguard.dev/directory/image/python/usage', 'https://images.chainguard.dev/directory/image/python/versions', 'https://images.chainguard.dev/directory/image/python/tags', 'https://images.chainguard.dev/directory/image/python/vuln']

Converting Dockerfile...

--- Conversion Result ---
To convert the provided Dockerfile to use Chainguard base images, I'll follow the instructions and recommendations from the Chainguard documentation.

Since there are two available image variants (latest-dev and minimal runtime), I will assume that we want to create a multi-stage build. The latest-dev variant includes pip, uv, and apk package managers, as well as bash, ash, and sh shells. However, for security reasons, the minimal runtime variant removes these tools.

... dockerfile here

```

### Notes from the Author
This is using AI and is non-deterministic, meaning YMMV in results. Please feel free to open a PR to adjust the prompting to make this application stronger!