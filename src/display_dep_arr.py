# standard
import time
from datetime import datetime
from pandas import date_range
# third-party
from pymongo import MongoClient
# project
from utils import *


def main():

    # connecting to server
    client = MongoClient(host='127.0.0.1',port=27017)

    # connecting to db
    db = client.flightTracker
    #db.drop_collection('arrivals')
    #db.drop_collection('departures')

    # get api token
    bearer = get_key(API_KEY_FILE,'lufthansa')
    headers = {'Authorization': 'Bearer '+ bearer}

    # airports to put in database
    airport = 'FRA'
    get_departures(db.departures,airport)
    get_arrivals(db.departures,airport)

if __name__ == "__main__":
    main()