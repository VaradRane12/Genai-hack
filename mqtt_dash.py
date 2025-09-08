import paho.mqtt.client as mqtt
import streamlit as st
from datetime import datetime
import time
import threading

# ==== MQTT CONFIG ====
BROKER = "test.mosquitto.org"
PORT = 1883
TOPICS = ["parking/slot1", "parking/slot2", "home/intrusion/alerts"]

# ==== GLOBAL STATE (thread-safe access with lock) ====
state_lock = threading.Lock()
slot_status = {"parking/slot1": "unknown", "parking/slot2": "unknown"}
slot_update = {"parking/slot1": None, "parking/slot2": None}
alerts = []

# ==== MQTT CALLBACKS ====
def on_connect(client, userdata, flags, rc):
    for t in TOPICS:
        client.subscribe(t)

def on_message(client, userdata, msg):
    global slot_status, slot_update, alerts
    payload = msg.payload.decode()
    topic = msg.topic

    with state_lock:
        if topic in slot_status:
            slot_status[topic] = payload
            slot_update[topic] = datetime.now().strftime("%H:%M:%S")
        elif topic == "home/intrusion/alerts":
            alerts.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] {payload}")
            if len(alerts) > 10:
                alerts.pop()

# ==== MQTT CLIENT (background thread) ====
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

# ==== STREAMLIT UI ====
st.set_page_config(page_title="Smart Home Dashboard", page_icon="🏠", layout="wide")
st.title("🏠 Smart Home Dashboard")

slot1_col, slot2_col = st.columns(2)
slot1_box = slot1_col.empty()
slot2_box = slot2_col.empty()
alerts_box = st.empty()

# Live update loop
while True:
    with state_lock:
        s1 = slot_status["parking/slot1"]
        s2 = slot_status["parking/slot2"]
        u1 = slot_update["parking/slot1"]
        u2 = slot_update["parking/slot2"]
        a_copy = alerts.copy()

    # Slot 1
    with slot1_box.container():
        st.subheader("🚗 Slot 1")
        if s1 == "occupied":
            st.error("Occupied")
        elif s1 == "free":
            st.success("Free")
        else:
            st.warning("Waiting for data...")
        if u1:
            st.caption(f"Last update: {u1}")

    # Slot 2
    with slot2_box.container():
        st.subheader("🚗 Slot 2")
        if s2 == "occupied":
            st.error("Occupied")
        elif s2 == "free":
            st.success("Free")
        else:
            st.warning("Waiting for data...")
        if u2:
            st.caption(f"Last update: {u2}")

    # Intrusion alerts
    with alerts_box.container():
        st.header("🚨 Intrusion Alerts")
        if a_copy:
            for alert in a_copy:
                st.error(alert)
        else:
            st.info("No intrusion alerts yet")

    time.sleep(1)

