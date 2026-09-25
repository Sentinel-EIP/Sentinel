#!/usr/bin/env bash
# Verifications identiques a la CI, a lancer avant chaque commit et chaque push.
#
#   scripts/verifier.sh                 tout : backend, ml, frontend, commits
#   scripts/verifier.sh backend ml      seulement ces parties
#   scripts/verifier.sh message F       un message de commit, AVANT de commiter :
#                                       scripts/verifier.sh message msg.txt && git commit -F msg.txt
#   scripts/verifier.sh titre "T"       un titre de PR (il devient le commit du
#                                       squash merge sur dev)
#
# Sort en echec (code non nul) des qu'une verification echoue, mais seulement
# apres les avoir toutes lancees : on voit tout ce qui est rouge d'un coup.
# `scripts/verifier.sh && git commit ...` ne commite donc jamais sur du rouge.
# Ne jamais filtrer sa sortie avant le && (`... | tail -1 && git commit`) :
# le filtre rendrait son propre code, pas celui des verifications.
#
# Commits : chaque message de VERIFIER_BASE..VERIFIER_HEAD (defaut
# origin/dev..HEAD) passe commitlint avec la configuration du depot, un par un.
# C'est ce meme script que lance la CI : une regle de convention se verifie par
# un outil, pas de memoire.
#
# Isolation : backend, ml, frontend et commitlint tournent dans des conteneurs
# ou le depot est monte EN LECTURE SEULE ; rien n'est ecrit dans l'arbre.
# VERIFIER_NATIVE=1 lance les outils deja installes, dans l'arbre lui-meme :
# reserve a la CI, dont l'espace de travail est jetable.
#
# VERIFIER_PYTEST_ARGS : arguments passes a pytest ; VERIFIER_EXTRA_TESTS :
# dossier de tests ajoutes a la partie verifiee (meta-test, voir
# scripts/verifier-autotest.sh).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMITLINT_PACKAGES="@commitlint/cli@19.8.1 @commitlint/config-conventional@19.8.1"
FAILED=()

step() {
  local label="$1"
  shift
  printf '\n=== %s\n' "$label"
  if "$@"; then
    printf -- '--- %s : OK\n' "$label"
  else
    printf -- '--- %s : ECHEC\n' "$label"
    FAILED+=("$label")
  fi
}

# Etapes des jobs backend et ml de .github/workflows/ci.yml. Chaque etape est
# lancee meme si la precedente echoue ; le code final les resume toutes.
python_checks() {
  local part="$1" dir="$2"
  cd "$dir"
  local status=0 extra added=()
  if [[ -n "${VERIFIER_EXTRA_TESTS:-}" ]]; then
    for extra in "$VERIFIER_EXTRA_TESTS"/*.py; do
      cp "$extra" tests/
      added+=("tests/$(basename "$extra")")
    done
  fi
  ruff check . || status=1
  if [[ "$part" == backend ]]; then
    ruff format --check . || status=1
    mypy app || status=1
    # shellcheck disable=SC2086 # arguments pytest volontairement decoupes
    POSTGRES_HOST=localhost POSTGRES_DB=sentinel_test POSTGRES_PASSWORD=sentinel \
      REDIS_HOST=localhost pytest -p no:cacheprovider ${VERIFIER_PYTEST_ARGS:-} || status=1
    python ../scripts/ci/critical_coverage.py || status=1
    ruff check --config pyproject.toml ../scripts || status=1
    ruff format --check --config pyproject.toml ../scripts || status=1
    mypy ../scripts || status=1
  else
    # shellcheck disable=SC2086
    pytest -p no:cacheprovider ${VERIFIER_PYTEST_ARGS:-} || status=1
  fi
  # Tests ajoutes retires : en mode natif, ils resteraient sinon dans l'arbre.
  [[ ${#added[@]} -eq 0 ]] || rm -f "${added[@]}"
  return "$status"
}

python_part() {
  local part="$1"
  if [[ "${VERIFIER_NATIVE:-0}" == 1 ]]; then
    (python_checks "$part" "$ROOT/$part")
    return
  fi
  local extra=()
  if [[ -n "${VERIFIER_EXTRA_TESTS:-}" ]]; then
    extra=(-v "$VERIFIER_EXTRA_TESTS":/extra:ro -e VERIFIER_EXTRA_TESTS=/extra)
  fi
  local torch=""
  [[ "$part" == ml ]] && torch="pip install -q torch --index-url https://download.pytorch.org/whl/cpu"
  # Copie de travail dans le conteneur : le depot est en lecture seule.
  docker run --rm \
    -v "$ROOT":/src:ro \
    -v sentineleip-verifier-pip:/root/.cache/pip \
    -e VERIFIER_PYTEST_ARGS="${VERIFIER_PYTEST_ARGS:-}" \
    ${extra[@]+"${extra[@]}"} \
    python:3.11-slim bash -c "
      set -euo pipefail
      export PIP_ROOT_USER_ACTION=ignore PIP_DISABLE_PIP_VERSION_CHECK=1
      mkdir -p /w && cp -r /src/$part /src/scripts /w/
      cd /w/$part
      $torch
      pip install -q -e '.[dev]'
      VERIFIER_NATIVE=1 bash /w/scripts/verifier.sh --inside $part
    "
}

# Etapes du job frontend de la CI.
frontend_checks() {
  local status=0
  npm ci --no-audit --no-fund || return 1
  npm run -s lint || status=1
  npx tsc -b || status=1
  npm run -s test || status=1
  return "$status"
}

frontend_part() {
  if [[ "${VERIFIER_NATIVE:-0}" == 1 ]]; then
    (cd "$ROOT/frontend" && frontend_checks)
    return
  fi
  docker run --rm \
    -v "$ROOT":/src:ro \
    -v sentineleip-verifier-npm:/root/.npm \
    node:22 bash -c "
      set -euo pipefail
      mkdir -p /w/frontend /w/scripts
      tar -C /src/frontend --exclude=node_modules -cf - . | tar -C /w/frontend -xf -
      cp /src/scripts/verifier.sh /w/scripts/
      VERIFIER_NATIVE=1 bash /w/scripts/verifier.sh frontend
    "
}

# Lance un script ou `commitlint` lit un message sur son entree standard, avec
# la configuration du depot. Le depot est dans $REPO (lecture seule en conteneur).
with_commitlint() {
  local script="$1"
  shift
  if [[ "${VERIFIER_NATIVE:-0}" == 1 ]]; then
    # Comme la CI : commitlint installe dans node_modules a la racine du depot.
    (cd "$ROOT" && REPO="$ROOT" bash -c "commitlint() { npx --no-install commitlint \"\$@\"; }; $script")
    return
  fi
  docker run --rm -v "$ROOT":/r:ro -v sentineleip-verifier-npm:/root/.npm "$@" node:22 bash -c "
    set -euo pipefail
    git config --global --add safe.directory /r
    mkdir -p /w && cd /w && cp /r/commitlint.config.cjs .
    npm install --silent --no-save --no-package-lock --no-audit --no-fund $COMMITLINT_PACKAGES > /dev/null
    export REPO=/r
    commitlint() { npx --no-install commitlint \"\$@\"; }
    $script
  "
}

commits_part() {
  local base="${VERIFIER_BASE:-origin/dev}" head="${VERIFIER_HEAD:-HEAD}"
  # shellcheck disable=SC2016 # developpe dans le conteneur
  with_commitlint '
    status=0
    shas=$(git -C "$REPO" rev-list --reverse '"$base"'..'"$head"')
    [ -n "$shas" ] || { echo "aucun commit dans '"$base"'..'"$head"'"; exit 0; }
    for sha in $shas; do
      subject=$(git -C "$REPO" log -1 --format=%s "$sha")
      if git -C "$REPO" log -1 --format=%B "$sha" | commitlint > /tmp/lint 2>&1; then
        echo "OK  ${sha:0:7} $subject"
      else
        echo "KO  ${sha:0:7} $subject"; grep "✖" /tmp/lint | head -5; status=1
      fi
    done
    exit $status'
}

message_part() {
  local file="$1"
  [[ -f "$file" ]] || { echo "message introuvable : $file" >&2; return 2; }
  local abs
  abs="$(cd "$(dirname "$file")" && pwd)/$(basename "$file")"
  if [[ "${VERIFIER_NATIVE:-0}" == 1 ]]; then
    with_commitlint 'commitlint < "'"$abs"'"'
  else
    with_commitlint 'commitlint < /message' -v "$abs":/message:ro
  fi
}

titre_part() {
  local title="$1" tmp status=0
  tmp="$(mktemp)"
  printf '%s\n' "$title" > "$tmp"
  message_part "$tmp" || status=$?
  rm -f "$tmp"
  return "$status"
}

case "${1:-}" in
  message)
    message_part "${2:?fichier du message attendu}"
    exit
    ;;
  titre)
    titre_part "${2:?titre de la PR attendu}"
    exit
    ;;
  --inside)
    # Appel interne depuis le conteneur : une partie Python, outils installes.
    python_checks "$2" "$ROOT/$2"
    exit
    ;;
esac

PARTS=("$@")
[[ ${#PARTS[@]} -eq 0 ]] && PARTS=(backend ml frontend commits)
for part in "${PARTS[@]}"; do
  case "$part" in
    backend | ml) step "$part" python_part "$part" ;;
    frontend) step "frontend" frontend_part ;;
    commits) step "commits" commits_part ;;
    *)
      echo "partie inconnue : $part (backend, ml, frontend ou commits)" >&2
      exit 2
      ;;
  esac
done

if [[ ${#FAILED[@]} -gt 0 ]]; then
  printf '\nECHEC : %s\n' "${FAILED[*]}"
  exit 1
fi
printf '\nTout est vert : %s\n' "${PARTS[*]}"
