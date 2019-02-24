# tablePackager
Pincab Table Packager

Dependances :

    pip install Pillow
    pip install numpy
    pip install tkinterhtml  ??
    pip install markdown
    
    
    
========================================================

Génération d'une distribution
-----------------------------

Pour simplifier l'installation et l'utilisation de tablePackager, celui-ci 
est distribué sous la forme d'un fichier d'installation Windows (_tablePackager-x.y-<arch>.msi_).

La génération de ce fichier .msi nécessite d'installer dans le virtuel env la librairie cx_freeze:

    > pip install cx_freeze

Ainsi que l'installation de 2 version de Python 3.6 en 32 et 64 bits ainsi que de 2 virtual
env associés

Il faut ensuite exécuter la commande :
    
    (venv) C:\tablePackager>python setup.py bdist_msi
    
Ce qui lance la production du fichier .msi qui va se trouver dans le répertoire `tablePackager\dist`.
En fonction du virtual env, une cible 32 ou 64 bit sera générée
    
Génération de l'aide HTML
-------------------------

    (venv) c:\tablePackager>python -m markdown packager/help/help.md > packager/help/help.html


Todo
====
    
- commencer menu
    - Aide => Test html + image
    

- Config:
    - Mise à jour de update file en cas de changement de configuration
    - fenetre config en dessous!!!

- support vp9 / future pinball


- traiter le cas du package invalid
    => ou version incompatible

+ Fonction check package:
    * Visual Pinball
        - 1 seul fichier vpx présent
        - directb2s présent
 
+ Extraction
    * Prendre Meta si installé
   
+ Edition
    * Afficher 1 image en édition si presente
    * Rename extension possible d'un fichier
    * Tester Ajout d'un fichier déja existant
    
Bug: 
    
 - preciser:
    flyer.back => GameInfo
                    xxx.flyer_back.jpg
                    xxx.flyer_front.jpg
                    
 - View image: PNG !
    
 - Typo des champs texts



Licenses
=========

https://commons.wikimedia.org/wiki/GNOME_Desktop_icons