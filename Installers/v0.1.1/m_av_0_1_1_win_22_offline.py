
import ctypes
import os
import subprocess
import requests

from posixpath import expanduser



class MayaAntivirusInstallationProgram:


    def PromptMayaInstallPath(maya_install_path):
        print("Maya has not beein detected on yout device")
        maya_install_path=input("Maya Install Path : ")
        while not os.path.isdir(maya_install_path):
            print("Maya has not beein detected on yout device")
            maya_install_path=input("Maya Install Path : ")
        return maya_install_path

    def CheckMayaInstallPath(maya_install_path):
        print("Verifying Maya Install Path...")
        while not os.path.isfile(maya_install_path + "\\bin\\mayapy.exe"):
            maya_install_path = MayaAntivirusInstallationProgram.PromptMayaInstallPath(maya_install_path)
            print("Verifying Maya Install Path...")
        print("Maya Installation is valid")
        return maya_install_path

    def InstallDependencies(maya_install_path):

        subprocess.run([maya_install_path+"\\bin\\mayapy.exe", "-m", "pip", "install", "requests"])

    def DownloadRemoteData(url: str, dest_folder: str):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)  # create folder if it does not exist

        filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
        file_path = os.path.join(dest_folder, filename)

        r = requests.get(url, stream=True)
        if not r.ok:
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))
        print("saving to", os.path.abspath(file_path))
        f = open(file_path, 'wb')
        for chunk in r.iter_content(chunk_size=1024 * 8):
            if not chunk:
                break
            f.write(chunk)
            f.flush()
            os.fsync(f.fileno())

    def Install(args):

        print("")
        print("MAYA-Antivirus Installation Program")
        print("")

        l_maya_install_path = MayaAntivirusInstallationProgram.CheckMayaInstallPath("C:\\Program Files\\Autodesk\\Maya2022")

        print("")
        print("Installing Dependencies")
        print("")

        MayaAntivirusInstallationProgram.InstallDependencies(l_maya_install_path)

        latest_release_url = "https://api.github.com/repos/LouisGJBertrand/MAYA_Antivirus/releases/tags/v0.1.0"

        try:
            latest_release = requests.get(latest_release_url).json()
        except:
            print("Unable to reach remote github server...\nplease download and install manually the plugin in Document/Maya/<Version>/plug-ins.")
            return

        latest_asset_url = latest_release["assets"][0]["browser_download_url"]

        ## User Dir
        shell32 = ctypes.OleDLL('shell32')
        buf = ctypes.create_unicode_buffer(4096)
        shell32.SHGetFolderPathW(0, 5, 0, 0, buf)
        install_path = buf.value

        plugin_script_data = r'''


from array import array
from datetime import date
from email.errors import MessageError
import os
from pickle import TRUE
import shutil
import sys
from time import sleep
import time
import webbrowser
import requests
import hashlib
import json

from asyncio.windows_events import NULL

import maya.cmds as cmds
import maya.OpenMayaMPx as OpenMayaMPx

PLUGIN_NAME = "Maya Antivirus Autoscan"
PLUGIN_COMPANY = "Studio Trente Trente-Six"
PLUGIN_VERSION = "v0.1.1"
PLUGIN_EXT_DEPEDENCIES = ""

class MAYAAV_MEM:
    ANTIVIRUS_OBJECT = NULL

class Debug:
    def Break(str=NULL):
        if not str == NULL : print (str)
        raise MessageError("Debug.Break")

class ScanReport():

    MAYA_FileName = NULL
    MAYA_AppName = NULL
    MAYA_BatchMod = NULL
    MAYA_CustomVersion = NULL
    MAYA_Version = NULL

    ANTIVIRUS_DATA_DIR = cmds.internalVar(userAppDir=True) + "00_MAYA_ANTIVIRUS"
    ANTIVIRUS_VERSION = cmds.internalVar(userAppDir=True) + "00_MAYA_ANTIVIRUS"

    SCAN_Date = NULL
    SCAN_Time = NULL
    SCAN_Positivity = False
    SCAN_Log = ""

    def RecordString(self, string: str, verbose: bool):
        ScanReport.SCAN_Log += string
        if verbose:
            print(string, end='')
    def RecordLine(self, string: str, verbose: bool):
        ScanReport.SCAN_Log += string + "\n"
        if verbose:
            print(string)

    def ExportToFile(self, filePath: str):
        f = open(filePath, 'w')
        f.write("Exported Scan\n")
        f.write("\n")
        f.write("MAYA_FileName: %s\n" % self.MAYA_FileName)
        f.write("MAYA_AppName: %s\n" % self.MAYA_AppName)
        f.write("MAYA_BatchMod: %s\n" % self.MAYA_BatchMod)
        f.write("MAYA_CustomVersion: %s\n" % self.MAYA_CustomVersion)
        f.write("MAYA_Version: %s\n" % self.MAYA_Version)
        f.write("\n")
        f.write("ANTIVIRUS_DATA_DIR: %s\n" % self.ANTIVIRUS_DATA_DIR)
        f.write("ANTIVIRUS_VERSION: %s\n" % self.ANTIVIRUS_VERSION)
        f.write("\n")
        f.write("SCAN_Date: %s\n" % self.SCAN_Date)
        f.write("SCAN_Time: %s\n" % self.SCAN_Time)
        f.write("SCAN_Positivity: %s\n" % self.SCAN_Positivity)
        f.write("SCAN_Log: \'\'\'\n%s\n\n\'\'\'\n\n" % self.SCAN_Log)
        f.flush()

    def GenerateFileName(self):
        return "scanReport."+self.MAYA_FileName+"."+str(self.SCAN_Date)+str(self.SCAN_Time)+".log"

class MAYAAntivirusCore():

    scanResult = NULL

    MAYA_AppName = NULL
    MAYA_BatchMode = NULL
    MAYA_CustomVersion = NULL
    MAYA_Version = NULL

    ANTIVIRUS_DATA_DIR = cmds.internalVar(userAppDir=True) + "00_MAYA_ANTIVIRUS"
    ANTIVIRUS_DB_URL = "https://raw.githubusercontent.com/LouisGJBertrand/MAYA_Antivirus/main/db/malware_db.json"
    ANTIVIRUS_DB_HASH_URL = "https://raw.githubusercontent.com/LouisGJBertrand/MAYA_Antivirus/main/db/malware_db.json.md5"

    DataBase = NULL

    CurrentReport = NULL

    LAST_REPORT_TIMER=0
    SESSION_SCAN_COUNT=0
    UPDATE_CLOCK=0
    CLK_DELTA=0

    ONLINE_CONNECTED = True

    def AnalyseUpdateTag(tag: str):
        l_ver = tag.split("-")[0].split(".")

        ## l_nightly_build_id = float(tag.split("-")[1]/(10 ** len(tag.split("-")[1])))
        l_i = 0
        for l_ver_el in l_ver:
            l_ver[l_i] = float(l_ver_el.replace("v","0"))
            l_i += 1

        return l_ver
    
    def CalculateVersionTag(tag: array):
        l_ver_calc = 0
        tag = tag[::-1]
        for l_i in range(0, len(tag)):
            l_ver_calc += tag[l_i] * (10 ** (l_i * 3))

        return l_ver_calc

    def CheckUpdate():
        url = "https://api.github.com/repos/LouisGJBertrand/MAYA_Antivirus/tags"

        try:
            tags = requests.get(url).json()

        except:
            MAYAAntivirusCore.ONLINE_CONNECTED = False
            print("Remote servers are unreachable, will proceed offline...")

            return True

        l_remote_tag_ver = MAYAAntivirusCore.CalculateVersionTag(MAYAAntivirusCore.AnalyseUpdateTag(tags[0]["name"]))
        l_local_tag_ver = MAYAAntivirusCore.CalculateVersionTag(MAYAAntivirusCore.AnalyseUpdateTag(PLUGIN_VERSION))

        # Debug.Break("VersionTest:\n"+str(l_remote_tag_ver)+"\n"+str(l_local_tag_ver)) #

        if l_local_tag_ver < l_remote_tag_ver:
            result = cmds.confirmDialog(
                title='Maya Antivirus Update',
                message='We\'ve detected that your antimalware version is not up to date anymore. please checkout the repository to update your antimalware',
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
        print("Initializing Internal UPDATE_CLOCK...")
        MAYAAntivirusCore.UPDATE_CLOCK = time.time()

    def InitVars():
        MAYAAntivirusCore.MAYA_AppName = cmds.about(version=True)
        MAYAAntivirusCore.MAYA_BatchMode = cmds.about(version=True)
        MAYAAntivirusCore.MAYA_CustomVersion = cmds.about(version=True)
        MAYAAntivirusCore.MAYA_Version = cmds.about(version=True)

    def CalculateMD5(filepath):
        f = open(filepath,'rb')
        m = hashlib.md5()
        while True:
            ## Don't read the entire file at once...
            data = f.read(10240)
            if len(data) == 0:
                break
            m.update(data)
        return m.hexdigest()

    def ValidateChecksum(filepath, md5):

            md5_returned = MAYAAntivirusCore.CalculateMD5(filepath)

            # print("local db hash: %s" % md5_returned)
            # print("local db hash verification: %s" % md5)

            return md5 == md5_returned

    def DownloadRemoteData(url: str, dest_folder: str):
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)  # create folder if it does not exist

        filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
        file_path = os.path.join(dest_folder, filename)

        r = requests.get(url, stream=True)
        if not r.ok:
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))
        print("saving to", os.path.abspath(file_path))
        f = open(file_path, 'wb')
        for chunk in r.iter_content(chunk_size=1024 * 8):
            if not chunk:
                break
            f.write(chunk)
            f.flush()
            os.fsync(f.fileno())

    def CompareHashToRemote(hash: str, remote_url: str):

        r = requests.get(remote_url, stream=True)
        return hash == r.text

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

        if not MAYAAntivirusCore.ONLINE_CONNECTED:
            if not MAYAAntivirusCore.ValidateChecksum(database_path, database_hash_value):
                cmds.confirmDialog( title='Invalid Malware Database', message='Remote servers can\'t be accessed and local DB cannot be validated.\nMaya Antivirus will be desactivated for the current session.', button=['OK'], defaultButton='OK', cancelButton='OK', dismissString='OK' )
                return
            print("Local database has been validated without remote checking due to lack of internet connectivity.")
            f = open(database_path)
            MAYAAntivirusCore.DataBase = json.loads(f.read())
            return

        if not MAYAAntivirusCore.CompareHashToRemote(
            database_hash_value,
            MAYAAntivirusCore.ANTIVIRUS_DB_HASH_URL):
            print("")
            print("Local Hash does not match remote Hash")
            print("Removing Previous DB...")
            print("")
            shutil.rmtree(l_av_path + "/db")

            MAYAAntivirusCore.InitializeDataStructure()
            database_hash_value = open(database_hash_path).read()

        checksumValidityTimeoutCounter = 10
        while not MAYAAntivirusCore.ValidateChecksum(database_path, database_hash_value):
            if checksumValidityTimeoutCounter <= 0:
                raise ValueError('Unable to validate the database')
            
            shutil.rmtree(l_av_path + "/db")
            MAYAAntivirusCore.InitializeDataStructure()
            database_hash_value = open(database_hash_path).read()
            checksumValidityTimeoutCounter -= 1


        f = open(database_path)
        MAYAAntivirusCore.DataBase = json.loads(f.read())

    def FormatPathString(str):
        str = str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True))
        str = str.replace("%mayaVersionSpecificUserDocDir%", cmds.internalVar(userAppDir=True) + MAYAAntivirusCore.MAYA_Version)
        str = str.replace("%mayaVersion%", MAYAAntivirusCore.MAYA_Version)
        return str

    def ScanFilesAction(unformatedPath, fileNames, ifPositive, report: ScanReport, verbose: bool):
        
        positivity = False

        for fileName in fileNames:
            virloc = MAYAAntivirusCore.FormatPathString(unformatedPath) + "/" + fileName

            if not os.path.isfile(virloc):
                continue

            if ifPositive == "Remove":
                os.remove(virloc)
                report.RecordLine("      file %s has been removed" % fileName, verbose)
                positivity = True
                continue
                
            if ifPositive == "Quarantine":
                shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + fileName + ".infected"))
                report.RecordLine("      file %s has been quarantined" % fileName, verbose)
                positivity = True
                continue

            # Default : Quarantine
            shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + fileName + ".infected"))
            report.RecordLine("      file %s has been quarantined" % fileName, verbose)
            positivity = True
            continue
        return positivity

    # INDEV
    # TODO: JSONParsing, Tests, Validate
    def ScanFilesMD5HashAction(unformatedPath, hashValues, ifPositive, report: ScanReport, verbose: bool):
        
        positivity = False


        virloc = MAYAAntivirusCore.FormatPathString(unformatedPath) + "/"

        l_fileTree = os.walk(virloc)

        for childname in l_fileTree:

            if os.path.isdir(virloc + childname):
                positivity = MAYAAntivirusCore.ScanFilesHashAction(virloc + childname, hashValues, ifPositive)
                continue

            for hash in hashValues:

                if not MAYAAntivirusCore.ValidateChecksum(childname, hash):
                    continue

                if ifPositive == "Remove":
                    os.remove(virloc)
                    report.RecordLine("      file %s has been removed" % childname, verbose)
                    positivity = True
                    continue

                if ifPositive == "Quarantine":
                    shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + childname + ".infected"))
                    report.RecordLine("      file %s has been quarantined" % childname, verbose)
                    positivity = True
                    continue

                # Default : Quarantine
                shutil.copyfile(virloc, str.replace("%mayaUserDocDir%", cmds.internalVar(userAppDir=True) + "QUARANTINE/" + childname + ".infected"))
                report.RecordLine("      file %s has been quarantined" % childname, verbose)
                positivity = True
                continue
        return positivity

    def ScanNodes(nodeNames, report: ScanReport, verbose: bool):
        bannedNodes = nodeNames

        positive = False

        for i in cmds.ls(type="script"):

            if i in bannedNodes:
                report.RecordLine(      "Found malicious scriptnode '%s', removing ..." % i, verbose)
                cmds.delete(i)
                positive = True

        return positive

    def AV_Clock_Update():
        MAYAAntivirusCore.CLK_DELTA = l_delta_time = time.time() - MAYAAntivirusCore.UPDATE_CLOCK
        MAYAAntivirusCore.LAST_REPORT_TIMER += l_delta_time
        MAYAAntivirusCore.UPDATE_CLOCK = time.time()

    def ExecuteScan(l_verbose = True, saveReport = True):

        MAYAAntivirusCore.AV_Clock_Update()

        # print ("\n")
        # print ("LAST_REPORT_TIMER:%s"%MAYAAntivirusCore.LAST_REPORT_TIMER)
        # print ("SESSION_SCAN_COUNT:%s"%MAYAAntivirusCore.SESSION_SCAN_COUNT)
        # print ("UPDATE_CLOCK:%s"%MAYAAntivirusCore.UPDATE_CLOCK)
        # print ("CLK_DELTA:%s"%MAYAAntivirusCore.CLK_DELTA)
        # print ("\n")

        if MAYAAntivirusCore.LAST_REPORT_TIMER < 5 & MAYAAntivirusCore.SESSION_SCAN_COUNT != 0:
            return

        l_ScanReport = ScanReport()

        l_ScanReport.MAYA_FileName = os.path.basename(cmds.file(q=True, sn=True)).split('/')[-1].replace(".","_")

        if l_ScanReport.MAYA_FileName == "":
            l_ScanReport.MAYA_FileName = "untitled_ma"

        l_ScanReport.SCAN_Date = str(date.today())
        l_ScanReport.SCAN_Time = str(time.time())

        l_ScanReport.MAYA_AppName = MAYAAntivirusCore.MAYA_AppName
        l_ScanReport.MAYA_BatchMod = MAYAAntivirusCore.MAYA_BatchMode
        l_ScanReport.MAYA_CustomVersion = MAYAAntivirusCore.MAYA_CustomVersion
        l_ScanReport.MAYA_Version = MAYAAntivirusCore.MAYA_Version

        l_ScanReport.ANTIVIRUS_VERSION = PLUGIN_VERSION

        # System Infos
        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("------------------------------------------------------", l_verbose)
        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("                MAYA ANTIVIRUS Scan", l_verbose)
        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("System Infos", l_verbose)
        l_ScanReport.RecordLine(
            "AppName:" + str(cmds.about(application= True)) +
            ", BatchMode:" + str(cmds.about(batch=True)) +
            ", CustomVersion:" + str(cmds.about(customVersion=True)) +
            ", Version:" + str(cmds.about(version=True)), l_verbose)
        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("", l_verbose)

        l_scanPositivity = False

        # print (MAYAAntivirusCore.DataBase)
        # raise MessageError("DEBUG -- Break")

        for l_Malware in MAYAAntivirusCore.DataBase["db"]:

            l_ScanReport.RecordLine("", l_verbose)
            l_ScanReport.RecordLine("Searching for %s malware" % l_Malware["MalwareName"], l_verbose)
            l_ScanReport.RecordLine("Malware Name: %s" % l_Malware["MalwareName"], l_verbose)
            l_ScanReport.RecordLine("Malware ID: %s" % l_Malware["MalwareID"], l_verbose)
            l_ScanReport.RecordLine("Malware Declaration URL: %s" % l_Malware["MalwareDeclarationURL"], l_verbose)
            l_ScanReport.RecordLine("Malware Severity: %s" % l_Malware["MalwareSeverity"], l_verbose)
            l_ScanReport.RecordLine("Malware Test count: %s" % len(l_Malware["Tests"]), l_verbose)

            for l_Test in l_Malware["Tests"]:

                l_ScanReport.RecordLine("", l_verbose)
                TestName = l_Test["Name"]
                l_TestType = l_Test["Type"]

                if l_TestType == "Files":
                    l_ScanReport.RecordLine("   Test : %s" % TestName, l_verbose)
                    l_ScanReport.RecordLine("   Test Type : %s" % l_TestType, l_verbose)
                    if MAYAAntivirusCore.ScanFilesAction(l_Test["FolderPath"], l_Test["FilesName"], l_Test["IfPositive"], l_ScanReport, l_verbose) :
                        l_scanPositivity = True
                        l_ScanReport.RecordLine("   result positive, positive action : %s " % l_Test["IfPositive"], l_verbose)
                        continue
                    l_ScanReport.RecordLine("   result Negative, OK", l_verbose)
                    continue

                if l_TestType == "Nodes":
                    l_ScanReport.RecordLine("   Test : %s" % TestName, l_verbose)
                    l_ScanReport.RecordLine("   Test Type : %s" % l_TestType, l_verbose)
                    if MAYAAntivirusCore.ScanNodes(l_Test["NodeNames"], l_ScanReport, l_verbose):
                        l_scanPositivity = True
                        l_ScanReport.RecordLine("   result positive, malicious nodes removed", l_verbose)
                        continue
                    l_ScanReport.RecordLine("   result Negative, OK", l_verbose)
                    continue

                # TODO: Implement MD5FileHash
                if l_TestType == "MD5FileHash":
                    print("NOT IMPLEMENTED YET, IGNORING")
                    continue

                l_ScanReport.RecordLine("      Test %s is not valid, continuing" % TestName, l_verbose)

        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("Scan Ended", l_verbose)

        if l_scanPositivity:
            result = cmds.confirmDialog(
                title='Malware Alert',
                message='One or multiple malware had been detected in your maya configuration file. Please check the console to see the scan result.',
                button=['Ok'],
                defaultButton='Ok',
                cancelButton='Ok',
                dismissString='Ok')
            l_ScanReport.RecordLine("Malware Found", l_verbose)

        l_ScanReport.RecordLine("", l_verbose)
        l_ScanReport.RecordLine("------------------------------------------------------", l_verbose)
        l_ScanReport.RecordLine("", l_verbose)

        l_ScanReport.SCAN_Positivity = l_scanPositivity

        if l_scanPositivity & saveReport:
            ReportSavePath =  MAYAAntivirusCore.ANTIVIRUS_DATA_DIR + "/reports/" + l_ScanReport.GenerateFileName()
            l_ScanReport.ExportToFile(ReportSavePath)
            print("\nREPORT SAVED AT : %s\n" % ReportSavePath)

        MAYAAntivirusCore.LAST_REPORT_TIMER = 0
        MAYAAntivirusCore.SESSION_SCAN_COUNT += 1


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
        #self.open_scene_job = cmds.scriptJob(e=["SceneOpened", lambda: MAYAAntivirusCore.ExecuteScan()], protected=True)

    def uninit(self):
        cmds.scriptJob( kill=self.open_scene_job, force=True)
        cmds.scriptJob( kill=self.save_scene_job, force=True)

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
    cmds.warning("Initializing %s plugin" % PLUGIN_NAME)

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, PLUGIN_COMPANY, PLUGIN_VERSION, "Any")
    try:
        print("  ")
        print("  ")
        print("%s" % PLUGIN_NAME)
        print("%s" % PLUGIN_VERSION)
        print("developed by %s" % PLUGIN_COMPANY)
        MAYAAV_MEM.ANTIVIRUS_OBJECT = MAYAAntivirusAutoscan()
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
        MAYAAV_MEM.ANTIVIRUS_OBJECT.uninit()
        MAYAAV_MEM.ANTIVIRUS_OBJECT = NULL
        print("  ")
        print("  ")
        print("Uninitialized Antivirus correctly")
        print("  ")
        print("  ")
    except:
        sys.stderr.write( "Failed to deregister command: %s" % PLUGIN_NAME )
        raise


'''

        print("")
        try:
            f = open(install_path+"/louisgjbertrand_Maya_Antivirus.py", "w")
            f.write(plugin_script_data)
            f.flush()
        except:
            print("")
            print("Unable to install the plugin.\nThis can be caused by your computer security system, try executing as admin/superuser or authorize the install program in your anti-malware.")
            print("")
            return

def main():
    MayaAntivirusInstallationProgram.Install([""])

if __name__ == '__main__':
    main()