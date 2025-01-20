# musicbox
This project is an open-source solution for media playback with **NTAGs**, **MQTT commands**, and providing an optional **web interface**. Designed to integrate seamlessly with platforms like **Home Assistant**, it offers a fun and flexible way to control smart devices or trigger automations using NFC tags and remote controls. 
You are welcome to incorporate parts of this project into your own and customize the code to suit your requirements.

---

## **Features**

### 1. **NTAG Reading and Writing with MFRC522**
This project utilizes the **MFRC522** RFID reader to read and write NTAGs in the NFC Data Exchange Format (NDEF).

### 2. **MQTT Integration**
The project can communicate with MQTT-compatible (e.g. Home Assistant) applications by publishing commands to a configurable MQTT topic. Common use cases include:
- Controlling media playback.
- Controlling volume and go to previous or next media.

### 3. **Optional Web Interface**
A lightweight web interface enhances the project with features like:
- **Status Monitoring**: View the system state and active commands.
- **Tag Management**: Write identifiers to NTAGs, including converting Spotify URLs into the proposed format (`spotify:album:<ID>`).
- **Debugging**: Monitor logs and commands for troubleshooting.

### 4. **Remote Control Support**
The project can capture commands from remote controls using Linux input handling (evdev) and publish them to MQTT. This enables integration of physical remote buttons into the musicbox setup.

---

## **Use Cases**
- **Media Playback**: Use NFC tags to trigger specific albums, playlists, or other media via platforms like Spotify.
- **Home Automation**: Assign tags to control lights, scenes, or custom scripts in Home Assistant.
- **Child-Friendly Control**: Provide an interactive way for kids to trigger their favorite actions using NFC tags.
- **Remote Control Integration**: Repurpose existing remotes to send MQTT commands or trigger automations.

---

## **Home Assistant Integration**
Example configurations are included to help you integrate the project with Home Assistant. These examples demonstrate how to:
- Respond to MQTT commands for media playback, automations, or other actions.
- Use NTAGs as automation triggers (e.g., play a Spotify album, adjust lighting).
- Configure MQTT topics and payloads for seamless communication.
- The example workflow shows that the setup can be used with the data written on tags as well as managed in Home Assistant Tag page by setting the name to the ID (proposed format is `<DOMAIN>:<TYPE>:<ID>`, examples would be `spotify:album:7MSnJiBuHQMTckW9K3L6bu` or `mpd:playlist:depeche_mode_rarities`). 

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

This guide provides examples for step-by-step instructions for setting up MusicBox, including its dependencies, environment, systemd service, and integration with Spotify (Raspotify) and Music Player Daemon (MPD). Adjust the steps according to your needs.

---

#### **1. Installation and Environment Setup**

Navigate to the MusicBox directory, create a Python virtual environment, and install the required dependencies:

```bash
cd /usr/local/bin/musicbox/
# Now, copy or clone the source code into the designated folder and modify the run.sh script to match your environment and needs.
python3 -m venv env-musicbox
sudo chown -R $USER:$USER ./env-musicbox  # Run this if you encounter permission issues
source env-musicbox/bin/activate
pip install -r requirements.txt
```

---

#### **2. Setting Up the Systemd Service**

You can use Systemd to start the service automatically at each startup. Create a new service file and user with the following commands:

**User**
```bash
sudo useradd -m -s /bin/bash musicbox
sudo passwd musicbox
sudo usermod -aG gpio musicbox # GPIO access to RFID Reader, assuming using a MFRC522 over GPIO
sudo usermod -aG spi musicbox # SPI access to RFID Reader
sudo usermod -aG input musicbox # needed when using a remote controller
sudo chown musicbox:musicbox /usr/local/bin/musicbox/run.sh
```

**Service**
```bash
cat <<EOF | sudo tee /etc/systemd/system/musicbox.service
[Unit]
Description=MusicBox
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/musicbox/run.sh
WorkingDirectory=/usr/local/bin/musicbox
StandardOutput=journal
StandardError=journal
Restart=always
User=musicbox

[Install]
WantedBy=multi-user.target
EOF
```

**Reload and check Service**

Reload systemd to recognize the new service, enable it to start at boot, and start it immediately:
```bash
sudo systemctl daemon-reload
sudo systemctl enable musicbox.service
sudo systemctl start musicbox.service
```

Check the status of the service or view recent logs for debugging:
```bash
sudo systemctl status musicbox.service
sudo journalctl -u musicbox.service --since "10 minutes ago"
```

### The following steps are optional if you want to use your musicbox also as speaker

#### **3. Spotify Integration (Raspotify)**

Install and configure Raspotify to enable Spotify playback, for further details see [Raspotify Github Repository](https://github.com/dtcooper/raspotify):

```bash
curl -sL https://dtcooper.github.io/raspotify/install.sh | sh
sudo nano /etc/raspotify/conf
```

In the configuration file, add or modify the following line if you want to use the RaspberryPi audio output (default is hdmi):

```
LIBRESPOT_DEVICE=hw:CARD=Headphones,DEV=0
```

Enable Raspotify to start at boot:

```bash
sudo systemctl enable raspotify
```

---

#### **4. Music Player Daemon (MPD) Setup**

Install MPD and ALSA utilities, then configure MPD for audio playback:

```bash
sudo apt update
sudo apt install alsa-utils mpd mpc
sudo nano /etc/mpd.conf
```

Modify the `audio_output` section in the configuration file if you want to use the RaspberryPi audio output (default is hdmi):

```ini
audio_output {
    type            "alsa"
    name            "Raspberry Pi Headphones"
    device          "hw:2,0"   # Use the device from the `aplay -l` output
    mixer_type      "software"
}
```

Enable MPD to start at boot:

```bash
sudo systemctl enable mpd
```

---

With these steps, you will have MusicBox system ready to use with Home Assistant. You need to configure Spotify, and/or MPD as well as the automations (examples for different steps can be found in the [HA-Folder](./ha)). For troubleshooting or additional configuration options, refer to the documentation for each component.


---
