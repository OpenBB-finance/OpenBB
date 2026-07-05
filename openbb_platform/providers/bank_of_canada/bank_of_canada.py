import requests
from datetime import datetime

import logging

logging.basicConfig(
    filename="app.log", 
    filemode="a", 
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BASE_URL = "https://www.bankofcanada.ca/valet/observations"


# get exchange rates
def get_exchange_rates():
    
    try:
        url = f"{BASE_URL}/FXUSDCAD/json"
        data = requests.get(url).json()
        latest = data['observations'][-1]
        
        return {
            'pair': 'USDCAD',
            'rate': float(latest['FXUSDCAD']['v']),
            'date': latest['d']
        }
    except Exception as e:
        logging.error(f"error: {e}")
        return None





# get interest rates
def get_interest():

    try:
        url = f"{BASE_URL}/CBC20210/json"
        data = requests.get(url).json()
        latest = data['observations'][-1]
        
        return {
            'interest_url': 'CBC20210',
            'rate': float(latest['CBC20210']['v']),
            'date': latest['d']
        }
    except Exception as e:
        logging.error(f"error: {e}")
        return None
    
    
    
    
# bond yields 
def get_bonds_rates():
    
    try:
        url = f"{BASE_URL}/BD.CDN.10YR.DQ.YLD/json"
        data = requests.get(url).json()
        latest = data['observations'][-1]
        
        
        return {
            'bond_int': 'BD.CDN.10YR.DQ.YLD',
            'rate': float(latest['BD.CDN.10YR.DQ.YLD']['v']),
            'date': latest['d']
        }
        
    except Exception as e:
        logging.error(f"error: {e}")
        return None




# callings 
print("exchange rates ", get_exchange_rates())
print("interest rates", get_interest())
print("bond yields", get_bonds_rates())


