from datetime import datetime
import random
from psycopg2 import connect # type: ignore
import psycopg2 # type: ignore
from dotenv import load_dotenv # type: ignore
from confluent_kafka import Consumer, KafkaException # type: ignore

from app.config import settings
from app.event_consumer import Event_Consumer

load_dotenv()

class Transaction_Controller (Event_Consumer):

    def __init__(self):
        self.sessions = {}
        self.consumer = Consumer(settings.KAFKA_CONFIG)
        self.conn = psycopg2.connect(settings.DB_CONNNECTION_STRING)
        self._setup_database()

    def _setup_database(self):
        with self.conn.cursor() as cursor:
            # Create events table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clickstream_events (
                event_id VARCHAR(36) PRIMARY KEY,
                session_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                event_type VARCHAR(20) NOT NULL,
                event_time TIMESTAMP NOT NULL,
                page_url TEXT NOT NULL,
                page_title TEXT,
                geo_location VARCHAR(10),
                duration INTEGER,
                utm_source VARCHAR(50),
                utm_medium VARCHAR(50),
                utm_campaign VARCHAR(50)
            )
            """)
        
            # Create sessions table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                ip_address VARCHAR(15) NOT NULL,
                user_agent TEXT NOT NULL,
                referrer TEXT,
                device_type VARCHAR(10) NOT NULL,
                os VARCHAR(20) NOT NULL,
                browser VARCHAR(20) NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                page_count INTEGER NOT NULL,
                session_duration INTEGER,
                is_converted BOOLEAN DEFAULT FALSE
            )
            """)
            
            # Create session metrics table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_metrics (
                session_id VARCHAR(36) PRIMARY KEY,
                avg_duration_per_page FLOAT,
                total_clicks INTEGER,
                total_scrolls INTEGER,
                total_form_submits INTEGER,
                total_add_to_cart INTEGER,
                last_updated TIMESTAMP
            )
            """)
        
        self.conn.commit()

    def cleanup_sessions(self):
        # Periodically check for inactive sessions
        if len(self.sessions) > 0 and random.random() < 0.1:
            current_time = datetime.now()
            for session_id in list(self.sessions.keys()):
                if (current_time - self.sessions[session_id]['last_activity']).total_seconds() > 1800:
                    self.close_session(session_id)

    def process_event(self, event):
        event_time = datetime.fromisoformat(event['event_time'])
               
        # Insert event into clickstream_events table
        with self.conn.cursor() as cursor:
            cursor.execute("""
                    INSERT INTO clickstream_events (
                        event_id, session_id, user_id, event_type, event_time, 
                        page_url, page_title, geo_location, duration, 
                        utm_source, utm_medium, utm_campaign
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (event_id) DO NOTHING
                """, 
            (
                event['event_id'], event['session_id'], event['user_id'], event['event_type'], event_time,
                event['page_url'], event['page_title'], event['geo_location'], event['duration'],
                event.get('utm_source'), event.get('utm_medium'), event.get('utm_campaign')
            ))
            self.conn.commit()
        
        # Update session information
        if event['session_id'] not in self.sessions:
            # This is the first event for this session
            self.sessions[event['session_id']] = {
                'user_id': event['user_id'],
                'start_time': event_time,
                'last_activity': event_time,
                'page_count': 1,
                'clicks': 1 if event['event_type'] == 'click' else 0,
                'scrolls': 1 if event['event_type'] == 'scroll' else 0,
                'form_submits': 1 if event['event_type'] == 'form_submit' else 0,
                'add_to_cart': 1 if event['event_type'] == 'add_to_cart' else 0,
                'total_duration': event['duration']
            }
        else:
            # Update existing session
            session = self.sessions[event['session_id']]
            session['last_activity'] = event_time
            session['page_count'] += 1
            session['total_duration'] += event['duration']
            
            if event['event_type'] == 'click':
                session['clicks'] += 1
            elif event['event_type'] == 'scroll':
                session['scrolls'] += 1
            elif event['event_type'] == 'form_submit':
                session['form_submits'] += 1
            elif event['event_type'] == 'add_to_cart':
                session['add_to_cart'] += 1
        
        # Check if session should be closed (inactive for 30 minutes)
        if (datetime.now() - self.sessions[event['session_id']]['last_activity']).total_seconds() > 1800:
            self.close_session(event['session_id'])

    def close_sessions(self):
        for session_id in list(self.sessions.keys()):
            self.close_session(session_id)

    def close_session(self, session_id):
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        session_duration = (session['last_activity'] - session['start_time']).total_seconds()
        is_converted = session['add_to_cart'] > 0 or session['form_submits'] > 0
        
        with self.conn.cursor() as cursor:
            # Insert or update session in user_sessions table
            cursor.execute("""
            INSERT INTO user_sessions (
                session_id, user_id, ip_address, user_agent, referrer, 
                device_type, os, browser, start_time, end_time, 
                page_count, session_duration, is_converted
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE SET
                end_time = EXCLUDED.end_time,
                page_count = EXCLUDED.page_count,
                session_duration = EXCLUDED.session_duration,
                is_converted = EXCLUDED.is_converted
            """, (
                session_id, session['user_id'], '192.168.1.1', 'Mozilla/5.0', 'https://example.com',
                'desktop', 'Windows', 'Chrome', session['start_time'], session['last_activity'],
                session['page_count'], session_duration, is_converted
            ))
            
            # Calculate and insert session metrics
            avg_duration = session['total_duration'] / session['page_count'] if session['page_count'] > 0 else 0
            
            cursor.execute("""
            INSERT INTO session_metrics (
                session_id, avg_duration_per_page, total_clicks, total_scrolls, 
                total_form_submits, total_add_to_cart, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (session_id) DO UPDATE SET
                avg_duration_per_page = EXCLUDED.avg_duration_per_page,
                total_clicks = EXCLUDED.total_clicks,
                total_scrolls = EXCLUDED.total_scrolls,
                total_form_submits = EXCLUDED.total_form_submits,
                total_add_to_cart = EXCLUDED.total_add_to_cart,
                last_updated = EXCLUDED.last_updated
            """, (
                session_id, avg_duration, session['clicks'], session['scrolls'],
                session['form_submits'], session['add_to_cart'], datetime.now()
            ))
        
        self.conn.commit()
        del self.sessions[session_id]