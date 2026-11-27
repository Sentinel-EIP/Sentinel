"""Importe chaque dependance runtime declaree dans le pyproject.toml de l'image.

A executer DANS une image prod (lu sur l'entree standard) :
    docker compose exec -T api python - < scripts/ci/import_runtime_deps.py

Les images prod n'ont ni pip ni setuptools : une dependance qui en aurait besoin
a l'import casserait uniquement en prod. La liste des modules est derivee du
pyproject.toml (dependances -> distributions installees -> modules de premier
niveau) : une dependance ajoutee est verifiee sans rien maintenir ici.
"""

import importlib
import importlib.metadata as md
import re
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path("/app/pyproject.toml")


def dist_name(requirement: str) -> str:
    """'uvicorn[standard]>=0.32' -> 'uvicorn' (nom normalise PEP 503)."""
    match = re.match(r"\s*([A-Za-z0-9._-]+)", requirement)
    return re.sub(r"[-_.]+", "-", match.group(1) if match else requirement).lower()


def main() -> int:
    deps = tomllib.loads(PYPROJECT.read_text())["project"]["dependencies"]
    wanted = {dist_name(d) for d in deps}
    modules: dict[str, str] = {}
    for module, dists in md.packages_distributions().items():
        for dist in dists:
            if dist_name(dist) in wanted and not module.startswith("_"):
                modules[module] = dist_name(dist)
    missing = wanted - set(modules.values())
    failed = sorted(missing)
    for module, dist in sorted(modules.items()):
        try:
            importlib.import_module(module)
        except Exception as exc:  # noqa: BLE001 - on rapporte toute erreur d'import
            print(f"ECHEC import {module} ({dist}) : {type(exc).__name__}: {exc}")
            failed.append(dist)
    for dist in sorted(missing):
        print(f"ECHEC {dist} : declaree mais introuvable dans l'image")
    print(f"{len(modules)} modules importes pour {len(wanted)} dependances declarees")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
