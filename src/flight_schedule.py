# standard
import time
from datetime import datetime, timedelta
# third-party
from pymongo import MongoClient
# project
from utils import *


def main():

    # connecting to server
    client = MongoClient(host='127.0.0.1',port=27017)

    # connect to DB and create/open collection
    db = client.flightTracker
    db.drop_collection("schedules") # pour test

    # get api token
    #API_KEY = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api_keys.txt'))
    bearer = get_key(API_KEY_FILE,'lufthansa')
    headers = {'Authorization': 'Bearer '+ bearer}

    # start (today)
    day=datetime.now().strftime("%d")
    month=str(datetime.now().strftime("%b"))[:3].upper()
    year=datetime.now().strftime("%y")
    start = day+month+year
    # end (today + 7 days)
    end_date = datetime.now() + timedelta(days=7)
    day = end_date.strftime("%d")
    month = end_date.strftime("%b")[:3].upper()
    year = end_date.strftime("%y")
    end = day+month+year

    remove_old_schedules(db.schedules, days=7)

    airlines=['LH','OS','LX','EN','WK'] # Lufthansa, Austrian, Swiss, Air Dolomiti and Edelweiss
    for airline in airlines:    
        get_schedules(db.schedules,airline, start, end, headers)
        time.sleep(1)


if __name__ == "__main__":
    main()