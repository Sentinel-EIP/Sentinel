#!/usr/bin/env python3
"""Couverture minimale des paquets critiques (politique de tests : 90 %).

Paquets et seuil lus dans backend/pyproject.toml, section [tool.sentinel].
A lancer depuis backend/ apres pytest (fichier .coverage). Echoue si :
  - un paquet declare n'existe plus (renomme ou deplace sans mise a jour) ;
  - la couverture d'un paquet est sous le seuil (un fichier jamais importe
    par les tests compte pour 0 %) ;
  - un fichier du paquet contient `pragma: no cover`, qui retirerait du calcul
    une fonction entiere sans qu'on le voie.
Un paquet sans aucune instruction executable (squelette) passe, signale.
"""

import sys
import tomllib
from pathlib import Path

import coverage


def main() -> int:
    with open("pyproject.toml", "rb") as f:
        conf = tomllib.load(f)["tool"]["sentinel"]
    threshold: float = conf["critical-coverage"]
    cov = coverage.Coverage()
    cov.load()

    failed = False
    for package in conf["critical-packages"]:
        path = Path(package)
        if not path.is_dir():
            print(
                f"ECHEC {package} : paquet critique introuvable (renomme ? mettre a jour "
                "[tool.sentinel] dans pyproject.toml)"
            )
            failed = True
            continue
        statements = missing = 0
        excluded = [s for s in sorted(path.rglob("*.py")) if "pragma: no cover" in s.read_text()]
        for source in excluded:
            print(f"ECHEC {package} : 'pragma: no cover' interdit ici ({source})")
            failed = True
        for source in sorted(path.rglob("*.py")):
            _, stmts, _, miss, _ = cov.analysis2(str(source.resolve()))
            statements += len(stmts)
            missing += len(miss)
        if statements == 0:
            print(
                f"ok    {package} : aucune instruction pour l'instant (seuil {threshold} % "
                "applique des la premiere ligne de code)"
            )
            continue
        percent = 100 * (statements - missing) / statements
        ok = percent >= threshold
        failed |= not ok
        print(
            f"{'ok   ' if ok else 'ECHEC'} {package} : {percent:.1f} % "
            f"({statements - missing}/{statements} instructions), seuil {threshold} %"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
