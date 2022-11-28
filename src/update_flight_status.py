# project
from utils import update_flight_status
from datetime import datetime

def main():
    """
    Loop over the airports to get arrival and departure flights
    and insert them in the MongoDB flights collection
    """

    update_flight_status()

    with open('/home/src/log/cron.log','a') as f:
        f.write("Update: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("\n")
    
if __name__ == "__main__":
    main()