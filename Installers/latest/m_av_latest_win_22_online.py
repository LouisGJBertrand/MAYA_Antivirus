
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

        latest_release_url = "https://api.github.com/repos/LouisGJBertrand/MAYA_Antivirus/releases/latest"

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

        print("")
        try:
            MayaAntivirusInstallationProgram.DownloadRemoteData(latest_asset_url, install_path +'\\maya\\2022\\plug-ins')
        except:
            print("")
            print("Unable to install the plugin.\nThis can be caused by your computer security system, try executing as admin/superuser or authorize the install program in your anti-malware.")
            print("")
            return

def main():
    MayaAntivirusInstallationProgram.Install([""])

if __name__ == '__main__':
    main()