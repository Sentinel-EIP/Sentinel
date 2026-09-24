# Image lourde (PyTorch). Separee du backend pour ne pas la rebuild a chaque
# modification d'une route API.
FROM python:3.11-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models/hf
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl && rm -rf /var/lib/apt/lists/*
COPY ml/pyproject.toml ./
# CPU-only : evite ~2 Go de CUDA tant qu'on ne branche pas le GPU du poste fixe.
RUN pip install --upgrade pip \
 && pip install torch --index-url https://download.pytorch.org/whl/cpu \
 && pip install -e ".[dev]"

FROM base AS dev
COPY ml/ ./
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]

FROM base AS prod
COPY ml/ ./
RUN useradd -m -u 10002 sentinelml && mkdir -p /models && chown -R sentinelml /models
USER sentinelml
EXPOSE 8100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
