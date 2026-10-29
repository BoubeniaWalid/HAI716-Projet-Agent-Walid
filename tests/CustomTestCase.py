import unittest
from reconfort_io import charger_carte

class CustomTestCase(unittest.TestCase):
    tests_reussis= 0
    tests_totaux= 0
    #fonction executee au debut de la phase de test
    @classmethod
    def setUpClass(cls):
        cls.tests_reussis= 0
        cls.tests_totaux= 0
        print("==========TestPerception==========")
        return super().setUpClass()

    #fonction executee a la fin de la phase de test
    @classmethod
    def tearDownClass(cls):
        print("==========Reussi: ",cls.tests_reussis,"/",cls.tests_totaux,"==========")
        return super().tearDownClass()
    
    #fonction executee au debut de chaque test
    def setUp(self):
        type(self).tests_totaux+=1
        self.carte1= charger_carte("tests/cartes/appartement_01.json")
        self.carte2= charger_carte("tests/cartes/appartement_02.json")
        #!------cartes,scenarios,etc... a rajouter ici si necessaire------!

    #fonction executee a la fin de chaque test
    def tearDown(self):
        #barbare mais necessaire à defaut de temps
        if hasattr(self, '_outcome') and self._outcome.result:
            resultat = self._outcome.result
            if not any(test == self for test, _ in resultat.failures + resultat.errors):
                type(self).tests_reussis += 1