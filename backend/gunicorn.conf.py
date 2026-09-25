"""Configuration gunicorn de l'image prod (chargee par -c gunicorn.conf.py).

Metriques Prometheus en multi-processus : chaque worker ecrit ses compteurs dans
PROMETHEUS_MULTIPROC_DIR et /metrics les agrege. Sans cela, chaque scrape
tomberait sur un worker different et les compteurs feraient des sauts.
"""

import os
import shutil

# Pose ICI et non dans l'image : ailleurs (worker Celery, `compose run api ...`)
# la variable pointerait vers un dossier que seul on_starting cree, et tout
# import de prometheus_client echouerait. Doit preceder cet import, qui choisit
# le mode multi-processus a ce moment-la. Dans le home de l'utilisateur
# d'execution plutot que sous un chemin fixe et previsible de /tmp.
os.environ.setdefault("PROMETHEUS_MULTIPROC_DIR", os.path.expanduser("~/.prometheus-multiproc"))

from prometheus_client import multiprocess  # noqa: E402

bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 4


def on_starting(server):  # noqa: ARG001 - signature imposee par gunicorn
    path = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if path:
        # Repartir d'un dossier vide : des fichiers d'un demarrage precedent
        # fausseraient les compteurs.
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)


def child_exit(server, worker):  # noqa: ARG001 - signature imposee par gunicorn
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        multiprocess.mark_process_dead(worker.pid)
