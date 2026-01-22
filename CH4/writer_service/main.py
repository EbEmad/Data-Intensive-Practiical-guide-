from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import List
import fastavro
from io import BytesIO
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import logging
from fastapi import Depends
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
app=FastAPI(title="Writer Service - Avro v1")

DATABASE_URL = os.getenv("DATABASE_URL")


with open("./person_v1.avsc","r") as f:
    schema = json.load(f)

class UserCreate(BaseModel):
    userName:str
    favoriteNumber:int|None=None
    interests:list[str]=[]

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        logger.info("Closing database connection")
        conn.close()


@app.post("/users/")
def create_user(user: UserCreate, conn = Depends(get_db)):
    # Serialize with Avro v1
    record = user.dict()
    bytes_writer=BytesIO()
    fastavro.schemaless_writer(bytes_writer, schema, record)
    avro_bytes = bytes_writer.getvalue()

    # Save to Postgres
    with conn.cursor() as cur:  # Fixed typo
        cur.execute(
            "INSERT INTO users (data) VALUES (%s) RETURNING id",
            (avro_bytes,)
        )
        user_id = cur.fetchone()["id"]
    conn.commit()
    
    logger.info(f"Created user with ID: {user_id}")
    return {"id": user_id, "data": record}

@app.on_event("startup")
def startup():
    # Create table if not exists
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    data BYTEA NOT NULL
                )
            """)
        conn.commit()