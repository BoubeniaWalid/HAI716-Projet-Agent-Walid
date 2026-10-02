"""Validation des fichiers d'entree du projet Robot de reconfort."""

from __future__ import annotations

from typing import Any

import reconfort_io as rio


def _exiger(condition: bool, message: str) -> None:
    if not condition:
        raise rio.ErreurFichier(message)


def _position_valide(valeur: Any, nom: str, hauteur: int, largeur: int) -> tuple[int, int]:
    _exiger(
        isinstance(valeur, list)
        and len(valeur) == 2
        and all(
            isinstance(coord, int) and not isinstance(coord, bool)
            for coord in valeur
        ),
        f"{nom} doit etre une position [ligne, colonne]",
    )
    ligne, colonne = valeur
    _exiger(
        0 <= ligne < hauteur and 0 <= colonne < largeur,
        f"{nom} hors de la grille : {valeur}",
    )
    return ligne, colonne


def _valider_carte(carte: dict) -> None:
    _exiger(isinstance(carte.get("nom"), str), "carte.nom manquant ou invalide")
    dimensions = carte.get("dimensions")
    _exiger(isinstance(dimensions, dict), "carte.dimensions manquant ou invalide")
    hauteur = dimensions.get("hauteur")
    largeur = dimensions.get("largeur")
    _exiger(
        isinstance(hauteur, int)
        and isinstance(largeur, int)
        and not isinstance(hauteur, bool)
        and not isinstance(largeur, bool)
        and hauteur > 0
        and largeur > 0,
        "les dimensions de la carte sont invalides",
    )
    _position_valide(carte.get("depart_robot"), "depart_robot", hauteur, largeur)
    armoire = carte.get("armoire")
    dictionnaire = carte.get("dictionnaire")
    _exiger(isinstance(armoire, dict), "carte.armoire manquant ou invalide")
    _exiger(isinstance(dictionnaire, dict), "carte.dictionnaire manquant ou invalide")
    _position_valide(armoire.get("position"), "armoire.position", hauteur, largeur)
    _position_valide(
        dictionnaire.get("position"), "dictionnaire.position", hauteur, largeur
    )

    residents = carte.get("residents")
    _exiger(isinstance(residents, list), "carte.residents manquant ou invalide")
    identifiants = set()
    for index, resident in enumerate(residents):
        _exiger(isinstance(resident, dict), f"resident {index} invalide")
        identifiant = resident.get("id")
        _exiger(
            isinstance(identifiant, str) and identifiant,
            f"resident {index}.id manquant ou invalide",
        )
        _exiger(
            identifiant not in identifiants,
            f"identifiant resident duplique : {identifiant}",
        )
        identifiants.add(identifiant)
        _exiger(
            isinstance(resident.get("nom"), str),
            f"resident {identifiant}.nom invalide",
        )
        _position_valide(
            resident.get("position"),
            f"resident {identifiant}.position",
            hauteur,
            largeur,
        )


def _valider_dictionnaire(dictionnaire: dict) -> None:
    emotions = dictionnaire.get("emotions")
    intensites = dictionnaire.get("intensites")
    entrees = dictionnaire.get("entrees")
    _exiger(
        isinstance(emotions, list)
        and all(isinstance(item, str) for item in emotions),
        "dictionnaire.emotions invalide",
    )
    _exiger(
        isinstance(intensites, list)
        and all(isinstance(item, str) for item in intensites),
        "dictionnaire.intensites invalide",
    )
    _exiger(isinstance(entrees, list), "dictionnaire.entrees manquant ou invalide")
    formes_vues = set()
    for index, entree in enumerate(entrees):
        _exiger(isinstance(entree, dict), f"entree dictionnaire {index} invalide")
        formes = entree.get("formes")
        _exiger(
            isinstance(formes, list)
            and formes
            and all(isinstance(forme, str) and forme for forme in formes),
            f"entree dictionnaire {index}.formes invalide",
        )
        for forme in formes:
            _exiger(
                forme not in formes_vues,
                f"forme dupliquee dans le dictionnaire : {forme}",
            )
            formes_vues.add(forme)
        _exiger(
            entree.get("emotion") in emotions,
            f"emotion inconnue : {entree.get('emotion')}",
        )
        _exiger(
            entree.get("intensite") in intensites,
            f"intensite inconnue : {entree.get('intensite')}",
        )


def _valider_armoire(armoire: dict, dictionnaire: dict) -> None:
    emotions = armoire.get("emotions")
    intensites = armoire.get("intensites")
    _exiger(
        emotions == dictionnaire["emotions"],
        "ordre des emotions incoherent dans l'armoire",
    )
    _exiger(
        intensites == dictionnaire["intensites"],
        "ordre des intensites incoherent dans l'armoire",
    )
    _exiger(
        len(emotions) == 8 and len(intensites) == 3,
        "dimensions de l'armoire invalides",
    )
    casier_depart = armoire.get("casier_depart")
    _exiger(
        isinstance(casier_depart, list)
        and len(casier_depart) == 2
        and all(
            isinstance(coord, int) and not isinstance(coord, bool)
            for coord in casier_depart
        )
        and 0 <= casier_depart[0] < 3
        and 0 <= casier_depart[1] < 8,
        f"casier_depart invalide : {casier_depart}",
    )
    casiers = armoire.get("casiers")
    _exiger(isinstance(casiers, list), "armoire.casiers manquant ou invalide")
    positions_vues = set()
    for index, casier in enumerate(casiers):
        _exiger(isinstance(casier, dict), f"casier {index} invalide")
        ligne = casier.get("ligne")
        colonne = casier.get("colonne")
        position = (ligne, colonne)
        _exiger(
            isinstance(ligne, int)
            and isinstance(colonne, int)
            and not isinstance(ligne, bool)
            and not isinstance(colonne, bool)
            and 0 <= ligne < 3
            and 0 <= colonne < 8,
            f"position casier invalide : {position}",
        )
        _exiger(position not in positions_vues, f"casier duplique : {position}")
        positions_vues.add(position)
        _exiger(
            casier.get("emotion") == emotions[colonne]
            and casier.get("intensite") == intensites[ligne],
            f"etiquette incoherente pour le casier {position}",
        )


def _valider_scenario(scenario: dict, carte: dict, armoire: dict) -> None:
    _exiger(
        scenario.get("carte") == carte.get("nom"),
        "scenario prevu pour une autre carte",
    )
    _exiger(
        scenario.get("armoire") == armoire.get("nom"),
        "scenario prevu pour une autre armoire",
    )
    residents = {resident["id"] for resident in carte["residents"]}
    demandes = scenario.get("demandes")
    _exiger(isinstance(demandes, list), "scenario.demandes manquant ou invalide")
    numeros = set()
    for index, demande in enumerate(demandes):
        _exiger(isinstance(demande, dict), f"demande {index} invalide")
        numero = demande.get("numero")
        _exiger(
            isinstance(numero, int) and numero not in numeros,
            f"numero de demande invalide : {numero}",
        )
        numeros.add(numero)
        _exiger(
            demande.get("resident") in residents,
            f"resident absent : {demande.get('resident')}",
        )
        _exiger(
            isinstance(demande.get("message"), str),
            f"message invalide pour la demande {numero}",
        )


def valider_entrees(carte: dict, scenario: dict, dictionnaire: dict, armoire: dict) -> None:
    _valider_carte(carte)
    _valider_dictionnaire(dictionnaire)
    _exiger(
        armoire.get("nom") and isinstance(armoire.get("nom"), str),
        "armoire.nom manquant ou invalide",
    )
    _valider_armoire(armoire, dictionnaire)
    _valider_scenario(scenario, carte, armoire)