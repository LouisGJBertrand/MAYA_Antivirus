
from email.errors import MessageError
import os
import shutil
import sys
import webbrowser
import requests
import hashlib
import json

from asyncio.windows_events import NULL

import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx

PLUGIN_NAME = "Maya Antivirus Autoscan"
PLUGIN_COMPANY = "Louis BERTRAND"
PLUGIN_VERSION = "v0.0.1"
PLUGIN_EXT_DEPEDENCIES = "github@RickHulzinga/MayaVaccineVirusRemovalTool"

ANTIVIRUS_OBJECT = NULL

class ScanReport():

    MAYA_FileName = NULL
    MAYA_AppName = NULL
    MAYA_BatchMod = NULL
    MAYA_CustomVersion = NULL
    MAYA_Version = NULL

    ANTIVIRUS_DATA_DIR = cmds.internalVar(userAppDir=True) + "00_MAYA_ANTIVIRUS"

    SCAN_Date = NULL
    SCAN_Time = NULL
    SCAN_Positivity = False
    SCAN_Log = NULL




class MAYAAntivirusCore():

    scanResult = NULL

    Maya_AppName = NULL
    Maya_BatchMode = NULL
    Maya_CustomVersion = NULL
    Maya_Version = NULL

    ANTIVIRUS_DATA_DIR = cmds.internalVar(userAppDir=True) + "00_MAYA_ANTIVIRUS"
    ANTIVIRUS_DB_URL = "https://raw.githubusercontent.com/LouisGJBertrand/MAYA_Antivirus/main/db/malware_db.json"
    ANTIVIRUS_DB_HASH_URL = "https://raw.githubusercontent.com/LouisGJBertrand/MAYA_Antivirus/main/db/malware_db.json.md5"

    DataBase = NULL

    CurrentReport = NULL

    def CheckUpdate():
        url = "https://api.github.com/repos/LouisGJBertrand/MAYA_Antivirus/tags"
        tags = requests.get(url).json()

        if PLUGIN_VERSION != tags[0]["name"]:
            result = cmds.confirmDialog(
                title='Maya Antivirus Update',
                message='We\'ve detected that your malware version is not up to date anymore. please checkout the repository to update your antimalware',
                button=['Ok'],
                defaultButton='Ok',
                cancelButton='Ok',
                dismissString='Ok')
            webbrowser.open('https://github.com/LouisGJBertrand/MAYA_Antivirus/releases/latest')
            return False

        return True


    def Initialize():
        print("Initializing Environment Variables...")
        MAYAAntivirusCore.InitVars()
        print("Initializing Data Structures...")
        MAYAAntivirusCore.InitializeDataStructure()
        print("Reloading Database...")
        MAYAAntivirusCore.ReloadDatabase()

    def InitVars():
        MAYAAntivirusCore.Maya_AppName = cmds.about(version=True)
        MAYAAntivirusCore.Maya_BatchMode = cmds.about(version=True)
        MAYAAntivirusCore.Maya_CustomVersion = cmds.about(version=True)
        MAYAAntivirusCore.Maya_Version = cmds.about(version=True)

    def ValidateChecksum(filepath, md5):
            # Open,close, read file and calculate MD5 on its contents 
            with open(filepath, 'rb') as file_to_check:
                # read contents of the file
                data = file_to_check.read()    
                # pipe contents of the file through
                md5_returned = hashlib.md5(data).hexdigest()

            return md5 == md5_returned

    def DownloadRemoteData(url: str, dest_folder: str):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)  # create folder if it does not exist

        filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
        file_path = os.path.join(dest_folder, filename)

        r = requests.get(url, stream=True)
        if r.ok:
            print("saving to", os.path.abspath(file_path))
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))

    def InitializeDataStructure():
        l_av_path = MAYAAntivirusCore.ANTIVIRUS_DATA_DIR

        if not os.path.isdir(l_av_path):
            os.mkdir(l_av_path)

        if not os.path.isdir(l_av_path + "/QUARANTINE"):
            os.mkdir(l_av_path + "/QUARANTINE")

        if not os.path.isdir(l_av_path + "/reports"):
            os.mkdir(l_av_path + "/reports")

        if not os.path.isdir(l_av_path + "/db"):
            os.mkdir(l_av_path + "/db")

        if not os.path.isfile(l_av_path + "/db/malware_db.json"):
            MAYAAntivirusCore.DownloadRemoteData(MAYAAntivirusCore.ANTIVIRUS_DB_URL, l_av_path + "/db/")

        if not os.path.isfile(l_av_path + "/db/malware_db.json.md5"):
            MAYAAntivirusCore.DownloadRemoteData(MAYAAntivirusCore.ANTIVIRUS_DB_HASH_URL, l_av_path + "/db/")

    def ReloadDatabase():

        l_av_path = MAYAAntivirusCore.ANTIVIRUS_DATA_DIR

        database_path = l_av_path + "/db/malware_db.json"
        database_hash_path = l_av_path + "/db/malware_db.json.md5"
        database_hash_value = open(database_hash_path).read()


        checksumValidityTimeoutCounter = 10
        while not MAYAAntivirusCore.ValidateChecksum(database_path, database_hash_value):

            if checksumValidityTimeoutCounter <= 0:
                raise ValueError('Unable to validate the database')
            
            shutil.rmtree(l_av_path + "/db")
            MAYAAntivirusCore.InitializeDataStructure()
            checksumValidityTimeoutCounter -= 1


        f = open(database_path)
        MAYAAntivirusCore.DataBase = json.loads(f.read())

    def FormatPathString(str):
        str = str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True))
        str = str.replace("%mayaVersionSpecificUserDocDir%", cmds.internalVar(userAppDir=True) + MAYAAntivirusCore.Maya_Version)
        return str

    def ScanFilesAction(unformatedPath, fileNames, ifPositive):
        
        positivity = False

        for fileName in fileNames:
            virloc = MAYAAntivirusCore.FormatPathString(unformatedPath) + "/" + fileName

            if not os.path.isfile(virloc):
                continue

            if ifPositive == "Remove":
                os.remove(virloc)
                print ("      file %s has been removed" % fileName)
                positivity = True
                continue
                
            if ifPositive == "Quarantine":
                shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + fileName + ".infected"))
                print ("      file %s has been quarantined" % fileName)
                positivity = True
                continue

            # Default : Quarantine
            shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + fileName + ".infected"))
            print ("      file %s has been quarantined" % fileName)
            positivity = True
            continue
        return positivity

    def ScanNodes(nodeNames):
        bannedNodes = nodeNames

        positive = False

        for i in cmds.ls(type="script"):

            if i in bannedNodes:
                print(      "Found malicious scriptnode '%s', removing ..." % i)
                cmds.delete(i)
                positive = True

        return positive

    def ExecuteScan(verbose = True):

        # System Infos
        print("")
        print("------------------------------------------------------")
        print("")
        print("                MAYA ANTIVIRUS Scan")
        print("")
        print("System Infos")
        print(
            "AppName:" + str(cmds.about(application= True)) +
            ", BatchMode:" + str(cmds.about(batch=True)) +
            ", CustomVersion:" + str(cmds.about(customVersion=True)) +
            ", Version:" + str(cmds.about(version=True)))
        print("")
        print("")

        scanPositivity = False
        CurrentReport = ScanReport()

        # print (MAYAAntivirusCore.DataBase)
        # raise MessageError("DEBUG -- Break")

        for Malware in MAYAAntivirusCore.DataBase["db"]:


            print ("")
            print ("Searching for %s malware" % Malware["MalwareName"])
            print ("Malware Name: %s" % Malware["MalwareName"])
            print ("Malware ID: %s" % Malware["MalwareID"])
            print ("Malware Declaration URL: %s" % Malware["MalwareDeclarationURL"])
            print ("Malware Severity: %s" % Malware["MalwareSeverity"])
            print ("Malware Test count: %s" % len(Malware["Tests"]))

            for Test in Malware["Tests"]:
                print ("")
                TestName = Test["Name"]
                TestType = Test["Type"]

                if TestType == "Files":
                    print("   Test : %s" % TestName)
                    print("   Test Type : %s" % TestType)
                    if MAYAAntivirusCore.ScanFilesAction(Test["FolderPath"], Test["FilesName"], Test["IfPositive"]) :
                        print("   result positive, positive action : %s " % Test["IfPositive"])
                        continue
                    print("   result Negative, OK")
                    continue
                if TestType == "Nodes":
                    print("   Test : %s" % TestName)
                    print("   Test Type : %s" % TestType)
                    if MAYAAntivirusCore.ScanNodes(Test["NodeNames"]):
                        print("   result positive, malicious nodes removed")
                        continue
                    print("   result Negative, OK")
                    continue

                print ("      Test %s is not valid, continuing" % TestName)

        print ("")
        print ("Scan Ended")

        if scanPositivity:
            result = cmds.confirmDialog(
                title='Malware Alert',
                message='One or multiple malware had been detected in your maya configuration file. Please check the console to see the scan result.',
                button=['Ok'],
                defaultButton='Ok',
                cancelButton='Ok',
                dismissString='Ok')
            cmds.warning("Malware Found")
        print ("")
        print("------------------------------------------------------")
        print("")

class MAYAAntivirusAutoscan():

    open_scene_job = NULL
    save_scene_job = NULL

    def __init__(self):

        if not MAYAAntivirusCore.CheckUpdate():
            print('The malware plugin is not up to date anymore, it may cause issues')
            print('please update at https://github.com/LouisGJBertrand/MAYA_Antivirus/releases')

        MAYAAntivirusCore.Initialize()

        MAYAAntivirusCore.ExecuteScan()
        self.open_scene_job = cmds.scriptJob(e=["SceneOpened", lambda: MAYAAntivirusCore.ExecuteScan()], protected=True)
        self.save_scene_job = cmds.scriptJob(e=["SceneSaved", lambda: MAYAAntivirusCore.ExecuteScan()], protected=True)

    def haveWriteMethod(self):
        return True
    def haveReadMethod(self):
        return True

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
