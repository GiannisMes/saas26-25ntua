from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Μοντέλο για την ενημέρωση από τον Orchestrator
class StatUpdate(BaseModel):
    event_type: str # π.χ. "RESERVATION_MADE" ή "RESERVATION_CANCELLED"

def get_db_connection():
    return mysql.connector.connect(
        host="stats_db",
        user="stats_user",
        password="stats_password",
        database="statistics_db"
    )

# --- 1. ENDPOINT ΓΙΑ ΤΟΝ ORCHESTRATOR (Ενημέρωση) ---
@app.post("/api/statistics/update")
def update_stats(update: StatUpdate):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        if update.event_type == "RESERVATION_MADE":
            cursor.execute("UPDATE GlobalStats SET metric_value = metric_value + 1 WHERE metric_name = 'total_reservations'")
        elif update.event_type == "RESERVATION_CANCELLED":
            cursor.execute("UPDATE GlobalStats SET metric_value = metric_value + 1 WHERE metric_name = 'total_cancellations'")
        
        db.commit()
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()

# --- 2. ENDPOINT ΓΙΑ ΤΟΝ ADMIN (Προβολή) ---
@app.get("/api/statistics/global")
def get_global_statistics():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM GlobalStats")
        rows = cursor.fetchall()
        # Μετατρέπουμε τη λίστα σε ένα ωραίο dictionary
        stats = {row['metric_name']: row['metric_value'] for row in rows}
        return {
            "status": "success",
            "data": stats
        }
    finally:
        cursor.close()
        db.close()