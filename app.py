import pymysql
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging



LOGGER = logging.getlogger((__name__))
LOGGER.setlevel(logging.INFO)

SH = logging.StreamHandler(stream=sys.stdout)
SH.setLevel(logging.INFO)

LOGGER.addhandler(SH)

FORMATTER = logging.Formatter(fmt="asctimes, levelname, message")

app = FastAPI()

metrics = {"requests": 0, "errors": 0, "failed_logins": 0}

def get_conn():
    for i in range(10):
        try:
            return pymysql.connect(
                host="localhost",
                user="root",
                password="root",
                database="api_db",
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception:
            time.sleep(2)
    raise Exception("Não foi possível conectar ao banco")

class LoginData(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    metrics["requests"] += 1
    return {"status": "OK"}

@app.post("/login")
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

@app.get("/metrics")
def get_metrics():
    metrics["requests"] += 1
    return metrics
