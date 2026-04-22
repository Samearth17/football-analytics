import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt 
from mplsoccer import Pitch
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="football_analytics",
    #table="Co_ordinate",
    user="postgres",
    password="Samarth30"
)

query = "SELECT x_coordinate, y_coordinate FROM Co_ordinate  "
df = pd.read_sql_query(query, conn)


pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white')
fig , ax = pitch.draw(figsize=(10,7))


sns.kdeplot(x = df['y_coordinate'], y = df['x_coordinate'], fill = True , thresh = 0.05 , levels = 100 , cmap = 'hot' , alpha = 0.5 , ax = ax)

plt.title("Heatmap of Player Actions in Match 1")
plt.show()
