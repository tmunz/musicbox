from mfrc522 import MFRC522
import ndef
import logging
import threading


class MifareUltralightMFRC522:

  RESERVED_BLOCKS = 4
  LIMIT_BYTE = 0xFE
  CHUNK_SIZE = 16  # chunks are required to be 16 bytes long by mfrc522 library

  def __init__(self, log_level='WARNING'):
    self.mfrc = MFRC522(debugLevel=log_level)
    self.mfrc.Write_MFRC522(self.mfrc.TxControlReg, 0x83)
    self.mfrc.Write_MFRC522(self.mfrc.RFCfgReg, 0x70)
    self.lock = threading.Lock() 

  def connect(self):
    with self.lock:  # threadsafe lock
      logging.debug('trying to establish connection')
      self.mfrc.MFRC522_Init()
      (status, _) = self.mfrc.MFRC522_Request(self.mfrc.PICC_REQIDL)
      if status != self.mfrc.MI_OK:
        logging.debug('status not OK for ID request')
        return (None, None, None, None)
      (status, uid) = self.mfrc.MFRC522_Anticoll()
      if status != self.mfrc.MI_OK:
        logging.debug('status not OK for Anticoll')
        return (None, None, None, None)
      block_size = self.mfrc.MFRC522_SelectTag(uid)
      id = self._uid_to_id(uid)
      logging.debug(f'connection established to {str(id)} ({str(uid)})')
      return (id, uid, status, block_size)

  def connect_retry(self):
    id = None
    while not id:
      (id, uid, status, block_size) = self.connect()
    return (id, uid, status, block_size)

  def read(self, retry=False):
    (id, uid, status, block_size) = self.connect_retry() if retry else self.connect()
    if status != self.mfrc.MI_OK:
      return (None, None)
    block_addr = 0
    message_size = 0
    bytes = None
    value = None
    with self.lock: # threadsafe lock
      block_data = self.mfrc.MFRC522_Read(block_addr)
      if (block_data):
        capability_memory_size = block_data[14]
        limit_block = capability_memory_size * 8 / block_size
        block_addr += block_size
        block_data = self.mfrc.MFRC522_Read(block_addr)
        assert block_data[0] == 0x03
        message_size = block_data[1]
        bytes = bytearray(block_data[2:])
        block_addr += block_size
      while block_addr < message_size and block_addr < limit_block:
        block_data = self.mfrc.MFRC522_Read(block_addr)
        if block_data:
          bytes += bytearray(block_data)
          if self.LIMIT_BYTE in block_data:
            break
        else:
          break
        block_addr += block_size
      self.mfrc.MFRC522_StopCrypto1()
      if (bytes):
        try:
          records = ndef.message_decoder(bytes)
          for record in records:
            if (isinstance(record, ndef.UriRecord)):
              value = record.uri
              break 
            elif (isinstance(record, ndef.SmartposterRecord)):
              value = record.uri_records[0].uri
              break 
            elif (isinstance(record, ndef.TextRecord)):
              value = record.text
              break
            else:
              logging.warning(f'Type of record is not supported: {type(record)}')
        except ndef.DecodeError as e:
          logging.info(f'Data is not in NDEF format')
      return (id, value)

  def read_id(self, retry=False):
    (id, uid, status, block_size) = self.connect_retry() if retry else self.connect()
    return id

  def write(self, data, retry=False):
    (id, uid, status, block_size) = self.connect_retry() if retry else self.connect()
    if status != self.mfrc.MI_OK:
      return (None, None)
    message = ndef.UriRecord(data)
    ndef_message = b''.join(ndef.message_encoder([message]))

    message_size = len(ndef_message)
    bytes = [0x03, message_size] + list(ndef_message) + [self.LIMIT_BYTE]
    chunks = self._convert_to_chunks(bytes, block_size)

    with self.lock: # threadsafe lock
      i = 0
      block_data = self.mfrc.MFRC522_Read(0)
      capability_memory_size = block_data[14]
      limit_block = capability_memory_size * 8 / block_size
      if message_size > (limit_block - self.RESERVED_BLOCKS) * block_size:
        raise OverflowError('Data too large to fit')
      while i < len(chunks) and self.RESERVED_BLOCKS + i < limit_block:
        chunk = chunks[i]
        block_addr = self.RESERVED_BLOCKS + i
        self.mfrc.MFRC522_Write(block_addr, chunk)
        i += 1
      self.mfrc.MFRC522_StopCrypto1()
    logging.info(f'Data written successfully to {id}')
    return (id, data)

  def write_block_bytes(self, block_addr, block_value, retry=False):
    (id, uid, status, block_size) = self.connect_retry() if retry else self.connect()
    if len(block_value) > block_size:
      logging.debug(f'block_value size cannot be larger than {block_size}')
      return (None, None)
    if status != self.mfrc.MI_OK:
      return (None, None)
    with self.lock: # threadsafe lock
      block_data = self._convert_to_chunks(block_value, block_size)
      self.mfrc.MFRC522_Read(block_addr)
      self.mfrc.MFRC522_Write(block_addr, block_data)
      self.mfrc.MFRC522_StopCrypto1()
      return (id, block_data)

  def _uid_to_id(self, uid):
    n = 0
    for i in range(0, 5):
      n = n * 0xFF + uid[i]
    return n

  def _convert_to_chunks(self, bytes, block_size):
    chunks = [bytes[i:i+block_size] for i in range(0, len(bytes), block_size)]
    for i in range(len(chunks)):
      chunks[i] = bytearray(chunks[i]) + bytearray(self.CHUNK_SIZE - len(chunks[i]))
    return chunks
