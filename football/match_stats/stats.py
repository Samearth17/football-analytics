import random
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="football_analytics",
    user="postgres",
    password="Samarth30"
)


cursor = conn.cursor()

cursor.execute("SELECT player_id FROM players WHERE team_id = 1")
team1_players = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT player_id FROM players WHERE team_id = 2")
team2_players = [row[0] for row in cursor.fetchall()]

print("Team 1 players:", team1_players)
print("Team 2 players:", team2_players)

match_id = 1
event_time = 0

actions = {"pass":1,"shot":2,"Goal":3,"tackle":4,"intercept":5,"Foul":6,"Corner":7,"Offside":8,"Yellow Card":9,"Red Card":10,"Dribble":11}

possession_team = 1



for i in range(2000):

    event_time += random.randint(2,8)

    if possession_team == 1:
        players = team1_players
        opponents = team2_players
        team_id = 1
    else:
        players = team2_players
        opponents = team1_players
        team_id = 2

    player = random.choice(players)

    action_name = random.choices(
        ["pass","shot","Goal","tackle","intercept","Foul","Corner","Offside","Yellow Card","Red Card","Dribble"],weights=[40,10,5,15,10,5,5,5,3,2,10],k=1)[0]

    action_id = actions[action_name]
    target_player = None

    if action_name == "pass":
        target_player = random.choice([p for p in players if p != player])

    if action_name in ["tackle","intercept"]:
        possession_team = 2 if possession_team == 1 else 1

    if action_name in ["Foul","Yellow Card","Red Card"]:
        target_player = random.choice(opponents)

    x_coordinate = random.uniform(0,90)
    y_coordinate = random.uniform(0,120)

    cursor.execute("""INSERT INTO match_events(match_id,event_time_seconds,team_id,player_id,action_id,target_player_id,x_coordinate , y_coordinate)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",(match_id,event_time,team_id,player,action_id,target_player,x_coordinate,y_coordinate))

conn.commit()

cursor.close()
conn.close()

