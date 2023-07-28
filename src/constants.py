import os

from dotenv import load_dotenv


load_dotenv(override=True)

BASE_URL_CFI = os.environ["BASE_URL_CFI"]
BASE_URL_SCHEDULES = os.environ["BASE_URL_SCHEDULES"]

# API_KEY_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api_keys.txt'))
DATA_PATH = os.environ["DATA_PATH"]
AIRPORTS_FILE = os.path.join(DATA_PATH, "airports_valid_for_update.csv")
FLIGHTS_IN_DB_FILE = os.path.join(DATA_PATH, "flights_in_collection.csv")
AIRPORTS_IN_DB_FILE = os.path.join(DATA_PATH, "airports_in_collection.csv")


DB_PATH = os.path.join(os.path.dirname(__file__), "codes.sqlite")
SQL_ALCHEMY_ENGINE = "sqlite:///" + DB_PATH

OPENSKY_USER = os.environ["OPENSKY_USER"]
OPENSKY_PASSWORD = os.environ["OPENSKY_PASSWORD"]

MAPBOX_API_TOKEN = os.environ["OPENSKY_USER"]

LUFTHANSA_API_KEY = os.environ["LUFTHANSA_API_KEY"]

# choose a connection string depending on manual or docker start up
try:
    MONGO_CONNECTION_STR = os.environ["MONGO_CONNECTION_STR"]
except Exception:
    MONGO_CONNECTION_STR = "mongodb://127.0.0.1:27017/"
