import logging

import utils
import constants as c


def main():
    """
    Loop over the airports to get arrival and departure flights
    and insert them in the MongoDB `flights` collection
    """

    # Parse commandline arguments
    args = utils.init_args()

    # Logging config
    utils.init_log_conf(args.loglevel, c.CRON_LOG_PATH)

    # Update flight status
    try:
        utils.update_flight_status()
        logging.info("Update flight status")
    except Exception as e:
        logging.error(f"Error Update flight status. {e}")


if __name__ == "__main__":
    main()
