# Image lourde (PyTorch). Separee du backend pour ne pas la rebuild a chaque
# modification d'une route API. Memes principes que Dockerfile.backend :
#   builder : venv /opt/venv, torch CPU + dependances runtime ; aucun compilateur
#             (toutes les deps ont des wheels ou sont en pur Python)
#   dev     : builder + extras [dev], hot-reload
#   prod    : python slim + venv runtime + code ; ni outil de dev, ni compilateur,
#             ni curl, ni pip ; utilisateur non-root
# Sans compilateur C++, torch.compile est indisponible (dev comme prod) : a
# reintroduire dans une etape dediee le jour ou il servira.

# ---------------------------------------------------------------- builder
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH
RUN python -m venv /opt/venv
# CPU-only : evite ~2 Go de CUDA tant qu'on ne branche pas le GPU du poste fixe.
# Couche separee : elle ne change pas quand pyproject.toml change.
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
COPY ml/pyproject.toml /tmp/pyproject.toml
RUN python -c "import tomllib; p = tomllib.load(open('/tmp/pyproject.toml', 'rb'))['project']; print('\n'.join(p['dependencies']))" > /tmp/requirements.txt \
 && pip install -r /tmp/requirements.txt

# -------------------------------------------------------------------- dev
FROM builder AS dev
RUN python -c "import tomllib; p = tomllib.load(open('/tmp/pyproject.toml', 'rb'))['project']; print('\n'.join(p['optional-dependencies']['dev']))" > /tmp/requirements-dev.txt \
 && pip install -r /tmp/requirements-dev.txt
ENV PYTHONPATH=/app HF_HOME=/models/hf
WORKDIR /app
COPY ml/ ./
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100", "--reload"]

# ------------------------------------------------------------------- prod
FROM python:3.11-slim AS prod
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:$PATH PYTHONPATH=/app \
    HF_HOME=/models/hf
COPY --from=builder /opt/venv /opt/venv
# Meme raison que Dockerfile.backend : pip/setuptools/wheel inutiles a
# l'execution et porteurs de CVE HIGH dans leurs bibliotheques embarquees.
# Correctifs de securite Debian publies depuis la derniere image de base
# (ex. libzstd1, HIGH) : sans eux, le scan Trivy de la CI echoue.
RUN apt-get update && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && /opt/venv/bin/python -m pip uninstall -y -q pip setuptools wheel \
 && /usr/local/bin/python -m pip uninstall -y -q pip setuptools wheel \
 && useradd -m -u 10002 sentinelml \
 && mkdir -p /models && chown -R sentinelml /models
WORKDIR /app
COPY ml/ ./
USER 10002:10002
EXPOSE 8100
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
