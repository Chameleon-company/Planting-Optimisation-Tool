import ee
from .config import SERVICE_ACCOUNT, KEY_PATH

def init_gee():
    """
    Initialize Google Earth Engine using a service account.

    This function loads the service account email and JSON key path 
    from environment variables (defined in .env via config.py) and 
    uses them to authenticate with Earth Engine.

    Raises:
        Exception: If required environment variables are missing or misconfigured.

    Returns:
        None: Prints a success message upon successful authentication.
    """

    # Ensure the service account email is available
    if SERVICE_ACCOUNT is None:
        raise Exception("Missing GEE_SERVICE_ACCOUNT in .env")

    # Ensure the private key JSON path is available
    if KEY_PATH is None:
        raise Exception("Missing GEE_KEY_PATH in .env")

    # Authenticate using the service account credentials and key file
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
    ee.Initialize(credentials)

    # Confirmation message
    print("GEE authenticated successfully.")
