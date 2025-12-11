import json
import sqlite3
import pandas as pd

with open("US_recipes_null.json" , 'r') as file:
    data = json.load(file)
rows=[]
for key,item in data.items():
  rows.append({
    "cuisine":item.get("cuisine"),
    "title":item.get("title"),
    "rating":item.get("rating"),
    "prep_time":item.get("prep_time"),
    "cook_time":item.get("cook_time"),
    "total_time":item.get("total_time"),
    "description":item.get("description"),
    "nutrients":json.dumps(item.get("nutrients",{})),
    "serves":item.get("serves"),
  })

df=pd.DataFrame(rows)

connector=sqlite3.connect('recipes.db')
df.to_sql('recipes',connector,if_exists='replace',index=False)
connector.close()

