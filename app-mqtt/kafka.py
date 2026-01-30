from confluent_kafka import Producer

conf = {
    "bootstrap.servers": "localhost:29092",
    # "sasl.mechanism": "PLAIN",
    # "security.protocol": "SASL_SSL",
    # "sasl.username": "admin",
    # "sasl.password": "1q2w3e",
}
producer = Producer(**conf)

def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

value = {
    "sensor": "temperature",
    "value": 22.5
}
producer.produce('my_topic', key="", value=str(value), callback=delivery_report)
producer.flush()