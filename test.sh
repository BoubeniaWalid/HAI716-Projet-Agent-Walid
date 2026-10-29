#!/bin/bash

dossier="tests"
pattern="Test*.py"

arg_s="-s ${dossier}"
arg_p="-p ${pattern}"
arg_v="-v"
args="${arg_s} ${arg_p} ${arg_v}"


if command -v python; then
    python -m unittest discover $args
else
    if command -v python3; then
        python3 -m unittest discover $args
    else
        read -p "Les commandes python et python3 ne semblent pas fonctionner, avez-vous python d'installe? Si oui quelle commande doit etre executee a la place?: " pythonCommand
        $pythonCommand -m unittest discover $args
    fi
fi