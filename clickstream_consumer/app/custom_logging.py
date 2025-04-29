import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kafka_consumer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)