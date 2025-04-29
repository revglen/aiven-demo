from app.config import settings
from app.transactionController import TransactionController

if __name__ == "__main__":
    print(f"Generating transactions...")
    TransactionController().generateMessages()