# standard
import time
from datetime import datetime
# third-party
from pymongo import MongoClient
# project
from utils import *


def main():

    # connecting to server
    client = MongoClient(host='127.0.0.1',port=27017)

    # connecting to db
    db = client.flightTracker
    db.drop_collection('arrivals')
    db.drop_collection('departures')

    # get api token
    bearer = get_key(API_KEY_FILE,'lufthansa')
    headers = {'Authorization': 'Bearer '+ bearer}


    # airports to put in database
    #airports=['FRA','BER','CDG','LHR','FCO','MAD','DUB','LIS','AMS','LUX','BUD','ATH']
    #airports with bad requests =['MRS','STO','RIX','HEL']
    airlines=['LH','OS','LX','EN','WK'] # Lufthansa, Austrian, Swiss, Air Dolomiti and Edelweiss
    
    # datetime for requests
    #date_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    date = datetime.now().strftime("%Y-%m-%dT08:00")

    for airline in airlines:    
        insert_flights(db.flights,airline,date,headers)
        time.sleep(1)

if __name__ == "__main__":
    main()