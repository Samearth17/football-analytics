import pandas as pd
import datetime 
import psycopg2
from statsbombpy import sb

conn = psycopg2.connect(
    host="localhost",
    database="football_analytics",
    user="postgres",
    password="Samarth30"
)
events = sb.events(match_id=7585 , flatten_attrs=True)
events['timestamp_dt'] = pd.to_datetime(events['timestamp'])
events['seconds_in_period'] = (events['timestamp_dt'].dt.hour * 3600 + events['timestamp_dt'].dt.minute * 60 + events['timestamp_dt'].dt.second)

events['match_seconds'] = events['seconds_in_period']
events.loc[events['period'] == 2 , 'match_seconds'] += 2700

events = events.sort_values('match_seconds')
events['duration'] = events['match_seconds'].shift(-1) - events['match_seconds']
events['duration'] = events['duration'].fillna(0)

teams = events[events['team'].notna()]['team'].unique()[:2]
team1_id = teams[0]
team2_id = teams[1]
print(f"Team1: {team1_id}, Team2: {team2_id}")

events['cumulative_possesion_team1'] = events.apply(lambda row: row['duration'] if row['team'] == team1_id else 0, axis=1).cumsum()
events['cumulative_possesion_team2'] = events.apply(lambda row: row['duration'] if row['team'] == team2_id else 0, axis=1).cumsum()

def possession_at_timestamp(timestamp):
    up_to_t = events[events['match_seconds'] <= timestamp]
    if up_to_t.empty:
        return {'error': 'No events up to timestamp'}
    
    poss1 = up_to_t[up_to_t['team'] == team1_id]['duration'].sum()
    poss2 = up_to_t[up_to_t['team'] == team2_id]['duration'].sum()
    total_time = poss1 + poss2
    
    p1 = (poss1 / total_time) * 100 if total_time > 0 else 0
    p2 = (poss2 / total_time) * 100 if total_time > 0 else 0
    
    return {
        'timestamp': timestamp,
        f'{team1_id}_cumulative': poss1,
        f'{team2_id}_cumulative': poss2,
        f'{team1_id}_possession_%': round(p1 , 1),
        f'{team2_id}_possession_%': round(p2 , 1)
    }


target_timestamp = 3600
possession_info = possession_at_timestamp(target_timestamp)
print(possession_info) 

def cumulative_stats_at_timestamp(timestamp, stat_type):
    
    up_to_t = events[events['match_seconds'] <= timestamp]
    
    if up_to_t.empty:
        return {'error': 'No events up to timestamp'}
    
    stat_counts = up_to_t[up_to_t['type'] == stat_type].groupby('team').size()
    total_stats = stat_counts.sum()
    
    result = {
        'timestamp': timestamp,
        'stat_type': stat_type,
        f'{team1_id}_{stat_type}s': int(stat_counts.get(team1_id, 0)),
        f'{team2_id}_{stat_type}s': int(stat_counts.get(team2_id, 0)),
        'total': int(total_stats)
    }
    
    if total_stats > 0:
        percentages = (stat_counts / total_stats * 100).round(1)
        result[f'{team1_id}_pct'] = float(percentages.get(team1_id, 0))
        result[f'{team2_id}_pct'] = float(percentages.get(team2_id, 0))
    
    return result
print(cumulative_stats_at_timestamp (4500 ,'Block'))



