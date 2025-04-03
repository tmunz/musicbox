import queue
import threading
import logging
import json
from RfidListener import RfidListener
from MifareUltralightMFRC522 import MifareUltralightMFRC522
from MqttPublisher import MqttPublisher

TOPIC = 'musicbox/playback'

class PlaybackController:
  def __init__(self, publisher: MqttPublisher, interval: float, resilience_threshold: int, is_content_mandatory: bool = False):
    self.lock = threading.Lock() 
    self.mfrc = MifareUltralightMFRC522()
    self.interval = interval
    self.resilience_threshold = resilience_threshold
    self.is_content_mandatory = is_content_mandatory
    self.resilience_counter = 0
    self.tag_id = None
    self.last_id = None
    self.current_id = None
    self.content = None
    self.rfid_signal_event = threading.Event()
    self.rfid_input_queue = queue.Queue()
    self.rfid_listener = RfidListener(self._enqueue_rfid_event, self.interval)
    self.publisher = publisher
    self.publisher.register_device()

  def _get_tag_data(self, action: str):
    message =  {'id': self.current_id, 'content': self.content, 'action': action}
    return json.dumps(message, indent=4)

  def _enqueue_rfid_event(self, input):
    self.rfid_input_queue.put(input)
    self.rfid_signal_event.set()

  def write_data(self, data):
    with self.lock:  # threadsafe lock
      result = (None, None)
      try:
        self.rfid_listener.pause();
        result = self.mfrc.write(data)
        self.last_id = None
        self.current_id = None
      except Exception as e:
        logging.warning(e)
      finally:
        self.rfid_listener.start()
        return result

  def start_process_queue(self):
    while True:
      try:
        self.rfid_signal_event.wait()
        while not self.rfid_input_queue.empty():
          self.tag_id = self.rfid_input_queue.get()
          if (self.tag_id is None):
            if (self.current_id is not None):
              self.pause_with_resilience()
          else:
            self.resilience_counter = 0
            if(self.current_id != self.tag_id):
              self.play(self.tag_id)
        self.rfid_signal_event.clear()
      except Exception as e:
        logging.warning(e)

  def pause_with_resilience(self):
    if (self.resilience_counter < self.resilience_threshold):
      self.resilience_counter += 1
    else:
      self.resilience_counter = 0
      self.publisher.publish(TOPIC, self._get_tag_data('pause_playback'))
      self.current_id = None
  
  def play(self, id):
    (_, content) = self.mfrc.read()
    if (content is None):
      if (self.is_content_mandatory):
        return
      content = '' # content has been read but is empty or not in the expected format
    self.content = content
    self.current_id = id
    if (self.current_id == self.last_id):
      self.publisher.publish(TOPIC, self._get_tag_data('resume_playback'))
    else:
      self.last_id = self.current_id
      self.publisher.register_tag(self.current_id)
      self.publisher.publish(TOPIC, self._get_tag_data('start_playback'))
