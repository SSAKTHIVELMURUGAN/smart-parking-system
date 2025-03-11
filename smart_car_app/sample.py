import urequests
import network

WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
API_URL = "http://your-server-ip:5000/update_sensor"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    while not wlan.isconnected():
        pass  # Wait until connected

def send_data(slot_name, status):
    data = {"slot_name": slot_name, "status": status}
    response = urequests.post(API_URL, json=data)
    print(response.text)

connect_wifi()

# Example: Send sensor data (Replace with real sensor logic)
send_data("A1", 1)  # A1 slot occupied
