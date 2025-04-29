import os
import random
import json
import time
from datetime import datetime, timedelta
from confluent_kafka import Producer

from app.config import settings
from app.transactionProducer import TransactionProducer
from app.custom_logging import logger

class TransactionController:

    def __init__(self):
        self.transaction_producer = TransactionProducer()
        self.active_sessions = {}
        self.producer = Producer(settings.KAFKA_CONFIG)
        self.producer.init_transactions() 
    
    def delivery_report(self, err, msg):
        if err:
            logger.error(f"🚨 Delivery failed: {err}")
        else:
            event = json.loads(msg.value())
            status = "✅"
            logger.info(f"{status} Produced event: {event['event_id']} for session: {event['session_id']} at time: {event['event_time']} ")

    def generateMessages(self):

        inf: bool = False
        count:int = 0
        if settings.NUMBER_OF_MESSAGES < 0:
            inf = True
        
        self.producer.begin_transaction()

        try:
            while inf or count < settings.NUMBER_OF_MESSAGES:
                # Randomly select a session or create new one
                session_id = random.choice(list(self.active_sessions.keys())) if self.active_sessions and random.random() < 0.7 else None
                user_session = self.active_sessions.get(session_id)
                
                event, updated_session = self.transaction_producer.generate_click_event(user_session)
                self.active_sessions[updated_session['session_id']] = updated_session
                
                # Send event to Kafka
                
                self.producer.produce(
                    settings.TOPIC_NAME,
                    value=json.dumps(event),
                    callback=self.delivery_report
                )

                logger.info(f"Produced event: {event['event_id']} for session: {event['session_id']}")
                
                # Clean up old sessions (inactive for more than 30 minutes)
                cutoff_time = datetime.now() - timedelta(minutes=30)
                self.active_sessions = {
                    k: v for k, v in self.active_sessions.items() 
                    if datetime.fromisoformat(v['last_activity']) > cutoff_time
                }
                
                time.sleep(random.uniform(0.1, 1.0))
                count = count + 1
            
            self.producer.commit_transaction()
                
        except KeyboardInterrupt:
            logger.error("Stopping producer...")
        except Exception as e:
            logger.error(f"Failed to configure producer: {str(e)}")
        finally:
            self.producer.flush()