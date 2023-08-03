import argparse
import logging
import os
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any

import requests
import pandas as pd
from pymongo import MongoClient, ASCENDING
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
import plotly.graph_objs as go

import constants as c
from sqldb_requests import get_airline_from_iata, get_airport_infos


def init_args() -> argparse.Namespace:
    """Parse the command line arguments and returns them"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--loglevel",
        default="INFO",
        help="Provide logging level. Example --loglevel debug, default=INFO",
    )
    return parser.parse_args()


def init_log_conf(level: str, filename: str) -> None:
    """Initialize the logging configuration"""

    dir_path = os.path.dirname(filename)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    logging.basicConfig(
        encoding="utf-8",
        level=level.upper(),
        format="[%(asctime)s] %(levelname)-7s %(module)-15s %(lineno)-5d : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            RotatingFileHandler(
                filename,
                maxBytes=2 * 1024 * 1024,
                backupCount=5,
            ),
            logging.StreamHandler(),
        ],
    )


def get_headers(api: str) -> dict:
    """returns headers with API token"""
    api_key = ""
    if api == "lufthansa":
        api_key = c.LUFTHANSA_API_KEY
    return {"Authorization": "Bearer " + api_key}


# UPDATE FUNCTIONS
def update_arrival(airport: str, date_time: str) -> None:
    """
    Insert all arrivals from API in the database

    Parameters:
    -----------
        airport     : airport for the arrivals
        date_time   : date and time required by the API. format : %Y-%m-%dT%H:%M
    """

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    # request
    url = f"{c.BASE_URL_CFI}arrivals/{airport}/{date_time}?offset=0&limit=100"
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:
        flights = response.json()["FlightInformation"]["Flights"]["Flight"]

        if isinstance(flights, (list)):
            for flight in flights:
                try:
                    query = {
                        "$and": [
                            {
                                "OperatingCarrier.AirlineID": {
                                    "$eq": flight["OperatingCarrier"][
                                        "AirlineID"
                                    ]
                                }
                            },
                            {
                                "OperatingCarrier.FlightNumber": {
                                    "$eq": flight["OperatingCarrier"][
                                        "FlightNumber"
                                    ]
                                }
                            },
                        ]
                    }
                    col.replace_one(query, flight, upsert=True)
                except (IndexError, TypeError) as e:
                    logging.error(f" URL : {url}\n{e}")
                    continue
        else:
            try:
                query = {
                    "$and": [
                        {
                            "OperatingCarrier.AirlineID": {
                                "$eq": flights["OperatingCarrier"]["AirlineID"]
                            }
                        },
                        {
                            "OperatingCarrier.FlightNumber": {
                                "$eq": flights["OperatingCarrier"][
                                    "FlightNumber"
                                ]
                            }
                        },
                    ]
                }
                col.replace_one(filter=query, replacement=flights, upsert=True)
            except (IndexError, TypeError) as e:
                logging.error(f" URL : {url}\n{e}")

    else:
        logging.error(
            f"Error for arrivals at {airport}\n"
            f"request status is : {response.status_code}\n"
            f"URL : {url}\n"
            f"{response.text}"
        )

    # close connection
    client.close()


def update_arrivals() -> None:
    """Update arrivals on all airports"""

    airports = ["FRA", "BER", "CDG"]

    # datetime for requests
    date_time = datetime.now().strftime("%Y-%m-%dT08:00")

    for airport in airports:
        update_arrival(airport, date_time)
        time.sleep(1)


def update_departure(airport: str, date_time: str) -> None:
    """
    Insert all departures from API in the database

    Parameters:
    -----------
        airport     : airport for the departures
        date_time   : date and time required by the API. format : %Y-%m-%dT%H:%M
    """
    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    # request
    url = f"{c.BASE_URL_CFI}departures/{airport}/{date_time}?offset=0&limit=100"  # fmt: skip
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:
        flights = response.json()["FlightInformation"]["Flights"]["Flight"]

        if isinstance(flights, (list)):
            for flight in flights:
                try:
                    query = {
                        "$and": [
                            {
                                "OperatingCarrier.AirlineID": {
                                    "$eq": flight["OperatingCarrier"][
                                        "AirlineID"
                                    ]
                                }
                            },
                            {
                                "OperatingCarrier.FlightNumber": {
                                    "$eq": flight["OperatingCarrier"][
                                        "FlightNumber"
                                    ]
                                }
                            },
                        ]
                    }
                    col.replace_one(filter=query, replacement=flight, upsert=True)  # fmt: skip
                except (IndexError, TypeError) as e:
                    logging.error(f" URL : {url}\n{e}")
                    continue
        else:
            try:
                query = {
                    "$and": [
                        {
                            "OperatingCarrier.AirlineID": {
                                "$eq": flights["OperatingCarrier"]["AirlineID"]
                            }
                        },
                        {
                            "OperatingCarrier.FlightNumber": {
                                "$eq": flights["OperatingCarrier"][
                                    "FlightNumber"
                                ]
                            }
                        },
                    ]
                }
                col.replace_one(filter=query, replacement=flights, upsert=True)
            except (IndexError, TypeError) as e:
                logging.error(f" URL : {url}\n{e}")

    else:
        logging.error(
            f"Error for departures at {airport}\n"
            f"request status is : {response.status_code}\n"
            f"URL : {url}\n"
            f"{response.text}"
        )

    # close connection
    client.close()


def update_departures() -> None:
    """Update departures on all airports"""

    airports = ["FRA", "BER", "CDG"]

    # datetime for requests
    date_time = datetime.now().strftime("%Y-%m-%dT08:00")

    for airport in airports:
        update_departure(airport, date_time)
        time.sleep(1)


def remove_old_schedules(days: int = 1) -> None:
    """Remove schedules older than (today - days) days from col"""

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.schedules

    date = datetime.now() - timedelta(days)
    col.delete_many({"insertedDate": {"$lt": date}})

    client.close()


def update_schedule(airline: str, start: str, end: str) -> None:
    """
    Update schedule from a given airline in col

    Parameters:
    -----------
        airline     : airline for which we want to get schedules
        start       : schedules start date required by the API. format : DDMMMYY (ex:20OCT22)
        end         : schedules end date required by the API. format : DDMMMYY (ex:27OCT22)
    """

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.schedules

    # request
    url = f"{c.BASE_URL_SCHEDULES}airlines={airline}&startDate={start}&endDate={end}&daysOfOperation=1234567&timeMode=UTC"
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    if response.status_code in [200, 206]:
        # insert schedule in col
        for flight in response.json():
            new_flight = {
                "schema_version": 1.0,
                "flightnumber": flight["airline"]
                + str(flight["flightNumber"]),
                "periodOfOperationUTC": flight["periodOfOperationUTC"],
                "periodOfOperationLT": flight["periodOfOperationLT"],
                "origin": flight["legs"][0]["origin"],
                "destination": flight["legs"][0]["destination"],
                "insertedDate": datetime.now(),
            }
            try:
                col.insert_one(new_flight)
            except OperationFailure as e:
                logging.error(f"Error during inserting flight {flight}. {e}")
                continue
            except ServerSelectionTimeoutError as e:
                logging.error(f"Cannot connect to server. {e}")
                continue
    else:
        logging.error(
            f"Error for airline {airline}\n"
            f"Request status : {response.status_code}\n"
            f"Reason : {response.reason}\n{response.text}"
        )

    # close connection
    client.close()


def update_schedules() -> None:
    """Update schedules from all compagnies"""

    # start (today)
    day = datetime.now().strftime("%d")
    month = str(datetime.now().strftime("%b"))[:3].upper()
    year = datetime.now().strftime("%y")
    start = day + month + year
    # end (today + 7 days)
    end_date = datetime.now() + timedelta(days=7)
    day = end_date.strftime("%d")
    month = end_date.strftime("%b")[:3].upper()
    year = end_date.strftime("%y")
    end = day + month + year

    # list of airlines (should be requested SQL DB or Mongo DB directly)
    # Lufthansa API offers only the following airline schedules
    # Lufthansa, Austrian, Swiss, Air Dolomiti and Edelweiss
    airlines = ["LH", "OS", "LX", "EN", "WK"]
    for airline in airlines:
        update_schedule(airline, start, end)
        time.sleep(5)


def update_flight(flightnumber: str) -> None:
    """
    Insert a flight from a given flightnumber in col

    Parameters:
    -----------
        col         : collection in which we want to insert data
        flightnumber: airline for which we want to get schedules
    """
    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    # request
    date = datetime.now().strftime("%Y-%m-%d")
    url = f"{c.BASE_URL_CFI}flightnumber/{date}"
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:
        flight = response.json()["FlightInformation"]["Flights"]["Flight"]
        try:
            query = {
                "$and": [
                    {
                        "OperatingCarrier.AirlineID": {
                            "$eq": flight["OperatingCarrier"]["AirlineID"]
                        }
                    },
                    {
                        "OperatingCarrier.FlightNumber": {
                            "$eq": flight["OperatingCarrier"]["FlightNumber"]
                        }
                    },
                ]
            }
            col.replace_one(filter=query, replacement=flight, upsert=True)
        except (IndexError, TypeError) as e:
            logging.error(f" URL : {url}\n{e}")

    else:
        logging.error(
            f"Error for flightnumber {flightnumber}\n"
            f"Request status is : {response.status_code}\n"
            f"URL : {url}\n"
            f"{response.text}"
        )

    # close connection
    client.close()


def update_flights() -> None:
    """Insert all flights from CSV in col"""

    # import flightnumbers to update from CSV
    # (should be requested SQL DB or Mongo DB directly)
    flights = pd.read_csv("data\\flightnumbers_update.csv")

    for flight in flights["flightnumber"]:
        update_flight(flight)
        time.sleep(1)


def update_route(dep: str, arr: str) -> None:
    """
    Update route given by dep and arr from the API in DB

    Parameters:
    -----------
        dep : departure iata airport code
        arr : arrival iata airport code
    """
    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.routes

    # request
    date = datetime.now().strftime("%Y-%m-%d")
    url = f"{c.BASE_URL_CFI}route/{dep}/{arr}/{date}"
    response = requests.request("GET", url, headers=get_headers("lufthansa"))

    # replace or insert all in given collection
    if response.status_code == requests.codes.OK:
        routes = response.json()["FlightInformation"]["Flights"]["Flight"]
        for route in routes:
            try:
                query = {
                    "$and": [
                        {
                            "OperatingCarrier.AirlineID": {
                                "$eq": route["OperatingCarrier"]["AirlineID"]
                            }
                        },
                        {
                            "OperatingCarrier.FlightNumber": {
                                "$eq": route["OperatingCarrier"][
                                    "FlightNumber"
                                ]
                            }
                        },
                    ]
                }
                col.replace_one(filter=query, replacement=route, upsert=True)
            except (IndexError, TypeError) as e:
                logging.error(f" URL : {url}\n{e}")
                continue
    else:
        logging.error(
            f"Error for route {dep}/{arr}\n"
            f"request status is : {response.status_code}\n"
            f"URL : {url}\n"
            f"{response.text}"
        )

    # close connection
    client.close()


def update_routes() -> None:
    """Updates all routes from API in the database"""

    # import routes to update from CSV
    # (should be requested SQL DB or Mongo DB directly)
    routes = pd.read_csv("data\\routes_update.csv")

    for dep, arr in zip(routes["origin"], routes["destination"]):
        update_route(dep, arr)
        time.sleep(1)


def update_flight_status() -> None:
    """Update flight status on all airports"""

    airports = pd.read_csv(c.VALID_AIRPORTS_FILE)
    airport_shortlist = airports["airport"]

    date_time = datetime.now().strftime("%Y-%m-%dT08:00")

    for airport in airport_shortlist:
        logging.debug(airport)

        update_departure(airport, date_time)
        update_arrival(airport, date_time)

        time.sleep(1)


def update_position(response: Any) -> None:
    """update airplane GPS position and altitude from opensky API"""

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.position

    # set index on 'callsign' in position collection if it doesn't exist
    indexes = []
    for idx in col.list_indexes():
        indexes.append(idx["name"])

    if "callsign_1" not in indexes:
        col.create_index([("callsign", ASCENDING)])

    # update flight position and altitude or insert if not found
    for flight in response["states"]:
        filter = {"callsign": flight[1]}
        update = {
            "$push": {
                "position": {"lat": flight[6], "lon": flight[5]},
                "altitude": flight[13],
                "date_time": datetime.now().strftime("%H:%M:%S"),
            }
        }

        try:
            col.update_one(filter=filter, update=update, upsert=True)
        except OperationFailure as e:
            logging.error(f"Error updating position of Flight : {flight}. {e}")
            continue
        except ServerSelectionTimeoutError as e:
            logging.error(f"Cannot connect to server. {e}")
            continue

    # close connection
    client.close()


# DB REQUESTS
def get_arrivals(airport: str) -> pd.DataFrame:
    """Get list of arrivals at given Airport"""

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    arr_found = list(
        col.find(
            filter={"Arrival.AirportCode": airport.upper()},
            sort=[("Arrival.Scheduled.Time", 1)],
        )
    )

    columns = ["Scheduled", "Actual", "Carrier", "Flight", "Status", "Origin"]
    data = []

    for x in arr_found:
        cols = []
        cols.append(x["Arrival"]["Scheduled"]["Time"])
        try:
            cols.append(x["Arrival"]["Actual"]["Time"])
        except KeyError:
            cols.append("")
        cols.append(x["OperatingCarrier"]["AirlineID"])
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])  # fmt: skip
        cols.append(x["Status"]["Description"])
        cols.append(x["Departure"]["AirportCode"])

        data.append(cols)

    df = pd.DataFrame(data, columns=columns)

    # close connection
    client.close()

    return df


def get_departures(airport: str) -> pd.DataFrame:
    """Get list of departures at given Airport"""

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    dep_found = list(
        col.find(
            filter={"Departure.AirportCode": airport.upper()},
            sort=[("Departure.Scheduled.Time", 1)],
        )
    )

    columns = [
        "Scheduled",
        "Actual",
        "Carrier",
        "Flight",
        "Status",
        "Destination",
    ]
    data = []
    for x in dep_found:
        cols = []
        cols.append(x["Departure"]["Scheduled"]["Time"])
        try:
            cols.append(x["Departure"]["Actual"]["Time"])
        except KeyError:
            cols.append("")
        cols.append(x["OperatingCarrier"]["AirlineID"])
        cols.append(x['OperatingCarrier']['AirlineID'] + x['OperatingCarrier']['FlightNumber'])  # fmt: skip
        cols.append(x["Status"]["Description"])
        cols.append(x["Arrival"]["AirportCode"])

        data.append(cols)

    df = pd.DataFrame(data, columns=columns)

    # close connection
    client.close()

    return df


def get_routes(dep: str, arr: str) -> pd.DataFrame:
    """Get list of routes between given departure and arrival airport"""

    # connecting collection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    # get routes from mongo collection
    filter = {
        "Departure.AirportCode": dep.upper(),
        "Arrival.AirportCode": arr.upper(),
    }
    routes = list(col.find(filter=filter))

    # format df columns
    columns = [
        "airline_name",
        "airline_iata",
        "flight",
        "dep_iata",
        "dep_airport",
        "dep_city",
        "dep_scheduled",
        "dep_actual",
        "arr_iata",
        "arr_airport",
        "arr_city",
        "arr_scheduled",
        "arr_ctual",
        "status",
    ]

    # create df
    data = []
    for x in routes:
        cols = []

        # flight
        airline_iata = x["OperatingCarrier"]["AirlineID"]
        airline_name = get_airline_from_iata(airline_iata)
        cols.append(airline_name)
        cols.append(airline_iata)
        cols.append(airline_iata + x["OperatingCarrier"]["FlightNumber"])

        # departure
        dep_iata = x["Departure"]["AirportCode"]
        dep_airport = get_airport_infos(dep_iata)[0]
        dep_city = get_airport_infos(dep_iata)[1]
        cols.append(dep_iata)
        cols.append(dep_airport)
        cols.append(dep_city)
        cols.append(x["Departure"]["Scheduled"]["Time"])
        try:
            cols.append(x["Departure"]["Actual"]["Time"])
        except KeyError:
            cols.append("")

        # arrival
        arr_iata = x["Arrival"]["AirportCode"]
        arr_airport = get_airport_infos(arr_iata)[0]
        arr_city = get_airport_infos(arr_iata)[1]
        cols.append(arr_iata)
        cols.append(arr_airport)
        cols.append(arr_city)
        cols.append(x["Arrival"]["Scheduled"]["Time"])
        try:
            cols.append(x["Arrival"]["Actual"]["Time"])
        except KeyError:
            cols.append("")

        # flight status
        cols.append(x["Status"]["Description"])

        # add line in df
        data.append(cols)

    df = pd.DataFrame(data=data, columns=columns)

    # close connection
    client.close()

    return df


def get_all_flights() -> pd.DataFrame:
    """get all flights in flights collection"""

    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.flights

    flights = list(col.find({}))

    columns = [
        "departure",
        "dep_iata",
        "dep_scheduled",
        "dep_actual",
        "terminal_gate",
        "arrival",
        "arr_iata",
        "arr_scheduled",
        "dep_actual",
        "terminal_gate",
        "carrier_code",
        "carrier",
        "flight",
        "status",
    ]
    data = []

    for x in flights:
        cols = []

        # departure
        try:
            cols.append(get_airport_infos(x["Departure"]["AirportCode"])[0])
        except IndexError:
            cols.append("")

        cols.append(x["Departure"]["AirportCode"])
        cols.append(x["Departure"]["Scheduled"]["Time"])

        try:
            cols.append(x["Departure"]["Actual"]["Time"])
        except KeyError:
            cols.append("")

        try:
            cols.append(
                f'{x["Departure"]["Terminal"]["Name"]}/{x["Departure"]["Terminal"]["Gate"]}'
            )
        except KeyError:
            cols.append("")

        # arrival
        try:
            cols.append(get_airport_infos(x["Arrival"]["AirportCode"])[0])
        except IndexError:
            cols.append("")
        cols.append(x["Arrival"]["AirportCode"])
        cols.append(x["Arrival"]["Scheduled"]["Time"])
        try:
            cols.append(x["Arrival"]["Actual"]["Time"])
        except KeyError:
            cols.append("")
        try:
            cols.append(
                x["Arrival"]["Terminal"]["Name"]
                + "/"
                + x["Arrival"]["Terminal"]["Gate"]
            )
        except KeyError:
            cols.append("")

        # general
        cols.append(x["OperatingCarrier"]["AirlineID"])
        cols.append(get_airline_from_iata(x["OperatingCarrier"]["AirlineID"]))
        cols.append(
            f'{x["OperatingCarrier"]["AirlineID"]}{x["OperatingCarrier"]["FlightNumber"]}'
        )
        cols.append(x["Status"]["Description"])

        data.append(cols)

    df = pd.DataFrame(data, columns=columns)
    df.to_csv(c.FLIGHTS_IN_DB_FILE, index=False)

    # close connection
    client.close()

    return df


def list_available_airports() -> pd.DataFrame:
    """get all airports available in the flights collection"""

    df = pd.read_csv(c.FLIGHTS_IN_DB_FILE)
    df1 = df[["dep_iata", "departure"]]
    df1.columns = ["iata", "airport"]
    df2 = df[["arr_iata", "arrival"]]
    df2.columns = ["iata", "airport"]
    df3 = pd.concat([df1, df2])

    airports = df3.drop_duplicates()
    airports.to_csv(c.AIRPORTS_IN_DB_FILE, index=False)

    return airports


def get_opensky_flights() -> Any:
    """get currently flying airplanes from opensky API"""

    # defining the spatial field
    lon_min, lat_min = -180.0, -90.0
    lon_max, lat_max = 180.0, 90.0

    # send request to get the current airplane data
    url_data = f"{c.OPENSKY_BASE_URL}?lamin={lat_min}&lomin={lon_min}&lamax={lat_max}&lomax={lon_max}"
    response = requests.get(url_data).json()

    update_position(response)

    return response


def get_opensky_df(response: Any) -> pd.DataFrame:
    """creates and returns dataframe from opensky response"""

    # load the data as a pandas dataframe
    columns = [
        "icao24",
        "callsign",
        "origin_country",
        "time_position",
        "last_contact",
        "long",
        "lat",
        "baro_altitude",
        "on_ground",
        "velocity",
        "true_track",
        "vertical_rate",
        "sensors",
        "geo_altitude",
        "squawk",
        "spi",
        "position_source",
    ]
    df = pd.DataFrame(response["states"], columns=columns)

    # filling missing data
    df.true_track = df.true_track.fillna(0)
    df = df.fillna("NaN")

    return df


def flight_tracker() -> tuple[pd.DataFrame, go.Figure]:
    """returns a map with all airplanes from opensky"""

    TOKEN = c.MAPBOX_API_TOKEN
    response = get_opensky_flights()
    df = get_opensky_df(response)

    # Define figure and its characteristics
    fig = go.Figure(
        go.Scattermapbox(
            lon=df.long,
            lat=df.lat,
            mode="markers",
            hoverinfo="none",
            marker={
                "size": 14,
                "symbol": "airport",
                "allowoverlap": True,
                "angle": df.true_track,
            },
        )
    )

    fig.update_layout(
        height=900,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox={"accesstoken": TOKEN, "style": "outdoors", "zoom": 1.9},
        showlegend=False,
        uirevision=True,
    )

    return df, fig


def get_altitudes(callsign: str) -> pd.DataFrame:
    """Get the list of altitudes for given airplane callsign"""

    # db connection
    client = MongoClient(c.MONGO_CONNECTION_STR)
    col = client.flightTracker.position

    # get the right callsign in collection
    filter = {"callsign": callsign}
    projection = {"_id": 0, "altitude": 1, "date_time": 1}
    result = col.find_one(filter=filter, projection=projection)
    altitude = result["altitude"] if result is not None else ""
    date_time = result["date_time"] if result is not None else ""

    df = pd.DataFrame(
        data=list(zip(date_time, altitude)),
        columns=["time", "altitude"],
    )

    return df
