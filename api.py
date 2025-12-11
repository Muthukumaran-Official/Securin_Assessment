from fastapi import FastAPI
import sqlite3
from fastapi.responses import FileResponse
import re
import json

app = FastAPI()
DB = "recipes.db"

def run(q, p=()):
    conn = sqlite3.connect(DB)
    cur = conn.execute(q, p)
    cols = [c[0] for c in cur.description]

    rows = []
    for r in cur.fetchall():
        row = dict(zip(cols, r))

        # Convert nutrient string → dict
        if "nutrients" in row and isinstance(row["nutrients"], str):
            try:
                row["nutrients"] = json.loads(row["nutrients"])
            except:
                pass

        rows.append(row)

    conn.close()
    return rows


#PAGINATED RECIPES (SORTED BY RATING)
@app.get("/api/recipes")
def list_recipes(page: int = 1, limit: int = 10):
    off = (page - 1) * limit
    q = "SELECT title,cuisine,rating,total_time,serves,nutrients FROM recipes ORDER BY rating DESC LIMIT ? OFFSET ?"
    data = run(q, (limit, off))
    return data if data else {"message": "No recipes found"}


#SEARCH WITH ALL FILTERS + PAGINATION (Flexible operators)
@app.get("/api/recipes/search")
def search(
    title: str = None,
    cuisine: str = None,
    total_time: str = None,
    rating: str = None,
    calories: str = None,
    carbohydrateContent: str = None,
    cholesterolContent: str = None,
    fiberContent: str = None,
    proteinContent: str = None,
    saturatedFatContent: str = None,
    sodiumContent: str = None,
    sugarContent: str = None,
    fatContent: str = None,
    page: int = 1, limit: int = 15,
):
    if limit < 15: limit = 15
    if limit > 50: limit = 50
    off = (page - 1) * limit

    q = "SELECT * FROM recipes WHERE 1=1"
    p = []

    if title:
        q += " AND title LIKE ?"
        p.append(f"%{title}%")
    if cuisine:
        q += " AND cuisine LIKE ?"
        p.append(f"%{cuisine}%")

    #Operator parser
    def parse_operator(value: str):
        match = re.match(r"(>=|<=|=|>|<)?\s*(\d+(\.\d+)?)", value)
        if match:
            op, val, _ = match.groups()
            if not op:
                op = "="
            return op, float(val)
        return None, None

    #Direct fields: rating, total_time
    for field, val in {"rating": rating, "total_time": total_time}.items():
        if val:
            op, num = parse_operator(val)
            if op and num is not None:
                q += f" AND {field} {op} ?"
                p.append(num)

    #Nutrients
    nutrients = {
        "calories": calories,
        "carbohydrateContent": carbohydrateContent,
        "cholesterolContent": cholesterolContent,
        "fiberContent": fiberContent,
        "proteinContent": proteinContent,
        "saturatedFatContent": saturatedFatContent,
        "sodiumContent": sodiumContent,
        "sugarContent": sugarContent,
        "fatContent": fatContent,
    }

    for k, v in nutrients.items():
        if v:
            op, num = parse_operator(v)
            if op and num is not None:
                q += f" AND CAST(JSON_EXTRACT(nutrients,'$.{k}') AS FLOAT) {op} ?"
                p.append(num)

    q += " LIMIT ? OFFSET ?"
    p += [limit, off]

    data = run(q, p)
    return data if data else {"message": "No results found"}


# Serve frontend
@app.get("/", response_class=FileResponse)
def serve_frontend():
    return "frontend.html"


