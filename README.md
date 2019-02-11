# tablePackager
Pincab Table Packager

Dependances :

    pip install Pillow
    pip install numpy
    
    
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

Installation 
============

##Pre requis pour Windows 7

To install Python successfully, download Visual C++ Redistributable 
from [here](https://www.microsoft.com/en-in/download/details.aspx?id=48145) and install it and Reboot the system.

Todo
====
- Import Ultra DMD
    => Deploy UltraDMD
    
- commencer menu
    - Aide => Test html + image
    

- Config:
    - Mise à jour de update file en cas de changement de configuration
    - fenetre config en dessous!!!

- support vp9 / future pinball


- extraction des media avec PinUp System
- cas si le nom est invalide
+ Test Extract/deploy+edit sha1)
- traiter le cas du package invalid

+ Fonction check package:
    * Visual Pinball
        - 1 seul fichier vpx présent
        - directb2s présent
 
Bug: 
   
  - Edition proprietes + save 
    => pas de mise a jour de l'arbre 
    => pas de close au save

 
 - save 
    => long => disable save et cancel
    
    
 - preciser:
    flyer.back => GameInfo
                    xxx.flyer_back.jpg
                    xxx.flyer_front.jpg
                    

    
Whish
=====
- merging si import installed packaged table


Licenses

https://commons.wikimedia.org/wiki/GNOME_Desktop_icons