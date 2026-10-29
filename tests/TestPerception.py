from CustomTestCase import CustomTestCase
from agent import Agent, voisins
from reconfort_io import PerceptionLocale, Trace


class TestPerception(CustomTestCase):
    #teste si percevoir_voisin() renvoit le bon voisin pour chaque direction
    def test_percoit_voisins_correctement(self):
        carte= self.carte1
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        for direction, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], agent.percevoir_voisin(direction))

    #teste si percevoir_voisin() renvoit le bon voisin pour chaque direction (en changeant la legende)
    def test_percoit_voisins_correctement2(self):
        carte= self.carte2
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        for direction, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], agent.percevoir_voisin(direction))

    #teste si percevoir_voisin() leve bien une erreur quand l'agent tente de percevoir un voisin hors de la carte(cas normallement impossible)
    def test_perception_voisin_hors_carte_leve_erreur(self):
        carte= self.carte1
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        agent.memoire.position= (0, 0)
        with self.assertRaises(IndexError):
            agent.percevoir_voisin("N")
        with self.assertRaises(IndexError):
            agent.percevoir_voisin("O")

    #teste si percevoir() renvoit bien les voisins
    def test_percevoir_renvoie_voisins(self):
        carte= self.carte1
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        perception= agent.percevoir()
        for direction, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], perception[direction])

    #teste si percevoir() renvoit bien les voisins (en changeant la legende)
    def test_percevoir_renvoie_voisins2(self):
        carte= self.carte2
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        perception= agent.percevoir()
        for direction, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], perception[direction])

    #teste si memoriser_perception enregistre correctement les voisins dans la carte mentale
    def test_memorise_perception_correctement(self):
        carte= self.carte1
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        agent.memoriser_perception(agent.percevoir())
        for _, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], agent.memoire.carte.connaitre(voisin))

    #teste si memoriser_perception enregistre correctement les voisins dans la carte mentale (en changeant la legende)
    def test_memorise_perception_correctement2(self):
        carte= self.carte2
        pl= PerceptionLocale(carte)
        agent= Agent(carte, dict, dict, Trace("", ""), pl.percevoir)
        agent.memoriser_perception(agent.percevoir())
        for _, voisin in voisins(agent.memoire.position):
            self.assertEqual(carte["legende"][carte["grille"][voisin[0]][voisin[1]]], agent.memoire.carte.connaitre(voisin))