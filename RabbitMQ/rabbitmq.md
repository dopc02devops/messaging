pip install -r requirements.txt


Send a message:

curl --location 'http://localhost:6000/send' \
--header 'Content-Type: application/json' \
--data '{"message": "Hello from Flask!"}'


Responce:
200 OK
{
    "message": "Hello from Flask!",
    "status": "Message sent successfully"
}