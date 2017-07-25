# A simple setup script to create an executable using PyQt4. This also
# demonstrates the method for creating a Windows executable that does not have
# an associated console.
#
# PyQt4app.py is a very simple type of PyQt4 application
#
# To generate the Window executable file, issue the following command
#   'python setup.py build'
#
# To generate Window install MSI file, issue the following command
#   'python setup.py bdist_msi'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys

from cx_Freeze import setup, Executable

application_title = "Remote Diff Tool" #what you want to application to be called
main_python_file = "RemoteDiffTool.py" #the name of the python file you use to run the program

include_files = ['ui/',
                 'log/',
                 'img/',
                 'winMerge/',
                 'Temp/']

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["atexit","re"]

build_exe_options = {"optimize": 2 ,"include_files":include_files, "includes" : includes}

setup(
        name = application_title,
        version = "1.4",
        description = "Remote Diff utility",
        options = {"build_exe" : build_exe_options},
        executables = [Executable(main_python_file, base = base, icon = "img/RDT.ico")])
