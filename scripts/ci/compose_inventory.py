#!/usr/bin/env python3
"""Inventaire des elements deployes, derive de la configuration compose.

Aucune liste n'est tenue a la main : les fichiers compose sont ceux que suit
git, les images et les ports sont ceux que `docker compose config` resout
(tous profils actifs). Un service ajoute demain est controle d'office.

Controles bloquants, dans chaque fichier compose et chaque base + surcharge :
  - tout port publie l'est sur 127.0.0.1 (locale-first), port hote aleatoire
    compris ;
  - aucun service en `network_mode: host` (il ecouterait sur toutes les
    interfaces de l'hote sans aucune publication visible).

Sorties pour la CI (--github-output) :
  - images      : images construites par le depot (matrice build + Trivy)
  - third_party : images tierces utilisees telles quelles (scan)

Usage : python3 scripts/ci/compose_inventory.py [--github-output FICHIER]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_HOST_IP = "127.0.0.1"
BASE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
# Variables obligatoires (${VAR:?...} ou ${VAR?...}) : valeur factice pour que
# `config` puisse resoudre le fichier. Les autres gardent leur valeur par defaut.
REQUIRED_VAR = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*):?\?")
PACKAGE_UPGRADE = re.compile(r"(apk\s+upgrade|apt-get\s+(dist-)?upgrade)")


def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
    # Commandes fixes (git, docker), sans shell ni entree utilisateur.
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)  # noqa: S603


def compose_files() -> list[Path]:
    res = run(["git", "ls-files", "*compose*.yml", "*compose*.yaml"], cwd=ROOT, check=True)
    return sorted(ROOT / f for f in res.stdout.split())


def combinations(files: list[Path]) -> list[list[Path]]:
    """Chaque fichier seul, sauf une surcharge (autre fichier compose a cote d'une
    base) qui est resolue avec sa base, comme en usage reel."""
    combos = []
    for f in files:
        base = next((f.parent / n for n in BASE_NAMES if f.parent / n in files), None)
        combos.append([base, f] if base and f != base else [f])
    return combos


def resolve(combo: list[Path]) -> dict[str, Any]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("COMPOSE_")}
    for f in combo:
        for var in REQUIRED_VAR.findall(f.read_text()):
            env.setdefault(var, "inventaire")
    with tempfile.NamedTemporaryFile("w", suffix=".env") as empty_env:
        # --env-file vide : le .env local n'influence pas l'inventaire.
        # --profile "*" : un service sous profil (proxy en dev...) est controle aussi.
        cmd = ["docker", "compose", "--project-name", "inventaire"]
        cmd += ["--env-file", empty_env.name, "--profile", "*"]
        for f in combo:
            cmd += ["-f", str(f)]
        res = run([*cmd, "config", "--format", "json"], cwd=combo[0].parent, env=env)
    if res.returncode != 0:
        sys.exit(f"docker compose config a echoue pour {combo}:\n{res.stderr}")
    config: dict[str, Any] = json.loads(res.stdout)
    return config


def stages(dockerfile: Path) -> list[tuple[str, str]]:
    """(nom, contenu) de chaque etape ; nom vide si l'etape n'a pas de AS."""
    result = []
    for body in re.split(r"(?im)^FROM\s+", dockerfile.read_text())[1:]:
        name = re.search(r"(?i)\bAS\s+(\S+)", body.splitlines()[0])
        result.append((name.group(1) if name else "", body))
    return result


def no_cache_stage(dockerfile: Path, target: str) -> str:
    """Nom de l'etape construite si elle applique des correctifs systeme (apk/apt
    upgrade) : elle doit etre reconstruite sans cache pour que le correctif compte."""
    all_stages = stages(dockerfile)
    built = next((s for s in all_stages if s[0] == target), None) if target else all_stages[-1]
    if not built or not PACKAGE_UPGRADE.search(built[1]):
        return ""
    if not built[0]:
        print(f"ATTENTION {dockerfile} : etape sans nom (AS), non reconstructible sans cache")
    return built[0]


def image_name(dockerfile: str, taken: set[str]) -> str:
    """Dockerfile.<x> -> <x> ; Dockerfile -> nom du dossier. Minuscules, unique."""
    path = Path(dockerfile)
    raw = path.name.split(".", 1)[1] if "." in path.name else path.parent.name
    name = re.sub(r"[^a-z0-9_.-]", "-", raw.lower()) or "image"
    candidate, i = name, 2
    while candidate in taken:
        candidate, i = f"{name}-{i}", i + 1
    taken.add(candidate)
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--github-output", help="fichier $GITHUB_OUTPUT")
    args = parser.parse_args()

    violations: list[str] = []
    built: dict[tuple[str, str], set[str]] = {}
    third_party: dict[str, set[str]] = {}
    for combo in combinations(compose_files()):
        label = " + ".join(str(f.relative_to(ROOT)) for f in combo)
        print(f"== {label}")
        for name, svc in sorted(resolve(combo).get("services", {}).items()):
            ports = svc.get("ports") or []
            for p in ports:
                if p.get("host_ip") != ALLOWED_HOST_IP:
                    violations.append(
                        f"{label} : {name} publie {p.get('published') or 'un port aleatoire'}"
                        f"->{p['target']} sur {p.get('host_ip') or 'toutes les interfaces'}"
                    )
            if svc.get("network_mode") == "host":
                violations.append(f"{label} : {name} est en network_mode: host")
            if "build" in svc:
                b = svc["build"]
                dockerfile = (Path(b["context"]) / b.get("dockerfile", "Dockerfile")).resolve()
                target = b.get("target", "")
                if len(combo) == 1:  # images de reference : cibles de la base, pas du dev
                    built.setdefault((str(dockerfile.relative_to(ROOT)), target), set()).add(name)
                origin = f"build {dockerfile.relative_to(ROOT)}{':' + target if target else ''}"
            else:
                third_party.setdefault(svc["image"], set()).add(f"{label}:{name}")
                origin = f"image {svc['image']}"
            shown = [
                f"{p.get('host_ip') or 'toutes-interfaces'}:{p.get('published') or '?'}"
                f"->{p['target']}"
                for p in ports
            ]
            print(f"   {name:16} {origin:55} ports={shown or '-'}")

    taken: set[str] = set()
    images = [
        {
            "name": image_name(dockerfile, taken),
            "file": dockerfile,
            "target": target,
            "no_cache": no_cache_stage(ROOT / dockerfile, target),
            "services": ",".join(sorted(services)),
        }
        for (dockerfile, target), services in sorted(built.items())
    ]
    tiers = [
        {"image": img, "used_by": ", ".join(sorted(u))} for img, u in sorted(third_party.items())
    ]

    print("\n== Images construites (build + Trivy bloquant)")
    for i in images:
        no_cache = f"  (sans cache : {i['no_cache']})" if i["no_cache"] else ""
        print(f"   {i['name']:10} {i['file']}  services={i['services']}{no_cache}")
    print("== Images tierces (scan)")
    for t in tiers:
        print(f"   {t['image']:40} {t['used_by']}")

    if args.github_output:
        with open(args.github_output, "a") as out:
            out.write(f"images={json.dumps(images)}\n")
            out.write(f"third_party={json.dumps(tiers)}\n")

    if violations:
        print("\nEXPOSITION HORS 127.0.0.1 (locale-first) :", file=sys.stderr)
        for v in violations:
            print(f"   {v}", file=sys.stderr)
        return 1
    print(f"\nPorts : tous publies sur {ALLOWED_HOST_IP} ; aucun network_mode: host.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
