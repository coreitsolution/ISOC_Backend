FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY app .
RUN pip3 install -r requirements.txt
CMD ["python", "./app.py"]

EXPOSE 80
EXPOSE 443