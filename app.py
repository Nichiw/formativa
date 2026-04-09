import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


API = FastAPI()

metrics = {"requests": 0, "errors": 0, "failed_logins": 0}

class LoginData(BaseModel):
    username: str
    password: str
    
def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="aLogins",
        cursorclass=pymysql.cursors.DictCursor
    )


class LoginData(BaseModel):
    username: str
    password: str

@API.get("/health")
def health():
    metrics["requests"] += 1
    return {"status": "OK"}


@API.post("/login")
def login(data: LoginData):
    metrics["requests"] += 1
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                    (data.username, data.password))
        user = cur.fetchone()
    conn.close()

    if not user:
        metrics["failed_logins"] += 1
        metrics["errors"] += 1
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    return {"message": "Login OK", "user": data.username}

@API.get("/metrics")
def get_metrics():
    metrics["requests"] += 1
    return metrics