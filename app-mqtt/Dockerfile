FROM python:3.11-slim

WORKDIR /

COPY requirements.txt requirements.txt
COPY . ./
RUN pip3 install -r requirements.txt
CMD ["python", "./app-mqtt.py"]