# Robot de réconfort

[Dépôt GitHub du projet](https://github.com/BoubeniaWalid/HAI716-Projet-Agent-Walid)

Projet HAI716 réalisé par **BOUBENIA Walid** et **BARRE-GUETROT Ilan**.

L'agent reçoit les demandes de résidents, identifie leur émotion à l'aide d'un
dictionnaire, choisit un objet dans une armoire et le livre au résident. Il
utilise uniquement une perception locale des quatre cases voisines et construit
sa propre carte mentale pour se déplacer.

## Pré-requis

- Python 3.10 ou supérieur ;
- aucune dépendance externe.

Le projet a été vérifié avec Python 3.14 dans l'environnement de développement.

## Organisation des fichiers

| Fichier ou dossier | Rôle |
|---|---|
| `agent.py` | Agent, mémoire, perception, BFS, décisions et livraisons |
| `reconfort_io.py` | Lecture/écriture JSON, simulateur de perception locale et trace |
| `validation.py` | Validation de la carte, du dictionnaire, de l'armoire et du scénario |
| `cartes/` | Cinq cartes et cinq scénarios fournis |
| `donnees/` | Dictionnaire des émotions et armoire standard |
| `tests/` | Tests de mémoire, perception, navigation, validation et trace |
| `start.sh` | Lanceur de l'agent |
| `test.sh` | Lanceur de la suite de tests |
| `rendu.json` | Métadonnées et commande du rendu |
| `RAPPORT.tex` | Rapport d'analyse au format LaTeX |
| `demo.mkv` | Video de démonstration de l'agent |

## Exécuter l'agent

La commande générale est :

```text
python agent.py <carte.json> <scenario.json> <dossier_donnees> <trace.json> [True|False]
```

Le dernier argument est facultatif :

- `True` affiche les cartes mentales pendant l'exécution ;
- `False` désactive l'affichage.

### Exemple sous Windows

Depuis la racine du projet :

```powershell
py -3 agent.py cartes\appartement_01.json cartes\scenario_01.json donnees sorties\trace_01.json False
```

### Exemple sous Linux ou macOS

```bash
./start.sh cartes/appartement_01.json cartes/scenario_01.json donnees sorties/trace_01.json False
```

Le fichier de trace est écrit dans le chemin fourni. Le dossier `sorties/` est
ignoré par Git car il contient des fichiers générés.

## Exécuter les tests

Avec le lanceur fourni :

```bash
./test.sh
```

Sous Windows, la commande équivalente est :

```powershell
py -3 -m unittest discover -s tests -p "Test*.py" -v
```

La suite contient actuellement **50 tests**. Elle vérifie notamment :

- la perception locale et la mémoire de la carte ;
- le calcul de chemins BFS et la replanification ;
- la lecture du premier mot reconnu dans un message ;
- l'ordre des casiers, les intensités et le bouclage horizontal ;
- les livraisons réussies et les échecs ;
- les règles de validation des quatre fichiers d'entrée ;
- la présence d'une bordure de murs autour de chaque carte ;
- la cohérence de la trace et de son résumé.

## Fonctionnalités implémentées

- validation des dimensions, symboles, positions et identifiants ;
- validation des émotions, intensités, formes du dictionnaire et casiers ;
- perception limitée aux cases voisines ;
- carte mentale séparée de la grille réelle ;
- déplacement par BFS avec mise à jour après chaque perception ;
- consultation du dictionnaire dans l'ordre des mots du message ;
- sélection des casiers selon l'émotion, l'intensité et les replis ;
- déplacement circulaire du sélecteur sur les huit colonnes ;
- perception et retrait des objets par l'interface du simulateur ;
- gestion des émotions inconnues, des armoires vides et des chemins
  inaccessibles ;
- enregistrement des actions et des résultats dans une trace JSON.

## Résultats vérifiés



Les cinq cartes fournies (`appartement_01.json` à
`appartement_05.json`) et leurs cinq scénarios associés ont tous été vérifiés.
Chaque carte s'exécute sans erreur avec son scénario et produit uniquement des
livraisons réussies. Ils peuvent être exécutés avec la même commande.

## Éléments du rendu

Les métadonnées de l'équipe, du langage, de la commande de lancement et de la
vidéo sont déclarées dans `rendu.json`. Le rapport d'analyse a été ajouté au
dépôt dans `RAPPORT_SMA.pdf` et la vidéo sous le nom `demo.mkv`.
