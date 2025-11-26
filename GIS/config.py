import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the process environment.
# This allows sensitive configuration values (like service account credentials)
# to be stored securely outside the codebase.
load_dotenv()

# Retrieve the Google Earth Engine service account email from the environment.
# This value is required for authenticating with Earth Engine via service accounts.
SERVICE_ACCOUNT = os.getenv("GEE_SERVICE_ACCOUNT")

# Retrieve the file path to the service account JSON key.
# This key is used to sign API requests and must remain confidential.
KEY_PATH = os.getenv("GEE_KEY_PATH")
