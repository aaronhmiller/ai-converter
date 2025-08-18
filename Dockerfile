FROM cgr.dev/chainguard/python:latest-dev
WORKDIR /app
COPY requirements.txt .
USER root
RUN pip install --no-cache-dir -r requirements.txt

#FROM cgr.dev/chainguard/python:latest
#WORKDIR /app
#COPY --from=builder /install /usr/local
COPY . .

ENTRYPOINT ["python", "rag_ollama_chainguard.py"]
