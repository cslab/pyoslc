#!/usr/bin/python
import os
import subprocess
import sys

subprocess.call(["virtualenv", "venv"])
if sys.platform == "win32":
    bin = "Scripts"
else:
    bin = "bin"

requirements = open("requirements.txt", "r")

for line in requirements:
    subprocess.call([os.path.join("venv", bin, "pip"), "install", "--upgrade", line])
