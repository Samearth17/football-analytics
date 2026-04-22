import datetime
import pandas as pd
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns
from statsbombpy import sb

def load_events(match_id):
    events = sb.events(match_id=match_id, flatten_attrs=True)
    return events

def pre_events(events):
    events['timestamp_dt'] = pd.to_datetime(events['timestamp'])
    events['seconds_in_period'] = (
        events['timestamp_dt'].dt.hour * 3600 + events['timestamp_dt'].dt.minute * 60 + events['timestamp_dt'].dt.second
    )
    events['match_seconds'] = events['seconds_in_period']
    events.loc[events['period'] == 2, 'match_seconds'] += 2700

    events = events.sort_values('match_seconds')

    events['duration'] = events['match_seconds'].shift(-1) - events['match_seconds']
    events['duration'] = events['duration'].fillna(0)
    return events

def generate_heatmap(start_time, end_time):
    try:
        events = pre_events(sb.events(match_id=7585, flatten_attrs=True))
        duration_events = events[
            (events['match_seconds'] >= start_time) & 
            (events['match_seconds'] < end_time)
        ]
        
        heatmap_events = duration_events[duration_events['type'].isin(['Pass', 'Shot', 'Carry'])]
        
        if heatmap_events.empty:
            return None
        
        locations = heatmap_events['location'].dropna()
        if locations.empty:
            return None
        
        x = []
        y = []
        for loc in locations:
            if isinstance(loc, list) and len(loc) == 2:
                x.append(loc[0])
                y.append(loc[1])
        
        if len(x) < 3:
            return None
        
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#3d7c25', line_color='white')
        fig, ax = pitch.draw(figsize=(12, 8))
        
        sns.kdeplot(x=pd.Series(x), y=pd.Series(y), fill=True, thresh=0.1, levels=15, cmap='Reds', alpha=0.7, ax=ax)
        
        plt.title(f'Heatmap {start_time//60}\'-{end_time//60}\' Match 7585', pad=20)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='white')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return img_b64
    except Exception as e:
        print(f'Heatmap error: {e}')
        return None

def generate_pass_network(start_time, end_time):
    try:
        events = pre_events(sb.events(match_id=7585, flatten_attrs=True))
        duration_events = events[
            (events['match_seconds'] >= start_time) & 
            (events['match_seconds'] < end_time)
        ]
        
        pass_events = duration_events[duration_events['type'] == 'Pass'].copy()
        if pass_events.empty:
            print('No pass events found')
            return None
        
        # Ultra-safe coordinate extraction
        def extract_coords(loc):
            try:
                if isinstance(loc, list) and len(loc) == 2 and all(isinstance(c, (int, float)) for c in loc):
                    return [float(loc[0]), float(loc[1])]
                return [None, None]
            except:
                return [None, None]
        
        loc_data = pass_events['location'].apply(extract_coords).tolist()
        end_loc_data = pass_events['pass_end_location'].apply(extract_coords).tolist()
        
        pass_events['x'] = pd.Series([d[0] for d in loc_data])
        pass_events['y'] = pd.Series([d[1] for d in loc_data])
        pass_events['end_x'] = pd.Series([d[0] for d in end_loc_data])
        pass_events['end_y'] = pd.Series([d[1] for d in end_loc_data])
        
        # Clean data
        pass_events = pass_events.dropna(subset=['x', 'y', 'end_x', 'end_y'])
        
        if pass_events.empty:
            print('No valid pass coordinates')
            return None
        
        print(f'Processing {len(pass_events)} valid passes')
        
        # Zone function
        def get_zone(x, y):
            if pd.isna(x) or pd.isna(y):
                return -1
            zone_x = min(int(x * 10 / 120), 9)
            zone_y = min(int(y * 7 / 80), 6)
            return zone_x + zone_y * 10
        
        pass_events['from_zone'] = pass_events[['x', 'y']].apply(lambda row: get_zone(row['x'], row['y']), axis=1)
        pass_events['to_zone'] = pass_events[['end_x', 'end_y']].apply(lambda row: get_zone(row['end_x'], row['end_y']), axis=1)
        
        pass_events = pass_events[pass_events['from_zone'] >= 0]
        pass_events = pass_events[pass_events['to_zone'] >= 0]
        
        if pass_events.empty:
            print('No valid zones')
            return None
        
        # FIXED: Use iterrows for safe unpacking
        pass_matrix = pd.DataFrame(0, index=range(70), columns=range(70))
        for idx, row in pass_events.iterrows():
            i = int(row['from_zone'])
            j = int(row['to_zone'])
            if 0 <= i < 70 and 0 <= j < 70:
                pass_matrix.at[i, j] += 1
        
        matrix = pass_matrix[pass_matrix.sum(axis=1) > 0][pass_matrix.sum(axis=0) > 0]
        
        if matrix.empty:
            print('Empty matrix')
            return None
        
        # Plot
        pitch = Pitch(pitch_type='statsbomb', pitch_color='#3d7c25', line_color='white')
        fig, ax = pitch.draw(figsize=(10, 7))
        
        for i in matrix.index:
            for j in matrix.columns:
                value = matrix.at[i, j]
                if value > 2:
                    x1 = (i % 10) * 12
                    y1 = (i // 10) * (80/7)
                    x2 = (j % 10) * 12
                    y2 = (j // 10) * (80/7)
                    alpha = min(value / 15.0, 0.8)
                    lw = min(value / 5.0, 8)
                    pitch.arrows(x1, y1, x2, y2, ax=ax, color='blue', alpha=alpha, lw=lw)
        
        plt.title(f'Pass Network {start_time//60}\'-{end_time//60}\' ({pass_events.shape[0]} passes)')
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='white', pad_inches=0.1)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        
        print(f'Generated pass network with {pass_events.shape[0]} passes')
        return img_b64
        
    except Exception as e:
        print(f'Pass network error: {e}')
        import traceback
        traceback.print_exc()
        return None

def stats_between(events=None, start_time=0, end_time=5400, team1=None, team2=None):
    events_full = pre_events(sb.events(match_id=7585, flatten_attrs=True))
    teams = events_full[events_full['team'].notna()]['team'].unique()[:2]
    team1_name = str(teams[0]) if len(teams) > 0 else 'Team1'
    team2_name = str(teams[1]) if len(teams) > 1 else 'Team2'
    
    duration = events_full[(events_full['match_seconds'] >= start_time) & (events_full['match_seconds'] < end_time)]
    if duration.empty:
        return {'error': 'No data', 'heatmap_b64': None, 'pass_network_b64': None}

    result = {'start_time': start_time, 'end_time': end_time}

    poss1 = duration[duration['team'] == team1_name]['duration'].sum()
    poss2 = duration[duration['team'] == team2_name]['duration'].sum()
    total_poss = poss1 + poss2
    result['possession'] = {
        team1_name: round((poss1 / total_poss * 100), 1) if total_poss > 0 else 0,
        team2_name: round((poss2 / total_poss * 100), 1) if total_poss > 0 else 0
    }

    shots = duration[duration['type'] == 'Shot'].groupby('team').size()
    result['shots'] = {team1_name: int(shots.get(team1_name, 0)), team2_name: int(shots.get(team2_name, 0))}

    passes = duration[duration['type'] == 'Pass']
    pass_count = passes.groupby('team').size()
    succ_pass_count = passes[passes['pass_outcome'].isna()].groupby('team').size()
    result['passes'] = {team1_name: int(pass_count.get(team1_name, 0)), team2_name: int(pass_count.get(team2_name, 0))}
    result['pass_accuracy'] = {
        team1_name: round((succ_pass_count.get(team1_name, 0) / pass_count.get(team1_name, 0) * 100), 1) if pass_count.get(team1_name, 0) > 0 else 0,
        team2_name: round((succ_pass_count.get(team2_name, 0) / pass_count.get(team2_name, 0) * 100), 1) if pass_count.get(team2_name, 0) > 0 else 0
    }

    fouls = duration[duration['type'] == 'Foul Committed'].groupby('team').size()
    result['fouls'] = {team1_name: int(fouls.get(team1_name, 0)), team2_name: int(fouls.get(team2_name, 0))}

    cards = duration[(duration['bad_behaviour_card'].notna()) | (duration['foul_committed_card'].notna())]
    yellow = cards[(cards['bad_behaviour_card'] == 'Yellow Card') | (cards['foul_committed_card'] == 'Yellow Card')].groupby('team').size()
    red = cards[(cards['bad_behaviour_card'] == 'Red Card') | (cards['foul_committed_card'] == 'Red Card')].groupby('team').size()
    result['yellow_cards'] = {team1_name: int(yellow.get(team1_name, 0)), team2_name: int(yellow.get(team2_name, 0))}
    result['red_cards'] = {team1_name: int(red.get(team1_name, 0)), team2_name: int(red.get(team2_name, 0))}

    offsides = duration[(duration['type'] == 'Offside') | (duration['pass_outcome'] == 'Offside')].groupby('team').size()
    result['offsides'] = {team1_name: int(offsides.get(team1_name, 0)), team2_name: int(offsides.get(team2_name, 0))}

    corners = passes[passes['pass_type'] == 'Corner'].groupby('team').size()
    result['corners'] = {team1_name: int(corners.get(team1_name, 0)), team2_name: int(corners.get(team2_name, 0))}

    goals = duration[duration['type'] == 'Goal'].groupby('team').size()
    result['goals'] = {team1_name: int(goals.get(team1_name, 0)), team2_name: int(goals.get(team2_name, 0))}

    result['heatmap_b64'] = generate_heatmap(start_time, end_time)
    result['pass_network_b64'] = generate_pass_network(start_time, end_time)
    
    return result
