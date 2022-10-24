from  src.utils import *

def test_get_key():
    """ Function must return the right key """

    assert get_key(API_KEY_FILE,'lufthansa') == 'p8jvtk36gwcxnx2p2brc9rpw'

"""    with pytest.raises(IndexError) as idxErr:
        get_key(FILE,'Lufty')
    assert "out of range" in str(idxErr.value)"""

def test_insert_arrivals():
    pass

def test_insert_departures():
    pass

def test_remove_old_schedules():
    pass

def test_get_schedules():
    pass