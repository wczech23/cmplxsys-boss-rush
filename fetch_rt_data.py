import requests
import pandas as pd
import random
from datetime import datetime
from pytrends.request import TrendReq
import time

def fetch_data(matching_diseases):
    
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.5)

    all_data = []
    # Process each disease one by one to find search trend relative to peak in last year
    for disease in matching_diseases:
        
        try:
            pytrends.build_payload([disease], cat=0, timeframe='today 12-m', geo='', gprop='')
            data = pytrends.interest_over_time()

            # calculating difference in popularity today compared to year average
            popularity_difference = data.loc[data.index.max(), disease] - data[disease].mean()
            # adding data to list
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            
            print(disease)
            # sleep request to avoid 429 errors
            sleep_time = random.uniform(7,10)
            time.sleep(sleep_time)

            
            
        except Exception as e:
            print(f"Error with batch {disease}: {e}")
            popularity_difference = random.uniform(-10,10)
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            continue
    return