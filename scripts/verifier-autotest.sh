#!/usr/bin/env bash
# Meta-test de scripts/verifier.sh : un message hors convention et un test
# volontairement rouge doivent le faire echouer, pour la bonne raison, y
# compris quand sa sortie passe dans un filtre. Sans ce controle, un
# verificateur qui rend toujours 0 passerait inapercu. Tourne en CI.
#
#   scripts/verifier-autotest.sh           tout
#   scripts/verifier-autotest.sh message   messages et titre seulement (job commits)
#   scripts/verifier-autotest.sh backend   test rouge seulement (job backend)
#
# Rien n'est ecrit dans le depot : les fichiers de test vivent dans un dossier
# temporaire, transmis a verifier.sh par VERIFIER_EXTRA_TESTS.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHAT="${1:-tout}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() {
  echo "ECHEC : $1" >&2
  [[ -n "${2:-}" ]] && tail -15 <<< "$2" >&2
  exit 1
}

if [[ "$WHAT" == "tout" || "$WHAT" == "message" ]]; then
  printf 'fix: message sans scope\n' > "$TMP/mauvais"
  printf 'fix(ci): message conforme\n' > "$TMP/bon"
  if output="$("$ROOT/scripts/verifier.sh" message "$TMP/mauvais" 2>&1)"; then
    fail "verifier.sh accepte un message sans scope"
  fi
  # Refuse pour la bonne raison, pas parce que l'outil manque.
  grep -q "scope-empty" <<< "$output" || fail "message refuse, mais pas par scope-empty :" "$output"
  "$ROOT/scripts/verifier.sh" message "$TMP/bon" > /dev/null 2>&1 \
    || fail "verifier.sh refuse un message conforme"
  if output="$("$ROOT/scripts/verifier.sh" titre "Feat/infra environnement projet" 2>&1)"; then
    fail "verifier.sh accepte un titre de PR hors convention"
  fi
  grep -q "type-empty" <<< "$output" || fail "titre refuse, mais pas par type-empty :" "$output"
  echo "verifier.sh : un message ou un titre hors convention le fait bien echouer"
  [[ "$WHAT" == "message" ]] && exit 0
fi

mkdir -p "$TMP/tests"
printf 'def test_rouge_volontaire() -> None:\n    assert 1 == 2\n' > "$TMP/tests/test_zz_rouge_volontaire.py"
export VERIFIER_EXTRA_TESTS="$TMP/tests" VERIFIER_PYTEST_ARGS="tests/test_zz_rouge_volontaire.py"
if output="$("$ROOT/scripts/verifier.sh" backend 2>&1)"; then
  fail "verifier.sh rend 0 sur un test rouge"
fi
# L'echec doit venir du test rouge, pas d'autre chose (Docker absent...) :
# sinon ce meta-test passerait a vide.
if ! grep -q "test_rouge_volontaire" <<< "$output" || ! grep -q "1 failed" <<< "$output"; then
  fail "verifier.sh a echoue, mais pas sur le test rouge :" "$output"
fi
# Meme chaine qu'un `verifier.sh | tail -1 && git commit`, avec pipefail.
if "$ROOT/scripts/verifier.sh" backend 2>&1 | tail -1 > /dev/null; then
  fail "un filtre en sortie masque le test rouge"
fi
echo "verifier.sh : un test rouge le fait bien echouer"
