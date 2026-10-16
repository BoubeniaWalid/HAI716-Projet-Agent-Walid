# Robot de réconfort — Boubenia Walid & Barré-Guétrot Ilan

Projet de semestre, master informatique. Un robot à perception locale
consulte un dictionnaire, fouille une armoire et rapporte un objet à un
résident.

Langage : *python* — Version : *3.12*

## Lancer

```
./start.sh
```

Dépendances : *aucune*.

## Tester

```
<votre commande de test>
```

*Il n'y a pour l'instant aucun test d'implémenté.*

## Organisation du code

| Fichier | Rôle |
|---|---|
| `agent.py` | point d'entrée, boucle de décision |
| `reconfort_io.py` | lecture des fichiers d'entrée et construction du fichier de sortie |
|`validation.py`| vérification de la validité des fichiers d'entrée|
|`start.sh`| démarrage du projet|

## État

**Ce qui marche.**
- *La lecture des fichiers d'entrée et la construction d'une trace* 
- *La vérification de la validité des fichiers d'entrée*
- *La perception des cases voisines du robot.*
- *La mémoire du robot (position de l'armoire, carte mentale, objet transporté,etc...)*
- *La recherche du plus court chemin*
- *La boucle de décision*
- *Un affichage console du trajet du robot*
- *Un fichier de lancement*

**Ce qui ne marche pas.** 
- *Les tests des différentes méthodes (pas encore implémentés)*

## Vidéo

`demo.mp4` (ou le lien), également déclarée dans `rendu.json`.
