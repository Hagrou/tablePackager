#Table Packager 

![alt text](../images/tablePackager.png "table Packager")

The aims of Table Packager is to gather all the files of a pinball table (table, rom, media, etc.) 
in a single compressed file, a compressed package. You can edit it, add file or info and then 
deploy it on you pincab or distribute it on the web.

For the moment, you can extract table and media files from Pinball X, PinUp System and Visual Pinball X.

A package can be installed on Pin Up System and Visual Pinball (Pinballx is not available on installation
because I don't know how Pinball X links media files with it's internal data)
![alt text](../images/tablePackagerPrinciple.png "table Packager")



- [Installation](#Installation)

- [Run Package Installer](#Run-Package-Installer)

- [Extract and Package a Table](#Extract-Package-Table)

- [Edit a Package](#Edit-Package)

    - [Rename a Package](#Rename-Package)
    
    - [Edit Meta Information](#Meta-Information)
    
    - [Add a file](#Add-File)
    
    - [Delete a file](#Delete-File)

    - [Rename a file](#Rename-File)
    
## <a name="Installation"></a>Installation


Table Packager is compatible on Windows 7 and more (32 or 64 bits). 

    On Windows 7, you must download Visual C++ Redistributable from 
    https://www.microsoft.com/en-in/download/details.aspx?id=48145, 
    install it and Reboot the system.

To install Table Packager, double click on 

    tablePackager-x.y-win32.msi
    
When the following window open, click "Next"

![alt text](../images/install1.png)

Then, accept the request for elevation of windows and wait during installation

![alt text](../images/install2.png)

At the end of installation, you should see something like this:

![alt text](../images/install3.png)
 
 And this icon on your desktop: 
 
 ![alt text](../images/install4.png)


## <a name="Run-Package-Installer"></a>Run Package Installer

To launch Table Packager, just double click on the icon:

![alt text](../images/install4.png)
 
Then, you should see an window like this:

![alt text](../images/overview.png)

This window is mainly divided into two lists:

- the list of "Installed Tables" that contains all the tables found by Table Packager

- the list of "Packaged Tables" which contains all the packaged tables (empty)

The "Installed Tables" (in red) list contains all table used by Visual Pinball

## <a name="Extract-Package-Table"></a>Extract and Package a Table

To transform a table and all associated files (sound, rom, flyers, etc.), simply:

1. Select the table to extract from the list "tables installed"

2. Click the "Extract" button.

3. Then, Table Packager searches for all the files linked to this table 
   (you can then see it in the Actions view) and create a file "table package" 
   (Elvira ad the Party Monsters (Bally 1989).zip) containing all the files and metadata.

![alt text](../images/extract1.png)

## <a name="Edit-Package"></a>Edit a Package

You can now edit this package to rename it, add information files or multimedia:

1. Select it and

2. Click on edition button

![alt text](../images/edit1.png)

Table Package unpack package in a tmp directory and then open an edition windows:

![alt text](../images/edit2.png)

You can add information on the flipper, rename the package, add a file, etc.

### <a name="Rename-Package"></a>Rename a Package

![alt text](../images/edit3.png)

To rename a package:
 
 1. modify the package name field 
 
 2. Click on rename button
 
 3. All files are renamed 
 
 4. Click on Save button to save the result or click on cancel otherwise
 
### <a name="Meta-Information"></a>Edit Meta Information

![alt text](../images/edit4.png)

You can add information about each file in a package. For that:

1. Select the file on the treeview and double click on it

2. An meta information window appears, add info and save it

### <a name="Add-File"></a>Add a file

![alt text](../images/edit5.png)

To add a file:

1. Select the file category (Instruction Cards on our example)

2. Click on the 'Add button',

3. Then choose your file with the Select File popup

4. Click on 'Open'

5. If the name of the file to be added is not exactly the same as the name of 
   the package, a popup proposes to rename the file.

### <a name="Delete-File"></a>Delete a file

![alt text](../images/edit6.png)

To delete a file:

1. Select the file to delete

2. Click on the 'Del button'

### <a name="Rename-File"></a>Rename a file

