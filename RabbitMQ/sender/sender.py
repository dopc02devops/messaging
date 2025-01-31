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

# Function to connect to RabbitMQ with retry logic
def connect_rabbitmq():
    while True:
        try:
            # Set connection parameters
            connection_params = pika.ConnectionParameters(
                host='rabbitmq',  # RabbitMQ service name from docker-compose.yml
                credentials=pika.PlainCredentials('user', 'password')  # RabbitMQ credentials
            )
            # Try to establish the connection
            connection = pika.BlockingConnection(connection_params)
            logger.info("Connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

# Function to declare the exchange with retry logic
def declare_exchange_with_retry(channel, exchange_name):
    retries = 5
    while retries > 0:
        try:
            channel.exchange_declare(exchange=exchange_name, exchange_type='direct', passive=False)
            logger.info(f"Successfully declared exchange '{exchange_name}'")
            return
        except pika.exceptions.AMQPChannelError as e:
            logger.warning(f"Failed to declare exchange '{exchange_name}', retrying... {e}")
            retries -= 1
            time.sleep(2)  # wait before retrying
    logger.error(f"Failed to declare exchange '{exchange_name}' after several retries.")
    raise Exception(f"Exchange '{exchange_name}' declaration failed.")

# Route to send a message to RabbitMQ
@app.route('/send', methods=['POST'])
def send_message():
    message = request.json.get('message', '')
    if not message:
        logger.error('No message provided')
        return jsonify({'error': 'No message provided'}), 400

    connection = None
    channel = None
    try:
        # Connect to RabbitMQ
        connection = connect_rabbitmq()
        channel = connection.channel()

        # Declare the exchange with retry logic
        declare_exchange_with_retry(channel, 'direct_logs')

        # Declare the queue
        channel.queue_declare(queue='task_queue', durable=True)
        logger.info(f"Declared queue 'task_queue'.")

        # Bind the queue to the exchange with a routing key
        routing_key = 'task_key'  # You can change this as per your requirement
        channel.queue_bind(exchange='direct_logs', queue='task_queue', routing_key=routing_key)
        logger.info(f"Queue 'task_queue' bound to exchange 'direct_logs' with routing key '{routing_key}'.")

        # Send the message to the exchange with the routing key
        channel.basic_publish(
            exchange='direct_logs',  # Specify the exchange here
            routing_key=routing_key,  # Routing key to match the binding
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make the message persistent
            )
        )
        logger.info(f"Message sent to 'task_queue' through exchange 'direct_logs': {message}")
        return jsonify({'status': 'Message sent successfully', 'message': message})

    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return jsonify({'error': 'Failed to send message to RabbitMQ'}), 500

    finally:
        # Ensure that the connection is closed after sending
        if connection and not connection.is_closed:
            connection.close()
            logger.info("RabbitMQ connection closed.")
        if channel and not channel.is_closed:
            channel.close()
            logger.info("RabbitMQ channel closed.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
