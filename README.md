# musicbox
This project is an open-source solution for media playback with **NTAGs**, **MQTT commands**, and providing an optional **web interface**. Designed to integrate seamlessly with platforms like **Home Assistant**, it offers a fun and flexible way to control smart devices or trigger automations using NFC tags and remote controls.

---

## **Features**

### 1. **NTAG Reading and Writing with MFRC522**
This project utilizes the **MFRC522** RFID reader to read and write NTAGs in the NFC Data Exchange Format (NDEF).

### 2. **MQTT Integration**
The project communicates can communicate with MQTT-compatible (eg Home Assistant) by publishing commands to a configurable MQTT topic. Common use cases include:
- Controlling media playback.
- Controlling volume and go to previous or next media.

### 3. **Optional Web Interface**
A lightweight web interface enhances the project with features like:
- **Status Monitoring**: View the system state and active commands.
- **Tag Management**: Write identifiers to NTAGs, including converting Spotify URLs into the required format (`spotify:album:<ID>`).
- **Debugging**: Monitor logs and commands for troubleshooting.

### 4. **Remote Control Support**
The project can capture commands from remote controls using Linux input handling (evdev) and publish them to MQTT. This enables integration of physical remote buttons into the musicbox setup.

---

## **Use Cases**
- **Media Playback**: Use NFC tags to trigger specific albums, playlists, or movies via platforms like Spotify.
- **Home Automation**: Assign tags to control lights, scenes, or custom scripts in Home Assistant.
- **Child-Friendly Control**: Provide an interactive way for kids to trigger their favorite actions using NFC tags.
- **Remote Control Integration**: Repurpose existing remotes to send MQTT commands or trigger automations.

---

## **Home Assistant Integration**
Example configurations are included to help you integrate the project with Home Assistant. These examples demonstrate how to:
- Respond to MQTT commands for media playback, automations, or other actions.
- Use NTAGs as automation triggers (e.g., play a Spotify album, adjust lighting).
- Configure MQTT topics and payloads for seamless communication.

---

## **Getting Started**

### **Hardware Requirements**
- MFRC522 RFID reader.
- NTAG-compatible NFC tags.
- (Optional) A remote control compatible with Linux input handling.

### **Software Requirements**
- Python 3.x.
- MQTT broker (e.g., Mosquitto).
- (Optional) Home Assistant for advanced automations.

### **Setup**
coming soon

---
