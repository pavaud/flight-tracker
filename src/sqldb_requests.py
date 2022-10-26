# third-party
from sqlalchemy import text
from sqlalchemy.exc import MultipleResultsFound, NoResultFound


def get_airport_infos(engine, airport_iata):
    """ 
    Get the name, city and country for given airport IATA code 

    Parameters:
    -----------
    engine      : engine connection with the database
    airport_iata: airport IATA code (3-letters)

    Returns :
    ---------
    result      : tuple with airport_name, city_name, country_name
    """

    with engine.connect() as conn:
        query = text("SELECT airport_name,city_name, country_name "
                     "FROM Airport JOIN City ON Airport.city_iata=City.city_iata "
                     "WHERE airport_iata = \"" + airport_iata.upper() + "\";")
        results = conn.execute(query)

        try:
            result = results.one()
        except MultipleResultsFound:
            print('Many results returned. Should be only one')
        except NoResultFound:
            print('No results returned')
            result = ""
            
        return result


def get_airline_from_iata(engine, airline_iata):
    """ 
    Get the name for given airline IATA code 

    Parameters:
    -----------
    engine      : engine connection with the database
    airline_iata: airline IATA code (2-letters)

    Returns :
    ---------
    result      : tuple with airline_name
    """

    with engine.connect() as conn:
        query = text("SELECT airline_name "
                     "FROM Airline "
                     "WHERE airline_iata = \"" + airline_iata.upper() + "\";")
        results = conn.execute(query)

        try:
            result = results.one()
        except MultipleResultsFound:
            print('Many results returned. Should be only one')
        except NoResultFound:
            print('No results returned')
            result = ""
            
        return result


def get_airline_from_icao(engine, airline_icao):
    """ 
    Get the name for given airline ICAO code 

    Parameters:
    -----------
    engine      : engine connection with the database
    airline_icao: airline ICAO code (-letters)

    Returns :
    ---------
    result      : tuple with airline_name
    """

    with engine.connect() as conn:
        query = text("SELECT airline_name "
                     "FROM Airline "
                     "WHERE airline_icao = \"" + airline_icao.upper() + "\";")
        results = conn.execute(query)

        try:
            result = results.one()
        except MultipleResultsFound:
            print('Many results returned. Should be only one')
        except NoResultFound:
            print('No results returned')
            result = ""
            
        return result
