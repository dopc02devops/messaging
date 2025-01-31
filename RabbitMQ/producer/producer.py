import pika
from flask import Flask, request, jsonify
import time
import logging

# Setup Flask app
app = Flask(__name__)

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create a console handler for logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter and attach it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add console handler to the logger
logger.addHandler(console_handler)

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_USER = "user"
RABBITMQ_PASSWORD = "password"
EXCHANGE_NAME = "direct_logs"  # Direct exchange for routing messages

# Function to connect to RabbitMQ with retry logic
def connect_rabbitmq():
    while True:
        try:
            connection_params = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            )
            connection = pika.BlockingConnection(connection_params)
            logger.info("Connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Function to declare exchange and queues with retry logic
def setup_rabbitmq(channel):
    retries = 5
    while retries > 0:
        try:
            # Declare exchange
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='direct', durable=True)
            logger.info(f"Declared exchange '{EXCHANGE_NAME}'.")

            # Declare queues
            channel.queue_declare(queue="finance_queue", durable=True)
            channel.queue_declare(queue="hr_queue", durable=True)
            logger.info("Declared queues: finance_queue, hr_queue.")

            # Bind queues to the exchange with routing keys
            channel.queue_bind(exchange=EXCHANGE_NAME, queue="finance_queue", routing_key="finance")
            channel.queue_bind(exchange=EXCHANGE_NAME, queue="hr_queue", routing_key="hr")
            logger.info("Queues bound to exchange with routing keys: 'finance', 'hr'.")
            
            return
        except pika.exceptions.AMQPChannelError as e:
            logger.warning(f"Failed to set up RabbitMQ, retrying... {e}")
            retries -= 1
            time.sleep(2)
    logger.error("Failed to set up RabbitMQ after several retries.")
    raise Exception("RabbitMQ setup failed.")

# Route to send a message to RabbitMQ
@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    queue_type = data.get('queue_type', '').lower()  # Expect 'finance' or 'hr'

    if not message or queue_type not in ['finance', 'hr']:
        logger.error("Invalid input: Must provide 'message' and valid 'queue_type' ('finance' or 'hr').")
        return jsonify({'error': "Must provide 'message' and valid 'queue_type' ('finance' or 'hr')."}), 400

    connection = None
    channel = None
    try:
        # Connect to RabbitMQ
        connection = connect_rabbitmq()
        channel = connection.channel()

        # Ensure exchange and queues are declared
        setup_rabbitmq(channel)

        # Send the message with the appropriate routing key
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=queue_type,  # 'finance' or 'hr'
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
        )

        logger.info(f"Message sent to '{queue_type}' queue: {message}")
        return jsonify({'status': 'Message sent successfully', 'queue': queue_type, 'message': message})

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return jsonify({'error': 'Failed to send message to RabbitMQ'}), 500

    finally:
        # Ensure that the connection is closed after sending
        if channel and not channel.is_closed:
            channel.close()
            logger.info("RabbitMQ channel closed.")
        if connection and not connection.is_closed:
            connection.close()
            logger.info("RabbitMQ connection closed.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
