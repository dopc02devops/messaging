from kafka import KafkaProducer
import time
import json

# Kafka configuration
KAFKA_SERVER = 'kafka:29092'
TOPIC_NAME = 'test-topic'

# Create a Kafka Producer with retry settings
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_SERVER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',  # Wait for acknowledgment from all replicas
        retries=5,  # Retry up to 5 times in case of failure
        max_in_flight_requests_per_connection=5  # Control how many requests Kafka can handle at once
    )
    print(f"Producer connected to {KAFKA_SERVER}")
except Exception as e:
    print(f"Error while connecting to Kafka: {e}")
    exit(1)

# Produce messages
try:
    for i in range(5):
        message = {"message": f"Message {i}"}
        # Sending message asynchronously with a callback for confirmation
        future = producer.send(TOPIC_NAME, value=message)
        # Block until the message is sent and get the result
        result = future.get(timeout=60)  # Adjust the timeout as needed
        print(f"Produced: {message}")
        time.sleep(1)

    # Wait for all messages to be sent
    producer.flush()
    print("All messages produced successfully.")

except Exception as e:
    print(f"Error while producing messages: {e}")
finally:
    # Ensure the producer is properly closed
    producer.close()
