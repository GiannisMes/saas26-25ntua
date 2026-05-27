from pydantic import BaseModel
from typing import Optional
import requests
from fastapi import FastAPI
from typing import List

class PointResJSON(BaseModel):
    pointId: str
    providerName: str
    status: str
    lat: str
    lon: str
    locationName: Optional[str] = None
    address: Optional[str] = None
    cap: Optional[int] = None
    connector: Optional[str] = None
    reservationEnd: Optional[str] = None
    pricePerKwh: Optional[float] = None


app = FastAPI()

API_KEY = "sk_saas_1bc1bc089068b423332e8c1e"

PROVIDERS = {
    "redPlug": {
        "url": "https://davinci.softlab.ntua.gr/saas26/redPlug/api/points",
        "headers": {"Authorization": f"Bearer {API_KEY}"} 
    },
    "greenPlug": {
        "url": "https://davinci.softlab.ntua.gr/saas26/greenPlug/api/chargingPoints", 
        "headers": {"Authorization": f"Bearer {API_KEY}"} 
    },
    "bluePlug": {
        "url": "https://davinci.softlab.ntua.gr/saas26/bluePlug/api/locations",
        "headers": {"Authorization": f"Bearer {API_KEY}"} 
    }
}

@app.post("/api/search", response_model=List[PointResJSON])
def search_points():
    list_points = []

    for name, info in PROVIDERS.items():
        try:
            response = requests.get(info['url'], headers=info['headers'], timeout=5)
            print(f"Provider: {name} | URL: {info['url']} | Status Code: {response.status_code}")
            
            if response.status_code == 200:
                raw_data = response.json()
                
                for item in raw_data:
                    # 1. ID & Status
                    pid = str(item.get('pointid') or item.get('id') or item.get('chargerId'))
                    status_val = str(item.get('status') or item.get('state') or item.get('currentStatus', 'available'))
                    
                    # 2. Συντεταγμένες
                    lat_val = str(
                        item.get('lat') or 
                        item.get('coords', {}).get('lat') or 
                        (item.get('geo') and item.get('geo')[1]) or "0"
                    )
                    lon_val = str(
                        item.get('long') or 
                        item.get('lon') or 
                        item.get('coords', {}).get('long') or 
                        (item.get('geo') and item.get('geo')[0]) or "0"
                    )

                    # 3. Χρόνος Λήξης Κράτησης (Ένωση των reservationendtime, reservedUntil, reservationEnd)
                    res_end = item.get('reservationEndTime') or item.get('reservationendtime') or item.get('reservedUntil') or item.get('reservationEnd')
                    if res_end is not None:
                        res_end = str(res_end)

                    # 4. Τιμή κιλοβατώρας (Ένωση των kwhRateEur, pricePerKwh)
                    price = item.get('pricePerKwh') or item.get('kwhRateEur')

                    # 5. Δημιουργία του ενιαίου, flat αντικειμένου
                    specific_point = PointResJSON(
                        pointId=pid,
                        providerName=name,
                        status=status_val,
                        lat=lat_val,
                        lon=lon_val,
                        locationName=item.get('locationName'),
                        address=item.get('address'),
                        cap=item.get('cap'),
                        connector=item.get('connector'),
                        reservationEnd=res_end,
                        pricePerKwh=price
                    )
                    list_points.append(specific_point)

        except Exception as e:
            print(f"Failed to connect to {name}: {e}")

    return list_points
