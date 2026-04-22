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

team1_id = events['team'].iloc[0]
team2_id = events['team'].iloc[1]

#events['cumulative_possesion_team1'] = events.apply(lambda row: row['duration'] if row['team'] == team1_id else 0, axis=1).cumsum()
#events['cumulative_possesion_team2'] = events.apply(lambda row: row ['duration'] if row['team'] == team2_id else 0, axis=1).cumsum()

"""def possession_at_timestamp(timestamp):
    up_to_t = events[events['match_seconds'] <= timestamp]
    if up_to_t.empty:
        return "No events up to timestamp"
    
    total_poss1 = up_to_t['cumulative_possesion_team1'].iloc[-1]
    total_poss2 = up_to_t['cumulative_possesion_team2'].iloc[-1]
    total_time = total_poss1 + total_poss2

    p1 = (total_poss1 / total_time) * 100 if total_time > 0 else 0
    p2 = (total_poss2 / total_time) * 100 if total_time > 0 else 0

    return {
        'timestamp': timestamp,
        f'{team1_id}_cumulative': total_poss1,
        f'{team2_id}_cumulative': total_poss2,
        f'{team1_id}_possession_%': round(p1 , 1),
        f'{team2_id}_possession_%': round(p2 , 1)
    }"""


#target_timestamp = 3600
#possession_info = possession_at_timestamp(target_timestamp)
#print(possession_info)

def cumulative_stats_at_timestamp(timestamp, stat_type):
    """
    stat_type: Exact values from events['type'].unique()
    Examples: 'Shot', 'Challenge', 'Foul Won', 'Corner'
    Run: print(events['type'].value_counts().head(10)) to see all
    """
    up_to_t = events[events['match_seconds'] <= timestamp]
    
    if up_to_t.empty:
        return {'error': 'No events up to timestamp'}
    
    stat_counts = up_to_t[up_to_t['type'] == stat_type].groupby('team').size()
    total_stats = stat_counts.sum()
    
    result = {
        'timestamp': timestamp,
        'stat_type': stat_type,
        f'{team1_id}_{stat_type.lower()}s': int(stat_counts.get(team1_id, 0)),
        f'{team2_id}_{stat_type.lower()}s': int(stat_counts.get(team2_id, 0)),
        'total': int(total_stats)
    }
    
    if total_stats > 0:
        percentages = (stat_counts / total_stats * 100).round(1)
        result[f'{team1_id}_pct'] = float(percentages.get(team1_id, 0))
        result[f'{team2_id}_pct'] = float(percentages.get(team2_id, 0))
    
    return result

print(cumulative_stats_at_timestamp(3600, 'Possesion'))
#match_slice = events[events['match_seconds'] <= target_timestamp]

#possesion_total = match_slice.groupby('team')['duration'].sum()
#total_time_elapsed = possesion_total.sum()
#possesion_percentage = (possesion_total / total_time_elapsed) * 100

#shots_total = match_slice[match_slice['type'] == 'Shot'].groupby('team').size()


#Interception_total = match_slice[match_slice['type'] == 'Interception'].groupby('team').size()



#Foul_won_total = match_slice[match_slice['type'] == 'Foul won'].groupby('team').size()


#Block_total = match_slice[match_slice['type'] == 'Block'].groupby('team').size()


#print(f"Goals found: {len(goals)}")
#if len(goals) > 0:
 #   print(goals[['team_name', 'player_name', 'minute']])


#print(f"Cumulative Possession Time up to {target_timestamp} seconds:")
#print(possesion_percentage)
#print(shots_total)
#print(Interception_total)
#print(Foul_won_total)
#print(Block_total)
#print("All event types:" , events ['type'].unique())
#print(events['type'].value_counts().head(20))
#print("Slice types:", match_slice['type'].unique())
#print(match_slice['type'].value_counts().head(20))

#print(events['period'].value_counts())
#print("Duration stats:", events['duration'].describe())
