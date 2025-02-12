from setuptools import setup
import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable(
        "db_cont.py",  # Your main script
        base=base,
        target_name="DB_Service_Controller.exe",
        icon=None,  # You can add an .ico file path here
        manifest="admin_manifest.xml"
    )
]

setup(
    name="DB Service Controller",
    version="1.0",
    description="Database Services Controller",
    executables=executables,
    options={
        "build_exe": {
            "packages": ["tkinter", "psutil"],
            "include_files": []
        }
    }
)