# standard
import time
from datetime import datetime
# third-party
from pymongo import MongoClient
import pandas as pd
# project
from utils import *


def main():

    # connecting to server
    client = MongoClient(host='127.0.0.1',port=27017)

    # connecting to db
    db = client.flightTracker
    #db.drop_collection('flights')

    # get api token
    bearer = get_key(API_KEY_FILE,'lufthansa')
    headers = {'Authorization': 'Bearer '+ bearer}

    # flights from CSV to update
    flights = pd.read_csv('data\\flightnumbers_update.csv')
    #flights = random.choices(df['flightnumber'],k=50)

    # datetime for requests
    date = datetime.now().strftime("%Y-%m-%d")

    for flight in flights['flightnumber']:    
        insert_flights(db.flights,flight,date,headers)
        time.sleep(1)

if __name__ == "__main__":
    main()