from dotenv import load_dotenv
import os

load_dotenv()
print(os.getcwd())

class Settings:
    
    # Kafka Connection
    KAFKA_SERVICE_URI:str=os.getenv("KAFKA_SERVICE_URI")
    KAFKA_HOST:str=os.getenv("KAFKA_HOST")
    KAFKA_PORT:int=os.getenv("KAFKA_PORT")
    KAFKA_PASSWORD:str=os.getenv("KAFKA_PASSWORD")
    KAFKA_CA_CERT_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CA_CERT_PATH")
    KAFKA_CLIENT_CERT_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CLIENT_CERT_PATH")
    KAFKA_CLIENT_KEY_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CLIENT_KEY_PATH")
    KAFKA_USERNAME:str=os.getenv("KAFKA_USERNAME")

    TOPIC_NAME:str=os.getenv("KAFKA_TOPIC_NAME")
    SECURITY_PROTOCOLS:str="ssl" 

    KAFKA_CONFIG = {
        "bootstrap.servers": KAFKA_SERVICE_URI,
        "security.protocol": SECURITY_PROTOCOLS,
        "ssl.ca.location": KAFKA_CA_CERT_PATH,
        "ssl.certificate.location":KAFKA_CLIENT_CERT_PATH,
        'ssl.key.location': KAFKA_CLIENT_KEY_PATH,
        "ssl.endpoint.identification.algorithm": "none",
        "transactional.id": TOPIC_NAME,
        "queue.buffering.max.messages": 100000,
        'retries': 5,
        'retry.backoff.ms': 1000,
        'transaction.timeout.ms': 60000,
        'request.timeout.ms': 30000,
        "default.topic.config": {"acks": "all"}
    }

    NUMBER_OF_MESSAGES=15
    MONTHS_SPAN=5

settings = Settings()

   