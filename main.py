import os
from fastapi import FastAPI, status, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Bookmarks API", version="1.0")

# DATABASE CONNECTION -------------------------------------------------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}

def get_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                            detail=f"Database does not answer: {str(e)}")

def close_db_connection(cursor, connection):
    cursor.close()
    connection.close()

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
@app.get("/health",status_code=status.HTTP_200_OK, operation_id="health")
def health():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute("SELECT 1;")
    except Exception as e:
        close_db_connection(cursor, conn)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Service up, but the database does not answer")

    close_db_connection(cursor, conn)

    return Health(status="ok")

# Get all bookmarks, or those with exactly this name
@app.get("/api/bookmarks", status_code=status.HTTP_200_OK, operation_id="listBookmarks")
def list_bookmarks(name: str | None = None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    result = []
    if name:
        cursor.execute("SELECT id, name, visits FROM bookmarks WHERE name = %s ORDER BY id ASC;", 
                       (name,))
    else:
        cursor.execute("SELECT id, name, visits FROM bookmarks ORDER BY id ASC;")
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result

# Create a bookmark
@app.post("/api/bookmarks", status_code=status.HTTP_201_CREATED,
           operation_id="createBookmark", 
           responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
def create_bookmark(bookmark: NewBookmark):
    try:
        bookmark = NewBookmark.model_validate(bookmark)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={"error": "The body is not a valid NewBookmark"}
        )
    if not bookmark.name or len(bookmark.name) < 1 or len(bookmark.name) > 100 or "\u0000" in bookmark.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"error": "The body is not a valid NewBookmark"})
    elif bookmark.visits < 0 or bookmark.visits > 1000000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail={"error": "The body is not a valid NewBookmark"})

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("INSERT INTO bookmarks (name, visits) VALUES (%s, %s) RETURNING id, name, visits;",
                   (bookmark.name, bookmark.visits))

    new_bookmark = cursor.fetchone()

    conn.commit()

    close_db_connection(cursor, conn)

    return new_bookmark

# Get a bookmark
@app.get("/api/bookmarks/{id}", status_code=status.HTTP_200_OK, 
         operation_id="getBookmark", 
         responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
def get_bookmark(id: int):
    if id <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail={"error": "The id is not a positive integer"})

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    result = []
    cursor.execute("SELECT id, name, visits FROM bookmarks WHERE id = %s;", (id,))
    result = cursor.fetchone()

    close_db_connection(cursor, conn)

    if not result:
        raise HTTPException(status_code=404, 
                            detail={"error": "No bookmark with this id"})

    return result

# Delete a bookmark
@app.delete("/api/bookmarks/{id}", status_code=status.HTTP_204_NO_CONTENT, 
            operation_id="deleteBookmark", 
            responses={status.HTTP_404_NOT_FOUND: {"model": Error}})
def delete_bookmark(id: int):
    if id <= 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"error": "The id is not a positive integer"})

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    result = []
    cursor.execute("DELETE FROM bookmarks WHERE id = %s RETURNING id;", (id,))
    result = cursor.fetchone()

    if not result:
        close_db_connection(cursor, conn)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={"error": "No bookmark with this id"})
    else:
        conn.commit()

    close_db_connection(cursor, conn)
