from CustomTestCase import CustomTestCase
from agent import CarteMentale, MemoireRobot
from random import randint

class TestMemoire(CustomTestCase):
    #teste si connaitre() renvoie bien la nature de la case pour chaque nature
    def test_connaitre_renvoie_bonne_nature(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        offsets= [-1, 0, 1]
        for offsetH in offsets:
            for offsetL in offsets:
                h= carte["depart_robot"][0]+offsetH
                l= carte["depart_robot"][1]+offsetL
                carte_mentale.cases[(h, l)]= carte["legende"][carte["grille"][h][l]]

        for offsetH in offsets:
            for offsetL in offsets:
                h= carte["depart_robot"][0]+offsetH
                l= carte["depart_robot"][1]+offsetL
                nature= carte_mentale.connaitre((h, l))
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]], nature)

    #teste si connaitre() renvoie bien la nature de la case pour chaque nature (en changeant la legende)
    def test_connaitre_renvoie_bonne_nature2(self):
        carte= self.carte2
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        offsets= [-1, 0, 1]
        for offsetH in offsets:
            for offsetL in offsets:
                h= carte["depart_robot"][0]+offsetH
                l= carte["depart_robot"][1]+offsetL
                carte_mentale.cases[(h, l)]= carte["legende"][carte["grille"][h][l]]

        for offsetH in offsets:
            for offsetL in offsets:
                h= carte["depart_robot"][0]+offsetH
                l= carte["depart_robot"][1]+offsetL
                nature= carte_mentale.connaitre((h, l))
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]], nature)
    
    #teste si connaitre() fonctionne correctement pour toutes les cases (chaque case est consideree connue ou inconnue aleatoirement) 
    def test_connaitre_fonctionne_pour_toutes_les_cases(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                if randint(0, 1)==1:
                    carte_mentale.cases[(h, l)]= carte["legende"][carte["grille"][h][l]]
        
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte_mentale.connaitre((h, l))
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]], nature)

    #teste si mettre_a_jour() fonctionne correctement pour toutes les cases
    def test_mettre_a_jour_fonctionne_pour_toutes_les_cases(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte["legende"][carte["grille"][h][l]]
                carte_mentale.mettre_a_jour((h, l), nature)
                self.assertEqual(nature, carte_mentale.cases[(h, l)])

    #teste si mettre_a_jour() leve bien une erreur si la case et hors de la carte
    def test_mettre_a_jour_case_hors_carte_leve_erreur(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        with self.assertRaises(IndexError):
            carte_mentale.mettre_a_jour((-1, 0), "libre")
        with self.assertRaises(IndexError):
            carte_mentale.mettre_a_jour((0, -1), "libre")
        with self.assertRaises(IndexError):
            carte_mentale.mettre_a_jour((carte_mentale.hauteur, 0), "libre")
        with self.assertRaises(IndexError):
            carte_mentale.mettre_a_jour((0, carte_mentale.largeur), "libre")

    #teste si est_traversable() fonctionne correctement pour toutes les cases
    def test_est_traversable_fonctionne_pour_toutes_les_cases(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte_mentale.cases.get((h, l), "inconnu")
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]] in {"libre", "depart du robot"}, carte_mentale.est_traversable((h, l)))
                else:
                    self.assertTrue(carte_mentale.est_traversable((h, l)))

    #teste si est_traversable() fonctionne correctement pour toutes les cases (en mettant a jour toutes les cases)
    def test_est_traversable_fonctionne_pour_toutes_les_cases2(self):
        carte= self.carte1
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                carte_mentale.cases[(h, l)]= carte["legende"][carte["grille"][h][l]]
        
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte_mentale.cases.get((h, l), "inconnu")
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]] in {"libre", "depart du robot"}, carte_mentale.est_traversable((h, l)))
                else:
                    self.assertTrue(carte_mentale.est_traversable((h, l)))

    #teste si est_traversable() fonctionne correctement pour toutes les cases (en changeant la legende)
    def test_est_traversable_fonctionne_pour_toutes_les_cases3(self):
        carte= self.carte2
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte_mentale.cases.get((h, l), "inconnu")
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]] in {"libre", "depart du robot"}, carte_mentale.est_traversable((h, l)))
                else:
                    self.assertTrue(carte_mentale.est_traversable((h, l)))

    #teste si est_traversable() fonctionne correctement pour toutes les cases (en changeant la legende et en mettant a jour toutes les cases)
    def test_est_traversable_fonctionne_pour_toutes_les_cases4(self):
        carte= self.carte2
        carte_mentale= CarteMentale(carte["dimensions"]["hauteur"], carte["dimensions"]["largeur"], tuple(carte["depart_robot"]), tuple(carte["armoire"]["position"]), tuple(carte["dictionnaire"]["position"]), list([tuple(resident["position"]) for resident in carte["residents"]]))
        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                carte_mentale.cases[(h, l)]= carte["legende"][carte["grille"][h][l]]

        for h in range(carte_mentale.hauteur):
            for l in range(carte_mentale.largeur):
                nature= carte_mentale.cases.get((h, l), "inconnu")
                if nature!="inconnu":
                    self.assertEqual(carte["legende"][carte["grille"][h][l]] in {"libre", "depart du robot"}, carte_mentale.est_traversable((h, l)))
                else:
                    self.assertTrue(carte_mentale.est_traversable((h, l)))