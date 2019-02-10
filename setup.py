import sys
from cx_Freeze import setup, Executable
import os.path

from packager.tablePackager import version


PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "Table Packager",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]tablePackager.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data}

options = {
    'build_exe': {
        'include_msvcr' : True,
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
    },
    'bdist_msi': bdist_msi_options,
}

executables = [
    Executable('packager/tablePackager.py',
               base='Win32GUI',
               icon='packager/images/tablePackager_128x128.ico',
               )
]

setup(name='tablePackager',
      version=version,
      description='Pincab Table Packager',
      options=options,
      executables=executables
)

