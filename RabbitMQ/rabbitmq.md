pip install -r requirements.txt


Send a message:

curl --location 'http://localhost:6000/send' \
--header 'Content-Type: application/json' \
--data '{
    "message": "Sample Message finance 000000073",
    "queue_type": "finance"  
}
'