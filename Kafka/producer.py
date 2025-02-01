from kafka import KafkaConsumer
from prometheus_client import start_http_server, Counter, Summary, Gauge
import json
import time
import psutil

# Kafka configuration
KAFKA_SERVER = 'kafka:29092'  # For Docker container communication, use kafka:29092
TOPIC_NAME = 'test-topic'

# Prometheus metrics
messages_consumed = Counter('kafka_consumer_messages_total', 'Total number of messages consumed')
message_processing_duration = Summary('kafka_consumer_duration_seconds', 'Time taken to process a message')

# New Prometheus metrics for CPU and memory
cpu_usage = Gauge('consumer_cpu_usage', 'CPU usage of the consumer service (%)')
memory_usage = Gauge('consumer_memory_usage', 'Memory usage of the consumer service (bytes)')

# Create a Kafka Consumer for payroll
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',  # Start reading from the earliest message
    group_id='payroll-group',  # Unique group ID for payroll
    enable_auto_commit=False,  # Disable auto commit to manually commit offsets
    consumer_timeout_ms=1000,  # Timeout after 1 second of no messages
    session_timeout_ms=30000,  # Consumer session timeout
    heartbeat_interval_ms=5000,  # Heartbeat interval
    max_poll_interval_ms=600000,  # Max time between poll calls (10 minutes)
)

# Start the Prometheus HTTP server to expose metrics
start_http_server(8001)  # Exposing metrics on port 8001

# Consume messages
try:
    while True:
        start_time = time.time()  # Start timer for message processing time
        
        # Consume message
        message = next(consumer)  # Blocking call, gets the next message
        
        print(f"Payroll Consumer - Consumed: {message.value}")
        
        # Measure the duration it took to process the message
        message_processing_duration.observe(time.time() - start_time)
        
        # Increment the message consumed counter
        messages_consumed.inc()
        
        # Manually commit the offset after processing the message
        consumer.commit()
        
        # Update CPU and memory usage metrics
        cpu_usage.set(psutil.cpu_percent())  # Get CPU usage percentage
        memory_usage.set(psutil.virtual_memory().used)  # Get memory usage in bytes
except Exception as e:
    print(f"Error while consuming messages: {e}")
finally:
    consumer.close()
