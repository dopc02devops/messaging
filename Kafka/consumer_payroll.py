from kafka import KafkaConsumer
import json

# Kafka configuration
KAFKA_SERVER = 'kafka:9093'
TOPIC_NAME = 'test-topic'

# Create a Kafka Consumer for payroll
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='payroll-group'  # Unique group ID for payroll
)

# Consume messages
for message in consumer:
    print(f"Payroll Consumer - Consumed: {message.value}")
