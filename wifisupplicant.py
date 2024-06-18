import os
import random
import subprocess
import sys

# Function to display help
def display_help():
    print("Usage: python3 wifi_connect.py [SSID] [PASSWORD]")
    print()
    print("Connect to a new Wi-Fi network.")
    print()
    print("Arguments:")
    print("  SSID      SSID of the Wi-Fi network")
    print("  PASSWORD  Password of the Wi-Fi network")
    print()
    print("Example:")
    print("  sudo python3 wifi_connect.py MyWiFiNetwork MyWiFiPassword")
    sys.exit(1)

# Function to check if wlan exists
def it_exists(wlan):
    return os.system(f"ip link show {wlan}") == 0

# Function to mask password
def mask_password(password):
    mask_char='✱'
    mask_ratio=7 # Approximation of 0.7 * 10
    password_length=len(password)
    num_chars_to_mask=(password_length * mask_ratio) // 10

    for i in range(num_chars_to_mask):
        index_to_mask=random.randint(0, password_length-1)
        password=password[:index_to_mask] + mask_char + password[index_to_mask+1:]

    return password

def restart_networking():
    
    # Stop existing wpa_supplicant processes
    os.system("killall wpa_supplicant")

    # Remove existing control interface file
    if it_exists("wlan0"):
        os.system("rm -f /var/run/wpa_supplicant/wlan0")
    else:
        os.system("rm -f /var/run/wpa_supplicant/wlan1")

    # Restart networking service
    os.system("systemctl restart networking")

# Function to update wpa_supplicant
def update_wpa_supplicant(ssid, password):
    wpa_supplicant_conf="/etc/wpa_supplicant/wpa_supplicant-wlan1.conf"

    psk=subprocess.check_output(f"wpa_passphrase \"{ssid}\" \"{password}\" | grep -v '#psk' | grep 'psk' | cut -d= -f2", shell=True).decode().strip()

    if psk == "":
        print("Failed to generate PSK. Please check your SSID and password.")
        return

    masked_password=mask_password(password)

    network_config=f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=PH

network={{
ssid="{ssid}"
#psk="{masked_password}"
psk={psk}
key_mgmt=WPA-PSK
proto=RSN
pairwise=CCMP TKIP
group=CCMP TKIP
}}"""

    with open(wpa_supplicant_conf, 'w') as f:
        f.write(network_config)

    
    if __name__ == "__main__":
        restart_networking()
    else:
        # Restart networking from the loginpage.py
        pass



# Main function
if __name__ == "__main__":
    if len(sys.argv) != 3:
        display_help()

    ssid=sys.argv[1]
    password=sys.argv[2]

    update_wpa_supplicant(ssid, password)
