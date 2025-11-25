import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")
KEY_PATH = os.getenv("GEE_KEY_PATH")