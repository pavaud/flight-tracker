from sqlalchemy import create_engine
from src.sqldb_requests import *


def test_get_airport_infos():
    """ Must return name, city and country for given airport IATA code """

    assert get_airport_infos('CDG') == ('Paris/ Ch.de Gaulle','Paris','France')
    assert get_airport_infos('cdg') == ('Paris/ Ch.de Gaulle','Paris','France')
    assert get_airport_infos('CDGX') == ""
    assert get_airport_infos('CD') == ""
    assert get_airport_infos('') == ""

def test_get_airline_from_iata():
    """ Must return name for given airline IATA code """

    assert get_airline_from_iata('LH') == 'Lufthansa'
    assert get_airline_from_iata('OS') == 'Austrian'
    assert get_airline_from_iata('os') == 'Austrian'
    assert get_airline_from_iata('LHX') == ""
    assert get_airline_from_iata('L') == ""
    assert get_airline_from_iata('') == ""

def test_get_airline_from_icao():
    """ Must return name for given airline ICAO code """

    assert get_airline_from_icao('DLH') == 'Lufthansa'
    assert get_airline_from_icao('AUA') == 'Austrian'
    assert get_airline_from_icao('aua') == 'Austrian'
    assert get_airline_from_icao('DLHX') == ""
    assert get_airline_from_icao('LH') == ""
    assert get_airline_from_icao('') == ""
       
