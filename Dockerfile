FROM debian:latest

RUN apt-get update && apt-get install -y python3-pip

# add source files to working directory
WORKDIR /home/
ADD data ${WORKDIR}data/
ADD src/assets ${WORKDIR}src/assets/
ADD src/app.py \
    src/utils.py \
    src/sqldb_requests.py \
    src/constants.py \
    src/sqldb_load.py \
    ${WORKDIR}src/
ADD .env.prod requirements.txt $WORKDIR
RUN mv .env.prod .env

# install required librairies
RUN pip3 install -r requirements.txt --break-system-packages

# make app available from outside of container
EXPOSE 8050

# Load SQL db, flights mongodb collection and start app
RUN python3 ./src/sqldb_load.py
CMD python3 ./src/app.py
