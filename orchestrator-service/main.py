from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()

# Οι διευθύνσεις των άλλων microservices
RESERVATION_URL = "http://reservation_api:8000/api/reserve"
STATISTICS_URL = "http://stats_api:8000/api/statistics/update"
PROVIDER_STATS_URL = "http://prov_stats_api:8000/api/provider_statistics/update"
# Το ίδιο "καλούπι" που στέλνει ο χρήστης
class ReservationReqJSON(BaseModel):
    pointId: str
    userId: str
    provider: str
    duration: int = 60

@app.post("/api/orchestrator/reserve")
def orchestrate_reservation(req: ReservationReqJSON):
    # ΒΗΜΑ 1: Ζητάμε από το Reservation Service να κάνει την κράτηση
    try:
        res_response = requests.post(RESERVATION_URL, json=req.dict())
        res_data = res_response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Το Reservation Service δεν είναι διαθέσιμο.")

    # ΒΗΜΑ 2: Αν η κράτηση ΠΕΤΥΧΕ, ειδοποιούμε το Statistics Service
    if res_response.status_code == 200 and res_data.get("success") == True:
        try:
            # Στέλνουμε το "γεγονός" στα στατιστικά
            requests.post(STATISTICS_URL, json={"event_type": "RESERVATION_MADE"})
        except Exception:
            # Αν τα στατιστικά έχουν "πέσει", δεν ακυρώνουμε την κράτηση του πελάτη.
            # Απλά το αγνοούμε (ή το γράφουμε σε ένα log).
            pass 
        # ΕΝΗΜΕΡΩΣΗ 2: Provider Statistics
        try:
            provider_payload = {
                "providerName": req.provider, 
                "pointId": req.pointId,       
                "eventType": "Reservation",
                "isSuccess": True,
                "pointStatus": "reserved"
            }
            requests.post(PROVIDER_STATS_URL, json=provider_payload)
        except Exception:
            pass

    # ΒΗΜΑ 3: Επιστρέφουμε την απάντηση στον πελάτη
    return res_data


@app.put("/api/orchestrator/reserve/{res_id}/cancel")
def orchestrate_cancellation(res_id: str, user_id: str):
    # ΒΗΜΑ 1: Ζητάμε ακύρωση από το Reservation Service
    try:
        cancel_url = f"{RESERVATION_URL}/{res_id}/cancel"
        res_response = requests.put(cancel_url, params={"user_id": user_id})
        res_data = res_response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Το Reservation Service δεν είναι διαθέσιμο.")

    # ΒΗΜΑ 2: Αν η ακύρωση ΠΕΤΥΧΕ, ειδοποιούμε το Statistics Service
    if res_response.status_code == 200 and res_data.get("success") == True:
        try:
            requests.post(STATISTICS_URL, json={"event_type": "RESERVATION_CANCELLED"})
        except Exception:
            pass

    return res_data

# --- 3. ΠΡΟΒΟΛΗ ΣΤΑΤΙΣΤΙΚΩΝ ΠΑΡΟΧΟΥ (PROXY) ---
@app.get("/api/orchestrator/statistics/provider/{provider_name}")
def get_orchestrated_provider_stats(provider_name: str):
    try:
        # Ο Orchestrator καλεί εσωτερικά το Provider Statistics Service (8084)
        target_url = f"http://172.17.0.1:8084/api/statistics/provider_statistics/{provider_name}/summary"
        
        response = requests.get(target_url)
        
        # Αν το service μας απαντήσει με σφάλμα, το μεταφέρουμε στον χρήστη
        if response.status_code != 200:
            return response.json()
            
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Provider Statistics Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")
