# project
from utils import update_flight_status


def main():
    """
    Loop over the airports to get arrival and departure flights
    and insert them in the MongoDB flights collection
    """
    
    update_flight_status()

if __name__ == "__main__":
    main()