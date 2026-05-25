from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI()

# Οι διευθύνσεις των άλλων microservices
RESERVATION_URL = "http://reservation_api:8000/api/reserve"
STATISTICS_URL = "http://stats_api:8000/api/statistics/update"
PROVIDER_STATS_URL = "http://prov_stats_api:8000/api/provider_statistics"
REGISTRATION_URL = "http://reg_app:8000/api"

def send_stat_event(event_type, provider_name=None, point_id=None, user_id=None, details=None):
    try:
        payload = {"event_type": event_type}
        if provider_name: payload["provider_name"] = provider_name
        if point_id: payload["point_id"] = point_id
        if user_id: payload["user_id"] = user_id
        if details: payload["details"] = details
        requests.post(STATISTICS_URL, json=payload, timeout=3)
    except:
        pass

class ProviderRegJSON(BaseModel):
    providerName: str
    apiBaseUrl: str
    apiKey: str
    listPointsEndpoint: str
    supportsReservations: bool = False
    hasLiveStatus: bool = False

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
        raise HTTPException(status_code=503, detail=f"Το Reservation Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")

    # ΒΗΜΑ 2: Αν η κράτηση ΠΕΤΥΧΕ, ειδοποιούμε το Statistics Service
    if res_response.status_code == 200 and res_data.get("success") == True:
        try:
            # Στέλνουμε το "γεγονός" στα στατιστικά
            send_stat_event("RESERVATION_MADE", provider_name=req.provider, point_id=req.pointId, user_id=req.userId)
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
            requests.post(f"{PROVIDER_STATS_URL}/update", json=provider_payload)
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
        raise HTTPException(status_code=503, detail=f"Το Reservation Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")

    # ΒΗΜΑ 2: Αν η ακύρωση ΠΕΤΥΧΕ, ειδοποιούμε το Statistics Service
    if res_response.status_code == 200 and res_data.get("success") == True:
        try:
           send_stat_event("RESERVATION_CANCELLED", user_id=user_id, details={"reservation_id": res_id})
        except Exception:
            pass

    return res_data

# --- 3. ΠΡΟΒΟΛΗ ΣΤΑΤΙΣΤΙΚΩΝ ΠΑΡΟΧΟΥ (PROXY) ---
@app.get("/api/orchestrator/statistics/provider/{provider_name}")
def get_orchestrated_provider_stats(provider_name: str):
    try:
        # Ο Orchestrator καλεί εσωτερικά το Provider Statistics Service (8084)
        target_url = f"{PROVIDER_STATS_URL}/{provider_name}/summary"
        
        response = requests.get(target_url)
        
        # Αν το service μας απαντήσει με σφάλμα, το μεταφέρουμε στον χρήστη
        if response.status_code != 200:
            return response.json()
            
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Provider Statistics Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")


# --- 4. REGISTRATION SERVICE (PROXY) ---

@app.post("/api/orchestrator/providers/register")
def orchestrate_register_provider(req: ProviderRegJSON):
    try:
        response = requests.post(f"{REGISTRATION_URL}/register", json=req.dict())
        if response.status_code in (200, 201):
            send_stat_event("PROVIDER_REGISTERED", provider_name=req.providerName)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Registration Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")


@app.get("/api/orchestrator/providers")
def orchestrate_list_providers():
    try:
        response = requests.get(f"{REGISTRATION_URL}/providers")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Registration Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")


@app.get("/api/orchestrator/providers/{provider_name}")
def orchestrate_get_provider(provider_name: str):
    try:
        response = requests.get(f"{REGISTRATION_URL}/providers/{provider_name}")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Registration Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")


@app.delete("/api/orchestrator/providers/{provider_name}")
def orchestrate_delete_provider(provider_name: str):
    try:
        response = requests.delete(f"{REGISTRATION_URL}/providers/{provider_name}")
        if response.status_code == 200:
            send_stat_event("PROVIDER_DELETED", provider_name=provider_name)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Το Registration Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")

@app.post("/api/orchestrator/search")
def orchestrate_search():
    try:

        response = requests.post(SEARCH_URL)
        send_stat_event("SEARCH_PERFORMED", details={"results_count": len(search_results) if isinstance(search_results, list) else 0})
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Σφάλμα στο Search Service")
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Το Search Service δεν είναι διαθέσιμο. Σφάλμα: {str(e)}")
    