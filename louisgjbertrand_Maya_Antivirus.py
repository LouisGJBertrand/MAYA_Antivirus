from asyncio.windows_events import NULL

import os
import sys
import asyncio

import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx
import threading

PLUGIN_NAME = "Maya Antivirus Autoscan"
PLUGIN_COMPANY = "Louis BERTRAND"
PLUGIN_VERSION = "v0.0.0"
PLUGIN_EXT_DEPEDENCIES = "github@RickHulzinga/MayaVaccineVirusRemovalTool"

ANTIVIRUS_OBJECT = NULL

class ScanResult():

    VaccineTrace = False
    VaccineTrace_Script = False
    VaccineTrace_Script_Cached = False
    VaccineTrace_Script_VersionSpecific = False
    VaccineTrace_Script_VersionSpecific_Cached = False
    VaccineTrace_Vaccine_OR_Breed_Node = False

    def __repr__(self):
        return "ScanResult()"
    def __str__(self):
        return "member of ScanResult"

    def Log(self):
        outputString = " \n"
        outputString += " -+--------------------------------------------------------------------+-\n"
        outputString += " \n"
        outputString += "Antivirus Scan Report\n"
        outputString += " \n"
        outputString += "VaccineTrace: "+str(self.VaccineTrace)+"\n"
        outputString += "+ VaccineTrace_Script: "+str(self.VaccineTrace_Script)+"\n"
        outputString += "+ VaccineTrace_Script_Cached: "+str(self.VaccineTrace_Script_Cached)+"\n"
        outputString += "+ VaccineTrace_Script_VersionSpecific: "+str(self.VaccineTrace_Script_VersionSpecific)+"\n"
        outputString += "+ VaccineTrace_Script_VersionSpecific_Cached: "+str(self.VaccineTrace_Script_VersionSpecific_Cached)+"\n"
        outputString += "+ VaccineTrace_Vaccine_OR_Breed_Node: "+str(self.VaccineTrace_Vaccine_OR_Breed_Node)+"\n"
        outputString += " \n"
        outputString += " -+--------------------------------------------------------------------+-\n"
        outputString += " \n"

        return outputString




class MAYAAntivirusAutoscan():

    open_scene_job = NULL
    scanResult = NULL

    Maya_AppName = NULL
    Maya_BatchMode = NULL
    Maya_CustomVersion = NULL
    Maya_Version = NULL


    def __init__(self):
        self.Execute_Antivirus()
        self.open_scene_job = cmds.scriptJob(e=["SceneOpened", lambda: self.Execute_Antivirus()], protected=True)
        self.open_scene_job = cmds.scriptJob(e=["SceneSaved", lambda: self.Execute_Antivirus()], protected=True)

    def haveWriteMethod(self):
        return True
    def haveReadMethod(self):
        return True
    def InitVars(self):
        self.Maya_AppName = cmds.about(version=True)
        self.Maya_BatchMode = cmds.about(version=True)
        self.Maya_CustomVersion = cmds.about(version=True)
        self.Maya_Version = cmds.about(version=True)


    # Code from github@RickHulzinga/MayaVaccineVirusRemovalTool  (https://github.com/RickHulzinga/MayaVaccineVirusRemovalTool)
    # Adapted by Louis BERTRAND
    # Cleans maya files from the vaccine.py virus
    def VaccineAntigene(self, verbose = True):

        if verbose:
            print("Searching for Vaccine")

        l_malicious_code_found = False

        scriptdir = cmds.internalVar(userAppDir=True) + 'scripts'
        if verbose:
            print ("scriptdir: "+scriptdir)

        ver_spec_scriptdir = cmds.internalVar(userAppDir=True) + self.Maya_Version + '/scripts'
        if verbose:
            print ("ver_spec_scriptdir: "+scriptdir)


        # VACCINE.PY
        virloc = os.path.join(scriptdir, "vaccine.py")
        ver_spec_virloc = os.path.join(ver_spec_scriptdir, "vaccine.py")

        if os.path.isfile(virloc):
            cmds.warning("Found vaccine.py in scriptlocation, removing ...")
            os.remove(virloc)
            l_malicious_code_found = True
            self.scanResult.VaccineTrace_Script = True
        else:
            if verbose:
                print("vaccine.py not found in scriptlocation, OK")

        if os.path.isfile(ver_spec_virloc):
            cmds.warning("Found vaccine.py in version specific scriptlocation, removing ...")
            os.remove(ver_spec_virloc)
            l_malicious_code_found = True
            self.scanResult.VaccineTrace_Script_VersionSpecific = True
        else:
            if verbose:
                print("vaccine.py not found in version specific scriptlocation, OK")


        # VACCINE.PYC
        virloc = os.path.join(scriptdir, "__pycache__/vaccine.pyc")
        ver_spec_virloc = os.path.join(ver_spec_scriptdir, "__pycache__/vaccine.pyc")

        if os.path.isfile(virloc):
            cmds.warning("Found vaccine.pyc` in scriptlocation, removing ...")
            os.remove(virloc)
            l_malicious_code_found = True
            self.scanResult.VaccineTrace_Script_Cached = True
        else:
            if verbose:
                print("vaccine.pyc not found in scriptlocation, OK")

        if os.path.isfile(ver_spec_virloc):
            cmds.warning("Found vaccine.py in version specific scriptlocation, removing ...")
            os.remove(ver_spec_virloc)
            l_malicious_code_found = True
            self.scanResult.VaccineTrace_Script_VersionSpecific_Cached = True
        else:
            if verbose:
                print("vaccine.pyc not found in version specific scriptlocation, OK")

        bannedNodes = ["vaccine_gene", "breed_gene"]

        for i in cmds.ls(type="script"):

            if i in bannedNodes:
                cmds.warning("Found malicious scriptnode '" + i + "', removing ...")
                cmds.delete(i)
                self.scanResult.VaccineTrace_Vaccine_OR_Breed_Node = True
                l_malicious_code_found = True

        if l_malicious_code_found:
            cmds.warning("traces of vaccine & breed had been found in your file or in your maya files")
            self.scanResult.VaccineTrace = True

        return l_malicious_code_found

    def Execute_Antivirus(self):


        # System Infos
        print("")
        print("System Infos")
        print(
            "AppName:" + str(cmds.about(application= True)) +
            ", BatchMode:" + str(cmds.about(batch=True)) +
            ", CustomVersion:" + str(cmds.about(customVersion=True)) +
            ", Version:" + str(cmds.about(version=True)))
        print("")
        print("")


        self.InitVars()


        self.scanResult = ScanResult()
        self.malicious_code_found = False
        l_malicious_code_found = self.malicious_code_found

        print("Start Malware Scan...")


        # VACCINE VIRUS DETECTION & REPAIRE (scene based)
        l_malicious_code_found = l_malicious_code_found or self.VaccineAntigene(True)


        cmds.warning("Scene Clear")
        if l_malicious_code_found:
            result = cmds.confirmDialog(
                title='Malware Alert',
                message='One or multiple malware had been detected in your maya configuration file. Please check the console to see the scan result.',
                button=['Ok'],
                defaultButton='Ok',
                cancelButton='Ok',
                dismissString='Ok')
            cmds.warning("Malware Found")
        else:
            cmds.warning("No Malicious nodes found")


        self.malicious_code_found = l_malicious_code_found
        print(self.scanResult.Log())

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
