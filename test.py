from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Mini Items API", version="1.0")

# DATABASE CONNECTION -------------------------------------------------------------------

DB_CONFIG = {
    "host": "172.30.160.1",
    "database": "postgres",
    "user": "postgres",
    "password": "Vic62189l555",
    "port": "5432"
}

def get_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database does not answer: {str(e)}")

# API -------------------------------------------------------------------

class Health(BaseModel):
    status: str

class Error(BaseModel):
    error: str

class NewBookmark(BaseModel):
    name: str
    visits: int

class Bookmark(BaseModel):
    id: int
    name: str
    visits: int

# Check if the service is up and can reach its database
@app.get("/health",status_code=200, operation_id="health")
def health():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT 1;")
    except Exception as e:
        raise HTTPException(status_code=503, detail="Service up, but the database does not answer")

    cursor.close()
    conn.close()

    return Health(status="ok")

# Get all bookmarks, or those with exactly this name
@app.get("/api/bookmarks", status_code=200, operation_id="listBookmarks")
def list_bookmarks(name: str | None = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    result = []
    if name:
        cursor.execute("SELECT id, name, visits FROM bookmarks WHERE name = %s ORDER BY id ASC;", (name,))
    else:
        cursor.execute("SELECT id, name, visits FROM bookmarks ORDER BY id ASC;")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Create a bookmark
@app.post("/api/bookmarks", status_code=201, operation_id="createBookmark", responses={400: {"model": Error}})
def create_item(bookmark: NewBookmark):
    conn = get_db_connection()

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("INSERT INTO bookmarks (name, visits) VALUES (%s, %s) RETURNING id, name, visits;",
                       (bookmark.name, bookmark.visits))
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "The body is not a valid NewBookmark"})

    new_bookmark = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return new_bookmark

# TODO: /api/bookmarks/{id}
