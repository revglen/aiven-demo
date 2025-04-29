import random
import datetime
from dotenv import load_dotenv
from faker import Faker # type: ignore

from app.custom_logging import logger
from app.config import settings

load_dotenv()

class TransactionProducer:    

    def __init__(self):             
        self.faker = Faker()

    def _get_random_date_spanning_months(self, months=settings.MONTHS_SPAN):
        today_date = datetime.datetime.now()
        past_date = today_date - datetime.timedelta(days=30*months)
        #future_date = today + datetime.timedelta(days=30*months)

        time_between = today_date - past_date
        random_days = random.randint(0, time_between.days)
        random_date = past_date + datetime.timedelta(days=random_days)
        
        return random_date.isoformat()

    def generate_click_event(self,user_session=None):
        current_time=datetime.datetime.now().isoformat() 
        event_time = self._get_random_date_spanning_months()
        if not user_session or random.random() < 0.3:  # 30% chance to start a new session
            user_session = {
                'session_id': self.faker.uuid4(),
                'user_id': self.faker.uuid4(),
                'ip_address': self.faker.ipv4(),
                'user_agent': self.faker.user_agent(),
                'referrer': self.faker.uri_path(),
                'device_type': random.choice(['desktop', 'mobile', 'tablet']),
                'os': random.choice(['Windows', 'MacOS', 'Linux', 'iOS', 'Android']),
                'browser': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
                'start_time': event_time,
                'last_activity': event_time,
                'page_count': 0
            }
               
        event_types = ['pageview', 'click', 'scroll', 'form_submit', 'add_to_cart']      
        event = {
            'event_id': self.faker.uuid4(),
            'session_id': user_session['session_id'],
            'user_id': user_session['user_id'],
            'event_type': random.choice(event_types),
            'event_time': event_time,
            'page_url': self.faker.uri_path(),
            'page_title': self.faker.sentence(),
            'geo_location': self.faker.country_code(),
            'duration': random.randint(1, 60),
            'utm_source': self.faker.domain_word() if random.random() > 0.7 else None,
            'utm_medium': random.choice(['organic', 'cpc', 'email', 'social']) if random.random() > 0.7 else None,
            'utm_campaign': self.faker.slug() if random.random() > 0.8 else None
        }
        
        user_session['last_activity'] = current_time
        user_session['page_count'] += 1
        
        return event, user_session



