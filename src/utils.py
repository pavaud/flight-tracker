from pymongo import MongoClient
import requests
import time
from datetime import datetime, timedelta
import os

# CONSTANTS
BASE_URL_CFI = "https://api.lufthansa.com/v1/operations/customerflightinformation/"
BASE_URL_SCHEDULES = "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger?"
API_KEY_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api_keys.txt'))

# FUNCTIONS
def get_key(textfile, api):
    """ 
    returns api token for specific API
    """

    with open(textfile,"r") as f:

        timeout = time.time() + 5      # timemout 5s from now
        while True:
            line = f.readline().split(",") 
            if line[0].lower() == api.lower() or time.time() > timeout:
                break
            time.sleep(0.5)

        try:        
            if line[1][-1:]=='\n':
                bearer = line[1][:-1]
            else:
                bearer = line[1]
        except IndexError:
            #sys.exit("No API key found")
            bearer = "No API key found"
            print("No API key found")
    
    return bearer


def insert_arrivals(col, airport, date_time,headers):
    """ 
    Insert all arrivals from API in the database
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        airport     : airport for the arrivals
        date_time   : date and time for the required by the API. format : %Y-%m-%dT%H:%M
        headers     : header with API token
    """

    # request
    url = BASE_URL_CFI +"arrivals/"+airport+"/"+date_time+"?offset=0&limit=100"
    response = requests.request("GET", url, headers=headers)
    
    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:

        flights = response.json()["FlightInformation"]["Flights"]["Flight"]
        for flight in flights:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                        ]}
                col.replace_one(query,flight,upsert=True)
            except IndexError:
                print(IndexError + "airport : " + airport)
                continue
            except TypeError:
                print(TypeError + "airport : " + airport)
                continue
    else:
        # test
        print("ERROR for arrivals at "  + airport + " - request status is : ", response.status_code)


def insert_departures(col, airport, date_time, headers):
    """ 
    Insert all departures from API in the database
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        airport     : airport for the departures
        date_time   : date and time for the required by the API. format : %Y-%m-%dT%H:%M
        headers     : header with API token
    """

    # request
    url = BASE_URL_CFI + "departures/"+airport+"/"+date_time+"?offset=0&limit=100"
    response = requests.request("GET", url, headers=headers)
    
    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:

        flights = response.json()["FlightInformation"]["Flights"]["Flight"]
        for flight in flights:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                        ]}
                col.replace_one(filter=query, replacement=flight,upsert=True)
            except IndexError:
                print(IndexError + "airport : " + airport)
                continue
            except TypeError:
                print(TypeError + "airport : " + airport)
                continue
            
    else:
        print("ERROR for departures at "  + airport + " - request status is : ", response.status_code)


def remove_old_schedules(col,days=1):
    """Remove schedules older than (today - days) days from col"""

    #d = datetime(2022, 10, 20)
    date = datetime.now() - timedelta(days)
    col.delete_many({"insertedDate":{"$lt": date}})


def get_schedules(col,airline, start, end, headers):
    """
    Insert all schedules from a given airport in col
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        airline     : airline for which we want to get schedules
        start       : schedules start date required by the API. format : DDMMMYY (ex:20OCT22)
        end         : schedules end date required by the API. format : DDMMMYY (ex:27OCT22)
        headers     : header with API token
    """    
        
    # request
    url = BASE_URL_SCHEDULES +"airlines="+airline+"&startDate="+start +"&endDate="+ end + "&daysOfOperation=1234567&timeMode=UTC"
    response = requests.request("GET", url, headers=headers)

    if response.status_code in [200,206]:

        # insert all in collection arrivals    
        for flight in response.json():
            new_flight = {"schema_version": 1.0,
                        "flightnumber":flight["airline"]+str(flight["flightNumber"]),
                        "periodOfOperationUTC":flight["periodOfOperationUTC"],
                        "periodOfOperationLT":flight["periodOfOperationLT"],
                        "origin":flight["legs"][0]["origin"],
                        "destination":flight["legs"][0]["destination"],
                        "insertedDate":datetime(2022,10,1)} # datetime.now() datetime(2022,10,10)
            try:                    
                col.insert_one(new_flight)
            except Exception:
                        print(Exception)
                        print(flight)
                        continue
    else:
        # pour test
        print("ERROR for " , airline, " - request status is : ", response.status_code, " ", response.reason)
        print(response.text)


def insert_flights(col,airline,date,headers):
    """
    Insert all flights from a given airline in col
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        airline     : airline for which we want to get schedules
        date        : date of flight info required by the API. format : %Y-%m-%d (ex:2022-10-23)
        headers     : header with API token
    """    

    # request
    url = BASE_URL_CFI + airline + "/" + date
    response = requests.request("GET", url, headers=headers)
    #print("status code :" + str(response.status_code))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:

        flights = response.json()["FlightInformation"]["Flights"]["Flight"]
        for flight in flights:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                        ]}
                col.replace_one(filter=query, replacement=flight,upsert=True)
            except IndexError:
                print(IndexError + "airport : " + airline)
                continue
            except TypeError:
                print(TypeError + "airport : " + airline)
                continue
    else:
        print("ERROR for departures at "  + airline + " - request status is : ", response.status_code)

