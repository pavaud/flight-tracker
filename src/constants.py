import os

from dotenv import load_dotenv

# fmt: off

# Load environment variables
dotenv_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path, override=True)

LOG_DIR = os.environ["LOG_DIR"]
DASH_LOG = os.environ["DASH_LOG"]
DASH_LOG_PATH = os.path.join(LOG_DIR, DASH_LOG)
CRON_LOG = os.environ["CRON_LOG"]
CRON_LOG_PATH = os.path.join(LOG_DIR, CRON_LOG)

MAP_UPDATE_INTERVAL = int(os.environ["MAP_UPDATE_INTERVAL"])

BASE_URL_CFI = os.environ["BASE_URL_CFI"]
BASE_URL_SCHEDULES = os.environ["BASE_URL_SCHEDULES"]

DATA_DIR = os.environ["DATA_DIR"]
VALID_AIRPORTS_FILE = os.path.join(DATA_DIR, "airports_valid_for_update.csv")
FLIGHTS_IN_DB_FILE = os.path.join(DATA_DIR, "flights_in_collection.csv")
AIRPORTS_IN_DB_FILE = os.path.join(DATA_DIR, "airports_in_collection.csv")

try:
    aws = os.environ["AWS"]
    AIRPORTS_FILE = "https://ft-app.s3.eu-west-3.amazonaws.com/airports.csv"
    AIRLINES_FILE = "https://ft-app.s3.eu-west-3.amazonaws.com/airlines.csv"
    CITIES_FILE = "https://ft-app.s3.eu-west-3.amazonaws.com/cities.csv"
except Exception:
    AIRPORTS_FILE = os.path.join(DATA_DIR, "load_sqlite", "airports.csv")
    AIRLINES_FILE = os.path.join(DATA_DIR, "load_sqlite", "airlines.csv")
    CITIES_FILE = os.path.join(DATA_DIR, "load_sqlite", "cities.csv")


DB_PATH = os.path.join(os.path.dirname(__file__), "codes.sqlite")
SQL_ALCHEMY_ENGINE = "sqlite:///" + DB_PATH

OPENSKY_BASE_URL = os.environ["OPENSKY_BASE_URL"]

MAPBOX_API_TOKEN = os.environ["MAPBOX_API_TOKEN"]

LUFTHANSA_API_KEY = os.environ["LUFTHANSA_API_KEY"]

# choose a connection string depending on manual or docker start up
try:
    MONGO_CONNECTION_STR = os.environ["MONGO_CONNECTION_STR"]
except Exception:
    MONGO_CONNECTION_STR = "mongodb://127.0.0.1:27017/"
