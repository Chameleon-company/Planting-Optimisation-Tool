from config.settings import KEY_JSON, KEY_PATH, SERVICE_ACCOUNT


def init_gee():
    """Initialize Google Earth Engine using central config."""
    import ee

    if not SERVICE_ACCOUNT:
        raise RuntimeError("Missing GEE_SERVICE_ACCOUNT in environment variables.")

    if KEY_JSON:
        creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, key_data=KEY_JSON)
    elif KEY_PATH:
        creds = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, key_file=KEY_PATH)
    else:
        raise RuntimeError("Missing GEE_KEY_JSON or GEE_KEY_PATH in environment variables.")

    ee.Initialize(creds)
    return True
