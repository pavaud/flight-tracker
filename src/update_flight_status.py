from datetime import datetime as dt

from utils import update_flight_status


def main():
    """
    Loop over the airports to get arrival and departure flights
    and insert them in the MongoDB flights collection
    """
    with open("/home/src/log/cron.log", "a") as f:
        try:
            update_flight_status()
            f.write(f"UPDATE: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        except Exception as e:
            f.write(f"ERROR: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n{e}\n")


if __name__ == "__main__":
    main()
