#!/usr/bin/env bash
# Verrous des dependances Python (backend et ml), generes par pip-tools depuis
# chaque pyproject.toml :
#   requirements.txt       dependances runtime : images prod et pip-audit
#   requirements-dev.txt   runtime + extra [dev], contraint par le premier :
#                          memes versions qu'en prod ; CI et postes de dev
#
# Usage :
#   scripts/lock-deps.sh            met les verrous a jour apres un changement
#                                   de pyproject.toml (garde les versions deja
#                                   verrouillees quand c'est possible)
#   scripts/lock-deps.sh --upgrade  monte tout a la derniere version admise
#   scripts/lock-deps.sh --check    echoue si un verrou n'est plus a jour (CI)
#
# Prerequis : Python 3.11 (celui des images) et pip-tools a la version ci-dessous,
#   python3.11 -m pip install "pip-tools==7.7.0"
# Les verrous dependent de la version de Python : jamais generes avec une autre.
set -euo pipefail

PIP_TOOLS_VERSION="7.7.0"
SERVICES=(backend ml)

mode="update"
case "${1:-}" in
  "") ;;
  --check) mode="check" ;;
  --upgrade) mode="upgrade" ;;
  *) echo "usage : $0 [--check|--upgrade]" >&2; exit 2 ;;
esac

root="$(cd "$(dirname "$0")/.." && pwd)"

python_version="$(python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
if [[ "$python_version" != "3.11" ]]; then
  echo "Python $python_version : les verrous se generent avec Python 3.11, celui des images." >&2
  exit 2
fi
installed="$(python -m pip show pip-tools 2>/dev/null | sed -n 's/^Version: //p')"
if [[ "$installed" != "$PIP_TOOLS_VERSION" ]]; then
  echo "pip-tools ${installed:-absent}, attendu $PIP_TOOLS_VERSION :" >&2
  echo "  python -m pip install \"pip-tools==$PIP_TOOLS_VERSION\"" >&2
  exit 2
fi

compile_args=(--quiet --strip-extras --no-emit-index-url --resolver=backtracking)
[[ "$mode" == "upgrade" ]] && compile_args+=(--upgrade)

for svc in "${SERVICES[@]}"; do
  (
    cd "$root/$svc"
    # Les chemins relatifs gardent l'en-tete des verrous identique d'un poste a l'autre.
    python -m piptools compile "${compile_args[@]}" \
      --output-file requirements.txt pyproject.toml
    python -m piptools compile "${compile_args[@]}" --extra dev \
      --constraint requirements.txt \
      --output-file requirements-dev.txt pyproject.toml
  )
done

if [[ "$mode" == "check" ]]; then
  locks=()
  for svc in "${SERVICES[@]}"; do
    locks+=("$svc/requirements.txt" "$svc/requirements-dev.txt")
  done
  if ! git -C "$root" diff --exit-code -- "${locks[@]}"; then
    echo "::error::Verrous Python pas a jour : lancer scripts/lock-deps.sh et committer." >&2
    exit 1
  fi
  echo "Verrous Python a jour."
fi
