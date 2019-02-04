# tablePackager
Pincab Table Packager


========================================================

Génération d'une distribution
-----------------------------

Pour simplifier l'installation et l'utilisation de tablePackager, celui-ci 
est distribué sous la forme d'un fichier d'installation Windows (_tablePackager-x.y-amd64.msi_).

La génération de ce fichier .msi nécessite d'installer dans le virtuel env la librairie cx_freeze:

    > pip install cx_freeze

Il faut ensuite exécuter la commande :
    
    (venv) C:\tablePackager>python setup.py bdist_msi
    
Ce qui lance la production du fichier .msi qui va se trouver dans le répertoire `tablePackager\dist`.

Todo
====

- commencer menu
    - Aide => Test html + image


- Edition Authors de chaque fichier + url
    => Affichage + edition sur double click
      

- Config:
    - Mise à jour de update file en cas de changement de configuration
    - fenetre config en dessous!!!


- Traiter les cas de UltraDMD

- support vp9 / future pinball


- extraction des media avec PinUp System
- cas si le nom est invalide
+ Test Extract/deploy+edit sha1)
- traiter le cas du package invalid

+ Fonction check package:
    * Visual Pinball
        - 1 seul fichier vpx présent
        - directb2s présent
        
Whish
=====
- stockage de manifest deployés + merging si import installed packaged table


Licenses

https://commons.wikimedia.org/wiki/GNOME_Desktop_icons