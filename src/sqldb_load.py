# third-party
import pandas as pd
from sqlalchemy import Table, Column, String, ForeignKey, MetaData, create_engine, text


# Creation d une base de donnee
engine = create_engine('sqlite:///codes.sqlite', echo=True)
meta = MetaData()


# CREATE TABLES

# drop all tables if they already exist
sql = text('DROP TABLE IF EXISTS City;')
result = engine.execute(sql)
sql = text('DROP TABLE IF EXISTS Airport;')
result = engine.execute(sql)
sql = text('DROP TABLE IF EXISTS Airline;')
result = engine.execute(sql)

# Table City
City = Table(
   'City', meta, 
   Column('city_iata', String(3), primary_key=True), 
   Column('city_name', String(40)),
   Column('country_name', String(40)),
)

# Table Airport
Airport = Table(
   'Airport', meta, 
   Column('airport_iata', String(3), primary_key=True),
   Column('airport_name', String(40)), 
   Column('city_iata', String(3), ForeignKey("City.city_iata")),
   Column('utc_offset', String(10)),
   Column('timezone_id', String(30)),
)

# Table Airline
Airline = Table(
   'Airline', meta, 
   Column('airline_iata', String(3), primary_key=True), 
   Column('airline_icao', String(3)), 
   Column('airline_name', String(40)),
)

# creation de toutes les tables
meta.create_all(engine)


# LOAD TABLES

# Importer CSV dans la Table Airport
df = pd.read_csv("https://ft-app.s3.eu-west-3.amazonaws.com/airports.csv")
df.to_sql('Airport', engine, if_exists='append', index=False, dtype={"airport_iata": String(), "airport_name": String(), "city_iata": String(), "utc_offset": String(), "timezone_id": String()})

# Importer CSV dans la Table City
df = pd.read_csv("https://ft-app.s3.eu-west-3.amazonaws.com/cities.csv")
df.to_sql('City', engine, if_exists='append', index=False, dtype={"city_iata": String(), "city_name": String(), "country_name": String()})

# Importer CSV dans la Table Airline
df = pd.read_csv("https://ft-app.s3.eu-west-3.amazonaws.com/airlines.csv")
df.to_sql('Airline', engine, if_exists='append', index=False, dtype={"airline_iata": String(), "airline_icao": String(), "airline_name": String()})


