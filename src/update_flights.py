# third-party
from pymongo import MongoClient
# project
from utils import *


def main():

    # update all flights in collection flights
    update_flights()

if __name__ == "__main__":
    main()