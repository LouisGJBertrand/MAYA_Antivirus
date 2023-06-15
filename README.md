# MAYA_Antivirus

An open source plugin that i made for myself that will compile multiple malicious script removers for maya into one plugin that can be activated in the plugin manager


# INSTALL

download the louisgjbertrand_Maya_Antivirus.py and put it in the `<user>\Documents\maya\2022\plug-ins` then activate it in the plugin manager.


This plugin requires the following pip libraries:
  - requests


to install the libraries, go to `C:\Program Files\Autodesk\Maya<version>\bin` and execute the following commands:

```sh
./mayapy -m pip install request
```

# Dependencies and tools used

RickHulzinga / MayaVaccineVirusRemovalTool:
  - a script that is executed on scene loading. initially in userSetup.py but for safety reasons maya does not execute it.
  - https://github.com/RickHulzinga/MayaVaccineVirusRemovalTool
