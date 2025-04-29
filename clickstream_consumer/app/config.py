import os
from dotenv import load_dotenv # type: ignore

load_dotenv()
print(os.getcwd())

class Settings:
    
    # Kafka Connection for Aiven
    KAFKA_SERVICE_URI:str=os.getenv("KAFKA_SERVICE_URI")
    KAFKA_HOST:str=os.getenv("KAFKA_HOST")
    KAFKA_PORT:int=os.getenv("KAFKA_PORT")    
    KAFKA_CA_CERT_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CA_CERT_PATH")
    KAFKA_CLIENT_CERT_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CLIENT_CERT_PATH")
    KAFKA_CLIENT_KEY_PATH:str=os.getcwd() + "/" + os.getenv("KAFKA_CLIENT_KEY_PATH")
    SASL_USERNAME = os.getenv('KAFKA_USERNAME')
    SASL_PASSWORD = os.getenv('KAFKA_PASSWORD')

    TOPIC_NAME:str=os.getenv("KAFKA_TOPIC_NAME")
    SECURITY_PROTOCOLS:str="ssl" 

    KAFKA_CONFIG = {
        "bootstrap.servers": KAFKA_SERVICE_URI,
        "security.protocol": SECURITY_PROTOCOLS,
        "ssl.ca.location": KAFKA_CA_CERT_PATH,
        "ssl.certificate.location":KAFKA_CLIENT_CERT_PATH,
        'ssl.key.location': KAFKA_CLIENT_KEY_PATH,
        "group.id": "clickstream-group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "isolation.level": "read_committed"
    }

    ###################################################

    #Database Settings for Aiven Postgres
    DB_NAME:str=os.getenv("PG_HOST")
    DB_USER:str=os.getenv("PG_USER")
    DB_PASSWORD:str=os.getenv("PG_PASSWORD")
    DB_HOST:str=os.getenv("PG_HOST")
    DB_PORT:int=os.getenv("PG_PORT")
    SSL_MODE:str="require"
    DB_CONNNECTION_STRING:str=os.getenv("PG_SERVICE_URI")


    ###################################################

    # OpenSearch Settings for Aiven OpenSearch
    OS_URI:str = os.getenv("OS_SERVICE_URI")
    OS_INDEX:str = 'clickstream-events'
    OS_USER:str=os.getenv("OS_USER")
    OS_PASSWORD:str=os.getenv("OS_PASSWORD")

settings = Settings()
   