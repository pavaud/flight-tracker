from sqlalchemy import create_engine, text
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

import constants as c


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

    engine = create_engine(c.SQL_ALCHEMY_ENGINE, echo=False)

    with engine.connect() as conn:
        query = text(
            "SELECT airport_name,city_name, country_name "
            "FROM Airport JOIN City ON Airport.city_iata=City.city_iata "
            f'WHERE airport_iata = "{airport_iata.upper()}";'
        )

        try:
            results = conn.execute(query)
            result = results.one() if results is not None else ""
        except MultipleResultsFound:
            print("Many results returned. Should be only one")
            result = ""
        except NoResultFound:
            print("No results returned")
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
    result      : airline_name
    """

    engine = create_engine(c.SQL_ALCHEMY_ENGINE, echo=False)

    with engine.connect() as conn:
        query = text(
            "SELECT airline_name "
            "FROM Airline "
            f'WHERE airline_iata = "{airline_iata.upper()}";'
        )

        try:
            results = conn.execute(query)
            result = results.one()[0] if results is not None else ""
        except MultipleResultsFound:
            print("Many results returned. Should be only one")
            result = ""
        except NoResultFound:
            print("No results returned")
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
    result      : airline_name
    """

    engine = create_engine(c.SQL_ALCHEMY_ENGINE, echo=False)

    with engine.connect() as conn:
        query = text(
            "SELECT airline_name "
            "FROM Airline "
            f'WHERE airline_icao = "{airline_icao.upper()}";'
        )

        try:
            results = conn.execute(query)
            result = results.one()[0] if results is not None else ""
        except MultipleResultsFound:
            print("Many results returned. Should be only one")
            result = ""
        except NoResultFound:
            print("No results returned")
            result = ""

        return result
