# Minecraft Mod Dependencies

> Ce repository a pour but de récupérer les dépendances d'un ou plusieurs mods Minecraft en utilisant l'API mise à disposition par CurseForge.

## Comment ça marche ?

Il vous suffit d'aller dans le fichier main.py, d'y renseigner la liste des slugs des mods d'ont vous souhaitez avoir les informations et de lancer le programme.
Ce qui vous génèrera un dossier avec l'ensemble des fichiers (un fichier = un mod) avec pour chacun, de nombreuses informations ainsi que la liste de leurs dépendances.

## Comment récupérer le slug d'un mod ?

C'est plutôt simple, vous avez deux méthodes :
 - Vous rendre sur CurseForge, aller sur la page du mod dont vous souhaité avoir le slug et il s'agit du texte situé dans l'URL à cet emplacement :
```
https://www.curseforge.com/minecraft/mc-mods/iron-chests <- Ici le slug est iron-chests
```
 - Ouvrir le fichier research.py, renseigner le nom du mod, la version de Minecraft et le modLoaderType puis lancer le programme. Vous verrez alors dans la console une liste de mod, plus qu'à trouver le bon et à récupérer le slug. Il est possible que le mod souhaité n'apparaisse pas, il faut alors augmenté l'index de 50 dans les params, jusqu'à trouver votre mod.

## Visualisation

Ensuite, il est possible de visualiser tout ça de deux manières différentes :
 - Dans la console sous forme de liste hiérarchique (console.py)
 - Dans un fichier HTML (graph.py)