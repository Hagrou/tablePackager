import sys
from cx_Freeze import setup, Executable
import os.path
import shutil

#https://fraoustin.fr/old/python_cx_freeze.html
#https://stackoverflow.com/questions/57184971/available-bdist-msi-options-when-creating-msi-with-cx-freeze

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



# force clean
if os.path.exists('build'):
    shutil.rmtree('build', ignore_errors=True)

print('Generate packager/help/help.html')
gen_help('./README.md','packager/help',version)
gen_about('./about.md','packager/help',version)

setup(name='tablePackager',
      version=version,
      description='Pincab Table Packager',
      options={ 'build_exe': { 'include_msvcr' : True,
                               'include_files':[
                                    os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
                                    os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
                                'post_install.py'
                              ]},
                'bdist_msi': {'data': {'Shortcut': shortcut_table},
                              'install_icon' : 'packager/images/tablePackager_128x128.ico',
                              'upgrade_code': '{006d3301-d595-49e5-81d0-4a906aa48bb8}', # required for msi upgrade
                             },
      },
      url='https://github.com/Hagrou/tablePackager',
      license="GPL 3.0",
      executables=[ Executable(script='packager/tablePackager.py',
                               base='Win32GUI',
                               icon='packager/images/tablePackager_128x128.ico')]
)

