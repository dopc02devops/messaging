from kafka import KafkaConsumer
from prometheus_client import start_http_server, Counter, Summary, Gauge
import json
import time
import logging
import psutil  # Using psutil for CPU and memory usage

# Enable logging
logging.basicConfig(level=logging.info)

# Prometheus metrics
messages_consumed = Counter('kafka_consumer_messages_total', 'Total number of messages consumed')
message_processing_duration = Summary('kafka_consumer_duration_seconds', 'Time taken to process a message')

# New Prometheus metrics for CPU and memory usage
cpu_usage = Gauge('consumer_cpu_usage', 'CPU usage of the consumer service (%)')
memory_usage = Gauge('consumer_memory_usage', 'Memory usage of the consumer service (bytes)')

# Kafka configuration
KAFKA_SERVER = 'kafka:29092'  # For Docker container communication, use kafka:29092
TOPIC_NAME = 'test-topic'

# Create a Kafka Consumer for payroll
consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),  # Deserialize JSON
    auto_offset_reset='earliest',  # Start reading from the earliest message
    group_id='payroll-group',  # Unique group ID for payroll
    enable_auto_commit=False,  # Disable auto commit to manually commit offsets
    consumer_timeout_ms=1000,  # Timeout after 1 second of no messages
    session_timeout_ms=30000,  # Consumer session timeout
    heartbeat_interval_ms=5000,  # Heartbeat interval
    max_poll_interval_ms=600000,  # Max time between poll calls (10 minutes)
)

# Function to get CPU usage percentage using psutil
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get memory usage in bytes using psutil
def get_memory_usage():
    return psutil.virtual_memory().used

# Start the Prometheus HTTP server to expose metrics
start_http_server(8001)  # Exposing metrics on port 8001

# Consume messages
try:
    for message in consumer:
        start_time = time.time()  # Start timer for message processing time
        
        # Log the entire message (message.value is already a dictionary)
        logging.info(f"✅ Consumed message: {message.value}")  
        
        # Process the message (check for required fields, 'amount' and 'customer_name')
        try:
            if 'amount' in message.value and 'customer_name' in message.value:
                # Ensure 'amount' is a number (float or int)
                transaction_amount = message.value['amount']
                if isinstance(transaction_amount, (int, float)):
                    customer_name = message.value['customer_name']
                    logging.info(f"Processing transaction for customer: {customer_name} with amount: {transaction_amount}")
                else:
                    logging.warning(f"❌ Invalid 'amount' type in message: {message.value}. Expected int or float, got {type(transaction_amount)}.")
                    continue  # Skip processing if 'amount' is not a valid number
            else:
                if 'amount' not in message.value:
                    logging.warning(f"❌ Missing 'amount' in message: {message.value}")
                if 'customer_name' not in message.value:
                    logging.warning(f"❌ Missing 'customer_name' in message: {message.value}")
                continue  # Skip processing if either required field is missing
            
        except KeyError as e:
            logging.warning(f"❌ Key error while processing message: {e}")
            continue
        
        # Measure the duration it took to process the message
        message_processing_duration.observe(time.time() - start_time)
        
        # Increment the message consumed counter
        messages_consumed.inc()
        
        # Manually commit the offset after processing the message
        consumer.commit()
        
        # Update CPU and memory usage metrics
        cpu_usage.set(get_cpu_usage())  # Get CPU usage percentage
        memory_usage.set(get_memory_usage())  # Get memory usage in bytes
        
except Exception as e:
    logging.error(f"❌ Error while consuming messages: {e}")
finally:
    consumer.close()
    logging.info("Kafka consumer closed.")
