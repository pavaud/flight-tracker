from datetime import datetime

from utils import update_flight_status


def main():
    """
    Loop over the airports to get arrival and departure flights
    and insert them in the MongoDB flights collection
    """

    update_flight_status()

    with open("/home/src/log/cron.log", "a") as f:
        f.write(f"Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
