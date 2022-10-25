# standard
import time
from datetime import datetime
from pandas import date_range
# third-party
from pymongo import MongoClient
# project
from utils import *


def main():

    update_departures()
    update_arrivals()

if __name__ == "__main__":
    main()