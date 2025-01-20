import logging
import argparse
from Api import Api
from PlaybackController import PlaybackController
from MqttPublisher import MqttPublisher
from RemoteController import RemoteController

class Musicbox: 
  def __init__(self, http_port, mqtt_host, mqtt_port, device_id, nfc_interval=0.3, nfc_resilience_threshold=3): 

    if (mqtt_host and mqtt_port):
      self.mqtt_publisher = MqttPublisher(mqtt_host, mqtt_port, device_id)

    self.remote_controller = RemoteController(self.mqtt_publisher)
    self.playback_controller = PlaybackController(self.mqtt_publisher, interval=nfc_interval, resilience_threshold=nfc_resilience_threshold)

    if (http_port):
      self.api = Api(port=http_port, controller=self.playback_controller);

    self.playback_controller.start_process_queue()


def setup_logging(log_level='INFO'):
  logging.basicConfig(
    level=logging.getLevelName(log_level),
    format='%(asctime)s - %(name)s - [%(threadName)s] - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
  )
  logging.info("Global logging initialized.")

def main():
  parser = argparse.ArgumentParser(description='Musicbox command-line interface')
  parser.add_argument('--http_port', type=int, help='enables the webserver-api at the given port e.g. tag writing via api)')
  parser.add_argument('--mqtt_host', type=str, help='sets the mqtt host. See also --mqtt_port')
  parser.add_argument('--mqtt_port', type=int, help='sets the mqtt port. See also --mqtt_host')
  parser.add_argument('--device_id', type=str, help='device id of the Musicbox (e.g. for Home Assistant)')
  parser.add_argument('--nfc_interval', type=float, help='sets the nfc polling interval, defaults to 0.3 seconds')
  parser.add_argument('--nfc_resilience_threshold', type=int, help='sets the nfc resilience threshold after change in polling result triggers pause, defaults to 3. The lower the more responsive, the higher the more stable is the playback')
  parser.add_argument('--log_level', type=str, help='log_level for the MusicBox')
  args = parser.parse_args()

  setup_logging(args.log_level)
  Musicbox(http_port=args.http_port, mqtt_host=args.mqtt_host, mqtt_port=args.mqtt_port, device_id=args.device_id, nfc_interval=args.nfc_interval, nfc_resilience_threshold=args.nfc_resilience_threshold)

if __name__ == '__main__':
  main()