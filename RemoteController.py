import evdev
import time
import logging
import threading
from evdev import InputDevice, categorize, ecodes
from MqttPublisher import MqttPublisher

TOPIC = 'musicbox/controls'

class RemoteController:
  def __init__(self, publisher: MqttPublisher, target_device_name="Satechi Media Button Keyboard"):
    self.publisher = publisher
    self.target_device_name = target_device_name
    self.device = None
    self.thread = threading.Thread(target=self._monitor_device, args=(), daemon=True)
    self.thread.start()
    self.last_event_time = 0
    self.delay_time = 0.3
    logging.info(f'{self} initialized')

  def __repr__(self):
    return f"RemoteController for {self.target_device_name}"

  def list_devices(self):
    return [InputDevice(path) for path in evdev.list_devices()]

  def find_target_device(self):
    for device in self.list_devices():
      if device.name == self.target_device_name:
        return device
    return None

  def _monitor_device(self):
    logging.info(f"Input device Monitoring started for: {self.target_device_name}")
    while True:
      if not self.device:
        self.device = self.find_target_device()
        if not self.device:
          logging.info(f"{self.target_device_name} currently not available. Retrying...")
          time.sleep(2)
          continue
        logging.info(f"Monitoring input device: {self.device.name} ({self.device.path})")
        try:
          self.device.grab()  # Grab the device to block system input
        except OSError as e:
          logging.warning(f"Failed to grab device: {e}")
          self.device = None
          continue

      try:
        for event in self.device.read_loop():
          if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            logging.debug(f"Key event: {key_event.keycode}, State: {key_event.keystate}")
            self.handle_keyevent(key_event.keycode, key_event.keystate)
      except:
        logging.info(f"Device {self.device.name} disconnected. Reconnecting...")
        self.device = None

  def handle_keyevent(self, keycode, keystate):  
    current_time = time.time()

    actions = {
      "KEY_VOLUMEDOWN": "volume_down",
      "KEY_VOLUMEUP": "volume_up",
      "KEY_PLAYPAUSE": "playpause",
      "KEY_PREVIOUSSONG": "prev",
      "KEY_NEXTSONG": "next"
    }
    
    if keycode in actions:
      action = actions[keycode]
      if keystate == 1:
        self.last_event_time = current_time
        self.publisher.publish(TOPIC, action)
      elif keystate == 2:
        if (current_time - self.last_event_time < self.delay_time):
          return
        self.last_event_time = current_time
        self.publisher.publish(TOPIC, action)
