#!/usr/bin/env python3
"""Squelette de l'agent du projet Robot de reconfort.
"""

from __future__ import annotations

import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import reconfort_io as rio
from validation import valider_entrees


Position = Tuple[int, int]

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "N": (-1, 0),
    "S": (1, 0),
    "E": (0, 1),
    "O": (0, -1),
}


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
    objet_transporte: Optional[str] = None


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
    ) -> None:
        dimensions = carte["dimensions"]
        depart = tuple(carte["depart_robot"])
        casier_depart = tuple(armoire["casier_depart"])
        self.carte = carte
        self.dictionnaire = dictionnaire
        self.armoire = armoire
        self.trace = trace
        self.memoire = MemoireRobot(
            position=depart,
            casier=casier_depart,
            carte=CarteMentale(
                hauteur=dimensions["hauteur"],
                largeur=dimensions["largeur"],
            ),
        )

    def percevoir(self) -> Dict[str, str]:
        """perception fournie par le simulateur."""
        # Le robot ne peut pas  lire la carte["grille"].
        raise NotImplementedError("brancher la perception locale du simulateur")

    def memoriser_perception(self, perception: Dict[str, str]) -> None:
        """Ajoute les quatre cases observees a la carte mentale."""
        for direction, nature in perception.items():
            row_delta, column_delta = DIRECTIONS[direction]
            position = (
                self.memoire.position[0] + row_delta,
                self.memoire.position[1] + column_delta,
            )
            self.memoire.carte.mettre_a_jour(position, nature)

    def choisir_action(self, demande: dict) -> Tuple[str, Optional[str]]:
        """Retourne l'action suivante;  a implementer."""
        del demande
        return "ATTENDRE", None

    def executer_action(
        self,
        demande: dict,
        action: str,
        argument: Optional[str],
        perception: Optional[Dict[str, str]] = None,
    ) -> None:
        """Journalise une action."""
        self.trace.ajouter_pas(
            demande=demande["numero"],
            position=self.memoire.position,
            casier=self.memoire.casier,
            action=action,
            argument=argument,
            perception=perception,
            commentaire="squelette: action a implementer",
        )

    def traiter_demande(self, demande: dict) -> None:
        action, argument = self.choisir_action(demande)
        self.executer_action(demande, action, argument)
        self.trace.ajouter_livraison(
            demande=demande["numero"],
            resident=demande["resident"],
            emotion=None,
            intensite=None,
            casier_choisi=None,
            repli="aucun",
            objet=None,
            succes=False,
            motif_echec="agent non implemente",
        )

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
        agent = Agent(carte, dictionnaire, armoire, trace)
        agent.executer(scenario["demandes"])
        trace.ecrire(chemin_sortie)
        return 0
    except (rio.ErreurFichier, KeyError, TypeError, ValueError) as err:
        print(f"erreur de chargement : {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))