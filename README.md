# tablePackager
Pincab Table Packager


SM Lib - Proclame la bonne parole de sieurs Sam et Max
========================================================

Ce module proclame la bonne parole de sieurs Sam et Max. Puissent-t-ils
retrouver une totale libert� de pens�e cosmique vers un nouvel age
reminiscent.

Vous pouvez l'installer avec pip:

    pip install sm_lib

Exemple d'usage:

    >>> from sm_lib import proclamer
    >>> proclamer()

Ce code est sous licence WTFPL.

Installation:
python setup.py install

Suppression du package
pip uninstall tablePackager

TODO:


- Popup Processing
- 

Production d'un package
=======================

Pr�requis : cx_freeze

    > python setup.py bdist_msi


TODO
====

- Edition Authors de chaque fichier
    => Affichage + edition sur double click
      
- commencer menu
    - Options   => sauvegarde configuration json
        - PinballX Path
        - etc.
    
    - Aide => Test html + image


- Ajouter selection produits extraction/install

- Traiter les cas de UltraDMD

- support vp9 / future pinball


- extraction des media avec PinUp System
- cas si le nom est invalide
+ Test Extract/deploy+edit sha1)
- traiter le cas du package invalid

+ Fonction check package:
    * Visual Pinball
        - 1 seul fichier vpx pr�sent
        - directb2s pr�sent
        
Whish
=====
- stockage de manifest deploy�s + merging si import installed packaged table


