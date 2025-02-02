from kafka import KafkaProducer
from prometheus_client import start_http_server, Counter, Summary, Gauge
import json
import time
import psutil
import logging
import random
from faker import Faker

# Enable logging
logging.basicConfig(level=logging.INFO)

# Prometheus metrics
messages_produced = Counter('kafka_producer_messages_total', 'Total number of messages produced')
message_production_duration = Summary('kafka_producer_duration_seconds', 'Time taken to produce a message')

# Prometheus metrics for CPU and memory usage
cpu_usage = Gauge('producer_cpu_usage', 'CPU usage of the producer service (%)')
memory_usage = Gauge('producer_memory_usage', 'Memory usage of the producer service (bytes)')

# Kafka configuration
KAFKA_SERVER = 'kafka:29092'  # Correct Kafka broker address
TOPIC_NAME = 'test-topic'

# Create a Kafka Producer with retry and connection handling
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    retries=5,  # Retries if Kafka is unavailable
    acks='all',  # Ensure message is acknowledged by all replicas
    max_in_flight_requests_per_connection=5  # Prevent too many unacknowledged messages
)

# Initialize Faker instance for generating random names
fake = Faker()

# Function to get CPU usage percentage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get memory usage in bytes
def get_memory_usage():
    return psutil.virtual_memory().used

# Generate random customer data
def generate_customer_transaction():
    transaction_types = ["Deposit", "Withdrawal", "Transfer"]
    amounts = [round(random.uniform(100, 5000), 2) for _ in range(5)]
    
    # Dynamically generate a customer name using Faker
    customer_name = fake.name()
    transaction_type = random.choice(transaction_types)
    transaction_amount = random.choice(amounts)
    
    # Create the transaction object
    transaction = {
        "customer_name": customer_name,
        "transaction_type": transaction_type,
        "amount": transaction_amount,
        "transaction_id": f"txn_{random.randint(1000, 9999)}",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # Human-readable timestamp
    }
    
    return transaction

# Start Prometheus HTTP server
start_http_server(8000)

# Produce messages
try:
    while True:
        start_time = time.time()
        
        # Create bank transaction message
        message = generate_customer_transaction()
        
        try:
            # Send the message to Kafka and wait for confirmation
            producer.send(TOPIC_NAME, value=message).get(timeout=10)  # Wait for confirmation or timeout after 10 seconds
            
            # Print message only after it's successfully sent
            print(f"✅ Producer - Sent: {json.dumps(message, indent=2)}")
        except Exception as e:
            logging.error(f"❌ Failed to send message: {e}")
            continue  # Skip to the next iteration if the message fails to send
        
        # Measure production duration
        message_production_duration.observe(time.time() - start_time)
        
        # Increment the message produced counter
        messages_produced.inc()
        
        # Update CPU and memory metrics
        cpu_usage.set(get_cpu_usage())
        memory_usage.set(get_memory_usage())
        
        time.sleep(1)  # Adjust sleep time to control message production rate
except Exception as e:
    logging.error(f"❌ Error while producing messages: {e}")
finally:
    logging.info("❗ Flushing and closing the Kafka producer...")
    producer.flush()  # Ensure all messages are sent before closing
    producer.close()
