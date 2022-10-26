from sqlalchemy import create_engine, text
from sqlalchemy.exc import MultipleResultsFound
from  src.sqldb_requests import *


def test_get_airport_infos():
    """ Must return name, city and country for given airport IATA code """

    engine = create_engine('sqlite:///codes.sqlite', echo=True)
    assert get_airport_infos(engine, 'CDG') == ('Paris/ Ch.de Gaulle','Paris','France')
    assert get_airport_infos(engine, 'cdg') == ('Paris/ Ch.de Gaulle','Paris','France')
    assert get_airport_infos(engine, 'CDGX') == ""
    assert get_airport_infos(engine, 'CD') == ""
    assert get_airport_infos(engine, '') == ""

def test_get_airline_from_iata():
    """ Must return name for given airline IATA code """

    engine = create_engine('sqlite:///codes.sqlite', echo=True)
    assert get_airline_from_iata(engine, 'LH') == ('Lufthansa',)
    assert get_airline_from_iata(engine, 'OS') == ('Austrian',)
    assert get_airline_from_iata(engine, 'os') == ('Austrian',)
    assert get_airline_from_iata(engine, 'LHX') == ""
    assert get_airline_from_iata(engine, 'L') == ""
    assert get_airline_from_iata(engine, '') == ""

def test_get_airline_from_icao():
    """ Must return name for given airline ICAO code """

    engine = create_engine('sqlite:///codes.sqlite', echo=True)
    assert get_airline_from_icao(engine, 'DLH') == ('Lufthansa',)
    assert get_airline_from_icao(engine, 'AUA') == ('Austrian',)
    assert get_airline_from_icao(engine, 'aua') == ('Austrian',)
    assert get_airline_from_icao(engine, 'DLHX') == ""
    assert get_airline_from_icao(engine, 'LH') == ""
    assert get_airline_from_icao(engine, '') == ""
       
