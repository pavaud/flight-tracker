# standard
import os
import time
from datetime import datetime, timedelta
# third-party
import requests
import pandas as pd
from pymongo import MongoClient


# CONSTANTS
BASE_URL_CFI = "https://api.lufthansa.com/v1/operations/customerflightinformation/"
BASE_URL_SCHEDULES = "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger?"
API_KEY_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api_keys.txt'))

# UPDATE FUNCTIONS
def get_key(textfile, api):
    """ returns api token for specific API """

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


def get_headers(api):
    """ returns headers with API token """

    bearer = get_key(API_KEY_FILE, api)
    headers = {'Authorization': 'Bearer '+ bearer}
    return headers


def get_mongo_client():
    """ returns Mongo client """
    
    client = MongoClient(host='127.0.0.1',port=27017)
    return client


def update_arrival(airport, date_time):
    """ 
    Insert all arrivals from API in the database
    
    Parameters:
    -----------
        airport     : airport for the arrivals
        date_time   : date and time required by the API. format : %Y-%m-%dT%H:%M
    """
    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    # request
    url = BASE_URL_CFI +"arrivals/"+airport+"/"+date_time+"?offset=0&limit=100"
    response = requests.request("GET", url, headers=get_headers('lufthansa'))
    
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
        print("URL : ",url,'\n\n')
    
    # close connection
    client.close()


def update_arrivals():
    """ Update arrivals on all airports"""

    #airports=['FRA','BER','CDG','LHR','FCO','MAD','DUB','LIS','AMS','LUX','BUD','ATH']
    #airports with bad requests =['MRS','STO','RIX','HEL']
    airports=['FRA','BER','CDG']
    
    # datetime for requests
    #date_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    date_time = datetime.now().strftime("%Y-%m-%dT08:00")
    
    for airport in airports:    
        update_arrival(airport, date_time)
        time.sleep(1)


def update_departure(airport, date_time):
    """ 
    Insert all departures from API in the database
    
    Parameters:
    -----------
        airport     : airport for the departures
        date_time   : date and time required by the API. format : %Y-%m-%dT%H:%M
    """
    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    # request
    url = BASE_URL_CFI + "departures/"+airport+"/"+date_time+"?offset=0&limit=100"
    response = requests.request("GET", url, headers=get_headers('lufthansa'))
    
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
        print(response.text)
        print("URL : ",url,'\n\n')

    # close connection
    client.close()


def update_departures():
    """ Update departures on all airports"""

    #airports=['FRA','BER','CDG','LHR','FCO','MAD','DUB','LIS','AMS','LUX','BUD','ATH']
    #airports with bad requests =['MRS','STO','RIX','HEL']
    airports=['FRA','BER','CDG']
    
    # datetime for requests
    #date_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    date_time = datetime.now().strftime("%Y-%m-%dT08:00")
    
    for airport in airports:    
        update_departure(airport, date_time)
        time.sleep(1)


def remove_old_schedules(days=1):
    """ Remove schedules older than (today - days) days from col """

    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.schedules

    #d = datetime(2022, 10, 20)
    date = datetime.now() - timedelta(days)
    col.delete_many({"insertedDate":{"$lt": date}})

    client.close()


def update_schedule(airline, start, end):
    """
    Update schedule from a given airline in col
    
    Parameters:
    -----------
        airline     : airline for which we want to get schedules
        start       : schedules start date required by the API. format : DDMMMYY (ex:20OCT22)
        end         : schedules end date required by the API. format : DDMMMYY (ex:27OCT22)
    """    
    
    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.schedules

    # request
    url = BASE_URL_SCHEDULES +"airlines="+airline+"&startDate="+start +"&endDate="+ end + "&daysOfOperation=1234567&timeMode=UTC"
    response = requests.request("GET", url, headers=get_headers('lufthansa'))

    if response.status_code in [200,206]:

        # insert schedule in col    
        for flight in response.json():
            new_flight = {"schema_version": 1.0,
                        "flightnumber":flight["airline"]+str(flight["flightNumber"]),
                        "periodOfOperationUTC":flight["periodOfOperationUTC"],
                        "periodOfOperationLT":flight["periodOfOperationLT"],
                        "origin":flight["legs"][0]["origin"],
                        "destination":flight["legs"][0]["destination"],
                        "insertedDate":datetime.now()} # datetime.now() datetime(2022,10,10)
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
    
    # close connection
    client.close()


def update_schedules():
    """ Update schedules from all compagnies"""
    
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

    # list of airlines (should be requested SQL DB or Mongo DB directly)
    # Lufthansa API offers only the following airline schedules
    airlines=['LH','OS','LX','EN','WK'] # Lufthansa, Austrian, Swiss, Air Dolomiti and Edelweiss
    for airline in airlines:    
        update_schedule(airline, start, end)
        time.sleep(5)


def update_flight(flightnumber):
    """
    Insert a flight from a given flightnumber in col
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        flightnumber: airline for which we want to get schedules
    """    
    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    # request
    date = datetime.now().strftime("%Y-%m-%d")
    url = BASE_URL_CFI + flightnumber + "/" + date
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:

        flight = response.json()["FlightInformation"]["Flights"]["Flight"]
        try:
            query = {'$and':[
                        {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                        {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                    ]}
            col.replace_one(filter=query, replacement=flight,upsert=True)
        except IndexError:
            print(IndexError + "flightnumber : " + flightnumber)
        except TypeError:
            print(TypeError + "flightnumber : " + flightnumber)
    else:
        print("ERROR for flightnumber : "  + flightnumber + " - request status is : ", response.status_code)

    # close connection
    client.close()


def update_flights():
    """ Insert all flights from CSV in col """

    # import flightnumbers to update from CSV 
    # (should be requested SQL DB or Mongo DB directly)
    flights = pd.read_csv('data\\flightnumbers_update.csv')

    for flight in flights['flightnumber']:    
        update_flight(flight)
        time.sleep(1)


def update_routes(departure, arrival, date, headers):
    """ 
    Updates all routes from API in the database
    
    Parameters:
    -----------
        col         : collection in which we want to insert data
        departure   : departure airport
        arrival     : arrival airport
        date        : date required by the API. format : %Y-%m-%d
        headers     : header with API token
    """


# DB REQUESTS
def get_arrivals(col,airport):
    """ Get list of arrivals at given Airport """

    arr_found = list(col.find(filter={'Arrival.AirportCode':airport},
                              sort=[('Arrival.Scheduled.Time',1)]))

    print("\n\nArrivals at airport : " + airport)
    
    columns = ['Scheduled','Actual','Carrier','Flight','Status','Origin']
    data=[]

    for x in arr_found:
        cols = []
        cols.append(x['Arrival']['Scheduled']['Time'])
        cols.append(x['Arrival']['Actual']['Time'])
        cols.append(x['OperatingCarrier']['AirlineID'])
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])
        cols.append(x['Status']['Description'])
        cols.append(x['Departure']['AirportCode'])

        data.append(cols)
    
    df = pd.DataFrame(data, columns=columns)
    print(df)
    return df


def get_departures(col,airport):
    """ Get list of departures at given Airport """

    dep_found = list(col.find(filter={'Departure.AirportCode':airport},
                              sort=[('Departure.Scheduled.Time',1)]))
    
    print("\n\nDepartures at airport : " + airport)
    
    columns = ['Scheduled','Actual','Carrier','Flight','Status','Destination']
    data=[]
    for x in dep_found:
        cols = []
        cols.append(x['Departure']['Scheduled']['Time'])
        try:
            cols.append(x['Departure']['Actual']['Time'])
        except KeyError:
            cols.append('')
        cols.append(x['OperatingCarrier']['AirlineID'])
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])
        cols.append(x['Status']['Description'])
        cols.append(x['Arrival']['AirportCode'])
        
        data.append(cols)
    
    df = pd.DataFrame(data, columns=columns)
    # print(df)
    return df


def get_routes(col, dep, arr, date):
    pass