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

def finance_callback(ch, method, properties, body):
    try:
        logger.info(f"[FINANCE] Received message: {body.decode()}")
        # Simulate finance processing
        time.sleep(2)  
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("[FINANCE] Message acknowledged.")
    except Exception as e:
        logger.error(f"[FINANCE] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_finance_consumer():
    connection = None
    channel = None
    try:
        connection = connect_rabbitmq()
        channel = connection.channel()

        channel.queue_declare(queue='finance_queue', durable=True)
        logger.info("Queue 'finance_queue' declared.")

        channel.basic_consume(queue='finance_queue', on_message_callback=finance_callback)

        logger.info("[FINANCE] Waiting for messages...")
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("[FINANCE] Consumer interrupted by user. Closing connection...")
    except Exception as e:
        logger.error(f"[FINANCE] Error in consuming messages: {e}")
    finally:
        if channel and not channel.is_closed:
            channel.close()
            logger.info("[FINANCE] RabbitMQ channel closed.")
        if connection and not connection.is_closed:
            connection.close()
            logger.info("[FINANCE] RabbitMQ connection closed.")

if __name__ == '__main__':
    start_finance_consumer()
