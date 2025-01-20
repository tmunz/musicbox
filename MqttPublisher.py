import paho.mqtt.client as mqtt
import json
import logging

class MqttPublisher:

  def __init__(self, host: str = 'localhost', port: int = 1883, device_id="B8A0F"):
    self.host = host
    self.port = port
    self.device_id = device_id
    self.client = mqtt.Client()

  def connect(self):
    try:
      self.client.connect(self.host, self.port)
      self.client.loop_start()
      logging.debug("MQTT client connected")
    except Exception as e:
      logging.error(f"Failed to connect to MQTT broker: {e}")

  def disconnect(self):
    self.client.loop_stop()
    self.client.disconnect()

  def register_device(self):
    """
    Register the device with Home Assistant via MQTT.
    """
    mqtt_topic = f'homeassistant/tag/{self.device_id}/config'
    message = {
      "topic": f"{self.device_id}/tag_scanned",
      "value_template": "{{ value_json.RC522.UID }}",
      "device": {
        "identifiers": [self.device_id],
        "name": "NFC-Reader",
        "manufacturer": "TMunz",
        "model": "SK61 NFC",
        "sw_version": "1.0.0"
      }
    }

    try:
      self.connect()
      result = self.client.publish(mqtt_topic, json.dumps(message))
      result.wait_for_publish()
      logging.info(f"Device registered with topic '{mqtt_topic}': {message}")
    except Exception as e:
      logging.error(f"Failed to register device: {e}")
    finally:
      self.disconnect()

  def register_tag(self, id: str):
    mqtt_topic = f"{self.device_id}/tag_scanned"
    message = json.dumps({"RC522": {"UID": id}}, indent=4)

    try:
      self.connect()
      result = self.client.publish(mqtt_topic, message)
      result.wait_for_publish()
      logging.info(f"Tag registered with topic '{mqtt_topic}': {message}")
    except Exception as e:
      logging.error(f"Failed to register tag: {e}")
    finally:
      self.disconnect()

  def publish(self, topic: str, message: str = ''):
    try:
      self.connect()
      result = self.client.publish(topic, message)
      result.wait_for_publish()
      logging.info(f"Published message to topic '{topic}': {message}")
    except Exception as e:
      logging.error(f"Failed to publish message: {e}")
    finally:
      self.disconnect()

  def __repr__(self):
    return f'{self.__class__.__name__} for {self.host}:{self.port}'
