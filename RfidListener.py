from MifareUltralightMFRC522 import MifareUltralightMFRC522
import threading
import RPi.GPIO as GPIO
import time
import logging

class RfidListener:

  def __init__(self, callback, interval=1):
    self.active = True
    self.mfrc = MifareUltralightMFRC522()
    self.interval = interval
    self.callback = callback
    self._stop_event = threading.Event()
    self.thread = threading.Thread(target=self._loop_function, args=(callback, ), daemon=True)
    self.thread.start()
    logging.info(f'{self} initialized')
  
  def __repr__(self):
    return f"RfidListener running every {self.interval} seconds"

  def _loop_function(self, callback):
    while True:
      try:
        if (self.active):
          callback(self.mfrc.read_id())
        time.sleep(self.interval)
      except Exception as e:
        logging.warning(f'Exception: {e}')
      finally:
        GPIO.cleanup()
        logging.debug("GPIO cleaned")

  def start(self):
    self.active = True

  def pause(self):
    self.active = False

  def stop(self):
    self.pause()
    self._stop_event.set()
    if self.thread:
      self.thread.join()
      self.thread = None

  def join(self):
    self.thread.join()
