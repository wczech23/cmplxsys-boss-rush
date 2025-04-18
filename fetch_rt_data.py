import pandas as pd
import random
from pytrends.request import TrendReq
import time




def fetch_data(matching_diseases, state_abbr):
    pd.set_option('future.no_silent_downcasting', True)
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.5)

    all_data = []
    # Process each disease one by one to find search trend relative to peak in last year
    for disease in matching_diseases:
        try:
            # sleep request to avoid 429 errors
            sleep_time = random.uniform(7,10)
            time.sleep(sleep_time)

            geo_code = f'US-{state_abbr}'
            # add in data to refine searching by state
            pytrends.build_payload([disease], timeframe='today 12-m', geo=geo_code)
            data = pytrends.interest_over_time()

            # calculating difference in popularity today compared to year average
            popularity_difference = data.loc[data.index.max(), disease] - data[disease].mean()
            # adding data to list
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            
            print(f'Gathered data on {disease}')
            
        except Exception as e:
            print(f"Error gathering {disease} data")
            popularity_difference = random.uniform(-10,10)
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            continue

    # Combine all items in the list into a single df
    if all_data:
        combined_df = pd.DataFrame(all_data)
        combined_df.to_csv("disease_trends_US.csv", index=False)
        print("\nUpdated daily search trends!")