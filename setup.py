import sys
from cx_Freeze import setup, Executable
import os.path
import shutil

from packager.tablePackager import version
from packager.help.genHelp import *

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

options = {
    'build_exe': {
        "excludes": ["numpy"], # cx_freeze 6.2 crash with numpy 1.19
        'include_msvcr' : True,
        'include_files':[
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
            os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
         ],
    },
    'bdist_msi': {'data': {'Shortcut': shortcut_table},
                  'upgrade_code': '{006d3301-d595-49e5-81d0-4a906aa48bb8}' # required for msi upgrade
                 },
}

executables = [
    Executable('packager/tablePackager.py',
               base='Win32GUI',
               icon='packager/images/tablePackager_128x128.ico',
               )
]

# force clean
if os.path.exists('build'):
    shutil.rmtree('build', ignore_errors=True)

print('Generate packager/help/help.html')
gen_help('./README.md','packager/help',version)
gen_about('./about.md','packager/help',version)

setup(name='tablePackager',
      version=version,
      description='Pincab Table Packager',
      options=options,
      executables=executables
)

