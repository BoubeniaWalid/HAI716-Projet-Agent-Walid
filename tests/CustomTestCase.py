import unittest
from reconfort_io import charger_carte

class CustomTestCase(unittest.TestCase):
    
    #fonction executee au debut de chaque test
    def setUp(self):
        self.carte1= charger_carte("tests/cartes/appartement_01.json")
        self.carte2= charger_carte("tests/cartes/appartement_02.json")
        #!------cartes,scenarios,etc... a rajouter ici si necessaire------!