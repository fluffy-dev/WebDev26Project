#!/usr/bin/env bash
# script to initialize kafka topics

echo 'Creating Kafka topics...'

kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1 --topic user.registered
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1 --topic submit.rewarded
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1 --topic debezium_configs --config cleanup.policy=compact
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1 --topic debezium_offsets --config cleanup.policy=compact
kafka-topics --create --if-not-exists --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1 --topic debezium_status --config cleanup.policy=compact

echo 'Topics created successfully!'
