from fastapi import FastAPI, HTTPException
import fastavro
from io import BytesIO
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reader Service - Avro v2 (evolved schema)")
DATABASE_URL = os.getenv("DATABASE_URL")


# Load reader schema v2 (evolved)
with open("./person_v2.avsc", "r") as f:
    reader_schema = json.load(f)

# Load writer schema v1 (original format data was written with)
with open("./person_v1.avsc", "r") as f:
    writer_schema = json.load(f)

def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

@app.get("/users/{user_id}")
def read_user(user_id:int):
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT data FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "User not found")
    finally:
        conn.close()
    
    # Deserialize using both writer schema (v1) and reader schema (v2) → Avro resolves differences
    bytes_reader = BytesIO(row["data"])
    record = fastavro.schemaless_reader(bytes_reader, writer_schema, reader_schema)

    # Avro automatically added photoUrl: null
    return {
        "user": record,
        "message": "Read successfully using evolved schema v2 (photoUrl added as default)"
    }