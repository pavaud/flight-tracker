FROM ubuntu:latest

RUN apt-get update && \
    apt-get install python3-pip -y && \
    apt-get install cron -y

# add source files to working directory
WORKDIR /home/
RUN mkdir -p ${WORKDIR}src/log
ADD src/utils.py \
    src/sqldb_requests.py \
    src/update_flight_status.py \
    ${WORKDIR}src/
ADD api_keys.txt requirements.txt $WORKDIR
ADD data/airports_valid_for_update.csv ${WORKDIR}data/

# install required librairies
RUN pip3 install -r requirements.txt

# append following cron command to /etc/crontab
RUN echo "* * * * * root /usr/bin/python3 /home/src/update_flight_status.py" >> /etc/crontab \
    && echo "" >> /etc/crontab

# add environment for cron
CMD env >> /etc/environment && cron -f