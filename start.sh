#!/bin/bash
type=".json"
dossierParDefaut="cartes/"
numeroParDefaut="01"
fichier1ParDefaut="appartement_"
fichier2ParDefaut="scenario_"
arg1ParDefaut="${dossierParDefaut}${fichier1ParDefaut}${numeroParDefaut}${type}"
arg2ParDefaut="${dossierParDefaut}${fichier2ParDefaut}${numeroParDefaut}${type}"
arg3ParDefaut="donnees/"
arg4ParDefaut="sortie.json"
arg5ParDefaut="True"
arg1=""
arg2=""
arg3=""
arg4=""
arg5=""

if [ $# -lt 1 ]; then
    read -p "quel appartement (soit chemin_complet ou nom_fichier ou numero)? (${arg1ParDefaut}) : " arg1
    if [ -z $arg1 ]; then
        arg1=$arg1ParDefaut
    else
        if ! [[ $arg1 == *"/"* ]] ; then
            if ! [ -f $arg2 ] ; then
                if [[ $arg1 =~ ^[0-9]+$ ]]; then
                    arg1="${dossierParDefaut}${fichier1ParDefaut}${arg1}${type}" 
                else 
                    arg1="${dossierParDefaut}${arg1}"
                fi
            else
                echo "Attention, si vous vouliez utiliser un fichier se situant dans ${dossierParDefaut} alors renommez le ou renommez le fichier de meme nom se situant dans la racine du projet pour regler le probleme!"
            fi
        else
            :
        fi
    fi
else
    arg1=$1
    if ! [[ $arg1 == *"/"* ]] ; then
        if ! [ -f $arg2 ] ; then
            if [[ $arg1 =~ ^[0-9]+$ ]]; then
                arg1="${dossierParDefaut}${fichier1ParDefaut}${arg1}${type}" 
            else 
                arg1="${dossierParDefaut}${arg1}"
            fi
        else
            echo "Attention, si vous vouliez utiliser un fichier se situant dans ${dossierParDefaut} alors renommez le ou renommez le fichier de meme nom se situant dans la racine du projet pour regler le probleme!"
        fi
    else
        :
    fi
fi

if [ $# -lt 2 ]; then
    read -p "quel scenario (soit chemin_complet ou nom_fichier ou numero)? (${arg2ParDefaut}) : " arg2
    if [ -z $arg2 ]; then
        arg2=$arg2ParDefaut
    else
        if ! [[ $arg2 == *"/"* ]] ; then
            if ! [ -f $arg2 ] ; then
                if [[ $arg2 =~ ^[0-9]+$ ]]; then
                    arg2="${dossierParDefaut}${fichier2ParDefaut}${arg2}${type}" 
                else 
                    arg2="${dossierParDefaut}${arg2}"
                fi
            else
                echo "Attention, si vous vouliez utiliser un fichier se situant dans ${dossierParDefaut} alors renommez le ou renommez le fichier de meme nom se situant dans la racine du projet pour regler le probleme!"
            fi
        else
            :
        fi
    fi
else
    arg2=$2
    if ! [[ $arg2 == *"/"* ]] ; then
        if ! [ -f $arg2 ] ; then
            if [[ $arg2 =~ ^[0-9]+$ ]]; then
                arg2="${dossierParDefaut}${fichier2ParDefaut}${arg2}${type}" 
            else 
                arg2="${dossierParDefaut}${arg2}"
            fi
        else
            echo "Attention, si vous vouliez utiliser un fichier se situant dans ${dossierParDefaut} alors renommez le ou renommez le fichier de meme nom se situant dans la racine du projet pour regler le probleme!"
        fi
    else
        :
    fi
fi

if [ $# -lt 3 ]; then
    read -p "quel dossier de donnees ? (${arg3ParDefaut}) : " arg3
    if [ -z $arg3 ]; then
        arg3=$arg3ParDefaut
    else
        :
    fi
else
    arg3=$3
fi

if [ $# -lt 4 ]; then
    read -p "quel fichier de sortie? (${arg4ParDefaut}) : " arg4
    if [ -z $arg4 ]; then
        arg4=$arg4ParDefaut
    else
        :
    fi
else
    arg4=$4
fi

if [ $# -eq 5 ]; then
    if [[ $5 == "True" || $5 == "False" ]]; then
        arg5=$5
    else
        echo "Argument 5 incorrect, attendu: 'True' ou 'False' ; recu: '$5'"
        exit 0
    fi
else
    arg5=$arg5ParDefaut
fi

if [ $# -gt 5 ]; then
    echo "Usage: $0 <appartement> <scenario> <dossier_donnees> <fichier_sortie> [avec_affichage?]"
    echo "L'appartement et le scenario peuvent etre soit le chemin complet, soit le nom du fichier si il se situe dans ${dossierParDefaut}, soit le numero du fichier si son nom commence par ${fichier1ParDefaut} ou ${fichier2ParDefaut} et se situe dans ${dossierParDefaut}."
    exit 0
else
    :
fi

if command -v python; then
    python agent.py $arg1 $arg2 $arg3 $arg4 $arg5
else
    if command -v python3; then
        python3 agent.py $arg1 $arg2 $arg3 $arg4 $arg5
    else
        read -p "Les commandes python et python3 ne semblent pas fonctionner, avez-vous python d'installe? Si oui quelle commande doit etre executee a la place?: " pythonCommand
        $pythonCommand agent.py $arg1 $arg2 $arg3 $arg4 $arg5
    fi
fi