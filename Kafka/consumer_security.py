from kafka import KafkaConsumer
import json

# Kafka configuration
KAFKA_SERVER = 'kafka:29092'  # For Docker container communication, use kafka:29092
TOPIC_NAME = 'test-topic'

# Create a Kafka Consumer for security
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',  # Start reading from the earliest message
    group_id='security-group',  # Unique group ID for security
    enable_auto_commit=False,  # Disable auto commit to manually commit offsets
    consumer_timeout_ms=1000,  # Timeout after 1 second of no messages
    session_timeout_ms=30000,  # Consumer session timeout
    heartbeat_interval_ms=5000,  # Heartbeat interval
    max_poll_interval_ms=600000,  # Max time between poll calls (10 minutes)
)

# Consume messages
try:
    for message in consumer:
        print(f"security Consumer - Consumed: {message.value}")
        # Manually commit the offset after processing the message
        consumer.commit()
except Exception as e:
    print(f"Error while consuming messages: {e}")
finally:
    consumer.close()
