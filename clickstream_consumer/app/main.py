from app.config import settings
from app.transaction_consumer import Transaction_Consumer

if __name__ == "__main__":
    print(f"Generating transactions...")
    Transaction_Consumer().process_messages()