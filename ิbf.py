import random
import pyautogui
import time
import subprocess
import os


def scan_wifi():
    # Scan for available networks
    scan_result = subprocess.run(["netsh", "wlan", "show", "networks"], capture_output=True, text=True, check=True)
    
    # Print the result
    print(scan_result.stdout)

# Usage
scan_wifi()

YourWiFiName = input("Enter YourWiFiName: ")

def connect_to_wifi(network_name, password):
    # Create an XML profile
    xml = f"""<?xml version="1.0"?>
    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
        <name>{network_name}</name>
        <SSIDConfig>
            <SSID>
                <name>{network_name}</name>
            </SSID>
        </SSIDConfig>
        <connectionType>ESS</connectionType>
        <MSM>
            <security>
                <authEncryption>
                    <authentication>WPA2PSK</authentication>
                    <encryption>AES</encryption>
                    <useOneX>false</useOneX>
                </authEncryption>
                <sharedKey>
                    <keyType>passPhrase</keyType>
                    <protected>false</protected>
                    <keyMaterial>{password}</keyMaterial>
                </sharedKey>
            </security>
        </MSM>
    </WLANProfile>"""

    # Save the XML to a temporary file
    with open('wifi.xml', 'w') as f:
        f.write(xml)
    try:
    # Add the WiFi profile
        subprocess.run(["netsh", "wlan", "add", "profile", "filename=wifi.xml"], check=True)

    # Try to connect to the WiFi network
        subprocess.run(["netsh", "wlan", "connect", "name=" + network_name], check=True)
        print(f"Successfully connected to {network_name}!")

    except subprocess.CalledProcessError:
        # If the connection fails, print an error message
        print(f"Failed to connect to {network_name}. Please check the network name and password.")
    finally:
    # Delete the temporary file
        os.remove('wifi.xml')
    
# Usage



# abcdefghijklmnopqrstuvwxyz    add to character to strong random and long time...
character="0123456789"
character_list=list(character)
password= pyautogui.password("Enter password to try hack!")
guss_password=''
attempts = 0

start_time = time.time()

while (guss_password != list(password)):
    guss_password=random.choices(character_list,k=len(password))
    print(">>>>>"+str(guss_password)+"<<<<<")
    connect_to_wifi(YourWiFiName, guss_password)
    attempts += 1

end_time = time.time()

print("Your password is: ", "".join(guss_password))
print("Number of attempts: ", attempts)
print("Time used: ", end_time - start_time, "seconds")
if end_time - start_time > 20:
    print("Your password is strong.")
else:
    print("Your password is weak.")
