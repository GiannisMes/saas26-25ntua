import requests
from fastapi import FastAPI
from typing import List
from schemas import  PointResJSON

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
                    # Get IDs
                    pid = str(item.get('pointid') or item.get('id') or item.get('chargerId'))
                    
                    # Get status
                    status_val = str(item.get('status') or item.get('state') or item.get('currentStatus', 'available'))
                    
                    # Get coordinates
                    lat_val = str(item.get('lat') or item.get('coords', {}).get('lat') or item.get('geo', [0,0])[1])
                    lon_val = str(item.get('long') or item.get('lon') or item.get('coords', {}).get('long') or item.get('geo', [0,0])[0])

                    specific_point = PointResJSON(
                        pointId=pid,
                        providerName=name,
                        status=status_val,
                        lat=lat_val,
                        lon=lon_val
                    )
                    list_points.append(specific_point)

        except Exception as e:
            print(f"Failed to connect to {name}: {e}")

    return list_points
