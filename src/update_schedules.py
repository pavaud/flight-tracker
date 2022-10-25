# standard
import time
from datetime import datetime, timedelta
# third-party
from pymongo import MongoClient
# project
from utils import *


def main():


    remove_old_schedules(days=7)
    update_schedules()

if __name__ == "__main__":
    main()