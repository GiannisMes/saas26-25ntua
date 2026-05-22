from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import mysql.connector
import requests
import uuid
from datetime import datetime

app = FastAPI()

# --- Αντικατάστησε με το δικό σου αληθινό κλειδί ---
MY_API_KEY = "sk_saas_1bc1bc089068b423332e8c1e" 

class ReservationReqJSON(BaseModel):
    pointId: str
    userId: str
    provider: str
    duration: int = 60

class ReservationResJSON(BaseModel):
    reservationId: str
    success: bool
    endTime: str
    errorMessage: Optional[str] = None

def get_db_connection():
    return mysql.connector.connect(
        host="res_db", 
        user="root",
        password="root_password",
        database="reservation_db"
    )

# --- 1. ENDPOINT ΓΙΑ ΚΡΑΤΗΣΗ ---
@app.post("/api/reserve", response_model=ReservationResJSON)
def create_reservation(req: ReservationReqJSON):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    headers = {"Authorization": f"Bearer {MY_API_KEY}"}
    
    try:
        # Έλεγχος αν είναι ήδη κρατημένο
        cursor.execute("SELECT id FROM Reservation WHERE pointId = %s AND status = 'ACTIVE'", (req.pointId,))
        if cursor.fetchone():
            return ReservationResJSON(reservationId="", success=False, endTime="", errorMessage="Point already reserved!")

        # Επικοινωνία με παρόχους
        if req.provider == "greenPlug":
            url = f"https://davinci.softlab.ntua.gr/saas26/greenPlug/api/chargingPoints/{req.pointId}/reservations"
            res = requests.post(url, json={"duration": req.duration}, headers=headers)
        elif req.provider == "bluePlug":
            url = f"https://davinci.softlab.ntua.gr/saas26/bluePlug/api/location/{req.pointId}/hold?minutes={req.duration}"
            res = requests.post(url, headers=headers)
        elif req.provider == "redPlug":
            # Check if the user provided a duration
            if req.duration is not 60:
                # Use the URL that includes the minutes
                url = f"https://davinci.softlab.ntua.gr/saas26/redPlug/api/reserve/{req.pointId}/{req.duration}"
            else:
                # Use the URL that relies on the provider's default
                url = f"https://davinci.softlab.ntua.gr/saas26/redPlug/api/reserve/{req.pointId}"
            res = requests.post(url, headers=headers)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")

        if res.status_code == 200:
            data = res.json()
            end_time = data.get("reservationEnd") or data.get("reservedUntil") or data.get("reservationendtime")
            new_id = str(uuid.uuid4())
            
            cursor.execute("INSERT INTO Reservation (id, pointId, userId, startTime, endTime, status) VALUES (%s, %s, %s, %s, %s, %s)",
                           (new_id, req.pointId, req.userId, datetime.now(), end_time, "ACTIVE"))
            db.commit()
            return ReservationResJSON(reservationId=new_id, success=True, endTime=end_time)
        
        return ReservationResJSON(reservationId="", success=False, endTime="", errorMessage=res.text)

    finally:
        cursor.close()
        db.close()

# --- 2. ENDPOINT ΓΙΑ ΑΚΥΡΩΣΗ ---
@app.put("/api/reserve/{res_id}/cancel")
def cancel_reservation(res_id: str, user_id: str):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Reservation WHERE id = %s", (res_id,))
        res = cursor.fetchone()
        if not res or res['userId'] != user_id:
            raise HTTPException(status_code=404, detail="Reservation not found or unauthorized")
        
        cursor.execute("UPDATE Reservation SET status = 'CANCELLED' WHERE id = %s", (res_id,))
        db.commit()
        return {"success": True, "message": "Cancelled successfully"}
    finally:
        cursor.close()
        db.close()


# ==========================================
# 3. ENDPOINT ΓΙΑ ΣΤΑΤΙΣΤΙΚΑ (GET) - Για το Admin Service
# ==========================================
@app.get("/api/admin/stats")
def get_reservation_stats():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # Μετράμε συνολικές κρατήσεις
        cursor.execute("SELECT COUNT(*) as total FROM Reservation")
        total = cursor.fetchone()['total']
        
        # Μετράμε μόνο τις ενεργές
        cursor.execute("SELECT COUNT(*) as active FROM Reservation WHERE status = 'ACTIVE'")
        active = cursor.fetchone()['active']
        
        # Μετράμε τις ακυρωμένες
        cursor.execute("SELECT COUNT(*) as cancelled FROM Reservation WHERE status = 'CANCELLED'")
        cancelled = cursor.fetchone()['cancelled']
        
        return {
            "total_reservations": total,
            "active_reservations": active,
            "cancelled_reservations": cancelled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        db.close()