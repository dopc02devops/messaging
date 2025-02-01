pip install -r requirements.txt
echo "[rabbitmq_management, rabbitmq_mqtt, rabbitmq_web_dispatch, rabbitmq_management_agent].
" > enabled_plugins
sudo chmod 777 enabled_plugins

Send a message:

curl --location 'http://localhost:6000/send' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Sample Message finance 000000073",
    "queue_type": "finance"  
}
'


docker-compose up --build -d


RabbitMQ is an open-source message broker that helps applications communicate with each other asynchronously using messages. It implements the AMQP (Advanced Message Queuing Protocol) and is widely used for decoupling microservices, distributing workloads, and handling real-time data processing.

🔹 Key Concepts of RabbitMQ
Producer 📨 → Sends messages to RabbitMQ.
Queue 📥 → Stores messages until they are processed.
Consumer 📤 → Receives and processes messages.
Exchange 🔀 → Routes messages to the correct queue(s).
Bindings 🔗 → Define the relationship between an exchange and a queue.
🔹 Why Use RabbitMQ?
✅ Scalability – Can handle high loads with clustering.
✅ Reliability – Supports message persistence and acknowledgments.
✅ Decoupling – Services don’t need to know about each other.
✅ Multiple Protocols – Supports AMQP, MQTT, and STOMP.

🔹 Example Use Cases
Microservices Communication 🏗️
Task Queues (e.g., Background Jobs, Email Processing) ✉️
Real-time Data Processing (e.g., Logs, Metrics) 📊
IoT Applications 📡


node-exporter collects system metrics (CPU, memory, disk, etc.).
prometheus scrapes metrics from node-exporter and stores them for analysis.
Exposing ports allows you to access Prometheus UI at http://localhost:9090.