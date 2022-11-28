FROM debian:latest

RUN apt-get update && apt-get install python3-pip -y

# add source files to working directory
WORKDIR /home/
ADD src/assets ${WORKDIR}src/assets/
ADD src/app.py src/utils.py \
    src/sqldb_requests.py \
    src/sqldb_load.py \
    ${WORKDIR}src/
ADD api_keys.txt requirements.txt $WORKDIR

# install required librairies
RUN pip3 install -r requirements.txt

# make app available from outside of container
EXPOSE 8050

# Load SQL db, flights mongodb collection and start app
WORKDIR /home/src/
RUN python3 sqldb_load.py
CMD python3 app.py