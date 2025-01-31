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
            # Set up connection parameters
            connection_params = pika.ConnectionParameters(
                host='rabbitmq',  # RabbitMQ service name from docker-compose.yml
                credentials=pika.PlainCredentials('user', 'password')  # RabbitMQ credentials
            )
            # Try to establish the connection
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
        # Here you can process the message as needed
        # Acknowledge the message after processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Message acknowledged.")
    except Exception as e:
        logger.error(f"Error while processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)  # Negative acknowledgment in case of error

# Main function to start consuming messages
def start_consuming():
    connection = None
    channel = None
    try:
        # Connect to RabbitMQ
        connection = connect_rabbitmq()
        channel = connection.channel()

        # Declare a queue (it must exist before consuming messages)
        channel.queue_declare(queue='task_queue', durable=True)
        logger.info("Queue 'task_queue' declared.")

        # Start consuming messages from the queue with a callback
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        logger.info("Waiting for messages...")
        channel.start_consuming()  # Block and wait for messages
    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user. Closing connection...")
    except Exception as e:
        logger.error(f"Error in consuming messages: {e}")
    finally:
        # Gracefully close the connection and channel when done
        if channel and not channel.is_closed:
            channel.close()
            logger.info("RabbitMQ channel closed.")
        if connection and not connection.is_closed:
            connection.close()
            logger.info("RabbitMQ connection closed.")

if __name__ == '__main__':
    start_consuming()
