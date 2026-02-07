#!/bin/bash

kafka-topics.sh \
  --create \
  --topic speed-events \
  --bootstrap-server kafka:9092 \
  --partitions 3 \
  --replication-factor 1
