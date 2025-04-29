from typing import Tuple
from opensearchpy import OpenSearch
from dotenv import load_dotenv
from datetime import datetime, timezone
import pycountry
from geopy.geocoders import Nominatim
import json
from urllib.request import urlopen

from app.config import settings
from app.event_consumer import Event_Consumer

load_dotenv()

class Opensearch_Streamer (Event_Consumer):
    def __init__(self):
        self.opensearch_client =  self.create_opensearch_client()
        self.index = self.create_index()

    def create_opensearch_client(self ):
        return OpenSearch(
            hosts=settings.OS_URI,
            http_compress=True,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=True,
            ca_certs=settings.KAFKA_CA_CERT_PATH,
            client_cert=settings.KAFKA_CLIENT_CERT_PATH,
            client_key=settings.KAFKA_CLIENT_KEY_PATH
        )

    def _generate_geo_data(self, country_code) -> Tuple[float, float, str]:
            
        try:
            country = pycountry.countries.get(alpha_2=country_code.upper())
            if not country:
                raise ValueError(f"Invalid country code: {country_code}")
        except Exception as e:
            raise ValueError(f"Invalid country code: {country_code}") from e

        country_name = country.name

        # Use geopy to get the coordinates
        geolocator = Nominatim(user_agent="country_locator", timeout=10 )
        location = geolocator.geocode(country_name)

        if location:            
            return (location.latitude, location.longitude, country_name)
        else:
            return (0, 0, country_name)

    def create_index(self):
        if not self.opensearch_client.indices.exists(index=settings.OS_INDEX):
            self.opensearch_client.indices.create(
                index=settings.OS_INDEX,
                body = {
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "@timestamp": {"type": "date"},
                            "start_time": {"type": "date"},
                            "event_time": {"type": "date"},
                            "event_id": {"type": "keyword"},
                            "session_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                            "event_type": {"type": "keyword"},
                            "page_url": {
                                "type": "text",
                                "fields": {
                                    "keyword": {"type": "keyword", "ignore_above": 256},
                                    "raw": {"type": "keyword"} 
                                }
                            },
                            "page_title": {"type": "text"},
                            "geo_location": {
                                "type": "geo_point" 
                            },
                            "geo_country": {"type": "keyword"}, 
                            "duration": {"type": "integer"},
                            "utm_source": {"type": "keyword"},
                            "utm_medium": {"type": "keyword"},
                            "utm_campaign": {"type": "keyword"},
                            "ip_address": {"type": "keyword"},
                            "user_agent" : {"type": "keyword"},
                            "referrer": {"type": "keyword"},
                            "device_type": {"type": "keyword"},
                            "os": {"type": "keyword"},
                            "browser": {"type": "keyword"}
                        }
                    }
                }
            )

    def process_event(self, event):
        timestamp_str = event["event_time"]
        dt = datetime.fromisoformat(timestamp_str)
        dt = dt.replace(tzinfo=timezone.utc)
        zulu_timestamp = dt.isoformat().replace('+00:00', 'Z')
        geo_data = self._generate_geo_data(event["geo_location"])

        doc = {
            "event_id": event["event_id"],
            "session_id": event["session_id"],
            "user_id": event["user_id"],
            "event_type": event["event_type"],
            "start_time": event["start_time"],
            "event_time": event["event_time"],
            "page_url": event["page_url"],
            "page_title": event["page_title"],
            "geo_country": geo_data[2], 
            "geo_location": {  
                "lat": float(geo_data[0]),
                "lon": float(geo_data[1])
            },
            "duration": event["duration"],
            "ip_address": event["ip_address"],
            "user_agent" : event["user_agent"],
            "referrer": event["referrer"],
            "device_type": event["device_type"],
            "os": event["os"],
            "browser": event["browser"],
            "@timestamp": zulu_timestamp
        }
        
        if event.get("utm_source"):
            doc["utm_source"] = event["utm_source"]
        if event.get("utm_medium"):
            doc["utm_medium"] = event["utm_medium"]
        if event.get("utm_campaign"):
            doc["utm_campaign"] = event["utm_campaign"]
        
        self.opensearch_client.index(
            index=settings.OS_INDEX,
            body=doc,
            id=event["event_id"]
        )