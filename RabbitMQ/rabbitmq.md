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