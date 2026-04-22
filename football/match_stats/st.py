from statsbombpy import sb
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="football_analytics",
    user="postgres",
    password="Samarth30"
)
events = sb.events(match_id=7585 , flatten_attrs=True)
if 'location'in events.columns:
    location_df = events['location'].apply(pd.Series)

    num_cols = location_df.shape[1]
    location_df.columns = [f'location_{i+1}' for i in range(num_cols)]
    events = pd.concat([events, location_df], axis=1)
    events = events.drop(columns=['location'])

for col in events.columns:
    if events[col].apply(lambda x: isinstance(x, (list,dict))).any():
        events[col] = events[col].astype(str)

engine = create_engine('postgresql://postgres:Samarth30@localhost:5432/football_analytics')
events.to_sql('match_events', engine, if_exists='replace', index=False)

print("Data inserted successfully into the database.")
