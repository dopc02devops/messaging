FROM python:3.9-slim

WORKDIR /app
COPY sender/sender.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["python", "sender.py"]