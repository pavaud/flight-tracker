FROM debian:latest
RUN apt-get update && apt-get install python3-pip -y

WORKDIR /home
ADD assets $WORKDIR/assets/
ADD src/app.py utils.py sqldb_requests.py $WORKDIR/src/
ADD api_keys.txt requirements.txt $WORKDIR/
ADD airports_valid_for_update.csv $WORKDIR/data/

ENV DASH_DEBUG_MODE False
EXPOSE 8050
RUN pip3 install -r requirements.txt
CMD ["gunicorn", "--workers=4", "-b", "0.0.0.0:8050", "--reload", "app:server"]