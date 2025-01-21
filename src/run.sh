#!/bin/bash
source ./env-musicbox/bin/activate
python Musicbox.py \
  --http_port 8061 \
  --mqtt_host "localhost" \
  --mqtt_port 1883 \
  --device_id "B8A0F" \
  --nfc_interval 0.3 \
  --nfc_resilience_threshold 3 \
  --log_level "INFO"
