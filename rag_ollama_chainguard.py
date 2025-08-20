from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from bs4 import BeautifulSoup
import requests
import os
import re

# 1. Scrape all image documentation links from images.chainguard.dev
# Recursively crawl all pages under /directory/image/ to find all documentation URLs
from urllib.parse import urljoin, urlparse

def crawl_chainguard_docs(base_url="https://images.chainguard.dev/directory/image/"):
    visited = set()
    to_visit = [base_url]
    doc_links = set()
    allowed_netloc = urlparse(base_url).netloc
    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        print(f"Crawling: {url}")
        visited.add(url)
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # Add this page if it's a documentation page (overview, usage, versions, etc)
            path = urlparse(url).path
            if any(path.endswith(f"/{section}") for section in ["overview", "usage", "versions", "tags", "vuln"]):
                doc_links.add(url)
            # Find all links to follow
            for a in soup.find_all("a", href=True):
                href = a["href"]
                abs_url = urljoin(url, href)
                parsed = urlparse(abs_url)
                # Only follow links within /directory/image/
                if parsed.netloc == allowed_netloc and parsed.path.startswith("/directory/image/"):
                    if abs_url not in visited:
                        to_visit.append(abs_url)
        except Exception as e:
            print(f"Warning: Failed to crawl {url}: {e}")
    return sorted(doc_links)


def get_base_images_from_dockerfile(dockerfile_contents):
    base_images = set()
    for line in dockerfile_contents.splitlines():
        line = line.strip()
        if line.lower().startswith("from "):
            # FROM <image>[:tag] [AS ...]
            match = re.match(r"from\s+([\w\-/\.]+)", line, re.IGNORECASE)
            if match:
                image = match.group(1)
                # Remove registry prefix if present (e.g., docker.io/library/ubuntu)
                image = image.split("/")[-1]
                # Remove tag if present
                image = image.split(":")[0]
                base_images.add(image)
    return list(base_images)

def get_doc_links_for_images(image_names, base_url="https://images.chainguard.dev"):
    doc_types = ["overview", "usage", "versions", "tags", "vuln"]
    links = []
    for name in image_names:
        for doc_type in doc_types:
            links.append(f"{base_url}/directory/image/{name}/{doc_type}")
    return links

def main():
    print("Chainguard Images Dockerfile Converter CLI")
    print("Type the path to a Dockerfile to convert, or 'exit' to quit.\n")
    while True:
        dockerfile_path = input("Enter Dockerfile path: ").strip()
        if dockerfile_path.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not os.path.isfile(dockerfile_path):
            print(f"Error: File not found: {dockerfile_path}\n")
            continue
        with open(dockerfile_path, "r") as f:
            dockerfile_contents = f.read()
        if not dockerfile_contents.strip():
            print("Error: Dockerfile is empty.\n")
            continue

        # Find base images in Dockerfile
        base_images = get_base_images_from_dockerfile(dockerfile_contents)
        if not base_images:
            print("Error: No FROM lines found in Dockerfile.\n")
            continue
        print(f"Detected base images in Dockerfile: {base_images}")

        # Only fetch docs for those images
        doc_links = get_doc_links_for_images(base_images)
        print(f"Fetching documentation for: {doc_links}")
        all_docs = []
        for url in doc_links:
            try:
                all_docs.extend(WebBaseLoader(url).load())
            except Exception as e:
                print(f"Warning: Failed to load {url}: {e}")

        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = splitter.split_documents(all_docs)

        # Check for empty documents and exit with error if none found
        if not documents:
            print("Error: No documentation content was loaded or parsed for the detected base images.\n")
            continue


        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
        embeddings = OllamaEmbeddings(model="llama3.2", base_url=ollama_base_url)
        vectorstore = FAISS.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever()

        system_prompt = (
            "You are an expert assistant on Chainguard Images. "
            "Your job is to help users convert Dockerfiles to use Chainguard base images. "
            "Use only information from https://images.chainguard.dev. "
            "If you don't know the answer, say so."
        )
        llm = OllamaLLM(model="llama3.2", system=system_prompt, base_url=ollama_base_url)
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        prompt = (
            "Convert the following Dockerfile to use Chainguard base images. "
            "Use information from https://images.chainguard.dev to find the equivalent Chainguard base image. "
            "Use the Overview information to update exposed ports, commands, environmental variables, etc. "
            "Create multi-stage builds if necessary. "
            "Explain any changes you make.\n\nDockerfile to convert:\n" + dockerfile_contents
        )
        print("\nConverting Dockerfile...\n")
        result = qa_chain.invoke({"query": prompt})
        print("--- Conversion Result ---")
        print(result['result'])
        print("------------------------\n")

if __name__ == "__main__":
    main()