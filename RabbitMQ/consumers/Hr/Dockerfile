FROM python:3.9-slim

WORKDIR /app
COPY consumers/Hr/hr_consumer.py /app/
COPY requirements.txt /app/

RUN pip install -r requirements.txt

CMD ["python", "hr_consumer.py"]
