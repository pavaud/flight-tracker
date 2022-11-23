from src.utils import *
import json

def test_get_key():
    """ Function must return the right key """

    assert get_key(API_KEY_FILE,'lufthansa') == 'vck7t48tns3fwmbnvvuy9dk4'


def test_update_position():
    """ Function must update present flight infos or create them """

    # db connection
    client = get_mongo_client()
    db = client.flightTracker

    # remove collection if exist for clean test
    db.position.drop()
    col = db.position

    # get test responses from file
    TEST_RESPONSES_FILE = os.path.realpath(os.path.join(os.path.dirname(__file__), 'opensky_responses.json'))
    with open(TEST_RESPONSES_FILE,'r') as f:
        responses = json.load(f)["responses"]    

    # test 1 : check first insertion
    update_position(responses[0])

    res = responses[0]["states"][0]
    filter = {"callsign":res[1]}
    flight = col.find_one(filter=filter)
    assert flight["callsign"] == res[1]
    assert flight["position"][0]["lat"] == res[6]
    assert flight["position"][0]["lon"] == res[5]
    assert flight["altitude"][0] == res[13]

    # test 2 : check that flight has second position and altitude
    # and another flight is appended
    update_position(responses[1])

    # check that flight has second position and altitude
    res = responses[1]["states"][0]
    filter = {"callsign":res[1]}
    flight = col.find_one(filter=filter)
    assert flight["callsign"] == res[1]
    assert flight["position"][1]["lat"] == res[6]
    assert flight["position"][1]["lon"] == res[5]
    assert flight["altitude"][1] == res[13]

    # check insertion when new flight and db already filled
    res = responses[1]["states"][1]
    filter = {"callsign":res[1]}
    flight = col.find_one(filter=filter)
    assert flight["callsign"] == res[1]
    assert flight["position"][0]["lat"] == res[6]
    assert flight["position"][0]["lon"] == res[5]
    assert flight["altitude"][0] == res[13]

    client.close()

