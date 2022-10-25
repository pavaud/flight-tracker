# project
from utils import *


def main():

    # update all schedules and remove old schedules
    remove_old_schedules(days=7)
    update_schedules()

if __name__ == "__main__":
    main()