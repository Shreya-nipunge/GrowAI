import os
import requests
from dotenv import load_dotenv

load_dotenv()
AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY")

def get_agmarknet_data(commodity="Onion", state="Maharashtra", market="Mumbai", date="2025-08-16"):
    """
    Fetch commodity price data from Agmarknet via data.gov.in API.
    You need to replace <resource_id> with the one for the commodity dataset.
    """
    resource_id = "35985678-0d79-46b4-9ed6-6f13308a1d24"  # Agmarknet dataset ID (All India prices)
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json"
    
    params = {
        "api-key": AGMARKNET_API_KEY,
        "format": "json",
        "limit": 10,
        "filters[commodity]": commodity,
        "filters[state]": state,
        "filters[market]": market,
        "filters[arrival_date]": date
    }
    
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    print(get_agmarknet_data())
