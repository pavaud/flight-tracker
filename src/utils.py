# standard
import os
import time
from datetime import datetime, timedelta
# third-party
import requests
import pandas as pd
from pymongo import MongoClient, ASCENDING
from string import *
import plotly.graph_objs as go
# project
from sqldb_requests import *




# CONSTANTS
BASE_URL_CFI = "https://api.lufthansa.com/v1/operations/customerflightinformation/"
BASE_URL_SCHEDULES = "https://api.lufthansa.com/v1/flight-schedules/flightschedules/passenger?"
API_KEY_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'api_keys.txt'))
AIRPORTS_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data','airports_valid_for_update.csv'))
FLIGHTS_IN_DB_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data','flights_in_collection.csv'))
AIRPORTS_IN_DB_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data','airports_in_collection.csv'))




def get_credentials(filepath=API_KEY_FILE):
    # Get credentials for opensky and token for mapbox
    
    f = open(filepath, 'r')
    lines = f.readlines()
    user_name = lines[1].strip()
    password = lines[2].strip()
    token = lines[3].strip()
    f.close()
    
    return user_name, password, token
    

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
    
    # choos a connection string depending on manual or docker start up
    try:
        MONGO_CONNECTION_STR = os.environ['MONGO_CONNECTION_STR']
    except:
        MONGO_CONNECTION_STR = 'mongodb://127.0.0.1:27017/'

    client = MongoClient(MONGO_CONNECTION_STR) #1.0.1
    
    return client


# UPDATE FUNCTIONS
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

        if isinstance(flights, (list)):
            for flight in flights:
                try:
                    query = {'$and':[
                                {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                                {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                            ]}
                    col.replace_one(query,flight,upsert=True)
                except IndexError:
                    print(IndexError)
                    print("URL : ",url,'\n\n')
                    continue
                except TypeError:
                    print(TypeError)
                    print("URL : ",url,'\n\n')
                    continue
        else:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':flights['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':flights['OperatingCarrier']['FlightNumber']}}
                        ]}
                col.replace_one(filter=query, replacement=flights,upsert=True)
            except IndexError:
                print(IndexError)
                print("URL : ",url,'\n\n')                
            except TypeError:
                print(TypeError)
                print("URL : ",url,'\n\n')

    else:
        print("ERROR for arrivals at "  + airport + " - request status is : ", response.status_code)
        print(response.text)
        print("URL : ",url,'\n\n')
    
    # close connection
    client.close()


def update_arrivals():
    """ Update arrivals on all airports"""

    airports=['FRA','BER','CDG']
    
    # datetime for requests
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

        if isinstance(flights, (list)):
            for flight in flights:
                try:
                    query = {'$and':[
                                {'OperatingCarrier.AirlineID': {'$eq':flight['OperatingCarrier']['AirlineID']}},
                                {'OperatingCarrier.FlightNumber': {'$eq':flight['OperatingCarrier']['FlightNumber']}}
                            ]}
                    col.replace_one(filter=query, replacement=flight,upsert=True)
                except IndexError:
                    print(IndexError)
                    print("URL : ",url,'\n\n')                
                    continue
                except TypeError:
                    print(TypeError)
                    print("URL : ",url,'\n\n')                
                    continue
        else:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':flights['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':flights['OperatingCarrier']['FlightNumber']}}
                        ]}
                col.replace_one(filter=query, replacement=flights,upsert=True)
            except IndexError:
                print(IndexError)
                print("URL : ",url,'\n\n')                
            except TypeError:
                print(TypeError)
                print("URL : ",url,'\n\n')                
            
    else:
        print("ERROR for departures at "  + airport + " - request status is : ", response.status_code)
        print(response.text)
        print("URL : ",url,'\n\n')

    # close connection
    client.close()


def update_departures():
    """ Update departures on all airports"""

    airports=['FRA','BER','CDG']
    
    # datetime for requests
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
            print(IndexError)
            print("URL : ",url,'\n\n')                
        except TypeError:
            print(IndexError)
            print("URL : ",url,'\n\n')                

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


def update_route(dep, arr):
    """
    Update route given by dep and arr from the API in DB
    
    Parameters:
    -----------
        dep : departure iata airport code
        arr : arrival iata airport code
    """    
    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.routes

    # request
    date = datetime.now().strftime("%Y-%m-%d")
    url = BASE_URL_CFI+ "route/" + dep + "/" + arr + "/" + date
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:

        routes = response.json()["FlightInformation"]["Flights"]["Flight"]
        for route in routes:
            try:
                query = {'$and':[
                            {'OperatingCarrier.AirlineID': {'$eq':route['OperatingCarrier']['AirlineID']}},
                            {'OperatingCarrier.FlightNumber': {'$eq':route['OperatingCarrier']['FlightNumber']}},
                        ]}
                col.replace_one(filter=query, replacement=route,upsert=True)
            except IndexError:
                print(IndexError)
                print("route : " + dep + "/"+ arr)
                continue
            except TypeError:
                print(IndexError)
                print("route : " + dep + "/"+ arr)
                continue
    else:
        print("ERROR for route : "  + dep + "/"+ arr + " - request status is : ", response.status_code)

    # close connection
    client.close()


def update_routes():
    """ Updates all routes from API in the database """
    
    # import routes to update from CSV 
    # (should be requested SQL DB or Mongo DB directly)
    routes = pd.read_csv('data\\routes_update.csv')

    for dep, arr in zip(routes['origin'],routes['destination']):    
        update_route(dep, arr)
        time.sleep(1)


def update_flight_status():
    """ Update flight status on all airports"""

    airports = pd.read_csv(AIRPORTS_FILE)
    #airports with bad requests =['STO','RIX','HEL']
    airport_shortlist = airports['airport']
    #airport_shortlist = ['STO','RIX','HEL']

    # datetime for requests
    #date_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    date_time = datetime.now().strftime("%Y-%m-%dT08:00")


    for airport in airport_shortlist:
        print(airport)
        update_departure(airport, date_time)
        update_arrival(airport,date_time)
        time.sleep(1)


def update_position(response):
    """update airplane GPS position and altitude from opensky API"""

    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.position

    # set index 'callsign' on position collection if it doesn't exist
    indexes = []
    for idx in col.list_indexes():
        indexes.append(idx["name"])

    if "callsign_1" not in indexes:
        col.create_index(["callsign", ASCENDING])
    
    # update flight position and altitude or insert if not found
    for flight in response["states"]:

        filter = {"callsign": flight[1]}
        update = {
            "$push": { 
                "position":{
                    "lat":flight[6],
                    "lon":flight[5]
                },
                "altitude": flight[13],
                "date_time": datetime.now().strftime("%H-%M-%S")
            }
        }

        try:                    
            col.update_one(filter=filter, 
                           update=update,
                           upsert=True)
        except Exception:
            print(Exception)
            print(flight)
            continue
    
    # close connection
    client.close()



# DB REQUESTS
def get_arrivals(airport):
    """ Get list of arrivals at given Airport """

    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    arr_found = list(col.find(filter={'Arrival.AirportCode':airport.upper()},
                              sort=[('Arrival.Scheduled.Time',1)]))
    
    columns = ['Scheduled','Actual','Carrier','Flight','Status','Origin']
    data=[]

    for x in arr_found:
        cols = []
        cols.append(x['Arrival']['Scheduled']['Time'])
        try:
            cols.append(x['Arrival']['Actual']['Time'])
        except KeyError:
            cols.append('')
        cols.append(x['OperatingCarrier']['AirlineID'])
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])
        cols.append(x['Status']['Description'])
        cols.append(x['Departure']['AirportCode'])

        data.append(cols)
    
    df = pd.DataFrame(data, columns=columns)

    # close connection
    client.close()

    return df


def get_departures(airport):
    """ Get list of departures at given Airport """

    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    dep_found = list(col.find(filter={'Departure.AirportCode':airport.upper()},
                              sort=[('Departure.Scheduled.Time',1)]))
        
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

    # close connection
    client.close()

    return df


def get_routes(dep, arr):
    """ Get list of routes between given departure and arrival airport """

    # connecting collection
    client = get_mongo_client()
    col = client.flightTracker.flights

    # get routes from mongo collection
    filter = {"Departure.AirportCode":dep.upper(),
              "Arrival.AirportCode":arr.upper()}
    routes = list(col.find(filter=filter))

    # format df columns
    columns = ['airline_name','airline_iata','flight', 
                'dep_iata','dep_airport','dep_city',
                'dep_scheduled','dep_actual',
                'arr_iata','arr_airport','arr_city',
                'arr_scheduled','arr_ctual',
                'status']

    # create df
    data=[]
    for x in routes:
        cols = []
        
        # flight
        airline_iata = x['OperatingCarrier']['AirlineID']
        airline_name = get_airline_from_iata(airline_iata)
        cols.append(airline_name)
        cols.append(airline_iata)
        cols.append(airline_iata + x['OperatingCarrier']['FlightNumber'])

        # departure
        dep_iata = x['Departure']['AirportCode']
        dep_airport = get_airport_infos(dep_iata)[0]
        dep_city = get_airport_infos(dep_iata)[1]
        cols.append(dep_iata)
        cols.append(dep_airport)
        cols.append(dep_city)
        cols.append(x['Departure']['Scheduled']['Time'])
        try:
            cols.append(x['Departure']['Actual']['Time'])
        except KeyError:
            cols.append('')

        # arrival
        arr_iata = x['Arrival']['AirportCode']
        arr_airport = get_airport_infos(arr_iata)[0]
        arr_city = get_airport_infos(arr_iata)[1]
        cols.append(arr_iata)
        cols.append(arr_airport)
        cols.append(arr_city)
        cols.append(x['Arrival']['Scheduled']['Time'])
        try:
            cols.append(x['Arrival']['Actual']['Time'])
        except KeyError:
            cols.append('')
        
        # flight status
        cols.append(x['Status']['Description'])
        
        # add line in df
        data.append(cols)

    df = pd.DataFrame(data=data, columns=columns)

    # close connection
    client.close()

    return df


def get_all_flights():
    """ get all flights in flights collection """

    client = get_mongo_client()
    col = client.flightTracker.flights

    flights = list(col.find({}))
    
    columns = ['departure','dep_iata','dep_scheduled','dep_actual','terminal_gate',
                'arrival','arr_iata','arr_scheduled','dep_actual','terminal_gate',
                'carrier_code','carrier','flight','status']
    data=[]

    for x in flights:
        cols = []
        
        # departure
        try:
            cols.append(get_airport_infos(x['Departure']['AirportCode'])[0])
        except IndexError:
            cols.append('')
        cols.append(x['Departure']['AirportCode'])
        cols.append(x['Departure']['Scheduled']['Time'])
        try:
            cols.append(x['Departure']['Actual']['Time'])
        except KeyError:
            cols.append('')
        try:
            cols.append(x['Departure']['Terminal']['Name']+"/"+x['Departure']['Terminal']['Gate'])
        except KeyError:
            cols.append('')

        # arrival
        try:
            cols.append(get_airport_infos(x['Arrival']['AirportCode'])[0])
        except IndexError:
            cols.append('')
        cols.append(x['Arrival']['AirportCode'])
        cols.append(x['Arrival']['Scheduled']['Time'])
        try:
            cols.append(x['Arrival']['Actual']['Time'])
        except KeyError:
            cols.append('')
        try:    
            cols.append(x['Arrival']['Terminal']['Name']+"/"+x['Arrival']['Terminal']['Gate'])
        except KeyError:
            cols.append('')

        # general
        cols.append(x['OperatingCarrier']['AirlineID'])
        cols.append(get_airline_from_iata(x['OperatingCarrier']['AirlineID']))
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])
        cols.append(x['Status']['Description'])

        data.append(cols)
    
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(FLIGHTS_IN_DB_FILE, index=False)

    # close connection
    client.close()

    return df


def list_available_airports():
    """ get all airports available in the flights collection """

    df = pd.read_csv(FLIGHTS_IN_DB_FILE)
    df1 = df[['dep_iata', 'departure']]
    df1.columns = ['iata','airport']
    df2 = df[['arr_iata', 'arrival']]
    df2.columns = ['iata','airport']
    df3 = pd.concat([df1,df2])

    airports = df3.drop_duplicates()
    airports.to_csv(AIRPORTS_IN_DB_FILE, index=False)

    return airports


def get_opensky_flights():
    """ get currently flying airplanes from opensky API """

    user_name, password = get_credentials()[:2]

    # defining the spatial field
    lon_min, lat_min = -180., -90.
    lon_max, lat_max = 180., 90.

    # send request to get the current airplane data
    url_data = 'https://'+user_name+':'+password+'@opensky-network.org/api/states/all?'+'lamin='+str(lat_min)+'&lomin='+str(lon_min)+'&lamax='+str(lat_max)+'&lomax='+str(lon_max)
    response = requests.get(url_data).json()

    update_position(response)

    return response


def get_opensky_df(response):
    """ creates and returns dataframe from opensky response """

    # load the data as a pandas dataframe
    columns = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'long', 'lat', 
                'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 'sensors', 
                'geo_altitude', 'squawk', 'spi', 'position_source']
    df = pd.DataFrame(response['states'],columns=columns)

    # filling missing data
    df.true_track = df.true_track.fillna(0)
    df = df.fillna('NaN')

    return df


def flight_tracker():
    """ returns a map with all airplanes from opensky """

    token = get_credentials()[2]
    response = get_opensky_flights()
    df = get_opensky_df(response)

    #Define figure and its characteristics
    fig = go.Figure(go.Scattermapbox(
            lon = df.long, 
            lat = df.lat, 
            #text = df.text, 
            mode = 'markers',
            hoverinfo='none',
            marker = {'size': 14,
                      'symbol': 'airport', 
                      'allowoverlap': True, 
                      'angle': df.true_track}
    ))

    fig.update_layout(height = 900, 
                      margin = {"r":0, "t":0, "l":0, "b":0},
                      mapbox = {'accesstoken': token, 
                                'style': "outdoors", 
                                'zoom': 1.9},
                      showlegend = False,
                      uirevision = True
    )

   
    return df, fig

def get_altitudes(callsign):
    """Get the list of altitudes for given airplane callsign"""
    
    # db connection
    client = get_mongo_client()
    col = client.flightTracker.position

    # get the right callsign in collection
    filter = {"callsign":callsign}
    projection = {"_id":0, "altitude":1, "date_time":1}
    result = col.find_one(filter=filter,
                          projection=projection)
    print(result)
    altitude = result['altitude']
    date_time = result['date_time']

    df = pd.DataFrame(data=list(zip(date_time, altitude)),
                      columns=["time","altitude"])
    print(df)

    return df