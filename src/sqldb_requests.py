# third-party
from sqlalchemy import create_engine, text
from sqlalchemy.exc import MultipleResultsFound, NoResultFound


SQL_ALCHEMY_ENGINE = 'sqlite:///codes.sqlite'

def get_airport_infos(airport_iata):
    """ 
    Get the name, city and country for given airport IATA code 

    Parameters:
    -----------
    airport_iata: airport IATA code (3-letters)

    Returns :
    ---------
    result      : tuple with airport_name, city_name, country_name
    """
    
    engine = create_engine(SQL_ALCHEMY_ENGINE, echo=True)

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


def get_airline_from_iata(airline_iata):
    """ 
    Get the name for given airline IATA code 

    Parameters:
    -----------
    airline_iata: airline IATA code (2-letters)

    Returns :
    ---------
    result      : tuple with airline_name
    """

    engine = create_engine(SQL_ALCHEMY_ENGINE, echo=True)

    with engine.connect() as conn:
        query = text("SELECT airline_name "
                     "FROM Airline "
                     "WHERE airline_iata = \"" + airline_iata.upper() + "\";")
        results = conn.execute(query)

        try:
            result = results.one()[0]
        except MultipleResultsFound:
            print('Many results returned. Should be only one')
        except NoResultFound:
            print('No results returned')
            result = ""
            
        return result


def get_airline_from_icao(airline_icao):
    """ 
    Get the name for given airline ICAO code 

    Parameters:
    -----------
    airline_icao: airline ICAO code (-letters)

    Returns :
    ---------
    result      : tuple with airline_name
    """
    
    engine = create_engine(SQL_ALCHEMY_ENGINE, echo=True)

    with engine.connect() as conn:
        query = text("SELECT airline_name "
                     "FROM Airline "
                     "WHERE airline_icao = \"" + airline_icao.upper() + "\";")
        results = conn.execute(query)

        try:
            result = results.one()[0]
        except MultipleResultsFound:
            print('Many results returned. Should be only one')
        except NoResultFound:
            print('No results returned')
            result = ""
            
        return result
