
import json
import urllib3
from confluent_kafka import Consumer, KafkaException # type: ignore
from app.transaction_controller import Transaction_Controller
from app.opensearch_streamer import Opensearch_Streamer
from app.config import settings
from app.custom_logging import logger

# Disable SSL warnings (not recommended for production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Transaction_Consumer:

    def __init__(self):
        self.consumer = Consumer(settings.KAFKA_CONFIG)
        self.trans = Transaction_Controller()
        self.opensearch=Opensearch_Streamer()
    
    def process_messages(self):
        self.consumer.subscribe([settings.TOPIC_NAME])
        try: 
            while True:                
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    raise KafkaException(msg.error())
                event = json.loads(msg.value())
                self.trans.process_event(event)
                self.opensearch.process_event(event)
                self.consumer.commit(asynchronous=False)
                self.trans.cleanup_sessions()                
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")       
        except KafkaException as k:
            logger.error(f"\nShutting down. {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            # Close all active sessions before exiting
            self.trans.close_sessions()            
            self.trans.consumer.close()
            