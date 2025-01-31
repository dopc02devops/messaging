import pika
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger()

def connect_rabbitmq():
    while True:
        try:
            connection_params = pika.ConnectionParameters(
                host='rabbitmq',  
                credentials=pika.PlainCredentials('user', 'password')  
            )
            connection = pika.BlockingConnection(connection_params)
            logger.info("Connected to RabbitMQ successfully.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def hr_callback(ch, method, properties, body):
    try:
        logger.info(f"[HR] Received message: {body.decode()}")
        # Simulate HR processing
        time.sleep(2)  
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("[HR] Message acknowledged.")
    except Exception as e:
        logger.error(f"[HR] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_hr_consumer():
    connection = None
    channel = None
    try:
        connection = connect_rabbitmq()
        channel = connection.channel()

        channel.queue_declare(queue='hr_queue', durable=True)
        logger.info("Queue 'hr_queue' declared.")

        channel.basic_consume(queue='hr_queue', on_message_callback=hr_callback)

        logger.info("[HR] Waiting for messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("[HR] Consumer interrupted by user. Closing connection...")
    except Exception as e:
        logger.error(f"[HR] Error in consuming messages: {e}")
    finally:
        if channel and not channel.is_closed:
            channel.close()
            logger.info("[HR] RabbitMQ channel closed.")
        if connection and not connection.is_closed:
            connection.close()
            logger.info("[HR] RabbitMQ connection closed.")

if __name__ == '__main__':
    start_hr_consumer()
