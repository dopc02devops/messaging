FROM python:3.9-slim

WORKDIR /app
COPY consumers/Finance/finance_consumer.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["python", "finance_consumer.py"]
