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
    db.drop_collection('flights')

    # get api token
    bearer = get_key(API_KEY_FILE,'lufthansa')
    headers = {'Authorization': 'Bearer '+ bearer}


    # airports to put in database
    #airports=['FRA','BER','CDG','LHR','FCO','MAD','DUB','LIS','AMS','LUX','BUD','ATH']
    #airports with bad requests =['MRS','STO','RIX','HEL']
    airports=['FRA','BER','CDG']
    
    # datetime for requests
    #date_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    date_time = datetime.now().strftime("%Y-%m-%d")
    
    for airport in airports:    
        insert_departures(db.departures,airport,date_time,headers)
        insert_arrivals(db.arrivals,airport,date_time,headers)
        time.sleep(1)

if __name__ == "__main__":
    main()