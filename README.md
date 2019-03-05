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
    
    
Logiciel supportés:

    Visual Pinball 9
    Visual Pinball X
    PinUp System (extraction et installation de media)
    Pinball X (extraction de média)
   
Génération de l'aide HTML
-------------------------

    (venv) c:\tablePackager>python -m markdown packager/help/help.md > packager/help/help.html


Todo
====

- Config:
    - Mise à jour de update file en cas de changement de configuration
    - fenetre config en dessous!!!




    
+ Package Manager
    + import package
         * Check Package compatibility version

    

Bug: 

- Extraction avec écraser d'un package
    => si Erreur, perte du package cible!!
    
                         
 - Typo des champs texts

Whish
=====

- / future pinball


- traiter le cas du package invalid
    => ou version incompatible
    

+ Fonction check package:
    * Visual Pinball
        - 1 seul fichier vpx présent
        - directb2s présent
 

Licenses
=========

https://commons.wikimedia.org/wiki/GNOME_Desktop_icons