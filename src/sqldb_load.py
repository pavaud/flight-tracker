import pandas as pd
from sqlalchemy import (
    Table,
    Column,
    String,
    ForeignKey,
    MetaData,
    create_engine,
    text,
)

import constants as c

# SQLite database creation
engine = create_engine(c.SQL_ALCHEMY_ENGINE, echo=True)
meta = MetaData()

# CREATE TABLES

# drop all tables if they already exist
with engine.begin() as conn:
    result = conn.execute(text("DROP TABLE IF EXISTS City;"))
    result = conn.execute(text("DROP TABLE IF EXISTS Airport;"))
    result = conn.execute(text("DROP TABLE IF EXISTS Airline;"))

# Table City
City = Table(
    "City",
    meta,
    Column("city_iata", String(3), primary_key=True),
    Column("city_name", String(40)),
    Column("country_name", String(40)),
)

# Table Airport
Airport = Table(
    "Airport",
    meta,
    Column("airport_iata", String(3), primary_key=True),
    Column("airport_name", String(40)),
    Column("city_iata", String(3), ForeignKey("City.city_iata")),
    Column("utc_offset", String(10)),
    Column("timezone_id", String(30)),
)

# Table Airline
Airline = Table(
    "Airline",
    meta,
    Column("airline_iata", String(3), primary_key=True),
    Column("airline_icao", String(3)),
    Column("airline_name", String(40)),
)

# Create all tables
meta.create_all(engine)


# LOAD TABLES

# Import CSV in Airport table
df = pd.read_csv(c.AIRPORTS_FILE)
df.to_sql(
    "Airport",
    engine,
    if_exists="append",
    index=False,
    dtype={
        "airport_iata": String(),
        "airport_name": String(),
        "city_iata": String(),
        "utc_offset": String(),
        "timezone_id": String(),
    },
)

# Import CSV in City table
df = pd.read_csv(c.CITIES_FILE)
df.to_sql(
    "City",
    engine,
    if_exists="append",
    index=False,
    dtype={
        "city_iata": String(),
        "city_name": String(),
        "country_name": String(),
    },
)

# Import CSV in Airline table
df = pd.read_csv(c.AIRLINES_FILE)
df.to_sql(
    "Airline",
    engine,
    if_exists="append",
    index=False,
    dtype={
        "airline_iata": String(),
        "airline_icao": String(),
        "airline_name": String(),
    },
)
