FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y

WORKDIR /home/
ADD src/assets ${WORKDIR}src/assets/
ADD src/app.py src/utils.py src/sqldb_requests.py src/sqldb_load.py ${WORKDIR}src/
ADD api_keys.txt requirements.txt $WORKDIR
ADD data/airports_valid_for_update.csv ${WORKDIR}data/

ENV DASH_DEBUG_MODE False
EXPOSE 8050
RUN pip3 install -r requirements.txt

WORKDIR /home/src/
RUN python3 sqldb_load.py
CMD python3 app.py