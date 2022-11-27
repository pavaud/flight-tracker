FROM debian:latest

RUN apt-get update && apt-get install python3-pip -y \
    && apt-get -y install cron

# add source files to working directory
WORKDIR /home/
ADD src/assets ${WORKDIR}src/assets/
ADD src/app.py src/utils.py src/sqldb_requests.py src/sqldb_load.py ${WORKDIR}src/
ADD api_keys.txt requirements.txt $WORKDIR
ADD data/airports_valid_for_update.csv ${WORKDIR}data/

# install required librairies
RUN pip3 install -r requirements.txt

# Add crontab file in the cron directory and change permissions
ADD crontab /etc/cron.d/flight_cron
RUN chmod 0644 /etc/cron.d/flight_cron

# make app available from outside container
EXPOSE 8050

# Load SQL db, flights mongodb collection and start app
WORKDIR /home/src/
RUN python3 sqldb_load.py
RUN cron
CMD python3 app.py