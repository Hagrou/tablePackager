# tablePackager
The aims of Table Packager is to gather all the files of a pinball table (table, rom, media, etc.) 
in a single compressed file, a compressed package. You can edit it, add file or info and then 
deploy it on you pincab or distribute it on the web.</p>
<p>For the moment, you can extract table and media files from Pinball X, PinUp System and Visual Pinball X.</p>
<p>A package can be installed on Pin Up System and Visual Pinball (Pinballx is not available on installation
because I don't know how Pinball X links media files with it's internal data)
     
## <a name="Installation"></a>Installation


Table Packager is compatible on Windows 7 and more (32 or 64 bits). 

    On Windows 7, you must download Visual C++ Redistributable from 
    https://www.microsoft.com/en-in/download/details.aspx?id=48145, 
    install it and Reboot the system.

To install Table Packager, double click on 

    tablePackager-x.y-win32.msi
    
    
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


