FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY data/faiss_index/ data/faiss_index/

# Ollama runs on the host, not in this container. Docker Desktop (Mac/
# Windows) resolves host.docker.internal automatically; on Linux, run with
# `--add-host=host.docker.internal:host-gateway` or override this.
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
