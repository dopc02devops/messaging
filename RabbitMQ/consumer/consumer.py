import pika
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger()

# Function to connect to RabbitMQ with retry logic
def connect_rabbitmq():
    while True:
        try:
            connection_params = pika.ConnectionParameters(
                host='rabbitmq',  # RabbitMQ service name from docker-compose.yml
                credentials=pika.PlainCredentials('user', 'password')  # RabbitMQ credentials
            )
            connection = pika.BlockingConnection(connection_params)
            logger.info("Connected to RabbitMQ successfully.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Callback function to process messages from RabbitMQ
def callback(ch, method, properties, body):
    try:
        logger.info(f"Received message: {body.decode()}")
        # Process the message here
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Message acknowledged.")
    except Exception as e:
        logger.error(f"Error while processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)  # Negative acknowledgment in case of error

# Main function to start consuming messages
def start_consuming():
    # Connect to RabbitMQ
    connection = connect_rabbitmq()
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue='task_queue', durable=True)
    logger.info("Queue 'task_queue' declared.")

    # Start consuming messages
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    try:
        logger.info("Waiting for messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user. Closing connection...")
    finally:
        if connection.is_open:
            connection.close()
            logger.info("RabbitMQ connection closed.")

if __name__ == '__main__':
    start_consuming()
