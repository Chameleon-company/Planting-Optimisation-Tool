import ee
from .config import SERVICE_ACCOUNT, KEY_PATH

def init_gee():
    if SERVICE_ACCOUNT is None:
        raise Exception("Missing GEE_SERVICE_ACCOUNT in .env")
    if KEY_PATH is None:
        raise Exception("Missing GEE_KEY_PATH in .env")

    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)
    print("GEE authenticated successfully.")
