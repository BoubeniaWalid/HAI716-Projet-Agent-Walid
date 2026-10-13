#!/usr/bin/env python3

from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import reconfort_io as rio
from validation import valider_entrees


Position = Tuple[int, int]

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "O": (0, -1),
}

#------------------------------MEMOIRE------------------------------
@dataclass
class CarteMentale:
    """Carte construite uniquement a partir des perceptions du robot."""

    hauteur: int
    largeur: int
    cases: Dict[Position, str] = field(default_factory=dict)

    def connaitre(self, position: Position) -> str:
        """Les cases inconnues sont supposees libres pour planifier."""
        return self.cases.get(position, "inconnu")

    def mettre_a_jour(self, position: Position, nature: str) -> None:
        self.cases[position] = nature

    def est_traversable(self, position: Position) -> bool:
        return self.connaitre(position) in {"inconnu", "libre"}


@dataclass
class MemoireRobot:
    position: Position
    casier: Position
    carte: CarteMentale
    contenus_casiers: Dict[Position, Optional[str]] = field(default_factory=dict)
    emotion_resident: Optional[Tuple[str, str]] = None
    objet_transporte: Optional[str] = None

#-------------------------------------------------------------------

def voisins(position: Position) -> Iterable[Tuple[str, Position]]:
    """Retourne les quatre voisins dans un ordre deterministe."""
    row, column = position
    for direction, (row_delta, column_delta) in DIRECTIONS.items():
        yield direction, (row + row_delta, column + column_delta)


def plus_court_chemin(
    depart: Position,
    arrivees: Sequence[Position],
    carte: CarteMentale,
) -> Optional[List[Position]]:
    """Calcule un chemin BFS sur la carte mentale."""
    cibles = set(arrivees)
    if depart in cibles:
        return [depart]

    parents: Dict[Position, Optional[Position]] = {depart: None}
    file = deque([depart])

    while file:
        courant = file.popleft()
        for _, voisin in voisins(courant):
            row, column = voisin
            dans_grille = (
                0 <= row < carte.hauteur and 0 <= column < carte.largeur
            )
            if not dans_grille or voisin in parents:
                continue
            if not carte.est_traversable(voisin):
                continue

            parents[voisin] = courant
            if voisin in cibles:
                chemin = [voisin]
                while parents[chemin[-1]] is not None:
                    chemin.append(parents[chemin[-1]])
                return list(reversed(chemin))
            file.append(voisin)

    return None


class Agent:
    """Coordonne perception, memoire, decision et journalisation."""

    def __init__(
        self,
        carte: dict,
        dictionnaire: dict,
        armoire: dict,
        trace: rio.Trace,
        perception_locale: Callable[[Position, str], str],
    ) -> None:
        dimensions = carte["dimensions"]
        depart = tuple(carte["depart_robot"])
        casier_depart = tuple(armoire["casier_depart"])
        self.carte = carte
        self.dictionnaire = dictionnaire
        self.armoire = armoire
        self.trace = trace
        self.perception_locale = perception_locale
        self.memoire = MemoireRobot(
            position=depart,
            casier=casier_depart,
            carte=CarteMentale(
                hauteur=dimensions["hauteur"],
                largeur=dimensions["largeur"],
            ),
        )
    #------------------------------PERCEPTION------------------------------
    #note: c'est une sous-methode servant a bien isoler l'acces a la grille et a le confiner a seulement les cases voisines
    def percevoir_voisin(self, direction : str) -> str:
        """Renvoie la nature de la case voisine de la direction correspondante"""
        return self.perception_locale(self.memoire.position, direction)

    def percevoir(self) -> Dict[str, str]:
        """Perception des cases voisines."""
        natures_voisins = {}
        for direction in DIRECTIONS:
            natures_voisins[direction] = self.percevoir_voisin(direction)
        return natures_voisins

    def memoriser_perception(self, perception: Dict[str, str]) -> None:
        """Ajoute les quatre cases observees a la carte mentale."""
        for (direction, position) in voisins(self.memoire.position):
            nature= perception[direction]
            self.memoire.carte.mettre_a_jour(position, nature)
    
    #-------------------------------------------------------------------    

    def symbole(self, mot : str) -> str:
        """Renvoie le symbole correspondant au mot"""
        for s, m in self.carte["legende"].items():
            if m==mot:
                return s
        raise NameError("Recherche d'un mot ne se situant pas dans la legende.")

    def _adjacent_a(self, position: Position) -> bool:
        return any(voisin == position for _, voisin in voisins(self.memoire.position))

    def _direction_vers(self, cible: Position) -> Optional[str]:
        destinations = [
            voisin
            for _, voisin in voisins(cible)
            if (
                0 <= voisin[0] < self.memoire.carte.hauteur
                and 0 <= voisin[1] < self.memoire.carte.largeur
                and self.memoire.carte.est_traversable(voisin)
            )
        ]
        chemin = plus_court_chemin(
            self.memoire.position,
            destinations,
            self.memoire.carte,
        )
        if chemin and len(chemin) >= 2:
            prochain = chemin[1]
            for direction, (row_delta, column_delta) in DIRECTIONS.items():
                if (
                    self.memoire.position[0] + row_delta,
                    self.memoire.position[1] + column_delta,
                ) == prochain:
                    return direction
        return None

    def _lire_emotion_message(self, message: str) -> Tuple[str, str]:
        mots = set(rio.normaliser(message))
        for entree in self.dictionnaire["entrees"]:
            if any(forme in mots for forme in entree["formes"]):
                return entree["emotion"], entree["intensite"]
        return self.dictionnaire["emotions"][0], self.dictionnaire["intensites"][0]

    def _choisir_objet(self) -> Tuple[Optional[str], Optional[Position]]:
        if self.memoire.emotion_resident is None:
            return None, None
        emotion, intensite = self.memoire.emotion_resident
        for casier in self.armoire["casiers"]:
            if casier.get("objet") is None:
                continue
            if casier["emotion"] == emotion and casier["intensite"] == intensite:
                return casier["objet"], (casier["ligne"], casier["colonne"])
        for casier in self.armoire["casiers"]:
            if casier.get("objet") is None:
                continue
            if casier["emotion"] == emotion:
                return casier["objet"], (casier["ligne"], casier["colonne"])
        for casier in self.armoire["casiers"]:
            if casier.get("objet") is not None:
                return casier["objet"], (casier["ligne"], casier["colonne"])
        return None, None

    def choisir_action(self, demande: dict) -> Tuple[str, Optional[str]]:
        """Retourne l'action suivante."""
        perception = self.percevoir()
        self.memoriser_perception(perception)

        if self.memoire.emotion_resident is None:
            if "dictionnaire" in perception.values():
                return "CONSULTER", None
            direction = self._direction_vers(
                tuple(self.carte["dictionnaire"]["position"])
            )
            return "AVANCER", direction

        if self.memoire.objet_transporte is None:
            if "armoire" in perception.values():
                return "PRENDRE", None
            direction = self._direction_vers(
                tuple(self.carte["armoire"]["position"])
            )
            return "AVANCER", direction

        resident = self._resident_position(demande["resident"])
        if self._adjacent_a(resident):
            return "DONNER", demande["resident"]
        direction = self._direction_vers(resident)
        return "AVANCER", direction

    def _resident_position(self, resident_id: str) -> Position:
        for resident in self.carte["residents"]:
            if resident["id"] == resident_id:
                return tuple(resident["position"])
        raise KeyError(f"resident inconnu : {resident_id}")

    def executer_action(
        self,
        demande: dict,
        action: str,
        argument: Optional[str],
        perception: Optional[Dict[str, str]] = None,
    ) -> None:
        """Journalise une action et met a jour l'etat interne du robot."""
        position_avant = self.memoire.position
        casier_avant = self.memoire.casier

        if action == "AVANCER" and argument in DIRECTIONS:
            row, column = self.memoire.position
            row_delta, column_delta = DIRECTIONS[argument]
            self.memoire.position = (row + row_delta, column + column_delta)
        elif action == "CHERCHER" and argument in DIRECTIONS:
            row, column = self.memoire.casier
            row_delta, column_delta = DIRECTIONS[argument]
            self.memoire.casier = (row + row_delta, column + column_delta)
        elif action == "CONSULTER":
            self.memoire.emotion_resident = self._lire_emotion_message(demande["message"])
        elif action == "PRENDRE":
            objet, casier = self._choisir_objet()
            self.memoire.objet_transporte = objet
            if casier is not None:
                self.memoire.casier = casier
        elif action == "DONNER":
            self.memoire.objet_transporte = None

        self.trace.ajouter_pas(
            demande=demande["numero"],
            position=position_avant,
            casier=casier_avant,
            action=action,
            argument=argument,
            perception=perception,
            commentaire=None,
        )

    def traiter_demande(self, demande: dict) -> None:
        while True:
            action, argument = self.choisir_action(demande)
            perception = self.percevoir()
            objet_avant = self.memoire.objet_transporte
            self.executer_action(demande, action, argument, perception)

            if action == "DONNER":
                emotion, intensite = self.memoire.emotion_resident or (None, None)
                casier_choisi = self.memoire.casier
                objet = objet_avant
                self.trace.ajouter_livraison(
                    demande=demande["numero"],
                    resident=demande["resident"],
                    emotion=emotion,
                    intensite=intensite,
                    casier_choisi=casier_choisi,
                    repli="aucun",
                    objet=objet,
                    succes=True,
                    motif_echec=None,
                )
                self.memoire.emotion_resident = None
                self.memoire.objet_transporte = None
                break
            if action in {"CONSULTER", "PRENDRE"}:
                continue

    def executer(self, demandes: Sequence[dict]) -> None:
        for demande in demandes:
            self.traiter_demande(demande)


def charger_entrees(argv: Sequence[str]):
    if len(argv) != 5:
        raise rio.ErreurFichier(
            "usage : agent.py carte.json scenario.json donnees trace.json"
        )

    chemin_carte = Path(argv[1])
    chemin_scenario = Path(argv[2])
    dossier_donnees = Path(argv[3])
    chemin_sortie = Path(argv[4])

    carte = rio.charger_carte(chemin_carte)
    scenario = rio.charger_scenario(chemin_scenario)
    dictionnaire = rio.charger_dictionnaire(dossier_donnees / "dictionnaire.json")
    armoire = rio.charger_armoire(
        dossier_donnees / f"{scenario['armoire']}.json"
    )
    valider_entrees(carte, scenario, dictionnaire, armoire)
    return carte, scenario, dictionnaire, armoire, chemin_sortie


def main(argv: Sequence[str]) -> int:
    try:
        carte, scenario, dictionnaire, armoire, chemin_sortie = charger_entrees(
            argv
        )
        trace = rio.Trace(
            nom_carte=carte["nom"],
            nom_scenario=scenario["nom"],
            equipe=["A completer", "A completer"],
        )
        simulateur = rio.PerceptionLocale(carte)
        agent = Agent(
            carte,
            dictionnaire,
            armoire,
            trace,
            simulateur.percevoir,
        )
        agent.executer(scenario["demandes"])
        trace.ecrire(chemin_sortie)
        return 0
    except (rio.ErreurFichier, KeyError, TypeError, ValueError) as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))