# MAYA Antivirus

An open source Anti-malware plugin that aims to reduce and treat threats for the software Autodesk Maya. This project is not affiliated with Autodesk.


# INSTALL

download the louisgjbertrand_Maya_Antivirus.py and put it in the `<user>\Documents\maya\2022\plug-ins` then activate it in the plugin manager.


This plugin requires the following pip libraries:
  - requests


to install the libraries, go to `C:\Program Files\Autodesk\Maya<version>\bin` and execute the following commands:

```sh
./mayapy -m pip install request
```

# Dependencies and tools used

originally RickHulzinga / MayaVaccineVirusRemovalTool:
  - this tool code base is not present anymore in the software
  - a script that is executed on scene loading. initially in userSetup.py but for safety reasons maya does not execute it.
  - https://github.com/RickHulzinga/MayaVaccineVirusRemovalTool

# Malware Reporting

You can report new malware and treatment if found in the issue reporting system for this repository (https://github.com/LouisGJBertrand/MAYA_Antivirus/issues)
The issue reports can serve also as an Autodesk Maya Malware database with every information on the threat
