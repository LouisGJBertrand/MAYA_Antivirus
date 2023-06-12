from asyncio.windows_events import NULL

import os
import sys

import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx


PLUGIN_NAME = "Maya Antivirus Autoscan"
PLUGIN_COMPANY = "Louis BERTRAND"
PLUGIN_VERSION = "v0.0.0"
PLUGIN_EXT_DEPEDENCIES = "github@RickHulzinga/MayaVaccineVirusRemovalTool"

ANTIVIRUS_OBJECT = NULL

class MAYAAntivirusAutoscan():
    open_scene_job = NULL

    def __init__(self):
        self.Execute_Antivirus()
        self.open_scene_job = cmds.scriptJob(e=["SceneOpened", lambda: self.Execute_Antivirus()], protected=True)
    def haveWriteMethod(self):
        return True
    def haveReadMethod(self):
        return True

    # Code from github@RickHulzinga/MayaVaccineVirusRemovalTool  (https://github.com/RickHulzinga/MayaVaccineVirusRemovalTool)
    # Adapted by Louis BERTRAND
    # Cleans maya files from the vaccine.py virus
    def Vaccine_Remover(self):

        malicious_code_found = False
        scriptdir = cmds.internalVar(userAppDir=True) + 'scripts'

        virloc = os.path.join(scriptdir, "vaccine.py")

        if os.path.isfile(virloc):
            cmds.warning("Found vaccine.py in scriptlocation, removing ...")
            os.remove(virloc)
            malicious_code_found = True

        virloc = os.path.join(scriptdir, "vaccine.pyc")

        if os.path.isfile(virloc):
            cmds.warning("Found vaccine.pyc` in scriptlocation, removing ...")
            os.remove(virloc)
            malicious_code_found = True

        bannedNodes = ["vaccine_gene", "breed_gene"]

        for i in cmds.ls(type="script"):

            if i in bannedNodes:
                cmds.warning("Found malicious scriptnode '" + i + "', removing ...")
                cmds.delete(i)
                malicious_code_found = True

        return malicious_code_found

    def Execute_Antivirus(self):

        malicious_code_found = False
        print("Scanning for malicious scripts and nodes...")

        # VACCINE VIRUS DETECTION & REPAIRE (scene based)
        malicious_code_found = self.Vaccine_Remover()

        cmds.warning("Scene Clear")
        if not malicious_code_found:
            cmds.warning("No Malicious nodes found")


# creator
def antivirus_init():
    return OpenMayaMPx.asMPxPtr( MAYAAntivirusAutoscan() )

# initializer
def nodeInitializer():
    # nothing to do
    cmds.warning("Initializing plugin")
    

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, PLUGIN_COMPANY, PLUGIN_VERSION, "Any")
    try:
        print("  ")
        print("  ")
        print("%s" % PLUGIN_NAME)
        print("%s" % PLUGIN_VERSION)
        print("developed by %s" % PLUGIN_COMPANY)
        ANTIVIRUS_OBJECT = MAYAAntivirusAutoscan()
        print("Initialized Antivirus correctly")
        print("  ")
        print("  ")
    except:
        sys.stderr.write( "Failed to deregister command: %s" % PLUGIN_NAME )
        raise

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        ANTIVIRUS_OBJECT = NULL
        print("  ")
        print("  ")
        print("Uninitialized Antivirus correctly")
        print("  ")
        print("  ")
    except:
        sys.stderr.write( "Failed to deregister command: %s" % PLUGIN_NAME )
        raise
