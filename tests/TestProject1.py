import json
import unittest
from copy import deepcopy
from pathlib import Path

from agent import Agent, CarteMentale, plus_court_chemin
from reconfort_io import (
    ErreurFichier,
    PerceptionLocale,
    Trace,
    charger_armoire,
    charger_carte,
    charger_dictionnaire,
)
from validation import valider_entrees


BASE = Path(__file__).parent.parent


class TestProject1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.carte = charger_carte(BASE / "cartes/appartement_01.json")
        cls.scenario = json.loads(
            (BASE / "cartes/scenario_01.json").read_text(encoding="utf-8")
        )
        cls.dictionnaire = charger_dictionnaire(BASE / "donnees/dictionnaire.json")
        cls.armoire = charger_armoire(BASE / "donnees/armoire_standard.json")

    def make_agent(self):
        simulateur = PerceptionLocale(self.carte, self.armoire)
        return Agent(
            self.carte,
            self.dictionnaire,
            self.armoire,
            Trace("", ""),
            simulateur.percevoir,
            simulateur.contenu_casier,
            simulateur.prendre_casier,
        )

    def test_bfs_finds_known_shortest_path(self):
        carte = CarteMentale(3, 3, (1, 0), (0, 0), (0, 1), [(2, 2)])
        carte.cases.update({
            (0, 0): "mur", (0, 1): "mur", (0, 2): "mur",
            (1, 0): "libre", (1, 1): "libre", (1, 2): "libre",
            (2, 0): "mur", (2, 1): "mur", (2, 2): "mur",
        })
        chemin = plus_court_chemin((1, 0), [(1, 2)], carte)
        self.assertEqual(chemin, [(1, 0), (1, 1), (1, 2)])

    def test_dictionary_uses_first_recognized_word(self):
        robot = self.make_agent()
        result = robot._lire_emotion_message("Je suis triste mais heureux")
        self.assertEqual(result, ("tristesse", "moyenne"))
        self.assertIsNone(robot._lire_emotion_message("mot totalement inconnu"))

    def test_cabinet_candidates_follow_wheel_order(self):
        robot = self.make_agent()
        robot.memoire.emotion_resident = ("tristesse", "moyenne")
        self.assertEqual(robot._casiers_candidats()[0], (1, 4))

    def test_cabinet_columns_wrap(self):
        robot = self.make_agent()
        robot.memoire.casier = (1, 7)
        self.assertEqual(robot._direction_vers_casier((1, 0)), "E")
        robot.memoire.casier = (1, 0)
        self.assertEqual(robot._direction_vers_casier((1, 7)), "O")

    def test_supplied_scenario_has_four_successful_deliveries(self):
        robot = self.make_agent()
        robot.executer(self.scenario["demandes"], avec_affichage=False)
        self.assertEqual(len(robot.trace.livraisons), 4)
        self.assertTrue(all(item["succes"] for item in robot.trace.livraisons))

    def test_unknown_emotion_creates_failure(self):
        robot = self.make_agent()
        demande = {
            "numero": 99,
            "resident": "R1",
            "message": "xyzzy totalement inconnu",
        }
        robot.traiter_demande(demande, avec_affichage=False)
        self.assertEqual(robot.trace.livraisons[-1]["motif_echec"], "emotion indeterminee")
        self.assertFalse(robot.trace.livraisons[-1]["succes"])

    def test_empty_cabinet_creates_failure(self):
        armoire = deepcopy(self.armoire)
        for casier in armoire["casiers"]:
            casier["objet"] = None
        simulateur = PerceptionLocale(self.carte, armoire)
        robot = Agent(
            self.carte,
            self.dictionnaire,
            armoire,
            Trace("", ""),
            simulateur.percevoir,
            simulateur.contenu_casier,
            simulateur.prendre_casier,
        )
        robot.traiter_demande(self.scenario["demandes"][0], avec_affichage=False)
        self.assertEqual(robot.trace.livraisons[-1]["motif_echec"], "armoire vide")
        self.assertFalse(robot.trace.livraisons[-1]["succes"])

    def test_inaccessible_target_has_no_known_path(self):
        robot = self.make_agent()
        robot.memoire.carte.cases = {
            (row, column): "mur"
            for row in range(robot.memoire.carte.hauteur)
            for column in range(robot.memoire.carte.largeur)
        }
        robot.memoire.carte.cases[robot.memoire.position] = "depart du robot"
        self.assertIsNone(
            robot._direction_vers(tuple(self.carte["residents"][0]["position"]))
        )

    def test_replanification_avoids_discovered_wall(self):
        carte = CarteMentale(3, 4, (1, 0), (0, 0), (0, 3), [(2, 3)])
        carte.cases.update({
            (0, 0): "mur", (0, 1): "libre", (0, 2): "libre", (0, 3): "mur",
            (1, 0): "libre", (1, 1): "libre", (1, 2): "libre", (1, 3): "libre",
            (2, 0): "mur", (2, 1): "mur", (2, 2): "mur", (2, 3): "mur",
        })
        first_path = plus_court_chemin((1, 0), [(1, 3)], carte)
        self.assertEqual(first_path, [(1, 0), (1, 1), (1, 2), (1, 3)])
        carte.mettre_a_jour((1, 2), "mur")
        self.assertIsNone(plus_court_chemin((1, 0), [(1, 3)], carte))

    def test_validation_rejects_duplicate_cabinet(self):
        armoire = deepcopy(self.armoire)
        armoire["casiers"][1]["ligne"] = armoire["casiers"][0]["ligne"]
        armoire["casiers"][1]["colonne"] = armoire["casiers"][0]["colonne"]
        with self.assertRaises(ErreurFichier):
            valider_entrees(
                self.carte,
                self.scenario,
                self.dictionnaire,
                armoire,
            )

    def test_validation_rejects_inconsistent_special_position(self):
        carte = deepcopy(self.carte)
        carte["armoire"]["position"] = [6, 5]
        with self.assertRaises(ErreurFichier):
            valider_entrees(
                carte,
                self.scenario,
                self.dictionnaire,
                self.armoire,
            )

    def test_validation_rejects_non_rectangular_grid(self):
        carte = deepcopy(self.carte)
        carte["grille"][0] = carte["grille"][0][:-1]
        with self.assertRaises(ErreurFichier):
            valider_entrees(
                carte,
                {"carte": carte["nom"], "armoire": self.armoire["nom"], "demandes": []},
                self.dictionnaire,
                self.armoire,
            )

    def assert_invalid_inputs(self, carte=None, scenario=None, dictionnaire=None, armoire=None):
        with self.assertRaises(ErreurFichier):
            valider_entrees(
                carte or self.carte,
                scenario or self.scenario,
                dictionnaire or self.dictionnaire,
                armoire or self.armoire,
            )

    def test_validation_rejects_invalid_dimensions(self):
        carte = deepcopy(self.carte)
        carte["dimensions"]["largeur"] = 0
        self.assert_invalid_inputs(carte=carte)

    def test_validation_rejects_position_out_of_bounds(self):
        carte = deepcopy(self.carte)
        carte["depart_robot"] = [999, 0]
        self.assert_invalid_inputs(carte=carte)

    def test_validation_rejects_unknown_grid_symbol(self):
        carte = deepcopy(self.carte)
        carte["grille"][1] = carte["grille"][1].replace(".", "?", 1)
        self.assert_invalid_inputs(carte=carte)

    def test_validation_rejects_duplicate_resident_id(self):
        carte = deepcopy(self.carte)
        carte["residents"][1]["id"] = carte["residents"][0]["id"]
        self.assert_invalid_inputs(carte=carte)

    def test_validation_rejects_resident_on_wrong_symbol(self):
        carte = deepcopy(self.carte)
        row, column = carte["residents"][0]["position"]
        ligne = list(carte["grille"][row])
        ligne[column] = "."
        carte["grille"][row] = "".join(ligne)
        self.assert_invalid_inputs(carte=carte)

    def test_validation_rejects_duplicate_dictionary_form(self):
        dictionnaire = deepcopy(self.dictionnaire)
        dictionnaire["entrees"][1]["formes"] = dictionnaire["entrees"][0]["formes"][:1]
        self.assert_invalid_inputs(dictionnaire=dictionnaire)

    def test_validation_rejects_unknown_dictionary_emotion(self):
        dictionnaire = deepcopy(self.dictionnaire)
        dictionnaire["entrees"][0]["emotion"] = "emotion_inconnue"
        self.assert_invalid_inputs(dictionnaire=dictionnaire)

    def test_validation_rejects_unknown_dictionary_intensity(self):
        dictionnaire = deepcopy(self.dictionnaire)
        dictionnaire["entrees"][0]["intensite"] = "intensite_inconnue"
        self.assert_invalid_inputs(dictionnaire=dictionnaire)

    def test_validation_rejects_inconsistent_cabinet_order(self):
        armoire = deepcopy(self.armoire)
        armoire["intensites"] = list(reversed(armoire["intensites"]))
        self.assert_invalid_inputs(armoire=armoire)

    def test_validation_rejects_invalid_cabinet_position(self):
        armoire = deepcopy(self.armoire)
        armoire["casiers"][0]["ligne"] = 3
        self.assert_invalid_inputs(armoire=armoire)

    def test_validation_rejects_inconsistent_cabinet_label(self):
        armoire = deepcopy(self.armoire)
        armoire["casiers"][0]["emotion"] = "tristesse"
        self.assert_invalid_inputs(armoire=armoire)

    def test_validation_rejects_invalid_cabinet_object(self):
        armoire = deepcopy(self.armoire)
        armoire["casiers"][0]["objet"] = 42
        self.assert_invalid_inputs(armoire=armoire)

    def test_validation_rejects_scenario_for_another_map(self):
        scenario = deepcopy(self.scenario)
        scenario["carte"] = "autre_carte"
        self.assert_invalid_inputs(scenario=scenario)

    def test_validation_rejects_duplicate_request_number(self):
        scenario = deepcopy(self.scenario)
        scenario["demandes"][1]["numero"] = scenario["demandes"][0]["numero"]
        self.assert_invalid_inputs(scenario=scenario)

    def test_validation_rejects_unknown_resident(self):
        scenario = deepcopy(self.scenario)
        scenario["demandes"][0]["resident"] = "R_inconnu"
        self.assert_invalid_inputs(scenario=scenario)

    def test_validation_rejects_non_string_request_message(self):
        scenario = deepcopy(self.scenario)
        scenario["demandes"][0]["message"] = None
        self.assert_invalid_inputs(scenario=scenario)

    def test_cabinet_candidates_prioritize_intensity_then_row(self):
        robot = self.make_agent()
        robot.memoire.emotion_resident = ("tristesse", "moyenne")
        candidats = robot._casiers_candidats()
        self.assertEqual(candidats[:3], [(1, 4), (0, 4), (2, 4)])

    def test_repli_reports_intensity_and_neighbour_emotion(self):
        robot = self.make_agent()
        robot.memoire.emotion_resident = ("tristesse", "forte")
        self.assertEqual(robot._repli_pour_casier((1, 4)), "intensite")
        self.assertEqual(robot._repli_pour_casier((2, 3)), "voisine_1")
        self.assertEqual(robot._repli_pour_casier((2, 2)), "voisine_2")

    def test_trace_records_state_before_each_action(self):
        robot = self.make_agent()
        robot.traiter_demande(self.scenario["demandes"][0], avec_affichage=False)
        self.assertTrue(robot.trace.pas)
        self.assertEqual(robot.trace.pas[0]["position"], [6, 1])
        self.assertEqual(robot.trace.pas[0]["casier"], [1, 0])
        self.assertEqual(
            robot.trace.livraisons[0]["pas_utilises"],
            sum(
                pas["demande"] == self.scenario["demandes"][0]["numero"]
                for pas in robot.trace.pas
            ),
        )

    def test_trace_summary_matches_deliveries(self):
        robot = self.make_agent()
        robot.executer(self.scenario["demandes"], avec_affichage=False)
        trace = robot.trace.en_dictionnaire()
        self.assertEqual(trace["resume"]["demandes"], len(trace["livraisons"]))
        self.assertEqual(
            trace["resume"]["reussies"],
            sum(livraison["succes"] for livraison in trace["livraisons"]),
        )
        self.assertEqual(trace["resume"]["pas_total"], len(trace["pas"]))
