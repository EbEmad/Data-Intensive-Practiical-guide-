import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
app = FastAPI()

# DB Connections (use DSNs from env)
import os
PRIMARY_DSN = os.getenv("PRIMARY_DSN")
REPLICA_DSN = os.getenv("REPLICA_DSN")

def get_primary_conn():
    return psycopg2.connect(PRIMARY_DSN, cursor_factory=RealDictCursor)

def get_replica_conn():
    return psycopg2.connect(REPLICA_DSN, cursor_factory=RealDictCursor)


class USER(BaseModel):
    name:str
    email:str

@app.post("/user/")
def create_user(user:USER):
    conn=get_primary_conn()
    try:
        with conn.cursor()as cur:
            cur.execute("""
            INSERT INTO users (name,email) VALUES (%s,%s) RETURNING id
            """,(user.name,user.email))
            user_id=cur.fetchone()["id"]
            conn.commit()
        return {"id":user_id,"name":user.name,"email":user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/users/{user_ia}")
def read_user(user_id:int):
    conn=get_replica_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""  SELECT * FROM users WHERE id = %s """,(user_id))
            user=cur.fetchone()
            if not user:
                raise HTTPException(status_code=404,detail="User not found")
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/users")
def read_all_users():
    conn=get_replica_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT * FROM users""")
            users=cur.fetchall()
            return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
        
@app.put("/users/{user_id}")
def update_user(user_id:int,user:USER):
    conn=get_primary_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (user.name, user.email, user_id)
            )
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        return {"id": user_id, "name": user.name, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_primary_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="User not found")
        return {"deleted": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()