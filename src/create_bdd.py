# %% [markdown]
# # **CREATION DES TABLES**

# %%
#Importation librarie
import sqlite3, sqlalchemy, csv
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, CHAR, Float, VARCHAR,Time, ForeignKey, MetaData, create_engine, text, inspect

#Creation d une base de donnee
engine = create_engine('sqlite:///DST.db', echo=True)
meta = MetaData()

#Table City
City = Table(
   'City', meta, 
   Column('city_iata', CHAR(3), primary_key=True), 
   Column('city_name', String),
   Column('country_name', String),
)

#Table Airport
Airport = Table(
   'Airport', meta, 
   Column('airport_iata', CHAR(3), primary_key=True),
   Column('airport_name', String), 
   Column('city_iata', CHAR(3), ForeignKey("City.city_iata")),
   Column('utc_offset', String),
   Column('timezone_id', String),

)

meta.create_all(engine)

#Table Airline
Airline = Table(
   'Airline', meta, 
   Column('airline_iata', VARCHAR(3), primary_key=True), 
   Column('airline_icao', CHAR(3)), 
   Column('airline_name', String),
)

meta.create_all(engine)

# %% [markdown]
# # **VERIFICATION EXISTANCE DES TABLES**
# 

# %%
inspector = inspect(engine)
inspector.get_table_names()

# %% [markdown]
# # **DETAILS DE LA TABLE AIRPORT**

# %%
inspector.get_columns(table_name='Airport')

# %% [markdown]
# # **Suppression de la TABLE AIRPORT**

# %%
sql = text('DROP TABLE IF EXISTS Airline;')
result = engine.execute(sql)

# %% [markdown]
# # **Afficher csv dataFrame**

# %%
data= pd.read_csv("airports.csv")
data

# %%
data= pd.read_csv("cities.csv")
data

# %%
data= pd.read_csv("airlines.csv")
data

# %% [markdown]
# # **Importer CSV dans la Table Airport**

# %%
conn = sqlite3.connect('DST')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS AIRPORT (airport_iata,airport_name,city_iata,utc_offset,timezone_id)')
conn.commit()

df = pd.read_csv("airports.csv")

df.to_sql('Airport', engine, if_exists='append', index=False, dtype={"airport_iata": CHAR(), "airport_name": String(), "city_iata": CHAR(), "utc_offset": String(), "timezone_id": String()})


# %% [markdown]
# # **Importer CSV dans la Table City**

# %%
conn = sqlite3.connect('DST')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS CITY (city_iata,city_name,country_name)')
conn.commit()

df = pd.read_csv("cities.csv")

df.to_sql('City', engine, if_exists='append', index=False, dtype={"city_iata": CHAR(), "city_name": String(), "country_name": String()})


# %% [markdown]
# # **Importer CSV dans la Table Airline

# %%
conn = sqlite3.connect('DST')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS AIRPORT (airport_iata,airport_icao,airline_name)')
conn.commit()

df = pd.read_csv("airlines.csv")

df.to_sql('Airline', engine, if_exists='append', index=False, dtype={"airport_iata": VARCHAR(), "airport_icao": CHAR(), "airline_name": String()})


# %% [markdown]
# #REQUETE --- ELEMENTS DANS LA BASE

# %%
conn = engine.connect()
data = text("SELECT * FROM Airport LIMIT 5;")
result = conn.execute(data)
result.fetchall() 

# %%
conn = engine.connect()
data = text("SELECT * FROM City LIMIT 5;")
result = conn.execute(data)
result.fetchall() 

# %%
conn = engine.connect()
data = text("SELECT * FROM Airline LIMIT 5;")
result = conn.execute(data)
result.fetchall() 